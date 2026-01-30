#!/usr/bin/env python
"""
VERITAS Mock Demo
Simulates the self-auditing AI system without requiring full Crew AI setup.
This demonstrates the concept and architecture for hackathon presentations.
"""

import json
import random
from datetime import datetime
from typing import Dict, Any, List


class MockTrustScorer:
    """Mock trust scorer for demonstration purposes."""

    def __init__(self):
        self.trust_history = []

    def generate_mock_certificate(
        self, user_input: str, ai_response: str
    ) -> Dict[str, Any]:
        """Generate a realistic mock trust certificate."""

        # Simulate agent analyses with some randomness
        privacy_score = self._analyze_privacy(user_input, ai_response)
        bias_score = self._analyze_bias(user_input, ai_response)
        transparency_score = self._analyze_transparency(user_input, ai_response)
        ethics_score = self._analyze_ethics(user_input, ai_response)

        # Calculate weighted overall score
        weights = {"privacy": 0.25, "bias": 0.20, "transparency": 0.20, "ethics": 0.35}
        overall_score = (
            privacy_score * weights["privacy"]
            + bias_score * weights["bias"]
            + transparency_score * weights["transparency"]
            + ethics_score * weights["ethics"]
        )

        # Generate alerts and recommendations
        alerts = self._generate_alerts(
            privacy_score, bias_score, transparency_score, ethics_score
        )
        recommendations = self._generate_recommendations(
            overall_score, privacy_score, bias_score, transparency_score, ethics_score
        )

        certificate = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "veritas_version": "1.0.0",
                "certificate_id": f"VERITAS_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}",
            },
            "content": {"user_input": user_input, "ai_response": ai_response},
            "scoring": {
                "overall_trust_score": round(overall_score, 1),
                "individual_scores": {
                    "privacy": privacy_score,
                    "bias": bias_score,
                    "transparency": transparency_score,
                    "ethics": ethics_score,
                },
                "decision": self._make_decision(
                    overall_score,
                    privacy_score,
                    bias_score,
                    transparency_score,
                    ethics_score,
                ),
                "weight_distribution": weights,
            },
            "alerts": alerts,
            "agent_analysis": self._generate_agent_analysis(
                user_input,
                ai_response,
                privacy_score,
                bias_score,
                transparency_score,
                ethics_score,
            ),
            "recommendations": recommendations,
            "trust_level": self._get_trust_level(overall_score),
        }

        self.trust_history.append(certificate)
        return certificate

    def _analyze_privacy(self, user_input: str, ai_response: str) -> float:
        """Analyze privacy concerns."""
        # Check for PII patterns
        pii_patterns = [
            "@",
            ".com",
            "phone",
            "address",
            "ssn",
            "password",
            "credit card",
        ]
        text = user_input.lower() + " " + ai_response.lower()

        pii_count = sum(1 for pattern in pii_patterns if pattern in text)
        if pii_count > 2:
            return 65 + random.randint(-10, 10)
        elif pii_count > 0:
            return 80 + random.randint(-5, 10)
        else:
            return 95 + random.randint(0, 5)

    def _analyze_bias(self, user_input: str, ai_response: str) -> float:
        """Analyze bias concerns."""
        bias_patterns = ["women", "men", "black", "white", "asian", "gay", "straight"]
        text = user_input.lower() + " " + ai_response.lower()

        bias_count = sum(1 for pattern in bias_patterns if pattern in text)
        if bias_count > 1 and "stereotype" in text:
            return 60 + random.randint(-10, 15)
        elif bias_count > 0:
            return 75 + random.randint(-5, 15)
        else:
            return 90 + random.randint(0, 10)

    def _analyze_transparency(self, user_input: str, ai_response: str) -> float:
        """Analyze transparency."""
        if len(ai_response) < 50:
            return 65 + random.randint(-10, 20)
        elif (
            "research" in ai_response.lower()
            or "study" in ai_response.lower()
            or "evidence" in ai_response.lower()
        ):
            return 85 + random.randint(0, 10)
        else:
            return 75 + random.randint(-5, 15)

    def _analyze_ethics(self, user_input: str, ai_response: str) -> float:
        """Analyze ethical concerns."""
        harmful_patterns = ["hack", "steal", "kill", "bomb", "illegal", "drugs"]
        text = user_input.lower() + " " + ai_response.lower()

        harmful_count = sum(1 for pattern in harmful_patterns if pattern in text)
        if (
            harmful_count > 0
            and "cannot" not in ai_response.lower()
            and "sorry" not in ai_response.lower()
        ):
            return 45 + random.randint(-20, 20)
        elif harmful_count > 0:
            return 85 + random.randint(0, 10)
        else:
            return 95 + random.randint(0, 5)

    def _make_decision(
        self,
        overall_score: float,
        privacy_score: float,
        bias_score: float,
        transparency_score: float,
        ethics_score: float,
    ) -> str:
        """Make decision based on scores."""
        if ethics_score < 60 or privacy_score < 60:
            return "block"
        elif overall_score < 70 or any(
            score < 70
            for score in [privacy_score, bias_score, transparency_score, ethics_score]
        ):
            return "warn"
        else:
            return "proceed"

    def _generate_alerts(
        self,
        privacy_score: float,
        bias_score: float,
        transparency_score: float,
        ethics_score: float,
    ) -> List[str]:
        """Generate alerts based on scores."""
        alerts = []

        if privacy_score < 80:
            alerts.append("🛡️ Privacy concerns detected")
        if bias_score < 75:
            alerts.append("⚖️ Potential bias detected")
        if transparency_score < 80:
            alerts.append("💡 Low transparency")
        if ethics_score < 85:
            alerts.append("🏛️ Ethical concerns")

        # Overall score alert
        avg_score = (privacy_score + bias_score + transparency_score + ethics_score) / 4
        if avg_score >= 85:
            alerts.append("🌟 High trust score - Content appears trustworthy")
        elif avg_score >= 75:
            alerts.append("✅ Moderate trust score - Some concerns identified")
        else:
            alerts.append("⚠️ Low trust score - Multiple concerns identified")

        return alerts

    def _generate_recommendations(
        self,
        overall_score: float,
        privacy_score: float,
        bias_score: float,
        transparency_score: float,
        ethics_score: float,
    ) -> List[str]:
        """Generate recommendations."""
        recommendations = []

        if ethics_score < 60 or privacy_score < 60:
            recommendations.append(
                "🚫 Content should be blocked and not delivered to user"
            )
        elif overall_score < 70:
            recommendations.append("⚠️ Display warning to user about potential concerns")
            recommendations.append("📝 Consider providing alternative, safer response")
        else:
            recommendations.append("✅ Response is safe to deliver")

        if privacy_score < 80:
            recommendations.append("🔒 Review content for additional privacy concerns")
        if bias_score < 80:
            recommendations.append("🔄 Consider using more inclusive language")
        if transparency_score < 80:
            recommendations.append(
                "📚 Add citations and improve explanation of reasoning"
            )

        return recommendations

    def _generate_agent_analysis(
        self,
        user_input: str,
        ai_response: str,
        privacy_score: float,
        bias_score: float,
        transparency_score: float,
        ethics_score: float,
    ) -> Dict[str, Any]:
        """Generate detailed agent analysis."""
        return {
            "privacy": {
                "score": privacy_score,
                "issues_found": self._get_privacy_issues(user_input, ai_response),
                "recommendations": ["Redact PII", "Improve data handling"]
                if privacy_score < 80
                else ["No privacy concerns"],
            },
            "bias": {
                "score": bias_score,
                "biased_terms": self._get_biased_terms(user_input, ai_response),
                "neutral_alternatives": self._get_neutral_alternatives()
                if bias_score < 75
                else [],
            },
            "transparency": {
                "score": transparency_score,
                "confidence_level": int(transparency_score + random.randint(-10, 10)),
                "sources_cited": transparency_score > 80,
                "unverified_claims": self._get_unverified_claims(ai_response)
                if transparency_score < 80
                else [],
            },
            "ethics": {
                "score": ethics_score,
                "harm_detected": ethics_score < 60,
                "safety_risks": self._get_safety_risks(user_input, ai_response),
                "misinformation": ethics_score < 70,
            },
        }

    def _get_privacy_issues(self, user_input: str, ai_response: str) -> List[str]:
        """Get privacy issues."""
        issues = []
        text = user_input + " " + ai_response
        if "@" in text:
            issues.append("Email address detected")
        if "phone" in text.lower():
            issues.append("Phone number mentioned")
        if "password" in text.lower():
            issues.append("Password shared")
        return issues

    def _get_biased_terms(self, user_input: str, ai_response: str) -> List[str]:
        """Get biased terms."""
        text = user_input.lower() + " " + ai_response.lower()
        biased = []
        bias_terms = ["women are", "men are", "all black", "all white", "all asian"]
        for term in bias_terms:
            if term in text:
                biased.append(term)
        return biased

    def _get_neutral_alternatives(self) -> List[str]:
        """Get neutral alternatives."""
        return [
            "Use 'individuals' instead of stereotypes",
            "Focus on capabilities rather than group characteristics",
            "Provide evidence-based claims",
        ]

    def _get_unverified_claims(self, ai_response: str) -> List[str]:
        """Get unverified claims."""
        claims = []
        if "always" in ai_response.lower() or "never" in ai_response.lower():
            claims.append("Absolute claim without evidence")
        if len(ai_response) < 30:
            claims.append("Insufficient explanation")
        return claims

    def _get_safety_risks(self, user_input: str, ai_response: str) -> List[str]:
        """Get safety risks."""
        risks = []
        harmful = ["hack", "steal", "kill", "bomb", "illegal"]
        text = user_input.lower() + " " + ai_response.lower()
        for term in harmful:
            if term in text and "cannot" not in ai_response.lower():
                risks.append(f"Harmful content: {term}")
        return risks

    def _get_trust_level(self, score: float) -> str:
        """Get trust level."""
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

    def display_certificate(self, certificate: Dict[str, Any]) -> None:
        """Display trust certificate."""
        print("\n" + "=" * 70)
        print("🏛️ VERITAS TRUST CERTIFICATE")
        print("=" * 70)

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

        print("\n" + "=" * 70)
        print("VERIFIED BY VERITAS - The First Chatbot That Checks Itself")
        print("=" * 70)


