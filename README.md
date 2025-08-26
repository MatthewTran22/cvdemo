# MentraOS Unmanaged RTMP Streaming

This MentraOS app has been configured to use **unmanaged RTMP streaming only** with the provided RTMP URL.

## Configuration

The app is configured to automatically stream to the URL specified in the `STREAM_URL` environment variable.

## Environment Setup

Set the STREAM_URL environment variable:
```bash
export STREAM_URL=your_rtmp_stream_url_here
```

## How It Works

### Automatic Streaming
- When a user starts the app, it automatically begins unmanaged RTMP streaming to the configured URL
- No user interaction required - streaming starts immediately upon session creation
- The stream status is displayed in the glasses and web interface

### Web Interface
- The web interface defaults to "Unmanaged RTMP" mode
- Users can still access other streaming options if needed
- Real-time status updates via Server-Sent Events (SSE)

### Voice Commands
- `"start streaming"` - Starts unmanaged RTMP stream
- `"stop streaming"` - Stops the current stream

## Key Changes Made

1. **Modified `src/index.ts`**:
   - Removed managed streaming subscriptions
   - Added automatic unmanaged stream startup
   - Set default RTMP URL

2. **Updated `src/tools.ts`**:
   - Voice commands now trigger unmanaged streaming
   - Simplified stream management

3. **Enhanced `src/webview.ts`**:
   - Added "Unmanaged RTMP" as default platform
   - Automatic handling of unmanaged stream requests

4. **Updated `src/views/webview.ejs`**:
   - "Unmanaged RTMP" is now the default selected option

## Usage

### Starting the App
1. Launch the app on MentraOS glasses
2. The app automatically starts streaming to the configured RTMP URL
3. Check the web interface at `/webview` for stream status

### Web Interface
1. Navigate to the web interface
2. The "Unmanaged RTMP" option is pre-selected
3. Click the stream toggle button to start/stop streaming
4. Monitor stream status in real-time

### Voice Commands
- Say "start streaming" to begin unmanaged RTMP streaming
- Say "stop streaming" to end the current stream

## Technical Details

- **Stream Type**: Unmanaged RTMP only
- **RTMP URL**: Set via `STREAM_URL` environment variable
- **Protocol**: RTMPS (secure RTMP)
- **Auto-start**: Enabled on session creation
- **Status Monitoring**: Real-time via SSE

## Troubleshooting

If streaming fails:
1. Check that the RTMP URL is accessible
2. Verify network connectivity
3. Check the web interface for error messages
4. Review server logs for detailed error information

## Integration with Camera Client

The system is designed to work with external camera clients that can:
1. Connect to the MentraOS API endpoints
2. Use the same RTMP URL for streaming
3. Monitor stream status via the web interface

To integrate with your Python camera client:
1. Use the `/api/stream/unmanaged/start` endpoint
2. Pass the RTMP URL as a parameter
3. Monitor status via `/stream-status` SSE endpoint