#!/usr/bin/env python3
"""
Animal Classification Module using YOLO
Handles real-time animal detection and classification
"""

import asyncio
import json
import base64
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO
from loguru import logger
import websockets
from websockets.server import serve
from pydantic import BaseModel

# Configure logging
logger.add("animal_classifier.log", rotation="1 day", retention="7 days")

@dataclass
class AnimalDetection:
    """Represents a detected animal"""
    class_id: int
    class_name: str
    confidence: float
    bbox: List[float]  # [x1, y1, x2, y2]
    center_x: float
    center_y: float

class DetectionRequest(BaseModel):
    """Request model for image detection"""
    image_data: str  # base64 encoded image
    image_id: str
    timestamp: float

class DetectionResponse(BaseModel):
    """Response model for detection results"""
    image_id: str
    detections: List[Dict[str, Any]]
    processing_time: float
    timestamp: float

class AnimalClassifier:
    """YOLO-based animal classifier"""
    
    # COCO dataset animal class IDs and names
    ANIMAL_CLASSES = {
        15: "cat",      # Added cat
        16: "dog",
        17: "horse", 
        18: "sheep",
        19: "cow",
        20: "elephant",
        21: "bear",
        22: "zebra",
        23: "giraffe"
    }
    
    def __init__(self, model_path: str = "yolov8n.pt", confidence_threshold: float = 0.5):
        """
        Initialize the animal classifier
        
        Args:
            model_path: Path to YOLO model file
            confidence_threshold: Minimum confidence for detections
        """
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.model_path = model_path
        self.is_loaded = False
        
        logger.info(f"Initializing AnimalClassifier with model: {model_path}")
        self._load_model()
    
    def _load_model(self):
        """Load the YOLO model"""
        try:
            # Download model if it doesn't exist
            if not Path(self.model_path).exists():
                logger.info(f"Downloading YOLO model: {self.model_path}")
                self.model = YOLO(self.model_path)
            else:
                logger.info(f"Loading existing model: {self.model_path}")
                self.model = YOLO(self.model_path)
            
            self.is_loaded = True
            logger.success("YOLO model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            raise
    
    def _filter_animal_detections(self, results) -> List[AnimalDetection]:
        """
        Filter YOLO results to only include animals
        
        Args:
            results: YOLO detection results
            
        Returns:
            List of animal detections
        """
        animal_detections = []
        
        if results and len(results) > 0:
            result = results[0]  # Get first result
            
            if result.boxes is not None:
                for box in result.boxes:
                    class_id = int(box.cls.item())
                    confidence = float(box.conf.item())
                    
                    # Check if it's an animal class and meets confidence threshold
                    if class_id in self.ANIMAL_CLASSES and confidence >= self.confidence_threshold:
                        # Get bounding box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        center_x = (x1 + x2) / 2
                        center_y = (y1 + y2) / 2
                        
                        detection = AnimalDetection(
                            class_id=class_id,
                            class_name=self.ANIMAL_CLASSES[class_id],
                            confidence=confidence,
                            bbox=[x1, y1, x2, y2],
                            center_x=center_x,
                            center_y=center_y
                        )
                        animal_detections.append(detection)
        
        return animal_detections
    
    def detect_animals(self, image: np.ndarray) -> List[AnimalDetection]:
        """
        Detect animals in an image
        
        Args:
            image: Input image as numpy array (BGR format)
            
        Returns:
            List of detected animals
        """
        if not self.is_loaded:
            logger.error("Model not loaded")
            return []
        
        try:
            # Run YOLO inference
            results = self.model(image, verbose=False)
            
            # Filter for animals only
            animal_detections = self._filter_animal_detections(results)
            
            logger.debug(f"Detected {len(animal_detections)} animals")
            return animal_detections
            
        except Exception as e:
            logger.error(f"Error during animal detection: {e}")
            return []
    
    def base64_to_image(self, base64_string: str) -> np.ndarray:
        """
        Convert base64 string to numpy image array
        
        Args:
            base64_string: Base64 encoded image string
            
        Returns:
            Image as numpy array
        """
        try:
            # Remove data URL prefix if present
            if base64_string.startswith('data:image'):
                base64_string = base64_string.split(',')[1]
            
            # Decode base64
            image_bytes = base64.b64decode(base64_string)
            
            # Convert to numpy array
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            return image
            
        except Exception as e:
            logger.error(f"Error converting base64 to image: {e}")
            raise
    
    def process_detection_request(self, request: DetectionRequest) -> DetectionResponse:
        """
        Process a detection request
        
        Args:
            request: Detection request with base64 image
            
        Returns:
            Detection response with results
        """
        import time
        start_time = time.time()
        
        try:
            # Convert base64 to image
            image = self.base64_to_image(request.image_data)
            
            # Detect animals
            detections = self.detect_animals(image)
            
            # Convert to serializable format
            detection_data = []
            for det in detections:
                detection_data.append({
                    "class_id": det.class_id,
                    "class_name": det.class_name,
                    "confidence": det.confidence,
                    "bbox": det.bbox,
                    "center_x": det.center_x,
                    "center_y": det.center_y
                })
            
            processing_time = time.time() - start_time
            
            response = DetectionResponse(
                image_id=request.image_id,
                detections=detection_data,
                processing_time=processing_time,
                timestamp=time.time()
            )
            
            logger.info(f"Processed detection in {processing_time:.3f}s - Found {len(detections)} animals")
            return response
            
        except Exception as e:
            logger.error(f"Error processing detection request: {e}")
            # Return empty response on error
            return DetectionResponse(
                image_id=request.image_id,
                detections=[],
                processing_time=time.time() - start_time,
                timestamp=time.time()
            )

class WebSocketServer:
    """WebSocket server for handling detection requests"""
    
    def __init__(self, classifier: AnimalClassifier, host: str = "localhost", port: int = 8765):
        self.classifier = classifier
        self.host = host
        self.port = port
        self.clients = set()
        
    async def handle_client(self, websocket, path):
        """Handle individual WebSocket client connections"""
        self.clients.add(websocket)
        logger.info(f"Client connected. Total clients: {len(self.clients)}")
        
        try:
            async for message in websocket:
                await self.process_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            logger.info("Client disconnected")
        except Exception as e:
            logger.error(f"Error handling client: {e}")
        finally:
            self.clients.remove(websocket)
            logger.info(f"Client disconnected. Total clients: {len(self.clients)}")
    
    async def process_message(self, websocket, message: str):
        """Process incoming WebSocket message"""
        try:
            # Parse JSON message
            data = json.loads(message)
            
            # Handle different message types
            if data.get("type") == "detection_request":
                await self.handle_detection_request(websocket, data)
            elif data.get("type") == "ping":
                await websocket.send(json.dumps({"type": "pong", "timestamp": data.get("timestamp")}))
            else:
                logger.warning(f"Unknown message type: {data.get('type')}")
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON message received")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    async def handle_detection_request(self, websocket, data: dict):
        """Handle animal detection request"""
        try:
            # Create detection request
            request = DetectionRequest(
                image_data=data["image_data"],
                image_id=data.get("image_id", "unknown"),
                timestamp=data.get("timestamp", 0)
            )
            
            # Process detection
            response = self.classifier.process_detection_request(request)
            
            # Send response
            response_data = {
                "type": "detection_response",
                "data": response.dict()
            }
            
            await websocket.send(json.dumps(response_data))
            
        except Exception as e:
            logger.error(f"Error handling detection request: {e}")
            # Send error response
            error_response = {
                "type": "detection_response",
                "error": str(e),
                "data": {
                    "image_id": data.get("image_id", "unknown"),
                    "detections": [],
                    "processing_time": 0,
                    "timestamp": 0
                }
            }
            await websocket.send(json.dumps(error_response))
    
    async def start_server(self):
        """Start the WebSocket server"""
        logger.info(f"Starting WebSocket server on {self.host}:{self.port}")
        
        async with serve(self.handle_client, self.host, self.port):
            logger.success(f"WebSocket server running on ws://{self.host}:{self.port}")
            await asyncio.Future()  # Run forever

async def main():
    """Main function to run the animal classifier server"""
    try:
        # Initialize classifier
        classifier = AnimalClassifier(
            model_path="yolov8n.pt",
            confidence_threshold=0.1
        )
        
        # Start WebSocket server
        server = WebSocketServer(classifier)
        await server.start_server()
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
