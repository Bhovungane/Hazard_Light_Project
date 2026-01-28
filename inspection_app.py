"""
Production GUI Application for Vehicle Light Inspection
Easy-to-use interface for inspectors on the production line
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import threading
import os
import sys
from pathlib import Path
from inference import EnhancedLightDetector, process_video, process_webcam
from light_detector import draw_detections
import numpy as np
import logging
from datetime import datetime

# Setup logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f"inspection_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)

class InspectionApp:
    """Main GUI application for vehicle light inspection"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Vehicle Light Inspection System")
        self.root.geometry("900x700")
        self.root.configure(bg='#2b2b2b')
        
        # State variables
        self.detector = None
        self.processing = False
        self.recording = False
        self.video_path = None
        self.model_path = None
        self.use_camera = True  # Default to camera mode
        self.recorded_video_path = None
        
        # Check for trained model
        if Path("light_classifier.pkl").exists():
            self.model_path = "light_classifier.pkl"
            logging.info("Found trained model: light_classifier.pkl")
        
        self.setup_ui()
        self.check_dependencies()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Header
        header_frame = tk.Frame(self.root, bg='#1e1e1e', height=80)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="VEHICLE LIGHT INSPECTION SYSTEM",
            font=('Arial', 20, 'bold'),
            bg='#1e1e1e',
            fg='#ffffff'
        )
        title_label.pack(pady=20)
        
        # Main content area
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Input source selection
        source_frame = tk.LabelFrame(
            main_frame,
            text="Input Source",
            font=('Arial', 12, 'bold'),
            bg='#2b2b2b',
            fg='#ffffff',
            padx=15,
            pady=15
        )
        source_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Radio buttons for source selection
        self.source_var = tk.StringVar(value="camera")
        
        camera_radio = tk.Radiobutton(
            source_frame,
            text="📷 Use Live Camera",
            variable=self.source_var,
            value="camera",
            command=self.on_source_change,
            font=('Arial', 11, 'bold'),
            bg='#2b2b2b',
            fg='#ffffff',
            selectcolor='#1e1e1e',
            activebackground='#2b2b2b',
            activeforeground='#4caf50',
            cursor='hand2'
        )
        camera_radio.pack(side=tk.LEFT, padx=20)
        
        video_radio = tk.Radiobutton(
            source_frame,
            text="📁 Use Video File",
            variable=self.source_var,
            value="video",
            command=self.on_source_change,
            font=('Arial', 11, 'bold'),
            bg='#2b2b2b',
            fg='#ffffff',
            selectcolor='#1e1e1e',
            activebackground='#2b2b2b',
            activeforeground='#4caf50',
            cursor='hand2'
        )
        video_radio.pack(side=tk.LEFT, padx=20)
        
        # Video file selection (hidden when camera is selected)
        self.video_frame = tk.Frame(source_frame, bg='#2b2b2b')
        self.video_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.video_path_label = tk.Label(
            self.video_frame,
            text="No video selected",
            font=('Arial', 10),
            bg='#2b2b2b',
            fg='#cccccc',
            wraplength=500,
            justify=tk.LEFT
        )
        self.video_path_label.pack(side=tk.LEFT, padx=10)
        
        self.browse_btn = tk.Button(
            self.video_frame,
            text="Browse Video",
            command=self.browse_video,
            bg='#4a9eff',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=5,
            cursor='hand2'
        )
        self.browse_btn.pack(side=tk.RIGHT, padx=10)
        
        # Initially hide video selection (camera is default)
        self.video_frame.pack_forget()
        
        # Model status section
        model_frame = tk.LabelFrame(
            main_frame,
            text="Model Status",
            font=('Arial', 12, 'bold'),
            bg='#2b2b2b',
            fg='#ffffff',
            padx=15,
            pady=15
        )
        model_frame.pack(fill=tk.X, pady=(0, 15))
        
        if self.model_path:
            model_status = "✓ Trained model loaded (Enhanced Accuracy)"
            model_color = '#4caf50'
        else:
            model_status = "ℹ Using rule-based detection (Train model for better accuracy)"
            model_color = '#ff9800'
        
        self.model_status_label = tk.Label(
            model_frame,
            text=model_status,
            font=('Arial', 10),
            bg='#2b2b2b',
            fg=model_color,
            wraplength=700
        )
        self.model_status_label.pack(anchor=tk.W, padx=10)
        
        # Control buttons
        control_frame = tk.Frame(main_frame, bg='#2b2b2b')
        control_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.record_btn = tk.Button(
            control_frame,
            text="🔴 RECORD VIDEO",
            command=self.start_recording,
            bg='#f44336',
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=20,
            pady=12,
            cursor='hand2',
            state=tk.NORMAL
        )
        self.record_btn.pack(side=tk.LEFT, padx=5)
        
        self.start_btn = tk.Button(
            control_frame,
            text="▶ START INSPECTION",
            command=self.start_inspection,
            bg='#4caf50',
            fg='white',
            font=('Arial', 14, 'bold'),
            padx=30,
            pady=15,
            cursor='hand2',
            state=tk.NORMAL  # Enabled by default for camera
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(
            control_frame,
            text="⏹ STOP",
            command=self.stop_inspection,
            bg='#ff9800',
            fg='white',
            font=('Arial', 14, 'bold'),
            padx=30,
            pady=15,
            cursor='hand2',
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Results section
        results_frame = tk.LabelFrame(
            main_frame,
            text="Inspection Results",
            font=('Arial', 12, 'bold'),
            bg='#2b2b2b',
            fg='#ffffff',
            padx=15,
            pady=15
        )
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Results display
        self.results_text = tk.Text(
            results_frame,
            height=15,
            font=('Courier', 11),
            bg='#1e1e1e',
            fg='#ffffff',
            wrap=tk.WORD,
            padx=15,
            pady=15
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(self.results_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.results_text.yview)
        
        # Instructions
        instructions = """
INSTRUCTIONS - RECORD & ANALYZE:
1. Click 'RECORD VIDEO' to record from camera
2. Point camera at vehicle lights
3. Click 'STOP' when done recording
4. AI will automatically analyze the recorded video
5. Results will appear in the video window

OR - LIVE INSPECTION:
1. Click 'START INSPECTION' for live detection
2. Point camera at vehicle lights
3. See real-time results

OR - USE VIDEO FILE:
1. Select 'Use Video File' option
2. Click 'Browse Video' to select a file
3. Click 'START INSPECTION'

RESULT INTERPRETATION:
• GREEN boxes = RUNNING LIGHT (steady, constant)
• RED boxes = BLINKING LIGHT (hazard light)
• Top panel shows total counts

Press 'q' in video window to close it.
        """
        self.results_text.insert('1.0', instructions)
        self.results_text.config(state=tk.DISABLED)
        
        # Initialize source state after all UI elements are created
        self.on_source_change(log=False)  # Set initial state
    
    def check_dependencies(self):
        """Check if all dependencies are installed"""
        try:
            import cv2
            import numpy
            import sklearn
            self.log_message("✓ All dependencies installed")
        except ImportError as e:
            error_msg = f"Missing dependency: {e}\n\nPlease run: pip install -r requirements.txt"
            messagebox.showerror("Missing Dependencies", error_msg)
            logging.error(f"Missing dependency: {e}")
    
    def on_source_change(self, log=True):
        """Handle source selection change"""
        if self.source_var.get() == "camera":
            self.use_camera = True
            self.video_frame.pack_forget()
            self.start_btn.config(state=tk.NORMAL)
            if log:
                self.log_message("Input source: Live Camera")
        else:
            self.use_camera = False
            self.video_frame.pack(fill=tk.X, pady=(10, 0))
            if self.video_path:
                self.start_btn.config(state=tk.NORMAL)
            else:
                self.start_btn.config(state=tk.DISABLED)
            if log:
                self.log_message("Input source: Video File")
    
    def browse_video(self):
        """Open file dialog to select video"""
        file_path = filedialog.askopenfilename(
            title="Select Inspection Video",
            filetypes=[
                ("Video files", "*.mp4 *.avi *.mov *.mkv"),
                ("MP4 files", "*.mp4"),
                ("AVI files", "*.avi"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.video_path = file_path
            self.video_path_label.config(
                text=f"Selected: {os.path.basename(file_path)}",
                fg='#4caf50'
            )
            self.start_btn.config(state=tk.NORMAL)
            self.log_message(f"Video selected: {os.path.basename(file_path)}")
    
    def log_message(self, message):
        """Add message to results text area"""
        self.results_text.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.results_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.results_text.see(tk.END)
        self.results_text.config(state=tk.DISABLED)
        logging.info(message)
    
    def start_recording(self):
        """Start recording video from camera"""
        if self.recording:
            return
        
        self.recording = True
        self.record_btn.config(state=tk.DISABLED, text="🔴 RECORDING...")
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL, text="⏹ STOP RECORDING")
        
        self.log_message("="*60)
        self.log_message("Starting video recording...")
        self.log_message("Point camera at vehicle lights")
        self.log_message("Click 'STOP RECORDING' when done")
        self.log_message("="*60)
        
        # Run recording in separate thread
        thread = threading.Thread(target=self.record_video, daemon=True)
        thread.start()
    
    def record_video(self):
        """Record video from camera and then analyze it"""
        from datetime import datetime
        
        try:
            # Open camera
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                self.root.after(0, lambda: messagebox.showerror("Camera Error", "Could not open camera"))
                return
            
            # Set camera properties
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            cap.set(cv2.CAP_PROP_FPS, 30)
            
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            
            # Create output directory
            output_dir = Path("recorded_videos")
            output_dir.mkdir(exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            video_filename = f"inspection_{timestamp}.mp4"
            video_path = output_dir / video_filename
            
            # Setup video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(str(video_path), fourcc, fps, (width, height))
            
            self.root.after(0, lambda: self.log_message(f"Recording to: {video_filename}"))
            self.root.after(0, lambda: self.log_message("Press 'q' in camera window to stop recording"))
            
            frame_count = 0
            window_name = "RECORDING - Press 'q' to stop"
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            
            # Recording loop
            while self.recording:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Add recording indicator
                cv2.putText(frame, "RECORDING...", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.putText(frame, f"Frames: {frame_count}", (10, 70), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, "Press 'q' to stop", (10, height - 20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Write frame
                out.write(frame)
                frame_count += 1
                
                # Display frame
                cv2.imshow(window_name, frame)
                
                # Check for 'q' key to stop
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.recording = False
                    break
            
            # Cleanup
            cap.release()
            out.release()
            cv2.destroyAllWindows()
            
            if frame_count > 0:
                self.recorded_video_path = str(video_path)
                self.root.after(0, lambda: self.log_message(f"Recording saved: {video_filename} ({frame_count} frames)"))
                self.root.after(0, lambda: self.log_message("Starting AI analysis..."))
                
                # Automatically analyze the recorded video
                self.root.after(0, self.analyze_recorded_video)
            else:
                self.root.after(0, lambda: self.log_message("Recording cancelled or failed"))
        
        except Exception as e:
            error_msg = f"Error during recording: {str(e)}"
            self.root.after(0, lambda: self.log_message(f"ERROR: {error_msg}"))
            logging.error(f"Recording error: {e}", exc_info=True)
            self.root.after(0, lambda: messagebox.showerror("Recording Error", error_msg))
        
        finally:
            self.recording = False
            self.root.after(0, self.reset_recording_buttons)
    
    def analyze_recorded_video(self):
        """Automatically analyze the recorded video"""
        if not self.recorded_video_path or not os.path.exists(self.recorded_video_path):
            self.log_message("ERROR: Recorded video not found")
            return
        
        self.log_message("="*60)
        self.log_message("AI Analysis Starting...")
        self.log_message(f"Video: {os.path.basename(self.recorded_video_path)}")
        if self.model_path:
            self.log_message("Using trained model for enhanced accuracy")
        else:
            self.log_message("Using rule-based AI detection (train model for better accuracy)")
        self.log_message("="*60)
        
        # Process the recorded video
        self.video_path = self.recorded_video_path
        self.processing = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL, text="⏹ STOP")
        
        # Run analysis in separate thread
        thread = threading.Thread(target=self.run_inspection, daemon=True)
        thread.start()
    
    def reset_recording_buttons(self):
        """Reset recording button states"""
        self.record_btn.config(state=tk.NORMAL, text="🔴 RECORD VIDEO")
        if self.use_camera or self.video_path:
            self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED, text="⏹ STOP")
    
    def start_inspection(self):
        """Start the inspection process"""
        if self.use_camera:
            # Using live camera
            self.processing = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            
            self.log_message("="*60)
            self.log_message("Starting live camera inspection...")
            if self.model_path:
                self.log_message("Using trained model for enhanced accuracy")
            else:
                self.log_message("Using rule-based detection")
            self.log_message("Camera window will open shortly...")
            self.log_message("="*60)
            
            # Run camera inspection in separate thread
            thread = threading.Thread(target=self.run_camera_inspection, daemon=True)
            thread.start()
        else:
            # Using video file
            if not self.video_path:
                messagebox.showwarning("No Video", "Please select a video file first")
                return
            
            if not os.path.exists(self.video_path):
                messagebox.showerror("File Not Found", f"Video file not found:\n{self.video_path}")
                return
            
            self.processing = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            
            self.log_message("="*60)
            self.log_message("Starting inspection...")
            self.log_message(f"Video: {os.path.basename(self.video_path)}")
            if self.model_path:
                self.log_message("Using trained model for enhanced accuracy")
            else:
                self.log_message("Using rule-based detection")
            self.log_message("="*60)
            
            # Run video inspection in separate thread
            thread = threading.Thread(target=self.run_inspection, daemon=True)
            thread.start()
    
    def run_inspection(self):
        """Run the actual inspection (in separate thread)"""
        try:
            # Initialize detector
            self.detector = EnhancedLightDetector(model_path=self.model_path)
            
            # Process video
            process_video(
                self.video_path,
                model_path=self.model_path,
                output_path=None
            )
            
            if self.processing:  # Only log if not stopped
                self.log_message("="*60)
                self.log_message("Inspection completed successfully!")
                self.log_message("Check the video window for detailed results")
                self.log_message("="*60)
                messagebox.showinfo("Inspection Complete", 
                                   "Inspection completed!\n\nCheck the results in the video window.")
        
        except Exception as e:
            error_msg = f"Error during inspection: {str(e)}"
            self.log_message(f"ERROR: {error_msg}")
            logging.error(f"Inspection error: {e}", exc_info=True)
            messagebox.showerror("Inspection Error", 
                               f"An error occurred:\n\n{error_msg}\n\nCheck logs for details.")
        
        finally:
            self.processing = False
            self.root.after(0, self.reset_buttons)
    
    def stop_inspection(self):
        """Stop the inspection or recording"""
        if self.recording:
            self.recording = False
            self.log_message("Recording stopped by user")
            self.reset_recording_buttons()
        else:
            self.processing = False
            self.log_message("Inspection stopped by user")
            self.reset_buttons()
    
    def run_camera_inspection(self):
        """Run live camera inspection (in separate thread)"""
        try:
            # Initialize detector
            self.detector = EnhancedLightDetector(model_path=self.model_path)
            
            # Process webcam
            process_webcam(model_path=self.model_path)
            
            if self.processing:  # Only log if not stopped
                self.log_message("="*60)
                self.log_message("Camera inspection completed!")
                self.log_message("="*60)
        
        except Exception as e:
            error_msg = f"Error during camera inspection: {str(e)}"
            self.log_message(f"ERROR: {error_msg}")
            logging.error(f"Camera inspection error: {e}", exc_info=True)
            messagebox.showerror("Camera Error", 
                               f"An error occurred:\n\n{error_msg}\n\nCheck logs for details.")
        
        finally:
            self.processing = False
            self.root.after(0, self.reset_buttons)
    
    def reset_buttons(self):
        """Reset button states"""
        if self.use_camera or self.video_path:
            self.start_btn.config(state=tk.NORMAL)
        else:
            self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.DISABLED, text="⏹ STOP")
        self.record_btn.config(state=tk.NORMAL, text="🔴 RECORD VIDEO")


def main():
    """Main entry point"""
    root = tk.Tk()
    app = InspectionApp(root)
    
    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()


if __name__ == "__main__":
    main()

