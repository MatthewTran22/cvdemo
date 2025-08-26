#!/usr/bin/env python3
"""
RTMP Server for MentraOS Camera Streaming
Receives video from Mentra glasses and serves as RTMP stream
"""

import subprocess
import signal
import sys
import time
from loguru import logger

class RTMPServer:
    def __init__(self, port=1935):
        self.port = port
        self.ffmpeg_process = None
        self.is_running = False
        
    def check_ffmpeg(self):
        """Check if FFmpeg is available"""
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                logger.success("FFmpeg is available")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        logger.error("FFmpeg is not installed or not found in PATH")
        return False
    
    def start_server(self):
        """Start RTMP server using FFmpeg"""
        if not self.check_ffmpeg():
            return False
            
        logger.info(f"Starting RTMP server on port {self.port}")
        
        # FFmpeg command to create RTMP server
        # This will listen for incoming RTMP streams and serve them
        cmd = [
            'ffmpeg',
            '-listen', '1',  # Listen for incoming connections
            '-i', f'rtmp://localhost:{self.port}/live/stream',  # Input from RTMP
            '-c', 'copy',  # Copy without re-encoding
            '-f', 'flv',  # Output format
            f'rtmp://localhost:{self.port}/live/stream'  # Output to same URL
        ]
        
        logger.info(f"Running command: {' '.join(cmd)}")
        
        try:
            self.ffmpeg_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a moment to see if it starts successfully
            time.sleep(2)
            
            if self.ffmpeg_process.poll() is None:
                self.is_running = True
                logger.success("RTMP server started successfully")
                logger.info(f"RTMP URL: rtmp://localhost:{self.port}/live/stream")
                return True
            else:
                stdout, stderr = self.ffmpeg_process.communicate()
                logger.error(f"RTMP server failed to start: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to start RTMP server: {e}")
            return False
    
    def stop_server(self):
        """Stop RTMP server"""
        logger.info("Stopping RTMP server...")
        
        if self.ffmpeg_process:
            try:
                self.ffmpeg_process.terminate()
                self.ffmpeg_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.ffmpeg_process.kill()
            except Exception as e:
                logger.error(f"Error stopping RTMP server: {e}")
        
        self.is_running = False
        logger.info("RTMP server stopped gracefully")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info("Received shutdown signal")
    if server:
        server.stop_server()
    sys.exit(0)

if __name__ == "__main__":
    # Configure logging
    logger.remove()
    logger.add(sys.stderr, level="INFO", format="{time} | {level:<8} | {name}:{function}:{line} - {message}")
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and start server
    server = RTMPServer()
    
    if server.start_server():
        logger.info("RTMP server is running. Press Ctrl+C to stop.")
        try:
            while server.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
    else:
        logger.error("Failed to start RTMP server")
        sys.exit(1)

