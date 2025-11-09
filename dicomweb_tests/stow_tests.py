"""
STOW-RS (Store Over The Web with RESTful Services) conformance tests.

This module implements comprehensive tests for DICOM store operations
including single and multi-part DICOM uploads, status validation,
and error handling.
"""

import json
import os
import base64
from typing import Dict, List, Any, Optional
from dicomweb_tests.base import DICOMwebBaseTest


class STOWTest(DICOMwebBaseTest):
    """
    Test suite for STOW-RS (Store) protocol compliance.
    
    Tests cover:
    - Single DICOM object upload
    - Multi-part DICOM upload
    - Upload status validation
    - DICOM content validation
    - Error handling for invalid uploads
    - Bulk store operations
    - Authentication requirements
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.protocol = "STOW"
    
    def run_tests(self) -> List:
        """Run all STOW-RS tests."""
        self.logger.info("Starting STOW-RS conformance tests...")
        
        # Test 1: Basic store operation
        self._test_basic_store()
        
        # Test 2: Store with metadata
        self._test_store_with_metadata()
        
        # Test 3: Store with custom content type
        self._test_store_custom_content_type()
        
        # Test 4: Store multiple DICOM objects
        self._test_store_multiple_objects()
        
        # Test 5: Store invalid DICOM data
        self._test_store_invalid_dicom()
        
        # Test 6: Store with authentication
        self._test_store_with_auth()
        
        # Test 7: Store response validation
        self._test_store_response_validation()
        
        # Test 8: Store without required permissions
        self._test_store_without_permissions()
        
        # Test 9: Store large DICOM object
        self._test_store_large_dicom()
        
        # Test 10: Store with different DICOM modalities
        self._test_store_different_modalities()
        
        # Test 11: Store with DICOM directory
        self._test_store_dicom_directory()
        
        # Test 12: Store with multipart upload
        self._test_multipart_upload()
        
        # Test 13: Store with concurrent uploads
        self._test_concurrent_uploads()
        
        # Test 14: Store with specific study/series
        self._test_store_specific_study_series()
        
        # Test 15: Store with patient information
        self._test_store_with_patient_info()
        
        # Test 16: Store empty payload
        self._test_store_empty_payload()
        
        # Test 17: Store corrupted DICOM
        self._test_store_corrupted_dicom()
        
        # Test 18: Store with unsupported format
        self._test_store_unsupported_format()
        
        return self.test_results
    
    def _test_basic_store(self):
        """Test basic DICOM store operation."""
        test_name = "Basic DICOM Store"
        
        try:
            # Create a minimal DICOM dataset for testing
            dicom_data = self._create_test_dicom()
            
            headers = {
                'Content-Type': 'application/dicom',
                'Accept': 'application/dicom+json'
            }
            
            response, response_time = self._make_request(
                'POST', 'studies', 
                data=dicom_data, 
                headers=headers
            )
            
            if self._validate_response(response, [200, 201, 204, 409]):  # OK, Created, No Content, Conflict
                self._record_test_result(
                    test_name, self.protocol, "PASS",
                    f"Basic store returned status {response.status_code}",
                    response_time,
                    {"endpoint": "studies", "method": "POST", "content_type": "application/dicom"},
                    {"status_code": response.status_code, "content_type": response.headers.get('content-type')},
                    "Basic DICOM store working correctly"
                )
            else:
                self._record_test_result(
                    test_name, self.protocol, "FAIL",
                    f"Basic store failed with status {response.status_code}",
                    response_time,
                    {"endpoint": "studies", "method": "POST", "content_type": "application/dicom"},
                    {"status_code": response.status_code, "response_text": response.text[:200]},
                    "Check STOW-RS implementation and server configuration"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Basic store exception: {str(e)}",
                0,
                {"endpoint": "studies", "method": "POST", "content_type": "application/dicom"},
                {"error": str(e)},
                "Verify server supports STOW-RS POST operations"
            )
    
    def _test_store_with_metadata(self):
        """Test DICOM store with explicit metadata."""
        test_name = "Store with Metadata"
        
        try:
            # Create a DICOM dataset with metadata
            dicom_data = self._create_test_dicom()
            metadata = {
                "0020000D": {  # Study Instance UID
                    "vr": "UI",
                    "Value": ["1.2.3.4.5.6.7.8.9.10.11.12.13.14.15"]
                },
                "0020000E": {  # Series Instance UID
                    "vr": "UI", 
                    "Value": ["1.2.3.4.5.6.7.8.9.10.11.12.13.14.16"]
                },
                "00080018": {  # SOP Instance UID
                    "vr": "UI",
                    "Value": ["1.2.3.4.5.6.7.8.9.10.11.12.13.14.17"]
                }
            }
            
            headers = {
                'Content-Type': 'application/dicom+json',
                'Accept': 'application/dicom+json'
            }
            
            response, response_time = self._make_request(
                'POST', 'studies',
                json=metadata,
                headers=headers
            )
            
            if self._validate_response(response, [200, 201, 204, 409]):
                self._record_test_result(
                    test_name, self.protocol, "PASS",
                    f"Store with metadata returned status {response.status_code}",
                    response_time,
                    {"endpoint": "studies", "method": "POST", "content_type": "application/dicom+json"},
                    {"status_code": response.status_code, "content_type": response.headers.get('content-type')},
                    "Store with metadata working correctly"
                )
            else:
                self._record_test_result(
                    test_name, self.protocol, "FAIL",
                    f"Store with metadata failed with status {response.status_code}",
                    response_time,
                    {"endpoint": "studies", "method": "POST", "content_type": "application/dicom+json"},
                    {"status_code": response.status_code, "response_text": response.text[:200]},
                    "Check metadata support in STOW-RS implementation"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Store with metadata exception: {str(e)}",
                0,
                {"endpoint": "studies", "method": "POST", "content_type": "application/dicom+json"},
                {"error": str(e)},
                "Verify server metadata support"
            )
    
    def _test_store_custom_content_type(self):
        """Test store with custom content type."""
        test_name = "Store Custom Content Type"
        
        try:
            dicom_data = self._create_test_dicom()
            
            # Test with different content types
            content_types = [
                'application/octet-stream',
                'multipart/related',
                'application/dicom'
            ]
            
            results = []
            for content_type in content_types:
                headers = {
                    'Content-Type': content_type,
                    'Accept': 'application/dicom+json'
                }
                
                try:
                    response, response_time = self._make_request(
                        'POST', 'studies',
                        data=dicom_data,
                        headers=headers
                    )
                    results.append({
                        'content_type': content_type,
                        'status': response.status_code
                    })
                except Exception as e:
                    results.append({
                        'content_type': content_type,
                        'status': 'error',
                        'error': str(e)
                    })
            
            # Check if at least one content type is accepted
            successful_stores = [r for r in results if r['status'] in [200, 201, 204, 409]]
            if successful_stores:
                self._record_test_result(
                    test_name, self.protocol, "PASS",
                    f"Content type handling: {len(successful_stores)}/{len(content_types)} accepted",
                    0,
                    {"endpoint": "studies", "method": "POST", "test_type": "content_types"},
                    {"content_type_results": results, "successful_count": len(successful_stores)},
                    "Content type handling working correctly"
                )
            else:
                self._record_test_result(
                    test_name, self.protocol, "FAIL",
                    f"No content types accepted",
                    0,
                    {"endpoint": "studies", "method": "POST", "test_type": "content_types"},
                    {"content_type_results": results, "successful_count": 0},
                    "Implement proper content type handling"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Store custom content type exception: {str(e)}",
                0,
                {"endpoint": "studies", "method": "POST", "test_type": "content_types"},
                {"error": str(e)},
                "Verify server content type support"
            )
    
    def _test_store_multiple_objects(self):
        """Test storing multiple DICOM objects."""
        test_name = "Store Multiple Objects"
        
        try:
            # Create multiple DICOM datasets
            dicom_objects = []
            for i in range(3):
                dicom_data = self._create_test_dicom(series_offset=i)
                dicom_objects.append(dicom_data)
            
            # Try to store them together (this might be multipart or series-based)
            headers = {
                'Content-Type': 'application/dicom',
                'Accept': 'application/dicom+json'
            }
            
            # Store individual objects
            results = []
            for i, dicom_data in enumerate(dicom_objects):
                try:
                    response, response_time = self._make_request(
                        'POST', 'studies',
                        data=dicom_data,
                        headers=headers
                    )
                    results.append({
                        'object_index': i,
                        'status': response.status_code,
                        'success': response.status_code in [200, 201, 204, 409]
                    })
                except Exception as e:
                    results.append({
                        'object_index': i,
                        'status': 'error',
                        'error': str(e),
                        'success': False
                    })
            
            successful_stores = [r for r in results if r.get('success', False)]
            if len(successful_stores) > 0:
                self._record_test_result(
                    test_name, self.protocol, "PASS",
                    f"Multiple object store: {len(successful_stores)}/{len(dicom_objects)} successful",
                    0,
                    {"endpoint": "studies", "method": "POST", "test_type": "multiple_objects", "object_count": len(dicom_objects)},
                    {"store_results": results, "successful_count": len(successful_stores)},
                    "Multiple object store working correctly"
                )
            else:
                self._record_test_result(
                    test_name, self.protocol, "FAIL",
                    f"No multiple object stores successful",
                    0,
                    {"endpoint": "studies", "method": "POST", "test_type": "multiple_objects", "object_count": len(dicom_objects)},
                    {"store_results": results, "successful_count": 0},
                    "Fix multiple object store implementation"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Store multiple objects exception: {str(e)}",
                0,
                {"endpoint": "studies", "method": "POST", "test_type": "multiple_objects"},
                {"error": str(e)},
                "Verify server multiple object store support"
            )
    
    def _test_store_invalid_dicom(self):
        """Test storing invalid DICOM data."""
        test_name = "Store Invalid DICOM"
        
        try:
            # Create invalid DICOM data
            invalid_data = b"This is not a valid DICOM file"
            
            headers = {
                'Content-Type': 'application/dicom',
                'Accept': 'application/dicom+json'
            }
            
            response, response_time = self._make_request(
                'POST', 'studies',
                data=invalid_data,
                headers=headers
            )
            
            # Should return error status for invalid DICOM
            if response.status_code in [400, 422, 415]:  # Bad Request, Validation Error, Unsupported Media Type
                self._record_test_result(
                    test_name, self.protocol, "PASS",
                    f"Invalid DICOM properly rejected with status {response.status_code}",
                    response_time,
                    {"endpoint": "studies", "method": "POST", "content_type": "application/dicom"},
                    {"status_code": response.status_code, "response_text": response.text[:200]},
                    "Invalid DICOM handling working correctly"
                )
            else:
                self._record_test_result(
                    test_name, self.protocol, "FAIL",
                    f"Invalid DICOM unexpected status {response.status_code}",
                    response_time,
                    {"endpoint": "studies", "method": "POST", "content_type": "application/dicom"},
                    {"status_code": response.status_code, "response_text": response.text[:200]},
                    "Return proper error status for invalid DICOM data"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Store invalid DICOM exception: {str(e)}",
                0,
                {"endpoint": "studies", "method": "POST", "content_type": "application/dicom"},
                {"error": str(e)},
                "Verify server invalid DICOM handling"
            )
    
    def _test_store_with_auth(self):
        """Test store operation with authentication."""
        test_name = "Store with Authentication"
        
        try:
            dicom_data = self._create_test_dicom()
            
            headers = {
                'Content-Type': 'application/dicom',
                'Accept': 'application/dicom+json'
            }
            
            # Test with authentication (if provided)
            if self.username and self.password:
                response, response_time = self._make_request(
                    'POST', 'studies',
                    data=dicom_data,
                    headers=headers
                )
                
                if self._validate_response(response, [200, 201, 204, 409]):
                    self._record_test_result(
                        test_name, self.protocol, "PASS",
                        f"Authenticated store successful with status {response.status_code}",
                        response_time,
                        {"endpoint": "studies", "method": "POST", "content_type": "application/dicom", "authenticated": True},
                        {"status_code": response.status_code, "content_type": response.headers.get('content-type')},
                        "Authenticated store working correctly"
                    )
                else:
                    self._record_test_result(
                        test_name, self.protocol, "FAIL",
                        f"Authenticated store failed with status {response.status_code}",
                        response_time,
                        {"endpoint": "studies", "method": "POST", "content_type": "application/dicom", "authenticated": True},
                        {"status_code": response.status_code, "response_text": response.text[:200]},
                        "Check authentication configuration and permissions"
                    )
            else:
                # Test without authentication
                response, response_time = self._make_request(
                    'POST', 'studies',
                    data=dicom_data,
                    headers=headers
                )
                
                if response.status_code in [401, 403]:
                    self._record_test_result(
                        test_name, self.protocol, "PASS",
                        f"Store properly requires authentication: status {response.status_code}",
                        response_time,
                        {"endpoint": "studies", "method": "POST", "content_type": "application/dicom", "authenticated": False},
                        {"status_code": response.status_code, "response_text": response.text[:200]},
                        "Authentication requirements working correctly"
                    )
                elif response.status_code in [200, 201, 204, 409]:
                    self._record_test_result(
                        test_name, self.protocol, "PASS",
                        f"Store allows anonymous access: status {response.status_code}",
                        response_time,
                        {"endpoint": "studies", "method": "POST", "content_type": "application/dicom", "authenticated": False},
                        {"status_code": response.status_code},
                        "Anonymous store access allowed - ensure this is intended"
                    )
                else:
                    self._record_test_result(
                        test_name, self.protocol, "FAIL",
                        f"Store authentication test unexpected status: {response.status_code}",
                        response_time,
                        {"endpoint": "studies", "method": "POST", "content_type": "application/dicom", "authenticated": False},
                        {"status_code": response.status_code, "response_text": response.text[:200]},
                        "Review authentication implementation"
                    )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Store with auth exception: {str(e)}",
                0,
                {"endpoint": "studies", "method": "POST", "content_type": "application/dicom"},
                {"error": str(e)},
                "Verify server authentication implementation"
            )
    
    def _test_store_response_validation(self):
        """Test store response validation."""
        test_name = "Store Response Validation"
        
        try:
            dicom_data = self._create_test_dicom()
            
            headers = {
                'Content-Type': 'application/dicom',
                'Accept': 'application/dicom+json'
            }
            
            response, response_time = self._make_request(
                'POST', 'studies',
                data=dicom_data,
                headers=headers
            )
            
            if self._validate_response(response, [200, 201, 204, 409]):
                content_type = response.headers.get('content-type', '')
                
                # Check if response is valid
                try:
                    if 'application/json' in content_type:
                        response_data = response.json()
                        if isinstance(response_data, dict):
                            self._record_test_result(
                                test_name, self.protocol, "PASS",
                                f"Store response validation passed: {content_type}",
                                response_time,
                                {"endpoint": "studies", "method": "POST", "content_type": "application/dicom"},
                                {"status_code": response.status_code, "content_type": content_type, "response_format": "json"},
                                "Store response validation working correctly"
                            )
                        else:
                            self._record_test_result(
                                test_name, self.protocol, "FAIL",
                                f"Store response not a JSON object: {type(response_data)}",
                                response_time,
                                {"endpoint": "studies", "method": "POST", "content_type": "application/dicom"},
                                {"status_code": response.status_code, "content_type": content_type, "response_type": type(response_data).__name__},
                                "Ensure store response returns valid JSON object"
                            )
                    else:
                        self._record_test_result(
                            test_name, self.protocol, "PASS",
                            f"Store response accepted: {content_type}",
                            response_time,
                            {"endpoint": "studies", "method": "POST", "content_type": "application/dicom"},
                            {"status_code": response.status_code, "content_type": content_type},
                            "Store response validation working correctly"
                        )
                except json.JSONDecodeError:
                    self._record_test_result(
                        test_name, self.protocol, "FAIL",
                        f"Store response not valid JSON",
                        response_time,
                        {"endpoint": "studies", "method": "POST", "content_type": "application/dicom"},
                        {"status_code": response.status_code, "content_type": content_type},
                        "Ensure store response returns valid JSON"
                    )
            else:
                self._record_test_result(
                    test_name, self.protocol, "FAIL",
                    f"Store response validation failed: status {response.status_code}",
                    response_time,
                    {"endpoint": "studies", "method": "POST", "content_type": "application/dicom"},
                    {"status_code": response.status_code, "response_text": response.text[:200]},
                    "Check store operation implementation"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Store response validation exception: {str(e)}",
                0,
                {"endpoint": "studies", "method": "POST", "content_type": "application/dicom"},
                {"error": str(e)},
                "Verify server store response implementation"
            )
    
    def _test_store_without_permissions(self):
        """Test store without required permissions."""
        test_name = "Store Without Permissions"
        
        try:
            dicom_data = self._create_test_dicom()
            
            headers = {
                'Content-Type': 'application/dicom',
                'Accept': 'application/dicom+json'
            }
            
            # Test without authentication (if auth is required)
            response, response_time = self._make_request(
                'POST', 'studies',
                data=dicom_data,
                headers=headers
            )
            
            if response.status_code in [401, 403]:  # Unauthorized, Forbidden
                self._record_test_result(
                    test_name, self.protocol, "PASS",
                    f"Store properly requires permissions: status {response.status_code}",
                    response_time,
                    {"endpoint": "studies", "method": "POST", "content_type": "application/dicom"},
                    {"status_code": response.status_code, "response_text": response.text[:200]},
                    "Permission requirements working correctly"
                )
            elif response.status_code in [200, 201, 204, 409]:
                self._record_test_result(
                    test_name, self.protocol, "PASS",
                    f"Store allows anonymous upload: status {response.status_code}",
                    response_time,
                    {"endpoint": "studies", "method": "POST", "content_type": "application/dicom"},
                    {"status_code": response.status_code},
                    "Anonymous upload allowed - ensure this is intended"
                )
            else:
                self._record_test_result(
                    test_name, self.protocol, "FAIL",
                    f"Store permission test unexpected status: {response.status_code}",
                    response_time,
                    {"endpoint": "studies", "method": "POST", "content_type": "application/dicom"},
                    {"status_code": response.status_code, "response_text": response.text[:200]},
                    "Review upload permission requirements"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Store without permissions exception: {str(e)}",
                0,
                {"endpoint": "studies", "method": "POST", "content_type": "application/dicom"},
                {"error": str(e)},
                "Verify server permission implementation"
            )
    
    def _test_store_large_dicom(self):
        """Test storing large DICOM objects."""
        test_name = "Store Large DICOM"
        
        try:
            # Create a larger DICOM dataset
            large_dicom_data = self._create_large_test_dicom()
            
            headers = {
                'Content-Type': 'application/dicom',
                'Accept': 'application/dicom+json'
            }
            
            response, response_time = self._make_request(
                'POST', 'studies',
                data=large_dicom_data,
                headers=headers
            )
            
            if self._validate_response(response, [200, 201, 204, 409]):
                file_size = len(large_dicom_data)
                if response_time < 60:  # Reasonable performance for large files
                    self._record_test_result(
                        test_name, self.protocol, "PASS",
                        f"Large DICOM store: {file_size} bytes in {response_time:.2f}s",
                        response_time,
                        {"endpoint": "studies", "method": "POST", "content_type": "application/dicom", "test_type": "large_file"},
                        {"status_code": response.status_code, "file_size": file_size, "transfer_rate": file_size / response_time if response_time > 0 else 0},
                        "Large DICOM store performance is acceptable"
                    )
                else:
                    self._record_test_result(
                        test_name, self.protocol, "FAIL",
                        f"Large DICOM store slow: {file_size} bytes in {response_time:.2f}s",
                        response_time,
                        {"endpoint": "studies", "method": "POST", "content_type": "application/dicom", "test_type": "large_file"},
                        {"status_code": response.status_code, "file_size": file_size, "transfer_time": response_time},
                        "Optimize large file upload performance"
                    )
            else:
                self._record_test_result(
                    test_name, self.protocol, "FAIL",
                    f"Large DICOM store failed: status {response.status_code}",
                    response_time,
                    {"endpoint": "studies", "method": "POST", "content_type": "application/dicom", "test_type": "large_file"},
                    {"status_code": response.status_code, "response_text": response.text[:200]},
                    "Check large file upload support"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Store large DICOM exception: {str(e)}",
                0,
                {"endpoint": "studies", "method": "POST", "content_type": "application/dicom", "test_type": "large_file"},
                {"error": str(e)},
                "Verify server large file upload support"
            )
    
    def _test_store_different_modalities(self):
        """Test storing DICOM objects from different modalities."""
        test_name = "Store Different Modalities"
        
        try:
            # Test different modality types
            modalities = ['CT', 'MR', 'US', 'CR', 'DX']
            results = []
            
            for modality in modalities:
                dicom_data = self._create_test_dicom(modality=modality)
                
                headers = {
                    'Content-Type': 'application/dicom',
                    'Accept': 'application/dicom+json'
                }
                
                try:
                    response, response_time = self._make_request(
                        'POST', 'studies',
                        data=dicom_data,
                        headers=headers
                    )
                    results.append({
                        'modality': modality,
                        'status': response.status_code,
                        'success': response.status_code in [200, 201, 204, 409]
                    })
                except Exception as e:
                    results.append({
                        'modality': modality,
                        'status': 'error',
                        'error': str(e),
                        'success': False
                    })
            
            successful_stores = [r for r in results if r.get('success', False)]
            if len(successful_stores) > 0:
                self._record_test_result(
                    test_name, self.protocol, "PASS",
                    f"Modality store: {len(successful_stores)}/{len(modalities)} successful",
                    0,
                    {"endpoint": "studies", "method": "POST", "test_type": "modalities", "modalities": modalities},
                    {"modality_results": results, "successful_count": len(successful_stores)},
                    "Different modality store working correctly"
                )
            else:
                self._record_test_result(
                    test_name, self.protocol, "FAIL",
                    f"No modality stores successful",
                    0,
                    {"endpoint": "studies", "method": "POST", "test_type": "modalities", "modalities": modalities},
                    {"modality_results": results, "successful_count": 0},
                    "Fix modality-specific store implementation"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Store different modalities exception: {str(e)}",
                0,
                {"endpoint": "studies", "method": "POST", "test_type": "modalities"},
                {"error": str(e)},
                "Verify server modality support"
            )
    
    def _test_store_dicom_directory(self):
        """Test storing DICOM directory structure."""
        test_name = "Store DICOM Directory"
        
        try:
            # Test storing with directory-like structure
            response, response_time = self._make_request(
                'POST', 'studies/1.2.3.4.5.6.7.8.9.10.11.12.13.14.15/series/1.2.3.4.5.6.7.8.9.10.11.12.13.14.16',
                data=self._create_test_dicom(),
                headers={'Content-Type': 'application/dicom', 'Accept': 'application/dicom+json'}
            )
            
            # This might be supported or return an error
            if response.status_code in [200, 201, 204, 409, 404, 400]:
                self._record_test_result(
                    test_name, self.protocol, "PASS",
                    f"DICOM directory store handled with status {response.status_code}",
                    response_time,
                    {"endpoint": "studies/{study}/series/{series}", "method": "POST", "test_type": "directory_structure"},
                    {"status_code": response.status_code, "content_type": response.headers.get('content-type')},
                    "DICOM directory structure handling working"
                )
            else:
                self._record_test_result(
                    test_name, self.protocol, "FAIL",
                    f"DICOM directory store unexpected status {response.status_code}",
                    response_time,
                    {"endpoint": "studies/{study}/series/{series}", "method": "POST", "test_type": "directory_structure"},
                    {"status_code": response.status_code, "response_text": response.text[:200]},
                    "Review DICOM directory structure support"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Store DICOM directory exception: {str(e)}",
                0,
                {"endpoint": "studies/{study}/series/{series}", "method": "POST", "test_type": "directory_structure"},
                {"error": str(e)},
                "Verify server DICOM directory support"
            )
    
    def _test_multipart_upload(self):
        """Test multipart upload functionality."""
        test_name = "Multipart Upload"
        
        try:
            # Test multipart upload
            files = {
                'file': ('test.dcm', self._create_test_dicom(), 'application/dicom')
            }
            
            response, response_time = self._make_request(
                'POST', 'studies',
                files=files
            )
            
            # Multipart uploads might not be fully supported
            if response.status_code in [200, 201, 204, 409, 400, 415]:
                self._record_test_result(
                    test_name, self.protocol, "PASS",
                    f"Multipart upload handled with status {response.status_code}",
                    response_time,
                    {"endpoint": "studies", "method": "POST", "test_type": "multipart"},
                    {"status_code": response.status_code, "content_type": response.headers.get('content-type')},
                    "Multipart upload handling working"
                )
            else:
                self._record_test_result(
                    test_name, self.protocol, "FAIL",
                    f"Multipart upload unexpected status {response.status_code}",
                    response_time,
                    {"endpoint": "studies", "method": "POST", "test_type": "multipart"},
                    {"status_code": response.status_code, "response_text": response.text[:200]},
                    "Review multipart upload implementation"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Multipart upload exception: {str(e)}",
                0,
                {"endpoint": "studies", "method": "POST", "test_type": "multipart"},
                {"error": str(e)},
                "Verify server multipart upload support"
            )
    
    def _test_concurrent_uploads(self):
        """Test concurrent upload operations."""
        test_name = "Concurrent Uploads"
        
        try:
            import threading
            import time
            
            results = []
            errors = []
            
            def make_upload():
                try:
                    dicom_data = self._create_test_dicom()
                    headers = {
                        'Content-Type': 'application/dicom',
                        'Accept': 'application/dicom+json'
                    }
                    start_time = time.time()
                    response, response_time = self._make_request(
                        'POST', 'studies',
                        data=dicom_data,
                        headers=headers
                    )
                    end_time = time.time()
                    results.append({
                        'response_time': response_time,
                        'total_time': end_time - start_time,
                        'status': response.status_code,
                        'success': response.status_code in [200, 201, 204, 409]
                    })
                except Exception as e:
                    errors.append(str(e))
            
            # Make 3 concurrent uploads
            threads = []
            for i in range(3):
                thread = threading.Thread(target=make_upload)
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            successful_uploads = [r for r in results if r.get('success', False)]
            if len(successful_uploads) > 0:
                avg_time = sum(r['total_time'] for r in results) / len(results) if results else 0
                self._record_test_result(
                    test_name, self.protocol, "PASS",
                    f"Concurrent uploads: {len(successful_uploads)}/{len(threads)} successful, {avg_time:.2f}s avg",
                    sum(r['total_time'] for r in results),
                    {"endpoint": "studies", "method": "POST", "test_type": "concurrent", "concurrent_uploads": 3},
                    {"results": results, "successful_count": len(successful_uploads), "error_count": len(errors), "average_time": avg_time},
                    "Concurrent upload performance is acceptable"
                )
            else:
                self._record_test_result(
                    test_name, self.protocol, "FAIL",
                    f"No concurrent uploads successful",
                    0,
                    {"endpoint": "studies", "method": "POST", "test_type": "concurrent", "concurrent_uploads": 3},
                    {"results": results, "successful_count": 0, "errors": errors, "error_count": len(errors)},
                    "Fix concurrent upload handling issues"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Concurrent uploads test exception: {str(e)}",
                0,
                {"endpoint": "studies", "method": "POST", "test_type": "concurrent"},
                {"error": str(e)},
                "Verify server concurrent upload support"
            )
    
    def _test_store_specific_study_series(self):
        """Test storing to specific study/series."""
        test_name = "Store Specific Study/Series"
        
        try:
            # Test storing to specific study and series
            study_uid = "1.2.3.4.5.6.7.8.9.10.11.12.13.14.15"
            series_uid = "1.2.3.4.5.6.7.8.9.10.11.12.13.14.16"
            
            dicom_data = self._create_test_dicom()
            
            headers = {
                'Content-Type': 'application/dicom',
                'Accept': 'application/dicom+json'
            }
            
            response, response_time = self._make_request(
                'POST', f'studies/{study_uid}/series/{series_uid}',
                data=dicom_data,
                headers=headers
            )
            
            if response.status_code in [200, 201, 204, 409, 400, 404]:
                self._record_test_result(
                    test_name, self.protocol, "PASS",
                    f"Store to specific study/series handled: status {response.status_code}",
                    response_time,
                    {"endpoint": f"studies/{study_uid}/series/{series_uid}", "method": "POST", "test_type": "specific_location"},
                    {"status_code": response.status_code, "content_type": response.headers.get('content-type')},
                    "Store to specific study/series working"
                )
            else:
                self._record_test_result(
                    test_name, self.protocol, "FAIL",
                    f"Store to specific study/series unexpected status {response.status_code}",
                    response_time,
                    {"endpoint": f"studies/{study_uid}/series/{series_uid}", "method": "POST", "test_type": "specific_location"},
                    {"status_code": response.status_code, "response_text": response.text[:200]},
                    "Review specific study/series store implementation"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Store specific study/series exception: {str(e)}",
                0,
                {"endpoint": f"studies/{study_uid if 'study_uid' in locals() else 'test'}/series/{series_uid if 'series_uid' in locals() else 'test'}", "method": "POST", "test_type": "specific_location"},
                {"error": str(e)},
                "Verify server specific location store support"
            )
    
    def _test_store_with_patient_info(self):
        """Test storing DICOM with patient information."""
        test_name = "Store with Patient Info"
        
        try:
            # Create DICOM with patient information
            dicom_data = self._create_test_dicom(
                patient_name="Test^Patient",
                patient_id="TEST123",
                patient_birth_date="19850101"
            )
            
            headers = {
                'Content-Type': 'application/dicom',
                'Accept': 'application/dicom+json'
            }
            
            response, response_time = self._make_request(
                'POST', 'studies',
                data=dicom_data,
                headers=headers
            )
            
            if self._validate_response(response, [200, 201, 204, 409]):
                self._record_test_result(
                    test_name, self.protocol, "PASS",
                    f"Store with patient info successful: status {response.status_code}",
                    response_time,
                    {"endpoint": "studies", "method": "POST", "content_type": "application/dicom", "test_type": "patient_info"},
                    {"status_code": response.status_code, "content_type": response.headers.get('content-type')},
                    "Store with patient information working correctly"
                )
            else:
                self._record_test_result(
                    test_name, self.protocol, "FAIL",
                    f"Store with patient info failed: status {response.status_code}",
                    response_time,
                    {"endpoint": "studies", "method": "POST", "content_type": "application/dicom", "test_type": "patient_info"},
                    {"status_code": response.status_code, "response_text": response.text[:200]},
                    "Check patient information handling in store operations"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Store with patient info exception: {str(e)}",
                0,
                {"endpoint": "studies", "method": "POST", "content_type": "application/dicom", "test_type": "patient_info"},
                {"error": str(e)},
                "Verify server patient information support"
            )
    
    def _test_store_empty_payload(self):
        """Test storing empty payload."""
        test_name = "Store Empty Payload"
        
        try:
            headers = {
                'Content-Type': 'application/dicom',
                'Accept': 'application/dicom+json'
            }
            
            response, response_time = self._make_request(
                'POST', 'studies',
                data=b'',
                headers=headers
            )
            
            # Should return error for empty payload
            if response.status_code in [400, 411, 422]:  # Bad Request, Length Required, Validation Error
                self._record_test_result(
                    test_name, self.protocol, "PASS",
                    f"Empty payload properly rejected: status {response.status_code}",
                    response_time,
                    {"endpoint": "studies", "method": "POST", "content_type": "application/dicom", "test_type": "empty_payload"},
                    {"status_code": response.status_code, "response_text": response.text[:200]},
                    "Empty payload handling working correctly"
                )
            else:
                self._record_test_result(
                    test_name, self.protocol, "FAIL",
                    f"Empty payload unexpected status: {response.status_code}",
                    response_time,
                    {"endpoint": "studies", "method": "POST", "content_type": "application/dicom", "test_type": "empty_payload"},
                    {"status_code": response.status_code, "response_text": response.text[:200]},
                    "Return proper error for empty payloads"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Store empty payload exception: {str(e)}",
                0,
                {"endpoint": "studies", "method": "POST", "content_type": "application/dicom", "test_type": "empty_payload"},
                {"error": str(e)},
                "Verify server empty payload handling"
            )
    
    def _test_store_corrupted_dicom(self):
        """Test storing corrupted DICOM data."""
        test_name = "Store Corrupted DICOM"
        
        try:
            # Create corrupted DICOM data
            corrupted_data = b"DICM\x00\x00\x00\x00" + b"corrupted_data_here" * 100
            
            headers = {
                'Content-Type': 'application/dicom',
                'Accept': 'application/dicom+json'
            }
            
            response, response_time = self._make_request(
                'POST', 'studies',
                data=corrupted_data,
                headers=headers
            )
            
            # Should return error for corrupted DICOM
            if response.status_code in [400, 422, 415]:
                self._record_test_result(
                    test_name, self.protocol, "PASS",
                    f"Corrupted DICOM properly rejected: status {response.status_code}",
                    response_time,
                    {"endpoint": "studies", "method": "POST", "content_type": "application/dicom", "test_type": "corrupted_dicom"},
                    {"status_code": response.status_code, "response_text": response.text[:200]},
                    "Corrupted DICOM handling working correctly"
                )
            else:
                self._record_test_result(
                    test_name, self.protocol, "FAIL",
                    f"Corrupted DICOM unexpected status: {response.status_code}",
                    response_time,
                    {"endpoint": "studies", "method": "POST", "content_type": "application/dicom", "test_type": "corrupted_dicom"},
                    {"status_code": response.status_code, "response_text": response.text[:200]},
                    "Return proper error for corrupted DICOM data"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Store corrupted DICOM exception: {str(e)}",
                0,
                {"endpoint": "studies", "method": "POST", "content_type": "application/dicom", "test_type": "corrupted_dicom"},
                {"error": str(e)},
                "Verify server corrupted DICOM handling"
            )
    
    def _test_store_unsupported_format(self):
        """Test storing unsupported format."""
        test_name = "Store Unsupported Format"
        
        try:
            # Test with unsupported format
            unsupported_data = b"This is just plain text, not DICOM"
            
            headers = {
                'Content-Type': 'text/plain',
                'Accept': 'application/dicom+json'
            }
            
            response, response_time = self._make_request(
                'POST', 'studies',
                data=unsupported_data,
                headers=headers
            )
            
            # Should return error for unsupported format
            if response.status_code in [400, 415, 422]:  # Bad Request, Unsupported Media Type, Validation Error
                self._record_test_result(
                    test_name, self.protocol, "PASS",
                    f"Unsupported format properly rejected: status {response.status_code}",
                    response_time,
                    {"endpoint": "studies", "method": "POST", "content_type": "text/plain", "test_type": "unsupported_format"},
                    {"status_code": response.status_code, "response_text": response.text[:200]},
                    "Unsupported format handling working correctly"
                )
            else:
                self._record_test_result(
                    test_name, self.protocol, "FAIL",
                    f"Unsupported format unexpected status: {response.status_code}",
                    response_time,
                    {"endpoint": "studies", "method": "POST", "content_type": "text/plain", "test_type": "unsupported_format"},
                    {"status_code": response.status_code, "response_text": response.text[:200]},
                    "Return proper error for unsupported formats"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Store unsupported format exception: {str(e)}",
                0,
                {"endpoint": "studies", "method": "POST", "content_type": "text/plain", "test_type": "unsupported_format"},
                {"error": str(e)},
                "Verify server format validation"
            )
    
    def _create_test_dicom(self, series_offset=0, modality="CT", patient_name="", patient_id="", patient_birth_date=""):
        """Create a minimal test DICOM dataset."""
        # This creates a minimal DICOM-like structure
        # In a real implementation, you would use pydicom to create proper DICOM files
        
        # Basic DICOM structure with required elements
        dicom_header = {
            'FileMetaInformationVersion': b'\x00\x01',
            'MediaStorageSOPClassUID': '1.2.840.10008.5.1.4.1.1.2',  # CT Image Storage
            'MediaStorageSOPInstanceUID': f'1.2.3.4.5.6.7.8.9.10.11.12.13.14.{17 + series_offset}',
            'TransferSyntaxUID': '1.2.840.10008.1.2',  # Implicit VR Little Endian
            'ImplementationClassUID': '1.2.3.4.5.6.7.8.9',
            'ImplementationVersionName': 'TEST_SOFT'
        }
        
        # Convert to minimal DICOM-like format
        dicom_data = b'DICM'  # DICOM magic number
        
        # Add simple pixel data (minimal)
        pixel_data = b'\x00' * 1024  # 1KB of zero data
        
        # Patient information (if provided)
        if patient_name or patient_id or patient_birth_date:
            # Add minimal patient info
            if patient_name:
                dicom_header['PatientName'] = patient_name
            if patient_id:
                dicom_header['PatientID'] = patient_id
            if patient_birth_date:
                dicom_header['PatientBirthDate'] = patient_birth_date
        
        # Add modality-specific info
        dicom_header['Modality'] = modality
        dicom_header['StudyInstanceUID'] = f'1.2.3.4.5.6.7.8.9.10.11.12.13.14.15'
        dicom_header['SeriesInstanceUID'] = f'1.2.3.4.5.6.7.8.9.10.11.12.13.14.{16 + series_offset}'
        dicom_header['SOPInstanceUID'] = f'1.2.3.4.5.6.7.8.9.10.11.12.13.14.{17 + series_offset}'
        dicom_header['SOPClassUID'] = '1.2.840.10008.5.1.4.1.1.2'
        
        # Create a simple binary structure
        dicom_data += pixel_data
        
        return dicom_data
    
    def _create_large_test_dicom(self):
        """Create a larger test DICOM dataset."""
        # Create a larger DICOM dataset
        dicom_data = b'DICM'
        
        # Add larger pixel data (10KB)
        pixel_data = b'\x00' * (10 * 1024)
        dicom_data += pixel_data
        
        return dicom_data