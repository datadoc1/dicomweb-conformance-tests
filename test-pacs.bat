@echo off
REM DICOMweb PACS Testing Script for Windows
REM One-click solution for PACS administrators to test DICOMweb compliance
REM Usage: test-pacs.bat [PACS_URL] [--email]

setlocal enabledelayedexpansion

set "RED="
set "GREEN="  
set "YELLOW="
set "BLUE="
set "NC="

REM Check if Python is available
python --version >nul 2>&1
if !errorlevel! neq 0 (
    echo [ERROR] Python not found. Please install Python 3.8 or higher.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [INFO] Using Python:
python --version

REM Install dependencies if needed
echo [INFO] Checking dependencies...
python -c "import requests, pydicom" >nul 2>&1
if !errorlevel! neq 0 (
    echo [INFO] Installing dependencies...
    python -m pip install -r requirements.txt
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
    echo [SUCCESS] Dependencies installed successfully
) else (
    echo [SUCCESS] Dependencies already installed
)

REM Parse command line arguments
set "PACS_URL="
set "SEND_EMAIL=false"

:parse_args
if "%~1"=="" goto :args_done
if "%~1"=="--email" (
    set "SEND_EMAIL=true"
    shift
    goto :parse_args
)
if "%~1"=="--help" (
    call :show_usage
    exit /b 0
)
if "%~1"=="-h" (
    call :show_usage
    exit /b 0
)
if "%~1" neq "" (
    if "!PACS_URL!"=="" (
        set "PACS_URL=%~1"
    )
)
shift
goto :parse_args

:args_done

REM Get PACS URL if not provided
if "!PACS_URL!"=="" (
    echo.
    echo [INFO] Please provide your PACS server URL
    set /p "PACS_URL=PACS URL (e.g., https://pacs.example.com or https://pacs.example.com/dicomweb): "
)

if "!PACS_URL!"=="" (
    echo [ERROR] No PACS URL provided
    call :show_usage
    pause
    exit /b 1
)

REM Clean up URL
set "PACS_URL=!PACS_URL:/=!"

REM Auto-discover DICOMweb endpoint if needed
echo !PACS_URL! | findstr /i "dicomweb dicom-web wado dicom api/dicom" >nul
if !errorlevel! neq 0 (
    echo [INFO] Auto-discovering DICOMweb endpoint...
    for %%e in (dicomweb dicom-web wado dicom api/dicomweb api/dicom-web) do (
        set "test_url=!PACS_URL!/%%e"
        echo [INFO] Trying endpoint: !test_url!
        curl -s --max-time 10 "!test_url!" >nul 2>&1
        if !errorlevel! equ 0 (
            echo [SUCCESS] Found working endpoint: !test_url!
            set "PACS_URL=!test_url!"
            goto :connectivity_test
        )
    )
    echo [WARNING] Could not auto-discover endpoint. Using: !PACS_URL!
)

:connectivity_test
REM Test connectivity
echo [INFO] Testing PACS connectivity...
curl -s --max-time 10 "!PACS_URL!" >nul 2>&1
if !errorlevel! neq 0 (
    echo [ERROR] Cannot connect to PACS server. Please check the URL and network connectivity.
    pause
    exit /b 1
)
echo [SUCCESS] PACS server is accessible

echo.
echo [INFO] Ready to test PACS at: !PACS_URL!
set /p "proceed=Proceed with testing? (y/n): "
if /i "!proceed!" neq "y" (
    echo [INFO] Testing cancelled by user
    exit /b 0
)

echo.

REM Run tests
echo [INFO] Running DICOMweb conformance tests...
if not exist "test_results" mkdir test_results

python run_tests.py --pacs-url "!PACS_URL!" --output-format both --output-file "test_results\dicomweb_conformance_!date:~-4,4!!date:~-10,2!!date:~-7,2!_!time:~0,2!!time:~3,2!!time:~6,2!" --verbose

if !errorlevel! equ 0 (
    echo [SUCCESS] DICOMweb compliance testing completed!
    
    if "!SEND_EMAIL!"=="true" (
        echo.
        call :generate_email "!PACS_URL!"
    )
    
    echo.
    echo [INFO] Results are available in the test_results\ directory
    echo [INFO] You can now review the reports and share them with your PACS vendor
    
) else (
    echo [ERROR] Testing failed. Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Thank you for using the DICOMweb Conformance Test Suite!
pause
exit /b 0

:show_usage
echo DICOMweb PACS Testing Script for Windows
echo.
echo Usage: %~nx0 [OPTIONS] [PACS_URL]
echo.
echo Options:
echo   -h, --help          Show this help message
echo   --email             Generate vendor email template after tests
echo.
echo Arguments:
echo   PACS_URL           Base URL of your PACS server (optional, will prompt if not provided)
echo.
echo Examples:
echo   %~nx0                              # Interactive mode
echo   %~nx0 https://pacs.example.com    # Test specific PACS
echo   %~nx0 --email https://pacs.example.com  # Test and generate email
echo.
echo For more information, see README.md
goto :eof

:generate_email
set "pacs_url=%~1"

echo [INFO] Generating vendor email template...

REM Find the most recent test results
for /f "delims=" %%f in ('dir test_results\dicomweb_conformance_*.txt /b /o:-d 2^>nul') do set "latest_text=test_results\%%f"
for /f "delims=" %%f in ('dir test_results\dicomweb_conformance_*.json /b /o:-d 2^>nul') do set "latest_json=test_results\%%f"

if "!latest_text!"=="" (
    echo [ERROR] No test results found. Please run tests first.
    goto :eof
)

REM Extract key information
for /f "tokens=3" %%a in ('findstr "Compliance Score:" "!latest_text!" 2^>nul') do set "compliance_score=%%a"
for /f "tokens=3" %%a in ('findstr "Conformance Level:" "!latest_text!" 2^>nul') do set "conformance_level=%%a"

if "!compliance_score!"=="" set "compliance_score=Unknown"
if "!conformance_level!"=="" set "conformance_level=Unknown"

REM Create email template
echo Subject: DICOMweb Compliance Assessment Results for !pacs_url! > vendor_email_template.txt
echo. >> vendor_email_template.txt
echo Dear [PACS Vendor Name], >> vendor_email_template.txt
echo. >> vendor_email_template.txt
echo I hope this message finds you well. I am writing to share the results of a comprehensive DICOMweb compliance assessment conducted on %date% for our PACS system at !pacs_url!. >> vendor_email_template.txt
echo. >> vendor_email_template.txt
echo ## Assessment Overview >> vendor_email_template.txt
echo. >> vendor_email_template.txt
echo We recently conducted a thorough evaluation of our PACS system's DICOMweb implementation using industry-standard testing tools. This assessment evaluated all three core DICOMweb protocols: >> vendor_email_template.txt
echo. >> vendor_email_template.txt
echo • QIDO-RS (Query Based on ID with RESTful Services) - 17 tests >> vendor_email_template.txt
echo • WADO-RS (Web Access to DICOM Objects via RESTful Services) - 18 tests >> vendor_email_template.txt
echo • STOW-RS (Store Over The Web with RESTful Services) - 18 tests >> vendor_email_template.txt
echo. >> vendor_email_template.txt
echo ## Key Findings >> vendor_email_template.txt
echo. >> vendor_email_template.txt
echo **Overall Compliance Score:** !compliance_score! >> vendor_email_template.txt
echo **Conformance Level:** !conformance_level! >> vendor_email_template.txt
echo. >> vendor_email_template.txt
echo Our assessment identified several areas where your DICOMweb implementation excels, as well as some opportunities for improvement to ensure full compliance with DICOMweb standards. >> vendor_email_template.txt
echo. >> vendor_email_template.txt
echo ## Attached Documentation >> vendor_email_template.txt
echo. >> vendor_email_template.txt
echo Please find the following documents attached: >> vendor_email_template.txt
echo • Detailed test results in JSON format >> vendor_email_template.txt
echo • Human-readable conformance report >> vendor_email_template.txt
echo • Technical recommendations for improvements >> vendor_email_template.txt
echo. >> vendor_email_template.txt
echo ## Next Steps >> vendor_email_template.txt
echo. >> vendor_email_template.txt
echo We would appreciate the opportunity to discuss these findings with your technical team. Specifically, we would like to understand: >> vendor_email_template.txt
echo. >> vendor_email_template.txt
echo 1. Your timeline for addressing any non-compliant areas >> vendor_email_template.txt
echo 2. Whether updates to our current implementation would resolve these issues >> vendor_email_template.txt
echo 3. What support you can provide to ensure full DICOMweb compliance >> vendor_email_template.txt
echo. >> vendor_email_template.txt
echo ## Business Impact >> vendor_email_template.txt
echo. >> vendor_email_template.txt
echo As you know, DICOMweb compliance is increasingly important for: >> vendor_email_template.txt
echo • Interoperability with modern healthcare systems >> vendor_email_template.txt
echo • Integration with AI/ML imaging workflows >> vendor_email_template.txt
echo • Meeting regulatory and security requirements >> vendor_email_template.txt
echo • Supporting telemedicine and remote diagnostics >> vendor_email_template.txt
echo • Enabling research collaborations and data sharing >> vendor_email_template.txt
echo. >> vendor_email_template.txt
echo We value our partnership and look forward to working together to ensure our PACS system meets the highest standards for DICOMweb compliance. >> vendor_email_template.txt
echo. >> vendor_email_template.txt
echo ## Contact Information >> vendor_email_template.txt
echo. >> vendor_email_template.txt
echo Please direct your response to: >> vendor_email_template.txt
echo Name: [Your Name] >> vendor_email_template.txt
echo Title: [Your Title] >> vendor_email_template.txt
echo Department: [Your Department] >> vendor_email_template.txt
echo Phone: [Your Phone] >> vendor_email_template.txt
echo Email: [Your Email] >> vendor_email_template.txt
echo. >> vendor_email_template.txt
echo We are available to discuss these findings at your convenience and appreciate your prompt attention to this matter. >> vendor_email_template.txt
echo. >> vendor_email_template.txt
echo Thank you for your continued support. >> vendor_email_template.txt
echo. >> vendor_email_template.txt
echo Best regards, >> vendor_email_template.txt
echo. >> vendor_email_template.txt
echo [Your Name] >> vendor_email_template.txt
echo [Your Title] >> vendor_email_template.txt
echo [Your Organization] >> vendor_email_template.txt
echo Date: %date% >> vendor_email_template.txt
echo. >> vendor_email_template.txt
echo --- >> vendor_email_template.txt
echo PACS URL Tested: !pacs_url! >> vendor_email_template.txt
echo Test Suite Version: DICOMweb Conformance Test Suite v1.0.0 >> vendor_email_template.txt
echo Test Date: %date% >> vendor_email_template.txt

echo [SUCCESS] Email template generated: vendor_email_template.txt
echo [INFO] The email template is ready to be customized with your specific details and sent to your PACS vendor.
goto :eof