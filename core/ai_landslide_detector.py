#!/usr/bin/env python3
"""
AI Landslide Detection Module
This module implements AI-based landslide detection using lightweight models
optimized for Raspberry Pi deployment.
"""

import os
import cv2
import numpy as np
import tensorflow as tf
from tensorflow import lite as tflite
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import json
import requests
from PIL import Image
import io

# Configure logging
logger = logging.getLogger(__name__)

class LandslideDetector:
    """AI-based landslide detection using lightweight models"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model = None
        self.interpreter = None
        self.input_details = None
        self.output_details = None
        self.class_names = ['normal', 'landslide']
        self.confidence_threshold = config.get('confidence_threshold', 0.7)
        self.model_path = config.get('model_path', 'models/landslide_detector.tflite')
        
        # Initialize model
        self.load_model()
    
    def load_model(self) -> bool:
        """Load the TensorFlow Lite model"""
        try:
            model_path = Path(self.model_path)
            
            if not model_path.exists():
                logger.warning(f"Model file not found: {model_path}")
                logger.info("Attempting to download pre-trained model...")
                if not self.download_pretrained_model():
                    logger.error("Failed to download pre-trained model")
                    return False
            
            # Load TensorFlow Lite model
            self.interpreter = tflite.Interpreter(model_path=str(model_path))
            self.interpreter.allocate_tensors()
            
            # Get input and output details
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
            
            logger.info(f"Model loaded successfully: {model_path}")
            logger.info(f"Input shape: {self.input_details[0]['shape']}")
            logger.info(f"Output shape: {self.output_details[0]['shape']}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
    
    def download_pretrained_model(self) -> bool:
        """Download a pre-trained model (placeholder for actual implementation)"""
        try:
            # Create models directory
            models_dir = Path(self.model_path).parent
            models_dir.mkdir(exist_ok=True)
            
            # For now, create a simple placeholder model
            # In a real implementation, this would download from a model repository
            logger.info("Creating placeholder model for demonstration...")
            self.create_placeholder_model()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to download model: {e}")
            return False
    
    def create_placeholder_model(self):
        """Create a placeholder TensorFlow Lite model for demonstration"""
        try:
            # Create a simple CNN model
            model = tf.keras.Sequential([
                tf.keras.layers.Conv2D(32, 3, activation='relu', input_shape=(224, 224, 3)),
                tf.keras.layers.MaxPooling2D(),
                tf.keras.layers.Conv2D(64, 3, activation='relu'),
                tf.keras.layers.MaxPooling2D(),
                tf.keras.layers.Conv2D(64, 3, activation='relu'),
                tf.keras.layers.Flatten(),
                tf.keras.layers.Dense(64, activation='relu'),
                tf.keras.layers.Dense(2, activation='softmax')  # 2 classes: normal, landslide
            ])
            
            # Compile the model
            model.compile(
                optimizer='adam',
                loss='sparse_categorical_crossentropy',
                metrics=['accuracy']
            )
            
            # Convert to TensorFlow Lite
            converter = tf.lite.TFLiteConverter.from_keras_model(model)
            converter.optimizations = [tf.lite.Optimize.DEFAULT]
            tflite_model = converter.convert()
            
            # Save the model
            models_dir = Path(self.model_path).parent
            models_dir.mkdir(exist_ok=True)
            
            with open(self.model_path, 'wb') as f:
                f.write(tflite_model)
            
            logger.info(f"Placeholder model created: {self.model_path}")
            
        except Exception as e:
            logger.error(f"Failed to create placeholder model: {e}")
            raise
    
    def preprocess_image(self, image_path: str) -> Optional[np.ndarray]:
        """Preprocess image for model input"""
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Failed to load image: {image_path}")
                return None
            
            # Convert BGR to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Get input shape from model
            input_shape = self.input_details[0]['shape']
            target_height, target_width = input_shape[1], input_shape[2]
            
            # Resize image
            image = cv2.resize(image, (target_width, target_height))
            
            # Normalize pixel values
            image = image.astype(np.float32) / 255.0
            
            # Add batch dimension
            image = np.expand_dims(image, axis=0)
            
            return image
            
        except Exception as e:
            logger.error(f"Failed to preprocess image: {e}")
            return None
    
    def detect_landslide(self, image_path: str) -> Dict[str, Any]:
        """Detect landslide in the given image"""
        try:
            if not self.interpreter:
                logger.error("Model not loaded")
                return {
                    'success': False,
                    'error': 'Model not loaded',
                    'confidence': 0.0,
                    'prediction': 'unknown'
                }
            
            # Preprocess image
            processed_image = self.preprocess_image(image_path)
            if processed_image is None:
                return {
                    'success': False,
                    'error': 'Failed to preprocess image',
                    'confidence': 0.0,
                    'prediction': 'unknown'
                }
            
            # Run inference
            self.interpreter.set_tensor(self.input_details[0]['index'], processed_image)
            self.interpreter.invoke()
            
            # Get prediction
            output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
            predictions = output_data[0]
            
            # Get class with highest confidence
            predicted_class_idx = np.argmax(predictions)
            confidence = float(predictions[predicted_class_idx])
            predicted_class = self.class_names[predicted_class_idx]
            
            # Determine if landslide detected
            landslide_detected = (predicted_class == 'landslide' and 
                                confidence >= self.confidence_threshold)
            
            result = {
                'success': True,
                'landslide_detected': landslide_detected,
                'prediction': predicted_class,
                'confidence': confidence,
                'all_predictions': {
                    self.class_names[i]: float(predictions[i]) 
                    for i in range(len(self.class_names))
                },
                'timestamp': datetime.now().isoformat(),
                'image_path': image_path
            }
            
            logger.info(f"Detection result: {predicted_class} (confidence: {confidence:.3f})")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to detect landslide: {e}")
            return {
                'success': False,
                'error': str(e),
                'confidence': 0.0,
                'prediction': 'unknown'
            }
    
    def batch_detect(self, image_paths: List[str]) -> List[Dict[str, Any]]:
        """Detect landslides in multiple images"""
        results = []
        
        for image_path in image_paths:
            result = self.detect_landslide(image_path)
            results.append(result)
        
        return results
    
    def analyze_time_series(self, image_directory: str) -> Dict[str, Any]:
        """Analyze a time series of images for landslide progression"""
        try:
            image_dir = Path(image_directory)
            if not image_dir.exists():
                return {'error': 'Image directory not found'}
            
            # Get all image files sorted by name (assuming timestamp in filename)
            image_files = sorted([
                f for f in image_dir.glob('*.jpg') 
                if f.is_file()
            ])
            
            if not image_files:
                return {'error': 'No image files found'}
            
            # Analyze each image
            results = []
            landslide_detections = []
            
            for image_file in image_files:
                result = self.detect_landslide(str(image_file))
                results.append(result)
                
                if result.get('landslide_detected', False):
                    landslide_detections.append({
                        'timestamp': result['timestamp'],
                        'confidence': result['confidence'],
                        'image_path': str(image_file)
                    })
            
            # Calculate statistics
            total_images = len(results)
            successful_analyses = sum(1 for r in results if r.get('success', False))
            landslide_count = len(landslide_detections)
            
            analysis = {
                'total_images': total_images,
                'successful_analyses': successful_analyses,
                'landslide_detections': landslide_count,
                'detection_rate': landslide_count / total_images if total_images > 0 else 0,
                'detections': landslide_detections,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            # Check for landslide progression
            if landslide_count > 0:
                analysis['first_detection'] = landslide_detections[0]
                analysis['latest_detection'] = landslide_detections[-1]
                analysis['progression_detected'] = landslide_count > 1
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze time series: {e}")
            return {'error': str(e)}
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        if not self.interpreter:
            return {'error': 'Model not loaded'}
        
        return {
            'model_path': self.model_path,
            'input_shape': self.input_details[0]['shape'].tolist(),
            'output_shape': self.output_details[0]['shape'].tolist(),
            'class_names': self.class_names,
            'confidence_threshold': self.confidence_threshold,
            'model_size_mb': Path(self.model_path).stat().st_size / (1024 * 1024)
        }

class LandslideAlertSystem:
    """Alert system for landslide detection"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.detector = LandslideDetector(config.get('detector', {}))
        self.alert_threshold = config.get('alert_threshold', 0.8)
        self.notification_config = config.get('notifications', {})
    
    def check_image(self, image_path: str) -> Dict[str, Any]:
        """Check a single image and trigger alerts if needed"""
        result = self.detector.detect_landslide(image_path)
        
        if (result.get('landslide_detected', False) and 
            result.get('confidence', 0) >= self.alert_threshold):
            
            # Trigger alert
            alert_result = self.trigger_alert(result)
            result['alert_triggered'] = True
            result['alert_result'] = alert_result
        else:
            result['alert_triggered'] = False
        
        return result
    
    def trigger_alert(self, detection_result: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger landslide alert notifications"""
        try:
            alert_data = {
                'timestamp': datetime.now().isoformat(),
                'confidence': detection_result.get('confidence', 0),
                'image_path': detection_result.get('image_path', ''),
                'location': self.config.get('location', 'Unknown'),
                'severity': self.get_severity_level(detection_result.get('confidence', 0))
            }
            
            notifications_sent = []
            
            # Email notification
            if self.notification_config.get('email_enabled', False):
                email_result = self.send_email_alert(alert_data)
                notifications_sent.append(email_result)
            
            # Webhook notification
            if self.notification_config.get('webhook_enabled', False):
                webhook_result = self.send_webhook_alert(alert_data)
                notifications_sent.append(webhook_result)
            
            logger.warning(f"LANDSLIDE ALERT: Confidence {alert_data['confidence']:.3f} at {alert_data['location']}")
            
            return {
                'success': True,
                'alert_data': alert_data,
                'notifications_sent': notifications_sent
            }
            
        except Exception as e:
            logger.error(f"Failed to trigger alert: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_severity_level(self, confidence: float) -> str:
        """Determine severity level based on confidence"""
        if confidence >= 0.9:
            return 'HIGH'
        elif confidence >= 0.8:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def send_email_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send email alert (placeholder implementation)"""
        try:
            # In a real implementation, this would use SMTP to send emails
            logger.info(f"Email alert would be sent: {alert_data}")
            return {'type': 'email', 'success': True}
        except Exception as e:
            return {'type': 'email', 'success': False, 'error': str(e)}
    
    def send_webhook_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send webhook alert"""
        try:
            webhook_url = self.notification_config.get('webhook_url')
            if not webhook_url:
                return {'type': 'webhook', 'success': False, 'error': 'No webhook URL configured'}
            
            response = requests.post(webhook_url, json=alert_data, timeout=10)
            response.raise_for_status()
            
            return {'type': 'webhook', 'success': True, 'status_code': response.status_code}
            
        except Exception as e:
            return {'type': 'webhook', 'success': False, 'error': str(e)}

# Example usage and testing
if __name__ == "__main__":
    # Example configuration
    config = {
        'detector': {
            'model_path': 'models/landslide_detector.tflite',
            'confidence_threshold': 0.7
        },
        'alert_threshold': 0.8,
        'location': 'Test Site',
        'notifications': {
            'email_enabled': False,
            'webhook_enabled': False,
            'webhook_url': 'https://example.com/webhook'
        }
    }
    
    # Test the detector
    try:
        detector = LandslideDetector(config['detector'])
        
        # Get model info
        model_info = detector.get_model_info()
        print("Model Info:")
        print(json.dumps(model_info, indent=2))
        
        # Test with a sample image (if available)
        test_image = "test_image.jpg"
        if Path(test_image).exists():
            result = detector.detect_landslide(test_image)
            print("\nDetection Result:")
            print(json.dumps(result, indent=2))
        else:
            print(f"\nTest image not found: {test_image}")
            print("Create a test image to run detection")
        
    except Exception as e:
        print(f"Error testing detector: {e}")

