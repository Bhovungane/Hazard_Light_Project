"""
Inference script for real-time vehicle light detection and classification
"""

import cv2
import numpy as np
import argparse
from light_detector import LightDetector, draw_detections
from train_model import LightModelTrainer
import pickle
from pathlib import Path


class EnhancedLightDetector(LightDetector):
    """Enhanced detector with trained model support"""
    
    def __init__(self, model_path: str = None, frame_buffer_size: int = 30):
        super().__init__(frame_buffer_size)
        self.model = None
        if model_path and Path(model_path).exists():
            trainer = LightModelTrainer()
            self.model = trainer.load_model(model_path)
            print("Loaded trained model for enhanced classification")
    
    def classify_with_model(self, light_id: str) -> str:
        """Classify using trained model if available, otherwise use rule-based"""
        if self.model is None:
            return self.classify_light_type(light_id)
        
        if light_id not in self.light_history:
            return 'unknown'
        
        history = list(self.light_history[light_id])
        if len(history) < 10:
            return 'unknown'
        
        # Extract features (same as training)
        intensities = [h['intensity'] for h in history]
        states = [h['on'] for h in history]
        
        mean_intensity = np.mean(intensities)
        std_intensity = np.std(intensities)
        transitions = sum(1 for i in range(1, len(states)) 
                         if states[i] != states[i-1])
        on_ratio = sum(states) / len(states)
        
        if transitions > 0:
            periods = []
            current_state = states[0]
            current_duration = 1
            for i in range(1, len(states)):
                if states[i] == current_state:
                    current_duration += 1
                else:
                    periods.append(current_duration)
                    current_state = states[i]
                    current_duration = 1
            periods.append(current_duration)
            avg_period = np.mean(periods) if periods else 0
            period_std = np.std(periods) if len(periods) > 1 else 0
        else:
            avg_period = len(states)
            period_std = 0
        
        centers = [h['center'] for h in history]
        center_x = np.mean([c[0] for c in centers])
        center_y = np.mean([c[1] for c in centers])
        movement = np.sqrt(np.var([c[0] for c in centers]) + 
                          np.var([c[1] for c in centers]))
        
        feature_vector = np.array([[
            mean_intensity, std_intensity, transitions, on_ratio,
            avg_period, period_std, center_x, center_y,
            movement, len(history)
        ]])
        
        prediction = self.model.predict(feature_vector)[0]
        return prediction


