"""
Human Detection Module for Assembly Line Safety
Combines YOLO object detection with MediaPipe pose estimation for comprehensive human detection
"""

import cv2
import numpy as np
import mediapipe as mp
import logging
from ultralytics import YOLO
from typing import List, Tuple, Dict, Any, Optional
import time

class HumanDetector:
    """
    Advanced human detection system combining multiple detection methods
    for maximum accuracy in industrial environments
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
        
        # Initialize MediaPipe
        self.mp_pose = None
        self.mp_hands = None
        self.pose_detector = None
        self.hands_detector = None
        self._init_mediapipe()
        
        # Detection parameters
        self.yolo_confidence = config.get('models', {}).get('yolo', {}).get('confidence_threshold', 0.5)
        self.pose_confidence = config.get('models', {}).get('pose_estimation', {}).get('min_detection_confidence', 0.7)
        self.tracking_confidence = config.get('models', {}).get('pose_estimation', {}).get('min_tracking_confidence', 0.5)
        
        # Performance tracking
        self.detection_times = []
        self.frame_count = 0
        
    def _init_yolo(self) -> None:
        """Initialize YOLO model for human detection"""
        try:
            model_path = self.config.get('models', {}).get('yolo', {}).get('model_path', 'yolov8n.pt')
            self.yolo_model = YOLO(model_path)
            self.logger.info(f"YOLO model loaded: {model_path}")
        except Exception as e:
            self.logger.error(f"Failed to load YOLO model: {str(e)}")
            raise
    
    def _init_mediapipe(self) -> None:
        """Initialize MediaPipe for pose and hand detection"""
        try:
            self.mp_pose = mp.solutions.pose
            self.mp_hands = mp.solutions.hands
            
            # Initialize pose detector
            self.pose_detector = self.mp_pose.Pose(
                static_image_mode=False,
                model_complexity=1,
                smooth_landmarks=True,
                enable_segmentation=False,
                smooth_segmentation=True,
                min_detection_confidence=self.pose_confidence,
                min_tracking_confidence=self.tracking_confidence
            )
            
            # Initialize hands detector
            self.hands_detector = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=10,  # Support multiple people
                model_complexity=1,
                min_detection_confidence=0.6,
                min_tracking_confidence=0.5
            )
            
            self.logger.info("MediaPipe models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize MediaPipe: {str(e)}")
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
    
    def detect_pose_landmarks(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect human pose landmarks using MediaPipe
        
        Args:
            frame: Input video frame
            
        Returns:
            List of pose detection dictionaries with landmarks
        """
        pose_detections = []
        
        try:
            # Convert BGR to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose_detector.process(rgb_frame)
            
            if results.pose_landmarks:
                landmarks = []
                h, w, _ = frame.shape
                
                # Extract landmark coordinates
                for landmark in results.pose_landmarks.landmark:
                    x = int(landmark.x * w)
                    y = int(landmark.y * h)
                    visibility = landmark.visibility
                    landmarks.append({
                        'x': x, 'y': y, 
                        'visibility': visibility,
                        'normalized': {'x': landmark.x, 'y': landmark.y}
                    })
                
                # Calculate bounding box from landmarks
                valid_landmarks = [lm for lm in landmarks if lm['visibility'] > 0.5]
                if valid_landmarks:
                    x_coords = [lm['x'] for lm in valid_landmarks]
                    y_coords = [lm['y'] for lm in valid_landmarks]
                    
                    bbox = [
                        min(x_coords) - 20,  # Add padding
                        min(y_coords) - 20,
                        max(x_coords) + 20,
                        max(y_coords) + 20
                    ]
                    
                    pose_detections.append({
                        'type': 'pose',
                        'landmarks': landmarks,
                        'bbox': bbox,
                        'confidence': np.mean([lm['visibility'] for lm in landmarks]),
                        'body_parts': self._extract_body_parts(landmarks)
                    })
            
        except Exception as e:
            self.logger.error(f"Pose detection error: {str(e)}")
        
        return pose_detections
    
    def detect_hands(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect hands using MediaPipe
        
        Args:
            frame: Input video frame
            
        Returns:
            List of hand detection dictionaries
        """
        hand_detections = []
        
        try:
            # Convert BGR to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands_detector.process(rgb_frame)
            
            if results.multi_hand_landmarks:
                h, w, _ = frame.shape
                
                for hand_landmarks in results.multi_hand_landmarks:
                    landmarks = []
                    
                    # Extract hand landmark coordinates
                    for landmark in hand_landmarks.landmark:
                        x = int(landmark.x * w)
                        y = int(landmark.y * h)
                        landmarks.append({'x': x, 'y': y})
                    
                    # Calculate hand bounding box
                    x_coords = [lm['x'] for lm in landmarks]
                    y_coords = [lm['y'] for lm in landmarks]
                    
                    bbox = [
                        min(x_coords) - 10,
                        min(y_coords) - 10,
                        max(x_coords) + 10,
                        max(y_coords) + 10
                    ]
                    
                    hand_detections.append({
                        'type': 'hand',
                        'landmarks': landmarks,
                        'bbox': bbox,
                        'center': [int((bbox[0] + bbox[2]) / 2), int((bbox[1] + bbox[3]) / 2)],
                        'confidence': 0.9  # MediaPipe doesn't provide confidence for hands
                    })
            
        except Exception as e:
            self.logger.error(f"Hand detection error: {str(e)}")
        
        return hand_detections
    
    def _extract_body_parts(self, landmarks: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Extract specific body parts from pose landmarks
        
        Args:
            landmarks: List of pose landmarks
            
        Returns:
            Dictionary containing body part coordinates
        """
        body_parts = {
            'head': [],
            'arms': [],
            'hands': [],
            'torso': []
        }
        
        try:
            # MediaPipe pose landmark indices
            head_indices = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # Face and head
            left_arm_indices = [11, 13, 15, 17, 19, 21]  # Left arm
            right_arm_indices = [12, 14, 16, 18, 20, 22]  # Right arm
            torso_indices = [11, 12, 23, 24]  # Shoulders and hips
            
            # Extract head landmarks
            for idx in head_indices:
                if idx < len(landmarks) and landmarks[idx]['visibility'] > 0.5:
                    body_parts['head'].append(landmarks[idx])
            
            # Extract arm landmarks
            for idx in left_arm_indices + right_arm_indices:
                if idx < len(landmarks) and landmarks[idx]['visibility'] > 0.5:
                    body_parts['arms'].append(landmarks[idx])
            
            # Extract hand landmarks (wrists)
            hand_indices = [15, 16, 19, 20, 21, 22]  # Wrist and hand landmarks
            for idx in hand_indices:
                if idx < len(landmarks) and landmarks[idx]['visibility'] > 0.5:
                    body_parts['hands'].append(landmarks[idx])
            
            # Extract torso landmarks
            for idx in torso_indices:
                if idx < len(landmarks) and landmarks[idx]['visibility'] > 0.5:
                    body_parts['torso'].append(landmarks[idx])
        
        except Exception as e:
            self.logger.error(f"Error extracting body parts: {str(e)}")
        
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
        
        # Run all detection methods
        yolo_detections = self.detect_humans_yolo(frame)
        pose_detections = self.detect_pose_landmarks(frame)
        hand_detections = self.detect_hands(frame)
        
        # Combine and filter detections
        all_detections = {
            'humans': yolo_detections,
            'poses': pose_detections,
            'hands': hand_detections,
            'combined': self._combine_detections(yolo_detections, pose_detections, hand_detections)
        }
        
        # Track performance
        detection_time = time.time() - start_time
        self.detection_times.append(detection_time)
        self.frame_count += 1
        
        # Keep only last 100 detection times for average calculation
        if len(self.detection_times) > 100:
            self.detection_times.pop(0)
        
        return all_detections
    
    def _combine_detections(self, yolo_detections: List[Dict], 
                          pose_detections: List[Dict], 
                          hand_detections: List[Dict]) -> List[Dict[str, Any]]:
        """
        Combine and deduplicate detections from different methods
        
        Args:
            yolo_detections: YOLO human detections
            pose_detections: MediaPipe pose detections
            hand_detections: MediaPipe hand detections
            
        Returns:
            List of combined, deduplicated detections
        """
        combined = []
        
        # Add all YOLO detections
        combined.extend(yolo_detections)
        
        # Add pose detections (these are more detailed)
        for pose in pose_detections:
            # Check if this pose overlaps significantly with any YOLO detection
            overlaps = False
            pose_bbox = pose['bbox']
            
            for yolo_det in yolo_detections:
                if self._calculate_iou(pose_bbox, yolo_det['bbox']) > 0.3:
                    # Merge information
                    yolo_det['pose_landmarks'] = pose['landmarks']
                    yolo_det['body_parts'] = pose['body_parts']
                    overlaps = True
                    break
            
            if not overlaps:
                combined.append(pose)
        
        # Add standalone hand detections
        for hand in hand_detections:
            # Check if hand is already part of a pose detection
            is_standalone = True
            hand_center = hand['center']
            
            for detection in combined:
                if 'body_parts' in detection and detection['body_parts'].get('hands'):
                    for hand_landmark in detection['body_parts']['hands']:
                        distance = np.sqrt((hand_center[0] - hand_landmark['x'])**2 + 
                                         (hand_center[1] - hand_landmark['y'])**2)
                        if distance < 50:  # 50 pixel threshold
                            is_standalone = False
                            break
                if not is_standalone:
                    break
            
            if is_standalone:
                combined.append(hand)
        
        return combined
    
    def _calculate_iou(self, box1: List[int], box2: List[int]) -> float:
        """
        Calculate Intersection over Union (IoU) of two bounding boxes
        
        Args:
            box1: First bounding box [x1, y1, x2, y2]
            box2: Second bounding box [x1, y1, x2, y2]
            
        Returns:
            IoU value between 0 and 1
        """
        # Calculate intersection
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])
        
        if x2 <= x1 or y2 <= y1:
            return 0.0
        
        intersection = (x2 - x1) * (y2 - y1)
        
        # Calculate union
        area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0
    
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
            if self.pose_detector:
                self.pose_detector.close()
            if self.hands_detector:
                self.hands_detector.close()
            self.logger.info("Human detector cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")