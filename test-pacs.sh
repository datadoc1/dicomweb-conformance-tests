#!/bin/bash

# DICOMweb PACS Testing Script
# One-click solution for PACS administrators to test DICOMweb compliance
# Usage: ./test-pacs.sh [PACS_URL] [--email]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
PACS_URL=""
SEND_EMAIL=false
INTERACTIVE=true

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

# Function to check if Python is available
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        print_error "Python not found. Please install Python 3.8 or higher."
        exit 1
    fi
    
    print_status "Using Python: $($PYTHON_CMD --version)"
}

# Function to install dependencies
install_dependencies() {
    print_status "Installing dependencies..."
    
    if [ -f "requirements.txt" ]; then
        $PYTHON_CMD -m pip install -r requirements.txt
        print_success "Dependencies installed successfully"
    else
        print_error "requirements.txt not found. Please ensure you're in the correct directory."
        exit 1
    fi
}

# Function to validate PACS URL
validate_pacs_url() {
    local url="$1"
    
    if [ -z "$url" ]; then
        return 1
    fi
    
    # Check if URL starts with http:// or https://
    if [[ ! "$url" =~ ^https?:// ]]; then
        print_warning "URL should start with http:// or https://"
        return 1
    fi
    
    return 0
}

# Function to test URL connectivity
test_url() {
    local url="$1"
    
    print_status "Testing connectivity to: $url"
    
    # Test basic connectivity
    if curl -s --max-time 10 "$url" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to auto-discover DICOMweb endpoint
discover_endpoint() {
    local base_url="$1"
    local endpoints=("dicomweb" "dicom-web" "wado" "dicom" "api/dicomweb" "api/dicom-web")
    
    for endpoint in "${endpoints[@]}"; do
        local full_url="${base_url%/}/${endpoint}"
        print_status "Trying endpoint: $full_url"
        
        if test_url "$full_url"; then
            print_success "Found working endpoint: $full_url"
            echo "$full_url"
            return 0
        fi
    done
    
    return 1
}

# Function to run DICOMweb tests
run_tests() {
    local url="$1"
    
    print_status "Running DICOMweb conformance tests..."
    
    # Create output directory
    mkdir -p test_results
    
    # Run the test suite
    $PYTHON_CMD run_tests.py \
        --pacs-url "$url" \
        --output-format both \
        --output-file "test_results/dicomweb_conformance_$(date +%Y%m%d_%H%M%S)" \
        --verbose
    
    if [ $? -eq 0 ]; then
        print_success "Tests completed successfully!"
        return 0
    else
        print_error "Tests failed. Check the logs for details."
        return 1
    fi
}

# Function to generate vendor email
generate_email() {
    local test_results_file="$1"
    local pacs_url="$2"
    
    print_status "Generating vendor email template..."
    
    # Find the most recent test results
    local latest_text=$(ls -t test_results/dicomweb_conformance_*.txt 2>/dev/null | head -1)
    local latest_json=$(ls -t test_results/dicomweb_conformance_*.json 2>/dev/null | head -1)
    
    if [ -z "$latest_text" ] || [ -z "$latest_json" ]; then
        print_error "No test results found. Please run tests first."
        return 1
    fi
    
    # Extract key information
    local report_date=$(date +"%B %d, %Y")
    local compliance_score=$(grep -o "Compliance Score: [0-9.]*%" "$latest_text" | cut -d' ' -f3)
    local conformance_level=$(grep -o "Conformance Level: [A-Z_]*" "$latest_text" | cut -d' ' -f3)
    
    # Create email template
    cat > vendor_email_template.txt << EOF
Subject: DICOMweb Compliance Assessment Results for $pacs_url

Dear [PACS Vendor Name],

I hope this message finds you well. I am writing to share the results of a comprehensive DICOMweb compliance assessment conducted on $(date +"%B %d, %Y") for our PACS system at $pacs_url.

## Assessment Overview

We recently conducted a thorough evaluation of our PACS system's DICOMweb implementation using industry-standard testing tools. This assessment evaluated all three core DICOMweb protocols:

• QIDO-RS (Query Based on ID with RESTful Services) - 17 tests
• WADO-RS (Web Access to DICOM Objects via RESTful Services) - 18 tests  
• STOW-RS (Store Over The Web with RESTful Services) - 18 tests

## Key Findings

**Overall Compliance Score:** $compliance_score
**Conformance Level:** $conformance_level

Our assessment identified several areas where your DICOMweb implementation excels, as well as some opportunities for improvement to ensure full compliance with DICOMweb standards.

## Attached Documentation

Please find the following documents attached:
• Detailed test results in JSON format
• Human-readable conformance report
• Technical recommendations for improvements

## Next Steps

We would appreciate the opportunity to discuss these findings with your technical team. Specifically, we would like to understand:

1. Your timeline for addressing any non-compliant areas
2. Whether updates to our current implementation would resolve these issues
3. What support you can provide to ensure full DICOMweb compliance

## Business Impact

As you know, DICOMweb compliance is increasingly important for:
• Interoperability with modern healthcare systems
• Integration with AI/ML imaging workflows
• Meeting regulatory and security requirements
• Supporting telemedicine and remote diagnostics
• Enabling research collaborations and data sharing

We value our partnership and look forward to working together to ensure our PACS system meets the highest standards for DICOMweb compliance.

## Contact Information

Please direct your response to:
Name: [Your Name]
Title: [Your Title]
Department: [Your Department]
Phone: [Your Phone]
Email: [Your Email]

We are available to discuss these findings at your convenience and appreciate your prompt attention to this matter.

Thank you for your continued support.

Best regards,

[Your Name]
[Your Title]
[Your Organization]
[Date: $report_date]

---
PACS URL Tested: $pacs_url
Test Suite Version: DICOMweb Conformance Test Suite v1.0.0
Test Date: $report_date
EOF

    print_success "Email template generated: vendor_email_template.txt"
    print_status "The email template is ready to be customized with your specific details and sent to your PACS vendor."
}

# Function to show usage
show_usage() {
    echo "DICOMweb PACS Testing Script"
    echo ""
    echo "Usage: $0 [OPTIONS] [PACS_URL]"
    echo ""
    echo "Options:"
    echo "  -h, --help          Show this help message"
    echo "  --email             Generate vendor email template after tests"
    echo "  --no-interactive    Run in non-interactive mode"
    echo ""
    echo "Arguments:"
    echo "  PACS_URL           Base URL of your PACS server (optional, will prompt if not provided)"
    echo ""
    echo "Examples:"
    echo "  $0                              # Interactive mode"
    echo "  $0 https://pacs.example.com    # Test specific PACS"
    echo "  $0 --email https://pacs.example.com  # Test and generate email"
    echo ""
    echo "For more information, see README.md"
}

# Main execution starts here
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}DICOMweb PACS Compliance Test Suite${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        --email)
            SEND_EMAIL=true
            shift
            ;;
        --no-interactive)
            INTERACTIVE=false
            shift
            ;;
        -*)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
        *)
            if [ -z "$PACS_URL" ]; then
                PACS_URL="$1"
            else
                print_error "Multiple PACS URLs provided"
                exit 1
            fi
            shift
            ;;
    esac
