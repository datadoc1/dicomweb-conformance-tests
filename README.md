# 🏥 DICOMweb Conformance Test Suite

**The easiest way to test your PACS server for DICOMweb compliance and generate vendor-ready reports.**

## ⚡ ONE-LINE SOLUTION (Copy & Paste Ready)

```bash
curl -sSL https://raw.githubusercontent.com/datadoc1/dicomweb-conformance-tests/main/test-pacs.sh | bash -s -- https://your-pacs-server.com
```

**That's it!** This single command will:
- ✅ Install all dependencies automatically
- ✅ Test your PACS for DICOMweb compliance 
- ✅ Generate professional reports
- ✅ Create a vendor email template
- ✅ Take less than 5 minutes

---

## 🎯 **Why This Matters: The DICOMweb Imperative**

### **The Healthcare Interoperability Crisis**

Modern healthcare **depends** on DICOMweb compliance, yet many PACS systems are non-compliant. This creates serious problems:

- **🚫 Integration Failures**: Modern healthcare systems can't talk to your PACS
- **🤖 AI/ML Roadblocks**: Advanced imaging AI tools require DICOMweb access
- **📱 Telemedicine Gaps**: Remote diagnostic capabilities are limited
- **🔒 Security Vulnerabilities**: Non-compliant systems are harder to secure
- **💰 Hidden Costs**: Manual workarounds and custom integrations are expensive
- **⚖️ Regulatory Risks**: Compliance requirements are increasing

### **The Business Case for DICOMweb Testing**

#### **For Hospital IT Teams**
- **Negotiate Better**: Use objective test results in vendor discussions
- **Budget Justification**: Document exactly what needs fixing (and why)
- **Compliance Assurance**: Prove DICOMweb compliance for audits
- **Vendor Accountability**: Track vendor promises against actual performance

#### **For PACS Administrators**  
- **End Vendor Lock-in**: Independent verification of PACS capabilities
- **Support Evidence**: Provide concrete data when requesting vendor fixes
- **Performance Baseline**: Establish current state before upgrades
- **Risk Management**: Identify compliance gaps before they cause problems

#### **For Healthcare Organizations**
- **ROI Protection**: Ensure your PACS investment meets modern standards
- **Patient Safety**: Faster, more reliable image access improves care
- **Future-Proofing**: DICOMweb is the standard - ensure your PACS supports it
- **Cost Reduction**: Eliminate expensive custom integrations and manual processes

---

## 📋 **What This Test Suite Does**

### **53 Comprehensive Tests Cover:**

#### 🔍 **QIDO-RS (Query) - 17 Tests**
- Patient, Study, Series, Instance level queries
- Parameter filtering and pagination
- Performance and error handling
- **Business Impact**: Ensures you can search and find images programmatically

#### 📥 **WADO-RS (Retrieve) - 18 Tests** 
- Metadata and image retrieval
- Content-type handling and authentication
- Concurrent access and performance
- **Business Impact**: Verifies you can actually access and use your images

#### 📤 **STOW-RS (Store) - 18 Tests**
- DICOM object upload capabilities
- Large file handling and error validation
- **Business Impact**: Confirms external systems can send images to your PACS

### **Generates Professional Reports:**
- 📊 **Executive Summary**: For hospital leadership
- 🔧 **Technical Details**: For IT teams and vendors
- 📧 **Vendor Email Template**: Ready to send to your PACS company
- 📈 **Performance Metrics**: Response times and reliability data
- ✅ **Compliance Scoring**: Objective measurement of DICOMweb compliance
---

## 🔍 **How to Find Your PACS DICOMweb Endpoint**

### **For Enterprise PACS Systems (Agfa, Fuji, GE, Philips, etc.)**

#### **Common DICOMweb Endpoint Patterns:**
Most enterprise PACS systems use these URL patterns:

- **`https://your-pacs-server.com/dicomweb`**
- **`https://your-pacs-server.com/dicom-web`**
- **`https://your-pacs-server.com/wado`**
- **`https://your-pacs-server.com/dicom`**
- **`https://your-pacs-server.com/api/dicomweb`**
- **`https://your-pacs-server.com/api/dicom-web`**

#### **How to Find the Correct Endpoint:**

**1. Check Your PACS Documentation**
- Look for "DICOMweb" or "WADO-RS" in vendor documentation
- Search for "RESTful Services" or "Web Access"

**2. Contact Your PACS Administrator**
```bash
# Tell them you need the DICOMweb endpoint URL
# Example: "We need the DICOMweb endpoint URL for integration testing"
```

**3. Check PACS Web Interface**
Most PACS systems have a web interface where you can find the DICOMweb URL:
- Look for "API", "Web Services", or "Integration" sections
- Check browser developer tools for API calls
- Search for URLs containing "dicom" in the network tab

**4. Common Vendor-Specific Locations:**

**Agfa Enterprise PACS:**
```
https://your-agfa-server.com/dicomweb
https://your-agfa-server.com/cs2000/dicomweb
```