def process_video(video_path: str, model_path: str = None, output_path: str = None):
    """
    Process video file and detect/classify lights
    
    Args:
        video_path: Path to input video
        model_path: Path to trained model (optional)
        output_path: Path to save output video (optional)
    """
    detector = EnhancedLightDetector(model_path=model_path)
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return
    
    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"Processing video: {video_path}")
    print(f"Resolution: {width}x{height}, FPS: {fps}, Frames: {total_frames}")
    
    # Setup video writer if output path provided
    writer = None
    if output_path:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    frame_count = 0
    results = {
        'running_lights': [],
        'hazard_lights': [],
        'unknown': []
    }
    
    print("\n" + "="*60)
    print("VEHICLE LIGHT INSPECTION SYSTEM")
    print("="*60)
    print("Processing frames...")
    print("Press 'q' to quit, 'p' to pause")
    print("="*60)
    print("\nINSPECTION RESULTS DISPLAY:")
    print("- GREEN boxes = RUNNING LIGHT (steady)")
    print("- RED boxes = BLINKING LIGHT (hazard)")
    print("- Results shown in top panel")
    print("="*60 + "\n")
    
    paused = False
    while True:
        if not paused:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Process frame
            lights, classifications = detector.process_frame(frame)
            
            # Get tracked lights
            tracked = {}
            for light_id in classifications.keys():
                if light_id in detector.light_history:
                    history = detector.light_history[light_id]
                    if len(history) > 0:
                        last = history[-1]
                        # Find corresponding light in current detections
                        for light in lights:
                            dist = np.sqrt((light['center'][0] - last['center'][0])**2 + 
                                          (light['center'][1] - last['center'][1])**2)
                            if dist < 30:
                                tracked[light_id] = light
                                break
            
            # Use model classification if available
            if detector.model:
                enhanced_classifications = {}
                for light_id in tracked.keys():
                    enhanced_classifications[light_id] = detector.classify_with_model(light_id)
                classifications = enhanced_classifications
            
            # Draw results (summary panel is now included in draw_detections)
            result_frame = draw_detections(frame, lights, classifications, tracked)
            
            # Add frame progress at bottom
            height, width = frame.shape[:2]
            progress_text = f"Frame: {frame_count}/{total_frames}"
            cv2.putText(result_frame, progress_text, (width - 200, height - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Save frame if writer available
            if writer:
                writer.write(result_frame)
            
            cv2.imshow("VEHICLE LIGHT INSPECTION - Press 'q' to quit", result_frame)
            frame_count += 1
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('p'):
            paused = not paused
            print("Paused" if paused else "Resumed")
    
    cap.release()
    if writer:
        writer.release()
    cv2.destroyAllWindows()
    
    print(f"\nProcessing complete! Processed {frame_count} frames.")
    if output_path:
        print(f"Output saved to: {output_path}")


def process_webcam(model_path: str = None):
    """Process live video from webcam"""
    detector = EnhancedLightDetector(model_path=model_path)
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return
    
    print("\n" + "="*60)
    print("VEHICLE LIGHT INSPECTION SYSTEM - LIVE MODE")
    print("="*60)
    print("Live detection started.")
    print("Press 'q' to quit, 's' to save frame")
    print("="*60)
    print("\nINSPECTION RESULTS DISPLAY:")
    print("- GREEN boxes = RUNNING LIGHT (steady)")
    print("- RED boxes = BLINKING LIGHT (hazard)")
    print("- Results shown in top panel")
    print("="*60 + "\n")
    
    frame_save_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Process frame
        lights, classifications = detector.process_frame(frame)
        
        # Get tracked lights
        tracked = {}
        for light_id in classifications.keys():
            if light_id in detector.light_history:
                history = detector.light_history[light_id]
                if len(history) > 0:
                    last = history[-1]
                    for light in lights:
                        dist = np.sqrt((light['center'][0] - last['center'][0])**2 + 
                                      (light['center'][1] - last['center'][1])**2)
                        if dist < 30:
                            tracked[light_id] = light
                            break
        
        # Use model classification if available
        if detector.model:
            enhanced_classifications = {}
            for light_id in tracked.keys():
                enhanced_classifications[light_id] = detector.classify_with_model(light_id)
            classifications = enhanced_classifications
        
        # Draw results (summary panel is now included in draw_detections)
        result_frame = draw_detections(frame, lights, classifications, tracked)
        
        cv2.imshow("VEHICLE LIGHT INSPECTION - LIVE - Press 'q' to quit", result_frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            cv2.imwrite(f"frame_{frame_save_count}.jpg", result_frame)
            print(f"Saved frame_{frame_save_count}.jpg")
            frame_save_count += 1
    
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vehicle Light Detection and Classification")
    parser.add_argument("--video", type=str, help="Path to input video file")
    parser.add_argument("--model", type=str, help="Path to trained model file")
    parser.add_argument("--output", type=str, help="Path to save output video")
    parser.add_argument("--webcam", action="store_true", help="Use webcam for live detection")
    
    args = parser.parse_args()
    
    if args.webcam:
        process_webcam(model_path=args.model)
    elif args.video:
        process_video(args.video, model_path=args.model, output_path=args.output)
    else:
        print("Please specify --video <path> or --webcam")
        print("\nExample usage:")
        print("  python inference.py --video input.mp4 --model light_classifier.pkl --output output.mp4")
        print("  python inference.py --webcam --model light_classifier.pkl")

