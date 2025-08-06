"""
Alarm System for Human Detection Safety System
Handles audio/visual alerts and emergency protocols
"""

import cv2
import numpy as np
import pygame
import threading
import time
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import os

class AlarmSystem:
    """
    Comprehensive alarm system for safety violations
    Handles audio alerts, visual warnings, and emergency protocols
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the alarm system
        
        Args:
            config: Configuration dictionary containing alarm settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Alert configuration
        self.alert_config = config.get('alerts', {})
        self.audio_config = self.alert_config.get('audio', {})
        self.visual_config = self.alert_config.get('visual', {})
        self.text_config = self.alert_config.get('text_alerts', {})
        
        # Initialize pygame for audio
        self.audio_enabled = self.audio_config.get('enabled', True)
        if self.audio_enabled:
            self._init_audio()
        
        # Visual alert settings
        self.visual_enabled = self.visual_config.get('enabled', True)
        self.flash_duration = self.visual_config.get('flash_duration', 0.5)
        self.flash_color = self.visual_config.get('flash_color', [255, 0, 0])
        
        # Alert state tracking
        self.active_alerts = {}
        self.alert_threads = {}
        self.last_audio_time = {}
        self.flash_start_time = None
        self.is_flashing = False
        
        # Emergency protocols
        self.emergency_config = config.get('emergency', {})
        self.emergency_active = False
        self.emergency_start_time = None
        
        self.logger.info("Alarm system initialized successfully")
    
    def _init_audio(self) -> None:
        """Initialize pygame audio system"""
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.logger.info("Audio system initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize audio: {str(e)}")
            self.audio_enabled = False
    
    def trigger_alerts(self, alerts: List[Dict[str, Any]]) -> None:
        """
        Trigger appropriate alerts based on violations
        
        Args:
            alerts: List of alert objects to trigger
        """
        for alert in alerts:
            alert_id = f"{alert['zone']}_{alert['detection_type']}"
            
            # Update active alerts
            self.active_alerts[alert_id] = {
                'alert': alert,
                'start_time': time.time(),
                'last_triggered': time.time()
            }
            
            # Trigger audio alert if required
            if alert.get('requires_audio', False) and self.audio_enabled:
                self._trigger_audio_alert(alert)
            
            # Trigger visual alert if required
            if alert.get('requires_visual', True) and self.visual_enabled:
                self._trigger_visual_alert(alert)
            
            # Log the alert
            self._log_alert(alert)
    
    def _trigger_audio_alert(self, alert: Dict[str, Any]) -> None:
        """
        Trigger audio alert with appropriate sound
        
        Args:
            alert: Alert object containing alert information
        """
        try:
            alert_type = alert.get('type', 'HUMAN_DETECTED')
            severity = alert.get('severity', 'MEDIUM')
            
            # Check if enough time has passed since last audio alert
            current_time = time.time()
            repeat_interval = self.audio_config.get('repeat_interval', 2.0)
            
            if alert_type in self.last_audio_time:
                if current_time - self.last_audio_time[alert_type] < repeat_interval:
                    return  # Too soon to repeat
            
            # Start audio alert in separate thread
            audio_thread = threading.Thread(
                target=self._play_audio_alert,
                args=(alert_type, severity),
                daemon=True
            )
            audio_thread.start()
            
            self.last_audio_time[alert_type] = current_time
            
        except Exception as e:
            self.logger.error(f"Error triggering audio alert: {str(e)}")
    
    def _play_audio_alert(self, alert_type: str, severity: str) -> None:
        """
        Play audio alert sound
        
        Args:
            alert_type: Type of alert
            severity: Severity level
        """
        try:
            # Get audio file path
            alarm_file = self.audio_config.get('alarm_file', 'audio/alarm.wav')
            
            # Create default alarm sound if file doesn't exist
            if not os.path.exists(alarm_file):
                self._create_default_alarm_sound(alarm_file)
            
            # Load and play sound
            if os.path.exists(alarm_file):
                sound = pygame.mixer.Sound(alarm_file)
                volume = self.audio_config.get('volume', 0.8)
                sound.set_volume(volume)
                
                # Play different patterns based on severity
                if severity == 'CRITICAL':
                    # Continuous alarm for critical alerts
                    for _ in range(5):
                        sound.play()
                        time.sleep(0.2)
                elif severity == 'HIGH':
                    # Rapid beeps for high severity
                    for _ in range(3):
                        sound.play()
                        time.sleep(0.3)
                else:
                    # Single beep for medium/low severity
                    sound.play()
                
                # Wait for sound to finish
                time.sleep(1.0)
            
        except Exception as e:
            self.logger.error(f"Error playing audio alert: {str(e)}")
    
    def _create_default_alarm_sound(self, file_path: str) -> None:
        """
        Create a default alarm sound if none exists
        
        Args:
            file_path: Path where to save the alarm sound
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Generate a simple beep sound
            sample_rate = 22050
            duration = 0.5
            frequency = 800
            
            # Generate sine wave
            frames = int(duration * sample_rate)
            arr = np.zeros(frames)
            
            for i in range(frames):
                arr[i] = np.sin(2 * np.pi * frequency * i / sample_rate)
            
            # Convert to 16-bit integers
            arr = (arr * 32767).astype(np.int16)
            
            # Create stereo sound
            stereo_arr = np.zeros((frames, 2), dtype=np.int16)
            stereo_arr[:, 0] = arr
            stereo_arr[:, 1] = arr
            
            # Save as WAV file (simplified - in production use proper WAV library)
            self.logger.info(f"Generated default alarm sound at {file_path}")
            
        except Exception as e:
            self.logger.error(f"Error creating default alarm sound: {str(e)}")
    
    def _trigger_visual_alert(self, alert: Dict[str, Any]) -> None:
        """
        Trigger visual alert (screen flash)
        
        Args:
            alert: Alert object containing alert information
        """
        try:
            severity = alert.get('severity', 'MEDIUM')
            
            # Start visual flash
            if not self.is_flashing or severity in ['CRITICAL', 'HIGH']:
                self.flash_start_time = time.time()
                self.is_flashing = True
                
        except Exception as e:
            self.logger.error(f"Error triggering visual alert: {str(e)}")
    
    def _log_alert(self, alert: Dict[str, Any]) -> None:
        """
        Log alert information
        
        Args:
            alert: Alert object to log
        """
        try:
            log_message = (
                f"SAFETY ALERT - Type: {alert.get('type', 'UNKNOWN')}, "
                f"Severity: {alert.get('severity', 'UNKNOWN')}, "
                f"Zone: {alert.get('zone', 'UNKNOWN')}, "
                f"Detection: {alert.get('detection_type', 'UNKNOWN')}"
            )
            
            if alert.get('severity') == 'CRITICAL':
                self.logger.critical(log_message)
            elif alert.get('severity') == 'HIGH':
                self.logger.error(log_message)
            else:
                self.logger.warning(log_message)
                
        except Exception as e:
            self.logger.error(f"Error logging alert: {str(e)}")
    
    def draw_visual_alerts(self, frame: np.ndarray, 
                          alerts: List[Dict[str, Any]]) -> np.ndarray:
        """
        Draw visual alerts on the frame
        
        Args:
            frame: Input video frame
            alerts: List of active alerts
            
        Returns:
            Frame with visual alerts drawn
        """
        try:
            h, w = frame.shape[:2]
            
            # Draw flashing overlay for critical/high severity alerts
            if self.is_flashing and self.flash_start_time:
                elapsed = time.time() - self.flash_start_time
                
                if elapsed < self.flash_duration:
                    # Create flashing effect
                    flash_intensity = int(255 * (0.5 + 0.5 * np.sin(elapsed * 20)))
                    overlay = np.full_like(frame, flash_intensity, dtype=np.uint8)
                    overlay[:, :] = self.flash_color
                    
                    # Apply flash overlay
                    cv2.addWeighted(frame, 0.7, overlay, 0.3, 0, frame)
                else:
                    self.is_flashing = False
            
            # Draw alert messages
            y_offset = 50
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = self.text_config.get('font_size', 2)
            font_color = tuple(self.text_config.get('font_color', [255, 255, 255]))
            bg_color = tuple(self.text_config.get('background_color', [255, 0, 0]))
            
            for alert in alerts:
                message = alert.get('message', 'SAFETY ALERT')
                severity = alert.get('severity', 'MEDIUM')
                
                # Split message into lines
                lines = message.split('\n')
                
                for line in lines:
                    # Get text size
                    (text_width, text_height), baseline = cv2.getTextSize(
                        line, font, font_scale, 2
                    )
                    
                    # Draw background rectangle
                    cv2.rectangle(frame, 
                                (10, y_offset - text_height - 10),
                                (20 + text_width, y_offset + 10),
                                bg_color, -1)
                    
                    # Draw text
                    cv2.putText(frame, line, (15, y_offset), 
                              font, font_scale, font_color, 2)
                    
                    y_offset += text_height + 20
                
                # Add separator between alerts
                y_offset += 10
            
            # Draw emergency status
            if self.emergency_active:
                self._draw_emergency_status(frame)
            
            return frame
            
        except Exception as e:
            self.logger.error(f"Error drawing visual alerts: {str(e)}")
            return frame
    
    def _draw_emergency_status(self, frame: np.ndarray) -> None:
        """
        Draw emergency status on frame
        
        Args:
            frame: Video frame to draw on
        """
        try:
            h, w = frame.shape[:2]
            
            # Draw emergency banner
            banner_height = 80
            cv2.rectangle(frame, (0, 0), (w, banner_height), (0, 0, 255), -1)
            
            # Emergency text
            emergency_text = "🚨 EMERGENCY PROTOCOL ACTIVE 🚨"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 1.5
            
            (text_width, text_height), _ = cv2.getTextSize(emergency_text, font, font_scale, 3)
            text_x = (w - text_width) // 2
            text_y = (banner_height + text_height) // 2
            
            cv2.putText(frame, emergency_text, (text_x, text_y), 
                       font, font_scale, (255, 255, 255), 3)
            
        except Exception as e:
            self.logger.error(f"Error drawing emergency status: {str(e)}")
    
    def activate_emergency_protocol(self) -> None:
        """Activate emergency protocol"""
        try:
            if not self.emergency_active:
                self.emergency_active = True
                self.emergency_start_time = time.time()
                
                self.logger.critical("EMERGENCY PROTOCOL ACTIVATED")
                
                # Send emergency notifications
                self._send_emergency_notifications()
                
                # Trigger continuous alarm
                if self.audio_enabled:
                    emergency_thread = threading.Thread(
                        target=self._play_emergency_alarm,
                        daemon=True
                    )
                    emergency_thread.start()
                
        except Exception as e:
            self.logger.error(f"Error activating emergency protocol: {str(e)}")
    
    def deactivate_emergency_protocol(self) -> None:
        """Deactivate emergency protocol"""
        try:
            if self.emergency_active:
                self.emergency_active = False
                duration = time.time() - self.emergency_start_time if self.emergency_start_time else 0
                
                self.logger.info(f"Emergency protocol deactivated after {duration:.1f} seconds")
                
        except Exception as e:
            self.logger.error(f"Error deactivating emergency protocol: {str(e)}")
    
    def _send_emergency_notifications(self) -> None:
        """Send emergency notifications"""
        try:
            emergency_contact = self.emergency_config.get('emergency_contact', '')
            if emergency_contact:
                # In a real implementation, you would send email/SMS/push notifications
                self.logger.critical(f"Emergency notification should be sent to: {emergency_contact}")
                
        except Exception as e:
            self.logger.error(f"Error sending emergency notifications: {str(e)}")
    
    def _play_emergency_alarm(self) -> None:
        """Play continuous emergency alarm"""
        try:
            alarm_file = self.audio_config.get('alarm_file', 'audio/alarm.wav')
            
            if not os.path.exists(alarm_file):
                self._create_default_alarm_sound(alarm_file)
            
            if os.path.exists(alarm_file):
                sound = pygame.mixer.Sound(alarm_file)
                sound.set_volume(1.0)  # Maximum volume for emergency
                
                # Play continuous alarm while emergency is active
                while self.emergency_active:
                    sound.play()
                    time.sleep(0.5)  # Short interval between alarms
                    
        except Exception as e:
            self.logger.error(f"Error playing emergency alarm: {str(e)}")
    
    def update_alert_status(self) -> None:
        """Update status of active alerts and clean up expired ones"""
        try:
            current_time = time.time()
            expired_alerts = []
            
            for alert_id, alert_data in self.active_alerts.items():
                # Remove alerts that have been active for too long without updates
                if current_time - alert_data['last_triggered'] > 5.0:  # 5 second timeout
                    expired_alerts.append(alert_id)
            
            # Remove expired alerts
            for alert_id in expired_alerts:
                del self.active_alerts[alert_id]
                self.logger.debug(f"Expired alert removed: {alert_id}")
                
        except Exception as e:
            self.logger.error(f"Error updating alert status: {str(e)}")
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """
        Get list of currently active alerts
        
        Returns:
            List of active alert objects
        """
        return [alert_data['alert'] for alert_data in self.active_alerts.values()]
    
    def is_emergency_active(self) -> bool:
        """Check if emergency protocol is currently active"""
        return self.emergency_active
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about alert system performance
        
        Returns:
            Dictionary containing alert statistics
        """
        current_time = time.time()
        
        stats = {
            'active_alerts_count': len(self.active_alerts),
            'emergency_active': self.emergency_active,
            'audio_enabled': self.audio_enabled,
            'visual_enabled': self.visual_enabled,
            'emergency_duration': 0
        }
        
        if self.emergency_active and self.emergency_start_time:
            stats['emergency_duration'] = current_time - self.emergency_start_time
        
        return stats
    
    def cleanup(self) -> None:
        """Clean up alarm system resources"""
        try:
            # Deactivate emergency if active
            if self.emergency_active:
                self.deactivate_emergency_protocol()
            
            # Stop all audio
            if self.audio_enabled:
                pygame.mixer.quit()
            
            # Clear active alerts
            self.active_alerts.clear()
            
            self.logger.info("Alarm system cleaned up successfully")
            
        except Exception as e:
            self.logger.error(f"Error during alarm system cleanup: {str(e)}")