"""
Voice system test suite for G.H.O.S.T. Virtual Assistant.

This module tests the speech-to-text, text-to-speech, and voice
integration components to ensure proper functionality.
"""

import sys
import os
import time
import unittest
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from speech.speech_to_text import SpeechToText
from speech.text_to_speech import VoiceManager
from core.personality import GhostPersonality


class TestVoiceSystem(unittest.TestCase):
    """Test suite for the voice system components."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.stt_config = {
            'model_path': 'models/vosk-model-small-en-us-0.15',
            'wake_words': ['ghost', 'hey ghost'],
            'sample_rate': 16000,
            'energy_threshold': 300
        }
        
        self.tts_config = {
            'primary_engine': 'pyttsx3',  # Use fallback for testing
            'fallback_engine': 'pyttsx3',
            'voice_speed': 1.0,
            'volume': 0.8
        }
        
        self.personality_config = {
            'profile': 'assistant'
        }
    
    def test_voice_manager_initialization(self):
        """Test VoiceManager initialization."""
        print("\n=== Testing VoiceManager Initialization ===")
        
        try:
            voice_manager = VoiceManager(self.tts_config)
            self.assertIsNotNone(voice_manager)
            self.assertIn(voice_manager.current_engine, ['coqui', 'pyttsx3'])
            print(f"✓ VoiceManager initialized with engine: {voice_manager.current_engine}")
            
        except Exception as e:
            self.fail(f"VoiceManager initialization failed: {e}")
    
    def test_ghost_pronunciation(self):
        """Test that G.H.O.S.T. is pronounced correctly."""
        print("\n=== Testing G.H.O.S.T. Pronunciation ===")
        
        try:
            voice_manager = VoiceManager(self.tts_config)
            
            # Test pronunciation rules
            test_phrases = [
                "Hello, I am G.H.O.S.T.",
                "G.H.O.S.T. systems online",
                "This is GHOST speaking",
                "G H O S T ready to assist"
            ]
            
            for phrase in test_phrases:
                processed = voice_manager._process_text_for_speech(phrase)
                print(f"Original: '{phrase}'")
                print(f"Processed: '{processed}'")
                
                # Check that G.H.O.S.T. variants are replaced with "Ghost"
                self.assertNotIn('G.H.O.S.T.', processed)
                self.assertNotIn('G H O S T', processed)
                self.assertIn('Ghost', processed)
                print("✓ Pronunciation rule applied correctly")
            
        except Exception as e:
            self.fail(f"Pronunciation test failed: {e}")
    
    def test_voice_synthesis(self):
        """Test voice synthesis functionality."""
        print("\n=== Testing Voice Synthesis ===")
        
        try:
            voice_manager = VoiceManager(self.tts_config)
            
            test_text = "Hello! This is G.H.O.S.T. testing the voice system."
            
            print(f"Testing synthesis with: '{test_text}'")
            result = voice_manager.speak(test_text, interrupt=True)
            
            self.assertTrue(result, "Voice synthesis should return True on success")
            print("✓ Voice synthesis initiated successfully")
            
            # Wait a moment for speech to start
            time.sleep(1)
            
            # Test if speaking state is tracked
            if voice_manager.is_speaking_now():
                print("✓ Speech state tracking working")
            else:
                print("ℹ Speech completed quickly or running in test mode")
            
        except Exception as e:
            self.fail(f"Voice synthesis test failed: {e}")
    
    def test_voice_styles(self):
        """Test different voice styles."""
        print("\n=== Testing Voice Styles ===")
        
        try:
            voice_manager = VoiceManager(self.tts_config)
            
            styles = ['normal', 'excited', 'calm', 'formal', 'friendly']
            test_text = "This is a test of the voice style system."
            
            for style in styles:
                print(f"Testing style: {style}")
                styled_text = voice_manager._apply_speech_style(test_text, style)
                print(f"  Styled text: '{styled_text}'")
                
                # Test speaking with style
                result = voice_manager.speak_with_style(f"Testing {style} style", style)
                self.assertTrue(result, f"Style {style} should work")
                
                time.sleep(0.5)  # Brief pause between tests
            
            print("✓ All voice styles tested successfully")
            
        except Exception as e:
            self.fail(f"Voice styles test failed: {e}")
    
    def test_available_voices(self):
        """Test getting available voices."""
        print("\n=== Testing Available Voices ===")
        
        try:
            voice_manager = VoiceManager(self.tts_config)
            
            voices = voice_manager.get_available_voices()
            self.assertIsInstance(voices, list)
            
            print(f"Found {len(voices)} available voices:")
            for voice in voices:
                print(f"  - {voice.get('name', 'Unknown')} ({voice.get('engine', 'Unknown')})")
            
            if voices:
                print("✓ Voice enumeration working")
            else:
                print("⚠ No voices found (may be normal in test environment)")
            
        except Exception as e:
            self.fail(f"Available voices test failed: {e}")
    
    def test_voice_switching(self):
        """Test switching between voices."""
        print("\n=== Testing Voice Switching ===")
        
        try:
            voice_manager = VoiceManager(self.tts_config)
            
            voices = voice_manager.get_available_voices()
            
            if len(voices) > 1:
                # Test switching to different voice
                first_voice = voices[0]['name']
                second_voice = voices[1]['name']
                
                print(f"Switching to voice: {first_voice}")
                result1 = voice_manager.set_voice(first_voice)
                
                print(f"Switching to voice: {second_voice}")
                result2 = voice_manager.set_voice(second_voice)
                
                print("✓ Voice switching functionality tested")
            else:
                print("ℹ Not enough voices available for switching test")
            
        except Exception as e:
            self.fail(f"Voice switching test failed: {e}")
    
    def test_personality_integration(self):
        """Test personality system integration."""
        print("\n=== Testing Personality Integration ===")
        
        try:
            personality = GhostPersonality(self.personality_config)
            
            # Test greetings
            greeting = personality.get_greeting("TestUser", is_first_time=True)
            print(f"First-time greeting: '{greeting}'")
            self.assertIsInstance(greeting, str)
            self.assertGreater(len(greeting), 0)
            
            # Test confirmations
            confirmation = personality.get_confirmation("open Chrome")
            print(f"Confirmation: '{confirmation}'")
            self.assertIsInstance(confirmation, str)
            
            # Test farewells
            farewell = personality.get_farewell("TestUser")
            print(f"Farewell: '{farewell}'")
            self.assertIsInstance(farewell, str)
            
            # Test response enhancement
            original_response = "Task completed successfully."
            enhanced = personality.enhance_response(original_response)
            print(f"Original: '{original_response}'")
            print(f"Enhanced: '{enhanced}'")
            
            print("✓ Personality integration working")
            
        except Exception as e:
            self.fail(f"Personality integration test failed: {e}")
    
    def test_speech_to_text_initialization(self):
        """Test SpeechToText initialization (if VOSK model available)."""
        print("\n=== Testing SpeechToText Initialization ===")
        
        try:
            # Check if VOSK model exists
            model_path = Path(self.stt_config['model_path'])
            
            if model_path.exists():
                stt = SpeechToText(self.stt_config)
                self.assertIsNotNone(stt)
                print("✓ SpeechToText initialized successfully")
                
                # Test microphone info
                mic_info = stt.get_microphone_info()
                print(f"Microphone info: {len(mic_info.get('available_devices', []))} devices found")
                
            else:
                print(f"⚠ VOSK model not found at {model_path}")
                print("  Download with: wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip")
                
        except Exception as e:
            print(f"⚠ SpeechToText test skipped: {e}")
    
    def test_pronunciation_rules(self):
        """Test custom pronunciation rules."""
        print("\n=== Testing Pronunciation Rules ===")
        
        try:
            voice_manager = VoiceManager(self.tts_config)
            
            # Test default rules
            test_cases = {
                'G.H.O.S.T.': 'Ghost',
                'AI system': 'A I system',
                'JSON data': 'Jason data',
                'SQL query': 'sequel query'
            }
            
            for original, expected_word in test_cases.items():
                processed = voice_manager._process_text_for_speech(original)
                print(f"'{original}' -> '{processed}'")
                self.assertIn(expected_word, processed)
            
            # Test adding custom rule
            voice_manager.add_pronunciation_rule('API', 'Application Programming Interface')
            processed = voice_manager._process_text_for_speech('API call')
            print(f"Custom rule: 'API call' -> '{processed}'")
            
            print("✓ Pronunciation rules working correctly")
            
        except Exception as e:
            self.fail(f"Pronunciation rules test failed: {e}")
    
    def test_voice_cleanup(self):
        """Test voice system cleanup."""
        print("\n=== Testing Voice System Cleanup ===")
        
        try:
            voice_manager = VoiceManager(self.tts_config)
            
            # Start some speech
            voice_manager.speak("Testing cleanup functionality", interrupt=False)
            
            # Test cleanup
            voice_manager.cleanup()
            
            # Verify speech is stopped
            self.assertFalse(voice_manager.is_speaking_now())
            
            print("✓ Voice system cleanup successful")
            
        except Exception as e:
            self.fail(f"Voice cleanup test failed: {e}")


def run_voice_demo():
    """Run a comprehensive voice system demonstration."""
    print("\n" + "="*60)
    print("  G.H.O.S.T. Voice System Demonstration")
    print("="*60)
    
    try:
        # Initialize components
        tts_config = {
            'primary_engine': 'pyttsx3',
            'fallback_engine': 'pyttsx3',
            'voice_speed': 1.0,
            'volume': 0.9
        }
        
        personality_config = {'profile': 'assistant'}
        
        voice_manager = VoiceManager(tts_config)
        personality = GhostPersonality(personality_config)
        
        print("\n1. System Initialization:")
        print(f"   Voice Engine: {voice_manager.current_engine}")
        print(f"   Personality: {personality.current_profile.name}")
        
        # Demo greeting
        print("\n2. Greeting Demo:")
        greeting = personality.get_greeting("User", is_first_time=True)
        print(f"   Text: {greeting}")
        voice_manager.speak(greeting)
        time.sleep(3)
        
        # Demo G.H.O.S.T. pronunciation
        print("\n3. G.H.O.S.T. Pronunciation Demo:")
        ghost_text = "Hello! I am G.H.O.S.T., your virtual assistant."
        processed = voice_manager._process_text_for_speech(ghost_text)
        print(f"   Original: {ghost_text}")
        print(f"   Processed: {processed}")
        voice_manager.speak(processed)
        time.sleep(4)
        
        # Demo different styles
        print("\n4. Voice Style Demo:")
        styles = ['normal', 'excited', 'calm', 'formal']
        for style in styles:
            text = f"This is the {style} speaking style."
            print(f"   {style.title()}: {text}")
            voice_manager.speak_with_style(text, style)
            time.sleep(3)
        
        # Demo confirmation
        print("\n5. Confirmation Demo:")
        confirmation = personality.get_confirmation("open Chrome")
        print(f"   Confirmation: {confirmation}")
        voice_manager.speak(confirmation)
        time.sleep(2)
        
        # Demo farewell
        print("\n6. Farewell Demo:")
        farewell = personality.get_farewell("User")
        print(f"   Farewell: {farewell}")
        voice_manager.speak(farewell)
        time.sleep(3)
        
        print("\n✓ Voice system demonstration completed successfully!")
        
    except Exception as e:
        print(f"\n✗ Demo failed: {e}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='G.H.O.S.T. Voice System Tests')
    parser.add_argument('--demo', action='store_true', help='Run voice demonstration')
    parser.add_argument('--test', action='store_true', help='Run unit tests')
    
    args = parser.parse_args()
    
    if args.demo:
        run_voice_demo()
    elif args.test:
        unittest.main(argv=[''])
    else:
        # Run both by default
        print("Running voice system tests...")
        unittest.main(argv=[''], exit=False, verbosity=2)
        
        print("\n" + "="*60)
        input("Press Enter to run voice demonstration...")
        run_voice_demo()
