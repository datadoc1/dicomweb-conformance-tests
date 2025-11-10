#!/bin/bash

# DICOMweb Conformance Test Suite - Fixed Docker Testing Script
# This script launches a properly configured Orthanc instance for DICOMweb testing

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ORTHANC_CONTAINER_NAME="dicomweb-test-orthanc"
ORTHANC_PORT=8042
ORTHANC_DICOM_PORT=4242
DOCKER_IMAGE="jodogne/orthanc-plugins"
SAMPLE_DATA_DIR="test_data"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to create enhanced Orthanc configuration
create_orthanc_config() {
    local config_file="/tmp/orthanc_$(date +%s).json"
    
    cat > "$config_file" << 'EOF'
{
  "Name" : "DICOMweb Test Server",
  "HttpServerEnabled" : true,
  "HttpPort" : 8042,
  "HttpDescribeErrors" : true,
  "AuthenticationEnabled" : true,
  "RegisteredUsers" : {
    "orthanc" : "orthanc"
  },
  
  "DicomWeb" : {
    "Enable" : true,
    "Root" : "/dicom-web/",
    "ServeUnknown" : true,
    "Json" : true
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
  
  "Plugins" : {
    "WebViewer" : true,
    "OrthancWebViewer" : true
  }
}
EOF

    echo "$config_file"
}

# Function to check if Docker is available
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        print_status "Please install Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running"
        print_status "Please start Docker daemon and try again"
        exit 1
    fi
    
    print_success "Docker is available and running"
}

# Function to cleanup existing containers
cleanup_existing() {
    print_status "Cleaning up existing containers..."
    
    if docker ps -a --format "table {{.Names}}" | grep -q "^${ORTHANC_CONTAINER_NAME}$"; then
        print_status "Stopping and removing existing container: $ORTHANC_CONTAINER_NAME"
        docker stop "$ORTHANC_CONTAINER_NAME" &> /dev/null || true
        docker rm "$ORTHANC_CONTAINER_NAME" &> /dev/null || true
    fi
}

