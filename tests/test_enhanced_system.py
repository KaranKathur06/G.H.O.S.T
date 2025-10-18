"""
Comprehensive unit tests for G.H.O.S.T. Enhanced system.

Tests all major components including:
- LLM Brain with structured responses
- Action Dispatcher
- System Indexer
- Enhanced TTS
- Speech Recognition
- Wake Word Detection
"""

import pytest
import asyncio
import json
import tempfile
import os
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path

# Import components to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.llm_brain import LLMBrain, LLMResponse
from core.action_dispatcher import ActionDispatcher, ActionResult
from core.system_indexer import SystemIndexer, IndexedItem, SearchResult
from speech.enhanced_tts import EnhancedTTS
from speech.speech_to_text import SpeechToText
from speech.wake_word_listener import WakeWordListener, WakeWordDetection

class TestLLMBrain:
    """Test LLM Brain with structured JSON responses."""
    
    @pytest.fixture
    def llm_brain(self):
        """Create LLM brain instance for testing."""
        config = {
            'use_openai': False,  # Don't use real API in tests
            'use_ollama': False,
            'use_local': False,
            'use_structured_responses': True,
            'immediate_ack': True
        }
        return LLMBrain(config)
    
    def test_initialization(self, llm_brain):
        """Test LLM brain initialization."""
        assert llm_brain is not None
        assert llm_brain.use_structured_responses is True
        assert llm_brain.immediate_ack is True
        assert llm_brain.personality_prompt is not None
    
    def test_parse_structured_response_valid_json(self, llm_brain):
        """Test parsing valid JSON response."""
        json_response = json.dumps({
            "reply_text": "Certainly, Sir. I'll open that application for you.",
            "action": {
                "type": "open_application",
                "parameters": {"app_name": "calculator"}
            }
        })
        
        parsed = llm_brain._parse_structured_response(json_response)
        
        assert parsed['reply_text'] == "Certainly, Sir. I'll open that application for you."
        assert parsed['action']['type'] == "open_application"
        assert parsed['action']['parameters']['app_name'] == "calculator"
    
    def test_parse_structured_response_invalid_json(self, llm_brain):
        """Test parsing invalid JSON response."""
        invalid_json = "This is not valid JSON"
        
        parsed = llm_brain._parse_structured_response(invalid_json)
        
        assert parsed['reply_text'] == invalid_json
        assert parsed['action'] is None
    
    def test_parse_structured_response_missing_fields(self, llm_brain):
        """Test parsing JSON with missing required fields."""
        json_response = json.dumps({
            "action": {"type": "test_action"}
        })
        
        parsed = llm_brain._parse_structured_response(json_response)
        
        assert parsed['reply_text'] == "I understand your request, Sir."
        assert parsed['action']['parameters'] == {}
    
    @pytest.mark.asyncio
    async def test_reason_fallback(self, llm_brain):
        """Test reasoning with fallback responses."""
        response = await llm_brain.reason("What time is it?")
        
        assert isinstance(response, LLMResponse)
        assert response.content is not None
        assert response.model_used == "fallback"
        assert response.requires_action is True  # Time request should trigger action
    
    def test_get_immediate_ack(self, llm_brain):
        """Test immediate acknowledgment messages."""
        ack = llm_brain.get_immediate_ack()
        
        assert isinstance(ack, str)
        assert "Sir" in ack
        assert len(ack) > 0

class TestActionDispatcher:
    """Test Action Dispatcher functionality."""
    
    @pytest.fixture
    def action_dispatcher(self):
        """Create action dispatcher for testing."""
        config = {
            'require_confirmation': False,  # Disable for testing
            'dangerous_actions': ['system_command'],
            'action_timeout': 5.0
        }
        return ActionDispatcher(config)
    
    def test_initialization(self, action_dispatcher):
        """Test action dispatcher initialization."""
        assert action_dispatcher is not None
        assert action_dispatcher.builtin_handlers is not None
        assert len(action_dispatcher.builtin_handlers) > 0
    
    @pytest.mark.asyncio
    async def test_execute_open_application(self, action_dispatcher):
        """Test opening application action."""
        action_data = {
            "type": "open_application",
            "parameters": {"app_name": "calculator"}
        }
        
        with patch('subprocess.Popen') as mock_popen:
            result = await action_dispatcher.execute_action(action_data)
            
            assert isinstance(result, ActionResult)
            # Should attempt to open calculator (common app)
            mock_popen.assert_called()
    
    @pytest.mark.asyncio
    async def test_execute_search_web(self, action_dispatcher):
        """Test web search action."""
        action_data = {
            "type": "search_web",
            "parameters": {"query": "Python tutorials"}
        }
        
        with patch('webbrowser.open') as mock_browser:
            result = await action_dispatcher.execute_action(action_data)
            
            assert result.success is True
            assert "Python tutorials" in result.message
            mock_browser.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_get_time(self, action_dispatcher):
        """Test get time action."""
        action_data = {
            "type": "get_time",
            "parameters": {}
        }
        
        result = await action_dispatcher.execute_action(action_data)
        
        assert result.success is True
        assert "time" in result.message.lower()
        assert result.data is not None
        assert 'time' in result.data
        assert 'date' in result.data
    
    @pytest.mark.asyncio
    async def test_execute_tell_joke(self, action_dispatcher):
        """Test joke telling action."""
        action_data = {
            "type": "tell_joke",
            "parameters": {"topic": "programming"}
        }
        
        result = await action_dispatcher.execute_action(action_data)
        
        assert result.success is True
        assert len(result.message) > 0
        assert "Sir" in result.message
    
    @pytest.mark.asyncio
    async def test_execute_invalid_action(self, action_dispatcher):
        """Test handling invalid action."""
        action_data = {
            "type": "nonexistent_action",
            "parameters": {}
        }
        
        result = await action_dispatcher.execute_action(action_data)
        
        assert result.success is False
        assert "not found" in result.message.lower() or "failed" in result.message.lower()
    
    def test_get_available_actions(self, action_dispatcher):
        """Test getting available actions."""
        actions = action_dispatcher.get_available_actions()
        
        assert isinstance(actions, list)
        assert len(actions) > 0
        assert "open_application" in actions
        assert "search_web" in actions
        assert "get_time" in actions

