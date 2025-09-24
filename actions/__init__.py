"""
Actions module for G.H.O.S.T. Virtual Assistant.

This module contains handlers for various tasks like opening applications,
web search, WhatsApp messaging, weather queries, jokes, and system control.
"""

from .action_dispatcher import ActionDispatcher
from .base_action import BaseAction
from .app_launcher import AppLauncher
from .web_search import WebSearch
from .system_control import SystemControl
from .weather import Weather
from .entertainment import Entertainment

__all__ = [
    'ActionDispatcher', 'BaseAction', 'AppLauncher', 
    'WebSearch', 'SystemControl', 'Weather', 'Entertainment'
]
