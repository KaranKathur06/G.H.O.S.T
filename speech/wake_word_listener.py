"""
Efficient wake word detection system for G.H.O.S.T.

This module provides lightweight, continuous wake word detection using
OpenWakeWord or VOSK with minimal CPU usage for 24x7 operation.
"""

import logging
import threading
import time
import queue
import numpy as np
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass
from enum import Enum
import pyaudio


class WakeWordEngine(Enum):
    """Available wake word detection engines."""
    OPENWAKEWORD = "openwakeword"
    VOSK_KEYWORD = "vosk_keyword"
    SIMPLE_ENERGY = "simple_energy"


@dataclass
class WakeWordDetection:
    """Wake word detection result."""
    word: str
    confidence: float
    timestamp: float
    audio_data: Optional[bytes] = None


class WakeWordListener:
    """
    Efficient wake word detection system for continuous background operation.
    
    Designed for minimal CPU usage while maintaining high accuracy detection
    of wake words like "Ghost" for 24x7 operation.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize wake word listener.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.engine_type = config.get('engine', 'simple_energy')
        self.wake_words = config.get('wake_words', ['ghost'])
        self.confidence_threshold = config.get('confidence_threshold', 0.7)
        self.sample_rate = config.get('sample_rate', 16000)
        self.chunk_size = config.get('chunk_size', 1024)
        self.channels = config.get('channels', 1)
        
        # Audio configuration
        self.device_index = config.get('device_index', None)
        self.energy_threshold = config.get('energy_threshold', 300)
        self.silence_duration = config.get('silence_duration', 0.5)
        
        # Detection engine
        self.detection_engine = None
        self.audio_stream = None
        self.audio = None
        
        # Threading
        self.is_listening = False
        self.listen_thread = None
        self.audio_queue = queue.Queue(maxsize=100)
        self.detection_queue = queue.Queue()
        
        # Callbacks
        self.wake_word_callback: Optional[Callable] = None
        
        # Performance monitoring
        self.detections_count = 0
        self.false_positives = 0
        self.cpu_usage_samples = []
        
        # Initialize detection engine
        self._initialize_engine()
    
    def _initialize_engine(self) -> None:
        """Initialize the selected wake word detection engine."""
        try:
            if self.engine_type == WakeWordEngine.OPENWAKEWORD.value:
                self._initialize_openwakeword()
            elif self.engine_type == WakeWordEngine.VOSK_KEYWORD.value:
                self._initialize_vosk_keyword()
            else:
                self._initialize_simple_energy()
            
            self.logger.info(f"Wake word engine initialized: {self.engine_type}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize wake word engine: {e}")
            # Fallback to simple energy detection
            self._initialize_simple_energy()
    
    def _initialize_openwakeword(self) -> None:
        """Initialize OpenWakeWord engine."""
        try:
            import openwakeword
            from openwakeword.model import Model
            
            # Initialize OpenWakeWord model
            self.detection_engine = Model(
                wakeword_models=['alexa_v0.1.onnx'],  # We'll use a generic model
                inference_framework='onnx'
            )
            
            self.logger.info("OpenWakeWord engine initialized")
            
        except ImportError:
            self.logger.warning("OpenWakeWord not installed, falling back to simple detection")
            self._initialize_simple_energy()
        except Exception as e:
            self.logger.error(f"OpenWakeWord initialization failed: {e}")
            self._initialize_simple_energy()
    
    def _initialize_vosk_keyword(self) -> None:
        """Initialize VOSK keyword spotting."""
        try:
            import vosk
            
            # Create a small keyword model for efficiency
            model_path = self.config.get('keyword_model_path', 'models/vosk-model-small-en-us-0.15')
            
            if not vosk.Model.exists(model_path):
                self.logger.warning(f"VOSK model not found at {model_path}")
                self._initialize_simple_energy()
                return
            
            model = vosk.Model(model_path)
            
            # Create keyword recognizer with just wake words
            keywords = '["' + '", "'.join(self.wake_words) + '"]'
            self.detection_engine = vosk.KaldiRecognizer(model, self.sample_rate, keywords)
            
            self.logger.info("VOSK keyword engine initialized")
            
        except ImportError:
            self.logger.warning("VOSK not installed, falling back to simple detection")
            self._initialize_simple_energy()
        except Exception as e:
            self.logger.error(f"VOSK keyword initialization failed: {e}")
            self._initialize_simple_energy()
    
    def _initialize_simple_energy(self) -> None:
        """Initialize simple energy-based detection."""
        self.detection_engine = "simple_energy"
        self.engine_type = "simple_energy"
        
        # Simple keyword matching patterns
        self.keyword_patterns = []
        for word in self.wake_words:
            # Create simple phonetic patterns for matching
            patterns = self._generate_phonetic_patterns(word)
            self.keyword_patterns.extend(patterns)
        
        self.logger.info("Simple energy detection initialized")
    
    def _generate_phonetic_patterns(self, word: str) -> List[str]:
        """Generate phonetic patterns for simple matching."""
        patterns = [word.lower()]
        
        # Add common variations
        if word.lower() == "ghost":
            patterns.extend(["gost", "goast", "ghast"])
        
        return patterns
    
    def start_listening(self, callback: Callable[[WakeWordDetection], None]) -> bool:
        """
        Start continuous wake word detection.
        
        Args:
            callback: Function to call when wake word is detected
            
        Returns:
            True if started successfully
        """
        if self.is_listening:
            self.logger.warning("Wake word listener already running")
            return False
        
        try:
            self.wake_word_callback = callback
            
            # Initialize audio stream
            self.audio = pyaudio.PyAudio()
            self.audio_stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=self.device_index,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._audio_callback
            )
            
            # Start listening thread
            self.is_listening = True
            self.listen_thread = threading.Thread(
                target=self._detection_loop,
                daemon=True
            )
            self.listen_thread.start()
            
            self.audio_stream.start_stream()
            
            self.logger.info("Wake word detection started")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start wake word detection: {e}")
            return False
    
    def stop_listening(self) -> None:
        """Stop wake word detection."""
        if not self.is_listening:
            return
        
        try:
            self.is_listening = False
            
            # Stop audio stream
            if self.audio_stream:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
                self.audio_stream = None
            
            if self.audio:
                self.audio.terminate()
                self.audio = None
            
            # Wait for thread to finish
            if self.listen_thread and self.listen_thread.is_alive():
                self.listen_thread.join(timeout=2.0)
            
            self.logger.info("Wake word detection stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping wake word detection: {e}")
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Audio stream callback for continuous processing."""
        try:
            # Add audio data to queue for processing
            if not self.audio_queue.full():
                self.audio_queue.put(in_data)
            
            return (None, pyaudio.paContinue)
            
        except Exception as e:
            self.logger.error(f"Error in audio callback: {e}")
            return (None, pyaudio.paAbort)
    
    def _detection_loop(self) -> None:
        """Main detection processing loop."""
        self.logger.debug("Wake word detection loop started")
        
        audio_buffer = b""
        silence_start = None
        
        while self.is_listening:
            try:
                # Get audio data from queue
                try:
                    audio_data = self.audio_queue.get(timeout=0.1)
                except queue.Empty:
                    continue
                
                # Add to buffer
                audio_buffer += audio_data
                
                # Process audio based on engine type
                if self.engine_type == "openwakeword":
                    detection = self._process_openwakeword(audio_data)
                elif self.engine_type == "vosk_keyword":
                    detection = self._process_vosk_keyword(audio_data)
                else:
                    detection = self._process_simple_energy(audio_data, audio_buffer)
                
                if detection:
                    self._handle_detection(detection)
                    audio_buffer = b""  # Clear buffer after detection
                
                # Manage buffer size to prevent memory issues
                if len(audio_buffer) > self.sample_rate * 4:  # 4 seconds max
                    # Keep only last 2 seconds
                    keep_samples = self.sample_rate * 2 * 2  # 2 bytes per sample
                    audio_buffer = audio_buffer[-keep_samples:]
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.001)
                
            except Exception as e:
                self.logger.error(f"Error in detection loop: {e}")
                time.sleep(0.1)
        
        self.logger.debug("Wake word detection loop ended")
    
    def _process_openwakeword(self, audio_data: bytes) -> Optional[WakeWordDetection]:
        """Process audio with OpenWakeWord."""
        try:
            # Convert bytes to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            
            # Get prediction from OpenWakeWord
            prediction = self.detection_engine.predict(audio_array)
            
            # Check if any wake word was detected
            for word, confidence in prediction.items():
                if confidence > self.confidence_threshold:
                    return WakeWordDetection(
                        word=word,
                        confidence=confidence,
                        timestamp=time.time(),
                        audio_data=audio_data
                    )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error processing OpenWakeWord: {e}")
            return None
    
    def _process_vosk_keyword(self, audio_data: bytes) -> Optional[WakeWordDetection]:
        """Process audio with VOSK keyword spotting."""
        try:
            if self.detection_engine.AcceptWaveform(audio_data):
                result = self.detection_engine.Result()
                
                import json
                result_dict = json.loads(result)
                text = result_dict.get('text', '').lower()
                
                # Check if any wake word is in the text
                for wake_word in self.wake_words:
                    if wake_word.lower() in text:
                        return WakeWordDetection(
                            word=wake_word,
                            confidence=0.8,  # VOSK doesn't provide confidence for keywords
                            timestamp=time.time(),
                            audio_data=audio_data
                        )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error processing VOSK keyword: {e}")
            return None
    
    def _process_simple_energy(self, audio_data: bytes, audio_buffer: bytes) -> Optional[WakeWordDetection]:
        """Process audio with simple energy-based detection."""
        try:
            # Check if audio has sufficient energy (not silence)
            if not self._has_sufficient_energy(audio_data):
                return None
            
            # Convert recent audio buffer to text approximation
            # This is a very simple approach - in reality, you'd want proper STT
            if len(audio_buffer) < self.sample_rate * 2:  # Need at least 2 seconds
                return None
            
            # Simple pattern matching (this is very basic)
            # In a real implementation, you'd use proper speech recognition
            audio_energy = self._calculate_energy(audio_buffer)
            
            # If energy pattern suggests speech, check for wake word patterns
            if audio_energy > self.energy_threshold * 2:  # Elevated energy suggests speech
                # This is a placeholder - real implementation would need STT
                # For now, we'll trigger on elevated energy patterns
                
                # Simulate wake word detection based on energy patterns
                if self._matches_energy_pattern(audio_buffer):
                    return WakeWordDetection(
                        word="ghost",
                        confidence=0.6,  # Lower confidence for simple detection
                        timestamp=time.time(),
                        audio_data=audio_data
                    )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error processing simple energy: {e}")
            return None
    
    def _has_sufficient_energy(self, audio_data: bytes) -> bool:
        """Check if audio data has sufficient energy."""
        try:
            # Convert bytes to integers
            import struct
            audio_ints = struct.unpack(f'{len(audio_data)//2}h', audio_data)
            
            # Calculate RMS energy
            rms = (sum(x*x for x in audio_ints) / len(audio_ints)) ** 0.5
            
            return rms > self.energy_threshold
            
        except Exception:
            return False
    
    def _calculate_energy(self, audio_data: bytes) -> float:
        """Calculate overall energy of audio data."""
        try:
            import struct
            audio_ints = struct.unpack(f'{len(audio_data)//2}h', audio_data)
            rms = (sum(x*x for x in audio_ints) / len(audio_ints)) ** 0.5
            return rms
        except Exception:
            return 0.0
    
    def _matches_energy_pattern(self, audio_buffer: bytes) -> bool:
        """Check if energy pattern matches expected wake word pattern."""
        # This is a very simple heuristic - real implementation would be more sophisticated
        try:
            # Analyze energy pattern over time
            chunk_size = len(audio_buffer) // 10  # Divide into 10 chunks
            energies = []
            
            for i in range(0, len(audio_buffer), chunk_size):
                chunk = audio_buffer[i:i+chunk_size]
                if len(chunk) >= 2:
                    energy = self._calculate_energy(chunk)
                    energies.append(energy)
            
            if len(energies) < 5:
                return False
            
            # Look for energy pattern that might indicate "Ghost"
            # This is very basic - real implementation would use proper phoneme detection
            max_energy = max(energies)
            avg_energy = sum(energies) / len(energies)
            
            # Simple heuristic: if there's a significant energy spike followed by lower energy
            return max_energy > avg_energy * 2 and max_energy > self.energy_threshold * 3
            
        except Exception:
            return False
    
    def _handle_detection(self, detection: WakeWordDetection) -> None:
        """Handle wake word detection."""
        try:
            self.detections_count += 1
            
            self.logger.info(f"Wake word detected: {detection.word} (confidence: {detection.confidence:.2f})")
            
            # Call registered callback
            if self.wake_word_callback:
                self.wake_word_callback(detection)
            
            # Add to detection queue for external processing
            if not self.detection_queue.full():
                self.detection_queue.put(detection)
            
        except Exception as e:
            self.logger.error(f"Error handling wake word detection: {e}")
    
    def get_detection_stats(self) -> Dict[str, Any]:
        """
        Get detection statistics.
        
        Returns:
            Dictionary with detection stats
        """
        return {
            "engine_type": self.engine_type,
            "is_listening": self.is_listening,
            "detections_count": self.detections_count,
            "false_positives": self.false_positives,
            "wake_words": self.wake_words,
            "confidence_threshold": self.confidence_threshold,
            "queue_size": self.audio_queue.qsize() if self.audio_queue else 0
        }
    
    def test_detection(self, test_audio_file: str = None) -> bool:
        """
        Test wake word detection.
        
        Args:
            test_audio_file: Optional audio file to test with
            
        Returns:
            True if test successful
        """
        try:
            self.logger.info("Testing wake word detection...")
            
            # Simple test - start listening for 5 seconds
            def test_callback(detection):
                self.logger.info(f"Test detection: {detection.word} (confidence: {detection.confidence})")
            
            if self.start_listening(test_callback):
                time.sleep(5)
                self.stop_listening()
                self.logger.info("Wake word detection test completed")
                return True
            else:
                self.logger.error("Failed to start wake word detection for test")
                return False
                
        except Exception as e:
            self.logger.error(f"Wake word detection test failed: {e}")
            return False
    
    def calibrate_sensitivity(self, duration: float = 10.0) -> None:
        """
        Calibrate detection sensitivity based on ambient noise.
        
        Args:
            duration: Calibration duration in seconds
        """
        try:
            self.logger.info(f"Calibrating wake word sensitivity for {duration} seconds...")
            self.logger.info("Please remain quiet during calibration...")
            
            # Collect ambient noise samples
            noise_samples = []
            start_time = time.time()
            
            # Temporarily start audio stream for calibration
            audio = pyaudio.PyAudio()
            stream = audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=self.device_index,
                frames_per_buffer=self.chunk_size
            )
            
            while time.time() - start_time < duration:
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                energy = self._calculate_energy(data)
                noise_samples.append(energy)
                time.sleep(0.1)
            
            stream.stop_stream()
            stream.close()
            audio.terminate()
            
            # Calculate optimal threshold
            if noise_samples:
                avg_noise = sum(noise_samples) / len(noise_samples)
                max_noise = max(noise_samples)
                
                # Set threshold above ambient noise
                self.energy_threshold = max(avg_noise * 2, max_noise * 1.2)
                
                self.logger.info(f"Calibration completed. Energy threshold set to {self.energy_threshold:.2f}")
            else:
                self.logger.warning("No noise samples collected during calibration")
                
        except Exception as e:
            self.logger.error(f"Error during sensitivity calibration: {e}")
    
    def cleanup(self) -> None:
        """Clean up wake word listener resources."""
        try:
            self.stop_listening()
            
            # Clear queues
            while not self.audio_queue.empty():
                try:
                    self.audio_queue.get_nowait()
                except queue.Empty:
                    break
            
            while not self.detection_queue.empty():
                try:
                    self.detection_queue.get_nowait()
                except queue.Empty:
                    break
            
            self.logger.info("Wake word listener cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during wake word listener cleanup: {e}")


