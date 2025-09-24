"""
Memory management system for G.H.O.S.T. virtual assistant.

This module handles short-term and long-term memory storage, user preferences,
and conversation context for improved interaction quality.
"""

import logging
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class Interaction:
    """Represents a single interaction in the conversation history."""
    timestamp: str
    content: str
    type: str  # 'user', 'assistant', 'system'
    metadata: Dict[str, Any] = None


@dataclass
class UserPreference:
    """Represents a user preference or setting."""
    key: str
    value: Any
    category: str
    timestamp: str


class MemoryManager:
    """
    Manages memory storage and retrieval for the virtual assistant.
    
    Handles conversation history, user preferences, and contextual information.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the memory manager.
        
        Args:
            config: Configuration dictionary for memory settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Memory storage paths
        self.data_dir = Path(config.get('data_dir', 'data/memory'))
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.conversation_file = self.data_dir / 'conversations.json'
        self.preferences_file = self.data_dir / 'preferences.json'
        self.context_file = self.data_dir / 'context.json'
        
        # In-memory storage
        self.current_session: List[Interaction] = []
        self.user_preferences: Dict[str, UserPreference] = {}
        self.context_memory: Dict[str, Any] = {}
        
        # Load existing data
        self._load_memory()
    
    def _load_memory(self) -> None:
        """Load memory data from persistent storage."""
        try:
            # Load conversation history
            if self.conversation_file.exists():
                with open(self.conversation_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Load recent conversations (last 24 hours)
                    cutoff = datetime.now() - timedelta(hours=24)
                    for item in data.get('recent', []):
                        if datetime.fromisoformat(item['timestamp']) > cutoff:
                            self.current_session.append(Interaction(**item))
            
            # Load user preferences
            if self.preferences_file.exists():
                with open(self.preferences_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for pref_data in data.get('preferences', []):
                        pref = UserPreference(**pref_data)
                        self.user_preferences[pref.key] = pref
            
            # Load context memory
            if self.context_file.exists():
                with open(self.context_file, 'r', encoding='utf-8') as f:
                    self.context_memory = json.load(f)
            
            self.logger.info("Memory data loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading memory data: {e}")
    
    def add_interaction(self, content: str, interaction_type: str, metadata: Dict[str, Any] = None) -> None:
        """
        Add a new interaction to the conversation history.
        
        Args:
            content: The interaction content (text)
            interaction_type: Type of interaction ('user', 'assistant', 'system')
            metadata: Optional metadata dictionary
        """
        interaction = Interaction(
            timestamp=datetime.now().isoformat(),
            content=content,
            type=interaction_type,
            metadata=metadata or {}
        )
        
        self.current_session.append(interaction)
        self.logger.debug(f"Added {interaction_type} interaction: {content[:50]}...")
    
    def get_recent_context(self, count: int = 10) -> List[Interaction]:
        """
        Get recent conversation context.
        
        Args:
            count: Number of recent interactions to retrieve
            
        Returns:
            List of recent interactions
        """
        return self.current_session[-count:] if self.current_session else []
    
    def set_preference(self, key: str, value: Any, category: str = 'general') -> None:
        """
        Set a user preference.
        
        Args:
            key: Preference key
            value: Preference value
            category: Preference category
        """
        preference = UserPreference(
            key=key,
            value=value,
            category=category,
            timestamp=datetime.now().isoformat()
        )
        
        self.user_preferences[key] = preference
        self.logger.info(f"Set preference: {key} = {value}")
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """
        Get a user preference value.
        
        Args:
            key: Preference key
            default: Default value if preference not found
            
        Returns:
            Preference value or default
        """
        preference = self.user_preferences.get(key)
        return preference.value if preference else default
    
    def store_context(self, key: str, value: Any) -> None:
        """
        Store contextual information.
        
        Args:
            key: Context key
            value: Context value
        """
        self.context_memory[key] = {
            'value': value,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """
        Retrieve contextual information.
        
        Args:
            key: Context key
            default: Default value if context not found
            
        Returns:
            Context value or default
        """
        context_item = self.context_memory.get(key)
        return context_item['value'] if context_item else default
    
    def add_feedback(self, intent, success: bool, feedback: str = None) -> None:
        """
        Store feedback for learning purposes.
        
        Args:
            intent: The intent that was executed
            success: Whether the action was successful
            feedback: Optional user feedback
        """
        feedback_data = {
            'intent': asdict(intent),
            'success': success,
            'feedback': feedback,
            'timestamp': datetime.now().isoformat()
        }
        
        # Store in context memory for analysis
        feedback_key = f"feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.store_context(feedback_key, feedback_data)
    
    def save_session(self) -> None:
        """Save current session data to persistent storage."""
        try:
            # Save conversation history
            conversation_data = {
                'recent': [asdict(interaction) for interaction in self.current_session],
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.conversation_file, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, indent=2, ensure_ascii=False)
            
            # Save preferences
            preferences_data = {
                'preferences': [asdict(pref) for pref in self.user_preferences.values()],
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.preferences_file, 'w', encoding='utf-8') as f:
                json.dump(preferences_data, f, indent=2, ensure_ascii=False)
            
            # Save context memory
            with open(self.context_file, 'w', encoding='utf-8') as f:
                json.dump(self.context_memory, f, indent=2, ensure_ascii=False)
            
            self.logger.info("Session data saved successfully")
            
        except Exception as e:
            self.logger.error(f"Error saving session data: {e}")
    
    def clear_old_data(self, days: int = 30) -> None:
        """
        Clear old conversation data beyond specified days.
        
        Args:
            days: Number of days to retain data
        """
        cutoff = datetime.now() - timedelta(days=days)
        
        # Filter current session
        self.current_session = [
            interaction for interaction in self.current_session
            if datetime.fromisoformat(interaction.timestamp) > cutoff
        ]
        
        # Clear old context data
        old_keys = []
        for key, value in self.context_memory.items():
            if 'timestamp' in value:
                timestamp = datetime.fromisoformat(value['timestamp'])
                if timestamp < cutoff:
                    old_keys.append(key)
        
        for key in old_keys:
            del self.context_memory[key]
        
        self.logger.info(f"Cleared data older than {days} days")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get memory usage statistics.
        
        Returns:
            Dictionary with memory statistics
        """
        return {
            'current_session_size': len(self.current_session),
            'preferences_count': len(self.user_preferences),
            'context_items': len(self.context_memory),
            'data_directory': str(self.data_dir),
            'last_interaction': self.current_session[-1].timestamp if self.current_session else None
        }
