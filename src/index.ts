import { ToolCall, AppServer, AppSession, StreamType } from '@mentra/sdk';
import path from 'path';
import { setupExpressRoutes } from './webview';
import { handleToolCall } from './tools';
import { broadcastStreamStatus, formatStreamStatus } from './webview';

// Extend AppSession interface to include custom properties
declare module '@mentra/sdk' {
  interface AppSession {
    streamType?: 'managed' | 'unmanaged' | null;
    streamStatus?: string;
    hlsUrl?: string | null;
    dashUrl?: string | null;
    streamId?: string | null;
    directRtmpUrl?: string | null;
    error?: string | null;
    previewUrl?: string | null;
    thumbnailUrl?: string | null;
    glassesBatteryPercent?: number | null;
    streamPlatform?: string;
    streamKey?: string;
    customRtmpUrl?: string;
    useCloudflareManaged?: boolean;
    restreamDestinations?: Array<{ url: string; name: string }>;
    mangedRtmpRestreamUrls?: string[] | null;
  }
}

const PACKAGE_NAME = process.env.PACKAGE_NAME ?? (() => { throw new Error('PACKAGE_NAME is not set in .env file'); })();
const MENTRAOS_API_KEY = process.env.MENTRAOS_API_KEY ?? (() => { throw new Error('MENTRAOS_API_KEY is not set in .env file'); })();
const PORT = parseInt(process.env.PORT || '3000');

class StreamerApp extends AppServer {
  constructor() {
    super({
      packageName: PACKAGE_NAME,
      apiKey: MENTRAOS_API_KEY,
      port: PORT,
      publicDir: path.join(__dirname, '../public'),
    });

    // Set up Express routes
    setupExpressRoutes(this);
  }

  /** Map to store active user sessions */
  private userSessionsMap = new Map<string, AppSession>();

  /**
   * Handles tool calls from the MentraOS system
   * @param toolCall - The tool call request
   * @returns Promise resolving to the tool call response or undefined
   */
  protected async onToolCall(toolCall: ToolCall): Promise<string | undefined> {
    return handleToolCall(toolCall, toolCall.userId, this.userSessionsMap.get(toolCall.userId));
  }

