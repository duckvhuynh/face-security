#!/usr/bin/env python3
"""
Complete System Demonstration
============================

This script demonstrates the complete facial recognition security system
with all enhanced features:

1. Multi-person detection (locks when owner + others present)
2. Modern blur screen with glassmorphism design
3. Higher camera resolution (1280x720)
4. Complete configuration loading
5. Elegant visual effects

Usage:
    python demo_complete_system.py
"""

import sys
import os
import time
import threading

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("=" * 80)
    print("🎨 COMPLETE FACIAL RECOGNITION SECURITY SYSTEM DEMO")
    print("=" * 80)
    print(__doc__)
    
    print("🔧 FEATURES INCLUDED:")
    print("  ✅ Multi-person detection (locks when owner + others present)")
    print("  ✅ Modern blur screen with glassmorphism design")
    print("  ✅ Higher camera resolution (1280x720)")
    print("  ✅ Complete configuration loading")
    print("  ✅ Elegant visual effects")
    print("  ✅ AI-powered facial recognition")
    
    # Load configuration
    try:
        from config_loader import config
        print(f"\n📋 CONFIGURATION LOADED:")
        print(f"  🎥 Camera: {config.camera_width}x{config.camera_height}")
        print(f"  🌟 Blur: {'Enabled' if config.enable_screen_blur else 'Disabled'}")
        print(f"  🎛️  Intensity: {config.blur_intensity}")
        print(f"  🔓 Unlock: {config.unlock_hotkey}")
        print(f"  ⏰ Lock delay: {config.lock_delay_seconds}s")
        print(f"  📱 Message lines: {len(config.lock_message.replace('\\n', '\n').split(chr(10)))}")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return
    
    # Try to load the system
    try:
        # Try MediaPipe first
        try:
            from mediapipe_face_security import MediaPipeFaceSecuritySystem
            system = MediaPipeFaceSecuritySystem()
            system_name = "MediaPipe AI System"
            print(f"\n🤖 USING: {system_name}")
        except Exception as e:
            print(f"⚠️  MediaPipe unavailable: {e}")
            from face_security_system import FaceSecuritySystem
            system = FaceSecuritySystem()
            system_name = "Face Recognition System"
            print(f"\n🔍 USING: {system_name}")
        
        print(f"✅ {system_name} loaded successfully!")
        
    except Exception as e:
        print(f"❌ System loading failed: {e}")
        return
    
    print("\n" + "=" * 80)
    print("🎮 DEMO OPTIONS")
    print("=" * 80)
    print("1. 📸 Test camera and face detection")
    print("2. 🎨 Demo modern blur effect")
    print("3. 🚀 Start complete security system")
    print("4. ❌ Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == "1":
                print("\n📸 TESTING CAMERA AND FACE DETECTION")
                print("=" * 50)
                
                import cv2
                cap = cv2.VideoCapture(0)
                if not cap.isOpened():
                    print("❌ Cannot open camera")
                    continue
                
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.camera_width)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.camera_height)
                
                print("📹 Camera opened. Press 'q' to quit, 's' to save frame")
                print("🔍 Face detection running...")
                
                frame_count = 0
                start_time = time.time()
                
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    frame_count += 1
                    
                    # Detect faces
                    faces = system.detect_faces(frame)
                    
                    # Draw face boxes
                    for face in faces:
                        if hasattr(face, 'bbox'):  # MediaPipe format
                            x, y, w, h = face.bbox
                        else:  # face_recognition format
                            y, x, h, w = face
                            w = x - w
                            h = h - y
                        
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    
                    # Show FPS and face count
                    fps = frame_count / (time.time() - start_time)
                    cv2.putText(frame, f"FPS: {fps:.1f} | Faces: {len(faces)}", 
                               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    cv2.imshow('Face Detection Test', frame)
                    
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        break
                    elif key == ord('s'):
                        cv2.imwrite(f'face_test_{frame_count}.jpg', frame)
                        print(f"📸 Saved frame {frame_count}")
                
                cap.release()
                cv2.destroyAllWindows()
                print("✅ Camera test completed")
                
            elif choice == "2":
                print("\n🎨 DEMO MODERN BLUR EFFECT")
                print("=" * 50)
                
                print("🌟 Creating modern blur overlay...")
                system.create_blur_overlay()
                print("✨ Modern blur effect active!")
                print("🎭 You should see a sleek, glassmorphism-style blur screen")
                
                print("⏰ Displaying for 10 seconds...")
                time.sleep(10)
                
                system.remove_blur_overlay()
                print("✅ Blur overlay removed")
                
            elif choice == "3":
                print("\n🚀 STARTING COMPLETE SECURITY SYSTEM")
                print("=" * 50)
                print("🔒 Security system will:")
                print("  • Monitor for faces continuously")
                print("  • Learn owner's face when alone")
                print("  • Lock screen when strangers or multiple people detected")
                print("  • Use modern blur effect when locked")
                print(f"  • Unlock with hotkey: {config.unlock_hotkey}")
                print("\n⚠️  Press Ctrl+C to stop the system")
                
                try:
                    system.start()
                except KeyboardInterrupt:
                    print("\n\n🛑 Security system stopped by user")
                    system.stop()
                except Exception as e:
                    print(f"\n❌ System error: {e}")
                    system.stop()
                
            elif choice == "4":
                print("\n👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please enter 1-4.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Demo interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Demo error: {e}")
            break
    
    print("\n" + "=" * 80)
    print("🎨 DEMO COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    main()
