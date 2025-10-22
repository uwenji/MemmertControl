#!/usr/bin/env python3
"""
Memmert AtmoWEB helper: robust parser and range handling for AtmoWEB API responses.

This module provides a clean interface to interact with Memmert incubators via
their AtmoWEB HTTP API interface.
"""
import json
import re
from typing import Any, Dict, Optional, Tuple
import requests


class AtmoWebParser:
    """Parser for AtmoWEB responses that handles various formatting quirks."""
    
    @staticmethod
    def parse_response(raw: str) -> Dict[str, Any]:
        """
        Parse AtmoWEB responses into valid JSON.
        
        Handles:
        - Missing braces
        - Trailing commas
        - Curly quotes („")
        - Unquoted keys in nested objects
        - Bareword values (N/A, N/D, unknown)
        
        Args:
            raw: Raw response string from AtmoWEB
            
        Returns:
            Parsed dictionary from the response
        """
        raw = (raw or "").strip()
        
        # Replace curly quotes with standard quotes
        raw = re.sub(r'[„""]', '"', raw)
        
        # Ensure proper JSON structure
        raw = AtmoWebParser._ensure_braces(raw)
        
        # Quote bare keys (e.g., {min: 18.0} -> {"min": 18.0})
        raw = re.sub(r'([,{]\s*)([A-Za-z_][A-Za-z0-9_]*)\s*:', r'\1"\2":', raw)
        
        # Quote bareword values
        raw = AtmoWebParser._quote_bareword_values(raw)
        
        return json.loads(raw)
    
    @staticmethod
    def _ensure_braces(text: str) -> str:
        """Add missing braces and clean up trailing commas."""
        if not text.startswith("{"):
            text = "{" + text
        if not text.endswith("}"):
            text = text.rstrip(", \r\n\t") + "}"
        # Remove trailing commas before closing braces
        text = re.sub(r",\s*}", "}", text)
        return text
    
    @staticmethod
    def _quote_bareword_values(text: str) -> str:
        """Quote unquoted string values like N/A, N/D, unknown."""
        def quote_match(match):
            return f':"{match.group(1)}"'
        
        # Match bareword values (not starting with ", digit, -, {, [)
        pattern = r':\s*([A-Za-z_][A-Za-z0-9_./-]*)\s*(?=[,}])'
        return re.sub(pattern, quote_match, text)


