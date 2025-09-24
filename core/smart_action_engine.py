"""
Smart Action Engine for G.H.O.S.T.

This module provides intelligent action execution for any user request.
Can handle applications, media, files, system control, and web actions
dynamically without hardcoded limitations.
"""

import os
import sys
import subprocess
import webbrowser
import psutil
import logging
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime
import json
import urllib.parse
import requests
from concurrent.futures import ThreadPoolExecutor

# Windows registry support
try:
    import winreg
    WINREG_AVAILABLE = True
except ImportError:
    WINREG_AVAILABLE = False
    winreg = None

# Windows-specific imports
WIN32_AVAILABLE = False
PYCAW_AVAILABLE = False

if sys.platform == "win32":
    try:
        import win32gui
        import win32con
        import win32api
        import win32process
        WIN32_AVAILABLE = True
    except ImportError:
        WIN32_AVAILABLE = False
    
    try:
        import pycaw.pycaw as pycaw
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        PYCAW_AVAILABLE = True
    except ImportError:
        PYCAW_AVAILABLE = False

@dataclass
class ActionResult:
    """Result of action execution."""
    success: bool
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    follow_up_suggestions: List[str] = field(default_factory=list)

@dataclass
class MediaSource:
    """Media source configuration."""
    name: str
    type: str  # youtube, spotify, local, vlc
    url_pattern: str = ""
    executable: str = ""
    api_endpoint: str = ""

