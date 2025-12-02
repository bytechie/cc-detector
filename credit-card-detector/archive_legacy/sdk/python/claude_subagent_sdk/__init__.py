"""
Credit Card Detector Python SDK

A comprehensive Python client library for the Credit Card Detector API.
Provides easy integration with resource-aware detection, adaptive skills,
and all advanced features of the platform.
"""

import json
import logging
import time
import uuid
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


@dataclass
class Detection:
    """Represents a credit card detection result"""
    start: int
    end: int
    raw: str
    number: str
    valid: bool
    confidence: float
    card_type: Optional[str] = None
    skill_source: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Detection':
        return cls(
            start=data.get('start', 0),
            end=data.get('end', 0),
            raw=data.get('raw', ''),
            number=data.get('number', ''),
            valid=data.get('valid', False),
            confidence=data.get('confidence', 0.0),
            card_type=data.get('card_type'),
            skill_source=data.get('skill_source')
        )

    def to_dict(self) -> Dict[str, Any]:
        result = {
            'start': self.start,
            'end': self.end,
            'raw': self.raw,
            'number': self.number,
            'valid': self.valid,
            'confidence': self.confidence
        }
        if self.card_type:
            result['card_type'] = self.card_type
        if self.skill_source:
            result['skill_source'] = self.skill_source
        return result


@dataclass
class ScanResult:
    """Result of a scan operation"""
    detections: List[Detection]
    redacted: str
    stats: Dict[str, Any]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScanResult':
        detections = [Detection.from_dict(d) for d in data.get('detections', [])]
        return cls(
            detections=detections,
            redacted=data.get('redacted', ''),
            stats=data.get('stats', {})
        )

    def has_detections(self) -> bool:
        """Check if any detections were found"""
        return len(self.detections) > 0

    def get_card_numbers(self) -> List[str]:
        """Get all detected card numbers"""
        return [d.number for d in self.detections if d.valid]

    def count_by_type(self) -> Dict[str, int]:
        """Count detections by card type"""
        counts = {}
        for detection in self.detections:
            card_type = detection.card_type or 'unknown'
            counts[card_type] = counts.get(card_type, 0) + 1
        return counts


@dataclass
class BatchScanResult:
    """Result of a batch scan operation"""
    results: List[Dict[str, Any]]
    summary: Dict[str, Any]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BatchScanResult':
        return cls(
            results=data.get('results', []),
            summary=data.get('summary', {})
        )

    def get_successful_results(self) -> List[Dict[str, Any]]:
        """Get only successful scan results"""
        return [r for r in self.results if 'error' not in r]

    def get_total_detections(self) -> int:
        """Get total number of detections across all results"""
        return sum(
            len(result.get('detections', []))
            for result in self.results
            if 'detections' in result
        )


class CreditCardDetectorError(Exception):
    """Base exception for the Credit Card Detector SDK"""

    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}


class RateLimitError(CreditCardDetectorError):
    """Raised when rate limit is exceeded"""
    pass


class AuthenticationError(CreditCardDetectorError):
    """Raised when authentication fails"""
    pass


class ResourceConstraintError(CreditCardDetectorError):
    """Raised when system is under resource constraints"""
    pass


