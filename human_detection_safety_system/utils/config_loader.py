"""
Configuration Loader for Human Detection Safety System
Handles loading and validation of YAML configuration files
"""

import yaml
import os
import logging
from typing import Dict, Any, List, Optional

class ConfigLoader:
    """Handles loading and validation of configuration files"""
    
    def __init__(self, config_path: str = "config/safety_config.yaml"):
        """
        Initialize the configuration loader
        
        Args:
            config_path: Path to the configuration YAML file
        """
        self.config_path = config_path
        self.config = None
        self.logger = logging.getLogger(__name__)
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from YAML file
        
        Returns:
            Dictionary containing configuration data
        """
        try:
            if not os.path.exists(self.config_path):
                raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
            
            with open(self.config_path, 'r') as file:
                self.config = yaml.safe_load(file)
            
            self._validate_config()
            self.logger.info(f"Configuration loaded successfully from {self.config_path}")
            return self.config
            
        except Exception as e:
            self.logger.error(f"Error loading configuration: {str(e)}")
            raise
    
    def _validate_config(self) -> None:
        """Validate the loaded configuration"""
        if not self.config:
            raise ValueError("Configuration is empty or invalid")
        
        # Validate required sections
        required_sections = ['camera', 'models', 'safety_zones', 'alerts']
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Missing required configuration section: {section}")
        
        # Validate camera settings
        camera_config = self.config.get('camera', {})
        if 'device_id' not in camera_config:
            raise ValueError("Camera device_id is required")
        
        # Validate safety zones
        safety_zones = self.config.get('safety_zones', {})
        if 'danger_zones' not in safety_zones:
            raise ValueError("At least one danger zone must be defined")
        
        # Validate zone coordinates
        for zone_type in ['danger_zones', 'safe_zones']:
            if zone_type in safety_zones:
                for zone in safety_zones[zone_type]:
                    if 'coordinates' not in zone:
                        raise ValueError(f"Zone coordinates missing for {zone.get('name', 'unnamed zone')}")
                    
                    coords = zone['coordinates']
                    if len(coords) < 3:
                        raise ValueError(f"Zone must have at least 3 coordinate points: {zone.get('name', 'unnamed zone')}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key (supports dot notation)
        
        Args:
            key: Configuration key (e.g., 'camera.device_id')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        if not self.config:
            return default
        
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_safety_zones(self) -> Dict[str, List[Dict]]:
        """Get all safety zones configuration"""
        return self.get('safety_zones', {})
    
    def get_camera_config(self) -> Dict[str, Any]:
        """Get camera configuration"""
        return self.get('camera', {})
    
    def get_model_config(self) -> Dict[str, Any]:
        """Get model configuration"""
        return self.get('models', {})
    
    def get_alert_config(self) -> Dict[str, Any]:
        """Get alert system configuration"""
        return self.get('alerts', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return self.get('logging', {})
    
    def get_performance_config(self) -> Dict[str, Any]:
        """Get performance configuration"""
        return self.get('performance', {})
    
    def is_audio_enabled(self) -> bool:
        """Check if audio alerts are enabled"""
        return self.get('alerts.audio.enabled', False)
    
    def is_visual_enabled(self) -> bool:
        """Check if visual alerts are enabled"""
        return self.get('alerts.visual.enabled', True)
    
    def get_confidence_threshold(self, model_type: str = 'yolo') -> float:
        """Get confidence threshold for specified model"""
        return self.get(f'models.{model_type}.confidence_threshold', 0.5)
    
    def create_directories(self) -> None:
        """Create necessary directories based on configuration"""
        # Create log directories
        log_file = self.get('logging.log_file')
        if log_file:
            log_dir = os.path.dirname(log_file)
            os.makedirs(log_dir, exist_ok=True)
        
        # Create screenshot directory
        screenshot_dir = self.get('logging.incident_logging.screenshot_dir')
        if screenshot_dir:
            os.makedirs(screenshot_dir, exist_ok=True)
        
        # Create audio directory
        audio_file = self.get('alerts.audio.alarm_file')
        if audio_file:
            audio_dir = os.path.dirname(audio_file)
            os.makedirs(audio_dir, exist_ok=True)
    
    def save_config(self, config_data: Dict[str, Any], output_path: Optional[str] = None) -> None:
        """
        Save configuration to YAML file
        
        Args:
            config_data: Configuration dictionary to save
            output_path: Output file path (defaults to current config path)
        """
        output_path = output_path or self.config_path
        
        try:
            with open(output_path, 'w') as file:
                yaml.dump(config_data, file, default_flow_style=False, indent=2)
            
            self.logger.info(f"Configuration saved to {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving configuration: {str(e)}")
            raise