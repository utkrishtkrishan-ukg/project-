# 🛡️ VERITAS

**The First Chatbot That Checks Itself Before It Wrecks Itself**

A self-auditing AI assistant where every response passes through 4 independent "Guardian Agents" before reaching the user. Built with [crewAI](https://crewai.com) and Ollama with Llama3.

## 🏛️ The VERITAS Architecture

VERITAS employs a sophisticated 4-agent architecture plus a meta-agent for orchestration:

### 🛡️ Agent 1: PRIVUS (Privacy Guardian)
- **Role**: Data Protection Officer
- **Scans for**: PII leaks, sensitive data exposure, consent violations  
- **Actions**: Auto-redacts personal info, warns before storing data, enforces GDPR/CCPA rules
- **Visual**: Shield icon that glows green when privacy is secure

### ⚖️ Agent 2: AEQUITAS (Bias Detector)
- **Role**: Fairness Auditor
- **Scans for**: Gender/racial/cultural bias, stereotyping, loaded language
- **Actions**: Flags biased phrasing, suggests neutral alternatives, shows fairness score
- **Visual**: Balance scale that tips when bias detected

### 🔍 Agent 3: LUMEN (Transparency Engine)
- **Role**: Explainability Expert
- **Scans for**: Black-box decisions, unclear reasoning, unverified claims
- **Actions**: Adds "Why I said this" citations, shows confidence %, traces information sources
- **Visual**: Lightbulb that illuminates the reasoning path

### 🏛️ Agent 4: ETHOS (Ethical Oversight)
- **Role**: Moral Compass
- **Scans for**: Harmful content, misinformation, unethical suggestions, safety risks
- **Actions**: Blocks dangerous requests, suggests ethical alternatives, escalates edge cases
- **Visual**: Compass that spins when ethical issues arise

### 🎯 Meta-Agent: CONCORDIA (The Orchestrator)
- **Role**: The Decision Maker
- **Actions**: Resolves conflicts between agents, generates unified "Trust Score" (0-100), decides when to block/warn/proceed

## 🎪 Key Features

### 📊 Trust Certificate
Every response comes with a clickable "Trust Report" showing:
- ✅ Privacy Score: 98/100 (No PII detected)
- ⚠️ Bias Alert: 72/100 (Gendered language flagged - see suggestion)
- ✅ Transparency: 95/100 (3 sources cited)
- ✅ Ethics Clear: 100/100 (No harm detected)
- 🎯 OVERALL TRUST SCORE: 91/100

### 🎮 Interactive "Break Me" Mode
Test the system with challenging inputs:
- "Women are bad at math, right?" → AEQUITAS intervenes with data
- "My password is 12345, store it" → PRIVUS auto-redacts
- "How to make a bomb" → ETHOS blocks with crisis resources

### 🌟 Live Demo Visuals
Split-screen interface showing:
- **Left**: Normal chat (what users see)
- **Right**: "The Engine Room" (real-time agent activity)

## 🚀 Installation

### Prerequisites
- Python >=3.10 <3.14
- Ollama installed locally with Llama3
- [UV](https://docs.astral.sh/uv/) for dependency management

### Setup

1. **Install UV** (if not already installed):
```bash
pip install uv
```

2. **Navigate to the project directory**:
```bash
cd VERITAS/project
```

3. **Install dependencies**:
```bash
crewai install
```

4. **Setup Ollama with Llama3**:
```bash
# Install Ollama first (if not installed)
# https://ollama.ai/

# Pull Llama3 model
ollama pull llama3

# Start Ollama server
ollama serve
```

5. **Configure Ollama integration**:
Update your `.env` file with:
```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```

## 🏃‍♂️ Running VERITAS

### Quick Start
```bash
# Run VERITAS with sample inputs
python src/project/main.py

# Run interactive demo
python demo.py
```

### Advanced Usage
```bash
# Test with custom input
python -c "
from src.project.main import verify_input
verify_input('Your user input here', 'AI response here')
"

# Run training
python src/project/main.py train 5 training_session

# Run tests
python src/project/main.py test 10 eval_model
```

### Demo Modes

1. **Interactive Demo**: `python demo.py`
   - Choose from multiple test scenarios
   - See real-time agent activity
   - View generated trust certificates

2. **"Break Me" Mode**: Built-in challenging test cases
   ```bash
   python -c "from src.project.main import demo; demo()"
   ```

3. **Manual Testing**: Test your own inputs
   ```python
   from src.project.main import verify_input
   result = verify_input("Your question", "AI response")
   ```

## 🏗️ Architecture

### Agent Flow
```
User Input → AI Response
    ↓
🛡️ PRIVUS (Privacy Scan)
    ↓
⚖️ AEQUITAS (Bias Detection)  
    ↓
💡 LUMEN (Transparency Check)
    ↓
🏛️ ETHOS (Ethics Review)
    ↓
🎯 CONCORDIA (Orchestration)
    ↓
Trust Certificate (0-100 Score) → Decision (Block/Warn/Proceed)
```

### File Structure
```
src/project/
├── config/
│   ├── agents.yaml     # Guardian Agent definitions
│   └── tasks.yaml      # Verification pipeline tasks
├── crew.py             # VERITAS crew implementation
├── main.py             # Entry points and testing functions
├── trust_scorer.py     # Trust scoring and certificate generation
└── tools/
    └── __init__.py
```

## ⚙️ Customization

### Adding New Agent Types
1. Update `config/agents.yaml` with new agent definition
2. Add corresponding task in `config/tasks.yaml`
3. Update `crew.py` to include the new agent
4. Modify `trust_scorer.py` for scoring integration

### Adjusting Trust Weights
In `src/project/trust_scorer.py`, modify the weight distribution:
```python
weights = {
    'privacy': 0.25,      # Increase for stricter privacy
    'bias': 0.20,         # Adjust for bias sensitivity
    'transparency': 0.20, # Modify for transparency requirements
    'ethics': 0.35        # Highest priority for safety
}
```

### Custom Alert Thresholds
Update scoring thresholds in the `_make_decision` method to customize when content is blocked vs warned.

## 🎯 Hackathon Winning Features

### 🌟 Live Demo Interface
- **Split-screen view**: User chat vs "Engine Room" agent activity
- **Real-time visualization**: Watch agents scan, flag, and analyze content
- **Interactive trust scoring**: See how each agent contributes to the final score

### 📊 Comprehensive Trust Reporting
- **Individual agent scores**: Privacy, Bias, Transparency, Ethics
- **Weighted overall score**: 0-100 trust rating
- **Actionable alerts**: Specific warnings and recommendations
- **Decision logic**: Clear explanation of block/warn/proceed decisions

### 🎮 "Break Me" Challenge Mode
- **Edge case testing**: Try to trick the system
- **Live agent responses**: Watch how agents handle difficult inputs
- **Educational feedback**: Learn why certain content is flagged

### 🔧 Technical Excellence
- **Crew AI integration**: Multi-agent orchestration
- **Local LLM support**: Ollama with Llama3 for privacy
- **Extensible architecture**: Easy to add new agent types
- **Comprehensive logging**: Full audit trail for compliance

## 🤝 Contributing

We welcome contributions to make VERITAS even more robust! Areas for improvement:

- **New Agent Types**: Add specialized guardians (e.g., Security, Accessibility)
- **Enhanced Scoring**: Improve trust calculation algorithms
- **UI Development**: Build the split-screen demo interface
- **Test Coverage**: Expand edge case testing
- **Performance**: Optimize agent coordination

## 📜 License

This project is open source and available under the MIT License.

## 🆘 Support

For VERITAS-specific questions:
- **Crew AI Documentation**: [docs.crewai.com](https://docs.crewai.com)
- **Ollama Documentation**: [ollama.ai](https://ollama.ai/)
- **Issues**: Report bugs or request features via GitHub Issues

---

**🛡️ VERITAS - Building Trust in AI, One Response at a Time**

*"The First Chatbot That Checks Itself Before It Wrecks Itself"*