class CreditCardDetector:
    """Main client class for the Credit Card Detector API"""

    def __init__(
        self,
        api_key: str = None,
        base_url: str = "http://localhost:5000",
        timeout: int = 30,
        max_retries: int = 3,
        retry_backoff_factor: float = 0.3,
        auto_retry: bool = True,
        enable_monitoring: bool = False
    ):
        """
        Initialize the Credit Card Detector client.

        Args:
            api_key: API key for authentication
            base_url: Base URL of the API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
            retry_backoff_factor: Backoff factor for retries
            auto_retry: Enable automatic retries for transient errors
            enable_monitoring: Enable request/response monitoring
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.auto_retry = auto_retry
        self.enable_monitoring = enable_monitoring

        # Set up session with retry logic
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=retry_backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS", "TRACE"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Monitoring callbacks
        self._request_callbacks: List[Callable] = []
        self._response_callbacks: List[Callable] = []

        logger.debug(f"Initialized CreditCardDetector client for {self.base_url}")

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Dict[str, Any] = None,
        params: Dict[str, Any] = None,
        headers: Dict[str, str] = None
    ) -> requests.Response:
        """Make HTTP request with error handling and retries"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        request_headers = {
            'Content-Type': 'application/json',
            'X-Request-ID': str(uuid.uuid4())
        }

        if self.api_key:
            request_headers['X-API-Key'] = self.api_key

        if headers:
            request_headers.update(headers)

        # Monitor request if enabled
        if self.enable_monitoring and self._request_callbacks:
            for callback in self._request_callbacks:
                callback(method, url, data, headers)

        start_time = time.time()

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=request_headers,
                timeout=self.timeout
            )

            # Monitor response if enabled
            if self.enable_monitoring and self._response_callbacks:
                duration = time.time() - start_time
                for callback in self._response_callbacks:
                    callback(response, duration)

            self._handle_response_errors(response)
            return response

        except requests.exceptions.Timeout:
            raise CreditCardDetectorError("Request timeout", "REQUEST_TIMEOUT")
        except requests.exceptions.ConnectionError:
            raise CreditCardDetectorError("Connection error", "CONNECTION_ERROR")
        except requests.exceptions.RequestException as e:
            raise CreditCardDetectorError(f"Request failed: {str(e)}", "REQUEST_FAILED")

    def _handle_response_errors(self, response: requests.Response):
        """Handle HTTP response errors"""
        if response.status_code == 401:
            raise AuthenticationError("Invalid API key")
        elif response.status_code == 429:
            raise RateLimitError("Rate limit exceeded", "RATE_LIMIT_EXCEEDED")
        elif response.status_code == 413:
            raise CreditCardDetectorError("Request entity too large", "REQUEST_TOO_LARGE")
        elif response.status_code == 503:
            raise ResourceConstraintError("Service unavailable - resource constraints", "RESOURCE_CONSTRAINTS")
        elif response.status_code >= 400:
            try:
                error_data = response.json()
                error_message = error_data.get('error', {}).get('message', 'Unknown error')
                error_code = error_data.get('error', {}).get('code', 'UNKNOWN_ERROR')
                details = error_data.get('error', {}).get('details', {})
                raise CreditCardDetectorError(error_message, error_code, details)
            except (ValueError, KeyError):
                raise CreditCardDetectorError(f"HTTP {response.status_code}: {response.text}", "HTTP_ERROR")

    def scan(
        self,
        text: str,
        include_metadata: bool = False,
        confidence_threshold: float = None
    ) -> ScanResult:
        """
        Scan text for credit card numbers.

        Args:
            text: Text to scan
            include_metadata: Include additional metadata in response
            confidence_threshold: Minimum confidence threshold for detections

        Returns:
            ScanResult containing detections and metadata
        """
        data = {"text": text}

        if include_metadata or confidence_threshold is not None:
            data["options"] = {}
            if include_metadata:
                data["options"]["include_metadata"] = True
            if confidence_threshold is not None:
                data["options"]["confidence_threshold"] = confidence_threshold

        response = self._make_request("POST", "/scan", data)
        result_data = response.json()

        return ScanResult.from_dict(result_data)

    def scan_batch(
        self,
        texts: List[str],
        parallel: bool = True,
        max_workers: int = 4
    ) -> BatchScanResult:
        """
        Scan multiple texts for credit card numbers.

        Args:
            texts: List of texts to scan
            parallel: Enable parallel processing
            max_workers: Maximum number of parallel workers

        Returns:
            BatchScanResult containing all scan results
        """
        data = {
            "texts": texts,
            "options": {
                "parallel": parallel,
                "max_workers": max_workers
            }
        }

        response = self._make_request("POST", "/scan-batch", data)
        result_data = response.json()

        return BatchScanResult.from_dict(result_data)

    def scan_enhanced(
        self,
        text: str,
        use_all_skills: bool = True,
        include_external: bool = True,
        resource_aware: bool = True,
        max_processing_time: int = 30
    ) -> ScanResult:
        """
        Scan text using all available adaptive skills and optimization.

        Args:
            text: Text to scan
            use_all_skills: Use all available adaptive skills
            include_external: Include external/integrated skills
            resource_aware: Enable resource-aware processing
            max_processing_time: Maximum processing time in seconds

        Returns:
            Enhanced ScanResult with additional metadata
        """
        data = {"text": text}

        options = {
            "use_all_skills": use_all_skills,
            "include_external": include_external,
            "resource_aware": resource_aware
        }

        if max_processing_time != 30:
            options["max_processing_time"] = max_processing_time

        data["options"] = options

        response = self._make_request("POST", "/scan-enhanced", data)
        result_data = response.json()

        return ScanResult.from_dict(result_data)

    def train_skill(
        self,
        examples: List[Dict[str, Any]],
        description: str = None,
        quality_threshold: float = None,
        auto_deploy: bool = True
    ) -> Dict[str, Any]:
        """
        Train new adaptive skills from examples.

        Args:
            examples: Training examples
            description: Description of what to detect
            quality_threshold: Minimum quality threshold
            auto_deploy: Auto-deploy successful skills

        Returns:
            Training result with skill information
        """
        data = {
            "examples": examples
        }

        if description:
            data["description"] = description
        if quality_threshold is not None:
            data["options"] = {"quality_threshold": quality_threshold}
        if not auto_deploy:
            data["options"] = data.get("options", {})
            data["options"]["auto_deploy"] = False

        response = self._make_request("POST", "/train", data)
        return response.json()

    def list_skills(self) -> Dict[str, Any]:
        """
        List all available adaptive skills.

        Returns:
            Skills information
        """
        response = self._make_request("GET", "/skills")
        return response.json()

    def get_skill_performance(self) -> Dict[str, Any]:
        """
        Get performance metrics for all skills.

        Returns:
            Performance metrics
        """
        response = self._make_request("GET", "/skill-performance")
        return response.json()

    def submit_feedback(
        self,
        input_text: str,
        skill_name: str,
        feedback_type: str,
        expected_detections: List[Dict[str, Any]] = None,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Submit feedback to improve skill performance.

        Args:
            input_text: The original text
            skill_name: Name of the skill
            feedback_type: Type of feedback (false_positive, false_negative, correct)
            expected_detections: Expected detection results
            context: Additional context information

        Returns:
            Feedback submission result
        """
        data = {
            "input_text": input_text,
            "skill_name": skill_name,
            "feedback_type": feedback_type
        }

        if expected_detections:
            data["expected_detections"] = expected_detections
        if context:
            data["context"] = context

        response = self._make_request("POST", "/feedback", data)
        return response.json()

    def get_resources(self) -> Dict[str, Any]:
        """
        Get current system resource usage.

        Returns:
            Resource monitoring information
        """
        response = self._make_request("GET", "/resource-monitor")
        return response.json()

    def get_health(self) -> Dict[str, Any]:
        """
        Get comprehensive health status.

        Returns:
            Health status information
        """
        response = self._make_request("GET", "/health")
        return response.json()

    def benchmark(
        self,
        texts: List[str],
        iterations: int = 1
    ) -> Dict[str, Any]:
        """
        Benchmark different processing strategies.

        Args:
            texts: Test texts
            iterations: Number of iterations

        Returns:
            Benchmark results
        """
        data = {
            "texts": texts,
            "iterations": iterations
        }

        response = self._make_request("POST", "/benchmark-processing", data)
        return response.json()

    def add_request_callback(self, callback: Callable):
        """Add callback to monitor requests"""
        self._request_callbacks.append(callback)

    def add_response_callback(self, callback: Callable):
        """Add callback to monitor responses"""
        self._response_callbacks.append(callback)

    def close(self):
        """Close the session and cleanup resources"""
        self.session.close()
        logger.debug("Closed CreditCardDetector client session")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


class AsyncCreditCardDetector:
    """
    Async wrapper for the Credit Card Detector client.

    Provides the same interface but with async support for better performance
    in asynchronous applications.
    """

    def __init__(self, **kwargs):
        """Initialize async client"""
        import asyncio
        self._loop = asyncio.get_event_loop()
        self._detector = CreditCardDetector(**kwargs)

    async def scan(self, *args, **kwargs):
        """Async version of scan method"""
        return await self._run_async(self._detector.scan, *args, **kwargs)

    async def scan_batch(self, *args, **kwargs):
        """Async version of scan_batch method"""
        return await self._run_async(self._detector.scan_batch, *args, **kwargs)

    async def scan_enhanced(self, *args, **kwargs):
        """Async version of scan_enhanced method"""
        return await self._run_async(self._detector.scan_enhanced, *args, **kwargs)

    async def _run_async(self, func, *args, **kwargs):
        """Run synchronous function in executor"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, func, *args, **kwargs)

    async def close(self):
        """Close the async client"""
        await self._run_async(self._detector.close)

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()


# Convenience function for quick usage
def quick_scan(
    text: str,
    api_key: str = None,
    base_url: str = "http://localhost:5000"
) -> ScanResult:
    """
    Quick scan function for one-off usage.

    Args:
        text: Text to scan
        api_key: API key (optional)
        base_url: Base URL (optional)

    Returns:
        ScanResult with detections
    """
    with CreditCardDetector(api_key=api_key, base_url=base_url) as detector:
        return detector.scan(text)


# Example usage monitoring functions
def log_requests(method: str, url: str, data: Dict[str, Any], headers: Dict[str, str]):
    """Example request logging callback"""
    logger.info(f"API Request: {method} {url}")
    logger.debug(f"Data: {json.dumps(data, indent=2)}")


def log_responses(response: requests.Response, duration: float):
    """Example response logging callback"""
    logger.info(f"API Response: {response.status_code} ({duration:.3f}s)")
    logger.debug(f"Response: {response.text[:200]}...")


# Example rate limiting monitor
class RateLimiter:
    """Simple rate limiter for API calls"""

    def __init__(self, max_calls: int, time_window: int):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []

    def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        now = time.time()

        # Remove old calls outside the time window
        self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]

        if len(self.calls) >= self.max_calls:
            sleep_time = self.time_window - (now - self.calls[0])
            if sleep_time > 0:
                logger.info(f"Rate limit reached, waiting {sleep_time:.2f} seconds")
                time.sleep(sleep_time)

        self.calls.append(now)