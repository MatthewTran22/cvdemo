#!/usr/bin/env python3
"""
Direct Camera Client for MentraOS
Registers MentraOS as a virtual camera input for maximum performance
"""

import cv2
import numpy as np
import asyncio
import aiohttp
import json
import time
import subprocess
import sys
from typing import Optional
from loguru import logger

class DirectCameraClient:
    """Direct Camera Client for maximum performance"""
    
    def __init__(self, sse_url: str = "http://localhost:3002/stream"):
        self.sse_url = sse_url
        self.is_running = False
        self.current_frame: Optional[np.ndarray] = None
        self.frame_count = 0
        self.last_frame_time = time.time()
        self.fps = 0
        self.sse_task: Optional[asyncio.Task] = None
        
        # GUI setup
        self.window_name = "MentraOS Direct Camera"
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, 640, 480)
        
        # Check if we can create virtual camera
        self.can_create_virtual_camera = self._check_virtual_camera_support()
        
    def _check_virtual_camera_support(self) -> bool:
        """Check if we can create a virtual camera"""
        try:
            # Try to import v4l2loopback (Linux) or similar
            if sys.platform == "linux":
                # Check if v4l2loopback is available
                result = subprocess.run(['modinfo', 'v4l2loopback'], 
                                      capture_output=True, text=True)
                return result.returncode == 0
            elif sys.platform == "darwin":  # macOS
                # Check if we can use AVFoundation
                return True
            else:
                return False
        except Exception:
            return False
    
    async def start(self):
        """Start the direct camera client"""
        logger.info("🎥 Starting Direct Camera Client...")
        logger.info(f"📡 Connecting to: {self.sse_url}")
        logger.info(f"🖥️ Virtual camera support: {self.can_create_virtual_camera}")
        logger.info("Controls:")
        logger.info("  Q - Quit")
        logger.info("  S - Save current frame")
        logger.info("  V - Create virtual camera (if supported)")
        
        self.is_running = True
        
        # Start SSE connection
        self.sse_task = asyncio.create_task(self._connect_to_sse())
        
        # Start GUI loop
        await self._gui_loop()
        
    async def _connect_to_sse(self):
        """Connect to SSE server"""
        logger.info(f"Connecting to SSE stream: {self.sse_url}")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.sse_url) as response:
                    if response.status == 200:
                        logger.info("✅ Connected to SSE stream")
                        async for line in response.content:
                            if not self.is_running:
                                break
                            line_str = line.decode('utf-8').strip()
                            if line_str.startswith('data:'):
                                try:
                                    data_str = line_str[len('data:'):].strip()
                                    data = json.loads(data_str)
                                    await self._sse_event_handler(data)
                                except json.JSONDecodeError as e:
                                    logger.error(f"Failed to parse SSE data: {e}")
                                except Exception as e:
                                    logger.error(f"Error handling SSE message: {e}")
                    else:
                        logger.error(f"Failed to connect to SSE stream. Status: {response.status}")
        except aiohttp.ClientError as e:
            logger.error(f"Connection error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in SSE connection: {e}")
        finally:
            if self.is_running:
                logger.info("SSE connection closed. Reconnecting in 5 seconds...")
                await asyncio.sleep(5)
                self.sse_task = asyncio.create_task(self._connect_to_sse())
    
    async def _sse_event_handler(self, data: dict):
        """Handle SSE events"""
        event_type = data.get('type')
        
        if event_type == 'frame_data':
            # Got frame data - process it
            frame_data = data.get('frameData')
            if frame_data:
                await self._process_frame(frame_data)
                
        elif event_type == 'connection_established':
            logger.info("✅ SSE connection established")
            
        elif event_type == 'start_streaming':
            logger.info("🎬 Streaming started")
            
        elif event_type == 'stop_streaming':
            logger.info("🛑 Streaming stopped")
    
    async def _process_frame(self, frame_data: str):
        """Process incoming frame data"""
        try:
            # Decode base64 frame
            import base64
            frame_bytes = base64.b64decode(frame_data)
            nparr = np.frombuffer(frame_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is not None:
                # Apply rotation (180 degrees)
                rotated_frame = cv2.rotate(frame, cv2.ROTATE_180)
                self.current_frame = rotated_frame
                self.frame_count += 1
                
                # Calculate FPS
                current_time = time.time()
                if current_time - self.last_frame_time > 0:
                    self.fps = 1.0 / (current_time - self.last_frame_time)
                self.last_frame_time = current_time
                
        except Exception as e:
            logger.error(f"Error processing frame: {e}")
    
    async def _create_virtual_camera(self):
        """Create a virtual camera device"""
        if not self.can_create_virtual_camera:
            logger.warning("Virtual camera not supported on this platform")
            return False
            
        try:
            if sys.platform == "linux":
                # Create v4l2loopback device
                subprocess.run(['sudo', 'modprobe', 'v4l2loopback', 'video_nr=10'], 
                             check=True)
                logger.info("✅ Virtual camera created: /dev/video10")
                return True
            elif sys.platform == "darwin":
                # On macOS, we can use OBS Virtual Camera or similar
                logger.info("On macOS, consider using OBS Virtual Camera")
                return False
            else:
                logger.warning("Virtual camera not supported on this platform")
                return False
        except Exception as e:
            logger.error(f"Failed to create virtual camera: {e}")
            return False
    
    async def _gui_loop(self):
        """Main GUI loop"""
        while self.is_running:
            try:
                if self.current_frame is not None:
                    # Display frame
                    display_frame = self.current_frame.copy()
                    
                    # Add info overlay
                    info_text = f"FPS: {self.fps:.1f} | Frames: {self.frame_count}"
                    cv2.putText(display_frame, info_text, (10, 30), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    # Add virtual camera status
                    vcam_status = "Virtual Camera: Available" if self.can_create_virtual_camera else "Virtual Camera: Not Available"
                    cv2.putText(display_frame, vcam_status, (10, 60), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                    
                    cv2.imshow(self.window_name, display_frame)
                else:
                    # Show waiting screen
                    await self._show_waiting_screen()
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    logger.info("Quit requested")
                    break
                elif key == ord('s') and self.current_frame is not None:
                    timestamp = int(time.time())
                    filename = f"frame_{timestamp}.jpg"
                    cv2.imwrite(filename, self.current_frame)
                    logger.info(f"Saved frame: {filename}")
                elif key == ord('v'):
                    await self._create_virtual_camera()
                
                # Small delay
                await asyncio.sleep(0.01)
                
            except Exception as e:
                logger.error(f"Error in GUI loop: {e}")
                await asyncio.sleep(0.1)
        
        # Cleanup
        cv2.destroyAllWindows()
        self.is_running = False
    
    async def _show_waiting_screen(self):
        """Show waiting screen"""
        waiting_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Add text
        text = "Waiting for camera stream..."
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
        text_x = (waiting_frame.shape[1] - text_size[0]) // 2
        text_y = (waiting_frame.shape[0] + text_size[1]) // 2
        
        cv2.putText(waiting_frame, text, (text_x, text_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Add connection info
        info_text = f"SSE: {self.sse_url}"
        cv2.putText(waiting_frame, info_text, (10, waiting_frame.shape[0] - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (128, 128, 128), 1)
        
        cv2.imshow(self.window_name, waiting_frame)
    
    async def stop(self):
        """Stop the client"""
        logger.info("Stopping Direct Camera Client...")
        self.is_running = False
        if self.sse_task:
            self.sse_task.cancel()

async def main():
    """Main function"""
    client = DirectCameraClient(sse_url="http://localhost:3002/stream")
    await client.start()

if __name__ == "__main__":
    asyncio.run(main())


