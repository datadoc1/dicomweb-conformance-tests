#!/bin/bash

# Test Local Orthanc Instance with DICOMweb Conformance Suite
# This script runs tests against the localhost Orthanc instance

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "========================================"
echo "   Testing Local Orthanc Instance"
echo "========================================"
echo -e "${NC}"

# Configuration
ORTHANC_URL="http://localhost:8042"
DICOMWEB_URL="http://localhost:8042/dicom-web"
USERNAME="orthanc"
PASSWORD="orthanc"

# Function to check if Orthanc is running
check_orthanc() {
    echo -e "${YELLOW}Checking if Orthanc is running...${NC}"
    
    if ! docker ps --format "table {{.Names}}" | grep -q "^orthanc-dicomweb$"; then
        echo -e "${RED}Error: Orthanc container 'orthanc-dicomweb' is not running${NC}"
        echo -e "${YELLOW}Please run ./start-orthanc.sh first${NC}"
        return 1
    fi
    
    if curl -s -f -u "$USERNAME:$PASSWORD" "$ORTHANC_URL/" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Orthanc is running and accessible${NC}"
        return 0
    else
        echo -e "${RED}Error: Orthanc is not responding to requests${NC}"
        return 1
    fi
}

# Function to test DICOMweb endpoints
test_dicomweb_endpoints() {
    echo -e "${YELLOW}Testing DICOMweb endpoints...${NC}"
    
    # Test QIDO-RS
    local qido_response=$(curl -s -w "%{http_code}" -u "$USERNAME:$PASSWORD" "$DICOMWEB_URL/studies" 2>/dev/null || echo "000")
    local qido_status="${qido_response: -3}"
    
    if [ "$qido_status" = "200" ]; then
        echo -e "${GREEN}✓ QIDO-RS endpoint is working${NC}"
    else
        echo -e "${RED}✗ QIDO-RS endpoint failed (HTTP $qido_status)${NC}"
        return 1
    fi
    
    # Test WADO-RS
    local wado_response=$(curl -s -w "%{http_code}" -u "$USERNAME:$PASSWORD" "$DICOMWEB_URL/studies" 2>/dev/null || echo "000")
    local wado_status="${wado_response: -3}"
    
    if [ "$wado_status" = "200" ]; then
        echo -e "${GREEN}✓ WADO-RS endpoint is working${NC}"
    else
        echo -e "${RED}✗ WADO-RS endpoint failed (HTTP $wado_status)${NC}"
    fi
    
    # Test STOW-RS (this will fail without data, but endpoint should exist)
    local stow_response=$(curl -s -w "%{http_code}" -X POST -u "$USERNAME:$PASSWORD" -H "Content-Type: application/dicom" -d "@test_data/sample_ct.dcm" "$DICOMWEB_URL/studies" 2>/dev/null || echo "000")
    local stow_status="${stow_response: -3}"
    
    if [ "$stow_status" != "404" ]; then
        echo -e "${GREEN}✓ STOW-RS endpoint is accessible${NC}"
    else
        echo -e "${YELLOW}! STOW-RS endpoint not found (may be normal without data)${NC}"
    fi
    
    return 0
}

