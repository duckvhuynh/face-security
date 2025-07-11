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

class FaceSecuritySystem:
    def __init__(self):
        self.owner_face_encodings = []
        self.owner_name = "Owner"
        self.config_file = "face_security_config.pkl"
        self.key_file = "security.key"
        self.is_monitoring = False
        self.screen_blurred = False
        self.camera = None
        self.blur_window = None
        self.blur_thread = None
        self.face_detection_interval = 1.0  # Check every 1 second
        self.last_face_time = time.time()
        self.grace_period = 3  # 3 seconds grace period before blurring
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
            
            cv2.imshow('Owner Registration', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord(' '):  # Space to capture
                if len(current_encodings) == 1:
                    face_encodings.append(current_encodings[0])
                    print(f"Face captured! Total samples: {len(face_encodings)}")
                    
                    if len(face_encodings) >= 5:  # Collect 5 samples
                        break
                else:
                    print("Please ensure exactly one face is visible")
            elif key == 27:  # ESC to cancel
                cap.release()
                cv2.destroyAllWindows()
                return False
        
        cap.release()
        cv2.destroyAllWindows()
        
        if len(face_encodings) >= 5:
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
        """Detect and recognize faces in frame"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        owner_detected = False
        unauthorized_face_detected = False
        total_faces = len(face_locations)
        recognized_faces = 0
        
        for face_encoding in face_encodings:
            # Compare with owner's face encodings
            matches = face_recognition.compare_faces(self.owner_face_encodings, face_encoding, tolerance=0.6)
            
            if True in matches:
                owner_detected = True
                recognized_faces += 1
            else:
                # This face is not the owner - unauthorized
                unauthorized_face_detected = True
        
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
        
        # Create blur effect
        blur_label = tk.Label(self.blur_window, 
                             text="UNAUTHORIZED ACCESS DETECTED\n\nScreen Locked for Security\n\nPress Ctrl+Alt+O to unlock", 
                             fg='red', bg='black', 
                             font=('Arial', 24, 'bold'))
        blur_label.pack(expand=True)
        
        # Bind unlock hotkey
        keyboard.add_hotkey('ctrl+alt+o', self.request_unlock)
    
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
        print("Starting face monitoring...")
        self.camera = cv2.VideoCapture(0)
        
        if not self.camera.isOpened():
            print("Error: Could not open camera")
            return
        
        while self.is_monitoring:
            ret, frame = self.camera.read()
            if not ret:
                print("Error: Could not read frame")
                break
            
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
                
                # Optional: Display monitoring window (comment out for stealth mode)
                if not self.screen_blurred:
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
                    cv2.imshow('Face Security Monitor', frame)
                
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
