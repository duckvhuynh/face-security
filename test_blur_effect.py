#!/usr/bin/env python3
"""
Screen Blur Effect Test
======================

This script tests the new enhanced screen blur functionality that captures
and blurs the actual screen content instead of showing a black overlay.

Features Tested:
1. Screen capture functionality
2. Real-time blur effect generation
3. Glassmorphism overlay design
4. Configuration-based blur settings
5. Fallback to black overlay if blur fails

Usage:
    python test_blur_effect.py

Controls:
    - Press 's' to trigger screen blur test
    - Press 'q' to quit
    - Press Ctrl+Alt+O to unlock blur overlay
"""

import sys
import os
import time
import tkinter as tk
from tkinter import messagebox

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_blur_capture():
    """Test the screen capture and blur functionality"""
    try:
        # Try MediaPipe system first
        try:
            from mediapipe_face_security import MediaPipeFaceSecuritySystem
            system = MediaPipeFaceSecuritySystem()
            print("✅ Using MediaPipe System for blur test")
        except Exception as e:
            print(f"⚠️  MediaPipe unavailable, using fallback system")
            from face_security_system import FaceSecuritySystem
            system = FaceSecuritySystem()
            print("✅ Using Face Recognition System for blur test")
        
        print("\n🔍 Testing screen capture...")
        screen_img = system.capture_screen()
        if screen_img:
            print(f"✅ Screen captured successfully: {screen_img.size}")
        else:
            print("❌ Screen capture failed")
            return False
        
        print("\n🌀 Testing blur effect generation...")
        blurred_img = system.create_blurred_background()
        if blurred_img:
            print(f"✅ Blur effect created successfully: {blurred_img.size}")
        else:
            print("❌ Blur effect generation failed")
            return False
        
        print("\n📱 Testing blur overlay window...")
        system.create_blur_overlay()
        print("✅ Blur overlay created - you should see the blurred screen!")
        print("⏰ Blur overlay will auto-close in 5 seconds...")
        
        # Wait for 5 seconds then remove overlay
        time.sleep(5)
        system.remove_blur_overlay()
        print("✅ Blur overlay removed")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during blur test: {e}")
        return False

def test_configuration():
    """Test blur configuration options"""
    try:
        from config_loader import config
        print("\n⚙️ Testing blur configuration:")
        print(f"  Blur enabled: {config.enable_screen_blur}")
        print(f"  Blur intensity: {config.blur_intensity}")
        print(f"  Quality reduction: {config.blur_quality_reduction}")
        print(f"  Overlay darkness: {config.blur_overlay_darkness}")
        return True
    except Exception as e:
        print(f"⚠️  Configuration test failed: {e}")
        return False

def interactive_test():
    """Interactive test with user controls"""
    print("\n🎮 Interactive Blur Test")
    print("Commands:")
    print("  's' - Trigger screen blur")
    print("  'c' - Test configuration")
    print("  'q' - Quit")
    
    while True:
        try:
            cmd = input("\nEnter command: ").strip().lower()
            
            if cmd == 's':
                print("\n🌀 Starting blur effect test...")
                if test_blur_capture():
                    print("✅ Blur test completed successfully!")
                else:
                    print("❌ Blur test failed!")
                    
            elif cmd == 'c':
                test_configuration()
                
            elif cmd == 'q':
                break
                
            else:
                print("❓ Unknown command. Use 's', 'c', or 'q'")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    print("=" * 60)
    print("🌀 SCREEN BLUR EFFECT TEST")
    print("=" * 60)
    print(__doc__)
    
    print("\n" + "=" * 60)
    print("TESTING ENHANCED BLUR FUNCTIONALITY")
    print("=" * 60)
    
    # Test configuration first
    config_ok = test_configuration()
    
    print(f"\n📊 SYSTEM STATUS:")
    print(f"  Configuration: {'✅ OK' if config_ok else '❌ Failed'}")
    
    # Ask user if they want to run the blur test
    print(f"\n⚠️  WARNING: This will briefly show a blur overlay on your screen!")
    response = input("Continue with blur test? (y/n): ").strip().lower()
    
    if response == 'y':
        print("\n🚀 Running automatic blur test...")
        success = test_blur_capture()
        
        if success:
            print("\n🎉 All tests passed! Blur effect is working correctly.")
            print("\n💡 You can now use the enhanced blur in your security system!")
        else:
            print("\n❌ Some tests failed. Check error messages above.")
            
        print("\n🎮 Starting interactive mode...")
        interactive_test()
    else:
        print("\n⏩ Skipping blur test. Starting interactive mode...")
        interactive_test()
    
    print("\n" + "=" * 60)
    print("🌀 BLUR EFFECT TEST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    main()
