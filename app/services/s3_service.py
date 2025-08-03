"""
S3 Service for uploading files to AWS S3
"""
import boto3
import os
import logging
from botocore.exceptions import ClientError, NoCredentialsError
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

class S3Service:
    """Service for uploading files to AWS S3"""
    
    def __init__(self, config):
        self.config = config
        self.s3_client = None
        
        # Handle both config class and config dict
        if hasattr(config, 'S3_BUCKET_NAME'):
            # Config class instance
            self.bucket_name = config.S3_BUCKET_NAME
            self.region_name = config.S3_REGION_NAME
            self.folder_prefix = config.S3_FOLDER_PREFIX.rstrip('/') + '/'
        else:
            # Config dict
            self.bucket_name = config.get('S3_BUCKET_NAME', '')
            self.region_name = config.get('S3_REGION_NAME', 'us-east-1')
            self.folder_prefix = config.get('S3_FOLDER_PREFIX', 'background-remover/').rstrip('/') + '/'
        
        # Initialize S3 client if credentials are provided
        if self._validate_credentials():
            self._initialize_s3_client()
    
    def _validate_credentials(self) -> bool:
        """Validate S3 credentials are provided"""
        required_fields = [
            'S3_BUCKET_NAME',
            'S3_ACCESS_KEY_ID', 
            'S3_SECRET_ACCESS_KEY'
        ]
        
        for field in required_fields:
            if hasattr(self.config, field):
                # Config class instance
                if not getattr(self.config, field, ''):
                    logging.warning(f"S3 {field} not configured")
                    return False
            else:
                # Config dict
                if not self.config.get(field, ''):
                    logging.warning(f"S3 {field} not configured")
                    return False
        
        return True
    
    def _initialize_s3_client(self):
        """Initialize S3 client with credentials"""
        try:
            # Get credentials from config
            if hasattr(self.config, 'S3_ACCESS_KEY_ID'):
                # Config class instance
                access_key = self.config.S3_ACCESS_KEY_ID
                secret_key = self.config.S3_SECRET_ACCESS_KEY
                region = self.config.S3_REGION_NAME
            else:
                # Config dict
                access_key = self.config.get('S3_ACCESS_KEY_ID', '')
                secret_key = self.config.get('S3_SECRET_ACCESS_KEY', '')
                region = self.config.get('S3_REGION_NAME', 'us-east-1')
            
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )
            logging.info("S3 client initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize S3 client: {e}")
            self.s3_client = None
    
    def is_enabled(self) -> bool:
        """Check if S3 upload is enabled and configured"""
        # Check if S3 upload is enabled
        if hasattr(self.config, 'ENABLE_S3_UPLOAD'):
            # Config class instance
            enabled = self.config.ENABLE_S3_UPLOAD
        else:
            # Config dict
            enabled = self.config.get('ENABLE_S3_UPLOAD', False)
        
        return (
            enabled and 
            self.s3_client is not None and 
            self.bucket_name
        )
    
    def upload_file(self, file_path: str, filename: str) -> Optional[Dict[str, Any]]:
        """
        Upload a file to S3
        
        Args:
            file_path: Local path to the file
            filename: Name to use for the file in S3
            
        Returns:
            Dict with upload result or None if failed
        """
        if not self.is_enabled():
            logging.warning("S3 upload is not enabled or not configured")
            return None
        
        if not os.path.exists(file_path):
            logging.error(f"File not found: {file_path}")
            return None
        
        try:
            # Generate S3 key with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            s3_key = f"{self.folder_prefix}{timestamp}_{filename}"
            
            # Upload file to S3
            self.s3_client.upload_file(
                file_path,
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    'ContentType': 'image/png',
                    'ACL': 'public-read'
                }
            )
            
            # Generate public URL
            public_url = f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/{s3_key}"
            
            # Generate presigned URL for private access
            if hasattr(self.config, 'S3_PUBLIC_URL_EXPIRY'):
                # Config class instance
                expiry = self.config.S3_PUBLIC_URL_EXPIRY
            else:
                # Config dict
                expiry = self.config.get('S3_PUBLIC_URL_EXPIRY', 3600)
            
            presigned_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expiry
            )
            
            logging.info(f"File uploaded to S3: {s3_key}")
            
            return {
                'success': True,
                's3_key': s3_key,
                'public_url': public_url,
                'presigned_url': presigned_url,
                'bucket': self.bucket_name,
                'filename': filename
            }
            
        except NoCredentialsError:
            logging.error("AWS credentials not found")
            return None
        except ClientError as e:
            logging.error(f"AWS S3 error: {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error uploading to S3: {e}")
            return None
    
    def upload_multiple_files(self, file_paths: list, filenames: list) -> Dict[str, Any]:
        """
        Upload multiple files to S3
        
        Args:
            file_paths: List of local file paths
            filenames: List of filenames for S3
            
        Returns:
            Dict with upload results
        """
        if not self.is_enabled():
            return {
                'success': False,
                'error': 'S3 upload is not enabled or not configured',
                'results': []
            }
        
        results = []
        successful = 0
        failed = 0
        
        for file_path, filename in zip(file_paths, filenames):
            result = self.upload_file(file_path, filename)
            if result and result.get('success'):
                results.append(result)
                successful += 1
            else:
                results.append({
                    'success': False,
                    'filename': filename,
                    'error': 'Upload failed'
                })
                failed += 1
        
        return {
            'success': successful > 0,
            'total': len(file_paths),
            'successful': successful,
            'failed': failed,
            'results': results
        }
    
    def delete_file(self, s3_key: str) -> bool:
        """
        Delete a file from S3
        
        Args:
            s3_key: S3 key of the file to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled():
            return False
        
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            logging.info(f"File deleted from S3: {s3_key}")
            return True
        except Exception as e:
            logging.error(f"Failed to delete file from S3: {e}")
            return False
    
    def get_bucket_info(self) -> Dict[str, Any]:
        """
        Get information about the S3 bucket
        
        Returns:
            Dict with bucket information
        """
        if not self.is_enabled():
            return {
                'enabled': False,
                'error': 'S3 upload is not enabled or not configured'
            }
        
        try:
            # Test bucket access
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            
            return {
                'enabled': True,
                'bucket_name': self.bucket_name,
                'region': self.region_name,
                'folder_prefix': self.folder_prefix,
                'status': 'connected'
            }
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                return {
                    'enabled': True,
                    'error': f'Bucket "{self.bucket_name}" not found'
                }
            elif error_code == '403':
                return {
                    'enabled': True,
                    'error': 'Access denied to bucket'
                }
            else:
                return {
                    'enabled': True,
                    'error': f'AWS error: {error_code}'
                }
        except Exception as e:
            return {
                'enabled': True,
                'error': f'Connection error: {str(e)}'
            } 