# MentraOS Animal Classification Demo Implementation Guide

## Overview

This document outlines the implementation plan for creating a demo application for MentraOS smart glasses that uses computer vision to classify animals in real-time. The demo will leverage OpenCV for camera access and pretrained deep learning models for animal classification.

## Technology Stack

### 1. MentraOS SDK
- **Library**: `@mentra/sdk`
- **Purpose**: Core framework for developing MentraOS applications
- **Key Features**:
  - Real-time camera access through glasses
  - AR display capabilities (text walls, reference cards, dashboard cards)
  - Event handling (transcription, location, battery, etc.)
  - Settings management
  - Session management and logging

### 2. OpenCV Integration
- **Library**: OpenCV (Python/C++ or JavaScript via OpenCV.js)
- **Purpose**: Computer vision processing and camera operations
- **Key Capabilities**:
  - Camera capture and frame processing
  - Image preprocessing for ML models
  - Real-time video stream handling
  - Image manipulation and enhancement

### 3. Pretrained Animal Classification Models

#### Option A: YOLO Models (Recommended)
- **YOLOv8/YOLOv9**: Latest versions with excellent animal detection
- **YOLOv5**: Stable, well-documented, good performance
- **YOLO-NAS**: Neural Architecture Search optimized for speed/accuracy
- **COCO Dataset**: 80 classes including many animals (dog, cat, horse, sheep, cow, elephant, bear, zebra, giraffe, etc.)
- **Advantages**: 
  - Real-time object detection (multiple animals in frame)
  - Bounding box detection for precise animal location
  - Excellent performance on edge devices
  - Can detect animals at various distances and angles

#### Option B: TensorFlow Lite Models
- **MobileNetV1/V2**: Lightweight, efficient for mobile devices
- **EfficientNet-Lite**: Optimized for edge devices
- **Model Zoo**: Available pretrained models for 1000+ ImageNet classes including animals

#### Option C: OpenCV DNN Module
- **Supported Formats**: ONNX, TensorFlow, Caffe, PyTorch
- **Pretrained Models**: 
  - ImageNet classification models
  - COCO object detection (includes animals)
  - Custom animal classification models

#### Option D: Hugging Face Models
- **Model Hub**: Access to thousands of pretrained models
- **Animal Classification**: Specialized models for wildlife/domestic animals
- **Easy Integration**: Simple API for model loading and inference

## Implementation Architecture

### 1. Application Structure

```
mentraOS-animal-classifier/
├── src/
│   ├── index.ts                 # Main application entry point
│   ├── camera/
│   │   ├── camera_manager.ts    # Camera initialization and management
│   │   └── frame_processor.ts   # Frame processing and ML inference
│   ├── ml/
│   │   ├── model_loader.ts      # Model loading and management
│   │   ├── classifier.ts        # Animal classification logic
│   │   └── preprocessing.ts     # Image preprocessing utilities
│   ├── ui/
│   │   ├── display_manager.ts   # AR display management
│   │   └── layout_utils.ts      # Layout utility functions
│   └── utils/
│       ├── logger.ts            # Logging utilities
│       └── config.ts            # Configuration management
├── models/                      # Pretrained model files
├── assets/                      # Static assets (labels, configs)
├── package.json
├── tsconfig.json
└── .env
```

### 2. Core Components

#### Camera Manager
```typescript
class CameraManager {
  private session: AppSession;
  private isStreaming: boolean = false;
  
  constructor(session: AppSession) {
    this.session = session;
  }
  
  async initializeCamera(): Promise<void> {
    // Initialize camera access through MentraOS
    // Set up frame capture callbacks
  }
  
  async startStreaming(): Promise<void> {
    // Start real-time camera feed
    // Process frames for ML inference
  }
  
  async stopStreaming(): Promise<void> {
    // Stop camera feed
    // Clean up resources
  }
}
```

