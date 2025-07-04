"""
Landslide Monitoring System API Routes
This module provides REST API endpoints for the web interface
"""

import os
import sys
import json
import zipfile
import tempfile
from datetime import datetime
from pathlib import Path
from flask import Blueprint, request, jsonify, send_file, send_from_directory
from flask_cors import cross_origin

# Add parent directory to path to import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    from scheduler import LandslideScheduler
    from camera_controller import create_camera_controller
except ImportError as e:
    print(f"Warning: Could not import landslide modules: {e}")
    LandslideScheduler = None
    create_camera_controller = None

landslide_bp = Blueprint('landslide', __name__)

# Global scheduler instance
scheduler_instance = None

def get_scheduler():
    """Get or create scheduler instance"""
    global scheduler_instance
    if scheduler_instance is None and LandslideScheduler is not None:
        try:
            # Use config from parent directory
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.json')
            scheduler_instance = LandslideScheduler(config_path)
        except Exception as e:
            print(f"Failed to initialize scheduler: {e}")
            return None
    return scheduler_instance

@landslide_bp.route('/status', methods=['GET'])
@cross_origin()
def get_status():
    """Get system status"""
    try:
        scheduler = get_scheduler()
        if scheduler is None:
            return jsonify({
                'error': 'Scheduler not available',
                'scheduler_running': False,
                'camera': {'status': 'not_available'}
            }), 500
        
        status = scheduler.get_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@landslide_bp.route('/capture', methods=['POST'])
