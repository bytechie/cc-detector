#!/usr/bin/env python3
"""
Webhook Server Example for Credit Card Detector
Provides HTTP endpoints for integration with web applications.
"""

from flask import Flask, request, jsonify
import requests
import logging
from datetime import datetime
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CreditCardWebhookServer:
    """Webhook server for Credit Card Detector integration"""

    def __init__(self, detector_url: str = "http://localhost:5000"):
        self.detector_url = detector_url
        self.app = Flask(__name__)
        self.setup_routes()
        self.scan_count = 0

    def setup_routes(self):
        """Setup webhook endpoints"""

        @self.app.route('/', methods=['GET'])
        def index():
            """Root endpoint with API info"""
            return jsonify({
                "service": "Credit Card Detector Webhook Server",
                "version": "1.0.0",
                "endpoints": {
                    "POST /scan": "Scan text for credit cards",
                    "POST /batch-scan": "Scan multiple texts",
                    "GET /stats": "Service statistics",
                    "GET /health": "Health check"
                },
                "timestamp": datetime.now().isoformat()
            })

        @self.app.route('/scan', methods=['POST'])
        def scan_text():
            """Scan text for credit cards"""
            try:
                data = request.get_json()
                text = data.get('text', '')

                if not text:
                    return jsonify({"error": "No text provided"}), 400

                # Call the detector
                result = self.call_detector(text)

                # Add metadata
                result['_webhook_info'] = {
                    'timestamp': datetime.now().isoformat(),
                    'source_ip': request.remote_addr,
                    'user_agent': request.headers.get('User-Agent'),
                    'scan_id': f"scan_{self.scan_count}"
                }

                self.scan_count += 1
                logger.info(f"Scan #{self.scan_count}: Found {len(result.get('detections', []))} cards")

                return jsonify(result)

            except Exception as e:
                logger.error(f"Error in scan endpoint: {str(e)}")
                return jsonify({"error": str(e)}), 500

        @self.app.route('/batch-scan', methods=['POST'])
        def batch_scan():
            """Batch scan multiple texts"""
            try:
                data = request.get_json()
                texts = data.get('texts', [])

                if not texts:
                    return jsonify({"error": "No texts provided"}), 400

                results = []
                total_cards = 0

                for i, text in enumerate(texts):
                    result = self.call_detector(text)
                    result['batch_index'] = i
                    results.append(result)
                    total_cards += len(result.get('detections', []))

                summary = {
                    "total_texts": len(texts),
                    "total_cards_found": total_cards,
                    "scan_timestamp": datetime.now().isoformat()
                }

                return jsonify({
                    "results": results,
                    "summary": summary
                })

            except Exception as e:
                logger.error(f"Error in batch scan endpoint: {str(e)}")
                return jsonify({"error": str(e)}), 500

        @self.app.route('/stats', methods=['GET'])
        def get_stats():
            """Get service statistics"""
            return jsonify({
                "scans_completed": self.scan_count,
                "detector_status": self.check_detector_health(),
                "service_uptime": self.get_service_uptime(),
                "timestamp": datetime.now().isoformat()
            })

        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            detector_healthy = self.check_detector_health()
            return jsonify({
                "status": "healthy" if detector_healthy else "unhealthy",
                "detector_health": detector_healthy,
                "service": "webhook_server",
                "scans_completed": self.scan_count,
                "timestamp": datetime.now().isoformat()
            })

    def call_detector(self, text: str) -> dict:
        """Call the credit card detector service"""
        try:
            response = requests.post(
                f"{self.detector_url}/scan",
                json={"text": text},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling detector: {str(e)}")
            return {
                "error": f"Detector service unavailable: {str(e)}",
                "detections": [],
                "redacted": text
            }

    def check_detector_health(self) -> bool:
        """Check if the detector service is healthy"""
        try:
            response = requests.get(f"{self.detector_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False

    def get_service_uptime(self) -> str:
        """Get service uptime (simplified)"""
        # In a real implementation, you'd track start time
        return "Unknown"

    def run(self, port: int = 8080, host: str = '0.0.0.0', debug: bool = False):
        """Run the webhook server"""
        logger.info(f"Starting webhook server on {host}:{port}")
        logger.info(f"Credit Card Detector at: {self.detector_url}")
        logger.info("Available endpoints:")
        logger.info("  POST /scan - Single text scanning")
        logger.info("  POST /batch-scan - Batch text scanning")
        logger.info("  GET /stats - Service statistics")
        logger.info("  GET /health - Health check")

        self.app.run(host=host, port=port, debug=debug)

# Configuration and usage
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Credit Card Detector Webhook Server")
    parser.add_argument("--port", type=int, default=8080, help="Port to run on")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--detector-url", type=str, default="http://localhost:5000",
                       help="URL of the detector service")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()

    server = CreditCardWebhookServer(detector_url=args.detector_url)
    server.run(port=args.port, host=args.host, debug=args.debug)