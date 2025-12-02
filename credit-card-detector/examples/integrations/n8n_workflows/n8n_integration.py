#!/usr/bin/env python3
"""
n8n Integration for Credit Card Detector
Provides webhook endpoints and tools for n8n workflow integration
"""

from flask import Flask, request, jsonify
import requests
import logging
from typing import Dict, Any
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class N8NIntegration:
    """n8n Integration Service for Credit Card Detector"""

    def __init__(self, detector_url: str = "http://localhost:5000"):
        self.detector_url = detector_url
        self.app = Flask(__name__)
        self.setup_routes()

    def setup_routes(self):
        """Setup Flask routes for n8n integration"""

        @self.app.route('/webhook/scan', methods=['POST'])
        def scan_text():
            """Webhook endpoint for text scanning"""
            try:
                data = request.get_json()
                text = data.get('text', '')

                if not text:
                    return jsonify({"error": "No text provided"}), 400

                # Call the credit card detector
                result = self.scan_credit_cards(text)

                # Add n8n metadata
                result['_n8n_metadata'] = {
                    'webhook': 'scan',
                    'timestamp': data.get('timestamp'),
                    'workflow_id': data.get('workflow_id'),
                    'node_id': data.get('node_id')
                }

                return jsonify(result)

            except Exception as e:
                logger.error(f"Error in scan webhook: {str(e)}")
                return jsonify({"error": str(e)}), 500

        @self.app.route('/webhook/batch-scan', methods=['POST'])
        def batch_scan():
            """Webhook endpoint for batch text scanning"""
            try:
                data = request.get_json()
                texts = data.get('texts', [])

                if not texts:
                    return jsonify({"error": "No texts provided"}), 400

                results = []
                for i, text in enumerate(texts):
                    result = self.scan_credit_cards(text)
                    result['batch_index'] = i
                    results.append(result)

                return jsonify({
                    "results": results,
                    "total_texts": len(texts),
                    "texts_with_cards": sum(1 for r in results if r.get('detections'))
                })

            except Exception as e:
                logger.error(f"Error in batch scan webhook: {str(e)}")
                return jsonify({"error": str(e)}), 500

        @self.app.route('/tools/scan', methods=['POST'])
        def n8n_tool():
            """n8n tool endpoint for structured tool calls"""
            try:
                # n8n tool format
                data = request.get_json()
                tool_name = data.get('tool')
                parameters = data.get('parameters', {})

                if tool_name == 'scan_credit_cards':
                    text = parameters.get('text', '')
                    result = self.scan_credit_cards(text)

                    return jsonify({
                        "tool": tool_name,
                        "result": result,
                        "success": True
                    })
                else:
                    return jsonify({"error": f"Unknown tool: {tool_name}"}), 400

            except Exception as e:
                logger.error(f"Error in tool endpoint: {str(e)}")
                return jsonify({"error": str(e)}), 500

        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Health check for n8n monitoring"""
            detector_health = self.check_detector_health()
            return jsonify({
                "status": "healthy" if detector_health else "unhealthy",
                "detector_health": detector_health,
                "service": "n8n_integration"
            })

    def scan_credit_cards(self, text: str) -> Dict[str, Any]:
        """Scan text for credit cards using the main detector service"""
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
        """Check if the main detector service is healthy"""
        try:
            response = requests.get(f"{self.detector_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False

    def run(self, port: int = 8080, host: str = '0.0.0.0'):
        """Run the n8n integration service"""
        logger.info(f"Starting n8n integration service on {host}:{port}")
        logger.info(f"Credit Card Detector at: {self.detector_url}")
        logger.info("Available endpoints:")
        logger.info("  POST /webhook/scan - Single text scanning")
        logger.info("  POST /webhook/batch-scan - Batch text scanning")
        logger.info("  POST /tools/scan - n8n tool interface")
        logger.info("  GET /health - Health check")

        self.app.run(host=host, port=port, debug=False)

# n8n Workflow Configuration Examples
N8N_WORKFLOW_EXAMPLES = {
    "simple_scan": {
        "name": "Credit Card Scan Workflow",
        "nodes": [
            {
                "id": "1",
                "name": "Manual Trigger",
                "type": "n8n-nodes-base.manualTrigger",
                "position": [250, 300]
            },
            {
                "id": "2",
                "name": "Text Input",
                "type": "n8n-nodes-base.set",
                "position": [450, 300],
                "parameters": {
                    "values": {
                        "string": [
                            {
                                "name": "text",
                                "value": "Enter your text here for credit card scanning"
                            }
                        ]
                    }
                }
            },
            {
                "id": "3",
                "name": "Scan Credit Cards",
                "type": "n8n-nodes-base.httpRequest",
                "position": [650, 300],
                "parameters": {
                    "url": "http://localhost:8080/webhook/scan",
                    "method": "POST",
                    "jsonParameters": True,
                    "jsonBody": {
                        "text": "={{$json.text}}"
                    }
                }
            },
            {
                "id": "4",
                "name": "Process Results",
                "type": "n8n-nodes-base.if",
                "position": [850, 300],
                "parameters": {
                    "conditions": {
                        "options": {
                            "caseSensitive": True,
                            "leftValue": "",
                            "typeValidation": "strict"
                        },
                        "conditions": [
                            {
                                "leftValue": "={{$json.detections}}",
                                "rightValue": "",
                                "operator": {
                                    "type": "array",
                                    "operation": "notEmpty"
                                }
                            }
                        ]
                    }
                }
            }
        ]
    },

    "batch_processing": {
        "name": "Batch Credit Card Processing",
        "nodes": [
            {
                "id": "1",
                "name": "CSV File Reader",
                "type": "n8n-nodes-base.readCsvFile",
                "position": [250, 300]
            },
            {
                "id": "2",
                "name": "Batch Scanner",
                "type": "n8n-nodes-base.httpRequest",
                "position": [450, 300],
                "parameters": {
                    "url": "http://localhost:8080/webhook/batch-scan",
                    "method": "POST",
                    "jsonParameters": True,
                    "jsonBody": {
                        "texts": "={{$json}}"
                    }
                }
            }
        ]
    }
}

if __name__ == "__main__":
    # Example usage
    integration = N8NIntegration()

    # You can run this as a separate service:
    # integration.run(port=8080)

    # Or import and use in your existing Flask app
    print("n8n Integration for Credit Card Detector")
    print("========================================")
    print("\nTo use this integration:")
    print("1. Start this service: python n8n_integration.py")
    print("2. Configure n8n workflows to call the webhook endpoints")
    print("3. Use the workflow examples in N8N_WORKFLOW_EXAMPLES")
    print("\nEndpoints:")
    print("- POST /webhook/scan - Single text scanning")
    print("- POST /webhook/batch-scan - Batch processing")
    print("- POST /tools/scan - n8n tool interface")
    print("- GET /health - Health monitoring")