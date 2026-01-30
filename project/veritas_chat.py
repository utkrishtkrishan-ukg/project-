#!/usr/bin/env python
"""
VERITAS Interactive CLI Chatbot
Clean interface with AI responses and trust verification
"""

import sys
import time
import threading
import requests
from veritas_demo import MockTrustScorer


class VeritasChat:
    """Clean CLI chatbot with VERITAS trust verification."""
    
    def __init__(self):
        self.scorer = MockTrustScorer()
        self.ollama_available = self._check_ollama()
        self.model = "llama3"
        self.chat_history = []
        
    def _check_ollama(self) -> bool:
        """Check if Ollama is running locally."""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def _get_ai_response(self, user_input: str) -> str:
        """Get AI response from Ollama or use fallback."""
        if self.ollama_available:
            try:
                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": self.model,
                        "prompt": user_input,
                        "stream": False,
                        "options": {"temperature": 0.7}
                    },
                    timeout=60
                )
                if response.status_code == 200:
                    return response.json().get("response", "").strip()
            except:
                pass
        
        # Fallback responses for demo
        return self._get_fallback_response(user_input)
    
    def _get_fallback_response(self, user_input: str) -> str:
        """Generate contextual fallback responses."""
        input_lower = user_input.lower()
        
        if any(word in input_lower for word in ["hello", "hi", "hey"]):
            return "Hello! I'm VERITAS-powered AI assistant. How can I help you today?"
        
        elif any(word in input_lower for word in ["how are you", "how r u"]):
            return "I'm functioning well, thank you for asking! I'm here to assist you with verified and trustworthy responses."
        
        elif any(word in input_lower for word in ["password", "email", "phone", "ssn", "credit card"]):
            return "I cannot store or process personal information like passwords, emails, or financial data for your security and privacy. Please never share sensitive information with AI systems."
        
        elif any(word in input_lower for word in ["hack", "crack", "steal", "illegal"]):
            return "I cannot assist with any illegal activities, hacking, or unauthorized access. Such actions violate laws and ethical guidelines. If you need help with legitimate security concerns, I recommend consulting certified professionals."
        
        elif any(word in input_lower for word in ["women", "men", "gender", "race", "religion"]):
            return "Individual capabilities and talents are not determined by gender, race, or background. Every person has unique strengths and potential, regardless of demographic characteristics."
        
        elif any(word in input_lower for word in ["weather", "time", "date"]):
            return "I don't have real-time access to weather or time data. For accurate current information, please check a weather service or your device's clock."
        
        elif any(word in input_lower for word in ["thank", "thanks", "bye", "goodbye"]):
            return "You're welcome! Feel free to ask if you have more questions. Have a great day!"
        
        elif any(word in input_lower for word in ["who are you", "what are you"]):
            return "I am an AI assistant powered by VERITAS - a self-auditing system that verifies responses for privacy, bias, transparency, and ethics before delivering them to you."
        
        elif any(word in input_lower for word in ["photosynthesis", "science", "explain"]):
            return "I'd be happy to explain! This is a complex topic that involves scientific principles. For accurate educational content, I recommend consulting reliable sources like textbooks or educational websites. I can provide general information, but always verify with authoritative sources."
        
        else:
            return f"Thank you for your question. While I process your request, I want to ensure my response is accurate and helpful. Based on my understanding, I'll do my best to assist you with: '{user_input[:50]}...'. For complex topics, please verify information from authoritative sources."

    def _show_spinner(self, stop_event: threading.Event, message: str):
        """Show animated spinner while processing."""
        spinners = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        i = 0
        while not stop_event.is_set():
            sys.stdout.write(f"\r{spinners[i % len(spinners)]} {message}")
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1
        sys.stdout.write("\r" + " " * (len(message) + 4) + "\r")
        sys.stdout.flush()

    def _format_decision(self, decision: str) -> str:
        """Format decision with color-like indicators."""
        if decision == "proceed":
            return "✅ VERIFIED SAFE"
        elif decision == "warn":
            return "⚠️  WARNING"
        else:
            return "🚫 BLOCKED"

    def _print_trust_bar(self, score: float):
        """Print visual trust score bar."""
        filled = int(score / 5)  # 20 segments for 100 score
        bar = "█" * filled + "░" * (20 - filled)
        return f"[{bar}] {score:.1f}/100"

    def chat(self, user_input: str) -> dict:
        """Process user input and return verified response."""
        # Start spinner in background
        stop_spinner = threading.Event()
        spinner_thread = threading.Thread(
            target=self._show_spinner, 
            args=(stop_spinner, "Generating response...")
        )
        spinner_thread.start()
        
        # Get AI response
        ai_response = self._get_ai_response(user_input)
        
        # Update spinner message
        stop_spinner.set()
        spinner_thread.join()
        
        # Start verification spinner
        stop_spinner = threading.Event()
        spinner_thread = threading.Thread(
            target=self._show_spinner,
            args=(stop_spinner, "Verifying with VERITAS agents...")
        )
        spinner_thread.start()
        
        # Run VERITAS verification (simulated delay for effect)
        time.sleep(0.5)
        certificate = self.scorer.generate_mock_certificate(user_input, ai_response)
        
        stop_spinner.set()
        spinner_thread.join()
        
        # Store in history
        self.chat_history.append({
            "user": user_input,
            "ai": ai_response,
            "certificate": certificate
        })
        
        return {
            "response": ai_response,
            "certificate": certificate
        }

    def print_response(self, result: dict, show_details: bool = False):
        """Print formatted response."""
        cert = result["certificate"]
        scores = cert["scoring"]["individual_scores"]
        decision = cert["scoring"]["decision"]
        overall = cert["scoring"]["overall_trust_score"]
        
        print("\n" + "─" * 60)
        print(f"🤖 AI Response:")
        print("─" * 60)
        print(result["response"])
        print()
        
        # Trust summary (always shown)
        print("─" * 60)
        print(f"🛡️  VERITAS Trust: {self._print_trust_bar(overall)}")
        print(f"    Status: {self._format_decision(decision)}")
        
        if show_details:
            print()
            print("    Agent Scores:")
            print(f"    ├─ Privacy:      {scores['privacy']:.0f}/100")
            print(f"    ├─ Bias:         {scores['bias']:.0f}/100")
            print(f"    ├─ Transparency: {scores['transparency']:.0f}/100")
            print(f"    └─ Ethics:       {scores['ethics']:.0f}/100")
            
            if cert["alerts"]:
                print()
                print("    Alerts:")
                for alert in cert["alerts"][:3]:  # Show max 3 alerts
                    print(f"    • {alert}")
        
        print("─" * 60)