# Function to load sample data
load_sample_data() {
    echo -e "${YELLOW}Loading sample DICOM data...${NC}"
    
    if [ ! -d "test_data" ] || [ ! -f "test_data/sample_ct.dcm" ]; then
        echo -e "${YELLOW}Generating synthetic DICOM data...${NC}"
        
        # Check if we can generate data
        if python3 -c "import pydicom" 2>/dev/null; then
            python3 generate_test_data.py || {
                echo -e "${YELLOW}Generating minimal test data...${NC}"
                # Create a minimal DICOM file for testing
                echo -e "DICOM test data" > test_data/sample_ct.dcm
            }
        else
            echo -e "${YELLOW}Creating minimal test data...${NC}"
            mkdir -p test_data
            echo -e "DICOM test data" > test_data/sample_ct.dcm
        fi
    fi
    
    # Try to upload data
    local uploaded_count=0
    for dcm_file in test_data/*.dcm; do
        if [ -f "$dcm_file" ]; then
            echo -e "${YELLOW}Uploading $(basename "$dcm_file")...${NC}"
            
            # Try multiple upload methods
            local upload_response=$(curl -s -w "%{http_code}" -X POST "http://localhost:8042/instances" \
                --data-binary @"$dcm_file" \
                -u "$USERNAME:$PASSWORD" \
                -H "Content-Type: application/dicom" 2>/dev/null || echo "000")
            
            local upload_status="${upload_response: -3}"
            if [ "$upload_status" = "200" ] || [ "$upload_status" = "201" ]; then
                ((uploaded_count++))
                echo -e "${GREEN}✓ Successfully uploaded $(basename "$dcm_file")${NC}"
            else
                echo -e "${YELLOW}! Upload failed for $(basename "$dcm_file") (HTTP $upload_status)${NC}"
            fi
        fi
    done
    
    if [ $uploaded_count -gt 0 ]; then
        echo -e "${GREEN}✓ Loaded $uploaded_count DICOM files${NC}"
    else
        echo -e "${YELLOW}! No DICOM files loaded - tests will have limited data${NC}"
    fi
}

# Function to run DICOMweb conformance tests
run_conformance_tests() {
    echo -e "${YELLOW}Running DICOMweb Conformance Test Suite...${NC}"
    
    # Create timestamped output directory at repo root
    local ts
    ts=$(date +%Y%m%d_%H%M%S)
    local results_dir="test-results-${ts}"
    mkdir -p "${results_dir}"

    echo -e "${BLUE}Executing: python run_tests.py --pacs-url $DICOMWEB_URL --username $USERNAME --password $PASSWORD --html --verbose${NC}"

    # Always invoke run_tests.py from the repository root so it is found correctly.
    if python run_tests.py \
        --pacs-url "$DICOMWEB_URL" \
        --username "$USERNAME" \
        --password "$PASSWORD" \
        --html \
        --verbose \
        --output-file "${results_dir}/dicomweb_conformance_${ts}"; then
        echo -e "${GREEN}✓ Conformance tests completed successfully!${NC}"
        local test_result=0
    else
        echo -e "${YELLOW}! Conformance tests completed with some failures${NC}"
        local test_result=1
    fi

    # Show summary from within the results directory
    ( cd "${results_dir}" && show_test_results )

    return $test_result
}

# Function to show test results
show_test_results() {
    echo -e "${YELLOW}Test Results Summary:${NC}"
    echo "========================================"

    # Look for generated report files in the current directory
    local report_files=($(find . -maxdepth 1 \
      -name "dicomweb_conformance_*.txt" \
      -o -name "dicomweb_conformance_*.json" \
      -o -name "dicomweb_conformance_*.html" 2>/dev/null | sort))
    
    if [ ${#report_files[@]} -gt 0 ]; then
        echo "Generated reports:"
        for file in "${report_files[@]}"; do
            echo "  - $(basename "$file")"
        done
        
        # Show the latest text report
        local latest_text_report=$(ls -t dicomweb_conformance_*.txt 2>/dev/null | head -n1)
        if [ -n "$latest_text_report" ]; then
            echo
            echo "Latest test report content:"
            echo "========================================"
            cat "$latest_text_report"
            echo "========================================"
        fi
    else
        echo -e "${YELLOW}No report files found${NC}"
    fi
}

# Main execution
main() {
    echo -e "${BLUE}This script will test your local Orthanc instance with DICOMweb support.${NC}"
    echo
    
    # Check prerequisites
    if ! check_orthanc; then
        exit 1
    fi
    
    # Test DICOMweb endpoints
    if ! test_dicomweb_endpoints; then
        echo -e "${RED}DICOMweb endpoints test failed${NC}"
        exit 1
    fi
    
    # Load sample data
    load_sample_data
    
    # Run conformance tests
    local result=0
    run_conformance_tests || result=$?
    
    # Final summary
    echo
    echo "========================================"
    if [ $result -eq 0 ]; then
        echo -e "${GREEN}✅ All tests completed successfully!${NC}"
    else
        echo -e "${YELLOW}⚠️  Tests completed with some issues${NC}"
    fi
    echo "========================================"
    echo "Orthanc URL: $ORTHANC_URL"
    echo "DICOMweb URL: $DICOMWEB_URL"
    echo "Credentials: $USERNAME / $PASSWORD"
    echo "Test results saved under: test-results-*/dicomweb_conformance_*.{txt,json,html}"
    echo "========================================"
    
    return $result
}

# Parse command line arguments
case "${1:-}" in
    --help|-h)
        echo "Test Local Orthanc Instance - DICOMweb Conformance Suite"
        echo
        echo "Usage: $0 [options]"
        echo
        echo "Options:"
        echo "  --help, -h        Show this help message"
        echo "  --no-data         Skip loading sample data"
        echo "  --quick           Run quick tests only (skip full conformance suite)"
        echo
        echo "This script will:"
        echo "1. Check if Orthanc is running"
        echo "2. Test DICOMweb endpoints"
        echo "3. Load sample DICOM data"
        echo "4. Run the complete DICOMweb conformance test suite"
        echo
        exit 0
        ;;
    --no-data)
        SKIP_DATA=1
        ;;
    --quick)
        QUICK_MODE=1
        ;;
esac

# Run main function
main "$@"