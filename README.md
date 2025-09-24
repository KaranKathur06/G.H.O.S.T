# 🤖 G.H.O.S.T. - Autonomous AI Assistant

**G.H.O.S.T.** (Generative Hybrid Omnipresent Support Technology) is a **fully autonomous, 24x7 J.A.R.V.I.S.-like AI assistant** built with Python. This is a complete transformation from a basic voice assistant into a true reasoning AI companion that can understand and execute ANY natural language request intelligently.

## 🎉 **AUTONOMOUS AI EVOLUTION COMPLETE!**

G.H.O.S.T. has evolved into a **true autonomous AI assistant** with:
- 🧠 **Universal Natural Language Understanding** - No hardcoded command limitations
- 🤖 **24/7 Autonomous Operation** - Continuous wake word detection and processing
- 🎯 **Intelligent Decision-Making** - Asks clarifying questions and provides options
- 🔍 **Dynamic System Indexing** - Real-time discovery of all files, apps, and resources
- ⚡ **Smart Action Execution** - Can launch any app, play any media, control system
- 🧠 **LLM-Powered Reasoning** - ChatGPT-style conversation and knowledge
- 🎭 **J.A.R.V.I.S. Personality** - Professional, respectful, addresses user as "Sir"
- 📈 **Continuous Learning** - Improves responses based on user interactions

## 🏗️ Generative AI Architecture

Clean, modular architecture focused on true AI capabilities:

```
GHOST_VA/
├── core/                         # Autonomous AI Brain
│   ├── universal_nlu.py          # Universal Natural Language Understanding
│   ├── llm_brain.py              # LLM-Based Reasoning Engine
│   ├── decision_engine.py        # Intelligent Decision-Making
│   ├── smart_action_engine.py    # Dynamic Action Execution
│   ├── system_indexer.py         # 24/7 System Indexing
│   ├── autonomous_manager.py     # 24/7 Operation Manager
│   └── enhanced_personality.py   # J.A.R.V.I.S. Personality
├── speech/                       # Voice Intelligence
│   ├── enhanced_tts.py           # G.H.O.S.T. pronunciation TTS
│   ├── speech_to_text.py         # Speech recognition
│   └── wake_word_listener.py     # Wake word detection
├── actions/                      # Modular Skills
│   ├── base_action.py            # Action framework
│   ├── app_launcher.py           # Application launching
│   ├── web_search.py             # Web search functionality
│   ├── system_control.py         # System operations
│   ├── weather.py                # Weather information
│   └── entertainment.py          # Jokes and entertainment
├── data/                         # Configuration & Storage
│   ├── config_manager.py         # Configuration management
│   └── logger_setup.py           # Logging setup
├── ghost_autonomous.py          # 🚀 Main Autonomous AI System
├── orchestrator.py              # Legacy System Orchestrator
└── tests/                        # Unit tests
```

## 🚀 Quick Start - Generative AI

### Prerequisites

- Python 3.8 or higher
- Windows, macOS, or Linux
- Microphone (for voice input - optional)
- Speakers/headphones (for voice output - optional)

### Installation

1. **Clone or download the project**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Run G.H.O.S.T. Autonomous AI

#### Option 1: Test Mode (Recommended for first run)
```bash
python ghost_autonomous.py --test        # Test with sample commands
```

#### Option 2: Full Autonomous Operation
```bash
python ghost_autonomous.py               # 24/7 autonomous mode with voice
python ghost_autonomous.py --debug       # Debug mode with detailed logging
```

#### Option 3: Legacy System
```bash
python orchestrator.py --test    # Test legacy components
python orchestrator.py --voice   # Legacy voice interaction mode
```

### Natural Language Examples

G.H.O.S.T. now understands natural language! Try these:

**Time & Date:**
- "What time is it right now?"
- "What's today's date?"

**Applications:**
- "Open calculator for me"
- "Launch notepad please"

**Web & Search:**
- "Open Wikipedia and search for AI"
- "Search for Python tutorials"

**Entertainment:**
- "Tell me a joke about computers"
- "Make me laugh"

**Conversational:**
- "Hello G.H.O.S.T., how are you?"
- "What can you help me with?"
- "Good morning, what's the weather like?"

## 🔧 Configuration

### Main Configuration

The assistant uses JSON configuration files in the `data/config/` directory:

- `config.json` - Main settings
- `paths.json` - Application paths
- `.env` - API keys and secrets

### Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Weather API
OPENWEATHER_API_KEY=your_api_key_here