**FUJI PACS:**
```
https://your-fuji-server.com/dicom-web
https://your-fuji-server.com/synapse/dicomweb
```

**GE PACS:**
```
https://your-ge-server.com/dicomweb
https://your-ge-server.com/centricity/dicomweb
```

**Philips PACS:**
```
https://your-philips-server.com/dicomweb
https://your-philips-server.com/intellispace/dicomweb
```

**5. Test Common Endpoints**
Our testing script will automatically try these endpoints:
```bash
# The script automatically tries:
/dicomweb, /dicom-web, /wado, /dicom, /api/dicomweb, /api/dicom-web
```

### **For Local Orthanc Testing:**

**Access the web interface at:**
```
http://localhost:8042/app/explorer.html
```

**Default credentials:**
- Username: `orthanc`
- Password: `orthanc`

**DICOMweb endpoint:**
```
http://localhost:8042/dicom-web
```

### **Testing with Authentication:**

If your PACS requires authentication, use these formats:

```bash
# Include credentials in the command
python run_tests.py --pacs-url https://your-pacs.com/dicomweb \
  --username your_username --password your_password

# Or use the bash script with auth
./test-pacs.sh --email https://your-pacs.com/dicomweb
# (Then enter credentials when prompted)
```

---

---

## 🚀 **Instant Start (3 Methods)**

### **Method 1: One-Click Testing Script** ⭐ **RECOMMENDED**
```bash
# Download and run the automated testing script
curl -sSL https://raw.githubusercontent.com/datadoc1/dicomweb-conformance-tests/main/test-pacs.sh | bash -s -- https://your-pacs-server.com
```

### **Method 2: Traditional Installation**
```bash
# 1. Install dependencies  
pip install -r requirements.txt

# 2. Run tests
python run_tests.py --pacs-url https://your-pacs-server.com/dicomweb --email

# 3. Check results in test_results/ directory
```

### **Method 3: Docker Testing (No Installation)**
```bash
# Test against a sample Orthanc server
./docker_test_suite.sh
```

---

## 📊 **Real-World Example Results**

Here's what actual test results look like:

```
DICOMWEB CONFORMANCE TEST REPORT
================================================================================

EXECUTIVE SUMMARY
----------------------------------------
Total Tests Run: 53
Passed: 31 ✓    Failed: 13 ✗    Skipped: 9 ⊘
Pass Rate: 58.5%    Compliance Score: 70.5%
Conformance Level: ACCEPTABLE

PROTOCOL PERFORMANCE BREAKDOWN
----------------------------------------
QIDO-RS:  Tests: 17 | Passed: 16 | Failed: 1 | Pass Rate: 94.1%
WADO-RS:  Tests: 18 | Passed: 9  | Failed: 0 | Pass Rate: 50.0%  
STOW-RS:  Tests: 18 | Passed: 6  | Failed: 12 | Pass Rate: 33.3%

CRITICAL ISSUES REQUIRING IMMEDIATE ATTENTION
----------------------------------------
• Patient Query: Returns 404 error - Implement patient-level QIDO-RS support
• Store Operations: 415 Unsupported Media Type - Fix STOW-RS content-type handling

HIGH PRIORITY RECOMMENDATIONS
----------------------------------------
1. Focus on implementing core DICOMweb operations (QIDO-RS, WADO-RS, STOW-RS)
2. Review and implement proper authentication mechanisms  
3. Improve error response handling and HTTP status code usage
```

---

## 💬 **Sample Vendor Email** *(Automatically Generated)*

The test suite creates a professional email template for you:

```email
Subject: DICOMweb Compliance Assessment Results for https://pacs.example.com

Dear [PACS Vendor Name],

I am writing to share the results of a comprehensive DICOMweb compliance assessment 
conducted on our PACS system at https://pacs.example.com.

## Key Findings
Overall Compliance Score: 70.5%
Conformance Level: ACCEPTABLE

Our assessment identified several areas where your DICOMweb implementation needs improvement:
- Patient-level queries not working (404 errors)
- Store operations using wrong content-type (415 errors) 
- Missing DICOMweb endpoint support

## Business Impact
As you know, DICOMweb compliance is increasingly important for:
- Interoperability with modern healthcare systems
- Integration with AI/ML imaging workflows
- Meeting regulatory and security requirements
- Supporting telemedicine and remote diagnostics

## Next Steps
We would like to understand:
1. Your timeline for addressing these non-compliant areas
2. Whether updates to our current implementation would resolve these issues  
3. What support you can provide to ensure full DICOMweb compliance

We value our partnership and look forward to working together to ensure our PACS 
system meets the highest standards for DICOMweb compliance.

Best regards,
[Your Name]
```

---

## 🛠️ **Advanced Usage**

### **Authentication-Required PACS Servers**
```bash
# Test with login credentials
python run_tests.py --pacs-url https://secure-pacs.example.com/dicomweb \
  --username radiologist --password secure_password
```