#### ML Classifier
```typescript
class AnimalClassifier {
  private model: any; // YOLO model via OpenCV DNN or TensorFlow Lite
  private labels: string[];
  private confidenceThreshold: number = 0.5;
  
  async loadModel(modelPath: string): Promise<void> {
    // Load YOLO model (ONNX format recommended)
    // Initialize inference engine
    // Load COCO labels for animal classes
  }
  
  async detectAnimals(imageData: ImageData): Promise<DetectionResult[]> {
    // Preprocess image for YOLO input
    // Run YOLO inference
    // Filter for animal classes only
    // Return detections with bounding boxes and confidence scores
  }
  
  private preprocessImage(image: ImageData): any {
    // Resize to YOLO input size (640x640 for YOLOv8)
    // Normalize pixel values (0-255 to 0-1)
    // Convert to blob format for OpenCV DNN
  }
  
  private filterAnimalDetections(detections: any[]): DetectionResult[] {
    // Filter COCO classes to only include animals
    // Apply confidence threshold
    // Return animal-specific detections
  }
}
```

#### Display Manager
```typescript
class DisplayManager {
  private session: AppSession;
  
  constructor(session: AppSession) {
    this.session = session;
  }
  
  showDetectionResults(detections: DetectionResult[]): void {
    // Display detected animals with bounding boxes
    // Show animal names and confidence scores
    // Display additional information (habitat, facts)
    // Update dashboard with real-time stats
  }
  
  showError(message: string): void {
    // Display error messages
    // Provide user guidance
  }
  
  updateDashboard(stats: ClassificationStats): void {
    // Update real-time statistics
    // Show battery level, connection status
  }
}
```

## Implementation Steps

### Phase 1: Basic Setup and Camera Access

1. **Initialize MentraOS Project**
   ```bash
   # Create new project from template
   gh repo create --template Mentra-Community/MentraOS-Cloud-Example-App mentraOS-animal-classifier
   cd mentraOS-animal-classifier
   
   # Install dependencies
   bun install
   
   # Set up environment
   cp .env.example .env
   # Configure MENTRAOS_API_KEY and other settings
   ```

2. **Camera Integration**
   - Implement camera access through MentraOS SDK
   - Set up frame capture and processing pipeline
   - Test real-time video streaming

3. **Basic UI Framework**
   - Implement AR display components
   - Create layout management system
   - Set up dashboard and status displays

### Phase 2: ML Model Integration

1. **Model Selection and Download**
   ```python
   # Example: Download YOLOv8 for animal detection
   import cv2
   import numpy as np
   
   # Download YOLOv8 ONNX model
   model_url = "https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt"
   
   # COCO dataset includes these animal classes:
   animal_classes = [
       0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
       21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39,
       40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59,
       60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79
   ]
   
   # Key animal classes in COCO:
   # 15: cat, 16: dog, 17: horse, 18: sheep, 19: cow, 20: elephant, 21: bear, 22: zebra, 23: giraffe
   ```

2. **Model Conversion**
   - Convert models to TensorFlow Lite format
   - Optimize for edge inference
   - Test model performance and accuracy

3. **Inference Pipeline**
   - Implement image preprocessing
   - Set up real-time inference
   - Add result post-processing

### Phase 3: Animal Classification Logic

1. **Animal Detection Filtering**
   ```typescript
   // COCO dataset animal class IDs
   const ANIMAL_CLASS_IDS = [15, 16, 17, 18, 19, 20, 21, 22, 23]; // cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe
   const ANIMAL_CLASS_NAMES = ['cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe'];
   
   function filterAnimalDetections(detections: Detection[]): AnimalDetection[] {
     return detections
       .filter(detection => ANIMAL_CLASS_IDS.includes(detection.classId))
       .map(detection => ({
         ...detection,
         animalType: ANIMAL_CLASS_NAMES[ANIMAL_CLASS_IDS.indexOf(detection.classId)],
         boundingBox: detection.bbox,
         confidence: detection.confidence
       }));
   }
   ```

2. **Confidence Thresholding**
   - Set minimum confidence thresholds
   - Implement result filtering
   - Add uncertainty handling

3. **Real-time Processing**
   - Optimize for low latency
   - Implement frame skipping if needed
   - Add performance monitoring

### Phase 4: Enhanced Features

