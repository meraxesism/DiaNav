#!/usr/bin/env python3
"""
Human Detection Safety System for Assembly Line
Main application integrating all safety monitoring components

This system provides real-time human detection with safety zone monitoring,
audio/visual alarms, and comprehensive incident logging for industrial safety.
"""

import cv2
import numpy as np
import time
import signal
import sys
import os
import argparse
from typing import Dict, Any, Optional
import threading
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import project modules
from utils.config_loader import ConfigLoader
from models.human_detector_simple import HumanDetector
from utils.safety_analyzer import SafetyZoneAnalyzer
from utils.alarm_system import AlarmSystem
from utils.logger_setup import SafetyLogger

class HumanDetectionSafetySystem:
    """
    Main safety system class integrating all components for comprehensive
    human detection and safety monitoring in assembly line environments
    """
    
    def __init__(self, config_path: str = "config/safety_config.yaml"):
        """
        Initialize the complete safety system
        
        Args:
            config_path: Path to configuration file
        """
        print("🚀 Initializing Human Detection Safety System...")
        
        # Load configuration
        self.config_loader = ConfigLoader(config_path)
        self.config = self.config_loader.load_config()
        
        # Create necessary directories
        self.config_loader.create_directories()
        
        # Initialize logging system
        self.safety_logger = SafetyLogger(self.config)
        self.logger = self.safety_logger.get_logger()
        
        # Initialize core components
        self.human_detector = None
        self.safety_analyzer = None
        self.alarm_system = None
        self.camera = None
        
        # System state
        self.running = False
        self.paused = False
        self.frame_count = 0
        self.start_time = None
        
        # Performance tracking
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.current_fps = 0
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.logger.info("Safety system initialization started")
    
    def initialize_components(self) -> bool:
        """
        Initialize all system components
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            self.logger.info("Initializing system components...")
            
            # Initialize human detector
            self.human_detector = HumanDetector(self.config)
            self.logger.info("✅ Human detector initialized")
            
            # Initialize safety analyzer
            self.safety_analyzer = SafetyZoneAnalyzer(self.config)
            self.logger.info("✅ Safety zone analyzer initialized")
            
            # Initialize alarm system
            self.alarm_system = AlarmSystem(self.config)
            self.logger.info("✅ Alarm system initialized")
            
            # Initialize camera
            if not self._initialize_camera():
                return False
            
            self.logger.info("✅ All components initialized successfully")
            self.safety_logger.log_system_event("INITIALIZATION", "All components initialized successfully")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {str(e)}")
            return False
    
    def _initialize_camera(self) -> bool:
        """
        Initialize camera/video source
        
        Returns:
            True if camera initialized successfully, False otherwise
        """
        try:
            camera_config = self.config_loader.get_camera_config()
            device_id = camera_config.get('device_id', 0)
            
            # Handle different device types (webcam index, IP camera URL, video file)
            if isinstance(device_id, str):
                # IP camera or video file
                self.camera = cv2.VideoCapture(device_id)
            else:
                # Webcam index
                self.camera = cv2.VideoCapture(device_id)
            
            if not self.camera.isOpened():
                raise RuntimeError(f"Could not open camera/video source: {device_id}")
            
            # Set camera properties
            resolution = camera_config.get('resolution', {})
            if 'width' in resolution and 'height' in resolution:
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, resolution['width'])
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution['height'])
            
            fps = camera_config.get('fps', 30)
            self.camera.set(cv2.CAP_PROP_FPS, fps)
            
            exposure = camera_config.get('exposure')
            if exposure is not None:
                self.camera.set(cv2.CAP_PROP_EXPOSURE, exposure)
            
            self.logger.info(f"✅ Camera initialized: {device_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize camera: {str(e)}")
            return False
    
    def run(self) -> None:
        """Main execution loop"""
        try:
            if not self.initialize_components():
                self.logger.error("Failed to initialize components. Exiting.")
                return
            
            self.running = True
            self.start_time = time.time()
            
            self.logger.info("🎯 Starting safety monitoring system...")
            self.safety_logger.log_system_event("STARTUP", "Safety monitoring system started")
            
            print("\n" + "="*60)
            print("🚨 HUMAN DETECTION SAFETY SYSTEM ACTIVE 🚨")
            print("="*60)
            print("Press 'q' to quit, 'p' to pause/resume, 's' for statistics")
            print("="*60 + "\n")
            
            # Main processing loop
            while self.running:
                if not self.paused:
                    success = self._process_frame()
                    if not success:
                        break
                else:
                    time.sleep(0.1)  # Sleep when paused
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    self.logger.info("Quit requested by user")
                    break
                elif key == ord('p'):
                    self.paused = not self.paused
                    status = "PAUSED" if self.paused else "RESUMED"
                    self.logger.info(f"System {status}")
                    print(f"System {status}")
                elif key == ord('s'):
                    self._print_statistics()
                elif key == ord('r'):
                    self._reset_emergency()
            
        except KeyboardInterrupt:
            self.logger.info("Interrupted by user")
        except Exception as e:
            self.logger.error(f"Error in main loop: {str(e)}")
        finally:
            self._cleanup()
    
    def _process_frame(self) -> bool:
        """
        Process a single video frame
        
        Returns:
            True if processing successful, False if should exit
        """
        try:
            # Read frame from camera
            ret, frame = self.camera.read()
            if not ret:
                self.logger.error("Failed to read frame from camera")
                return False
            
            self.frame_count += 1
            original_frame = frame.copy()
            
            # Run human detection
            detections = self.human_detector.detect_all(frame)
            
            # Analyze safety violations
            safety_analysis = self.safety_analyzer.analyze_detections(
                detections, frame.shape
            )
            
            # Handle violations and alerts
            if safety_analysis['violations']:
                self._handle_violations(safety_analysis, original_frame)
            
            # Update alarm system
            self.alarm_system.update_alert_status()
            
            # Check for emergency conditions
            if safety_analysis['emergency_status'] and not self.alarm_system.is_emergency_active():
                self.alarm_system.activate_emergency_protocol()
                self.safety_logger.log_system_event(
                    "EMERGENCY", "Emergency protocol activated due to consecutive violations", "CRITICAL"
                )
            
            # Draw visualizations
            display_frame = self._draw_visualizations(frame, detections, safety_analysis)
            
            # Display frame
            cv2.imshow("Assembly Line Safety Monitor", display_frame)
            
            # Update performance metrics
            self._update_performance_metrics()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error processing frame: {str(e)}")
            return False
    
    def _handle_violations(self, safety_analysis: Dict[str, Any], frame: np.ndarray) -> None:
        """
        Handle safety violations - trigger alarms and log incidents
        
        Args:
            safety_analysis: Safety analysis results
            frame: Original video frame
        """
        try:
            violations = safety_analysis.get('violations', [])
            alerts = safety_analysis.get('alerts', [])
            
            # Trigger alarms
            if alerts:
                self.alarm_system.trigger_alerts(alerts)
            
            # Log incidents
            for violation in violations:
                emergency_triggered = safety_analysis.get('emergency_status', False)
                incident_id = self.safety_logger.log_incident(
                    violation, frame, emergency_triggered
                )
                
                if incident_id:
                    self.logger.warning(f"Safety incident logged: {incident_id}")
            
        except Exception as e:
            self.logger.error(f"Error handling violations: {str(e)}")
    
    def _draw_visualizations(self, frame: np.ndarray, 
                           detections: Dict[str, Any], 
                           safety_analysis: Dict[str, Any]) -> np.ndarray:
        """
        Draw all visualizations on the frame
        
        Args:
            frame: Input video frame
            detections: Detection results
            safety_analysis: Safety analysis results
            
        Returns:
            Frame with visualizations drawn
        """
        try:
            gui_config = self.config.get('gui', {})
            
            # Draw safety zones
            if gui_config.get('show_safety_zones', True):
                frame = self.safety_analyzer.draw_safety_zones(frame)
            
            # Draw detection boxes
            if gui_config.get('show_detection_boxes', True):
                frame = self._draw_detection_boxes(frame, detections)
            
            # Draw pose landmarks
            if gui_config.get('show_pose_landmarks', True):
                frame = self._draw_pose_landmarks(frame, detections.get('poses', []))
            
            # Draw alerts
            active_alerts = self.alarm_system.get_active_alerts()
            frame = self.alarm_system.draw_visual_alerts(frame, active_alerts)
            
            # Draw system information
            frame = self._draw_system_info(frame, safety_analysis)
            
            return frame
            
        except Exception as e:
            self.logger.error(f"Error drawing visualizations: {str(e)}")
            return frame
    
    def _draw_detection_boxes(self, frame: np.ndarray, 
                            detections: Dict[str, Any]) -> np.ndarray:
        """Draw bounding boxes for detections"""
        try:
            # Draw human detections
            for human in detections.get('humans', []):
                bbox = human.get('bbox', [])
                if len(bbox) == 4:
                    x1, y1, x2, y2 = bbox
                    confidence = human.get('confidence', 0)
                    
                    # Color based on confidence
                    color = (0, 255, 0) if confidence > 0.7 else (0, 255, 255)
                    
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(frame, f"Human {confidence:.2f}", (x1, y1-10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Draw hand detections
            for hand in detections.get('hands', []):
                bbox = hand.get('bbox', [])
                if len(bbox) == 4:
                    x1, y1, x2, y2 = bbox
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 255), 2)
                    cv2.putText(frame, "Hand", (x1, y1-10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)
            
            return frame
            
        except Exception as e:
            self.logger.error(f"Error drawing detection boxes: {str(e)}")
            return frame
    
    def _draw_pose_landmarks(self, frame: np.ndarray, 
                           pose_detections: list) -> np.ndarray:
        """Draw pose landmarks"""
        try:
            for pose in pose_detections:
                landmarks = pose.get('landmarks', [])
                
                # Draw key points
                for landmark in landmarks:
                    if landmark.get('visibility', 0) > 0.5:
                        x, y = landmark['x'], landmark['y']
                        cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)
                
                # Draw connections (simplified)
                # You can add more sophisticated pose drawing here
                
            return frame
            
        except Exception as e:
            self.logger.error(f"Error drawing pose landmarks: {str(e)}")
            return frame
    
    def _draw_system_info(self, frame: np.ndarray, 
                         safety_analysis: Dict[str, Any]) -> np.ndarray:
        """Draw system information overlay"""
        try:
            h, w = frame.shape[:2]
            
            # Create info panel
            info_height = 120
            info_panel = np.zeros((info_height, w, 3), dtype=np.uint8)
            info_panel[:] = (50, 50, 50)  # Dark gray background
            
            # System status
            status = "EMERGENCY" if self.alarm_system.is_emergency_active() else "ACTIVE"
            status_color = (0, 0, 255) if status == "EMERGENCY" else (0, 255, 0)
            
            cv2.putText(info_panel, f"Status: {status}", (10, 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
            
            # Safety score
            safety_score = safety_analysis.get('safety_score', 1.0)
            score_color = (0, 255, 0) if safety_score > 0.8 else (0, 255, 255) if safety_score > 0.5 else (0, 0, 255)
            
            cv2.putText(info_panel, f"Safety Score: {safety_score:.2f}", (10, 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, score_color, 2)
            
            # FPS and frame count
            cv2.putText(info_panel, f"FPS: {self.current_fps:.1f} | Frame: {self.frame_count}", (10, 75),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Runtime
            if self.start_time:
                runtime = time.time() - self.start_time
                runtime_str = f"Runtime: {int(runtime//3600):02d}:{int((runtime%3600)//60):02d}:{int(runtime%60):02d}"
                cv2.putText(info_panel, runtime_str, (10, 95),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Active violations
            violations_count = len(safety_analysis.get('violations', []))
            if violations_count > 0:
                cv2.putText(info_panel, f"⚠️ Active Violations: {violations_count}", (300, 25),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            # Combine with main frame
            combined_frame = np.vstack([frame, info_panel])
            
            return combined_frame
            
        except Exception as e:
            self.logger.error(f"Error drawing system info: {str(e)}")
            return frame
    
    def _update_performance_metrics(self) -> None:
        """Update performance metrics"""
        try:
            self.fps_counter += 1
            current_time = time.time()
            
            # Update FPS every second
            if current_time - self.fps_start_time >= 1.0:
                self.current_fps = self.fps_counter / (current_time - self.fps_start_time)
                self.fps_counter = 0
                self.fps_start_time = current_time
                
                # Log performance metrics periodically
                if self.frame_count % 300 == 0:  # Every 10 seconds at 30 FPS
                    detector_stats = self.human_detector.get_performance_stats()
                    alarm_stats = self.alarm_system.get_alert_statistics()
                    
                    metrics = {
                        'fps': self.current_fps,
                        'frame_count': self.frame_count,
                        'detection_fps': detector_stats.get('fps', 0),
                        'active_alerts': alarm_stats.get('active_alerts_count', 0),
                        'emergency_active': alarm_stats.get('emergency_active', False)
                    }
                    
                    self.safety_logger.log_performance_metrics(metrics)
                    
        except Exception as e:
            self.logger.error(f"Error updating performance metrics: {str(e)}")
    
    def _print_statistics(self) -> None:
        """Print system statistics"""
        try:
            print("\n" + "="*50)
            print("📊 SYSTEM STATISTICS")
            print("="*50)
            
            # Basic stats
            runtime = time.time() - self.start_time if self.start_time else 0
            print(f"Runtime: {int(runtime//3600):02d}:{int((runtime%3600)//60):02d}:{int(runtime%60):02d}")
            print(f"Frames processed: {self.frame_count}")
            print(f"Current FPS: {self.current_fps:.1f}")
            
            # Detection stats
            detector_stats = self.human_detector.get_performance_stats()
            print(f"Detection FPS: {detector_stats.get('fps', 0):.1f}")
            print(f"Avg detection time: {detector_stats.get('avg_detection_time', 0)*1000:.1f}ms")
            
            # Safety stats
            violation_summary = self.safety_analyzer.get_violation_summary()
            print(f"Emergency risk level: {violation_summary.get('emergency_risk_level', 'UNKNOWN')}")
            
            # Alarm stats
            alarm_stats = self.alarm_system.get_alert_statistics()
            print(f"Active alerts: {alarm_stats.get('active_alerts_count', 0)}")
            print(f"Emergency active: {alarm_stats.get('emergency_active', False)}")
            
            # Logging stats
            logging_stats = self.safety_logger.get_statistics()
            print(f"Total incidents: {logging_stats.get('total_incidents', 0)}")
            print(f"Screenshots captured: {logging_stats.get('screenshots_captured', 0)}")
            
            print("="*50 + "\n")
            
        except Exception as e:
            self.logger.error(f"Error printing statistics: {str(e)}")
    
    def _reset_emergency(self) -> None:
        """Reset emergency protocol"""
        try:
            if self.alarm_system.is_emergency_active():
                self.alarm_system.deactivate_emergency_protocol()
                self.safety_logger.log_system_event("EMERGENCY", "Emergency protocol manually reset")
                print("Emergency protocol reset")
            else:
                print("No active emergency to reset")
                
        except Exception as e:
            self.logger.error(f"Error resetting emergency: {str(e)}")
    
    def _signal_handler(self, signum, frame) -> None:
        """Handle system signals for graceful shutdown"""
        self.logger.info(f"Received signal {signum}, initiating shutdown...")
        self.running = False
    
    def _cleanup(self) -> None:
        """Clean up resources"""
        try:
            self.logger.info("Starting system cleanup...")
            
            self.running = False
            
            # Cleanup components
            if self.alarm_system:
                self.alarm_system.cleanup()
            
            if self.human_detector:
                self.human_detector.cleanup()
            
            if self.camera:
                self.camera.release()
            
            cv2.destroyAllWindows()
            
            # Final statistics
            if self.start_time:
                total_runtime = time.time() - self.start_time
                self.logger.info(f"Total runtime: {total_runtime:.1f} seconds")
                self.logger.info(f"Total frames processed: {self.frame_count}")
                
                if self.frame_count > 0:
                    avg_fps = self.frame_count / total_runtime
                    self.logger.info(f"Average FPS: {avg_fps:.1f}")
            
            self.safety_logger.log_system_event("SHUTDOWN", "System shutdown completed")
            self.logger.info("✅ System cleanup completed")
            
            print("\n🔒 Human Detection Safety System Shutdown Complete")
            
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Human Detection Safety System for Assembly Lines")
    parser.add_argument('--config', '-c', default='config/safety_config.yaml',
                       help='Path to configuration file')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    try:
        # Initialize and run the system
        safety_system = HumanDetectionSafetySystem(args.config)
        safety_system.run()
        
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()