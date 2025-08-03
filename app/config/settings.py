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
    
    # Background removal quality settings
    DEFAULT_ALPHA_MATTING = False
    DEFAULT_ALPHA_MATTING_FOREGROUND_THRESHOLD = 240
    DEFAULT_ALPHA_MATTING_BACKGROUND_THRESHOLD = 10
    DEFAULT_ALPHA_MATTING_ERODE_SIZE = 10
    DEFAULT_ALPHA_MATTING_BASE_SIZE = 1000
    
    # AI model settings
    AVAILABLE_MODELS = ['u2net', 'u2netp', 'u2net_human_seg', 'u2net_cloth_seg']
    DEFAULT_MODEL = 'u2net'
    
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