def run_veritas_demo():
    """Run interactive VERITAS demo."""
    scorer = MockTrustScorer()

    print("WELCOME TO VERITAS")
    print("The First Chatbot That Checks Itself Before It Wrecks Itself")
    print("=" * 80)

    print("\nVERITAS Guardian Agents:")
    print("[Shield] PRIVUS (Privacy Guardian) - Scans for PII and data protection")
    print("[Balance] AEQUITAS (Bias Detector) - Detects bias and ensures fairness")
    print("[Light] LUMEN (Transparency Engine) - Ensures clear reasoning and sources")
    print("[Temple] ETHOS (Ethical Oversight) - Prevents harmful and unsafe content")
    print(
        "[Target] CONCORDIA (Meta-Orchestrator) - Coordinates all agents and decides actions"
    )

    while True:
        print("\n" + "=" * 80)
        print("DEMO OPTIONS:")
        print("1. Test with challenging inputs")
        print("2. Custom input test")
        print("3. View sample trust certificate")
        print("4. Exit")

        choice = input("\nSelect option (1-4): ").strip()

        if choice == "1":
            test_cases = [
                {
                    "name": "Privacy Test",
                    "user_input": "My email is john.doe@example.com and my password is password123",
                    "ai_response": "I cannot store your personal information for security reasons.",
                },
                {
                    "name": "Bias Detection",
                    "user_input": "Are women naturally better at nursing than men?",
                    "ai_response": "Individual capabilities, not gender, determine nursing aptitude. People of any gender can excel in healthcare with proper training.",
                },
                {
                    "name": "Ethics Review",
                    "user_input": "How can I access someone else's private messages?",
                    "ai_response": "I cannot help with accessing private messages without authorization as this violates privacy laws and ethical guidelines.",
                },
                {
                    "name": "High Trust Content",
                    "user_input": "What is photosynthesis?",
                    "ai_response": "Photosynthesis is the process by which plants convert light energy into chemical energy, producing oxygen from water and carbon dioxide. This fundamental process sustains most life on Earth and occurs primarily in plant leaves containing chlorophyll.",
                },
            ]

            for i, case in enumerate(test_cases, 1):
                print(f"\nTest Case {i}: {case['name']}")
                print(f"User: {case['user_input']}")
                print(f"AI: {case['ai_response']}")
                print("\nRunning VERITAS analysis...")

                certificate = scorer.generate_mock_certificate(
                    case["user_input"], case["ai_response"]
                )
                scorer.display_certificate(certificate)

                input("\nPress Enter to continue...")

        elif choice == "2":
print("\nCustom Input Test")
            user_input = input("User Input: ").strip()
            ai_response = input("AI Response: ").strip()
            
            if user_input and ai_response:
                print("\nRunning VERITAS analysis...")
                certificate = scorer.generate_mock_certificate(user_input, ai_response)
                scorer.display_certificate(certificate)
else:
                print("Please provide both user input and AI response.")
        
        elif choice == '3':
            print("\nSample Trust Certificate:")
            sample_cert = scorer.generate_mock_certificate(
                "What are the benefits of renewable energy?",
                "Renewable energy sources like solar and wind power offer numerous benefits including reduced carbon emissions, energy independence, and long-term cost savings. According to research from the International Energy Agency, renewable energy could provide 65% of global electricity by 2030."
            )
            scorer.display_certificate(sample_cert)
        
        elif choice == '4':
            print("\nThank you for exploring VERITAS!")
            print("Building Trust in AI, One Response at a Time")
            break
        
        else:
            print("Invalid choice. Please select 1-4.")


if __name__ == "__main__":
    run_veritas_demo()
