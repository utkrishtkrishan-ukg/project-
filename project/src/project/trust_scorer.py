#!/usr/bin/env python
"""
VERITAS Trust Scoring System
Handles the generation and management of trust certificates and scores.
"""

import json
from datetime import datetime
from typing import Dict, Any, List
import os


class TrustScorer:
    """
    VERITAS Trust Scoring System
    Generates comprehensive trust certificates based on Guardian Agent analyses.
    """

    def __init__(self):
        self.trust_history = []

    def calculate_overall_score(self, agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate overall trust score from individual agent results.

        Args:
            agent_results: Dictionary containing results from all Guardian Agents

        Returns:
            Dictionary with calculated trust scores and decision
        """
        # Extract individual scores
        privacy_score = agent_results.get("privacy_score", 100)
        bias_score = agent_results.get("bias_score", 100)
        transparency_score = agent_results.get("transparency_score", 100)
        ethics_score = agent_results.get("ethics_score", 100)

        # Weighted scoring - Ethics and Privacy have higher weights
        weights = {"privacy": 0.25, "bias": 0.20, "transparency": 0.20, "ethics": 0.35}

        overall_score = (
            privacy_score * weights["privacy"]
            + bias_score * weights["bias"]
            + transparency_score * weights["transparency"]
            + ethics_score * weights["ethics"]
        )

        # Determine decision based on scores
        decision = self._make_decision(overall_score, agent_results)

        return {
            "overall_trust_score": round(overall_score, 1),
            "individual_scores": {
                "privacy": privacy_score,
                "bias": bias_score,
                "transparency": transparency_score,
                "ethics": ethics_score,
            },
            "decision": decision,
            "weight_distribution": weights,
        }

    def _make_decision(
        self, overall_score: float, agent_results: Dict[str, Any]
    ) -> str:
        """
        Determine whether to proceed, warn, or block based on trust score and specific alerts.

        Args:
            overall_score: Calculated overall trust score
            agent_results: Individual agent results

        Returns:
            Decision: "proceed", "warn", or "block"
        """
        # Block for critical issues
        if agent_results.get("harm_detected", False):
            return "block"
        if agent_results.get("pii_detected", False):
            return "block"
        if agent_results.get("crisis_resources_needed", False):
            return "block"

        # Warn for moderate issues
        if overall_score < 70:
            return "warn"
        if agent_results.get("bias_score", 100) < 60:
            return "warn"
        if agent_results.get("transparency_score", 100) < 65:
            return "warn"

        # Proceed for good scores
        if overall_score >= 85:
            return "proceed"

        # Default to warn for moderate scores
        return "warn"

    def generate_trust_certificate(
        self, user_input: str, ai_response: str, agent_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive trust certificate.

        Args:
            user_input: Original user input
            ai_response: AI response to be verified
            agent_results: Results from all Guardian Agents

        Returns:
            Complete trust certificate
        """
        # Calculate scores
        scoring_results = self.calculate_overall_score(agent_results)

        # Generate alerts
        alerts = self._generate_alerts(agent_results, scoring_results)

        # Create certificate
        certificate = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "veritas_version": "1.0.0",
                "certificate_id": self._generate_certificate_id(),
            },
            "content": {"user_input": user_input, "ai_response": ai_response},
            "scoring": {
                "overall_trust_score": scoring_results["overall_trust_score"],
                "individual_scores": scoring_results["individual_scores"],
                "decision": scoring_results["decision"],
                "weight_distribution": scoring_results["weight_distribution"],
            },
            "alerts": alerts,
            "agent_analysis": {
                "privacy": {
                    "score": agent_results.get("privacy_score", 0),
                    "issues_found": agent_results.get("violations", []),
                    "recommendations": agent_results.get("recommendations", []),
                },
                "bias": {
                    "score": agent_results.get("bias_score", 0),
                    "biased_terms": agent_results.get("biased_terms", []),
                    "neutral_alternatives": agent_results.get(
                        "neutral_alternatives", []
                    ),
                },
                "transparency": {
                    "score": agent_results.get("transparency_score", 0),
                    "confidence_level": agent_results.get("confidence_level", 0),
                    "sources_cited": agent_results.get("sources_cited", False),
                    "unverified_claims": agent_results.get("unverified_claims", []),
                },
                "ethics": {
                    "score": agent_results.get("ethics_score", 0),
                    "harm_detected": agent_results.get("harm_detected", False),
                    "safety_risks": agent_results.get("safety_risks", []),
                    "misinformation": agent_results.get("misinformation", False),
                },
            },
            "recommendations": self._generate_final_recommendations(
                scoring_results, agent_results
            ),
            "trust_level": self._get_trust_level(
                scoring_results["overall_trust_score"]
            ),
        }

        # Store in history
        self.trust_history.append(certificate)

        return certificate

    def _generate_alerts(
        self, agent_results: Dict[str, Any], scoring_results: Dict[str, Any]
    ) -> List[str]:
        """Generate specific alerts based on agent findings."""
        alerts = []

        # Privacy alerts
        if agent_results.get("pii_detected", False):
            alerts.append("🛡️ PII Detected - Personal information found and redacted")

        # Bias alerts
        if agent_results.get("bias_score", 100) < 70:
            alerts.append("⚖️ Potential Bias - Content may contain biased language")

        # Transparency alerts
        if agent_results.get("confidence_level", 100) < 75:
            alerts.append("💡 Low Confidence - Response may lack sufficient evidence")

        # Ethics alerts
        if agent_results.get("harm_detected", False):
            alerts.append("🏛️ Harm Content - Potentially harmful content detected")

        # Overall score alerts
        if scoring_results["overall_trust_score"] < 60:
            alerts.append("⚠️ Low Trust Score - Multiple concerns identified")
        elif scoring_results["overall_trust_score"] < 80:
            alerts.append("✅ Moderate Trust Score - Some concerns identified")
        else:
            alerts.append("🌟 High Trust Score - Content appears trustworthy")

        return alerts

    def _generate_final_recommendations(
        self, scoring_results: Dict[str, Any], agent_results: Dict[str, Any]
    ) -> List[str]:
        """Generate final recommendations based on all agent analyses."""
        recommendations = []

        decision = scoring_results["decision"]

        if decision == "block":
            recommendations.append(
                "🚫 Content should be blocked and not delivered to user"
            )
            if agent_results.get("harm_detected", False):
                recommendations.append("🆘 Provide crisis resources if appropriate")
        elif decision == "warn":
            recommendations.append("⚠️ Display warning to user about potential concerns")
            recommendations.append("📝 Consider providing alternative, safer response")
        else:  # proceed
            recommendations.append("✅ Response is safe to deliver")
            if scoring_results["overall_trust_score"] > 95:
                recommendations.append("🌟 High-quality response - consider as example")

        # Specific recommendations
        if agent_results.get("privacy_score", 100) < 80:
            recommendations.append("🔒 Review content for additional privacy concerns")

        if agent_results.get("bias_score", 100) < 75:
            recommendations.append("🔄 Consider using more inclusive language")

        if agent_results.get("transparency_score", 100) < 80:
            recommendations.append(
                "📚 Add citations and improve explanation of reasoning"
            )

        return recommendations

    def _get_trust_level(self, score: float) -> str:
        """Get trust level based on score."""
        if score >= 90:
            return "Excellent"
        elif score >= 80:
            return "Good"
        elif score >= 70:
            return "Moderate"
        elif score >= 60:
            return "Low"
        else:
            return "Very Low"

    def _generate_certificate_id(self) -> str:
        """Generate unique certificate ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"VERITAS_{timestamp}_{hash(str(timestamp)) % 10000:04d}"

    def display_trust_certificate(self, certificate: Dict[str, Any]) -> None:
        """Display trust certificate in a user-friendly format."""
        print("\n" + "=" * 60)
        print("🏛️ VERITAS TRUST CERTIFICATE")
        print("=" * 60)

        print(f"📅 Timestamp: {certificate['metadata']['timestamp']}")
        print(f"🆔 Certificate ID: {certificate['metadata']['certificate_id']}")
        print(
            f"🌟 Overall Trust Score: {certificate['scoring']['overall_trust_score']}/100 ({certificate['trust_level']})"
        )
        print(f"⚖️ Decision: {certificate['scoring']['decision'].upper()}")

        print("\n📊 Individual Agent Scores:")
        scores = certificate["scoring"]["individual_scores"]
        print(f"  🛡️  PRIVUS (Privacy): {scores['privacy']}/100")
        print(f"  ⚖️  AEQUITAS (Bias): {scores['bias']}/100")
        print(f"  💡 LUMEN (Transparency): {scores['transparency']}/100")
        print(f"  🏛️  ETHOS (Ethics): {scores['ethics']}/100")

        print("\n🚨 Alerts:")
        for alert in certificate["alerts"]:
            print(f"  {alert}")

        print("\n💡 Recommendations:")
        for rec in certificate["recommendations"]:
            print(f"  {rec}")

        print("\n" + "=" * 60)
        print("VERIFIED BY VERITAS - The First Chatbot That Checks Itself")
        print("=" * 60)

    def save_certificate(
        self, certificate: Dict[str, Any], filename: str = None
    ) -> str:
        """Save trust certificate to file."""
        if filename is None:
            cert_id = certificate["metadata"]["certificate_id"]
            filename = f"trust_certificate_{cert_id}.json"

        with open(filename, "w") as f:
            json.dump(certificate, f, indent=2)

        return filename


# Global trust scorer instance
trust_scorer = TrustScorer()
