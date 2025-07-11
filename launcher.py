"""
Face Security System Launcher
A comprehensive facial recognition security system that:
1. Registers owner faces with password protection
2. Monitors webcam continuously
3. Blurs screen when unauthorized person is detected
4. Allows password unlock

Features:
- Uses MediaPipe for fast face detection
- Secure encrypted storage of face data
- Real-time monitoring with minimal CPU usage
- Fullscreen blur overlay for security
- Hotkey unlock system (Ctrl+Alt+O)

Usage:
1. Run this script
2. Choose "Register Owner" first time
3. Start monitoring to protect your screen
"""

import sys
import tkinter as tk
from tkinter import messagebox, simpledialog
import threading
import time

# Try importing our modules
try:
    from mediapipe_face_security import MediaPipeFaceSecuritySystem
    MEDIAPIPE_AVAILABLE = True
except ImportError as e:
    print(f"MediaPipe system not available: {e}")
    MEDIAPIPE_AVAILABLE = False

try:
    from face_security_system import FaceSecuritySystem
    BASIC_AVAILABLE = True
except ImportError as e:
    print(f"Basic system not available: {e}")
    BASIC_AVAILABLE = False

class FaceSecurityLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Face Security System")
        self.root.geometry("500x400")
        self.root.configure(bg='#2c3e50')
        
        self.current_system = None
        self.monitoring_thread = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Header
        header_label = tk.Label(
            self.root, 
            text="🔒 Face Security System", 
            font=('Arial', 20, 'bold'),
            bg='#2c3e50', 
            fg='#ecf0f1'
        )
        header_label.pack(pady=20)
        
        # Description
        desc_text = """Protect your computer with facial recognition technology.
Only authorized users can access your screen."""
        desc_label = tk.Label(
            self.root, 
            text=desc_text, 
            font=('Arial', 11),
            bg='#2c3e50', 
            fg='#bdc3c7',
            justify='center'
        )
        desc_label.pack(pady=10)
        
        # System selection
        system_frame = tk.Frame(self.root, bg='#2c3e50')
        system_frame.pack(pady=20)
        
        tk.Label(
            system_frame, 
            text="Choose Recognition System:", 
            font=('Arial', 12, 'bold'),
            bg='#2c3e50', 
            fg='#ecf0f1'
        ).pack()
        
        self.system_var = tk.StringVar(value="mediapipe" if MEDIAPIPE_AVAILABLE else "basic")
        
        if MEDIAPIPE_AVAILABLE:
            tk.Radiobutton(
                system_frame, 
                text="MediaPipe (Recommended - Fast & Accurate)", 
                variable=self.system_var, 
                value="mediapipe",
                bg='#2c3e50', 
                fg='#27ae60', 
                selectcolor='#34495e',
                font=('Arial', 10)
            ).pack(anchor='w', padx=20)
        
        if BASIC_AVAILABLE:
            tk.Radiobutton(
                system_frame, 
                text="Basic Face Recognition (Slower but Compatible)", 
                variable=self.system_var, 
                value="basic",
                bg='#2c3e50', 
                fg='#f39c12', 
                selectcolor='#34495e',
                font=('Arial', 10)
            ).pack(anchor='w', padx=20)
        
        # Buttons
        button_frame = tk.Frame(self.root, bg='#2c3e50')
        button_frame.pack(pady=30)
        
        self.register_btn = tk.Button(
            button_frame, 
            text="👤 Register Owner", 
            command=self.register_owner,
            bg='#3498db', 
            fg='white', 
            font=('Arial', 12, 'bold'),
            padx=20, 
            pady=10,
            relief='flat'
        )
        self.register_btn.pack(side='left', padx=10)
        
        self.monitor_btn = tk.Button(
            button_frame, 
            text="🔍 Start Monitoring", 
            command=self.toggle_monitoring,
            bg='#27ae60', 
            fg='white', 
            font=('Arial', 12, 'bold'),
            padx=20, 
            pady=10,
            relief='flat'
        )
        self.monitor_btn.pack(side='left', padx=10)
        
        self.exit_btn = tk.Button(
            button_frame, 
            text="❌ Exit", 
            command=self.exit_app,
            bg='#e74c3c', 
            fg='white', 
            font=('Arial', 12, 'bold'),
            padx=20, 
            pady=10,
            relief='flat'
        )
        self.exit_btn.pack(side='left', padx=10)
        
        # Status
        self.status_label = tk.Label(
            self.root, 
            text="Ready to start", 
            font=('Arial', 10),
            bg='#2c3e50', 
            fg='#95a5a6'
        )
        self.status_label.pack(pady=20)
        
        # Instructions
        instructions = """Instructions:
1. First, register as owner with your face and password
2. Start monitoring to protect your screen
3. If unauthorized person detected, screen will blur
4. Press Ctrl+Alt+O to unlock with password"""
        
        tk.Label(
            self.root, 
            text=instructions, 
            font=('Arial', 9),
            bg='#2c3e50', 
            fg='#7f8c8d',
            justify='left'
        ).pack(pady=10, padx=20)
        
    def get_system(self):
        """Get the selected security system"""
        if self.system_var.get() == "mediapipe" and MEDIAPIPE_AVAILABLE:
            return MediaPipeFaceSecuritySystem()
        elif self.system_var.get() == "basic" and BASIC_AVAILABLE:
            return FaceSecuritySystem()
        else:
            messagebox.showerror("Error", "Selected system is not available!")
            return None
    
    def register_owner(self):
        """Register the owner's face"""
        try:
            self.status_label.config(text="Initializing registration...", fg='#f39c12')
            self.root.update()
            
            system = self.get_system()
            if not system:
                return
                
            self.status_label.config(text="Starting registration process...", fg='#f39c12')
            self.root.update()
            
            # Hide main window during registration
            self.root.withdraw()
            
            success = system.register_owner()
            
            # Show main window again
            self.root.deiconify()
            
            if success:
                self.status_label.config(text="Owner registered successfully!", fg='#27ae60')
                messagebox.showinfo("Success", "Owner registration completed successfully!\nYou can now start monitoring.")
            else:
                self.status_label.config(text="Registration failed", fg='#e74c3c')
                messagebox.showerror("Error", "Owner registration failed. Please try again.")
                
        except Exception as e:
            self.root.deiconify()
            self.status_label.config(text="Registration error", fg='#e74c3c')
            messagebox.showerror("Error", f"Registration failed: {str(e)}")
    
    def toggle_monitoring(self):
        """Start or stop monitoring"""
        if self.current_system is None:
            self.start_monitoring()
        else:
            self.stop_monitoring()
    
    def start_monitoring(self):
        """Start the monitoring system"""
        try:
            self.current_system = self.get_system()
            if not self.current_system:
                return
                
            self.status_label.config(text="Starting monitoring system...", fg='#f39c12')
            self.root.update()
            
            success = self.current_system.start_monitoring()
            
            if success:
                self.status_label.config(text="🟢 Monitoring ACTIVE - Screen Protected", fg='#27ae60')
                self.monitor_btn.config(text="⏹️ Stop Monitoring", bg='#e74c3c')
                self.register_btn.config(state='disabled')
                
                # Update status periodically
                self.update_monitoring_status()
            else:
                self.status_label.config(text="Failed to start monitoring", fg='#e74c3c')
                messagebox.showerror("Error", "Failed to start monitoring. Please register as owner first.")
                self.current_system = None
                
        except Exception as e:
            self.status_label.config(text="Monitoring error", fg='#e74c3c')
            messagebox.showerror("Error", f"Failed to start monitoring: {str(e)}")
            self.current_system = None
    
    def stop_monitoring(self):
        """Stop the monitoring system"""
        try:
            if self.current_system:
                self.current_system.stop_monitoring()
                self.current_system = None
                
            self.status_label.config(text="🔴 Monitoring STOPPED", fg='#e74c3c')
            self.monitor_btn.config(text="🔍 Start Monitoring", bg='#27ae60')
            self.register_btn.config(state='normal')
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop monitoring: {str(e)}")
    
    def update_monitoring_status(self):
        """Update monitoring status display"""
        if self.current_system and self.current_system.is_monitoring:
            # Update status based on system state
            if hasattr(self.current_system, 'screen_blurred') and self.current_system.screen_blurred:
                self.status_label.config(text="🚨 UNAUTHORIZED ACCESS - SCREEN LOCKED", fg='#e74c3c')
            else:
                self.status_label.config(text="🟢 Monitoring ACTIVE - Screen Protected", fg='#27ae60')
            
            # Schedule next update
            self.root.after(1000, self.update_monitoring_status)
    
    def exit_app(self):
        """Exit the application"""
        if self.current_system:
            self.stop_monitoring()
        
        self.root.quit()
    
    def run(self):
        """Run the launcher"""
        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)
        self.root.mainloop()

def main():
    """Main function"""
    print("=== Face Security System Launcher ===")
    
    if not MEDIAPIPE_AVAILABLE and not BASIC_AVAILABLE:
        print("ERROR: No face recognition systems available!")
        print("Please install required packages:")
        print("pip install opencv-python mediapipe scikit-learn")
        input("Press Enter to exit...")
        return
    
    launcher = FaceSecurityLauncher()
    launcher.run()

if __name__ == "__main__":
    main()
