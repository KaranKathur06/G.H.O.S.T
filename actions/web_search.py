"""
Web search action for G.H.O.S.T. virtual assistant.

This module handles web search queries using various search engines
and opens results in the default browser.
"""

import webbrowser
import urllib.parse
import logging
from typing import Dict, Any, Optional
from .base_action import BaseAction


class WebSearch(BaseAction):
    """
    Handles web search operations.
    
    Supports searching with different search engines and opening results.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the web search handler.
        
        Args:
            config: Configuration dictionary for web search settings
        """
        super().__init__(config)
        
        # Search engine configurations
        self.default_engine = config.get('default_engine', 'google')
        self.search_engines = {
            'google': 'https://www.google.com/search?q={}',
            'bing': 'https://www.bing.com/search?q={}',
            'duckduckgo': 'https://duckduckgo.com/?q={}',
            'yahoo': 'https://search.yahoo.com/search?p={}',
            'youtube': 'https://www.youtube.com/results?search_query={}',
            'wikipedia': 'https://en.wikipedia.org/wiki/Special:Search?search={}'
        }
        
        # Add custom search engines from config
        custom_engines = config.get('custom_engines', {})
        self.search_engines.update(custom_engines)
    
    def execute(self, parameters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Perform a web search.
        
        Args:
            parameters: Dictionary containing 'query' and optional 'engine'
            
        Returns:
            Dictionary with execution result
        """
        if not self.is_available():
            return self.handle_error(Exception("Web search is disabled"), parameters)
        
        query = parameters.get('query', '').strip()
        engine = parameters.get('engine', self.default_engine).lower()
        
        if not query:
            return {
                'success': False,
                'message': 'Please provide a search query',
                'available_engines': list(self.search_engines.keys())
            }
        
        try:
            # Validate search engine
            if engine not in self.search_engines:
                engine = self.default_engine
                self.logger.warning(f"Unknown search engine, using {engine}")
            
            # Perform the search
            search_url = self._build_search_url(query, engine)
            success = self._open_search(search_url)
            
            if success:
                result = {
                    'success': True,
                    'message': f'Searching for "{query}" using {engine}',
                    'query': query,
                    'engine': engine,
                    'url': search_url
                }
            else:
                result = {
                    'success': False,
                    'message': f'Failed to open search for "{query}"',
                    'query': query,
                    'engine': engine
                }
            
            self.log_execution(parameters, result)
            return result
            
        except Exception as e:
            return self.handle_error(e, parameters)
    
    def _build_search_url(self, query: str, engine: str) -> str:
        """
        Build search URL for the given query and engine.
        
        Args:
            query: Search query
            engine: Search engine name
            
        Returns:
            Complete search URL
        """
        # URL encode the query
        encoded_query = urllib.parse.quote_plus(query)
        
        # Get search engine URL template
        url_template = self.search_engines[engine]
        
        # Build the complete URL
        search_url = url_template.format(encoded_query)
        
        self.logger.debug(f"Built search URL: {search_url}")
        return search_url
    
    def _open_search(self, url: str) -> bool:
        """
        Open the search URL in the default browser.
        
        Args:
            url: Search URL to open
            
        Returns:
            True if successful, False otherwise
        """
        try:
            webbrowser.open(url)
            self.logger.info(f"Opened search URL: {url}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to open search URL: {e}")
            return False
    
    def search_specific_site(self, query: str, site: str) -> Optional[Dict[str, Any]]:
        """
        Search within a specific website.
        
        Args:
            query: Search query
            site: Website to search within
            
        Returns:
            Dictionary with execution result
        """
        site_query = f"site:{site} {query}"
        return self.execute({'query': site_query, 'engine': 'google'})
    
    def get_description(self) -> str:
        """Get description of this action."""
        return "Perform web searches using various search engines"
    
    def get_required_parameters(self) -> list:
        """Get required parameters for this action."""
        return ['query']
    
    def get_optional_parameters(self) -> list:
        """Get optional parameters for this action."""
        return ['engine']
    
    def get_examples(self) -> list:
        """Get example usage for this action."""
        return [
            "search for weather today",
            "google python tutorials",
            "look up artificial intelligence",
            "youtube how to cook pasta"
        ]
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """
        Validate parameters for web search.
        
        Args:
            parameters: Parameters to validate
            
        Returns:
            True if parameters are valid
        """
        return 'query' in parameters and bool(parameters['query'].strip())
    
    def get_available_engines(self) -> Dict[str, str]:
        """
        Get available search engines.
        
        Returns:
            Dictionary mapping engine names to their URLs
        """
        return self.search_engines.copy()
    
    def add_search_engine(self, name: str, url_template: str) -> bool:
        """
        Add a custom search engine.
        
        Args:
            name: Name of the search engine
            url_template: URL template with {} placeholder for query
            
        Returns:
            True if engine was added successfully
        """
        if '{}' not in url_template:
            self.logger.error(f"Invalid URL template for {name}: missing {{}} placeholder")
            return False
        
        self.search_engines[name.lower()] = url_template
        self.logger.info(f"Added search engine: {name}")
        return True
    
    def remove_search_engine(self, name: str) -> bool:
        """
        Remove a search engine.
        
        Args:
            name: Name of the search engine to remove
            
        Returns:
            True if engine was removed successfully
        """
        name = name.lower()
        if name in self.search_engines:
            del self.search_engines[name]
            self.logger.info(f"Removed search engine: {name}")
            return True
        else:
            self.logger.warning(f"Search engine {name} not found")
            return False
