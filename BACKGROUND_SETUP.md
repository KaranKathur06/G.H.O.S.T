# G.H.O.S.T. Background Operation Setup Guide

Transform G.H.O.S.T. into a 24×7 background assistant that automatically responds to wake words without manual execution.

## 🌙 Overview

G.H.O.S.T. Background Mode provides:
- **24×7 Operation** - Runs continuously in the background
- **Wake Word Activation** - Say "Ghost" to activate voice commands
- **System Tray Integration** - Control and monitor from system tray
- **Resource Efficient** - Minimal CPU usage when idle
- **Auto-Startup** - Automatically starts with Windows
- **State Management** - Smart state transitions (IDLE → LISTENING → RESPONDING)

## 📦 Installation

### Step 1: Install Background Dependencies

```bash
# Install background operation requirements
pip install -r requirements_background.txt

# Key packages installed:
# - pystray (system tray)
# - Pillow (tray icons)  
# - pyaudio (audio input)
# - vosk (wake word detection)
# - psutil (system monitoring)
```

### Step 2: Download Wake Word Model

```bash
# Create models directory
mkdir models

# Download VOSK model for wake word detection (39MB)
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip -d models/

# Verify model installation
ls models/vosk-model-small-en-us-0.15/
```

### Step 3: Test Background System

```bash
# Test wake word detection
python tests/test_wake_word.py --test

# Test system tray (if available)
python -c "import pystray, PIL; print('System tray ready!')"

# Test audio system
python -c "import pyaudio; print('Audio system ready!')"
```

## 🚀 Quick Start

### Method 1: Using Startup Scripts (Recommended)

```bash
# 1. Install G.H.O.S.T. to Windows startup
cd scripts
install_startup.bat

# 2. G.H.O.S.T. will now start automatically with Windows
# 3. Look for G.H.O.S.T. icon in system tray
# 4. Say "Ghost" to activate voice commands
```

### Method 2: Manual Background Start

```bash
# Start G.H.O.S.T. in background mode
python main.py --background

# Or start silently (no console window)
pythonw main.py --background --no-console
```

### Method 3: Service Mode (Advanced)

```bash
# Start as Windows service (requires admin rights)
python -m core.background_orchestrator --service-install
net start "G.H.O.S.T. Assistant"
```

## 🎯 Usage

### Wake Word Activation

```
User: "Ghost"
G.H.O.S.T.: "Yes? How can I help?"

User: "What time is it?"
G.H.O.S.T.: "The current time is 3:45 PM."

User: "Open Chrome"
G.H.O.S.T.: "Opening Chrome for you now."
```

### System Tray Controls

Right-click the G.H.O.S.T. tray icon for:
- **G.H.O.S.T. Status** - View current state and statistics
- **Enable/Disable Listening** - Toggle wake word detection
- **Show Last Interaction** - See recent voice command
- **Settings** - Configure G.H.O.S.T. options
- **View Logs** - Open log directory
- **Exit G.H.O.S.T.** - Stop background operation

### State Machine

G.H.O.S.T. operates in different states:

1. **IDLE** 🟢 - Listening for wake word "Ghost"
2. **LISTENING** 🔵 - Capturing your voice command  
3. **RESPONDING** 🟠 - Processing and executing command
4. **DISABLED** ⚫ - Wake word detection disabled
5. **ERROR** 🔴 - Error state with automatic recovery

## ⚙️ Configuration

### Background Configuration (`data/config/config.json`)

```json
{
  "background_mode": true,
  "wake_word": {
    "enabled": true,
    "engine": "simple_energy",
    "wake_words": ["ghost", "hey ghost"],
    "confidence_threshold": 0.6,
    "energy_threshold": 300
  },
  "voice": {
    "enabled": true,
    "primary_engine": "pyttsx3",
    "volume": 0.9
  },
  "tray": {
    "enabled": true,
    "show_notifications": true
  },
  "state_machine": {
    "max_listening_duration": 30.0,
    "max_responding_duration": 60.0,
    "idle_sleep_duration": 0.1
  }
}
```

### Wake Word Engines

Choose from different wake word detection engines:

**Simple Energy Detection** (Default)
```json
{
  "wake_word": {
    "engine": "simple_energy",
    "energy_threshold": 300
  }
}
```

**VOSK Keyword Spotting** (Better accuracy)
```json
{
  "wake_word": {
    "engine": "vosk_keyword",
    "model_path": "models/vosk-model-small-en-us-0.15"
  }
}
```

**OpenWakeWord** (Advanced - requires installation)
```json
{
  "wake_word": {
    "engine": "openwakeword",
    "confidence_threshold": 0.8
  }
}
```

## 🔧 Management Scripts

### Start/Stop Scripts

```bash
# Start G.H.O.S.T. background service
scripts/start_ghost_service.bat

# Stop G.H.O.S.T. background service  
scripts/stop_ghost_service.bat

# Install to Windows startup
scripts/install_startup.bat

# Remove from Windows startup
scripts/uninstall_startup.bat
```

### Programmatic Control

```python
from core.background_orchestrator import start_ghost_background, stop_ghost_background

# Start G.H.O.S.T. programmatically
orchestrator = start_ghost_background()

# Get system status
status = orchestrator.get_system_status()
print(f"Current state: {status['current_state']}")

# Handle system commands
result = orchestrator.handle_system_command("disable_listening")
print(f"Command result: {result}")

# Stop G.H.O.S.T.
stop_ghost_background(orchestrator)
```

## 📊 Monitoring

### System Status

```python
# Get comprehensive status
status = orchestrator.get_system_status()

print(f"Running: {status['is_running']}")
print(f"State: {status['current_state']}")  
print(f"Uptime: {status['uptime_seconds']}s")
print(f"Interactions: {status['interaction_count']}")
print(f"Wake words: {status['wake_word_count']}")
```

