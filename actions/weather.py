"""
Weather action for G.H.O.S.T. virtual assistant.

This module handles weather queries and provides weather information
using weather APIs or web scraping.
"""

import logging
import requests
from typing import Dict, Any, Optional
from .base_action import BaseAction


class Weather(BaseAction):
    """
    Handles weather information queries.
    
    Supports getting current weather and forecasts for specified locations.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the weather handler.
        
        Args:
            config: Configuration dictionary for weather settings
        """
        super().__init__(config)
        
        # Weather API configuration
        self.api_key = config.get('api_key', '')
        self.default_location = config.get('default_location', 'New York')
        self.api_provider = config.get('provider', 'openweathermap')  # openweathermap, weatherapi, etc.
        self.units = config.get('units', 'metric')  # metric, imperial, kelvin
        
        # API endpoints
        self.api_endpoints = {
            'openweathermap': 'https://api.openweathermap.org/data/2.5/weather',
            'weatherapi': 'https://api.weatherapi.com/v1/current.json'
        }
    
    def execute(self, parameters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get weather information.
        
        Args:
            parameters: Dictionary containing optional 'location' parameter
            
        Returns:
            Dictionary with weather information
        """
        if not self.is_available():
            return self.handle_error(Exception("Weather service is disabled"), parameters)
        
        location = parameters.get('location', self.default_location).strip()
        
        if not location:
            location = self.default_location
        
        try:
            # Get weather data
            if self.api_key:
                weather_data = self._get_weather_from_api(location)
            else:
                weather_data = self._get_weather_fallback(location)
            
            if weather_data:
                result = {
                    'success': True,
                    'message': self._format_weather_message(weather_data),
                    'location': location,
                    'data': weather_data
                }
            else:
                result = {
                    'success': False,
                    'message': f'Could not get weather information for {location}',
                    'location': location
                }
            
            self.log_execution(parameters, result)
            return result
            
        except Exception as e:
            return self.handle_error(e, parameters)
    
    def _get_weather_from_api(self, location: str) -> Optional[Dict[str, Any]]:
        """
        Get weather data from API.
        
        Args:
            location: Location to get weather for
            
        Returns:
            Dictionary with weather data, None if failed
        """
        try:
            if self.api_provider == 'openweathermap':
                return self._get_openweathermap_data(location)
            elif self.api_provider == 'weatherapi':
                return self._get_weatherapi_data(location)
            else:
                self.logger.error(f"Unknown weather API provider: {self.api_provider}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting weather from API: {e}")
            return None
    
    def _get_openweathermap_data(self, location: str) -> Optional[Dict[str, Any]]:
        """
        Get weather data from OpenWeatherMap API.
        
        Args:
            location: Location to get weather for
            
        Returns:
            Dictionary with weather data, None if failed
        """
        url = self.api_endpoints['openweathermap']
        params = {
            'q': location,
            'appid': self.api_key,
            'units': self.units
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract relevant information
        return {
            'location': data['name'],
            'country': data['sys']['country'],
            'temperature': data['main']['temp'],
            'feels_like': data['main']['feels_like'],
            'humidity': data['main']['humidity'],
            'pressure': data['main']['pressure'],
            'description': data['weather'][0]['description'],
            'main': data['weather'][0]['main'],
            'wind_speed': data.get('wind', {}).get('speed', 0),
            'visibility': data.get('visibility', 0) / 1000,  # Convert to km
            'units': self.units
        }
    
    def _get_weatherapi_data(self, location: str) -> Optional[Dict[str, Any]]:
        """
        Get weather data from WeatherAPI.
        
        Args:
            location: Location to get weather for
            
        Returns:
            Dictionary with weather data, None if failed
        """
        url = self.api_endpoints['weatherapi']
        params = {
            'key': self.api_key,
            'q': location,
            'aqi': 'no'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract relevant information
        current = data['current']
        location_data = data['location']
        
        return {
            'location': location_data['name'],
            'country': location_data['country'],
            'temperature': current['temp_c'] if self.units == 'metric' else current['temp_f'],
            'feels_like': current['feelslike_c'] if self.units == 'metric' else current['feelslike_f'],
            'humidity': current['humidity'],
            'pressure': current['pressure_mb'],
            'description': current['condition']['text'],
            'main': current['condition']['text'],
            'wind_speed': current['wind_kph'] if self.units == 'metric' else current['wind_mph'],
            'visibility': current['vis_km'] if self.units == 'metric' else current['vis_miles'],
            'units': self.units
        }
    
    def _get_weather_fallback(self, location: str) -> Optional[Dict[str, Any]]:
        """
        Get weather data using fallback method (no API key required).
        
        Args:
            location: Location to get weather for
            
        Returns:
            Dictionary with basic weather data, None if failed
        """
        # Placeholder for fallback weather data
        # In a real implementation, this could scrape weather websites
        # or use free weather services
        
        self.logger.warning("No API key configured, using fallback weather data")
        
        return {
            'location': location,
            'country': 'Unknown',
            'temperature': 22,  # Placeholder temperature
            'feels_like': 24,
            'humidity': 65,
            'pressure': 1013,
            'description': 'partly cloudy',
            'main': 'Clouds',
            'wind_speed': 5,
            'visibility': 10,
            'units': self.units,
            'note': 'This is placeholder data. Configure an API key for real weather information.'
        }
    
    def _format_weather_message(self, weather_data: Dict[str, Any]) -> str:
        """
        Format weather data into a human-readable message.
        
        Args:
            weather_data: Dictionary with weather information
            
        Returns:
            Formatted weather message
        """
        location = weather_data['location']
        temp = weather_data['temperature']
        description = weather_data['description']
        humidity = weather_data['humidity']
        
        # Determine temperature unit
        temp_unit = '°C' if weather_data['units'] == 'metric' else '°F'
        
        message = f"The weather in {location} is {description} with a temperature of {temp}{temp_unit}"
        
        # Add additional details
        if weather_data.get('feels_like'):
            feels_like = weather_data['feels_like']
            message += f", feels like {feels_like}{temp_unit}"
        
        message += f". Humidity is {humidity}%"
        
        if weather_data.get('wind_speed'):
            wind_speed = weather_data['wind_speed']
            wind_unit = 'km/h' if weather_data['units'] == 'metric' else 'mph'
            message += f" with wind speed of {wind_speed} {wind_unit}"
        
        return message
    
    def get_description(self) -> str:
        """Get description of this action."""
        return "Get current weather information for specified locations"
    
    def get_required_parameters(self) -> list:
        """Get required parameters for this action."""
        return []  # Location is optional, uses default if not provided
    
    def get_optional_parameters(self) -> list:
        """Get optional parameters for this action."""
        return ['location']
    
    def get_examples(self) -> list:
        """Get example usage for this action."""
        return [
            "what's the weather",
            "weather in London",
            "temperature in Tokyo",
            "how's the weather in Paris"
        ]
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """
        Validate parameters for weather queries.
        
        Args:
            parameters: Parameters to validate
            
        Returns:
            True if parameters are valid
        """
        # Weather queries don't require specific parameters
        return True
    
    def set_default_location(self, location: str) -> None:
        """
        Set the default location for weather queries.
        
        Args:
            location: Default location name
        """
        self.default_location = location
        self.logger.info(f"Default weather location set to: {location}")
    
    def set_units(self, units: str) -> bool:
        """
        Set the units for weather data.
        
        Args:
            units: 'metric', 'imperial', or 'kelvin'
            
        Returns:
            True if units were set successfully
        """
        if units in ['metric', 'imperial', 'kelvin']:
            self.units = units
            self.logger.info(f"Weather units set to: {units}")
            return True
        else:
            self.logger.error(f"Invalid units: {units}")
            return False
