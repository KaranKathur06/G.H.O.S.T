"""
Unit tests for core module components.

Tests the orchestrator, reasoning engine, and memory manager functionality.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.reasoning_engine import ReasoningEngine, Intent
from core.memory_manager import MemoryManager, Interaction, UserPreference
from core.orchestrator import Orchestrator


class TestReasoningEngine(unittest.TestCase):
    """Test cases for the ReasoningEngine class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {'test': True}
        self.memory_manager = Mock(spec=MemoryManager)
        self.reasoning_engine = ReasoningEngine(self.config, self.memory_manager)
    
    def test_analyze_simple_command(self):
        """Test analysis of simple commands."""
        # Test open application command
        intent = self.reasoning_engine.analyze_command("open chrome")
        self.assertIsNotNone(intent)
        self.assertEqual(intent.action, 'open_application')
        self.assertEqual(intent.parameters.get('app_name'), 'chrome')
    
    def test_analyze_search_command(self):
        """Test analysis of search commands."""
        intent = self.reasoning_engine.analyze_command("search for python tutorials")
        self.assertIsNotNone(intent)
        self.assertEqual(intent.action, 'web_search')
        self.assertEqual(intent.parameters.get('query'), 'python tutorials')
    
    def test_analyze_weather_command(self):
        """Test analysis of weather commands."""
        intent = self.reasoning_engine.analyze_command("what's the weather in London")
        self.assertIsNotNone(intent)
        self.assertEqual(intent.action, 'weather')
        self.assertEqual(intent.parameters.get('location'), 'London')
    
    def test_analyze_empty_command(self):
        """Test analysis of empty or invalid commands."""
        intent = self.reasoning_engine.analyze_command("")
        self.assertIsNone(intent)
        
        intent = self.reasoning_engine.analyze_command("   ")
        self.assertIsNone(intent)
    
    def test_get_suggestions(self):
        """Test command suggestions functionality."""
        suggestions = self.reasoning_engine.get_suggestions("open")
        self.assertIsInstance(suggestions, list)
        self.assertTrue(len(suggestions) <= 5)


class TestMemoryManager(unittest.TestCase):
    """Test cases for the MemoryManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'data_dir': 'test_data/memory',
            'max_conversation_history': 100
        }
        self.memory_manager = MemoryManager(self.config)
    
    def test_add_interaction(self):
        """Test adding interactions to memory."""
        initial_count = len(self.memory_manager.current_session)
        
        self.memory_manager.add_interaction("Hello", "user")
        self.assertEqual(len(self.memory_manager.current_session), initial_count + 1)
        
        latest_interaction = self.memory_manager.current_session[-1]
        self.assertEqual(latest_interaction.content, "Hello")
        self.assertEqual(latest_interaction.type, "user")
    
    def test_get_recent_context(self):
        """Test retrieving recent conversation context."""
        # Add some interactions
        for i in range(5):
            self.memory_manager.add_interaction(f"Message {i}", "user")
        
        recent = self.memory_manager.get_recent_context(3)
        self.assertEqual(len(recent), 3)
        self.assertEqual(recent[-1].content, "Message 4")
    
    def test_preferences(self):
        """Test user preference management."""
        # Set a preference
        self.memory_manager.set_preference("theme", "dark", "ui")
        
        # Retrieve the preference
        theme = self.memory_manager.get_preference("theme")
        self.assertEqual(theme, "dark")
        
        # Test default value
        unknown = self.memory_manager.get_preference("unknown", "default")
        self.assertEqual(unknown, "default")
    
    def test_context_storage(self):
        """Test contextual information storage."""
        self.memory_manager.store_context("last_search", "python tutorials")
        
        context = self.memory_manager.get_context("last_search")
        self.assertEqual(context, "python tutorials")
        
        # Test default value
        unknown_context = self.memory_manager.get_context("unknown", "default")
        self.assertEqual(unknown_context, "default")


class TestOrchestrator(unittest.TestCase):
    """Test cases for the Orchestrator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'speech': {'enabled': False},  # Disable speech for testing
            'actions': {'enabled': True},
            'memory': {'data_dir': 'test_data/memory'},
            'reasoning': {'test_mode': True}
        }
        self.orchestrator = Orchestrator(self.config)
    
    @patch('core.orchestrator.SpeechManager')
    @patch('core.orchestrator.ActionDispatcher')
    def test_initialization(self, mock_dispatcher, mock_speech):
        """Test orchestrator initialization."""
        # Mock the components
        mock_speech.return_value = Mock()
        mock_dispatcher.return_value = Mock()
        
        # Test initialization
        result = self.orchestrator.initialize()
        self.assertTrue(result)
        self.assertIsNotNone(self.orchestrator.memory_manager)
        self.assertIsNotNone(self.orchestrator.reasoning_engine)
    
    def test_process_command(self):
        """Test command processing flow."""
        # Mock the required components
        self.orchestrator.reasoning_engine = Mock()
        self.orchestrator.action_dispatcher = Mock()
        self.orchestrator.speech_manager = Mock()
        
        # Set up mock returns
        mock_intent = Mock()
        mock_intent.action = 'test_action'
        self.orchestrator.reasoning_engine.analyze_command.return_value = mock_intent
        
        mock_result = {'success': True, 'response': 'Test completed'}
        self.orchestrator.action_dispatcher.execute.return_value = mock_result
        
        # Test command processing
        self.orchestrator._process_command("test command")
        
        # Verify calls were made
        self.orchestrator.reasoning_engine.analyze_command.assert_called_once_with("test command")
        self.orchestrator.action_dispatcher.execute.assert_called_once_with(mock_intent)
        self.orchestrator.speech_manager.speak.assert_called_once_with('Test completed')


if __name__ == '__main__':
    # Create test data directory
    os.makedirs('test_data/memory', exist_ok=True)
    
    # Run tests
    unittest.main()