@cross_origin()
def capture_image():
    """Capture a single image"""
    try:
        scheduler = get_scheduler()
        if scheduler is None:
            return jsonify({'error': 'Scheduler not available'}), 500
        
        image_path = scheduler.capture_image()
        if image_path:
            filename = os.path.basename(image_path)
            return jsonify({
                'success': True,
                'filename': filename,
                'path': image_path,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({'error': 'Failed to capture image'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@landslide_bp.route('/interval', methods=['POST'])
@cross_origin()
def update_interval():
    """Update capture interval"""
    try:
        data = request.get_json()
        minutes = data.get('minutes')
        
        if not minutes or minutes < 1 or minutes > 1440:
            return jsonify({'error': 'Invalid interval. Must be between 1 and 1440 minutes.'}), 400
        
        scheduler = get_scheduler()
        if scheduler is None:
            return jsonify({'error': 'Scheduler not available'}), 500
        
        scheduler.update_interval(minutes)
        return jsonify({
            'success': True,
            'interval_minutes': minutes,
            'message': f'Capture interval updated to {minutes} minutes'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@landslide_bp.route('/scheduler/start', methods=['POST'])
@cross_origin()
def start_scheduler():
    """Start the scheduler"""
    try:
        scheduler = get_scheduler()
        if scheduler is None:
            return jsonify({'error': 'Scheduler not available'}), 500
        
        scheduler.start_scheduler()
        return jsonify({
            'success': True,
            'message': 'Scheduler started successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@landslide_bp.route('/scheduler/stop', methods=['POST'])
@cross_origin()
def stop_scheduler():
    """Stop the scheduler"""
    try:
        scheduler = get_scheduler()
        if scheduler is None:
            return jsonify({'error': 'Scheduler not available'}), 500
        
        scheduler.stop_scheduler()
        return jsonify({
            'success': True,
            'message': 'Scheduler stopped successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@landslide_bp.route('/zoom', methods=['POST'])
@cross_origin()
def set_zoom():
    """Set camera zoom level (DSLR only)"""
    try:
        data = request.get_json()
        zoom_level = data.get('level')
        
        if zoom_level is None or zoom_level < 1 or zoom_level > 10:
            return jsonify({'error': 'Invalid zoom level. Must be between 1 and 10.'}), 400
        
        scheduler = get_scheduler()
        if scheduler is None:
            return jsonify({'error': 'Scheduler not available'}), 500
        
        # Check if camera supports zoom
        if hasattr(scheduler.camera, 'set_zoom'):
            success = scheduler.camera.set_zoom(zoom_level)
            return jsonify({
                'success': success,
                'zoom_level': zoom_level,
                'message': f'Zoom set to level {zoom_level}' if success else 'Zoom control not supported'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Current camera does not support zoom control'
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@landslide_bp.route('/camera/detect', methods=['POST'])
@cross_origin()
def detect_camera():
    """Detect and reinitialize camera"""
    try:
        scheduler = get_scheduler()
        if scheduler is None:
            return jsonify({'error': 'Scheduler not available'}), 500
        
        # Reinitialize camera
        scheduler.initialize_camera()
        camera_status = scheduler.camera.get_status()
        
        return jsonify({
            'success': True,
            'camera_type': camera_status.get('type', 'unknown'),
            'camera_status': camera_status,
            'message': 'Camera detected and initialized successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@landslide_bp.route('/config', methods=['GET', 'POST'])
@cross_origin()
def handle_config():
    """Get or update configuration"""
    try:
        scheduler = get_scheduler()
        if scheduler is None:
            return jsonify({'error': 'Scheduler not available'}), 500
        
        if request.method == 'GET':
            return jsonify(scheduler.config)
        
        elif request.method == 'POST':
            data = request.get_json()
            
            # Update configuration
            if 'camera_type' in data:
                scheduler.config['camera_type'] = data['camera_type']
            if 'quality' in data:
                scheduler.config['quality'] = data['quality']
            if 'max_images' in data:
                scheduler.config['max_images'] = data['max_images']
            
            # Save configuration
            scheduler.save_config()
            
            return jsonify({
                'success': True,
                'config': scheduler.config,
                'message': 'Configuration updated successfully'
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@landslide_bp.route('/images', methods=['GET'])
@cross_origin()
def get_images():
    """Get list of captured images"""
    try:
        scheduler = get_scheduler()
        if scheduler is None:
            return jsonify({'error': 'Scheduler not available'}), 500
        
        image_dir = Path(scheduler.config.get('image_directory', './images'))
        if not image_dir.exists():
            return jsonify([])
        
        images = []
        for image_file in sorted(image_dir.glob('*.jpg'), key=lambda x: x.stat().st_mtime, reverse=True):
            stat = image_file.stat()
            images.append({
                'filename': image_file.name,
                'timestamp': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'size': stat.st_size
            })
        
        return jsonify(images[:50])  # Return last 50 images
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@landslide_bp.route('/images/<filename>', methods=['GET'])
@cross_origin()
def get_image(filename):
    """Serve individual image file"""
    try:
        scheduler = get_scheduler()
        if scheduler is None:
            return jsonify({'error': 'Scheduler not available'}), 500
        
        image_dir = scheduler.config.get('image_directory', './images')
        return send_from_directory(image_dir, filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@landslide_bp.route('/images/download', methods=['GET'])
@cross_origin()
def download_images():
    """Download all images as a ZIP file"""
    try:
        scheduler = get_scheduler()
        if scheduler is None:
            return jsonify({'error': 'Scheduler not available'}), 500
        
        image_dir = Path(scheduler.config.get('image_directory', './images'))
        if not image_dir.exists():
            return jsonify({'error': 'No images directory found'}), 404
        
        # Create temporary ZIP file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        
        with zipfile.ZipFile(temp_file.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for image_file in image_dir.glob('*.jpg'):
                zipf.write(image_file, image_file.name)
        
        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name=f'landslide_images_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip',
            mimetype='application/zip'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@landslide_bp.route('/logs', methods=['GET', 'DELETE'])
@cross_origin()
def handle_logs():
    """Get or clear system logs"""
    try:
        log_file = Path('landslide_scheduler.log')
        
        if request.method == 'GET':
            if not log_file.exists():
                return jsonify([])
            
            logs = []
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    # Get last 100 lines
                    for line in lines[-100:]:
                        line = line.strip()
                        if line:
                            # Parse log format: timestamp - level - message
                            parts = line.split(' - ', 2)
                            if len(parts) >= 3:
                                timestamp_str = parts[0]
                                level = parts[1].lower()
                                message = parts[2]
                                
                                logs.append({
                                    'timestamp': timestamp_str,
                                    'level': level,
                                    'message': message
                                })
                            else:
                                logs.append({
                                    'timestamp': datetime.now().isoformat(),
                                    'level': 'info',
                                    'message': line
                                })
            except Exception as e:
                logs.append({
                    'timestamp': datetime.now().isoformat(),
                    'level': 'error',
                    'message': f'Failed to read log file: {e}'
                })
            
            return jsonify(logs)
        
        elif request.method == 'DELETE':
            if log_file.exists():
                log_file.unlink()
            return jsonify({
                'success': True,
                'message': 'Logs cleared successfully'
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@landslide_bp.route('/health', methods=['GET'])
@cross_origin()
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'scheduler_available': get_scheduler() is not None
    })


@landslide_bp.route('/cloud/status', methods=['GET'])
@cross_origin()
def get_cloud_status():
    """Get cloud storage status"""
    try:
        scheduler = get_scheduler()
        if scheduler is None:
            return jsonify({'error': 'Scheduler not available'}), 500
        
        if hasattr(scheduler, 'cloud_manager') and scheduler.cloud_manager:
            status = scheduler.cloud_manager.get_status()
            return jsonify(status)
        else:
            return jsonify({
                'enabled': False,
                'message': 'Cloud storage not configured'
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@landslide_bp.route('/cloud/images', methods=['GET'])
@cross_origin()
def get_cloud_images():
    """Get list of images from cloud storage"""
    try:
        scheduler = get_scheduler()
        if scheduler is None:
            return jsonify({'error': 'Scheduler not available'}), 500
        
        if hasattr(scheduler, 'get_cloud_images'):
            images = scheduler.get_cloud_images()
            return jsonify(images)
        else:
            return jsonify([])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@landslide_bp.route('/cloud/upload/<filename>', methods=['POST'])
@cross_origin()
def upload_to_cloud(filename):
    """Manually upload a specific image to cloud storage"""
    try:
        scheduler = get_scheduler()
        if scheduler is None:
            return jsonify({'error': 'Scheduler not available'}), 500
        
        if not hasattr(scheduler, 'cloud_manager') or not scheduler.cloud_manager:
            return jsonify({'error': 'Cloud storage not configured'}), 400
        
        # Find the image file
        image_dir = Path(scheduler.config.get('image_directory', './images'))
        image_path = image_dir / filename
        
        if not image_path.exists():
            return jsonify({'error': 'Image file not found'}), 404
        
        # Upload to cloud
        success = scheduler.cloud_manager.upload_image(str(image_path))
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Successfully uploaded {filename} to cloud storage'
            })
        else:
            return jsonify({'error': 'Failed to upload to cloud storage'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@landslide_bp.route('/cloud/config', methods=['GET', 'POST'])
@cross_origin()
def handle_cloud_config():
    """Get or update cloud storage configuration"""
    try:
        scheduler = get_scheduler()
        if scheduler is None:
            return jsonify({'error': 'Scheduler not available'}), 500
        
        if request.method == 'GET':
            cloud_config = scheduler.config.get('cloud_upload', {})
            # Remove sensitive information
            safe_config = cloud_config.copy()
            if 'aws_s3' in safe_config:
                safe_config['aws_s3'] = {k: v if k not in ['access_key', 'secret_key'] else '***' 
                                       for k, v in safe_config['aws_s3'].items()}
            if 'sftp' in safe_config:
                safe_config['sftp'] = {k: v if k not in ['password'] else '***' 
                                     for k, v in safe_config['sftp'].items()}
            return jsonify(safe_config)
        
        elif request.method == 'POST':
            data = request.get_json()
            
            # Update cloud configuration
            if 'enabled' in data:
                scheduler.config['cloud_upload']['enabled'] = data['enabled']
            if 'provider' in data:
                scheduler.config['cloud_upload']['provider'] = data['provider']
            if 'upload_immediately' in data:
                scheduler.config['cloud_upload']['upload_immediately'] = data['upload_immediately']
            
            # Save configuration
            scheduler.save_config()
            
            # Reinitialize cloud storage if needed
            if data.get('enabled', False):
                scheduler.initialize_cloud_storage()
            
            return jsonify({
                'success': True,
                'message': 'Cloud storage configuration updated'
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@landslide_bp.route('/upload-queue', methods=['GET'])
@cross_origin()
def get_upload_queue():
    """Get current upload queue status"""
    try:
        scheduler = get_scheduler()
        if scheduler is None:
            return jsonify({'error': 'Scheduler not available'}), 500
        
        if hasattr(scheduler, 'upload_queue_lock') and hasattr(scheduler, 'upload_queue'):
            with scheduler.upload_queue_lock:
                queue_items = []
                for item in scheduler.upload_queue:
                    queue_items.append({
                        'path': item['path'],
                        'timestamp': item['timestamp'].isoformat(),
                        'retries': item['retries']
                    })
                
                return jsonify({
                    'queue_size': len(queue_items),
                    'items': queue_items
                })
        else:
            return jsonify({'queue_size': 0, 'items': []})
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

