# Quick Start Deployment Guide (DSLR-Only)

## Landslide Monitoring System - Quick Deployment

This guide provides step-by-step instructions for rapidly deploying the Landslide Monitoring System with a DSLR camera in the field.

### Prerequisites Checklist

**Hardware Required:**
- [ ] Raspberry Pi 4 (4GB RAM recommended)
- [ ] MicroSD card (32GB minimum, Class 10)
- [ ] Compatible DSLR camera with USB cable (ensure `gphoto2` support)
- [ ] Power supply (5V 3A for Pi 4) OR battery pack OR solar panel system
- [ ] Weatherproof enclosure (IP65 rated minimum)
- [ ] Network connectivity (Wi-Fi, Ethernet, or cellular modem)

**Software Required:**
- [ ] Raspberry Pi Imager
- [ ] SSH client (PuTTY for Windows, Terminal for Mac/Linux)
- [ ] Web browser for system configuration

### Step 1: Prepare Raspberry Pi

1. **Flash Raspberry Pi OS:**
   ```bash
   # Download Raspberry Pi OS Lite from official website
   # Use Raspberry Pi Imager to flash to microSD card
   # Enable SSH by creating empty \'ssh\' file in boot partition
   ```

2. **Configure Wi-Fi (if needed):**
   ```bash
   # Create wpa_supplicant.conf in boot partition:
   country=US
   ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
   update_config=1
   
   network={
       ssid=\"YourNetworkName\"
       psk=\"YourPassword\"
   }
   ```

3. **Boot and Connect:**
   ```bash
   # Insert microSD card and power on Raspberry Pi
   # Find IP address using network scanner or router admin panel
   # Connect via SSH: ssh pi@[IP_ADDRESS]
   # Default password: raspberry (change immediately!)
   ```

### Step 2: Install System Software

1. **Update System:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo raspi-config
   # Expand filesystem
   # Set timezone
   ```

2. **Download and Install:**
   ```bash
   # Download system files
   git clone [repository_url] landslide_monitoring
   cd landslide_monitoring
   
   # Run installation script (installs gphoto2 and Python dependencies)
   chmod +x setup_scripts/setup.sh
   sudo ./setup_scripts/setup.sh
   ```

### Step 3: Basic Configuration

1. **Edit Configuration File:**
   ```bash
   nano config/config.json
   ```

2. **Essential Settings:**
   Ensure `"camera_type": "dslr"` is set. Example:
   ```json
   {
     "camera_type": "dslr",
     "capture_interval_minutes": 60,
     "image_quality": 95,
     "location": "Your Site Name",
     "cloud_storage": {
       "enabled": true,
       "provider": "aws_s3"
     }
   }
   ```

3. **Test Camera Capture:**
   Ensure your DSLR is connected and powered on. Then, activate the virtual environment and run a test capture:
   ```bash
   source venv/bin/activate
   python3 core/camera_controller.py
   ```
   This will attempt to capture a test image. Check the `./images` directory for the captured photo.

4. **Start System:**
   To start the monitoring system, activate the virtual environment and run the scheduler:
   ```bash
   source venv/bin/activate
   python3 core/scheduler.py
   ```
   For automatic startup on boot, you can enable the systemd service:
   ```bash
   sudo systemctl enable landslide-monitor.service
   sudo systemctl start landslide-monitor.service
   ```

### Step 4: Web Interface Setup

1. **Start Web Interface:**
   ```bash
   cd web_interface
   source venv/bin/activate
   python src/main.py
   ```

2. **Access Dashboard:**
   - Open browser to `http://[PI_IP_ADDRESS]:5001`
   - Verify system status
   - Test manual image capture
   - Configure alerts and notifications

### Step 5: Cloud Storage Setup

1. **Choose Your Cloud Provider:** Decide which cloud service you want to use (AWS S3, Google Drive, or SFTP).

2. **Obtain Credentials:**
    *   **AWS S3:** You\'ll need an AWS account, an S3 bucket, and IAM user credentials (Access Key ID and Secret Access Key) with permissions to write to the bucket.
    *   **Google Drive:** You\'ll need a Google Cloud project, enable the Google Drive API, and create a service account key (JSON file) with access to your Google Drive folder.
    *   **SFTP:** You\'ll need an SFTP server address, username, and password/SSH key.

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

4.  **Run Cloud Setup Script (Optional but Recommended):**
    The `setup_cloud.sh` script can help with some cloud-specific configurations, especially for Google Drive authentication.
    ```bash
    chmod +x setup_scripts/setup_cloud.sh
    sudo ./setup_scripts/setup_cloud.sh
    ```

5.  **Verify Uploads:**
    After starting the monitoring system, captured images should automatically be uploaded to your configured cloud storage. Check your cloud storage to verify.

### Step 6: Field Deployment

1. **Hardware Installation:**
   - Mount camera with clear view of monitoring area
   - Install Raspberry Pi in weatherproof enclosure
   - Connect power supply (battery/solar)
   - Verify network connectivity

2. **Final Testing:**
   - Verify remote access via web interface
   - Test image capture and AI detection
   - Confirm cloud storage uploads
   - Test alert notifications

3. **Monitoring:**
   - Check system status daily via web interface
   - Monitor power levels and connectivity
   - Review captured images and detection results

### Troubleshooting Quick Fixes

**Camera Not Working:**
```bash
# Check camera connection
gphoto2 --auto-detect

# Restart camera service
sudo systemctl restart landslide-monitor
```

**Network Issues:**
```bash
# Check connectivity
ping google.com

# Restart networking
sudo systemctl restart networking
```

**Storage Full:**
```bash
# Check disk space
df -h

# Clean old images
sudo systemctl restart landslide-monitor
```

### Emergency Contacts

- **Technical Support:** [support_email]
- **Emergency Response:** [emergency_contact]
- **System Documentation:** See full documentation PDF

### Maintenance Schedule

**Daily:**
- Check web interface status
- Verify image capture

**Weekly:**
- Review detection results
- Check power levels
- Clean camera lens if needed

**Monthly:**
- Update system software
- Backup configuration
- Inspect hardware connections

---

**Deployment Checklist:**
- [ ] Hardware assembled and tested
- [ ] Software installed and configured
- [ ] Network connectivity verified
- [ ] Cloud storage operational
- [ ] Web interface accessible
- [ ] Alert notifications tested
- [ ] Field installation complete
- [ ] System monitoring established

**For detailed information, refer to the complete documentation PDF.**


