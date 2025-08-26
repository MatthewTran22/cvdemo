#!/bin/bash
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
