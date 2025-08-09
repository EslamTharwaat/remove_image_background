"""
API routes for programmatic access to background removal
"""
from flask import Blueprint, request, jsonify, send_file
from werkzeug.exceptions import BadRequest, UnsupportedMediaType
from app.utils.file_utils import (
    allowed_file, generate_secure_filename, validate_file_security,
    is_zip_file, validate_zip_file, extract_images_from_zip,
    cleanup_old_files, safe_join
)
from app.utils.auth import require_bearer_token, get_auth_info
from app.services.background_remover import BackgroundRemoverService
from app.services.batch_processor import BatchProcessor
from app.services.s3_service import S3Service
import os
import tempfile
import base64
from io import BytesIO

# Create API blueprint
api = Blueprint('api', __name__, url_prefix='/api/v1')

def init_api_routes(app, config):
    """Initialize API routes with app and config"""
    # Get the actual config instance
    config_instance = config if hasattr(config, 'AVAILABLE_MODELS') else app.config
    background_remover = BackgroundRemoverService(config_instance)
    batch_processor = BatchProcessor(config_instance, background_remover)
    s3_service = S3Service(config_instance)
    
    @api.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'service': 'background-remover',
            'version': '1.0.0',
            'authentication_required': config_instance.API_REQUIRE_AUTH
        })
    
    @api.route('/auth/info', methods=['GET'])
    def auth_info():
        """Get authentication information"""
        return jsonify(get_auth_info())
    
    @api.route('/process', methods=['POST'])
    @require_bearer_token
    def process_single_image():
        """
        Process a single image via API
        
        Expected format:
        - multipart/form-data with 'image' file
        - JSON with base64 encoded image in 'image_data' field
        
        Returns:
        - JSON response with processing results
        """
        # Clean up old files
        cleanup_old_files(config_instance.UPLOAD_FOLDER, config_instance.OUTPUT_FOLDER, config_instance.FILE_CLEANUP_MAX_AGE)
        
        # Fixed settings for human segmentation (API uses same simplified settings as web UI)
        quality_settings = {
            'alpha_matting': False  # Disabled for human segmentation
        }
        
        # Use human segmentation model (API is optimized for human background removal)
        ai_model = 'u2net_human_seg'
        
        # Check for file upload
        if 'image' in request.files:
            file = request.files['image']
            
            if file.filename == '':
                raise BadRequest("No image file provided")
            
            # Validate file
            is_valid, error_message = validate_file_security(file)
            if not is_valid:
                raise BadRequest(error_message)
            
            if not allowed_file(file.filename, config_instance.ALLOWED_EXTENSIONS):
                raise UnsupportedMediaType("Unsupported file format")
            
            # Process file upload
            secure_filename_gen = generate_secure_filename(file.filename)
            filepath = safe_join(config_instance.UPLOAD_FOLDER, secure_filename_gen)
            
            if filepath is None:
                raise BadRequest("Invalid file path")
            
            file.save(filepath)
            
        # Check for base64 encoded image
        elif 'image_data' in request.form:
            try:
                # Decode base64 image
                image_data = request.form['image_data']
                if image_data.startswith('data:image'):
                    # Remove data URL prefix
                    image_data = image_data.split(',')[1]
                
                image_bytes = base64.b64decode(image_data)
                
                # Save to temporary file
                secure_filename_gen = generate_secure_filename('api_image.jpg')
                filepath = safe_join(config_instance.UPLOAD_FOLDER, secure_filename_gen)
                
                if filepath is None:
                    raise BadRequest("Invalid file path")
                
                with open(filepath, 'wb') as f:
                    f.write(image_bytes)
                    
            except Exception as e:
                raise BadRequest(f"Invalid image data: {str(e)}")
        
        else:
            raise BadRequest("No image provided. Use 'image' file upload or 'image_data' base64 field")
        
        try:
            # Process image
            output_filename = f"no_bg_{secure_filename_gen}"
            output_path = safe_join(config_instance.OUTPUT_FOLDER, output_filename)
            
            if output_path is None:
                raise BadRequest("Invalid output path")
            
            result = background_remover.process_image(
                filepath, 
                output_path, 
                quality_settings, 
                ai_model
            )
            
            # Read processed image
            with open(output_path, 'rb') as f:
                processed_image_data = f.read()
            
            # Encode to base64
            processed_image_b64 = base64.b64encode(processed_image_data).decode('utf-8')
            
            return jsonify({
                'success': True,
                'message': f'Image processed successfully in {result["processing_time"]} seconds',
                'processing_time': result['processing_time'],
                'ai_model': result['ai_model'],
                'original_filename': file.filename if 'image' in request.files else 'api_image.jpg',
                'processed_image': f'data:image/png;base64,{processed_image_b64}',
                'download_url': f'/api/v1/download/{output_filename}'
            })
            
        except Exception as e:
            # Clean up uploaded file if processing fails
            if os.path.exists(filepath):
                os.remove(filepath)
            raise BadRequest(f"Error processing image: {str(e)}")
    
    @api.route('/process-zip', methods=['POST'])
    @require_bearer_token
    def process_zip_file():
        """
        Process multiple images from ZIP file
        
        Expected format:
        - multipart/form-data with 'zip_file' file
        
        Returns:
        - JSON response with batch processing results
        """
        # Clean up old files
        cleanup_old_files(config_instance.UPLOAD_FOLDER, config_instance.OUTPUT_FOLDER, config_instance.FILE_CLEANUP_MAX_AGE)
        
        if 'zip_file' not in request.files:
            raise BadRequest("No ZIP file provided")
        
        zip_file = request.files['zip_file']
        
        if zip_file.filename == '':
            raise BadRequest("No ZIP file selected")
        
        # Validate ZIP file
        is_valid, error_message = validate_zip_file(zip_file)
        if not is_valid:
            raise BadRequest(error_message)
        
        # Fixed settings for human segmentation (API uses same simplified settings as web UI)
        quality_settings = {
            'alpha_matting': False  # Disabled for human segmentation
        }
        
        # Use human segmentation model (API is optimized for human background removal)
        ai_model = 'u2net_human_seg'
        
        try:
            # Create temporary extraction folder
            with tempfile.TemporaryDirectory() as temp_dir:
                # Extract images from ZIP
                extracted_files = extract_images_from_zip(zip_file, temp_dir)
                
                if not extracted_files:
                    raise BadRequest("No valid images found in ZIP file")
                
                # Process images
                results = []
                errors = []
                
                for image_path in extracted_files:
                    try:
                        # Generate output filename
                        filename = os.path.basename(image_path)
                        output_filename = f"no_bg_{filename}"
                        output_path = safe_join(config_instance.OUTPUT_FOLDER, output_filename)
                        
                        if output_path is None:
                            continue
                        
                        # Process image
                        result = background_remover.process_image(
                            image_path, 
                            output_path, 
                            quality_settings, 
                            ai_model
                        )
                        
                        results.append({
                            'original_filename': filename,
                            'processed_filename': output_filename,
                            'processing_time': result['processing_time'],
                            'ai_model': result['ai_model'],
                            'download_url': f'/api/v1/download/{output_filename}'
                        })
                        
                    except Exception as e:
                        errors.append({
                            'filename': os.path.basename(image_path),
                            'error': str(e)
                        })
                
                return jsonify({
                    'success': True,
                    'message': f'Processed {len(results)} images from ZIP file',
                    'total_images': len(extracted_files),
                    'successful': len(results),
                    'failed': len(errors),
                    'results': results,
                    'errors': errors,
                    'quality_settings': quality_settings,
                    'ai_model': ai_model
                })
                
        except Exception as e:
            raise BadRequest(f"Error processing ZIP file: {str(e)}")
    
    @api.route('/download/<filename>', methods=['GET'])
    @require_bearer_token
    def download_processed_image(filename):
        """Download a processed image"""
        # Validate filename
        if not filename or '..' in filename or '/' in filename:
            raise BadRequest("Invalid filename")
        
        filepath = safe_join(config_instance.OUTPUT_FOLDER, filename)
        if filepath is None or not os.path.exists(filepath):
            raise BadRequest("File not found")
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='image/png'
        )
    
    @api.route('/models', methods=['GET'])
    @require_bearer_token
    def get_available_models():
        """Get list of available AI models (fixed to human segmentation)"""
        return jsonify({
            'models': ['u2net_human_seg'],
            'default_model': 'u2net_human_seg',
            'description': 'Optimized for human background removal'
        })
    
    @api.route('/settings', methods=['GET'])
    @require_bearer_token
    def get_default_settings():
        """Get default quality settings (fixed for human segmentation)"""
        return jsonify({
            'alpha_matting': False,
            'ai_model': 'u2net_human_seg',
            'description': 'Fixed settings optimized for human background removal',
            'max_file_size': config_instance.MAX_CONTENT_LENGTH,
            'allowed_extensions': list(config_instance.ALLOWED_EXTENSIONS)
        })
    
    @api.route('/test-s3', methods=['POST'])
    def test_s3_connection():
        """Test S3 connection with provided credentials"""
        try:
            data = request.get_json()
            
            # Create temporary config with S3 settings
            class TempConfig:
                def __init__(self, data):
                    self.ENABLE_S3_UPLOAD = data.get('enable_s3_upload', False)
                    self.S3_BUCKET_NAME = data.get('s3_bucket_name', '')
                    self.S3_ACCESS_KEY_ID = data.get('s3_access_key_id', '')
                    self.S3_SECRET_ACCESS_KEY = data.get('s3_secret_access_key', '')
                    self.S3_REGION_NAME = data.get('s3_region_name', 'us-east-1')
                    self.S3_FOLDER_PREFIX = data.get('s3_folder_prefix', 'background-remover/')
                    self.S3_PUBLIC_URL_EXPIRY = 3600
            
            temp_config = TempConfig(data)
            test_s3_service = S3Service(temp_config)
            
            # Test connection
            bucket_info = test_s3_service.get_bucket_info()
            
            if bucket_info.get('enabled') and 'error' not in bucket_info:
                return jsonify({
                    'success': True,
                    'bucket_name': bucket_info.get('bucket_name'),
                    'region': bucket_info.get('region'),
                    'message': 'S3 connection successful'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': bucket_info.get('error', 'Unknown error')
                })
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Connection test failed: {str(e)}'
            })
    
    # Register API blueprint
    app.register_blueprint(api) 