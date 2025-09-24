"""
Unit tests for actions module components.

Tests all action handlers including app launcher, web search, system control, etc.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from actions.app_launcher import AppLauncher
from actions.web_search import WebSearch
from actions.system_control import SystemControl
from actions.weather import Weather
from actions.entertainment import Entertainment
from actions.action_dispatcher import ActionDispatcher


class TestAppLauncher(unittest.TestCase):
    """Test cases for the AppLauncher class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'paths': {
                'test_app': 'C:\\test\\app.exe'
            }
        }
        self.app_launcher = AppLauncher(self.config)
    
    def test_find_app_path(self):
        """Test finding application paths."""
        # Test direct match
        path = self.app_launcher._find_app_path('notepad')
        self.assertIsNotNone(path)
        
        # Test unknown app
        path = self.app_launcher._find_app_path('unknown_app')
        self.assertIsNone(path)
    
    @patch('subprocess.Popen')
    def test_launch_app_success(self, mock_popen):
        """Test successful app launching."""
        mock_popen.return_value = Mock()
        
        result = self.app_launcher._launch_app('notepad.exe', 'notepad')
        self.assertTrue(result)
        mock_popen.assert_called_once()
    
    @patch('subprocess.Popen')
    def test_launch_app_failure(self, mock_popen):
        """Test app launching failure."""
        mock_popen.side_effect = Exception("Launch failed")
        
        result = self.app_launcher._launch_app('invalid.exe', 'invalid')
        self.assertFalse(result)
    
    def test_execute_missing_app_name(self):
        """Test execution with missing app name."""
        result = self.app_launcher.execute({})
        self.assertFalse(result['success'])
        self.assertIn('specify an application name', result['message'])
    
    def test_validate_parameters(self):
        """Test parameter validation."""
        # Valid parameters
        self.assertTrue(self.app_launcher.validate_parameters({'app_name': 'chrome'}))
        
        # Invalid parameters
        self.assertFalse(self.app_launcher.validate_parameters({}))
        self.assertFalse(self.app_launcher.validate_parameters({'app_name': ''}))


class TestWebSearch(unittest.TestCase):
    """Test cases for the WebSearch class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'default_engine': 'google',
            'custom_engines': {}
        }
        self.web_search = WebSearch(self.config)
    
    def test_build_search_url(self):
        """Test search URL building."""
        url = self.web_search._build_search_url('python tutorials', 'google')
        self.assertIn('google.com', url)
        self.assertIn('python+tutorials', url)
    
    @patch('webbrowser.open')
    def test_open_search_success(self, mock_open):
        """Test successful search opening."""
        mock_open.return_value = True
        
        result = self.web_search._open_search('https://google.com/search?q=test')
        self.assertTrue(result)
        mock_open.assert_called_once()
    
    @patch('webbrowser.open')
    def test_open_search_failure(self, mock_open):
        """Test search opening failure."""
        mock_open.side_effect = Exception("Browser error")
        
        result = self.web_search._open_search('https://google.com/search?q=test')
        self.assertFalse(result)
    
    def test_execute_missing_query(self):
        """Test execution with missing query."""
        result = self.web_search.execute({})
        self.assertFalse(result['success'])
        self.assertIn('provide a search query', result['message'])
    
    def test_validate_parameters(self):
        """Test parameter validation."""
        # Valid parameters
        self.assertTrue(self.web_search.validate_parameters({'query': 'test search'}))
        
        # Invalid parameters
        self.assertFalse(self.web_search.validate_parameters({}))
        self.assertFalse(self.web_search.validate_parameters({'query': ''}))


class TestSystemControl(unittest.TestCase):
    """Test cases for the SystemControl class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'confirm_dangerous': True,
            'allowed_operations': ['time', 'date', 'shutdown', 'restart']
        }
        self.system_control = SystemControl(self.config)
    
    def test_handle_time_date(self):
        """Test time and date handling."""
        # Test time query
        result = self.system_control._handle_time_date('time')
        self.assertTrue(result['success'])
        self.assertIn('current time', result['message'])
        
        # Test date query
        result = self.system_control._handle_time_date('date')
        self.assertTrue(result['success'])
        self.assertIn('Today is', result['message'])
    
    def test_dangerous_operations_blocked(self):
        """Test that dangerous operations are blocked when confirmation is required."""
        result = self.system_control._handle_shutdown()
        self.assertFalse(result['success'])
        self.assertTrue(result['requires_confirmation'])
    
    def test_validate_parameters(self):
        """Test parameter validation."""
        # System control accepts various parameter combinations
        self.assertTrue(self.system_control.validate_parameters({'operation': 'time'}))
        self.assertTrue(self.system_control.validate_parameters({'query': 'what time is it'}))
        self.assertTrue(self.system_control.validate_parameters({}))


