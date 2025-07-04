#!/usr/bin/env python3
"""
Web Interface Integration Script
This script helps integrate the web interface with the core landslide monitoring system
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def setup_web_interface():
    """Set up the web interface with the core monitoring system"""
    
    print("Setting up Landslide Monitoring Web Interface...")
    
    # Check if we're in the right directory
    if not Path("camera_controller.py").exists() or not Path("scheduler.py").exists():
        print("Error: Please run this script from the directory containing the landslide monitoring files")
        return False
    
    web_dir = Path("landslide_web")
    
    # Create web directory if it doesn't exist
    if not web_dir.exists():
        print("Creating web application...")
        result = subprocess.run(["manus-create-flask-app", "landslide_web"], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Failed to create Flask app: {result.stderr}")
            return False
    
    # Copy core files to web directory
    print("Copying core monitoring files...")
    core_files = ["camera_controller.py", "scheduler.py", "config.json"]
    for file in core_files:
        if Path(file).exists():
            shutil.copy2(file, web_dir / file)
            print(f"  Copied {file}")
    
    # Create images directory
    (web_dir / "images").mkdir(exist_ok=True)
    
    # Install dependencies
    print("Installing web dependencies...")
    venv_python = web_dir / "venv" / "bin" / "python"
    venv_pip = web_dir / "venv" / "bin" / "pip"
    
    if venv_python.exists():
        subprocess.run([str(venv_pip), "install", "flask-cors"], 
                      cwd=web_dir, capture_output=True)
        print("  Installed flask-cors")
    
    # Update requirements.txt
    requirements_file = web_dir / "requirements.txt"
    if requirements_file.exists():
        with open(requirements_file, "a") as f:
            f.write("\nflask-cors\n")
    
    print("Web interface setup completed!")
    print(f"\nTo start the web interface:")
    print(f"1. cd {web_dir}")
    print(f"2. source venv/bin/activate")
    print(f"3. python src/main.py")
    print(f"4. Open http://localhost:5001 in your browser")
    
    return True

def create_startup_script():
    """Create a startup script for the complete system"""
    
    startup_script = """#!/bin/bash

# Landslide Monitoring System Startup Script

echo "Starting Landslide Monitoring System..."

# Function to check if a process is running
check_process() {
    pgrep -f "$1" > /dev/null
    return $?
}

# Function to start the core monitoring system
start_core_system() {
    echo "Starting core monitoring system..."
    if [ -f "scheduler.py" ]; then
        python3 scheduler.py --daemon &
        echo "Core system started (PID: $!)"
    else
        echo "Error: scheduler.py not found"
        return 1
    fi
}

# Function to start the web interface
start_web_interface() {
    echo "Starting web interface..."
    if [ -d "landslide_web" ]; then
        cd landslide_web
        source venv/bin/activate
        python src/main.py &
        WEB_PID=$!
        echo "Web interface started (PID: $WEB_PID)"
        cd ..
    else
        echo "Error: landslide_web directory not found"
        return 1
    fi
}

# Function to stop all processes
stop_system() {
    echo "Stopping landslide monitoring system..."
    pkill -f "scheduler.py"
    pkill -f "landslide_web"
    echo "System stopped"
}

# Handle command line arguments
case "$1" in
    start)
        start_core_system
        start_web_interface
        echo "System started successfully!"
        echo "Web interface: http://localhost:5001"
        ;;
    stop)
        stop_system
        ;;
    restart)
        stop_system
        sleep 2
        start_core_system
        start_web_interface
        echo "System restarted!"
        ;;
    status)
        if check_process "scheduler.py"; then
            echo "Core system: Running"
        else
            echo "Core system: Stopped"
        fi
        
        if check_process "landslide_web"; then
            echo "Web interface: Running"
        else
            echo "Web interface: Stopped"
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        echo ""
        echo "Commands:"
        echo "  start   - Start both core system and web interface"
        echo "  stop    - Stop all components"
        echo "  restart - Restart all components"
        echo "  status  - Show status of all components"
        exit 1
        ;;
esac
"""
    
    with open("landslide_system.sh", "w") as f:
        f.write(startup_script)
    
    os.chmod("landslide_system.sh", 0o755)
    print("Created startup script: landslide_system.sh")

def main():
    """Main function"""
    print("Landslide Monitoring System - Web Interface Setup")
    print("=" * 50)
    
    # Setup web interface
    if setup_web_interface():
        print("\n" + "=" * 50)
        
        # Create startup script
        create_startup_script()
        
        print("\nSetup completed successfully!")
        print("\nQuick start commands:")
        print("  ./landslide_system.sh start    # Start everything")
        print("  ./landslide_system.sh stop     # Stop everything")
        print("  ./landslide_system.sh status   # Check status")
        
    else:
        print("Setup failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

