@echo off
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
