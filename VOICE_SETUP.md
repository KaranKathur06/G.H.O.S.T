# G.H.O.S.T. Voice System Setup Guide

This guide will help you set up G.H.O.S.T.'s advanced voice system with natural speech synthesis and offline voice recognition.

## 🎯 Overview

G.H.O.S.T.'s voice system includes:
- **Offline Speech Recognition** using VOSK
- **Natural Text-to-Speech** using Coqui TTS with pyttsx3 fallback
- **Wake Word Detection** for hands-free operation
- **Personality-Aware Speech** with natural pauses and emphasis
- **Perfect G.H.O.S.T. Pronunciation** (says "Ghost" not "G-H-O-S-T")

## 📦 Installation

### Step 1: Install Voice Dependencies

```bash
# Install voice system requirements
pip install -r requirements_voice.txt

# Core dependencies (if installing manually)
pip install pyttsx3 pyaudio vosk TTS pygame numpy scipy
```

### Step 2: Download VOSK Model

```bash
# Create models directory
mkdir models

# Download small English model (39MB)
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip

# Extract to models directory
unzip vosk-model-small-en-us-0.15.zip -d models/

# Verify installation
ls models/vosk-model-small-en-us-0.15/
```

### Step 3: Test Audio System

```bash
# Test microphone and speakers
python tests/test_voice.py --test

# Run voice demonstration
python tests/test_voice.py --demo
```

## 🔧 Configuration

### Voice Configuration (`data/config/config.json`)

```json
{
  "voice": {
    "enabled": true,
    "primary_engine": "coqui",
    "fallback_engine": "pyttsx3",
    "voice_speed": 1.0,
    "volume": 0.9
  },
  "speech_to_text": {
    "enabled": true,
    "model_path": "models/vosk-model-small-en-us-0.15",
    "wake_words": ["ghost", "hey ghost"],
    "sample_rate": 16000,
    "energy_threshold": 300
  },
  "personality": {
    "profile": "assistant"
  }
}
```

### Personality Profiles

Choose from different personality profiles:

- **`assistant`** - Professional and helpful
- **`companion`** - Friendly and enthusiastic  
- **`expert`** - Technical and confident

## 🎤 Voice Features

### 1. Natural Speech Synthesis

G.H.O.S.T. uses Coqui TTS for natural-sounding speech:

```python
from speech.text_to_speech import VoiceManager

voice_manager = VoiceManager(config)

# Basic speech
voice_manager.speak("Hello! I am G.H.O.S.T.")

# Speech with style
voice_manager.speak_with_style("Great job!", "excited")
voice_manager.speak_with_style("Let me think about that...", "calm")
```

### 2. Perfect G.H.O.S.T. Pronunciation

The system automatically converts text for proper pronunciation:

```
Input:  "I am G.H.O.S.T."
Output: "I am Ghost."

Input:  "G H O S T systems online"
Output: "Ghost systems online"
```

### 3. Speech Styles

Available speech styles:
- **normal** - Standard speaking voice
- **excited** - Enthusiastic and energetic
- **calm** - Slow and soothing
- **formal** - Professional tone
- **friendly** - Warm and approachable

### 4. Wake Word Detection

G.H.O.S.T. listens for wake words in the background:

```python
# Start wake word detection
wake_detector.start_listening(on_wake_word_callback)

# Wake words: "ghost", "hey ghost"
# User: "Ghost, what time is it?"
# G.H.O.S.T.: "The current time is 3:45 PM."
```

## 🎭 Personality System

### Using Personality Features

```python
from core.personality import GhostPersonality

personality = GhostPersonality(config)

# Get contextual greeting
greeting = personality.get_greeting("John", is_first_time=True)
# Output: "Hello John! I'm G.H.O.S.T., your virtual assistant. Great to meet you!"

# Get confirmation with style
confirmation = personality.get_confirmation("open Chrome")
# Output: "Right away." (professional) or "You got it!" (enthusiastic)

# Enhance responses
enhanced = personality.enhance_response("Task completed.")
# Output: "Great! Task completed successfully."
```

### Personality Traits

- **Professional** - Formal language, confident responses
- **Friendly** - Warm greetings, enthusiastic confirmations
- **Enthusiastic** - Exclamation points, energy words
- **Calm** - Soothing pauses, gentle language
- **Witty** - Occasional humor and clever responses

## 🛠️ Usage Examples

### Basic Voice Interaction

```python
# Initialize voice system
from core.brain_orchestrator import BrainOrchestrator

config = {
    'voice': {'enabled': True},
    'speech_to_text': {'enabled': True},
    'personality': {'profile': 'assistant'}
}

orchestrator = BrainOrchestrator(config)
orchestrator.start()

# G.H.O.S.T. will:
# 1. Greet you with personality
# 2. Listen for wake word "Ghost"
# 3. Process your commands with natural responses
# 4. Speak with perfect pronunciation
```

### Custom Voice Integration

```python
from speech.text_to_speech import VoiceManager
from core.personality import GhostPersonality

# Initialize components
voice_manager = VoiceManager(voice_config)
personality = GhostPersonality(personality_config)

# Create natural interaction
user_input = "I'm feeling bored"
response = "I can help with that! Would you like me to tell you a joke?"

# Enhance with personality
enhanced_response = personality.enhance_response(response, {'context': 'boredom'})

# Speak with appropriate style
voice_manager.speak(enhanced_response, style="friendly")
```

## 🔍 Testing Voice System

### Run Comprehensive Tests

