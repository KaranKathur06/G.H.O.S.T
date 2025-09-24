"""
System control action for G.H.O.S.T. virtual assistant.

This module handles system operations like shutdown, restart, sleep,
time/date queries, and other system-level commands.
"""

import os
import subprocess
import platform
from datetime import datetime
import logging
from typing import Dict, Any, Optional
from .base_action import BaseAction


class SystemControl(BaseAction):
    """
    Handles system control operations.
    
    Supports system shutdown, restart, sleep, and information queries.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the system control handler.
        
        Args:
            config: Configuration dictionary for system settings
        """
        super().__init__(config)
        
        # System configuration
        self.confirm_dangerous_operations = config.get('confirm_dangerous', True)
        self.allowed_operations = config.get('allowed_operations', [
            'time', 'date', 'shutdown', 'restart', 'sleep', 'lock'
        ])
        
        # Detect operating system
        self.os_type = platform.system().lower()
    
    def execute(self, parameters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Execute a system control operation.
        
        Args:
            parameters: Dictionary containing 'operation' parameter
            
        Returns:
            Dictionary with execution result
        """
        if not self.is_available():
            return self.handle_error(Exception("System control is disabled"), parameters)
        
        operation = parameters.get('operation', '').lower().strip()
        
        if not operation:
            # Check if this is a time/date query from reasoning engine
            query = parameters.get('query', '').lower()
            if any(word in query for word in ['time', 'date', 'clock']):
                operation = 'time' if 'time' in query else 'date'
            else:
                return {
                    'success': False,
                    'message': 'Please specify a system operation',
                    'available_operations': self.allowed_operations
                }
        
        if operation not in self.allowed_operations:
            return {
                'success': False,
                'message': f'Operation "{operation}" is not allowed',
                'available_operations': self.allowed_operations
            }
        
        try:
            # Route to appropriate handler
            if operation in ['time', 'date']:
                return self._handle_time_date(operation)
            elif operation == 'shutdown':
                return self._handle_shutdown()
            elif operation == 'restart':
                return self._handle_restart()
            elif operation == 'sleep':
                return self._handle_sleep()
            elif operation == 'lock':
                return self._handle_lock()
            else:
                return {
                    'success': False,
                    'message': f'Unknown operation: {operation}'
                }
                
        except Exception as e:
            return self.handle_error(e, parameters)
    
    def _handle_time_date(self, operation: str) -> Dict[str, Any]:
        """
        Handle time and date queries.
        
        Args:
            operation: 'time' or 'date'
            
        Returns:
            Dictionary with current time/date information
        """
        now = datetime.now()
        
        if operation == 'time':
            time_str = now.strftime("%I:%M %p")
            message = f"The current time is {time_str}"
        else:  # date
            date_str = now.strftime("%A, %B %d, %Y")
            message = f"Today is {date_str}"
        
        return {
            'success': True,
            'message': message,
            'operation': operation,
            'data': {
                'timestamp': now.isoformat(),
                'formatted_time': now.strftime("%I:%M %p"),
                'formatted_date': now.strftime("%A, %B %d, %Y"),
                'day_of_week': now.strftime("%A"),
                'month': now.strftime("%B"),
                'year': now.year
            }
        }
    
    def _handle_shutdown(self) -> Dict[str, Any]:
        """
        Handle system shutdown.
        
        Returns:
            Dictionary with shutdown result
        """
        if self.confirm_dangerous_operations:
            return {
                'success': False,
                'message': 'Shutdown requires confirmation. This operation is disabled for safety.',
                'operation': 'shutdown',
                'requires_confirmation': True
            }
        
        try:
            if self.os_type == 'windows':
                subprocess.run(['shutdown', '/s', '/t', '10'], check=True)
            elif self.os_type in ['linux', 'darwin']:  # Linux or macOS
                subprocess.run(['sudo', 'shutdown', '-h', '+1'], check=True)
            
            return {
                'success': True,
                'message': 'System shutdown initiated',
                'operation': 'shutdown'
            }
            
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'message': f'Failed to shutdown system: {e}',
                'operation': 'shutdown'
            }
    
    def _handle_restart(self) -> Dict[str, Any]:
        """
        Handle system restart.
        
        Returns:
            Dictionary with restart result
        """
        if self.confirm_dangerous_operations:
            return {
                'success': False,
                'message': 'Restart requires confirmation. This operation is disabled for safety.',
                'operation': 'restart',
                'requires_confirmation': True
            }
        
        try:
            if self.os_type == 'windows':
                subprocess.run(['shutdown', '/r', '/t', '10'], check=True)
            elif self.os_type in ['linux', 'darwin']:
                subprocess.run(['sudo', 'shutdown', '-r', '+1'], check=True)
            
            return {
                'success': True,
                'message': 'System restart initiated',
                'operation': 'restart'
            }
            
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'message': f'Failed to restart system: {e}',
                'operation': 'restart'
            }
    
    def _handle_sleep(self) -> Dict[str, Any]:
        """
        Handle system sleep/suspend.
        
        Returns:
            Dictionary with sleep result
        """
        try:
            if self.os_type == 'windows':
                # Use rundll32 to put system to sleep
                subprocess.run(['rundll32.exe', 'powrprof.dll,SetSuspendState', '0,1,0'], check=True)
            elif self.os_type == 'linux':
                subprocess.run(['systemctl', 'suspend'], check=True)
            elif self.os_type == 'darwin':  # macOS
                subprocess.run(['pmset', 'sleepnow'], check=True)
            
            return {
                'success': True,
                'message': 'System sleep initiated',
                'operation': 'sleep'
            }
            
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'message': f'Failed to put system to sleep: {e}',
                'operation': 'sleep'
            }
    
    def _handle_lock(self) -> Dict[str, Any]:
        """
        Handle screen lock.
        
        Returns:
            Dictionary with lock result
        """
        try:
            if self.os_type == 'windows':
                subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'], check=True)
            elif self.os_type == 'linux':
                # Try common lock commands
                for cmd in [['gnome-screensaver-command', '--lock'], 
                           ['xdg-screensaver', 'lock'],
                           ['loginctl', 'lock-session']]:
                    try:
                        subprocess.run(cmd, check=True)
                        break
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        continue
            elif self.os_type == 'darwin':  # macOS
                subprocess.run(['/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession', '-suspend'], check=True)
            
            return {
                'success': True,
                'message': 'Screen locked',
                'operation': 'lock'
            }
            
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'message': f'Failed to lock screen: {e}',
                'operation': 'lock'
            }
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get system information.
        
        Returns:
            Dictionary with system information
        """
        return {
            'os': platform.system(),
            'os_version': platform.version(),
            'architecture': platform.architecture()[0],
            'processor': platform.processor(),
            'hostname': platform.node(),
            'python_version': platform.python_version()
        }
    
    def get_description(self) -> str:
        """Get description of this action."""
        return "Control system operations like shutdown, restart, sleep, and get time/date"
    
    def get_required_parameters(self) -> list:
        """Get required parameters for this action."""
        return []  # Operation can be inferred from query
    
    def get_optional_parameters(self) -> list:
        """Get optional parameters for this action."""
        return ['operation', 'query']
    
    def get_examples(self) -> list:
        """Get example usage for this action."""
        return [
            "what time is it",
            "what's the date",
            "shutdown computer",
            "restart system",
            "put computer to sleep",
            "lock screen"
        ]
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """
        Validate parameters for system control.
        
        Args:
            parameters: Parameters to validate
            
        Returns:
            True if parameters are valid
        """
        # System control can work with operation or query parameters
        return ('operation' in parameters or 
                'query' in parameters or 
                len(parameters) == 0)  # Allow empty for time/date queries