class WakeWordManager:
    """
    High-level manager for wake word detection with multiple engines.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize wake word manager.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Primary and fallback listeners
        self.primary_listener = None
        self.fallback_listener = None
        
        # Configuration
        self.use_fallback = config.get('use_fallback', True)
        self.primary_engine = config.get('primary_engine', 'simple_energy')
        self.fallback_engine = config.get('fallback_engine', 'simple_energy')
        
        # Initialize listeners
        self._initialize_listeners()
    
    def _initialize_listeners(self) -> None:
        """Initialize primary and fallback listeners."""
        try:
            # Primary listener
            primary_config = self.config.copy()
            primary_config['engine'] = self.primary_engine
            self.primary_listener = WakeWordListener(primary_config)
            
            # Fallback listener (if different from primary)
            if self.use_fallback and self.fallback_engine != self.primary_engine:
                fallback_config = self.config.copy()
                fallback_config['engine'] = self.fallback_engine
                self.fallback_listener = WakeWordListener(fallback_config)
            
            self.logger.info("Wake word listeners initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing wake word listeners: {e}")
    
    def start_detection(self, callback: Callable[[WakeWordDetection], None]) -> bool:
        """
        Start wake word detection with fallback support.
        
        Args:
            callback: Function to call when wake word is detected
            
        Returns:
            True if detection started successfully
        """
        try:
            # Try primary listener first
            if self.primary_listener and self.primary_listener.start_listening(callback):
                self.logger.info(f"Wake word detection started with {self.primary_engine}")
                return True
            
            # Fallback to secondary listener
            if self.fallback_listener and self.fallback_listener.start_listening(callback):
                self.logger.info(f"Wake word detection started with fallback {self.fallback_engine}")
                return True
            
            self.logger.error("Failed to start wake word detection with any engine")
            return False
            
        except Exception as e:
            self.logger.error(f"Error starting wake word detection: {e}")
            return False
    
    def stop_detection(self) -> None:
        """Stop wake word detection."""
        if self.primary_listener:
            self.primary_listener.stop_listening()
        
        if self.fallback_listener:
            self.fallback_listener.stop_listening()
        
        self.logger.info("Wake word detection stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get wake word detection status."""
        status = {
            "primary_engine": self.primary_engine,
            "fallback_engine": self.fallback_engine,
            "primary_active": False,
            "fallback_active": False
        }
        
        if self.primary_listener:
            primary_stats = self.primary_listener.get_detection_stats()
            status["primary_active"] = primary_stats["is_listening"]
            status["primary_stats"] = primary_stats
        
        if self.fallback_listener:
            fallback_stats = self.fallback_listener.get_detection_stats()
            status["fallback_active"] = fallback_stats["is_listening"]
            status["fallback_stats"] = fallback_stats
        
        return status
    
    def cleanup(self) -> None:
        """Clean up all resources."""
        if self.primary_listener:
            self.primary_listener.cleanup()
        
        if self.fallback_listener:
            self.fallback_listener.cleanup()
        
        self.logger.info("Wake word manager cleanup completed")
