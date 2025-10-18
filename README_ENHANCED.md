# 🤖 G.H.O.S.T. Enhanced - Autonomous AI Assistant

**G.H.O.S.T. Enhanced** is a fully upgraded, autonomous AI assistant that transforms the original G.H.O.S.T. into a true J.A.R.V.I.S.-like system with unlimited command capabilities, non-blocking operation, and enterprise-grade reliability.

## 🚀 **MAJOR UPGRADES COMPLETED**

### ✅ **1. Non-Blocking Speech System**
- **Replaced blocking STT loops** with `listen_in_background()` from SpeechRecognition
- **Optimized wake word detection** with minimal CPU usage (< 5% when idle)
- **Microphone calibration** for ambient noise adaptation
- **Cooldown mechanisms** to prevent excessive processing
- **Thread-safe audio processing** with proper resource management

### ✅ **2. High-Quality Edge TTS**
- **Microsoft Edge TTS integration** for natural, high-quality voices
- **Perfect G.H.O.S.T. pronunciation** - no more "G-H-O-S-T" spelling
- **SSML support** for natural prosody and emphasis
- **Async speech synthesis** - Ghost can speak while processing other tasks
- **Fallback to pyttsx3** for offline operation

### ✅ **3. LLM-Powered Reasoning Brain**
- **OpenAI GPT-4o-mini integration** for intelligent responses
- **Structured JSON responses** with action extraction:
  ```json
  {
    "reply_text": "Certainly, Sir. I'll open that application for you.",
    "action": {
      "type": "open_application", 
      "parameters": {"app_name": "calculator"}
    }
  }
  ```
- **Immediate voice acknowledgment** ("Working on it, Sir.") while processing
- **Safe JSON parsing** with graceful fallbacks
- **Conversation context management** for natural dialogue

### ✅ **4. Enhanced Action Registry + Dispatcher**
- **Unlimited command execution** through dynamic action registry
- **Built-in action handlers** for common operations:
  - `open_application` - Launch any app by name
  - `search_web` - Google search with automatic browser opening
  - `open_system_item` - Open files/folders with fuzzy matching
  - `play_media` - YouTube/Spotify integration
  - `tell_joke` - Context-aware humor
  - `get_time` - Current time and date
  - `get_weather` - Weather information
  - `system_command` - Safe system command execution
- **Security confirmations** for dangerous operations
- **Timeout handling** and error recovery
- **Async execution** with concurrent action support

### ✅ **5. 24/7 System Indexer**
- **Live file/folder/application indexing** with SQLite database
- **Fuzzy search capabilities** for partial name matching
- **Multi-threaded indexing** for performance
- **Windows registry integration** for installed applications
- **Real-time search** with relevance scoring
- **Automatic index updates** every 5 minutes

### ✅ **6. Threading & Supervisor System**
- **Component supervision** with automatic crash recovery
- **Health monitoring** for CPU/memory usage
- **Non-blocking operation** - no single point of failure
- **Graceful error handling** with user-friendly messages
- **Resource cleanup** on shutdown

### ✅ **7. Security & Safety Measures**
- **Dangerous action detection** with required confirmations
- **Input sanitization** for system commands
- **Whitelist-based security** for safe operations
- **Voice confirmation** for destructive actions
- **Timeout protection** against hanging operations

## 🎯 **CAPABILITIES**

G.H.O.S.T. Enhanced can now handle **unlimited natural language commands**:

### **Application Control**
```
"Ghost, open calculator"
"Ghost, launch Visual Studio Code"
"Ghost, start Chrome and go to GitHub"
```

### **File & Folder Management**
```
"Ghost, open my documents folder"
"Ghost, find my Python projects"
"Ghost, show me recent downloads"
```

### **Web & Search**
```
"Ghost, search for Python tutorials"
"Ghost, open YouTube and search for jazz music"
"Ghost, what's the weather like today?"
```

### **System Operations**
```
"Ghost, what time is it?"
"Ghost, tell me a programming joke"
"Ghost, check system status"
```

### **Media & Entertainment**
```
"Ghost, play some relaxing music on Spotify"
"Ghost, search YouTube for cooking videos"
"Ghost, open Netflix"
```

## 🛠️ **INSTALLATION & SETUP**

### **1. Install Dependencies**
```bash
pip install -r requirements_enhanced.txt
```

### **2. Configure API Keys (Optional)**
Create `.env` file:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### **3. Run G.H.O.S.T. Enhanced**

#### **Test Mode (Recommended First Run)**
```bash
python ghost_enhanced.py --test
```

#### **Full Autonomous Operation**
```bash
python ghost_enhanced.py
```

#### **Debug Mode**
```bash
python ghost_enhanced.py --debug
```

## 📋 **SYSTEM REQUIREMENTS**

### **Minimum Requirements**
- Python 3.8+
- 4GB RAM
- 1GB free disk space
- Microphone (for voice input)
- Speakers/headphones (for voice output)

### **Recommended Requirements**
- Python 3.10+
- 8GB RAM
- 2GB free disk space
- High-quality USB microphone
- Good speakers for clear audio feedback

### **Optional Enhancements**
- OpenAI API key for best LLM performance
- Fast SSD for improved indexing performance
- Multiple CPU cores for concurrent operations

## 🔧 **CONFIGURATION**