1. **Voice Commands**
   ```typescript
   // Voice activation for camera control
   session.events.onTranscription((data) => {
     if (data.isFinal) {
       const command = data.text.toLowerCase().trim();
       
       if (command.includes('start camera')) {
         cameraManager.startStreaming();
       } else if (command.includes('stop camera')) {
         cameraManager.stopStreaming();
       } else if (command.includes('what animal')) {
         // Trigger classification
       }
     }
   });
   ```

2. **Location-Based Features**
   - Use GPS for habitat information
   - Provide local wildlife facts
   - Track animal sightings

3. **Battery and Performance Optimization**
   - Monitor battery usage
   - Adjust processing frequency
   - Implement power-saving modes

## Model Options and Recommendations

### 1. YOLO Models (Recommended)

**YOLOv8n (Recommended for MVP)**
- Size: ~6MB (nano version)
- Accuracy: Excellent for animal detection
- Speed: Very fast inference (~10ms on modern devices)
- Classes: 80 COCO classes (includes 8+ animal types)
- Features: Bounding box detection, multiple objects per frame

**YOLOv8s (Small)**
- Size: ~22MB
- Accuracy: Better than nano version
- Speed: Still very fast (~20ms)
- Classes: 80 COCO classes
- Features: Better accuracy for distant animals

**YOLOv9 (Latest)**
- Size: ~20MB
- Accuracy: State-of-the-art
- Speed: Optimized for edge devices
- Classes: 80 COCO classes
- Features: Latest improvements in accuracy and speed

### 2. TensorFlow Lite Models

### 3. OpenCV DNN Models

**YOLO Object Detection**
- Can detect multiple animals in frame
- Provides bounding boxes
- Good for wildlife photography

**ImageNet Classification Models**
- High accuracy for single animal classification
- Fast inference with OpenCV DNN backend

### 4. Specialized Animal Models

**Hugging Face Animal Classification**
- Models specifically trained on animal datasets
- Better accuracy for wildlife
- Smaller class sets (focus on animals only)

## Performance Considerations

### 1. Latency Optimization
- Target: <500ms end-to-end latency
- Frame processing: <200ms
- Model inference: <150ms
- Display update: <50ms

### 2. Battery Management
- Monitor battery level continuously
- Adjust processing frequency based on battery
- Implement sleep modes when not in use

### 3. Memory Usage
- Optimize model size for edge devices
- Implement efficient frame buffering
- Monitor memory leaks

## Testing Strategy

### 1. Unit Testing
- Test individual components
- Mock camera and ML model interfaces
- Validate preprocessing functions

### 2. Integration Testing
- Test camera-to-ML pipeline
- Validate AR display integration
- Test voice command integration

### 3. Performance Testing
- Measure inference latency
- Test battery consumption
- Validate memory usage

### 4. User Testing
- Test with real MentraOS glasses
- Validate user experience
- Gather feedback on accuracy and usability

## Deployment and Distribution

### 1. Model Distribution
- Package models with application
- Implement model versioning
- Add model update capabilities

### 2. Application Deployment
- Deploy to MentraOS app store
- Implement over-the-air updates
- Monitor application performance

### 3. Analytics and Monitoring
- Track classification accuracy
- Monitor user engagement
- Collect performance metrics

## Future Enhancements

### 1. Advanced Features
- Multi-animal detection in single frame
- Animal behavior analysis
- Species identification with subspecies
- Conservation status information

### 2. Social Features
- Share animal sightings
- Community-driven animal database
- Wildlife photography tips

### 3. Educational Content
- Animal facts and information
- Habitat and behavior details
- Conservation education

## Conclusion

This implementation guide provides a comprehensive roadmap for creating an animal classification demo for MentraOS glasses. The approach leverages proven technologies (OpenCV, TensorFlow Lite) while taking advantage of MentraOS's unique capabilities for AR display and real-time processing.

The modular architecture allows for iterative development and easy enhancement. Starting with basic camera access and a simple classification model, the application can be progressively enhanced with more sophisticated features and better-performing models.

Key success factors include:
- Optimizing for low latency and battery efficiency
- Ensuring high classification accuracy
- Creating an intuitive user experience
- Maintaining robust error handling and recovery

This demo showcases the potential of MentraOS for real-world computer vision applications while providing a foundation for more advanced wildlife and nature applications.
