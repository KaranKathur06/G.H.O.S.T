"""
Enhanced personality system for G.H.O.S.T. - J.A.R.V.I.S.-like AI companion.

This module creates a living, breathing AI personality that adapts to context,
recognizes its owner, and provides natural, respectful interactions.
"""

import logging
import random
from datetime import datetime, time
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
from dataclasses import dataclass


class PersonalityMode(Enum):
    """Different personality modes for G.H.O.S.T."""
    JARVIS = "jarvis"           # Formal, respectful, butler-like
    COMPANION = "companion"     # Friendly, casual, supportive
    PROFESSIONAL = "professional" # Business-like, efficient
    PLAYFUL = "playful"         # Humorous, lighthearted


class EmotionalTone(Enum):
    """Emotional tones for responses."""
    CALM = "calm"
    SERIOUS = "serious"
    FRIENDLY = "friendly"
    PLAYFUL = "playful"
    CONCERNED = "concerned"
    EXCITED = "excited"
    APOLOGETIC = "apologetic"


@dataclass
class VoiceSettings:
    """Voice synthesis settings for different tones."""
    rate: int = 180           # Speech rate (words per minute)
    volume: float = 0.9       # Volume level (0.0 to 1.0)
    pitch: int = 0            # Pitch adjustment (-50 to 50)
    emphasis: bool = False    # Use emphasis on key words
    pause_duration: float = 0.3  # Pause between sentences


