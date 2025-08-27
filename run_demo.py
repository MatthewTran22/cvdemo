#!/usr/bin/env python3
"""
Demo Runner for MentraOS Animal Classification System
Launches animal classifier server and camera client GUI with direct MP4 input
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
        self.running = False
        self.selected_video_file = None
        
    def print_banner(self):
        """Print the demo banner"""
        print("=" * 70)
        print("🐾 MentraOS Animal Classification Demo (Direct MP4 Input)")
        print("=" * 70)
        print("This will launch:")
        print("  📡 Animal Classifier Server (Python backend)")
        print("  🎥 Camera Client GUI (Direct MP4 file input)")
        print("=" * 70)
        print("Press Ctrl+C to stop all components")
        print("=" * 70)
    
    def select_video_file(self):
        """Allow user to select a video file"""
        print("\n🎬 Video File Selection")
        print("=" * 40)
        
        # Check if dog.mp4 exists as default
        default_file = "dog.mp4"
        if Path(default_file).exists():
            print(f"📁 Default video file found: {default_file}")
            print("\nOptions:")
            print("  1. Use default file (dog.mp4)")
            print("  2. Choose a different video file")
            print("  3. Enter custom file path")
            
            while True:
                choice = input("\nEnter your choice (1-3): ").strip()
                
                if choice == "1":
                    self.selected_video_file = default_file
                    print(f"✅ Using default file: {default_file}")
                    return True
                    
                elif choice == "2":
                    # Use file dialog if available
                    if self._show_file_dialog():
                        return True
                    else:
                        print("⚠️  File dialog not available, please use option 3")
                        continue
                        
                elif choice == "3":
                    if self._enter_custom_path():
                        return True
                    continue
                    
                else:
                    print("❌ Invalid choice. Please enter 1, 2, or 3.")
        else:
            print(f"⚠️  Default file {default_file} not found")
            print("\nOptions:")
            print("  1. Choose a video file")
            print("  2. Enter custom file path")
            
            while True:
                choice = input("\nEnter your choice (1-2): ").strip()
                
                if choice == "1":
                    if self._show_file_dialog():
                        return True
                    else:
                        print("⚠️  File dialog not available, please use option 2")
                        continue
                        
                elif choice == "2":
                    if self._enter_custom_path():
                        return True
                    continue
                    
                else:
                    print("❌ Invalid choice. Please enter 1 or 2.")
    
    def _show_file_dialog(self):
        """Show file dialog for video selection"""
        try:
            # Try to use tkinter file dialog
            import tkinter as tk
            from tkinter import filedialog
            
            # Create a hidden root window
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            
            # Show file dialog
            file_path = filedialog.askopenfilename(
                title="Select Video File",
                filetypes=[
                    ("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv"),
                    ("MP4 files", "*.mp4"),
                    ("All files", "*.*")
                ]
            )
            
            root.destroy()
            
            if file_path:
                if Path(file_path).exists():
                    self.selected_video_file = file_path
                    print(f"✅ Selected file: {file_path}")
                    return True
                else:
                    print("❌ Selected file does not exist")
                    return False
            else:
                print("❌ No file selected")
                return False
                
        except ImportError:
            print("⚠️  tkinter not available for file dialog")
            return False
        except Exception as e:
            print(f"❌ Error showing file dialog: {e}")
            return False
    
    def _enter_custom_path(self):
        """Allow user to enter custom file path"""
        while True:
            file_path = input("\nEnter the path to your video file: ").strip()
            
            if not file_path:
                print("❌ No path entered")
                continue
            
            # Remove quotes if present
            file_path = file_path.strip('"\'')
            
            if Path(file_path).exists():
                # Check if it's a video file
                video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']
                if any(file_path.lower().endswith(ext) for ext in video_extensions):
                    self.selected_video_file = file_path
                    print(f"✅ Video file found: {file_path}")
                    return True
                else:
                    print("⚠️  File doesn't appear to be a video file")
                    continue_choice = input("Use this file anyway? (y/n): ").strip().lower()
                    if continue_choice in ['y', 'yes']:
                        self.selected_video_file = file_path
                        print(f"✅ Using file: {file_path}")
                        return True
            else:
                print("❌ File not found")
                retry = input("Try again? (y/n): ").strip().lower()
                if retry not in ['y', 'yes']:
                    return False
    
    def check_dependencies(self):
        """Check if required files exist"""
        required_files = [
            "animal_classifier.py",
            "camera_client_gui_smooth.py",
            "requirements.txt"
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
        """Start the camera client GUI with selected video file"""
        print("🎥 Starting Camera Client GUI...")
        
        try:
            # Start the client process with selected video file
            cmd = [sys.executable, "camera_client_gui_smooth.py"]
            if self.selected_video_file:
                cmd.append(self.selected_video_file)
            
            self.client_process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                text=True
            )
            
            print(f"✅ Client started (PID: {self.client_process.pid})")
            print(f"📹 Using video file: {self.selected_video_file}")
            print("✅ Camera GUI should open shortly...")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to start client: {e}")
            return False
    
    def monitor_processes(self):
        """Monitor all processes and show their output"""
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
        server_thread = threading.Thread(target=monitor_server, daemon=True)
        client_thread = threading.Thread(target=monitor_client, daemon=True)
        
        server_thread.start()
        client_thread.start()
        
        return server_thread, client_thread
    
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
        
        print("✅ All processes stopped")
    
    def run_demo(self):
        """Run the complete demo with selected video file"""
        self.print_banner()
        
        # Check prerequisites
        if not self.check_dependencies():
            return False
        
        if not self.check_virtual_environment():
            return False
        
        # Select video file
        if not self.select_video_file():
            print("❌ No video file selected. Demo cannot continue.")
            return False
        
        print(f"\n🎯 Starting Animal Classification Demo with: {self.selected_video_file}")
        
        # Start server first
        if not self.start_server():
            print("❌ Failed to start server.")
            return False
        
        # Wait for server to be ready
        print("⏳ Waiting for server to initialize...")
        time.sleep(2)
        
        # Start client
        if not self.start_client():
            print("❌ Failed to start client.")
            self.stop_processes()
            return False
        
        print("\n🎉 Demo is running!")
        print("📡 Server: ws://localhost:8765")
        print("🎥 Client: Camera GUI window should be open")
        print(f"📹 Video source: {self.selected_video_file}")
        print("🔍 Animal detection should work with the video file")
        print("⌨️  Press 'Q' in the camera window to quit")
        print("🛑 Press Ctrl+C here to stop all components")
        
        # Monitor processes
        self.running = True
        server_thread, client_thread = self.monitor_processes()
        
        try:
            # Keep running until interrupted
            while self.running:
                time.sleep(1)
                
                # Check if processes are still running
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
