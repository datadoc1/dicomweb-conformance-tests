# DICOMweb Conformance Test Suite

A comprehensive, open-source Python-based test suite for verifying PACS compliance with the DICOMweb standard (QIDO-RS, WADO-RS, STOW-RS).

## Overview

This tool allows hospital IT teams, PACS integrators, and radiology researchers to:
- Objectively verify DICOMweb standard compliance
- Generate both human-readable and machine-readable conformance reports
- Use modular/extensible tests for community-driven development

## Project Goal

Create an open-source, easy-to-run test suite that provides absolute out-of-the-box usability while offering comprehensive, real-world test coverage. The tool is designed to create positive pressure for DICOMweb conformance in the PACS market.

## Key Features

- **Single-command execution**: Run all tests with `python run_tests.py --pacs-url https://server/dicomweb [options]`
- **Full DICOMweb Support**:
  - QIDO-RS (query): Multiple query types, edge cases, filters, pagination, error handling
  - WADO-RS (retrieve): Metadata retrieval, image download, frame-specific retrieval, performance testing
  - STOW-RS (store): Single and multi-part DICOM uploads, status validation, error handling
- **Comprehensive Reporting**: JSON and human-readable reports with actionable recommendations
- **Modular Design**: Easy for the community to add new tests

## Directory Structure

```
dicomweb-conformance-tests/
├── README.md
├── requirements.txt
├── run_tests.py
├── dicomweb_tests/
│   ├── base.py
│   ├── qido_tests.py
│   ├── wado_tests.py
│   ├── stow_tests.py
│   └── conformance_report.py
└── test_data/
    ├── sample_ct.dcm
    └── sample_xray.dcm
```

## Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run tests: `python run_tests.py --pacs-url https://your-pacs-server/dicomweb`

## Usage

```bash
# Basic usage
python run_tests.py --pacs-url https://server/dicomweb

# With authentication
python run_tests.py --pacs-url https://server/dicomweb --username user --password pass

# Custom output format
python run_tests.py --pacs-url https://server/dicomweb --output-format json
```

## Technical Specifications

- **Python**: 3.8+
- **Dependencies**: requests, pydicom, pytest
- **Architecture**: Each protocol (QIDO, WADO, STOW) has its own test suite inheriting from shared base
- **Test Structure**: Setup → Request → Validate Response → Log Result

## Reports

The tool generates two types of reports:
- **JSON**: Detailed results for automation and CI/CD integration
- **Human-readable**: Summary with pass/fail counts, failure details, and vendor-facing recommendations

## Extending the Suite

The modular design allows easy addition of new tests:
1. Create new test modules in `dicomweb_tests/`
2. Inherit from `base.py`
3. Follow the established test structure

## Contributing

We welcome community contributions! Please see our contributing guidelines for:
- How to add new tests
- Code style and testing requirements
- Submitting pull requests

## Success Criteria

- Usable out of the box by anyone in less than 5 minutes
- Produces actionable reports with vendor-facing language
- Enables community-driven test development
- Creates positive pressure for DICOMweb conformance in the PACS market

## License

This project is open source. Please see LICENSE file for details.

---

*This tool is designed to empower hospitals and help break vendor lock-in by providing objective DICOMweb compliance verification.*