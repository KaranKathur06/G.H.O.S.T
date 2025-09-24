"""
Decision-Making & Clarification Engine for G.H.O.S.T.

This module handles intelligent decision-making, clarification requests,
and proactive interaction management for the autonomous AI assistant.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json

class DecisionType(Enum):
    """Types of decisions the engine can make."""
    DIRECT_EXECUTION = "direct_execution"      # Clear request, execute immediately
    CLARIFICATION_NEEDED = "clarification"    # Need more information
    CONFIRMATION_REQUIRED = "confirmation"    # Dangerous action, need confirmation
    MULTIPLE_OPTIONS = "multiple_options"     # Multiple valid options available
    PROACTIVE_SUGGESTION = "proactive"        # Suggest helpful actions
    CONTEXT_DEPENDENT = "context_dependent"   # Need more context

@dataclass
class DecisionOption:
    """A possible decision option."""
    id: str
    description: str
    action_type: str
    parameters: Dict[str, Any]
    confidence: float
    risk_level: str = "low"  # low, medium, high
    estimated_time: float = 0.0
    prerequisites: List[str] = field(default_factory=list)

@dataclass
class DecisionResult:
    """Result of decision-making process."""
    decision_type: DecisionType
    chosen_option: Optional[DecisionOption] = None
    available_options: List[DecisionOption] = field(default_factory=list)
    clarification_question: str = ""
    confidence: float = 0.0
    reasoning: List[str] = field(default_factory=list)
    requires_user_input: bool = False
    timeout_seconds: float = 30.0

@dataclass
class ConversationState:
    """Current state of conversation with user."""
    pending_decision: Optional[DecisionResult] = None
    last_user_input: str = ""
    last_response: str = ""
    context_history: List[Dict[str, Any]] = field(default_factory=list)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    current_task: str = ""
    awaiting_response: bool = False
    response_deadline: Optional[datetime] = None

class DecisionEngine:
    """
    Intelligent Decision-Making & Clarification Engine.
    
    Handles:
    - Analyzing user requests for clarity and completeness
    - Making intelligent decisions about action execution
    - Asking clarifying questions when needed
    - Managing conversation flow and context
    - Providing proactive suggestions
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize Decision Engine."""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Conversation state
        self.conversation_state = ConversationState()
        
        # Decision-making configuration
        self.confidence_threshold = self.config.get('confidence_threshold', 0.7)
        self.clarification_threshold = self.config.get('clarification_threshold', 0.4)
        self.max_options_to_show = self.config.get('max_options_to_show', 5)
        self.default_timeout = self.config.get('default_timeout', 30.0)
        
        # Risk assessment
        self.high_risk_actions = {
            'system_control', 'file_deletion', 'shutdown', 'restart',
            'format', 'delete', 'uninstall'
        }
        
        # User preference learning
        self.preference_weights = {
            'platform_preference': 0.3,
            'action_frequency': 0.2,
            'time_of_day': 0.1,
            'recent_choices': 0.4
        }
        
        self.logger.info("Decision Engine initialized")
    
    async def make_decision(self, request, search_results: List[Any] = None, 
                          context: Dict[str, Any] = None) -> DecisionResult:
        """
        Make an intelligent decision about how to handle a request.
        
        Args:
            request: Universal request from NLU
            search_results: Available options from system search
            context: Additional context information
            
        Returns:
            DecisionResult with decision and reasoning
        """
        try:
            self.logger.debug(f"Making decision for: {request.original_text}")
            
            # Update conversation context
            self._update_conversation_context(request, context)
            
            # Analyze request clarity and completeness
            clarity_score = self._assess_request_clarity(request)
            
            # Generate possible options
            options = await self._generate_decision_options(request, search_results, context)
            
            # Apply decision logic
            decision = await self._apply_decision_logic(request, options, clarity_score)
            
            # Store decision for potential follow-up
            self.conversation_state.pending_decision = decision
            
            return decision
            
        except Exception as e:
            self.logger.error(f"Error in decision making: {e}")
            return DecisionResult(
                decision_type=DecisionType.DIRECT_EXECUTION,
                clarification_question="I encountered an issue processing your request, Sir. Could you please try again?",
                requires_user_input=True
            )
    
    def _update_conversation_context(self, request, context: Dict[str, Any] = None):
        """Update conversation context with new information."""
        self.conversation_state.last_user_input = request.original_text
        self.conversation_state.current_task = request.intent.value
        
        # Add to context history
        context_entry = {
            'timestamp': datetime.now(),
            'user_input': request.original_text,
            'intent': request.intent.value,
            'entities': [{'type': e.type, 'value': e.value} for e in request.entities],
            'confidence': request.confidence
        }
        
        if context:
            context_entry.update(context)
        
        self.conversation_state.context_history.append(context_entry)
        
        # Keep only recent context (last 10 interactions)
        if len(self.conversation_state.context_history) > 10:
            self.conversation_state.context_history = self.conversation_state.context_history[-10:]
    
    def _assess_request_clarity(self, request) -> float:
        """Assess how clear and complete the request is."""
        clarity_score = 0.0
        
        # Base score from NLU confidence
        clarity_score += request.confidence * 0.4
        
        # Check for specific entities
        if request.entities:
            clarity_score += min(len(request.entities) * 0.1, 0.3)
        
        # Check for action verb
        if request.action_verb:
            clarity_score += 0.2
        
        # Check for target object
        if request.target_object:
            clarity_score += 0.2
        
        # Penalty for ambiguous words
        ambiguous_words = ['it', 'that', 'this', 'something', 'anything']
        if any(word in request.processed_text.lower() for word in ambiguous_words):
            clarity_score -= 0.1
        
        return max(0.0, min(1.0, clarity_score))
    
    async def _generate_decision_options(self, request, search_results: List[Any] = None, 
                                       context: Dict[str, Any] = None) -> List[DecisionOption]:
        """Generate possible decision options for the request."""
        options = []
        
        try:
            # Generate options based on intent type
            if hasattr(request.intent, 'value'):
                intent_value = request.intent.value
            else:
                intent_value = str(request.intent)
            
            if intent_value == "play_media":
                options.extend(await self._generate_media_options(request, search_results))
            
            elif intent_value == "open_application":
                options.extend(await self._generate_app_options(request, search_results))
            
            elif intent_value == "open_file":
                options.extend(await self._generate_file_options(request, search_results))
            
            elif intent_value == "search_web":
                options.extend(await self._generate_search_options(request))
            
            elif intent_value == "system_control":
                options.extend(await self._generate_system_options(request))
            
            # Add generic options if no specific ones found
            if not options:
                options.extend(await self._generate_generic_options(request))
            
            # Sort options by confidence and user preferences
            options = self._rank_options(options)
            
            return options[:self.max_options_to_show]
            
        except Exception as e:
            self.logger.error(f"Error generating decision options: {e}")
            return []
    
    async def _generate_media_options(self, request, search_results: List[Any] = None) -> List[DecisionOption]:
        """Generate media playback options."""
        options = []
        content = request.target_object
        
        if not content:
            return options
        
        # YouTube option
        options.append(DecisionOption(
            id="youtube_play",
            description=f"Play '{content}' on YouTube",
            action_type="play_media",
            parameters={"content": content, "platform": "youtube"},
            confidence=0.8
        ))
        
        # Spotify option
        options.append(DecisionOption(
            id="spotify_play",
            description=f"Play '{content}' on Spotify",
            action_type="play_media",
            parameters={"content": content, "platform": "spotify"},
            confidence=0.7
        ))
        
        # Local files option
        if search_results:
            local_media = [r for r in search_results if self._is_media_file(r)]
            if local_media:
                options.append(DecisionOption(
                    id="local_play",
                    description=f"Play '{content}' from local files",
                    action_type="play_media",
                    parameters={"content": content, "platform": "local"},
                    confidence=0.9
                ))
        
        return options
    
    async def _generate_app_options(self, request, search_results: List[Any] = None) -> List[DecisionOption]:
        """Generate application opening options."""
        options = []
        app_name = request.target_object
        
        if search_results:
            for i, result in enumerate(search_results[:3]):
                if hasattr(result, 'item'):
                    item = result.item
                    confidence = 0.9 - (i * 0.1)  # Decrease confidence for lower-ranked results
                    
                    options.append(DecisionOption(
                        id=f"app_{i}",
                        description=f"Open {item.name}",
                        action_type="open_application",
                        parameters={"app_name": item.name, "path": item.path},
                        confidence=confidence
                    ))
        
        return options
    
    async def _generate_search_options(self, request) -> List[DecisionOption]:
        """Generate web search options."""
        options = []
        query = request.target_object
        
        if not query:
            return options
        
        search_engines = [
            ("google", "Google", 0.9),
            ("bing", "Bing", 0.7),
            ("duckduckgo", "DuckDuckGo", 0.6)
        ]
        
        for engine_id, engine_name, confidence in search_engines:
            options.append(DecisionOption(
                id=f"search_{engine_id}",
                description=f"Search for '{query}' on {engine_name}",
                action_type="web_search",
                parameters={"query": query, "platform": engine_id},
                confidence=confidence
            ))
        
        return options
    
    async def _generate_system_options(self, request) -> List[DecisionOption]:
        """Generate system control options."""
        options = []
        command = request.target_object.lower() if request.target_object else ""
        
        if "shutdown" in command:
            options.append(DecisionOption(
                id="shutdown",
                description="Shutdown the system",
                action_type="system_control",
                parameters={"command": "shutdown"},
                confidence=0.9,
                risk_level="high"
            ))
        
        elif "restart" in command:
            options.append(DecisionOption(
                id="restart",
                description="Restart the system",
                action_type="system_control",
                parameters={"command": "restart"},
                confidence=0.9,
                risk_level="high"
            ))
        
        return options
    
    async def _generate_generic_options(self, request) -> List[DecisionOption]:
        """Generate generic fallback options."""
        return [
            DecisionOption(
                id="clarify",
                description="Ask for clarification",
                action_type="clarification",
                parameters={"original_request": request.original_text},
                confidence=0.5
            )
        ]
    
    def _rank_options(self, options: List[DecisionOption]) -> List[DecisionOption]:
        """Rank options based on confidence and user preferences."""
        def option_score(option):
            score = option.confidence
            
            # Apply user preference weights
            if option.action_type in self.conversation_state.user_preferences:
                preference_boost = self.conversation_state.user_preferences[option.action_type]
                score += preference_boost * self.preference_weights['platform_preference']
            
            # Penalty for high-risk actions
            if option.risk_level == "high":
                score -= 0.2
            elif option.risk_level == "medium":
                score -= 0.1
            
            return score
        
        return sorted(options, key=option_score, reverse=True)
    
    async def _apply_decision_logic(self, request, options: List[DecisionOption], 
                                  clarity_score: float) -> DecisionResult:
        """Apply decision logic to determine the best course of action."""
        reasoning = []
        
        # Check if request is clear enough
        if clarity_score < self.clarification_threshold:
            reasoning.append(f"Request clarity score: {clarity_score:.2f} (below threshold)")
            return DecisionResult(
                decision_type=DecisionType.CLARIFICATION_NEEDED,
                available_options=options,
                clarification_question=self._generate_clarification_question(request, options),
                confidence=clarity_score,
                reasoning=reasoning,
                requires_user_input=True
            )
        
        # Check if we have no valid options
        if not options:
            reasoning.append("No valid options found")
            return DecisionResult(
                decision_type=DecisionType.CLARIFICATION_NEEDED,
                clarification_question=f"I'm not sure how to help with '{request.original_text}', Sir. Could you provide more details?",
                confidence=0.0,
                reasoning=reasoning,
                requires_user_input=True
            )
        
        # Check if top option is high confidence
        top_option = options[0]
        if top_option.confidence >= self.confidence_threshold:
            reasoning.append(f"High confidence option: {top_option.confidence:.2f}")
            
            # Check if it's a high-risk action
            if top_option.risk_level == "high":
                reasoning.append("High-risk action requires confirmation")
                return DecisionResult(
                    decision_type=DecisionType.CONFIRMATION_REQUIRED,
                    chosen_option=top_option,
                    available_options=options,
                    clarification_question=f"Are you sure you want me to {top_option.description.lower()}, Sir?",
                    confidence=top_option.confidence,
                    reasoning=reasoning,
                    requires_user_input=True
                )
            else:
                reasoning.append("Proceeding with direct execution")
                return DecisionResult(
                    decision_type=DecisionType.DIRECT_EXECUTION,
                    chosen_option=top_option,
                    available_options=options,
                    confidence=top_option.confidence,
                    reasoning=reasoning,
                    requires_user_input=False
                )
        
        # Multiple reasonable options
        if len(options) > 1 and options[1].confidence > 0.5:
            reasoning.append(f"Multiple options with reasonable confidence")
            return DecisionResult(
                decision_type=DecisionType.MULTIPLE_OPTIONS,
                available_options=options,
                clarification_question=self._generate_options_question(options),
                confidence=top_option.confidence,
                reasoning=reasoning,
                requires_user_input=True
            )
        
        # Single option with medium confidence
        reasoning.append(f"Single option with medium confidence: {top_option.confidence:.2f}")
        return DecisionResult(
            decision_type=DecisionType.DIRECT_EXECUTION,
            chosen_option=top_option,
            available_options=options,
            confidence=top_option.confidence,
            reasoning=reasoning,
            requires_user_input=False
        )
    
    def _generate_clarification_question(self, request, options: List[DecisionOption]) -> str:
        """Generate an appropriate clarification question."""
        if hasattr(request.intent, 'value'):
            intent_value = request.intent.value
        else:
            intent_value = str(request.intent)
        
        if intent_value == "play_media" and not request.target_object:
            return "What would you like me to play, Sir?"
        
        elif intent_value == "open_application" and not request.target_object:
            return "Which application would you like me to open, Sir?"
        
        elif intent_value == "search_web" and not request.target_object:
            return "What would you like me to search for, Sir?"
        
        elif options:
            return f"I found several ways to handle '{request.original_text}', Sir. Which would you prefer?"
        
        else:
            return f"Could you please provide more details about '{request.original_text}', Sir?"
    
    def _generate_options_question(self, options: List[DecisionOption]) -> str:
        """Generate a question presenting multiple options."""
        if len(options) <= 3:
            option_descriptions = [opt.description for opt in options]
            if len(option_descriptions) == 2:
                return f"I can {option_descriptions[0]} or {option_descriptions[1]}, Sir. Which would you prefer?"
            else:
                options_str = ", ".join(option_descriptions[:-1]) + f", or {option_descriptions[-1]}"
                return f"I can {options_str}, Sir. Which would you like?"
        else:
            return f"I found {len(options)} options, Sir. The top choices are: {', '.join([opt.description for opt in options[:3]])}. Which would you prefer?"
    
    async def handle_user_response(self, response: str) -> Optional[DecisionOption]:
        """Handle user response to clarification question."""
        if not self.conversation_state.pending_decision:
            return None
        
        try:
            pending = self.conversation_state.pending_decision
            response_lower = response.lower().strip()
            
            # Handle confirmation responses
            if pending.decision_type == DecisionType.CONFIRMATION_REQUIRED:
                if any(word in response_lower for word in ['yes', 'confirm', 'proceed', 'do it']):
                    return pending.chosen_option
                elif any(word in response_lower for word in ['no', 'cancel', 'stop', 'abort']):
                    return None
            
            # Handle option selection
            elif pending.decision_type == DecisionType.MULTIPLE_OPTIONS:
                # Try to match response to option
                for i, option in enumerate(pending.available_options):
                    # Check for numeric selection
                    if str(i + 1) in response_lower or f"option {i + 1}" in response_lower:
                        return option
                    
                    # Check for keyword matching
                    option_keywords = option.description.lower().split()
                    if any(keyword in response_lower for keyword in option_keywords if len(keyword) > 3):
                        return option
            
            # Clear pending decision
            self.conversation_state.pending_decision = None
            return None
            
        except Exception as e:
            self.logger.error(f"Error handling user response: {e}")
            return None
    
    def generate_proactive_suggestion(self, context: Dict[str, Any]) -> Optional[str]:
        """Generate proactive suggestions based on context."""
        try:
            current_time = datetime.now()
            
            # Time-based suggestions
            if current_time.hour < 12:
                return "Good morning, Sir. Would you like me to provide your daily briefing?"
            
            elif current_time.hour > 18:
                return "Good evening, Sir. Is there anything you'd like me to prepare for tomorrow?"
            
            # Context-based suggestions
            if context.get('last_action') == 'open_application':
                return "Would you like me to open any related files or documents, Sir?"
            
            elif context.get('last_action') == 'play_media':
                return "Shall I adjust the volume or create a playlist, Sir?"
            
            elif context.get('system_idle_time', 0) > 300:  # 5 minutes idle
                return "I'm here if you need assistance with anything, Sir."
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error generating proactive suggestion: {e}")
            return None
    
    def learn_from_decision(self, decision: DecisionResult, user_choice: str, outcome: bool):
        """Learn from decision outcomes to improve future decisions."""
        try:
            if outcome and decision.chosen_option:
                # Successful decision - boost preference
                action_type = decision.chosen_option.action_type
                current_pref = self.conversation_state.user_preferences.get(action_type, 0.0)
                self.conversation_state.user_preferences[action_type] = min(1.0, current_pref + 0.1)
            
            elif not outcome:
                # Failed decision - reduce preference
                if decision.chosen_option:
                    action_type = decision.chosen_option.action_type
                    current_pref = self.conversation_state.user_preferences.get(action_type, 0.0)
                    self.conversation_state.user_preferences[action_type] = max(0.0, current_pref - 0.05)
            
            self.logger.debug(f"Learning from decision outcome: {outcome}")
            
        except Exception as e:
            self.logger.error(f"Error learning from decision: {e}")
    
    def _is_media_file(self, search_result) -> bool:
        """Check if search result is a media file."""
        if hasattr(search_result, 'item') and hasattr(search_result.item, 'path'):
            media_extensions = {'.mp3', '.wav', '.mp4', '.avi', '.mkv', '.mov'}
            return any(search_result.item.path.lower().endswith(ext) for ext in media_extensions)
        return False
    
    def get_conversation_state(self) -> Dict[str, Any]:
        """Get current conversation state."""
        return {
            'has_pending_decision': self.conversation_state.pending_decision is not None,
            'awaiting_response': self.conversation_state.awaiting_response,
            'current_task': self.conversation_state.current_task,
            'context_history_length': len(self.conversation_state.context_history),
            'user_preferences': self.conversation_state.user_preferences
        }
    
    def reset_conversation(self):
        """Reset conversation state."""
        self.conversation_state = ConversationState()
        self.logger.info("Conversation state reset")
    
    def cleanup(self):
        """Clean up resources."""
        self.logger.info("Decision Engine cleaned up")
