# MentraOS RTMP Streaming Demo

This demo showcases a smooth, high-performance video streaming system that integrates MentraOS camera feeds with real-time animal detection using RTMP streaming technology.

## 🏗️ Architecture Overview

```
┌─────────────────┐    RTMP Stream    ┌─────────────────┐    WebSocket    ┌─────────────────┐
│   MentraOS App  │ ────────────────► │  RTMP Server    │ ──────────────► │ Animal Classifier│
│   (index.ts)    │                   │  (FFmpeg)       │                 │  (YOLO)         │
└─────────────────┘                   └─────────────────┘                 └─────────────────┘
                                              │                                    │
                                              │ RTMP Stream                        │ Detection Results
                                              ▼                                    ▼
                                       ┌─────────────────┐                 ┌─────────────────┐
                                       │  Python Client  │ ◄────────────── │  GUI Display    │
                                       │ (PyAV + OpenCV) │                 │ (Real-time)     │
                                       └─────────────────┘                 └─────────────────┘
```

## ✨ Features

- **Smooth Video Streaming**: High frame rate (30 FPS) video playback with minimal latency
- **Real-time Animal Detection**: YOLO-based animal detection running at 10 FPS
- **RTMP Protocol**: Industry-standard streaming protocol for reliable video transmission
- **Low Latency**: Optimized for real-time applications with sub-second delay
- **Cross-platform**: Works on Windows, macOS, and Linux
- **Easy Setup**: Automated setup script with dependency management

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+**
2. **FFmpeg** (for RTMP streaming)
3. **Node.js** (for MentraOS app)

### Installation

1. **Run the setup script:**
   ```bash
   python setup_rtmp_streaming.py
   ```

2. **Start the MentraOS app:**
   ```bash
   cd src
   npm install
   npm start
   ```

3. **Run the demo:**
   ```bash
   # Unix/Mac
   ./start_demo.sh
   
   # Windows
   start_demo.bat
   ```

## 📋 Manual Setup

If you prefer to set up components manually:

### 1. Install FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
- Download from https://ffmpeg.org/download.html
- Add to PATH environment variable

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start Services (in separate terminals)

**Terminal 1 - RTMP Server:**
```bash
python rtmp_server.py
```

**Terminal 2 - Animal Classifier:**
```bash
python animal_classifier.py
```

**Terminal 3 - Camera Client:**
```bash
python camera_client_gui_smooth.py
```

## 🔧 Configuration

### RTMP Server Configuration

The RTMP server runs on port 1935 by default. You can modify the configuration in `rtmp_server.py`:

```python
server = RTMPServer(port=1935, app_name="live")
```

### Camera Client Configuration

Modify the camera client settings in `camera_client_gui_smooth.py`:

```python
client = SmoothGUICameraClient(
    rtmp_url="rtmp://localhost:1935/live/stream",
    websocket_url="ws://localhost:8765",
    display_fps=30,      # Display frame rate
    detection_fps=10     # Detection frame rate
)
```

### MentraOS App Configuration

The MentraOS app automatically starts RTMP streaming when camera streaming is activated. The RTMP URL is logged when streaming begins.

## 📊 Performance Optimization

### Frame Rate Control

- **Display FPS**: 30 FPS for smooth video playback
- **Detection FPS**: 10 FPS for optimal performance
- **Buffer Size**: 30 frames (1 second at 30 FPS)

### Latency Optimization

- **RTMP Buffer**: 1 second buffer for network stability
- **Low Delay Mode**: Enabled for minimal latency
- **Frame Skipping**: Disabled for smooth playback

### Memory Management

- **Frame Buffer**: Limited to 30 frames to prevent memory overflow
- **Detection Queue**: Limited to 5 frames for real-time processing
- **Automatic Cleanup**: Resources are properly released on shutdown

## 🐛 Troubleshooting

### Common Issues

**1. FFmpeg not found:**
```
❌ FFmpeg is not installed
```
**Solution:** Install FFmpeg using the instructions in the setup script.

**2. RTMP connection failed:**
```
Error initializing RTMP connection: [Errno 111] Connection refused
```
**Solution:** Make sure the RTMP server is running on port 1935.

**3. WebSocket connection failed:**
```
WebSocket connection failed: [Errno 111] Connection refused
```
**Solution:** Make sure the animal classifier is running on port 8765.

**4. Low frame rate:**
- Check system resources (CPU, memory)
- Reduce display FPS in configuration
- Ensure FFmpeg is properly installed

### Debug Mode

Enable debug logging by modifying the log level in the Python files:

```python
logger.add("debug.log", level="DEBUG")
```

### Port Conflicts

If you encounter port conflicts, you can change the default ports:

- **RTMP Server**: Modify port in `rtmp_server.py`
- **Animal Classifier**: Modify port in `animal_classifier.py`
- **MentraOS SSE**: Modify `SSE_PORT` in `index.ts`

## 🔄 Integration with MentraOS

The MentraOS app has been enhanced with RTMP streaming capabilities:

### New Features in index.ts

1. **RTMP Server Setup**: Automatic RTMP server initialization
2. **Stream Management**: Start/stop RTMP streams per user
3. **Frame Broadcasting**: Real-time camera frame transmission
4. **Status Monitoring**: RTMP connection status tracking

### Stream Lifecycle

1. **User starts streaming** → RTMP stream is created
2. **Camera frames captured** → Transmitted via RTMP
3. **Python client connects** → Receives RTMP stream
4. **Animal detection** → WebSocket communication
5. **User stops streaming** → RTMP stream is closed

## 📈 Performance Metrics

### Expected Performance

- **Video Latency**: < 500ms end-to-end
- **Frame Rate**: 30 FPS display, 10 FPS detection
- **CPU Usage**: < 50% on modern systems
- **Memory Usage**: < 500MB total

### Monitoring

The system provides real-time metrics:

- **FPS Counter**: Display frame rate
- **Connection Status**: RTMP and WebSocket status
- **Detection Count**: Number of detected animals
- **Frame Counter**: Total frames processed

## 🔮 Future Enhancements

### Planned Features

1. **Multi-stream Support**: Multiple concurrent RTMP streams
2. **Stream Recording**: Save RTMP streams to files
3. **Quality Adaptation**: Dynamic bitrate adjustment
4. **Web Interface**: Browser-based stream viewer
5. **Cloud Integration**: Stream to cloud services

### Scalability

The architecture is designed for scalability:

- **Horizontal Scaling**: Multiple RTMP servers
- **Load Balancing**: Distribute streams across servers
- **Caching**: Frame buffer optimization
- **Compression**: Adaptive video compression

## 📚 Technical Details

### RTMP Protocol

RTMP (Real-Time Messaging Protocol) is used for:
- **Low Latency**: Sub-second video transmission
- **Reliability**: Built-in error correction
- **Compatibility**: Industry-standard protocol
- **Scalability**: Supports multiple concurrent streams

### PyAV Integration

PyAV provides:
- **High Performance**: C-based video processing
- **Format Support**: Multiple video codecs
- **Low Latency**: Optimized for real-time streaming
- **Cross-platform**: Works on all major platforms

### WebSocket Communication

WebSocket is used for:
- **Real-time Detection**: Instant animal detection results
- **Bidirectional Communication**: Client-server messaging
- **Low Overhead**: Efficient data transmission
- **Reliability**: Automatic reconnection

## 🤝 Contributing

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **FFmpeg**: Video processing and streaming
- **PyAV**: Python video processing library
- **OpenCV**: Computer vision capabilities
- **Ultralytics**: YOLO model implementation
- **MentraOS**: Smart glasses platform
