#!/usr/bin/env python3
"""
Test script to verify installation of all required packages
"""

import sys
import importlib

def test_import(module_name, package_name=None):
    """Test if a module can be imported"""
    try:
        importlib.import_module(module_name)
        print(f"✅ {package_name or module_name} - OK")
        return True
    except ImportError as e:
        print(f"❌ {package_name or module_name} - FAILED: {e}")
        return False

def main():
    """Test all required packages"""
    print("🧪 Testing Animal Classification System Installation")
    print("=" * 50)
    
    # Core ML and Computer Vision
    print("\n📦 Core ML and Computer Vision:")
    core_packages = [
        ("ultralytics", "YOLO (Ultralytics)"),
        ("cv2", "OpenCV"),
        ("numpy", "NumPy"),
        ("PIL", "Pillow")
    ]
    
    core_success = True
    for module, name in core_packages:
        if not test_import(module, name):
            core_success = False
    
    # WebSocket Communication
    print("\n📡 WebSocket Communication:")
    websocket_packages = [
        ("websockets", "WebSockets"),
        ("asyncio_mqtt", "AsyncIO MQTT")
    ]
    
    websocket_success = True
    for module, name in websocket_packages:
        if not test_import(module, name):
            websocket_success = False
    
    # Image Processing and Utilities
    print("\n🖼️ Image Processing and Utilities:")
    image_packages = [
        ("matplotlib", "Matplotlib"),
        ("seaborn", "Seaborn")
    ]
    
    image_success = True
    for module, name in image_packages:
        if not test_import(module, name):
            image_success = False
    
    # JSON and Data Handling
    print("\n📊 JSON and Data Handling:")
    data_packages = [
        ("pydantic", "Pydantic"),
        ("dotenv", "Python-dotenv")
    ]
    
    data_success = True
    for module, name in data_packages:
        if not test_import(module, name):
            data_success = False
    
    # Logging and Monitoring
    print("\n📝 Logging and Monitoring:")
    logging_success = test_import("loguru", "Loguru")
    
    # Test YOLO model loading
    print("\n🤖 Testing YOLO Model:")
    try:
        from ultralytics import YOLO
        model = YOLO("yolov8n.pt")
        print("✅ YOLO model loaded successfully")
        yolo_success = True
    except Exception as e:
        print(f"❌ YOLO model loading failed: {e}")
        yolo_success = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Installation Summary:")
    
    all_success = (
        core_success and 
        websocket_success and 
        image_success and 
        data_success and 
        logging_success and 
        yolo_success
    )
    
    if all_success:
        print("🎉 All packages installed successfully!")
        print("\n🚀 You can now run:")
        print("   python animal_classifier.py")
        print("   python camera_client.py")
    else:
        print("⚠️ Some packages failed to install.")
        print("\n🔧 Try running the alternative setup:")
        print("   python setup_alternative.py")
        print("\nOr install missing packages manually:")
        print("   pip install <package_name>")

if __name__ == "__main__":
    main()
