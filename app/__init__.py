"""
Flask Application Factory
"""
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from app.config.settings import config
from app.routes.main import init_routes
from app.routes.api import init_api_routes
from app.utils.file_utils import ensure_directories_exist


def create_app(config_name='default'):
    """Create and configure Flask application"""
    
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize CSRF protection
    csrf = CSRFProtect(app)
    
    # Ensure required directories exist
    ensure_directories_exist(
        app.config['UPLOAD_FOLDER'],
        app.config['OUTPUT_FOLDER']
    )
    
    # Initialize routes
    init_routes(app, app.config)
    
    # Initialize API routes
    init_api_routes(app, config[config_name])
    
    # Disable CSRF for API routes after blueprint registration
    if 'api' in app.blueprints:
        csrf.exempt(app.blueprints['api'])
    
    return app 