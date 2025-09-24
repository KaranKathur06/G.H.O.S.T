"""
Natural Language Understanding Engine for G.H.O.S.T.

This module provides intent classification, entity extraction, and natural language
processing capabilities to transform G.H.O.S.T. from hardcoded commands to 
true generative AI understanding.
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json

class IntentType(Enum):
    """Supported intent types."""
    # Core system intents
    GREETING = "greeting"
    FAREWELL = "goodbye"
    STATUS = "status"
    HELP = "help"
    
    # Information intents
    TIME_DATE = "time_date"
    WEATHER = "weather"
    SEARCH = "search"
    QUESTION = "question"
    
    # Action intents
    OPEN_APP = "open_app"
    OPEN_WEBSITE = "open_website"
    SYSTEM_CONTROL = "system_control"
    FILE_OPERATION = "file_operation"
    
    # Entertainment intents
    JOKE = "joke"
    MUSIC = "music"
    NEWS = "news"
    
    # Communication intents
    EMAIL = "email"
    MESSAGE = "message"
    CALL = "call"
    
    # Unknown/fallback
    UNKNOWN = "unknown"
    CONVERSATION = "conversation"

@dataclass
class Entity:
    """Extracted entity from user input."""
    type: str
    value: str
    confidence: float
    start_pos: int = 0
    end_pos: int = 0

@dataclass
class Intent:
    """Classified intent with entities."""
    type: IntentType
    confidence: float
    entities: List[Entity]
    original_text: str
    processed_text: str
    parameters: Dict[str, Any]

class NLUEngine:
    """
    Natural Language Understanding Engine for G.H.O.S.T.
    
    Provides intent classification and entity extraction using pattern matching
    and keyword analysis. Can be extended with ML models later.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize NLU engine."""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Intent patterns - extensible pattern matching
        self.intent_patterns = self._load_intent_patterns()
        
        # Entity extractors
        self.entity_extractors = self._load_entity_extractors()
        
        # Confidence thresholds
        self.min_confidence = self.config.get('min_confidence', 0.6)
        self.fallback_threshold = self.config.get('fallback_threshold', 0.3)
        
        self.logger.info("NLU Engine initialized with pattern-based classification")
    
    def _load_intent_patterns(self) -> Dict[IntentType, List[Dict[str, Any]]]:
        """Load intent classification patterns."""
        return {
            IntentType.GREETING: [
                {"patterns": ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"], "weight": 1.0},
                {"patterns": ["greetings", "howdy", "what's up", "whats up"], "weight": 0.9}
            ],
            
            IntentType.FAREWELL: [
                {"patterns": ["goodbye", "bye", "see you", "farewell", "good night"], "weight": 1.0},
                {"patterns": ["catch you later", "talk to you later", "ttyl"], "weight": 0.8}
            ],
            
            IntentType.TIME_DATE: [
                {"patterns": ["what time", "time is it", "current time", "tell me the time"], "weight": 1.0},
                {"patterns": ["what date", "date is it", "today is", "what day"], "weight": 1.0},
                {"patterns": ["clock", "calendar"], "weight": 0.7}
            ],
            
            IntentType.OPEN_APP: [
                {"patterns": ["open", "launch", "start", "run"], "weight": 0.8},
                {"patterns": ["calculator", "notepad", "browser", "chrome", "firefox", "edge"], "weight": 0.9}
            ],
            
            IntentType.OPEN_WEBSITE: [
                {"patterns": ["open", "go to", "visit", "navigate to"], "weight": 0.7},
                {"patterns": ["wikipedia", "google", "youtube", "facebook", "twitter", "github"], "weight": 1.0},
                {"patterns": ["website", "site", "web", "url"], "weight": 0.6}
            ],
            
            IntentType.SEARCH: [
                {"patterns": ["search", "find", "look up", "google"], "weight": 0.9},
                {"patterns": ["what is", "who is", "where is", "when is", "how to"], "weight": 0.8},
                {"patterns": ["tell me about", "information about"], "weight": 0.7}
            ],
            
            IntentType.WEATHER: [
                {"patterns": ["weather", "temperature", "forecast", "climate"], "weight": 1.0},
                {"patterns": ["hot", "cold", "rain", "sunny", "cloudy"], "weight": 0.6}
            ],
            
            IntentType.JOKE: [
                {"patterns": ["joke", "funny", "make me laugh", "tell me something funny"], "weight": 1.0},
                {"patterns": ["humor", "comedy", "amusing"], "weight": 0.8}
            ],
            
            IntentType.STATUS: [
                {"patterns": ["how are you", "status", "system status", "are you okay"], "weight": 1.0},
                {"patterns": ["health", "performance", "running"], "weight": 0.7}
            ],
            
            IntentType.HELP: [
                {"patterns": ["help", "assist", "support", "what can you do"], "weight": 1.0},
                {"patterns": ["commands", "functions", "capabilities"], "weight": 0.8}
            ],
            
            IntentType.SYSTEM_CONTROL: [
                {"patterns": ["shutdown", "restart", "sleep", "lock", "volume"], "weight": 0.9},
                {"patterns": ["mute", "unmute", "brightness"], "weight": 0.8}
            ],
            
            IntentType.MUSIC: [
                {"patterns": ["play music", "song", "playlist", "spotify", "music"], "weight": 0.9},
                {"patterns": ["pause", "stop", "next", "previous", "skip"], "weight": 0.7}
            ],
            
            IntentType.QUESTION: [
                {"patterns": ["what", "why", "how", "when", "where", "who"], "weight": 0.6},
                {"patterns": ["explain", "define", "meaning"], "weight": 0.8}
            ]
        }
    
    def _load_entity_extractors(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load entity extraction patterns."""
        return {
            "app_name": [
                {"pattern": r"\\b(calculator|notepad|browser|chrome|firefox|edge|word|excel|powerpoint)\\b", "type": "application"},
                {"pattern": r"\\b(spotify|vlc|media player|paint|cmd|terminal)\\b", "type": "application"}
            ],
            
            "website": [
                {"pattern": r"\\b(wikipedia|google|youtube|facebook|twitter|github|stackoverflow)\\b", "type": "website"},
                {"pattern": r"\\b(amazon|netflix|reddit|linkedin)\\b", "type": "website"}
            ],
            
            "location": [
                {"pattern": r"\\bin\\s+([A-Za-z\\s]+)\\b", "type": "location"},
                {"pattern": r"\\bat\\s+([A-Za-z\\s]+)\\b", "type": "location"}
            ],
            
            "time_reference": [
                {"pattern": r"\\b(today|tomorrow|yesterday|now|later)\\b", "type": "time"},
                {"pattern": r"\\b(morning|afternoon|evening|night)\\b", "type": "time_period"}
            ],
            
            "search_query": [
                {"pattern": r"search\\s+(?:for\\s+)?(.+)", "type": "query"},
                {"pattern": r"(?:what|who|where|when|how)\\s+(?:is|are|was|were)\\s+(.+)", "type": "query"}
            ]
        }
    
    def understand(self, text: str) -> Intent:
        """
        Process natural language input and return classified intent with entities.
        
        Args:
            text: User input text
            
        Returns:
            Intent object with classification and extracted entities
        """
        try:
            # Preprocess text
            processed_text = self._preprocess_text(text)
            
            # Classify intent
            intent_type, intent_confidence = self._classify_intent(processed_text)
            
            # Extract entities
            entities = self._extract_entities(processed_text, intent_type)
            
            # Build parameters from entities
            parameters = self._build_parameters(entities, intent_type, processed_text)
            
            # Create intent object
            intent = Intent(
                type=intent_type,
                confidence=intent_confidence,
                entities=entities,
                original_text=text,
                processed_text=processed_text,
                parameters=parameters
            )
            
            self.logger.debug(f"Classified intent: {intent_type.value} (confidence: {intent_confidence:.2f})")
            
            return intent
            
        except Exception as e:
            self.logger.error(f"Error in NLU processing: {e}")
            
            # Return fallback intent
            return Intent(
                type=IntentType.UNKNOWN,
                confidence=0.0,
                entities=[],
                original_text=text,
                processed_text=text,
                parameters={"error": str(e)}
            )
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess input text for better understanding."""
        # Convert to lowercase
        processed = text.lower().strip()
        
        # Remove extra whitespace
        processed = re.sub(r'\\s+', ' ', processed)
        
        # Remove punctuation at the end
        processed = re.sub(r'[.!?]+$', '', processed)
        
        # Expand contractions
        contractions = {
            "what's": "what is",
            "how's": "how is",
            "where's": "where is",
            "when's": "when is",
            "who's": "who is",
            "can't": "cannot",
            "won't": "will not",
            "don't": "do not",
            "didn't": "did not"
        }
        
        for contraction, expansion in contractions.items():
            processed = processed.replace(contraction, expansion)
        
        return processed
    
    def _classify_intent(self, text: str) -> Tuple[IntentType, float]:
        """Classify the intent of the input text."""
        best_intent = IntentType.UNKNOWN
        best_confidence = 0.0
        
        for intent_type, pattern_groups in self.intent_patterns.items():
            confidence = 0.0
            
            for pattern_group in pattern_groups:
                patterns = pattern_group["patterns"]
                weight = pattern_group["weight"]
                
                # Check if any pattern matches
                for pattern in patterns:
                    if pattern in text:
                        # Calculate confidence based on pattern match and weight
                        match_confidence = weight * (len(pattern) / len(text))
                        confidence = max(confidence, match_confidence)
            
            # Update best match
            if confidence > best_confidence:
                best_confidence = confidence
                best_intent = intent_type
        
        # Apply minimum confidence threshold
        if best_confidence < self.min_confidence:
            # Check for conversational patterns
            if self._is_conversational(text):
                return IntentType.CONVERSATION, 0.7
            else:
                return IntentType.UNKNOWN, best_confidence
        
        return best_intent, best_confidence
    
    def _is_conversational(self, text: str) -> bool:
        """Check if text appears to be conversational."""
        conversational_indicators = [
            "i think", "i believe", "in my opinion", "i feel",
            "tell me", "can you", "would you", "could you",
            "please", "thank you", "thanks"
        ]
        
        return any(indicator in text for indicator in conversational_indicators)
    
    def _extract_entities(self, text: str, intent_type: IntentType) -> List[Entity]:
        """Extract entities from text based on intent type."""
        entities = []
        
        for entity_type, extractors in self.entity_extractors.items():
            for extractor in extractors:
                pattern = extractor["pattern"]
                entity_subtype = extractor["type"]
                
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    entity_value = match.group(1) if match.groups() else match.group(0)
                    
                    entity = Entity(
                        type=entity_type,
                        value=entity_value.strip(),
                        confidence=0.8,  # Default confidence for pattern matches
                        start_pos=match.start(),
                        end_pos=match.end()
                    )
                    entities.append(entity)
        
        return entities
    
    def _build_parameters(self, entities: List[Entity], intent_type: IntentType, text: str) -> Dict[str, Any]:
        """Build parameters dictionary from extracted entities and intent."""
        parameters = {}
        
        # Add entities to parameters
        for entity in entities:
            if entity.type not in parameters:
                parameters[entity.type] = []
            parameters[entity.type].append(entity.value)
        
        # Flatten single-item lists
        for key, value in parameters.items():
            if isinstance(value, list) and len(value) == 1:
                parameters[key] = value[0]
        
        # Add intent-specific parameters
        if intent_type == IntentType.SEARCH:
            # Extract search query if not already found
            if "search_query" not in parameters:
                # Try to extract query after common search prefixes
                search_patterns = [
                    r"search\\s+(?:for\\s+)?(.+)",
                    r"find\\s+(?:me\\s+)?(.+)",
                    r"look\\s+up\\s+(.+)",
                    r"what\\s+is\\s+(.+)",
                    r"who\\s+is\\s+(.+)",
                    r"tell\\s+me\\s+about\\s+(.+)"
                ]
                
                for pattern in search_patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        parameters["search_query"] = match.group(1).strip()
                        break
        
        elif intent_type == IntentType.OPEN_APP:
            # Ensure we have an app name
            if "app_name" not in parameters:
                # Try to extract from common patterns
                app_pattern = r"open\\s+(\\w+)"
                match = re.search(app_pattern, text, re.IGNORECASE)
                if match:
                    parameters["app_name"] = match.group(1)
        
        elif intent_type == IntentType.OPEN_WEBSITE:
            # Ensure we have a website
            if "website" not in parameters:
                website_pattern = r"(?:open|go\\s+to|visit)\\s+(\\w+(?:\\.\\w+)*)"
                match = re.search(website_pattern, text, re.IGNORECASE)
                if match:
                    parameters["website"] = match.group(1)
        
        # Add original text for fallback
        parameters["original_text"] = text
        
        return parameters
    
    def get_intent_confidence_breakdown(self, text: str) -> Dict[str, float]:
        """Get confidence scores for all intents (useful for debugging)."""
        processed_text = self._preprocess_text(text)
        confidence_scores = {}
        
        for intent_type, pattern_groups in self.intent_patterns.items():
            confidence = 0.0
            
            for pattern_group in pattern_groups:
                patterns = pattern_group["patterns"]
                weight = pattern_group["weight"]
                
                for pattern in patterns:
                    if pattern in processed_text:
                        match_confidence = weight * (len(pattern) / len(processed_text))
                        confidence = max(confidence, match_confidence)
            
            confidence_scores[intent_type.value] = confidence
        
        return confidence_scores
    
    def add_intent_pattern(self, intent_type: IntentType, patterns: List[str], weight: float = 1.0):
        """Dynamically add new intent patterns."""
        if intent_type not in self.intent_patterns:
            self.intent_patterns[intent_type] = []
        
        self.intent_patterns[intent_type].append({
            "patterns": patterns,
            "weight": weight
        })
        
        self.logger.info(f"Added new patterns for intent {intent_type.value}")
    
    def add_entity_extractor(self, entity_type: str, pattern: str, extractor_type: str):
        """Dynamically add new entity extractors."""
        if entity_type not in self.entity_extractors:
            self.entity_extractors[entity_type] = []
        
        self.entity_extractors[entity_type].append({
            "pattern": pattern,
            "type": extractor_type
        })
        
        self.logger.info(f"Added new entity extractor for {entity_type}")
