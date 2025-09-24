"""
Configuration manager for G.H.O.S.T. virtual assistant.

This module handles loading, saving, and managing configuration files
including settings, API keys, and application paths.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging
from configparser import ConfigParser


class ConfigManager:
    """
    Manages configuration files and settings for the virtual assistant.
    
    Handles JSON config files, environment variables, and .ini files.
    """
    
    def __init__(self, config_dir: str = "data/config"):
        """
        Initialize the configuration manager.
        
        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        
        # Configuration files
        self.main_config_file = self.config_dir / "config.json"
        self.paths_config_file = self.config_dir / "paths.json"
        self.env_config_file = self.config_dir / ".env"
        
        # Loaded configurations
        self.main_config: Dict[str, Any] = {}
        self.paths_config: Dict[str, Any] = {}
        self.env_config: Dict[str, str] = {}
        
        # Load existing configurations
        self._load_configurations()
    
    def _load_configurations(self) -> None:
        """Load all configuration files."""
        try:
            # Load main configuration
            if self.main_config_file.exists():
                with open(self.main_config_file, 'r', encoding='utf-8') as f:
                    self.main_config = json.load(f)
            else:
                self.main_config = self._get_default_config()
                self.save_main_config()
            
            # Load paths configuration
            if self.paths_config_file.exists():
                with open(self.paths_config_file, 'r', encoding='utf-8') as f:
                    self.paths_config = json.load(f)
            else:
                self.paths_config = self._get_default_paths()
                self.save_paths_config()
            
            # Load environment configuration
            self._load_env_config()
            
            self.logger.info("Configuration files loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading configurations: {e}")
            # Use defaults if loading fails
            self.main_config = self._get_default_config()
            self.paths_config = self._get_default_paths()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration settings.
        
        Returns:
            Dictionary with default configuration
        """
        return {
            "assistant": {
                "name": "G.H.O.S.T.",
                "version": "1.0.0",
                "debug_mode": False,
                "log_level": "INFO"
            },
            "speech": {
                "stt": {
                    "engine": "google",
                    "language": "en-US",
                    "energy_threshold": 300,
                    "dynamic_energy_threshold": True
                },
                "tts": {
                    "engine": "pyttsx3",
                    "rate": 200,
                    "volume": 0.9,
                    "voice_id": None
                }
            },
            "actions": {
                "apps": {
                    "enabled": True,
                    "paths": {}
                },
                "web": {
                    "enabled": True,
                    "default_engine": "google",
                    "custom_engines": {}
                },
                "system": {
                    "enabled": True,
                    "confirm_dangerous": True,
                    "allowed_operations": ["time", "date", "shutdown", "restart", "sleep", "lock"]
                },
                "weather": {
                    "enabled": True,
                    "api_key": "",
                    "provider": "openweathermap",
                    "default_location": "New York",
                    "units": "metric"
                },
                "entertainment": {
                    "enabled": True,
                    "default_type": "joke"
                }
            },
            "memory": {
                "data_dir": "data/memory",
                "max_conversation_history": 1000,
                "auto_cleanup_days": 30
            },
            "ui": {
                "enabled": False,
                "port": 8080,
                "host": "localhost"
            }
        }
    
    def _get_default_paths(self) -> Dict[str, Any]:
        """
        Get default application paths.
        
        Returns:
            Dictionary with default application paths
        """
        return {
            "applications": {
                "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                "firefox": "C:\\Program Files\\Mozilla Firefox\\firefox.exe",
                "notepad": "notepad.exe",
                "calculator": "calc.exe",
                "vscode": "C:\\Users\\%USERNAME%\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
                "spotify": "C:\\Users\\%USERNAME%\\AppData\\Roaming\\Spotify\\Spotify.exe",
                "discord": "C:\\Users\\%USERNAME%\\AppData\\Local\\Discord\\Update.exe",
                "whatsapp": "C:\\Users\\%USERNAME%\\AppData\\Local\\WhatsApp\\WhatsApp.exe"
            },
            "directories": {
                "downloads": "C:\\Users\\%USERNAME%\\Downloads",
                "documents": "C:\\Users\\%USERNAME%\\Documents",
                "desktop": "C:\\Users\\%USERNAME%\\Desktop",
                "music": "C:\\Users\\%USERNAME%\\Music",
                "pictures": "C:\\Users\\%USERNAME%\\Pictures"
            }
        }
    
    def _load_env_config(self) -> None:
        """Load environment configuration from .env file."""
        if self.env_config_file.exists():
            try:
                with open(self.env_config_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            self.env_config[key.strip()] = value.strip()
            except Exception as e:
                self.logger.error(f"Error loading .env file: {e}")
        else:
            # Create example .env file
            self._create_example_env_file()
    
    def _create_example_env_file(self) -> None:
        """Create an example .env file with placeholder values."""
        example_content = """# G.H.O.S.T. Virtual Assistant Environment Configuration
# Copy this file to .env and fill in your actual API keys

