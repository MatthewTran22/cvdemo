#!/usr/bin/env python3
"""
Simple camera test with GUI - no WebSocket communication
Just shows the webcam feed to verify everything is working
"""

import cv2
import time
import numpy as np

def main():
    """Simple camera test with GUI"""
    print("🎥 Starting Simple Camera Test")
    print("Controls:")
    print("  Q - Quit")
    print("  S - Save current frame")
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Failed to open camera 0")
        return
    
    # Set camera properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 10)  # Lower FPS for testing
    
    print("✅ Camera initialized successfully")
    print("📹 Starting video feed...")
    
    frame_count = 0
    start_time = time.time()
    
    try:
        while True:
            # Capture frame
            ret, frame = cap.read()
            if not ret:
                print("❌ Failed to capture frame")
                break
            
            frame_count += 1
            
            # Calculate FPS
            elapsed_time = time.time() - start_time
            fps = frame_count / elapsed_time if elapsed_time > 0 else 0
            
            # Add text overlay
            cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Frame: {frame_count}", (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, "Press Q to quit, S to save", (10, 110), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Display frame
            cv2.imshow("Simple Camera Test", frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("👋 Quit key pressed")
                break
            elif key == ord('s'):
                filename = f"frame_{frame_count}.jpg"
                cv2.imwrite(filename, frame)
                print(f"💾 Saved frame as {filename}")
            
            # Limit FPS
            time.sleep(0.1)  # 10 FPS
            
    except KeyboardInterrupt:
        print("👋 Interrupted by user")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("🎉 Camera test completed")

if __name__ == "__main__":
    main()
