"""
Setup script for Vehicle Light Detection System
"""

import os
from pathlib import Path

def setup_directories():
    """Create necessary directories for the project"""
    directories = [
        "training_data/running_lights",
        "training_data/hazard_lights",
        "output"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory}")

if __name__ == "__main__":
    print("Setting up Vehicle Light Detection System...")
    setup_directories()
    print("\nSetup complete!")
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Add your training videos to training_data/running_lights/ and training_data/hazard_lights/")
    print("3. Run: python train_model.py")
    print("4. Use: python inference.py --video your_video.mp4 --model light_classifier.pkl")

