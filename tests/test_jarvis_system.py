"""
Comprehensive test suite for G.H.O.S.T. J.A.R.V.I.S.-like system.

This module tests all advanced features including personality, voice recognition,
enhanced TTS, proactive intelligence, and advanced actions.
"""

import sys
import os
import time
import unittest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.enhanced_personality import EnhancedPersonality, PersonalityMode, EmotionalTone
from speech.speaker_identification import SpeakerIdentifier, SpeakerIdentificationResult
from speech.enhanced_tts import EnhancedTTS, VoiceEngine
from core.proactive_intelligence import ProactiveIntelligence, ProactiveEventType
from actions.advanced_actions import AdvancedActionDispatcher, ActionResult


class TestEnhancedPersonality(unittest.TestCase):
    """Test suite for enhanced personality system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'mode': 'jarvis',
            'owner_name': 'Karan',
            'owner_title': 'Sir',
            'assistant_name': 'G.H.O.S.T.'
        }
        self.personality = EnhancedPersonality(self.config)
    
    def test_personality_initialization(self):
        """Test personality system initialization."""
        self.assertEqual(self.personality.mode, PersonalityMode.JARVIS)
        self.assertEqual(self.personality.owner_name, 'Karan')
        self.assertEqual(self.personality.owner_title, 'Sir')
        self.assertIsNotNone(self.personality.voice_settings)
        self.assertIsNotNone(self.personality.response_templates)
    
    def test_owner_greeting(self):
        """Test greeting for recognized owner."""
        greeting, voice_settings = self.personality.get_greeting(is_owner=True, is_first_time=True)
        
        self.assertIn('Sir', greeting)
        self.assertIn('G.H.O.S.T.', greeting)
        self.assertIsNotNone(voice_settings)
        
        # Test return greeting
        return_greeting, _ = self.personality.get_greeting(is_owner=True, is_first_time=False)
        self.assertIn('Sir', return_greeting)
    
    def test_unknown_user_greeting(self):
        """Test greeting for unknown user."""
        greeting, voice_settings = self.personality.get_greeting(is_owner=False)
        
        # Should not contain owner-specific terms
        self.assertNotIn('Sir', greeting)
        self.assertIn('G.H.O.S.T.', greeting)
        self.assertIsNotNone(voice_settings)
    
    def test_wake_word_response(self):
        """Test wake word response generation."""
        # Owner response
        response, voice_settings = self.personality.get_wake_word_response(is_owner=True)
        self.assertIn('Sir', response)
        
        # Unknown user response
        response, voice_settings = self.personality.get_wake_word_response(is_owner=False)
        self.assertNotIn('Sir', response)
    
    def test_confirmation_messages(self):
        """Test confirmation message generation."""
        confirmation, voice_settings = self.personality.get_confirmation(
            task_description="opening Chrome", 
            is_owner=True
        )
        
        self.assertIn('Sir', confirmation)
        self.assertIsNotNone(voice_settings)
    
    def test_error_responses(self):
        """Test error response generation."""
        error_response, voice_settings = self.personality.get_error_response(
            error_type="network", 
            is_owner=True
        )
        
        self.assertIn('Sir', error_response)
        self.assertIn('connectivity', error_response.lower())
        self.assertEqual(voice_settings.rate, 160)  # Apologetic tone
    
    def test_personality_mode_switching(self):
        """Test switching between personality modes."""
        # Switch to companion mode
        self.personality.update_context(mode='companion')
        self.assertEqual(self.personality.mode, PersonalityMode.COMPANION)
        
        # Test companion mode greeting
        greeting, _ = self.personality.get_greeting(is_owner=True)
        self.assertIn('Karan', greeting)  # Uses name instead of title
    
    def test_proactive_messages(self):
        """Test proactive message generation."""
        morning_briefing = self.personality.get_proactive_message('morning_briefing', is_owner=True)
        self.assertIsNotNone(morning_briefing)
        
        message, voice_settings = morning_briefing
        self.assertIn('Sir', message)
        self.assertIn('briefing', message.lower())
    
    def test_response_enhancement(self):
        """Test response enhancement with personality."""
        base_response = "Task completed successfully."
        enhanced, voice_settings = self.personality.enhance_response(
            base_response, 
            context={'action_taken': True}, 
            is_owner=True
        )
        
        # Should contain personality flourishes
        self.assertIn('Sir', enhanced)
        self.assertIsNotNone(voice_settings)


class TestSpeakerIdentification(unittest.TestCase):
    """Test suite for speaker identification system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'owner_name': 'Karan',
            'owner_title': 'Sir',
            'confidence_threshold': 0.75,
            'profile_path': tempfile.mktemp(suffix='.json')
        }
    
    @patch('speech.speaker_identification.SPEAKER_ID_AVAILABLE', True)
    @patch('speech.speaker_identification.librosa')
    @patch('speech.speaker_identification.sklearn')
    def test_speaker_identification_available(self, mock_sklearn, mock_librosa):
        """Test speaker identification when libraries are available."""
        speaker_id = SpeakerIdentifier(self.config)
        
        self.assertTrue(speaker_id.is_available)
        self.assertEqual(speaker_id.owner_name, 'Karan')
        self.assertEqual(speaker_id.owner_title, 'Sir')
    
    def test_speaker_identification_unavailable(self):
        """Test speaker identification when libraries are not available."""
        with patch('speech.speaker_identification.SPEAKER_ID_AVAILABLE', False):
            speaker_id = SpeakerIdentifier(self.config)
            
            self.assertFalse(speaker_id.is_available)
    
    @patch('speech.speaker_identification.SPEAKER_ID_AVAILABLE', True)
    @patch('speech.speaker_identification.librosa')
    @patch('speech.speaker_identification.sklearn')
    def test_voice_profile_training(self, mock_sklearn, mock_librosa):
        """Test voice profile training."""
        speaker_id = SpeakerIdentifier(self.config)
        
        # Mock audio samples
        import numpy as np
        audio_samples = [
            np.random.rand(48000),  # 3 seconds at 16kHz
            np.random.rand(48000),
            np.random.rand(48000)
        ]
        
        # Mock feature extraction
        speaker_id.extract_voice_features = Mock(return_value=np.random.rand(30))
        
        success = speaker_id.train_owner_profile(audio_samples)
        self.assertTrue(success)
        self.assertIn('Karan', speaker_id.profiles)
    
    @patch('speech.speaker_identification.SPEAKER_ID_AVAILABLE', True)
    def test_identification_result(self):
        """Test speaker identification result structure."""
        result = SpeakerIdentificationResult(
            is_owner=True,
            speaker_name='Karan',
            confidence=0.85,
            title='Sir'
        )
        
        self.assertTrue(result.is_owner)
        self.assertEqual(result.speaker_name, 'Karan')
        self.assertEqual(result.confidence, 0.85)
        self.assertEqual(result.title, 'Sir')
    
    def tearDown(self):
        """Clean up test files."""
        profile_path = Path(self.config['profile_path'])
        if profile_path.exists():
            profile_path.unlink()


