"""
Main routes for the background removal application
"""
from flask import Blueprint, render_template, request, jsonify, send_from_directory
from app.utils.file_utils import (
    allowed_file, generate_secure_filename, validate_file_security, 
    cleanup_old_files, ensure_directories_exist, safe_join,
    is_zip_file, validate_zip_file, extract_images_from_zip
)
from app.services.background_remover import BackgroundRemoverService
from app.services.batch_processor import BatchProcessor
from app.services.s3_service import S3Service
import os
import tempfile

# Create blueprint
main = Blueprint('main', __name__)

def init_routes(app, config):
    """Initialize routes with app and config"""
    background_remover = BackgroundRemoverService(config)
    batch_processor = BatchProcessor(config, background_remover)
    s3_service = S3Service(config)
    
    @main.route('/')
    def index():
        """Main page"""
        return render_template('index.html')
    
    @main.route('/settings')
    def settings():
        """Settings page"""
        return render_template('settings.html')
    
    @main.route('/upload', methods=['POST'])
    def upload_file():
        """Handle single image upload and background removal"""
        # Clean up old files for security
        cleanup_old_files(config.UPLOAD_FOLDER, config.OUTPUT_FOLDER, config.FILE_CLEANUP_MAX_AGE)
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        # Validate file security
        is_valid, error_message = validate_file_security(file)
        if not is_valid:
            return jsonify({'error': error_message}), 400
        
        # Get quality settings from request
        quality_settings = {
            'alpha_matting': request.form.get('alpha_matting', 'false').lower() == 'true',
            'foreground_threshold': int(request.form.get('foreground_threshold', config.DEFAULT_ALPHA_MATTING_FOREGROUND_THRESHOLD)),
            'background_threshold': int(request.form.get('background_threshold', config.DEFAULT_ALPHA_MATTING_BACKGROUND_THRESHOLD)),
            'erode_size': int(request.form.get('erode_size', config.DEFAULT_ALPHA_MATTING_ERODE_SIZE)),
            'base_size': int(request.form.get('base_size', config.DEFAULT_ALPHA_MATTING_BASE_SIZE))
        }
        
        # Get AI model selection
        ai_model = request.form.get('ai_model', config.DEFAULT_MODEL)
        if ai_model not in config.AVAILABLE_MODELS:
            ai_model = config.DEFAULT_MODEL
        
        if file and allowed_file(file.filename, config.ALLOWED_EXTENSIONS):
            # Generate secure filename
            secure_filename_gen = generate_secure_filename(file.filename)
            filepath = safe_join(config.UPLOAD_FOLDER, secure_filename_gen)
            
            if filepath is None:
                return jsonify({'error': 'Invalid file path'}), 400
            
            # Save the uploaded file
            file.save(filepath)
            
            try:
                # Remove background
                output_filename = f"no_bg_{secure_filename_gen}"
                output_path = safe_join(config.OUTPUT_FOLDER, output_filename)
                
                if output_path is None:
                    return jsonify({'error': 'Invalid output path'}), 400
                
                # Process image
                result = background_remover.process_image(
                    filepath, 
                    output_path, 
                    quality_settings, 
                    ai_model
                )
                
                # Upload to S3 if enabled
                s3_result = None
                if s3_service.is_enabled():
                    s3_result = s3_service.upload_file(output_path, output_filename)
                
                response_data = {
                    'success': True,
                    'original_image': f'/uploads/{secure_filename_gen}',
                    'processed_image': f'/outputs/{output_filename}',
                    'message': f'Background removed successfully in {result["processing_time"]} seconds!',
                    'processing_time': result['processing_time'],
                    'ai_model': result['ai_model']
                }
                
                # Add S3 information if upload was successful
                if s3_result and s3_result.get('success'):
                    response_data['s3_upload'] = {
                        'success': True,
                        'public_url': s3_result['public_url'],
                        'presigned_url': s3_result['presigned_url'],
                        's3_key': s3_result['s3_key']
                    }
                elif s3_service.is_enabled():
                    response_data['s3_upload'] = {
                        'success': False,
                        'error': 'S3 upload failed'
                    }
                
                return jsonify(response_data)
                
            except Exception as e:
                # Clean up uploaded file if processing fails
                if os.path.exists(filepath):
                    os.remove(filepath)
                return jsonify({'error': f'Error processing image: {str(e)}'}), 500
        
        return jsonify({'error': 'Invalid file type'}), 400
    
    @main.route('/batch-upload', methods=['POST'])
    def batch_upload():
        """Handle batch upload of multiple images"""
        # Clean up old files for security
        cleanup_old_files(config.UPLOAD_FOLDER, config.OUTPUT_FOLDER, config.FILE_CLEANUP_MAX_AGE)
        
        if 'files[]' not in request.files:
            return jsonify({'error': 'No files uploaded'}), 400
        
        files = request.files.getlist('files[]')
        
        if not files or all(file.filename == '' for file in files):
            return jsonify({'error': 'No files selected'}), 400
        
        # Get quality settings from request
        quality_settings = {
            'alpha_matting': request.form.get('alpha_matting', 'false').lower() == 'true',
            'foreground_threshold': int(request.form.get('foreground_threshold', config.DEFAULT_ALPHA_MATTING_FOREGROUND_THRESHOLD)),
            'background_threshold': int(request.form.get('background_threshold', config.DEFAULT_ALPHA_MATTING_BACKGROUND_THRESHOLD)),
            'erode_size': int(request.form.get('erode_size', config.DEFAULT_ALPHA_MATTING_ERODE_SIZE)),
            'base_size': int(request.form.get('base_size', config.DEFAULT_ALPHA_MATTING_BASE_SIZE))
        }
        
        # Get AI model selection
        ai_model = request.form.get('ai_model', config.DEFAULT_MODEL)
        if ai_model not in config.AVAILABLE_MODELS:
            ai_model = config.DEFAULT_MODEL
        
        # Validate all files
        valid_files = []
        for file in files:
            if file.filename:
                # Check if it's a ZIP file
                if is_zip_file(file.filename):
                    is_valid, error_message = validate_zip_file(file)
                    if is_valid:
                        # Extract images from ZIP
                        try:
                            with tempfile.TemporaryDirectory() as temp_dir:
                                extracted_files = extract_images_from_zip(file, temp_dir)
                                
                                # Create FileStorage-like objects for extracted files
                                for extracted_path in extracted_files:
                                    with open(extracted_path, 'rb') as f:
                                        file_data = f.read()
                                    
                                    # Create a proper mock file object
                                    class MockFile:
                                        def __init__(self, filename, data):
                                            self.filename = filename
                                            self._data = data
                                            self._position = 0
                                        
                                        def read(self, size=None):
                                            if size is None:
                                                return self._data
                                            else:
                                                data = self._data[self._position:self._position + size]
                                                self._position += size
                                                return data
                                        
                                        def seek(self, position):
                                            self._position = position
                                        
                                        def save(self, path):
                                            with open(path, 'wb') as f:
                                                f.write(self._data)
                                    
                                    mock_file = MockFile(os.path.basename(extracted_path), file_data)
                                    valid_files.append(mock_file)
                        except Exception as e:
                            return jsonify({'error': f'Error processing ZIP file {file.filename}: {str(e)}'}), 400
                    else:
                        return jsonify({'error': f'Invalid ZIP file {file.filename}: {error_message}'}), 400
                else:
                    # Regular image file
                    is_valid, error_message = validate_file_security(file)
                    if is_valid and allowed_file(file.filename, config.ALLOWED_EXTENSIONS):
                        valid_files.append(file)
                    else:
                        return jsonify({'error': f'Invalid file {file.filename}: {error_message}'}), 400
        
        if not valid_files:
            return jsonify({'error': 'No valid files found'}), 400
        
        # Process batch
        batch_id = batch_processor.process_batch(valid_files, quality_settings, ai_model)
        
        return jsonify({
            'success': True,
            'batch_id': batch_id,
            'total_files': len(valid_files),
            'message': f'Started processing {len(valid_files)} images in parallel'
        })
    
    @main.route('/batch-status/<batch_id>')
    def batch_status(batch_id):
        """Get batch processing status"""
        status = batch_processor.get_batch_status(batch_id)
        if status is None:
            return jsonify({'error': 'Batch not found'}), 404
        
        return jsonify(status)
    
    @main.route('/reprocess', methods=['POST'])
    def reprocess_image():
        """Reprocess an image with different settings"""
        # Clean up old files for security
        cleanup_old_files(config.UPLOAD_FOLDER, config.OUTPUT_FOLDER, config.FILE_CLEANUP_MAX_AGE)
        
        # Get image path and settings from request
        image_path = request.form.get('image_path')
        if not image_path:
            return jsonify({'error': 'No image path provided'}), 400
        
        # Validate image path for security
        if not image_path.startswith('/uploads/') or '..' in image_path or '/' in image_path[9:]:
            return jsonify({'error': 'Invalid image path'}), 400
        
        # Get quality settings from request
        quality_settings = {
            'alpha_matting': request.form.get('alpha_matting', 'false').lower() == 'true',
            'foreground_threshold': int(request.form.get('foreground_threshold', config.DEFAULT_ALPHA_MATTING_FOREGROUND_THRESHOLD)),
            'background_threshold': int(request.form.get('background_threshold', config.DEFAULT_ALPHA_MATTING_BACKGROUND_THRESHOLD)),
            'erode_size': int(request.form.get('erode_size', config.DEFAULT_ALPHA_MATTING_ERODE_SIZE)),
            'base_size': int(request.form.get('base_size', config.DEFAULT_ALPHA_MATTING_BASE_SIZE))
        }
        
        # Get AI model selection
        ai_model = request.form.get('ai_model', config.DEFAULT_MODEL)
        if ai_model not in config.AVAILABLE_MODELS:
            ai_model = config.DEFAULT_MODEL
        
        try:
            # Extract filename from path
            filename = image_path.split('/')[-1]
            filepath = safe_join(config.UPLOAD_FOLDER, filename)
            
            if filepath is None or not os.path.exists(filepath):
                return jsonify({'error': 'Image file not found'}), 404
            
            # Remove background
            output_filename = f"no_bg_{filename}"
            output_path = safe_join(config.OUTPUT_FOLDER, output_filename)
            
            if output_path is None:
                return jsonify({'error': 'Invalid output path'}), 400
            
            # Process image
            result = background_remover.process_image(
                filepath, 
                output_path, 
                quality_settings, 
                ai_model
            )
            
            return jsonify({
                'success': True,
                'original_image': image_path,
                'processed_image': f'/outputs/{output_filename}',
                'message': f'Image reprocessed successfully in {result["processing_time"]} seconds!',
                'processing_time': result['processing_time'],
                'ai_model': result['ai_model']
            })
            
        except Exception as e:
            return jsonify({'error': f'Error reprocessing image: {str(e)}'}), 500
    

    
    @main.route('/uploads/<filename>')
    def uploaded_file(filename):
        """Serve uploaded files"""
        # Validate filename for security
        if not filename or '..' in filename or '/' in filename:
            return jsonify({'error': 'Invalid filename'}), 400
        
        filepath = safe_join(config.UPLOAD_FOLDER, filename)
        if filepath is None or not os.path.exists(filepath):
            return jsonify({'error': f'File not found: {filepath}'}), 404
        
        try:
            # Use absolute path
            abs_path = os.path.abspath(config.UPLOAD_FOLDER)
            response = send_from_directory(abs_path, filename)
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            return response
        except Exception as e:
            return jsonify({'error': f'Send from directory error: {str(e)}', 'path': abs_path if 'abs_path' in locals() else 'not set'}), 500
    
    @main.route('/outputs/<filename>')
    def output_file(filename):
        """Serve processed files"""
        # Validate filename for security
        if not filename or '..' in filename or '/' in filename:
            return jsonify({'error': 'Invalid filename'}), 400
        
        filepath = safe_join(config.OUTPUT_FOLDER, filename)
        if filepath is None or not os.path.exists(filepath):
            return jsonify({'error': f'File not found: {filepath}'}), 404
        
        try:
            # Use absolute path
            abs_path = os.path.abspath(config.OUTPUT_FOLDER)
            response = send_from_directory(abs_path, filename)
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            return response
        except Exception as e:
            return jsonify({'error': f'Send from directory error: {str(e)}', 'path': abs_path if 'abs_path' in locals() else 'not set'}), 500
    
    @main.route('/favicon.ico')
    def favicon():
        """Handle favicon requests"""
        return ('', 204)
    
    # Register blueprint
    app.register_blueprint(main) 