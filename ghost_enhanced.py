"""
G.H.O.S.T. Enhanced - Fully Autonomous AI Assistant

This is the main entry point for the upgraded G.H.O.S.T. system with:
- Non-blocking speech recognition with listen_in_background()
- Edge TTS for high-quality voice synthesis
- LLM-based reasoning with structured JSON responses
- Enhanced action dispatcher for unlimited commands
- 24/7 autonomous operation with crash recovery
- Security measures and confirmation for dangerous actions
"""

import sys
import time
import asyncio
import logging
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Core G.H.O.S.T. components
from core.llm_brain import LLMBrain
from core.action_dispatcher import ActionDispatcher
from core.system_indexer import SystemIndexer
from core.enhanced_personality import EnhancedPersonality
from speech.enhanced_tts import EnhancedTTS
from speech.speech_to_text import SpeechToText
from speech.wake_word_listener import WakeWordListener
from data.logger_setup import setup_logging

class GhostEnhanced:
    """
    G.H.O.S.T. Enhanced - Fully Autonomous AI Assistant
    
    Features:
    - Non-blocking speech recognition
    - High-quality Edge TTS
    - LLM-powered reasoning with structured responses
    - Unlimited command execution
    - 24/7 autonomous operation
    - Crash recovery and error handling
    - Security confirmations
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize G.H.O.S.T. Enhanced."""
        self.config = config or self._create_default_config()
        self.logger = logging.getLogger(__name__)
        
        # System state
        self.is_running = False
        self.is_listening = False
        self.startup_time = None
        
        # Core components
        self.llm_brain = None
        self.action_dispatcher = None
        self.system_indexer = None
        self.personality = None
        self.tts_system = None
        self.stt_system = None
        self.wake_word_listener = None
        
        # Performance tracking
        self.interaction_count = 0
        self.successful_interactions = 0
        self.wake_word_detections = 0
        self.last_interaction_time = 0
        
        # Threading and supervision
        self.supervisor_thread = None
        self.component_health = {}
        
        # Current conversation state
        self.awaiting_confirmation = False
        self.pending_action = None
        
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default configuration for G.H.O.S.T. Enhanced."""
        return {
            # Core system
            'owner_name': 'Sir',
            'assistant_name': 'G.H.O.S.T.',
            'operation_mode': 'enhanced_autonomous',
            
            # LLM Brain configuration
            'llm': {
                'use_openai': True,  # Enable for best performance
                'openai_model': 'gpt-4o-mini',
                'use_structured_responses': True,
                'immediate_ack': True,
                'max_context_length': 4000,
                'max_response_tokens': 500
            },
            
            # Speech Recognition (non-blocking)
            'speech_recognition': {
                'use_speech_recognition': True,
                'energy_threshold': 200,
                'pause_threshold': 0.5,
                'phrase_time_limit': 5,
                'recognition_cooldown': 0.5
            },
            
            # Wake Word Detection
            'wake_word': {
                'engine': 'simple_energy',
                'wake_words': ['ghost', 'hey ghost'],
                'confidence_threshold': 0.6,
                'energy_threshold': 300,
                'sample_rate': 16000,
                'chunk_size': 1024
            },
            
            # Text-to-Speech (Edge TTS)
            'tts': {
                'primary_engine': 'edge_tts',
                'edge_voice': 'en-US-AriaNeural',
                'edge_rate': '+0%',
                'edge_pitch': '+0Hz',
                'fallback_engine': 'pyttsx3',
                'rate': 180,
                'volume': 0.9,
                'add_pauses': True
            },
            
            # Action Dispatcher
            'actions': {
                'require_confirmation': True,
                'dangerous_actions': [
                    'system_command', 'delete_file', 'shutdown', 'restart'
                ],
                'max_concurrent_actions': 3,
                'action_timeout': 30.0
            },
            
            # System Indexing
            'indexing': {
                'auto_start': True,
                'update_interval': 300,  # 5 minutes
                'max_workers': 4,
                'batch_size': 1000
            },
            
            # Personality
            'personality': {
                'mode': 'jarvis',
                'owner_name': 'Sir',
                'assistant_name': 'G.H.O.S.T.'
            },
            
            # Autonomous Operation
            'autonomous': {
                'enable_24x7': True,
                'health_check_interval': 30,
                'max_cpu_usage': 80.0,
                'max_memory_usage': 80.0,
                'auto_restart_on_error': True,
                'supervisor_enabled': True
            },
            
            # Performance
            'performance': {
                'enable_caching': True,
                'cache_expiry_minutes': 30,
                'max_response_time': 10.0,
                'idle_cpu_target': 5.0
            },
            
            # Logging
            'logging': {
                'level': 'INFO',
                'file_logging': True,
                'console_logging': True,
                'log_file': 'logs/ghost_enhanced.log'
            }
        }
    
    async def initialize(self) -> bool:
        """Initialize all G.H.O.S.T. Enhanced components."""
        try:
            self.startup_time = datetime.now()
            
            print("🤖 Initializing G.H.O.S.T. Enhanced - Autonomous AI Assistant")
            print("=" * 70)
            
            # Setup logging
            setup_logging(self.config['logging'])
            self.logger.info("G.H.O.S.T. Enhanced initialization started")
            
            # Initialize System Indexer first (needed by other components)
            print("📁 Initializing 24/7 System Indexer...")
            self.system_indexer = SystemIndexer(self.config['indexing'])
            if self.config['indexing']['auto_start']:
                self.system_indexer.start_indexing()
            print("   ✅ Live indexing of all files, apps, and system resources")
            
            # Initialize LLM Brain
            print("🧠 Initializing LLM-Based Reasoning Brain...")
            self.llm_brain = LLMBrain(self.config['llm'])          
            print("   ✅ GPT-4o-mini with structured JSON responses")
            
            # Initialize Action Dispatcher
            print("⚡ Initializing Enhanced Action Dispatcher...")
            self.action_dispatcher = ActionDispatcher(self.config['actions'])
            self.action_dispatcher.set_system_indexer(self.system_indexer)
            print("   ✅ Unlimited command execution with security measures")
            
            # Initialize Personality
            print("🎭 Initializing J.A.R.V.I.S. Personality...")
            self.personality = EnhancedPersonality(self.config['personality'])
            print("   ✅ Professional, respectful AI assistant personality")
            
            # Initialize Enhanced TTS
            print("🔊 Initializing Edge TTS System...")
            self.tts_system = EnhancedTTS(self.config['tts'])
            print("   ✅ High-quality voice synthesis with G.H.O.S.T. pronunciation")
            
            # Initialize Speech Recognition
            print("🎤 Initializing Non-Blocking Speech Recognition...")
            self.stt_system = SpeechToText(self.config['speech_recognition'])
            print("   ✅ Optimized background listening with Google STT")
            
            # Initialize Wake Word Detection
            print("👂 Initializing Wake Word Detection...")
            self.wake_word_listener = WakeWordListener(self.config['wake_word'])
            print("   ✅ Continuous 'Ghost' detection with minimal CPU usage")
            
            # Start supervisor if enabled
            if self.config['autonomous']['supervisor_enabled']:
                print("🛡️  Starting Component Supervisor...")
                self._start_supervisor()
                print("   ✅ Crash recovery and health monitoring")
            
            print("=" * 70)
            print("🚀 SUCCESS: G.H.O.S.T. Enhanced fully initialized!")
            print()
            
            # Display capabilities
            self._display_capabilities()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize G.H.O.S.T. Enhanced: {e}")
            print(f"❌ ERROR: Initialization failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _display_capabilities(self):
        """Display G.H.O.S.T. Enhanced capabilities."""
        print("🎯 G.H.O.S.T. ENHANCED CAPABILITIES:")
        print("   • Non-blocking voice recognition with 'Ghost' wake word")
        print("   • High-quality Edge TTS with natural speech")
        print("   • GPT-4o-mini powered reasoning with structured responses")
        print("   • Unlimited command execution through action dispatcher")
        print("   • 24/7 system indexing for instant file/app search")
        print("   • Security confirmations for dangerous operations")
        print("   • Crash recovery and component supervision")
        print("   • J.A.R.V.I.S.-like professional personality")
        print()
        print("💬 EXAMPLE COMMANDS:")
        print("   - 'Ghost, open calculator'")
        print("   - 'Ghost, search for Python tutorials'")
        print("   - 'Ghost, play some music on YouTube'")
        print("   - 'Ghost, what time is it?'")
        print("   - 'Ghost, tell me a programming joke'")
        print("   - 'Ghost, open my documents folder'")
        print()
    
    async def start_autonomous_operation(self):
        """Start 24/7 autonomous operation."""
        if not self.startup_time:
            print("❌ ERROR: G.H.O.S.T. not initialized. Call initialize() first.")
            return False
        
        try:
            print("🌟 Starting 24/7 Autonomous Operation...")
            
            # Initial greeting
            greeting, _ = self.personality.get_greeting(is_owner=True, is_first_time=True)
            print(f"G.H.O.S.T.: {greeting}")
            
            # Provide immediate acknowledgment
            ack_message = self.llm_brain.get_immediate_ack()
            await self.tts_system.speak(greeting, blocking=False)
            
            # Start wake word detection
            success = self.wake_word_listener.start_listening(self._on_wake_word_detected)
            
            if not success:
                print("❌ ERROR: Failed to start wake word detection")
                return False
            
            self.is_running = True
            
            print("✅ SUCCESS: G.H.O.S.T. Enhanced is now online!")
            print("🎧 Listening for 'Ghost' wake word...")
            print("💡 Speak naturally - G.H.O.S.T. understands any reasonable request!")
            print()
            print("📊 System Status:")
            await self._display_system_status()
            print()
            print("Press Ctrl+C to stop G.H.O.S.T.")
            print("=" * 70)
            
            # Keep running until interrupted
            while self.is_running:
                await asyncio.sleep(1)
                
                # Periodic status updates (every 5 minutes)
                if int(time.time()) % 300 == 0:
                    await self._periodic_status_update()
            
            return True
            
        except KeyboardInterrupt:
            print("\\n🛑 Shutdown requested by user...")
            await self.stop_autonomous_operation()
            return True
            
        except Exception as e:
            self.logger.error(f"Error in autonomous operation: {e}")
            print(f"❌ ERROR: Autonomous operation error: {e}")
            return False
    
    def _on_wake_word_detected(self, detection):
        """Handle wake word detection."""
        try:
            self.wake_word_detections += 1
            print(f"\\n👂 Wake word detected: '{detection.word}' (confidence: {detection.confidence:.2f})")
            
            # Provide immediate audio feedback
            wake_response, _ = self.personality.get_wake_word_response(is_owner=True)
            print(f"G.H.O.S.T.: {wake_response}")
            
            # Speak acknowledgment (non-blocking)
            asyncio.create_task(self.tts_system.speak(wake_response, blocking=False))
            
            # Listen for command
            asyncio.create_task(self._listen_for_command())
            
        except Exception as e:
            self.logger.error(f"Error handling wake word: {e}")
    
    async def _listen_for_command(self):
        """Listen for user command after wake word detection."""
        try:
            print("🎤 Listening for your command...")
            
            # Listen for command with timeout
            command = self.stt_system.listen(timeout=10.0, phrase_timeout=2.0)
            
            if command:
                print(f"📝 Command: {command}")
                self.interaction_count += 1
                
                # Check if awaiting confirmation
                if self.awaiting_confirmation:
                    await self._handle_confirmation_response(command)
                    return
                
                # Provide immediate acknowledgment
                ack_message = self.llm_brain.get_immediate_ack()
                print(f"G.H.O.S.T.: {ack_message}")
                await self.tts_system.speak(ack_message, blocking=False)
                
                # Process command with LLM brain
                start_time = time.time()
                llm_response = await self.llm_brain.reason(command)
                
                # Execute any actions
                if llm_response.requires_action and llm_response.suggested_actions:
                    action = llm_response.suggested_actions[0]  # Take first action
                    
                    # Execute action with confirmation callback
                    action_result = await self.action_dispatcher.execute_action(
                        action, 
                        confirmation_callback=self._request_confirmation
                    )
                    
                    if action_result.success:
                        response = action_result.message
                        self.successful_interactions += 1
                    else:
                        response = action_result.message
                else:
                    response = llm_response.content
                    self.successful_interactions += 1
                
                # Speak final response
                print(f"G.H.O.S.T.: {response}")
                await self.tts_system.speak(response, blocking=False)
                
                # Update performance tracking
                self.last_interaction_time = time.time()
                response_time = self.last_interaction_time - start_time
                
                print(f"⏱️  Response time: {response_time:.2f}s")
                print("-" * 50)
                
            else:
                response = "I didn't catch that, Sir. Please try again."
                print(f"G.H.O.S.T.: {response}")
                await self.tts_system.speak(response, blocking=False)
                
        except Exception as e:
            self.logger.error(f"Error listening for command: {e}")
            response = "I encountered an issue processing your command, Sir."
            await self.tts_system.speak(response, blocking=False)
    
    async def _request_confirmation(self, message: str, action_type: str, 
                                  parameters: Dict[str, Any]) -> bool:
        """Request user confirmation for dangerous actions."""
        try:
            self.awaiting_confirmation = True
            self.pending_action = {'type': action_type, 'parameters': parameters}
            
            confirmation_message = f"{message} Please say 'yes' to confirm or 'no' to cancel."
            print(f"⚠️  G.H.O.S.T.: {confirmation_message}")
            await self.tts_system.speak(confirmation_message, blocking=True)
            
            # Wait for response (handled in _handle_confirmation_response)
            timeout = 30.0
            start_time = time.time()
            
            while self.awaiting_confirmation and (time.time() - start_time) < timeout:
                await asyncio.sleep(0.1)
            
            if self.awaiting_confirmation:
                # Timeout
                self.awaiting_confirmation = False
                self.pending_action = None
                timeout_msg = "Confirmation timeout. Action cancelled, Sir."
                print(f"G.H.O.S.T.: {timeout_msg}")
                await self.tts_system.speak(timeout_msg, blocking=False)
                return False
            
            # Return result (set by _handle_confirmation_response)
            return getattr(self, '_confirmation_result', False)
            
        except Exception as e:
            self.logger.error(f"Error requesting confirmation: {e}")
            self.awaiting_confirmation = False
            self.pending_action = None
            return False
    
    async def _handle_confirmation_response(self, response: str):
        """Handle user's confirmation response."""
        try:
            response_lower = response.lower().strip()
            
            if any(word in response_lower for word in ['yes', 'confirm', 'proceed', 'do it']):
                self._confirmation_result = True
                confirm_msg = "Confirmed. Proceeding with the action, Sir."
                print(f"✅ G.H.O.S.T.: {confirm_msg}")
                await self.tts_system.speak(confirm_msg, blocking=False)
            
            elif any(word in response_lower for word in ['no', 'cancel', 'stop', 'abort']):
                self._confirmation_result = False
                cancel_msg = "Action cancelled, Sir."
                print(f"❌ G.H.O.S.T.: {cancel_msg}")
                await self.tts_system.speak(cancel_msg, blocking=False)
            
            else:
                # Unclear response, ask again
                clarify_msg = "I didn't understand, Sir. Please say 'yes' to confirm or 'no' to cancel."
                print(f"❓ G.H.O.S.T.: {clarify_msg}")
                await self.tts_system.speak(clarify_msg, blocking=False)
                return  # Don't clear awaiting_confirmation
            
            self.awaiting_confirmation = False
            self.pending_action = None
            
        except Exception as e:
            self.logger.error(f"Error handling confirmation response: {e}")
            self.awaiting_confirmation = False
            self.pending_action = None
            self._confirmation_result = False
    
    def _start_supervisor(self):
        """Start component supervisor thread."""
        self.supervisor_thread = threading.Thread(
            target=self._supervisor_loop,
            daemon=True
        )
        self.supervisor_thread.start()
    
    def _supervisor_loop(self):
        """Supervisor loop for monitoring component health."""
        while self.is_running:
            try:
                # Check component health
                self._check_component_health()
                
                # Sleep for health check interval
                time.sleep(self.config['autonomous']['health_check_interval'])
                
            except Exception as e:
                self.logger.error(f"Error in supervisor loop: {e}")
                time.sleep(5)
    
    def _check_component_health(self):
        """Check health of all components."""
        try:
            # Check system resources
            import psutil
            
            cpu_usage = psutil.cpu_percent(interval=1)
            memory_usage = psutil.virtual_memory().percent
            
            self.component_health.update({
                'cpu_usage': cpu_usage,
                'memory_usage': memory_usage,
                'timestamp': datetime.now()
            })
            
            # Log warnings for high resource usage
            if cpu_usage > self.config['autonomous']['max_cpu_usage']:
                self.logger.warning(f"High CPU usage: {cpu_usage}%")
            
            if memory_usage > self.config['autonomous']['max_memory_usage']:
                self.logger.warning(f"High memory usage: {memory_usage}%")
            
        except Exception as e:
            self.logger.error(f"Error checking component health: {e}")
    
    async def _display_system_status(self):
        """Display current system status."""
        try:
            if hasattr(self, 'component_health') and self.component_health:
                health = self.component_health
                print(f"   💻 CPU: {health.get('cpu_usage', 0):.1f}% | "
                      f"Memory: {health.get('memory_usage', 0):.1f}%")
            
            print(f"   📊 Interactions: {self.interaction_count} | "
                  f"Success Rate: {(self.successful_interactions / max(self.interaction_count, 1)) * 100:.1f}% | "
                  f"Wake Words: {self.wake_word_detections}")
            
            if self.system_indexer:
                indexer_stats = self.system_indexer.get_statistics()
                print(f"   📁 Indexed Items: {indexer_stats.get('total_items', 0)} | "
                      f"Indexing: {'✅ Active' if indexer_stats.get('is_running', False) else '❌ Stopped'}")
            
        except Exception as e:
            print(f"   ❌ Error getting system status: {e}")
    
    async def _periodic_status_update(self):
        """Provide periodic status updates."""
        try:
            uptime = datetime.now() - self.startup_time
            uptime_str = str(uptime).split('.')[0]  # Remove microseconds
            
            print(f"\\n📊 G.H.O.S.T. Status Update - Uptime: {uptime_str}")
            await self._display_system_status()
            print()
            
        except Exception as e:
            self.logger.error(f"Error in periodic status update: {e}")
    
    async def stop_autonomous_operation(self):
        """Stop autonomous operation gracefully."""
        try:
            print("🛑 Stopping G.H.O.S.T. Enhanced autonomous operation...")
            
            self.is_running = False
            
            # Stop wake word detection
            if self.wake_word_listener:
                self.wake_word_listener.stop_listening()
            
            # Stop system indexer
            if self.system_indexer:
                self.system_indexer.stop_indexing()
            
            # Farewell message
            farewell, _ = self.personality.get_farewell(is_owner=True)
            print(f"G.H.O.S.T.: {farewell}")
            await self.tts_system.speak(farewell, blocking=True)
            
            # Show final statistics
            await self._display_final_statistics()
            
            print("✅ SUCCESS: G.H.O.S.T. Enhanced stopped gracefully")
            
        except Exception as e:
            self.logger.error(f"Error stopping autonomous operation: {e}")
    
    async def _display_final_statistics(self):
        """Display final statistics before shutdown."""
        try:
            uptime = datetime.now() - self.startup_time
            
            print("\\n📈 FINAL STATISTICS:")
            print(f"   ⏰ Total Uptime: {str(uptime).split('.')[0]}")
            print(f"   💬 Total Interactions: {self.interaction_count}")
            print(f"   ✅ Successful: {self.successful_interactions}")
            print(f"   📊 Success Rate: {(self.successful_interactions / max(self.interaction_count, 1)) * 100:.1f}%")
            print(f"   👂 Wake Word Detections: {self.wake_word_detections}")
            
            if self.system_indexer:
                stats = self.system_indexer.get_statistics()
                print(f"   📁 Items Indexed: {stats.get('total_items', 0)}")
            
        except Exception as e:
            self.logger.error(f"Error displaying final statistics: {e}")
    
    def cleanup(self):
        """Clean up all resources."""
        try:
            if self.wake_word_listener:
                self.wake_word_listener.cleanup()
            
            if self.stt_system:
                self.stt_system.cleanup()
            
            if self.tts_system:
                self.tts_system.cleanup()
            
            if self.system_indexer:
                self.system_indexer.cleanup()
            
            if self.llm_brain:
                self.llm_brain.cleanup()
            
            self.logger.info("G.H.O.S.T. Enhanced cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

async def main():
    """Main function for G.H.O.S.T. Enhanced."""
    import argparse
    
    parser = argparse.ArgumentParser(description='G.H.O.S.T. Enhanced - Autonomous AI Assistant')
    parser.add_argument('--test', action='store_true', help='Test mode with sample commands')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--config', type=str, help='Path to configuration file')
    
    args = parser.parse_args()
    
    # Load configuration
    config = None
    if args.config:
        try:
            import json
            with open(args.config, 'r') as f:
                config = json.load(f)
        except Exception as e:
            print(f"Error loading config file: {e}")
    
    # Set debug logging
    if args.debug:
        if not config:
            config = {}
        config.setdefault('logging', {})['level'] = 'DEBUG'
    
    # Create G.H.O.S.T. Enhanced instance
    ghost = GhostEnhanced(config)
    
    try:
        # Initialize G.H.O.S.T.
        if not await ghost.initialize():
            print("❌ ERROR: Failed to initialize G.H.O.S.T. Enhanced.")
            return 1
        
        if args.test:
            # Test mode
            print("\\n🧪 Testing G.H.O.S.T. Enhanced with sample commands...")
            print("=" * 60)
            
            test_commands = [
                "What time is it?",
                "Open calculator",
                "Search for Python tutorials",
                "Tell me a programming joke",
                "What's the weather like?",
                "Open my documents folder"
            ]
            
            for i, command in enumerate(test_commands, 1):
                print(f"\\n[Test {i}/{len(test_commands)}] {command}")
                print("-" * 40)
                
                # Process command
                llm_response = await ghost.llm_brain.reason(command)
                print(f"Response: {llm_response.content}")
                
                # Execute action if any
                if llm_response.requires_action and llm_response.suggested_actions:
                    action = llm_response.suggested_actions[0]
                    action_result = await ghost.action_dispatcher.execute_action(action)
                    print(f"Action Result: {action_result.message}")
                
                await asyncio.sleep(2)  # Brief pause between tests
        
        else:
            # Normal autonomous operation
            await ghost.start_autonomous_operation()
        
        return 0
        
    except Exception as e:
        print(f"❌ ERROR: Error running G.H.O.S.T. Enhanced: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        ghost.cleanup()

if __name__ == '__main__':
    asyncio.run(main())
