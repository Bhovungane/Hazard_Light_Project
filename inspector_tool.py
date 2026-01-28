"""
Simple Inspector Interface - Easy to use script for vehicle light inspection
Just run this script and provide your video file path
"""

import sys
import cv2
from inference import process_video, EnhancedLightDetector

def main():
    print("\n" + "="*70)
    print(" " * 15 + "VEHICLE LIGHT INSPECTION SYSTEM")
    print("="*70)
    print("\nThis system will detect and classify vehicle lights:")
    print("  ✓ RUNNING LIGHT - Steady, constant illumination (GREEN)")
    print("  ✓ BLINKING LIGHT - Hazard lights that blink (RED)")
    print("\n" + "="*70)
    
    # Get video path
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
    else:
        video_path = input("\nEnter the path to your inspection video: ").strip().strip('"')
    
    if not video_path:
        print("\nError: No video path provided.")
        print("Usage: python inspector_tool.py <video_path>")
        print("   or: python inspector_tool.py")
        return
    
    # Check if model exists
    import os
    model_path = None
    if os.path.exists("light_classifier.pkl"):
        model_path = "light_classifier.pkl"
        print("\n✓ Using trained model for better accuracy")
    else:
        print("\nℹ Using rule-based detection (train a model for better accuracy)")
    
    print("\n" + "="*70)
    print("Starting inspection...")
    print("="*70 + "\n")
    
    # Process video
    try:
        process_video(video_path, model_path=model_path)
        
        print("\n" + "="*70)
        print("Inspection Complete!")
        print("="*70)
        print("\nResults Summary:")
        print("  - Check the video window for detailed results")
        print("  - GREEN boxes indicate RUNNING LIGHTS")
        print("  - RED boxes indicate BLINKING LIGHTS (hazard)")
        print("  - Top panel shows total counts")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\nError during inspection: {e}")
        print("Please check:")
        print("  1. Video file path is correct")
        print("  2. Video format is supported (MP4, AVI)")
        print("  3. All dependencies are installed: pip install -r requirements.txt")

if __name__ == "__main__":
    main()