class SmartActionEngine:
    """
    Smart Action Engine that can execute any user request intelligently.
    
    Capabilities:
    - Launch any application by name
    - Play media from any source (YouTube, Spotify, local files)
    - Open any file or folder
    - Control system settings
    - Perform web searches and navigation
    - Handle complex multi-step actions
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize Smart Action Engine."""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # System indexer for finding items
        self.system_indexer = None
        
        # Application registry
        self.installed_apps = {}
        self.app_aliases = {}
        
        # Media sources
        self.media_sources = self._load_media_sources()
        
        # Browser preferences
        self.default_browser = self._detect_default_browser()
        
        # System control interfaces
        self.volume_interface = None
        
        # Performance settings
        self.max_workers = self.config.get('max_workers', 4)
        self.timeout = self.config.get('action_timeout', 30.0)
        
        # Initialize components
        self._initialize_system_interfaces()
        self._discover_applications()
        
        self.logger.info("Smart Action Engine initialized")
    
    def _load_media_sources(self) -> Dict[str, MediaSource]:
        """Load available media sources."""
        return {
            "youtube": MediaSource(
                name="YouTube",
                type="youtube",
                url_pattern="https://www.youtube.com/results?search_query={query}"
            ),
            "spotify": MediaSource(
                name="Spotify",
                type="spotify",
                executable="spotify.exe",
                url_pattern="spotify:search:{query}"
            ),
            "vlc": MediaSource(
                name="VLC Media Player",
                type="vlc",
                executable="vlc.exe"
            ),
            "windows_media": MediaSource(
                name="Windows Media Player",
                type="windows_media",
                executable="wmplayer.exe"
            )
        }
    
    def _detect_default_browser(self) -> str:
        """Detect the default web browser."""
        try:
            if sys.platform == "win32" and WINREG_AVAILABLE:
                # Check registry for default browser
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                  r"Software\\Microsoft\\Windows\\Shell\\Associations\\UrlAssociations\\http\\UserChoice") as key:
                    prog_id = winreg.QueryValueEx(key, "ProgId")[0]
                    
                    if "chrome" in prog_id.lower():
                        return "chrome"
                    elif "firefox" in prog_id.lower():
                        return "firefox"
                    elif "edge" in prog_id.lower():
                        return "edge"
            
            return "default"
            
        except Exception as e:
            self.logger.debug(f"Could not detect default browser: {e}")
            return "default"
    
    def _initialize_system_interfaces(self):
        """Initialize system control interfaces."""
        try:
            if sys.platform == "win32" and PYCAW_AVAILABLE:
                # Initialize volume control
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                self.volume_interface = interface.QueryInterface(IAudioEndpointVolume)
                
        except Exception as e:
            self.logger.warning(f"Could not initialize system interfaces: {e}")
    
    def _discover_applications(self):
        """Discover installed applications."""
        try:
            self.installed_apps = {}
            self.app_aliases = {}
            
            if sys.platform == "win32":
                self._discover_windows_applications()
            
            self.logger.info(f"Discovered {len(self.installed_apps)} applications")
            
        except Exception as e:
            self.logger.error(f"Error discovering applications: {e}")
    
    def _discover_windows_applications(self):
        """Discover Windows applications."""
        # Common application paths
        search_paths = [
            "C:\\Program Files",
            "C:\\Program Files (x86)",
            os.path.expanduser("~\\AppData\\Local\\Programs"),
            os.path.expanduser("~\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs")
        ]
        
        if WINREG_AVAILABLE:
            # Registry locations
            registry_paths = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall"),
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall")
            ]
            
            # Scan registry
            for hkey, subkey_path in registry_paths:
                try:
                    with winreg.OpenKey(hkey, subkey_path) as key:
                        for i in range(winreg.QueryInfoKey(key)[0]):
                            try:
                                subkey_name = winreg.EnumKey(key, i)
                                with winreg.OpenKey(key, subkey_name) as subkey:
                                    self._extract_app_from_registry(subkey)
                            except Exception:
                                continue
                except Exception:
                    continue
        
        # Add common aliases
        self._add_common_aliases()
    
    def _extract_app_from_registry(self, registry_key):
        """Extract application info from registry."""
        try:
            display_name = winreg.QueryValueEx(registry_key, "DisplayName")[0]
            
            try:
                install_location = winreg.QueryValueEx(registry_key, "InstallLocation")[0]
            except FileNotFoundError:
                install_location = ""
            
            try:
                display_icon = winreg.QueryValueEx(registry_key, "DisplayIcon")[0]
            except FileNotFoundError:
                display_icon = ""
            
            if display_name:
                app_key = display_name.lower()
                self.installed_apps[app_key] = {
                    "name": display_name,
                    "path": install_location,
                    "icon": display_icon,
                    "source": "registry"
                }
                
                # Create aliases
                words = display_name.lower().split()
                for word in words:
                    if len(word) > 3:
                        self.app_aliases[word] = app_key
                        
        except Exception as e:
            self.logger.debug(f"Error extracting app from registry: {e}")
    
    def _add_common_aliases(self):
        """Add common application aliases."""
        common_aliases = {
            "chrome": ["google chrome", "chrome"],
            "firefox": ["mozilla firefox", "firefox"],
            "edge": ["microsoft edge", "edge"],
            "notepad": ["notepad"],
            "calculator": ["calculator", "calc"],
            "word": ["microsoft word", "word"],
            "excel": ["microsoft excel", "excel"],
            "powerpoint": ["microsoft powerpoint", "powerpoint"],
            "outlook": ["microsoft outlook", "outlook"],
            "vlc": ["vlc media player", "vlc"],
            "spotify": ["spotify"],
            "discord": ["discord"],
            "steam": ["steam"],
            "vscode": ["visual studio code", "code"],
            "photoshop": ["adobe photoshop", "photoshop"]
        }
        
        for alias, possible_names in common_aliases.items():
            for name in possible_names:
                if name in self.installed_apps:
                    self.app_aliases[alias] = name
                    break
    
    async def execute_action(self, action_type: str, parameters: Dict[str, Any]) -> ActionResult:
        """
        Execute any action intelligently.
        
        Args:
            action_type: Type of action to execute
            parameters: Action parameters
            
        Returns:
            ActionResult with execution details
        """
        start_time = datetime.now()
        
        try:
            result = None
            
            if action_type == "play_media":
                result = await self._execute_play_media(parameters)
            elif action_type == "open_application":
                result = await self._execute_open_application(parameters)
            elif action_type == "open_file":
                result = await self._execute_open_file(parameters)
            elif action_type == "web_search":
                result = await self._execute_web_search(parameters)
            elif action_type == "navigate_web":
                result = await self._execute_navigate_web(parameters)
            elif action_type == "system_control":
                result = await self._execute_system_control(parameters)
            elif action_type == "device_control":
                result = await self._execute_device_control(parameters)
            elif action_type == "find_item":
                result = await self._execute_find_item(parameters)
            else:
                result = ActionResult(
                    success=False,
                    message=f"Unknown action type: {action_type}"
                )
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            result.execution_time = execution_time
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing action {action_type}: {e}")
            return ActionResult(
                success=False,
                message=f"Error executing action: {str(e)}",
                execution_time=(datetime.now() - start_time).total_seconds()
            )
    
    async def _execute_play_media(self, parameters: Dict[str, Any]) -> ActionResult:
        """Execute media playback action."""
        content = parameters.get("content", "")
        platform = parameters.get("platform", "").lower()
        
        if not content:
            return ActionResult(
                success=False,
                message="No content specified for playback, Sir."
            )
        
        # Determine platform if not specified
        if not platform:
            platform = await self._suggest_media_platform(content)
        
        try:
            if platform == "youtube":
                return await self._play_on_youtube(content)
            elif platform == "spotify":
                return await self._play_on_spotify(content)
            elif platform == "local":
                return await self._play_local_media(content)
            elif platform == "vlc":
                return await self._play_with_vlc(content)
            else:
                # Default to YouTube
                return await self._play_on_youtube(content)
                
        except Exception as e:
            return ActionResult(
                success=False,
                message=f"Failed to play media: {str(e)}"
            )
    
    async def _play_on_youtube(self, content: str) -> ActionResult:
        """Play content on YouTube."""
        try:
            query = urllib.parse.quote(content)
            url = f"https://www.youtube.com/results?search_query={query}"
            
            webbrowser.open(url)
            
            return ActionResult(
                success=True,
                message=f"Opening YouTube search for '{content}', Sir.",
                data={"platform": "youtube", "query": content, "url": url},
                follow_up_suggestions=[
                    "Would you like me to open the first result?",
                    "Shall I adjust the volume for you?"
                ]
            )
            
        except Exception as e:
            raise Exception(f"YouTube playback failed: {e}")
    
    async def _play_on_spotify(self, content: str) -> ActionResult:
        """Play content on Spotify."""
        try:
            # Try to open Spotify app
            if "spotify" in self.app_aliases:
                app_info = self.installed_apps[self.app_aliases["spotify"]]
                if app_info.get("path"):
                    subprocess.Popen([app_info["path"]])
                else:
                    subprocess.Popen(["spotify"])
            else:
                # Open web version
                query = urllib.parse.quote(content)
                url = f"https://open.spotify.com/search/{query}"
                webbrowser.open(url)
            
            return ActionResult(
                success=True,
                message=f"Opening Spotify to play '{content}', Sir.",
                data={"platform": "spotify", "query": content}
            )
            
        except Exception as e:
            raise Exception(f"Spotify playback failed: {e}")
    
    async def _play_local_media(self, content: str) -> ActionResult:
        """Play local media files."""
        try:
            # Search for local media files
            if self.system_indexer:
                results = self.system_indexer.search(content, item_type="file")
                media_files = [r for r in results if self._is_media_file(r.item.path)]
                
                if media_files:
                    file_path = media_files[0].item.path
                    os.startfile(file_path)
                    
                    return ActionResult(
                        success=True,
                        message=f"Playing '{content}' from local files, Sir.",
                        data={"platform": "local", "file": file_path}
                    )
            
            # Fallback: open default media player
            subprocess.Popen(["wmplayer"])
            
            return ActionResult(
                success=True,
                message=f"Opening media player to find '{content}', Sir.",
                data={"platform": "local"}
            )
            
        except Exception as e:
            raise Exception(f"Local media playback failed: {e}")
    
    async def _execute_open_application(self, parameters: Dict[str, Any]) -> ActionResult:
        """Execute application opening action."""
        app_name = parameters.get("app_name", "").lower()
        
        if not app_name:
            return ActionResult(
                success=False,
                message="No application name specified, Sir."
            )
        
        try:
            # Try exact match first
            if app_name in self.installed_apps:
                return await self._launch_application(self.installed_apps[app_name])
            
            # Try alias match
            if app_name in self.app_aliases:
                app_key = self.app_aliases[app_name]
                return await self._launch_application(self.installed_apps[app_key])
            
            # Try partial match
            matches = []
            for key, app_info in self.installed_apps.items():
                if app_name in key or any(app_name in word for word in key.split()):
                    matches.append((key, app_info))
            
            if len(matches) == 1:
                return await self._launch_application(matches[0][1])
            elif len(matches) > 1:
                # Multiple matches - ask for clarification
                match_names = [app[1]["name"] for app in matches[:5]]
                return ActionResult(
                    success=False,
                    message=f"I found multiple applications matching '{app_name}', Sir. Did you mean: {', '.join(match_names)}?",
                    data={"matches": match_names}
                )
            
            # Try system command
            try:
                subprocess.Popen([app_name])
                return ActionResult(
                    success=True,
                    message=f"Launching {app_name}, Sir.",
                    data={"method": "system_command"}
                )
            except FileNotFoundError:
                pass
            
            return ActionResult(
                success=False,
                message=f"I couldn't find an application named '{app_name}', Sir. Could you be more specific?",
                follow_up_suggestions=[
                    "Try using the full application name",
                    "Check if the application is installed",
                    "Would you like me to search for similar applications?"
                ]
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                message=f"Error opening application: {str(e)}"
            )
    
    async def _launch_application(self, app_info: Dict[str, Any]) -> ActionResult:
        """Launch a specific application."""
        try:
            app_name = app_info["name"]
            app_path = app_info.get("path", "")
            
            if app_path and os.path.exists(app_path):
                # Launch from path
                if os.path.isfile(app_path):
                    subprocess.Popen([app_path])
                else:
                    # Path is a directory, look for executable
                    exe_files = list(Path(app_path).glob("*.exe"))
                    if exe_files:
                        subprocess.Popen([str(exe_files[0])])
                    else:
                        raise Exception("No executable found in application directory")
            else:
                # Try to launch by name
                app_executable = app_name.lower().replace(" ", "")
                subprocess.Popen([app_executable])
            
            return ActionResult(
                success=True,
                message=f"Launching {app_name}, Sir.",
                data={"app_name": app_name, "path": app_path},
                follow_up_suggestions=[
                    "Would you like me to open any specific files?",
                    "Shall I minimize other windows?"
                ]
            )
            
        except Exception as e:
            raise Exception(f"Failed to launch {app_info['name']}: {e}")
    
    async def _execute_web_search(self, parameters: Dict[str, Any]) -> ActionResult:
        """Execute web search action."""
        query = parameters.get("query", "")
        platform = parameters.get("platform", "google").lower()
        
        if not query:
            return ActionResult(
                success=False,
                message="No search query specified, Sir."
            )
        
        try:
            search_urls = {
                "google": "https://www.google.com/search?q={}",
                "bing": "https://www.bing.com/search?q={}",
                "duckduckgo": "https://duckduckgo.com/?q={}",
                "youtube": "https://www.youtube.com/results?search_query={}",
                "wikipedia": "https://en.wikipedia.org/wiki/Special:Search?search={}"
            }
            
            if platform in search_urls:
                encoded_query = urllib.parse.quote(query)
                url = search_urls[platform].format(encoded_query)
                webbrowser.open(url)
                
                return ActionResult(
                    success=True,
                    message=f"Searching for '{query}' on {platform.title()}, Sir.",
                    data={"query": query, "platform": platform, "url": url},
                    follow_up_suggestions=[
                        "Would you like me to read the first result?",
                        "Shall I open the top link?"
                    ]
                )
            else:
                # Default to Google
                encoded_query = urllib.parse.quote(query)
                url = f"https://www.google.com/search?q={encoded_query}"
                webbrowser.open(url)
                
                return ActionResult(
                    success=True,
                    message=f"Searching for '{query}' on Google, Sir.",
                    data={"query": query, "platform": "google", "url": url}
                )
                
        except Exception as e:
            return ActionResult(
                success=False,
                message=f"Error performing web search: {str(e)}"
            )
    
    async def _execute_system_control(self, parameters: Dict[str, Any]) -> ActionResult:
        """Execute system control action."""
        command = parameters.get("command", "").lower()
        
        if not command:
            return ActionResult(
                success=False,
                message="No system command specified, Sir."
            )
        
        try:
            if command in ["shutdown", "shut down"]:
                return await self._confirm_system_action("shutdown", "shutdown the system")
            
            elif command in ["restart", "reboot"]:
                return await self._confirm_system_action("restart", "restart the system")
            
            elif command in ["sleep", "hibernate"]:
                return await self._confirm_system_action("sleep", "put the system to sleep")
            
            elif command == "lock":
                if sys.platform == "win32":
                    subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
                    return ActionResult(
                        success=True,
                        message="Locking the workstation, Sir.",
                        data={"command": "lock"}
                    )
            
            else:
                return ActionResult(
                    success=False,
                    message=f"Unknown system command: {command}, Sir."
                )
                
        except Exception as e:
            return ActionResult(
                success=False,
                message=f"Error executing system command: {str(e)}"
            )
    
    async def _execute_device_control(self, parameters: Dict[str, Any]) -> ActionResult:
        """Execute device control action."""
        device = parameters.get("device", "").lower()
        action = parameters.get("action", "").lower()
        value = parameters.get("value")
        
        try:
            if device == "volume":
                return await self._control_volume(action, value)
            
            elif device == "brightness":
                return await self._control_brightness(action, value)
            
            else:
                return ActionResult(
                    success=False,
                    message=f"Device control for {device} not implemented yet, Sir."
                )
                
        except Exception as e:
            return ActionResult(
                success=False,
                message=f"Error controlling device: {str(e)}"
            )
    
    async def _control_volume(self, action: str, value: Optional[float] = None) -> ActionResult:
        """Control system volume."""
        try:
            if not self.volume_interface:
                return ActionResult(
                    success=False,
                    message="Volume control interface not available, Sir."
                )
            
            current_volume = self.volume_interface.GetMasterScalarVolume()
            
            if action == "up":
                new_volume = min(1.0, current_volume + 0.1)
                self.volume_interface.SetMasterScalarVolume(new_volume, None)
                return ActionResult(
                    success=True,
                    message=f"Volume increased to {int(new_volume * 100)}%, Sir.",
                    data={"volume": new_volume}
                )
            
            elif action == "down":
                new_volume = max(0.0, current_volume - 0.1)
                self.volume_interface.SetMasterScalarVolume(new_volume, None)
                return ActionResult(
                    success=True,
                    message=f"Volume decreased to {int(new_volume * 100)}%, Sir.",
                    data={"volume": new_volume}
                )
            
            elif action == "mute":
                self.volume_interface.SetMute(True, None)
                return ActionResult(
                    success=True,
                    message="Volume muted, Sir.",
                    data={"muted": True}
                )
            
            elif action == "unmute":
                self.volume_interface.SetMute(False, None)
                return ActionResult(
                    success=True,
                    message="Volume unmuted, Sir.",
                    data={"muted": False}
                )
            
            elif action == "set" and value is not None:
                new_volume = max(0.0, min(1.0, value / 100.0))
                self.volume_interface.SetMasterScalarVolume(new_volume, None)
                return ActionResult(
                    success=True,
                    message=f"Volume set to {int(new_volume * 100)}%, Sir.",
                    data={"volume": new_volume}
                )
            
            else:
                return ActionResult(
                    success=False,
                    message=f"Unknown volume action: {action}, Sir."
                )
                
        except Exception as e:
            raise Exception(f"Volume control failed: {e}")
    
    async def _suggest_media_platform(self, content: str) -> str:
        """Suggest the best platform for media content."""
        content_lower = content.lower()
        
        # Check for platform hints in content
        if any(word in content_lower for word in ["song", "music", "album", "artist"]):
            return "spotify"
        elif any(word in content_lower for word in ["video", "movie", "show", "channel"]):
            return "youtube"
        else:
            # Default to YouTube for general content
            return "youtube"
    
    def _is_media_file(self, file_path: str) -> bool:
        """Check if file is a media file."""
        media_extensions = {
            '.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a',
            '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv'
        }
        
        return Path(file_path).suffix.lower() in media_extensions
    
    async def _confirm_system_action(self, action: str, description: str) -> ActionResult:
        """Request confirmation for system actions."""
        return ActionResult(
            success=False,
            message=f"Are you sure you want me to {description}, Sir? Please confirm.",
            data={"requires_confirmation": True, "action": action}
        )
    
    def set_system_indexer(self, indexer):
        """Set the system indexer reference."""
        self.system_indexer = indexer
    
    def get_available_applications(self) -> List[str]:
        """Get list of available applications."""
        return list(self.installed_apps.keys())
    
    def get_media_sources(self) -> List[str]:
        """Get list of available media sources."""
        return list(self.media_sources.keys())
    
    def cleanup(self):
        """Clean up resources."""
        self.logger.info("Smart Action Engine cleaned up")
