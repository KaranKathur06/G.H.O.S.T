"""
24/7 Autonomous Operation Manager for G.H.O.S.T.

This module manages the continuous 24/7 operation of G.H.O.S.T.,
including wake word detection, performance optimization, and system health monitoring.
"""

import os
import sys
import time
import threading
import asyncio
import logging
import psutil
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import queue
import json

# Speech recognition imports
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    sr = None

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False

SPEECH_AVAILABLE = SPEECH_RECOGNITION_AVAILABLE and PYAUDIO_AVAILABLE

@dataclass
class SystemHealth:
    """System health metrics."""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_status: bool
    microphone_status: bool
    speaker_status: bool
    last_check: datetime = field(default_factory=datetime.now)

@dataclass
class PerformanceMetrics:
    """Performance tracking metrics."""
    total_interactions: int = 0
    successful_interactions: int = 0
    average_response_time: float = 0.0
    wake_word_detections: int = 0
    false_positives: int = 0
    uptime_hours: float = 0.0
    last_reset: datetime = field(default_factory=datetime.now)

class AutonomousManager:
    """
    24/7 Autonomous Operation Manager for G.H.O.S.T.
    
    Manages:
    - Continuous wake word detection
    - System health monitoring
    - Performance optimization
    - Resource management
    - Error recovery
    - Automatic restarts and maintenance
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize Autonomous Manager."""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Core components (will be injected)
        self.nlu_engine = None
        self.decision_engine = None
        self.action_engine = None
        self.llm_brain = None
        self.system_indexer = None
        
        # Operation state
        self.is_running = False
        self.is_listening = False
        self.is_processing = False
        
        # Speech recognition
        self.recognizer = None
        self.microphone = None
        self.wake_words = self.config.get('wake_words', ['ghost', 'hey ghost'])
        self.wake_word_threshold = self.config.get('wake_word_threshold', 0.7)
        
        # Performance monitoring
        self.performance_metrics = PerformanceMetrics()
        self.system_health = SystemHealth(0, 0, 0, False, False, False)
        
        # Threading and queues
        self.main_thread = None
        self.health_monitor_thread = None
        self.speech_thread = None
        self.command_queue = queue.Queue()
        self.response_queue = queue.Queue()
        
        # Performance optimization
        self.max_cpu_usage = self.config.get('max_cpu_usage', 80.0)
        self.max_memory_usage = self.config.get('max_memory_usage', 80.0)
        self.health_check_interval = self.config.get('health_check_interval', 30)
        self.optimization_interval = self.config.get('optimization_interval', 300)
        
        # Error recovery
        self.max_consecutive_errors = self.config.get('max_consecutive_errors', 5)
        self.consecutive_errors = 0
        self.last_error_time = None
        
        # Callbacks
        self.on_wake_word_detected = None
        self.on_command_received = None
        self.on_response_ready = None
        self.on_error_occurred = None
        
        # Initialize speech recognition
        if SPEECH_AVAILABLE:
            self._initialize_speech_recognition()
        
        self.logger.info("Autonomous Manager initialized")
    
    def _initialize_speech_recognition(self):
        """Initialize speech recognition components."""
        try:
            self.recognizer = sr.Recognizer()
            
            # Configure recognizer for better performance
            self.recognizer.energy_threshold = self.config.get('energy_threshold', 300)
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.dynamic_energy_adjustment_damping = 0.15
            self.recognizer.dynamic_energy_ratio = 1.5
            self.recognizer.pause_threshold = self.config.get('pause_threshold', 0.8)
            self.recognizer.operation_timeout = None
            self.recognizer.phrase_threshold = 0.3
            self.recognizer.non_speaking_duration = 0.5
            
            # Initialize microphone
            self.microphone = sr.Microphone()
            
            # Calibrate for ambient noise
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            self.system_health.microphone_status = True
            self.logger.info("Speech recognition initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize speech recognition: {e}")
            self.system_health.microphone_status = False
    
    def set_components(self, nlu_engine, decision_engine, action_engine, llm_brain, system_indexer):
        """Set references to core G.H.O.S.T. components."""
        self.nlu_engine = nlu_engine
        self.decision_engine = decision_engine
        self.action_engine = action_engine
        self.llm_brain = llm_brain
        self.system_indexer = system_indexer
        
        self.logger.info("Core components linked to Autonomous Manager")
    
    def set_callbacks(self, on_wake_word=None, on_command=None, on_response=None, on_error=None):
        """Set callback functions for events."""
        self.on_wake_word_detected = on_wake_word
        self.on_command_received = on_command
        self.on_response_ready = on_response
        self.on_error_occurred = on_error
    
    def start_autonomous_operation(self):
        """Start 24/7 autonomous operation."""
        if self.is_running:
            self.logger.warning("Autonomous operation already running")
            return
        
        try:
            self.is_running = True
            self.performance_metrics.last_reset = datetime.now()
            
            # Start main operation thread
            self.main_thread = threading.Thread(target=self._main_operation_loop, daemon=True)
            self.main_thread.start()
            
            # Start health monitoring
            self.health_monitor_thread = threading.Thread(target=self._health_monitoring_loop, daemon=True)
            self.health_monitor_thread.start()
            
            # Start speech recognition if available
            if SPEECH_AVAILABLE and self.system_health.microphone_status:
                self.speech_thread = threading.Thread(target=self._speech_recognition_loop, daemon=True)
                self.speech_thread.start()
                self.is_listening = True
            
            self.logger.info("G.H.O.S.T. 24/7 autonomous operation started")
            
        except Exception as e:
            self.logger.error(f"Failed to start autonomous operation: {e}")
            self.is_running = False
            raise
    
    def stop_autonomous_operation(self):
        """Stop autonomous operation."""
        self.logger.info("Stopping autonomous operation...")
        
        self.is_running = False
        self.is_listening = False
        
        # Wait for threads to finish
        if self.main_thread and self.main_thread.is_alive():
            self.main_thread.join(timeout=5)
        
        if self.health_monitor_thread and self.health_monitor_thread.is_alive():
            self.health_monitor_thread.join(timeout=5)
        
        if self.speech_thread and self.speech_thread.is_alive():
            self.speech_thread.join(timeout=5)
        
        self.logger.info("Autonomous operation stopped")
    
    def _main_operation_loop(self):
        """Main operation loop that processes commands."""
        try:
            while self.is_running:
                try:
                    # Process command queue
                    if not self.command_queue.empty():
                        command = self.command_queue.get_nowait()
                        asyncio.run(self._process_command(command))
                    
                    # Periodic optimization
                    if time.time() % self.optimization_interval < 1:
                        self._optimize_performance()
                    
                    # Brief sleep to prevent high CPU usage
                    time.sleep(0.1)
                    
                except Exception as e:
                    self._handle_error(e, "main_operation_loop")
                    
        except Exception as e:
            self.logger.error(f"Fatal error in main operation loop: {e}")
            self._handle_fatal_error(e)
    
    def _speech_recognition_loop(self):
        """Continuous speech recognition loop for wake word detection."""
        try:
            while self.is_running and self.is_listening:
                try:
                    # Listen for audio
                    with self.microphone as source:
                        # Listen with timeout to allow periodic checks
                        audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    
                    # Process audio in background
                    threading.Thread(
                        target=self._process_audio,
                        args=(audio,),
                        daemon=True
                    ).start()
                    
                except sr.WaitTimeoutError:
                    # Timeout is normal, continue listening
                    continue
                    
                except Exception as e:
                    self._handle_error(e, "speech_recognition_loop")
                    time.sleep(1)  # Brief pause before retrying
                    
        except Exception as e:
            self.logger.error(f"Fatal error in speech recognition loop: {e}")
            self.is_listening = False
    
    def _process_audio(self, audio):
        """Process audio for wake word and command detection."""
        try:
            # Convert speech to text
            text = self.recognizer.recognize_google(audio, language='en-US').lower()
            
            # Check for wake word
            if self._contains_wake_word(text):
                self.performance_metrics.wake_word_detections += 1
                self.logger.info(f"Wake word detected: {text}")
                
                # Trigger wake word callback
                if self.on_wake_word_detected:
                    self.on_wake_word_detected(text)
                
                # Listen for command
                self._listen_for_command()
            
        except sr.UnknownValueError:
            # Speech not recognized - this is normal
            pass
        except sr.RequestError as e:
            self.logger.error(f"Speech recognition service error: {e}")
        except Exception as e:
            self._handle_error(e, "process_audio")
    
    def _contains_wake_word(self, text: str) -> bool:
        """Check if text contains wake word."""
        text_lower = text.lower()
        for wake_word in self.wake_words:
            if wake_word.lower() in text_lower:
                return True
        return False
    
    def _listen_for_command(self):
        """Listen for user command after wake word detection."""
        try:
            with self.microphone as source:
                self.logger.debug("Listening for command...")
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=10)
            
            # Recognize command
            command = self.recognizer.recognize_google(audio, language='en-US')
            
            if command.strip():
                self.logger.info(f"Command received: {command}")
                
                # Add to command queue for processing
                self.command_queue.put({
                    'text': command,
                    'timestamp': datetime.now(),
                    'source': 'voice'
                })
                
                # Trigger command callback
                if self.on_command_received:
                    self.on_command_received(command)
            
        except sr.WaitTimeoutError:
            self.logger.debug("Command listening timeout")
        except sr.UnknownValueError:
            self.logger.debug("Could not understand command")
        except sr.RequestError as e:
            self.logger.error(f"Speech recognition error: {e}")
        except Exception as e:
            self._handle_error(e, "listen_for_command")
    
    async def _process_command(self, command_data: Dict[str, Any]):
        """Process a received command through the G.H.O.S.T. pipeline."""
        try:
            self.is_processing = True
            start_time = time.time()
            
            command_text = command_data['text']
            self.performance_metrics.total_interactions += 1
            
            # Step 1: Natural Language Understanding
            if not self.nlu_engine:
                raise Exception("NLU Engine not available")
            
            nlu_request = self.nlu_engine.understand(command_text)
            
            # Step 2: Search for relevant items if needed
            search_results = []
            if self.system_indexer and nlu_request.target_object:
                search_results = self.system_indexer.search(nlu_request.target_object)
            
            # Step 3: Decision making
            if not self.decision_engine:
                raise Exception("Decision Engine not available")
            
            decision = await self.decision_engine.make_decision(
                nlu_request, search_results, {'source': 'voice'}
            )
            
            # Step 4: Execute action or ask for clarification
            response_text = ""
            
            if decision.requires_user_input:
                response_text = decision.clarification_question
            else:
                if decision.chosen_option and self.action_engine:
                    action_result = await self.action_engine.execute_action(
                        decision.chosen_option.action_type,
                        decision.chosen_option.parameters
                    )
                    response_text = action_result.message
                else:
                    # Use LLM for response
                    if self.llm_brain:
                        llm_response = await self.llm_brain.reason(command_text)
                        response_text = llm_response.content
                    else:
                        response_text = "I understand your request, Sir, but I'm unable to process it at the moment."
            
            # Calculate response time
            response_time = time.time() - start_time
            self.performance_metrics.average_response_time = (
                (self.performance_metrics.average_response_time * (self.performance_metrics.total_interactions - 1) + response_time) /
                self.performance_metrics.total_interactions
            )
            
            # Send response
            response_data = {
                'text': response_text,
                'timestamp': datetime.now(),
                'response_time': response_time,
                'success': True
            }
            
            self.response_queue.put(response_data)
            
            # Trigger response callback
            if self.on_response_ready:
                self.on_response_ready(response_data)
            
            self.performance_metrics.successful_interactions += 1
            self.consecutive_errors = 0
            
        except Exception as e:
            self._handle_error(e, "process_command")
            
            # Send error response
            error_response = {
                'text': "I apologize, Sir, but I encountered an issue processing your request.",
                'timestamp': datetime.now(),
                'response_time': time.time() - start_time if 'start_time' in locals() else 0,
                'success': False,
                'error': str(e)
            }
            
            self.response_queue.put(error_response)
            
            if self.on_response_ready:
                self.on_response_ready(error_response)
        
        finally:
            self.is_processing = False
    
    def _health_monitoring_loop(self):
        """Monitor system health continuously."""
        try:
            while self.is_running:
                try:
                    self._check_system_health()
                    
                    # Check for performance issues
                    if (self.system_health.cpu_usage > self.max_cpu_usage or 
                        self.system_health.memory_usage > self.max_memory_usage):
                        self._handle_performance_issue()
                    
                    time.sleep(self.health_check_interval)
                    
                except Exception as e:
                    self._handle_error(e, "health_monitoring_loop")
                    time.sleep(5)
                    
        except Exception as e:
            self.logger.error(f"Fatal error in health monitoring loop: {e}")
    
    def _check_system_health(self):
        """Check current system health metrics."""
        try:
            # CPU usage
            self.system_health.cpu_usage = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.system_health.memory_usage = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            self.system_health.disk_usage = disk.percent
            
            # Network status (basic check)
            try:
                import socket
                socket.create_connection(("8.8.8.8", 53), timeout=3)
                self.system_health.network_status = True
            except OSError:
                self.system_health.network_status = False
            
            # Update timestamp
            self.system_health.last_check = datetime.now()
            
            # Update uptime
            uptime_delta = datetime.now() - self.performance_metrics.last_reset
            self.performance_metrics.uptime_hours = uptime_delta.total_seconds() / 3600
            
        except Exception as e:
            self.logger.error(f"Error checking system health: {e}")
    
    def _optimize_performance(self):
        """Optimize system performance."""
        try:
            # Clear caches if memory usage is high
            if self.system_health.memory_usage > 70:
                if self.system_indexer:
                    # Clear search cache
                    self.system_indexer.search_cache.clear()
                
                if self.llm_brain:
                    # Trim conversation history
                    if len(self.llm_brain.conversation_context.messages) > 10:
                        self.llm_brain.conversation_context.messages = \
                            self.llm_brain.conversation_context.messages[-10:]
            
            # Garbage collection
            import gc
            gc.collect()
            
            self.logger.debug("Performance optimization completed")
            
        except Exception as e:
            self.logger.error(f"Error during performance optimization: {e}")
    
    def _handle_performance_issue(self):
        """Handle performance issues."""
        self.logger.warning(f"Performance issue detected - CPU: {self.system_health.cpu_usage}%, Memory: {self.system_health.memory_usage}%")
        
        # Immediate optimization
        self._optimize_performance()
        
        # Reduce processing if needed
        if self.system_health.cpu_usage > 90:
            self.logger.warning("High CPU usage - reducing processing frequency")
            time.sleep(2)
    
    def _handle_error(self, error: Exception, context: str):
        """Handle non-fatal errors."""
        self.consecutive_errors += 1
        self.last_error_time = datetime.now()
        
        self.logger.error(f"Error in {context}: {error}")
        
        # Trigger error callback
        if self.on_error_occurred:
            self.on_error_occurred(error, context)
        
        # Check if we need to restart
        if self.consecutive_errors >= self.max_consecutive_errors:
            self.logger.error("Too many consecutive errors - initiating restart")
            self._restart_components()
    
    def _handle_fatal_error(self, error: Exception):
        """Handle fatal errors that require system restart."""
        self.logger.error(f"Fatal error occurred: {error}")
        
        # Trigger error callback
        if self.on_error_occurred:
            self.on_error_occurred(error, "fatal")
        
        # Attempt restart
        self._restart_components()
    
    def _restart_components(self):
        """Restart G.H.O.S.T. components."""
        try:
            self.logger.info("Restarting G.H.O.S.T. components...")
            
            # Reset error counter
            self.consecutive_errors = 0
            
            # Reinitialize speech recognition if needed
            if SPEECH_AVAILABLE and not self.system_health.microphone_status:
                self._initialize_speech_recognition()
            
            # Clear queues
            while not self.command_queue.empty():
                self.command_queue.get_nowait()
            
            while not self.response_queue.empty():
                self.response_queue.get_nowait()
            
            # Reset conversation state
            if self.decision_engine:
                self.decision_engine.reset_conversation()
            
            if self.llm_brain:
                self.llm_brain.reset_conversation()
            
            self.logger.info("Component restart completed")
            
        except Exception as e:
            self.logger.error(f"Error during component restart: {e}")
    
    def add_command_to_queue(self, command_text: str, source: str = "manual"):
        """Add a command to the processing queue."""
        command_data = {
            'text': command_text,
            'timestamp': datetime.now(),
            'source': source
        }
        self.command_queue.put(command_data)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        return {
            'operation_status': {
                'is_running': self.is_running,
                'is_listening': self.is_listening,
                'is_processing': self.is_processing
            },
            'system_health': {
                'cpu_usage': self.system_health.cpu_usage,
                'memory_usage': self.system_health.memory_usage,
                'disk_usage': self.system_health.disk_usage,
                'network_status': self.system_health.network_status,
                'microphone_status': self.system_health.microphone_status,
                'last_check': self.system_health.last_check.isoformat()
            },
            'performance_metrics': {
                'total_interactions': self.performance_metrics.total_interactions,
                'successful_interactions': self.performance_metrics.successful_interactions,
                'success_rate': (self.performance_metrics.successful_interactions / 
                               max(self.performance_metrics.total_interactions, 1)) * 100,
                'average_response_time': self.performance_metrics.average_response_time,
                'wake_word_detections': self.performance_metrics.wake_word_detections,
                'uptime_hours': self.performance_metrics.uptime_hours
            },
            'queue_status': {
                'pending_commands': self.command_queue.qsize(),
                'pending_responses': self.response_queue.qsize()
            },
            'error_status': {
                'consecutive_errors': self.consecutive_errors,
                'last_error_time': self.last_error_time.isoformat() if self.last_error_time else None
            }
        }
    
    def cleanup(self):
        """Clean up resources."""
        self.stop_autonomous_operation()
        self.logger.info("Autonomous Manager cleaned up")
