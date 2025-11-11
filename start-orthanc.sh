#!/bin/bash

# Enhanced Orthanc DICOM server with DICOMweb support and sample data
# This script properly configures Orthanc with DICOMweb plugin and loads test data

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "========================================"
echo "   Starting Orthanc DICOM Server"
echo "========================================"
echo -e "${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

echo -e "${YELLOW}Creating proper Orthanc configuration...${NC}"

# Create configuration directory
mkdir -p orthanc-config
mkdir -p dicom-data

# Create a proper Orthanc configuration file with plugin path
cat > orthanc-config/orthanc.json << 'EOF'
{
  "Name" : "DICOMweb Test Server",
  "HttpServerEnabled" : true,
  "HttpPort" : 8042,
  "HttpDescribeErrors" : true,
  "AuthenticationEnabled" : true,
  "RemoteAccessAllowed" : true,
  "RegisteredUsers" : {
    "orthanc" : "orthanc"
  },
  
  "DicomWeb" : {
    "Enable" : true,
    "Root" : "/dicom-web/",
    "EnableWado" : true,
    "WadoRoot" : "/wado",
    "ServeUnknown" : true,
    "StudiesMetadata" : "Full",
    "SeriesMetadata" : "Full",
    "EnableMetadataCache": true,
    "EnablePerformanceLogs": true
  },
  
  "HttpCompressionEnabled" : true,
  "HttpThreadsCount" : 16,
  "HttpMaxClients" : 16,
  
  "DicomServer" : {
    "Enabled" : true,
    "Port" : 4242,
    "ConnectionTimeout" : 10
  },
  
  "Storage" : {
    "StorageDirectory" : "/var/lib/orthanc/db",
    "MaximumStorageSize" : 5000,
    "MaximumPatientRecords" : 10000
  },
  
  "LogLevel" : 2,
  "TraceLevel" : 1,
  "DefaultEncoding" : "Utf8"
}
EOF

echo -e "${YELLOW}Extracting test DICOM data...${NC}"

# Use the local DICOM test data (CT and X-ray studies)
echo -e "${YELLOW}Extracting CT study (multiple slices)...${NC}"
unzip -q test_data/02ef8f31ea86a45cfce6eb297c274598.zip -d dicom-data/ct_study/

echo -e "${YELLOW}Extracting X-ray study (single image)...${NC}"
unzip -q test_data/feb6447a72c9a0a31e1bb4459e547964.zip -d dicom-data/xray_study/

echo -e "${YELLOW}Cleaning up existing containers...${NC}"

# Stop and remove any existing container
if docker ps -a --format "table {{.Names}}" | grep -q "^orthanc-dicomweb$"; then
    echo -e "${YELLOW}Stopping existing Orthanc container...${NC}"
    docker stop orthanc-dicomweb &> /dev/null || true
    docker rm orthanc-dicomweb &> /dev/null || true
fi

# Remove old data volume if it exists
docker volume rm orthanc-storage &> /dev/null || true

echo -e "${YELLOW}Starting Orthanc with DICOMweb support...${NC}"

# Start Orthanc with the correct image and configuration
docker run -d \
    --name orthanc-dicomweb \
    -p 8042:8042 \
    -p 4242:4242 \
    -v "$(pwd)/orthanc-config:/etc/orthanc:ro" \
    -v "orthanc-storage:/var/lib/orthanc/db" \
    jodogne/orthanc-plugins

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to start Orthanc container${NC}"
    exit 1
fi

echo -e "${YELLOW}Waiting for Orthanc to be ready...${NC}"

# Wait for Orthanc to be ready
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -s -f -u orthanc:orthanc "http://localhost:8042/" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Orthanc is ready!${NC}"
        break
    fi
    attempt=$((attempt + 1))
    echo -e "${YELLOW}Waiting for Orthanc... (attempt $attempt/$max_attempts)${NC}"
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo -e "${RED}✗ Orthanc failed to start within timeout${NC}"
    docker logs orthanc-dicomweb
    exit 1
fi

echo -e "${YELLOW}Loading DICOM data...${NC}"

# Load extracted DICOM files
echo -e "${YELLOW}Uploading CT study files...${NC}"
for dcm_file in dicom-data/ct_study/series-000001/*.dcm; do
    if [ -f "$dcm_file" ]; then
        echo -e "${YELLOW}Uploading $(basename "$dcm_file")...${NC}"
        curl -s -X POST "http://localhost:8042/instances" \
            --data-binary @"$dcm_file" \
            -u orthanc:orthanc \
            -H "Content-Type: application/dicom" > /dev/null 2>&1 || {
            echo -e "${YELLOW}! Upload failed for $(basename "$dcm_file")${NC}"
        }
    fi
done

echo -e "${YELLOW}Uploading X-ray study file...${NC}"
for dcm_file in dicom-data/xray_study/series-000001/*.dcm; do
    if [ -f "$dcm_file" ]; then
        echo -e "${YELLOW}Uploading $(basename "$dcm_file")...${NC}"
        curl -s -X POST "http://localhost:8042/instances" \
            --data-binary @"$dcm_file" \
            -u orthanc:orthanc \
            -H "Content-Type: application/dicom" > /dev/null 2>&1 || {
            echo -e "${YELLOW}! Upload failed for $(basename "$dcm_file")${NC}"
        }
    fi
done

# Give Orthanc time to process the data
sleep 3

echo -e "${YELLOW}Testing DICOMweb endpoints...${NC}"

# Test DICOMweb functionality
if curl -s -u orthanc:orthanc "http://localhost:8042/dicom-web/studies" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ DICOMweb QIDO-RS is working!${NC}"
else
    echo -e "${YELLOW}! DICOMweb QIDO-RS may need more time to initialize${NC}"
fi

# Check if we have any data
studies_count=$(curl -s "http://localhost:8042/dicom-web/studies" -u "orthanc:orthanc" 2>/dev/null | python3 -c "import json,sys; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
if [ "$studies_count" -gt 0 ]; then
    echo -e "${GREEN}✓ Loaded $studies_count studies for testing${NC}"
else
    echo -e "${YELLOW}! No studies loaded - tests will have limited data${NC}"
fi

echo -e "${GREEN}"
echo "========================================"
echo "✅ Orthanc DICOM Server is Ready!"
echo "========================================"
echo "Web Interface: http://localhost:8042/"
echo "DICOMweb URL: http://localhost:8042/dicom-web/"
echo "Username: orthanc"
echo "Password: orthanc"
echo "Studies loaded: $studies_count"
echo "========================================"
echo ""
echo "To stop: docker stop orthanc-dicomweb"
echo "To remove: docker rm orthanc-dicomweb"
echo -e "${NC}"

# Keep the container running
echo -e "${YELLOW}Orthanc container is running in the background.${NC}"
echo -e "${YELLOW}Use the test-local-orthanc.sh script to run tests.${NC}"