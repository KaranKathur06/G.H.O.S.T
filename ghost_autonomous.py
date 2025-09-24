"""
J.A.R.V.I.S.-like Autonomous G.H.O.S.T. AI Assistant

This is the main entry point for the fully autonomous, 24x7 G.H.O.S.T. AI assistant
that can understand and respond to any natural language request intelligently.
"""

import sys
import time
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Core G.H.O.S.T. components
from core.universal_nlu import UniversalNLU
from core.system_indexer import SystemIndexer
from core.llm_brain import LLMBrain
from core.smart_action_engine import SmartActionEngine
from core.decision_engine import DecisionEngine
from core.autonomous_manager import AutonomousManager
from core.enhanced_personality import EnhancedPersonality
from speech.enhanced_tts import EnhancedTTS

class JarvisGhost:
    """
    J.A.R.V.I.S.-like Autonomous G.H.O.S.T. AI Assistant.
    
    A fully autonomous, 24x7 AI assistant that can:
    - Understand any natural language command
    - Make intelligent decisions and ask clarifying questions
    - Execute any reasonable request
    - Learn and improve over time
    - Operate continuously without manual intervention
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize J.A.R.V.I.S. G.H.O.S.T."""
        self.config = config or self._create_default_config()
        self.logger = logging.getLogger(__name__)
        
        # Core AI components
        self.nlu_engine = None
        self.system_indexer = None
        self.llm_brain = None
        self.action_engine = None
        self.decision_engine = None
        self.personality = None
        self.tts_system = None
        
        # Autonomous operation manager
        self.autonomous_manager = None
        
        # System state
        self.is_initialized = False
        self.is_running = False
        self.startup_time = None
        
        # User interaction tracking
        self.current_conversation = None
        self.pending_clarification = None
        
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default configuration for autonomous G.H.O.S.T."""
        return {
            # Core system
            'owner_name': 'Sir',
            'assistant_name': 'G.H.O.S.T.',
            'operation_mode': 'autonomous',
            
            # Natural Language Understanding
            'nlu': {
                'min_confidence': 0.6,
                'clarification_threshold': 0.4,
                'enable_learning': True
            },
            
            # System Indexing
            'indexing': {
                'auto_start': True,
                'update_interval': 300,  # 5 minutes
                'max_workers': 4
            },
            
            # LLM Brain
            'llm': {
                'use_openai': False,  # Set to True and add API key to use
                'use_ollama': True,   # Local LLM
                'use_local': False,   # Transformers models
                'max_context_length': 4000,
                'max_response_tokens': 500
            },
            
            # Decision Making
            'decision': {
                'confidence_threshold': 0.7,
                'clarification_threshold': 0.4,
                'max_options_to_show': 5
            },
            
            # Speech & Voice
            'speech': {
                'wake_words': ['ghost', 'hey ghost'],
                'energy_threshold': 300,
                'pause_threshold': 0.8,
                'enable_voice_response': True
            },
            
            # TTS Configuration
            'tts': {
                'primary_engine': 'pyttsx3',
                'rate': 180,
                'volume': 0.9,
                'voice_id': None,  # Auto-select best voice
                'add_pauses': True
            },
            
            # Autonomous Operation
            'autonomous': {
                'enable_24x7': True,
                'health_check_interval': 30,
                'max_cpu_usage': 80.0,
                'max_memory_usage': 80.0,
                'auto_restart_on_error': True
            },
            
            # Performance
            'performance': {
                'enable_caching': True,
                'cache_expiry_minutes': 30,
                'max_concurrent_actions': 3,
                'response_timeout': 30.0
            },
            
            # Logging
            'logging': {
                'level': 'INFO',
                'file_logging': True,
                'console_logging': True
            }
        }
    
    async def initialize(self) -> bool:
        """Initialize all G.H.O.S.T. components."""
        try:
            self.startup_time = datetime.now()
            
            print("Initializing J.A.R.V.I.S. G.H.O.S.T. AI Assistant...")
            print("=" * 60)
            
            # Configure logging
            self._setup_logging()
            
            # Initialize Universal NLU Engine
            print("Initializing Universal Natural Language Understanding...")
            self.nlu_engine = UniversalNLU(self.config['nlu'])
            print("   OK: Can understand ANY natural language command")
            
            # Initialize System Indexer
            print("Initializing 24/7 System Indexer...")
            self.system_indexer = SystemIndexer(self.config['indexing'])
            if self.config['indexing']['auto_start']:
                self.system_indexer.start_indexing()
            print("   OK: Live indexing of all files, apps, and system resources")
            
            # Initialize LLM Brain
            print("Initializing LLM-Based Reasoning Brain...")
            self.llm_brain = LLMBrain(self.config['llm'])
            print("   OK: ChatGPT-style reasoning and conversation capabilities")
            
            # Initialize Smart Action Engine
            print("Initializing Smart Action Engine...")
            self.action_engine = SmartActionEngine()
            self.action_engine.set_system_indexer(self.system_indexer)
            print("   OK: Can execute any application, media, or system command")
            
            # Initialize Decision Engine
            print("Initializing Decision-Making Engine...")
            self.decision_engine = DecisionEngine(self.config['decision'])
            print("   OK: Intelligent decision-making and clarification system")
            
            # Initialize Personality
            print("Initializing J.A.R.V.I.S. Personality...")
            self.personality = EnhancedPersonality({
                'mode': 'jarvis',
                'owner_name': self.config['owner_name'],
                'assistant_name': self.config['assistant_name']
            })
            print("   OK: Professional, polite, and helpful J.A.R.V.I.S.-like personality")
            
            # Initialize TTS System
            print("Initializing Enhanced Text-to-Speech...")
            self.tts_system = EnhancedTTS(self.config['tts'])
            print("   OK: Natural speech with G.H.O.S.T. pronunciation")
            
            # Initialize Autonomous Manager
            print("Initializing 24/7 Autonomous Operation Manager...")
            self.autonomous_manager = AutonomousManager(self.config['autonomous'])
            
            # Link all components
            self.autonomous_manager.set_components(
                self.nlu_engine,
                self.decision_engine,
                self.action_engine,
                self.llm_brain,
                self.system_indexer
            )
            
            # Set up callbacks
            self.autonomous_manager.set_callbacks(
                on_wake_word=self._on_wake_word_detected,
                on_command=self._on_command_received,
                on_response=self._on_response_ready,
                on_error=self._on_error_occurred
            )
            
            print("   OK: Continuous wake word detection and command processing")
            
            self.is_initialized = True
            
            print("=" * 60)
            print("SUCCESS: J.A.R.V.I.S. G.H.O.S.T. AI Assistant fully initialized!")
            print()
            
            # Show system capabilities
            self._display_capabilities()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize G.H.O.S.T.: {e}")
            print(f"ERROR: Initialization failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _setup_logging(self):
        """Set up logging configuration."""
        log_level = getattr(logging, self.config['logging']['level'], logging.INFO)
        
        # Configure root logger
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[]
        )
        
        # Console logging
        if self.config['logging']['console_logging']:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            logging.getLogger().addHandler(console_handler)
        
        # File logging
        if self.config['logging']['file_logging']:
            file_handler = logging.FileHandler('ghost_jarvis.log')
            file_handler.setLevel(log_level)
            logging.getLogger().addHandler(file_handler)
    
    def _display_capabilities(self):
        """Display G.H.O.S.T.'s capabilities."""
        print("G.H.O.S.T. CAPABILITIES:")
        print("   - Universal Natural Language Understanding")
        print("   - Intelligent Decision-Making & Clarification")
        print("   - Dynamic System Indexing & Search")
        print("   - Smart Action Execution (Apps, Media, Files, Web)")
        print("   - LLM-Based Reasoning & Conversation")
        print("   - 24/7 Autonomous Operation")
        print("   - Proactive Assistance & Learning")
        print("   - J.A.R.V.I.S.-like Personality")
        print()
        print("EXAMPLE COMMANDS:")
        print("   - 'Ghost, play some relaxing music on Spotify'")
        print("   - 'Open my project files and launch VS Code'")
        print("   - 'Search for Python tutorials and open the best one'")
        print("   - 'What's the weather like and what time is it?'")
        print("   - 'Shutdown the computer in 10 minutes'")
        print("   - 'Tell me about artificial intelligence'")
        print()
    
    async def start_autonomous_operation(self):
        """Start 24/7 autonomous operation."""
        if not self.is_initialized:
            print("ERROR: G.H.O.S.T. not initialized. Call initialize() first.")
            return False
        
        try:
            print("Starting 24/7 Autonomous Operation...")
            
            # Initial greeting
            greeting, _ = self.personality.get_greeting(is_owner=True, is_first_time=True)
            print(f"G.H.O.S.T.: {greeting}")
            self.tts_system.speak(greeting, blocking=True)
            
            # Start autonomous manager
            self.autonomous_manager.start_autonomous_operation()
            self.is_running = True
            
            print("SUCCESS: G.H.O.S.T. is now online and listening for 'Ghost' wake word...")
            print("READY: Speak naturally - G.H.O.S.T. can understand any reasonable request!")
            print()
            print("System Status:")
            await self._display_system_status()
            print()
            print("Press Ctrl+C to stop G.H.O.S.T.")
            print("=" * 60)
            
            # Keep running until interrupted
            while self.is_running:
                await asyncio.sleep(1)
                
                # Periodic status updates (every 5 minutes)
                if int(time.time()) % 300 == 0:
                    await self._periodic_status_update()
            
            return True
            
        except KeyboardInterrupt:
   
            await self.stop_autonomous_operation()
            return True
            
        except Exception as e:
            self.logger.error(f"Error in autonomous operation: {e}")
            print(f"ERROR: Autonomous operation error: {e}")
            return False
    
    async def stop_autonomous_operation(self):
        """Stop autonomous operation gracefully."""
        try:
            print("Stopping G.H.O.S.T. autonomous operation...")
            
            self.is_running = False
            
            if self.autonomous_manager:
                self.autonomous_manager.stop_autonomous_operation()
            
            # Farewell message
            farewell, _ = self.personality.get_farewell(is_owner=True)
            print(f"G.H.O.S.T.: {farewell}")
            self.tts_system.speak(farewell, blocking=True)
            
            # Show final statistics
            await self._display_final_statistics()
            
            print("SUCCESS: G.H.O.S.T. autonomous operation stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping autonomous operation: {e}")
    
    async def process_text_command(self, command: str) -> str:
        """Process a text command manually (for testing/debugging)."""
        try:
            if not self.is_initialized:
                return "G.H.O.S.T. is not initialized."
            
            # Add command to processing queue
            self.autonomous_manager.add_command_to_queue(command, source="manual")
            
            # Wait for response (with timeout)
            timeout = 30.0
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                if not self.autonomous_manager.response_queue.empty():
                    response_data = self.autonomous_manager.response_queue.get_nowait()
                    return response_data['text']
                
                await asyncio.sleep(0.1)
            
            return "Response timeout - G.H.O.S.T. is taking too long to process the request."
            
        except Exception as e:
            self.logger.error(f"Error processing text command: {e}")
            return f"Error processing command: {str(e)}"
    
    def _on_wake_word_detected(self, text: str):
        """Handle wake word detection."""
        print(f"\\nWake word detected: '{text}'")
        
        # Provide audio feedback
        wake_response, _ = self.personality.get_wake_word_response(is_owner=True)
        print(f"G.H.O.S.T.: {wake_response}")
        self.tts_system.speak(wake_response, blocking=False)
    
    def _on_command_received(self, command: str):
        """Handle command reception."""
        print(f"Command received: '{command}'")
        print("G.H.O.S.T. is thinking...")
    
    def _on_response_ready(self, response_data: Dict[str, Any]):
        """Handle response ready."""
        response_text = response_data['text']
        response_time = response_data.get('response_time', 0)
        success = response_data.get('success', True)
        
        status_icon = "SUCCESS" if success else "ERROR"
        print(f"{status_icon}: G.H.O.S.T.: {response_text}")
        print(f"Response time: {response_time:.2f}s")
        
        # Speak response
        if self.config['speech']['enable_voice_response']:
            self.tts_system.speak(response_text, blocking=False)
        
        print("-" * 40)
    
    def _on_error_occurred(self, error: Exception, context: str):
        """Handle error occurrence."""
        print(f"WARNING: Error in {context}: {str(error)}")
        self.logger.error(f"Error in {context}: {error}")
    
    async def _display_system_status(self):
        """Display current system status."""
        try:
            status = self.autonomous_manager.get_system_status()
            
            print(f"   CPU: {status['system_health']['cpu_usage']:.1f}% | "
                  f"Memory: {status['system_health']['memory_usage']:.1f}% | "
                  f"Network: {'OK' if status['system_health']['network_status'] else 'ERROR'}")
            
            print(f"   Interactions: {status['performance_metrics']['total_interactions']} | "
                  f"Success Rate: {status['performance_metrics']['success_rate']:.1f}% | "
                  f"Avg Response: {status['performance_metrics']['average_response_time']:.2f}s")
            
            if self.system_indexer:
                indexer_stats = self.system_indexer.get_statistics()
                print(f"   Indexed Items: {indexer_stats.get('total_items', 0)} | "
                      f"Indexing: {'OK' if indexer_stats.get('is_running', False) else 'STOPPED'}")
            
        except Exception as e:
            print(f"   ERROR: Error getting system status: {e}")
    
    async def _periodic_status_update(self):
        """Provide periodic status updates."""
        try:
            uptime = datetime.now() - self.startup_time
            uptime_str = str(uptime).split('.')[0]  # Remove microseconds
            
            print(f"\\nG.H.O.S.T. Status Update - Uptime: {uptime_str}")
            await self._display_system_status()
            print()
            
        except Exception as e:
            self.logger.error(f"Error in periodic status update: {e}")
    
    async def _display_final_statistics(self):
        """Display final statistics before shutdown."""
        try:
            if self.autonomous_manager:
                status = self.autonomous_manager.get_system_status()
                uptime = datetime.now() - self.startup_time
                
                print("\\nFINAL STATISTICS:")
                print(f"   Total Uptime: {str(uptime).split('.')[0]}")
                print(f"   Total Interactions: {status['performance_metrics']['total_interactions']}")
                print(f"   Successful: {status['performance_metrics']['successful_interactions']}")
                print(f"   Success Rate: {status['performance_metrics']['success_rate']:.1f}%")
                print(f"   Wake Word Detections: {status['performance_metrics']['wake_word_detections']}")
                print(f"   Average Response Time: {status['performance_metrics']['average_response_time']:.2f}s")
                
        except Exception as e:
            self.logger.error(f"Error displaying final statistics: {e}")
    
    def cleanup(self):
        """Clean up all resources."""
        try:
            if self.autonomous_manager:
                self.autonomous_manager.cleanup()
            
            if self.system_indexer:
                self.system_indexer.cleanup()
            
            if self.llm_brain:
                self.llm_brain.cleanup()
            
            if self.action_engine:
                self.action_engine.cleanup()
            
            if self.decision_engine:
                self.decision_engine.cleanup()
            
            self.logger.info("G.H.O.S.T. cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

async def main():
    """Main function for J.A.R.V.I.S. G.H.O.S.T."""
    import argparse
    
    parser = argparse.ArgumentParser(description='J.A.R.V.I.S.-like G.H.O.S.T. AI Assistant')
    parser.add_argument('--test', action='store_true', help='Test mode with sample commands')
    parser.add_argument('--voice', action='store_true', help='Voice-only mode (default)')
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
    
    # Create G.H.O.S.T. instance
    ghost = JarvisGhost(config)
    
    try:
        # Initialize G.H.O.S.T.
        if not await ghost.initialize():
            print("ERROR: Failed to initialize G.H.O.S.T.")
            return 1
        
        if args.test:
            # Test mode
            print("\\nTesting G.H.O.S.T. with sample commands...")
            print("=" * 50)
            
            test_commands = [
                "What time is it?",
                "Open calculator",
                "Play some music on YouTube",
                "Search for Python tutorials",
                "Tell me a joke",
                "What's the weather like?",
                "How are you doing today?",
                "Open my documents folder"
            ]
            
            for i, command in enumerate(test_commands, 1):
                print(f"\\n[Test {i}/{len(test_commands)}] {command}")
                print("-" * 30)
                
                response = await ghost.process_text_command(command)
                print(f"Response: {response}")
                
                await asyncio.sleep(2)  # Brief pause between tests
        
        else:
            # Normal autonomous operation
            await ghost.start_autonomous_operation()
        
        return 0
        
    except Exception as e:
        print(f"ERROR: Error running G.H.O.S.T.: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        ghost.cleanup()

if __name__ == '__main__':
    import asyncio
    sys.exit(asyncio.run(main()))
