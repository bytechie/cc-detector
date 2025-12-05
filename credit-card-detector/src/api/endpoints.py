"""
API Endpoints

Clean, focused API endpoint implementations.
"""

import time
import logging
from datetime import datetime
from typing import Dict, Any

from flask import Flask, request, jsonify, g
from werkzeug.exceptions import HTTPException

from ..detector import CreditCardDetector
from ..utils.config import Config
from .schemas import ScanRequest, ScanResponse, HealthResponse, ErrorResponse, Detection
from .metrics import track_request_metrics, record_credit_card_detection, record_scan_duration, initialize_metrics, update_uptime


class CreditCardAPI:
    """Clean API endpoint implementation."""

    def __init__(self, config: Config):
        """
        Initialize API with configuration.

        Args:
            config: Application configuration
        """
        self.config = config
        self.detector = CreditCardDetector(
            validation=config.get('detection.validation.enabled', True),
            card_type_detection=config.get('detection.validation.card_type_detection', False)
        )
        self.logger = self._setup_logging()

        # Initialize metrics if enabled
        if config.get('monitoring.prometheus.enabled', False):
            try:
                initialize_metrics()
                self.start_time = time.time()
                self.logger.info("Prometheus metrics enabled")
            except ImportError:
                self.logger.warning("prometheus_client not available, metrics disabled")
                self.start_time = None
            except Exception as e:
                self.logger.error(f"Failed to initialize metrics: {e}")
                self.start_time = None
        else:
            self.start_time = None

    def _setup_logging(self) -> logging.Logger:
        """Setup API logging."""
        logger = logging.getLogger(__name__)
        logger.setLevel(self.config.get('monitoring.logging_level', 'INFO'))
        return logger

    def create_endpoints(self, app: Flask):
        """Register all API endpoints."""

        @app.route('/', methods=['GET'])
        @track_request_metrics
        def index():
            """Root endpoint with service information."""
            # Update uptime metric
            if self.start_time:
                update_uptime(self.start_time)

            return jsonify({
                "service": "Credit Card Detector",
                "version": "2.0.0",
                "status": "running",
                "timestamp": datetime.utcnow().isoformat(),
                "endpoints": {
                    "/health": "Health check",
                    "/scan": "Credit card detection (POST)",
                    "/metrics": "Prometheus metrics (if enabled)"
                }
            })

        @app.route('/health', methods=['GET'])
        @track_request_metrics
        def health():
            """Health check endpoint."""
            try:
                # Update uptime metric
                if self.start_time:
                    update_uptime(self.start_time)

                # Test detector functionality
                test_result = self.detector.detect("test")

                health_response = HealthResponse(
                    status="healthy",
                    service="Credit Card Detector",
                    version="2.0.0",
                    timestamp=datetime.utcnow().isoformat(),
                    components={
                        "detector": "healthy",
                        "database": "not_used",
                        "memory": "ok"
                    }
                )

                return jsonify(health_response.to_dict()), 200

            except Exception as e:
                self.logger.error(f"Health check failed: {str(e)}")
                health_response = HealthResponse(
                    status="unhealthy",
                    service="Credit Card Detector",
                    version="2.0.0",
                    timestamp=datetime.utcnow().isoformat(),
                    components={"detector": f"error: {str(e)}"}
                )
                return jsonify(health_response.to_dict()), 503

        @app.route('/scan', methods=['POST'])
        @track_request_metrics
        def scan():
            """Main credit card detection endpoint."""
            start_time = time.time()

            try:
                # Update uptime metric
                if self.start_time:
                    update_uptime(self.start_time)

                # Parse request
                data = request.get_json()
                if not data:
                    return jsonify({"error": "Invalid JSON"}), 400

                # Validate request
                scan_request = ScanRequest(
                    text=data.get('text', ''),
                    redact_mode=data.get('redact_mode', 'redact'),
                    validation=data.get('validation', True),
                    card_type_detection=data.get('card_type_detection', False)
                )

                # Perform scan
                scan_result = self.detector.scan(
                    scan_request.text,
                    redact_mode=scan_request.redact_mode
                )

                # Convert detections to schema objects
                detections = [
                    Detection(
                        number=d.number,
                        start=d.start,
                        end=d.end,
                        raw=d.raw,
                        valid=d.valid,
                        card_type=d.card_type
                    )
                    for d in scan_result.detections
                ]

                # Record metrics for each detection
                for detection in scan_result.detections:
                    record_credit_card_detection({
                        'valid': detection.valid,
                        'card_type': detection.card_type or 'unknown'
                    })

                # Record scan duration metric
                scan_duration = time.time() - start_time
                record_scan_duration(scan_duration, scan_result.cards_found)

                # Create response
                response = ScanResponse(
                    detections=detections,
                    redacted=scan_result.redacted,
                    scan_duration_seconds=scan_result.scan_duration,
                    cards_found=scan_result.cards_found,
                    valid_cards=scan_result.valid_cards,
                    timestamp=datetime.utcnow().isoformat()
                )

                # Log request
                self.logger.info(f"Scan completed: {response.cards_found} cards found in {response.scan_duration_seconds:.3f}s")

                return jsonify(response.to_dict()), 200

            except ValueError as e:
                # Validation errors
                error_response = ErrorResponse(
                    error="validation_error",
                    message=str(e),
                    timestamp=datetime.utcnow().isoformat()
                )
                return jsonify(error_response.to_dict()), 400

            except Exception as e:
                # Unexpected errors
                self.logger.error(f"Scan error: {str(e)}")
                error_response = ErrorResponse(
                    error="internal_error",
                    message="An internal error occurred",
                    timestamp=datetime.utcnow().isoformat()
                )
                return jsonify(error_response.to_dict()), 500

        # Optional metrics endpoint
        if self.config.get('monitoring.prometheus.enabled', False):
            self._add_metrics_endpoint(app)

        # Error handlers
        self._setup_error_handlers(app)

    def _add_metrics_endpoint(self, app: Flask):
        """Add Prometheus metrics endpoint if available."""
        try:
            from .metrics import get_metrics

            @app.route('/metrics', methods=['GET'])
            def metrics():
                """Prometheus metrics endpoint."""
                return get_metrics()

            self.logger.info("Prometheus metrics endpoint enabled")

        except ImportError:
            self.logger.warning("Metrics module not available, metrics endpoint disabled")
        except Exception as e:
            self.logger.error(f"Failed to add metrics endpoint: {e}")

    def _setup_error_handlers(self, app: Flask):
        """Setup global error handlers."""

        @app.errorhandler(404)
        def not_found(error):
            """Handle 404 errors."""
            error_response = ErrorResponse(
                error="not_found",
                message="Endpoint not found",
                timestamp=datetime.utcnow().isoformat()
            )
            return jsonify(error_response.to_dict()), 404

        @app.errorhandler(405)
        def method_not_allowed(error):
            """Handle 405 errors."""
            error_response = ErrorResponse(
                error="method_not_allowed",
                message="HTTP method not allowed",
                timestamp=datetime.utcnow().isoformat()
            )
            return jsonify(error_response.to_dict()), 405

        @app.errorhandler(413)
        def payload_too_large(error):
            """Handle 413 errors."""
            error_response = ErrorResponse(
                error="payload_too_large",
                message="Request payload too large",
                timestamp=datetime.utcnow().isoformat()
            )
            return jsonify(error_response.to_dict()), 413

        @app.errorhandler(500)
        def internal_error(error):
            """Handle 500 errors."""
            self.logger.error(f"Internal server error: {str(error)}")
            error_response = ErrorResponse(
                error="internal_error",
                message="Internal server error",
                timestamp=datetime.utcnow().isoformat()
            )
            return jsonify(error_response.to_dict()), 500


def create_app(config: Config = None) -> Flask:
    """
    Create and configure Flask application.

    Args:
        config: Application configuration

    Returns:
        Configured Flask app
    """
    if config is None:
        from ..utils.config import load_config
        config = load_config()

    app = Flask(__name__)

    # Configure Flask app
    app.config['JSON_SORT_KEYS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024  # 1MB limit

    # Create API instance
    api = CreditCardAPI(config)

    # Register endpoints
    api.create_endpoints(app)

    return app