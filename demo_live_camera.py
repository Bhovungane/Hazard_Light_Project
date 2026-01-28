"""
Live Camera Demo for Supervisor Presentation
Real-time vehicle light detection using laptop camera
"""

import cv2
import numpy as np
import sys
from light_detector import LightDetector, draw_detections
from inference import EnhancedLightDetector
from pathlib import Path
import time

class LiveCameraDemo:
    """Live camera demonstration for supervisor presentation"""
    
    def __init__(self, use_model=True):
        """Initialize the demo"""
        self.use_model = use_model
        self.model_path = None
        
        # Check for trained model
        if use_model and Path("light_classifier.pkl").exists():
            self.model_path = "light_classifier.pkl"
            print("✓ Using trained model for enhanced accuracy")
        else:
            print("ℹ Using rule-based detection")
        
        self.detector = EnhancedLightDetector(model_path=self.model_path)
        self.frame_count = 0
        self.start_time = time.time()
        
    def run_demo(self, camera_index=0):
        """Run the live camera demonstration"""
        print("\n" + "="*70)
        print(" " * 15 + "VEHICLE LIGHT INSPECTION - LIVE DEMO")
        print("="*70)
        print("\nInstructions:")
        print("  1. Point camera at vehicle lights")
        print("  2. Ensure lights are clearly visible")
        print("  3. Wait 2-3 seconds for detection")
        print("  4. Results will appear in real-time")
        print("\nControls:")
        print("  - Press 'q' to quit")
        print("  - Press 'r' to reset detection")
        print("  - Press 's' to save screenshot")
        print("="*70 + "\n")
        
        # Open camera
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            print(f"ERROR: Could not open camera {camera_index}")
            print("\nTrying alternative camera...")
            cap = cv2.VideoCapture(1)
            if not cap.isOpened():
                print("ERROR: No camera found. Please check camera connection.")
                return
        
        # Set camera properties for better quality
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Get actual camera properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        print(f"Camera opened: {width}x{height} @ {fps:.1f} FPS")
        print("Starting live detection...\n")
        
        screenshot_count = 0
        paused = False
        
        # Create window
        window_name = "VEHICLE LIGHT INSPECTION - LIVE DEMO (Press 'q' to quit)"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 1280, 720)
        
        try:
            while True:
                if not paused:
                    ret, frame = cap.read()
                    if not ret:
                        print("ERROR: Could not read from camera")
                        break
                    
                    # Flip frame horizontally for mirror effect (optional)
                    frame = cv2.flip(frame, 1)
                    
                    # Process frame
                    lights, classifications = self.detector.process_frame(frame)
                    
                    # Get tracked lights for drawing
                    tracked = {}
                    for light_id in classifications.keys():
                        if light_id in self.detector.light_history:
                            history = self.detector.light_history[light_id]
                            if len(history) > 0:
                                last = history[-1]
                                # Find corresponding light in current detections
                                for light in lights:
                                    dist = np.sqrt((light['center'][0] - last['center'][0])**2 + 
                                                  (light['center'][1] - last['center'][1])**2)
                                    if dist < 50:
                                        tracked[light_id] = light
                                        break
                    
                    # Use model classification if available
                    if self.detector.model:
                        enhanced_classifications = {}
                        for light_id in tracked.keys():
                            enhanced_classifications[light_id] = self.detector.classify_with_model(light_id)
                        classifications = enhanced_classifications
                    
                    # Draw results
                    result_frame = draw_detections(frame, lights, classifications, tracked)
                    
                    # Add demo information
                    self.add_demo_info(result_frame, classifications)
                    
                    # Display frame
                    cv2.imshow(window_name, result_frame)
                    self.frame_count += 1
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('r'):
                    # Reset detector
                    self.detector = EnhancedLightDetector(model_path=self.model_path)
                    self.frame_count = 0
                    self.start_time = time.time()
                    print("\n✓ Detection reset")
                elif key == ord('s'):
                    # Save screenshot
                    screenshot_path = f"demo_screenshot_{screenshot_count:03d}.jpg"
                    cv2.imwrite(screenshot_path, result_frame)
                    print(f"✓ Screenshot saved: {screenshot_path}")
                    screenshot_count += 1
                elif key == ord('p'):
                    paused = not paused
                    print("Paused" if paused else "Resumed")
                elif key == ord(' '):
                    # Spacebar also pauses
                    paused = not paused
        
        except KeyboardInterrupt:
            print("\n\nDemo interrupted by user")
        
        finally:
            # Cleanup
            cap.release()
            cv2.destroyAllWindows()
            
            # Print summary
            elapsed = time.time() - self.start_time
            print("\n" + "="*70)
            print("DEMO SUMMARY")
            print("="*70)
            print(f"Total frames processed: {self.frame_count}")
            print(f"Total time: {elapsed:.1f} seconds")
            if elapsed > 0:
                print(f"Average FPS: {self.frame_count/elapsed:.1f}")
            print("="*70)
    
    def add_demo_info(self, frame, classifications):
        """Add demonstration information to frame"""
        height, width = frame.shape[:2]
        
        # Add bottom info bar
        info_height = 60
        cv2.rectangle(frame, (0, height - info_height), (width, height), (0, 0, 0), -1)
        cv2.rectangle(frame, (0, height - info_height), (width, height), (255, 255, 255), 2)
        
        # Statistics
        running_count = sum(1 for c in classifications.values() if c == 'running_light')
        blinking_count = sum(1 for c in classifications.values() if c == 'hazard_light')
        total = len(classifications)
        
        # Demo status
        elapsed = time.time() - self.start_time
        fps = self.frame_count / elapsed if elapsed > 0 else 0
        
        # Left side - Detection status
        status_text = f"LIVE DETECTION | FPS: {fps:.1f} | Frame: {self.frame_count}"
        cv2.putText(frame, status_text, (10, height - 35), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Right side - Results summary
        if total > 0:
            results_text = f"RUNNING: {running_count} | BLINKING: {blinking_count} | TOTAL: {total}"
            text_size, _ = cv2.getTextSize(results_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            text_x = width - text_size[0] - 10
            cv2.putText(frame, results_text, (text_x, height - 35), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        else:
            hint_text = "Point camera at vehicle lights and wait 2-3 seconds..."
            text_size, _ = cv2.getTextSize(hint_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            text_x = width - text_size[0] - 10
            cv2.putText(frame, hint_text, (text_x, height - 35), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        # Instructions at bottom
        instructions = "Press 'q'=Quit | 'r'=Reset | 's'=Screenshot | 'p'=Pause"
        cv2.putText(frame, instructions, (10, height - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)


def main():
    """Main entry point for demo"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Live Camera Demo for Vehicle Light Inspection")
    parser.add_argument("--camera", type=int, default=0, help="Camera index (default: 0)")
    parser.add_argument("--no-model", action="store_true", help="Don't use trained model")
    
    args = parser.parse_args()
    
    # Create and run demo
    demo = LiveCameraDemo(use_model=not args.no_model)
    demo.run_demo(camera_index=args.camera)


if __name__ == "__main__":
    main()

