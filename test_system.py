"""
Quick Test Script for Face Security System
Tests all components without requiring full registration
"""

import sys
import os

def test_imports():
    """Test all required imports"""
    print("=== Testing Imports ===")
    
    try:
        import cv2
        print("✅ OpenCV:", cv2.__version__)
    except ImportError as e:
        print("❌ OpenCV:", e)
        return False
    
    try:
        import mediapipe as mp
        print("✅ MediaPipe imported successfully")
    except ImportError as e:
        print("❌ MediaPipe:", e)
        return False
    
    try:
        import numpy as np
        print("✅ NumPy:", np.__version__)
    except ImportError as e:
        print("❌ NumPy:", e)
        return False
    
    try:
        import tkinter as tk
        print("✅ Tkinter available")
    except ImportError as e:
        print("❌ Tkinter:", e)
        return False
    
    try:
        from cryptography.fernet import Fernet
        print("✅ Cryptography available")
    except ImportError as e:
        print("❌ Cryptography:", e)
        return False
    
    try:
        import keyboard
        print("✅ Keyboard library available")
    except ImportError as e:
        print("❌ Keyboard:", e)
        return False
    
    try:
        from sklearn.metrics.pairwise import cosine_similarity
        print("✅ Scikit-learn available")
    except ImportError as e:
        print("❌ Scikit-learn:", e)
        return False
    
    return True

def test_config():
    """Test configuration loading"""
    print("\\n=== Testing Configuration ===")
    
    try:
        from config_loader import config
        print("✅ Configuration loaded successfully")
        print(f"   Grace period: {config.grace_period} seconds")
        print(f"   Detection confidence: {config.detection_confidence}")
        print(f"   Camera index: {config.camera_index}")
        return True
    except ImportError as e:
        print("❌ Configuration loader:", e)
        return False

def test_camera():
    """Test camera access"""
    print("\\n=== Testing Camera ===")
    
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print("✅ Camera working - Frame size:", frame.shape)
                cap.release()
                return True
            else:
                print("❌ Camera opened but cannot read frames")
                cap.release()
                return False
        else:
            print("❌ Cannot open camera (may be in use by another app)")
            return False
    except Exception as e:
        print("❌ Camera test failed:", e)
        return False

def test_mediapipe():
    """Test MediaPipe face detection"""
    print("\\n=== Testing MediaPipe ===")
    
    try:
        import mediapipe as mp
        import cv2
        
        mp_face_detection = mp.solutions.face_detection
        face_detection = mp_face_detection.FaceDetection(
            model_selection=1, min_detection_confidence=0.7)
        
        print("✅ MediaPipe face detection initialized")
        
        # Test with a simple image (create a dummy test)
        import numpy as np
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        rgb_image = cv2.cvtColor(test_image, cv2.COLOR_BGR2RGB)
        results = face_detection.process(rgb_image)
        
        print("✅ MediaPipe processing test successful")
        return True
        
    except Exception as e:
        print("❌ MediaPipe test failed:", e)
        return False

def test_system_initialization():
    """Test system class initialization"""
    print("\\n=== Testing System Initialization ===")
    
    try:
        from mediapipe_face_security import MediaPipeFaceSecuritySystem
        system = MediaPipeFaceSecuritySystem()
        print("✅ MediaPipe security system initialized")
        
        # Test encryption setup
        if os.path.exists(system.key_file):
            print("✅ Encryption key file created")
        
        return True
    except Exception as e:
        print("❌ System initialization failed:", e)
        return False

def test_launcher():
    """Test launcher components"""
    print("\\n=== Testing Launcher ===")
    
    try:
        from launcher import FaceSecurityLauncher
        print("✅ Launcher imports successful")
        return True
    except Exception as e:
        print("❌ Launcher test failed:", e)
        return False

def main():
    """Main test function"""
    print("🔒 Face Security System - Component Test")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Configuration Test", test_config),
        ("Camera Test", test_camera),
        ("MediaPipe Test", test_mediapipe),
        ("System Initialization Test", test_system_initialization),
        ("Launcher Test", test_launcher)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
    
    print("\\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your system is ready to use.")
        print("\\nNext steps:")
        print("1. Run 'python launcher.py' to start the GUI")
        print("2. Or run 'start.bat' for automatic startup")
        print("3. Register as owner first, then start monitoring")
    else:
        print("⚠️  Some tests failed. Please install missing dependencies:")
        print("pip install -r requirements.txt")
    
    input("\\nPress Enter to exit...")

if __name__ == "__main__":
    main()
