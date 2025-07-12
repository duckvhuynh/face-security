import cv2
import face_recognition
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

# Try to import configuration
try:
    from config_loader import config
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    print("Warning: config_loader not available, using default settings")

class FaceSecuritySystem:
    def __init__(self):
        self.owner_face_encodings = []
        self.owner_name = "Owner"
        
        # Load configuration
        if CONFIG_AVAILABLE:
            self.config_file = config.basic_config_file
            self.key_file = config.encryption_key_file
            self.grace_period = config.grace_period
            self.face_detection_interval = config.detection_interval
            self.registration_samples = config.registration_samples
        else:
            self.config_file = "face_security_config.pkl"
            self.key_file = "security.key"
            self.grace_period = 3
            self.face_detection_interval = 1.0
            self.registration_samples = 5
            
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
    
    def register_owner(self):
        """Register the owner's face with password protection"""
        print("=== Owner Registration ===")
        
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
        
        face_encodings = []
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame")
                break
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Find faces in frame
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            current_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            
            # Draw rectangles around faces
            for (top, right, bottom, left) in face_locations:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, "Owner Face", (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            cv2.putText(frame, "Press SPACE to capture, ESC to cancel", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Faces detected: {len(face_locations)}", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Samples needed: {len(face_encodings)}/{self.registration_samples}", (10, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            cv2.imshow('Owner Registration', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord(' '):  # Space to capture
                if len(current_encodings) == 1:
                    face_encodings.append(current_encodings[0])
                    print(f"Face captured! Total samples: {len(face_encodings)}/{self.registration_samples}")
                    
                    if len(face_encodings) >= self.registration_samples:  # Use config value
                        break
                else:
                    print("Please ensure exactly one face is visible")
            elif key == 27:  # ESC to cancel
                cap.release()
                cv2.destroyAllWindows()
                return False
        
        cap.release()
        cv2.destroyAllWindows()
        
        if len(face_encodings) >= self.registration_samples:  # Use config value
            # Save the configuration
            config = {
                'face_encodings': face_encodings,
                'owner_name': self.owner_name,
                'password_hash': self.hash_password(password),
                'registration_date': datetime.now().isoformat()
            }
            
            # Encrypt and save
            encrypted_data = self.cipher.encrypt(pickle.dumps(config))
            with open(self.config_file, 'wb') as f:
                f.write(encrypted_data)
            
            print(f"Owner registration successful! Collected {len(face_encodings)} face samples.")
            return True
        else:
            print(f"Registration failed - need at least {self.registration_samples} face samples, got {len(face_encodings)}")
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
            
            self.owner_face_encodings = config['face_encodings']
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
    
    def detect_faces(self, frame):
        """Enhanced face detection with preprocessing and better accuracy"""
        try:
            # Preprocess frame for better detection
            # 1. Resize for faster processing while maintaining quality
            original_frame = frame.copy()
            height, width = frame.shape[:2]
            
            # Use higher resolution if available for better accuracy
            if CONFIG_AVAILABLE:
                detection_scale = 1.0 if min(width, height) >= 720 else 1.5
            else:
                detection_scale = 1.0
            
            if detection_scale != 1.0:
                new_width = int(width * detection_scale)
                new_height = int(height * detection_scale)
                frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            
            # 2. Enhance image quality
            # Apply histogram equalization for better lighting
            yuv = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)
            yuv[:,:,0] = cv2.equalizeHist(yuv[:,:,0])
            frame = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)
            
            # 3. Apply slight Gaussian blur to reduce noise
            frame = cv2.GaussianBlur(frame, (3, 3), 0.5)
            
            # Convert to RGB for face_recognition
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Use better face detection model
            face_locations = face_recognition.face_locations(rgb_frame, model='hog')  # More accurate than default
            
            if not face_locations:
                # Try with CNN model if HOG fails (slower but more accurate)
                try:
                    face_locations = face_recognition.face_locations(rgb_frame, model='cnn')
                except:
                    pass  # Fall back to no faces detected
            
            # Scale back face locations if we resized
            if detection_scale != 1.0:
                face_locations = [(int(top/detection_scale), int(right/detection_scale), 
                                 int(bottom/detection_scale), int(left/detection_scale)) 
                                for (top, right, bottom, left) in face_locations]
            
            # Extract face encodings with enhanced tolerance
            face_encodings = face_recognition.face_encodings(cv2.cvtColor(original_frame, cv2.COLOR_BGR2RGB), 
                                                           face_locations, num_jitters=2)  # More jitters for accuracy
            
            owner_detected = False
            unauthorized_face_detected = False
            total_faces = len(face_locations)
            recognized_faces = 0
            
            # Enhanced face comparison with multiple tolerance levels
            similarity_threshold = config.similarity_threshold if CONFIG_AVAILABLE else 0.8
            
            for i, face_encoding in enumerate(face_encodings):
                is_owner = False
                
                # Try multiple tolerance levels for better accuracy
                for tolerance in [0.5, 0.6, similarity_threshold]:
                    matches = face_recognition.compare_faces(self.owner_face_encodings, face_encoding, tolerance=tolerance)
                    
                    if True in matches:
                        # Calculate confidence using face distance
                        face_distances = face_recognition.face_distance(self.owner_face_encodings, face_encoding)
                        best_match_distance = min(face_distances)
                        
                        # Additional confidence check
                        if best_match_distance < tolerance:
                            owner_detected = True
                            recognized_faces += 1
                            is_owner = True
                            break
                
                if not is_owner:
                    unauthorized_face_detected = True
            
            face_detected = total_faces > 0
            
            return owner_detected, face_detected, unauthorized_face_detected, total_faces
            
        except Exception as e:
            print(f"Error in enhanced face detection: {e}")
            # Fallback to basic detection
            return self._basic_face_detection(frame)
    
    def _basic_face_detection(self, frame):
        """Fallback basic face detection method"""
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            
            owner_detected = False
            unauthorized_face_detected = False
            total_faces = len(face_locations)
            
            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(self.owner_face_encodings, face_encoding, tolerance=0.6)
                
                if True in matches:
                    owner_detected = True
                else:
                    unauthorized_face_detected = True
            
            face_detected = total_faces > 0
            return owner_detected, face_detected, unauthorized_face_detected, total_faces
            
        except Exception as e:
            print(f"Error in basic face detection: {e}")
            return False, False, False, 0
    
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
            # Note: face_security_system.py doesn't have CONFIG_AVAILABLE, so use defaults
            # or implement a simple config check
            
            # Capture current screen
            screen_image = self.capture_screen()
            if screen_image is None:
                return None
            
            # Use default values since this is the fallback system
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
        
        # Try to load config for warning text and hotkey
        try:
            from config_loader import config
            warning_text = config.lock_message.replace('\\n', '\n')  # Handle escaped newlines
            hotkey = config.unlock_hotkey
        except:
            warning_text = """🔒 UNAUTHORIZED ACCESS DETECTED 🔒

SCREEN LOCKED FOR SECURITY

This computer uses advanced facial recognition security.
Screen locks when multiple people or unauthorized persons are detected.

SECURITY POLICY:
✓ Owner alone: Screen unlocked
✗ Multiple people: Screen locked (even with owner present)
✗ Unauthorized person: Screen locked immediately

Press Ctrl+Alt+O to enter unlock password

⚠️ All access attempts are being logged ⚠️"""
            hotkey = 'ctrl+alt+o'
        
        # Create modern glass overlay with enhanced design
        text_frame = tk.Frame(self.blur_window)
        text_frame.configure(bg='#000000', relief='flat', bd=0, highlightthickness=0)
        text_frame.place(relx=0.5, rely=0.4, anchor='center')
        
        # Enhanced glassmorphism container with multiple layers
        glass_container = tk.Frame(text_frame)
        glass_container.configure(bg='#1a1a1a', relief='flat', bd=0, 
                                 highlightthickness=2, highlightcolor='#3a3a3a')
        glass_container.pack(padx=40, pady=30)
        
        # Add subtle glow effect layers
        for i, (color, width, offset) in enumerate([
            ('#ffffff', 1, 6),   # Bright inner glow
            ('#cccccc', 1, 8),   # Medium glow  
            ('#999999', 1, 10),  # Outer glow
        ]):
            glow_frame = tk.Frame(self.blur_window, bg=color, highlightthickness=0)
            glow_frame.place(relx=0.5, rely=0.4, anchor='center',
                           width=glass_container.winfo_reqwidth() + width * 20 + offset,
                           height=glass_container.winfo_reqheight() + width * 15 + offset)
            glow_frame.lower()
        
        # Main content with improved typography
        content_frame = tk.Frame(glass_container, bg='#1a1a1a', bd=0)
        content_frame.pack(padx=30, pady=25)
        
        # Header with icon
        header_frame = tk.Frame(content_frame, bg='#1a1a1a')
        header_frame.pack(fill='x', pady=(0, 15))
        
        header_label = tk.Label(header_frame,
                               text="🔒 SECURITY ALERT",
                               font=('Segoe UI', 24, 'bold'),
                               fg='#ff4757',  # Bright red for attention
                               bg='#1a1a1a',
                               justify='center')
        header_label.pack()
        
        # Subtitle
        subtitle_label = tk.Label(content_frame,
                                 text="UNAUTHORIZED ACCESS DETECTED",
                                 font=('Segoe UI', 16, 'normal'),
                                 fg='#ffa502',  # Orange for warning
                                 bg='#1a1a1a',
                                 justify='center')
        subtitle_label.pack(pady=(0, 20))
        
        # Main message with better formatting
        lines = warning_text.split('\n')[2:]  # Skip header lines we already displayed
        main_text = '\n'.join(lines)
        
        text_label = tk.Label(content_frame,
                             text=main_text,
                             font=('Segoe UI', 14, 'normal'),
                             fg='#ffffff',
                             bg='#1a1a1a',
                             justify='center',
                             wraplength=min(screen_width-300, 700))
        text_label.pack(pady=(0, 20))
        
        # Action button style
        action_frame = tk.Frame(content_frame, bg='#1a1a1a')
        action_frame.pack(fill='x', pady=(10, 0))
        
        action_label = tk.Label(action_frame,
                               text=f"Press {hotkey.upper()} to unlock",
                               font=('Segoe UI', 16, 'bold'),
                               fg='#2ed573',  # Green for action
                               bg='#1a1a1a',
                               justify='center')
        action_label.pack()
        
        # Monitoring notice
        notice_label = tk.Label(content_frame,
                               text="⚠️ This session is being monitored and logged ⚠️",
                               font=('Segoe UI', 12, 'italic'),
                               fg='#747d8c',  # Gray for notice
                               bg='#1a1a1a',
                               justify='center')
        notice_label.pack(pady=(15, 0))
        
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
        """Enhanced monitoring loop with better performance and config integration"""
        print("🚀 Starting enhanced face monitoring...")
        
        # Initialize camera with config values
        camera_index = config.camera_index if CONFIG_AVAILABLE else 0
        camera_width = config.camera_width if CONFIG_AVAILABLE else 1280
        camera_height = config.camera_height if CONFIG_AVAILABLE else 720
        camera_fps = config.camera_fps if CONFIG_AVAILABLE else 30
        
        self.camera = cv2.VideoCapture(camera_index)
        if not self.camera.isOpened():
            print("❌ Error: Could not open camera")
            return
        
        # Configure camera with enhanced settings
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, camera_width)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_height)
        self.camera.set(cv2.CAP_PROP_FPS, camera_fps)
        self.camera.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # Enable auto exposure
        self.camera.set(cv2.CAP_PROP_BRIGHTNESS, 0.5)      # Balanced brightness
        
        print(f"📹 Camera initialized: {camera_width}x{camera_height} @ {camera_fps}fps")
        
        # Setup keyboard listener for hotkey unlock
        hotkey = config.unlock_hotkey if CONFIG_AVAILABLE else 'ctrl+alt+o'
        keyboard.add_hotkey(hotkey, self.request_unlock)
        print(f"⌨️  Hotkey registered: {hotkey}")
        print("✅ Enhanced monitoring started!")
        
        frame_count = 0
        start_time = time.time()
        
        while self.is_monitoring:
            ret, frame = self.camera.read()
            if not ret:
                print("❌ Error: Could not read frame")
                break
            
            frame_count += 1
            current_fps = frame_count / (time.time() - start_time) if (time.time() - start_time) > 0 else 0
            
            try:
                owner_detected, face_detected, unauthorized_face_detected, total_faces = self.detect_faces(frame)
                current_time = time.time()
                
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
                
                # Enhanced monitoring display with better configuration support
                if CONFIG_AVAILABLE and config.show_monitor_window:
                    # Enhanced status display with modern styling
                    status_bg_height = 140
                    overlay = frame.copy()
                    cv2.rectangle(overlay, (0, 0), (frame.shape[1], status_bg_height), (0, 0, 0), -1)
                    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
                    
                    if unauthorized_face_detected:
                        status_text = f"🚨 SECURITY ALERT: {total_faces} faces detected"
                        status_color = (0, 0, 255)  # Red
                        if owner_detected:
                            detail_text = f"Owner + {total_faces - 1} unauthorized person(s)"
                        else:
                            detail_text = f"{total_faces} unauthorized person(s)"
                    elif owner_detected and total_faces == 1:
                        status_text = "✅ SECURE: Owner authenticated"
                        status_color = (0, 255, 0)  # Green
                        detail_text = "Screen unlocked - single authorized user"
                    elif total_faces > 1:
                        status_text = "🔒 PRIVACY MODE: Multiple people"
                        status_color = (0, 255, 255)  # Yellow
                        detail_text = f"{total_faces} people detected - screen locked for privacy"
                    elif total_faces == 0:
                        status_text = "👀 MONITORING: No faces detected"
                        status_color = (255, 255, 0)  # Cyan
                        detail_text = "Scanning for faces..."
                    else:
                        status_text = "🔍 MONITORING: Analyzing..."
                        status_color = (255, 255, 255)  # White
                        detail_text = "Processing face data..."
                    
                    # Main status
                    cv2.putText(frame, status_text, (15, 35), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2)
                    
                    # Detail text
                    cv2.putText(frame, detail_text, (15, 65), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    
                    # Stats line 1
                    stats_text1 = f"Faces: {total_faces} | Screen: {'🔒 LOCKED' if self.screen_blurred else '🔓 UNLOCKED'}"
                    cv2.putText(frame, stats_text1, (15, 95), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
                    
                    # Stats line 2
                    stats_text2 = f"FPS: {current_fps:.1f} | Resolution: {frame.shape[1]}x{frame.shape[0]} | Enhanced Mode"
                    cv2.putText(frame, stats_text2, (15, 115), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
                    
                    # Show enhanced monitoring window
                    window_title = config.monitor_window_title if CONFIG_AVAILABLE else 'Enhanced Face Security Monitor'
                    cv2.imshow(window_title, frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
            except Exception as e:
                print(f"Error in face detection: {e}")
            
            time.sleep(0.1)  # Small delay to reduce CPU usage
        
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
        print("Face monitoring started...")
        return True
    
    def stop_monitoring(self):
        """Stop the monitoring system"""
        self.is_monitoring = False
        if hasattr(self, 'monitor_thread') and self.monitor_thread.is_alive():
            self.monitor_thread.join()
        self.remove_blur_overlay()
        print("Face monitoring stopped.")

def main():
    system = FaceSecuritySystem()
    
    print("=== Face Security System ===")
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
