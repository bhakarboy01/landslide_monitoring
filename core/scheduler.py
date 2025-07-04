#!/usr/bin/env python3
"""
Landslide Monitoring System - Scheduler Module
This script handles automated image capture at user-defined intervals
"""

import time
import json
import threading
import signal
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional
import logging

from camera_controller import create_camera_controller, CameraController

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('landslide_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LandslideScheduler:
    """Main scheduler class for automated landslide monitoring"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.camera: Optional[CameraController] = None
        self.running = False
        self.scheduler_thread: Optional[threading.Thread] = None
        self.last_capture_time: Optional[datetime] = None
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Initialize camera
        self.initialize_camera()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        config_path = Path(self.config_file)
        
        # Default configuration
        default_config = {
            "camera_type": "pi_camera",
            "image_directory": "./images",
            "resolution": [2592, 1944],
            "quality": 95,
            "capture_interval_minutes": 60,
            "enable_scheduler": True,
            "max_images": 1000,
            "image_prefix": "landslide",
            "timezone": "UTC"
        }
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
                    logger.info(f"Configuration loaded from {config_path}")
            except Exception as e:
                logger.error(f"Failed to load config file: {e}")
                logger.info("Using default configuration")
        else:
            # Create default config file
            self.save_config(default_config)
            logger.info(f"Created default configuration file: {config_path}")
        
        return default_config
    
    def save_config(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Save configuration to JSON file"""
        if config is None:
            config = self.config
            
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            logger.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
    def initialize_camera(self) -> None:
        """Initialize the camera controller"""
        try:
            self.camera = create_camera_controller(self.config)
            logger.info("Camera initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize camera: {e}")
            raise
    
    def capture_image(self) -> Optional[str]:
        """Capture a single image"""
        if not self.camera:
            logger.error("Camera not initialized")
            return None
        
        try:
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            prefix = self.config.get('image_prefix', 'landslide')
            filename = f"{prefix}_{timestamp}.jpg"
            
            # Capture image
            image_path = self.camera.capture_image(filename)
            self.last_capture_time = datetime.now()
            
            # Log capture info
            logger.info(f"Image captured: {image_path}")
            
            # Check if we need to clean up old images
            self.cleanup_old_images()
            
            return image_path
            
        except Exception as e:
            logger.error(f"Failed to capture image: {e}")
            return None
    
    def cleanup_old_images(self) -> None:
        """Remove old images if max_images limit is exceeded"""
        max_images = self.config.get('max_images', 1000)
        if max_images <= 0:
            return
        
        try:
            image_dir = Path(self.config.get('image_directory', './images'))
            if not image_dir.exists():
                return
            
            # Get all image files sorted by modification time
            image_files = list(image_dir.glob('*.jpg'))
            image_files.sort(key=lambda x: x.stat().st_mtime)
            
            # Remove oldest files if we exceed the limit
            if len(image_files) > max_images:
                files_to_remove = image_files[:-max_images]
                for file_path in files_to_remove:
                    try:
                        file_path.unlink()
                        logger.info(f"Removed old image: {file_path}")
                    except Exception as e:
                        logger.error(f"Failed to remove {file_path}: {e}")
                        
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def scheduler_loop(self) -> None:
        """Main scheduler loop"""
        logger.info("Scheduler loop started")
        
        while self.running:
            try:
                # Capture image
                image_path = self.capture_image()
                
                if image_path:
                    logger.info(f"Scheduled capture completed: {image_path}")
                else:
                    logger.error("Scheduled capture failed")
                
                # Calculate next capture time
                interval_minutes = self.config.get('capture_interval_minutes', 60)
                next_capture = datetime.now() + timedelta(minutes=interval_minutes)
                logger.info(f"Next capture scheduled for: {next_capture.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Wait for the specified interval
                sleep_seconds = interval_minutes * 60
                
                # Sleep in small chunks to allow for responsive shutdown
                for _ in range(int(sleep_seconds)):
                    if not self.running:
                        break
                    time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                # Wait a bit before retrying
                time.sleep(60)
        
        logger.info("Scheduler loop stopped")
    
    def start_scheduler(self) -> None:
        """Start the automated scheduler"""
        if self.running:
            logger.warning("Scheduler is already running")
            return
        
        if not self.config.get('enable_scheduler', True):
            logger.info("Scheduler is disabled in configuration")
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self.scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        logger.info("Scheduler started")
    
    def stop_scheduler(self) -> None:
        """Stop the automated scheduler"""
        if not self.running:
            logger.warning("Scheduler is not running")
            return
        
        logger.info("Stopping scheduler...")
        self.running = False
        
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        
        logger.info("Scheduler stopped")
    
    def update_interval(self, minutes: int) -> None:
        """Update capture interval"""
        if minutes <= 0:
            raise ValueError("Interval must be positive")
        
        self.config['capture_interval_minutes'] = minutes
        self.save_config()
        logger.info(f"Capture interval updated to {minutes} minutes")
    
    def get_status(self) -> Dict[str, Any]:
        """Get system status"""
        camera_status = self.camera.get_status() if self.camera else {"status": "not_initialized"}
        
        return {
            "scheduler_running": self.running,
            "capture_interval_minutes": self.config.get('capture_interval_minutes', 60),
            "last_capture_time": self.last_capture_time.isoformat() if self.last_capture_time else None,
            "camera": camera_status,
            "image_directory": self.config.get('image_directory', './images'),
            "max_images": self.config.get('max_images', 1000)
        }
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.stop_scheduler()
        sys.exit(0)

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Landslide Monitoring Scheduler")
    parser.add_argument("--config", default="config.json", help="Configuration file path")
    parser.add_argument("--capture", action="store_true", help="Capture a single image and exit")
    parser.add_argument("--interval", type=int, help="Update capture interval (minutes)")
    parser.add_argument("--status", action="store_true", help="Show system status")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon (default)")
    
    args = parser.parse_args()
    
    try:
        # Create scheduler instance
        scheduler = LandslideScheduler(args.config)
        
        if args.capture:
            # Single capture mode
            print("Capturing single image...")
            image_path = scheduler.capture_image()
            if image_path:
                print(f"Image captured: {image_path}")
            else:
                print("Failed to capture image")
                sys.exit(1)
                
        elif args.interval:
            # Update interval mode
            scheduler.update_interval(args.interval)
            print(f"Capture interval updated to {args.interval} minutes")
            
        elif args.status:
            # Status mode
            status = scheduler.get_status()
            print(json.dumps(status, indent=2))
            
        else:
            # Daemon mode (default)
            print("Starting landslide monitoring scheduler...")
            print(f"Configuration: {args.config}")
            print(f"Capture interval: {scheduler.config.get('capture_interval_minutes', 60)} minutes")
            print("Press Ctrl+C to stop")
            
            scheduler.start_scheduler()
            
            # Keep main thread alive
            try:
                while scheduler.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nShutdown requested...")
                scheduler.stop_scheduler()
    
    except Exception as e:
        logger.error(f"Error in main: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

