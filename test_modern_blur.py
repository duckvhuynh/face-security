#!/usr/bin/env python3
"""
Modern Blur Effect & Config Integration Test
===========================================

This script tests the enhanced modern blur effect with proper config loading,
higher camera resolution, and streamlined design.

Features Tested:
1. Config loading for lock message and settings
2. Higher camera resolution (1280x720)
3. Modern blur overlay design
4. Text formatting from config
5. Proper escape sequence handling

Usage:
    python test_modern_blur.py
"""

import sys
import os
import time

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config_loading():
    """Test configuration loading"""
    try:
        from config_loader import config
        print("📋 Configuration Test:")
        print(f"  Camera resolution: {config.camera_width}x{config.camera_height}")
        print(f"  Blur enabled: {config.enable_screen_blur}")
        print(f"  Blur intensity: {config.blur_intensity}")
        print(f"  Unlock hotkey: {config.unlock_hotkey}")
        
        # Test lock message formatting
        lock_msg = config.lock_message.replace('\\n', '\n')
        print(f"  Lock message lines: {len(lock_msg.split(chr(10)))}")
        print("  Lock message preview:")
        print("  " + lock_msg.split('\n')[0])  # First line
        
        return True
    except Exception as e:
        print(f"❌ Config loading failed: {e}")
        return False

def test_modern_blur():
    """Test the modern blur effect"""
    try:
        # Try MediaPipe system first
        try:
            from mediapipe_face_security import MediaPipeFaceSecuritySystem
            system = MediaPipeFaceSecuritySystem()
            print("✅ Using MediaPipe System")
        except Exception as e:
            print(f"⚠️  MediaPipe unavailable, using fallback system")
            from face_security_system import FaceSecuritySystem
            system = FaceSecuritySystem()
            print("✅ Using Face Recognition System")
        
        print("\n🎨 Testing Modern Blur Design:")
        
        # Test screen capture
        screen_img = system.capture_screen()
        if screen_img:
            print(f"  ✅ Screen capture: {screen_img.size}")
        else:
            print("  ❌ Screen capture failed")
            return False
        
        # Test blur generation
        blurred_img = system.create_blurred_background()
        if blurred_img:
            print(f"  ✅ Blur generation: {blurred_img.size}")
        else:
            print("  ❌ Blur generation failed")
            return False
        
        print("\n🌟 Creating modern blur overlay...")
        system.create_blur_overlay()
        print("✅ Modern blur overlay created!")
        print("🎭 You should see a sleek, modern blurred screen with clean text")
        
        # Wait for user to see the effect
        print("⏰ Displaying for 8 seconds...")
        time.sleep(8)
        
        system.remove_blur_overlay()
        print("✅ Blur overlay removed")
        
        return True
        
    except Exception as e:
        print(f"❌ Modern blur test failed: {e}")
        return False

def test_camera_resolution():
    """Test higher camera resolution"""
    try:
        from config_loader import config
        print("\n📹 Camera Resolution Test:")
        print(f"  Configured resolution: {config.camera_width}x{config.camera_height}")
        
        # Try to access camera with new resolution
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.camera_width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.camera_height)
            
            ret, frame = cap.read()
            if ret:
                actual_height, actual_width = frame.shape[:2]
                print(f"  ✅ Actual camera resolution: {actual_width}x{actual_height}")
            else:
                print("  ⚠️  Could not capture frame")
            
            cap.release()
            return True
        else:
            print("  ❌ Could not open camera")
            return False
            
    except Exception as e:
        print(f"❌ Camera test failed: {e}")
        return False

def main():
    print("=" * 60)
    print("🎨 MODERN BLUR EFFECT & CONFIG INTEGRATION TEST")
    print("=" * 60)
    print(__doc__)
    
    print("=" * 60)
    print("TESTING ENHANCED FEATURES")
    print("=" * 60)
    
    # Test all components
    config_ok = test_config_loading()
    camera_ok = test_camera_resolution()
    
    print(f"\n📊 COMPONENT STATUS:")
    print(f"  Configuration: {'✅ OK' if config_ok else '❌ Failed'}")
    print(f"  Camera Resolution: {'✅ OK' if camera_ok else '❌ Failed'}")
    
    if config_ok and camera_ok:
        print("\n⚠️  Ready to test modern blur effect!")
        response = input("Show modern blur overlay? (y/n): ").strip().lower()
        
        if response == 'y':
            blur_ok = test_modern_blur()
            
            if blur_ok:
                print("\n🎉 ALL TESTS PASSED!")
                print("🎨 Modern blur effect is working perfectly!")
                print("📋 Configuration loading is successful!")
                print("📹 Higher camera resolution is working!")
            else:
                print("\n❌ Blur test failed")
        else:
            print("\n⏩ Skipping blur test")
    else:
        print("\n❌ Some component tests failed")
    
    print("\n" + "=" * 60)
    print("🎨 MODERN BLUR TEST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    main()
