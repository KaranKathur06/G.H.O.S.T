"""
LLM-Based Reasoning Brain for G.H.O.S.T.

This module provides ChatGPT-style reasoning capabilities using local and cloud LLMs.
Enables G.H.O.S.T. to understand, reason about, and respond to any request intelligently.
"""

import os
import re
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
# OpenAI support
try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None
    OpenAI = None

# Local LLM support
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    ollama = None

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

@dataclass
class LLMResponse:
    """Response from LLM with metadata."""
    content: str
    confidence: float
    reasoning_steps: List[str] = field(default_factory=list)
    tokens_used: int = 0
    response_time: float = 0.0
    model_used: str = ""
    requires_action: bool = False
    suggested_actions: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class ConversationContext:
    """Context for ongoing conversation."""
    messages: List[Dict[str, str]] = field(default_factory=list)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    current_topic: str = ""
    last_action: str = ""
    session_start: datetime = field(default_factory=datetime.now)

class LLMBrain:
    """
    LLM-Based Reasoning Brain for G.H.O.S.T.
    
    Provides intelligent reasoning, conversation, and decision-making
    using various LLM backends (OpenAI, Ollama, local models).
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize LLM Brain."""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # LLM Configuration
        self.use_openai = self.config.get('use_openai', False)
        self.use_ollama = self.config.get('use_ollama', True)
        self.use_local = self.config.get('use_local', False)
        
        # OpenAI settings - upgraded to use gpt-4o-mini for better performance
        self.openai_api_key = self.config.get('openai_api_key') or os.getenv('OPENAI_API_KEY')
        self.openai_model = self.config.get('openai_model', 'gpt-4o-mini')  # Better model
        self.openai_client = None
        
        # Structured response settings
        self.use_structured_responses = self.config.get('use_structured_responses', True)
        self.immediate_ack = self.config.get('immediate_ack', True)
        
        # Ollama settings
        self.ollama_model = self.config.get('ollama_model', 'llama2')
        self.ollama_host = self.config.get('ollama_host', 'http://localhost:11434')
        
        # Local model settings
        self.local_model = self.config.get('local_model', 'microsoft/DialoGPT-medium')
        self.local_pipeline = None
        
        # Conversation management
        self.conversation_context = ConversationContext()
        self.max_context_length = self.config.get('max_context_length', 4000)
        self.max_response_tokens = self.config.get('max_response_tokens', 500)
        
        # G.H.O.S.T. personality
        self.personality_prompt = self._create_personality_prompt()
        
        # Initialize LLM backends
        self._initialize_llm_backends()
        
        self.logger.info("LLM Brain initialized")
    
    def _create_personality_prompt(self) -> str:
        """Create G.H.O.S.T.'s personality prompt with structured response requirements."""
        return """You are G.H.O.S.T. (Generative Hybrid Omnipresent Support Technology), an advanced AI assistant similar to J.A.R.V.I.S. from Iron Man.

PERSONALITY TRAITS:
- Professional, polite, and respectful
- Always address the user as "Sir" 
- Slightly witty and sophisticated
- Helpful and proactive
- Confident but not arrogant
- Formal speech pattern

CAPABILITIES:
- Control computer systems and applications
- Search and retrieve information
- Manage files and folders
- Play media content
- Answer questions and provide explanations
- Assist with productivity tasks
- Engage in natural conversation

IMPORTANT: You must ALWAYS respond with valid JSON in this exact format:
{
  "reply_text": "Your spoken response to the user",
  "action": {
    "type": "action_name",
    "parameters": {
      "key": "value"
    }
  }
}

If no action is needed, use:
{
  "reply_text": "Your response",
  "action": null
}

AVAILABLE ACTIONS:
- "open_application": {"app_name": "application name"}
- "open_web": {"url": "website URL"}
- "search_web": {"query": "search terms"}
- "open_system_item": {"path": "file/folder path"}
- "play_media": {"content": "media name", "source": "youtube/spotify/local"}
- "tell_joke": {"topic": "joke category"}
- "get_time": {}
- "get_weather": {"location": "city name"}
- "system_command": {"command": "system command"}

RESPONSE STYLE:
- Always end responses with "Sir" when appropriate
- Use formal language but remain conversational
- Provide clear, actionable responses
- Ask clarifying questions when needed
- Offer helpful suggestions
- Confirm important actions before execution

EXAMPLE RESPONSES:
{
  "reply_text": "Certainly, Sir. I'll open that application for you.",
  "action": {"type": "open_application", "parameters": {"app_name": "calculator"}}
}

{
  "reply_text": "I found several results for your search, Sir. Which would you prefer?",
  "action": null
}

Remember: You are an intelligent, capable assistant. ALWAYS respond with valid JSON only."""
    
    def _initialize_llm_backends(self):
        """Initialize available LLM backends."""
        try:
            # Initialize OpenAI
            if self.use_openai and self.openai_api_key:
                self.openai_client = OpenAI(api_key=self.openai_api_key)
                self.logger.info("OpenAI client initialized")
            
            # Initialize local model
            if self.use_local and TRANSFORMERS_AVAILABLE:
                try:
                    self.local_pipeline = pipeline(
                        "text-generation",
                        model=self.local_model,
                        tokenizer=self.local_model,
                        device=-1  # CPU
                    )
                    self.logger.info(f"Local model {self.local_model} initialized")
                except Exception as e:
                    self.logger.warning(f"Failed to initialize local model: {e}")
                    self.use_local = False
            
            # Check Ollama availability
            if self.use_ollama and OLLAMA_AVAILABLE:
                try:
                    # Test connection
                    ollama.list()
                    self.logger.info("Ollama connection established")
                except Exception as e:
                    self.logger.warning(f"Ollama not available: {e}")
                    self.use_ollama = False
            
        except Exception as e:
            self.logger.error(f"Error initializing LLM backends: {e}")
    
    async def reason(self, query: str, context: Dict[str, Any] = None) -> LLMResponse:
        """
        Process query using LLM reasoning with structured JSON responses.
        
        Args:
            query: User query or request
            context: Additional context information
            
        Returns:
            LLMResponse with structured reasoning and actions
        """
        try:
            start_time = datetime.now()
            
            # Provide immediate acknowledgment if requested
            if self.immediate_ack and context and context.get('provide_ack', False):
                # This would be handled by the calling system
                pass
            
            # Prepare context
            full_context = self._prepare_context(query, context)
            
            # Try different LLM backends in order of preference
            response = None
            
            if self.use_openai and self.openai_client:
                response = await self._query_openai(full_context)
            
            elif self.use_ollama and OLLAMA_AVAILABLE:
                response = await self._query_ollama(full_context)
            
            elif self.use_local and self.local_pipeline:
                response = await self._query_local_model(full_context)
            
            else:
                # Fallback to rule-based response
                response = self._create_fallback_response(query)
            
            # Calculate response time
            response.response_time = (datetime.now() - start_time).total_seconds()
            
            # Update conversation context
            self._update_conversation_context(query, response.content)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error in LLM reasoning: {e}")
            return self._create_error_response(query, str(e))
    
    def get_immediate_ack(self) -> str:
        """Get immediate acknowledgment message while processing."""
        ack_messages = [
            "Working on it, Sir.",
            "Processing your request, Sir.",
            "One moment, Sir.",
            "Certainly, Sir. Let me handle that.",
            "Right away, Sir."
        ]
        import random
        return random.choice(ack_messages)
    
    def _prepare_context(self, query: str, context: Dict[str, Any] = None) -> str:
        """Prepare full context for LLM."""
        context_parts = [self.personality_prompt]
        
        # Add conversation history
        if self.conversation_context.messages:
            context_parts.append("\\nCONVERSATION HISTORY:")
            for msg in self.conversation_context.messages[-5:]:  # Last 5 messages
                context_parts.append(f"{msg['role']}: {msg['content']}")
        
        # Add current context
        if context:
            context_parts.append("\\nCURRENT CONTEXT:")
            
            if 'intent' in context:
                context_parts.append(f"Detected Intent: {context['intent']}")
            
            if 'entities' in context:
                entities_str = ", ".join([f"{e['type']}: {e['value']}" for e in context['entities']])
                context_parts.append(f"Extracted Entities: {entities_str}")
            
            if 'system_info' in context:
                context_parts.append(f"System Information: {context['system_info']}")
            
            if 'search_results' in context:
                context_parts.append(f"Available Options: {context['search_results']}")
        
        # Add current query
        context_parts.append(f"\\nUSER REQUEST: {query}")
        context_parts.append("\\nRESPONSE:")
        
        return "\\n".join(context_parts)
    
    async def _query_openai(self, context: str) -> LLMResponse:
        """Query OpenAI GPT models with structured JSON response."""
        try:
            messages = [
                {"role": "system", "content": self.personality_prompt},
                {"role": "user", "content": context}
            ]
            
            response = self.openai_client.chat.completions.create(
                model=self.openai_model,
                messages=messages,
                max_tokens=self.max_response_tokens,
                temperature=0.7,
                response_format={"type": "json_object"}  # Force JSON response
            )
            
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            # Parse structured JSON response
            parsed_response = self._parse_structured_response(content)
            
            return LLMResponse(
                content=parsed_response.get('reply_text', content),
                confidence=0.9,
                tokens_used=tokens_used,
                model_used=self.openai_model,
                requires_action=parsed_response.get('action') is not None,
                suggested_actions=[parsed_response.get('action')] if parsed_response.get('action') else []
            )
            
        except Exception as e:
            self.logger.error(f"OpenAI query error: {e}")
            raise
    
    async def _query_ollama(self, context: str) -> LLMResponse:
        """Query Ollama local models."""
        try:
            response = ollama.generate(
                model=self.ollama_model,
                prompt=context,
                options={
                    'temperature': 0.7,
                    'max_tokens': self.max_response_tokens
                }
            )
            
            content = response['response']
            
            # Analyze response for actions
            requires_action, suggested_actions = self._analyze_response_for_actions(content)
            
            return LLMResponse(
                content=content,
                confidence=0.8,
                model_used=self.ollama_model,
                requires_action=requires_action,
                suggested_actions=suggested_actions
            )
            
        except Exception as e:
            self.logger.error(f"Ollama query error: {e}")
            raise
    
    async def _query_local_model(self, context: str) -> LLMResponse:
        """Query local transformer model."""
        try:
            # Truncate context if too long
            if len(context) > self.max_context_length:
                context = context[-self.max_context_length:]
            
            response = self.local_pipeline(
                context,
                max_length=len(context) + self.max_response_tokens,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.local_pipeline.tokenizer.eos_token_id
            )
            
            generated_text = response[0]['generated_text']
            content = generated_text[len(context):].strip()
            
            # Analyze response for actions
            requires_action, suggested_actions = self._analyze_response_for_actions(content)
            
            return LLMResponse(
                content=content,
                confidence=0.7,
                model_used=self.local_model,
                requires_action=requires_action,
                suggested_actions=suggested_actions
            )
            
        except Exception as e:
            self.logger.error(f"Local model query error: {e}")
            raise
    
    def _parse_structured_response(self, content: str) -> Dict[str, Any]:
        """Parse structured JSON response from LLM."""
        try:
            # Try to parse as JSON
            import json
            parsed = json.loads(content)
            
            # Validate required fields
            if 'reply_text' not in parsed:
                self.logger.warning("Missing reply_text in structured response")
                parsed['reply_text'] = "I understand your request, Sir."
            
            # Ensure action is properly formatted
            if 'action' in parsed and parsed['action'] is not None:
                action = parsed['action']
                if not isinstance(action, dict) or 'type' not in action:
                    self.logger.warning("Invalid action format in structured response")
                    parsed['action'] = None
                else:
                    # Ensure parameters exist
                    if 'parameters' not in action:
                        action['parameters'] = {}
            
            return parsed
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON response: {e}")
            # Fallback to text-only response
            return {
                'reply_text': content,
                'action': None
            }
        except Exception as e:
            self.logger.error(f"Error parsing structured response: {e}")
            return {
                'reply_text': "I apologize, Sir, but I encountered an issue processing your request.",
                'action': None
            }
    
    def _analyze_response_for_actions(self, content: str) -> Tuple[bool, List[Dict[str, Any]]]:
        """Legacy method - kept for compatibility with non-structured responses."""
        requires_action = False
        suggested_actions = []
        
        # Look for action indicators
        action_indicators = [
            "i'll open", "i'll launch", "i'll search", "i'll play",
            "let me open", "let me search", "let me find",
            "opening", "launching", "searching", "playing"
        ]
        
        content_lower = content.lower()
        
        for indicator in action_indicators:
            if indicator in content_lower:
                requires_action = True
                break
        
        # Extract specific actions
        if "open" in content_lower:
            # Try to extract what to open
            open_match = re.search(r"open\s+([\w\s]+)", content_lower)
            if open_match:
                target = open_match.group(1).strip()
                suggested_actions.append({
                    "type": "open_application",
                    "parameters": {"app_name": target},
                    "description": f"Open {target}"
                })
        
        if "search" in content_lower:
            # Try to extract search query
            search_match = re.search(r"search\s+(?:for\s+)?([\w\s]+)", content_lower)
            if search_match:
                query = search_match.group(1).strip()
                suggested_actions.append({
                    "type": "search_web",
                    "parameters": {"query": query},
                    "description": f"Search for {query}"
                })
        
        if "play" in content_lower:
            # Try to extract what to play
            play_match = re.search(r"play\s+([\w\s]+)", content_lower)
            if play_match:
                content_name = play_match.group(1).strip()
                suggested_actions.append({
                    "type": "play_media",
                    "parameters": {"content": content_name, "source": "youtube"},
                    "description": f"Play {content_name}"
                })
        
        return requires_action, suggested_actions
    
    def _create_fallback_response(self, query: str) -> LLMResponse:
        """Create structured fallback response when no LLM is available."""
        fallback_responses = {
            "greeting": {
                "reply_text": "Good day, Sir. How may I assist you today?",
                "action": None
            },
            "time": {
                "reply_text": "Certainly, Sir. Let me get the current time for you.",
                "action": {"type": "get_time", "parameters": {}}
            },
            "weather": {
                "reply_text": "I can assist with weather information, Sir. Which location would you like?",
                "action": None
            },
            "search": {
                "reply_text": "I can help you search for information, Sir. What would you like to search for?",
                "action": None
            },
            "open": {
                "reply_text": "I can help you open applications or files, Sir. What would you like me to open?",
                "action": None
            },
            "default": {
                "reply_text": "I understand your request, Sir. How would you like me to proceed?",
                "action": None
            }
        }
        
        query_lower = query.lower()
        
        for key, response_data in fallback_responses.items():
            if key in query_lower:
                return LLMResponse(
                    content=response_data["reply_text"],
                    confidence=0.6,
                    model_used="fallback",
                    reasoning_steps=["Used fallback response pattern"],
                    requires_action=response_data["action"] is not None,
                    suggested_actions=[response_data["action"]] if response_data["action"] else []
                )
        
        default_response = fallback_responses["default"]
        return LLMResponse(
            content=default_response["reply_text"],
            confidence=0.5,
            model_used="fallback",
            requires_action=False,
            suggested_actions=[]
        )
    
    def _create_error_response(self, query: str, error: str) -> LLMResponse:
        """Create structured error response."""
        return LLMResponse(
            content="I apologize, Sir, but I encountered an issue processing your request. Please try again.",
            confidence=0.0,
            model_used="error",
            reasoning_steps=[f"Error: {error}"],
            requires_action=False,
            suggested_actions=[]
        )
    
    def _update_conversation_context(self, user_input: str, assistant_response: str):
        """Update conversation context with new exchange."""
        self.conversation_context.messages.extend([
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": assistant_response}
        ])
        
        # Keep only recent messages to manage context length
        if len(self.conversation_context.messages) > 20:
            self.conversation_context.messages = self.conversation_context.messages[-20:]
    
    def ask_clarification(self, options: List[str], context: str = "") -> str:
        """Generate clarification question with options."""
        if len(options) == 1:
            return f"Did you mean {options[0]}, Sir?"
        
        elif len(options) <= 3:
            options_str = ", ".join(options[:-1]) + f", or {options[-1]}"
            return f"I found several options, Sir. Did you mean {options_str}?"
        
        else:
            return f"I found {len(options)} options, Sir. Could you be more specific? The top choices are: {', '.join(options[:3])}."
    
    def generate_proactive_suggestion(self, context: Dict[str, Any]) -> Optional[str]:
        """Generate proactive suggestions based on context."""
        suggestions = []
        
        if context.get('last_action') == 'open_application':
            suggestions.append("Would you like me to open any related files or documents, Sir?")
        
        elif context.get('last_action') == 'search':
            suggestions.append("Shall I open the first result for you, Sir?")
        
        elif context.get('last_action') == 'play_media':
            suggestions.append("Would you like me to adjust the volume or create a playlist, Sir?")
        
        if context.get('time_of_day') == 'morning':
            suggestions.append("Good morning, Sir. Shall I provide your daily briefing?")
        
        elif context.get('time_of_day') == 'evening':
            suggestions.append("Good evening, Sir. Is there anything you'd like me to prepare for tomorrow?")
        
        return suggestions[0] if suggestions else None
    
    def learn_from_interaction(self, query: str, response: str, user_feedback: str, outcome: bool):
        """Learn from user interactions to improve responses."""
        # Store interaction for future learning
        interaction = {
            'timestamp': datetime.now(),
            'query': query,
            'response': response,
            'feedback': user_feedback,
            'outcome': outcome
        }
        
        # Update user preferences based on successful interactions
        if outcome:
            # Extract preferences from successful interactions
            if 'play' in query.lower() and 'youtube' in response.lower():
                self.conversation_context.user_preferences['preferred_media_platform'] = 'youtube'
            
            elif 'search' in query.lower() and 'google' in response.lower():
                self.conversation_context.user_preferences['preferred_search_engine'] = 'google'
        
        self.logger.debug(f"Learning from interaction: {outcome}")
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of current conversation."""
        return {
            'message_count': len(self.conversation_context.messages),
            'session_duration': (datetime.now() - self.conversation_context.session_start).total_seconds(),
            'current_topic': self.conversation_context.current_topic,
            'user_preferences': self.conversation_context.user_preferences,
            'last_action': self.conversation_context.last_action
        }
    
    def reset_conversation(self):
        """Reset conversation context."""
        self.conversation_context = ConversationContext()
        self.logger.info("Conversation context reset")
    
    def cleanup(self):
        """Clean up resources."""
        if self.local_pipeline:
            del self.local_pipeline
        
        self.logger.info("LLM Brain cleaned up")
