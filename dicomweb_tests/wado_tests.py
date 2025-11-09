"""
WADO-RS (Web Access to DICOM Objects via RESTful Services) conformance tests.

This module implements comprehensive tests for DICOM retrieval operations
including metadata retrieval, image download, frame-specific retrieval,
and performance testing.
"""

import json
import os
from typing import Dict, List, Any, Optional
from dicomweb_tests.base import DICOMwebBaseTest


class WADOTest(DICOMwebBaseTest):
    """
    Test suite for WADO-RS (Retrieve) protocol compliance.
    
    Tests cover:
    - Metadata retrieval at different levels
    - Image and document retrieval
    - Frame-specific retrieval
    - Content-Type validation
    - Performance testing
    - Error handling
    - DICOMweb compliance validation
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.protocol = "WADO"
    
    def run_tests(self) -> List:
        """Run all WADO-RS tests."""
        self.logger.info("Starting WADO-RS conformance tests...")
        
        # Test 1: Basic metadata retrieval - Studies
        self._test_study_metadata_retrieval()
        
        # Test 2: Basic metadata retrieval - Series
        self._test_series_metadata_retrieval()
        
        # Test 3: Basic metadata retrieval - Instances
        self._test_instance_metadata_retrieval()
        
        # Test 4: Image retrieval
        self._test_image_retrieval()
        
        # Test 5: Frame retrieval
        self._test_frame_retrieval()
        
        # Test 6: Bulk data retrieval
        self._test_bulk_data_retrieval()
        
        # Test 7: Content-Type validation
        self._test_content_type_validation()
        
        # Test 8: Accept header handling
        self._test_accept_header_handling()
        
        # Test 9: Range request support
        self._test_range_request_support()
        
        # Test 10: Invalid study UID
        self._test_invalid_study_uid()
        
        # Test 11: Invalid series UID
        self._test_invalid_series_uid()
        
        # Test 12: Invalid instance UID
        self._test_invalid_instance_uid()
        
        # Test 13: Malformed request
        self._test_malformed_request()
        
        # Test 14: Large file retrieval performance
        self._test_large_file_performance()
        
        # Test 15: Concurrent retrieval
        self._test_concurrent_retrieval()
        
        # Test 16: DICOM validation
        self._test_dicom_validation()
        
        # Test 17: Error response handling
        self._test_error_response_handling()
        
        # Test 18: Authentication requirements
        self._test_authentication_requirements()
        
        return self.test_results
    
    def _test_study_metadata_retrieval(self):
        """Test study-level metadata retrieval."""
        test_name = "Study Metadata Retrieval"
        
        try:
            # First query for available studies
            query_response, _ = self._make_request('GET', 'studies', params={'limit': 1})
            
            if self._validate_response(query_response):
                studies = query_response.json()
                if studies and len(studies) > 0:
                    study_uid = studies[0].get('0020000D', {}).get('Value', [None])[0]
                    if study_uid:
                        response, response_time = self._make_request('GET', f'studies/{study_uid}/metadata')
                        
                        if self._validate_response(response):
                            try:
                                metadata = response.json()
                                if isinstance(metadata, list) and len(metadata) > 0:
                                    self._record_test_result(
                                        test_name, self.protocol, "PASS",
                                        f"Study metadata retrieved successfully",
                                        response_time,
                                        {"endpoint": f"studies/{study_uid}/metadata", "method": "GET"},
                                        {"status_code": response.status_code, "metadata_count": len(metadata)},
                                        "Study metadata retrieval working correctly"
                                    )
                                else:
                                    self._record_test_result(
                                        test_name, self.protocol, "FAIL",
                                        "Study metadata response format invalid",
                                        response_time,
                                        {"endpoint": f"studies/{study_uid}/metadata", "method": "GET"},
                                        {"status_code": response.status_code, "content_type": response.headers.get('content-type')},
                                        "Ensure study metadata returns proper DICOM JSON format"
                                    )
                            except json.JSONDecodeError:
                                self._record_test_result(
                                    test_name, self.protocol, "FAIL",
                                    "Study metadata response is not valid JSON",
                                    response_time,
                                    {"endpoint": f"studies/{study_uid}/metadata", "method": "GET"},
                                    {"status_code": response.status_code, "content_type": response.headers.get('content-type')},
                                    "Ensure study metadata returns valid JSON"
                                )
                        else:
                            self._record_test_result(
                                test_name, self.protocol, "FAIL",
                                f"Study metadata retrieval failed with status {response.status_code}",
                                response_time,
                                {"endpoint": f"studies/{study_uid}/metadata", "method": "GET"},
                                {"status_code": response.status_code, "response_text": response.text[:200]},
                                "Check study UID validity and server configuration"
                            )
                    else:
                        self._record_test_result(
                            test_name, self.protocol, "SKIP",
                            "No studies available for metadata retrieval test",
                            0,
                            {"endpoint": "studies", "method": "GET"},
                            {"note": "No studies found to test with"},
                            "Add test data to enable study metadata tests"
                        )
                else:
                    self._record_test_result(
                        test_name, self.protocol, "SKIP",
                        "No studies available for metadata retrieval test",
                        0,
                        {"endpoint": "studies", "method": "GET"},
                        {"note": "No studies found to test with"},
                        "Add test data to enable study metadata tests"
                    )
            else:
                self._record_test_result(
                    test_name, self.protocol, "SKIP",
                    "Cannot query studies for metadata retrieval test",
                    0,
                    {"endpoint": "studies", "method": "GET"},
                    {"status_code": query_response.status_code},
                    "QIDO-RS must be working for WADO-RS tests"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Study metadata retrieval exception: {str(e)}",
                0,
                {"endpoint": "studies", "method": "GET"},
                {"error": str(e)},
                "Verify server supports WADO-RS metadata endpoints"
            )
    
    def _test_series_metadata_retrieval(self):
        """Test series-level metadata retrieval."""
        test_name = "Series Metadata Retrieval"
        
        try:
            # First query for available series
            query_response, _ = self._make_request('GET', 'series', params={'limit': 1})
            
            if self._validate_response(query_response):
                series = query_response.json()
                if series and len(series) > 0:
                    series_uid = series[0].get('0020000E', {}).get('Value', [None])[0]
                    if series_uid:
                        response, response_time = self._make_request('GET', f'series/{series_uid}/metadata')
                        
                        if self._validate_response(response):
                            try:
                                metadata = response.json()
                                if isinstance(metadata, list):
                                    self._record_test_result(
                                        test_name, self.protocol, "PASS",
                                        f"Series metadata retrieved successfully ({len(metadata)} items)",
                                        response_time,
                                        {"endpoint": f"series/{series_uid}/metadata", "method": "GET"},
                                        {"status_code": response.status_code, "metadata_count": len(metadata)},
                                        "Series metadata retrieval working correctly"
                                    )
                                else:
                                    self._record_test_result(
                                        test_name, self.protocol, "FAIL",
                                        "Series metadata response format invalid",
                                        response_time,
                                        {"endpoint": f"series/{series_uid}/metadata", "method": "GET"},
                                        {"status_code": response.status_code, "content_type": response.headers.get('content-type')},
                                        "Ensure series metadata returns proper DICOM JSON format"
                                    )
                            except json.JSONDecodeError:
                                self._record_test_result(
                                    test_name, self.protocol, "FAIL",
                                    "Series metadata response is not valid JSON",
                                    response_time,
                                    {"endpoint": f"series/{series_uid}/metadata", "method": "GET"},
                                    {"status_code": response.status_code, "content_type": response.headers.get('content-type')},
                                    "Ensure series metadata returns valid JSON"
                                )
                        else:
                            self._record_test_result(
                                test_name, self.protocol, "FAIL",
                                f"Series metadata retrieval failed with status {response.status_code}",
                                response_time,
                                {"endpoint": f"series/{series_uid}/metadata", "method": "GET"},
                                {"status_code": response.status_code, "response_text": response.text[:200]},
                                "Check series UID validity and server configuration"
                            )
                    else:
                        self._record_test_result(
                            test_name, self.protocol, "SKIP",
                            "No series available for metadata retrieval test",
                            0,
                            {"endpoint": "series", "method": "GET"},
                            {"note": "No series found to test with"},
                            "Add test data to enable series metadata tests"
                        )
                else:
                    self._record_test_result(
                        test_name, self.protocol, "SKIP",
                        "No series available for metadata retrieval test",
                        0,
                        {"endpoint": "series", "method": "GET"},
                        {"note": "No series found to test with"},
                        "Add test data to enable series metadata tests"
                    )
            else:
                self._record_test_result(
                    test_name, self.protocol, "SKIP",
                    "Cannot query series for metadata retrieval test",
                    0,
                    {"endpoint": "series", "method": "GET"},
                    {"status_code": query_response.status_code},
                    "QIDO-RS must be working for WADO-RS tests"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Series metadata retrieval exception: {str(e)}",
                0,
                {"endpoint": "series", "method": "GET"},
                {"error": str(e)},
                "Verify server supports WADO-RS metadata endpoints"
            )
    
    def _test_instance_metadata_retrieval(self):
        """Test instance-level metadata retrieval."""
        test_name = "Instance Metadata Retrieval"
        
        try:
            # First query for available instances
            query_response, _ = self._make_request('GET', 'instances', params={'limit': 1})
            
            if self._validate_response(query_response):
                instances = query_response.json()
                if instances and len(instances) > 0:
                    instance_uid = instances[0].get('00080018', {}).get('Value', [None])[0]
                    if instance_uid:
                        response, response_time = self._make_request('GET', f'instances/{instance_uid}/metadata')
                        
                        if self._validate_response(response):
                            try:
                                metadata = response.json()
                                if isinstance(metadata, list):
                                    self._record_test_result(
                                        test_name, self.protocol, "PASS",
                                        f"Instance metadata retrieved successfully ({len(metadata)} items)",
                                        response_time,
                                        {"endpoint": f"instances/{instance_uid}/metadata", "method": "GET"},
                                        {"status_code": response.status_code, "metadata_count": len(metadata)},
                                        "Instance metadata retrieval working correctly"
                                    )
                                else:
                                    self._record_test_result(
                                        test_name, self.protocol, "FAIL",
                                        "Instance metadata response format invalid",
                                        response_time,
                                        {"endpoint": f"instances/{instance_uid}/metadata", "method": "GET"},
                                        {"status_code": response.status_code, "content_type": response.headers.get('content-type')},
                                        "Ensure instance metadata returns proper DICOM JSON format"
                                    )
                            except json.JSONDecodeError:
                                self._record_test_result(
                                    test_name, self.protocol, "FAIL",
                                    "Instance metadata response is not valid JSON",
                                    response_time,
                                    {"endpoint": f"instances/{instance_uid}/metadata", "method": "GET"},
                                    {"status_code": response.status_code, "content_type": response.headers.get('content-type')},
                                    "Ensure instance metadata returns valid JSON"
                                )
                        else:
                            self._record_test_result(
                                test_name, self.protocol, "FAIL",
                                f"Instance metadata retrieval failed with status {response.status_code}",
                                response_time,
                                {"endpoint": f"instances/{instance_uid}/metadata", "method": "GET"},
                                {"status_code": response.status_code, "response_text": response.text[:200]},
                                "Check instance UID validity and server configuration"
                            )
                    else:
                        self._record_test_result(
                            test_name, self.protocol, "SKIP",
                            "No instances available for metadata retrieval test",
                            0,
                            {"endpoint": "instances", "method": "GET"},
                            {"note": "No instances found to test with"},
                            "Add test data to enable instance metadata tests"
                        )
                else:
                    self._record_test_result(
                        test_name, self.protocol, "SKIP",
                        "No instances available for metadata retrieval test",
                        0,
                        {"endpoint": "instances", "method": "GET"},
                        {"note": "No instances found to test with"},
                        "Add test data to enable instance metadata tests"
                    )
            else:
                self._record_test_result(
                    test_name, self.protocol, "SKIP",
                    "Cannot query instances for metadata retrieval test",
                    0,
                    {"endpoint": "instances", "method": "GET"},
                    {"status_code": query_response.status_code},
                    "QIDO-RS must be working for WADO-RS tests"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Instance metadata retrieval exception: {str(e)}",
                0,
                {"endpoint": "instances", "method": "GET"},
                {"error": str(e)},
                "Verify server supports WADO-RS metadata endpoints"
            )
    
    def _test_image_retrieval(self):
        """Test image retrieval."""
        test_name = "Image Retrieval"
        
        try:
            # First query for available instances
            query_response, _ = self._make_request('GET', 'instances', params={'limit': 1})
            
            if self._validate_response(query_response):
                instances = query_response.json()
                if instances and len(instances) > 0:
                    instance_uid = instances[0].get('00080018', {}).get('Value', [None])[0]
                    if instance_uid:
                        headers = {'Accept': 'application/dicom'}
                        response, response_time = self._make_request(
                            'GET', f'instances/{instance_uid}', headers=headers
                        )
                        
                        if self._validate_response(response):
                            content_type = response.headers.get('content-type', '')
                            if 'application/dicom' in content_type and len(response.content) > 0:
                                self._record_test_result(
                                    test_name, self.protocol, "PASS",
                                    f"Image retrieved successfully ({len(response.content)} bytes)",
                                    response_time,
                                    {"endpoint": f"instances/{instance_uid}", "method": "GET", "headers": headers},
                                    {"status_code": response.status_code, "content_type": content_type, "size": len(response.content)},
                                    "Image retrieval working correctly"
                                )
                            else:
                                self._record_test_result(
                                    test_name, self.protocol, "FAIL",
                                    f"Invalid image response: {content_type}, {len(response.content)} bytes",
                                    response_time,
                                    {"endpoint": f"instances/{instance_uid}", "method": "GET", "headers": headers},
                                    {"status_code": response.status_code, "content_type": content_type, "size": len(response.content)},
                                    "Ensure image retrieval returns application/dicom with valid data"
                                )
                        else:
                            self._record_test_result(
                                test_name, self.protocol, "FAIL",
                                f"Image retrieval failed with status {response.status_code}",
                                response_time,
                                {"endpoint": f"instances/{instance_uid}", "method": "GET", "headers": headers},
                                {"status_code": response.status_code, "response_text": response.text[:200]},
                                "Check instance UID validity and image support"
                            )
                    else:
                        self._record_test_result(
                            test_name, self.protocol, "SKIP",
                            "No instances available for image retrieval test",
                            0,
                            {"endpoint": "instances", "method": "GET"},
                            {"note": "No instances found to test with"},
                            "Add test data to enable image retrieval tests"
                        )
                else:
                    self._record_test_result(
                        test_name, self.protocol, "SKIP",
                        "No instances available for image retrieval test",
                        0,
                        {"endpoint": "instances", "method": "GET"},
                        {"note": "No instances found to test with"},
                        "Add test data to enable image retrieval tests"
                    )
            else:
                self._record_test_result(
                    test_name, self.protocol, "SKIP",
                    "Cannot query instances for image retrieval test",
                    0,
                    {"endpoint": "instances", "method": "GET"},
                    {"status_code": query_response.status_code},
                    "QIDO-RS must be working for WADO-RS tests"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Image retrieval exception: {str(e)}",
                0,
                {"endpoint": "instances", "method": "GET"},
                {"error": str(e)},
                "Verify server supports WADO-RS image endpoints"
            )
    
    def _test_frame_retrieval(self):
        """Test frame retrieval for multi-frame objects."""
        test_name = "Frame Retrieval"
        
        try:
            # First query for available instances and check if any have multiple frames
            query_response, _ = self._make_request('GET', 'instances', params={'limit': 5})
            
            if self._validate_response(query_response):
                instances = query_response.json()
                multi_frame_found = False
                test_instance = None
                
                for instance in instances:
                    # Check NumberOfFrames attribute
                    num_frames = instance.get('00280008', {}).get('Value', [1])[0]
                    if num_frames and num_frames > 1:
                        multi_frame_found = True
                        test_instance = instance
                        break
                
                if multi_frame_found and test_instance:
                    instance_uid = test_instance.get('00080018', {}).get('Value', [None])[0]
                    frame_num = 1  # Try to retrieve first frame
                    
                    headers = {'Accept': 'application/dicom'}
                    response, response_time = self._make_request(
                        'GET', f'instances/{instance_uid}/frames/{frame_num}', headers=headers
                    )
                    
                    if self._validate_response(response):
                        content_type = response.headers.get('content-type', '')
                        if 'application/dicom' in content_type and len(response.content) > 0:
                            self._record_test_result(
                                test_name, self.protocol, "PASS",
                                f"Frame retrieved successfully ({len(response.content)} bytes)",
                                response_time,
                                {"endpoint": f"instances/{instance_uid}/frames/{frame_num}", "method": "GET", "headers": headers},
                                {"status_code": response.status_code, "content_type": content_type, "size": len(response.content)},
                                "Frame retrieval working correctly"
                            )
                        else:
                            self._record_test_result(
                                test_name, self.protocol, "FAIL",
                                f"Invalid frame response: {content_type}, {len(response.content)} bytes",
                                response_time,
                                {"endpoint": f"instances/{instance_uid}/frames/{frame_num}", "method": "GET", "headers": headers},
                                {"status_code": response.status_code, "content_type": content_type, "size": len(response.content)},
                                "Ensure frame retrieval returns application/dicom with valid data"
                            )
                    else:
                        self._record_test_result(
                            test_name, self.protocol, "FAIL",
                            f"Frame retrieval failed with status {response.status_code}",
                            response_time,
                            {"endpoint": f"instances/{instance_uid}/frames/{frame_num}", "method": "GET", "headers": headers},
                            {"status_code": response.status_code, "response_text": response.text[:200]},
                            "Check frame retrieval support and instance UID validity"
                        )
                else:
                    self._record_test_result(
                        test_name, self.protocol, "SKIP",
                        "No multi-frame instances available for frame retrieval test",
                        0,
                        {"endpoint": "instances", "method": "GET"},
                        {"note": "No multi-frame instances found"},
                        "Add multi-frame DICOM objects to enable frame retrieval tests"
                    )
            else:
                self._record_test_result(
                    test_name, self.protocol, "SKIP",
                    "Cannot query instances for frame retrieval test",
                    0,
                    {"endpoint": "instances", "method": "GET"},
                    {"status_code": query_response.status_code},
                    "QIDO-RS must be working for WADO-RS tests"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Frame retrieval exception: {str(e)}",
                0,
                {"endpoint": "instances", "method": "GET"},
                {"error": str(e)},
                "Verify server supports WADO-RS frame endpoints"
            )
    
    def _test_bulk_data_retrieval(self):
        """Test bulk data retrieval."""
        test_name = "Bulk Data Retrieval"
        
        try:
            # Test bulk data endpoint
            response, response_time = self._make_request('GET', 'bulkdata/test')
            
            # This might not be supported, so we check the response
            if response.status_code in [200, 404, 400, 501]:  # OK, Not Found, Bad Request, Not Implemented
                self._record_test_result(
                    test_name, self.protocol, "PASS",
                    f"Bulk data endpoint handled with status {response.status_code}",
                    response_time,
                    {"endpoint": "bulkdata/test", "method": "GET"},
                    {"status_code": response.status_code, "content_type": response.headers.get('content-type')},
                    "Bulk data endpoint handling working"
                )
            else:
                self._record_test_result(
                    test_name, self.protocol, "FAIL",
                    f"Bulk data endpoint unexpected status {response.status_code}",
                    response_time,
                    {"endpoint": "bulkdata/test", "method": "GET"},
                    {"status_code": response.status_code, "response_text": response.text[:200]},
                    "Review bulk data endpoint implementation"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Bulk data retrieval exception: {str(e)}",
                0,
                {"endpoint": "bulkdata/test", "method": "GET"},
                {"error": str(e)},
                "Verify server bulk data endpoint support"
            )
    
    def _test_content_type_validation(self):
        """Test content-type validation for different accept headers."""
        test_name = "Content-Type Validation"
        
        try:
            # First get a valid instance UID
            query_response, _ = self._make_request('GET', 'instances', params={'limit': 1})
            
            if self._validate_response(query_response):
                instances = query_response.json()
                if instances and len(instances) > 0:
                    instance_uid = instances[0].get('00080018', {}).get('Value', [None])[0]
                    if instance_uid:
                        # Test different Accept headers
                        accept_headers = [
                            'application/dicom',
                            'application/dicom+json',
                            'image/jpeg',
                            'image/png',
                            '*/*'
                        ]
                        
                        results = []
                        for accept in accept_headers:
                            headers = {'Accept': accept}
                            response, response_time = self._make_request(
                                'GET', f'instances/{instance_uid}/metadata', headers=headers
                            )
                            results.append({
                                'accept': accept,
                                'status': response.status_code,
                                'content_type': response.headers.get('content-type', '')
                            })
                        
                        # Check if at least some accept headers are handled properly
                        valid_responses = [r for r in results if r['status'] == 200]
                        if valid_responses:
                            self._record_test_result(
                                test_name, self.protocol, "PASS",
                                f"Accept header handling: {len(valid_responses)}/{len(accept_headers)} valid responses",
                                0,
                                {"endpoint": f"instances/{instance_uid}/metadata", "method": "GET", "test_type": "accept_headers"},
                                {"accept_results": results, "valid_count": len(valid_responses)},
                                "Accept header handling working correctly"
                            )
                        else:
                            self._record_test_result(
                                test_name, self.protocol, "FAIL",
                                f"No Accept headers handled properly",
                                0,
                                {"endpoint": f"instances/{instance_uid}/metadata", "method": "GET", "test_type": "accept_headers"},
                                {"accept_results": results, "valid_count": 0},
                                "Implement proper Accept header handling"
                            )
                    else:
                        self._record_test_result(
                            test_name, self.protocol, "SKIP",
                            "No instances available for content-type validation test",
                            0,
                            {"endpoint": "instances", "method": "GET"},
                            {"note": "No instances found to test with"},
                            "Add test data to enable content-type validation tests"
                        )
                else:
                    self._record_test_result(
                        test_name, self.protocol, "SKIP",
                        "No instances available for content-type validation test",
                        0,
                        {"endpoint": "instances", "method": "GET"},
                        {"note": "No instances found to test with"},
                        "Add test data to enable content-type validation tests"
                    )
            else:
                self._record_test_result(
                    test_name, self.protocol, "SKIP",
                    "Cannot query instances for content-type validation test",
                    0,
                    {"endpoint": "instances", "method": "GET"},
                    {"status_code": query_response.status_code},
                    "QIDO-RS must be working for WADO-RS tests"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Content-Type validation exception: {str(e)}",
                0,
                {"endpoint": "instances", "method": "GET"},
                {"error": str(e)},
                "Verify server Accept header handling"
            )
    
    def _test_accept_header_handling(self):
        """Test Accept header handling for different content types."""
        test_name = "Accept Header Handling"
        
        try:
            # Test with various Accept headers
            accept_headers = [
                'application/dicom',
                'application/dicom+json',
                'image/jpeg',
                '*/*',
                ''  # No Accept header
            ]
            
            results = []
            for accept in accept_headers:
                headers = {'Accept': accept} if accept else {}
                response, response_time = self._make_request('GET', 'studies', headers=headers)
                results.append({
                    'accept': accept or '(none)',
                    'status': response.status_code,
                    'content_type': response.headers.get('content-type', '')
                })
            
            # Check if responses are reasonable
            successful_responses = [r for r in results if r['status'] == 200]
            if successful_responses:
                self._record_test_result(
                    test_name, self.protocol, "PASS",
                    f"Accept header handling: {len(successful_responses)}/{len(accept_headers)} successful responses",
                    0,
                    {"endpoint": "studies", "method": "GET", "test_type": "accept_headers"},
                    {"accept_results": results, "successful_count": len(successful_responses)},
                    "Accept header handling working correctly"
                )
            else:
                self._record_test_result(
                    test_name, self.protocol, "FAIL",
                    f"No Accept headers handled successfully",
                    0,
                    {"endpoint": "studies", "method": "GET", "test_type": "accept_headers"},
                    {"accept_results": results, "successful_count": 0},
                    "Implement proper Accept header handling for QIDO-RS endpoints"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Accept header handling exception: {str(e)}",
                0,
                {"endpoint": "studies", "method": "GET", "test_type": "accept_headers"},
                {"error": str(e)},
                "Verify server Accept header handling"
            )
    
    def _test_range_request_support(self):
        """Test HTTP Range request support."""
        test_name = "Range Request Support"
        
        try:
            # First get a valid instance UID
            query_response, _ = self._make_request('GET', 'instances', params={'limit': 1})
            
            if self._validate_response(query_response):
                instances = query_response.json()
                if instances and len(instances) > 0:
                    instance_uid = instances[0].get('00080018', {}).get('Value', [None])[0]
                    if instance_uid:
                        headers = {
                            'Accept': 'application/dicom',
                            'Range': 'bytes=0-1023'  # Request first 1KB
                        }
                        response, response_time = self._make_request(
                            'GET', f'instances/{instance_uid}', headers=headers
                        )
                        
                        # Range requests are optional, so both 200 and 206 are acceptable
                        if response.status_code in [200, 206]:  # OK or Partial Content
                            content_range = response.headers.get('content-range', '')
                            self._record_test_result(
                                test_name, self.protocol, "PASS",
                                f"Range request handled with status {response.status_code}",
                                response_time,
                                {"endpoint": f"instances/{instance_uid}", "method": "GET", "headers": headers},
                                {"status_code": response.status_code, "content_range": content_range, "size": len(response.content)},
                                "Range request handling working correctly"
                            )
                        else:
                            self._record_test_result(
                                test_name, self.protocol, "FAIL",
                                f"Range request failed with status {response.status_code}",
                                response_time,
                                {"endpoint": f"instances/{instance_uid}", "method": "GET", "headers": headers},
                                {"status_code": response.status_code, "response_text": response.text[:200]},
                                "Implement Range request support for large DICOM objects"
                            )
                    else:
                        self._record_test_result(
                            test_name, self.protocol, "SKIP",
                            "No instances available for range request test",
                            0,
                            {"endpoint": "instances", "method": "GET"},
                            {"note": "No instances found to test with"},
                            "Add test data to enable range request tests"
                        )
                else:
                    self._record_test_result(
                        test_name, self.protocol, "SKIP",
                        "No instances available for range request test",
                        0,
                        {"endpoint": "instances", "method": "GET"},
                        {"note": "No instances found to test with"},
                        "Add test data to enable range request tests"
                    )
            else:
                self._record_test_result(
                    test_name, self.protocol, "SKIP",
                    "Cannot query instances for range request test",
                    0,
                    {"endpoint": "instances", "method": "GET"},
                    {"status_code": query_response.status_code},
                    "QIDO-RS must be working for WADO-RS tests"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Range request support exception: {str(e)}",
                0,
                {"endpoint": "instances", "method": "GET"},
                {"error": str(e)},
                "Verify server Range request support"
            )
    
    def _test_invalid_study_uid(self):
        """Test handling of invalid study UID."""
        test_name = "Invalid Study UID"
        
        try:
            invalid_uid = "1.2.3.4.5.6.7.8.9.10.11.12.13.14.15"
            response, response_time = self._make_request('GET', f'studies/{invalid_uid}/metadata')
            
            # Should return 404 Not Found for invalid UID
            if response.status_code == 404:
                self._record_test_result(
                    test_name, self.protocol, "PASS",
                    f"Invalid study UID properly rejected with status {response.status_code}",
                    response_time,
                    {"endpoint": f"studies/{invalid_uid}/metadata", "method": "GET"},
                    {"status_code": response.status_code, "response_text": response.text[:200]},
                    "Invalid UID handling working correctly"
                )
            elif response.status_code in [400, 422]:  # Bad Request or Validation Error
                self._record_test_result(
                    test_name, self.protocol, "PASS",
                    f"Invalid study UID properly rejected with status {response.status_code}",
                    response_time,
                    {"endpoint": f"studies/{invalid_uid}/metadata", "method": "GET"},
                    {"status_code": response.status_code, "response_text": response.text[:200]},
                    "Invalid UID handling working correctly"
                )
            else:
                self._record_test_result(
                    test_name, self.protocol, "FAIL",
                    f"Invalid study UID unexpected status {response.status_code}",
                    response_time,
                    {"endpoint": f"studies/{invalid_uid}/metadata", "method": "GET"},
                    {"status_code": response.status_code, "response_text": response.text[:200]},
                    "Return 404 for non-existent study UIDs"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Invalid study UID test exception: {str(e)}",
                0,
                {"endpoint": f"studies/{invalid_uid if 'invalid_uid' in locals() else 'test'}/metadata", "method": "GET"},
                {"error": str(e)},
                "Verify server error handling for invalid UIDs"
            )
    
    def _test_invalid_series_uid(self):
        """Test handling of invalid series UID."""
        test_name = "Invalid Series UID"
        
        try:
            invalid_uid = "1.2.3.4.5.6.7.8.9.10.11.12.13.14.15"
            response, response_time = self._make_request('GET', f'series/{invalid_uid}/metadata')
            
            # Should return 404 Not Found for invalid UID
            if response.status_code == 404:
                self._record_test_result(
                    test_name, self.protocol, "PASS",
                    f"Invalid series UID properly rejected with status {response.status_code}",
                    response_time,
                    {"endpoint": f"series/{invalid_uid}/metadata", "method": "GET"},
                    {"status_code": response.status_code, "response_text": response.text[:200]},
                    "Invalid UID handling working correctly"
                )
            elif response.status_code in [400, 422]:  # Bad Request or Validation Error
                self._record_test_result(
                    test_name, self.protocol, "PASS",
                    f"Invalid series UID properly rejected with status {response.status_code}",
                    response_time,
                    {"endpoint": f"series/{invalid_uid}/metadata", "method": "GET"},
                    {"status_code": response.status_code, "response_text": response.text[:200]},
                    "Invalid UID handling working correctly"
                )
            else:
                self._record_test_result(
                    test_name, self.protocol, "FAIL",
                    f"Invalid series UID unexpected status {response.status_code}",
                    response_time,
                    {"endpoint": f"series/{invalid_uid}/metadata", "method": "GET"},
                    {"status_code": response.status_code, "response_text": response.text[:200]},
                    "Return 404 for non-existent series UIDs"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Invalid series UID test exception: {str(e)}",
                0,
                {"endpoint": f"series/{invalid_uid if 'invalid_uid' in locals() else 'test'}/metadata", "method": "GET"},
                {"error": str(e)},
                "Verify server error handling for invalid UIDs"
            )
    
    def _test_invalid_instance_uid(self):
        """Test handling of invalid instance UID."""
        test_name = "Invalid Instance UID"
        
        try:
            invalid_uid = "1.2.3.4.5.6.7.8.9.10.11.12.13.14.15"
            response, response_time = self._make_request('GET', f'instances/{invalid_uid}/metadata')
            
            # Should return 404 Not Found for invalid UID
            if response.status_code == 404:
                self._record_test_result(
                    test_name, self.protocol, "PASS",
                    f"Invalid instance UID properly rejected with status {response.status_code}",
                    response_time,
                    {"endpoint": f"instances/{invalid_uid}/metadata", "method": "GET"},
                    {"status_code": response.status_code, "response_text": response.text[:200]},
                    "Invalid UID handling working correctly"
                )
            elif response.status_code in [400, 422]:  # Bad Request or Validation Error
                self._record_test_result(
                    test_name, self.protocol, "PASS",
                    f"Invalid instance UID properly rejected with status {response.status_code}",
                    response_time,
                    {"endpoint": f"instances/{invalid_uid}/metadata", "method": "GET"},
                    {"status_code": response.status_code, "response_text": response.text[:200]},
                    "Invalid UID handling working correctly"
                )
            else:
                self._record_test_result(
                    test_name, self.protocol, "FAIL",
                    f"Invalid instance UID unexpected status {response.status_code}",
                    response_time,
                    {"endpoint": f"instances/{invalid_uid}/metadata", "method": "GET"},
                    {"status_code": response.status_code, "response_text": response.text[:200]},
                    "Return 404 for non-existent instance UIDs"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Invalid instance UID test exception: {str(e)}",
                0,
                {"endpoint": f"instances/{invalid_uid if 'invalid_uid' in locals() else 'test'}/metadata", "method": "GET"},
                {"error": str(e)},
                "Verify server error handling for invalid UIDs"
            )
    
    def _test_malformed_request(self):
        """Test handling of malformed requests."""
        test_name = "Malformed Request"
        
        try:
            # Test with malformed endpoint
            response, response_time = self._make_request('GET', 'studies/invalid/endpoint/metadata')
            
            # Should return 400 Bad Request or 404 Not Found
            if response.status_code in [400, 404, 422]:
                self._record_test_result(
                    test_name, self.protocol, "PASS",
                    f"Malformed request properly rejected with status {response.status_code}",
                    response_time,
                    {"endpoint": "studies/invalid/endpoint/metadata", "method": "GET"},
                    {"status_code": response.status_code, "response_text": response.text[:200]},
                    "Malformed request handling working correctly"
                )
            else:
                self._record_test_result(
                    test_name, self.protocol, "FAIL",
                    f"Malformed request unexpected status {response.status_code}",
                    response_time,
                    {"endpoint": "studies/invalid/endpoint/metadata", "method": "GET"},
                    {"status_code": response.status_code, "response_text": response.text[:200]},
                    "Return proper error status for malformed requests"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Malformed request test exception: {str(e)}",
                0,
                {"endpoint": "studies/invalid/endpoint/metadata", "method": "GET"},
                {"error": str(e)},
                "Verify server error handling for malformed requests"
            )
    
    def _test_large_file_performance(self):
        """Test large file retrieval performance."""
        test_name = "Large File Performance"
        
        try:
            # First get a valid instance UID
            query_response, _ = self._make_request('GET', 'instances', params={'limit': 1})
            
            if self._validate_response(query_response):
                instances = query_response.json()
                if instances and len(instances) > 0:
                    instance_uid = instances[0].get('00080018', {}).get('Value', [None])[0]
                    if instance_uid:
                        headers = {'Accept': 'application/dicom'}
                        response, response_time = self._make_request(
                            'GET', f'instances/{instance_uid}', headers=headers
                        )
                        
                        if self._validate_response(response) and len(response.content) > 0:
                            file_size = len(response.content)
                            if response_time < 30 and file_size > 0:  # Reasonable performance
                                self._record_test_result(
                                    test_name, self.protocol, "PASS",
                                    f"Large file retrieved: {file_size} bytes in {response_time:.2f}s",
                                    response_time,
                                    {"endpoint": f"instances/{instance_uid}", "method": "GET", "headers": headers},
                                    {"status_code": response.status_code, "size": file_size, "transfer_rate": file_size / response_time if response_time > 0 else 0},
                                    "Large file retrieval performance is acceptable"
                                )
                            else:
                                self._record_test_result(
                                    test_name, self.protocol, "FAIL",
                                    f"Large file retrieval slow: {file_size} bytes in {response_time:.2f}s",
                                    response_time,
                                    {"endpoint": f"instances/{instance_uid}", "method": "GET", "headers": headers},
                                    {"status_code": response.status_code, "size": file_size, "transfer_time": response_time},
                                    "Optimize large file retrieval performance"
                                )
                        else:
                            self._record_test_result(
                                test_name, self.protocol, "FAIL",
                                f"Large file retrieval failed or empty",
                                response_time,
                                {"endpoint": f"instances/{instance_uid}", "method": "GET", "headers": headers},
                                {"status_code": response.status_code, "size": len(response.content) if 'response' in locals() else 0},
                                "Verify large file retrieval implementation"
                            )
                    else:
                        self._record_test_result(
                            test_name, self.protocol, "SKIP",
                            "No instances available for large file performance test",
                            0,
                            {"endpoint": "instances", "method": "GET"},
                            {"note": "No instances found to test with"},
                            "Add test data to enable large file performance tests"
                        )
                else:
                    self._record_test_result(
                        test_name, self.protocol, "SKIP",
                        "No instances available for large file performance test",
                        0,
                        {"endpoint": "instances", "method": "GET"},
                        {"note": "No instances found to test with"},
                        "Add test data to enable large file performance tests"
                    )
            else:
                self._record_test_result(
                    test_name, self.protocol, "SKIP",
                    "Cannot query instances for large file performance test",
                    0,
                    {"endpoint": "instances", "method": "GET"},
                    {"status_code": query_response.status_code},
                    "QIDO-RS must be working for WADO-RS tests"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Large file performance test exception: {str(e)}",
                0,
                {"endpoint": "instances", "method": "GET"},
                {"error": str(e)},
                "Verify server large file performance"
            )
    
    def _test_concurrent_retrieval(self):
        """Test concurrent retrieval performance."""
        test_name = "Concurrent Retrieval"
        
        try:
            # Test multiple concurrent requests
            import threading
            import time
            
            results = []
            errors = []
            
            def make_request():
                try:
                    start_time = time.time()
                    response, response_time = self._make_request('GET', 'studies', params={'limit': 5})
                    end_time = time.time()
                    results.append({
                        'response_time': response_time,
                        'status': response.status_code,
                        'total_time': end_time - start_time
                    })
                except Exception as e:
                    errors.append(str(e))
            
            # Make 3 concurrent requests
            threads = []
            for i in range(3):
                thread = threading.Thread(target=make_request)
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            if len(results) == 3 and len(errors) == 0:
                avg_time = sum(r['total_time'] for r in results) / len(results)
                if avg_time < 15:  # Reasonable concurrent performance
                    self._record_test_result(
                        test_name, self.protocol, "PASS",
                        f"Concurrent retrieval: {len(results)} requests in {avg_time:.2f}s average",
                        sum(r['total_time'] for r in results),
                        {"endpoint": "studies", "method": "GET", "test_type": "concurrent", "concurrent_requests": 3},
                        {"results": results, "average_time": avg_time, "error_count": len(errors)},
                        "Concurrent retrieval performance is acceptable"
                    )
                else:
                    self._record_test_result(
                        test_name, self.protocol, "FAIL",
                        f"Concurrent retrieval slow: {avg_time:.2f}s average",
                        sum(r['total_time'] for r in results),
                        {"endpoint": "studies", "method": "GET", "test_type": "concurrent", "concurrent_requests": 3},
                        {"results": results, "average_time": avg_time, "error_count": len(errors)},
                        "Optimize concurrent request handling"
                    )
            else:
                self._record_test_result(
                    test_name, self.protocol, "FAIL",
                    f"Concurrent retrieval issues: {len(results)} successful, {len(errors)} errors",
                    0,
                    {"endpoint": "studies", "method": "GET", "test_type": "concurrent", "concurrent_requests": 3},
                    {"results": results, "errors": errors, "error_count": len(errors)},
                    "Fix concurrent request handling issues"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Concurrent retrieval test exception: {str(e)}",
                0,
                {"endpoint": "studies", "method": "GET", "test_type": "concurrent"},
                {"error": str(e)},
                "Verify server concurrent request support"
            )
    
    def _test_dicom_validation(self):
        """Test DICOM data validation in responses."""
        test_name = "DICOM Validation"
        
        try:
            # First get a valid instance UID
            query_response, _ = self._make_request('GET', 'instances', params={'limit': 1})
            
            if self._validate_response(query_response):
                instances = query_response.json()
                if instances and len(instances) > 0:
                    instance_uid = instances[0].get('00080018', {}).get('Value', [None])[0]
                    if instance_uid:
                        headers = {'Accept': 'application/dicom+json'}
                        response, response_time = self._make_request(
                            'GET', f'instances/{instance_uid}/metadata', headers=headers
                        )
                        
                        if self._validate_response(response):
                            try:
                                metadata = response.json()
                                if isinstance(metadata, list) and len(metadata) > 0:
                                    # Check for required DICOM tags
                                    required_tags = ['00080005', '00080020', '00080030']  # SpecificCharacterSet, StudyDate, StudyTime
                                    found_tags = [tag for tag in required_tags if any(item.get('0020000D') == tag for item in metadata)]
                                    
                                    if len(found_tags) > 0:
                                        self._record_test_result(
                                            test_name, self.protocol, "PASS",
                                            f"DICOM validation: {len(found_tags)}/{len(required_tags)} required tags found",
                                            response_time,
                                            {"endpoint": f"instances/{instance_uid}/metadata", "method": "GET", "headers": headers},
                                            {"status_code": response.status_code, "metadata_count": len(metadata), "tags_found": len(found_tags)},
                                            "DICOM validation working correctly"
                                        )
                                    else:
                                        self._record_test_result(
                                            test_name, self.protocol, "FAIL",
                                            f"DICOM validation: no required tags found",
                                            response_time,
                                            {"endpoint": f"instances/{instance_uid}/metadata", "method": "GET", "headers": headers},
                                            {"status_code": response.status_code, "metadata_count": len(metadata), "tags_found": 0},
                                            "Ensure DICOM metadata contains required DICOM tags"
                                        )
                                else:
                                    self._record_test_result(
                                        test_name, self.protocol, "FAIL",
                                        "DICOM validation: invalid metadata format",
                                        response_time,
                                        {"endpoint": f"instances/{instance_uid}/metadata", "method": "GET", "headers": headers},
                                        {"status_code": response.status_code, "metadata_format": type(metadata).__name__},
                                        "Ensure metadata returns proper DICOM JSON format"
                                    )
                            except json.JSONDecodeError:
                                self._record_test_result(
                                    test_name, self.protocol, "FAIL",
                                    "DICOM validation: invalid JSON response",
                                    response_time,
                                    {"endpoint": f"instances/{instance_uid}/metadata", "method": "GET", "headers": headers},
                                    {"status_code": response.status_code, "content_type": response.headers.get('content-type')},
                                    "Ensure metadata returns valid JSON"
                                )
                        else:
                            self._record_test_result(
                                test_name, self.protocol, "FAIL",
                                f"DICOM validation: metadata retrieval failed",
                                response_time,
                                {"endpoint": f"instances/{instance_uid}/metadata", "method": "GET", "headers": headers},
                                {"status_code": response.status_code, "response_text": response.text[:200]},
                                "Check metadata retrieval implementation"
                            )
                    else:
                        self._record_test_result(
                            test_name, self.protocol, "SKIP",
                            "No instances available for DICOM validation test",
                            0,
                            {"endpoint": "instances", "method": "GET"},
                            {"note": "No instances found to test with"},
                            "Add test data to enable DICOM validation tests"
                        )
                else:
                    self._record_test_result(
                        test_name, self.protocol, "SKIP",
                        "No instances available for DICOM validation test",
                        0,
                        {"endpoint": "instances", "method": "GET"},
                        {"note": "No instances found to test with"},
                        "Add test data to enable DICOM validation tests"
                    )
            else:
                self._record_test_result(
                    test_name, self.protocol, "SKIP",
                    "Cannot query instances for DICOM validation test",
                    0,
                    {"endpoint": "instances", "method": "GET"},
                    {"status_code": query_response.status_code},
                    "QIDO-RS must be working for WADO-RS tests"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"DICOM validation test exception: {str(e)}",
                0,
                {"endpoint": "instances", "method": "GET"},
                {"error": str(e)},
                "Verify server DICOM compliance"
            )
    
    def _test_error_response_handling(self):
        """Test error response handling."""
        test_name = "Error Response Handling"
        
        try:
            # Test with various error conditions
            error_tests = [
                ('studies/invalid_uid/metadata', 'Invalid Study UID'),
                ('series/invalid_uid/metadata', 'Invalid Series UID'),
                ('instances/invalid_uid/metadata', 'Invalid Instance UID'),
            ]
            
            results = []
            for endpoint, description in error_tests:
                response, response_time = self._make_request('GET', endpoint)
                results.append({
                    'endpoint': endpoint,
                    'description': description,
                    'status': response.status_code,
                    'has_error_message': len(response.text) > 0
                })
            
            # Check if errors are properly handled
            proper_errors = [r for r in results if r['status'] in [400, 404, 422]]
            if len(proper_errors) > 0:
                self._record_test_result(
                    test_name, self.protocol, "PASS",
                    f"Error handling: {len(proper_errors)}/{len(error_tests)} endpoints return proper errors",
                    0,
                    {"endpoint": "error_handling", "method": "GET", "test_type": "error_responses"},
                    {"error_results": results, "proper_error_count": len(proper_errors)},
                    "Error response handling working correctly"
                )
            else:
                self._record_test_result(
                    test_name, self.protocol, "FAIL",
                    f"Error handling: no proper error responses",
                    0,
                    {"endpoint": "error_handling", "method": "GET", "test_type": "error_responses"},
                    {"error_results": results, "proper_error_count": 0},
                    "Implement proper error response handling"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Error response handling test exception: {str(e)}",
                0,
                {"endpoint": "error_handling", "method": "GET", "test_type": "error_responses"},
                {"error": str(e)},
                "Verify server error response handling"
            )
    
    def _test_authentication_requirements(self):
        """Test authentication requirements."""
        test_name = "Authentication Requirements"
        
        try:
            # Test without authentication (if server requires auth)
            response, response_time = self._make_request('GET', 'studies')
            
            # If authentication is required, server should return 401 or 403
            if response.status_code in [401, 403]:
                self._record_test_result(
                    test_name, self.protocol, "PASS",
                    f"Authentication properly required: status {response.status_code}",
                    response_time,
                    {"endpoint": "studies", "method": "GET", "test_type": "auth_required"},
                    {"status_code": response.status_code, "response_text": response.text[:200]},
                    "Authentication requirements working correctly"
                )
            elif response.status_code == 200:
                self._record_test_result(
                    test_name, self.protocol, "PASS",
                    f"Server allows anonymous access: status {response.status_code}",
                    response_time,
                    {"endpoint": "studies", "method": "GET", "test_type": "auth_optional"},
                    {"status_code": response.status_code},
                    "Anonymous access allowed - ensure this is intended"
                )
            else:
                self._record_test_result(
                    test_name, self.protocol, "FAIL",
                    f"Unexpected authentication status: {response.status_code}",
                    response_time,
                    {"endpoint": "studies", "method": "GET", "test_type": "auth_unexpected"},
                    {"status_code": response.status_code, "response_text": response.text[:200]},
                    "Review authentication requirements and implementation"
                )
                
        except Exception as e:
            self._record_test_result(
                test_name, self.protocol, "FAIL",
                f"Authentication requirements test exception: {str(e)}",
                0,
                {"endpoint": "studies", "method": "GET", "test_type": "auth_test"},
                {"error": str(e)},
                "Verify server authentication implementation"
            )