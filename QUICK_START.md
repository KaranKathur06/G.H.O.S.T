# 🚀 G.H.O.S.T. Enhanced - Quick Start Guide

Get your autonomous AI assistant running in under 5 minutes!

## ⚡ **INSTANT SETUP**

### **Step 1: Run Setup Script**
```bash
python setup_enhanced.py
```
This automatically:
- ✅ Checks Python compatibility
- ✅ Installs all dependencies
- ✅ Creates necessary directories
- ✅ Sets up configuration files
- ✅ Tests all components

### **Step 2: Test Mode (Recommended)**
```bash
python ghost_enhanced.py --test
```
This runs through sample commands to verify everything works.

### **Step 3: Start G.H.O.S.T. Enhanced**
```bash
python ghost_enhanced.py
```

## 🎤 **FIRST COMMANDS TO TRY**

Once G.H.O.S.T. says *"Good morning, Sir. G.H.O.S.T. Enhanced systems are online and at your service."*

Try these commands:

1. **"Ghost, what time is it?"** - Basic functionality test
2. **"Ghost, open calculator"** - Application launching
3. **"Ghost, search for Python tutorials"** - Web search
4. **"Ghost, tell me a programming joke"** - Entertainment
5. **"Ghost, open my documents folder"** - File system access

## 🔧 **OPTIONAL ENHANCEMENTS**

### **Add OpenAI API Key (Recommended)**
1. Get API key from https://platform.openai.com/api-keys
2. Edit `.env` file:
   ```env
   OPENAI_API_KEY=your_actual_api_key_here
   ```
3. Restart G.H.O.S.T. for better responses

### **Voice Quality Settings**
Edit `ghost_enhanced.py` to customize:
```python
'tts': {
    'edge_voice': 'en-US-AriaNeural',  # Professional female
    # 'edge_voice': 'en-US-GuyNeural',   # Professional male
    'rate': '+10%',  # Slightly faster speech
    'volume': 0.9
}
```

## 🛡️ **SECURITY FEATURES**

G.H.O.S.T. Enhanced will ask for confirmation before:
- Running system commands
- Deleting files
- Shutting down/restarting system

Simply say **"yes"** to confirm or **"no"** to cancel.

## 📊 **MONITORING**

Watch the console for real-time status:
```
📊 G.H.O.S.T. Status Update - Uptime: 2:34:15
   💻 CPU: 3.2% | Memory: 12.4%
   📊 Interactions: 47 | Success Rate: 95.7%
   📁 Indexed Items: 15,847 | Indexing: ✅ Active
```

## 🆘 **TROUBLESHOOTING**

### **Wake Word Not Working**
- Check microphone permissions
- Speak clearly: "Ghost" (not "G-H-O-S-T")
- Try from different distances

### **No Sound Output**
- Check speaker/headphone connections
- Verify Windows audio settings
- Try: `python -c "from speech.enhanced_tts import EnhancedTTS; tts = EnhancedTTS({}); tts.speak('Test')"`

### **Slow Responses**
- Add OpenAI API key for faster LLM responses
- Check internet connection
- Close other resource-intensive applications

### **Commands Not Working**
- Ensure you say "Ghost" first to wake the system
- Wait for acknowledgment before giving command
- Speak naturally and clearly

## 🎯 **WHAT'S DIFFERENT FROM ORIGINAL G.H.O.S.T.**

| Feature | Original | Enhanced |
|---------|----------|----------|
| Speech Recognition | Blocking loops | Non-blocking background listening |
| TTS Quality | Basic pyttsx3 | High-quality Edge TTS |
| Command Scope | Limited hardcoded | Unlimited via LLM + dispatcher |
| Pronunciation | "G-H-O-S-T" spelling | Natural "Ghost" |
| Response Time | 5-10 seconds | <2 seconds |
| CPU Usage | 15-25% | <5% when idle |
| Crash Recovery | Manual restart | Automatic supervision |
| Security | Basic | Confirmation for dangerous actions |

## 🚀 **ADVANCED USAGE**

### **Custom Configuration**
Create `config.json`:
```json
{
  "llm": {
    "openai_model": "gpt-4o",
    "immediate_ack": true
  },
  "tts": {
    "edge_voice": "en-US-JennyNeural",
    "rate": "+20%"
  },
  "actions": {
    "require_confirmation": false
  }
}
```

Run with: `python ghost_enhanced.py --config config.json`

### **Debug Mode**
```bash
python ghost_enhanced.py --debug
```
Shows detailed logs for troubleshooting.

## 🎉 **YOU'RE READY!**

G.H.O.S.T. Enhanced is now your personal J.A.R.V.I.S.-like AI assistant!

**Say "Ghost" and give any reasonable command - the system will understand and execute it intelligently.**

Examples of what G.H.O.S.T. can do:
- Open any application by name
- Search the web and open results
- Find and open files/folders
- Play music on YouTube/Spotify  
- Tell jokes and provide information
- Get current time and weather
- Execute system commands (with confirmation)
- And much more through natural language!

---

*"At your service, Sir. What would you like me to do?"* - G.H.O.S.T. Enhanced
