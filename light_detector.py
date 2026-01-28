"""
Vehicle Light Detection and Classification System
Detects and distinguishes between running lights and hazard lights
"""

import cv2
import numpy as np
from typing import List, Tuple, Dict
from collections import deque
import time


class LightDetector:
    """Detects vehicle lights and classifies them as running or hazard lights"""
    
    def __init__(self, frame_buffer_size: int = 30):
        """
        Initialize the light detector
        
        Args:
            frame_buffer_size: Number of frames to keep for temporal analysis
        """
        self.frame_buffer_size = frame_buffer_size
        self.light_history = {}  # Track light states over time
        self.frame_count = 0
        
    def detect_lights(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect bright regions (lights) in the frame
        
        Args:
            frame: Input image frame
            
        Returns:
            List of detected light regions with bounding boxes
        """
        # Convert to HSV for better color-based detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Create mask for bright/white and yellow/amber lights
        # White/clear lights
        lower_white = np.array([0, 0, 200])
        upper_white = np.array([180, 30, 255])
        mask_white = cv2.inRange(hsv, lower_white, upper_white)
        
        # Yellow/amber lights (hazard lights often amber)
        lower_yellow = np.array([20, 100, 100])
        upper_yellow = np.array([30, 255, 255])
        mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
        
        # Combine masks
        mask = cv2.bitwise_or(mask_white, mask_yellow)
        
        # Apply morphological operations to clean up
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        detected_lights = []
        for contour in contours:
            area = cv2.contourArea(contour)
            # Filter by area (lights should be reasonably sized)
            if area > 100 and area < 50000:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h if h > 0 else 0
                
                # Filter by aspect ratio (lights are typically wider than tall)
                if 0.5 < aspect_ratio < 3.0:
                    # Calculate brightness/intensity
                    roi = frame[y:y+h, x:x+w]
                    intensity = np.mean(cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY))
                    
                    if intensity > 150:  # Threshold for bright lights
                        detected_lights.append({
                            'bbox': (x, y, w, h),
                            'center': (x + w//2, y + h//2),
                            'area': area,
                            'intensity': intensity,
                            'id': len(detected_lights)
                        })
        
        return detected_lights
    
    def track_lights(self, detected_lights: List[Dict], frame_number: int) -> Dict:
        """
        Track lights across frames and build history for blinking detection
        
        Args:
            detected_lights: List of detected lights in current frame
            frame_number: Current frame number
            
        Returns:
            Dictionary mapping light IDs to their states
        """
        current_light_states = {}
        
        # Match detected lights with previous detections
        for light in detected_lights:
            center = light['center']
            light_id = None
            min_distance = float('inf')
            
            # Find closest previous light
            for prev_id, history in self.light_history.items():
                if len(history) > 0:
                    last_center = history[-1]['center']
                    distance = np.sqrt((center[0] - last_center[0])**2 + 
                                     (center[1] - last_center[1])**2)
                    if distance < 50 and distance < min_distance:  # Max 50 pixels movement
                        min_distance = distance
                        light_id = prev_id
            
            # Create new ID if no match found
            if light_id is None:
                light_id = f"light_{len(self.light_history)}"
                self.light_history[light_id] = deque(maxlen=self.frame_buffer_size)
            
            # Add current state to history
            self.light_history[light_id].append({
                'center': center,
                'intensity': light['intensity'],
                'frame': frame_number,
                'on': light['intensity'] > 180  # Threshold for "on" state
            })
            
            current_light_states[light_id] = light
        
        # Clean up old lights that haven't been seen
        active_ids = set(current_light_states.keys())
        for light_id in list(self.light_history.keys()):
            if light_id not in active_ids:
                # Check if it's been missing for too long
                if len(self.light_history[light_id]) > 0:
                    last_frame = self.light_history[light_id][-1]['frame']
                    if frame_number - last_frame > 10:  # Remove after 10 frames
                        del self.light_history[light_id]
        
        return current_light_states
    
    def classify_light_type(self, light_id: str) -> str:
        """
        Classify light as running light or hazard light based on blinking pattern
        
        Args:
            light_id: ID of the light to classify
            
        Returns:
            'running_light' or 'hazard_light'
        """
        if light_id not in self.light_history:
            return 'unknown'
        
        history = list(self.light_history[light_id])
        if len(history) < 10:  # Need enough frames to detect pattern
            return 'unknown'
        
        # Extract on/off states
        states = [h['on'] for h in history]
        
        # Count transitions (on->off or off->on)
        transitions = sum(1 for i in range(1, len(states)) if states[i] != states[i-1])
        
        # Calculate average on/off duration
        if transitions == 0:
            # No transitions - steady light (running light)
            return 'running_light'
        
        # Calculate blinking frequency
        on_periods = []
        off_periods = []
        current_state = states[0]
        current_duration = 1
        
        for i in range(1, len(states)):
            if states[i] == current_state:
                current_duration += 1
            else:
                if current_state:
                    on_periods.append(current_duration)
                else:
                    off_periods.append(current_duration)
                current_state = states[i]
                current_duration = 1
        
        # Add last period
        if current_state:
            on_periods.append(current_duration)
        else:
            off_periods.append(current_duration)
        
        # Hazard lights typically blink at ~1-2 Hz (every 15-30 frames at 30fps)
        # Running lights are steady or have very slow changes
        avg_on_period = np.mean(on_periods) if on_periods else float('inf')
        avg_off_period = np.mean(off_periods) if off_periods else float('inf')
        
        # If there are regular on/off cycles with similar periods, it's blinking
        if transitions > 3 and 5 < avg_on_period < 30 and 5 < avg_off_period < 30:
            return 'hazard_light'
        elif transitions > 0 and (avg_on_period < 5 or avg_off_period < 5):
            # Very fast blinking - could be hazard light
            return 'hazard_light'
        else:
            # Steady or slow changes - running light
            return 'running_light'
    
    def process_frame(self, frame: np.ndarray) -> Tuple[List[Dict], Dict]:
        """
        Process a single frame and return detections with classifications
        
        Args:
            frame: Input image frame
            
        Returns:
            Tuple of (detected_lights, classifications)
        """
        self.frame_count += 1
        
        # Detect lights
        detected_lights = self.detect_lights(frame)
        
        # Track lights
        tracked_lights = self.track_lights(detected_lights, self.frame_count)
        
        # Classify each tracked light
        classifications = {}
        for light_id in tracked_lights.keys():
            classifications[light_id] = self.classify_light_type(light_id)
        
        return detected_lights, classifications


def draw_detections(frame: np.ndarray, lights: List[Dict], 
                   classifications: Dict, tracked_lights: Dict) -> np.ndarray:
    """
    Draw bounding boxes and labels on frame with clear inspector-friendly display
    
    Args:
        frame: Input frame
        lights: List of detected lights
        classifications: Dictionary mapping light IDs to classifications
        tracked_lights: Dictionary of tracked lights
        
    Returns:
        Annotated frame
    """
    result_frame = frame.copy()
    height, width = frame.shape[:2]
    
    # Color mapping - bright, clear colors
    colors = {
        'running_light': (0, 255, 0),  # Bright Green
        'hazard_light': (0, 0, 255),   # Bright Red
        'unknown': (128, 128, 128)     # Gray
    }
    
    # Inspector-friendly label mapping
    label_map = {
        'running_light': 'RUNNING LIGHT',
        'hazard_light': 'BLINKING LIGHT',
        'unknown': 'ANALYZING...'
    }
    
    # Draw detections with large, clear labels
    for light_id, light in tracked_lights.items():
        x, y, w, h = light['bbox']
        classification = classifications.get(light_id, 'unknown')
        color = colors.get(classification, (128, 128, 128))
        
        # Draw thick bounding box (3px for visibility)
        cv2.rectangle(result_frame, (x, y), (x + w, y + h), color, 3)
        
        # Draw large, clear label
        label = label_map.get(classification, 'ANALYZING...')
        font_scale = 0.8
        thickness = 2
        label_size, baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
        
        # Background rectangle for label
        label_y = max(y - 10, label_size[1] + 10)
        cv2.rectangle(result_frame, 
                     (x, label_y - label_size[1] - 10), 
                     (x + label_size[0] + 10, label_y + 5), 
                     color, -1)
        
        # Draw label text
        cv2.putText(result_frame, label, (x + 5, label_y - 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness)
    
    # Draw summary panel at top of screen
    running_count = sum(1 for c in classifications.values() if c == 'running_light')
    blinking_count = sum(1 for c in classifications.values() if c == 'hazard_light')
    total_detected = len(tracked_lights)
    
    # Create summary panel background
    panel_height = 120
    cv2.rectangle(result_frame, (0, 0), (width, panel_height), (0, 0, 0), -1)
    cv2.rectangle(result_frame, (0, 0), (width, panel_height), (255, 255, 255), 2)
    
    # Title
    title = "VEHICLE LIGHT INSPECTION RESULT"
    title_size, _ = cv2.getTextSize(title, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2)
    title_x = (width - title_size[0]) // 2
    cv2.putText(result_frame, title, (title_x, 35), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
    
    # Results display
    result_y = 70
    if total_detected > 0:
        # Running lights count
        running_text = f"RUNNING LIGHTS: {running_count}"
        cv2.putText(result_frame, running_text, (50, result_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        # Blinking lights count
        blinking_text = f"BLINKING LIGHTS: {blinking_count}"
        cv2.putText(result_frame, blinking_text, (400, result_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        # Total detected
        total_text = f"TOTAL DETECTED: {total_detected}"
        cv2.putText(result_frame, total_text, (750, result_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    else:
        status_text = "SCANNING FOR LIGHTS... (Please ensure lights are visible)"
        text_size, _ = cv2.getTextSize(status_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        text_x = (width - text_size[0]) // 2
        cv2.putText(result_frame, status_text, (text_x, result_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
    
    return result_frame


if __name__ == "__main__":
    # Example usage
    detector = LightDetector()
    
    # Test with video file
    video_path = input("Enter video file path (or press Enter for webcam): ").strip()
    
    if not video_path:
        cap = cv2.VideoCapture(0)
    else:
        cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("Error: Could not open video source")
        exit(1)
    
    print("Press 'q' to quit, 's' to save frame")
    
    frame_save_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Process frame
        lights, classifications = detector.process_frame(frame)
        
        # Get tracked lights for drawing
        tracked = {lid: light for lid, light in zip(classifications.keys(), 
                   [l for l in lights if len(lights) > 0])}
        
        # Draw results
        result_frame = draw_detections(frame, lights, classifications, tracked)
        
        # Display is now handled in draw_detections function
        cv2.imshow("VEHICLE LIGHT INSPECTION - Press 'q' to quit", result_frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            cv2.imwrite(f"frame_{frame_save_count}.jpg", result_frame)
            print(f"Saved frame_{frame_save_count}.jpg")
            frame_save_count += 1
    
    cap.release()
    cv2.destroyAllWindows()

