import { ToolCall, AppSession } from '@mentra/sdk';
import { broadcastStreamStatus, formatStreamStatus } from './webview';

/**
 * Handle a tool call
 * @param toolCall - The tool call from the server
 * @param userId - The user ID of the user who called the tool
 * @param session - The session object if the user has an active session
 * @returns A promise that resolves to the tool call result
 */
export async function handleToolCall(toolCall: ToolCall, userId: string, session: AppSession|undefined): Promise<string | undefined> {
  console.log(`Tool called: ${toolCall.toolId}`);
  console.log(`Tool call timestamp: ${toolCall.timestamp}`);
  console.log(`Tool call userId: ${toolCall.userId}`);
  if (toolCall.toolParameters && Object.keys(toolCall.toolParameters).length > 0) {
    console.log("Tool call parameter values:", toolCall.toolParameters);
  }

  if (toolCall.toolId === "start_streaming") {
    // Start unmanaged RTMP stream with default URL
    if (!session) {
      return "Error: No active session";
    }

    try {
      const DEFAULT_RTMP_URL = process.env.STREAM_URL;
      await session.camera.startStream({ rtmpUrl: DEFAULT_RTMP_URL });
      session.streamType = 'unmanaged';
      session.streamStatus = 'starting';
      session.directRtmpUrl = DEFAULT_RTMP_URL;
      broadcastStreamStatus(userId, formatStreamStatus(session));
      return "Unmanaged RTMP stream started successfully";
    } catch (error: any) {
      console.error("Error starting unmanaged stream:", error);
      return `Error: ${error?.message || error}`;
    }
  } else if (toolCall.toolId === "stop_streaming") {
    if (!session) {
      return "Error: No active session";
    }

    try {
      if (session.streamType === 'unmanaged') {
        await session.camera.stopStream();
        session.streamType = null;
        session.streamStatus = 'idle';
        session.directRtmpUrl = null;
        broadcastStreamStatus(userId, formatStreamStatus(session));
        return "Unmanaged stream stopped successfully";
      } else {
        return "No active unmanaged stream to stop";
      }
    } catch (error: any) {
      console.error("Error stopping stream:", error);
      return `Error: ${error?.message || error}`;
    }
  }

  return undefined;
}