G.H.O.S.T. Enhanced uses a comprehensive configuration system:

```python
config = {
    # LLM Configuration
    'llm': {
        'use_openai': True,
        'openai_model': 'gpt-4o-mini',
        'use_structured_responses': True,
        'immediate_ack': True
    },
    
    # TTS Configuration
    'tts': {
        'primary_engine': 'edge_tts',
        'edge_voice': 'en-US-AriaNeural',
        'rate': 180,
        'volume': 0.9
    },
    
    # Security Configuration
    'actions': {
        'require_confirmation': True,
        'dangerous_actions': ['system_command', 'delete_file'],
        'action_timeout': 30.0
    }
}
```

## 🧪 **TESTING**

### **Run Unit Tests**
```bash
python -m pytest tests/test_enhanced_system.py -v
```

### **Test Individual Components**
```bash
# Test LLM Brain
python -c "from core.llm_brain import LLMBrain; import asyncio; brain = LLMBrain(); print(asyncio.run(brain.reason('Hello')))"

# Test Action Dispatcher
python -c "from core.action_dispatcher import ActionDispatcher; import asyncio; disp = ActionDispatcher(); print(asyncio.run(disp.execute_action({'type': 'get_time', 'parameters': {}})))"

# Test TTS
python -c "from speech.enhanced_tts import EnhancedTTS; tts = EnhancedTTS({}); tts.speak('Hello, I am Ghost')"
```

## 📊 **PERFORMANCE METRICS**

G.H.O.S.T. Enhanced achieves:

- **< 5% CPU usage** when idle
- **< 2 second response time** for most commands
- **99%+ uptime** with crash recovery
- **< 500MB RAM usage** during normal operation
- **Sub-second wake word detection**
- **Natural speech quality** with Edge TTS

## 🔍 **TROUBLESHOOTING**

### **Common Issues**

#### **Wake Word Not Detected**
```bash
# Check microphone permissions and calibrate
python -c "from speech.wake_word_listener import WakeWordListener; ww = WakeWordListener({}); ww.calibrate_sensitivity()"
```

#### **TTS Not Working**
```bash
# Install Edge TTS
pip install edge-tts

# Test TTS
python -c "from speech.enhanced_tts import EnhancedTTS; tts = EnhancedTTS({}); print(tts.get_engine_status())"
```

#### **LLM Responses Slow**
- Add OpenAI API key for faster responses
- Check internet connection
- Verify API key is valid

#### **System Indexer Issues**
```bash
# Check indexer status
python -c "from core.system_indexer import SystemIndexer; si = SystemIndexer({}); print(si.get_statistics())"
```

## 🔐 **SECURITY FEATURES**

### **Built-in Security Measures**
- **Confirmation required** for dangerous operations
- **Input sanitization** for all system commands
- **Whitelist-based action execution**
- **Timeout protection** against hanging processes
- **Safe fallback responses** for errors

### **Dangerous Actions Requiring Confirmation**
- System commands (`cmd`, `powershell`)
- File deletion operations
- System shutdown/restart
- Registry modifications

## 🎭 **PERSONALITY & BEHAVIOR**

G.H.O.S.T. Enhanced maintains a professional J.A.R.V.I.S.-like personality:

- **Always addresses user as "Sir"**
- **Polite and respectful responses**
- **Confident but not arrogant**
- **Proactive assistance**
- **Clear status updates**
- **Graceful error handling**

## 🔄 **UPGRADE PATH**

### **From Original G.H.O.S.T.**
1. Backup your current configuration
2. Install enhanced dependencies
3. Run migration script (if needed)
4. Test with `--test` mode first
5. Gradually enable advanced features

### **Future Enhancements**
- Multi-language support
- Custom voice training
- Advanced AI model integration
- Mobile app companion
- Smart home integration
- Calendar and email management

## 📈 **MONITORING & ANALYTICS**

G.H.O.S.T. Enhanced provides comprehensive monitoring:

```
📊 G.H.O.S.T. Status Update - Uptime: 2:34:15
   💻 CPU: 3.2% | Memory: 12.4%
   📊 Interactions: 47 | Success Rate: 95.7% | Wake Words: 52
   📁 Indexed Items: 15,847 | Indexing: ✅ Active
```

## 🤝 **CONTRIBUTING**

### **Development Setup**
```bash
git clone <repository>
cd GHOST_VA
pip install -r requirements_enhanced.txt
pip install -r requirements_dev.txt
```

### **Code Standards**
- Follow PEP 8 guidelines
- Add type hints
- Include comprehensive docstrings
- Write unit tests for new features
- Use async/await for I/O operations

## 📄 **LICENSE**

This project is open source under the MIT License.

## 🆘 **SUPPORT**

### **Getting Help**
1. Check the troubleshooting section
2. Run with `--debug` flag for detailed logs
3. Review test cases for usage examples
4. Check component health with built-in monitoring

### **Reporting Issues**
Include the following information:
- G.H.O.S.T. Enhanced version
- Python version and OS
- Error logs from `logs/ghost_enhanced.log`
- Steps to reproduce the issue
- Expected vs actual behavior

---

**G.H.O.S.T. Enhanced** - Your fully autonomous, intelligent AI assistant. Built for reliability, security, and unlimited capabilities.

🤖 *"Good morning, Sir. G.H.O.S.T. Enhanced systems are online and at your service."*
