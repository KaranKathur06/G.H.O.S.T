"""
Entertainment action for G.H.O.S.T. virtual assistant.

This module handles entertainment-related requests like jokes,
fun facts, quotes, and other amusing content.
"""

import random
import logging
from typing import Dict, Any, Optional, List
from .base_action import BaseAction


class Entertainment(BaseAction):
    """
    Handles entertainment requests like jokes and fun facts.
    
    Provides various forms of entertainment content to users.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the entertainment handler.
        
        Args:
            config: Configuration dictionary for entertainment settings
        """
        super().__init__(config)
        
        # Entertainment content
        self.jokes = self._load_jokes()
        self.fun_facts = self._load_fun_facts()
        self.quotes = self._load_quotes()
        
        # Configuration
        self.content_type = config.get('default_type', 'joke')
    
    def execute(self, parameters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Provide entertainment content.
        
        Args:
            parameters: Dictionary containing optional 'type' parameter
            
        Returns:
            Dictionary with entertainment content
        """
        if not self.is_available():
            return self.handle_error(Exception("Entertainment is disabled"), parameters)
        
        content_type = parameters.get('type', self.content_type).lower()
        
        try:
            if content_type == 'joke':
                content = self._get_joke()
                message = content
            elif content_type == 'fact':
                content = self._get_fun_fact()
                message = f"Here's a fun fact: {content}"
            elif content_type == 'quote':
                content = self._get_quote()
                message = content
            else:
                # Default to joke
                content = self._get_joke()
                message = content
            
            result = {
                'success': True,
                'message': message,
                'content': content,
                'type': content_type
            }
            
            self.log_execution(parameters, result)
            return result
            
        except Exception as e:
            return self.handle_error(e, parameters)
    
    def _load_jokes(self) -> List[str]:
        """
        Load a collection of jokes.
        
        Returns:
            List of joke strings
        """
        return [
            "Why don't scientists trust atoms? Because they make up everything!",
            "I told my wife she was drawing her eyebrows too high. She looked surprised.",
            "Why don't programmers like nature? It has too many bugs.",
            "I'm reading a book about anti-gravity. It's impossible to put down!",
            "Why did the scarecrow win an award? He was outstanding in his field!",
            "I used to hate facial hair, but then it grew on me.",
            "Why don't eggs tell jokes? They'd crack each other up!",
            "What do you call a fake noodle? An impasta!",
            "I'm on a seafood diet. I see food and I eat it.",
            "Why did the math book look so sad? Because it had too many problems!",
            "What do you call a bear with no teeth? A gummy bear!",
            "Why don't skeletons fight each other? They don't have the guts.",
            "I wondered why the baseball kept getting bigger. Then it hit me.",
            "What's the best thing about Switzerland? I don't know, but the flag is a big plus.",
            "Why did the coffee file a police report? It got mugged!"
        ]
    
    def _load_fun_facts(self) -> List[str]:
        """
        Load a collection of fun facts.
        
        Returns:
            List of fun fact strings
        """
        return [
            "Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still perfectly edible.",
            "A group of flamingos is called a 'flamboyance'.",
            "Octopuses have three hearts and blue blood.",
            "Bananas are berries, but strawberries aren't.",
            "A shrimp's heart is in its head.",
            "It's impossible to hum while holding your nose closed.",
            "The shortest war in history lasted only 38-45 minutes between Britain and Zanzibar in 1896.",
            "Dolphins have names for each other - they use unique whistle signatures.",
            "A cloud can weigh more than a million pounds.",
            "Your stomach gets an entirely new lining every 3-4 days because stomach acid would otherwise digest it.",
            "Wombat poop is cube-shaped.",
            "There are more possible games of chess than there are atoms in the observable universe.",
            "A group of pandas is called an 'embarrassment'.",
            "The human brain uses about 20% of the body's total energy.",
            "Sea otters hold hands while sleeping to prevent drifting apart."
        ]
    
    def _load_quotes(self) -> List[str]:
        """
        Load a collection of inspirational quotes.
        
        Returns:
            List of quote strings
        """
        return [
            "\"The only way to do great work is to love what you do.\" - Steve Jobs",
            "\"Innovation distinguishes between a leader and a follower.\" - Steve Jobs",
            "\"Life is what happens to you while you're busy making other plans.\" - John Lennon",
            "\"The future belongs to those who believe in the beauty of their dreams.\" - Eleanor Roosevelt",
            "\"It is during our darkest moments that we must focus to see the light.\" - Aristotle",
            "\"The only impossible journey is the one you never begin.\" - Tony Robbins",
            "\"Success is not final, failure is not fatal: it is the courage to continue that counts.\" - Winston Churchill",
            "\"The way to get started is to quit talking and begin doing.\" - Walt Disney",
            "\"Don't let yesterday take up too much of today.\" - Will Rogers",
            "\"You learn more from failure than from success. Don't let it stop you. Failure builds character.\" - Unknown",
            "\"If you are working on something that you really care about, you don't have to be pushed. The vision pulls you.\" - Steve Jobs",
            "\"Experience is the teacher of all things.\" - Julius Caesar",
            "\"The only true wisdom is in knowing you know nothing.\" - Socrates",
            "\"Be yourself; everyone else is already taken.\" - Oscar Wilde",
            "\"Two things are infinite: the universe and human stupidity; and I'm not sure about the universe.\" - Albert Einstein"
        ]
    
    def _get_joke(self) -> str:
        """
        Get a random joke.
        
        Returns:
            Random joke string
        """
        return random.choice(self.jokes)
    
    def _get_fun_fact(self) -> str:
        """
        Get a random fun fact.
        
        Returns:
            Random fun fact string
        """
        return random.choice(self.fun_facts)
    
    def _get_quote(self) -> str:
        """
        Get a random inspirational quote.
        
        Returns:
            Random quote string
        """
        return random.choice(self.quotes)
    
    def add_joke(self, joke: str) -> None:
        """
        Add a new joke to the collection.
        
        Args:
            joke: Joke text to add
        """
        if joke and joke not in self.jokes:
            self.jokes.append(joke)
            self.logger.info("Added new joke to collection")
    
    def add_fun_fact(self, fact: str) -> None:
        """
        Add a new fun fact to the collection.
        
        Args:
            fact: Fun fact text to add
        """
        if fact and fact not in self.fun_facts:
            self.fun_facts.append(fact)
            self.logger.info("Added new fun fact to collection")
    
    def add_quote(self, quote: str) -> None:
        """
        Add a new quote to the collection.
        
        Args:
            quote: Quote text to add
        """
        if quote and quote not in self.quotes:
            self.quotes.append(quote)
            self.logger.info("Added new quote to collection")
    
    def get_description(self) -> str:
        """Get description of this action."""
        return "Provide entertainment content like jokes, fun facts, and quotes"
    
    def get_required_parameters(self) -> list:
        """Get required parameters for this action."""
        return []  # No required parameters
    
    def get_optional_parameters(self) -> list:
        """Get optional parameters for this action."""
        return ['type']
    
    def get_examples(self) -> list:
        """Get example usage for this action."""
        return [
            "tell me a joke",
            "make me laugh",
            "give me a fun fact",
            "share an inspirational quote"
        ]
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """
        Validate parameters for entertainment requests.
        
        Args:
            parameters: Parameters to validate
            
        Returns:
            True if parameters are valid
        """
        # Entertainment doesn't require specific parameters
        return True
    
    def get_content_stats(self) -> Dict[str, int]:
        """
        Get statistics about available content.
        
        Returns:
            Dictionary with content counts
        """
        return {
            'jokes': len(self.jokes),
            'fun_facts': len(self.fun_facts),
            'quotes': len(self.quotes),
            'total_content': len(self.jokes) + len(self.fun_facts) + len(self.quotes)
        }
