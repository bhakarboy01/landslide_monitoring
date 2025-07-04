#!/bin/bash

# Landslide Monitoring System Setup Script
# This script installs dependencies and sets up the monitoring system

set -e

echo "=========================================="
echo "Landslide Monitoring System Setup"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on Raspberry Pi
check_raspberry_pi() {
    if [[ -f /proc/device-tree/model ]] && grep -q "Raspberry Pi" /proc/device-tree/model; then
        print_status "Running on Raspberry Pi"
        return 0
    else
        print_warning "Not running on Raspberry Pi - some features may not work"
        return 1
    fi
}

# Update system packages
update_system() {
    print_status "Updating system packages..."
    sudo apt-get update
    sudo apt-get upgrade -y
}

# Install system dependencies
install_system_deps() {
    print_status "Installing system dependencies..."
    
    # Basic dependencies
    sudo apt-get install -y \
        python3 \
        python3-pip \
        python3-venv \
        git \
        curl \
        wget \
        unzip \
        build-essential \
        cmake \
        pkg-config \
        libjpeg-dev \
        libpng-dev \
        libtiff-dev \
        libavcodec-dev \
        libavformat-dev \
        libswscale-dev \
        libv4l-dev \
        libxvidcore-dev \
        libx264-dev \
        libgtk-3-dev \
        libatlas-base-dev \
        gfortran
    
    # Install gphoto2 for DSLR support
    print_status "Installing gphoto2 for DSLR camera support..."
    sudo apt-get install -y gphoto2 libgphoto2-dev
    
    # Install camera-specific packages for Raspberry Pi
    if check_raspberry_pi; then
        print_status "Installing Raspberry Pi camera support..."
        sudo apt-get install -y \
            python3-picamera \
            python3-picamera2 \
            libcamera-apps \
            libcamera-dev
        
        # Enable camera interface
        print_status "Enabling camera interface..."
        sudo raspi-config nonint do_camera 0
    fi
}

# Create Python virtual environment
setup_python_env() {
    print_status "Setting up Python virtual environment..."
    
    if [[ ! -d "venv" ]]; then
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install Python dependencies
    print_status "Installing Python packages..."
    pip install \
        flask \
        flask-cors \
        requests \
        pillow \
        numpy \
        opencv-python \
        schedule \
        boto3 \
        google-cloud-storage \
        paramiko \
        python-crontab
    
    # Try to install picamera2 if on Raspberry Pi
    if check_raspberry_pi; then
        pip install picamera2 || print_warning "Could not install picamera2 via pip"
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating directories..."
    mkdir -p images
    mkdir -p logs
    mkdir -p backups
}

# Set up systemd service
setup_systemd_service() {
    print_status "Setting up systemd service..."
    
    SERVICE_FILE="/etc/systemd/system/landslide-monitor.service"
    CURRENT_DIR=$(pwd)
    
    sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=Landslide Monitoring System
After=network.target
Wants=network.target

[Service]
Type=simple
User=pi
Group=pi
WorkingDirectory=$CURRENT_DIR
Environment=PATH=$CURRENT_DIR/venv/bin
ExecStart=$CURRENT_DIR/venv/bin/python $CURRENT_DIR/scheduler.py --daemon
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable landslide-monitor.service
    
    print_status "Systemd service created and enabled"
}

# Test camera functionality
test_camera() {
    print_status "Testing camera functionality..."
    
    source venv/bin/activate
    
    if python3 camera_controller.py; then
        print_status "Camera test successful!"
    else
        print_error "Camera test failed. Please check your camera connection."
        return 1
    fi
}

# Create backup script
create_backup_script() {
    print_status "Creating backup script..."
    
    cat > backup_images.sh <<'EOF'
#!/bin/bash

# Backup script for landslide monitoring images
BACKUP_DIR="./backups"
IMAGE_DIR="./images"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/landslide_backup_$DATE.tar.gz"

mkdir -p "$BACKUP_DIR"

if [[ -d "$IMAGE_DIR" ]] && [[ $(ls -A "$IMAGE_DIR") ]]; then
    echo "Creating backup: $BACKUP_FILE"
    tar -czf "$BACKUP_FILE" -C "$IMAGE_DIR" .
    echo "Backup created successfully"
    
    # Keep only last 10 backups
    ls -t "$BACKUP_DIR"/landslide_backup_*.tar.gz | tail -n +11 | xargs -r rm
    echo "Old backups cleaned up"
else
    echo "No images to backup"
fi
EOF

    chmod +x backup_images.sh
}

# Main setup function
main() {
    print_status "Starting setup process..."
    
    # Check if script is run from the correct directory
    if [[ ! -f "camera_controller.py" ]] || [[ ! -f "scheduler.py" ]]; then
        print_error "Please run this script from the directory containing the landslide monitoring files"
        exit 1
    fi
    
    # Run setup steps
    update_system
    install_system_deps
    setup_python_env
    create_directories
    create_backup_script
    
    # Test camera (optional)
    read -p "Do you want to test the camera now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        test_camera
    fi
    
    # Setup systemd service (optional)
    read -p "Do you want to set up the system service for automatic startup? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        setup_systemd_service
    fi
    
    print_status "Setup completed successfully!"
    echo
    echo "=========================================="
    echo "Next steps:"
    echo "1. Edit config.json to customize settings"
    echo "2. Test the system: source venv/bin/activate && python3 scheduler.py --capture"
    echo "3. Start monitoring: source venv/bin/activate && python3 scheduler.py"
    echo "4. Or start the service: sudo systemctl start landslide-monitor"
    echo "=========================================="
}

# Run main function
main "$@"