# Speech Recognition (optional)
GOOGLE_SPEECH_API_KEY=your_api_key_here
```

### Application Paths

Edit `data/config/paths.json` to customize application paths:

```json
{
  "applications": {
    "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "vscode": "C:\\Users\\%USERNAME%\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"
  }
}
```

## 🎯 Features

### Core Capabilities

- **Voice Recognition**: Converts speech to text using multiple engines
- **Natural Language Processing**: Understands user intents and commands
- **Voice Synthesis**: Responds with natural speech
- **Memory Management**: Remembers conversations and user preferences
- **Modular Actions**: Extensible system for adding new capabilities

### Built-in Actions

1. **Application Launcher**: Open programs by voice command
2. **Web Search**: Search using Google, Bing, DuckDuckGo, etc.
3. **System Control**: Get time/date, control system power
4. **Weather Information**: Current weather for any location
5. **Entertainment**: Jokes, fun facts, and inspirational quotes

## 🔌 Extending G.H.O.S.T.

### Adding New Actions

1. **Create a new action handler:**
   ```python
   # actions/my_action.py
   from .base_action import BaseAction
   
   class MyAction(BaseAction):
       def execute(self, parameters):
           # Your action logic here
           return {'success': True, 'message': 'Action completed'}
       
       def get_description(self):
           return "Description of what this action does"
   ```

2. **Register the action:**
   ```python
   # In action_dispatcher.py
   self.register_handler('my_action', MyAction(config))
   ```

3. **Add intent patterns:**
   ```python
   # In reasoning_engine.py
   self.intent_patterns['my_action'] = [
       r'do something with (.+)',
       r'perform (.+) action'
   ]
   ```

### Switching Speech Engines

The modular design allows easy switching between speech engines:

```python
# In config.json
{
  "speech": {
    "stt": {
      "engine": "google",  # or "sphinx", "azure"
    },
    "tts": {
      "engine": "pyttsx3"  # or "azure", "google"
    }
  }
}
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_core.py

# Run with coverage
python -m pytest tests/ --cov=.
```

## 📊 Monitoring and Debugging

### Logging

G.H.O.S.T. provides comprehensive logging:

- **Main log**: `data/logs/ghost.log`
- **Error log**: `data/logs/errors.log`
- **Console output**: Real-time status updates

### Debug Mode

Start with debug mode for detailed logging:

```bash
python main.py --debug
```

### Configuration Validation

The system validates configuration on startup and reports:
- Missing required settings
- Invalid file paths
- Missing API keys

## 🔒 Security Considerations

- **API Keys**: Store in `.env` file, never commit to version control
- **System Operations**: Dangerous operations require confirmation
- **File Paths**: Validate all file paths before execution
- **Input Sanitization**: All user inputs are sanitized

## 🚀 Production Deployment

### Performance Optimization

1. **Disable debug mode** in production
2. **Configure log rotation** to prevent disk space issues
3. **Set appropriate memory limits** for conversation history
4. **Use production-grade speech engines** for better accuracy

### Service Installation

Create a system service for automatic startup:

```bash
# Example systemd service (Linux)
sudo cp ghost.service /etc/systemd/system/
sudo systemctl enable ghost
sudo systemctl start ghost
```

## 🤝 Contributing

### Development Setup

1. **Install development dependencies:**
   ```bash
   pip install -r requirements_ghost.txt
   pip install black flake8 pytest
   ```

2. **Run code formatting:**
   ```bash
   black .
   flake8 .
   ```

3. **Run tests before committing:**
   ```bash
   pytest tests/
   ```

### Code Style

- Follow PEP 8 guidelines
- Use type hints where possible
- Add docstrings to all classes and functions
- Keep functions focused and modular

## 📝 License

This project is open source. See LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

**Speech recognition not working:**
- Check microphone permissions
- Install PyAudio: `pip install pyaudio`
- Try different speech engines

**Applications not launching:**
- Verify paths in `data/config/paths.json`
- Check file permissions
- Use absolute paths

**Import errors:**
- Ensure all dependencies are installed
- Check Python path configuration
- Verify module structure

### Getting Help

1. Check the logs in `data/logs/`
2. Run with `--debug` flag for detailed output
3. Validate configuration with built-in validator
4. Review the test cases for usage examples

## 🔮 Future Enhancements

The modular architecture supports easy addition of:

- **LLM Integration**: GPT, Claude, or local models
- **Smart Home Control**: IoT device management
- **Calendar Integration**: Schedule and reminder management
- **Email Management**: Voice-controlled email operations
- **Advanced Memory**: Long-term learning and adaptation
- **Multi-language Support**: International language support
- **Mobile App**: Companion mobile application
- **Plugin System**: Third-party plugin support

---

**G.H.O.S.T.** - Your intelligent, modular, and extensible virtual assistant. Built for developers, by developers.
