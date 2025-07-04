#!/usr/bin/env python3
"""
Cloud Storage Module for Landslide Monitoring System
This module provides cloud storage integration for automatic image upload
"""

import os
import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

class CloudStorageProvider(ABC):
    """Abstract base class for cloud storage providers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get('enabled', False)
    
    @abstractmethod
    def upload_file(self, local_path: str, remote_path: str) -> bool:
        """Upload a file to cloud storage"""
        pass
    
    @abstractmethod
    def download_file(self, remote_path: str, local_path: str) -> bool:
        """Download a file from cloud storage"""
        pass
    
    @abstractmethod
    def list_files(self, prefix: str = "") -> List[Dict[str, Any]]:
        """List files in cloud storage"""
        pass
    
    @abstractmethod
    def delete_file(self, remote_path: str) -> bool:
        """Delete a file from cloud storage"""
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Get provider status"""
        pass

class AWSS3Provider(CloudStorageProvider):
    """AWS S3 cloud storage provider"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.bucket_name = config.get('bucket_name')
        self.access_key = config.get('access_key')
        self.secret_key = config.get('secret_key')
        self.region = config.get('region', 'us-east-1')
        self.s3_client = None
        
        if self.enabled:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize S3 client"""
        try:
            import boto3
            from botocore.exceptions import ClientError, NoCredentialsError
            
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.region
            )
            
            # Test connection
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"AWS S3 client initialized for bucket: {self.bucket_name}")
            
        except ImportError:
            logger.error("boto3 not installed. Install with: pip install boto3")
            self.enabled = False
        except (ClientError, NoCredentialsError) as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            self.enabled = False
        except Exception as e:
            logger.error(f"Unexpected error initializing S3: {e}")
            self.enabled = False
    
    def upload_file(self, local_path: str, remote_path: str) -> bool:
        """Upload file to S3"""
        if not self.enabled or not self.s3_client:
            return False
        
        try:
            self.s3_client.upload_file(local_path, self.bucket_name, remote_path)
            logger.info(f"Uploaded {local_path} to S3: s3://{self.bucket_name}/{remote_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to upload {local_path} to S3: {e}")
            return False
    
    def download_file(self, remote_path: str, local_path: str) -> bool:
        """Download file from S3"""
        if not self.enabled or not self.s3_client:
            return False
        
        try:
            self.s3_client.download_file(self.bucket_name, remote_path, local_path)
            logger.info(f"Downloaded s3://{self.bucket_name}/{remote_path} to {local_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to download {remote_path} from S3: {e}")
            return False
    
    def list_files(self, prefix: str = "") -> List[Dict[str, Any]]:
        """List files in S3 bucket"""
        if not self.enabled or not self.s3_client:
            return []
        
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            files = []
            for obj in response.get('Contents', []):
                files.append({
                    'name': obj['Key'],
                    'size': obj['Size'],
                    'modified': obj['LastModified'].isoformat(),
                    'url': f"s3://{self.bucket_name}/{obj['Key']}"
                })
            
            return files
        except Exception as e:
            logger.error(f"Failed to list S3 files: {e}")
            return []
    
    def delete_file(self, remote_path: str) -> bool:
        """Delete file from S3"""
        if not self.enabled or not self.s3_client:
            return False
        
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=remote_path)
            logger.info(f"Deleted s3://{self.bucket_name}/{remote_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete {remote_path} from S3: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get S3 provider status"""
        return {
            'provider': 'aws_s3',
            'enabled': self.enabled,
            'bucket': self.bucket_name,
            'region': self.region,
            'connected': self.s3_client is not None
        }

class GoogleDriveProvider(CloudStorageProvider):
    """Google Drive cloud storage provider"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.credentials_file = config.get('credentials_file')
        self.folder_id = config.get('folder_id')
        self.drive_service = None
        
        if self.enabled:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Google Drive client"""
        try:
            from googleapiclient.discovery import build
            from google.oauth2.service_account import Credentials
            
            if not self.credentials_file or not Path(self.credentials_file).exists():
                logger.error("Google Drive credentials file not found")
                self.enabled = False
                return
            
            credentials = Credentials.from_service_account_file(
                self.credentials_file,
                scopes=['https://www.googleapis.com/auth/drive.file']
            )
            
            self.drive_service = build('drive', 'v3', credentials=credentials)
            logger.info("Google Drive client initialized")
            
        except ImportError:
            logger.error("Google API client not installed. Install with: pip install google-api-python-client google-auth")
            self.enabled = False
        except Exception as e:
            logger.error(f"Failed to initialize Google Drive client: {e}")
            self.enabled = False
    
    def upload_file(self, local_path: str, remote_path: str) -> bool:
        """Upload file to Google Drive"""
        if not self.enabled or not self.drive_service:
            return False
        
        try:
            from googleapiclient.http import MediaFileUpload
            
            file_metadata = {
                'name': Path(remote_path).name,
                'parents': [self.folder_id] if self.folder_id else []
            }
            
            media = MediaFileUpload(local_path, resumable=True)
            
            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            logger.info(f"Uploaded {local_path} to Google Drive: {file.get('id')}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upload {local_path} to Google Drive: {e}")
            return False
    
    def download_file(self, remote_path: str, local_path: str) -> bool:
        """Download file from Google Drive"""
        # Implementation would require file ID lookup
        logger.warning("Google Drive download not implemented")
        return False
    
    def list_files(self, prefix: str = "") -> List[Dict[str, Any]]:
        """List files in Google Drive"""
        if not self.enabled or not self.drive_service:
            return []
        
        try:
            query = f"'{self.folder_id}' in parents" if self.folder_id else ""
            if prefix:
                query += f" and name contains '{prefix}'"
            
            results = self.drive_service.files().list(
                q=query,
                fields="files(id, name, size, modifiedTime)"
            ).execute()
            
            files = []
            for file in results.get('files', []):
                files.append({
                    'name': file['name'],
                    'size': int(file.get('size', 0)),
                    'modified': file['modifiedTime'],
                    'url': f"https://drive.google.com/file/d/{file['id']}/view"
                })
            
            return files
            
        except Exception as e:
            logger.error(f"Failed to list Google Drive files: {e}")
            return []
    
    def delete_file(self, remote_path: str) -> bool:
        """Delete file from Google Drive"""
        logger.warning("Google Drive delete not implemented")
        return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get Google Drive provider status"""
        return {
            'provider': 'google_drive',
            'enabled': self.enabled,
            'folder_id': self.folder_id,
            'connected': self.drive_service is not None
        }

class SFTPProvider(CloudStorageProvider):
    """SFTP cloud storage provider"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.hostname = config.get('hostname')
        self.port = config.get('port', 22)
        self.username = config.get('username')
        self.password = config.get('password')
        self.key_file = config.get('key_file')
        self.remote_directory = config.get('remote_directory', '/')
        
        if self.enabled:
            self._test_connection()
    
    def _test_connection(self):
        """Test SFTP connection"""
        try:
            import paramiko
            
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            if self.key_file and Path(self.key_file).exists():
                ssh.connect(self.hostname, port=self.port, username=self.username, key_filename=self.key_file)
            else:
                ssh.connect(self.hostname, port=self.port, username=self.username, password=self.password)
            
            ssh.close()
            logger.info(f"SFTP connection test successful: {self.hostname}")
            
        except ImportError:
            logger.error("paramiko not installed. Install with: pip install paramiko")
            self.enabled = False
        except Exception as e:
            logger.error(f"SFTP connection test failed: {e}")
            self.enabled = False
    
    def _get_sftp_client(self):
        """Get SFTP client"""
        try:
            import paramiko
            
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            if self.key_file and Path(self.key_file).exists():
                ssh.connect(self.hostname, port=self.port, username=self.username, key_filename=self.key_file)
            else:
                ssh.connect(self.hostname, port=self.port, username=self.username, password=self.password)
            
            return ssh.open_sftp(), ssh
            
        except Exception as e:
            logger.error(f"Failed to create SFTP client: {e}")
            return None, None
    
    def upload_file(self, local_path: str, remote_path: str) -> bool:
        """Upload file via SFTP"""
        if not self.enabled:
            return False
        
        sftp, ssh = self._get_sftp_client()
        if not sftp:
            return False
        
        try:
            remote_full_path = f"{self.remote_directory.rstrip('/')}/{remote_path}"
            
            # Create remote directory if needed
            remote_dir = str(Path(remote_full_path).parent)
            try:
                sftp.makedirs(remote_dir)
            except:
                pass  # Directory might already exist
            
            sftp.put(local_path, remote_full_path)
            logger.info(f"Uploaded {local_path} to SFTP: {remote_full_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upload {local_path} via SFTP: {e}")
            return False
        finally:
            sftp.close()
            ssh.close()
    
    def download_file(self, remote_path: str, local_path: str) -> bool:
        """Download file via SFTP"""
        if not self.enabled:
            return False
        
        sftp, ssh = self._get_sftp_client()
        if not sftp:
            return False
        
        try:
            remote_full_path = f"{self.remote_directory.rstrip('/')}/{remote_path}"
            sftp.get(remote_full_path, local_path)
            logger.info(f"Downloaded {remote_full_path} to {local_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download {remote_path} via SFTP: {e}")
            return False
        finally:
            sftp.close()
            ssh.close()
    
    def list_files(self, prefix: str = "") -> List[Dict[str, Any]]:
        """List files via SFTP"""
        if not self.enabled:
            return []
        
        sftp, ssh = self._get_sftp_client()
        if not sftp:
            return []
        
        try:
            files = []
            for file_attr in sftp.listdir_attr(self.remote_directory):
                if prefix and not file_attr.filename.startswith(prefix):
                    continue
                
                files.append({
                    'name': file_attr.filename,
                    'size': file_attr.st_size,
                    'modified': datetime.fromtimestamp(file_attr.st_mtime).isoformat(),
                    'url': f"sftp://{self.hostname}{self.remote_directory}/{file_attr.filename}"
                })
            
            return files
            
        except Exception as e:
            logger.error(f"Failed to list SFTP files: {e}")
            return []
        finally:
            sftp.close()
            ssh.close()
    
    def delete_file(self, remote_path: str) -> bool:
        """Delete file via SFTP"""
        if not self.enabled:
            return False
        
        sftp, ssh = self._get_sftp_client()
        if not sftp:
            return False
        
        try:
            remote_full_path = f"{self.remote_directory.rstrip('/')}/{remote_path}"
            sftp.remove(remote_full_path)
            logger.info(f"Deleted SFTP file: {remote_full_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete {remote_path} via SFTP: {e}")
            return False
        finally:
            sftp.close()
            ssh.close()
    
    def get_status(self) -> Dict[str, Any]:
        """Get SFTP provider status"""
        return {
            'provider': 'sftp',
            'enabled': self.enabled,
            'hostname': self.hostname,
            'port': self.port,
            'username': self.username,
            'remote_directory': self.remote_directory
        }

class CloudStorageManager:
    """Manager for cloud storage operations"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.providers = {}
        self.active_provider = None
        
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize all configured cloud storage providers"""
        cloud_config = self.config.get('cloud_upload', {})
        
        # AWS S3
        if cloud_config.get('aws_s3', {}).get('enabled', False):
            self.providers['aws_s3'] = AWSS3Provider(cloud_config['aws_s3'])
        
        # Google Drive
        if cloud_config.get('google_drive', {}).get('enabled', False):
            self.providers['google_drive'] = GoogleDriveProvider(cloud_config['google_drive'])
        
        # SFTP
        if cloud_config.get('sftp', {}).get('enabled', False):
            self.providers['sftp'] = SFTPProvider(cloud_config['sftp'])
        
        # Set active provider
        active_provider_name = cloud_config.get('provider', 'aws_s3')
        if active_provider_name in self.providers:
            self.active_provider = self.providers[active_provider_name]
            logger.info(f"Active cloud storage provider: {active_provider_name}")
        else:
            logger.warning("No active cloud storage provider configured")
    
    def upload_image(self, image_path: str) -> bool:
        """Upload an image to cloud storage"""
        if not self.active_provider or not self.active_provider.enabled:
            logger.warning("No active cloud storage provider available")
            return False
        
        try:
            # Generate remote path with timestamp
            timestamp = datetime.now().strftime("%Y/%m/%d")
            filename = Path(image_path).name
            remote_path = f"landslide_images/{timestamp}/{filename}"
            
            return self.active_provider.upload_file(image_path, remote_path)
            
        except Exception as e:
            logger.error(f"Failed to upload image {image_path}: {e}")
            return False
    
    def get_cloud_images(self) -> List[Dict[str, Any]]:
        """Get list of images from cloud storage"""
        if not self.active_provider or not self.active_provider.enabled:
            return []
        
        return self.active_provider.list_files("landslide_images/")
    
    def get_status(self) -> Dict[str, Any]:
        """Get cloud storage status"""
        status = {
            'enabled': bool(self.active_provider and self.active_provider.enabled),
            'active_provider': None,
            'providers': {}
        }
        
        if self.active_provider:
            status['active_provider'] = self.active_provider.get_status()
        
        for name, provider in self.providers.items():
            status['providers'][name] = provider.get_status()
        
        return status

# Example usage and testing
if __name__ == "__main__":
    # Example configuration
    config = {
        'cloud_upload': {
            'provider': 'aws_s3',
            'aws_s3': {
                'enabled': True,
                'bucket_name': 'my-landslide-bucket',
                'access_key': 'your-access-key',
                'secret_key': 'your-secret-key',
                'region': 'us-east-1'
            },
            'google_drive': {
                'enabled': False,
                'credentials_file': 'credentials.json',
                'folder_id': 'your-folder-id'
            },
            'sftp': {
                'enabled': False,
                'hostname': 'your-server.com',
                'username': 'username',
                'password': 'password',
                'remote_directory': '/uploads'
            }
        }
    }
    
    # Test cloud storage manager
    manager = CloudStorageManager(config)
    status = manager.get_status()
    print(json.dumps(status, indent=2))

