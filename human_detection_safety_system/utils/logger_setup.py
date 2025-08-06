"""
Logging System Setup for Human Detection Safety System
Handles comprehensive logging, incident tracking, and screenshot capture
"""

import logging
import logging.handlers
import os
import csv
import cv2
import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional, List
import threading
import json

class SafetyLogger:
    """
    Comprehensive logging system for safety incidents and system events
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the safety logging system
        
        Args:
            config: Configuration dictionary containing logging settings
        """
        self.config = config
        self.logging_config = config.get('logging', {})
        
        # Setup main logger
        self.logger = self._setup_main_logger()
        
        # Incident logging setup
        self.incident_config = self.logging_config.get('incident_logging', {})
        self.incident_enabled = self.incident_config.get('enabled', True)
        self.incident_file = self.incident_config.get('incident_file', 'logs/incidents.csv')
        self.screenshot_enabled = self.incident_config.get('include_screenshots', True)
        self.screenshot_dir = self.incident_config.get('screenshot_dir', 'logs/screenshots')
        
        # Create necessary directories
        self._create_directories()
        
        # Initialize incident CSV file
        self._init_incident_file()
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Statistics tracking
        self.stats = {
            'total_incidents': 0,
            'incidents_by_severity': {},
            'incidents_by_zone': {},
            'screenshots_captured': 0
        }
        
        self.logger.info("Safety logging system initialized")
    
    def _setup_main_logger(self) -> logging.Logger:
        """
        Setup the main application logger with file and console handlers
        
        Returns:
            Configured logger instance
        """
        # Create logger
        logger = logging.getLogger('safety_system')
        
        # Set log level
        log_level = self.logging_config.get('log_level', 'INFO')
        logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        
        # Clear any existing handlers
        logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # File handler with rotation
        log_file = self.logging_config.get('log_file', 'logs/safety_system.log')
        max_bytes = self.logging_config.get('max_log_size', 10485760)  # 10MB
        backup_count = self.logging_config.get('backup_count', 5)
        
        if log_file:
            # Create log directory if it doesn't exist
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            
            file_handler = logging.handlers.RotatingFileHandler(
                log_file, maxBytes=max_bytes, backupCount=backup_count
            )
            file_handler.setFormatter(detailed_formatter)
            logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(simple_formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    def _create_directories(self) -> None:
        """Create necessary directories for logging"""
        directories = []
        
        # Log file directory
        log_file = self.logging_config.get('log_file')
        if log_file:
            directories.append(os.path.dirname(log_file))
        
        # Incident file directory
        if self.incident_file:
            directories.append(os.path.dirname(self.incident_file))
        
        # Screenshot directory
        if self.screenshot_enabled and self.screenshot_dir:
            directories.append(self.screenshot_dir)
        
        # Create directories
        for directory in directories:
            if directory:
                os.makedirs(directory, exist_ok=True)
    
    def _init_incident_file(self) -> None:
        """Initialize the incident CSV file with headers"""
        if not self.incident_enabled or not self.incident_file:
            return
        
        try:
            # Check if file exists and has content
            file_exists = os.path.exists(self.incident_file)
            
            if not file_exists or os.path.getsize(self.incident_file) == 0:
                with open(self.incident_file, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([
                        'timestamp',
                        'incident_id',
                        'severity',
                        'alert_type',
                        'zone',
                        'detection_type',
                        'message',
                        'screenshot_path',
                        'coordinates',
                        'confidence',
                        'body_parts_involved',
                        'consecutive_count',
                        'emergency_triggered'
                    ])
                    
                self.logger.info(f"Incident log file initialized: {self.incident_file}")
                
        except Exception as e:
            self.logger.error(f"Error initializing incident file: {str(e)}")
    
    def log_incident(self, violation: Dict[str, Any], 
                    frame: Optional[np.ndarray] = None,
                    emergency_triggered: bool = False) -> str:
        """
        Log a safety incident with optional screenshot
        
        Args:
            violation: Violation dictionary containing incident details
            frame: Optional video frame for screenshot
            emergency_triggered: Whether this incident triggered emergency protocol
            
        Returns:
            Unique incident ID
        """
        if not self.incident_enabled:
            return ""
        
        try:
            with self.lock:
                # Generate unique incident ID
                incident_id = f"INC_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]}"
                
                # Capture screenshot if enabled
                screenshot_path = ""
                if self.screenshot_enabled and frame is not None:
                    screenshot_path = self._capture_screenshot(frame, incident_id)
                
                # Extract incident details
                timestamp = datetime.now().isoformat()
                severity = violation.get('severity', 'UNKNOWN')
                alert_type = violation.get('detection_type', 'UNKNOWN')
                zone = violation.get('zone', {}).get('name', 'UNKNOWN')
                detection_type = violation.get('detection_type', 'UNKNOWN')
                message = self._format_incident_message(violation)
                coordinates = str(violation.get('coordinates', []))
                confidence = violation.get('detection', {}).get('confidence', 0.0)
                
                # Body parts information
                body_parts = []
                if 'body_part_violations' in violation:
                    body_parts = [bp['body_part'] for bp in violation['body_part_violations']]
                body_parts_str = ','.join(body_parts) if body_parts else ""
                
                # Consecutive count (if available)
                consecutive_count = violation.get('consecutive_count', 1)
                
                # Write to CSV
                with open(self.incident_file, 'a', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([
                        timestamp,
                        incident_id,
                        severity,
                        alert_type,
                        zone,
                        detection_type,
                        message,
                        screenshot_path,
                        coordinates,
                        confidence,
                        body_parts_str,
                        consecutive_count,
                        emergency_triggered
                    ])
                
                # Update statistics
                self._update_statistics(severity, zone, screenshot_path)
                
                # Log to main logger
                log_level = logging.CRITICAL if severity == 'CRITICAL' else logging.ERROR
                self.logger.log(log_level, f"INCIDENT LOGGED: {incident_id} - {message}")
                
                return incident_id
                
        except Exception as e:
            self.logger.error(f"Error logging incident: {str(e)}")
            return ""
    
    def _capture_screenshot(self, frame: np.ndarray, incident_id: str) -> str:
        """
        Capture and save screenshot of the incident
        
        Args:
            frame: Video frame to save
            incident_id: Unique incident identifier
            
        Returns:
            Path to saved screenshot
        """
        try:
            if not os.path.exists(self.screenshot_dir):
                os.makedirs(self.screenshot_dir, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{incident_id}_{timestamp}.jpg"
            filepath = os.path.join(self.screenshot_dir, filename)
            
            # Save screenshot
            cv2.imwrite(filepath, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            
            self.stats['screenshots_captured'] += 1
            
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error capturing screenshot: {str(e)}")
            return ""
    
    def _format_incident_message(self, violation: Dict[str, Any]) -> str:
        """
        Format incident message from violation data
        
        Args:
            violation: Violation dictionary
            
        Returns:
            Formatted incident message
        """
        try:
            detection_type = violation.get('detection_type', 'Unknown')
            zone_name = violation.get('zone', {}).get('name', 'Unknown Zone')
            severity = violation.get('severity', 'Unknown')
            
            message = f"{detection_type.upper()} detected in {zone_name} (Severity: {severity})"
            
            # Add body part information if available
            if 'body_part_violations' in violation:
                body_parts = [bp['body_part'] for bp in violation['body_part_violations']]
                if body_parts:
                    message += f" - Body parts: {', '.join(body_parts)}"
            
            return message
            
        except Exception as e:
            self.logger.error(f"Error formatting incident message: {str(e)}")
            return "Incident details unavailable"
    
    def _update_statistics(self, severity: str, zone: str, screenshot_path: str) -> None:
        """
        Update incident statistics
        
        Args:
            severity: Incident severity
            zone: Zone where incident occurred
            screenshot_path: Path to screenshot (empty if none)
        """
        try:
            self.stats['total_incidents'] += 1
            
            # Update severity statistics
            if severity not in self.stats['incidents_by_severity']:
                self.stats['incidents_by_severity'][severity] = 0
            self.stats['incidents_by_severity'][severity] += 1
            
            # Update zone statistics
            if zone not in self.stats['incidents_by_zone']:
                self.stats['incidents_by_zone'][zone] = 0
            self.stats['incidents_by_zone'][zone] += 1
            
        except Exception as e:
            self.logger.error(f"Error updating statistics: {str(e)}")
    
    def log_system_event(self, event_type: str, message: str, 
                        level: str = 'INFO', data: Optional[Dict] = None) -> None:
        """
        Log system events (startup, shutdown, errors, etc.)
        
        Args:
            event_type: Type of system event
            message: Event message
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            data: Optional additional data
        """
        try:
            log_level = getattr(logging, level.upper(), logging.INFO)
            
            # Format message with event type
            formatted_message = f"[{event_type}] {message}"
            
            # Add additional data if provided
            if data:
                formatted_message += f" | Data: {json.dumps(data, default=str)}"
            
            self.logger.log(log_level, formatted_message)
            
        except Exception as e:
            self.logger.error(f"Error logging system event: {str(e)}")
    
    def log_performance_metrics(self, metrics: Dict[str, Any]) -> None:
        """
        Log performance metrics
        
        Args:
            metrics: Dictionary containing performance data
        """
        try:
            metrics_str = ", ".join([f"{k}: {v}" for k, v in metrics.items()])
            self.logger.info(f"PERFORMANCE METRICS - {metrics_str}")
            
        except Exception as e:
            self.logger.error(f"Error logging performance metrics: {str(e)}")
    
    def get_incident_summary(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get summary of incidents from the last N hours
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            Dictionary containing incident summary
        """
        try:
            if not os.path.exists(self.incident_file):
                return {'error': 'Incident file not found'}
            
            # Read incidents from CSV
            incidents = []
            cutoff_time = datetime.now().timestamp() - (hours * 3600)
            
            with open(self.incident_file, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    try:
                        incident_time = datetime.fromisoformat(row['timestamp']).timestamp()
                        if incident_time >= cutoff_time:
                            incidents.append(row)
                    except (ValueError, KeyError):
                        continue
            
            # Generate summary
            summary = {
                'total_incidents': len(incidents),
                'time_period_hours': hours,
                'incidents_by_severity': {},
                'incidents_by_zone': {},
                'incidents_by_type': {},
                'emergency_incidents': 0,
                'most_active_hour': None
            }
            
            # Analyze incidents
            hour_counts = {}
            for incident in incidents:
                # Severity breakdown
                severity = incident.get('severity', 'UNKNOWN')
                summary['incidents_by_severity'][severity] = \
                    summary['incidents_by_severity'].get(severity, 0) + 1
                
                # Zone breakdown
                zone = incident.get('zone', 'UNKNOWN')
                summary['incidents_by_zone'][zone] = \
                    summary['incidents_by_zone'].get(zone, 0) + 1
                
                # Type breakdown
                alert_type = incident.get('alert_type', 'UNKNOWN')
                summary['incidents_by_type'][alert_type] = \
                    summary['incidents_by_type'].get(alert_type, 0) + 1
                
                # Emergency count
                if incident.get('emergency_triggered', 'False').lower() == 'true':
                    summary['emergency_incidents'] += 1
                
                # Hour analysis
                try:
                    hour = datetime.fromisoformat(incident['timestamp']).hour
                    hour_counts[hour] = hour_counts.get(hour, 0) + 1
                except (ValueError, KeyError):
                    pass
            
            # Find most active hour
            if hour_counts:
                summary['most_active_hour'] = max(hour_counts, key=hour_counts.get)
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating incident summary: {str(e)}")
            return {'error': str(e)}
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get current logging statistics
        
        Returns:
            Dictionary containing logging statistics
        """
        return dict(self.stats)
    
    def export_incidents(self, output_file: str, 
                        start_date: Optional[str] = None,
                        end_date: Optional[str] = None) -> bool:
        """
        Export incidents to a new file with optional date filtering
        
        Args:
            output_file: Path to output file
            start_date: Start date filter (ISO format)
            end_date: End date filter (ISO format)
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            if not os.path.exists(self.incident_file):
                self.logger.error("Source incident file not found")
                return False
            
            # Parse date filters
            start_timestamp = None
            end_timestamp = None
            
            if start_date:
                start_timestamp = datetime.fromisoformat(start_date).timestamp()
            if end_date:
                end_timestamp = datetime.fromisoformat(end_date).timestamp()
            
            # Read and filter incidents
            filtered_incidents = []
            
            with open(self.incident_file, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                headers = reader.fieldnames
                
                for row in reader:
                    try:
                        incident_time = datetime.fromisoformat(row['timestamp']).timestamp()
                        
                        # Apply date filters
                        if start_timestamp and incident_time < start_timestamp:
                            continue
                        if end_timestamp and incident_time > end_timestamp:
                            continue
                        
                        filtered_incidents.append(row)
                        
                    except (ValueError, KeyError):
                        continue
            
            # Write filtered incidents to output file
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                writer.writerows(filtered_incidents)
            
            self.logger.info(f"Exported {len(filtered_incidents)} incidents to {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting incidents: {str(e)}")
            return False
    
    def cleanup_old_files(self, days: int = 30) -> None:
        """
        Clean up old log files and screenshots
        
        Args:
            days: Number of days to keep files
        """
        try:
            cutoff_time = datetime.now().timestamp() - (days * 24 * 3600)
            
            # Clean up screenshots
            if os.path.exists(self.screenshot_dir):
                for filename in os.listdir(self.screenshot_dir):
                    filepath = os.path.join(self.screenshot_dir, filename)
                    
                    if os.path.isfile(filepath):
                        file_time = os.path.getmtime(filepath)
                        if file_time < cutoff_time:
                            os.remove(filepath)
                            self.logger.info(f"Removed old screenshot: {filename}")
            
            self.logger.info(f"Cleanup completed for files older than {days} days")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")
    
    def get_logger(self) -> logging.Logger:
        """Get the main logger instance"""
        return self.logger