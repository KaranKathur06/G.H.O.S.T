"""
Wake word detection test suite for G.H.O.S.T.

This module tests wake word detection, state transitions,
and background operation functionality.
"""

import sys
import os
import time
import unittest
import threading
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.ghost_states import GhostStateMachine, GhostState, StateTransition
from speech.wake_word_listener import WakeWordListener, WakeWordManager, WakeWordDetection
from core.background_orchestrator import BackgroundOrchestrator


class TestGhostStateMachine(unittest.TestCase):
    """Test suite for G.H.O.S.T. state machine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'max_listening_duration': 10.0,
            'max_responding_duration': 30.0,
            'idle_timeout': 60.0
        }
        self.state_machine = GhostStateMachine(self.config)
    
    def test_initial_state(self):
        """Test initial state is IDLE."""
        self.assertEqual(self.state_machine.get_current_state(), GhostState.IDLE)
    
    def test_wake_word_transition(self):
        """Test wake word detection transition."""
        # Should start in IDLE
        self.assertEqual(self.state_machine.get_current_state(), GhostState.IDLE)
        
        # Wake word should transition to LISTENING
        result = self.state_machine.wake_word_detected("ghost")
        self.assertTrue(result)
        self.assertEqual(self.state_machine.get_current_state(), GhostState.LISTENING)
    
    def test_speech_captured_transition(self):
        """Test speech captured transition."""
        # Start in LISTENING state
        self.state_machine.transition_to(GhostState.LISTENING, "test")
        
        # Speech captured should transition to RESPONDING
        result = self.state_machine.speech_captured("hello ghost")
        self.assertTrue(result)
        self.assertEqual(self.state_machine.get_current_state(), GhostState.RESPONDING)
    
    def test_response_completed_transition(self):
        """Test response completed transition."""
        # Start in RESPONDING state
        self.state_machine.transition_to(GhostState.RESPONDING, "test")
        
        # Response completed should return to IDLE
        result = self.state_machine.response_completed("response text")
        self.assertTrue(result)
        self.assertEqual(self.state_machine.get_current_state(), GhostState.IDLE)
    
    def test_invalid_transitions(self):
        """Test invalid state transitions are rejected."""
        # Can't go from IDLE to RESPONDING directly
        result = self.state_machine.transition_to(GhostState.RESPONDING, "invalid")
        self.assertFalse(result)
        self.assertEqual(self.state_machine.get_current_state(), GhostState.IDLE)
    
    def test_error_handling(self):
        """Test error state handling."""
        # Error can be triggered from any state
        result = self.state_machine.handle_error("test error")
        self.assertTrue(result)
        self.assertEqual(self.state_machine.get_current_state(), GhostState.ERROR)
        
        # Should be able to recover
        result = self.state_machine.recover_from_error()
        self.assertTrue(result)
        self.assertEqual(self.state_machine.get_current_state(), GhostState.IDLE)
    
    def test_disable_enable_listening(self):
        """Test disabling and enabling listening."""
        # Should be able to disable from IDLE
        result = self.state_machine.disable_listening()
        self.assertTrue(result)
        self.assertEqual(self.state_machine.get_current_state(), GhostState.DISABLED)
        
        # Should be able to re-enable
        result = self.state_machine.enable_listening()
        self.assertTrue(result)
        self.assertEqual(self.state_machine.get_current_state(), GhostState.IDLE)
    
    def test_state_history(self):
        """Test state transition history tracking."""
        # Make some transitions
        self.state_machine.wake_word_detected("ghost")
        self.state_machine.speech_captured("test")
        self.state_machine.response_completed("done")
        
        # Check history
        history = self.state_machine.get_state_history()
        self.assertGreaterEqual(len(history), 3)
        
        # Check last transition
        last_transition = history[-1]
        self.assertEqual(last_transition['to_state'], 'idle')
        self.assertEqual(last_transition['trigger'], 'response_completed')
    
    def test_state_timeouts(self):
        """Test state timeout handling."""
        # Transition to LISTENING state
        self.state_machine.transition_to(GhostState.LISTENING, "test")
        
        # Wait for timeout (should be quick in test)
        time.sleep(0.1)
        
        # Manually trigger timeout for testing
        self.state_machine._handle_state_timeout()
        
        # Should return to IDLE
        self.assertEqual(self.state_machine.get_current_state(), GhostState.IDLE)
    
    def tearDown(self):
        """Clean up after tests."""
        if self.state_machine:
            self.state_machine.cleanup()


class TestWakeWordListener(unittest.TestCase):
    """Test suite for wake word detection."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'engine': 'simple_energy',
            'wake_words': ['ghost', 'hey ghost'],
            'confidence_threshold': 0.6,
            'sample_rate': 16000,
            'chunk_size': 1024,
            'energy_threshold': 300
        }
    
    @patch('speech.wake_word_listener.pyaudio.PyAudio')
    def test_wake_word_listener_initialization(self, mock_pyaudio):
        """Test wake word listener initialization."""
        listener = WakeWordListener(self.config)
        
        self.assertIsNotNone(listener)
        self.assertEqual(listener.engine_type, 'simple_energy')
        self.assertEqual(listener.wake_words, ['ghost', 'hey ghost'])
    
    @patch('speech.wake_word_listener.pyaudio.PyAudio')
    def test_detection_callback(self, mock_pyaudio):
        """Test wake word detection callback."""
        listener = WakeWordListener(self.config)
        
        # Mock callback
        callback_called = threading.Event()
        detected_word = None
        
        def test_callback(detection):
            nonlocal detected_word
            detected_word = detection.word
            callback_called.set()
        
        # Test detection handling
        detection = WakeWordDetection(
            word="ghost",
            confidence=0.8,
            timestamp=time.time()
        )
        
        listener.wake_word_callback = test_callback
        listener._handle_detection(detection)
        
        # Verify callback was called
        self.assertTrue(callback_called.wait(timeout=1.0))
        self.assertEqual(detected_word, "ghost")
    
    def test_energy_calculation(self):
        """Test audio energy calculation."""
        listener = WakeWordListener(self.config)
        
        # Create test audio data (silence)
        silence_data = b'\x00' * 1000
        
        # Create test audio data (noise)
        noise_data = b'\xff\x7f' * 500
        
        # Test energy calculation
        silence_energy = listener._calculate_energy(silence_data)
        noise_energy = listener._calculate_energy(noise_data)
        
        # Noise should have higher energy than silence
        self.assertGreater(noise_energy, silence_energy)
        self.assertGreaterEqual(silence_energy, 0)
    
    def test_wake_word_patterns(self):
        """Test wake word pattern generation."""
        listener = WakeWordListener(self.config)
        
        # Test pattern generation for "ghost"
        patterns = listener._generate_phonetic_patterns("ghost")
        
        self.assertIn("ghost", patterns)
        self.assertGreater(len(patterns), 1)  # Should have variations
    
    def test_detection_stats(self):
        """Test detection statistics."""
        listener = WakeWordListener(self.config)
        
        stats = listener.get_detection_stats()
        
        self.assertIn('engine_type', stats)
        self.assertIn('wake_words', stats)
        self.assertIn('detections_count', stats)
        self.assertEqual(stats['detections_count'], 0)  # No detections yet
    
    @patch('speech.wake_word_listener.pyaudio.PyAudio')
    def test_cleanup(self, mock_pyaudio):
        """Test wake word listener cleanup."""
        listener = WakeWordListener(self.config)
        
        # Should not raise exception
        listener.cleanup()