# Function to start Orthanc container with proper configuration
start_orthanc() {
    print_status "Starting enhanced Orthanc container..."
    
    local config_file=$(create_orthanc_config)
    
    # Create a temporary directory for sample data
    local sample_data_volume="/tmp/orthanc-sample-data-$(date +%s)"
    mkdir -p "$sample_data_volume"
    
    # Copy sample DICOM files if they exist
    if [ -d "$SAMPLE_DATA_DIR" ]; then
        print_status "Copying sample DICOM data..."
        cp -r "$SAMPLE_DATA_DIR"/* "$sample_data_volume/" 2>/dev/null || true
    fi
    
    # Start container with proper configuration
    docker run -d \
        --name "$ORTHANC_CONTAINER_NAME" \
        -p "$ORTHANC_PORT:8042" \
        -p "$ORTHANC_DICOM_PORT:4242" \
        -v "$sample_data_volume:/var/lib/orthanc/db:rw" \
        -v "$config_file:/etc/orthanc/orthanc.json:ro" \
        -e ORTHANC__CONFIGURATION__FILE=/etc/orthanc/orthanc.json \
        "$DOCKER_IMAGE"
    
    if [ $? -eq 0 ]; then
        print_success "Orthanc container started successfully"
        # Clean up the config file since it's now mounted in the container
        rm -f "$config_file"
        # Store the volume path for cleanup
        echo "$sample_data_volume" > /tmp/orthanc_volume_path
    else
        print_error "Failed to start Orthanc container"
        rm -f "$config_file"
        rm -rf "$sample_data_volume"
        exit 1
    fi
}

# Function to wait for Orthanc to be ready
wait_for_orthanc() {
    print_status "Waiting for Orthanc to be ready..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        # Test basic connectivity with authentication
        if curl -s -f -u orthanc:orthanc "http://localhost:$ORTHANC_PORT/" > /dev/null 2>&1; then
            print_success "Orthanc is ready and responding!"
            return 0
        fi
        
        # Also test DICOMweb endpoint for more comprehensive check
        if curl -s -f -u orthanc:orthanc "http://localhost:$ORTHANC_PORT/dicom-web/studies" > /dev/null 2>&1; then
            print_success "Orthanc DICOMweb endpoint is ready!"
            return 0
        fi
        
        print_status "Attempt $attempt/$max_attempts - Orthanc not ready yet, waiting..."
        sleep 2
        ((attempt++))
    done
    
    print_error "Orthanc failed to start within expected time"
    print_status "Checking container status..."
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep dicomweb-test-orthanc || true
    return 1
}

# Function to load sample DICOM data
load_sample_data() {
    print_status "Loading comprehensive DICOM test data..."
    
    # Give Orthanc more time to fully initialize
    sleep 5
    
    # First, try to load existing sample data files
    local loaded_count=0
    if [ -d "$SAMPLE_DATA_DIR" ]; then
        for dcm_file in "$SAMPLE_DATA_DIR"/*.dcm; do
            if [ -f "$dcm_file" ]; then
                print_status "Loading DICOM file: $(basename "$dcm_file")"
                # Try multiple content types for STOW-RS compatibility
                local response=$(curl -s -w "%{http_code}" -X POST "http://localhost:$ORTHANC_PORT/instances" \
                    --data-binary @"$dcm_file" \
                    -u "orthanc:orthanc" \
                    -H "Content-Type: application/dicom" \
                    -H "Accept: application/dicom+json" 2>/dev/null || echo "000")
                
                local status_code="${response: -3}"
                if [ "$status_code" = "200" ] || [ "$status_code" = "201" ]; then
                    ((loaded_count++))
                    print_success "Successfully loaded $(basename "$dcm_file")"
                else
                    print_warning "Failed to load $(basename "$dcm_file") (HTTP $status_code)"
                fi
            fi
        done
    fi
    
    # If no existing files, generate synthetic DICOM data
    if [ $loaded_count -eq 0 ]; then
        print_status "No existing DICOM files found, generating synthetic test data..."
        generate_synthetic_dicom_data
    fi
    
    # Wait for data to be processed and indexed
    sleep 3
    
    # Verify data was loaded by checking studies count
    local studies_response=$(curl -s "http://localhost:$ORTHANC_PORT/dicom-web/studies" -u "orthanc:orthanc" 2>/dev/null || echo "[]")
    local studies_count=$(echo "$studies_response" | python -c "import json,sys; data=json.load(sys.stdin); print(len(data))" 2>/dev/null || echo "0")
    
    if [ "$studies_count" -gt 0 ]; then
        print_success "Sample data loading completed - $studies_count studies available for testing"
    else
        print_warning "Sample data loading completed but no studies found - WADO-RS tests will be limited"
    fi
}

# Function to generate synthetic DICOM data for testing
generate_synthetic_dicom_data() {
    print_status "Generating synthetic DICOM test data..."
    
    # Create a temporary Python script to generate DICOM data
    local temp_script="/tmp/generate_dicom.py"
    
    cat > "$temp_script" << 'EOF'
#!/usr/bin/env python3
import pydicom
import numpy as np
from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import ImplicitVRLittleEndian, generate_uid
import datetime
import os

def create_sample_dicom(modality="CT", patient_name="Test^Patient", patient_id="TEST001"):
    """Create a sample DICOM file with proper metadata."""
    # Create dataset
    ds = Dataset()
    ds.file_meta = Dataset()
    ds.file_meta.TransferSyntaxUID = ImplicitVRLittleEndian
    
    # Set SOP Class based on modality
    sop_classes = {
        "CT": "1.2.840.10008.5.1.4.1.1.2",      # CT Image Storage
        "MR": "1.2.840.10008.5.1.4.1.1.4",      # MR Image Storage
        "CR": "1.2.840.10008.5.1.4.1.1.1",      # Computed Radiography
        "US": "1.2.840.10008.5.1.4.1.1.6.1",    # Ultrasound Image Storage
    }
    
    sop_class = sop_classes.get(modality, sop_classes["CT"])
    ds.file_meta.MediaStorageSOPClassUID = sop_class
    ds.file_meta.MediaStorageSOPInstanceUID = generate_uid()
    ds.file_meta.ImplementationClassUID = "1.2.3.4.5.6.7.8.9"
    
    # Generate unique UIDs
    study_uid = generate_uid()
    series_uid = generate_uid()
    instance_uid = generate_uid()
    
    # Patient information
    ds.PatientName = patient_name
    ds.PatientID = patient_id
    ds.PatientBirthDate = "19850101"
    ds.PatientSex = "M" if patient_name.endswith("^M") else "F"
    
    # Study information
    ds.StudyInstanceUID = study_uid
    ds.StudyDate = "20230101"
    ds.StudyTime = "120000"
    ds.AccessionNumber = f"ACC_{patient_id}"
    ds.StudyID = f"STUDY_{patient_id}"
    ds.StudyDescription = f"{modality} Test Study"
    
    # Series information
    ds.SeriesInstanceUID = series_uid
    ds.SeriesNumber = 1
    ds.Modality = modality
    ds.SeriesDate = "20230101"
    ds.SeriesTime = "120000"
    ds.SeriesDescription = f"{modality} Series 1"
    
    # Instance information
    ds.SOPInstanceUID = instance_uid
    ds.SOPClassUID = sop_class
    ds.InstanceNumber = 1
    
    # Image information (vary based on modality)
    if modality in ["CT", "MR"]:
        rows, cols = 512, 512
    elif modality == "CR":
        rows, cols = 1024, 1024
    else:  # US
        rows, cols = 800, 600
    
    ds.Rows = rows
    ds.Columns = cols
    ds.BitsAllocated = 16
    ds.BitsStored = 16
    ds.HighBit = 15
    ds.PixelRepresentation = 0
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    
    # Create pixel data
    if modality == "CT":
        # CT uses Hounsfield units (-1000 to +3000)
        ds.PixelData = np.random.randint(0, 4096, (rows, cols), dtype=np.uint16).tobytes()
        ds.WindowCenter = "40"
        ds.WindowWidth = "400"
    elif modality == "MR":
        # MR uses arbitrary units
        ds.PixelData = np.random.randint(0, 256, (rows, cols), dtype=np.uint16).tobytes()
    else:
        # X-ray and ultrasound
        ds.PixelData = np.random.randint(0, 4096, (rows, cols), dtype=np.uint16).tobytes()
    
    return ds

def main():
    """Generate multiple DICOM files for testing."""
    print("Generating DICOM test files...")
    
    # Create test data directory
    test_dir = "/tmp/orthanc_test_data"
    os.makedirs(test_dir, exist_ok=True)
    
    # Generate different types of DICOM files
    test_cases = [
        ("CT", "Test^CTPatient", "CT001"),
        ("MR", "Test^MRPatient", "MR001"),
        ("CR", "Test^XRayPatient", "CR001"),
        ("US", "Test^USPatient", "US001"),
    ]
    
    for modality, patient_name, patient_id in test_cases:
        try:
            ds = create_sample_dicom(modality, patient_name, patient_id)
            filename = f"{test_dir}/sample_{modality.lower()}_{patient_id}.dcm"
            ds.save_as(filename)
            print(f"Generated: {filename}")
        except Exception as e:
            print(f"Error generating {modality} file: {e}")
    
    print("DICOM generation complete")

if __name__ == "__main__":
    main()
EOF

    # Run the script and capture output
    if python "$temp_script"; then
        print_status "Synthetic DICOM files generated successfully"
        
        # Now upload the generated files
        local uploaded_count=0
        for dcm_file in /tmp/orthanc_test_data/*.dcm; do
            if [ -f "$dcm_file" ]; then
                print_status "Uploading generated file: $(basename "$dcm_file")"
                # Try Orthanc's DICOMweb STOW endpoint with different content types
                local response=$(curl -s -w "%{http_code}" -X POST "http://localhost:$ORTHANC_PORT/dicom-web/studies" \
                    --data-binary @"$dcm_file" \
                    -H "Content-Type: application/dicom" \
                    -u "orthanc:orthanc" 2>/dev/null || echo "000")
                
                local status_code="${response: -3}"
                if [ "$status_code" = "200" ] || [ "$status_code" = "201" ]; then
                    ((uploaded_count++))
                    print_success "Successfully uploaded $(basename "$dcm_file")"
                else
                    # Try alternative upload method via instances endpoint
                    local alt_response=$(curl -s -w "%{http_code}" -X POST "http://localhost:$ORTHANC_PORT/instances" \
                        --data-binary @"$dcm_file" \
                        -H "Content-Type: application/dicom" \
                        -u "orthanc:orthanc" 2>/dev/null || echo "000")
                    
                    local alt_status="${alt_response: -3}"
                    if [ "$alt_status" = "200" ] || [ "$alt_status" = "201" ]; then
                        ((uploaded_count++))
                        print_success "Successfully uploaded $(basename "$dcm_file") via instances endpoint"
                    else
                        print_warning "Failed to upload $(basename "$dcm_file") (HTTP $alt_status)"
                    fi
                fi
            fi
        done
        
        print_status "Uploaded $uploaded_count synthetic DICOM files"
    else
        print_warning "Failed to generate synthetic DICOM files"
    fi
    
    # Clean up
    rm -f "$temp_script"
    rm -rf /tmp/orthanc_test_data
}

# Function to check Python dependencies
check_dependencies() {
    print_status "Checking Python dependencies..."
    
    if ! command -v python &> /dev/null; then
        print_error "Python is not installed or not in PATH"
        exit 1
    fi
    
    # Check if required packages are installed
    python -c "import requests, pydicom, pytest, colorama, tabulate" 2>/dev/null
    if [ $? -ne 0 ]; then
        print_warning "Some Python dependencies are missing"
        print_status "Installing dependencies from requirements.txt..."
        pip install -r requirements.txt
        if [ $? -ne 0 ]; then
            print_error "Failed to install dependencies"
            exit 1
        fi
    fi
    
    print_success "Python dependencies are available"
}

# Function to test Orthanc DICOMweb endpoints
test_orthanc_endpoints() {
    print_status "Testing Orthanc DICOMweb endpoints..."
    
    # Test basic connectivity
    local status_code=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$ORTHANC_PORT/" || echo "000")
    if [ "$status_code" = "200" ]; then
        print_success "Orthanc web interface is accessible"
    else
        print_error "Orthanc web interface is not accessible (HTTP $status_code)"
        return 1
    fi
    
    # Test DICOMweb QIDO-RS endpoint
    status_code=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$ORTHANC_PORT/dicom-web/studies" || echo "000")
    if [ "$status_code" = "200" ]; then
        print_success "DICOMweb QIDO-RS endpoint is accessible"
    else
        print_warning "DICOMweb QIDO-RS endpoint returned HTTP $status_code"
    fi
    
    # Test DICOMweb WADO-RS endpoint
    status_code=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$ORTHANC_PORT/dicom-web/instances" || echo "000")
    if [ "$status_code" = "200" ]; then
        print_success "DICOMweb WADO-RS endpoint is accessible"
    else
        print_warning "DICOMweb WADO-RS endpoint returned HTTP $status_code"
    fi
    
    # Test authentication
    status_code=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$ORTHANC_PORT/dicom-web/studies" -u "orthanc:orthanc" || echo "000")
    if [ "$status_code" = "200" ]; then
        print_success "DICOMweb authentication is working"
    else
        print_warning "DICOMweb authentication returned HTTP $status_code"
    fi
    
    # Check if we have any studies to work with
    local studies_response=$(curl -s "http://localhost:$ORTHANC_PORT/dicom-web/studies" -u "orthanc:orthanc" || echo "[]")
    local studies_count=$(echo "$studies_response" | python -c "import json,sys; data=json.load(sys.stdin); print(len(data))" 2>/dev/null || echo "0")
    
    if [ "$studies_count" -gt 0 ]; then
        print_success "Found $studies_count studies for testing"
    else
        print_warning "No studies found - tests may have limited success"
    fi
    
    return 0
}

# Function to run the DICOMweb test suite
run_test_suite() {
    print_status "Running DICOMweb Conformance Test Suite..."
    
    # Set the PACS URL for Orthanc DICOMweb
    local pacs_url="http://localhost:$ORTHANC_PORT/dicom-web/"
    
    # Run tests with authentication
    print_status "Executing: python run_tests.py --pacs-url $pacs_url --username orthanc --password orthanc --html --verbose"
    
    if python run_tests.py --pacs-url "$pacs_url" --username orthanc --password orthanc --html --verbose; then
        print_success "Test suite completed successfully!"
        return 0
    else
        local exit_code=$?
        print_warning "Test suite completed with some failures (exit code: $exit_code)"
        return $exit_code
    fi
}

# Function to display test results
show_results() {
    print_status "Looking for generated test reports..."
    
    # Look for any generated report files
    local report_files=($(find . -maxdepth 1 -name "dicomweb_conformance_*.txt" -o -name "dicomweb_conformance_*.json" -o -name "dicomweb_conformance_*.html" | sort))
    
    if [ ${#report_files[@]} -gt 0 ]; then
        print_success "Generated report files:"
        for file in "${report_files[@]}"; do
            print_status "  - $file"
        done
        
        # Show the most recent text report content
        local latest_text_report=$(ls -t dicomweb_conformance_*.txt 2>/dev/null | head -n1)
        if [ -n "$latest_text_report" ]; then
            print_status "Contents of the latest text report:"
            echo "=========================================="
            cat "$latest_text_report"
            echo "=========================================="
        fi
    else
        print_warning "No report files found"
    fi
}

# Function to check system resources (simplified for Windows)
check_resources() {
    print_status "Checking system resources..."
    
    # Check available disk space (require at least 1GB)
    local available_space=$(df -BG . 2>/dev/null | awk 'NR==2 {print $4}' | sed 's/G//' || echo "100")
    if [ "$available_space" -lt 1 ]; then
        print_warning "Low disk space detected: ${available_space}GB available"
    else
        print_success "Sufficient disk space: ${available_space}GB available"
    fi
    
    # Skip memory check on Windows systems
    print_success "Memory check skipped (Windows system)"
}

# Function to generate summary
generate_summary() {
    local test_result=$1
    local total_time=$2
    
    echo
    echo "=========================================="
    echo "    ENHANCED DOCKER TEST SUITE SUMMARY    "
    echo "=========================================="
    echo "Total execution time: ${total_time}s"
    echo "Test result: $([ $test_result -eq 0 ] && echo "PASS" || echo "NEEDS INVESTIGATION")"
    echo "Orthanc container: $ORTHANC_CONTAINER_NAME"
    echo "DICOMweb URL: http://localhost:$ORTHANC_PORT/dicom-web/"
    echo "Web interface: http://localhost:$ORTHANC_PORT/"
    echo "Credentials: orthanc / orthanc"
    echo "=========================================="
    
    if [ $test_result -eq 0 ]; then
        print_success "Docker test suite completed successfully!"
        print_status "You can access Orthanc at: http://localhost:$ORTHANC_PORT/"
        print_status "DICOMweb endpoint: http://localhost:$ORTHANC_PORT/dicom-web/"
        print_status "Username: orthanc, Password: orthanc"
    else
        print_warning "Docker test suite completed - results require investigation"
        print_status "Check the generated reports for detailed analysis"
        print_status "Note: Some failures may be expected with minimal test data"
    fi
}

# Function to cleanup on exit
cleanup() {
    local exit_code=$?
    
    print_status "Cleaning up..."
    
    if docker ps --format "table {{.Names}}" | grep -q "^${ORTHANC_CONTAINER_NAME}$"; then
        print_status "Stopping Orthanc container..."
        docker stop "$ORTHANC_CONTAINER_NAME" &> /dev/null || true
        print_success "Orthanc container stopped"
    fi
    
    # Clean up temporary volume if it exists
    if [ -f /tmp/orthanc_volume_path ]; then
        local volume_path=$(cat /tmp/orthanc_volume_path)
        rm -rf "$volume_path" 2>/dev/null || true
        rm -f /tmp/orthanc_volume_path
    fi
    
    # Calculate total time
    local total_time=$((SECONDS))
    
    generate_summary $exit_code $total_time
    
    exit $exit_code
}

# Set up cleanup on script exit
trap cleanup EXIT INT TERM

# Main execution
main() {
    local start_time=$SECONDS
    
    echo "=========================================="
    echo "  DICOMWEB CONFORMANCE TEST SUITE"
    echo "  Enhanced Docker Testing Script"
    echo "=========================================="
    echo
    echo "This script will:"
    echo "• Start a properly configured Orthanc instance"
    echo "• Enable DICOMweb support with authentication"
    echo "• Load sample DICOM data for testing"
    echo "• Run the complete DICOMweb test suite"
    echo "• Generate comprehensive reports"
    echo
    
    # Check prerequisites
    check_docker
    check_dependencies
    check_resources
    
    # Setup Orthanc
    cleanup_existing
    start_orthanc
    wait_for_orthanc
    
    # Load sample data
    load_sample_data
    
    # Test Orthanc functionality
    test_orthanc_endpoints
    
    # Run the test suite
    run_test_suite
    local test_result=$?
    
    # Show results
    show_results
    
    # Cleanup will be handled by the trap
    return $test_result
}

# Parse command line arguments
case "${1:-}" in
    --help|-h)
        echo "DICOMweb Conformance Test Suite - Enhanced Docker Testing"
        echo
        echo "Usage: $0 [options]"
        echo
        echo "Options:"
        echo "  --help, -h        Show this help message"
        echo "  --no-cleanup      Don't stop the Orthanc container after testing"
        echo "  --keep-running    Keep Orthanc running after tests complete"
        echo
        echo "This enhanced script will:"
        echo "1. Start a properly configured Orthanc instance with DICOMweb support"
        echo "2. Enable authentication (orthanc/orthanc)"
        echo "3. Load sample DICOM data for testing"
        echo "4. Run the complete DICOMweb test suite with authentication"
        echo "5. Generate comprehensive reports"
        echo "6. Clean up resources"
        echo
        exit 0
        ;;
    --no-cleanup)
        print_status "Running with --no-cleanup - Orthanc will remain running"
        trap '' EXIT  # Disable cleanup trap
        ;;
    --keep-running)
        print_status "Running with --keep-running - Orthanc will remain running"
        trap '' EXIT  # Disable cleanup trap
        ;;
    "")
        # No arguments, run normally
        ;;
    *)
        print_error "Unknown option: $1"
        print_status "Use --help for usage information"
        exit 1
        ;;
esac

# Run main function
main "$@"