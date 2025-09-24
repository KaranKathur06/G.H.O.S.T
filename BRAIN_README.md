# G.H.O.S.T. Brain System - Advanced AI Integration

This document explains the advanced Brain system that transforms G.H.O.S.T. from a simple command-driven assistant into a context-aware, reasoning AI companion.

## 🧠 Brain System Overview

The Brain system consists of four core components:

### 1. **Brain (`core/brain.py`)**
- Central reasoning engine that processes natural language
- Analyzes user intent and chooses appropriate actions
- Provides conversational fallback when no action matches
- Supports multiple reasoning modes (offline/online/hybrid)

### 2. **Advanced Memory (`core/memory.py`)**
- SQLite-based persistent storage system
- Stores conversations, preferences, reminders, and context
- Supports search, filtering, and automatic cleanup
- Thread-safe with proper data management

### 3. **Wake Word Detection (`core/wake_word.py`)**
- Always-listening background mode
- Activates assistant when "Ghost" is detected
- Supports multiple detection engines (Porcupine, VOSK, Simple)
- Lightweight and runs offline

### 4. **Brain Orchestrator (`core/brain_orchestrator.py`)**
- Replaces original orchestrator with brain-powered version
- Integrates all brain components seamlessly
- Manages wake word detection and conversation flow
- Provides personalized user interactions

## 🚀 Quick Start with Brain Mode

### Running with Brain System

```bash
# Use advanced brain system (default)
python main.py --brain-mode

# Use legacy system
python main.py --legacy-mode

# Enable wake word detection
python main.py --brain-mode  # Wake word enabled by default
```

### First Time Setup

1. **Start G.H.O.S.T.:**
   ```bash
   python main.py
   ```

2. **The system will:**
   - Initialize the brain and memory systems
   - Create SQLite database for persistent storage
   - Start wake word detection (if enabled)
   - Greet you and wait for commands

3. **Try these interactions:**
   - Say "Ghost" (wake word) then "Open Chrome"
   - Say "Ghost" then "I'm bored" (conversational mode)
   - Say "Ghost" then "Remember my name is John"
   - Say "Ghost" then "What's the weather?"

## 🎯 Key Features

### **Natural Language Understanding**
```
User: "I'm feeling bored, can you help?"
Brain: Analyzes intent → No specific action → Conversational mode
Response: "I can help with that! Would you like me to tell you a joke, 
          play some music, or find something interesting online?"
```

### **Context Awareness**
```
User: "Open Chrome"
Brain: Executes action → Stores in memory
User: "Close it"
Brain: Uses context → Knows "it" refers to Chrome
```

### **Personalized Interactions**
```
User: "Remember my name is Sarah"
Brain: Stores in memory → Updates user preferences
Later: "Welcome back, Sarah! How can I help you today?"
```

### **Smart Action Routing**
```
User: "I want to search for Python tutorials"
Brain: Analyzes → Routes to web_search action → Executes
Response: "Searching the web for you now! [Opens browser with results]"
```

## 🔧 Configuration

### Brain Configuration (`data/config/config.json`)

```json
{
  "brain": {
    "enabled": true,
    "mode": "hybrid",
    "model_provider": "local",
    "model_name": "gpt4all",
    "confidence_threshold": 0.7,
    "max_context_length": 2000
  },
  "memory": {
    "db_path": "data/memory/ghost_memory.db",
    "max_interactions": 10000,
    "context_window_size": 20,
    "auto_cleanup_days": 30
  },
  "wake_word": {
    "enabled": true,
    "engine": "simple",
    "wake_words": ["ghost", "hey ghost"],
    "sensitivity": 0.5
  }
}
```

### Memory Database Structure

The brain system creates these tables:
- **interactions**: Conversation history
- **preferences**: User settings and preferences
- **reminders**: Tasks and reminders
- **context_storage**: Temporary contextual data
- **user_profile**: User information

## 🎮 Usage Examples

### **Basic Interactions**

```bash
# Wake word activation
User: "Ghost"
G.H.O.S.T.: "Yes? How can I help?"
User: "Open Spotify"
G.H.O.S.T.: "Done! Opening Spotify for you now."

# Conversational mode
User: "Ghost"
G.H.O.S.T.: "I'm listening."
User: "How are you today?"
G.H.O.S.T.: "I'm doing great! Ready to help you with whatever you need. What can I do for you?"

# Memory and preferences
User: "Ghost"
G.H.O.S.T.: "What can I do for you?"
User: "Remember that I like jazz music"
G.H.O.S.T.: "Got it! I'll remember that you like jazz music."
```

### **Advanced Features**

```bash
# Context-aware responses
User: "Ghost, search for weather in London"
G.H.O.S.T.: "Here's the weather information for London! [Shows results]"
User: "What about Paris?"
G.H.O.S.T.: "Let me check the weather in Paris for you. [Shows Paris weather]"

# Reminders and tasks
User: "Ghost, remind me to call mom tomorrow"
G.H.O.S.T.: "I've added a reminder to call mom tomorrow. I'll let you know!"

# System commands
User: "Ghost, what time is it?"
G.H.O.S.T.: "The current time is 3:45 PM."
```

