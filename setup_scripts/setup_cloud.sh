#!/bin/bash

# Cloud Storage Setup Script for Landslide Monitoring System
# This script helps set up cloud storage providers

set -e

echo "=========================================="
echo "Cloud Storage Setup for Landslide Monitor"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_header() {
    echo -e "${BLUE}[SETUP]${NC} $1"
}

# Check if virtual environment exists
check_venv() {
    if [[ -d "venv" ]]; then
        print_status "Virtual environment found"
        return 0
    else
        print_error "Virtual environment not found. Please run setup.sh first."
        return 1
    fi
}

# Install cloud storage dependencies
install_cloud_deps() {
    print_header "Installing cloud storage dependencies..."
    
    source venv/bin/activate
    
    # AWS S3 support
    print_status "Installing AWS S3 support (boto3)..."
    pip install boto3
    
    # Google Drive support
    print_status "Installing Google Drive support..."
    pip install google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2
    
    # SFTP support
    print_status "Installing SFTP support (paramiko)..."
    pip install paramiko
    
    # Additional utilities
    print_status "Installing additional utilities..."
    pip install requests python-dotenv
    
    print_status "Cloud storage dependencies installed successfully!"
}

# Setup AWS S3
setup_aws_s3() {
    print_header "Setting up AWS S3..."
    
    echo "Please provide your AWS S3 configuration:"
    read -p "AWS Access Key ID: " aws_access_key
    read -p "AWS Secret Access Key: " aws_secret_key
    read -p "S3 Bucket Name: " bucket_name
    read -p "AWS Region (default: us-east-1): " aws_region
    aws_region=${aws_region:-us-east-1}
    
    # Test AWS credentials
    print_status "Testing AWS S3 connection..."
    
    python3 << EOF
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

try:
    s3_client = boto3.client(
        's3',
        aws_access_key_id='$aws_access_key',
        aws_secret_access_key='$aws_secret_key',
        region_name='$aws_region'
    )
    
    # Test bucket access
    s3_client.head_bucket(Bucket='$bucket_name')
    print("✓ AWS S3 connection successful!")
    
except ClientError as e:
    error_code = e.response['Error']['Code']
    if error_code == '404':
        print("✗ Bucket not found. Please check the bucket name.")
    elif error_code == '403':
        print("✗ Access denied. Please check your credentials and permissions.")
    else:
        print(f"✗ AWS S3 error: {e}")
    exit(1)
except NoCredentialsError:
    print("✗ Invalid AWS credentials")
    exit(1)
except Exception as e:
    print(f"✗ Unexpected error: {e}")
    exit(1)
EOF
    
    if [[ $? -eq 0 ]]; then
        # Update configuration
        python3 << EOF
import json

with open('config.json', 'r') as f:
    config = json.load(f)

config['cloud_upload']['enabled'] = True
config['cloud_upload']['provider'] = 'aws_s3'
config['cloud_upload']['aws_s3']['enabled'] = True
config['cloud_upload']['aws_s3']['bucket_name'] = '$bucket_name'
config['cloud_upload']['aws_s3']['access_key'] = '$aws_access_key'
config['cloud_upload']['aws_s3']['secret_key'] = '$aws_secret_key'
config['cloud_upload']['aws_s3']['region'] = '$aws_region'

with open('config.json', 'w') as f:
    json.dump(config, f, indent=2)

print("Configuration updated successfully!")
EOF
        print_status "AWS S3 setup completed!"
    else
        print_error "AWS S3 setup failed. Please check your credentials."
        return 1
    fi
}