class TestSystemIndexer:
    """Test System Indexer functionality."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create some test files
            test_files = [
                "test_document.txt",
                "python_script.py",
                "image_file.jpg",
                "data_file.csv"
            ]
            
            for filename in test_files:
                file_path = Path(temp_dir) / filename
                file_path.write_text(f"Test content for {filename}")
            
            yield temp_dir
    
    @pytest.fixture
    def system_indexer(self, temp_dir):
        """Create system indexer for testing."""
        config = {
            'db_path': os.path.join(temp_dir, 'test_index.db'),
            'index_paths': [temp_dir],
            'auto_start': False,  # Don't auto-start for tests
            'max_workers': 1,
            'batch_size': 10
        }
        return SystemIndexer(config)
    
    def test_initialization(self, system_indexer):
        """Test system indexer initialization."""
        assert system_indexer is not None
        assert system_indexer.db_connection is not None
    
    def test_create_indexed_item(self, system_indexer, temp_dir):
        """Test creating indexed item from file."""
        test_file = Path(temp_dir) / "test_document.txt"
        
        item = system_indexer._create_indexed_item(str(test_file), "file")
        
        assert isinstance(item, IndexedItem)
        assert item.name == "test_document.txt"
        assert item.type == "file"
        assert item.path == str(test_file)
        assert "txt" in item.search_terms
    
    def test_index_directory(self, system_indexer, temp_dir):
        """Test indexing a directory."""
        items_count = system_indexer._index_directory(temp_dir)
        
        assert items_count > 0
        
        # Verify items were saved to database
        cursor = system_indexer.db_connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM indexed_items")
        db_count = cursor.fetchone()[0]
        
        assert db_count > 0
    
    def test_search_functionality(self, system_indexer, temp_dir):
        """Test search functionality."""
        # First index the directory
        system_indexer._index_directory(temp_dir)
        system_indexer._rebuild_search_index()
        
        # Search for Python file
        results = system_indexer.search("python", limit=5)
        
        assert isinstance(results, list)
        if results:  # If any results found
            assert isinstance(results[0], SearchResult)
            assert results[0].item.name is not None
    
    def test_get_statistics(self, system_indexer, temp_dir):
        """Test getting indexer statistics."""
        # Index some files first
        system_indexer._index_directory(temp_dir)
        
        stats = system_indexer.get_statistics()
        
        assert isinstance(stats, dict)
        assert 'total_items' in stats
        assert 'by_type' in stats
        assert stats['total_items'] >= 0

class TestEnhancedTTS:
    """Test Enhanced TTS functionality."""
    
    @pytest.fixture
    def enhanced_tts(self):
        """Create enhanced TTS for testing."""
        config = {
            'primary_engine': 'pyttsx3',  # Use pyttsx3 for testing
            'edge_voice': 'en-US-AriaNeural',
            'rate': 180,
            'volume': 0.9
        }
        return EnhancedTTS(config)
    
    def test_initialization(self, enhanced_tts):
        """Test TTS initialization."""
        assert enhanced_tts is not None
        assert enhanced_tts.pronunciation_rules is not None
        assert enhanced_tts.current_engine is not None
    
    def test_pronunciation_rules(self, enhanced_tts):
        """Test G.H.O.S.T. pronunciation rules."""
        test_text = "Hello, I am G.H.O.S.T., your AI assistant."
        processed = enhanced_tts._apply_pronunciation_rules(test_text)
        
        # Should replace G.H.O.S.T. with Ghost
        assert "Ghost" in processed
        assert "G.H.O.S.T." not in processed
    
    def test_prosody_markup(self, enhanced_tts):
        """Test prosody markup addition."""
        from speech.enhanced_tts import SpeechSettings
        
        settings = SpeechSettings(add_pauses=True, emotion="friendly")
        test_text = "Hello, Sir. How are you today?"
        
        processed = enhanced_tts._add_prosody_markup(test_text, settings)
        
        # Should add break tags after punctuation
        assert "<break" in processed or "prosody" in processed
    
    def test_get_engine_status(self, enhanced_tts):
        """Test getting engine status."""
        status = enhanced_tts.get_engine_status()
        
        assert isinstance(status, dict)
        assert 'current_engine' in status
        assert 'pyttsx3_available' in status

class TestSpeechToText:
    """Test Speech-to-Text functionality."""
    
    @pytest.fixture
    def speech_to_text(self):
        """Create STT system for testing."""
        config = {
            'use_speech_recognition': True,
            'use_vosk': False,  # Don't require VOSK for tests
            'energy_threshold': 200,
            'pause_threshold': 0.5
        }
        return SpeechToText(config)
    
    def test_initialization(self, speech_to_text):
        """Test STT initialization."""
        assert speech_to_text is not None
        assert speech_to_text.config is not None
    
    def test_wake_word_detection(self, speech_to_text):
        """Test wake word detection logic."""
        # Test various wake word formats
        test_phrases = [
            "ghost",
            "hey ghost",
            "Ghost, what time is it?",
            "Hello ghost"
        ]
        
        for phrase in test_phrases:
            result = speech_to_text._contains_wake_word(phrase)
            assert result is True, f"Failed to detect wake word in: {phrase}"
    
    def test_silence_detection(self, speech_to_text):
        """Test silence detection."""
        # Create mock audio data (silence = low amplitude)
        silence_data = b'\x00\x01' * 1024  # Low amplitude audio
        loud_data = b'\xff\xfe' * 1024     # High amplitude audio
        
        assert speech_to_text._is_silent(silence_data) is True
        assert speech_to_text._is_silent(loud_data) is False

class TestWakeWordListener:
    """Test Wake Word Listener functionality."""
    
    @pytest.fixture
    def wake_word_listener(self):
        """Create wake word listener for testing."""
        config = {
            'engine': 'simple_energy',
            'wake_words': ['ghost'],
            'confidence_threshold': 0.6,
            'energy_threshold': 300,
            'sample_rate': 16000,
            'chunk_size': 1024
        }
        return WakeWordListener(config)
    
    def test_initialization(self, wake_word_listener):
        """Test wake word listener initialization."""
        assert wake_word_listener is not None
        assert wake_word_listener.wake_words == ['ghost']
        assert wake_word_listener.detection_engine is not None
    
    def test_phonetic_patterns(self, wake_word_listener):
        """Test phonetic pattern generation."""
        patterns = wake_word_listener._generate_phonetic_patterns("ghost")
        
        assert isinstance(patterns, list)
        assert "ghost" in patterns
        assert len(patterns) > 1  # Should include variations
    
    def test_energy_calculation(self, wake_word_listener):
        """Test audio energy calculation."""
        # Create mock audio data
        test_data = b'\x00\x01' * 1024  # Low energy
        energy = wake_word_listener._calculate_energy(test_data)
        
        assert isinstance(energy, float)
        assert energy >= 0
    
    def test_detection_stats(self, wake_word_listener):
        """Test getting detection statistics."""
        stats = wake_word_listener.get_detection_stats()
        
        assert isinstance(stats, dict)
        assert 'engine_type' in stats
        assert 'is_listening' in stats
        assert 'detections_count' in stats

class TestIntegration:
    """Integration tests for the complete system."""
    
    @pytest.mark.asyncio
    async def test_llm_to_action_pipeline(self):
        """Test complete pipeline from LLM to action execution."""
        # Create components
        llm_brain = LLMBrain({'use_openai': False, 'use_ollama': False, 'use_local': False})
        action_dispatcher = ActionDispatcher({'require_confirmation': False})
        
        # Test time request
        llm_response = await llm_brain.reason("What time is it?")
        
        if llm_response.requires_action and llm_response.suggested_actions:
            action = llm_response.suggested_actions[0]
            action_result = await action_dispatcher.execute_action(action)
            
            assert action_result.success is True
            assert "time" in action_result.message.lower()
    
    @pytest.mark.asyncio
    async def test_joke_request_pipeline(self):
        """Test joke request pipeline."""
        llm_brain = LLMBrain({'use_openai': False, 'use_ollama': False, 'use_local': False})
        action_dispatcher = ActionDispatcher({'require_confirmation': False})
        
        # Test joke request
        llm_response = await llm_brain.reason("Tell me a joke")
        
        if llm_response.requires_action and llm_response.suggested_actions:
            action = llm_response.suggested_actions[0]
            action_result = await action_dispatcher.execute_action(action)
            
            assert action_result.success is True
            assert len(action_result.message) > 0

# Test fixtures and utilities
@pytest.fixture
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
