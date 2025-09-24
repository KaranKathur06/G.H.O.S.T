"""
Speech-to-Text module for G.H.O.S.T. Virtual Assistant.

This module handles converting voice input to text using VOSK offline STT engine.
Includes wake word detection and continuous listening capabilities.
"""

import json
import logging
import threading
import time
import queue
from typing import Dict, Any, Optional, Callable, List
import pyaudio
import vosk
try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False
    sr = None


class SpeechToText:
    """
    Offline Speech-to-Text handler using VOSK.
    
    Provides wake word detection and continuous listening capabilities
    for natural voice interaction with G.H.O.S.T.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Speech-to-Text system with optimized performance.
        
        Args:
            config: Configuration dictionary for STT settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Engine selection - prefer SpeechRecognition for better performance
        self.use_sr = config.get('use_speech_recognition', True) and SR_AVAILABLE
        self.use_vosk = config.get('use_vosk', False) or not SR_AVAILABLE
        
        # VOSK configuration (fallback)
        self.model_path = config.get('model_path', 'models/vosk-model-small-en-us-0.15')
        self.sample_rate = config.get('sample_rate', 16000)
        self.channels = config.get('channels', 1)
        self.chunk_size = config.get('chunk_size', 1024)  # Reduced for better performance
        
        # Wake word configuration
        self.wake_words = [word.lower() for word in config.get('wake_words', ['ghost'])]
        self.wake_word_threshold = config.get('wake_word_threshold', 0.6)  # Lower threshold
        
        # Audio configuration - optimized for performance
        self.energy_threshold = config.get('energy_threshold', 200)  # Lower threshold
        self.pause_threshold = config.get('pause_threshold', 0.5)  # Shorter pause
        self.device_index = config.get('device_index', None)
        
        # Recognition state
        self.is_listening = False
        self.is_continuous_listening = False
        self.model = None
        self.recognizer = None
        self.audio = None
        self.stream = None
        
        # SpeechRecognition components
        self.sr_recognizer = None
        self.sr_microphone = None
        
        # Threading
        self._listen_thread = None
        self._stop_event = threading.Event()
        self._audio_queue = queue.Queue()
        self._background_listener = None
        
        # Performance optimization
        self._last_recognition_time = 0
        self._recognition_cooldown = 0.5  # Minimum time between recognitions
        
        # Initialize engines
        self._initialize_engines()
    
    def _initialize_engines(self) -> None:
        """Initialize available STT engines."""
        engines_initialized = []
        
        # Try SpeechRecognition first (better performance)
        if self.use_sr and SR_AVAILABLE:
            try:
                self.sr_recognizer = sr.Recognizer()
                self.sr_microphone = sr.Microphone()
                
                # Optimize for performance
                self.sr_recognizer.energy_threshold = self.energy_threshold
                self.sr_recognizer.pause_threshold = self.pause_threshold
                self.sr_recognizer.dynamic_energy_threshold = True
                
                # Quick calibration
                with self.sr_microphone as source:
                    self.sr_recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                engines_initialized.append('SpeechRecognition')
                self.logger.info("SpeechRecognition STT initialized")
                
            except Exception as e:
                self.logger.warning(f"Failed to initialize SpeechRecognition: {e}")
                self.use_sr = False
        
        # Initialize VOSK as fallback
        if self.use_vosk:
            try:
                self._initialize_vosk()
                engines_initialized.append('VOSK')
            except Exception as e:
                self.logger.warning(f"Failed to initialize VOSK: {e}")
                self.use_vosk = False
        
        if not engines_initialized:
            raise RuntimeError("No STT engines could be initialized")
        
        self.logger.info(f"STT engines initialized: {', '.join(engines_initialized)}")
    
    def _initialize_vosk(self) -> None:
        """Initialize VOSK model and recognizer."""
        try:
            # Check if model exists
            from pathlib import Path
            model_path = Path(self.model_path)
            if not model_path.exists():
                self.logger.error(f"VOSK model not found at {self.model_path}")
                self.logger.info("Please download the model using:")
                self.logger.info("wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip")
                self.logger.info("unzip vosk-model-small-en-us-0.15.zip -d models/")
                raise FileNotFoundError(f"VOSK model not found: {self.model_path}")
            
            self.model = vosk.Model(self.model_path)
            self.recognizer = vosk.KaldiRecognizer(self.model, self.sample_rate)
            
            # Initialize PyAudio
            self.audio = pyaudio.PyAudio()
            
            self.logger.info("VOSK STT engine initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize VOSK: {e}")
            raise
    
    def listen(self, timeout: float = 5.0, phrase_timeout: float = 1.0) -> Optional[str]:
        """
        Listen for voice input and return recognized text.
        
        Args:
            timeout: Maximum time to wait for speech
            phrase_timeout: Time to wait after speech ends
            
        Returns:
            Recognized text or None if no speech detected
        """
        if not self.model or not self.recognizer:
            self.logger.error("VOSK not initialized")
            return None
        
        try:
            self.logger.debug(f"Listening for speech (timeout: {timeout}s)")
            
            # Open audio stream
            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=self.device_index,
                frames_per_buffer=self.chunk_size
            )
            
            self.is_listening = True
            start_time = time.time()
            silence_start = None
            audio_data = b""
            
            while self.is_listening and (time.time() - start_time) < timeout:
                try:
                    # Read audio chunk
                    data = stream.read(self.chunk_size, exception_on_overflow=False)
                    audio_data += data
                    
                    # Process with VOSK
                    if self.recognizer.AcceptWaveform(data):
                        result = json.loads(self.recognizer.Result())
                        text = result.get('text', '').strip()
                        
                        if text:
                            self.logger.info(f"Recognized: {text}")
                            stream.stop_stream()
                            stream.close()
                            self.is_listening = False
                            return text
                    
                    # Check for silence (basic implementation)
                    if self._is_silent(data):
                        if silence_start is None:
                            silence_start = time.time()
                        elif time.time() - silence_start > phrase_timeout:
                            # Get partial result
                            partial_result = json.loads(self.recognizer.PartialResult())
                            partial_text = partial_result.get('partial', '').strip()
                            
                            if partial_text:
                                self.logger.info(f"Partial recognition: {partial_text}")
                                stream.stop_stream()
                                stream.close()
                                self.is_listening = False
                                return partial_text
                            break
                    else:
                        silence_start = None
                
                except Exception as e:
                    self.logger.error(f"Error reading audio: {e}")
                    break
            
            # Cleanup
            stream.stop_stream()
            stream.close()
            self.is_listening = False
            
            # Try to get final result
            final_result = json.loads(self.recognizer.FinalResult())
            final_text = final_result.get('text', '').strip()
            
            if final_text:
                self.logger.info(f"Final recognition: {final_text}")
                return final_text
            
            self.logger.debug("No speech recognized")
            return None
            
        except Exception as e:
            self.logger.error(f"Error during speech recognition: {e}")
            return None
    
    def continuous_listen(self, callback: Callable[[str], None], wake_word_only: bool = True) -> None:
        """
        Start optimized continuous listening with callback for recognized speech.
        
        Args:
            callback: Function to call when speech is recognized
            wake_word_only: If True, only trigger callback on wake word detection
        """
        if self.is_continuous_listening:
            self.logger.warning("Continuous listening already active")
            return
        
        self.logger.info("Starting optimized continuous listening mode")
        self.is_continuous_listening = True
        self._stop_event.clear()
        
        # Use SpeechRecognition's background listening if available
        if self.use_sr and self.sr_recognizer and self.sr_microphone:
            self._start_background_listening(callback, wake_word_only)
        else:
            # Fallback to VOSK continuous listening
            self._listen_thread = threading.Thread(
                target=self._continuous_listen_loop,
                args=(callback, wake_word_only),
                daemon=True
            )
            self._listen_thread.start()
    
    def _start_background_listening(self, callback: Callable[[str], None], wake_word_only: bool) -> None:
        """
        Start background listening using SpeechRecognition (non-blocking, efficient).
        
        Args:
            callback: Function to call when speech is recognized
            wake_word_only: If True, only trigger callback on wake word detection
        """
        def audio_callback(recognizer, audio):
            """Process audio in background thread."""
            try:
                # Check cooldown to prevent excessive processing
                current_time = time.time()
                if current_time - self._last_recognition_time < self._recognition_cooldown:
                    return
                
                # Recognize speech
                text = recognizer.recognize_google(audio, language='en-US')
                text = text.lower().strip()
                
                if text:
                    self._last_recognition_time = current_time
                    
                    if wake_word_only:
                        # Check for wake words
                        if self._contains_wake_word(text):
                            self.logger.info(f"Wake word detected: {text}")
                            callback(text)
                    else:
                        # Call callback for any recognized text
                        callback(text)
                        
            except sr.UnknownValueError:
                # No speech detected - normal, don't log
                pass
            except sr.RequestError as e:
                self.logger.warning(f"Speech recognition service error: {e}")
            except Exception as e:
                self.logger.error(f"Error in background audio callback: {e}")
        
        try:
            # Start background listening
            self._background_listener = self.sr_recognizer.listen_in_background(
                self.sr_microphone, 
                audio_callback,
                phrase_time_limit=5
            )
            self.logger.info("Background listening started with SpeechRecognition")
            
        except Exception as e:
            self.logger.error(f"Failed to start background listening: {e}")
            # Fallback to VOSK
            self._listen_thread = threading.Thread(
                target=self._continuous_listen_loop,
                args=(callback, wake_word_only),
                daemon=True
            )
            self._listen_thread.start()
    
    def stop_continuous_listen(self) -> None:
        """Stop continuous listening."""
        if not self.is_continuous_listening:
            return
        
        self.logger.info("Stopping continuous listening")
        self.is_continuous_listening = False
        self._stop_event.set()
        
        # Stop background listener if active
        if self._background_listener:
            try:
                self._background_listener(wait_for_stop=False)
                self._background_listener = None
                self.logger.info("Background listener stopped")
            except Exception as e:
                self.logger.error(f"Error stopping background listener: {e}")
        
        # Stop thread-based listening
        if self._listen_thread and self._listen_thread.is_alive():
            self._listen_thread.join(timeout=2.0)
    
    def _continuous_listen_loop(self, callback: Callable[[str], None], wake_word_only: bool) -> None:
        """Main loop for continuous listening."""
        try:
            # Open audio stream
            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=self.device_index,
                frames_per_buffer=self.chunk_size
            )
            
            self.logger.debug("Continuous listening loop started")
            
            while not self._stop_event.is_set():
                try:
                    # Read audio chunk
                    data = stream.read(self.chunk_size, exception_on_overflow=False)
                    
                    # Process with VOSK
                    if self.recognizer.AcceptWaveform(data):
                        result = json.loads(self.recognizer.Result())
                        text = result.get('text', '').strip().lower()
                        
                        if text:
                            self.logger.debug(f"Continuous recognition: {text}")
                            
                            if wake_word_only:
                                # Check for wake words
                                if self._contains_wake_word(text):
                                    self.logger.info(f"Wake word detected: {text}")
                                    callback(text)
                            else:
                                # Call callback for any recognized text
                                callback(text)
                    
                    # Optimized delay to prevent excessive CPU usage
                    time.sleep(0.05)  # Increased from 0.01 to reduce CPU load
                
                except Exception as e:
                    self.logger.error(f"Error in continuous listening: {e}")
                    time.sleep(0.1)
            
            # Cleanup
            stream.stop_stream()
            stream.close()
            
        except Exception as e:
            self.logger.error(f"Fatal error in continuous listening: {e}")
        finally:
            self.logger.debug("Continuous listening loop ended")
    
    def _contains_wake_word(self, text: str) -> bool:
        """
        Check if text contains any wake words.
        
        Args:
            text: Recognized text to check
            
        Returns:
            True if wake word found, False otherwise
        """
        text_lower = text.lower()
        
        for wake_word in self.wake_words:
            if wake_word in text_lower:
                # Additional confidence check could be added here
                return True
        
        return False
    
    def _is_silent(self, audio_data: bytes) -> bool:
        """
        Check if audio data represents silence.
        
        Args:
            audio_data: Raw audio data
            
        Returns:
            True if audio is considered silent
        """
        # Simple silence detection based on audio amplitude
        import struct
        
        # Convert bytes to integers
        audio_ints = struct.unpack(f'{len(audio_data)//2}h', audio_data)
        
        # Calculate RMS (Root Mean Square)
        rms = (sum(x*x for x in audio_ints) / len(audio_ints)) ** 0.5
        
        return rms < self.energy_threshold
    
    def calibrate_microphone(self, duration: float = 2.0) -> None:
        """
        Calibrate microphone for ambient noise.
        
        Args:
            duration: Duration to sample ambient noise
        """
        try:
            self.logger.info(f"Calibrating microphone for {duration} seconds...")
            self.logger.info("Please remain quiet during calibration...")
            
            # Open audio stream
            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=self.device_index,
                frames_per_buffer=self.chunk_size
            )
            
            # Collect ambient noise samples
            noise_samples = []
            start_time = time.time()
            
            while time.time() - start_time < duration:
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                
                # Calculate RMS for this chunk
                import struct
                audio_ints = struct.unpack(f'{len(data)//2}h', data)
                rms = (sum(x*x for x in audio_ints) / len(audio_ints)) ** 0.5
                noise_samples.append(rms)
            
            # Calculate average noise level and set threshold
            avg_noise = sum(noise_samples) / len(noise_samples)
            self.energy_threshold = avg_noise * 1.5  # Set threshold above ambient noise
            
            stream.stop_stream()
            stream.close()
            
            self.logger.info(f"Calibration completed. Energy threshold set to {self.energy_threshold:.2f}")
            
        except Exception as e:
            self.logger.error(f"Error during microphone calibration: {e}")
    
    def get_microphone_info(self) -> Dict[str, Any]:
        """
        Get information about available microphones.
        
        Returns:
            Dictionary with microphone information
        """
        try:
            devices = []
            
            for i in range(self.audio.get_device_count()):
                device_info = self.audio.get_device_info_by_index(i)
                if device_info['maxInputChannels'] > 0:  # Input device
                    devices.append({
                        'index': i,
                        'name': device_info['name'],
                        'channels': device_info['maxInputChannels'],
                        'sample_rate': device_info['defaultSampleRate']
                    })
            
            return {
                'default_device': self.audio.get_default_input_device_info(),
                'available_devices': devices,
                'current_threshold': self.energy_threshold,
                'wake_words': self.wake_words
            }
            
        except Exception as e:
            self.logger.error(f"Error getting microphone info: {e}")
            return {}
    
    def test_microphone(self) -> bool:
        """
        Test if microphone is working.
        
        Returns:
            True if microphone is working, False otherwise
        """
        try:
            self.logger.info("Testing microphone... Please say something.")
            
            # Try to capture a short audio sample
            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=self.device_index,
                frames_per_buffer=self.chunk_size
            )
            
            # Record for 2 seconds
            test_duration = 2.0
            start_time = time.time()
            audio_detected = False
            
            while time.time() - start_time < test_duration:
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                
                if not self._is_silent(data):
                    audio_detected = True
                    break
            
            stream.stop_stream()
            stream.close()
            
            if audio_detected:
                self.logger.info("Microphone test successful - audio detected")
                return True
            else:
                self.logger.warning("Microphone test - no audio detected")
                return False
            
        except Exception as e:
            self.logger.error(f"Microphone test failed: {e}")
            return False
    
    def set_language(self, language: str) -> None:
        """
        Set the recognition language.
        
        Args:
            language: Language code (e.g., 'en-US', 'es-ES')
        """
        self.language = language
        self.logger.info(f"Recognition language set to {language}")
    
    def cleanup(self) -> None:
        """Clean up STT resources."""
        try:
            self.logger.info("Cleaning up STT resources")
            
            # Stop continuous listening
            self.stop_continuous_listen()
            
            # Stop regular listening
            self.is_listening = False
            
            # Cleanup PyAudio
            if self.audio:
                self.audio.terminate()
            
            self.logger.info("STT cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during STT cleanup: {e}")
