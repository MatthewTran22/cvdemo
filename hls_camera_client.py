#!/usr/bin/env python3
"""
HLS Camera Client for MentraOS
Reads HLS streams directly for smooth video playback
"""

import cv2
import numpy as np
import asyncio
import aiohttp
import json
import time
from typing import Optional
from loguru import logger

class HLSCameraClient:
    """HLS Camera Client for smooth video streaming"""
    
    def __init__(self, sse_url: str = "http://localhost:3002/stream"):
        self.sse_url = sse_url
        self.is_running = False
        self.current_frame: Optional[np.ndarray] = None
        self.frame_count = 0
        self.last_frame_time = time.time()
        self.fps = 0
        self.sse_task: Optional[asyncio.Task] = None
        self.hls_url: Optional[str] = None
        self.cap: Optional[cv2.VideoCapture] = None
        
        # GUI setup
        self.window_name = "MentraOS HLS Stream"
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, 640, 480)
        
    async def start(self):
        """Start the HLS camera client"""
        logger.info("🎥 Starting HLS Camera Client...")
        logger.info(f"📡 Connecting to: {self.sse_url}")
        logger.info("Controls:")
        logger.info("  Q - Quit")
        logger.info("  S - Save current frame")
        
        self.is_running = True
        
        # Start SSE connection to get HLS URL
        self.sse_task = asyncio.create_task(self._connect_to_sse())
        
        # Start GUI loop
        await self._gui_loop()
        
    async def _connect_to_sse(self):
        """Connect to SSE server to get HLS stream URL"""
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
        
        if event_type == 'managed_stream_url':
            # Got HLS stream URL - start reading it
            stream_url = data.get('streamUrl')
            if stream_url:
                logger.info(f"🎥 Received HLS stream URL: {stream_url}")
                await self._start_hls_stream(stream_url)
                
        elif event_type == 'connection_established':
            logger.info("✅ SSE connection established")
            
        elif event_type == 'start_streaming':
            logger.info("🎬 Streaming started")
            
        elif event_type == 'stop_streaming':
            logger.info("🛑 Streaming stopped")
            await self._stop_hls_stream()
    
    async def _start_hls_stream(self, stream_url: str):
        """Start reading HLS stream"""
        try:
            # Stop any existing stream
            await self._stop_hls_stream()
            
            # Start new HLS stream
            self.hls_url = stream_url
            self.cap = cv2.VideoCapture(stream_url)
            
            if not self.cap.isOpened():
                logger.error(f"Failed to open HLS stream: {stream_url}")
                return
                
            logger.info(f"✅ HLS stream opened: {stream_url}")
            
        except Exception as e:
            logger.error(f"Error starting HLS stream: {e}")
    
    async def _stop_hls_stream(self):
        """Stop HLS stream"""
        if self.cap:
            self.cap.release()
            self.cap = None
            self.hls_url = None
            logger.info("🛑 HLS stream stopped")
    
    async def _gui_loop(self):
        """Main GUI loop for displaying video"""
        while self.is_running:
            try:
                # Read frame from HLS stream
                if self.cap and self.cap.isOpened():
                    ret, frame = self.cap.read()
                    if ret:
                        # Apply rotation if needed (180 degrees)
                        rotated_frame = cv2.rotate(frame, cv2.ROTATE_180)
                        self.current_frame = rotated_frame
                        self.frame_count += 1
                        
                        # Calculate FPS
                        current_time = time.time()
                        if current_time - self.last_frame_time > 0:
                            self.fps = 1.0 / (current_time - self.last_frame_time)
                        self.last_frame_time = current_time
                        
                        # Display frame
                        display_frame = self.current_frame.copy()
                        
                        # Add info overlay
                        info_text = f"FPS: {self.fps:.1f} | Frames: {self.frame_count}"
                        cv2.putText(display_frame, info_text, (10, 30), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        
                        cv2.imshow(self.window_name, display_frame)
                    else:
                        # No frame available, show waiting screen
                        await self._show_waiting_screen()
                else:
                    # No HLS stream, show waiting screen
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
                
                # Small delay to prevent high CPU usage
                await asyncio.sleep(0.01)
                
            except Exception as e:
                logger.error(f"Error in GUI loop: {e}")
                await asyncio.sleep(0.1)
        
        # Cleanup
        await self._stop_hls_stream()
        cv2.destroyAllWindows()
        self.is_running = False
    
    async def _show_waiting_screen(self):
        """Show waiting screen when no stream is available"""
        # Create a simple waiting screen
        waiting_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Add text
        text = "Waiting for HLS stream..."
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
        logger.info("Stopping HLS Camera Client...")
        self.is_running = False
        if self.sse_task:
            self.sse_task.cancel()
        await self._stop_hls_stream()

async def main():
    """Main function"""
    client = HLSCameraClient(sse_url="http://localhost:3002/stream")
    await client.start()

if __name__ == "__main__":
    asyncio.run(main())


