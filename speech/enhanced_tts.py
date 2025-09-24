"""
Enhanced Text-to-Speech system for G.H.O.S.T. with Coqui TTS and natural voice.

This module provides high-quality, natural-sounding speech synthesis with
personality-aware prosody control and proper pronunciation of "G.H.O.S.T."
"""

import logging
import re
import time
import threading
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import queue

try:
    from TTS.api import TTS
    COQUI_AVAILABLE = True
except ImportError:
    COQUI_AVAILABLE = False
    TTS = None

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    pyttsx3 = None

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    pygame = None


class VoiceEngine(Enum):
    """Available TTS engines."""
    COQUI = "coqui"          # High-quality neural TTS
    PYTTSX3 = "pyttsx3"      # System TTS fallback
    SYSTEM = "system"        # OS native TTS


@dataclass
class SpeechSettings:
    """Settings for speech synthesis."""
    rate: int = 180           # Words per minute
    volume: float = 0.9       # Volume (0.0 to 1.0)
    pitch: int = 0            # Pitch adjustment (-50 to 50)
    voice_id: Optional[str] = None  # Specific voice ID
    emotion: str = "neutral"  # Emotional tone
    speed: float = 1.0        # Speed multiplier
    add_pauses: bool = True   # Add natural pauses


class EnhancedTTS:
    """
    Enhanced Text-to-Speech system with natural voice synthesis.
    
    Provides high-quality speech with personality-aware prosody,
    proper pronunciation rules, and fallback engines.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize enhanced TTS system.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Engine configuration
        self.primary_engine = config.get('primary_engine', 'coqui')
        self.fallback_engine = config.get('fallback_engine', 'pyttsx3')
        self.use_fallback = config.get('use_fallback', True)
        
        # Voice settings
        self.default_settings = SpeechSettings(
            rate=config.get('rate', 180),
            volume=config.get('volume', 0.9),
            pitch=config.get('pitch', 0),
            voice_id=config.get('voice_id'),
            emotion=config.get('emotion', 'neutral'),
            speed=config.get('speed', 1.0),
            add_pauses=config.get('add_pauses', True)
        )
        
        # Engine instances
        self.coqui_tts = None
        self.pyttsx3_engine = None
        self.current_engine = None
        
        # Audio output
        self.audio_output_path = Path(config.get('audio_output_path', 'temp/tts_output.wav'))
        self.audio_output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Pronunciation rules
        self.pronunciation_rules = self._load_pronunciation_rules()
        
        # Initialize engines
        self._initialize_engines()
        
        # Initialize audio playback
        if PYGAME_AVAILABLE:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        self.logger.info(f"Enhanced TTS initialized with {self.current_engine} engine")
    
    def _initialize_engines(self) -> None:
        """Initialize available TTS engines."""
        try:
            # Try to initialize Coqui TTS first
            if COQUI_AVAILABLE and self.primary_engine == 'coqui':
                self._initialize_coqui()
            
            # Initialize pyttsx3 as fallback
            if PYTTSX3_AVAILABLE:
                self._initialize_pyttsx3()
            
            # Set current engine
            if self.coqui_tts and self.primary_engine == 'coqui':
                self.current_engine = 'coqui'
            elif self.pyttsx3_engine:
                self.current_engine = 'pyttsx3'
            else:
                self.current_engine = None
                self.logger.error("No TTS engines available")
                
        except Exception as e:
            self.logger.error(f"Error initializing TTS engines: {e}")
    
    def _initialize_coqui(self) -> None:
        """Initialize Coqui TTS engine."""
        try:
            # Use a fast, high-quality model
            model_name = self.config.get('coqui_model', 'tts_models/en/ljspeech/tacotron2-DDC')
            
            self.coqui_tts = TTS(model_name=model_name, progress_bar=False)
            self.logger.info(f"Coqui TTS initialized with model: {model_name}")
            
        except Exception as e:
            self.logger.warning(f"Failed to initialize Coqui TTS: {e}")
            self.coqui_tts = None
    
    def _initialize_pyttsx3(self) -> None:
        """Initialize pyttsx3 engine."""
        try:
            self.pyttsx3_engine = pyttsx3.init()
            
            # Configure pyttsx3 settings
            self.pyttsx3_engine.setProperty('rate', self.default_settings.rate)
            self.pyttsx3_engine.setProperty('volume', self.default_settings.volume)
            
            # Try to set a good voice
            voices = self.pyttsx3_engine.getProperty('voices')
            if voices:
                # Prefer female voices for a more pleasant sound
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        self.pyttsx3_engine.setProperty('voice', voice.id)
                        break
                else:
                    # Use first available voice
                    self.pyttsx3_engine.setProperty('voice', voices[0].id)
            
            self.logger.info("pyttsx3 TTS initialized")
            
        except Exception as e:
            self.logger.warning(f"Failed to initialize pyttsx3: {e}")
            self.pyttsx3_engine = None
    
    def _load_pronunciation_rules(self) -> Dict[str, str]:
        """
        Load pronunciation rules for better speech quality.
        
        Returns:
            Dictionary mapping text patterns to pronunciations
        """
        return {
            # G.H.O.S.T. pronunciation - CRITICAL FIX!
            r'\bG\.H\.O\.S\.T\.?\b': 'Ghost',
            r'\bG H O S T\b': 'Ghost', 
            r'\bGHOST\b': 'Ghost',
            r'\bg\.h\.o\.s\.t\.?\b': 'Ghost',
            r'\bg h o s t\b': 'Ghost',
            r'\bghosT\b': 'Ghost',
            
            # Technical terms
            r'\bCPU\b': 'see pee you',
            r'\bRAM\b': 'ram',
            r'\bGPU\b': 'gee pee you',
            r'\bSSD\b': 'solid state drive',
            r'\bHDD\b': 'hard disk drive',
            r'\bUSB\b': 'you ess bee',
            r'\bWiFi\b': 'why fy',
            r'\bAPI\b': 'ay pee eye',
            r'\bURL\b': 'you are ell',
            r'\bHTML\b': 'H T M L',
            r'\bCSS\b': 'see ess ess',
            r'\bJS\b': 'JavaScript',
            
            # Common abbreviations
            r'\bvs\.?\b': 'versus',
            r'\betc\.?\b': 'etcetera',
            r'\be\.g\.?\b': 'for example',
            r'\bi\.e\.?\b': 'that is',
            
            # Numbers and units
            r'\b(\d+)GB\b': r'\1 gigabytes',
            r'\b(\d+)MB\b': r'\1 megabytes', 
            r'\b(\d+)KB\b': r'\1 kilobytes',
            r'\b(\d+)TB\b': r'\1 terabytes',
            r'\b(\d+)GHz\b': r'\1 gigahertz',
            r'\b(\d+)MHz\b': r'\1 megahertz',
            
            # Time formats
            r'\b(\d{1,2}):(\d{2})\s*(AM|PM)\b': r'\1 \2 \3',
            r'\b(\d{1,2}):(\d{2})\b': r'\1 \2',
        }
    
    def _apply_pronunciation_rules(self, text: str) -> str:
        """Apply pronunciation rules to text."""
        processed_text = text
        
        for original, replacement in self.pronunciation_rules.items():
            # Case-insensitive replacement but preserve context
            pattern = re.compile(original, re.IGNORECASE)
            processed_text = pattern.sub(replacement, processed_text)
        
        return processed_text
    
    def _add_prosody_markup(self, text: str, settings: SpeechSettings) -> str:
        """Add prosody markup for natural speech."""
        if not settings.add_pauses:
            return text
        
        # Add pauses after punctuation
        text = re.sub(r'([.!?])\s+', r'\1 <break time="0.5s"/> ', text)
        text = re.sub(r'([,;:])\s+', r'\1 <break time="0.3s"/> ', text)
        
        # Add emphasis to important words
        if settings.emotion == 'excited':
            text = re.sub(r'\b(amazing|great|excellent|perfect|wonderful)\b', 
                         r'<emphasis level="strong">\1</emphasis>', text, flags=re.IGNORECASE)
        
        # Add emotional prosody
        if settings.emotion == 'serious':
            text = f'<prosody rate="slow" pitch="-10%">{text}</prosody>'
        elif settings.emotion == 'friendly':
            text = f'<prosody rate="medium" pitch="+5%">{text}</prosody>'
        elif settings.emotion == 'excited':
            text = f'<prosody rate="fast" pitch="+15%">{text}</prosody>'
        
        return text
    
    def speak(self, text: str, settings: Optional[SpeechSettings] = None, 
              style: str = "neutral", blocking: bool = True) -> bool:
        """
        Speak the given text with specified settings.
        
        Args:
            text: Text to speak
            settings: Speech settings to use
            style: Voice style (friendly, serious, excited, etc.)
            blocking: Whether to wait for speech to complete
            
        Returns:
            True if speech was successful, False otherwise
        """
        if not text or not text.strip():
            return False
        
        try:
            # Apply pronunciation rules FIRST - critical for G.H.O.S.T.
            processed_text = self._apply_pronunciation_rules(text)
            
            # Apply style settings
            if not settings:
                settings = self.default_settings
            
            settings = self._apply_style_settings(settings, style)
            
            # Add prosody markup for natural speech
            if settings.add_pauses:
                processed_text = self._add_prosody_markup(processed_text, settings)
            
            # Use threading for non-blocking speech
            if not blocking:
                speech_thread = threading.Thread(
                    target=self._speak_threaded,
                    args=(processed_text, settings),
                    daemon=True
                )
                speech_thread.start()
                return True
            else:
                return self._speak_threaded(processed_text, settings)
                
        except Exception as e:
            self.logger.error(f"Error in speak method: {e}")
            return False
    
    def _speak_threaded(self, text: str, settings: SpeechSettings) -> bool:
        """
        Internal method for threaded speech synthesis.
        
        Args:
            text: Processed text to speak
            settings: Speech settings
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Try primary engine first
            if self.current_engine == 'pyttsx3' and self.pyttsx3_engine:
                return self._speak_with_pyttsx3(text, settings, True)
            elif self.current_engine == 'coqui' and self.coqui_tts:
                return self._speak_with_coqui(text, settings)
            else:
                self.logger.error("No TTS engine available")
                return False
                
        except Exception as e:
            self.logger.error(f"Error in threaded speech: {e}")
            
            # Try fallback engine
            if self.use_fallback and self.pyttsx3_engine:
                try:
                    return self._speak_with_pyttsx3(text, settings, True)
                except Exception as fallback_error:
                    self.logger.error(f"Fallback TTS also failed: {fallback_error}")
            
            return False
    
    def _apply_style_settings(self, settings: SpeechSettings, style: str) -> SpeechSettings:
        """Apply style-specific settings."""
        # Create a copy to avoid modifying the original
        new_settings = SpeechSettings(
            rate=settings.rate,
            volume=settings.volume,
            pitch=settings.pitch,
            voice_id=settings.voice_id,
            emotion=settings.emotion,
            speed=settings.speed,
            add_pauses=settings.add_pauses
        )
        
        # Apply style modifications
        if style == "friendly":
            new_settings.emotion = "friendly"
            new_settings.pitch += 5
            new_settings.rate += 10
        elif style == "serious":
            new_settings.emotion = "serious"
            new_settings.pitch -= 5
            new_settings.rate -= 20
        elif style == "calm":
            new_settings.emotion = "neutral"
            new_settings.rate -= 10
            new_settings.add_pauses = True
        elif style == "excited":
            new_settings.emotion = "excited"
            new_settings.pitch += 15
            new_settings.rate += 30
        
        return new_settings
    
    def _preprocess_text(self, text: str, settings: SpeechSettings) -> str:
        """Preprocess text for better speech synthesis."""
        # Apply pronunciation rules
        processed = self._apply_pronunciation_rules(text)
        
        # Add prosody markup
        processed = self._add_prosody_markup(processed, settings)
        
        # Clean up extra whitespace
        processed = re.sub(r'\s+', ' ', processed).strip()
        
        return processed
    
    def _speak_with_coqui(self, text: str, settings: SpeechSettings) -> bool:
        """Synthesize speech using Coqui TTS."""
        try:
            # Generate audio
            self.coqui_tts.tts_to_file(
                text=text,
                file_path=str(self.audio_output_path),
                speed=settings.speed
            )
            
            # Play audio
            if PYGAME_AVAILABLE:
                pygame.mixer.music.load(str(self.audio_output_path))
                pygame.mixer.music.set_volume(settings.volume)
                pygame.mixer.music.play()
                
                # Wait for playback to complete
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                
                return True
            else:
                self.logger.warning("Pygame not available for audio playback")
                return False
                
        except Exception as e:
            self.logger.error(f"Error with Coqui TTS: {e}")
            return False
    
    def _speak_with_pyttsx3(self, text: str, settings: SpeechSettings, blocking: bool) -> bool:
        """Synthesize speech using pyttsx3."""
        try:
            # Apply settings
            self.pyttsx3_engine.setProperty('rate', settings.rate)
            self.pyttsx3_engine.setProperty('volume', settings.volume)
            
            # Remove SSML markup (pyttsx3 doesn't support it)
            clean_text = re.sub(r'<[^>]+>', '', text)
            
            # Speak
            self.pyttsx3_engine.say(clean_text)
            
            if blocking:
                self.pyttsx3_engine.runAndWait()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error with pyttsx3: {e}")
            return False
    
    def get_available_voices(self) -> List[Dict[str, str]]:
        """Get list of available voices."""
        voices = []
        
        try:
            if self.pyttsx3_engine:
                pyttsx3_voices = self.pyttsx3_engine.getProperty('voices')
                for voice in pyttsx3_voices:
                    voices.append({
                        'id': voice.id,
                        'name': voice.name,
                        'engine': 'pyttsx3',
                        'gender': 'female' if 'female' in voice.name.lower() else 'male'
                    })
            
            if self.coqui_tts:
                # Coqui voices depend on the model
                voices.append({
                    'id': 'coqui_default',
                    'name': 'Coqui Neural Voice',
                    'engine': 'coqui',
                    'gender': 'female'
                })
                
        except Exception as e:
            self.logger.error(f"Error getting available voices: {e}")
        
        return voices
    
    def set_voice(self, voice_id: str) -> bool:
        """
        Set the active voice.
        
        Args:
            voice_id: Voice identifier
            
        Returns:
            True if voice was set successfully
        """
        try:
            if self.pyttsx3_engine and voice_id != 'coqui_default':
                self.pyttsx3_engine.setProperty('voice', voice_id)
                self.logger.info(f"Voice set to: {voice_id}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error setting voice: {e}")
            return False
    
    def test_pronunciation(self, test_phrases: Optional[List[str]] = None) -> None:
        """Test pronunciation of key phrases."""
        if not test_phrases:
            test_phrases = [
                "Hello, I am G.H.O.S.T., your AI assistant.",
                "Good morning, Sir. How may I assist you today?",
                "G.H.O.S.T. systems are online and ready.",
                "At your service, Sir. All systems operational.",
                "Processing your request now, Sir."
            ]
        
        print("\n🎤 Testing G.H.O.S.T. Pronunciation")
        print("=" * 35)
        
        for i, phrase in enumerate(test_phrases, 1):
            print(f"\n{i}. Testing: {phrase}")
            input("Press Enter to hear pronunciation...")
            
            success = self.speak(phrase, style="friendly")
            if not success:
                print("❌ Speech synthesis failed")
            else:
                print("✅ Pronunciation test completed")
    
    def get_engine_status(self) -> Dict[str, Any]:
        """Get current engine status."""
        return {
            'current_engine': self.current_engine,
            'coqui_available': self.coqui_tts is not None,
            'pyttsx3_available': self.pyttsx3_engine is not None,
            'pygame_available': PYGAME_AVAILABLE,
            'fallback_enabled': self.use_fallback,
            'default_settings': {
                'rate': self.default_settings.rate,
                'volume': self.default_settings.volume,
                'pitch': self.default_settings.pitch,
                'emotion': self.default_settings.emotion
            }
        }
    
    def cleanup(self) -> None:
        """Clean up TTS resources."""
        try:
            if self.pyttsx3_engine:
                self.pyttsx3_engine.stop()
            
            if PYGAME_AVAILABLE:
                pygame.mixer.quit()
            
            # Clean up temporary files
            if self.audio_output_path.exists():
                self.audio_output_path.unlink()
            
            self.logger.info("TTS cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during TTS cleanup: {e}")


