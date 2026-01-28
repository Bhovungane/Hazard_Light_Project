"""
Training script for vehicle light classification model
Uses collected video data to train a model that distinguishes running lights from hazard lights
"""

import cv2
import numpy as np
import os
import json
from pathlib import Path
from light_detector import LightDetector
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import pickle
from tqdm import tqdm


class LightModelTrainer:
    """Train a model to classify vehicle lights"""
    
    def __init__(self):
        self.detector = LightDetector()
        self.features = []
        self.labels = []
        
    def extract_features(self, video_path: str, label: str, max_frames: int = 100):
        """
        Extract features from video frames
        
        Args:
            video_path: Path to video file
            label: 'running_light' or 'hazard_light'
            max_frames: Maximum number of frames to process
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Warning: Could not open {video_path}")
            return
        
        frame_count = 0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frames_to_process = min(max_frames, total_frames)
        step = max(1, total_frames // frames_to_process)
        
        print(f"Processing {video_path} ({label})...")
        
        while frame_count < frames_to_process:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Skip frames
            for _ in range(step - 1):
                cap.read()
            
            # Process frame
            lights, classifications = self.detector.process_frame(frame)
            
            # Extract features for each detected light
            for light_id, light in self.detector.light_history.items():
                history = list(self.detector.light_history[light_id])
                if len(history) >= 10:  # Need enough history
                    # Extract temporal features
                    intensities = [h['intensity'] for h in history]
                    states = [h['on'] for h in history]
                    
                    # Calculate features
                    mean_intensity = np.mean(intensities)
                    std_intensity = np.std(intensities)
                    transitions = sum(1 for i in range(1, len(states)) 
                                    if states[i] != states[i-1])
                    on_ratio = sum(states) / len(states)
                    
                    # Calculate blinking frequency
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
                    
                    # Spatial features
                    centers = [h['center'] for h in history]
                    center_x = np.mean([c[0] for c in centers])
                    center_y = np.mean([c[1] for c in centers])
                    movement = np.sqrt(np.var([c[0] for c in centers]) + 
                                     np.var([c[1] for c in centers]))
                    
                    # Create feature vector
                    feature_vector = [
                        mean_intensity,
                        std_intensity,
                        transitions,
                        on_ratio,
                        avg_period,
                        period_std,
                        center_x,
                        center_y,
                        movement,
                        len(history)
                    ]
                    
                    self.features.append(feature_vector)
                    self.labels.append(label)
            
            frame_count += 1
        
        cap.release()
        print(f"Extracted {len([f for f in self.labels if f == label])} samples from {video_path}")
    
    def train(self, test_size: float = 0.2):
        """
        Train the classification model
        
        Args:
            test_size: Proportion of data to use for testing
        """
        if len(self.features) == 0:
            print("Error: No features extracted. Please process videos first.")
            return None
        
        print(f"\nTraining on {len(self.features)} samples...")
        
        # Convert to numpy arrays
        X = np.array(self.features)
        y = np.array(self.labels)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        print(f"Training set: {len(X_train)} samples")
        print(f"Test set: {len(X_test)} samples")
        
        # Train Random Forest classifier
        print("\nTraining Random Forest classifier...")
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"\nTest Accuracy: {accuracy:.4f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        
        # Feature importance
        print("\nFeature Importances:")
        feature_names = [
            'mean_intensity', 'std_intensity', 'transitions', 'on_ratio',
            'avg_period', 'period_std', 'center_x', 'center_y', 
            'movement', 'history_length'
        ]
        importances = model.feature_importances_
        for name, importance in sorted(zip(feature_names, importances), 
                                      key=lambda x: x[1], reverse=True):
            print(f"  {name}: {importance:.4f}")
        
        return model
    
    def save_model(self, model, path: str = "light_classifier.pkl"):
        """Save trained model to file"""
        with open(path, 'wb') as f:
            pickle.dump(model, f)
        print(f"\nModel saved to {path}")
    
    def load_model(self, path: str = "light_classifier.pkl"):
        """Load trained model from file"""
        with open(path, 'rb') as f:
            model = pickle.load(f)
        print(f"Model loaded from {path}")
        return model


def collect_training_data():
    """Interactive function to collect and label training data"""
    trainer = LightModelTrainer()
    
    print("=== Vehicle Light Classification Training Data Collection ===\n")
    print("This script will help you collect training data from videos.")
    print("You'll need videos showing:")
    print("  1. Running lights (steady lights)")
    print("  2. Hazard lights (blinking lights)\n")
    
    # Create data directory
    data_dir = Path("training_data")
    data_dir.mkdir(exist_ok=True)
    
    running_dir = data_dir / "running_lights"
    hazard_dir = data_dir / "hazard_lights"
    running_dir.mkdir(exist_ok=True)
    hazard_dir.mkdir(exist_ok=True)
    
    print("Please organize your videos:")
    print(f"  - Running lights: {running_dir}")
    print(f"  - Hazard lights: {hazard_dir}\n")
    
    # Process running lights
    running_videos = list(running_dir.glob("*.mp4")) + list(running_dir.glob("*.avi"))
    if running_videos:
        print(f"Found {len(running_videos)} running light video(s)")
        for video in running_videos:
            trainer.extract_features(str(video), "running_light")
    else:
        print("No running light videos found. Please add videos to the directory.")
    
    # Process hazard lights
    hazard_videos = list(hazard_dir.glob("*.mp4")) + list(hazard_dir.glob("*.avi"))
    if hazard_videos:
        print(f"Found {len(hazard_videos)} hazard light video(s)")
        for video in hazard_videos:
            trainer.extract_features(str(video), "hazard_light")
    else:
        print("No hazard light videos found. Please add videos to the directory.")
    
    if len(trainer.features) > 0:
        print(f"\nTotal samples collected: {len(trainer.features)}")
        print(f"  Running lights: {sum(1 for l in trainer.labels if l == 'running_light')}")
        print(f"  Hazard lights: {sum(1 for l in trainer.labels if l == 'hazard_light')}")
        
        # Train model
        model = trainer.train()
        
        if model:
            trainer.save_model(model)
            print("\nTraining complete! You can now use the model for inference.")
    else:
        print("\nNo training data collected. Please add videos to the directories.")


if __name__ == "__main__":
    collect_training_data()