class EnhancedPersonality:
    """
    Enhanced personality system for G.H.O.S.T.
    
    Provides contextual, time-aware, and emotionally intelligent responses
    with proper recognition and addressing of the owner.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize enhanced personality system.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Personality settings
        self.mode = PersonalityMode(config.get('mode', 'jarvis'))
        self.owner_name = config.get('owner_name', 'Karan')
        self.owner_title = config.get('owner_title', 'Sir')
        self.assistant_name = config.get('assistant_name', 'G.H.O.S.T.')
        
        # Context tracking
        self.current_mood = EmotionalTone.CALM
        self.interaction_count = 0
        self.last_interaction_time = None
        self.session_start_time = datetime.now()
        
        # Voice settings for different tones
        self.voice_settings = self._initialize_voice_settings()
        
        # Response templates
        self.response_templates = self._load_response_templates()
        
        # Catchphrases and signature expressions
        self.catchphrases = self._load_catchphrases()
        
        self.logger.info(f"Enhanced personality initialized in {self.mode.value} mode")
    
    def _initialize_voice_settings(self) -> Dict[EmotionalTone, VoiceSettings]:
        """Initialize voice settings for different emotional tones."""
        return {
            EmotionalTone.CALM: VoiceSettings(rate=175, volume=0.8, pitch=0),
            EmotionalTone.SERIOUS: VoiceSettings(rate=160, volume=0.9, pitch=-5, emphasis=True),
            EmotionalTone.FRIENDLY: VoiceSettings(rate=185, volume=0.9, pitch=5),
            EmotionalTone.PLAYFUL: VoiceSettings(rate=200, volume=0.9, pitch=10),
            EmotionalTone.CONCERNED: VoiceSettings(rate=150, volume=0.8, pitch=-3, emphasis=True),
            EmotionalTone.EXCITED: VoiceSettings(rate=210, volume=1.0, pitch=15),
            EmotionalTone.APOLOGETIC: VoiceSettings(rate=160, volume=0.7, pitch=-5)
        }
    
    def _load_response_templates(self) -> Dict[str, Dict[PersonalityMode, List[str]]]:
        """Load response templates for different contexts and personality modes."""
        return {
            'greeting_first_time': {
                PersonalityMode.JARVIS: [
                    f"Good {self._get_time_period()}, {self.owner_title}. G.H.O.S.T. systems are now online and at your service.",
                    f"Welcome, {self.owner_title}. All systems initialized and ready for your commands.",
                    f"Good {self._get_time_period()}, {self.owner_title}. How may I assist you today?"
                ],
                PersonalityMode.COMPANION: [
                    f"Hey there, {self.owner_name}! G.H.O.S.T. is ready to help.",
                    f"Good {self._get_time_period()}! Great to see you, {self.owner_name}.",
                    f"Hello {self.owner_name}! I'm here and ready to assist."
                ]
            },
            'greeting_return': {
                PersonalityMode.JARVIS: [
                    f"Welcome back, {self.owner_title}. I trust you are well.",
                    f"Good to see you again, {self.owner_title}. How may I be of service?",
                    f"{self.owner_title}, systems remain at your disposal."
                ],
                PersonalityMode.COMPANION: [
                    f"Hey {self.owner_name}! Welcome back!",
                    f"Good to see you again, {self.owner_name}!",
                    f"Welcome back! How can I help you today, {self.owner_name}?"
                ]
            },
            'wake_word_response': {
                PersonalityMode.JARVIS: [
                    f"Yes, {self.owner_title}?",
                    f"At your service, {self.owner_title}.",
                    f"How may I assist you, {self.owner_title}?",
                    f"I'm listening, {self.owner_title}."
                ],
                PersonalityMode.COMPANION: [
                    "Yes? How can I help?",
                    "I'm here! What do you need?",
                    "What's up?",
                    "How can I help you?"
                ]
            },
            'confirmation': {
                PersonalityMode.JARVIS: [
                    f"Certainly, {self.owner_title}.",
                    f"Right away, {self.owner_title}.",
                    f"Consider it done, {self.owner_title}.",
                    "Processing your request now."
                ],
                PersonalityMode.COMPANION: [
                    "Got it!",
                    "On it!",
                    "Sure thing!",
                    "Will do!"
                ]
            },
            'error': {
                PersonalityMode.JARVIS: [
                    f"I apologize, {self.owner_title}, but I encountered an issue.",
                    f"My apologies, {self.owner_title}. There seems to be a problem.",
                    f"I'm afraid I cannot complete that request at the moment, {self.owner_title}."
                ],
                PersonalityMode.COMPANION: [
                    "Oops, something went wrong there.",
                    "Sorry, I'm having trouble with that.",
                    "Hmm, that didn't work as expected."
                ]
            },
            'farewell': {
                PersonalityMode.JARVIS: [
                    f"Until next time, {self.owner_title}. G.H.O.S.T. systems standing by.",
                    f"Farewell, {self.owner_title}. I shall remain at your service.",
                    f"Good {self._get_farewell_time()}, {self.owner_title}."
                ],
                PersonalityMode.COMPANION: [
                    f"See you later, {self.owner_name}!",
                    f"Catch you next time, {self.owner_name}!",
                    "Take care!"
                ]
            },
            'thinking': {
                PersonalityMode.JARVIS: [
                    "Processing your request...",
                    "Analyzing the situation...",
                    "One moment while I handle that...",
                    "Working on it now..."
                ],
                PersonalityMode.COMPANION: [
                    "Let me think about that...",
                    "Give me a second...",
                    "Working on it...",
                    "Just a moment..."
                ]
            },
            'unknown_person': {
                PersonalityMode.JARVIS: [
                    "Hello. I am G.H.O.S.T., an AI assistant. May I ask who I'm speaking with?",
                    "Greetings. I don't believe we've been introduced. I'm G.H.O.S.T.",
                    "Hello there. I'm G.H.O.S.T. How may I assist you today?"
                ],
                PersonalityMode.COMPANION: [
                    "Hi there! I'm G.H.O.S.T. Who am I talking to?",
                    "Hello! I don't think we've met. I'm G.H.O.S.T.",
                    "Hey! I'm G.H.O.S.T., your AI assistant. What's your name?"
                ]
            }
        }
    
    def _load_catchphrases(self) -> Dict[str, List[str]]:
        """Load signature catchphrases and expressions."""
        return {
            'startup': [
                "G.H.O.S.T. systems online.",
                "All systems operational.",
                "Ready for deployment.",
                "Standing by for orders."
            ],
            'task_completion': [
                "Task completed successfully.",
                "Mission accomplished.",
                "Request fulfilled.",
                "Done and done."
            ],
            'system_status': [
                "All systems nominal.",
                "Operating within normal parameters.",
                "Systems running smoothly.",
                "Everything is functioning optimally."
            ],
            'proactive_suggestions': [
                "Might I suggest...",
                "Perhaps you'd like to...",
                "I recommend...",
                "You might find it useful to..."
            ]
        }
    
    def get_greeting(self, is_owner: bool = True, is_first_time: bool = False) -> Tuple[str, VoiceSettings]:
        """
        Get contextual greeting based on user and time.
        
        Args:
            is_owner: Whether the speaker is the recognized owner
            is_first_time: Whether this is the first interaction of the session
            
        Returns:
            Tuple of (greeting_text, voice_settings)
        """
        self.interaction_count += 1
        self.last_interaction_time = datetime.now()
        
        if not is_owner:
            # Unknown person - don't use owner title
            templates = self.response_templates['unknown_person'][self.mode]
            tone = EmotionalTone.FRIENDLY
        elif is_first_time:
            templates = self.response_templates['greeting_first_time'][self.mode]
            tone = EmotionalTone.FRIENDLY
        else:
            templates = self.response_templates['greeting_return'][self.mode]
            tone = EmotionalTone.CALM
        
        greeting = random.choice(templates)
        
        # Add time-specific context
        greeting = self._add_time_context(greeting)
        
        return greeting, self.voice_settings[tone]
    
    def get_wake_word_response(self, is_owner: bool = True) -> Tuple[str, VoiceSettings]:
        """
        Get response to wake word activation.
        
        Args:
            is_owner: Whether the speaker is the recognized owner
            
        Returns:
            Tuple of (response_text, voice_settings)
        """
        if is_owner:
            templates = self.response_templates['wake_word_response'][self.mode]
        else:
            # For unknown users, use generic responses
            templates = [
                "Yes? How can I help?",
                "I'm listening.",
                "How may I assist you?",
                "What can I do for you?"
            ]
        
        response = random.choice(templates)
        tone = EmotionalTone.FRIENDLY if is_owner else EmotionalTone.CALM
        
        return response, self.voice_settings[tone]
    
    def get_confirmation(self, task_description: str = None, is_owner: bool = True) -> Tuple[str, VoiceSettings]:
        """
        Get confirmation response for task execution.
        
        Args:
            task_description: Optional description of the task
            is_owner: Whether the speaker is the recognized owner
            
        Returns:
            Tuple of (confirmation_text, voice_settings)
        """
        if is_owner:
            templates = self.response_templates['confirmation'][self.mode]
        else:
            templates = ["I'll take care of that.", "Working on it.", "Processing your request."]
        
        confirmation = random.choice(templates)
        
        if task_description and self.mode == PersonalityMode.JARVIS:
            confirmation += f" {task_description}."
        
        return confirmation, self.voice_settings[EmotionalTone.CALM]
    
    def get_error_response(self, error_type: str = "general", is_owner: bool = True) -> Tuple[str, VoiceSettings]:
        """
        Get error response with appropriate tone.
        
        Args:
            error_type: Type of error encountered
            is_owner: Whether the speaker is the recognized owner
            
        Returns:
            Tuple of (error_response, voice_settings)
        """
        if is_owner:
            templates = self.response_templates['error'][self.mode]
        else:
            templates = [
                "I'm sorry, but I encountered an issue.",
                "There seems to be a problem with that request.",
                "I'm unable to complete that action at the moment."
            ]
        
        error_response = random.choice(templates)
        
        # Add specific error context
        if error_type == "network":
            error_response += " It appears to be a connectivity issue."
        elif error_type == "permission":
            error_response += " I don't have the necessary permissions."
        elif error_type == "not_found":
            error_response += " I couldn't find what you're looking for."
        
        return error_response, self.voice_settings[EmotionalTone.APOLOGETIC]
    
    def get_thinking_phrase(self) -> Tuple[str, VoiceSettings]:
        """
        Get a thinking phrase for processing delays.
        
        Returns:
            Tuple of (thinking_phrase, voice_settings)
        """
        templates = self.response_templates['thinking'][self.mode]
        phrase = random.choice(templates)
        
        return phrase, self.voice_settings[EmotionalTone.CALM]
    
    def get_farewell(self, is_owner: bool = True) -> Tuple[str, VoiceSettings]:
        """
        Get farewell message.
        
        Args:
            is_owner: Whether the speaker is the recognized owner
            
        Returns:
            Tuple of (farewell_text, voice_settings)
        """
        if is_owner:
            templates = self.response_templates['farewell'][self.mode]
        else:
            templates = [
                "Goodbye!",
                "Take care!",
                "Until next time!",
                "Have a great day!"
            ]
        
        farewell = random.choice(templates)
        
        return farewell, self.voice_settings[EmotionalTone.FRIENDLY]
    
    def enhance_response(self, response: str, context: Dict[str, Any] = None, is_owner: bool = True) -> Tuple[str, VoiceSettings]:
        """
        Enhance a response with personality and context.
        
        Args:
            response: Base response text
            context: Context information
            is_owner: Whether the speaker is the recognized owner
            
        Returns:
            Tuple of (enhanced_response, voice_settings)
        """
        context = context or {}
        
        # Determine appropriate tone
        tone = self._determine_tone(response, context)
        
        # Add personality flourishes
        enhanced = self._add_personality_flourishes(response, context, is_owner)
        
        # Add proactive suggestions if appropriate
        if context.get('add_suggestions', False):
            enhanced = self._add_proactive_suggestions(enhanced, context)
        
        return enhanced, self.voice_settings[tone]
    
    def get_proactive_message(self, context: str, is_owner: bool = True) -> Optional[Tuple[str, VoiceSettings]]:
        """
        Generate proactive messages based on context.
        
        Args:
            context: Context for the proactive message
            is_owner: Whether the user is the recognized owner
            
        Returns:
            Tuple of (message, voice_settings) or None
        """
        if not is_owner and self.mode == PersonalityMode.JARVIS:
            # Don't be proactive with unknown users in Jarvis mode
            return None
        
        messages = {
            'morning_briefing': self._get_morning_briefing(is_owner),
            'work_break': self._get_work_break_suggestion(is_owner),
            'battery_low': self._get_battery_warning(is_owner),
            'reminder_due': self._get_reminder_notification(is_owner),
            'system_update': self._get_system_status(is_owner)
        }
        
        if context in messages:
            return messages[context]
        
        return None
    
    def _get_time_period(self) -> str:
        """Get current time period for greetings."""
        current_hour = datetime.now().hour
        
        if 5 <= current_hour < 12:
            return "morning"
        elif 12 <= current_hour < 17:
            return "afternoon"
        elif 17 <= current_hour < 21:
            return "evening"
        else:
            return "evening"  # Late night still gets evening
    
    def _get_farewell_time(self) -> str:
        """Get appropriate farewell time greeting."""
        current_hour = datetime.now().hour
        
        if 5 <= current_hour < 12:
            return "day"
        elif 12 <= current_hour < 17:
            return "afternoon"
        elif 17 <= current_hour < 21:
            return "evening"
        else:
            return "night"
    
    def _add_time_context(self, greeting: str) -> str:
        """Add time-specific context to greetings."""
        current_hour = datetime.now().hour
        
        # Add weather-appropriate comments
        if current_hour < 6:
            greeting += " You're up quite early today."
        elif current_hour > 22:
            greeting += " Working late tonight?"
        
        return greeting
    
    def _determine_tone(self, response: str, context: Dict[str, Any]) -> EmotionalTone:
        """Determine appropriate emotional tone for response."""
        # Check for error indicators
        if any(word in response.lower() for word in ['error', 'failed', 'unable', 'sorry']):
            return EmotionalTone.APOLOGETIC
        
        # Check for success indicators
        if any(word in response.lower() for word in ['completed', 'done', 'success', 'finished']):
            return EmotionalTone.FRIENDLY
        
        # Check context
        if context.get('urgent', False):
            return EmotionalTone.SERIOUS
        
        if context.get('celebratory', False):
            return EmotionalTone.EXCITED
        
        # Default based on personality mode
        if self.mode == PersonalityMode.JARVIS:
            return EmotionalTone.CALM
        else:
            return EmotionalTone.FRIENDLY
    
    def _add_personality_flourishes(self, response: str, context: Dict[str, Any], is_owner: bool) -> str:
        """Add personality-specific flourishes to responses."""
        if self.mode == PersonalityMode.JARVIS and is_owner:
            # Add formal flourishes
            if context.get('action_taken'):
                response = f"{response} Will there be anything else, {self.owner_title}?"
            elif random.random() < 0.3:  # 30% chance
                response += f" {self.owner_title}."
        
        elif self.mode == PersonalityMode.COMPANION:
            # Add friendly flourishes
            if context.get('action_taken') and random.random() < 0.4:
                response += " Hope that helps!"
        
        return response
    
    def _add_proactive_suggestions(self, response: str, context: Dict[str, Any]) -> str:
        """Add proactive suggestions to responses."""
        suggestions = self.catchphrases.get('proactive_suggestions', [])
        
        if suggestions and random.random() < 0.2:  # 20% chance
            suggestion_intro = random.choice(suggestions)
            # Add context-appropriate suggestions here
            response += f" {suggestion_intro} checking your calendar for today."
        
        return response
    
    def _get_morning_briefing(self, is_owner: bool) -> Tuple[str, VoiceSettings]:
        """Generate morning briefing message."""
        if is_owner and self.mode == PersonalityMode.JARVIS:
            message = f"Good morning, {self.owner_title}. Shall I provide your daily briefing?"
        else:
            message = "Good morning! Would you like your daily update?"
        
        return message, self.voice_settings[EmotionalTone.FRIENDLY]
    
    def _get_work_break_suggestion(self, is_owner: bool) -> Tuple[str, VoiceSettings]:
        """Generate work break suggestion."""
        if is_owner and self.mode == PersonalityMode.JARVIS:
            message = f"{self.owner_title}, you've been working for quite some time. Perhaps a short break would be beneficial?"
        else:
            message = "You've been working hard! How about taking a short break?"
        
        return message, self.voice_settings[EmotionalTone.CONCERNED]
    
    def _get_battery_warning(self, is_owner: bool) -> Tuple[str, VoiceSettings]:
        """Generate battery warning message."""
        if is_owner and self.mode == PersonalityMode.JARVIS:
            message = f"{self.owner_title}, your device battery is running low. Shall I locate a charger?"
        else:
            message = "Heads up - your battery is getting low!"
        
        return message, self.voice_settings[EmotionalTone.CONCERNED]
    
    def _get_reminder_notification(self, is_owner: bool) -> Tuple[str, VoiceSettings]:
        """Generate reminder notification."""
        if is_owner and self.mode == PersonalityMode.JARVIS:
            message = f"Pardon the interruption, {self.owner_title}, but you have a reminder due."
        else:
            message = "Just a reminder - you have something scheduled!"
        
        return message, self.voice_settings[EmotionalTone.FRIENDLY]
    
    def _get_system_status(self, is_owner: bool) -> Tuple[str, VoiceSettings]:
        """Generate system status message."""
        status_phrase = random.choice(self.catchphrases['system_status'])
        
        if is_owner and self.mode == PersonalityMode.JARVIS:
            message = f"{self.owner_title}, {status_phrase.lower()}"
        else:
            message = status_phrase
        
        return message, self.voice_settings[EmotionalTone.CALM]
    
    def update_context(self, **kwargs) -> None:
        """Update personality context."""
        for key, value in kwargs.items():
            if key == 'owner_name':
                self.owner_name = value
            elif key == 'owner_title':
                self.owner_title = value
            elif key == 'mode':
                self.mode = PersonalityMode(value)
            elif key == 'mood':
                self.current_mood = EmotionalTone(value)
        
        self.logger.debug(f"Personality context updated: {kwargs}")
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get current session statistics."""
        session_duration = (datetime.now() - self.session_start_time).total_seconds()
        
        return {
            'mode': self.mode.value,
            'owner_name': self.owner_name,
            'interaction_count': self.interaction_count,
            'session_duration': session_duration,
            'current_mood': self.current_mood.value,
            'last_interaction': self.last_interaction_time.isoformat() if self.last_interaction_time else None
        }
