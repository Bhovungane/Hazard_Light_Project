# Production Deployment Guide

This guide will help you deploy the Vehicle Light Inspection System on your production line for inspectors to use.

## Prerequisites

- Windows 10/11 computer (or Windows Server)
- Python 3.8 or higher
- At least 4GB RAM
- Webcam or video camera (for live inspection) OR video files
- Internet connection (for initial installation only)

## Deployment Steps

### Option 1: Quick Deployment (Recommended)

1. **Copy the entire folder** to the production computer
   - Copy `hazard_blinkingAI` folder to: `C:\InspectionSystem\`

2. **Run Installation**
   - Double-click `install.bat`
   - Wait for installation to complete (5-10 minutes)
   - Installation will:
     - Check Python installation
     - Create necessary folders
     - Install all dependencies
     - Verify installation

3. **Launch the Application**
   - Double-click `start_inspection.bat`
   - The GUI application will open

4. **First Use**
   - Click "Browse Video" to select an inspection video
   - Click "START INSPECTION"
   - Results will appear in real-time

### Option 2: Manual Installation

If you prefer manual installation:

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Create directories
python setup.py

# 3. Launch application
python inspection_app.py
```

## Production Setup

### 1. Create Desktop Shortcut

1. Right-click `start_inspection.bat`
2. Select "Create Shortcut"
3. Drag shortcut to Desktop
4. Rename to "Vehicle Inspection"
5. (Optional) Right-click shortcut → Properties → Change Icon

### 2. Train Custom Model (Optional but Recommended)

For better accuracy on your specific vehicles:

1. Collect training videos:
   - Videos showing running lights → `training_data/running_lights/`
   - Videos showing hazard lights → `training_data/hazard_lights/`

2. Run training:
   ```bash
   python train_model.py
   ```

3. The trained model (`light_classifier.pkl`) will be automatically used

### 3. Configure for Production Line

#### For Video File Inspection:
- Inspectors can select video files from a shared folder
- Results are displayed in real-time
- Logs are saved in `logs/` folder

#### For Live Camera Inspection:
- Connect webcam/camera to computer
- Use the command line version:
  ```bash
  python inference.py --webcam
  ```

### 4. Network Deployment (Multiple Stations)

If deploying to multiple inspection stations:

1. **Central Installation**:
   - Install on one computer first
   - Test thoroughly
   - Copy entire folder to other computers

2. **Shared Model** (Optional):
   - Train model once
   - Copy `light_classifier.pkl` to all stations
   - Place in each station's folder

3. **Shared Training Data** (Optional):
   - Use network drive for training videos
   - All stations can access same training data

## User Guide for Inspectors

### Daily Use

1. **Launch Application**
   - Double-click "Vehicle Inspection" shortcut
   - Wait for application to load

2. **Select Video**
   - Click "Browse Video" button
   - Navigate to inspection video
   - Select video file (MP4, AVI, etc.)

3. **Start Inspection**
   - Click "START INSPECTION" button
   - Video window will open showing:
     - **GREEN boxes** = RUNNING LIGHT
     - **RED boxes** = BLINKING LIGHT
     - Top panel shows counts

4. **View Results**
   - Results appear in real-time in video window
   - Summary appears in application window
   - Press 'q' in video window to close

5. **Next Inspection**
   - Click "Browse Video" again
   - Select next video
   - Repeat process

### Understanding Results

- **RUNNING LIGHT** (Green): Steady, constant illumination - Normal operation
- **BLINKING LIGHT** (Red): Hazard lights that blink - May indicate issue
- **ANALYZING...** (Gray): System is still processing (wait a few seconds)

### Troubleshooting

**Application won't start:**
- Check if Python is installed: Open Command Prompt, type `python --version`
- Run `install.bat` again
- Check logs folder for error messages

**No lights detected:**
- Ensure video quality is good
- Check that lights are clearly visible
- Try different video angle/lighting

**Wrong classification:**
- Train a custom model with your vehicle data
- Ensure video shows at least 2-3 seconds of lights
- Check lighting conditions

**Video won't load:**
- Check file format (MP4, AVI supported)
- Ensure file is not corrupted
- Try a different video file

## Maintenance

### Regular Tasks

1. **Check Logs** (Weekly):
   - Review `logs/` folder
   - Look for errors or warnings
   - Archive old logs monthly

2. **Update Model** (As needed):
   - Collect new training videos
   - Retrain model: `python train_model.py`
   - Replace old `light_classifier.pkl`

3. **Backup** (Monthly):
   - Backup entire folder
   - Backup trained models
   - Backup configuration files

### System Requirements Check

Run this periodically:
```bash
python -c "import cv2, numpy, sklearn; print('All OK')"
```

## Advanced Configuration

### Adjust Detection Sensitivity

Edit `light_detector.py`:
- Line ~77: `intensity > 150` - Adjust for brighter/dimmer lights
- Line ~67: `area > 100` - Adjust for larger/smaller lights

### Performance Tuning

For faster processing:
- Reduce video resolution
- Use trained model (faster than rule-based)
- Process shorter video segments

## Support and Logs

- **Logs Location**: `logs/inspection_YYYYMMDD.log`
- **Error Reports**: Check logs folder for detailed error messages
- **Training Data**: `training_data/` folder

## Security Considerations

- Application runs locally (no internet required after installation)
- No data is sent to external servers
- All processing happens on local computer
- Logs contain only local inspection data

## Updating the System

1. Backup current installation
2. Download new version
3. Copy new files (preserve `light_classifier.pkl` if you have one)
4. Run `install.bat` to update dependencies
5. Test before deploying to production

## Contact and Support

For issues or questions:
1. Check logs in `logs/` folder
2. Review this deployment guide
3. Check README.md for technical details

---

**Production Checklist:**
- [ ] Python installed
- [ ] Dependencies installed (run install.bat)
- [ ] Application launches (test start_inspection.bat)
- [ ] Test with sample video
- [ ] Desktop shortcut created
- [ ] Inspectors trained on usage
- [ ] Backup created
- [ ] Logs folder accessible

