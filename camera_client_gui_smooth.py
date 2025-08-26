#!/usr/bin/env python3
"""
Smooth GUI Camera Client Module
High frame rate camera client for smooth video playback
Handles camera capture and WebSocket communication with animal classifier
"""

import asyncio
import json
import base64
import time
import cv2
import numpy as np
import os
from typing import Optional, Callable
from dataclasses import dataclass
from pathlib import Path
import threading
from queue import Queue

import websockets
from websockets.client import connect
from loguru import logger

# Configure logging
logger.add("camera_client_gui_smooth.log", rotation="1 day", retention="7 days")

@dataclass
class DetectionResult:
    """Result from animal detection"""
    image_id: str
    detections: list
    processing_time: float
    timestamp: float

class SmoothGUICameraClient:
    """Smooth GUI camera client for high frame rate video with detection overlays"""
    
    def __init__(self, 
                 input_source: str = "http://localhost:8080/video.mjpg",
                 websocket_url: str = "ws://localhost:8765",
                 display_fps: int = 30,  # High display frame rate
                 detection_fps: int = 10,  # Lower detection frame rate
                 window_width: int = 800,
                 window_height: int = 600):
        """
        Initialize the camera client
        
        Args:
            input_source: Input source (RTMP URL or camera device ID)
            websocket_url: WebSocket server URL
            display_fps: Target display frame rate for smooth video
            detection_fps: Target detection frame rate (lower for performance)
            window_width: GUI window width
            window_height: GUI window height
        """
        self.input_source = input_source
        self.websocket_url = websocket_url
        self.display_fps = display_fps
        self.detection_fps = detection_fps
        self.window_width = window_width
        self.window_height = window_height
        
        # Camera and display
        self.cap = None
        self.is_running = False
        self.frame_count = 0
        self.start_time = time.time()
        
        # Stream configuration
        self.is_stream = "http://" in input_source.lower() or "rtmp://" in input_source.lower() or "rtmps://" in input_source.lower()
        
        # WebSocket
        self.websocket = None
        self.is_connected = False
        self.connection_retries = 0
        self.max_retries = 3
        
        # Detection results
        self.current_detections = []
        self.detection_queue = Queue(maxsize=5)  # Smaller queue for faster updates
        self.last_detection_time = 0
        self.detection_interval = 1.0 / detection_fps
        
        # Threading
        self.websocket_thread = None
        self.capture_thread = None
        
        logger.info(f"Initializing SmoothGUICameraClient - Input: {input_source}, Display FPS: {display_fps}, Detection FPS: {detection_fps}")
    
    def _initialize_camera(self) -> bool:
        """Initialize camera capture or RTMP stream with high frame rate"""
        try:
            if self.is_stream:
                # For HTTP/RTMP streams, use the URL directly
                self.cap = cv2.VideoCapture(self.input_source)
                
                # Network streams need different buffer settings
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)  # Larger buffer for network streams
                
                logger.info(f"Attempting to connect to stream: {self.input_source}")
            else:
                # For camera devices, use as integer
                camera_id = int(self.input_source)
                self.cap = cv2.VideoCapture(camera_id)
                
                # Set camera properties for high frame rate
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                self.cap.set(cv2.CAP_PROP_FPS, self.display_fps)
                
                # Additional optimizations for smooth video
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize buffer delay
            
            if not self.cap.isOpened():
                logger.error(f"Failed to open input source: {self.input_source}")
                return False
            
            # Wait a moment for stream connection to establish
            if self.is_stream:
                logger.info("Waiting for stream to connect...")
                time.sleep(2)
                
                # Try to read a test frame
                ret, test_frame = self.cap.read()
                if not ret:
                    logger.error("Failed to read from stream")
                    return False
            
            source_type = "network stream" if self.is_stream else f"camera {self.input_source}"
            logger.success(f"{source_type} initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing input source: {e}")
            return False
    
    async def _connect_websocket(self) -> bool:
        """Connect to WebSocket server with retry logic"""
        try:
            if self.websocket:
                await self.websocket.close()
            
            logger.info(f"Connecting to WebSocket server: {self.websocket_url}")
            self.websocket = await connect(self.websocket_url, ping_interval=30, ping_timeout=15)
            self.is_connected = True
            self.connection_retries = 0
            logger.success(f"Connected to WebSocket server: {self.websocket_url}")
            return True
            
        except Exception as e:
            self.connection_retries += 1
            logger.error(f"WebSocket connection failed (attempt {self.connection_retries}): {e}")
            
            if self.connection_retries < self.max_retries:
                logger.info(f"Retrying connection in 2 seconds...")
                await asyncio.sleep(2)
                return await self._connect_websocket()
            else:
                logger.error("Max connection retries reached")
                return False
    
    async def _send_detection_request(self, frame: np.ndarray) -> Optional[dict]:
        """Send detection request with optimized performance"""
        if not self.is_connected or not self.websocket:
            return None
        
        try:
            # Resize frame for faster processing (optional)
            # frame_resized = cv2.resize(frame, (320, 240))
            
            # Convert frame to base64 with lower quality for speed
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            image_data = base64.b64encode(buffer).decode('utf-8')
            
            # Create request
            request = {
                "type": "detection_request",
                "image_data": image_data,
                "image_id": f"frame_{self.frame_count}",
                "timestamp": time.time()
            }
            
            # Send with shorter timeout
            await asyncio.wait_for(
                self.websocket.send(json.dumps(request)),
                timeout=0.5
            )
            
            # Wait for response with shorter timeout
            response = await asyncio.wait_for(
                self.websocket.recv(),
                timeout=2.0
            )
            
            response_data = json.loads(response)
            if response_data.get("type") == "detection_response":
                return response_data.get("data")
            
            return None
            
        except asyncio.TimeoutError:
            logger.warning("Detection request timed out")
            return None
        except Exception as e:
            logger.error(f"Error sending detection request: {e}")
            # Try to reconnect
            await self._connect_websocket()
            return None
    
    async def _websocket_loop(self):
        """WebSocket communication loop"""
        while self.is_running:
            try:
                if not self.is_connected:
                    await self._connect_websocket()
                
                # Keep connection alive
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"WebSocket loop error: {e}")
                self.is_connected = False
                await asyncio.sleep(2)
    
    async def _detection_loop(self):
        """Separate detection loop running at lower frequency"""
        logger.info("Starting detection loop")
        
        while self.is_running:
            try:
                current_time = time.time()
                
                # Only send for detection at specified interval
                if current_time - self.last_detection_time >= self.detection_interval:
                    if self.cap and self.cap.isOpened() and self.is_connected:
                        # Capture a frame for detection
                        ret, frame = self.cap.read()
                        if ret:
                            detection_result = await self._send_detection_request(frame)
                            if detection_result:
                                self.current_detections = detection_result.get("detections", [])
                                logger.debug(f"Detection updated: {len(self.current_detections)} animals")
                    
                    self.last_detection_time = current_time
                
                # Sleep for detection interval
                await asyncio.sleep(self.detection_interval)
                
            except Exception as e:
                logger.error(f"Detection loop error: {e}")
                await asyncio.sleep(0.1)
    
    async def _capture_loop(self):
        """High-speed camera capture loop for smooth video"""
        logger.info("Starting high-speed camera capture loop")
        
        frame_interval = 1.0 / self.display_fps
        last_frame_time = time.time()
        consecutive_failures = 0
        max_failures = 10
        
        while self.is_running:
            try:
                if not self.cap or not self.cap.isOpened():
                    logger.error("Video capture device is not available")
                    break
                
                current_time = time.time()
                
                # Control frame rate precisely
                if current_time - last_frame_time >= frame_interval:
                    # Capture frame
                    ret, frame = self.cap.read()
                    if not ret:
                        consecutive_failures += 1
                        logger.warning(f"Failed to capture frame ({consecutive_failures}/{max_failures})")
                        
                        if consecutive_failures >= max_failures:
                            if self.is_stream:
                                logger.error("Too many consecutive failures, network stream may be unavailable")
                                logger.info("Make sure the HTTP stream server is running and dog.mp4 is being streamed")
                            else:
                                logger.error("Too many consecutive failures, camera may be disconnected")
                            break
                        
                        await asyncio.sleep(0.1)
                        continue
                    
                    consecutive_failures = 0  # Reset failure counter on successful read
                    self.frame_count += 1
                    
                    # Update display immediately
                    self._update_display(frame)
                    
                    last_frame_time = current_time
                
                # Small sleep to prevent CPU overload
                await asyncio.sleep(0.001)  # 1ms sleep
                
            except Exception as e:
                logger.error(f"Capture loop error: {e}")
                consecutive_failures += 1
                await asyncio.sleep(0.01)
    
    def _update_display(self, frame: np.ndarray):
        """Update the display with frame and detections"""
        try:
            # Create display frame
            display_frame = frame.copy()
            
            # Calculate FPS
            elapsed_time = time.time() - self.start_time
            fps = self.frame_count / elapsed_time if elapsed_time > 0 else 0
            
            # Add FPS and frame counter
            cv2.putText(display_frame, f"FPS: {fps:.1f}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(display_frame, f"Frame: {self.frame_count}", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Add connection status
            status_color = (0, 255, 0) if self.is_connected else (0, 0, 255)
            status_text = "Connected" if self.is_connected else "Disconnected"
            cv2.putText(display_frame, f"Status: {status_text}", (10, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
            
            # Draw detections with smooth rendering
            for detection in self.current_detections:
                bbox = detection.get("bbox", [])
                class_name = detection.get("class_name", "Unknown")
                confidence = detection.get("confidence", 0)
                
                if len(bbox) == 4:
                    x1, y1, x2, y2 = map(int, bbox)
                    
                    # Draw bounding box with thickness based on confidence
                    thickness = max(1, int(confidence * 3))
                    cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 0), thickness)
                    
                    # Draw label with background for better visibility
                    label = f"{class_name} {confidence:.2f}"
                    (label_width, label_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                    
                    # Draw background rectangle for text
                    cv2.rectangle(display_frame, (x1, y1-label_height-10), (x1+label_width, y1), (0, 255, 0), -1)
                    cv2.putText(display_frame, label, (x1, y1-5), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
            
            # Add detection count
            cv2.putText(display_frame, f"Detections: {len(self.current_detections)}", (10, 120), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Add controls info
            cv2.putText(display_frame, "Q: Quit, S: Save", (10, 150), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Add input source info
            source_text = "HTTP: dog.mp4" if self.is_stream else f"Camera: {self.input_source}"
            cv2.putText(display_frame, f"Source: {source_text}", (10, 180), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Display frame
            window_title = "Animal Detection - HTTP Stream" if self.is_stream else "Animal Detection - Camera"
            cv2.imshow(window_title, display_frame)
            
        except Exception as e:
            logger.error(f"Display update error: {e}")
    
    async def _gui_loop(self):
        """Main GUI loop"""
        logger.info("GUI window opened")
        
        try:
            while self.is_running:
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q'):
                    logger.info("Quit key pressed")
                    break
                elif key == ord('s'):
                    # Save current frame
                    if self.cap and self.cap.isOpened():
                        ret, frame = self.cap.read()
                        if ret:
                            filename = f"frame_{self.frame_count}.jpg"
                            cv2.imwrite(filename, frame)
                            logger.info(f"Saved frame as {filename}")
                
                await asyncio.sleep(0.001)  # Very short sleep for responsiveness
                
        except Exception as e:
            logger.error(f"GUI loop error: {e}")
        finally:
            logger.info("GUI window closed")
    
    async def start(self):
        """Start the camera client"""
        source_type = "network stream" if self.is_stream else "camera"
        print(f"Starting Smooth GUI client with {source_type} input...")
        print(f"Input source: {self.input_source}")
        print(f"Display FPS: {self.display_fps}")
        print(f"Detection FPS: {self.detection_fps}")
        print("Controls:")
        print("  Q - Quit")
        print("  S - Save current frame")
        print("Press Ctrl+C to stop")
        
        # Initialize camera
        if not self._initialize_camera():
            logger.error("Failed to initialize camera")
            return
        
        self.is_running = True
        
        # Start WebSocket connection
        await self._connect_websocket()
        
        # Start threads
        self.websocket_thread = asyncio.create_task(self._websocket_loop())
        self.detection_thread = asyncio.create_task(self._detection_loop())
        self.capture_thread = asyncio.create_task(self._capture_loop())
        self.gui_thread = asyncio.create_task(self._gui_loop())
        
        try:
            # Wait for completion
            await asyncio.gather(
                self.websocket_thread,
                self.detection_thread,
                self.capture_thread,
                self.gui_thread
            )
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop the camera client"""
        logger.info("Stopping camera client")
        self.is_running = False
        
        # Cancel tasks
        if self.websocket_thread:
            self.websocket_thread.cancel()
        if self.detection_thread:
            self.detection_thread.cancel()
        if self.capture_thread:
            self.capture_thread.cancel()
        if self.gui_thread:
            self.gui_thread.cancel()
        
        # Close WebSocket
        if self.websocket:
            await self.websocket.close()
        
        # Release camera
        if self.cap:
            self.cap.release()
        
        # Close windows
        cv2.destroyAllWindows()
        
        logger.info("Camera client stopped")

async def main():
    """Main function"""
    client = SmoothGUICameraClient(
        input_source=os.getenv('STREAM_URL'),  # HTTP stream URL
        websocket_url="ws://localhost:8765",
        display_fps=30,  # High display frame rate for smooth video
        detection_fps=10  # Lower detection frame rate for performance
    )
    
    await client.start()

if __name__ == "__main__":
    asyncio.run(main())