  /**
   * Handles new user sessions
   * Sets up event listeners and displays welcome message
   * @param session - The app session instance
   * @param sessionId - Unique session identifier
   * @param userId - User identifier
   */
  protected async onSession(session: AppSession, sessionId: string, userId: string): Promise<void> {
    // Track the session for this user
    this.userSessionsMap.set(userId, session);

    // Only subscribe to unmanaged RTMP stream status
    session.subscribe(StreamType.RTMP_STREAM_STATUS);

    // Default RTMP URL for unmanaged streaming
    const DEFAULT_RTMP_URL = process.env.STREAM_URL;

    // Start unmanaged RTMP stream automatically
    try {
      console.log('\n' + '='.repeat(80));
      console.log('🚀 STARTING MENTRAOS RTMP STREAM');
      console.log('='.repeat(80));
      console.log(`🎥 RTMP URL: ${DEFAULT_RTMP_URL}`);
      console.log(`👤 User ID: ${userId}`);
      console.log(`📱 Session ID: ${sessionId}`);
      console.log('⏳ Initializing stream...');
      console.log('='.repeat(80) + '\n');
      
      // Check camera capabilities first
      console.log('📷 Checking camera capabilities...');
      const caps = session.capabilities;
      console.log('🔍 Full capabilities:', JSON.stringify(caps, null, 2));
      if (caps?.hasCamera) {
        console.log('✅ Camera is available');
        console.log(`📷 Resolution: ${caps.camera?.resolution?.width}x${caps.camera?.resolution?.height}`);
        console.log(`📹 Can stream: ${caps.camera?.video?.canStream}`);
        console.log(`📹 Supported stream types: ${caps.camera?.video?.supportedStreamTypes?.join(', ')}`);
      } else {
        console.log('❌ Camera is NOT available - this will cause timeout!');
        console.log('⚠️  Your glasses may not have a camera or camera permissions are denied');
      }
      
      console.log(`🎯 Attempting to start stream with URL: ${DEFAULT_RTMP_URL}`);
      await session.camera.startStream({ rtmpUrl: DEFAULT_RTMP_URL });
      session.streamType = 'unmanaged';
      session.streamStatus = 'starting';
      session.directRtmpUrl = DEFAULT_RTMP_URL;
      console.log(`✅ Stream started with URL: ${session.directRtmpUrl}`);
      broadcastStreamStatus(userId, formatStreamStatus(session));
      
      console.log('✅ Stream initialization request sent successfully!');
      console.log('📡 Waiting for stream to become active...');
      console.log('⚠️  If stream times out, check:');
      console.log('   - Camera permissions on glasses');
      console.log('   - Internet connection');
      console.log('   - RTMP server availability');
      console.log('');
    } catch (error) {
      console.error('Error starting unmanaged stream:', error);
      session.error = error instanceof Error ? error.message : String(error);
      broadcastStreamStatus(userId, formatStreamStatus(session));
    }

    // Only handle unmanaged RTMP stream status
    const rtmpStatusUnsubscribe = session.camera.onStreamStatus((data) => {
      console.log('\n' + '='.repeat(60));
      console.log('📡 STREAM STATUS UPDATE');
      console.log('='.repeat(60));
      console.log(`🎥 RTMP URL: ${DEFAULT_RTMP_URL}`);
      console.log(`📡 Stream ID: ${data.streamId ?? 'unknown'}`);
      console.log(`🔄 Status: ${data.status.toUpperCase()}`);
      console.log(`⏰ Timestamp: ${data.timestamp || new Date().toISOString()}`);
      console.log('='.repeat(60) + '\n');
      
      session.streamType = 'unmanaged';
      session.streamStatus = data.status;
      session.hlsUrl = null;
      session.dashUrl = null;
      session.streamId = data.streamId ?? null;
      session.directRtmpUrl = DEFAULT_RTMP_URL; // Use the default URL we set
      session.error = data.errorDetails ?? null;
      
      // Broadcast updated status to the user's SSE clients
      broadcastStreamStatus(userId, formatStreamStatus(session));
      
      // Show status updates in terminal
      if (data.status === 'active') {
        console.log('\n' + '🎉'.repeat(20));
        console.log('🎉🎉🎉 STREAM IS NOW ACTIVE! 🎉🎉🎉');
        console.log('🎉'.repeat(20));
        console.log(`🎥 RTMP URL: ${session.directRtmpUrl}`);
        console.log(`📡 Stream ID: ${session.streamId}`);
        console.log(`🔗 Test with: ffprobe ${session.directRtmpUrl}`);
        console.log(`📺 Or use VLC: Media > Open Network Stream > ${session.directRtmpUrl}`);
        console.log(`🐍 Python client ready to connect!`);
        console.log('🎉'.repeat(20) + '\n');
        
        session.layouts.showTextWall(`✅ Stream active!\n\nRTMP: ${session.directRtmpUrl}`);
      } else if (data.status === 'error') {
        console.log('\n' + '❌'.repeat(20));
        console.log('❌❌❌ STREAM ERROR ❌❌❌');
        console.log('❌'.repeat(20));
        console.log(`Error: ${session.error || 'Unknown error'}`);
        console.log(`Stream ID: ${session.streamId}`);
        console.log('❌'.repeat(20) + '\n');
        
        session.layouts.showTextWall(`❌ Stream error: ${session.error || 'Unknown error'}`);
      } else if (data.status === 'timeout') {
        console.log('\n' + '⏰'.repeat(20));
        console.log('⏰⏰⏰ STREAM TIMEOUT ⏰⏰⏰');
        console.log('⏰'.repeat(20));
        console.log(`Stream ID: ${session.streamId}`);
        console.log(`Status: ${data.status}`);
        console.log(`RTMP URL: ${session.directRtmpUrl}`);
        console.log('');
        console.log('🔍 TROUBLESHOOTING TIMEOUT:');
        console.log('1. Check if camera permissions are granted on glasses');
        console.log('2. Verify internet connection is stable');
        console.log('3. Test RTMP server: ffprobe ' + session.directRtmpUrl);
        console.log('4. Check if glasses have camera hardware');
        console.log('5. Try restarting the app on glasses');
        console.log('⏰'.repeat(20) + '\n');
      }
    });

    // Glasses battery level updates (if available)
    const batteryUnsubscribe = session.events?.onGlassesBattery?.((data: any) => {
      try {
        const pct = typeof data?.percent === 'number' ? data.percent : (typeof data === 'number' ? data : null);
        session.glassesBatteryPercent = pct ?? null;
      } catch {
        session.glassesBatteryPercent = null;
      }
      broadcastStreamStatus(userId, formatStreamStatus(session));
    }) ?? (() => {});

    // Broadcast on disconnect and cleanup the mapping
    const disconnectedUnsubscribe = session.events.onDisconnected((info: any) => {
      try {
        // Only broadcast a disconnected state if the SDK marks it as permanent
        if (info && typeof info === 'object' && info.permanent === true) {
          this.userSessionsMap.delete(userId);
          broadcastStreamStatus(userId, formatStreamStatus(undefined));
        }
        // Otherwise, allow auto-reconnect without UI flicker
      } catch {
        // No-op
      }
    });

    this.addCleanupHandler(() => {
      rtmpStatusUnsubscribe();
      batteryUnsubscribe();
      disconnectedUnsubscribe();
    });

    // Send an initial status snapshot
    broadcastStreamStatus(userId, formatStreamStatus(session));

    // tell the user that they can start streaming via the webview (speak)
  }

  /**
   * Handles stop requests to ensure SSE clients are notified of disconnection
   */
  protected async onStop(sessionId: string, userId: string, reason: string): Promise<void> {
    try {
      // Ensure base cleanup (disconnects and clears SDK's active session maps)
      await super.onStop(sessionId, userId, reason);
      // Remove any cached session for this user
      this.userSessionsMap.delete(userId);
    } finally {
      // Broadcast a no-session status so clients update UI promptly
      broadcastStreamStatus(userId, formatStreamStatus(undefined));
    }
  }
}

// Start the server
const app = new StreamerApp();

app.start().catch(console.error);