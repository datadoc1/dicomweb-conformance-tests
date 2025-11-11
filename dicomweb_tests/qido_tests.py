"""
QIDO-RS (Query Based on ID with RESTful Services) conformance tests.

This module implements comprehensive tests for DICOM query operations
including patient, study, series, and instance level queries with
various filters, parameters, and error conditions.
"""

import json
from typing import Dict, List, Any, Optional
from dicomweb_tests.base import DICOMwebBaseTest


class QIDOTest(DICOMwebBaseTest):
    """
    Test suite for QIDO-RS (Query) protocol compliance.
    
    Tests cover:
    - Query operations at different levels (Patient, Study, Series, Instance)
    - Query parameters and filtering
    - Pagination and limits
    - Error handling and edge cases
    - DICOMweb compliance validation
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.protocol = "QIDO"
    
    def run_tests(self) -> List:
        """Run all QIDO-RS tests."""
        self.logger.info("Starting QIDO-RS conformance tests...")
        
        # Test 1: Basic Patient Level Query
        self._test_basic_patient_query()
        
        # QIDO_001 / QIDO_002 / QIDO_005: Studies endpoint + dicom+json + limit
        self._test_basic_study_query()
        
        # Test 3: Basic Series Level Query
        self._test_basic_series_query()
        
        # Test 4: Basic Instance Level Query
        self._test_basic_instance_query()
        
        # Test 5: Query with parameters
        self._test_query_with_params()
        
        # Test 6: Query with filters
        self._test_query_with_filters()
        
        # Test 7: Query with limit
        self._test_query_with_limit()
        
        # Test 8: Query with offset
        self._test_query_with_offset()
        
        # Test 9: Query with field specification
        self._test_query_with_fields()
        
        # Test 10: Query with fuzzy matching
        self._test_query_with_fuzzy()
        
        # Test 11: Query with case sensitivity
        self._test_query_case_sensitivity()
        
        # Test 12: Invalid query parameters
        self._test_invalid_query_params()
        
        # Test 13: Empty result set
        self._test_empty_result_query()
        
        # Test 14: Large result set pagination
        self._test_pagination()
        
        # Test 15: Content-Type validation
        self._test_content_type_validation()
        
        # Test 16: Response format validation
        self._test_response_format()
        
        # Test 17: Performance test
        self._test_query_performance()
        
        return self.test_results
    
    def _test_basic_patient_query(self):
        """Test basic patient level query."""
        test_name = "Basic Patient Query"
        
        try:
            response, response_time = self._make_request('GET', 'patients')
            
            if self._validate_response(response):
                try:
                    data = response.json()
                    if isinstance(data, list):
                        self._record_test_result(
                            test_name, self.protocol, "PASS",
                            f"Patient query returned {len(data)} results",
                            response_time,
                            {"endpoint": "patients", "method": "GET"},
                            {"status_code": response.status_code, "result_count": len(data)},
                            "Patient level query working correctly"
                        )
                    else:
                        self._record_test_result(
                            test_name, self.protocol, "FAIL",
                            "Patient query did not return a list",
                            response_time,
                            {"endpoint": "patients", "method": "GET"},
                            {"status_code": response.status_code, "content_type": response.headers.get('content-type')},
                            "Ensure patient query returns JSON array"
                        )
                except json.JSONDecodeError:
                    self._record_test_result(
                        test_name, self.protocol, "FAIL",
                        "Patient query response is not valid JSON",
                        response_time,
                        {"endpoint": "patients", "method": "GET"},
                        {"status_code": response.status_code, "content_type": response.headers.get('content-type')},
                        "Ensure patient query returns valid JSON"
                    )
            else:
                self._record_test_result(
                    test_name, self.protocol, "FAIL",
                    f"Patient query failed with status {response.status_code}",
                    response_time,
                    {"endpoint": "patients", "method": "GET"},
                    {"status_code": response.status_code, "response_text": response.text[:200]},
                    "Check server configuration and authentication"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Patient query exception: {str(e)}",
                0,
                {"endpoint": "patients", "method": "GET"},
                {"error": str(e)},
                "Verify server is running and accessible"
            )
    
    def _test_basic_study_query(self):
        """QIDO_001 / QIDO_002: validate canonical /studies and application/dicom+json.

        PASS criteria (SHALL):
        - 200 OK response
        - Content-Type contains application/dicom+json
        - Body is a JSON array of objects (or empty array)

        Any deviation is a FAIL for this requirement.
        """
        test_name = "QIDO_001/QIDO_002 Studies Endpoint and Content-Type"

        try:
            response, response_time = self._make_request('GET', 'studies')

            content_type = response.headers.get('content-type', '')
            if response.status_code == 200 and 'application/dicom+json' in content_type:
                try:
                    data = response.json()
                    if isinstance(data, list) and all(isinstance(item, dict) for item in (data or [])):
                        self._record_test_result(
                            test_name, self.protocol, "PASS",
                            f"/studies returned {len(data)} matches with valid application/dicom+json payload",
                            response_time,
                            {"endpoint": "/studies", "method": "GET"},
                            {
                                "status_code": response.status_code,
                                "content_type": content_type,
                                "result_count": len(data)
                            },
                            "QIDO-RS Studies endpoint implemented per PS3.18 10.6",
                            mapping_id="QIDO_001",
                            requirement="SHALL implement QIDO-RS Studies endpoint and return application/dicom+json",
                            requirement_level="SHALL"
                        )
                    else:
                        self._record_test_result(
                            test_name, self.protocol, "FAIL",
                            "QIDO_001/QIDO_002: /studies did not return a JSON array of datasets",
                            response_time,
                            {"endpoint": "/studies", "method": "GET"},
                            {
                                "status_code": response.status_code,
                                "content_type": content_type
                            },
                            "Server MUST return application/dicom+json with an array of DICOM dataset objects "
                            "for /studies per PS3.18 10.6",
                            mapping_id="QIDO_001",
                            requirement="SHALL implement QIDO-RS Studies endpoint and return application/dicom+json",
                            requirement_level="SHALL"
                        )
                except json.JSONDecodeError:
                    self._record_test_result(
                        test_name, self.protocol, "FAIL",
                        "QIDO_001/QIDO_002: /studies response is not valid JSON",
                        response_time,
                        {"endpoint": "/studies", "method": "GET"},
                        {
                            "status_code": response.status_code,
                            "content_type": content_type
                        },
                        "Server MUST return valid JSON for QIDO-RS search results",
                        mapping_id="QIDO_001",
                        requirement="SHALL implement QIDO-RS Studies endpoint and return application/dicom+json",
                        requirement_level="SHALL"
                    )
            else:
                # Any non-200 or wrong content-type is a strict FAIL for SHALL
                self._record_test_result(
                    test_name, self.protocol, "FAIL",
                    f"QIDO_001/QIDO_002: /studies failed with status {response.status_code} "
                    f"or invalid Content-Type '{content_type}'",
                    response_time,
                    {"endpoint": "/studies", "method": "GET"},
                    {
                        "status_code": response.status_code,
                        "content_type": content_type,
                        "response_text": response.text[:200]
                    },
                    "Server MUST support /studies with application/dicom+json per PS3.18 10.6",
                    mapping_id="QIDO_001",
                    requirement="SHALL implement QIDO-RS Studies endpoint and return application/dicom+json",
                    requirement_level="SHALL"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Study query exception: {str(e)}",
                0,
                {"endpoint": "studies", "method": "GET"},
                {"error": str(e)},
                "Verify server is running and accessible"
            )
    
    def _test_basic_series_query(self):
        """Test basic series level query."""
        test_name = "Basic Series Query"
        
        try:
            response, response_time = self._make_request('GET', 'series')
            
            if self._validate_response(response):
                try:
                    data = response.json()
                    if isinstance(data, list):
                        self._record_test_result(
                            test_name, self.protocol, "PASS",
                            f"Series query returned {len(data)} results",
                            response_time,
                            {"endpoint": "series", "method": "GET"},
                            {"status_code": response.status_code, "result_count": len(data)},
                            "Series level query working correctly"
                        )
                    else:
                        self._record_test_result(
                            test_name, self.protocol, "FAIL",
                            "Series query did not return a list",
                            response_time,
                            {"endpoint": "series", "method": "GET"},
                            {"status_code": response.status_code, "content_type": response.headers.get('content-type')},
                            "Ensure series query returns JSON array"
                        )
                except json.JSONDecodeError:
                    self._record_test_result(
                        test_name, self.protocol, "FAIL",
                        "Series query response is not valid JSON",
                        response_time,
                        {"endpoint": "series", "method": "GET"},
                        {"status_code": response.status_code, "content_type": response.headers.get('content-type')},
                        "Ensure series query returns valid JSON"
                    )
            else:
                self._record_test_result(
                    test_name, self.protocol, "FAIL",
                    f"Series query failed with status {response.status_code}",
                    response_time,
                    {"endpoint": "series", "method": "GET"},
                    {"status_code": response.status_code, "response_text": response.text[:200]},
                    "Check server configuration and authentication"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Series query exception: {str(e)}",
                0,
                {"endpoint": "series", "method": "GET"},
                {"error": str(e)},
                "Verify server is running and accessible"
            )
    
    def _test_basic_instance_query(self):
        """Test basic instance level query."""
        test_name = "Basic Instance Query"
        
        try:
            response, response_time = self._make_request('GET', 'instances')
            
            if self._validate_response(response):
                try:
                    data = response.json()
                    if isinstance(data, list):
                        self._record_test_result(
                            test_name, self.protocol, "PASS",
                            f"Instance query returned {len(data)} results",
                            response_time,
                            {"endpoint": "instances", "method": "GET"},
                            {"status_code": response.status_code, "result_count": len(data)},
                            "Instance level query working correctly"
                        )
                    else:
                        self._record_test_result(
                            test_name, self.protocol, "FAIL",
                            "Instance query did not return a list",
                            response_time,
                            {"endpoint": "instances", "method": "GET"},
                            {"status_code": response.status_code, "content_type": response.headers.get('content-type')},
                            "Ensure instance query returns JSON array"
                        )
                except json.JSONDecodeError:
                    self._record_test_result(
                        test_name, self.protocol, "FAIL",
                        "Instance query response is not valid JSON",
                        response_time,
                        {"endpoint": "instances", "method": "GET"},
                        {"status_code": response.status_code, "content_type": response.headers.get('content-type')},
                        "Ensure instance query returns valid JSON"
                    )
            else:
                self._record_test_result(
                    test_name, self.protocol, "FAIL",
                    f"Instance query failed with status {response.status_code}",
                    response_time,
                    {"endpoint": "instances", "method": "GET"},
                    {"status_code": response.status_code, "response_text": response.text[:200]},
                    "Check server configuration and authentication"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Instance query exception: {str(e)}",
                0,
                {"endpoint": "instances", "method": "GET"},
                {"error": str(e)},
                "Verify server is running and accessible"
            )
    
    def _test_query_with_params(self):
        """
        QIDO_003/QIDO_004 (SHOULD): basic semantic validation that common key
        parameters are accepted and influence results.

        PASS:
            - 200 OK AND valid JSON list

        Non-support:
            - 400/422 for unsupported param MAY be SKIP at mapping layer,
              so we record as SKIP here when clearly rejected.

        Note: This is recommended, not mandatory.
        """
        test_name = "QIDO_003/QIDO_004 Common Parameter Support"

        try:
            params = {
                'PatientID': '12345',
                'StudyInstanceUID': '1.2.3.4.5.6.7.8.9'
            }
            response, response_time = self._make_request('GET', 'studies', params=params)

            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        self._record_test_result(
                            test_name, self.protocol, "PASS",
                            "Server supports common QIDO parameters (PatientID, StudyInstanceUID)",
                            response_time,
                            {"endpoint": "/studies", "params": params, "method": "GET"},
                            {
                                "status_code": response.status_code,
                                "result_count": len(data)
                            },
                            "QIDO-RS recommended parameter support implemented",
                            mapping_id="QIDO_003",
                            requirement="SHOULD support PatientID and StudyInstanceUID query parameters",
                            requirement_level="SHOULD"
                        )
                    else:
                        # JSON but wrong shape: treat as FAIL for this behavioral expectation
                        self._record_test_result(
                            test_name, self.protocol, "FAIL",
                            "Common QIDO parameters did not return a JSON array",
                            response_time,
                            {"endpoint": "/studies", "params": params, "method": "GET"},
                            {
                                "status_code": response.status_code,
                                "response_type": type(data).__name__
                            },
                            "If supported, parameterized QIDO-RS results SHOULD follow standard array semantics",
                            mapping_id="QIDO_003",
                            requirement="SHOULD support PatientID and StudyInstanceUID query parameters",
                            requirement_level="SHOULD"
                        )
                except json.JSONDecodeError:
                    self._record_test_result(
                        test_name, self.protocol, "FAIL",
                        "Common QIDO parameters response is not valid JSON",
                        response_time,
                        {"endpoint": "/studies", "params": params, "method": "GET"},
                        {
                            "status_code": response.status_code,
                            "content_type": response.headers.get('content-type')
                        },
                        "If supported, parameterized QIDO-RS results SHOULD be valid JSON",
                        mapping_id="QIDO_003",
                        requirement="SHOULD support PatientID and StudyInstanceUID query parameters",
                        requirement_level="SHOULD"
                    )
            elif response.status_code in (400, 422):
                # Explicit rejection -> treat as non-support of SHOULD requirement
                self._record_test_result(
                    test_name, self.protocol, "SKIP",
                    f"Common QIDO parameters not supported (status {response.status_code})",
                    response_time,
                    {"endpoint": "/studies", "params": params, "method": "GET"},
                    {
                        "status_code": response.status_code,
                        "response_text": response.text[:200]
                    },
                    "Recommended but not mandatory parameters are not supported",
                    mapping_id="QIDO_003",
                    requirement="SHOULD support PatientID and StudyInstanceUID query parameters",
                    requirement_level="SHOULD"
                )
            else:
                # Unexpected status codes indicate problematic behavior
                self._record_test_result(
                    test_name, self.protocol, "FAIL",
                    f"Query with parameters returned unexpected status {response.status_code}",
                    response_time,
                    {"endpoint": "/studies", "params": params, "method": "GET"},
                    {
                        "status_code": response.status_code,
                        "response_text": response.text[:200]
                    },
                    "Unexpected handling of common QIDO parameters",
                    mapping_id="QIDO_003",
                    requirement="SHOULD support PatientID and StudyInstanceUID query parameters",
                    requirement_level="SHOULD"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Query with parameters exception: {str(e)}",
                0,
                {"endpoint": "studies", "params": params if 'params' in locals() else {}},
                {"error": str(e)},
                "Verify server supports query parameters"
            )
    
    def _test_query_with_filters(self):
        """Test query with filter parameters."""
        test_name = "Query with Filters"
        
        try:
            # Test with limit and offset for filtering
            params = {
                'limit': 10,
                'offset': 0,
                'includefield': 'all'
            }
            response, response_time = self._make_request('GET', 'studies', params=params)
            
            if self._validate_response(response):
                try:
                    data = response.json()
                    if isinstance(data, list):
                        self._record_test_result(
                            test_name, self.protocol, "PASS",
                            f"Query with filters returned {len(data)} results",
                            response_time,
                            {"endpoint": "studies", "params": params, "method": "GET"},
                            {"status_code": response.status_code, "result_count": len(data)},
                            "Query with filters working correctly"
                        )
                    else:
                        self._record_test_result(
                            test_name, self.protocol, "FAIL",
                            "Query with filters did not return a list",
                            response_time,
                            {"endpoint": "studies", "params": params, "method": "GET"},
                            {"status_code": response.status_code, "content_type": response.headers.get('content-type')},
                            "Ensure filter query returns JSON array"
                        )
                except json.JSONDecodeError:
                    self._record_test_result(
                        test_name, self.protocol, "FAIL",
                        "Query with filters response is not valid JSON",
                        response_time,
                        {"endpoint": "studies", "params": params, "method": "GET"},
                        {"status_code": response.status_code, "content_type": response.headers.get('content-type')},
                        "Ensure filter query returns valid JSON"
                    )
            else:
                self._record_test_result(
                    test_name, self.protocol, "FAIL",
                    f"Query with filters failed with status {response.status_code}",
                    response_time,
                    {"endpoint": "studies", "params": params, "method": "GET"},
                    {"status_code": response.status_code, "response_text": response.text[:200]},
                    "Check filter parameter support"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Query with filters exception: {str(e)}",
                0,
                {"endpoint": "studies", "params": params if 'params' in locals() else {}},
                {"error": str(e)},
                "Verify server supports filter parameters"
            )
    
    def _test_query_with_limit(self):
        """Test query with limit parameter."""
        test_name = "Query with Limit"
        
        try:
            params = {'limit': 5}
            response, response_time = self._make_request('GET', 'studies', params=params)
            
            if self._validate_response(response):
                try:
                    data = response.json()
                    if isinstance(data, list) and len(data) <= 5:
                        self._record_test_result(
                            test_name, self.protocol, "PASS",
                            f"Query with limit returned {len(data)} results (max 5)",
                            response_time,
                            {"endpoint": "studies", "params": params, "method": "GET"},
                            {"status_code": response.status_code, "result_count": len(data)},
                            "Query with limit working correctly"
                        )
                    else:
                        self._record_test_result(
                            test_name, self.protocol, "FAIL",
                            f"Query with limit returned {len(data)} results (expected <= 5)",
                            response_time,
                            {"endpoint": "studies", "params": params, "method": "GET"},
                            {"status_code": response.status_code, "result_count": len(data)},
                            "Ensure limit parameter properly restricts result count"
                        )
                except json.JSONDecodeError:
                    self._record_test_result(
                        test_name, self.protocol, "FAIL",
                        "Query with limit response is not valid JSON",
                        response_time,
                        {"endpoint": "studies", "params": params, "method": "GET"},
                        {"status_code": response.status_code, "content_type": response.headers.get('content-type')},
                        "Ensure limit query returns valid JSON"
                    )
            else:
                self._record_test_result(
                    test_name, self.protocol, "FAIL",
                    f"Query with limit failed with status {response.status_code}",
                    response_time,
                    {"endpoint": "studies", "params": params, "method": "GET"},
                    {"status_code": response.status_code, "response_text": response.text[:200]},
                    "Check limit parameter support"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Query with limit exception: {str(e)}",
                0,
                {"endpoint": "studies", "params": params if 'params' in locals() else {}},
                {"error": str(e)},
                "Verify server supports limit parameter"
            )
    
    def _test_query_with_offset(self):
        """Test query with offset parameter."""
        test_name = "Query with Offset"
        
        try:
            params = {'offset': 10}
            response, response_time = self._make_request('GET', 'studies', params=params)
            
            if self._validate_response(response):
                self._record_test_result(
                    test_name, self.protocol, "PASS",
                    f"Query with offset returned status {response.status_code}",
                    response_time,
                    {"endpoint": "studies", "params": params, "method": "GET"},
                    {"status_code": response.status_code, "content_type": response.headers.get('content-type')},
                    "Query with offset working correctly"
                )
            else:
                self._record_test_result(
                    test_name, self.protocol, "FAIL",
                    f"Query with offset failed with status {response.status_code}",
                    response_time,
                    {"endpoint": "studies", "params": params, "method": "GET"},
                    {"status_code": response.status_code, "response_text": response.text[:200]},
                    "Check offset parameter support"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Query with offset exception: {str(e)}",
                0,
                {"endpoint": "studies", "params": params if 'params' in locals() else {}},
                {"error": str(e)},
                "Verify server supports offset parameter"
            )
    
    def _test_query_with_fields(self):
        """Test query with field specification."""
        test_name = "Query with Field Specification"
        
        try:
            params = {'includefield': 'PatientID,StudyDate,ModalitiesInStudy'}
            response, response_time = self._make_request('GET', 'studies', params=params)
            
            if self._validate_response(response):
                try:
                    data = response.json()
                    if isinstance(data, list):
                        self._record_test_result(
                            test_name, self.protocol, "PASS",
                            f"Query with fields returned {len(data)} results",
                            response_time,
                            {"endpoint": "studies", "params": params, "method": "GET"},
                            {"status_code": response.status_code, "result_count": len(data)},
                            "Query with field specification working correctly"
                        )
                    else:
                        self._record_test_result(
                            test_name, self.protocol, "FAIL",
                            "Query with fields did not return a list",
                            response_time,
                            {"endpoint": "studies", "params": params, "method": "GET"},
                            {"status_code": response.status_code, "content_type": response.headers.get('content-type')},
                            "Ensure field specification query returns JSON array"
                        )
                except json.JSONDecodeError:
                    self._record_test_result(
                        test_name, self.protocol, "FAIL",
                        "Query with fields response is not valid JSON",
                        response_time,
                        {"endpoint": "studies", "params": params, "method": "GET"},
                        {"status_code": response.status_code, "content_type": response.headers.get('content-type')},
                        "Ensure field specification query returns valid JSON"
                    )
            else:
                self._record_test_result(
                    test_name, self.protocol, "FAIL",
                    f"Query with fields failed with status {response.status_code}",
                    response_time,
                    {"endpoint": "studies", "params": params, "method": "GET"},
                    {"status_code": response.status_code, "response_text": response.text[:200]},
                    "Check field specification support"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Query with fields exception: {str(e)}",
                0,
                {"endpoint": "studies", "params": params if 'params' in locals() else {}},
                {"error": str(e)},
                "Verify server supports field specification"
            )
    
    def _test_query_with_fuzzy(self):
        """Test query with fuzzy matching."""
        test_name = "Query with Fuzzy Matching"
        
        try:
            params = {'fuzzymatching': 'true'}
            response, response_time = self._make_request('GET', 'studies', params=params)
            
            if self._validate_response(response):
                self._record_test_result(
                    test_name, self.protocol, "PASS",
                    f"Query with fuzzy matching returned status {response.status_code}",
                    response_time,
                    {"endpoint": "studies", "params": params, "method": "GET"},
                    {"status_code": response.status_code, "content_type": response.headers.get('content-type')},
                    "Query with fuzzy matching working correctly"
                )
            else:
                self._record_test_result(
                    test_name, self.protocol, "FAIL",
                    f"Query with fuzzy matching failed with status {response.status_code}",
                    response_time,
                    {"endpoint": "studies", "params": params, "method": "GET"},
                    {"status_code": response.status_code, "response_text": response.text[:200]},
                    "Check fuzzy matching parameter support"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Query with fuzzy matching exception: {str(e)}",
                0,
                {"endpoint": "studies", "params": params if 'params' in locals() else {}},
                {"error": str(e)},
                "Verify server supports fuzzy matching"
            )
    
    def _test_query_case_sensitivity(self):
        """Test query case sensitivity."""
        test_name = "Query Case Sensitivity"
        
        try:
            # Test with uppercase parameters
            params = {'PATIENTID': '12345'}
            response, response_time = self._make_request('GET', 'studies', params=params)
            
            # This might be supported or not, so we check the response
            if response.status_code in [200, 400, 422]:  # OK, Bad Request, or Validation Error
                self._record_test_result(
                    test_name, self.protocol, "PASS",
                    f"Query case sensitivity handled with status {response.status_code}",
                    response_time,
                    {"endpoint": "studies", "params": params, "method": "GET"},
                    {"status_code": response.status_code, "content_type": response.headers.get('content-type')},
                    "Case sensitivity parameter handling working"
                )
            else:
                self._record_test_result(
                    test_name, self.protocol, "FAIL",
                    f"Query case sensitivity unexpected status {response.status_code}",
                    response_time,
                    {"endpoint": "studies", "params": params, "method": "GET"},
                    {"status_code": response.status_code, "response_text": response.text[:200]},
                    "Review parameter case sensitivity handling"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Query case sensitivity exception: {str(e)}",
                0,
                {"endpoint": "studies", "params": params if 'params' in locals() else {}},
                {"error": str(e)},
                "Verify server parameter handling"
            )
    
    def _test_invalid_query_params(self):
        """Test query with invalid parameters."""
        test_name = "Invalid Query Parameters"
        
        try:
            # Test with completely invalid parameters
            params = {'InvalidParam': 'invalidvalue', 'AnotherInvalid': 'test'}
            response, response_time = self._make_request('GET', 'studies', params=params)
            
            # Should return error status (400, 422) for invalid parameters
            if response.status_code in [400, 422, 200]:  # Bad Request, Validation Error, or OK (if ignored)
                self._record_test_result(
                    test_name, self.protocol, "PASS",
                    f"Invalid query parameters handled with status {response.status_code}",
                    response_time,
                    {"endpoint": "studies", "params": params, "method": "GET"},
                    {"status_code": response.status_code, "content_type": response.headers.get('content-type')},
                    "Invalid parameter handling working correctly"
                )
            else:
                self._record_test_result(
                    test_name, self.protocol, "FAIL",
                    f"Invalid query parameters unexpected status {response.status_code}",
                    response_time,
                    {"endpoint": "studies", "params": params, "method": "GET"},
                    {"status_code": response.status_code, "response_text": response.text[:200]},
                    "Ensure proper error handling for invalid parameters"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Invalid query parameters exception: {str(e)}",
                0,
                {"endpoint": "studies", "params": params if 'params' in locals() else {}},
                {"error": str(e)},
                "Verify server error handling"
            )
    
    def _test_empty_result_query(self):
        """Test query that should return empty results."""
        test_name = "Empty Result Query"
        
        try:
            # Query for non-existent data
            params = {'PatientID': 'NONEXISTENT123'}
            response, response_time = self._make_request('GET', 'studies', params=params)
            
            if self._validate_response(response):
                try:
                    data = response.json()
                    if isinstance(data, list):
                        self._record_test_result(
                            test_name, self.protocol, "PASS",
                            f"Empty result query returned {len(data)} results",
                            response_time,
                            {"endpoint": "studies", "params": params, "method": "GET"},
                            {"status_code": response.status_code, "result_count": len(data)},
                            "Empty result query working correctly"
                        )
                    else:
                        self._record_test_result(
                            test_name, self.protocol, "FAIL",
                            "Empty result query did not return a list",
                            response_time,
                            {"endpoint": "studies", "params": params, "method": "GET"},
                            {"status_code": response.status_code, "content_type": response.headers.get('content-type')},
                            "Ensure empty result query returns JSON array"
                        )
                except json.JSONDecodeError:
                    self._record_test_result(
                        test_name, self.protocol, "FAIL",
                        "Empty result query response is not valid JSON",
                        response_time,
                        {"endpoint": "studies", "params": params, "method": "GET"},
                        {"status_code": response.status_code, "content_type": response.headers.get('content-type')},
                        "Ensure empty result query returns valid JSON"
                    )
            else:
                self._record_test_result(
                    test_name, self.protocol, "FAIL",
                    f"Empty result query failed with status {response.status_code}",
                    response_time,
                    {"endpoint": "studies", "params": params, "method": "GET"},
                    {"status_code": response.status_code, "response_text": response.text[:200]},
                    "Check empty result handling"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Empty result query exception: {str(e)}",
                0,
                {"endpoint": "studies", "params": params if 'params' in locals() else {}},
                {"error": str(e)},
                "Verify server empty result handling"
            )
    
    def _test_pagination(self):
        """Test query pagination."""
        test_name = "Query Pagination"
        
        try:
            # Test pagination with limit and offset
            params = {'limit': 2, 'offset': 0}
            response1, response_time1 = self._make_request('GET', 'studies', params=params)
            
            params['offset'] = 2
            response2, response_time2 = self._make_request('GET', 'studies', params=params)
            
            if self._validate_response(response1) and self._validate_response(response2):
                try:
                    data1 = response1.json()
                    data2 = response2.json()
                    if isinstance(data1, list) and isinstance(data2, list):
                        total_time = response_time1 + response_time2
                        self._record_test_result(
                            test_name, self.protocol, "PASS",
                            f"Pagination test returned {len(data1)} and {len(data2)} results",
                            total_time,
                            {"endpoint": "studies", "method": "GET", "test_type": "pagination"},
                            {"status_code_1": response1.status_code, "status_code_2": response2.status_code,
                             "result_count_1": len(data1), "result_count_2": len(data2)},
                            "Query pagination working correctly"
                        )
                    else:
                        self._record_test_result(
                            test_name, self.protocol, "FAIL",
                            "Pagination test did not return valid lists",
                            response_time1 + response_time2,
                            {"endpoint": "studies", "method": "GET", "test_type": "pagination"},
                            {"status_code_1": response1.status_code, "status_code_2": response2.status_code},
                            "Ensure pagination query returns JSON arrays"
                        )
                except json.JSONDecodeError:
                    self._record_test_result(
                        test_name, self.protocol, "FAIL",
                        "Pagination test response is not valid JSON",
                        response_time1 + response_time2,
                        {"endpoint": "studies", "method": "GET", "test_type": "pagination"},
                        {"status_code_1": response1.status_code, "status_code_2": response2.status_code},
                        "Ensure pagination query returns valid JSON"
                    )
            else:
                self._record_test_result(
                    test_name, self.protocol, "FAIL",
                    f"Pagination test failed with statuses {response1.status_code}, {response2.status_code}",
                    response_time1 + response_time2,
                    {"endpoint": "studies", "method": "GET", "test_type": "pagination"},
                    {"status_code_1": response1.status_code, "status_code_2": response2.status_code,
                     "response_text_1": response1.text[:200], "response_text_2": response2.text[:200]},
                    "Check pagination parameter support"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Pagination test exception: {str(e)}",
                0,
                {"endpoint": "studies", "method": "GET", "test_type": "pagination"},
                {"error": str(e)},
                "Verify server supports pagination"
            )
    
    def _test_content_type_validation(self):
        """Test content-type validation."""
        test_name = "Content-Type Validation"
        
        try:
            response, response_time = self._make_request('GET', 'studies')
            
            content_type = response.headers.get('content-type', '')
            if 'application/dicom+json' in content_type or 'application/json' in content_type:
                self._record_test_result(
                    test_name, self.protocol, "PASS",
                    f"Content-Type is appropriate: {content_type}",
                    response_time,
                    {"endpoint": "studies", "method": "GET", "test_type": "content_type"},
                    {"content_type": content_type, "status_code": response.status_code},
                    "Content-Type validation working correctly"
                )
            else:
                self._record_test_result(
                    test_name, self.protocol, "FAIL",
                    f"Inappropriate Content-Type: {content_type}",
                    response_time,
                    {"endpoint": "studies", "method": "GET", "test_type": "content_type"},
                    {"content_type": content_type, "status_code": response.status_code},
                    "Ensure responses use application/dicom+json or application/json"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Content-Type validation exception: {str(e)}",
                0,
                {"endpoint": "studies", "method": "GET", "test_type": "content_type"},
                {"error": str(e)},
                "Verify server content-type headers"
            )
    
    def _test_response_format(self):
        """Test response format validation."""
        test_name = "Response Format Validation"
        
        try:
            response, response_time = self._make_request('GET', 'studies')
            
            if self._validate_response(response):
                try:
                    data = response.json()
                    # Check if response is a list (required for QIDO-RS)
                    if isinstance(data, list):
                        # Check if items are dictionaries (DICOM datasets)
                        if len(data) == 0 or all(isinstance(item, dict) for item in data):
                            self._record_test_result(
                                test_name, self.protocol, "PASS",
                                f"Response format is valid: {len(data)} items",
                                response_time,
                                {"endpoint": "studies", "method": "GET", "test_type": "response_format"},
                                {"status_code": response.status_code, "result_count": len(data),
                                 "is_list": True, "all_dicts": len(data) == 0 or all(isinstance(item, dict) for item in data)},
                                "Response format validation working correctly"
                            )
                        else:
                            self._record_test_result(
                                test_name, self.protocol, "FAIL",
                                "Response contains non-dictionary items",
                                response_time,
                                {"endpoint": "studies", "method": "GET", "test_type": "response_format"},
                                {"status_code": response.status_code, "result_count": len(data),
                                 "item_types": [type(item).__name__ for item in data[:5]]},
                                "Ensure all response items are dictionaries representing DICOM datasets"
                            )
                    else:
                        self._record_test_result(
                            test_name, self.protocol, "FAIL",
                            "Response is not a list",
                            response_time,
                            {"endpoint": "studies", "method": "GET", "test_type": "response_format"},
                            {"status_code": response.status_code, "response_type": type(data).__name__},
                            "Ensure QIDO-RS responses return JSON arrays"
                        )
                except json.JSONDecodeError:
                    self._record_test_result(
                        test_name, self.protocol, "FAIL",
                        "Response is not valid JSON",
                        response_time,
                        {"endpoint": "studies", "method": "GET", "test_type": "response_format"},
                        {"status_code": response.status_code, "content_type": response.headers.get('content-type')},
                        "Ensure response is valid JSON"
                    )
            else:
                self._record_test_result(
                    test_name, self.protocol, "FAIL",
                    f"Response format test failed with status {response.status_code}",
                    response_time,
                    {"endpoint": "studies", "method": "GET", "test_type": "response_format"},
                    {"status_code": response.status_code, "response_text": response.text[:200]},
                    "Check response format"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Response format validation exception: {str(e)}",
                0,
                {"endpoint": "studies", "method": "GET", "test_type": "response_format"},
                {"error": str(e)},
                "Verify server response format"
            )
    
    def _test_query_performance(self):
        """Test query performance."""
        test_name = "Query Performance"
        
        try:
            # Test multiple queries for performance
            query_times = []
            for i in range(3):
                response, response_time = self._make_request('GET', 'studies', params={'limit': 10})
                if self._validate_response(response):
                    query_times.append(response_time)
                else:
                    break
            
            if len(query_times) == 3:
                avg_time = sum(query_times) / len(query_times)
                max_time = max(query_times)
                
                if avg_time < 5.0 and max_time < 10.0:  # Reasonable performance thresholds
                    self._record_test_result(
                        test_name, self.protocol, "PASS",
                        f"Average query time: {avg_time:.2f}s, Max: {max_time:.2f}s",
                        sum(query_times),
                        {"endpoint": "studies", "method": "GET", "test_type": "performance", "iterations": 3},
                        {"query_times": query_times, "average": avg_time, "maximum": max_time},
                        "Query performance is acceptable"
                    )
                else:
                    self._record_test_result(
                        test_name, self.protocol, "FAIL",
                        f"Query performance is slow: Avg {avg_time:.2f}s, Max {max_time:.2f}s",
                        sum(query_times),
                        {"endpoint": "studies", "method": "GET", "test_type": "performance", "iterations": 3},
                        {"query_times": query_times, "average": avg_time, "maximum": max_time},
                        "Optimize database queries and indexing for better performance"
                    )
            else:
                self._record_test_result(
                    test_name, self.protocol, "FAIL",
                    f"Performance test failed: only {len(query_times)} queries completed",
                    sum(query_times) if query_times else 0,
                    {"endpoint": "studies", "method": "GET", "test_type": "performance", "iterations": 3},
                    {"completed_queries": len(query_times)},
                    "Check server performance and stability"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Query performance test exception: {str(e)}",
                0,
                {"endpoint": "studies", "method": "GET", "test_type": "performance"},
                {"error": str(e)},
                "Verify server performance"
            )