class TestEnhancedTTS(unittest.TestCase):
    """Test suite for enhanced TTS system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'primary_engine': 'pyttsx3',
            'fallback_engine': 'pyttsx3',
            'rate': 180,
            'volume': 0.9,
            'add_pauses': True
        }
    
    @patch('speech.enhanced_tts.PYTTSX3_AVAILABLE', True)
    @patch('speech.enhanced_tts.pyttsx3')
    def test_tts_initialization(self, mock_pyttsx3):
        """Test TTS system initialization."""
        mock_engine = Mock()
        mock_pyttsx3.init.return_value = mock_engine
        mock_engine.getProperty.return_value = []
        
        tts = EnhancedTTS(self.config)
        
        self.assertIsNotNone(tts.pyttsx3_engine)
        self.assertEqual(tts.current_engine, 'pyttsx3')
    
    def test_pronunciation_rules(self):
        """Test pronunciation rule application."""
        tts = EnhancedTTS(self.config)
        
        # Test G.H.O.S.T. pronunciation
        text = "Hello, I am G.H.O.S.T."
        processed = tts._apply_pronunciation_rules(text)
        self.assertIn('Ghost', processed)
        self.assertNotIn('G.H.O.S.T.', processed)
        
        # Test other technical terms
        text = "The CPU usage is high"
        processed = tts._apply_pronunciation_rules(text)
        self.assertIn('C P U', processed)
    
    def test_prosody_markup(self):
        """Test prosody markup addition."""
        from speech.enhanced_tts import SpeechSettings
        
        tts = EnhancedTTS(self.config)
        settings = SpeechSettings(add_pauses=True, emotion='friendly')
        
        text = "Hello, Sir. How are you today?"
        processed = tts._add_prosody_markup(text, settings)
        
        # Should contain break tags
        self.assertIn('break', processed.lower())
    
    @patch('speech.enhanced_tts.PYTTSX3_AVAILABLE', True)
    @patch('speech.enhanced_tts.pyttsx3')
    def test_speech_synthesis(self, mock_pyttsx3):
        """Test speech synthesis."""
        mock_engine = Mock()
        mock_pyttsx3.init.return_value = mock_engine
        mock_engine.getProperty.return_value = []
        
        tts = EnhancedTTS(self.config)
        
        # Test speaking
        success = tts.speak("Hello, Sir. G.H.O.S.T. is ready.", style="friendly")
        
        # Should call pyttsx3 engine
        mock_engine.say.assert_called()
        mock_engine.runAndWait.assert_called()
    
    def test_voice_style_application(self):
        """Test voice style application."""
        from speech.enhanced_tts import SpeechSettings
        
        tts = EnhancedTTS(self.config)
        base_settings = SpeechSettings()
        
        # Test friendly style
        friendly_settings = tts._apply_style_settings(base_settings, "friendly")
        self.assertEqual(friendly_settings.emotion, "friendly")
        self.assertGreater(friendly_settings.pitch, base_settings.pitch)
        
        # Test serious style
        serious_settings = tts._apply_style_settings(base_settings, "serious")
        self.assertEqual(serious_settings.emotion, "serious")
        self.assertLess(serious_settings.pitch, base_settings.pitch)


class TestProactiveIntelligence(unittest.TestCase):
    """Test suite for proactive intelligence system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'proactive_enabled': True,
            'check_interval': 60,
            'daily_briefing': {
                'briefing_time': '08:00',
                'include_weather': True,
                'include_system_status': True
            },
            'health_monitor': {
                'work_session_threshold': 90,
                'break_reminder_interval': 60
            }
        }
        
        # Use temporary files for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            self.config['daily_briefing']['state_file'] = f"{temp_dir}/briefing_state.json"
            self.config['health_monitor']['activity_log'] = f"{temp_dir}/activity_log.json"
    
    def test_proactive_intelligence_initialization(self):
        """Test proactive intelligence initialization."""
        pi = ProactiveIntelligence(self.config)
        
        self.assertTrue(pi.proactive_enabled)
        self.assertIsNotNone(pi.briefing_manager)
        self.assertIsNotNone(pi.health_monitor)
        self.assertIsNotNone(pi.motivational_manager)
    
    def test_daily_briefing_generation(self):
        """Test daily briefing generation."""
        pi = ProactiveIntelligence(self.config)
        
        # Force briefing generation
        pi.briefing_manager.last_briefing_date = None
        
        briefing_event = pi.briefing_manager.generate_daily_briefing("Sir")
        
        self.assertEqual(briefing_event.event_type, ProactiveEventType.DAILY_BRIEFING)
        self.assertIn('Sir', briefing_event.message)
        self.assertGreater(briefing_event.priority, 5)
    
    def test_health_monitoring(self):
        """Test health monitoring functionality."""
        pi = ProactiveIntelligence(self.config)
        
        # Start work session
        pi.start_work_session()
        self.assertIsNotNone(pi.health_monitor.session_start_time)
        
        # Simulate long work session
        pi.health_monitor.session_start_time = datetime.now() - timedelta(minutes=95)
        pi.health_monitor.last_break_time = datetime.now() - timedelta(minutes=70)
        
        health_events = pi.health_monitor.check_health_reminders()
        
        # Should generate break suggestions
        self.assertGreater(len(health_events), 0)
        
        break_events = [e for e in health_events if e.event_type == ProactiveEventType.BREAK_SUGGESTION]
        self.assertGreater(len(break_events), 0)
    
    def test_proactive_event_checking(self):
        """Test proactive event checking."""
        pi = ProactiveIntelligence(self.config)
        
        # Force check by resetting last check time
        pi.last_check_time = datetime.now() - timedelta(minutes=10)
        
        events = pi.check_proactive_events("Sir")
        
        # Should return list of events
        self.assertIsInstance(events, list)
        
        # Events should be sorted by priority
        if len(events) > 1:
            for i in range(len(events) - 1):
                self.assertGreaterEqual(events[i].priority, events[i + 1].priority)
    
    def test_productivity_insights(self):
        """Test productivity insights generation."""
        pi = ProactiveIntelligence(self.config)
        
        # Add some mock activity data
        pi.health_monitor.activity_log = [
            {
                'type': 'session_end',
                'timestamp': datetime.now().isoformat(),
                'duration_minutes': 60
            },
            {
                'type': 'session_end',
                'timestamp': (datetime.now() - timedelta(days=1)).isoformat(),
                'duration_minutes': 90
            }
        ]
        
        insights = pi.get_productivity_insights()
        
        self.assertIn('sessions_count', insights)
        self.assertIn('average_session_minutes', insights)
        self.assertIn('total_time_hours', insights)


