# Vehicle Light Detection and Classification System

An AI-powered solution for automotive inspection that automatically detects and distinguishes between **running lights** and **hazard lights** on vehicles (specifically designed for Toyota Fortuner SUV inspections).

## Problem Statement

During vehicle inspections, inspectors face difficulty distinguishing between running lights (steady lights) and hazard lights (blinking lights) because they can appear very similar in appearance. This system uses computer vision and machine learning to automatically detect and classify these lights based on their temporal behavior (blinking patterns).

## Features

- **Automatic Light Detection**: Detects bright regions (lights) in video frames using color-based segmentation
- **Temporal Analysis**: Tracks lights across multiple frames to detect blinking patterns
- **Classification**: Distinguishes between:
  - **Running Lights**: Steady, constant illumination
  - **Hazard Lights**: Blinking lights with regular on/off cycles
- **Real-time Processing**: Can process live video from webcam or recorded video files
- **Model Training**: Train custom models on your specific vehicle data for improved accuracy

## Installation

1. **Clone or download this repository**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Quick Start

### 🎥 For Supervisor Demo (Laptop Camera)

**Live Camera Demonstration:**
```bash
# Double-click this file:
start_demo.bat

# Or run directly:
python demo_live_camera.py
```

Point your laptop camera at vehicle lights and see real-time detection!

See `DEMO_GUIDE.md` for full demonstration guide.

### Easiest Way (Recommended for Inspectors)

Simply run the inspector-friendly script:

```bash
python inspector_tool.py "your_video.mp4"
```

Or just:
```bash
python inspector_tool.py
```
Then enter your video path when prompted.

### Alternative Methods

For immediate use without training:

```bash
# Process a video file
python inference.py --video your_video.mp4

# Or use the basic detector
python light_detector.py
```

### Training a Custom Model (Recommended)

For better accuracy on your specific inspection scenarios:

1. **Organize your training videos**:
   ```
   training_data/
   ├── running_lights/
   │   ├── video1.mp4
   │   ├── video2.mp4
   │   └── ...
   └── hazard_lights/
       ├── video1.mp4
       ├── video2.mp4
       └── ...
   ```

2. **Run the training script**:
   ```bash
   python train_model.py
   ```

   The script will:
   - Extract features from your videos
   - Train a Random Forest classifier
   - Save the model as `light_classifier.pkl`

3. **Use the trained model**:
   ```bash
   python inference.py --video inspection_video.mp4 --model light_classifier.pkl
   ```

## Usage Examples

### Process Video File
```bash
python inference.py --video "WhatsApp Video 2025-11-16 at 20.57.26_7d7569ee.mp4" --output result.mp4
```

### Process with Trained Model
```bash
python inference.py --video inspection.mp4 --model light_classifier.pkl --output annotated_output.mp4
```

### Live Webcam Detection
```bash
python inference.py --webcam --model light_classifier.pkl
```

### Basic Detection (No Model)
```bash
python light_detector.py
# Then enter video path when prompted, or press Enter for webcam
```

## How It Works

### Detection Pipeline

1. **Light Detection**:
   - Converts frame to HSV color space
   - Creates masks for bright/white and yellow/amber lights
   - Finds contours and filters by size and aspect ratio
   - Detects bright regions above intensity threshold

2. **Light Tracking**:
   - Matches detected lights across frames
   - Maintains history of each light's state (on/off, position, intensity)
   - Tracks lights for temporal analysis

3. **Classification**:
   - **Rule-based**: Analyzes blinking patterns (transitions, periods)
   - **ML-based**: Uses trained model with features like:
     - Mean/std intensity
     - Number of on/off transitions
     - Blinking frequency
     - Light position and movement

### Key Features

- **Temporal Analysis**: Requires ~10-30 frames to accurately detect blinking patterns
- **Adaptive Thresholding**: Adjusts to different lighting conditions
- **Multi-light Tracking**: Can track multiple lights simultaneously
- **Visual Feedback**: Clear, inspector-friendly display with:
  - 🟢 **GREEN boxes with "RUNNING LIGHT" label**: Steady, constant lights
  - 🔴 **RED boxes with "BLINKING LIGHT" label**: Hazard lights that blink
  - 📊 **Summary Panel**: Shows total counts at the top of screen
  - ⚪ Gray: Analyzing (when not enough data yet)

## File Structure

```
hazard_blinkingAI/
├── inspector_tool.py     # Simple inspector interface (EASIEST TO USE)
├── light_detector.py     # Core detection and classification logic
├── train_model.py        # Model training script
├── inference.py          # Inference script with video/webcam support
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── QUICKSTART.md        # Quick start guide
└── training_data/       # Your training videos (create this)
    ├── running_lights/
    └── hazard_lights/
```

## Tips for Best Results

1. **Video Quality**:
   - Use videos with good lighting
   - Ensure lights are clearly visible
   - Stable camera position helps tracking

2. **Training Data**:
   - Collect multiple videos of each type
   - Include various angles and lighting conditions
   - Ensure videos show clear examples of running vs hazard lights

3. **Inspection Setup**:
   - Position camera to clearly see vehicle lights
   - Ensure consistent lighting
   - Allow a few seconds for the system to track and classify lights

## Troubleshooting

### No lights detected
- Check video quality and lighting
- Adjust intensity thresholds in `light_detector.py` (line ~60)
- Ensure lights are bright enough in the video

### Incorrect classifications
- Train a model with your specific vehicle data
- Increase `frame_buffer_size` for better temporal analysis
- Collect more diverse training data

### Performance issues
- Reduce video resolution if processing is slow
- Use GPU acceleration if available (modify code to use CUDA)

## Technical Details

- **Detection Method**: HSV color space segmentation + contour detection
- **Tracking**: Simple distance-based matching across frames
- **Classification**: Random Forest (scikit-learn) with temporal features
- **Frame Buffer**: 30 frames default (adjustable for different frame rates)

## Future Enhancements

- Deep learning-based detection (YOLO, Faster R-CNN)
- Better tracking algorithms (Kalman filter, DeepSORT)
- Support for more light types (brake lights, turn signals)
- Mobile app for on-site inspections
- Cloud-based processing for batch inspections

## License

This project is provided as-is for automotive inspection purposes.

## Support

For issues or questions, please check:
- Video file format compatibility (MP4, AVI supported)
- Python version (3.8+ recommended)
- All dependencies installed correctly

---

**Note**: This system is designed specifically for the Toyota Fortuner SUV inspection use case but can be adapted for other vehicles with appropriate training data.