class TestWakeWordManager(unittest.TestCase):
    """Test suite for wake word manager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'primary_engine': 'simple_energy',
            'fallback_engine': 'simple_energy',
            'use_fallback': True,
            'wake_words': ['ghost'],
            'confidence_threshold': 0.6
        }
    
    @patch('speech.wake_word_listener.WakeWordListener')
    def test_manager_initialization(self, mock_listener_class):
        """Test wake word manager initialization."""
        manager = WakeWordManager(self.config)
        
        self.assertIsNotNone(manager)
        self.assertEqual(manager.primary_engine, 'simple_energy')
        self.assertEqual(manager.fallback_engine, 'simple_energy')
    
    @patch('speech.wake_word_listener.WakeWordListener')
    def test_detection_start_stop(self, mock_listener_class):
        """Test starting and stopping detection."""
        # Mock listener instance
        mock_listener = Mock()
        mock_listener.start_listening.return_value = True
        mock_listener_class.return_value = mock_listener
        
        manager = WakeWordManager(self.config)
        manager.primary_listener = mock_listener
        
        # Test callback
        def test_callback(detection):
            pass
        
        # Start detection
        result = manager.start_detection(test_callback)
        self.assertTrue(result)
        mock_listener.start_listening.assert_called_once_with(test_callback)
        
        # Stop detection
        manager.stop_detection()
        mock_listener.stop_listening.assert_called_once()
    
    @patch('speech.wake_word_listener.WakeWordListener')
    def test_status_reporting(self, mock_listener_class):
        """Test status reporting."""
        mock_listener = Mock()
        mock_listener.get_detection_stats.return_value = {
            'is_listening': True,
            'detections_count': 5
        }
        mock_listener_class.return_value = mock_listener
        
        manager = WakeWordManager(self.config)
        manager.primary_listener = mock_listener
        
        status = manager.get_status()
        
        self.assertIn('primary_engine', status)
        self.assertIn('primary_active', status)
        self.assertIn('primary_stats', status)


class TestBackgroundOrchestrator(unittest.TestCase):
    """Test suite for background orchestrator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'background_mode': True,
            'wake_word': {
                'enabled': True,
                'engine': 'simple_energy',
                'wake_words': ['ghost']
            },
            'voice': {
                'enabled': True,
                'primary_engine': 'pyttsx3'
            },
            'tray': {
                'enabled': False  # Disable for testing
            },
            'state_machine': {
                'max_listening_duration': 5.0,
                'max_responding_duration': 10.0
            }
        }
    
    @patch('core.background_orchestrator.create_tray_manager')
    @patch('core.background_orchestrator.WakeWordManager')
    @patch('core.background_orchestrator.VoiceManager')
    @patch('core.background_orchestrator.Brain')
    @patch('core.background_orchestrator.AdvancedMemoryManager')
    def test_orchestrator_initialization(self, mock_memory, mock_brain, 
                                       mock_voice, mock_wake_word, mock_tray):
        """Test background orchestrator initialization."""
        # Mock all dependencies
        mock_memory.return_value = Mock()
        mock_brain.return_value = Mock()
        mock_voice.return_value = Mock()
        mock_wake_word.return_value = Mock()
        mock_tray.return_value = Mock()
        
        orchestrator = BackgroundOrchestrator(self.config)
        
        self.assertIsNotNone(orchestrator)
        self.assertIsNotNone(orchestrator.state_machine)
        self.assertFalse(orchestrator.is_running)
    
    @patch('core.background_orchestrator.create_tray_manager')
    @patch('core.background_orchestrator.WakeWordManager')
    @patch('core.background_orchestrator.VoiceManager')
    @patch('core.background_orchestrator.Brain')
    @patch('core.background_orchestrator.AdvancedMemoryManager')
    def test_wake_word_handling(self, mock_memory, mock_brain, 
                               mock_voice, mock_wake_word, mock_tray):
        """Test wake word detection handling."""
        # Mock dependencies
        mock_memory.return_value = Mock()
        mock_brain.return_value = Mock()
        mock_voice.return_value = Mock()
        mock_wake_word.return_value = Mock()
        mock_tray.return_value = Mock()
        
        orchestrator = BackgroundOrchestrator(self.config)
        
        # Test wake word detection
        detection = WakeWordDetection(
            word="ghost",
            confidence=0.8,
            timestamp=time.time()
        )
        
        # Should transition to LISTENING state
        initial_state = orchestrator.state_machine.get_current_state()
        orchestrator._on_wake_word_detected(detection)
        
        # Verify state transition
        current_state = orchestrator.state_machine.get_current_state()
        self.assertEqual(current_state, GhostState.LISTENING)
    
    @patch('core.background_orchestrator.create_tray_manager')
    @patch('core.background_orchestrator.WakeWordManager')
    @patch('core.background_orchestrator.VoiceManager')
    @patch('core.background_orchestrator.Brain')
    @patch('core.background_orchestrator.AdvancedMemoryManager')
    def test_system_status(self, mock_memory, mock_brain, 
                          mock_voice, mock_wake_word, mock_tray):
        """Test system status reporting."""
        # Mock dependencies
        mock_memory.return_value = Mock()
        mock_brain.return_value = Mock()
        mock_voice.return_value = Mock()
        mock_wake_word_manager = Mock()
        mock_wake_word_manager.get_status.return_value = {'primary_active': True}
        mock_wake_word.return_value = mock_wake_word_manager
        mock_tray.return_value = Mock()
        
        orchestrator = BackgroundOrchestrator(self.config)
        
        status = orchestrator.get_system_status()
        
        self.assertIn('is_running', status)
        self.assertIn('current_state', status)
        self.assertIn('uptime_seconds', status)
        self.assertIn('components', status)
    
    @patch('core.background_orchestrator.create_tray_manager')
    @patch('core.background_orchestrator.WakeWordManager')
    @patch('core.background_orchestrator.VoiceManager')
    @patch('core.background_orchestrator.Brain')
    @patch('core.background_orchestrator.AdvancedMemoryManager')
    def test_system_commands(self, mock_memory, mock_brain, 
                            mock_voice, mock_wake_word, mock_tray):
        """Test system command handling."""
        # Mock dependencies
        mock_memory.return_value = Mock()
        mock_brain.return_value = Mock()
        mock_voice.return_value = Mock()
        mock_wake_word.return_value = Mock()
        mock_tray.return_value = Mock()
        
        orchestrator = BackgroundOrchestrator(self.config)
        
        # Test status command
        result = orchestrator.handle_system_command("status")
        self.assertIn('success', result)
        
        # Test enable/disable listening
        result = orchestrator.handle_system_command("disable_listening")
        self.assertTrue(result.get('success', False))
        
        result = orchestrator.handle_system_command("enable_listening")
        self.assertTrue(result.get('success', False))
        
        # Test unknown command
        result = orchestrator.handle_system_command("unknown_command")
        self.assertFalse(result.get('success', True))


