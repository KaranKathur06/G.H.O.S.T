"""
Dynamic Action Registry for G.H.O.S.T.

This module provides a dynamic action registration system that allows
actions to register themselves automatically, making the system easily extensible.
"""

import logging
import importlib
import inspect
from pathlib import Path
from typing import Dict, Any, List, Type, Optional, Callable
from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class ActionMetadata:
    """Metadata for registered actions."""
    name: str
    description: str
    category: str
    intent_types: List[str]
    parameters: Dict[str, Any]
    priority: int = 1
    enabled: bool = True

class BaseAction(ABC):
    """Base class for all G.H.O.S.T. actions."""
    
    @abstractmethod
    def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the action with given parameters."""
        pass
    
    @abstractmethod
    def get_metadata(self) -> ActionMetadata:
        """Get action metadata for registration."""
        pass
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validate action parameters."""
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get action status information."""
        return {"status": "ready", "enabled": True}

class ActionRegistry:
    """
    Dynamic action registry that auto-discovers and manages actions.
    
    Actions can register themselves by inheriting from BaseAction and
    being placed in the actions/ directory.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the action registry."""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Registry storage
        self._actions: Dict[str, BaseAction] = {}
        self._metadata: Dict[str, ActionMetadata] = {}
        self._intent_mappings: Dict[str, List[str]] = {}
        
        # Configuration
        self.actions_directory = Path(self.config.get('actions_directory', 'actions'))
        self.auto_discover = self.config.get('auto_discover', True)
        
        # Initialize registry
        if self.auto_discover:
            self.discover_actions()
    
    def discover_actions(self) -> None:
        """Automatically discover and register actions from the actions directory."""
        try:
            self.logger.info("Discovering actions...")
            
            if not self.actions_directory.exists():
                self.logger.warning(f"Actions directory not found: {self.actions_directory}")
                return
            
            # Find all Python files in actions directory
            action_files = list(self.actions_directory.glob("*.py"))
            
            for action_file in action_files:
                if action_file.name.startswith("__"):
                    continue  # Skip __init__.py and similar
                
                try:
                    self._load_action_module(action_file)
                except Exception as e:
                    self.logger.error(f"Failed to load action from {action_file}: {e}")
            
            self.logger.info(f"Discovered {len(self._actions)} actions")
            
        except Exception as e:
            self.logger.error(f"Error during action discovery: {e}")
    
    def _load_action_module(self, action_file: Path) -> None:
        """Load actions from a Python module file."""
        try:
            # Import the module
            import importlib.util
            module_name = f"actions.{action_file.stem}"
            spec = importlib.util.spec_from_file_location(module_name, action_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find action classes in the module
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, BaseAction) and 
                    obj != BaseAction):
                    
                    try:
                        # Instantiate the action
                        action_instance = obj(self.config)
                        self.register_action(action_instance)
                        
                    except Exception as e:
                        self.logger.error(f"Failed to instantiate action {name}: {e}")
                        
        except Exception as e:
            self.logger.error(f"Error loading module {action_file}: {e}")
    
    def register_action(self, action: BaseAction) -> None:
        """Register an action instance."""
        try:
            metadata = action.get_metadata()
            
            # Store action and metadata
            self._actions[metadata.name] = action
            self._metadata[metadata.name] = metadata
            
            # Update intent mappings
            for intent_type in metadata.intent_types:
                if intent_type not in self._intent_mappings:
                    self._intent_mappings[intent_type] = []
                self._intent_mappings[intent_type].append(metadata.name)
            
            self.logger.debug(f"Registered action: {metadata.name}")
            
        except Exception as e:
            self.logger.error(f"Error registering action: {e}")
    
    def unregister_action(self, action_name: str) -> bool:
        """Unregister an action by name."""
        try:
            if action_name in self._actions:
                metadata = self._metadata[action_name]
                
                # Remove from intent mappings
                for intent_type in metadata.intent_types:
                    if intent_type in self._intent_mappings:
                        self._intent_mappings[intent_type].remove(action_name)
                        if not self._intent_mappings[intent_type]:
                            del self._intent_mappings[intent_type]
                
                # Remove action and metadata
                del self._actions[action_name]
                del self._metadata[action_name]
                
                self.logger.info(f"Unregistered action: {action_name}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error unregistering action {action_name}: {e}")
            return False
    
    def get_action(self, action_name: str) -> Optional[BaseAction]:
        """Get an action by name."""
        return self._actions.get(action_name)
    
    def get_actions_for_intent(self, intent_type: str) -> List[BaseAction]:
        """Get all actions that can handle a specific intent type."""
        action_names = self._intent_mappings.get(intent_type, [])
        return [self._actions[name] for name in action_names if name in self._actions]
    
    def execute_action(self, action_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an action by name with parameters."""
        try:
            action = self.get_action(action_name)
            if not action:
                return {
                    "success": False,
                    "error": f"Action '{action_name}' not found",
                    "message": f"I don't know how to handle '{action_name}', Sir."
                }
            
            # Validate parameters
            if not action.validate_parameters(parameters):
                return {
                    "success": False,
                    "error": "Invalid parameters",
                    "message": "The parameters for that action are not valid, Sir."
                }
            
            # Execute action
            result = action.execute(parameters)
            
            # Ensure result has required fields
            if not isinstance(result, dict):
                result = {"success": True, "result": result}
            
            if "success" not in result:
                result["success"] = True
            
            if "message" not in result and result["success"]:
                result["message"] = "Action completed successfully, Sir."
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing action {action_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"I encountered an issue executing that action, Sir: {str(e)}"
            }
    
    def execute_intent(self, intent_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the best action for a given intent type."""
        try:
            actions = self.get_actions_for_intent(intent_type)
            
            if not actions:
                return {
                    "success": False,
                    "error": f"No actions available for intent '{intent_type}'",
                    "message": f"I don't know how to handle '{intent_type}' requests, Sir."
                }
            
            # Sort actions by priority (higher priority first)
            actions.sort(key=lambda a: self._metadata[a.get_metadata().name].priority, reverse=True)
            
            # Try actions in priority order
            for action in actions:
                try:
                    if action.validate_parameters(parameters):
                        result = action.execute(parameters)
                        
                        # Ensure result format
                        if not isinstance(result, dict):
                            result = {"success": True, "result": result}
                        
                        if result.get("success", True):
                            return result
                        
                except Exception as e:
                    self.logger.warning(f"Action {action.get_metadata().name} failed: {e}")
                    continue
            
            # All actions failed
            return {
                "success": False,
                "error": "All available actions failed",
                "message": "I tried several approaches but couldn't complete that request, Sir."
            }
            
        except Exception as e:
            self.logger.error(f"Error executing intent {intent_type}: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"I encountered an issue processing that request, Sir: {str(e)}"
            }
    
    def get_all_actions(self) -> Dict[str, ActionMetadata]:
        """Get metadata for all registered actions."""
        return self._metadata.copy()
    
    def get_actions_by_category(self, category: str) -> Dict[str, ActionMetadata]:
        """Get actions filtered by category."""
        return {
            name: metadata 
            for name, metadata in self._metadata.items() 
            if metadata.category == category
        }
    
    def get_supported_intents(self) -> List[str]:
        """Get list of all supported intent types."""
        return list(self._intent_mappings.keys())
    
    def reload_actions(self) -> None:
        """Reload all actions from the actions directory."""
        self.logger.info("Reloading actions...")
        
        # Clear current registry
        self._actions.clear()
        self._metadata.clear()
        self._intent_mappings.clear()
        
        # Rediscover actions
        self.discover_actions()
    
    def get_registry_status(self) -> Dict[str, Any]:
        """Get status information about the registry."""
        return {
            "total_actions": len(self._actions),
            "supported_intents": len(self._intent_mappings),
            "actions_by_category": {
                category: len([m for m in self._metadata.values() if m.category == category])
                for category in set(m.category for m in self._metadata.values())
            },
            "enabled_actions": len([m for m in self._metadata.values() if m.enabled]),
            "disabled_actions": len([m for m in self._metadata.values() if not m.enabled])
        }

# Global registry instance
_global_registry: Optional[ActionRegistry] = None

def get_global_registry() -> ActionRegistry:
    """Get the global action registry instance."""
    global _global_registry
    if _global_registry is None:
        _global_registry = ActionRegistry()
    return _global_registry

def register_action(action: BaseAction) -> None:
    """Register an action with the global registry."""
    get_global_registry().register_action(action)
