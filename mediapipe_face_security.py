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
        else:
            detection_confidence = 0.7
            self.config_file = "mediapipe_security_config.pkl"
            self.key_file = "security.key"
            self.grace_period = 3
            self.face_detection_interval = 1.0
            self.similarity_threshold = 0.8
        
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
            cv2.putText(frame, f"Samples collected: {len(face_features)}/5", (10, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imshow('Owner Registration', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord(' '):  # Space to capture
                current_features = self.extract_face_features(frame)
                if len(current_features) == 1:
                    face_features.append(current_features[0])
                    print(f"Face captured! Total samples: {len(face_features)}")
                    
                    if len(face_features) >= 5:  # Collect 5 samples
                        break
                else:
                    print("Please ensure exactly one face is visible")
            elif key == 27:  # ESC to cancel
                cap.release()
                cv2.destroyAllWindows()
                return False
        
        cap.release()
        cv2.destroyAllWindows()
        
        if len(face_features) >= 5:
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
        """Compare two face feature sets using cosine similarity"""
        try:
            if threshold is None:
                threshold = self.similarity_threshold
            similarity = cosine_similarity([features1], [features2])[0][0]
            return similarity > threshold
        except:
            return False
    
    def detect_faces(self, frame):
        """Detect and recognize faces in frame"""
        current_features = self.extract_face_features(frame)
        
        owner_detected = False
        unauthorized_face_detected = False
        total_faces = len(current_features)
        
        # Track which faces are recognized as owner
        recognized_faces = 0
        
        for features in current_features:
            is_owner = False
            # Compare with owner's face features
            for owner_features in self.owner_face_features:
                if self.compare_faces(features, owner_features):
                    is_owner = True
                    owner_detected = True
                    recognized_faces += 1
                    break
            
            # If this face is not the owner, it's unauthorized
            if not is_owner and total_faces > 0:
                unauthorized_face_detected = True
        
        # Security logic: Lock if unauthorized faces detected, regardless of owner presence
        face_detected = total_faces > 0
        
        return owner_detected, face_detected, unauthorized_face_detected, total_faces
    
    def get_screen_size(self):
        """Get screen dimensions"""
        user32 = windll.user32
        return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    
    def create_blur_overlay(self):
        """Create a blurred overlay window"""
        if self.blur_window:
            return
        
        screen_width, screen_height = self.get_screen_size()
        
        # Create fullscreen window
        self.blur_window = tk.Toplevel()
        self.blur_window.title("Screen Security")
        self.blur_window.configure(bg='black')
        self.blur_window.attributes('-fullscreen', True)
        self.blur_window.attributes('-topmost', True)
        self.blur_window.attributes('-toolwindow', True)
        
        # Create blur effect with warning
        if CONFIG_AVAILABLE:
            warning_text = config.lock_message
        else:
            warning_text = """🔒 UNAUTHORIZED ACCESS DETECTED 🔒

SCREEN LOCKED FOR SECURITY

This computer is protected by facial recognition security.
Only the registered owner can unlock this screen.

Press Ctrl+Alt+O to enter unlock password

⚠️ All access attempts are being logged ⚠️"""
        
        blur_label = tk.Label(self.blur_window, 
                             text=warning_text, 
                             fg='red', bg='black', 
                             font=('Arial', 20, 'bold'),
                             justify='center')
        blur_label.pack(expand=True)
        
        # Bind unlock hotkey
        if CONFIG_AVAILABLE:
            hotkey = config.unlock_hotkey
        else:
            hotkey = 'ctrl+alt+o'
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
                
                # Enhanced security logic
                if unauthorized_face_detected:
                    # Lock screen if ANY unauthorized face is detected, even with owner present
                    if not self.screen_blurred:
                        if owner_detected:
                            print(f"SECURITY ALERT: Owner present but {total_faces - 1} unauthorized face(s) detected - locking screen")
                        else:
                            print(f"Unknown person(s) detected ({total_faces} faces) - locking screen")
                        self.create_blur_overlay()
                        self.screen_blurred = True
                elif owner_detected and not unauthorized_face_detected and total_faces == 1:
                    # Only unlock if ONLY the owner is present (no other faces)
                    self.last_face_time = current_time
                    self.owner_detected = True
                    if self.screen_blurred:
                        self.remove_blur_overlay()
                        print("Owner detected alone - screen unlocked")
                elif owner_detected and total_faces > 1:
                    # Owner is present but with other faces - keep locked
                    if not self.screen_blurred:
                        print(f"Owner present with {total_faces - 1} other person(s) - maintaining lock")
                        self.create_blur_overlay()
                        self.screen_blurred = True
                elif not face_detected:
                    # No face detected - update timer but don't unlock yet
                    self.last_face_time = current_time
                elif face_detected and not owner_detected:
                    # Only unauthorized faces detected
                    if not self.screen_blurred and (current_time - self.last_face_time > self.grace_period):
                        print(f"Only unauthorized person(s) detected ({total_faces} faces) - locking screen")
                        self.create_blur_overlay()
                        self.screen_blurred = True
                
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