### **Protocol-Specific Testing**
```bash
# Test only query and retrieval (skip storage)
python run_tests.py --pacs-url https://pacs.example.com/dicomweb \
  --protocols qido,wado
```

### **Performance Testing**
```bash
# Extended timeout for large datasets
python run_tests.py --pacs-url https://pacs.example.com/dicomweb \
  --timeout 300 --verbose
```

### **Automated/CI Testing**
```bash
# Silent mode for scripts
python run_tests.py --pacs-url https://pacs.example.com/dicomweb \
  --output-format json --output-file ci_results --quiet
```

---

## 📖 **Understanding DICOMweb Standards**

### **What is DICOMweb?**
DICOMweb is the modern web standard for medical imaging that allows healthcare systems to:
- **Query** for medical images and studies
- **Retrieve** images and metadata over HTTP
- **Store** new images via web APIs

### **Why Should You Care?**

#### **✅ Modern Healthcare Integration**
- Connect with cloud-based AI diagnostic tools
- Enable mobile and web-based viewing applications  
- Support telemedicine and remote diagnostics
- Integrate with EHR systems and health information exchanges

#### **✅ Future-Proofing Your Investment**
- DICOMweb is the industry standard (approved by DICOM Committee)
- Modern PACS systems are expected to support it
- Legacy PACS without DICOMweb support are becoming obsolete
- Regulatory bodies are increasingly requiring web-based access

#### **✅ Cost Reduction**
- Eliminate expensive custom interfaces
- Reduce manual image transfer processes
- Enable automated workflows and AI integration
- Lower total cost of ownership

#### **✅ Security & Compliance**
- Web-standard security protocols (HTTPS, OAuth, etc.)
- Better audit trails and access logging
- Easier compliance with healthcare privacy regulations
- Standard encryption and authentication methods

### **The Three Core DICOMweb Protocols:**

1. **QIDO-RS (Query)**: Find and search for medical images
2. **WADO-RS (Retrieve)**: Download images and metadata  
3. **STOW-RS (Store)**: Upload new images to the PACS

---

## 🏥 **Use Cases by Organization Type**

### **Hospitals & Healthcare Systems**
```
Scenario: Evaluating new PACS vendors
Use Case: Run tests during vendor selection to ensure future DICOMweb compliance
Result: Objective data to compare vendors and negotiate requirements
```

```
Scenario: Annual compliance audit
Use Case: Document DICOMweb compliance status for regulatory requirements
Result: Professional reports for auditors and compliance teams
```

### **Radiology Groups & Imaging Centers**
```
Scenario: Planning to implement AI diagnostic tools
Use Case: Verify current PACS can support AI integration requirements
Result: Technical roadmap for AI implementation
```

### **Healthcare IT Consultants**
```
Scenario: PACS implementation projects
Use Case: Pre-deployment testing to verify DICOMweb compliance
Result: Avoid implementation delays and vendor disputes
```

### **Medical Device Manufacturers**
```
Scenario: Ensuring interoperability with PACS systems
Use Case: Test against multiple PACS vendors to verify compatibility
Result: List of supported/unsupported PACS systems
```

---

## 📞 **Support & Getting Help**

### **Quick Troubleshooting**
- **"Connection refused"**: Check your PACS URL and network connectivity
- **"Authentication failed"**: Verify username/password or test without auth
- **"Timeout errors"**: Try `--timeout 300` for slow servers
- **"No DICOM data found"**: Ensure your PACS has test images loaded

### **Getting Help**
1. **Check the generated reports** - they include detailed error information
2. **Run with verbose mode** for detailed debugging: `--verbose`
3. **Test against Orthanc** (known working DICOMweb server) as a baseline
4. **Contact your PACS vendor** with the generated reports

### **Community & Contributions**
- **GitHub Issues**: Report bugs and request features
- **Pull Requests**: Contribute new tests and improvements
- **Discussions**: Share experiences and best practices

---

## 🏆 **Success Stories**

> *"We discovered our $2M PACS system was only 60% DICOMweb compliant. The test results gave us the leverage we needed to get the vendor to fix the issues during our support contract renewal."*  
> **- Hospital IT Director**

> *"The automated vendor email template saved us weeks of work. We sent the test results to our PACS vendor and they scheduled an emergency patch within 48 hours."*  
> **- PACS Administrator** 

> *"Before deploying AI diagnostic tools, we ran these tests and discovered our PACS couldn't handle the DICOMweb load. We upgraded to a compliant system and avoided a costly project failure."*  
> **- Healthcare IT Consultant**

---

## 📄 **License & Credits**

This project is open source under the [MIT License](LICENSE).

**Built for the healthcare community by healthcare IT professionals.**

**DICOMweb Conformance Test Suite v1.0.0**  
*Empowering hospitals and breaking vendor lock-in through objective DICOMweb compliance verification.*