# Weather API Keys
OPENWEATHER_API_KEY=your_openweathermap_api_key_here
WEATHERAPI_KEY=your_weatherapi_key_here

# Speech Recognition API Keys
GOOGLE_SPEECH_API_KEY=your_google_speech_api_key_here
AZURE_SPEECH_KEY=your_azure_speech_key_here

# Other API Keys
WOLFRAM_ALPHA_API_KEY=your_wolfram_alpha_key_here

# Database Configuration (if needed)
DATABASE_URL=sqlite:///data/ghost.db

# Security Settings
SECRET_KEY=your_secret_key_here
"""
        
        example_file = self.config_dir / ".env.example"
        try:
            with open(example_file, 'w', encoding='utf-8') as f:
                f.write(example_content)
            self.logger.info("Created .env.example file")
        except Exception as e:
            self.logger.error(f"Error creating .env.example file: {e}")
    
    def get_config(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to the configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self.main_config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set_config(self, key_path: str, value: Any) -> None:
        """
        Set configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to the configuration key
            value: Value to set
        """
        keys = key_path.split('.')
        config = self.main_config
        
        # Navigate to the parent dictionary
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # Set the final value
        config[keys[-1]] = value
        self.logger.debug(f"Set config {key_path} = {value}")
    
    def get_path(self, path_name: str) -> Optional[str]:
        """
        Get application or directory path.
        
        Args:
            path_name: Name of the path to retrieve
            
        Returns:
            Path string or None if not found
        """
        # Check applications first
        app_path = self.paths_config.get('applications', {}).get(path_name)
        if app_path:
            return os.path.expandvars(app_path)
        
        # Check directories
        dir_path = self.paths_config.get('directories', {}).get(path_name)
        if dir_path:
            return os.path.expandvars(dir_path)
        
        return None
    
    def set_path(self, path_name: str, path_value: str, path_type: str = 'applications') -> None:
        """
        Set application or directory path.
        
        Args:
            path_name: Name of the path
            path_value: Path value
            path_type: Type of path ('applications' or 'directories')
        """
        if path_type not in self.paths_config:
            self.paths_config[path_type] = {}
        
        self.paths_config[path_type][path_name] = path_value
        self.logger.info(f"Set {path_type} path {path_name} = {path_value}")
    
    def get_env(self, key: str, default: str = "") -> str:
        """
        Get environment variable value.
        
        Args:
            key: Environment variable key
            default: Default value if not found
            
        Returns:
            Environment variable value or default
        """
        # Check loaded .env file first
        if key in self.env_config:
            return self.env_config[key]
        
        # Check system environment variables
        return os.getenv(key, default)
    
    def save_main_config(self) -> bool:
        """
        Save main configuration to file.
        
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            with open(self.main_config_file, 'w', encoding='utf-8') as f:
                json.dump(self.main_config, f, indent=2, ensure_ascii=False)
            self.logger.info("Main configuration saved")
            return True
        except Exception as e:
            self.logger.error(f"Error saving main configuration: {e}")
            return False
    
    def save_paths_config(self) -> bool:
        """
        Save paths configuration to file.
        
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            with open(self.paths_config_file, 'w', encoding='utf-8') as f:
                json.dump(self.paths_config, f, indent=2, ensure_ascii=False)
            self.logger.info("Paths configuration saved")
            return True
        except Exception as e:
            self.logger.error(f"Error saving paths configuration: {e}")
            return False
    
    def reload_config(self) -> None:
        """Reload all configuration files."""
        self.logger.info("Reloading configuration files")
        self._load_configurations()
    
    def get_full_config(self) -> Dict[str, Any]:
        """
        Get the complete configuration.
        
        Returns:
            Dictionary with all configuration data
        """
        return {
            'main': self.main_config.copy(),
            'paths': self.paths_config.copy(),
            'env_keys': list(self.env_config.keys())  # Don't expose env values
        }
    
    def validate_config(self) -> Dict[str, list]:
        """
        Validate configuration and return any issues.
        
        Returns:
            Dictionary with validation results
        """
        issues = {
            'errors': [],
            'warnings': [],
            'missing_paths': []
        }
        
        # Check required configuration sections
        required_sections = ['assistant', 'speech', 'actions', 'memory']
        for section in required_sections:
            if section not in self.main_config:
                issues['errors'].append(f"Missing required section: {section}")
        
        # Check application paths
        for app_name, app_path in self.paths_config.get('applications', {}).items():
            expanded_path = os.path.expandvars(app_path)
            if not os.path.exists(expanded_path) and app_name not in ['notepad', 'calculator']:
                issues['missing_paths'].append(f"{app_name}: {expanded_path}")
        
        # Check API keys
        weather_enabled = self.get_config('actions.weather.enabled', False)
        if weather_enabled and not self.get_env('OPENWEATHER_API_KEY'):
            issues['warnings'].append("Weather is enabled but no API key configured")
        
        return issues
