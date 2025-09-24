"""
G.H.O.S.T. Main Orchestrator

This is the central orchestrator that integrates all G.H.O.S.T. systems:
- Natural Language Understanding (NLU)
- Reasoning Engine with Chain-of-Thought
- Dynamic Action Registry
- Speech Recognition and Synthesis
- Personality System
- LLM Fallback Integration

Transforms G.H.O.S.T. from hardcoded commands to true generative AI.
"""

import sys
import time
import threading
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Core G.H.O.S.T. components
from core.nlu_engine import NLUEngine, IntentType
from core.reasoning_engine import ReasoningEngine, ReasoningResult
from core.action_registry import ActionRegistry, get_global_registry
from core.enhanced_personality import EnhancedPersonality
from speech.enhanced_tts import EnhancedTTS
from speech.speech_to_text import SpeechToText

class GhostOrchestrator:
    """
    Main orchestrator for G.H.O.S.T. generative AI system.
    
    Integrates all components to provide natural language understanding,
    reasoning, and execution capabilities.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize G.H.O.S.T. orchestrator."""
        self.config = config or self._create_default_config()
        self.logger = logging.getLogger(__name__)
        
        # System state
        self.is_running = False
        self.is_listening = False
        
        # Core components
        self.nlu_engine = None
        self.reasoning_engine = None
        self.action_registry = None
        self.personality = None
        self.tts_system = None
        self.stt_system = None
        
        # Performance tracking
        self.last_interaction_time = 0
        self.interaction_count = 0
        self.successful_interactions = 0
        
        # Threading
        self.background_listener = None
        
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default configuration for G.H.O.S.T."""
        return {
            # Core system
            'owner_name': 'Karan',
            'owner_title': 'Sir',
            'assistant_name': 'G.H.O.S.T.',
            
            # Personality
            'personality': {
                'mode': 'jarvis',
                'owner_name': 'Karan',
                'owner_title': 'Sir',
                'assistant_name': 'G.H.O.S.T.'
            },
            
            # NLU Engine
            'nlu': {
                'min_confidence': 0.6,
                'fallback_threshold': 0.3
            },
            
            # Reasoning Engine
            'reasoning': {
                'reasoning_mode': 'hybrid',
                'use_local_llm': False,
                'use_cloud_llm': False,
                'fallback_to_llm': True,
                'enable_chain_of_thought': True,
                'cot_max_steps': 3
            },
            
            # Action Registry
            'actions': {
                'actions_directory': 'actions',
                'auto_discover': True
            },
            
            # Speech Recognition
            'speech_recognition': {
                'use_speech_recognition': True,
                'wake_words': ['ghost'],
                'energy_threshold': 200,
                'pause_threshold': 0.5
            },
            
            # Text-to-Speech
            'tts': {
                'primary_engine': 'pyttsx3',
                'rate': 180,
                'volume': 0.9,
                'add_pauses': True
            },
            
            # Performance
            'performance': {
                'max_response_time': 5.0,
                'enable_caching': True,
                'log_level': 'WARNING'
            }
        }
    
    def initialize(self) -> bool:
        """Initialize all G.H.O.S.T. components."""
        try:
            self.logger.info("Initializing G.H.O.S.T. Generative AI System...")
            
            # Set logging level
            log_level = getattr(logging, self.config['performance']['log_level'], logging.WARNING)
            logging.getLogger().setLevel(log_level)
            
            # Initialize NLU Engine
            self.nlu_engine = NLUEngine(self.config['nlu'])
            self.logger.info("✓ Natural Language Understanding Engine")
            
            # Initialize Action Registry
            self.action_registry = ActionRegistry(self.config['actions'])
            self.logger.info(f"✓ Dynamic Action Registry ({len(self.action_registry.get_all_actions())} actions)")
            
            # Initialize Reasoning Engine
            reasoning_config = self.config['reasoning'].copy()
            reasoning_config['nlu'] = self.config['nlu']
            self.reasoning_engine = ReasoningEngine(reasoning_config)
            self.logger.info("✓ Enhanced Reasoning Engine with Chain-of-Thought")
            
            # Initialize Personality System
            self.personality = EnhancedPersonality(self.config['personality'])
            self.logger.info("✓ J.A.R.V.I.S. Personality System")
            
            # Initialize TTS System
            self.tts_system = EnhancedTTS(self.config['tts'])
            self.logger.info("✓ Enhanced Text-to-Speech (G.H.O.S.T. pronunciation)")
            
            # Initialize STT System
            self.stt_system = SpeechToText(self.config['speech_recognition'])
            self.logger.info("✓ Optimized Speech Recognition")
            
            self.logger.info("SUCCESS: All G.H.O.S.T. components initialized!")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize G.H.O.S.T.: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def process_natural_language(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process natural language input using the full G.H.O.S.T. pipeline.
        
        Args:
            user_input: Natural language input from user
            context: Optional context information
            
        Returns:
            Processing result with response and actions
        """
        try:
            start_time = time.time()
            self.interaction_count += 1
            
            self.logger.debug(f"Processing: {user_input}")
            
            # Step 1: Reasoning (includes NLU)
            reasoning_result = self.reasoning_engine.process_input(user_input, context)
            
            # Step 2: Execute actions if any
            execution_results = []
            if reasoning_result.actions:
                for action in reasoning_result.actions:
                    action_type = action.get('type')
                    parameters = action.get('parameters', {})
                    
                    # Execute using action registry
                    result = self.action_registry.execute_action(action_type, parameters)
                    execution_results.append(result)
            
            # Step 3: Generate final response
            final_response = self._generate_final_response(reasoning_result, execution_results)
            
            # Step 4: Track performance
            processing_time = time.time() - start_time
            self.last_interaction_time = time.time()
            
            if reasoning_result.confidence > 0.5:
                self.successful_interactions += 1
            
            # Return comprehensive result
            return {
                'success': True,
                'response': final_response,
                'intent': reasoning_result.intent,
                'confidence': reasoning_result.confidence,
                'actions_executed': len(execution_results),
                'processing_time': processing_time,
                'reasoning_steps': reasoning_result.reasoning_steps,
                'entities': getattr(reasoning_result, 'entities', []),
                'suggestions': getattr(reasoning_result, 'suggestions', [])
            }
            
        except Exception as e:
            self.logger.error(f"Error processing natural language: {e}")
            return {
                'success': False,
                'response': "I apologize, Sir, but I encountered an issue processing your request.",
                'error': str(e),
                'intent': 'error',
                'confidence': 0.0
            }
    
    def _generate_final_response(self, reasoning_result: ReasoningResult, execution_results: List[Dict[str, Any]]) -> str:
        """Generate final response combining reasoning and execution results."""
        try:
            # Start with reasoning response
            response = reasoning_result.response
            
            # Add execution feedback if available
            if execution_results:
                successful_executions = [r for r in execution_results if r.get('success', False)]
                failed_executions = [r for r in execution_results if not r.get('success', False)]
                
                if successful_executions and not failed_executions:
                    # All successful - response is already good
                    pass
                elif failed_executions:
                    # Some failures - add error information
                    if successful_executions:
                        response += " However, I encountered some issues with part of your request."
                    else:
                        response = "I apologize, Sir, but I encountered issues executing that request."
                        
                        # Add specific error if available
                        if failed_executions[0].get('message'):
                            response = failed_executions[0]['message']
            
            # Ensure proper addressing
            if not any(title in response for title in ['Sir', 'sir']):
                response = response.rstrip('.') + ', Sir.'
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error generating final response: {e}")
            return reasoning_result.response
    
    def speak(self, text: str, blocking: bool = False) -> bool:
        """Speak text using the TTS system."""
        try:
            return self.tts_system.speak(text, blocking=blocking)
        except Exception as e:
            self.logger.error(f"Speech error: {e}")
            print(f"G.H.O.S.T.: {text}")
            return False
    
    def start_voice_interaction(self) -> None:
        """Start voice interaction mode."""
        try:
            self.logger.info("Starting voice interaction mode...")
            
            # Initial greeting
            greeting, _ = self.personality.get_greeting(is_owner=True, is_first_time=True)
            print(f"G.H.O.S.T.: {greeting}")
            self.speak(greeting, blocking=True)
            
            print("\\n=== G.H.O.S.T. Generative AI Online ===")
            print("Features:")
            print("  • Natural Language Understanding")
            print("  • Chain-of-Thought Reasoning")
            print("  • Dynamic Action Registry")
            print("  • LLM Fallback Integration")
            print("  • J.A.R.V.I.S. Personality")
            print()
            print("You can now speak naturally to G.H.O.S.T.!")
            print("Say 'Ghost' to activate, then speak any request.")
            print("Examples:")
            print("  - 'Open Wikipedia and search for artificial intelligence'")
            print("  - 'What's the weather like and what time is it?'")
            print("  - 'Tell me a joke about programming'")
            print("  - 'How do I install Python packages?'")
            print()
            print("Press Ctrl+C to stop.")
            print()
            
            # Start listening
            self.is_listening = True
            self.stt_system.continuous_listen(
                callback=self._on_wake_word_detected,
                wake_word_only=True
            )
            
            # Keep running
            self.is_running = True
            while self.is_running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("Voice interaction stopped by user")
        except Exception as e:
            self.logger.error(f"Error in voice interaction: {e}")
        finally:
            self.stop_voice_interaction()
    
    def _on_wake_word_detected(self, text: str) -> None:
        """Handle wake word detection."""
        try:
            print(f"\\n🎤 Wake word detected: {text}")
            
            # Respond to wake word
            wake_response, _ = self.personality.get_wake_word_response(is_owner=True)
            print(f"G.H.O.S.T.: {wake_response}")
            self.speak(wake_response, blocking=False)
            
            # Listen for command
            self._listen_for_command()
            
        except Exception as e:
            self.logger.error(f"Error handling wake word: {e}")
    
    def _listen_for_command(self) -> None:
        """Listen for user command after wake word."""
        try:
            print("Listening for your command...")
            
            # Listen for command
            command = self.stt_system.listen(timeout=10.0, phrase_timeout=2.0)
            
            if command:
                print(f"Command: {command}")
                
                # Process with full G.H.O.S.T. pipeline
                result = self.process_natural_language(command)
                
                # Speak response
                response = result.get('response', 'I processed your request, Sir.')
                print(f"G.H.O.S.T.: {response}")
                self.speak(response, blocking=False)
                
                # Show additional info if available
                if result.get('suggestions'):
                    print(f"Suggestions: {', '.join(result['suggestions'])}")
                
            else:
                response = "I didn't catch that, Sir. Please try again."
                print(f"G.H.O.S.T.: {response}")
                self.speak(response, blocking=False)
                
        except Exception as e:
            self.logger.error(f"Error listening for command: {e}")
            response = "I encountered an issue listening for your command, Sir."
            self.speak(response, blocking=False)
    
    def stop_voice_interaction(self) -> None:
        """Stop voice interaction mode."""
        try:
            self.is_running = False
            self.is_listening = False
            
            if self.stt_system:
                self.stt_system.stop_continuous_listen()
            
            # Farewell
            farewell, _ = self.personality.get_farewell(is_owner=True)
            print(f"G.H.O.S.T.: {farewell}")
            self.speak(farewell, blocking=True)
            
            print("G.H.O.S.T. systems offline.")
            
        except Exception as e:
            self.logger.error(f"Error stopping voice interaction: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        try:
            return {
                'system': {
                    'running': self.is_running,
                    'listening': self.is_listening,
                    'uptime': time.time() - self.last_interaction_time if self.last_interaction_time else 0
                },
                'performance': {
                    'total_interactions': self.interaction_count,
                    'successful_interactions': self.successful_interactions,
                    'success_rate': (self.successful_interactions / max(self.interaction_count, 1)) * 100
                },
                'components': {
                    'nlu_engine': bool(self.nlu_engine),
                    'reasoning_engine': bool(self.reasoning_engine),
                    'action_registry': self.action_registry.get_registry_status() if self.action_registry else None,
                    'personality': bool(self.personality),
                    'tts_system': bool(self.tts_system),
                    'stt_system': bool(self.stt_system)
                }
            }
        except Exception as e:
            self.logger.error(f"Error getting system status: {e}")
            return {'error': str(e)}
    
    def cleanup(self) -> None:
        """Clean up system resources."""
        try:
            self.logger.info("Cleaning up G.H.O.S.T. resources...")
            
            if self.stt_system:
                self.stt_system.cleanup()
            
            self.is_running = False
            self.is_listening = False
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

def main():
    """Main function for running G.H.O.S.T. orchestrator."""
    import argparse
    
    parser = argparse.ArgumentParser(description='G.H.O.S.T. Generative AI Assistant')
    parser.add_argument('--test', action='store_true', help='Test mode - process sample inputs')
    parser.add_argument('--voice', action='store_true', help='Voice interaction mode')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Configure logging
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)
    
    # Create orchestrator
    orchestrator = GhostOrchestrator()
    
    if not orchestrator.initialize():
        print("Failed to initialize G.H.O.S.T.")
        return 1
    
    try:
        if args.test:
            # Test mode - process sample inputs
            test_inputs = [
                "What time is it?",
                "Open Wikipedia and search for machine learning",
                "Tell me a joke about computers",
                "How do I create a Python virtual environment?",
                "What's the weather like today?",
                "Open calculator and notepad"
            ]
            
            print("Testing G.H.O.S.T. with sample inputs...")
            print("=" * 50)
            
            for test_input in test_inputs:
                print(f"\\nInput: {test_input}")
                result = orchestrator.process_natural_language(test_input)
                print(f"Response: {result.get('response', 'No response')}")
                print(f"Intent: {result.get('intent', 'unknown')} (confidence: {result.get('confidence', 0):.2f})")
                if result.get('reasoning_steps'):
                    print(f"Reasoning: {' -> '.join(result['reasoning_steps'])}")
                time.sleep(1)
        
        elif args.voice:
            # Voice interaction mode
            orchestrator.start_voice_interaction()
        
        else:
            # Interactive text mode
            print("G.H.O.S.T. Interactive Mode")
            print("Type your requests naturally, or 'quit' to exit.")
            print()
            
            while True:
                try:
                    user_input = input("You: ").strip()
                    
                    if user_input.lower() in ['quit', 'exit', 'bye']:
                        break
                    
                    if user_input:
                        result = orchestrator.process_natural_language(user_input)
                        print(f"G.H.O.S.T.: {result.get('response', 'No response')}")
                        
                        if result.get('suggestions'):
                            print(f"Suggestions: {', '.join(result['suggestions'])}")
                
                except (EOFError, KeyboardInterrupt):
                    break
        
        return 0
        
    except Exception as e:
        print(f"Error running G.H.O.S.T.: {e}")
        return 1
    
    finally:
        orchestrator.cleanup()

if __name__ == '__main__':
    sys.exit(main())
