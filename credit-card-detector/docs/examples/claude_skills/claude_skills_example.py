#!/usr/bin/env python3
"""
Example: Integrating Credit Card Detector with Claude Skills
This demonstrates how to create a Claude skill that uses the Credit Card Detector API.
"""

import requests
import json
from typing import Dict, Any, List

class CreditCardDetectorSkill:
    """Claude Skill for Credit Card Detection"""

    def __init__(self, api_url: str = "http://localhost:5000"):
        self.api_url = api_url
        self.session = requests.Session()

    def detect_credit_cards(self, text: str) -> Dict[str, Any]:
        """
        Detect credit cards in text using the Credit Card Detector API

        Args:
            text: Text to scan for credit cards

        Returns:
            Detection results with redacted text
        """
        try:
            response = self.session.post(
                f"{self.api_url}/scan",
                json={"text": text},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": f"API request failed: {str(e)}",
                "detections": [],
                "redacted": text
            }

    def analyze_text_security(self, text: str) -> Dict[str, Any]:
        """
        Comprehensive security analysis of text

        Args:
            text: Text to analyze

        Returns:
            Security analysis results
        """
        # Get credit card detections
        detection_result = self.detect_credit_cards(text)

        # Add additional analysis
        analysis = {
            "security_score": self._calculate_security_score(text, detection_result),
            "risk_level": self._assess_risk_level(detection_result),
            "recommendations": self._generate_recommendations(detection_result),
            "detection_summary": {
                "cards_found": len(detection_result.get("detections", [])),
                "valid_cards": len([d for d in detection_result.get("detections", []) if d.get("valid", False)]),
                "scan_duration": detection_result.get("scan_duration_seconds", 0)
            }
        }

        return {
            **detection_result,
            "security_analysis": analysis
        }

    def _calculate_security_score(self, text: str, detection_result: Dict) -> int:
        """Calculate security score (0-100)"""
        detections = detection_result.get("detections", [])
        if not detections:
            return 100  # No credit cards found

        # Penalize for each credit card found
        base_score = 100
        penalty_per_card = 25

        score = base_score - (len(detections) * penalty_per_card)
        return max(0, score)

    def _assess_risk_level(self, detection_result: Dict) -> str:
        """Assess risk level based on detections"""
        detections = detection_result.get("detections", [])

        if not detections:
            return "LOW"
        elif len(detections) == 1:
            return "MEDIUM"
        else:
            return "HIGH"

    def _generate_recommendations(self, detection_result: Dict) -> List[str]:
        """Generate security recommendations"""
        detections = detection_result.get("detections", [])
        recommendations = []

        if detections:
            recommendations.extend([
                "Remove or redact credit card numbers from the text",
                "Use tokenization for payment processing",
                "Implement proper data encryption at rest",
                "Review data access controls"
            ])
        else:
            recommendations.append("No credit card data detected - text appears safe")

        return recommendations

# Claude Skill Function
def credit_card_detector_skill(text: str, analysis_type: str = "basic") -> Dict[str, Any]:
    """
    Claude skill function for credit card detection

    Args:
        text: Text to analyze for credit cards
        analysis_type: Type of analysis - "basic" or "comprehensive"

    Returns:
        Detection and analysis results
    """
    detector = CreditCardDetectorSkill()

    if analysis_type == "comprehensive":
        return detector.analyze_text_security(text)
    else:
        return detector.detect_credit_cards(text)

# Example usage as a Claude skill
if __name__ == "__main__":
    # Test the skill
    test_text = "Customer John Doe has Visa card 4111111111111111 and MasterCard 5555555555554444"

    print("=== Claude Skills Integration Example ===\n")

    # Basic detection
    print("1. Basic Credit Card Detection:")
    basic_result = credit_card_detector_skill(test_text, "basic")
    print(json.dumps(basic_result, indent=2))

    print("\n" + "="*50 + "\n")

    # Comprehensive analysis
    print("2. Comprehensive Security Analysis:")
    comprehensive_result = credit_card_detector_skill(test_text, "comprehensive")
    print(json.dumps(comprehensive_result, indent=2))