class TestWeather(unittest.TestCase):
    """Test cases for the Weather class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'api_key': '',  # No API key for testing
            'default_location': 'New York',
            'provider': 'openweathermap',
            'units': 'metric'
        }
        self.weather = Weather(self.config)
    
    def test_format_weather_message(self):
        """Test weather message formatting."""
        weather_data = {
            'location': 'London',
            'temperature': 20,
            'description': 'sunny',
            'humidity': 65,
            'units': 'metric',
            'feels_like': 22,
            'wind_speed': 5
        }
        
        message = self.weather._format_weather_message(weather_data)
        self.assertIn('London', message)
        self.assertIn('20°C', message)
        self.assertIn('sunny', message)
        self.assertIn('65%', message)
    
    def test_fallback_weather_data(self):
        """Test fallback weather data when no API key is available."""
        result = self.weather._get_weather_fallback('Test City')
        self.assertIsNotNone(result)
        self.assertEqual(result['location'], 'Test City')
        self.assertIn('note', result)  # Should have placeholder note
    
    def test_validate_parameters(self):
        """Test parameter validation."""
        # Weather accepts any parameters (location is optional)
        self.assertTrue(self.weather.validate_parameters({}))
        self.assertTrue(self.weather.validate_parameters({'location': 'London'}))


class TestEntertainment(unittest.TestCase):
    """Test cases for the Entertainment class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {'default_type': 'joke'}
        self.entertainment = Entertainment(self.config)
    
    def test_get_joke(self):
        """Test joke retrieval."""
        joke = self.entertainment._get_joke()
        self.assertIsInstance(joke, str)
        self.assertTrue(len(joke) > 0)
    
    def test_get_fun_fact(self):
        """Test fun fact retrieval."""
        fact = self.entertainment._get_fun_fact()
        self.assertIsInstance(fact, str)
        self.assertTrue(len(fact) > 0)
    
    def test_get_quote(self):
        """Test quote retrieval."""
        quote = self.entertainment._get_quote()
        self.assertIsInstance(quote, str)
        self.assertTrue(len(quote) > 0)
    
    def test_execute_different_types(self):
        """Test execution with different content types."""
        # Test joke
        result = self.entertainment.execute({'type': 'joke'})
        self.assertTrue(result['success'])
        self.assertEqual(result['type'], 'joke')
        
        # Test fact
        result = self.entertainment.execute({'type': 'fact'})
        self.assertTrue(result['success'])
        self.assertEqual(result['type'], 'fact')
        
        # Test quote
        result = self.entertainment.execute({'type': 'quote'})
        self.assertTrue(result['success'])
        self.assertEqual(result['type'], 'quote')
    
    def test_validate_parameters(self):
        """Test parameter validation."""
        # Entertainment accepts any parameters
        self.assertTrue(self.entertainment.validate_parameters({}))
        self.assertTrue(self.entertainment.validate_parameters({'type': 'joke'}))


class TestActionDispatcher(unittest.TestCase):
    """Test cases for the ActionDispatcher class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'apps': {},
            'web': {},
            'system': {},
            'weather': {},
            'entertainment': {}
        }
        self.dispatcher = ActionDispatcher(self.config)
    
    def test_register_handler(self):
        """Test handler registration."""
        mock_handler = Mock()
        self.dispatcher.register_handler('test_action', mock_handler)
        
        self.assertIn('test_action', self.dispatcher.action_handlers)
        self.assertEqual(self.dispatcher.action_handlers['test_action'], mock_handler)
    
    def test_unregister_handler(self):
        """Test handler unregistration."""
        mock_handler = Mock()
        self.dispatcher.register_handler('test_action', mock_handler)
        self.dispatcher.unregister_handler('test_action')
        
        self.assertNotIn('test_action', self.dispatcher.action_handlers)
    
    def test_execute_unknown_action(self):
        """Test execution of unknown action."""
        mock_intent = Mock()
        mock_intent.action = 'unknown_action'
        
        result = self.dispatcher.execute(mock_intent)
        self.assertFalse(result['success'])
        self.assertIn('unknown_action', result['response'])
    
    def test_get_available_actions(self):
        """Test getting available actions."""
        actions = self.dispatcher.get_available_actions()
        self.assertIsInstance(actions, dict)
        self.assertGreater(len(actions), 0)  # Should have default handlers


if __name__ == '__main__':
    unittest.main()
