# Quick Start Deployment Guide

## Landslide Monitoring System - Quick Deployment

This guide provides step-by-step instructions for rapidly deploying the Landslide Monitoring System in the field.

### Prerequisites Checklist

**Hardware Required:**
- [ ] Raspberry Pi 4 (4GB RAM recommended)
- [ ] MicroSD card (32GB minimum, Class 10)
- [ ] Raspberry Pi Camera Module v1.3 OR DSLR camera with USB cable
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
   # Enable SSH by creating empty 'ssh' file in boot partition
   ```

2. **Configure Wi-Fi (if needed):**
   ```bash
   # Create wpa_supplicant.conf in boot partition:
   country=US
   ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
   update_config=1
   
   network={
       ssid="YourNetworkName"
       psk="YourPassword"
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
   # Enable camera interface
   # Expand filesystem
   # Set timezone
   ```

2. **Download and Install:**
   ```bash
   # Download system files
   git clone [repository_url] landslide_monitoring
   cd landslide_monitoring
   
   # Run installation script
   chmod +x setup.sh
   sudo ./setup.sh
   ```

3. **Configure Camera:**
   ```bash
   # Test Pi Camera
   raspistill -o test.jpg
   
   # OR test DSLR camera
   gphoto2 --capture-image-and-download
   ```

### Step 3: Basic Configuration

1. **Edit Configuration File:**
   ```bash
   nano config.json
   ```

2. **Essential Settings:**
   ```json
   {
     "camera_type": "pi_camera",
     "capture_interval_minutes": 60,
     "image_quality": 95,
     "location": "Your Site Name",
     "cloud_storage": {
       "enabled": true,
       "provider": "aws_s3"
     }
   }
   ```

3. **Start System:**
   ```bash
   sudo systemctl start landslide-monitor
   sudo systemctl enable landslide-monitor
   ```

### Step 4: Web Interface Setup

1. **Start Web Interface:**
   ```bash
   cd landslide_web
   source venv/bin/activate
   python src/main.py
   ```

2. **Access Dashboard:**
   - Open browser to `http://[PI_IP_ADDRESS]:5001`
   - Verify system status
   - Test manual image capture
   - Configure alerts and notifications

### Step 5: Cloud Storage Setup

1. **AWS S3 Configuration:**
   ```bash
   # Run cloud setup script
   ./setup_cloud.sh
   # Follow prompts for AWS credentials
   ```

2. **Test Upload:**
   ```bash
   # Capture and upload test image
   python test_system.py
   ```

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
vcgencmd get_camera

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

