"""
Camera Test Script
Tests basic camera functionality and face detection
"""

import cv2
import sys

def test_camera():
    """Test basic camera functionality"""
    print("Testing camera access...")
    
    # Try to open camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Error: Could not open camera")
        print("Make sure:")
        print("- Camera is connected")
        print("- No other application is using the camera")
        print("- Camera drivers are installed")
        return False
    
    print("✅ Camera opened successfully")
    
    # Test frame capture
    ret, frame = cap.read()
    if not ret:
        print("❌ Error: Could not read frame from camera")
        cap.release()
        return False
    
    print(f"✅ Frame captured successfully - Size: {frame.shape}")
    
    # Display test window
    print("Camera test window will open...")
    print("Press 'q' to quit, 's' to save test image")
    
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to read frame")
            break
        
        frame_count += 1
        
        # Flip frame for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Add text overlay
        cv2.putText(frame, f"Camera Test - Frame {frame_count}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, "Press 'q' to quit, 's' to save", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        cv2.imshow('Camera Test', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            cv2.imwrite('test_frame.jpg', frame)
            print("✅ Test frame saved as 'test_frame.jpg'")
    
    cap.release()
    cv2.destroyAllWindows()
    print("✅ Camera test completed successfully")
    return True

def test_mediapipe():
    """Test MediaPipe face detection"""
    try:
        import mediapipe as mp
        print("Testing MediaPipe face detection...")
        
        mp_face_detection = mp.solutions.face_detection
        mp_drawing = mp.solutions.drawing_utils
        
        face_detection = mp_face_detection.FaceDetection(
            model_selection=0, min_detection_confidence=0.5)
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Camera not available for MediaPipe test")
            return False
        
        print("MediaPipe face detection test window opened...")
        print("Press 'q' to quit")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_detection.process(rgb_frame)
            
            # Convert back to BGR
            frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)
            
            # Draw face detections
            if results.detections:
                for detection in results.detections:
                    mp_drawing.draw_detection(frame, detection)
                    cv2.putText(frame, f"Faces: {len(results.detections)}", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            else:
                cv2.putText(frame, "No faces detected", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            cv2.imshow('MediaPipe Face Detection Test', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        print("✅ MediaPipe test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ MediaPipe test failed: {e}")
        return False

def main():
    """Main test function"""
    print("=== Face Security System - Camera Test ===\n")
    
    # Test basic camera
    if not test_camera():
        print("\n❌ Basic camera test failed. Please fix camera issues before proceeding.")
        input("Press Enter to exit...")
        return
    
    print("\n" + "="*50)
    
    # Test MediaPipe
    if test_mediapipe():
        print("\n✅ All tests passed! Your system is ready for face security.")
    else:
        print("\n⚠️  MediaPipe test failed, but basic camera works.")
        print("You can still use the basic face recognition system.")
    
    print("\nYou can now run 'python launcher.py' to start the Face Security System")
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
