"""
Safety Zone Analyzer for Human Detection System
Analyzes detections against configured safety zones and triggers alerts
"""

import cv2
import numpy as np
import logging
from typing import List, Dict, Any, Tuple, Optional
import time
from datetime import datetime

class SafetyZoneAnalyzer:
    """
    Analyzes human detections against configured safety zones
    and determines appropriate safety responses
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the safety zone analyzer
        
        Args:
            config: Configuration dictionary containing safety zone settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Load safety zones
        self.safety_zones = config.get('safety_zones', {})
        self.danger_zones = self.safety_zones.get('danger_zones', [])
        self.safe_zones = self.safety_zones.get('safe_zones', [])
        
        # Alert tracking
        self.active_alerts = []
        self.alert_history = []
        self.consecutive_detections = {}
        self.last_detection_time = {}
        
        # Emergency settings
        self.emergency_config = config.get('emergency', {})
        self.max_consecutive = self.emergency_config.get('max_consecutive_detections', 5)
        self.detection_timeout = self.emergency_config.get('detection_timeout', 10.0)
        
        self.logger.info(f"Safety analyzer initialized with {len(self.danger_zones)} danger zones")
    
    def analyze_detections(self, detections: Dict[str, List[Dict]], 
                         frame_shape: Tuple[int, int]) -> Dict[str, Any]:
        """
        Analyze detections against safety zones
        
        Args:
            detections: Detection results from human detector
            frame_shape: Shape of the video frame (height, width)
            
        Returns:
            Dictionary containing safety analysis results
        """
        analysis_results = {
            'violations': [],
            'alerts': [],
            'emergency_status': False,
            'zone_occupancy': {},
            'safety_score': 1.0
        }
        
        h, w = frame_shape[:2]
        current_time = time.time()
        
        # Analyze each detection type
        for detection_type, detection_list in detections.items():
            if detection_type == 'combined':
                continue  # Skip combined for now, analyze individual types
                
            for detection in detection_list:
                violation = self._check_zone_violation(detection, detection_type, w, h)
                if violation:
                    analysis_results['violations'].append(violation)
                    
                    # Track consecutive detections for emergency protocols
                    self._update_consecutive_tracking(violation, current_time)
        
        # Check for emergency conditions
        analysis_results['emergency_status'] = self._check_emergency_conditions()
        
        # Calculate safety score
        analysis_results['safety_score'] = self._calculate_safety_score(analysis_results['violations'])
        
        # Generate alerts
        analysis_results['alerts'] = self._generate_alerts(analysis_results['violations'])
        
        # Update zone occupancy
        analysis_results['zone_occupancy'] = self._calculate_zone_occupancy(detections, w, h)
        
        return analysis_results
    
    def _check_zone_violation(self, detection: Dict[str, Any], 
                            detection_type: str, 
                            frame_width: int, 
                            frame_height: int) -> Optional[Dict[str, Any]]:
        """
        Check if a detection violates any safety zone
        
        Args:
            detection: Single detection object
            detection_type: Type of detection (humans, poses, hands)
            frame_width: Width of the video frame
            frame_height: Height of the video frame
            
        Returns:
            Violation dictionary if violation detected, None otherwise
        """
        # Get detection center point
        if 'center' in detection:
            center_point = detection['center']
        elif 'bbox' in detection:
            bbox = detection['bbox']
            center_point = [(bbox[0] + bbox[2]) // 2, (bbox[1] + bbox[3]) // 2]
        else:
            return None
        
        # Normalize coordinates (0.0 to 1.0)
        norm_x = center_point[0] / frame_width
        norm_y = center_point[1] / frame_height
        
        # Check against danger zones
        for zone in self.danger_zones:
            if self._point_in_polygon([norm_x, norm_y], zone['coordinates']):
                violation = {
                    'detection': detection,
                    'detection_type': detection_type,
                    'zone': zone,
                    'severity': self._calculate_severity(detection, zone),
                    'timestamp': datetime.now(),
                    'coordinates': [norm_x, norm_y]
                }
                
                # Add specific body part violations if available
                if 'body_parts' in detection:
                    body_violations = self._check_body_part_violations(
                        detection['body_parts'], zone, frame_width, frame_height
                    )
                    if body_violations:
                        violation['body_part_violations'] = body_violations
                
                return violation
        
        return None
    
    def _check_body_part_violations(self, body_parts: Dict[str, List[Dict]], 
                                  zone: Dict[str, Any], 
                                  frame_width: int, 
                                  frame_height: int) -> List[Dict[str, Any]]:
        """
        Check if specific body parts violate safety zones
        
        Args:
            body_parts: Dictionary of body part landmarks
            zone: Safety zone to check against
            frame_width: Width of the video frame
            frame_height: Height of the video frame
            
        Returns:
            List of body part violations
        """
        violations = []
        
        # Check critical body parts (hands, head, arms)
        critical_parts = ['hands', 'head', 'arms']
        
        for part_name in critical_parts:
            if part_name in body_parts:
                for landmark in body_parts[part_name]:
                    norm_x = landmark['x'] / frame_width
                    norm_y = landmark['y'] / frame_height
                    
                    if self._point_in_polygon([norm_x, norm_y], zone['coordinates']):
                        violations.append({
                            'body_part': part_name,
                            'landmark': landmark,
                            'zone': zone['name'],
                            'severity': 'HIGH' if part_name in ['hands', 'head'] else 'MEDIUM'
                        })
        
        return violations
    
    def _point_in_polygon(self, point: List[float], polygon: List[List[float]]) -> bool:
        """
        Check if a point is inside a polygon using ray casting algorithm
        
        Args:
            point: [x, y] coordinates (normalized 0.0-1.0)
            polygon: List of [x, y] polygon vertices (normalized 0.0-1.0)
            
        Returns:
            True if point is inside polygon, False otherwise
        """
        x, y = point
        n = len(polygon)
        inside = False
        
        p1x, p1y = polygon[0]
        for i in range(1, n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside
    
    def _calculate_severity(self, detection: Dict[str, Any], zone: Dict[str, Any]) -> str:
        """
        Calculate violation severity based on detection and zone characteristics
        
        Args:
            detection: Detection object
            zone: Safety zone object
            
        Returns:
            Severity level string
        """
        # Base severity on zone name and detection type
        zone_name = zone.get('name', '').lower()
        detection_type = detection.get('type', '').lower()
        
        # Critical zones
        if 'robot' in zone_name or 'machinery' in zone_name:
            return 'CRITICAL'
        
        # High risk for hands in any danger zone
        if detection_type == 'hand' or 'hand' in str(detection.get('body_part_violations', [])):
            return 'HIGH'
        
        # Medium risk for human presence
        if detection_type in ['human', 'pose']:
            return 'MEDIUM'
        
        return 'LOW'
    
    def _update_consecutive_tracking(self, violation: Dict[str, Any], current_time: float) -> None:
        """
        Update tracking of consecutive detections for emergency protocols
        
        Args:
            violation: Violation dictionary
            current_time: Current timestamp
        """
        zone_name = violation['zone']['name']
        detection_id = f"{zone_name}_{violation['detection_type']}"
        
        # Check if this is a continuation of previous detections
        if detection_id in self.last_detection_time:
            time_diff = current_time - self.last_detection_time[detection_id]
            
            if time_diff <= self.detection_timeout:
                # Consecutive detection
                self.consecutive_detections[detection_id] = \
                    self.consecutive_detections.get(detection_id, 0) + 1
            else:
                # Reset counter due to timeout
                self.consecutive_detections[detection_id] = 1
        else:
            # First detection
            self.consecutive_detections[detection_id] = 1
        
        self.last_detection_time[detection_id] = current_time
        
        # Log consecutive detections
        count = self.consecutive_detections[detection_id]
        if count >= 3:  # Log when approaching emergency threshold
            self.logger.warning(
                f"Consecutive detection #{count} in {zone_name}: {violation['detection_type']}"
            )
    
    def _check_emergency_conditions(self) -> bool:
        """
        Check if emergency conditions are met
        
        Returns:
            True if emergency conditions are detected
        """
        for detection_id, count in self.consecutive_detections.items():
            if count >= self.max_consecutive:
                self.logger.critical(f"EMERGENCY: {count} consecutive detections for {detection_id}")
                return True
        
        return False
    
    def _calculate_safety_score(self, violations: List[Dict[str, Any]]) -> float:
        """
        Calculate overall safety score based on violations
        
        Args:
            violations: List of safety violations
            
        Returns:
            Safety score from 0.0 (unsafe) to 1.0 (safe)
        """
        if not violations:
            return 1.0
        
        severity_weights = {
            'CRITICAL': 0.0,
            'HIGH': 0.2,
            'MEDIUM': 0.5,
            'LOW': 0.8
        }
        
        total_weight = 0
        for violation in violations:
            severity = violation.get('severity', 'LOW')
            total_weight += (1.0 - severity_weights.get(severity, 0.8))
        
        # Normalize by number of violations
        safety_score = max(0.0, 1.0 - (total_weight / len(violations)))
        return safety_score
    
    def _generate_alerts(self, violations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate appropriate alerts based on violations
        
        Args:
            violations: List of safety violations
            
        Returns:
            List of alert objects
        """
        alerts = []
        alert_config = self.config.get('alerts', {})
        messages = alert_config.get('text_alerts', {}).get('messages', {})
        
        for violation in violations:
            alert_type = self._determine_alert_type(violation)
            message = self._get_alert_message(violation, messages)
            
            alert = {
                'type': alert_type,
                'message': message,
                'severity': violation['severity'],
                'timestamp': violation['timestamp'],
                'zone': violation['zone']['name'],
                'detection_type': violation['detection_type'],
                'requires_audio': violation['severity'] in ['CRITICAL', 'HIGH'],
                'requires_visual': True
            }
            
            alerts.append(alert)
        
        return alerts
    
    def _determine_alert_type(self, violation: Dict[str, Any]) -> str:
        """
        Determine the type of alert based on violation characteristics
        
        Args:
            violation: Violation dictionary
            
        Returns:
            Alert type string
        """
        detection_type = violation['detection_type']
        severity = violation['severity']
        
        if detection_type == 'hand' or 'hand' in str(violation.get('body_part_violations', [])):
            return 'HAND_DETECTED'
        elif severity == 'CRITICAL':
            return 'CRITICAL_VIOLATION'
        else:
            return 'HUMAN_DETECTED'
    
    def _get_alert_message(self, violation: Dict[str, Any], messages: Dict[str, str]) -> str:
        """
        Get appropriate alert message for violation
        
        Args:
            violation: Violation dictionary
            messages: Configured alert messages
            
        Returns:
            Alert message string
        """
        detection_type = violation['detection_type']
        zone_name = violation['zone']['name']
        severity = violation['severity']
        
        if detection_type == 'hand':
            base_message = messages.get('hand_detected', '⚠️ HAND DETECTED IN RESTRICTED AREA ⚠️')
        elif 'pose' in detection_type:
            base_message = messages.get('pose_detected', '⚠️ UNSAFE POSTURE DETECTED ⚠️')
        else:
            base_message = messages.get('human_detected', '⚠️ HUMAN DETECTED IN DANGER ZONE ⚠️')
        
        # Add zone and severity information
        detailed_message = f"{base_message}\nZone: {zone_name}\nSeverity: {severity}"
        
        return detailed_message
    
    def _calculate_zone_occupancy(self, detections: Dict[str, List[Dict]], 
                                frame_width: int, 
                                frame_height: int) -> Dict[str, Dict[str, Any]]:
        """
        Calculate occupancy statistics for each zone
        
        Args:
            detections: All detection results
            frame_width: Width of the video frame
            frame_height: Height of the video frame
            
        Returns:
            Dictionary containing zone occupancy information
        """
        occupancy = {}
        
        # Initialize all zones
        for zone in self.danger_zones + self.safe_zones:
            zone_name = zone['name']
            occupancy[zone_name] = {
                'count': 0,
                'types': {},
                'zone_type': 'danger' if zone in self.danger_zones else 'safe'
            }
        
        # Count detections in each zone
        for detection_type, detection_list in detections.items():
            if detection_type == 'combined':
                continue
                
            for detection in detection_list:
                # Get detection center
                if 'center' in detection:
                    center = detection['center']
                elif 'bbox' in detection:
                    bbox = detection['bbox']
                    center = [(bbox[0] + bbox[2]) // 2, (bbox[1] + bbox[3]) // 2]
                else:
                    continue
                
                norm_x = center[0] / frame_width
                norm_y = center[1] / frame_height
                
                # Check which zones contain this detection
                for zone in self.danger_zones + self.safe_zones:
                    if self._point_in_polygon([norm_x, norm_y], zone['coordinates']):
                        zone_name = zone['name']
                        occupancy[zone_name]['count'] += 1
                        
                        if detection_type not in occupancy[zone_name]['types']:
                            occupancy[zone_name]['types'][detection_type] = 0
                        occupancy[zone_name]['types'][detection_type] += 1
        
        return occupancy
    
    def draw_safety_zones(self, frame: np.ndarray) -> np.ndarray:
        """
        Draw safety zones on the video frame
        
        Args:
            frame: Input video frame
            
        Returns:
            Frame with safety zones drawn
        """
        h, w = frame.shape[:2]
        overlay = frame.copy()
        
        # Draw danger zones
        for zone in self.danger_zones:
            points = np.array([[int(coord[0] * w), int(coord[1] * h)] 
                             for coord in zone['coordinates']], np.int32)
            
            color = zone.get('color', [255, 0, 0])  # Default red
            alpha = zone.get('alpha', 0.3)
            
            # Fill polygon
            cv2.fillPoly(overlay, [points], color)
            
            # Draw border
            cv2.polylines(frame, [points], True, color, 3)
            
            # Add zone label
            label_pos = (int(np.mean([p[0] for p in points])), 
                        int(np.mean([p[1] for p in points])))
            cv2.putText(frame, zone['name'], label_pos, 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Draw safe zones
        for zone in self.safe_zones:
            points = np.array([[int(coord[0] * w), int(coord[1] * h)] 
                             for coord in zone['coordinates']], np.int32)
            
            color = zone.get('color', [0, 255, 0])  # Default green
            alpha = zone.get('alpha', 0.2)
            
            # Fill polygon
            cv2.fillPoly(overlay, [points], color)
            
            # Draw border
            cv2.polylines(frame, [points], True, color, 2)
        
        # Blend overlay with original frame
        cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
        
        return frame
    
    def get_violation_summary(self) -> Dict[str, Any]:
        """
        Get summary of recent violations
        
        Returns:
            Dictionary containing violation statistics
        """
        current_time = time.time()
        recent_violations = [
            alert for alert in self.alert_history 
            if current_time - alert.get('timestamp', 0) < 3600  # Last hour
        ]
        
        summary = {
            'total_violations_last_hour': len(recent_violations),
            'consecutive_detections': dict(self.consecutive_detections),
            'zones_with_violations': list(set(
                alert.get('zone', 'Unknown') for alert in recent_violations
            )),
            'most_violated_zone': None,
            'emergency_risk_level': 'LOW'
        }
        
        # Find most violated zone
        if recent_violations:
            zone_counts = {}
            for alert in recent_violations:
                zone = alert.get('zone', 'Unknown')
                zone_counts[zone] = zone_counts.get(zone, 0) + 1
            
            summary['most_violated_zone'] = max(zone_counts, key=zone_counts.get)
        
        # Determine emergency risk level
        max_consecutive = max(self.consecutive_detections.values()) if self.consecutive_detections else 0
        if max_consecutive >= self.max_consecutive:
            summary['emergency_risk_level'] = 'CRITICAL'
        elif max_consecutive >= self.max_consecutive * 0.6:
            summary['emergency_risk_level'] = 'HIGH'
        elif max_consecutive >= self.max_consecutive * 0.3:
            summary['emergency_risk_level'] = 'MEDIUM'
        
        return summary