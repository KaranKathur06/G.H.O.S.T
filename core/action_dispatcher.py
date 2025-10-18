"""
Enhanced Action Dispatcher for G.H.O.S.T.

This module provides intelligent action dispatching based on LLM-generated
structured responses, enabling unlimited command execution capabilities.
"""

import logging
import asyncio
import threading
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from datetime import datetime
import json
import subprocess
import webbrowser
import os
import sys
from pathlib import Path

# Import action registry
from .action_registry import ActionRegistry, get_global_registry
from .system_indexer import SystemIndexer

@dataclass
class ActionResult:
    """Result of action execution."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    execution_time: float = 0.0
    error: Optional[str] = None

class ActionDispatcher:
    """
    Enhanced action dispatcher that executes actions from structured LLM responses.
    
    Supports unlimited command execution through dynamic action registry
    and intelligent parameter handling.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize action dispatcher."""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Core components
        self.action_registry = get_global_registry()
        self.system_indexer = None
        
        # Security settings
        self.require_confirmation = self.config.get('require_confirmation', True)
        self.dangerous_actions = self.config.get('dangerous_actions', [
            'system_command', 'delete_file', 'shutdown', 'restart'
        ])
        
        # Performance settings
        self.max_concurrent_actions = self.config.get('max_concurrent_actions', 3)
        self.action_timeout = self.config.get('action_timeout', 30.0)
        
        # Built-in action handlers
        self._register_builtin_actions()
        
        self.logger.info("Action Dispatcher initialized")
    
    def set_system_indexer(self, indexer: SystemIndexer):
        """Set system indexer for file/app search capabilities."""
        self.system_indexer = indexer
    
    def _register_builtin_actions(self):
        """Register built-in action handlers."""
        self.builtin_handlers = {
            'open_application': self._handle_open_application,
            'open_web': self._handle_open_web,
            'search_web': self._handle_search_web,
            'open_system_item': self._handle_open_system_item,
            'play_media': self._handle_play_media,
            'tell_joke': self._handle_tell_joke,
            'get_time': self._handle_get_time,
            'get_weather': self._handle_get_weather,
            'system_command': self._handle_system_command
        }
    
    async def execute_action(self, action_data: Dict[str, Any], 
                           confirmation_callback: Optional[Callable] = None) -> ActionResult:
        """
        Execute an action from structured LLM response.
        
        Args:
            action_data: Action data with 'type' and 'parameters'
            confirmation_callback: Optional callback for dangerous action confirmation
            
        Returns:
            ActionResult with execution details
        """
        if not action_data or not isinstance(action_data, dict):
            return ActionResult(
                success=False,
                message="Invalid action data provided, Sir.",
                error="Action data must be a dictionary"
            )
        
        action_type = action_data.get('type')
        parameters = action_data.get('parameters', {})
        
        if not action_type:
            return ActionResult(
                success=False,
                message="No action type specified, Sir.",
                error="Missing action type"
            )
        
        try:
            start_time = datetime.now()
            
            # Check for dangerous actions
            if self._is_dangerous_action(action_type):
                if self.require_confirmation:
                    if confirmation_callback:
                        confirmed = await self._get_confirmation(
                            action_type, parameters, confirmation_callback
                        )
                        if not confirmed:
                            return ActionResult(
                                success=False,
                                message="Action cancelled by user, Sir.",
                                error="User declined confirmation"
                            )
                    else:
                        return ActionResult(
                            success=False,
                            message="This action requires confirmation, Sir.",
                            error="No confirmation callback provided"
                        )
            
            # Execute action
            result = await self._execute_action_internal(action_type, parameters)
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            result.execution_time = execution_time
            
            self.logger.info(f"Action '{action_type}' executed in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing action '{action_type}': {e}")
            return ActionResult(
                success=False,
                message=f"I encountered an error executing that action, Sir: {str(e)}",
                error=str(e)
            )
    
    async def _execute_action_internal(self, action_type: str, 
                                     parameters: Dict[str, Any]) -> ActionResult:
        """Internal action execution with timeout."""
        try:
            # Try built-in handlers first
            if action_type in self.builtin_handlers:
                handler = self.builtin_handlers[action_type]
                
                # Execute with timeout
                result = await asyncio.wait_for(
                    self._run_handler(handler, parameters),
                    timeout=self.action_timeout
                )
                return result
            
            # Try action registry
            registry_result = self.action_registry.execute_action(action_type, parameters)
            
            if registry_result.get('success', False):
                return ActionResult(
                    success=True,
                    message=registry_result.get('message', 'Action completed successfully, Sir.'),
                    data=registry_result
                )
            else:
                return ActionResult(
                    success=False,
                    message=registry_result.get('message', f"Failed to execute '{action_type}', Sir."),
                    error=registry_result.get('error', 'Unknown error')
                )
                
        except asyncio.TimeoutError:
            return ActionResult(
                success=False,
                message="The action timed out, Sir.",
                error="Action execution timeout"
            )
        except Exception as e:
            return ActionResult(
                success=False,
                message=f"Error executing action, Sir: {str(e)}",
                error=str(e)
            )
    
    async def _run_handler(self, handler: Callable, parameters: Dict[str, Any]) -> ActionResult:
        """Run handler in thread pool for non-blocking execution."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, handler, parameters)
    
    def _is_dangerous_action(self, action_type: str) -> bool:
        """Check if action is potentially dangerous."""
        return action_type in self.dangerous_actions
    
    async def _get_confirmation(self, action_type: str, parameters: Dict[str, Any],
                              callback: Callable) -> bool:
        """Get user confirmation for dangerous actions."""
        try:
            confirmation_message = f"Are you sure you want to execute '{action_type}', Sir?"
            return await callback(confirmation_message, action_type, parameters)
        except Exception as e:
            self.logger.error(f"Error getting confirmation: {e}")
            return False
    
    # Built-in Action Handlers
    
    def _handle_open_application(self, parameters: Dict[str, Any]) -> ActionResult:
        """Handle opening applications."""
        try:
            app_name = parameters.get('app_name', '').lower()
            
            if not app_name:
                return ActionResult(
                    success=False,
                    message="No application name provided, Sir.",
                    error="Missing app_name parameter"
                )
            
            # Search for application using system indexer
            if self.system_indexer:
                search_results = self.system_indexer.search(app_name, item_type='application', limit=5)
                
                if search_results:
                    # Use best match
                    best_match = search_results[0]
                    app_path = best_match.item.path
                    
                    if app_path and os.path.exists(app_path):
                        subprocess.Popen([app_path], shell=True)
                        return ActionResult(
                            success=True,
                            message=f"Opening {best_match.item.name}, Sir.",
                            data={'app_name': best_match.item.name, 'path': app_path}
                        )
            
            # Fallback to common applications
            common_apps = {
                'calculator': 'calc.exe',
                'notepad': 'notepad.exe',
                'paint': 'mspaint.exe',
                'browser': 'start chrome',
                'chrome': 'start chrome',
                'firefox': 'start firefox',
                'edge': 'start msedge',
                'explorer': 'explorer.exe',
                'cmd': 'cmd.exe',
                'powershell': 'powershell.exe'
            }
            
            if app_name in common_apps:
                subprocess.Popen(common_apps[app_name], shell=True)
                return ActionResult(
                    success=True,
                    message=f"Opening {app_name}, Sir.",
                    data={'app_name': app_name}
                )
            
            return ActionResult(
                success=False,
                message=f"I couldn't find '{app_name}' on your system, Sir.",
                error="Application not found"
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                message=f"Error opening application, Sir: {str(e)}",
                error=str(e)
            )
    
    def _handle_open_web(self, parameters: Dict[str, Any]) -> ActionResult:
        """Handle opening web URLs."""
        try:
            url = parameters.get('url', '')
            
            if not url:
                return ActionResult(
                    success=False,
                    message="No URL provided, Sir.",
                    error="Missing url parameter"
                )
            
            # Ensure URL has protocol
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            webbrowser.open(url)
            
            return ActionResult(
                success=True,
                message=f"Opening {url}, Sir.",
                data={'url': url}
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                message=f"Error opening website, Sir: {str(e)}",
                error=str(e)
            )
    
    def _handle_search_web(self, parameters: Dict[str, Any]) -> ActionResult:
        """Handle web search."""
        try:
            query = parameters.get('query', '')
            
            if not query:
                return ActionResult(
                    success=False,
                    message="No search query provided, Sir.",
                    error="Missing query parameter"
                )
            
            # Create Google search URL
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(search_url)
            
            return ActionResult(
                success=True,
                message=f"Searching for '{query}', Sir.",
                data={'query': query, 'url': search_url}
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                message=f"Error performing web search, Sir: {str(e)}",
                error=str(e)
            )
    
    def _handle_open_system_item(self, parameters: Dict[str, Any]) -> ActionResult:
        """Handle opening files/folders."""
        try:
            path = parameters.get('path', '')
            
            if not path:
                return ActionResult(
                    success=False,
                    message="No path provided, Sir.",
                    error="Missing path parameter"
                )
            
            # Search for item using system indexer if path is not absolute
            if not os.path.isabs(path) and self.system_indexer:
                search_results = self.system_indexer.search(path, limit=5)
                
                if search_results:
                    best_match = search_results[0]
                    path = best_match.item.path
            
            if os.path.exists(path):
                if sys.platform == "win32":
                    os.startfile(path)
                else:
                    subprocess.run(['xdg-open', path])
                
                return ActionResult(
                    success=True,
                    message=f"Opening {os.path.basename(path)}, Sir.",
                    data={'path': path}
                )
            else:
                return ActionResult(
                    success=False,
                    message=f"I couldn't find '{path}', Sir.",
                    error="Path not found"
                )
                
        except Exception as e:
            return ActionResult(
                success=False,
                message=f"Error opening system item, Sir: {str(e)}",
                error=str(e)
            )
    
    def _handle_play_media(self, parameters: Dict[str, Any]) -> ActionResult:
        """Handle media playback."""
        try:
            content = parameters.get('content', '')
            source = parameters.get('source', 'youtube')
            
            if not content:
                return ActionResult(
                    success=False,
                    message="No media content specified, Sir.",
                    error="Missing content parameter"
                )
            
            if source.lower() == 'youtube':
                # Search YouTube
                search_url = f"https://www.youtube.com/results?search_query={content.replace(' ', '+')}"
                webbrowser.open(search_url)
                
                return ActionResult(
                    success=True,
                    message=f"Searching YouTube for '{content}', Sir.",
                    data={'content': content, 'source': 'youtube', 'url': search_url}
                )
            
            elif source.lower() == 'spotify':
                # Open Spotify search
                spotify_url = f"https://open.spotify.com/search/{content.replace(' ', '%20')}"
                webbrowser.open(spotify_url)
                
                return ActionResult(
                    success=True,
                    message=f"Searching Spotify for '{content}', Sir.",
                    data={'content': content, 'source': 'spotify', 'url': spotify_url}
                )
            
            else:
                return ActionResult(
                    success=False,
                    message=f"Unsupported media source '{source}', Sir.",
                    error="Unsupported source"
                )
                
        except Exception as e:
            return ActionResult(
                success=False,
                message=f"Error playing media, Sir: {str(e)}",
                error=str(e)
            )
    
    def _handle_tell_joke(self, parameters: Dict[str, Any]) -> ActionResult:
        """Handle joke telling."""
        try:
            topic = parameters.get('topic', 'general')
            
            jokes = {
                'general': [
                    "Why don't scientists trust atoms? Because they make up everything, Sir!",
                    "I told my wife she was drawing her eyebrows too high. She looked surprised, Sir.",
                    "Why don't eggs tell jokes? They'd crack each other up, Sir!"
                ],
                'computer': [
                    "Why do programmers prefer dark mode? Because light attracts bugs, Sir!",
                    "There are only 10 types of people in the world: those who understand binary and those who don't, Sir.",
                    "Why did the computer go to the doctor? Because it had a virus, Sir!"
                ],
                'programming': [
                    "A SQL query goes into a bar, walks up to two tables and asks: 'Can I join you?', Sir.",
                    "Why do Java developers wear glasses? Because they don't C#, Sir!",
                    "How many programmers does it take to change a light bulb? None, that's a hardware problem, Sir!"
                ]
            }
            
            import random
            joke_list = jokes.get(topic.lower(), jokes['general'])
            joke = random.choice(joke_list)
            
            return ActionResult(
                success=True,
                message=joke,
                data={'topic': topic, 'joke': joke}
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                message=f"Error telling joke, Sir: {str(e)}",
                error=str(e)
            )
    
    def _handle_get_time(self, parameters: Dict[str, Any]) -> ActionResult:
        """Handle time requests."""
        try:
            from datetime import datetime
            
            now = datetime.now()
            time_str = now.strftime("%I:%M %p")
            date_str = now.strftime("%A, %B %d, %Y")
            
            message = f"The current time is {time_str} on {date_str}, Sir."
            
            return ActionResult(
                success=True,
                message=message,
                data={
                    'time': time_str,
                    'date': date_str,
                    'timestamp': now.isoformat()
                }
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                message=f"Error getting time, Sir: {str(e)}",
                error=str(e)
            )
    
    def _handle_get_weather(self, parameters: Dict[str, Any]) -> ActionResult:
        """Handle weather requests."""
        try:
            location = parameters.get('location', 'current location')
            
            # For now, open weather website
            weather_url = f"https://www.weather.com/weather/today/l/{location.replace(' ', '+')}"
            webbrowser.open(weather_url)
            
            return ActionResult(
                success=True,
                message=f"Opening weather information for {location}, Sir.",
                data={'location': location, 'url': weather_url}
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                message=f"Error getting weather, Sir: {str(e)}",
                error=str(e)
            )
    
    def _handle_system_command(self, parameters: Dict[str, Any]) -> ActionResult:
        """Handle system commands (dangerous - requires confirmation)."""
        try:
            command = parameters.get('command', '')
            
            if not command:
                return ActionResult(
                    success=False,
                    message="No command provided, Sir.",
                    error="Missing command parameter"
                )
            
            # Execute system command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return ActionResult(
                    success=True,
                    message=f"Command executed successfully, Sir.",
                    data={
                        'command': command,
                        'output': result.stdout,
                        'return_code': result.returncode
                    }
                )
            else:
                return ActionResult(
                    success=False,
                    message=f"Command failed with error, Sir.",
                    error=result.stderr,
                    data={
                        'command': command,
                        'return_code': result.returncode
                    }
                )
                
        except subprocess.TimeoutExpired:
            return ActionResult(
                success=False,
                message="Command timed out, Sir.",
                error="Command execution timeout"
            )
        except Exception as e:
            return ActionResult(
                success=False,
                message=f"Error executing command, Sir: {str(e)}",
                error=str(e)
            )
    
    def get_available_actions(self) -> List[str]:
        """Get list of available action types."""
        builtin_actions = list(self.builtin_handlers.keys())
        registry_actions = self.action_registry.get_supported_intents()
        
        return list(set(builtin_actions + registry_actions))
    
    def get_action_info(self, action_type: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific action type."""
        if action_type in self.builtin_handlers:
            return {
                'type': action_type,
                'source': 'builtin',
                'dangerous': action_type in self.dangerous_actions,
                'description': f"Built-in {action_type} handler"
            }
        
        # Check action registry
        action = self.action_registry.get_action(action_type)
        if action:
            metadata = action.get_metadata()
            return {
                'type': action_type,
                'source': 'registry',
                'dangerous': action_type in self.dangerous_actions,
                'description': metadata.description,
                'category': metadata.category,
                'parameters': metadata.parameters
            }
        
        return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get dispatcher status."""
        return {
            'available_actions': len(self.get_available_actions()),
            'builtin_actions': len(self.builtin_handlers),
            'registry_actions': len(self.action_registry.get_all_actions()),
            'dangerous_actions': len(self.dangerous_actions),
            'require_confirmation': self.require_confirmation,
            'max_concurrent_actions': self.max_concurrent_actions,
            'action_timeout': self.action_timeout
        }