class TTSManager:
    """Manager for TTS system with personality integration."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize TTS manager.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize TTS engine
        self.tts = EnhancedTTS(config.get('tts', {}))
        
        # Personality integration
        self.personality_mode = config.get('personality_mode', 'jarvis')
        
    def speak_with_personality(self, text: str, emotion: str = "neutral", 
                             is_owner: bool = True, blocking: bool = True) -> bool:
        """
        Speak text with personality-appropriate style.
        
        Args:
            text: Text to speak
            emotion: Emotional tone
            is_owner: Whether speaking to the owner
            blocking: Whether to wait for completion
            
        Returns:
            True if successful
        """
        # Determine style based on personality and context
        if self.personality_mode == 'jarvis' and is_owner:
            if emotion == "greeting":
                style = "friendly"
            elif emotion == "confirmation":
                style = "calm"
            elif emotion == "error":
                style = "serious"
            else:
                style = "normal"
        else:
            # Generic style for unknown users
            style = "friendly" if emotion == "greeting" else "normal"
        
        return self.tts.speak(text, style=style, blocking=blocking)
    
    def get_status(self) -> Dict[str, Any]:
        """Get TTS manager status."""
        return {
            'tts_engine': self.tts.get_engine_status(),
            'personality_mode': self.personality_mode
        }


# Fallback implementation when TTS libraries are not available
class DummyTTS:
    """Dummy TTS for when libraries are not available."""
    
    def __init__(self, config: Dict[str, Any]):
        self.logger = logging.getLogger(__name__)
        self.logger.warning("Using dummy TTS (libraries not available)")
    
    def speak(self, text: str, settings=None, style: str = "normal", blocking: bool = True) -> bool:
        print(f"🔊 G.H.O.S.T.: {text}")
        return True
    
    def get_available_voices(self) -> List[Dict[str, str]]:
        return []
    
    def set_voice(self, voice_id: str) -> bool:
        return False
    
    def test_pronunciation(self, test_phrases=None) -> None:
        print("TTS not available - using text output")
    
    def get_engine_status(self) -> Dict[str, Any]:
        return {'current_engine': 'dummy', 'available': False}
    
    def cleanup(self) -> None:
        pass


def create_tts_system(config: Dict[str, Any]) -> EnhancedTTS:
    """
    Create appropriate TTS system based on availability.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        EnhancedTTS or DummyTTS instance
    """
    if COQUI_AVAILABLE or PYTTSX3_AVAILABLE:
        return EnhancedTTS(config)
    else:
        return DummyTTS(config)