# Setup Google Drive
setup_google_drive() {
    print_header "Setting up Google Drive..."
    
    echo "To set up Google Drive, you need to:"
    echo "1. Go to Google Cloud Console (https://console.cloud.google.com/)"
    echo "2. Create a new project or select existing one"
    echo "3. Enable Google Drive API"
    echo "4. Create service account credentials"
    echo "5. Download the JSON credentials file"
    echo ""
    
    read -p "Do you have the Google Drive credentials JSON file? (y/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter the path to your credentials JSON file: " creds_file
        
        if [[ -f "$creds_file" ]]; then
            cp "$creds_file" "google_credentials.json"
            
            read -p "Enter Google Drive folder ID (optional): " folder_id
            
            # Update configuration
            python3 << EOF
import json

with open('config.json', 'r') as f:
    config = json.load(f)

config['cloud_upload']['enabled'] = True
config['cloud_upload']['provider'] = 'google_drive'
config['cloud_upload']['google_drive']['enabled'] = True
config['cloud_upload']['google_drive']['credentials_file'] = 'google_credentials.json'
config['cloud_upload']['google_drive']['folder_id'] = '$folder_id'

with open('config.json', 'w') as f:
    json.dump(config, f, indent=2)

print("Configuration updated successfully!")
EOF
            print_status "Google Drive setup completed!"
        else
            print_error "Credentials file not found: $creds_file"
            return 1
        fi
    else
        print_warning "Please obtain Google Drive credentials and run this setup again."
        return 1
    fi
}

# Setup SFTP
setup_sftp() {
    print_header "Setting up SFTP..."
    
    echo "Please provide your SFTP server configuration:"
    read -p "SFTP Hostname: " sftp_hostname
    read -p "SFTP Port (default: 22): " sftp_port
    sftp_port=${sftp_port:-22}
    read -p "Username: " sftp_username
    read -p "Password (leave empty to use key file): " sftp_password
    
    if [[ -z "$sftp_password" ]]; then
        read -p "SSH Key file path: " sftp_key_file
    fi
    
    read -p "Remote directory (default: /uploads/landslide): " remote_dir
    remote_dir=${remote_dir:-/uploads/landslide}
    
    # Test SFTP connection
    print_status "Testing SFTP connection..."
    
    python3 << EOF
import paramiko
import sys

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    if '$sftp_password':
        ssh.connect('$sftp_hostname', port=$sftp_port, username='$sftp_username', password='$sftp_password')
    else:
        ssh.connect('$sftp_hostname', port=$sftp_port, username='$sftp_username', key_filename='$sftp_key_file')
    
    sftp = ssh.open_sftp()
    
    # Try to create remote directory
    try:
        sftp.makedirs('$remote_dir')
    except:
        pass  # Directory might already exist
    
    sftp.close()
    ssh.close()
    print("✓ SFTP connection successful!")
    
except Exception as e:
    print(f"✗ SFTP connection failed: {e}")
    sys.exit(1)
EOF
    
    if [[ $? -eq 0 ]]; then
        # Update configuration
        python3 << EOF
import json

with open('config.json', 'r') as f:
    config = json.load(f)

config['cloud_upload']['enabled'] = True
config['cloud_upload']['provider'] = 'sftp'
config['cloud_upload']['sftp']['enabled'] = True
config['cloud_upload']['sftp']['hostname'] = '$sftp_hostname'
config['cloud_upload']['sftp']['port'] = $sftp_port
config['cloud_upload']['sftp']['username'] = '$sftp_username'
config['cloud_upload']['sftp']['password'] = '$sftp_password'
config['cloud_upload']['sftp']['key_file'] = '$sftp_key_file'
config['cloud_upload']['sftp']['remote_directory'] = '$remote_dir'

with open('config.json', 'w') as f:
    json.dump(config, f, indent=2)

print("Configuration updated successfully!")
EOF
        print_status "SFTP setup completed!"
    else
        print_error "SFTP setup failed. Please check your connection details."
        return 1
    fi
}

