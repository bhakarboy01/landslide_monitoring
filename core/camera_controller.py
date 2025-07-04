#!/usr/bin/env python3
"""
Landslide Monitoring System - Camera Control Module
This script handles camera operations for both Raspberry Pi Camera and DSLR cameras
"""

import os
import time
import datetime
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('landslide_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CameraController:
    """Base class for camera control"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.image_dir = Path(config.get('image_directory', './images'))
        self.image_dir.mkdir(exist_ok=True)
        
    def capture_image(self, filename: Optional[str] = None) -> str:
        """Capture an image and return the filename"""
        raise NotImplementedError("Subclasses must implement capture_image")
    
    def get_status(self) -> Dict[str, Any]:
        """Get camera status information"""
        return {"status": "unknown", "type": "base"}

class PiCameraController(CameraController):
    """Controller for Raspberry Pi Camera Module"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        try:
            # Try importing picamera2 (newer) first, then fall back to picamera
            try:
                from picamera2 import Picamera2
                self.camera = Picamera2()
                self.camera_type = "picamera2"
                logger.info("Using picamera2 library")
            except ImportError:
                from picamera import PiCamera
                self.camera = PiCamera()
                self.camera_type = "picamera"
                logger.info("Using legacy picamera library")
                
            self.resolution = config.get('resolution', (2592, 1944))
            self.quality = config.get('quality', 95)
            
            if self.camera_type == "picamera2":
                self.camera.configure(self.camera.create_still_configuration())
                self.camera.start()
            else:
                self.camera.resolution = self.resolution
                
        except Exception as e:
            logger.error(f"Failed to initialize Pi Camera: {e}")
            raise
    
    def capture_image(self, filename: Optional[str] = None) -> str:
        """Capture an image using Pi Camera"""
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"landslide_{timestamp}.jpg"
        
        filepath = self.image_dir / filename
        
        try:
            if self.camera_type == "picamera2":
                self.camera.capture_file(str(filepath))
            else:
                self.camera.capture(str(filepath), quality=self.quality)
                
            logger.info(f"Image captured: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Failed to capture image: {e}")
            raise
    
    def get_status(self) -> Dict[str, Any]:
        """Get Pi Camera status"""
        return {
            "status": "active",
            "type": "pi_camera",
            "library": self.camera_type,
            "resolution": self.resolution,
            "quality": self.quality
        }
    
    def __del__(self):
        """Cleanup camera resources"""
        try:
            if hasattr(self, 'camera'):
                if self.camera_type == "picamera2":
                    self.camera.stop()
                else:
                    self.camera.close()
        except:
            pass

class DSLRController(CameraController):
    """Controller for DSLR cameras using gphoto2"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.gphoto2_available = self._check_gphoto2()
        if not self.gphoto2_available:
            raise RuntimeError("gphoto2 not available. Install with: sudo apt-get install gphoto2")
        
        self.camera_model = self._detect_camera()
        if not self.camera_model:
            raise RuntimeError("No compatible DSLR camera detected")
            
        logger.info(f"DSLR camera detected: {self.camera_model}")
    
    def _check_gphoto2(self) -> bool:
        """Check if gphoto2 is available"""
        try:
            result = os.system("which gphoto2 > /dev/null 2>&1")
            return result == 0
        except:
            return False
    
    def _detect_camera(self) -> Optional[str]:
        """Detect connected DSLR camera"""
        try:
            import subprocess
            result = subprocess.run(
                ["gphoto2", "--auto-detect"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0 and "usb:" in result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if "usb:" in line:
                        return line.split()[0]
            return None
        except Exception as e:
            logger.error(f"Failed to detect DSLR camera: {e}")
            return None
    
    def capture_image(self, filename: Optional[str] = None) -> str:
        """Capture an image using DSLR camera"""
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"landslide_dslr_{timestamp}.jpg"
        
        filepath = self.image_dir / filename
        
        try:
            import subprocess
            
            # Capture image and download it
            result = subprocess.run([
                "gphoto2",
                "--capture-image-and-download",
                "--filename", str(filepath)
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info(f"DSLR image captured: {filepath}")
                return str(filepath)
            else:
                logger.error(f"gphoto2 error: {result.stderr}")
                raise RuntimeError(f"Failed to capture DSLR image: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.error("DSLR capture timeout")
            raise RuntimeError("DSLR capture timeout")
        except Exception as e:
            logger.error(f"Failed to capture DSLR image: {e}")
            raise
    
    def set_zoom(self, zoom_level: int) -> bool:
        """Attempt to set zoom level (if supported by camera/lens)"""
        try:
            import subprocess
            
            # This is camera/lens dependent and may not work for all models
            result = subprocess.run([
                "gphoto2",
                "--set-config",
                f"zoom={zoom_level}"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logger.info(f"Zoom set to level: {zoom_level}")
                return True
            else:
                logger.warning(f"Zoom control not supported or failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to set zoom: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get DSLR camera status"""
        return {
            "status": "active",
            "type": "dslr",
            "model": self.camera_model,
            "gphoto2_available": self.gphoto2_available
        }

def create_camera_controller(config: Dict[str, Any]) -> CameraController:
    """Factory function to create appropriate camera controller"""
    camera_type = config.get('camera_type', 'pi_camera')
    
    if camera_type == 'pi_camera':
        return PiCameraController(config)
    elif camera_type == 'dslr':
        return DSLRController(config)
    else:
        raise ValueError(f"Unsupported camera type: {camera_type}")

# Example usage and testing
if __name__ == "__main__":
    # Example configuration
    config = {
        'camera_type': 'pi_camera',  # or 'dslr'
        'image_directory': './images',
        'resolution': (2592, 1944),
        'quality': 95
    }
    
    try:
        # Create camera controller
        camera = create_camera_controller(config)
        
        # Get camera status
        status = camera.get_status()
        print(f"Camera Status: {json.dumps(status, indent=2)}")
        
        # Capture a test image
        print("Capturing test image...")
        image_path = camera.capture_image("test_image.jpg")
        print(f"Image saved to: {image_path}")
        
    except Exception as e:
        logger.error(f"Error in camera test: {e}")
        print(f"Error: {e}")

