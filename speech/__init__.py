"""
Speech module for G.H.O.S.T. Generative AI Virtual Assistant.

This module handles voice input (speech-to-text) and voice output (text-to-speech)
functionality for natural voice interaction with the assistant.
"""

from .speech_to_text import SpeechToText
from .enhanced_tts import EnhancedTTS
from .wake_word_listener import WakeWordListener

__all__ = ['SpeechToText', 'EnhancedTTS', 'WakeWordListener']
