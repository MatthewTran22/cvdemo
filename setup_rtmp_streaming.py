#!/usr/bin/env python3
"""
Setup Script for MentraOS RTMP Streaming Demo
Installs dependencies and provides instructions for running the complete system
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def check_ffmpeg():
    """Check if FFmpeg is installed"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ FFmpeg is installed")
            return True
        else:
            print("❌ FFmpeg is not working properly")
            return False
    except FileNotFoundError:
        print("❌ FFmpeg is not installed")
        return False

def install_ffmpeg():
    """Provide instructions for installing FFmpeg"""
    system = platform.system().lower()
    
    print("\n📋 FFmpeg Installation Instructions:")
    
    if system == "darwin":  # macOS
        print("On macOS, install FFmpeg using Homebrew:")
        print("  brew install ffmpeg")
    elif system == "linux":
        print("On Ubuntu/Debian:")
        print("  sudo apt update")
        print("  sudo apt install ffmpeg")
        print("\nOn CentOS/RHEL/Fedora:")
        print("  sudo yum install ffmpeg  # or sudo dnf install ffmpeg")
    elif system == "windows":
        print("On Windows:")
        print("  1. Download from https://ffmpeg.org/download.html")
        print("  2. Extract to a folder (e.g., C:\\ffmpeg)")
        print("  3. Add C:\\ffmpeg\\bin to your PATH environment variable")
    else:
        print("Please install FFmpeg from https://ffmpeg.org/download.html")

def install_python_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing Python dependencies...")
    
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True)
        print("✅ Python dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Python dependencies: {e}")
        return False

def create_startup_script():
    """Create a startup script for easy launching"""
    script_content = """#!/bin/bash
# MentraOS RTMP Streaming Demo Startup Script

echo "🚀 Starting MentraOS RTMP Streaming Demo..."

# Check if FFmpeg is available
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ FFmpeg is not installed. Please install FFmpeg first."
    exit 1
fi

# Start RTMP server
echo "📡 Starting RTMP server..."
python rtmp_server.py &
RTMP_PID=$!

# Wait a moment for RTMP server to start
sleep 2

# Start animal classifier
echo "🤖 Starting animal classifier..."
python animal_classifier.py &
CLASSIFIER_PID=$!

# Wait a moment for classifier to start
sleep 2

# Start camera client
echo "📹 Starting camera client..."
python camera_client_gui_smooth.py &
CLIENT_PID=$!

echo "✅ All services started!"
echo "Press Ctrl+C to stop all services"

# Function to cleanup on exit
cleanup() {
    echo "🛑 Stopping all services..."
    kill $RTMP_PID $CLASSIFIER_PID $CLIENT_PID 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Wait for all processes
wait
"""

    # Write the script
    with open('start_demo.sh', 'w') as f:
        f.write(script_content)
    
    # Make it executable on Unix systems
    if platform.system() != "Windows":
        os.chmod('start_demo.sh', 0o755)
    
    print("✅ Created startup script: start_demo.sh")

def create_windows_batch():
    """Create a Windows batch file for easy launching"""
    batch_content = """@echo off
REM MentraOS RTMP Streaming Demo Startup Script

echo 🚀 Starting MentraOS RTMP Streaming Demo...

REM Check if FFmpeg is available
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo ❌ FFmpeg is not installed. Please install FFmpeg first.
    pause
    exit /b 1
)

REM Start RTMP server
echo 📡 Starting RTMP server...
start /B python rtmp_server.py

REM Wait a moment for RTMP server to start
timeout /t 2 /nobreak >nul

REM Start animal classifier
echo 🤖 Starting animal classifier...
start /B python animal_classifier.py

REM Wait a moment for classifier to start
timeout /t 2 /nobreak >nul

REM Start camera client
echo 📹 Starting camera client...
start /B python camera_client_gui_smooth.py

echo ✅ All services started!
echo Press any key to stop all services
pause

REM Kill all Python processes (be careful with this in production)
taskkill /f /im python.exe >nul 2>&1
"""

    with open('start_demo.bat', 'w') as f:
        f.write(batch_content)
    
    print("✅ Created Windows batch file: start_demo.bat")

def main():
    """Main setup function"""
    print("🎯 MentraOS RTMP Streaming Demo Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check FFmpeg
    if not check_ffmpeg():
        install_ffmpeg()
        print("\n⚠️  Please install FFmpeg and run this script again.")
        sys.exit(1)
    
    # Install Python dependencies
    if not install_python_dependencies():
        sys.exit(1)
    
    # Create startup scripts
    create_startup_script()
    create_windows_batch()
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Start the MentraOS app (index.ts)")
    print("2. Run the demo using one of these methods:")
    print("   - Unix/Mac: ./start_demo.sh")
    print("   - Windows: start_demo.bat")
    print("   - Manual: Start each service in separate terminals")
    print("\n📖 Manual startup order:")
    print("1. python rtmp_server.py")
    print("2. python animal_classifier.py")
    print("3. python camera_client_gui_smooth.py")
    print("\n🔧 Troubleshooting:")
    print("- Make sure FFmpeg is in your PATH")
    print("- Check that all Python dependencies are installed")
    print("- Ensure ports 1935 (RTMP), 8765 (WebSocket), and 3002 (SSE) are available")

if __name__ == "__main__":
    main()


