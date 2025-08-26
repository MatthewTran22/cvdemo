#!/usr/bin/env python3
"""
Simple test script to check WebSocket server status
"""

import asyncio
import websockets
import json

async def test_server():
    """Test if the WebSocket server is running"""
    try:
        print("🔍 Testing WebSocket server connection...")
        
        # Try to connect to the server
        async with websockets.connect('ws://localhost:8765') as websocket:
            print("✅ Successfully connected to WebSocket server!")
            
            # Send a ping message
            ping_message = {
                "type": "ping",
                "timestamp": 1234567890.123
            }
            
            await websocket.send(json.dumps(ping_message))
            print("📤 Sent ping message")
            
            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"📥 Received response: {response}")
                print("✅ Server is responding correctly!")
                return True
            except asyncio.TimeoutError:
                print("❌ No response received from server")
                return False
                
    except ConnectionRefusedError:
        print("❌ Connection refused - server is not running")
        return False
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_server())
    if result:
        print("\n🎉 Server is ready for camera client!")
    else:
        print("\n🔧 Please start the animal classifier server first:")
        print("   python animal_classifier.py")