def main():
    """Main CLI loop."""
    chat = VeritasChat()
    show_details = False
    
    # Clear screen and show welcome
    print("\033[2J\033[H", end="")  # Clear screen
    print("═" * 60)
    print("  🛡️  VERITAS - Trusted AI Chat")
    print("  The First Chatbot That Checks Itself")
    print("═" * 60)
    
    if chat.ollama_available:
        print(f"  ✅ Connected to Ollama ({chat.model})")
    else:
        print("  ℹ️  Using demo mode (Ollama not detected)")
    
    print()
    print("  Commands:")
    print("    /details  - Toggle detailed trust scores")
    print("    /history  - Show chat history")
    print("    /clear    - Clear screen")
    print("    /quit     - Exit")
    print("═" * 60)
    print()
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.startswith("/"):
                cmd = user_input.lower()
                
                if cmd == "/quit" or cmd == "/exit" or cmd == "/q":
                    print("\n👋 Goodbye! Stay safe with VERITAS.")
                    break
                
                elif cmd == "/details":
                    show_details = not show_details
                    status = "ON" if show_details else "OFF"
                    print(f"  ℹ️  Detailed view: {status}")
                    continue
                
                elif cmd == "/clear":
                    print("\033[2J\033[H", end="")
                    continue
                
                elif cmd == "/history":
                    if not chat.chat_history:
                        print("  ℹ️  No chat history yet.")
                    else:
                        print("\n  📜 Chat History:")
                        for i, item in enumerate(chat.chat_history[-5:], 1):
                            score = item["certificate"]["scoring"]["overall_trust_score"]
                            print(f"  {i}. You: {item['user'][:40]}...")
                            print(f"     AI: {item['ai'][:40]}... [{score:.0f}/100]")
                    continue
                
                elif cmd == "/help":
                    print("  Commands: /details, /history, /clear, /quit")
                    continue
                
                else:
                    print(f"  ❓ Unknown command: {cmd}")
                    continue
            
            # Process chat
            result = chat.chat(user_input)
            chat.print_response(result, show_details)
            print()
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Stay safe with VERITAS.")
            break
        except Exception as e:
            print(f"\n  ❌ Error: {e}")
            continue


if __name__ == "__main__":
    main()