class TestAdvancedActions(unittest.TestCase):
    """Test suite for advanced actions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'file_manager': {},
            'clipboard': {},
            'timers': {},
            'system_monitor': {},
            'news': {}
        }
        self.dispatcher = AdvancedActionDispatcher(self.config)
    
    def test_action_dispatcher_initialization(self):
        """Test action dispatcher initialization."""
        self.assertIsNotNone(self.dispatcher.file_manager)
        self.assertIsNotNone(self.dispatcher.clipboard_manager)
        self.assertIsNotNone(self.dispatcher.timer_manager)
        self.assertIsNotNone(self.dispatcher.system_monitor)
        
        # Check available actions
        actions = self.dispatcher.get_available_actions()
        self.assertIn('find_files', actions)
        self.assertIn('system_status', actions)
        self.assertIn('set_timer', actions)
    
    @patch('actions.advanced_actions.Path')
    def test_file_finding(self, mock_path):
        """Test file finding functionality."""
        # Mock file system
        mock_file = Mock()
        mock_file.is_file.return_value = True
        mock_file.name = 'test_document.pdf'
        mock_file.stat.return_value.st_size = 1024
        mock_file.stat.return_value.st_mtime = time.time()
        mock_file.suffix = '.pdf'
        
        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.rglob.return_value = [mock_file]
        mock_path.return_value = mock_path_instance
        
        # Test file search
        result = self.dispatcher.execute_action('find_files', {'query': 'document'})
        
        self.assertEqual(result.result, ActionResult.SUCCESS)
        self.assertIn('files', result.data)
    
    def test_timer_management(self):
        """Test timer management functionality."""
        # Set a timer
        result = self.dispatcher.execute_action('set_timer', {
            'duration_minutes': 5,
            'label': 'Test Timer'
        })
        
        self.assertEqual(result.result, ActionResult.SUCCESS)
        self.assertIn('timer_id', result.data)
        
        # Check for due items
        due_items = self.dispatcher.check_due_items()
        self.assertIsInstance(due_items, list)
    
    @patch('actions.advanced_actions.PSUTIL_AVAILABLE', True)
    @patch('actions.advanced_actions.psutil')
    def test_system_monitoring(self, mock_psutil):
        """Test system monitoring functionality."""
        # Mock system data
        mock_psutil.cpu_percent.return_value = 25.5
        mock_psutil.cpu_count.return_value = 8
        
        mock_memory = Mock()
        mock_memory.percent = 45.2
        mock_memory.available = 8 * 1024**3  # 8GB
        mock_memory.total = 16 * 1024**3     # 16GB
        mock_psutil.virtual_memory.return_value = mock_memory
        
        mock_disk = Mock()
        mock_disk.used = 500 * 1024**3       # 500GB
        mock_disk.total = 1000 * 1024**3     # 1TB
        mock_disk.free = 500 * 1024**3       # 500GB
        mock_psutil.disk_usage.return_value = mock_disk
        
        mock_network = Mock()
        mock_network.bytes_sent = 1024**3
        mock_network.bytes_recv = 2 * 1024**3
        mock_psutil.net_io_counters.return_value = mock_network
        
        # Test system status
        result = self.dispatcher.execute_action('system_status', {})
        
        self.assertEqual(result.result, ActionResult.SUCCESS)
        self.assertIn('cpu', result.data)
        self.assertIn('memory', result.data)
        self.assertIn('disk', result.data)
    
    def test_unknown_action(self):
        """Test handling of unknown actions."""
        result = self.dispatcher.execute_action('unknown_action', {})
        
        self.assertEqual(result.result, ActionResult.FAILED)
        self.assertIn('Unknown action', result.message)
        self.assertIsNotNone(result.suggestions)


def run_jarvis_tests():
    """Run all J.A.R.V.I.S. system tests."""
    print("Running G.H.O.S.T. J.A.R.V.I.S. System Tests")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestEnhancedPersonality,
        TestSpeakerIdentification,
        TestEnhancedTTS,
        TestProactiveIntelligence,
        TestAdvancedActions
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\nOverall result: {'PASS' if success else 'FAIL'}")
    
    return success


def demo_jarvis_features():
    """Demonstrate J.A.R.V.I.S.-like features."""
    print("\n🤖 G.H.O.S.T. J.A.R.V.I.S. Features Demo")
    print("=" * 40)
    
    try:
        # Demo personality system
        print("\n1. 🎭 Enhanced Personality System")
        print("-" * 30)
        
        config = {
            'mode': 'jarvis',
            'owner_name': 'Karan',
            'owner_title': 'Sir'
        }
        
        personality = EnhancedPersonality(config)
        
        # Owner greeting
        greeting, voice_settings = personality.get_greeting(is_owner=True, is_first_time=True)
        print(f"Owner Greeting: {greeting}")
        print(f"Voice Rate: {voice_settings.rate} WPM")
        
        # Wake word response
        wake_response, _ = personality.get_wake_word_response(is_owner=True)
        print(f"Wake Word Response: {wake_response}")
        
        # Unknown user greeting
        unknown_greeting, _ = personality.get_greeting(is_owner=False)
        print(f"Unknown User Greeting: {unknown_greeting}")
        
        # Demo proactive intelligence
        print("\n2. 🧠 Proactive Intelligence")
        print("-" * 30)
        
        pi_config = {
            'proactive_enabled': True,
            'daily_briefing': {'briefing_time': '08:00'},
            'health_monitor': {'work_session_threshold': 90}
        }
        
        pi = ProactiveIntelligence(pi_config)
        
        # Start work session
        pi.start_work_session()
        print("✅ Work session started")
        
        # Check proactive events
        events = pi.check_proactive_events("Sir")
        print(f"📋 Found {len(events)} proactive events")
        
        for event in events[:2]:  # Show first 2 events
            print(f"  - {event.event_type.value}: {event.message[:60]}...")
        
        # Demo advanced actions
        print("\n3. ⚡ Advanced Actions")
        print("-" * 30)
        
        dispatcher = AdvancedActionDispatcher({})
        
        # List available actions
        actions = dispatcher.get_available_actions()
        print(f"📝 Available Actions: {', '.join(actions[:5])}...")
        
        # Demo timer
        timer_result = dispatcher.execute_action('set_timer', {
            'duration_minutes': 1,
            'label': 'Demo Timer'
        })
        print(f"⏰ Timer Result: {timer_result.message}")
        
        # Demo system status
        try:
            status_result = dispatcher.execute_action('system_status', {})
            print(f"💻 System Status: {status_result.message}")
        except:
            print("💻 System Status: Monitoring not available")
        
        print("\n✅ J.A.R.V.I.S. features demo completed!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='G.H.O.S.T. J.A.R.V.I.S. System Tests')
    parser.add_argument('--demo', action='store_true', help='Run feature demonstration')
    parser.add_argument('--test', action='store_true', help='Run unit tests')
    
    args = parser.parse_args()
    
    if args.demo:
        demo_jarvis_features()
    elif args.test:
        run_jarvis_tests()
    else:
        # Run both by default
        print("Running J.A.R.V.I.S. system tests and demonstration...")
        test_success = run_jarvis_tests()
        
        print("\n" + "=" * 60)
        input("Press Enter to run feature demonstration...")
        demo_jarvis_features()
        
        if not test_success:
            sys.exit(1)
