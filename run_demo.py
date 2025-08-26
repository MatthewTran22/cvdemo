#!/usr/bin/env python3
"""
Demo Runner for MentraOS Animal Classification System
Launches RTMP stream from dog.mp4, animal classifier server, and camera client GUI
in separate terminals for easy testing
"""

import subprocess
import sys
import os
import time
import threading
import signal
from pathlib import Path

class DemoRunner:
    """Manages running all components of the animal classification system"""
    
    def __init__(self):
        self.server_process = None
        self.client_process = None
        self.rtmp_process = None  # FFmpeg process for RTMP streaming
        self.running = False
        
    def print_banner(self):
        """Print the demo banner"""
        print("=" * 70)
        print("🐾 MentraOS Animal Classification Demo (RTMP Stream)")
        print("=" * 70)
        print("This will launch:")
        print("  📹 HTTP Stream Server (dog.mp4 → http://localhost:8080/video.mjpg)")
        print("  📡 Animal Classifier Server (Python backend)")
        print("  🎥 Camera Client GUI (HTTP stream input)")
        print("=" * 70)
        print("Press Ctrl+C to stop all components")
        print("=" * 70)
    
    def check_dependencies(self):
        """Check if required files exist"""
        required_files = [
            "animal_classifier.py",
            "camera_client_gui_smooth.py",
            "requirements.txt",
            "dog.mp4"
        ]
        
        missing_files = []
        for file in required_files:
            if not Path(file).exists():
                missing_files.append(file)
        
        if missing_files:
            print(f"❌ Missing required files: {', '.join(missing_files)}")
            return False
        
        print("✅ All required files found")
        return True
    
    def check_ffmpeg(self):
        """Check if FFmpeg is available"""
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("✅ FFmpeg is available")
                return True
            else:
                print("❌ FFmpeg is not working properly")
                return False
        except FileNotFoundError:
            print("❌ FFmpeg is not installed")
            print("   Please install FFmpeg and ensure it's in your PATH")
            return False
    
    def check_virtual_environment(self):
        """Check if virtual environment is activated"""
        if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            print("⚠️  Virtual environment not detected")
            print("   Please activate your virtual environment first:")
            print("   Windows: venv\\Scripts\\activate")
            print("   macOS/Linux: source venv/bin/activate")
            return False
        
        print("✅ Virtual environment detected")
        return True
    
    def start_rtmp_stream(self):
        """Start FFmpeg to create a local HTTP stream from dog.mp4"""
        print("📹 Starting local HTTP stream from dog.mp4...")
        
        try:
            # Create a simple HTTP server using FFmpeg
            # This creates an MJPEG stream that OpenCV can read directly
            cmd = [
                'ffmpeg',
                '-re',  # Read at native frame rate
                '-stream_loop', '-1',  # Loop indefinitely
                '-i', 'dog.mp4',  # Input file
                '-c:v', 'mjpeg',  # MJPEG codec for easy streaming
                '-f', 'mjpeg',  # MJPEG format
                '-listen', '1',  # Enable listening mode
                'http://localhost:8080/video.mjpg'  # HTTP stream URL
            ]
            
            self.rtmp_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            print(f"✅ HTTP stream started (PID: {self.rtmp_process.pid})")
            print("   Source: dog.mp4")
            print("   Destination: http://localhost:8080/video.mjpg")
            
            # Wait a moment for stream to start
            time.sleep(3)
            
            # Check if process is still running
            if self.rtmp_process.poll() is None:
                print("✅ HTTP stream is running")
                return True
            else:
                stdout, stderr = self.rtmp_process.communicate()
                print(f"❌ HTTP stream failed to start: {stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start HTTP stream: {e}")
            return False
    
    def start_server(self):
        """Start the animal classifier server"""
        print("🚀 Starting Animal Classifier Server...")
        
        try:
            # Start the server process
            self.server_process = subprocess.Popen([
                sys.executable, "animal_classifier.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            
            print(f"✅ Server started (PID: {self.server_process.pid})")
            
            # Wait a moment for server to start
            time.sleep(3)
            
            # Check if server is still running
            if self.server_process.poll() is None:
                print("✅ Server is running and ready")
                return True
            else:
                print("❌ Server failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            return False
    
    def start_client(self):
        """Start the camera client GUI"""
        print("🎥 Starting Camera Client GUI (RTMP input)...")
        
        try:
            # Start the client process
            self.client_process = subprocess.Popen([
                sys.executable, "camera_client_gui_smooth.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            
            print(f"✅ Client started (PID: {self.client_process.pid})")
            print("✅ Camera GUI should open shortly...")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to start client: {e}")
            return False
    
    def monitor_processes(self):
        """Monitor all processes and show their output"""
        def monitor_rtmp():
            if self.rtmp_process:
                while self.rtmp_process.poll() is None:
                    output = self.rtmp_process.stdout.readline()
                    if output:
                        print(f"[RTMP] {output.strip()}")
        
        def monitor_server():
            if self.server_process:
                while self.server_process.poll() is None:
                    output = self.server_process.stdout.readline()
                    if output:
                        print(f"[SERVER] {output.strip()}")
        
        def monitor_client():
            if self.client_process:
                while self.client_process.poll() is None:
                    output = self.client_process.stdout.readline()
                    if output:
                        print(f"[CLIENT] {output.strip()}")
        
        # Start monitoring threads
        rtmp_thread = threading.Thread(target=monitor_rtmp, daemon=True)
        server_thread = threading.Thread(target=monitor_server, daemon=True)
        client_thread = threading.Thread(target=monitor_client, daemon=True)
        
        rtmp_thread.start()
        server_thread.start()
        client_thread.start()
        
        return rtmp_thread, server_thread, client_thread
    
    def stop_processes(self):
        """Stop all processes gracefully"""
        print("\n🛑 Stopping all processes...")
        
        if self.client_process:
            print("Stopping camera client...")
            self.client_process.terminate()
            try:
                self.client_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print("Force killing camera client...")
                self.client_process.kill()
        
        if self.server_process:
            print("Stopping animal classifier server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print("Force killing server...")
                self.server_process.kill()
        
        if self.rtmp_process:
            print("Stopping RTMP stream...")
            self.rtmp_process.terminate()
            try:
                self.rtmp_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print("Force killing RTMP stream...")
                self.rtmp_process.kill()
        
        print("✅ All processes stopped")
    
    def run_demo(self):
        """Run the complete demo with RTMP streaming"""
        self.print_banner()
        
        # Check prerequisites
        if not self.check_dependencies():
            return False
        
        if not self.check_virtual_environment():
            return False
        
        if not self.check_ffmpeg():
            return False
        
        print("\n🎯 Starting Animal Classification Demo with HTTP streaming...")
        
        # Start HTTP stream first
        if not self.start_rtmp_stream():
            print("❌ Failed to start HTTP stream. Demo cannot continue.")
            return False
        
        # Wait for HTTP stream to be ready
        print("⏳ Waiting for HTTP stream to initialize...")
        time.sleep(2)
        
        # Start server
        if not self.start_server():
            print("❌ Failed to start server.")
            self.stop_processes()
            return False
        
        # Wait for server to be ready
        print("⏳ Waiting for server to initialize...")
        time.sleep(2)
        
        # Start client
        if not self.start_client():
            print("❌ Failed to start client.")
            self.stop_processes()
            return False
        
        print("\n🎉 Demo is running with HTTP streaming!")
        print("📹 HTTP Stream: http://localhost:8080/video.mjpg")
        print("📡 Server: ws://localhost:8765")
        print("🎥 Client: Camera GUI window should be open")
        print("🐕 Video source: dog.mp4 (looping)")
        print("🔍 Animal detection should work with the video stream")
        print("⌨️  Press 'Q' in the camera window to quit")
        print("🛑 Press Ctrl+C here to stop all components")
        
        # Monitor processes
        self.running = True
        rtmp_thread, server_thread, client_thread = self.monitor_processes()
        
        try:
            # Keep running until interrupted
            while self.running:
                time.sleep(1)
                
                # Check if processes are still running
                if self.rtmp_process and self.rtmp_process.poll() is not None:
                    print("❌ RTMP stream process died unexpectedly")
                    break
                
                if self.server_process and self.server_process.poll() is not None:
                    print("❌ Server process died unexpectedly")
                    break
                
                if self.client_process and self.client_process.poll() is not None:
                    print("❌ Client process died unexpectedly")
                    break
                    
        except KeyboardInterrupt:
            print("\n🛑 Interrupted by user")
        finally:
            self.running = False
            self.stop_processes()
        
        return True
    
    def cleanup(self):
        """Cleanup function for signal handlers"""
        if self.running:
            self.stop_processes()

def signal_handler(signum, frame):
    """Handle interrupt signals"""
    print(f"\n🛑 Received signal {signum}")
    if hasattr(signal_handler, 'runner'):
        signal_handler.runner.cleanup()
    sys.exit(0)

def main():
    """Main function"""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and run demo
    runner = DemoRunner()
    signal_handler.runner = runner  # Store reference for signal handler
    
    try:
        success = runner.run_demo()
        if success:
            print("\n✅ Demo completed successfully")
        else:
            print("\n❌ Demo failed")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        runner.cleanup()
        sys.exit(1)

if __name__ == "__main__":
    main()
