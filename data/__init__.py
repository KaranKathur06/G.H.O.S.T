"""
Data module for G.H.O.S.T. Virtual Assistant.

This module handles configuration files, user data storage, logging,
and memory persistence for the virtual assistant.
"""

from .config_manager import ConfigManager
from .logger_setup import setup_logging

__all__ = ['ConfigManager', 'setup_logging']
