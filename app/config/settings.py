"""
Application Configuration Settings
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Flask Configuration
class Config:
    """Base configuration class"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24).hex()
    
    # File upload settings
    UPLOAD_FOLDER = 'uploads'
    OUTPUT_FOLDER = 'outputs'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}
    
    # Performance optimization settings
    ENABLE_IMAGE_OPTIMIZATION = True
    MAX_IMAGE_SIZE = 1024  # Maximum dimension for processing
    ENABLE_ALPHA_MATTING = False  # Disable for speed
    ENABLE_MODEL_CACHING = True
    
    # Background removal quality settings - simplified for human segmentation
    DEFAULT_ALPHA_MATTING = False
    
    # AI model settings - optimized for humans wearing clothes
    AVAILABLE_MODELS = ['u2net_human_seg']
    DEFAULT_MODEL = 'u2net_human_seg'
    
    # S3 Configuration
    ENABLE_S3_UPLOAD = False
    S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', '')
    S3_ACCESS_KEY_ID = os.environ.get('S3_ACCESS_KEY_ID', '')
    S3_SECRET_ACCESS_KEY = os.environ.get('S3_SECRET_ACCESS_KEY', '')
    S3_REGION_NAME = os.environ.get('S3_REGION_NAME', 'us-east-1')
    S3_FOLDER_PREFIX = os.environ.get('S3_FOLDER_PREFIX', 'background-remover/')
    S3_PUBLIC_URL_EXPIRY = 3600  # 1 hour
    
    # Security settings
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # File cleanup settings
    FILE_CLEANUP_MAX_AGE = 3600  # 1 hour
    
    # Batch processing settings
    MAX_BATCH_WORKERS = 4
    BATCH_STATUS_POLL_INTERVAL = 1  # seconds
    
    # API Authentication settings
    API_REQUIRE_AUTH = True
    API_BEARER_TOKEN = os.environ.get('API_BEARER_TOKEN', 'otrium-bg-remover-2025-secure-token')
    API_TOKEN_HEADER = 'Authorization'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 