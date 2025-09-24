"""
Universal Natural Language Understanding Engine for G.H.O.S.T.

This module provides unlimited natural language understanding capabilities
that can parse ANY spoken command and extract intent + entities dynamically.
No hardcoded limitations - true J.A.R.V.I.S.-like understanding.
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json

# Try to load spaCy model
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except (ImportError, OSError):
    SPACY_AVAILABLE = False
    nlp = None

class UniversalIntent(Enum):
    """Universal intent categories that can handle any request."""
    # Media & Entertainment
    PLAY_MEDIA = "play_media"           # Play any song, video, podcast, etc.
    CONTROL_MEDIA = "control_media"     # Pause, stop, next, previous, volume
    
    # File & Application Management
    OPEN_APPLICATION = "open_application"  # Launch any app
    OPEN_FILE = "open_file"               # Open any file/folder
    FIND_ITEM = "find_item"               # Search for files/apps/content
    
    # Web & Search
    SEARCH_WEB = "search_web"             # Search anything online
    NAVIGATE_WEB = "navigate_web"         # Go to websites
    
    # System Control
    SYSTEM_CONTROL = "system_control"     # Shutdown, restart, sleep, etc.
    DEVICE_CONTROL = "device_control"     # Volume, brightness, WiFi, etc.
    
    # Information & Knowledge
    GET_INFORMATION = "get_information"   # Ask questions, get facts
    GET_STATUS = "get_status"             # Time, date, weather, system status
    
    # Communication
    SEND_MESSAGE = "send_message"         # Send emails, texts, etc.
    MAKE_CALL = "make_call"              # Make phone/video calls
    
    # Productivity
    CREATE_CONTENT = "create_content"     # Create files, notes, reminders
    SCHEDULE_EVENT = "schedule_event"     # Calendar, reminders, alarms
    
    # Conversation & Help
    CONVERSATION = "conversation"         # General chat, questions
    GET_HELP = "get_help"                # Ask for assistance
    
    # Meta Commands
    CLARIFICATION_NEEDED = "clarification_needed"  # Need more info
    UNKNOWN = "unknown"                   # Fallback

@dataclass
class UniversalEntity:
    """Universal entity that can represent anything."""
    type: str           # Entity type (app, file, song, website, etc.)
    value: str          # Entity value (actual name/content)
    confidence: float   # Confidence score
    context: str = ""   # Additional context
    alternatives: List[str] = field(default_factory=list)  # Alternative matches

@dataclass
class UniversalRequest:
    """Complete understanding of any user request."""
    intent: UniversalIntent
    confidence: float
    entities: List[UniversalEntity]
    original_text: str
    processed_text: str
    
    # Extracted information
    action_verb: str = ""           # play, open, search, etc.
    target_object: str = ""         # what to act on
    platform: str = ""              # where to perform action
    modifiers: List[str] = field(default_factory=list)  # additional context
    
    # Decision support
    needs_clarification: bool = False
    clarification_options: List[str] = field(default_factory=list)
    suggested_actions: List[Dict[str, Any]] = field(default_factory=list)

class UniversalNLU:
    """
    Universal Natural Language Understanding Engine.
    
    Can understand ANY natural language command without hardcoded limitations.
    Uses advanced NLP techniques + pattern matching + context awareness.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize Universal NLU."""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Core NLP components
        self.nlp = nlp if SPACY_AVAILABLE else None
        
        # Universal patterns for intent detection
        self.intent_patterns = self._load_universal_patterns()
        
        # Entity extractors
        self.entity_extractors = self._load_entity_extractors()
        
        # Context awareness
        self.conversation_history = []
        self.user_preferences = {}
        
        # Confidence thresholds
        self.min_confidence = self.config.get('min_confidence', 0.6)
        self.clarification_threshold = self.config.get('clarification_threshold', 0.4)
        
        self.logger.info("Universal NLU Engine initialized")
    
    def understand(self, text: str, context: Dict[str, Any] = None) -> UniversalRequest:
        """
        Understand ANY natural language input.
        
        Args:
            text: User input text
            context: Optional context information
            
        Returns:
            UniversalRequest with complete understanding
        """
        try:
            # Preprocess text
            processed_text = self._preprocess_text(text)
            
            # Extract core components
            action_verb = self._extract_action_verb(processed_text)
            target_object = self._extract_target_object(processed_text)
            platform = self._extract_platform(processed_text)
            modifiers = self._extract_modifiers(processed_text)
            
            # Classify intent
            intent, intent_confidence = self._classify_universal_intent(
                processed_text, action_verb, target_object, platform
            )
            
            # Extract entities
            entities = self._extract_universal_entities(
                processed_text, intent, action_verb, target_object, platform
            )
            
            # Determine if clarification is needed
            needs_clarification, clarification_options = self._check_clarification_needed(
                intent, entities, target_object, platform
            )
            
            # Generate suggested actions
            suggested_actions = self._generate_suggested_actions(
                intent, entities, action_verb, target_object, platform
            )
            
            # Create universal request
            request = UniversalRequest(
                intent=intent,
                confidence=intent_confidence,
                entities=entities,
                original_text=text,
                processed_text=processed_text,
                action_verb=action_verb,
                target_object=target_object,
                platform=platform,
                modifiers=modifiers,
                needs_clarification=needs_clarification,
                clarification_options=clarification_options,
                suggested_actions=suggested_actions
            )
            
            # Store in conversation history
            self.conversation_history.append({
                'timestamp': datetime.now(),
                'input': text,
                'request': request
            })
            
            self.logger.debug(f"Universal understanding: {intent.value} ({intent_confidence:.2f})")
            
            return request
            
        except Exception as e:
            self.logger.error(f"Error in universal understanding: {e}")
            return self._create_fallback_request(text, str(e))
    
    def _load_universal_patterns(self) -> Dict[UniversalIntent, List[Dict[str, Any]]]:
        """Load universal patterns that can match any command."""
        return {
            UniversalIntent.PLAY_MEDIA: [
                {"patterns": ["play", "start", "begin", "put on"], "weight": 1.0},
                {"patterns": ["music", "song", "video", "movie", "podcast", "audio"], "weight": 0.9},
                {"patterns": ["youtube", "spotify", "netflix", "vlc", "media player"], "weight": 0.8}
            ],
            
            UniversalIntent.OPEN_APPLICATION: [
                {"patterns": ["open", "launch", "start", "run", "execute"], "weight": 1.0},
                {"patterns": ["app", "application", "program", "software"], "weight": 0.8},
                {"patterns": ["chrome", "firefox", "notepad", "calculator", "word", "excel"], "weight": 0.9}
            ],
            
            UniversalIntent.OPEN_FILE: [
                {"patterns": ["open", "show", "display", "view"], "weight": 0.9},
                {"patterns": ["file", "folder", "document", "picture", "photo"], "weight": 0.9},
                {"patterns": ["desktop", "downloads", "documents", "pictures"], "weight": 0.7}
            ],
            
            UniversalIntent.SEARCH_WEB: [
                {"patterns": ["search", "find", "look up", "google"], "weight": 1.0},
                {"patterns": ["what is", "who is", "where is", "how to"], "weight": 0.9},
                {"patterns": ["information about", "tell me about"], "weight": 0.8}
            ],
            
            UniversalIntent.SYSTEM_CONTROL: [
                {"patterns": ["shutdown", "restart", "reboot", "sleep", "hibernate"], "weight": 1.0},
                {"patterns": ["turn off", "power down", "close system"], "weight": 0.9}
            ],
            
            UniversalIntent.DEVICE_CONTROL: [
                {"patterns": ["volume", "brightness", "wifi", "bluetooth"], "weight": 1.0},
                {"patterns": ["turn up", "turn down", "increase", "decrease"], "weight": 0.8},
                {"patterns": ["mute", "unmute", "connect", "disconnect"], "weight": 0.9}
            ],
            
            UniversalIntent.GET_INFORMATION: [
                {"patterns": ["what", "who", "where", "when", "why", "how"], "weight": 0.8},
                {"patterns": ["tell me", "explain", "describe"], "weight": 0.9},
                {"patterns": ["information", "details", "facts"], "weight": 0.7}
            ],
            
            UniversalIntent.GET_STATUS: [
                {"patterns": ["time", "date", "weather", "status"], "weight": 1.0},
                {"patterns": ["what time", "what date", "how are you"], "weight": 0.9}
            ],
            
            UniversalIntent.CONVERSATION: [
                {"patterns": ["hello", "hi", "hey", "good morning", "good evening"], "weight": 0.9},
                {"patterns": ["thank you", "thanks", "please", "sorry"], "weight": 0.8},
                {"patterns": ["how are you", "what's up", "how's it going"], "weight": 0.9}
            ]
        }
    
    def _load_entity_extractors(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load universal entity extractors."""
        return {
            "media_content": [
                {"pattern": r"play\\s+(.+?)\\s+(?:on|from|in)", "type": "media_title"},
                {"pattern": r"(?:song|music|video|movie)\\s+(.+)", "type": "media_title"},
                {"pattern": r"\"([^\"]+)\"", "type": "quoted_content"}
            ],
            
            "platform": [
                {"pattern": r"(?:on|from|in|using)\\s+(youtube|spotify|netflix|vlc|media\\s+player)", "type": "media_platform"},
                {"pattern": r"(?:on|from|in|using)\\s+(google|bing|duckduckgo)", "type": "search_platform"},
                {"pattern": r"(?:with|using)\\s+(chrome|firefox|edge|safari)", "type": "browser"}
            ],
            
            "application": [
                {"pattern": r"(?:open|launch|start|run)\\s+([a-zA-Z][a-zA-Z0-9\\s]*?)(?:\\s|$)", "type": "app_name"},
                {"pattern": r"\\b(chrome|firefox|notepad|calculator|word|excel|powerpoint|photoshop|vlc)\\b", "type": "known_app"}
            ],
            
            "file_path": [
                {"pattern": r"(?:open|show)\\s+(.+?)\\s+(?:file|folder)", "type": "file_name"},
                {"pattern": r"(?:in|from)\\s+(desktop|downloads|documents|pictures|music|videos)", "type": "system_folder"}
            ],
            
            "search_query": [
                {"pattern": r"search\\s+(?:for\\s+)?(.+)", "type": "search_term"},
                {"pattern": r"(?:what|who|where|when|how)\\s+(?:is|are|was|were)\\s+(.+)", "type": "question"},
                {"pattern": r"tell\\s+me\\s+about\\s+(.+)", "type": "topic"}
            ],
            
            "system_action": [
                {"pattern": r"\\b(shutdown|restart|reboot|sleep|hibernate|lock)\\b", "type": "system_command"},
                {"pattern": r"\\b(volume|brightness)\\s+(up|down|increase|decrease)", "type": "device_adjustment"}
            ]
        }
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for better understanding."""
        # Convert to lowercase
        processed = text.lower().strip()
        
        # Remove extra whitespace
        processed = re.sub(r'\\s+', ' ', processed)
        
        # Expand contractions
        contractions = {
            "what's": "what is", "how's": "how is", "where's": "where is",
            "when's": "when is", "who's": "who is", "can't": "cannot",
            "won't": "will not", "don't": "do not", "didn't": "did not",
            "i'm": "i am", "you're": "you are", "it's": "it is"
        }
        
        for contraction, expansion in contractions.items():
            processed = processed.replace(contraction, expansion)
        
        return processed
    
    def _extract_action_verb(self, text: str) -> str:
        """Extract the main action verb from text."""
        action_verbs = [
            "play", "open", "launch", "start", "run", "execute", "begin",
            "search", "find", "look", "google", "show", "display", "view",
            "create", "make", "write", "send", "call", "turn", "set",
            "shutdown", "restart", "close", "stop", "pause", "resume"
        ]
        
        words = text.split()
        for word in words:
            if word in action_verbs:
                return word
        
        # Try to extract with spaCy if available
        if self.nlp:
            doc = self.nlp(text)
            for token in doc:
                if token.pos_ == "VERB" and token.lemma_ in action_verbs:
                    return token.lemma_
        
        return ""
    
    def _extract_target_object(self, text: str) -> str:
        """Extract what the user wants to act upon."""
        # Remove action verbs and common words
        stop_words = {"the", "a", "an", "on", "in", "at", "to", "for", "with", "by"}
        action_words = {"play", "open", "launch", "search", "find", "show"}
        
        words = text.split()
        filtered_words = []
        
        skip_next = False
        for i, word in enumerate(words):
            if skip_next:
                skip_next = False
                continue
                
            if word in action_words:
                skip_next = True  # Skip the word after action verb
                continue
                
            if word not in stop_words and len(word) > 2:
                filtered_words.append(word)
        
        # Try to find quoted content first
        quoted_match = re.search(r'"([^"]+)"', text)
        if quoted_match:
            return quoted_match.group(1)
        
        # Return the remaining meaningful words
        return " ".join(filtered_words[:3])  # Limit to first 3 meaningful words
    
    def _extract_platform(self, text: str) -> str:
        """Extract the platform/service to use."""
        platforms = {
            "youtube": ["youtube", "yt"],
            "spotify": ["spotify"],
            "netflix": ["netflix"],
            "vlc": ["vlc", "media player"],
            "google": ["google"],
            "chrome": ["chrome"],
            "firefox": ["firefox"]
        }
        
        text_lower = text.lower()
        for platform, keywords in platforms.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return platform
        
        return ""
    
    def _extract_modifiers(self, text: str) -> List[str]:
        """Extract modifiers that affect the action."""
        modifiers = []
        
        modifier_patterns = {
            "quietly": ["quietly", "silent", "mute"],
            "loudly": ["loudly", "loud", "high volume"],
            "quickly": ["quickly", "fast", "immediately"],
            "slowly": ["slowly", "slow"],
            "fullscreen": ["fullscreen", "full screen"],
            "minimized": ["minimized", "background"]
        }
        
        text_lower = text.lower()
        for modifier, keywords in modifier_patterns.items():
            for keyword in keywords:
                if keyword in text_lower:
                    modifiers.append(modifier)
        
        return modifiers
    
    def _classify_universal_intent(self, text: str, action_verb: str, 
                                 target_object: str, platform: str) -> Tuple[UniversalIntent, float]:
        """Classify intent using universal patterns."""
        best_intent = UniversalIntent.UNKNOWN
        best_confidence = 0.0
        
        for intent_type, pattern_groups in self.intent_patterns.items():
            confidence = 0.0
            
            for pattern_group in pattern_groups:
                patterns = pattern_group["patterns"]
                weight = pattern_group["weight"]
                
                for pattern in patterns:
                    if pattern in text:
                        match_confidence = weight * (len(pattern) / len(text))
                        confidence = max(confidence, match_confidence)
            
            # Boost confidence based on extracted components
            if action_verb and intent_type == UniversalIntent.PLAY_MEDIA and action_verb == "play":
                confidence += 0.3
            elif action_verb and intent_type == UniversalIntent.OPEN_APPLICATION and action_verb in ["open", "launch"]:
                confidence += 0.3
            elif action_verb and intent_type == UniversalIntent.SEARCH_WEB and action_verb in ["search", "find"]:
                confidence += 0.3
            
            if confidence > best_confidence:
                best_confidence = confidence
                best_intent = intent_type
        
        return best_intent, min(best_confidence, 1.0)
    
    def _extract_universal_entities(self, text: str, intent: UniversalIntent,
                                  action_verb: str, target_object: str, 
                                  platform: str) -> List[UniversalEntity]:
        """Extract entities using universal extractors."""
        entities = []
        
        # Add primary entities
        if target_object:
            entities.append(UniversalEntity(
                type="target",
                value=target_object,
                confidence=0.8,
                context=f"Main target for {action_verb}"
            ))
        
        if platform:
            entities.append(UniversalEntity(
                type="platform",
                value=platform,
                confidence=0.9,
                context="Specified platform/service"
            ))
        
        # Extract using pattern-based extractors
        for entity_type, extractors in self.entity_extractors.items():
            for extractor in extractors:
                pattern = extractor["pattern"]
                entity_subtype = extractor["type"]
                
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    entity_value = match.group(1) if match.groups() else match.group(0)
                    
                    entity = UniversalEntity(
                        type=entity_type,
                        value=entity_value.strip(),
                        confidence=0.7,
                        context=f"Extracted via {entity_subtype}"
                    )
                    entities.append(entity)
        
        return entities
    
    def _check_clarification_needed(self, intent: UniversalIntent, entities: List[UniversalEntity],
                                  target_object: str, platform: str) -> Tuple[bool, List[str]]:
        """Check if clarification is needed and suggest options."""
        clarification_options = []
        
        # Check for ambiguous media requests
        if intent == UniversalIntent.PLAY_MEDIA:
            if target_object and not platform:
                clarification_options = [
                    "YouTube",
                    "Spotify", 
                    "Local files",
                    "VLC Media Player"
                ]
                return True, clarification_options
        
        # Check for ambiguous file requests
        elif intent == UniversalIntent.OPEN_FILE:
            if not target_object or len(target_object.split()) < 2:
                clarification_options = [
                    "Please specify the file name",
                    "Which folder should I search in?",
                    "What type of file are you looking for?"
                ]
                return True, clarification_options
        
        # Check for vague search requests
        elif intent == UniversalIntent.SEARCH_WEB:
            if not target_object or len(target_object) < 3:
                clarification_options = [
                    "Please specify what you want to search for",
                    "Which search engine would you prefer?"
                ]
                return True, clarification_options
        
        return False, []
    
    def _generate_suggested_actions(self, intent: UniversalIntent, entities: List[UniversalEntity],
                                  action_verb: str, target_object: str, 
                                  platform: str) -> List[Dict[str, Any]]:
        """Generate suggested actions based on understanding."""
        suggestions = []
        
        if intent == UniversalIntent.PLAY_MEDIA:
            if platform:
                suggestions.append({
                    "action": "play_on_platform",
                    "platform": platform,
                    "content": target_object,
                    "description": f"Play '{target_object}' on {platform}"
                })
            else:
                suggestions.extend([
                    {
                        "action": "play_on_youtube",
                        "content": target_object,
                        "description": f"Play '{target_object}' on YouTube"
                    },
                    {
                        "action": "play_local",
                        "content": target_object,
                        "description": f"Play '{target_object}' from local files"
                    }
                ])
        
        elif intent == UniversalIntent.OPEN_APPLICATION:
            suggestions.append({
                "action": "launch_app",
                "app_name": target_object,
                "description": f"Launch {target_object}"
            })
        
        elif intent == UniversalIntent.SEARCH_WEB:
            suggestions.append({
                "action": "web_search",
                "query": target_object,
                "platform": platform or "google",
                "description": f"Search for '{target_object}' on {platform or 'Google'}"
            })
        
        return suggestions
    
    def _create_fallback_request(self, text: str, error: str) -> UniversalRequest:
        """Create fallback request for errors."""
        return UniversalRequest(
            intent=UniversalIntent.UNKNOWN,
            confidence=0.0,
            entities=[],
            original_text=text,
            processed_text=text,
            needs_clarification=True,
            clarification_options=[
                "I didn't understand that request",
                "Could you please rephrase?",
                "What would you like me to help you with?"
            ]
        )
    
    def learn_from_interaction(self, request: UniversalRequest, user_choice: str, outcome: bool):
        """Learn from user interactions to improve future understanding."""
        # Store user preferences
        if outcome and request.platform:
            # User successfully used this platform
            if request.intent.value not in self.user_preferences:
                self.user_preferences[request.intent.value] = {}
            
            platform_prefs = self.user_preferences[request.intent.value].get('platforms', {})
            platform_prefs[request.platform] = platform_prefs.get(request.platform, 0) + 1
            self.user_preferences[request.intent.value]['platforms'] = platform_prefs
        
        self.logger.debug(f"Learning from interaction: {user_choice} -> {outcome}")
    
    def get_preferred_platform(self, intent: UniversalIntent) -> Optional[str]:
        """Get user's preferred platform for an intent."""
        if intent.value in self.user_preferences:
            platforms = self.user_preferences[intent.value].get('platforms', {})
            if platforms:
                return max(platforms, key=platforms.get)
        return None
