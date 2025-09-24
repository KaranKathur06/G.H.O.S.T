"""
Application launcher action for G.H.O.S.T. virtual assistant.

This module handles opening and launching various applications
based on user commands and configured application paths.
"""

import os
import subprocess
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from .base_action import BaseAction


class AppLauncher(BaseAction):
    """
    Handles launching applications and programs.
    
    Supports launching applications by name using configured paths.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the application launcher.
        
        Args:
            config: Configuration dictionary with app paths
        """
        super().__init__(config)
        
        # Load application paths from config
        self.app_paths = config.get('paths', {})
        self.default_apps = self._get_default_apps()
        
        # Merge default and configured apps
        self.available_apps = {**self.default_apps, **self.app_paths}
    
    def _get_default_apps(self) -> Dict[str, str]:
        """
        Get default application paths for common programs.
        
        Returns:
            Dictionary mapping app names to their paths
        """
        defaults = {
            'chrome': 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
            'firefox': 'C:\\Program Files\\Mozilla Firefox\\firefox.exe',
            'notepad': 'notepad.exe',
            'calculator': 'calc.exe',
            'vscode': 'C:\\Users\\%USERNAME%\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe',
            'spotify': 'C:\\Users\\%USERNAME%\\AppData\\Roaming\\Spotify\\Spotify.exe',
            'discord': 'C:\\Users\\%USERNAME%\\AppData\\Local\\Discord\\Update.exe',
            'whatsapp': 'C:\\Users\\%USERNAME%\\AppData\\Local\\WhatsApp\\WhatsApp.exe'
        }
        
        # Expand environment variables
        expanded_defaults = {}
        for name, path in defaults.items():
            expanded_path = os.path.expandvars(path)
            if os.path.exists(expanded_path) or name in ['notepad', 'calculator']:
                expanded_defaults[name] = expanded_path
        
        return expanded_defaults
    
    def execute(self, parameters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Launch an application.
        
        Args:
            parameters: Dictionary containing 'app_name' parameter
            
        Returns:
            Dictionary with execution result
        """
        if not self.is_available():
            return self.handle_error(Exception("App launcher is disabled"), parameters)
        
        app_name = parameters.get('app_name', '').lower().strip()
        
        if not app_name:
            return {
                'success': False,
                'message': 'Please specify an application name',
                'available_apps': list(self.available_apps.keys())
            }
        
        try:
            # Find matching application
            app_path = self._find_app_path(app_name)
            
            if not app_path:
                return {
                    'success': False,
                    'message': f'Application "{app_name}" not found',
                    'suggestions': self._get_app_suggestions(app_name),
                    'available_apps': list(self.available_apps.keys())
                }
            
            # Launch the application
            success = self._launch_app(app_path, app_name)
            
            if success:
                result = {
                    'success': True,
                    'message': f'Successfully launched {app_name}',
                    'app_name': app_name,
                    'app_path': app_path
                }
            else:
                result = {
                    'success': False,
                    'message': f'Failed to launch {app_name}',
                    'app_name': app_name
                }
            
            self.log_execution(parameters, result)
            return result
            
        except Exception as e:
            return self.handle_error(e, parameters)
    
    def _find_app_path(self, app_name: str) -> Optional[str]:
        """
        Find the path for an application by name.
        
        Args:
            app_name: Name of the application to find
            
        Returns:
            Path to the application, None if not found
        """
        # Direct match
        if app_name in self.available_apps:
            return self.available_apps[app_name]
        
        # Partial match
        for name, path in self.available_apps.items():
            if app_name in name or name in app_name:
                return path
        
        return None
    
    def _launch_app(self, app_path: str, app_name: str) -> bool:
        """
        Launch an application using its path.
        
        Args:
            app_path: Path to the application executable
            app_name: Name of the application (for logging)
            
        Returns:
            True if launch was successful, False otherwise
        """
        try:
            self.logger.info(f"Launching {app_name} from {app_path}")
            
            # Use subprocess to launch the application
            if os.name == 'nt':  # Windows
                subprocess.Popen([app_path], shell=True)
            else:  # Unix-like systems
                subprocess.Popen([app_path])
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to launch {app_name}: {e}")
            return False
    
    def _get_app_suggestions(self, app_name: str) -> list:
        """
        Get suggestions for similar application names.
        
        Args:
            app_name: The requested app name
            
        Returns:
            List of suggested app names
        """
        suggestions = []
        
        for available_app in self.available_apps.keys():
            # Simple similarity check
            if (app_name in available_app or 
                available_app in app_name or
                any(word in available_app for word in app_name.split())):
                suggestions.append(available_app)
        
        return suggestions[:3]  # Return top 3 suggestions
    
    def get_description(self) -> str:
        """Get description of this action."""
        return "Launch applications and programs by name"
    
    def get_required_parameters(self) -> list:
        """Get required parameters for this action."""
        return ['app_name']
    
    def get_examples(self) -> list:
        """Get example usage for this action."""
        return [
            "open chrome",
            "launch spotify",
            "start calculator",
            "open notepad"
        ]
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """
        Validate parameters for app launching.
        
        Args:
            parameters: Parameters to validate
            
        Returns:
            True if parameters are valid
        """
        return 'app_name' in parameters and bool(parameters['app_name'].strip())
