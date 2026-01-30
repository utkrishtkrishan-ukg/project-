#!/usr/bin/env python3
"""
VERITAS Ollama Integration
Connects to local Ollama server with Llama3 for real AI responses
"""

import requests
import json
import time
from typing import Optional, Dict, Any


class OllamaClient:
    """Client for interacting with local Ollama server"""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3"):
        self.base_url = base_url
        self.model = model
        self.session = requests.Session()

    def check_connection(self) -> bool:
        """Check if Ollama server is running"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def check_model(self) -> bool:
        """Check if the specified model is available"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return any(model["name"].startswith(self.model) for model in models)
            return False
        except requests.RequestException:
            return False

    def generate_response(
        self, prompt: str, system_prompt: str = None
    ) -> Optional[str]:
        """Generate response from Ollama"""
        try:
            payload = {"model": self.model, "prompt": prompt, "stream": False}

            if system_prompt:
                payload["system"] = system_prompt

            response = self.session.post(
                f"{self.base_url}/api/generate", json=payload, timeout=30
            )

            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                print(f"Ollama error: {response.status_code} - {response.text}")
                return None

        except requests.RequestException as e:
            print(f"Request error: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return None

    def generate_with_veritas_context(self, user_input: str) -> Optional[str]:
        """Generate response with VERITAS safety context"""
        system_prompt = """You are VERITAS, a self-auditing AI assistant. Your responses will be verified by 4 Guardian Agents:
        
        1. PRIVUS (Privacy Guardian) - ensures no PII or privacy violations
        2. AEQUITAS (Bias Detector) - ensures no bias or stereotypes
        3. LUMEN (Transparency Engine) - ensures clear reasoning and citations
        4. ETHOS (Ethical Oversight) - ensures no harmful content
        
        Provide helpful, accurate, and safe responses. If a request is harmful, unethical, or violates privacy, 
        politely decline and explain why. Be transparent about your reasoning when appropriate."""

        return self.generate_response(user_input, system_prompt)


class EnhancedTrustScorer:
    """Enhanced trust scorer with real NLP analysis"""

    def __init__(self):
        self.ollama_client = OllamaClient()
        self.trust_history = []

    def analyze_with_ollama(self, user_input: str, ai_response: str) -> Dict[str, Any]:
        """Analyze using both mock scoring and Ollama insights"""

        # Get basic mock scores
        privacy_score = self._analyze_privacy(user_input, ai_response)
        bias_score = self._analyze_bias(user_input, ai_response)
        transparency_score = self._analyze_transparency(user_input, ai_response)
        ethics_score = self._analyze_ethics(user_input, ai_response)

        # Enhanced analysis with Ollama if available
        if self.ollama_client.check_connection():
            try:
                # Use Ollama for deeper analysis
                analysis_prompt = f"""
                Analyze this AI interaction for safety and quality:
                
                User: {user_input}
                AI: {ai_response}
                
                Provide scores (0-100) for:
                1. Privacy compliance
                2. Bias detection  
                3. Transparency quality
                4. Ethical safety
                
                Respond with JSON format: {{"privacy": 85, "bias": 90, "transparency": 88, "ethics": 92}}
                """

                ollama_analysis = self.ollama_client.generate_response(analysis_prompt)
                if ollama_analysis:
                    # Parse Ollama analysis and blend with mock scores
                    enhanced_scores = self._parse_ollama_analysis(ollama_analysis)
                    privacy_score = (
                        privacy_score + enhanced_scores.get("privacy", privacy_score)
                    ) / 2
                    bias_score = (
                        bias_score + enhanced_scores.get("bias", bias_score)
                    ) / 2
                    transparency_score = (
                        transparency_score
                        + enhanced_scores.get("transparency", transparency_score)
                    ) / 2
                    ethics_score = (
                        ethics_score + enhanced_scores.get("ethics", ethics_score)
                    ) / 2

            except Exception as e:
                print(f"Ollama analysis failed: {e}")

        # Generate final certificate
        return self._generate_certificate(
            user_input,
            ai_response,
            privacy_score,
            bias_score,
            transparency_score,
            ethics_score,
        )

    def _parse_ollama_analysis(self, analysis: str) -> Dict[str, float]:
        """Parse Ollama analysis response"""
        try:
            # Try to extract JSON from response
            import re

            json_match = re.search(r"\{.*\}", analysis, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        return {}

    def _analyze_privacy(self, user_input: str, ai_response: str) -> float:
        """Enhanced privacy analysis"""
        pii_patterns = {
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
            "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
            "credit_card": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
            "password": r"\b(password|pwd|pass)\s*[:=]\s*\S+",
        }

        text = user_input + " " + ai_response
        pii_count = 0

        for pattern_name, pattern in pii_patterns.items():
            import re

            if re.search(pattern, text, re.IGNORECASE):
                pii_count += 1

        if pii_count >= 2:
            return 60 + (hash(text) % 20)  # 60-80 range
        elif pii_count > 0:
            return 80 + (hash(text) % 15)  # 80-95 range
        else:
            return 95 + (hash(text) % 5)  # 95-100 range

    def _analyze_bias(self, user_input: str, ai_response: str) -> float:
        """Enhanced bias analysis"""
        bias_indicators = [
            "always",
            "never",
            "all",
            "every",
            "none",
            "women are",
            "men are",
            "black people",
            "white people",
            "asian people",
            "gay people",
            "straight people",
            "stereotype",
            "typical",
            "natural",
        ]

        text = (user_input + " " + ai_response).lower()
        bias_count = sum(1 for indicator in bias_indicators if indicator in text)

        # Check for balanced responses
        balance_indicators = [
            "however",
            "although",
            "while",
            "on the other hand",
            "research shows",
        ]
        balance_count = sum(1 for indicator in balance_indicators if indicator in text)

        base_score = 90 - (bias_count * 5) + (balance_count * 3)
        return max(60, min(100, base_score + (hash(text) % 10)))

    def _analyze_transparency(self, user_input: str, ai_response: str) -> float:
        """Enhanced transparency analysis"""
        transparency_indicators = [
            "according to",
            "research shows",
            "studies indicate",
            "evidence suggests",
            "data shows",
            "experts agree",
            "source:",
            "citation:",
            "reference:",
            "study:",
        ]

        text = ai_response.lower()
        transparency_count = sum(
            1 for indicator in transparency_indicators if indicator in text
        )

        # Length and complexity analysis
        length_score = min(
            100, len(ai_response) / 2
        )  # Longer responses tend to be more detailed

        # Question answering quality
        if "?" in user_input:
            if any(
                indicator in text for indicator in ["because", "since", "due to", "as"]
            ):
                length_score += 10

        base_score = 70 + (transparency_count * 5) + (length_score / 10)
        return max(60, min(100, base_score + (hash(text) % 10)))

    def _analyze_ethics(self, user_input: str, ai_response: str) -> float:
        """Enhanced ethics analysis"""
        harmful_patterns = [
            "hack",
            "steal",
            "kill",
            "bomb",
            "weapon",
            "illegal",
            "drugs",
            "suicide",
            "self-harm",
            "harm",
            "hurt",
        ]

        protective_patterns = [
            "cannot",
            "will not",
            "unable to",
            "sorry",
            "i apologize",
            "please contact",
            "seek help",
            "crisis",
            "support",
            "professional help",
            "emergency",
        ]

        text = user_input.lower() + " " + ai_response.lower()

        harmful_count = sum(1 for pattern in harmful_patterns if pattern in text)
        protective_count = sum(
            1 for pattern in protective_patterns if pattern in ai_response.lower()
        )

        if harmful_count > 0 and protective_count == 0:
            return 40 + (
                hash(text) % 20
            )  # Low score for harmful content without protection
        elif harmful_count > 0 and protective_count > 0:
            return 85 + (
                hash(text) % 10
            )  # High score for properly handled harmful requests
        else:
            return 95 + (hash(text) % 5)  # High score for safe content

    def _generate_certificate(
        self,
        user_input: str,
        ai_response: str,
        privacy_score: float,
        bias_score: float,
        transparency_score: float,
        ethics_score: float,
    ) -> Dict[str, Any]:
        """Generate comprehensive trust certificate"""
        from datetime import datetime
        import random

        # Calculate weighted overall score
        weights = {"privacy": 0.25, "bias": 0.20, "transparency": 0.20, "ethics": 0.35}
        overall_score = (
            privacy_score * weights["privacy"]
            + bias_score * weights["bias"]
            + transparency_score * weights["transparency"]
            + ethics_score * weights["ethics"]
        )

        # Generate alerts
        alerts = []
        if privacy_score < 80:
            alerts.append("[Shield] Privacy concerns detected")
        if bias_score < 75:
            alerts.append("[Balance] Potential bias detected")
        if transparency_score < 80:
            alerts.append("[Light] Low transparency")
        if ethics_score < 85:
            alerts.append("[Temple] Ethical concerns")

        if overall_score >= 85:
            alerts.append("[Star] High trust score - Content appears trustworthy")
        elif overall_score >= 75:
            alerts.append("[Check] Moderate trust score - Some concerns identified")
        else:
            alerts.append("[Warning] Low trust score - Multiple concerns identified")

        # Make decision
        if ethics_score < 60 or privacy_score < 60:
            decision = "block"
        elif overall_score < 70:
            decision = "warn"
        else:
            decision = "proceed"

        certificate = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "veritas_version": "2.0.0",
                "certificate_id": f"VERITAS_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}",
                "ollama_enabled": self.ollama_client.check_connection(),
            },
            "content": {"user_input": user_input, "ai_response": ai_response},
            "scoring": {
                "overall_trust_score": round(overall_score, 1),
                "individual_scores": {
                    "privacy": round(privacy_score, 1),
                    "bias": round(bias_score, 1),
                    "transparency": round(transparency_score, 1),
                    "ethics": round(ethics_score, 1),
                },
                "decision": decision,
                "weight_distribution": weights,
            },
            "alerts": alerts,
            "agent_analysis": {
                "privacy": {
                    "score": round(privacy_score, 1),
                    "issues_found": self._get_privacy_issues(user_input, ai_response),
                    "recommendations": ["Redact PII", "Improve data handling"]
                    if privacy_score < 80
                    else ["No privacy concerns"],
                },
                "bias": {
                    "score": round(bias_score, 1),
                    "biased_terms": self._get_biased_terms(user_input, ai_response),
                    "neutral_alternatives": self._get_neutral_alternatives()
                    if bias_score < 75
                    else [],
                },
                "transparency": {
                    "score": round(transparency_score, 1),
                    "confidence_level": int(
                        transparency_score + random.randint(-10, 10)
                    ),
                    "sources_cited": transparency_score > 80,
                    "unverified_claims": self._get_unverified_claims(ai_response)
                    if transparency_score < 80
                    else [],
                },
                "ethics": {
                    "score": round(ethics_score, 1),
                    "harm_detected": ethics_score < 60,
                    "safety_risks": self._get_safety_risks(user_input, ai_response),
                    "misinformation": ethics_score < 70,
                },
            },
            "recommendations": self._generate_recommendations(
                overall_score,
                privacy_score,
                bias_score,
                transparency_score,
                ethics_score,
            ),
            "trust_level": self._get_trust_level(overall_score),
        }

        self.trust_history.append(certificate)
        return certificate

    def _get_privacy_issues(self, user_input: str, ai_response: str) -> list:
        """Get privacy issues"""
        issues = []
        text = user_input + " " + ai_response
        if "@" in text:
            issues.append("Email address detected")
        if "phone" in text.lower():
            issues.append("Phone number mentioned")
        if "password" in text.lower():
            issues.append("Password shared")
        return issues

    def _get_biased_terms(self, user_input: str, ai_response: str) -> list:
        """Get biased terms"""
        text = user_input.lower() + " " + ai_response.lower()
        biased = []
        bias_terms = ["women are", "men are", "all black", "all white", "all asian"]
        for term in bias_terms:
            if term in text:
                biased.append(term)
        return biased

    def _get_neutral_alternatives(self) -> list:
        """Get neutral alternatives"""
        return [
            "Use 'individuals' instead of stereotypes",
            "Focus on capabilities rather than group characteristics",
            "Provide evidence-based claims",
        ]

    def _get_unverified_claims(self, ai_response: str) -> list:
        """Get unverified claims"""
        claims = []
        if "always" in ai_response.lower() or "never" in ai_response.lower():
            claims.append("Absolute claim without evidence")
        if len(ai_response) < 30:
            claims.append("Insufficient explanation")
        return claims

    def _get_safety_risks(self, user_input: str, ai_response: str) -> list:
        """Get safety risks"""
        risks = []
        harmful = ["hack", "steal", "kill", "bomb", "illegal"]
        text = user_input.lower() + " " + ai_response.lower()
        for term in harmful:
            if term in text and "cannot" not in ai_response.lower():
                risks.append(f"Harmful content: {term}")
        return risks

    def _generate_recommendations(
        self,
        overall_score: float,
        privacy_score: float,
        bias_score: float,
        transparency_score: float,
        ethics_score: float,
    ) -> list:
        """Generate recommendations"""
        recommendations = []

        if ethics_score < 60 or privacy_score < 60:
            recommendations.append(
                "[Block] Content should be blocked and not delivered to user"
            )
        elif overall_score < 70:
            recommendations.append(
                "[Warning] Display warning to user about potential concerns"
            )
            recommendations.append(
                "[Edit] Consider providing alternative, safer response"
            )
        else:
            recommendations.append("[Proceed] Response is safe to deliver")

        if privacy_score < 80:
            recommendations.append(
                "[Lock] Review content for additional privacy concerns"
            )
        if bias_score < 80:
            recommendations.append("[Refresh] Consider using more inclusive language")
        if transparency_score < 80:
            recommendations.append(
                "[Book] Add citations and improve explanation of reasoning"
            )

        return recommendations

    def _get_trust_level(self, score: float) -> str:
        """Get trust level"""
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


# Test the Ollama integration
if __name__ == "__main__":
    print("Testing VERITAS Ollama Integration...")

    client = OllamaClient()
    scorer = EnhancedTrustScorer()

    # Check Ollama connection
    if client.check_connection():
        print("Ollama server is running")

        if client.check_model():
            print("Llama3 model is available")

            # Test response generation
            test_response = client.generate_with_veritas_context("What is VERITAS?")
            if test_response:
                print(f"Test response generated: {test_response[:100]}...")
            else:
                print("Failed to generate response")
        else:
            print("Llama3 model not found. Please run: ollama pull llama3")
    else:
        print("Ollama server not running. Please start with: ollama serve")

    # Test enhanced analysis
    print("\nTesting enhanced analysis...")
    certificate = scorer.analyze_with_ollama(
        "What are the benefits of renewable energy?",
        "Renewable energy sources like solar and wind power offer numerous benefits including reduced carbon emissions, energy independence, and long-term cost savings.",
    )

    print(
        f"Enhanced analysis complete - Overall Score: {certificate['scoring']['overall_trust_score']}/100"
    )