# Test cloud storage
test_cloud_storage() {
    print_header "Testing cloud storage configuration..."
    
    source venv/bin/activate
    
    python3 << 'EOF'
import sys
sys.path.append('.')

from cloud_storage import CloudStorageManager
import json

try:
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    manager = CloudStorageManager(config)
    status = manager.get_status()
    
    print("Cloud Storage Status:")
    print(json.dumps(status, indent=2))
    
    if status['enabled']:
        print("✓ Cloud storage is configured and ready!")
    else:
        print("✗ Cloud storage is not properly configured")
        sys.exit(1)
        
except Exception as e:
    print(f"✗ Error testing cloud storage: {e}")
    sys.exit(1)
EOF
    
    if [[ $? -eq 0 ]]; then
        print_status "Cloud storage test successful!"
    else
        print_error "Cloud storage test failed."
        return 1
    fi
}

# Create cloud storage documentation
create_documentation() {
    print_header "Creating cloud storage documentation..."
    
    cat > cloud_storage_guide.md << 'EOF'
# Cloud Storage Setup Guide

This guide explains how to configure cloud storage for the Landslide Monitoring System.

## Supported Providers

### AWS S3
1. Create an AWS account and S3 bucket
2. Create IAM user with S3 permissions
3. Get Access Key ID and Secret Access Key
4. Run: `./setup_cloud.sh` and select AWS S3

### Google Drive
1. Go to Google Cloud Console
2. Create project and enable Google Drive API
3. Create service account and download JSON credentials
4. Share target folder with service account email
5. Run: `./setup_cloud.sh` and select Google Drive

### SFTP
1. Set up SFTP server or use existing one
2. Create user account with upload permissions
3. Note hostname, port, username, and password/key
4. Run: `./setup_cloud.sh` and select SFTP

## Configuration

Edit `config.json` to customize cloud storage settings:

```json
{
  "cloud_upload": {
    "enabled": true,
    "provider": "aws_s3",
    "upload_immediately": true,
    "retry_failed_uploads": true,
    "max_retries": 3
  }
}
```

## Testing

Test your cloud storage configuration:
```bash
python3 enhanced_scheduler.py --cloud-status
```

## Troubleshooting

### AWS S3 Issues
- Check bucket permissions
- Verify IAM user has S3 access
- Ensure bucket region matches configuration

### Google Drive Issues
- Verify service account has access to target folder
- Check credentials file path
- Ensure Google Drive API is enabled

### SFTP Issues
- Test connection with SSH client
- Check firewall settings
- Verify remote directory permissions
EOF

    print_status "Documentation created: cloud_storage_guide.md"
}

# Main menu
main_menu() {
    echo ""
    echo "Select cloud storage provider to set up:"
    echo "1) AWS S3"
    echo "2) Google Drive"
    echo "3) SFTP"
    echo "4) Test current configuration"
    echo "5) Install dependencies only"
    echo "6) Exit"
    echo ""
    
    read -p "Enter your choice (1-6): " choice
    
    case $choice in
        1)
            setup_aws_s3
            ;;
        2)
            setup_google_drive
            ;;
        3)
            setup_sftp
            ;;
        4)
            test_cloud_storage
            ;;
        5)
            install_cloud_deps
            ;;
        6)
            echo "Exiting..."
            exit 0
            ;;
        *)
            print_error "Invalid choice. Please try again."
            main_menu
            ;;
    esac
}

# Main execution
main() {
    print_status "Starting cloud storage setup..."
    
    # Check prerequisites
    if ! check_venv; then
        exit 1
    fi
    
    # Install dependencies
    install_cloud_deps
    
    # Create documentation
    create_documentation
    
    # Show main menu
    main_menu
    
    echo ""
    print_status "Cloud storage setup completed!"
    echo "Next steps:"
    echo "1. Test your configuration: python3 enhanced_scheduler.py --cloud-status"
    echo "2. Start the enhanced scheduler: python3 enhanced_scheduler.py"
    echo "3. Check the cloud storage guide: cloud_storage_guide.md"
}

# Run main function
main "$@"
EOF

