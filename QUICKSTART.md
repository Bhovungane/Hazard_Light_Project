# Quick Start Guide

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Test with Your Video (Immediate Use)

If you have a video file (like your WhatsApp video):

```bash
python inference.py --video "WhatsApp Video 2025-11-16 at 20.57.26_7d7569ee.mp4"
```

This will:
- Open the video
- Detect lights automatically
- Show real-time classification (running lights vs hazard lights)
- Display results with color-coded boxes:
  - **Green boxes** = Running lights (steady)
  - **Red boxes** = Hazard lights (blinking)

Press `q` to quit, `p` to pause.

## Step 3: Train Your Own Model (For Better Accuracy)

1. **Organize your videos**:
   - Create folders: `training_data/running_lights/` and `training_data/hazard_lights/`
   - Put videos of running lights in the first folder
   - Put videos of hazard lights in the second folder

2. **Run training**:
   ```bash
   python train_model.py
   ```

3. **Use the trained model**:
   ```bash
   python inference.py --video your_video.mp4 --model light_classifier.pkl
   ```

## Tips

- **For best results**: Train with multiple videos showing different angles and lighting conditions
- **Video format**: MP4 or AVI files work best
- **Lighting**: Ensure lights are clearly visible in the video
- **Duration**: Videos should show at least 2-3 seconds of lights to detect blinking patterns

## Troubleshooting

**Problem**: No lights detected
- **Solution**: Check that lights are bright enough. You may need to adjust the intensity threshold in the code.

**Problem**: Wrong classification
- **Solution**: Train a model with your specific vehicle data. The rule-based detection works, but training improves accuracy.

**Problem**: Video won't open
- **Solution**: Make sure the video path is correct and the file format is supported (MP4, AVI).

## Example Workflow

```bash
# 1. Setup (one time)
python setup.py
pip install -r requirements.txt

# 2. Test immediately (no training needed)
python inference.py --video "your_video.mp4"

# 3. Train model (optional, for better accuracy)
# Add videos to training_data folders first
python train_model.py

# 4. Use trained model
python inference.py --video "your_video.mp4" --model light_classifier.pkl --output "result.mp4"
```

That's it! The system will automatically detect and classify the lights for you.

