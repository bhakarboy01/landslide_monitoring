#!/usr/bin/env python3
"""
Test script for the Landslide Monitoring System
This script tests various components of the system
"""

import json
import sys
import os
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import camera_controller
        print("✓ camera_controller module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import camera_controller: {e}")
        return False
    
    try:
        import scheduler
        print("✓ scheduler module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import scheduler: {e}")
        return False
    
    return True

def test_config():
    """Test configuration loading"""
    print("\nTesting configuration...")
    
    try:
        from scheduler import LandslideScheduler
        
        # Test with default config
        if not Path("config.json").exists():
            print("✓ No config.json found, will create default")
        
        scheduler_instance = LandslideScheduler()
        config = scheduler_instance.config
        
        print(f"✓ Configuration loaded successfully")
        print(f"  - Camera type: {config.get('camera_type')}")
        print(f"  - Image directory: {config.get('image_directory')}")
        print(f"  - Capture interval: {config.get('capture_interval_minutes')} minutes")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def test_camera_detection():
    """Test camera detection and initialization"""
    print("\nTesting camera detection...")
    
    try:
        from camera_controller import create_camera_controller
        
        # Test Pi Camera
        try:
            config = {'camera_type': 'pi_camera', 'image_directory': './test_images'}
            camera = create_camera_controller(config)
            status = camera.get_status()
            print(f"✓ Pi Camera detected: {status}")
            return True
        except Exception as e:
            print(f"✗ Pi Camera not available: {e}")
        
        # Test DSLR Camera
        try:
            config = {'camera_type': 'dslr', 'image_directory': './test_images'}
            camera = create_camera_controller(config)
            status = camera.get_status()
            print(f"✓ DSLR Camera detected: {status}")
            return True
        except Exception as e:
            print(f"✗ DSLR Camera not available: {e}")
        
        print("✗ No cameras detected")
        return False
        
    except Exception as e:
        print(f"✗ Camera detection failed: {e}")
        return False

def test_directories():
    """Test directory creation and permissions"""
    print("\nTesting directories...")
    
    test_dirs = ['./test_images', './test_logs']
    
    for dir_path in test_dirs:
        try:
            Path(dir_path).mkdir(exist_ok=True)
            
            # Test write permissions
            test_file = Path(dir_path) / "test_write.txt"
            test_file.write_text("test")
            test_file.unlink()
            
            print(f"✓ Directory {dir_path} is writable")
            
        except Exception as e:
            print(f"✗ Directory {dir_path} test failed: {e}")
            return False
    
    return True

def test_system_commands():
    """Test system commands availability"""
    print("\nTesting system commands...")
    
    commands = {
        'gphoto2': 'DSLR camera control',
        'python3': 'Python interpreter',
        'pip3': 'Python package manager'
    }
    
    all_good = True
    
    for cmd, description in commands.items():
        result = os.system(f"which {cmd} > /dev/null 2>&1")
        if result == 0:
            print(f"✓ {cmd} available ({description})")
        else:
            print(f"✗ {cmd} not found ({description})")
            if cmd == 'gphoto2':
                print("  Install with: sudo apt-get install gphoto2")
            all_good = False
    
    return all_good

def test_capture():
    """Test image capture functionality"""
    print("\nTesting image capture...")
    
    try:
        from scheduler import LandslideScheduler
        
        # Create test directory
        test_dir = Path("./test_images")
        test_dir.mkdir(exist_ok=True)
        
        # Create scheduler with test config
        scheduler_instance = LandslideScheduler()
        scheduler_instance.config['image_directory'] = str(test_dir)
        scheduler_instance.initialize_camera()
        
        # Attempt to capture image
        image_path = scheduler_instance.capture_image()
        
        if image_path and Path(image_path).exists():
            print(f"✓ Image capture successful: {image_path}")
            file_size = Path(image_path).stat().st_size
            print(f"  Image size: {file_size} bytes")
            return True
        else:
            print("✗ Image capture failed")
            return False
            
    except Exception as e:
        print(f"✗ Image capture test failed: {e}")
        return False

def cleanup_test_files():
    """Clean up test files and directories"""
    print("\nCleaning up test files...")
    
    import shutil
    
    test_paths = ['./test_images', './test_logs']
    
    for path in test_paths:
        try:
            if Path(path).exists():
                shutil.rmtree(path)
                print(f"✓ Removed {path}")
        except Exception as e:
            print(f"✗ Failed to remove {path}: {e}")

def main():
    """Run all tests"""
    print("Landslide Monitoring System - Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Configuration Test", test_config),
        ("Directory Test", test_directories),
        ("System Commands Test", test_system_commands),
        ("Camera Detection Test", test_camera_detection),
    ]
    
    # Ask user if they want to test capture (requires camera)
    try:
        response = input("\nDo you want to test image capture? This requires a camera. (y/n): ")
        if response.lower().startswith('y'):
            tests.append(("Image Capture Test", test_capture))
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        return
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your system is ready.")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    # Cleanup
    try:
        response = input("\nDo you want to clean up test files? (y/n): ")
        if response.lower().startswith('y'):
            cleanup_test_files()
    except KeyboardInterrupt:
        pass
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

