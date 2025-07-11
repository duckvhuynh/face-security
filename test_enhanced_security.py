#!/usr/bin/env python3
"""
Enhanced Multi-Person Security Test
===================================

This script demonstrates the enhanced facial recognition security system
that locks the screen when multiple people are detected, even if the owner
is present.

Features Tested:
1. Owner alone → Screen unlocked ✓
2. Owner + other person → Screen locked ✗
3. Multiple unauthorized people → Screen locked ✗  
4. No faces → No change in state
5. Only unauthorized person → Screen locked ✗

Usage:
    python test_enhanced_security.py

Controls:
    - Press 'q' to quit monitoring
    - Press Ctrl+Alt+O to unlock if screen gets locked
    - Watch console for detailed security events
"""

import sys
import os
import time

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("=" * 60)
    print("🛡️  ENHANCED MULTI-PERSON SECURITY TEST")
    print("=" * 60)
    print(__doc__)
    
    print("\n" + "=" * 60)
    print("STARTING ENHANCED SECURITY SYSTEM")
    print("=" * 60)
    
    try:
        # Try MediaPipe system first
        try:
            from mediapipe_face_security import MediaPipeFaceSecuritySystem
            system = MediaPipeFaceSecuritySystem()
            print("✅ Using MediaPipe Advanced System")
        except Exception as e:
            print(f"⚠️  MediaPipe unavailable ({str(e)[:50]}...), using fallback")
            from face_security_system import FaceSecuritySystem
            system = FaceSecuritySystem()
            print("✅ Using Face Recognition Fallback System")
        
        # Check if owner is registered
        if not system.load_owner_data():
            print("\n❌ ERROR: No owner registered!")
            print("Please run 'python launcher.py' first to register an owner.")
            return
        
        print("\n✅ Owner registration found")
        print("\n🔍 SECURITY TEST SCENARIOS:")
        print("1. Show only your face → Should unlock")
        print("2. Have someone join you → Should lock (even with owner)")
        print("3. Multiple unauthorized people → Should lock")
        print("4. Only unauthorized person → Should lock")
        print("\n⚠️  IMPORTANT: Screen will LOCK when multiple faces detected!")
        print("Use Ctrl+Alt+O to unlock if needed")
        
        input("\nPress Enter to start monitoring...")
        
        # Start monitoring
        if system.start_monitoring():
            print("\n🚀 Enhanced security monitoring started!")
            print("Watch for security alerts in console...")
            print("Press Ctrl+C to stop")
            
            try:
                while system.is_monitoring:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n\n⏹️  Stopping security monitoring...")
                system.stop_monitoring()
        else:
            print("❌ Failed to start monitoring!")
    
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all dependencies are installed:")
        print("pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    print("\n" + "=" * 60)
    print("🛡️  ENHANCED SECURITY TEST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    main()
