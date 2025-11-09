"""
Base test framework for DICOMweb conformance testing.

This module provides the foundation for all DICOMweb protocol tests,
defining common functionality, test structure, and reporting mechanisms.
"""

import requests
import json
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging


@dataclass
class TestResult:
    """Represents the result of a single test."""
    test_name: str
    protocol: str  # QIDO, WADO, or STOW
    status: str  # PASS, FAIL, or SKIP
    message: str
    response_time: float
    request_details: Dict[str, Any]
    response_details: Dict[str, Any]
    timestamp: str
    recommendation: Optional[str] = None


class DICOMwebBaseTest(ABC):
    """
    Abstract base class for all DICOMweb conformance tests.
    
    This class provides common functionality for:
    - HTTP request handling with authentication
    - Response validation
    - Test result tracking
    - Error handling
    """
    
    def __init__(self, pacs_url: str, username: str = None, password: str = None, 
                 timeout: int = 30, verbose: bool = False):
        """
        Initialize the base test.
        
        Args:
            pacs_url: Base URL of the PACS server (e.g., https://server/dicomweb)
            username: Optional username for authentication
            password: Optional password for authentication
            timeout: Request timeout in seconds
            verbose: Enable verbose logging
        """
        self.pacs_url = pacs_url.rstrip('/')
        self.username = username
        self.password = password
        self.timeout = timeout
        self.verbose = verbose
        self.test_results: List[TestResult] = []
        
        # Setup logging
        logging.basicConfig(
            level=logging.DEBUG if verbose else logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Setup session with authentication
        self.session = requests.Session()
        if username and password:
            self.session.auth = (username, password)
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Tuple[requests.Response, float]:
        """
        Make an HTTP request to the PACS server.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (relative to pacs_url)
            **kwargs: Additional arguments for requests
            
        Returns:
            Tuple of (response, response_time)
        """
        url = f"{self.pacs_url}/{endpoint.lstrip('/')}"
        start_time = time.time()
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            )
            response_time = time.time() - start_time
            
            self.logger.debug(f"{method} {endpoint} - Status: {response.status_code} - Time: {response_time:.2f}s")
            return response, response_time
            
        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            self.logger.error(f"Request failed: {e}")
            raise
    
    def _validate_response(self, response: requests.Response, 
                          expected_status_codes: List[int] = None) -> bool:
        """
        Validate HTTP response.
        
        Args:
            response: HTTP response object
            expected_status_codes: List of acceptable status codes
            
        Returns:
            True if response is valid
        """
        if expected_status_codes is None:
            expected_status_codes = [200, 201, 204]
        
        return response.status_code in expected_status_codes
    
    def _record_test_result(self, test_name: str, protocol: str, status: str, 
                          message: str, response_time: float, 
                          request_details: Dict, response_details: Dict,
                          recommendation: str = None):
        """
        Record a test result.
        
        Args:
            test_name: Name of the test
            protocol: DICOMweb protocol (QIDO, WADO, STOW)
            status: Test status (PASS, FAIL, SKIP)
            message: Result message
            response_time: Time taken for the request
            request_details: Request information
            response_details: Response information
            recommendation: Optional recommendation for failures
        """
        result = TestResult(
            test_name=test_name,
            protocol=protocol,
            status=status,
            message=message,
            response_time=response_time,
            request_details=request_details,
            response_details=response_details,
            timestamp=datetime.now().isoformat(),
            recommendation=recommendation
        )
        self.test_results.append(result)
        
        # Log result
        if status == "PASS":
            self.logger.info(f"✓ {test_name}: {message}")
        elif status == "FAIL":
            self.logger.error(f"✗ {test_name}: {message}")
            if recommendation:
                self.logger.info(f"  Recommendation: {recommendation}")
        else:  # SKIP
            self.logger.warning(f"⊘ {test_name}: {message}")
    
    def _check_dicomweb_compliance(self, response: requests.Response) -> Tuple[bool, str]:
        """
        Check if response indicates DICOMweb compliance.
        
        Args:
            response: HTTP response object
            
        Returns:
            Tuple of (is_compliant, message)
        """
        # Check for DICOMweb-specific headers
        content_type = response.headers.get('content-type', '')
        
        if 'application/dicom' in content_type or 'application/dicom+json' in content_type:
            return True, "Response has DICOM-compatible content type"
        
        # Check for DICOM tags in response (for JSON responses)
        if 'application/json' in content_type:
            try:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    if isinstance(data[0], dict) and any(
                        tag in data[0] for tag in ['00080005', '00080020', '00080030']
                    ):
                        return True, "Response contains DICOM metadata"
            except json.JSONDecodeError:
                pass
        
        return False, "Response does not appear to contain DICOM data"
    
    @abstractmethod
    def run_tests(self) -> List[TestResult]:
        """
        Run all tests for this protocol.
        
        Returns:
            List of test results
        """
        pass
    
    def get_results_by_status(self, status: str) -> List[TestResult]:
        """Get test results by status."""
        return [r for r in self.test_results if r.status == status]
    
    def get_results_by_protocol(self, protocol: str) -> List[TestResult]:
        """Get test results by protocol."""
        return [r for r in self.test_results if r.protocol == protocol]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of all test results."""
        total = len(self.test_results)
        passed = len(self.get_results_by_status("PASS"))
        failed = len(self.get_results_by_status("FAIL"))
        skipped = len(self.get_results_by_status("SKIP"))
        
        return {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "pass_rate": (passed / total * 100) if total > 0 else 0,
            "protocols_tested": list(set(r.protocol for r in self.test_results))
        }