class AtmoWebClient:
    """Client for communicating with Memmert AtmoWEB interface."""
    
    # Parameter keys mapping
    PARAM_KEYS = {
        'temperature': 'TempSet',
        'humidity': 'HumSet',
        'co2': 'CO2Set',
        'o2': 'O2Set',
        'fan': 'FanSet'
    }
    
    READ_KEYS = {
        'temperature': 'Temp1Read',
        'humidity': 'HumRead',
        'co2': 'CO2Read',
        'o2': 'O2Read',
        'fan': 'FanRead'
    }
    
    def __init__(self, ip: str, port: int = 80, timeout: int = 5):
        """
        Initialize AtmoWeb client.
        
        Args:
            ip: IP address of the Memmert device
            port: HTTP port (default: 80)
            timeout: Request timeout in seconds (default: 5)
        """
        self.base_url = f"http://{ip}:{port}/atmoweb"
        self.timeout = timeout
        self.parser = AtmoWebParser()
    
    def query(self, **params) -> Dict[str, Any]:
        """
        Send a query to the AtmoWEB interface.
        
        Args:
            **params: Query parameters to send
            
        Returns:
            Parsed response dictionary
            
        Raises:
            requests.RequestException: On network errors
            json.JSONDecodeError: On parsing errors
        """
        response = requests.get(self.base_url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return self.parser.parse_response(response.text)
    
    def get_parameter_range(self, key: str) -> Optional[Tuple[float, float]]:
        """
        Get the valid range for a parameter from the device.
        
        Args:
            key: Parameter key (e.g., 'TempSet')
            
        Returns:
            Tuple of (min, max) values, or None if not available
        """
        try:
            info = self.query(**{key: ""})
            
            # Check for nested dict format (new firmware)
            range_block = info.get(f"{key}_Range")
            if isinstance(range_block, dict):
                min_val = self._get_dict_value(range_block, ['min', 'Min', 'MIN'])
                max_val = self._get_dict_value(range_block, ['max', 'Max', 'MAX'])
                if min_val is not None and max_val is not None:
                    return float(min_val), float(max_val)
            
            # Check for flat keys format (old firmware)
            min_key, max_key = f"{key}_RangeMin", f"{key}_RangeMax"
            if min_key in info and max_key in info:
                return float(info[min_key]), float(info[max_key])
            
        except (KeyError, ValueError, TypeError):
            pass
        
        return None
    
    def _get_dict_value(self, data: dict, keys: list) -> Any:
        """Get value from dict trying multiple key variations."""
        for key in keys:
            if key in data:
                return data[key]
        return None
    
    def set_parameter(self, key: str, value: float) -> Optional[float]:
        """
        Set a parameter value with range validation.
        
        Args:
            key: Parameter key
            value: Value to set
            
        Returns:
            Actual value set by the device
            
        Raises:
            ValueError: If value is outside valid range
            KeyError: If parameter is not supported
        """
        value = float(value)
        
        # Validate against range if available
        param_range = self.get_parameter_range(key)
        if param_range:
            min_val, max_val = param_range
            if not (min_val <= value <= max_val):
                raise ValueError(
                    f"{key}={value} is outside valid range [{min_val}, {max_val}]"
                )
        
        # Send the value to the device
        result = self.query(**{key: value}).get(key)
        
        # Check if device rejected the value
        if isinstance(result, str):
            error_values = {"N/A", "N/D", "UNKNOWN"}
            if result.strip().upper() in error_values:
                raise KeyError(f"{key} not supported or rejected by controller")
        
        return self._parse_numeric(result)
    
    @staticmethod
    def _parse_numeric(value: Any) -> Optional[float]:
        """Safely parse a numeric value."""
        try:
            return float(value) if value is not None else None
        except (TypeError, ValueError):
            return None
    
    # Convenience setters
    def set_temperature(self, value: float) -> Optional[float]:
        """Set temperature setpoint (°C)."""
        return self.set_parameter('TempSet', value)
    
    def set_humidity(self, value: float) -> Optional[float]:
        """Set humidity setpoint (% RH)."""
        return self.set_parameter('HumSet', value)
    
    def set_co2(self, value: float) -> Optional[float]:
        """Set CO2 setpoint (%)."""
        return self.set_parameter('CO2Set', value)
    
    def set_o2(self, value: float) -> Optional[float]:
        """Set O2 setpoint (%)."""
        return self.set_parameter('O2Set', value)
    
    def set_fan(self, value: float) -> Optional[float]:
        """Set fan speed setpoint (%)."""
        return self.set_parameter('FanSet', value)
    
    def get_setpoints(self) -> Dict[str, Optional[float]]:
        """
        Get all current setpoints.
        
        Returns:
            Dictionary of parameter names to their current setpoints
        """
        setpoints = {}
        for key in self.PARAM_KEYS.values():
            try:
                response = self.query(**{key: ""})
                setpoints[key] = self._parse_numeric(response.get(key))
            except Exception:
                setpoints[key] = None
        return setpoints
    
    def get_readings(self) -> Dict[str, Optional[float]]:
        """
        Get all current sensor readings.
        
        Returns:
            Dictionary of sensor names to their current readings
        """
        readings = {}
        for key in self.READ_KEYS.values():
            try:
                response = self.query(**{key: ""})
                readings[key] = self._parse_numeric(response.get(key))
            except Exception:
                readings[key] = None
        return readings
    
    def get_status(self) -> Dict[str, Dict[str, Optional[float]]]:
        """
        Get complete status including setpoints and readings.
        
        Returns:
            Dictionary with 'setpoints' and 'readings' sections
        """
        return {
            'setpoints': self.get_setpoints(),
            'readings': self.get_readings()
        }