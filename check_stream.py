#!/usr/bin/env python3
"""
Stream Status Checker for Current MentraOS Implementation
Quick script to check if the MentraOS RTMP stream is running
"""

import requests
import subprocess
import sys
import time
import os

def check_mentraos_app():
    """Check if MentraOS app is running"""
    print("🔍 Checking MentraOS App status...")
    
    try:
        response = requests.get("http://localhost:3000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ MentraOS App: {data.get('status', 'unknown')}")
            print(f"   App: {data.get('app', 'unknown')}")
            print(f"   Active Sessions: {data.get('activeSessions', 0)}")
            return True
        else:
            print(f"❌ MentraOS App returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Could not connect to MentraOS App: {e}")
        return False

def check_rtmp_stream():
    """Check if RTMP stream is accessible"""
    print("\n🔍 Checking RTMP stream accessibility...")
    
    # Primary RTMP URL from the current implementation
    primary_rtmp_url = os.getenv('STREAM_URL')
    
    print(f"   Testing primary URL: {primary_rtmp_url}")
    
    try:
        # Use ffprobe to check stream
        result = subprocess.run([
            'ffprobe', '-v', 'quiet', '-print_format', 'json', 
            '-show_streams', primary_rtmp_url
        ], capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            print(f"✅ RTMP stream is accessible!")
            print("   Stream is ready for Python clients!")
            print(f"   URL: {primary_rtmp_url}")
            return True
        else:
            print(f"   ❌ Not accessible: {result.stderr[:200]}...")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"   ❌ Timeout - stream may not be active yet")
        return False
    except FileNotFoundError:
        print("   ❌ ffprobe not found. Install FFmpeg to test RTMP streams.")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def check_processes():
    """Check if relevant processes are running"""
    print("\n🔍 Checking system processes...")
    
    try:
        # Check for FFmpeg processes
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        ffmpeg_count = result.stdout.count('ffmpeg')
        nginx_count = result.stdout.count('nginx')
        bun_count = result.stdout.count('bun')
        
        print(f"✅ FFmpeg processes: {ffmpeg_count}")
        print(f"✅ Nginx processes: {nginx_count}")
        print(f"✅ Bun processes: {bun_count}")
        
    except Exception as e:
        print(f"❌ Error checking processes: {e}")

def check_network_ports():
    """Check if relevant ports are listening"""
    print("\n🔍 Checking network ports...")
    
    ports_to_check = [3000, 1935, 8080]
    
    try:
        result = subprocess.run(['netstat', '-tuln'], capture_output=True, text=True)
        
        for port in ports_to_check:
            if str(port) in result.stdout:
                print(f"✅ Port {port} is listening")
            else:
                print(f"❌ Port {port} is not listening")
                
    except Exception as e:
        print(f"❌ Error checking network ports: {e}")

def check_current_implementation_info():
    """Provide information about the current implementation"""
    print("\n📋 Current Implementation Info:")
    print(f"• RTMP URL: {os.getenv('STREAM_URL')}")
    print("• This is the primary stream URL for your Python clients")
    print("• Stream starts automatically when you connect via MentraOS glasses")

def main():
    """Main function"""
    print("🎥 MentraOS RTMP Stream Status Checker")
    print("=" * 60)
    
    app_running = check_mentraos_app()
    rtmp_accessible = check_rtmp_stream()
    check_processes()
    check_network_ports()
    
    print("\n" + "=" * 60)
    print("📋 Summary:")
    
    if app_running:
        print("✅ MentraOS app is running")
    else:
        print("❌ MentraOS app is not running")
        print("   Start it with: bun run src/index.ts")
    
    if rtmp_accessible:
        print("✅ RTMP stream is accessible")
        print("   Your Python clients should be able to connect!")
        print("   Use this URL in your Python client:")
        print(f"   {os.getenv('STREAM_URL')}")
    else:
        print("❌ RTMP stream is not accessible")
        print("   Make sure to:")
        print("   1. Start the MentraOS app: bun run src/index.ts")
        print("   2. Connect via your MentraOS glasses")
        print("   3. Wait for the stream to initialize")
    
    check_current_implementation_info()
    
    print("\n🔗 Next Steps:")
    if rtmp_accessible:
        print("1. Update your Python client to use the RTMP URL above")
        print("2. Start animal_classifier.py")
        print("3. Start camera_client_gui_smooth.py with the new URL")
    else:
        print("1. Make sure MentraOS app is running")
        print("2. Connect via your MentraOS glasses")
        print("3. Wait for stream to start, then run this check again")

if __name__ == "__main__":
    main()