done

# Check dependencies
check_python

# Install dependencies if needed
print_status "Checking dependencies..."
if ! $PYTHON_CMD -c "import requests, pydicom" 2>/dev/null; then
    install_dependencies
else
    print_success "Dependencies already installed"
fi

# Get PACS URL (interactive or from argument)
if [ -z "$PACS_URL" ] && [ "$INTERACTIVE" = true ]; then
    echo ""
    print_status "Please provide your PACS server URL"
    echo -n "PACS URL (e.g., https://pacs.example.com or https://pacs.example.com/dicomweb): "
    read -r PACS_URL
fi

if [ -z "$PACS_URL" ]; then
    print_error "No PACS URL provided"
    show_usage
    exit 1
fi

# Clean up URL
PACS_URL=$(echo "$PACS_URL" | sed 's:/*$::')

# Validate URL
if ! validate_pacs_url "$PACS_URL"; then
    print_error "Invalid PACS URL format. Please use http:// or https://"
    exit 1
fi

# Auto-discover DICOMweb endpoint if needed
if [[ ! "$PACS_URL" =~ dicomweb|dicom-web|wado|dicom|api/dicom ]]; then
    print_status "Auto-discovering DICOMweb endpoint..."
    DISCOVERED_URL=$(discover_endpoint "$PACS_URL")
    if [ $? -eq 0 ]; then
        PACS_URL="$DISCOVERED_URL"
    else
        print_warning "Could not auto-discover endpoint. Using: $PACS_URL"
    fi
fi

# Test connectivity
print_status "Testing PACS connectivity..."
if test_url "$PACS_URL"; then
    print_success "PACS server is accessible"
else
    print_error "Cannot connect to PACS server. Please check the URL and network connectivity."
    exit 1
fi

echo ""
print_status "Ready to test PACS at: $PACS_URL"
if [ "$INTERACTIVE" = true ]; then
    echo -n "Proceed with testing? (y/n): "
    read -r proceed
    if [[ ! "$proceed" =~ ^[Yy]$ ]]; then
        print_status "Testing cancelled by user"
        exit 0
    fi
fi

echo ""

# Run tests
if run_tests "$PACS_URL"; then
    print_success "DICOMweb compliance testing completed!"
    
    if [ "$SEND_EMAIL" = true ]; then
        echo ""
        generate_email "" "$PACS_URL"
    fi
    
    echo ""
    print_status "Results are available in the test_results/ directory"
    print_status "You can now review the reports and share them with your PACS vendor"
    
else
    print_error "Testing failed. Please check the error messages above."
    exit 1
fi

echo ""
print_success "Thank you for using the DICOMweb Conformance Test Suite!"