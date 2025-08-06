"""
Simplified Human Detection Module for Assembly Line Safety
Uses only YOLO for human detection (MediaPipe not available on Python 3.13)
"""

import cv2
import numpy as np
import logging
from ultralytics import YOLO
from typing import List, Tuple, Dict, Any, Optional
import time

class HumanDetector:
    """
    Simplified human detection system using YOLO for demonstration
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the human detection system
        
        Args:
            config: Configuration dictionary containing model settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize YOLO model
        self.yolo_model = None
        self._init_yolo()
        
        # Detection parameters
        self.yolo_confidence = config.get('models', {}).get('yolo', {}).get('confidence_threshold', 0.5)
        
        # Performance tracking
        self.detection_times = []
        self.frame_count = 0
        
        self.logger.info("Simplified human detector initialized (YOLO only)")
        
    def _init_yolo(self) -> None:
        """Initialize YOLO model for human detection"""
        try:
            model_path = self.config.get('models', {}).get('yolo', {}).get('model_path', 'yolov8n.pt')
            self.yolo_model = YOLO(model_path)
            self.logger.info(f"YOLO model loaded: {model_path}")
        except Exception as e:
            self.logger.error(f"Failed to load YOLO model: {str(e)}")
            raise
    
    def detect_humans_yolo(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect humans using YOLO model
        
        Args:
            frame: Input video frame
            
        Returns:
            List of detection dictionaries with bounding boxes and confidence scores
        """
        detections = []
        
        try:
            # Run YOLO inference
            results = self.yolo_model(frame, verbose=False)
            
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Check if detection is a person (class 0 in COCO dataset)
                        if int(box.cls) == 0 and float(box.conf) >= self.yolo_confidence:
                            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                            confidence = float(box.conf)
                            
                            detections.append({
                                'type': 'human',
                                'bbox': [int(x1), int(y1), int(x2), int(y2)],
                                'confidence': confidence,
                                'center': [int((x1 + x2) / 2), int((y1 + y2) / 2)],
                                'area': int((x2 - x1) * (y2 - y1))
                            })
            
        except Exception as e:
            self.logger.error(f"YOLO detection error: {str(e)}")
        
        return detections
    
    def detect_body_parts_from_bbox(self, frame: np.ndarray, bbox: List[int]) -> Dict[str, List[Dict]]:
        """
        Estimate body parts from bounding box (simplified approach)
        
        Args:
            frame: Input video frame
            bbox: Bounding box [x1, y1, x2, y2]
            
        Returns:
            Dictionary containing estimated body part locations
        """
        x1, y1, x2, y2 = bbox
        w = x2 - x1
        h = y2 - y1
        
        # Simple body part estimation based on human proportions
        body_parts = {
            'head': [{
                'x': int(x1 + w/2),
                'y': int(y1 + h*0.15),
                'visibility': 0.8
            }],
            'hands': [
                {  # Left hand (estimated)
                    'x': int(x1 + w*0.2),
                    'y': int(y1 + h*0.6),
                    'visibility': 0.7
                },
                {  # Right hand (estimated)
                    'x': int(x2 - w*0.2),
                    'y': int(y1 + h*0.6),
                    'visibility': 0.7
                }
            ],
            'arms': [
                {  # Left shoulder
                    'x': int(x1 + w*0.25),
                    'y': int(y1 + h*0.35),
                    'visibility': 0.8
                },
                {  # Right shoulder
                    'x': int(x2 - w*0.25),
                    'y': int(y1 + h*0.35),
                    'visibility': 0.8
                }
            ],
            'torso': [{
                'x': int(x1 + w/2),
                'y': int(y1 + h*0.5),
                'visibility': 0.9
            }]
        }
        
        return body_parts
    
    def detect_all(self, frame: np.ndarray) -> Dict[str, List[Dict[str, Any]]]:
        """
        Run all detection methods on the frame
        
        Args:
            frame: Input video frame
            
        Returns:
            Dictionary containing all detection results
        """
        start_time = time.time()
        
        # Run YOLO detection
        yolo_detections = self.detect_humans_yolo(frame)
        
        # Create pose-like detections from YOLO bounding boxes
        pose_detections = []
        hand_detections = []
        
        for detection in yolo_detections:
            bbox = detection['bbox']
            
            # Estimate body parts from bounding box
            body_parts = self.detect_body_parts_from_bbox(frame, bbox)
            
            # Create pose detection
            pose_detection = {
                'type': 'pose',
                'bbox': bbox,
                'confidence': detection['confidence'],
                'body_parts': body_parts,
                'landmarks': []  # Empty for simplified version
            }
            pose_detections.append(pose_detection)
            
            # Create hand detections from estimated hand positions
            for hand in body_parts['hands']:
                if hand['visibility'] > 0.5:
                    hand_bbox = [
                        hand['x'] - 20, hand['y'] - 20,
                        hand['x'] + 20, hand['y'] + 20
                    ]
                    hand_detection = {
                        'type': 'hand',
                        'bbox': hand_bbox,
                        'center': [hand['x'], hand['y']],
                        'confidence': hand['visibility']
                    }
                    hand_detections.append(hand_detection)
        
        # Combine results
        all_detections = {
            'humans': yolo_detections,
            'poses': pose_detections,
            'hands': hand_detections,
            'combined': yolo_detections + pose_detections + hand_detections
        }
        
        # Track performance
        detection_time = time.time() - start_time
        self.detection_times.append(detection_time)
        self.frame_count += 1
        
        # Keep only last 100 detection times for average calculation
        if len(self.detection_times) > 100:
            self.detection_times.pop(0)
        
        return all_detections
    
    def get_performance_stats(self) -> Dict[str, float]:
        """
        Get performance statistics
        
        Returns:
            Dictionary containing performance metrics
        """
        if not self.detection_times:
            return {'avg_detection_time': 0.0, 'fps': 0.0}
        
        avg_time = np.mean(self.detection_times)
        fps = 1.0 / avg_time if avg_time > 0 else 0.0
        
        return {
            'avg_detection_time': avg_time,
            'fps': fps,
            'total_frames': self.frame_count
        }
    
    def cleanup(self) -> None:
        """Clean up resources"""
        try:
            self.logger.info("Human detector cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")