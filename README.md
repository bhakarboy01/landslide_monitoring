# Landslide Monitoring System v1.0 (DSLR-Only)

## Complete Project Package

This package contains the complete Landslide Monitoring System, now specialized for DSLR camera control, along with documentation and setup tools needed for deployment.

### Package Contents

```
landslide_monitoring_system_v1.0/
├── core/                           # Core system modules (DSLR camera control, scheduler, AI detection, cloud storage)
│   ├── camera_controller.py        # DSLR Camera interface and control
│   ├── scheduler.py                # Basic scheduling system
│   ├── enhanced_scheduler.py       # Advanced scheduler with cloud integration
│   ├── ai_landslide_detector.py    # AI detection engine
│   ├── cloud_storage.py           # Cloud storage integration
│   └── test_system.py             # System testing utilities
├── web_interface/                  # Web-based monitoring interface
│   ├── src/                       # Flask application source
│   ├── venv/                      # Python virtual environment
│   └── requirements.txt           # Python dependencies
├── documentation/                  # Complete documentation
│   ├── landslide_monitoring_documentation.pdf  # Full technical manual
│   ├── quick_start_guide.md       # Rapid deployment guide
│   ├── ai_landslide_research.md   # AI research and implementation
│   └── system_architecture_research.md  # Architecture design
├── setup_scripts/                 # Installation and setup tools
│   ├── setup.sh                   # Main system installation
│   ├── setup_cloud.sh            # Cloud storage configuration
│   └── setup_web.py              # Web interface setup
├── config/                        # Configuration templates
│   └── config.json               # Default system configuration
└── README.md                      # This file
```

### Quick Start: Raspberry Pi Deployment (DSLR Camera)

This guide assumes you have a Raspberry Pi (4 recommended) with Raspberry Pi OS (Bullseye or later) installed, and a compatible DSLR camera connected via USB.

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/bhakarboy01/landslide_monitoring.git
    cd landslide_monitoring
    ```

2.  **Run the Setup Script:**
    This script will install necessary system dependencies (including `gphoto2` for DSLR control) and set up a Python virtual environment.
    ```bash
    chmod +x setup_scripts/setup.sh
    sudo ./setup_scripts/setup.sh
    ```
    *During the setup, you will be prompted to test the camera and set up a system service. You can choose 'n' for now and configure these later.* 

3.  **Configure the System:**
    Edit `config/config.json` to customize settings such as image directory, capture intervals, and cloud storage options. Ensure `"camera_type": "dslr"` is set.
    ```bash
    nano config/config.json
    ```

4.  **Test Camera Capture:**
    Ensure your DSLR is connected and powered on. Then, activate the virtual environment and run a test capture:
    ```bash
    source venv/bin/activate
    python3 core/camera_controller.py
    ```
    This will attempt to capture a test image. Check the `./images` directory for the captured photo.

5.  **Start Monitoring:**
    To start the monitoring system, activate the virtual environment and run the scheduler:
    ```bash
    source venv/bin/activate
    python3 core/scheduler.py
    ```
    For automatic startup on boot, you can enable the systemd service (if you chose not to during setup):
    ```bash
    sudo systemctl enable landslide-monitor.service
    sudo systemctl start landslide-monitor.service
    ```

### Cloud Photo Access Setup

The system supports uploading captured images to cloud storage (AWS S3, Google Drive, SFTP). Here's a general overview of the process:

1.  **Choose Your Cloud Provider:** Decide which cloud service you want to use (AWS S3, Google Drive, or SFTP).

2.  **Obtain Credentials:**
    *   **AWS S3:** You'll need an AWS account, an S3 bucket, and IAM user credentials (Access Key ID and Secret Access Key) with permissions to write to the bucket.
    *   **Google Drive:** You'll need a Google Cloud project, enable the Google Drive API, and create a service account key (JSON file) with access to your Google Drive folder.
    *   **SFTP:** You'll need an SFTP server address, username, and password/SSH key.

3.  **Configure `config.json`:**
    Open `config/config.json` and locate the `cloud_storage` section. Update the `enabled` flag to `true` and fill in the details for your chosen provider. Example for AWS S3:
    ```json
    "cloud_storage": {
        "enabled": true,
        "provider": "aws_s3",
        "aws_s3": {
            "bucket_name": "your-s3-bucket-name",
            "access_key_id": "YOUR_AWS_ACCESS_KEY_ID",
            "secret_access_key": "YOUR_AWS_SECRET_ACCESS_KEY",
            "region": "your-aws-region"
        }
    }
    ```
    *Refer to `documentation/landslide_monitoring_documentation.pdf` for detailed configuration examples for each cloud provider.*

4.  **Run Cloud Setup Script (Optional but Recommended):**
    The `setup_cloud.sh` script can help with some cloud-specific configurations, especially for Google Drive authentication.
    ```bash
    chmod +x setup_scripts/setup_cloud.sh
    sudo ./setup_scripts/setup_cloud.sh
    ```

5.  **Verify Uploads:**
    After starting the monitoring system, captured images should automatically be uploaded to your configured cloud storage. Check your cloud storage to verify.

### Key Features (DSLR-Focused)

✅ **Automated Image Capture**
- Configurable intervals (1 minute to hours)
- Support for DSLR cameras only
- Remote zoom and camera control (if supported by DSLR)

✅ **AI-Powered Detection**
- Real-time landslide detection
- TensorFlow Lite optimized for Raspberry Pi
- Configurable confidence thresholds

✅ **Cloud Storage Integration**
- AWS S3, Google Drive, SFTP support
- Automatic upload and backup
- Redundant storage options

✅ **Web-Based Monitoring**
- Real-time dashboard
- Remote configuration
- Image browsing and download

✅ **Alert System**
- Email and webhook notifications
- Multi-level alert escalation
- Customizable alert conditions

✅ **Robust Design**
- Weatherproof deployment ready
- Power management for battery operation
- Comprehensive error handling

### System Requirements

**Hardware:**
- Raspberry Pi 4 (4GB RAM recommended)
- MicroSD card (32GB minimum)
- Compatible DSLR Camera (with USB connectivity and `gphoto2` support)
- Power supply or battery system
- Network connectivity (Wi-Fi, Ethernet, or cellular)

**Software:**
- Raspberry Pi OS (Bullseye or later)
- Python 3.8+
- Internet connection for initial setup

### Documentation

**Complete Technical Manual:** `documentation/landslide_monitoring_documentation.pdf`
- Comprehensive documentation for DSLR-focused deployment
- Installation, configuration, and operation procedures
- Troubleshooting and maintenance guides
- Technical specifications and performance data

**Quick Start Guide:** `documentation/quick_start_guide.md`
- Rapid deployment checklist for DSLR-only setup
- Essential configuration steps
- Field installation procedures

### Support and Updates

For technical support, updates, or additional information:
- Review the complete documentation
- Check the troubleshooting section
- Consult the system logs via web interface

### License

This project is provided under open source licensing for research and educational use. See individual component licenses for specific terms.

### Version History

**v1.0 (June 2025)**
- Initial release
- Complete system implementation
- Full documentation package
- Production-ready deployment

---

**Developed by:** Manus AI  
**Project Type:** Landslide Monitoring and Detection System (DSLR-Focused)  
**Target Platform:** Raspberry Pi with DSLR Camera Integration  
**Deployment:** Remote geological monitoring applications


