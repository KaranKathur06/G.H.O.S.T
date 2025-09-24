"""
Advanced reasoning engine for G.H.O.S.T. virtual assistant.

This module handles natural language understanding, intent recognition,
multi-step task planning, and decision-making logic with local/cloud LLM support.
"""

import logging
import re
import json
import asyncio
from typing import Dict, Any, Optional, List, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from .memory_manager import MemoryManager
from .nlu_engine import NLUEngine, Intent, IntentType

try:
    # Local LLM support
    from gpt4all import GPT4All
    GPT4ALL_AVAILABLE = True
except ImportError:
    GPT4ALL_AVAILABLE = False
    GPT4All = None

try:
    # Cloud LLM support (optional)
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None


class ReasoningMode(Enum):
    """Different reasoning modes for G.H.O.S.T."""
    PATTERN_MATCHING = "pattern_matching"  # Fast rule-based matching
    LOCAL_LLM = "local_llm"              # Local LLM reasoning
    CLOUD_LLM = "cloud_llm"              # Cloud LLM reasoning
    HYBRID = "hybrid"                    # Combination of methods


class TaskComplexity(Enum):
    """Task complexity levels."""
    SIMPLE = "simple"        # Single action
    MODERATE = "moderate"    # 2-3 steps
    COMPLEX = "complex"      # Multi-step planning required


@dataclass
class Intent:
    """Represents a parsed user intent with associated parameters."""
    action: str
    confidence: float
    parameters: Dict[str, Any]
    raw_command: str
    complexity: TaskComplexity = TaskComplexity.SIMPLE
    reasoning_mode: ReasoningMode = ReasoningMode.PATTERN_MATCHING
    explanation: Optional[str] = None
    sub_tasks: List['TaskStep'] = field(default_factory=list)


@dataclass
class TaskStep:
    """Represents a single step in a multi-step task."""
    step_id: str
    action: str
    parameters: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)
    estimated_duration: float = 1.0
    completed: bool = False
    result: Optional[Any] = None


@dataclass
class ReasoningResult:
    """Enhanced result of reasoning process."""
    intent: str
    confidence: float
    actions: List[Dict[str, Any]]
    response: str
    reasoning_steps: List[str] = field(default_factory=list)
    complexity: TaskComplexity = TaskComplexity.SIMPLE
    requires_llm: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    entities: List[Any] = field(default_factory=list)  # NLU entities
    parameters: Dict[str, Any] = field(default_factory=dict)  # Extracted parameters
    suggestions: List[str] = field(default_factory=list)  # Helpful suggestions