### Log Files

G.H.O.S.T. creates detailed logs in `data/logs/`:
- `ghost.log` - General system logs
- `brain.log` - Brain reasoning and decisions  
- `memory.log` - Memory operations
- `voice.log` - Voice system events
- `system.log` - Background operation logs

### Performance Monitoring

```bash
# Monitor resource usage
python -c "
import psutil
from core.background_orchestrator import BackgroundOrchestrator

# Check G.H.O.S.T. process
for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
    if 'python' in proc.info['name'].lower():
        print(f'PID: {proc.info[\"pid\"]} CPU: {proc.info[\"cpu_percent\"]}% Memory: {proc.info[\"memory_info\"].rss / 1024 / 1024:.1f}MB')
"
```

## 🛠️ Troubleshooting

### Common Issues

**1. Wake Word Not Working**
```bash
# Check microphone permissions
python tests/test_wake_word.py --simulate

# Test audio input
python -c "
from speech.wake_word_listener import WakeWordListener
config = {'engine': 'simple_energy', 'wake_words': ['ghost']}
listener = WakeWordListener(config)
listener.test_detection()
"

# Calibrate microphone sensitivity
python -c "
from speech.wake_word_listener import WakeWordListener
config = {'engine': 'simple_energy'}
listener = WakeWordListener(config)
listener.calibrate_sensitivity(duration=5.0)
"
```

**2. System Tray Not Appearing**
```bash
# Check if pystray is installed
pip install pystray pillow

# Test tray functionality
python -c "
from ui.system_tray import create_tray_manager
config = {'tray': {'enabled': True}}
tray = create_tray_manager(config)
print('Tray manager created successfully')
"
```

**3. High CPU Usage**
```bash
# Check wake word detection efficiency
python tests/test_wake_word.py --test

# Adjust sleep duration in config
{
  "state_machine": {
    "idle_sleep_duration": 0.2  // Increase for lower CPU usage
  }
}
```

**4. Background Process Not Starting**
```bash
# Check for errors in logs
type data\logs\system.log

# Test background orchestrator
python -c "
from core.background_orchestrator import BackgroundOrchestrator
config = {'background_mode': True}
orchestrator = BackgroundOrchestrator(config)
print('Background orchestrator created')
"
```

**5. VOSK Model Issues**
```bash
# Re-download VOSK model
rmdir /s models\vosk-model-small-en-us-0.15
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip -d models/

# Test VOSK installation
python -c "
import vosk
print('VOSK installed successfully')
"
```

### Debug Mode

```bash
# Start with debug logging
python main.py --background --debug

# Check debug logs
tail -f data/logs/system.log
```

### Resource Optimization

**Low Resource Mode**
```json
{
  "wake_word": {
    "engine": "simple_energy",
    "chunk_size": 2048,
    "sample_rate": 8000
  },
  "voice": {
    "primary_engine": "pyttsx3"
  },
  "state_machine": {
    "idle_sleep_duration": 0.2
  }
}
```

**High Accuracy Mode**
```json
{
  "wake_word": {
    "engine": "vosk_keyword", 
    "model_path": "models/vosk-model-en-us-0.22",
    "chunk_size": 1024,
    "sample_rate": 16000
  },
  "voice": {
    "primary_engine": "coqui"
  }
}
```

## 🔄 Updates and Maintenance

### Updating G.H.O.S.T.

```bash
# Stop background service
scripts/stop_ghost_service.bat

# Update code
git pull origin main

# Update dependencies  
pip install -r requirements_background.txt --upgrade

# Restart service
scripts/start_ghost_service.bat
```

### Backup Configuration

```bash
# Backup user data
xcopy data\config backup\config /E /I
xcopy data\memory backup\memory /E /I
xcopy data\logs backup\logs /E /I
```

### Reset G.H.O.S.T.

```bash
# Stop service
scripts/stop_ghost_service.bat

# Clear memory and logs
rmdir /s data\memory
rmdir /s data\logs

# Restart with fresh state
scripts/start_ghost_service.bat
```

## 🚀 Advanced Features

### Custom Wake Words

```python
from speech.wake_word_listener import WakeWordListener

config = {
    'engine': 'simple_energy',
    'wake_words': ['computer', 'assistant', 'jarvis']
}

listener = WakeWordListener(config)
```

### Multiple Instances

```bash
# Run multiple G.H.O.S.T. instances with different configs
python main.py --background --config config1.json
python main.py --background --config config2.json
```

### Remote Control

```python
# Control G.H.O.S.T. remotely via API
import requests

# Send command to running G.H.O.S.T. instance
response = requests.post('http://localhost:8080/api/command', 
                        json={'command': 'status'})
print(response.json())
```

## 📚 API Reference

### BackgroundOrchestrator Methods

```python
# System control
start_background_operation() -> bool
stop_background_operation() -> None
get_system_status() -> Dict[str, Any]
handle_system_command(command: str, args: Dict = None) -> Dict[str, Any]

# State management  
state_machine.get_current_state() -> GhostState
state_machine.transition_to(state: GhostState, trigger: str) -> bool
state_machine.get_state_history(limit: int = 10) -> List[Dict]
```

### System Commands

```python
# Available system commands
commands = [
    "status",           # Get system status
    "enable_listening", # Enable wake word detection  
    "disable_listening",# Disable wake word detection
    "restart_wake_word",# Restart wake word detection
    "shutdown"          # Stop G.H.O.S.T.
]

# Execute command
result = orchestrator.handle_system_command("status")
```

---

**G.H.O.S.T. Background Operation** - Your 24×7 AI assistant, always ready to help!