class TestStateTransitions(unittest.TestCase):
    """Integration tests for state transitions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'max_listening_duration': 1.0,  # Short for testing
            'max_responding_duration': 2.0,
            'idle_timeout': 60.0
        }
        self.state_machine = GhostStateMachine(self.config)
    
    def test_complete_interaction_cycle(self):
        """Test complete interaction cycle from IDLE to IDLE."""
        # Start in IDLE
        self.assertEqual(self.state_machine.get_current_state(), GhostState.IDLE)
        
        # Wake word detected -> LISTENING
        self.assertTrue(self.state_machine.wake_word_detected("ghost"))
        self.assertEqual(self.state_machine.get_current_state(), GhostState.LISTENING)
        
        # Speech captured -> RESPONDING
        self.assertTrue(self.state_machine.speech_captured("hello"))
        self.assertEqual(self.state_machine.get_current_state(), GhostState.RESPONDING)
        
        # Response completed -> IDLE
        self.assertTrue(self.state_machine.response_completed("Hi there!"))
        self.assertEqual(self.state_machine.get_current_state(), GhostState.IDLE)
    
    def test_error_recovery_cycle(self):
        """Test error handling and recovery."""
        # Start in IDLE
        self.assertEqual(self.state_machine.get_current_state(), GhostState.IDLE)
        
        # Trigger error
        self.assertTrue(self.state_machine.handle_error("test error"))
        self.assertEqual(self.state_machine.get_current_state(), GhostState.ERROR)
        
        # Recover from error
        self.assertTrue(self.state_machine.recover_from_error())
        self.assertEqual(self.state_machine.get_current_state(), GhostState.IDLE)
    
    def test_disable_enable_cycle(self):
        """Test disable/enable listening cycle."""
        # Start in IDLE
        self.assertEqual(self.state_machine.get_current_state(), GhostState.IDLE)
        
        # Disable listening
        self.assertTrue(self.state_machine.disable_listening())
        self.assertEqual(self.state_machine.get_current_state(), GhostState.DISABLED)
        
        # Wake word should not work when disabled
        self.assertFalse(self.state_machine.wake_word_detected("ghost"))
        self.assertEqual(self.state_machine.get_current_state(), GhostState.DISABLED)
        
        # Re-enable listening
        self.assertTrue(self.state_machine.enable_listening())
        self.assertEqual(self.state_machine.get_current_state(), GhostState.IDLE)
        
        # Wake word should work again
        self.assertTrue(self.state_machine.wake_word_detected("ghost"))
        self.assertEqual(self.state_machine.get_current_state(), GhostState.LISTENING)
    
    def tearDown(self):
        """Clean up after tests."""
        if self.state_machine:
            self.state_machine.cleanup()


def run_wake_word_tests():
    """Run all wake word tests."""
    print("Running G.H.O.S.T. Wake Word Detection Tests")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestGhostStateMachine,
        TestWakeWordListener,
        TestWakeWordManager,
        TestBackgroundOrchestrator,
        TestStateTransitions
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


def simulate_wake_word_detection():
    """Simulate wake word detection for manual testing."""
    print("\nSimulating Wake Word Detection")
    print("-" * 30)
    
    try:
        config = {
            'engine': 'simple_energy',
            'wake_words': ['ghost'],
            'confidence_threshold': 0.6
        }
        
        # Create state machine
        state_machine = GhostStateMachine({})
        
        print(f"Initial state: {state_machine.get_current_state().value}")
        
        # Simulate wake word detection
        print("Simulating wake word 'ghost' detection...")
        result = state_machine.wake_word_detected("ghost")
        print(f"Transition successful: {result}")
        print(f"New state: {state_machine.get_current_state().value}")
        
        # Simulate speech capture
        print("Simulating speech capture...")
        result = state_machine.speech_captured("hello ghost")
        print(f"Transition successful: {result}")
        print(f"New state: {state_machine.get_current_state().value}")
        
        # Simulate response completion
        print("Simulating response completion...")
        result = state_machine.response_completed("Hello! How can I help?")
        print(f"Transition successful: {result}")
        print(f"New state: {state_machine.get_current_state().value}")
        
        # Get state history
        history = state_machine.get_state_history()
        print(f"\nState transitions: {len(history)}")
        for i, transition in enumerate(history[-3:], 1):
            print(f"  {i}. {transition['from_state']} -> {transition['to_state']} ({transition['trigger']})")
        
        # Cleanup
        state_machine.cleanup()
        
        print("\nSimulation completed successfully!")
        return True
        
    except Exception as e:
        print(f"Simulation failed: {e}")
        return False


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='G.H.O.S.T. Wake Word Tests')
    parser.add_argument('--simulate', action='store_true', help='Run wake word simulation')
    parser.add_argument('--test', action='store_true', help='Run unit tests')
    
    args = parser.parse_args()
    
    if args.simulate:
        simulate_wake_word_detection()
    elif args.test:
        run_wake_word_tests()
    else:
        # Run both by default
        print("Running wake word tests and simulation...")
        test_success = run_wake_word_tests()
        
        print("\n" + "=" * 60)
        input("Press Enter to run wake word simulation...")
        simulate_wake_word_detection()
        
        if not test_success:
            sys.exit(1)