## 🔌 Extending the Brain System

### Adding New Actions

1. **Create Action Handler** (`actions/my_action.py`):
```python
from .base_action import BaseAction

class MyAction(BaseAction):
    def execute(self, parameters):
        # Your action logic
        return {'success': True, 'message': 'Action completed'}
    
    def get_description(self):
        return "Description of my action"
```

2. **Register with Brain** (`core/brain.py`):
```python
# Add to intent_patterns
'my_action': [
    {'pattern': r'do something with (.+)', 'confidence': 0.9}
]
```

3. **Register with Dispatcher** (`actions/action_dispatcher.py`):
```python
self.register_handler('my_action', MyAction(config))
```

### Adding Memory Fields

```python
# Store custom data
memory.store_context('user_mood', 'happy', expires_in_hours=24)

# Retrieve custom data
mood = memory.get_context('user_mood', 'neutral')

# Add preferences
memory.set_preference('favorite_color', 'blue', 'personal')
```

### Customizing Conversations

Edit the `_analyze_conversation_intent` method in `core/brain.py`:

```python
def _analyze_conversation_intent(self, user_input: str, user_name: str, context: List) -> str:
    # Add your custom conversation logic
    if 'my custom trigger' in user_input.lower():
        return "Custom response for my trigger"
    
    # ... existing logic
```

## 🔄 Reasoning Modes

### **Offline Mode**
- Uses local models only
- No internet required
- Faster response times
- Limited reasoning capabilities

### **Online Mode**
- Uses cloud-based models (GPT-4, Claude, etc.)
- Requires internet connection
- Advanced reasoning capabilities
- Higher latency

### **Hybrid Mode** (Default)
- Tries online first, falls back to offline
- Best of both worlds
- Automatic failover

```python
# Change reasoning mode programmatically
brain.set_reasoning_mode(ReasoningMode.OFFLINE)
```

## 📊 Monitoring and Debugging

### System Status

```python
# Get comprehensive status
status = orchestrator.get_system_status()
print(status)

# Get brain-specific status
brain_status = brain.get_brain_status()
print(brain_status)

# Get memory statistics
memory_stats = memory.get_memory_stats()
print(memory_stats)
```

### Logging

The brain system creates specialized logs:
- `data/logs/brain.log` - Brain reasoning and decisions
- `data/logs/memory.log` - Memory operations
- `data/logs/ghost.log` - General system logs

### Debug Mode

```bash
# Run with detailed logging
python main.py --debug --brain-mode
```

## 🛠️ Troubleshooting

### Common Issues

**Brain not responding:**
- Check if brain mode is enabled in config
- Verify memory database permissions
- Check logs for initialization errors

**Wake word not working:**
- Ensure microphone permissions
- Try different wake word engines
- Adjust sensitivity settings

**Memory issues:**
- Check SQLite database file permissions
- Verify disk space for database growth
- Clear old data if needed

### Memory Management

```python
# Clear session data
memory.clear_session_data()

# Backup memory
memory.backup_memory('backup_path.db')

# Get memory statistics
stats = memory.get_memory_stats()
```

## 🔮 Future Enhancements

The brain system is designed for easy extension:

### **Planned Features**
- **LLM Integration**: GPT-4, Claude, local models
- **Advanced Memory**: Vector embeddings, semantic search
- **Multi-modal Input**: Image, document processing
- **Proactive Assistance**: Scheduled tasks, notifications
- **Learning System**: Adaptive behavior based on usage
- **Plugin Architecture**: Third-party brain extensions

### **Integration Points**
- **Model Providers**: Easy switching between AI models
- **Memory Backends**: Support for different storage systems
- **Action Plugins**: Modular action system
- **UI Interfaces**: Web, mobile, desktop integration

## 📝 API Reference

### Brain Class Methods

```python
# Process user input
response = brain.process_input("user input", context={})

# Get brain status
status = brain.get_brain_status()

# Change reasoning mode
brain.set_reasoning_mode(ReasoningMode.ONLINE)

# Clear context
brain.clear_context()
```

### Memory Class Methods

```python
# Interactions
interaction_id = memory.add_interaction("content", "user", metadata={})
recent = memory.get_recent_context(count=10)

# Preferences
memory.set_preference("key", "value", "category")
value = memory.get_preference("key", default="default")

# Reminders
reminder_id = memory.add_reminder("title", "description", due_date="2024-01-01")
reminders = memory.get_reminders(completed=False)

# Context storage
memory.store_context("key", "value", expires_in_hours=24)
value = memory.get_context("key", default="default")
```

---

**G.H.O.S.T. Brain System** - Transforming virtual assistance through intelligent reasoning and memory.
