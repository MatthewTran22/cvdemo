#!/usr/bin/env python3
"""
Simple camera test to check if webcam is accessible
"""

import cv2
import time

def test_camera():
    """Test if camera is accessible"""
    print("🔍 Testing camera access...")
    
    # Try to open camera
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Failed to open camera 0")
        
        # Try camera 1
        cap = cv2.VideoCapture(1)
        if not cap.isOpened():
            print("❌ Failed to open camera 1")
            print("🔧 Please check:")
            print("   - Camera is connected")
            print("   - Camera is not in use by another application")
            print("   - Camera permissions are granted")
            return False
        else:
            print("✅ Camera 1 opened successfully")
    else:
        print("✅ Camera 0 opened successfully")
    
    # Set camera properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 10)
    
    print("📹 Testing camera capture...")
    
    # Try to capture a few frames
    for i in range(5):
        ret, frame = cap.read()
        if ret:
            print(f"✅ Frame {i+1} captured successfully - Size: {frame.shape}")
        else:
            print(f"❌ Failed to capture frame {i+1}")
            cap.release()
            return False
        time.sleep(0.1)
    
    cap.release()
    print("🎉 Camera test completed successfully!")
    return True

if __name__ == "__main__":
    success = test_camera()
    if success:
        print("\n🚀 Camera is ready for the GUI client!")
    else:
        print("\n🔧 Please fix camera issues before running the GUI client")