class ReasoningEngine:
    """
    Advanced reasoning engine for G.H.O.S.T.
    
    Handles natural language understanding, intent recognition,
    multi-step task planning, and decision-making with LLM support.
    Now integrated with NLU engine for true generative AI capabilities.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the reasoning engine.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Core components
        self.memory_manager = MemoryManager(config.get('memory', {}))
        self.nlu_engine = NLUEngine(config.get('nlu', {}))
        
        # Reasoning configuration
        self.reasoning_mode = ReasoningMode(config.get('reasoning_mode', 'hybrid'))
        self.use_local_llm = config.get('use_local_llm', False)
        self.use_cloud_llm = config.get('use_cloud_llm', False)
        self.fallback_to_llm = config.get('fallback_to_llm', True)
        
        # LLM instances
        self.local_llm = None
        self.cloud_llm_client = None
        
        # Intent patterns and rules (legacy support)
        self.intent_patterns = self._load_intent_patterns()
        self.action_rules = self._load_action_rules()
        
        # Task planning
        self.max_planning_steps = config.get('max_planning_steps', 5)
        self.planning_timeout = config.get('planning_timeout', 30.0)
        
        # Chain-of-thought reasoning
        self.enable_cot = config.get('enable_chain_of_thought', True)
        self.cot_max_steps = config.get('cot_max_steps', 3)
        
        # Initialize components
        self._initialize_llms()
        
        self.logger.info(f"Enhanced reasoning engine initialized in {self.reasoning_mode.value} mode with NLU")
    
    def _initialize_llms(self) -> None:
        """Initialize LLM components if available."""
        try:
            # Initialize local LLM if requested and available
            if self.use_local_llm and GPT4ALL_AVAILABLE:
                try:
                    model_path = self.config.get('local_llm_model', 'orca-mini-3b-gguf2-q4_0.gguf')
                    self.local_llm = GPT4All(model_path)
                    self.logger.info("Local LLM (GPT4All) initialized")
                except Exception as e:
                    self.logger.warning(f"Failed to initialize local LLM: {e}")
                    self.use_local_llm = False
            
            # Initialize cloud LLM if requested and available
            if self.use_cloud_llm and OPENAI_AVAILABLE:
                try:
                    api_key = self.config.get('openai_api_key')
                    if api_key:
                        openai.api_key = api_key
                        self.cloud_llm_client = openai
                        self.logger.info("Cloud LLM (OpenAI) initialized")
                    else:
                        self.logger.warning("OpenAI API key not provided")
                        self.use_cloud_llm = False
                except Exception as e:
                    self.logger.warning(f"Failed to initialize cloud LLM: {e}")
                    self.use_cloud_llm = False
                    
        except Exception as e:
            self.logger.error(f"Error initializing LLMs: {e}")
    
    def process_input(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> ReasoningResult:
        """
        Process user input using enhanced NLU and generate reasoning result.
        
        Args:
            user_input: Raw user input text
            context: Optional context information
            
        Returns:
            ReasoningResult with intent, actions, and response
        """
        try:
            self.logger.debug(f"Processing input: {user_input[:100]}...")
            
            # Store context
            if context:
                self.memory_manager.store_context(context)
            
            # Step 1: NLU Processing
            intent = self.nlu_engine.understand(user_input)
            self.logger.debug(f"NLU classified intent: {intent.type.value} (confidence: {intent.confidence:.2f})")
            
            # Step 2: Analyze complexity and determine reasoning approach
            complexity = self._analyze_intent_complexity(intent)
            
            # Step 3: Choose reasoning approach
            if intent.type == IntentType.UNKNOWN and intent.confidence < 0.3:
                # Use LLM for unknown intents
                result = self._llm_fallback_reasoning(user_input, intent, complexity)
            elif self.reasoning_mode == ReasoningMode.HYBRID:
                result = self._enhanced_hybrid_reasoning(user_input, intent, complexity)
            elif self.reasoning_mode == ReasoningMode.LOCAL_LLM and self.local_llm:
                result = self._local_llm_reasoning(user_input, complexity)
            elif self.reasoning_mode == ReasoningMode.CLOUD_LLM and self.cloud_llm_client:
                result = self._cloud_llm_reasoning(user_input, complexity)
            else:
                # Enhanced pattern-based reasoning with NLU
                result = self._nlu_pattern_reasoning(user_input, intent, complexity)
            
            # Step 4: Apply chain-of-thought if enabled and needed
            if self.enable_cot and complexity != TaskComplexity.SIMPLE:
                result = self._apply_chain_of_thought(result, intent)
            
            # Store interaction in memory
            self.memory_manager.store_interaction(user_input, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing input: {e}")
            return self._create_error_result(user_input, str(e))
    
    def _load_intent_patterns(self) -> Dict[str, List[str]]:
        """
        Load intent recognition patterns.
        
        Returns:
            Dict mapping intent names to regex patterns
        """
        return {
            'open_application': [
                r'open\s+(\w+)',
                r'launch\s+(\w+)',
                r'start\s+(\w+)'
            ],
            'web_search': [
                r'search\s+(?:for\s+)?(.+)',
                r'google\s+(.+)',
                r'look\s+up\s+(.+)'
            ],
            'system_control': [
                r'(shutdown|restart|sleep)\s*(?:the\s+)?(?:computer|system)?',
                r'(lock|unlock)\s+(?:the\s+)?(?:screen|computer)'
            ],
            'weather': [
                r'(?:what\'?s\s+the\s+)?weather\s*(?:like)?(?:\s+in\s+(.+))?',
                r'temperature\s*(?:in\s+(.+))?'
            ],
            'time_date': [
                r'(?:what\s+)?(?:time|date)\s+(?:is\s+)?it',
                r'current\s+(?:time|date)'
            ],
            'joke': [
                r'tell\s+(?:me\s+)?(?:a\s+)?joke',
                r'make\s+me\s+laugh'
            ],
            'stop_assistant': [
                r'(?:stop|exit|quit|goodbye|bye)',
                r'turn\s+off'
            ]
        }
    
    def _load_action_rules(self) -> Dict[str, Dict[str, Any]]:
        """
        Load action rules for intent-to-action mapping.
        
        Returns:
            Dict mapping intent names to action rules
        """
        return {
            'open_application': {
                'action_type': 'open_application',
                'parameters': {'app_name': str},
                'priority': 1
            },
            'web_search': {
                'action_type': 'web_search',
                'parameters': {'query': str},
                'priority': 1
            },
            'system_control': {
                'action_type': 'system_control',
                'parameters': {'command': str},
                'priority': 2
            },
            'weather': {
                'action_type': 'get_weather',
                'parameters': {'location': str},
                'priority': 1
            },
            'time_date': {
                'action_type': 'get_time_date',
                'parameters': {},
                'priority': 1
            },
            'joke': {
                'action_type': 'tell_joke',
                'parameters': {},
                'priority': 1
            }
        }
    
    def _analyze_intent_complexity(self, intent: Intent) -> TaskComplexity:
        """
        Analyze the complexity of an intent-based request.
        
        Args:
            intent: Classified intent from NLU
            
        Returns:
            TaskComplexity level
        """
        # Analyze based on intent type and entities
        word_count = len(intent.original_text.split())
        entity_count = len(intent.entities)
        
        # Complex intent types
        complex_intents = {
            IntentType.SEARCH,
            IntentType.QUESTION,
            IntentType.CONVERSATION,
            IntentType.FILE_OPERATION
        }
        
        # Moderate intent types
        moderate_intents = {
            IntentType.SYSTEM_CONTROL,
            IntentType.MUSIC,
            IntentType.EMAIL,
            IntentType.MESSAGE
        }
        
        # Check for complexity indicators in text
        complex_indicators = [
            "and then", "after that", "first", "second", "next",
            "multiple", "several", "both", "also", "additionally",
            "explain", "how to", "why", "because"
        ]
        
        # Determine complexity
        if (intent.type in complex_intents or 
            word_count > 15 or 
            entity_count > 3 or
            any(indicator in intent.original_text.lower() for indicator in complex_indicators)):
            return TaskComplexity.COMPLEX
        
        elif (intent.type in moderate_intents or 
              word_count > 8 or 
              entity_count > 1):
            return TaskComplexity.MODERATE
        
        else:
            return TaskComplexity.SIMPLE
    
    def _apply_chain_of_thought(self, result: ReasoningResult, intent: Intent) -> ReasoningResult:
        """
        Apply chain-of-thought reasoning to improve result quality.
        
        Args:
            result: Initial reasoning result
            intent: Original intent
            
        Returns:
            Enhanced ReasoningResult
        """
        try:
            cot_steps = []
            
            # Step 1: Analyze the request
            cot_steps.append(f"Analysis: User wants to {intent.type.value}")
            
            # Step 2: Consider context and entities
            if intent.entities:
                entity_summary = ", ".join([f"{e.type}: {e.value}" for e in intent.entities])
                cot_steps.append(f"Context: Entities found - {entity_summary}")
            
            # Step 3: Plan execution
            if result.actions:
                action_summary = ", ".join([a.get('type', 'unknown') for a in result.actions])
                cot_steps.append(f"Execution: Will perform - {action_summary}")
            
            # Step 4: Enhance response with reasoning
            enhanced_response = result.response
            if len(cot_steps) > 1:
                enhanced_response += f" I determined this by: {' -> '.join(cot_steps[1:])}"
            
            # Update result with chain-of-thought
            result.reasoning_steps.extend(cot_steps)
            result.response = enhanced_response
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in chain-of-thought reasoning: {e}")
            return result
    
    def _local_llm_reasoning(self, user_input: str, complexity: TaskComplexity) -> ReasoningResult:
        """Local LLM reasoning (placeholder for now)."""
        return ReasoningResult(
            intent="llm_response",
            confidence=0.8,
            actions=[],
            response="I would use local LLM to process this request, Sir.",
            reasoning_steps=["Local LLM processing"],
            complexity=complexity,
            requires_llm=True
        )
    
    def _cloud_llm_reasoning(self, user_input: str, complexity: TaskComplexity) -> ReasoningResult:
        """Cloud LLM reasoning (placeholder for now)."""
        return ReasoningResult(
            intent="llm_response", 
            confidence=0.8,
            actions=[],
            response="I would use cloud LLM to process this request, Sir.",
            reasoning_steps=["Cloud LLM processing"],
            complexity=complexity,
            requires_llm=True
        )
    
    def _create_error_result(self, user_input: str, error: str) -> ReasoningResult:
        """Create error result."""
        return ReasoningResult(
            intent="error",
            confidence=0.0,
            actions=[],
            response=f"I apologize, Sir, but I encountered an error: {error}",
            reasoning_steps=[f"Error: {error}"],
            complexity=TaskComplexity.SIMPLE,
            requires_llm=False
        )
    
    def _enhanced_hybrid_reasoning(self, user_input: str, intent: Intent, complexity: TaskComplexity) -> ReasoningResult:
        """
        Enhanced hybrid reasoning combining NLU with LLM when needed.
        
        Args:
            user_input: User input text
            intent: Classified intent from NLU
            complexity: Task complexity level
            
        Returns:
            ReasoningResult
        """
        # Start with NLU-based reasoning
        if intent.confidence >= 0.7 and intent.type != IntentType.UNKNOWN:
            # High confidence NLU result - use pattern-based approach
            return self._nlu_pattern_reasoning(user_input, intent, complexity)
        
        elif intent.type == IntentType.CONVERSATION or intent.type == IntentType.QUESTION:
            # Conversational or complex questions - use LLM
            return self._llm_fallback_reasoning(user_input, intent, complexity)
        
        elif complexity == TaskComplexity.COMPLEX:
            # Complex tasks - use LLM for planning
            return self._llm_fallback_reasoning(user_input, intent, complexity)
        
        else:
            # Medium confidence - try pattern first, fallback to LLM
            pattern_result = self._nlu_pattern_reasoning(user_input, intent, complexity)
            
            if pattern_result.confidence < 0.5:
                return self._llm_fallback_reasoning(user_input, intent, complexity)
            else:
                return pattern_result
    
    def _llm_fallback_reasoning(self, user_input: str, intent: Intent, complexity: TaskComplexity) -> ReasoningResult:
        """
        LLM-based reasoning for unknown or complex intents.
        
        Args:
            user_input: User input text
            intent: Classified intent from NLU
            complexity: Task complexity level
            
        Returns:
            ReasoningResult
        """
        try:
            # Try local LLM first if available
            if self.use_local_llm and self.local_llm:
                return self._local_llm_reasoning(user_input, complexity)
            
            # Try cloud LLM if available
            elif self.use_cloud_llm and self.cloud_llm_client:
                return self._cloud_llm_reasoning(user_input, complexity)
            
            else:
                # No LLM available - provide helpful fallback
                return self._create_helpful_fallback(user_input, intent)
                
        except Exception as e:
            self.logger.error(f"Error in LLM fallback reasoning: {e}")
            return self._create_helpful_fallback(user_input, intent)
    
    def _create_helpful_fallback(self, user_input: str, intent: Intent) -> ReasoningResult:
        """
        Create a helpful fallback response when LLM is not available.
        
        Args:
            user_input: User input text
            intent: Classified intent from NLU
            
        Returns:
            ReasoningResult with helpful suggestions
        """
        # Analyze what the user might want
        suggestions = []
        
        if "open" in user_input.lower():
            suggestions.extend(["open calculator", "open notepad", "open wikipedia"])
        
        if any(word in user_input.lower() for word in ["what", "how", "when", "where"]):
            suggestions.extend(["what time is it", "what's the date", "how are you"])
        
        if "tell" in user_input.lower():
            suggestions.append("tell me a joke")
        
        # Create response
        if suggestions:
            response = f"I'm not sure about '{user_input}', Sir. Perhaps you meant one of these: {', '.join(suggestions[:3])}"
        else:
            response = f"I understand you said '{user_input}', Sir, but I'm not sure how to help with that specific request. You can ask me to open apps, get the time/date, tell jokes, or search for information."
        
        return ReasoningResult(
            intent="unknown_helpful",
            confidence=0.3,
            actions=[],
            response=response,
            reasoning_steps=["Fallback reasoning with suggestions"],
            complexity=TaskComplexity.SIMPLE,
            requires_llm=False,
            suggestions=suggestions[:3]
        )
    
    def _nlu_pattern_reasoning(self, user_input: str, intent: Intent, complexity: TaskComplexity) -> ReasoningResult:
        """
        Enhanced pattern-based reasoning using NLU engine results.
        
        Args:
            user_input: User input text
            intent: Classified intent from NLU
            complexity: Task complexity level
            
        Returns:
            ReasoningResult
        """
        try:
            # Generate actions based on NLU intent
            actions = self._generate_actions_for_nlu_intent(intent)
            
            # Generate contextual response
            response = self._generate_contextual_response(intent)
            
            # Build reasoning steps
            reasoning_steps = [
                f"NLU Classification: {intent.type.value} (confidence: {intent.confidence:.2f})",
                f"Entities extracted: {len(intent.entities)}",
                f"Actions planned: {len(actions)}"
            ]
            
            return ReasoningResult(
                intent=intent.type.value,
                confidence=intent.confidence,
                actions=actions,
                response=response,
                reasoning_steps=reasoning_steps,
                complexity=complexity,
                requires_llm=False,
                entities=intent.entities,
                parameters=intent.parameters
            )
            
        except Exception as e:
            self.logger.error(f"Error in NLU pattern reasoning: {e}")
            return self._create_error_result(user_input, str(e))