```bash
# Test all voice components
python tests/test_voice.py

# Test specific features
python -c "
from tests.test_voice import TestVoiceSystem
import unittest

# Test G.H.O.S.T. pronunciation
suite = unittest.TestSuite()
suite.addTest(TestVoiceSystem('test_ghost_pronunciation'))
runner = unittest.TextTestRunner()
runner.run(suite)
"
```

### Voice Quality Tests

```bash
# Test different speech styles
python -c "
from speech.text_to_speech import VoiceManager

config = {'primary_engine': 'pyttsx3'}
vm = VoiceManager(config)

styles = ['normal', 'excited', 'calm', 'formal', 'friendly']
for style in styles:
    print(f'Testing {style} style...')
    vm.speak_with_style(f'This is the {style} speaking style.', style)
    input('Press Enter for next style...')
"
```

## 🚨 Troubleshooting

### Common Issues

**1. VOSK Model Not Found**
```
Error: VOSK model not found at models/vosk-model-small-en-us-0.15
Solution: Download the model using the commands in Step 2
```

**2. Audio Device Issues**
```bash
# List available audio devices
python -c "
from speech.speech_to_text import SpeechToText
stt = SpeechToText({'model_path': 'models/vosk-model-small-en-us-0.15'})
info = stt.get_microphone_info()
for device in info['available_devices']:
    print(f'{device[\"index\"]}: {device[\"name\"]}')
"

# Test microphone
python -c "
from speech.speech_to_text import SpeechToText
stt = SpeechToText({'model_path': 'models/vosk-model-small-en-us-0.15'})
stt.test_microphone()
"
```

**3. TTS Engine Issues**
```bash
# Test pyttsx3 fallback
python -c "
from speech.text_to_speech import VoiceManager
vm = VoiceManager({'primary_engine': 'pyttsx3'})
vm.test_voice()
"

# List available voices
python -c "
from speech.text_to_speech import VoiceManager
vm = VoiceManager({'primary_engine': 'pyttsx3'})
voices = vm.get_available_voices()
for voice in voices:
    print(f'{voice[\"name\"]} ({voice[\"engine\"]})')
"
```

**4. Coqui TTS Issues**
```bash
# Test Coqui TTS installation
python -c "
try:
    from TTS.api import TTS
    tts = TTS('tts_models/en/ljspeech/glow-tts')
    print('Coqui TTS working!')
except Exception as e:
    print(f'Coqui TTS error: {e}')
    print('Falling back to pyttsx3')
"
```

### Performance Optimization

**1. Faster Startup**
```bash
# Pre-download Coqui TTS model
python -c "from TTS.api import TTS; TTS('tts_models/en/ljspeech/glow-tts')"
```

**2. Lower Latency**
```json
{
  "voice": {
    "primary_engine": "pyttsx3"
  },
  "speech_to_text": {
    "chunk_size": 2000,
    "energy_threshold": 200
  }
}
```

**3. Better Quality**
```json
{
  "voice": {
    "primary_engine": "coqui",
    "voice_model": "tts_models/en/ljspeech/glow-tts"
  },
  "speech_to_text": {
    "model_path": "models/vosk-model-en-us-0.22"
  }
}
```

## 🎯 Advanced Features

### Custom Pronunciation Rules

```python
from speech.text_to_speech import VoiceManager

voice_manager = VoiceManager(config)

# Add custom pronunciations
voice_manager.add_pronunciation_rule("API", "Application Programming Interface")
voice_manager.add_pronunciation_rule("SQL", "Structured Query Language")

# Test custom rule
voice_manager.speak("The API uses SQL queries.")
# Speaks: "The Application Programming Interface uses Structured Query Language queries."
```

### Voice Style Customization

```python
from core.personality import GhostPersonality

personality = GhostPersonality(config)

# Customize personality responses
personality.current_profile.confirmation_style = "enthusiastic"

confirmation = personality.get_confirmation("search the web")
# Output: "Absolutely! I'll search the web for you!"
```

### Wake Word Customization

```python
from speech.speech_to_text import SpeechToText

stt = SpeechToText(config)

# Add custom wake words
stt.add_wake_word("computer")
stt.add_wake_word("assistant")

# Now responds to: "ghost", "hey ghost", "computer", "assistant"
```

## 📚 API Reference

### VoiceManager Methods

```python
# Speech synthesis
speak(text: str, interrupt: bool = True, style: str = "normal") -> bool
speak_with_style(text: str, style: str = "normal") -> bool

# Voice control
stop() -> None
is_speaking_now() -> bool
set_voice(voice_name: str) -> bool

# Configuration
get_available_voices() -> List[Dict[str, Any]]
add_pronunciation_rule(original: str, replacement: str) -> None
test_voice(test_text: str = None) -> bool
```

### SpeechToText Methods

```python
# Speech recognition
listen(timeout: float = 5.0, phrase_timeout: float = 1.0) -> Optional[str]
continuous_listen(callback: Callable, wake_word_only: bool = True) -> None

# Configuration
calibrate_microphone(duration: float = 2.0) -> None
get_microphone_info() -> Dict[str, Any]
test_microphone() -> bool
```

### GhostPersonality Methods

```python
# Response generation
get_greeting(user_name: str = None, is_first_time: bool = False) -> str
get_confirmation(action: str = None) -> str
get_farewell(user_name: str = None) -> str
enhance_response(response: str, context: Dict = None) -> str
```

---

**G.H.O.S.T. Voice System** - Natural, offline, and completely free voice interaction for your virtual assistant!
