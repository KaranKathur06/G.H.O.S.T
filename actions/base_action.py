"""
Base action class for G.H.O.S.T. virtual assistant actions.

This module provides the abstract base class that all action handlers
must inherit from to ensure consistent interface and behavior.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseAction(ABC):
    """
    Abstract base class for all action handlers.
    
    Defines the interface that all action handlers must implement.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the base action.
        
        Args:
            config: Configuration dictionary for this action
        """
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.is_enabled = config.get('enabled', True)
    
    @abstractmethod
    def execute(self, parameters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Execute the action with given parameters.
        
        Args:
            parameters: Dictionary of parameters for the action
            
        Returns:
            Dictionary with execution result, None if failed
        """
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """
        Get a human-readable description of this action.
        
        Returns:
            String description of what this action does
        """
        pass
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """
        Validate if the provided parameters are sufficient for execution.
        
        Args:
            parameters: Parameters to validate
            
        Returns:
            True if parameters are valid, False otherwise
        """
        # Default implementation - override in subclasses for specific validation
        return True
    
    def get_required_parameters(self) -> list:
        """
        Get list of required parameter names for this action.
        
        Returns:
            List of required parameter names
        """
        # Default implementation - override in subclasses
        return []
    
    def get_optional_parameters(self) -> list:
        """
        Get list of optional parameter names for this action.
        
        Returns:
            List of optional parameter names
        """
        # Default implementation - override in subclasses
        return []
    
    def is_available(self) -> bool:
        """
        Check if this action is currently available for execution.
        
        Returns:
            True if action is available, False otherwise
        """
        return self.is_enabled
    
    def enable(self) -> None:
        """Enable this action."""
        self.is_enabled = True
        self.logger.info(f"Action {self.__class__.__name__} enabled")
    
    def disable(self) -> None:
        """Disable this action."""
        self.is_enabled = False
        self.logger.info(f"Action {self.__class__.__name__} disabled")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get status information about this action.
        
        Returns:
            Dictionary with status information
        """
        return {
            'name': self.__class__.__name__,
            'enabled': self.is_enabled,
            'available': self.is_available(),
            'description': self.get_description(),
            'required_parameters': self.get_required_parameters(),
            'optional_parameters': self.get_optional_parameters()
        }
    
    def log_execution(self, parameters: Dict[str, Any], result: Optional[Dict[str, Any]]) -> None:
        """
        Log the execution of this action.
        
        Args:
            parameters: Parameters used for execution
            result: Result of the execution
        """
        success = result is not None and result.get('success', False)
        self.logger.info(f"Action executed - Success: {success}, Parameters: {parameters}")
    
    def handle_error(self, error: Exception, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle errors that occur during action execution.
        
        Args:
            error: The exception that occurred
            parameters: Parameters that were being used
            
        Returns:
            Dictionary with error information
        """
        self.logger.error(f"Error in {self.__class__.__name__}: {error}")
        
        return {
            'success': False,
            'error': str(error),
            'error_type': type(error).__name__,
            'message': f"Failed to execute {self.__class__.__name__}"
        }
    
    def get_help(self) -> Dict[str, Any]:
        """
        Get help information for this action.
        
        Returns:
            Dictionary with help information
        """
        return {
            'name': self.__class__.__name__,
            'description': self.get_description(),
            'required_parameters': self.get_required_parameters(),
            'optional_parameters': self.get_optional_parameters(),
            'examples': self.get_examples()
        }
    
    def get_examples(self) -> list:
        """
        Get example usage for this action.
        
        Returns:
            List of example usage strings
        """
        # Default implementation - override in subclasses
        return []
    
    def cleanup(self) -> None:
        """
        Cleanup resources used by this action.
        
        Called when the action is being destroyed or the system is shutting down.
        """
        # Default implementation - override in subclasses if cleanup is needed
        pass
