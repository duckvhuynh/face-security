import cv2
import mediapipe as mp
import numpy as np
import pickle
import os
import time
import threading
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk, ImageFilter
import hashlib
from cryptography.fernet import Fernet
import win32gui
import win32con
import win32api
import win32ui
from ctypes import windll
import keyboard
from sklearn.metrics.pairwise import cosine_similarity
import joblib

try:
    from config_loader import config
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    print("Warning: config_loader not available, using default settings")

class MediaPipeFaceSecuritySystem:
    def __init__(self):
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Load configuration
        if CONFIG_AVAILABLE:
            detection_confidence = config.detection_confidence
            self.config_file = config.mediapipe_config_file
            self.key_file = config.encryption_key_file
            self.grace_period = config.grace_period
            self.face_detection_interval = config.detection_interval
            self.similarity_threshold = config.similarity_threshold
            self.registration_samples = config.registration_samples  # Use config value
        else:
            detection_confidence = 0.7
            self.config_file = "mediapipe_security_config.pkl"
            self.key_file = "security.key"
            self.grace_period = 3
            self.face_detection_interval = 1.0
            self.similarity_threshold = 0.8
            self.registration_samples = 5  # Fallback value
        
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=1, min_detection_confidence=detection_confidence)
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=5,
            refine_landmarks=True,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=0.5)
        
        self.owner_face_features = []
        self.owner_name = "Owner"
        self.is_monitoring = False
        self.screen_blurred = False
        self.camera = None
        self.blur_window = None
        self.blur_thread = None
        self.last_face_time = time.time()
        self.owner_detected = True
        self.setup_encryption()
        
    def setup_encryption(self):
        """Setup encryption for storing face data securely"""
        if not os.path.exists(self.key_file):
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
        
        with open(self.key_file, 'rb') as f:
            self.encryption_key = f.read()
        self.cipher = Fernet(self.encryption_key)
    
    def hash_password(self, password):
        """Hash password for secure storage"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def extract_face_features(self, image):
        """Extract face features using MediaPipe face mesh"""
        try:
            # Ensure image is in correct format (8-bit, 3-channel BGR)
            if image.dtype != np.uint8:
                image = image.astype(np.uint8)
            
            if len(image.shape) != 3 or image.shape[2] != 3:
                print(f"Warning: Unexpected image shape {image.shape}, converting...")
                if len(image.shape) == 2:  # Grayscale
                    image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
                elif image.shape[2] == 4:  # RGBA
                    image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
            
            # Convert BGR to RGB for MediaPipe
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Ensure RGB image is contiguous in memory
            rgb_image = np.ascontiguousarray(rgb_image)
            
            results = self.face_mesh.process(rgb_image)
            
            if results.multi_face_landmarks:
                features = []
                for face_landmarks in results.multi_face_landmarks:
                    # Extract key facial landmarks
                    landmarks = []
                    for landmark in face_landmarks.landmark:
                        landmarks.extend([landmark.x, landmark.y, landmark.z])
                    features.append(np.array(landmarks))
                return features
        except Exception as e:
            print(f"Error in extract_face_features: {e}")
        return []
    
    def register_owner(self):
        """Register the owner's face with password protection"""
        print("=== Owner Registration (MediaPipe) ===")
        
        # Get password for registration
        root = tk.Tk()
        root.withdraw()
        
        password = simpledialog.askstring("Registration", "Set a password for owner registration:", show='*')
        if not password:
            messagebox.showerror("Error", "Password is required!")
            return False
        
        confirm_password = simpledialog.askstring("Registration", "Confirm password:", show='*')
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match!")
            return False
        
        root.destroy()
        
        print("Position yourself in front of the camera...")
        print("Press SPACE to capture your face, ESC to cancel")
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open camera")
            return False
        
        # Set camera properties to ensure proper format
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        face_features = []
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame")
                break
            
            # Ensure frame is in correct format
            if frame is None or frame.size == 0:
                print("Warning: Empty frame received")
                continue
                
            # Ensure frame is uint8 and 3-channel
            if frame.dtype != np.uint8:
                frame = frame.astype(np.uint8)
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Detect faces using MediaPipe face detection (more robust than face mesh for detection)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb_frame = np.ascontiguousarray(rgb_frame)  # Ensure contiguous memory
            detection_results = self.face_detection.process(rgb_frame)
            
            face_count = 0
            if detection_results.detections:
                face_count = len(detection_results.detections)
                for detection in detection_results.detections:
                    bbox = detection.location_data.relative_bounding_box
                    h, w, _ = frame.shape
                    x = int(bbox.xmin * w)
                    y = int(bbox.ymin * h)
                    width = int(bbox.width * w)
                    height = int(bbox.height * h)
                    
                    cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 255, 0), 2)
                    cv2.putText(frame, "Owner Face", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            cv2.putText(frame, "Press SPACE to capture, ESC to cancel", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Faces detected: {face_count}", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Samples collected: {len(face_features)}/{self.registration_samples}", (10, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imshow('Owner Registration', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord(' '):  # Space to capture
                current_features = self.extract_face_features(frame)
                if len(current_features) == 1:
                    face_features.append(current_features[0])
                    print(f"Face captured! Total samples: {len(face_features)}")
                    
                    if len(face_features) >= self.registration_samples:  # Use config value
                        break
                else:
                    print("Please ensure exactly one face is visible")
            elif key == 27:  # ESC to cancel
                cap.release()
                cv2.destroyAllWindows()
                return False
        
        cap.release()
        cv2.destroyAllWindows()
        
        if len(face_features) >= self.registration_samples:
            # Save the configuration
            config = {
                'face_features': face_features,
                'owner_name': self.owner_name,
                'password_hash': self.hash_password(password),
                'registration_date': datetime.now().isoformat()
            }
            
            # Encrypt and save
            encrypted_data = self.cipher.encrypt(pickle.dumps(config))
            with open(self.config_file, 'wb') as f:
                f.write(encrypted_data)
            
            print("Owner registration successful!")
            return True
        else:
            print("Registration failed - insufficient face samples")
            return False
    
    def load_owner_data(self):
        """Load owner's face data"""
        if not os.path.exists(self.config_file):
            return False
        
        try:
            with open(self.config_file, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.cipher.decrypt(encrypted_data)
            config = pickle.loads(decrypted_data)
            
            self.owner_face_features = config['face_features']
            self.owner_name = config['owner_name']
            return True
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return False
    
    def verify_password(self, password):
        """Verify password against stored hash"""
        if not os.path.exists(self.config_file):
            return False
        
        try:
            with open(self.config_file, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.cipher.decrypt(encrypted_data)
            config = pickle.loads(decrypted_data)
            
            return config['password_hash'] == self.hash_password(password)
        except Exception as e:
            print(f"Error verifying password: {e}")
            return False
    
    def compare_faces(self, features1, features2, threshold=None):
        """Enhanced face comparison using multiple metrics for better accuracy"""
        try:
            if threshold is None:
                threshold = self.similarity_threshold
            
            # Convert to numpy arrays if needed
            if not isinstance(features1, np.ndarray):
                features1 = np.array(features1)
            if not isinstance(features2, np.ndarray):
                features2 = np.array(features2)
            
            # Normalize features for better comparison
            features1_norm = features1 / np.linalg.norm(features1)
            features2_norm = features2 / np.linalg.norm(features2)
            
            # Use multiple similarity metrics for robust comparison
            # 1. Cosine similarity
            cosine_sim = cosine_similarity([features1_norm], [features2_norm])[0][0]
            
            # 2. Euclidean distance (converted to similarity)
            euclidean_dist = np.linalg.norm(features1_norm - features2_norm)
            euclidean_sim = 1 / (1 + euclidean_dist)
            
            # 3. Dot product similarity
            dot_sim = np.dot(features1_norm, features2_norm)
            
            # Weighted combination of similarities
            combined_similarity = (cosine_sim * 0.5) + (euclidean_sim * 0.3) + (dot_sim * 0.2)
            
            # Adaptive threshold based on feature quality
            feature_quality = min(np.std(features1), np.std(features2))
            adaptive_threshold = threshold * (0.8 + 0.2 * min(feature_quality, 1.0))
            
            return combined_similarity > adaptive_threshold
            
        except Exception as e:
            print(f"Error in face comparison: {e}")
            return False
    
    def detect_faces(self, frame):
        """Enhanced face detection with preprocessing and quality checks"""
        try:
            # Preprocess frame for better detection
            # 1. Enhance contrast and brightness
            enhanced_frame = cv2.convertScaleAbs(frame, alpha=1.2, beta=10)
            
            # 2. Apply noise reduction
            denoised_frame = cv2.bilateralFilter(enhanced_frame, 9, 75, 75)
            
            # 3. Extract face features from enhanced frame
            current_features = self.extract_face_features(denoised_frame)
            
            owner_detected = False
            unauthorized_face_detected = False
            total_faces = len(current_features)
            
            # Track which faces are recognized as owner
            recognized_faces = 0
            face_confidence_scores = []
            
            for features in current_features:
                is_owner = False
                best_match_score = 0
                
                # Compare with owner's face features using multiple samples
                for owner_features in self.owner_face_features:
                    if self.compare_faces(features, owner_features):
                        is_owner = True
                        owner_detected = True
                        recognized_faces += 1
                        
                        # Calculate confidence score for this match
                        features_norm = features / np.linalg.norm(features)
                        owner_norm = owner_features / np.linalg.norm(owner_features)
                        match_score = cosine_similarity([features_norm], [owner_norm])[0][0]
                        best_match_score = max(best_match_score, match_score)
                        break
                
                face_confidence_scores.append(best_match_score)
                
                # If this face is not the owner, it's unauthorized
                if not is_owner and total_faces > 0:
                    unauthorized_face_detected = True
            
            # Additional security check: verify owner confidence
            if owner_detected and face_confidence_scores:
                avg_confidence = np.mean([score for score in face_confidence_scores if score > 0])
                if avg_confidence < self.similarity_threshold * 0.9:  # High confidence required
                    print(f"⚠️  Owner detection confidence low ({avg_confidence:.2f}) - treating as unauthorized")
                    owner_detected = False
                    unauthorized_face_detected = True
            
            face_detected = total_faces > 0
            
            return owner_detected, face_detected, unauthorized_face_detected, total_faces
            
        except Exception as e:
            print(f"Error in face detection: {e}")
            return False, False, True, 0  # Fail-safe: assume unauthorized on error
    
    def get_screen_size(self):
        """Get screen dimensions"""
        user32 = windll.user32
        return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    
    def capture_screen(self):
        """Capture the current screen content"""
        try:
            # Get screen dimensions
            screen_width, screen_height = self.get_screen_size()
            
            # Create device context
            hwindc = win32gui.GetWindowDC(0)
            srcdc = win32ui.CreateDCFromHandle(hwindc)
            memdc = srcdc.CreateCompatibleDC()
            
            # Create bitmap
            bmp = win32ui.CreateBitmap()
            bmp.CreateCompatibleBitmap(srcdc, screen_width, screen_height)
            memdc.SelectObject(bmp)
            
            # Copy screen to bitmap
            memdc.BitBlt((0, 0), (screen_width, screen_height), srcdc, (0, 0), win32con.SRCCOPY)
            
            # Convert to PIL Image
            bmpinfo = bmp.GetInfo()
            bmpstr = bmp.GetBitmapBits(True)
            
            # Create PIL image from bitmap data
            img = Image.frombuffer(
                'RGB',
                (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                bmpstr, 'raw', 'BGRX', 0, 1)
            
            # Clean up
            srcdc.DeleteDC()
            memdc.DeleteDC()
            win32gui.ReleaseDC(0, hwindc)
            win32gui.DeleteObject(bmp.GetHandle())
            
            return img
            
        except Exception as e:
            print(f"Error capturing screen: {e}")
            return None
    
    def create_blurred_background(self):
        """Create a blurred version of the current screen"""
        try:
            # Check if blur is enabled
            if CONFIG_AVAILABLE and not config.enable_screen_blur:
                return None
                
            # Capture current screen
            screen_image = self.capture_screen()
            if screen_image is None:
                return None
            
            # Get configuration values
            if CONFIG_AVAILABLE:
                blur_intensity = config.blur_intensity
                quality_reduction = config.blur_quality_reduction
                overlay_darkness = config.blur_overlay_darkness
            else:
                blur_intensity = 15
                quality_reduction = 4
                overlay_darkness = 100
            
            # Apply blur effect
            # Reduce size for performance, then upscale
            small_size = (screen_image.width // quality_reduction, screen_image.height // quality_reduction)
            screen_image_small = screen_image.resize(small_size, Image.Resampling.LANCZOS)
            
            # Apply multiple blur passes for stronger effect
            blurred = screen_image_small.filter(ImageFilter.GaussianBlur(radius=blur_intensity))
            blurred = blurred.filter(ImageFilter.GaussianBlur(radius=blur_intensity//2))
            
            # Scale back to full size
            blurred_full = blurred.resize(screen_image.size, Image.Resampling.LANCZOS)
            
            # Add darkening overlay for better text readability
            overlay = Image.new('RGBA', blurred_full.size, (0, 0, 0, overlay_darkness))  # Semi-transparent black
            blurred_full = blurred_full.convert('RGBA')
            blurred_full = Image.alpha_composite(blurred_full, overlay)
            
            return blurred_full.convert('RGB')
            
        except Exception as e:
            print(f"Error creating blurred background: {e}")
            return None

    def create_blur_overlay(self):
        """Create a modern blurred overlay window with text"""
        if self.blur_window:
            return
        
        screen_width, screen_height = self.get_screen_size()
        
        # Create fullscreen window
        self.blur_window = tk.Toplevel()
        self.blur_window.title("Screen Security")
        self.blur_window.attributes('-fullscreen', True)
        self.blur_window.attributes('-topmost', True)
        self.blur_window.attributes('-toolwindow', True)
        self.blur_window.configure(bg='#000000')
        
        try:
            # Create blurred background
            print("Capturing and blurring screen...")
            blurred_bg = self.create_blurred_background()
            
            if blurred_bg:
                # Convert PIL image to PhotoImage for tkinter
                photo = ImageTk.PhotoImage(blurred_bg)
                
                # Create background label with blurred image
                bg_label = tk.Label(self.blur_window, image=photo, bd=0, highlightthickness=0)
                bg_label.image = photo  # Keep a reference
                bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            else:
                # Fallback to gradient background if screen capture fails
                self.blur_window.configure(bg='#1a1a1a')
                
        except Exception as e:
            print(f"Error setting blurred background: {e}")
            # Fallback to dark background
            self.blur_window.configure(bg='#1a1a1a')
        
        # Get warning text from config
        if CONFIG_AVAILABLE:
            warning_text = config.lock_message.replace('\\n', '\n')  # Handle escaped newlines
            hotkey = config.unlock_hotkey
        else:
            warning_text = """🔒 UNAUTHORIZED ACCESS DETECTED 🔒

ADVANCED FACIAL RECOGNITION SECURITY

This computer is protected by AI-powered face recognition.
Access is restricted to authorized personnel only.

SECURITY STATUS:
⚠️  Unauthorized person(s) detected
🔒 Screen automatically locked
🛡️  All access attempts are logged

Press Ctrl+Alt+O to enter unlock password

For assistance, contact system administrator"""
            hotkey = 'ctrl+alt+o'
        
        # Create modern glassmorphism overlay with gradient background
        overlay_frame = tk.Frame(self.blur_window, bg='#1a1a2e', bd=0, highlightthickness=0)
        overlay_frame.place(relx=0.5, rely=0.5, anchor='center', 
                           width=min(screen_width-100, 900), 
                           height=min(screen_height-100, 600))
        
        # Add subtle gradient effect using Canvas
        canvas = tk.Canvas(overlay_frame, 
                          width=min(screen_width-100, 900), 
                          height=min(screen_height-100, 600),
                          bg='#1a1a2e', highlightthickness=0, bd=0)
        canvas.pack(fill='both', expand=True)
        
        # Create gradient background on canvas
        for i in range(0, min(screen_height-100, 600), 5):
            alpha = int(255 * (i / min(screen_height-100, 600)))
            color = f"#{alpha:02x}{alpha//4:02x}{alpha//2:02x}"
            canvas.create_rectangle(0, i, min(screen_width-100, 900), i+5, 
                                  fill=color, outline=color)
        
        # Add security icon
        canvas.create_text(min(screen_width-100, 900)//2, 80, 
                          text="🛡️", font=('Segoe UI Emoji', 48), 
                          fill='#00d4ff', anchor='center')
        
        # Add main title
        canvas.create_text(min(screen_width-100, 900)//2, 150, 
                          text="SECURITY LOCKDOWN", 
                          font=('Segoe UI', 28, 'bold'), 
                          fill='#ffffff', anchor='center')
        
        # Add subtitle
        canvas.create_text(min(screen_width-100, 900)//2, 190, 
                          text="AI Face Recognition Protection Active", 
                          font=('Segoe UI', 14), 
                          fill='#00d4ff', anchor='center')
        
        # Split warning text into lines and display
        lines = warning_text.split('\n')
        y_start = 250
        for i, line in enumerate(lines):
            if line.strip():  # Skip empty lines
                font_size = 16 if '🔒' in line or '⚠️' in line else 14
                font_weight = 'bold' if '🔒' in line or '⚠️' in line else 'normal'
                color = '#ff6b6b' if '⚠️' in line else '#ffffff'
                
                canvas.create_text(min(screen_width-100, 900)//2, y_start + i*25, 
                                  text=line, 
                                  font=('Segoe UI', font_size, font_weight), 
                                  fill=color, anchor='center')
        
        # Add pulsing border effect
        border_color = '#00d4ff'
        canvas.create_rectangle(5, 5, min(screen_width-100, 900)-5, min(screen_height-100, 600)-5, 
                              outline=border_color, width=3, fill='')
        
        # Add unlock instruction at bottom
        canvas.create_text(min(screen_width-100, 900)//2, min(screen_height-100, 600)-50, 
                          text=f"Press {hotkey.upper()} to unlock", 
                          font=('Segoe UI', 16, 'bold'), 
                          fill='#00ff88', anchor='center')
        
        # Bind unlock hotkey
        keyboard.add_hotkey(hotkey, self.request_unlock)
    
    def request_unlock(self):
        """Request password to unlock screen"""
        if not self.screen_blurred:
            return
        
        root = tk.Tk()
        root.withdraw()
        
        password = simpledialog.askstring("Unlock Screen", "Enter owner password:", show='*')
        
        if password and self.verify_password(password):
            self.remove_blur_overlay()
            messagebox.showinfo("Success", "Screen unlocked!")
        else:
            messagebox.showerror("Error", "Invalid password!")
        
        root.destroy()
    
    def remove_blur_overlay(self):
        """Remove the blur overlay"""
        if self.blur_window:
            self.blur_window.destroy()
            self.blur_window = None
        self.screen_blurred = False
    
    def monitor_faces(self):
        """Main monitoring loop"""
        print("Starting MediaPipe face monitoring...")
        
        # Get camera settings from config
        if CONFIG_AVAILABLE:
            camera_index = config.camera_index
            camera_width = config.camera_width
            camera_height = config.camera_height
            camera_fps = config.camera_fps
            show_monitor = config.show_monitor_window
            show_rectangles = config.show_face_rectangles
            window_title = config.monitor_window_title
            processing_delay = config.processing_delay
        else:
            camera_index = 0
            camera_width = 640
            camera_height = 480
            camera_fps = 30
            show_monitor = True
            show_rectangles = True
            window_title = "MediaPipe Face Security Monitor"
            processing_delay = 0.1
        
        self.camera = cv2.VideoCapture(camera_index)
        
        if not self.camera.isOpened():
            print("Error: Could not open camera")
            return
        
        # Set camera properties for better performance
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, camera_width)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_height)
        self.camera.set(cv2.CAP_PROP_FPS, camera_fps)
        
        while self.is_monitoring:
            ret, frame = self.camera.read()
            if not ret:
                print("Error: Could not read frame")
                break
            
            try:
                owner_detected, face_detected, unauthorized_face_detected, total_faces = self.detect_faces(frame)
                current_time = time.time()
                
                # Store current features for display purposes
                current_features = self.extract_face_features(frame)
                
                # Enhanced security logic - Lock screen whenever ANY unauthorized face is detected
                if unauthorized_face_detected:
                    # Immediate lock when ANY unauthorized face is detected
                    if not self.screen_blurred:
                        if owner_detected and total_faces > 1:
                            print(f"🚨 SECURITY ALERT: Owner present with {total_faces - 1} unauthorized person(s) - LOCKING SCREEN")
                        elif not owner_detected:
                            print(f"🚨 UNAUTHORIZED ACCESS: {total_faces} unknown person(s) detected - LOCKING SCREEN")
                        self.create_blur_overlay()
                        self.screen_blurred = True
                elif owner_detected and not unauthorized_face_detected and total_faces == 1:
                    # Only unlock if ONLY the owner is present (no other faces)
                    self.last_face_time = current_time
                    self.owner_detected = True
                    if self.screen_blurred:
                        self.remove_blur_overlay()
                        print("✅ Owner verified alone - screen unlocked")
                        self.screen_blurred = False
                elif not face_detected:
                    # No face detected - grace period before action
                    if current_time - self.last_face_time > self.grace_period and not self.screen_blurred:
                        print("⚠️  No authorized user detected - maintaining current state")
                else:
                    # Other scenarios - maintain current state
                    self.last_face_time = current_time
                
                # Optional: Display monitoring window (comment out for stealth mode)
                if not self.screen_blurred and show_monitor:
                    # Draw face detection results
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    detection_results = self.face_detection.process(rgb_frame)
                    
                    if detection_results.detections and show_rectangles:
                        face_index = 0
                        for detection in detection_results.detections:
                            bbox = detection.location_data.relative_bounding_box
                            h, w, _ = frame.shape
                            x = int(bbox.xmin * w)
                            y = int(bbox.ymin * h)
                            width = int(bbox.width * w)
                            height = int(bbox.height * h)
                            
                            # Determine if this face is the owner
                            is_owner_face = False
                            if face_index < len(current_features):
                                for owner_features in self.owner_face_features:
                                    if self.compare_faces(current_features[face_index], owner_features):
                                        is_owner_face = True
                                        break
                            
                            color = (0, 255, 0) if is_owner_face else (0, 0, 255)
                            cv2.rectangle(frame, (x, y), (x + width, y + height), color, 2)
                            label = "Owner" if is_owner_face else "Unauthorized"
                            cv2.putText(frame, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                            face_index += 1
                    
                    # Enhanced status display
                    if unauthorized_face_detected:
                        status_text = f"SECURITY ALERT: {total_faces} faces ({('Owner + ' if owner_detected else '') + str(total_faces - (1 if owner_detected else 0)) + ' unauthorized'})"
                        status_color = (0, 0, 255)  # Red
                    elif owner_detected and total_faces == 1:
                        status_text = "Authorized (Owner Only)"
                        status_color = (0, 255, 0)  # Green
                    elif not face_detected:
                        status_text = "No faces detected"
                        status_color = (255, 255, 0)  # Yellow
                    else:
                        status_text = "Monitoring..."
                        status_color = (255, 255, 255)  # White
                    
                    cv2.putText(frame, status_text, (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
                    cv2.putText(frame, f"Total Faces: {total_faces}", (10, 60), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    cv2.putText(frame, f"Owner Present: {'Yes' if owner_detected else 'No'}", (10, 90), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0) if owner_detected else (255, 255, 255), 2)
                    cv2.putText(frame, f"Unauthorized: {'Yes' if unauthorized_face_detected else 'No'}", (10, 120), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255) if unauthorized_face_detected else (255, 255, 255), 2)
                    cv2.imshow(window_title, frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
            except Exception as e:
                print(f"Error in face detection: {e}")
            
            time.sleep(processing_delay)  # Configurable delay to reduce CPU usage
        
        self.camera.release()
        cv2.destroyAllWindows()
    
    def start_monitoring(self):
        """Start the monitoring system"""
        if not self.load_owner_data():
            print("No owner data found. Please register first.")
            return False
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self.monitor_faces, daemon=True)
        self.monitor_thread.start()
        print("MediaPipe face monitoring started...")
        return True
    
    def stop_monitoring(self):
        """Stop the monitoring system"""
        self.is_monitoring = False
        if hasattr(self, 'monitor_thread') and self.monitor_thread.is_alive():
            self.monitor_thread.join()
        self.remove_blur_overlay()
        print("Face monitoring stopped.")

def main():
    system = MediaPipeFaceSecuritySystem()
    
    print("=== MediaPipe Face Security System ===")
    print("1. Register Owner")
    print("2. Start Monitoring")
    print("3. Stop Monitoring")
    print("4. Exit")
    
    while True:
        try:
            choice = input("\nSelect option (1-4): ").strip()
            
            if choice == '1':
                if system.register_owner():
                    print("Registration completed successfully!")
                else:
                    print("Registration failed!")
            
            elif choice == '2':
                if system.start_monitoring():
                    print("Monitoring started. Press 'q' in the camera window to stop, or Ctrl+C here.")
                    print("Use Ctrl+Alt+O to unlock if screen gets blurred.")
                    try:
                        while system.is_monitoring:
                            time.sleep(1)
                    except KeyboardInterrupt:
                        system.stop_monitoring()
                else:
                    print("Failed to start monitoring!")
            
            elif choice == '3':
                system.stop_monitoring()
            
            elif choice == '4':
                system.stop_monitoring()
                print("Goodbye!")
                break
            
            else:
                print("Invalid option!")
        
        except KeyboardInterrupt:
            system.stop_monitoring()
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
