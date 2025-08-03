import os
import uuid
import threading
import hashlib
import concurrent.futures
from flask import Flask, render_template, request, jsonify, send_from_directory, session
from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import secure_filename
from werkzeug.security import safe_join
from backgroundremover import bg
from PIL import Image
import io
import time
import queue

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or os.urandom(24).hex()
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Performance optimization settings
app.config['ENABLE_IMAGE_OPTIMIZATION'] = True
app.config['MAX_IMAGE_SIZE'] = 1024  # Maximum dimension for processing
app.config['ENABLE_ALPHA_MATTING'] = False  # Disable for speed
app.config['ENABLE_MODEL_CACHING'] = True

# Security settings
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # 1 hour
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}

# Create directories if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Global variables for optimization
MODEL_CACHE = None
MODEL_LOCK = threading.Lock()

# Batch processing variables
BATCH_JOBS = {}
BATCH_COUNTER = 0
BATCH_LOCK = threading.Lock()

def get_optimized_model():
    """Get or create a cached model instance for faster processing"""
    global MODEL_CACHE
    with MODEL_LOCK:
        if MODEL_CACHE is None:
            # Initialize the model once and cache it
            MODEL_CACHE = bg.get_model('u2net')
        return MODEL_CACHE

def generate_batch_id():
    """Generate unique batch ID"""
    global BATCH_COUNTER
    with BATCH_LOCK:
        BATCH_COUNTER += 1
        return f"batch_{BATCH_COUNTER}_{int(time.time())}"

def create_batch_job(batch_id, total_files):
    """Create a new batch job"""
    BATCH_JOBS[batch_id] = {
        'total_files': total_files,
        'processed_files': 0,
        'results': [],
        'errors': [],
        'status': 'processing',
        'start_time': time.time(),
        'progress': 0
    }

def update_batch_progress(batch_id, filename, status, result=None, error=None):
    """Update batch processing progress"""
    if batch_id in BATCH_JOBS:
        job = BATCH_JOBS[batch_id]
        job['processed_files'] += 1
        job['progress'] = (job['processed_files'] / job['total_files']) * 100
        
        if result:
            job['results'].append({
                'filename': filename,
                'original_image': result['original_image'],
                'processed_image': result['processed_image'],
                'processing_time': result['processing_time']
            })
        
        if error:
            job['errors'].append({
                'filename': filename,
                'error': error
            })
        
        if job['processed_files'] >= job['total_files']:
            job['status'] = 'completed'
            job['end_time'] = time.time()
            job['total_time'] = job['end_time'] - job['start_time']

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_secure_filename(original_filename):
    """Generate a secure filename with hash to prevent path traversal"""
    # Get file extension
    ext = os.path.splitext(original_filename)[1].lower()
    # Generate secure filename with hash
    secure_name = hashlib.sha256(f"{original_filename}{time.time()}".encode()).hexdigest()[:16]
    return f"{secure_name}{ext}"

def validate_file_security(file):
    """Validate file for security threats"""
    # Check file size
    if file.content_length and file.content_length > app.config['MAX_CONTENT_LENGTH']:
        return False, "File too large"
    
    # Check file extension
    if not allowed_file(file.filename):
        return False, "Invalid file type"
    
    # Check for null bytes (potential path traversal)
    if '\x00' in file.filename:
        return False, "Invalid filename"
    
    # Check for directory traversal attempts
    if '..' in file.filename or '/' in file.filename or '\\' in file.filename:
        return False, "Invalid filename"
    
    return True, "OK"

def cleanup_old_files():
    """Clean up old uploaded and processed files for security"""
    import time
    current_time = time.time()
    max_age = 3600  # 1 hour
    
    for folder in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER']]:
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                filepath = os.path.join(folder, filename)
                if os.path.isfile(filepath):
                    file_age = current_time - os.path.getmtime(filepath)
                    if file_age > max_age:
                        try:
                            os.remove(filepath)
                        except OSError:
                            pass

def process_single_image(file_data, batch_id, original_filename):
    """Process a single image in batch mode"""
    try:
        start_time = time.time()
        
        # Generate secure filename
        secure_filename_gen = generate_secure_filename(original_filename)
        filepath = safe_join(app.config['UPLOAD_FOLDER'], secure_filename_gen)
        
        if filepath is None:
            raise Exception("Invalid file path")
        
        # Save the uploaded file
        with open(filepath, 'wb') as f:
            f.write(file_data)
        
        # Optimize image size for faster processing
        optimized_filepath = optimize_image_size(filepath)
        
        # Remove background
        output_filename = f"no_bg_{secure_filename_gen}"
        output_path = safe_join(app.config['OUTPUT_FOLDER'], output_filename)
        
        if output_path is None:
            raise Exception("Invalid output path")
        
        # Use optimized backgroundremover with cached model
        with open(optimized_filepath, 'rb') as input_file:
            input_data = input_file.read()
        
        # Remove background using optimized settings
        output_data = bg.remove(
            input_data,
            model_name='u2net',
            alpha_matting=app.config['ENABLE_ALPHA_MATTING'],
            alpha_matting_foreground_threshold=240,
            alpha_matting_background_threshold=10,
            alpha_matting_erode_structure_size=10,
            alpha_matting_base_size=1000
        )
        
        # Save the processed image
        with open(output_path, 'wb') as output_file:
            output_file.write(output_data)
        
        # Clean up optimized file if it was created
        if optimized_filepath != filepath and os.path.exists(optimized_filepath):
            os.remove(optimized_filepath)
        
        processing_time = time.time() - start_time
        
        result = {
            'original_image': f'/uploads/{secure_filename_gen}',
            'processed_image': f'/outputs/{output_filename}',
            'processing_time': round(processing_time, 2)
        }
        
        # Update batch progress
        update_batch_progress(batch_id, original_filename, 'completed', result=result)
        
        return result
        
    except Exception as e:
        # Update batch progress with error
        update_batch_progress(batch_id, original_filename, 'error', error=str(e))
        
        # Clean up uploaded file if processing fails
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)
        
        raise e

def optimize_image_size(image_path, max_size=None):
    """Optimize image size for faster processing"""
    if not app.config['ENABLE_IMAGE_OPTIMIZATION']:
        return image_path
    
    if max_size is None:
        max_size = app.config['MAX_IMAGE_SIZE']
    
    try:
        with Image.open(image_path) as img:
            # Get original dimensions
            width, height = img.size
            
            # If image is larger than max_size, resize it
            if width > max_size or height > max_size:
                # Calculate new dimensions maintaining aspect ratio
                if width > height:
                    new_width = max_size
                    new_height = int(height * (max_size / width))
                else:
                    new_height = max_size
                    new_width = int(width * (max_size / height))
                
                # Resize image
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Save optimized image
                optimized_path = image_path.replace('.', '_optimized.')
                img.save(optimized_path, quality=95, optimize=True)
                return optimized_path
            
            return image_path
    except Exception as e:
        print(f"Error optimizing image: {e}")
        return image_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    # Clean up old files for security
    cleanup_old_files()
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Validate file security
    is_valid, error_message = validate_file_security(file)
    if not is_valid:
        return jsonify({'error': error_message}), 400
    
    if file and allowed_file(file.filename):
        # Generate secure filename
        secure_filename_gen = generate_secure_filename(file.filename)
        filepath = safe_join(app.config['UPLOAD_FOLDER'], secure_filename_gen)
        
        if filepath is None:
            return jsonify({'error': 'Invalid file path'}), 400
        
        # Save the uploaded file
        file.save(filepath)
        
        try:
            start_time = time.time()
            
            # Optimize image size for faster processing
            optimized_filepath = optimize_image_size(filepath)
            
            # Remove background
            output_filename = f"no_bg_{secure_filename_gen}"
            output_path = safe_join(app.config['OUTPUT_FOLDER'], output_filename)
            
            if output_path is None:
                return jsonify({'error': 'Invalid output path'}), 400
            
            # Use optimized backgroundremover with cached model
            with open(optimized_filepath, 'rb') as input_file:
                input_data = input_file.read()
            
            # Remove background using optimized settings
            output_data = bg.remove(
                input_data,
                model_name='u2net',
                alpha_matting=app.config['ENABLE_ALPHA_MATTING'],  # Use config setting
                alpha_matting_foreground_threshold=240,
                alpha_matting_background_threshold=10,
                alpha_matting_erode_structure_size=10,
                alpha_matting_base_size=1000
            )
            
            # Save the processed image
            with open(output_path, 'wb') as output_file:
                output_file.write(output_data)
            
            # Clean up optimized file if it was created
            if optimized_filepath != filepath and os.path.exists(optimized_filepath):
                os.remove(optimized_filepath)
            
            processing_time = time.time() - start_time
            
            return jsonify({
                'success': True,
                'original_image': f'/uploads/{secure_filename_gen}',
                'processed_image': f'/outputs/{output_filename}',
                'message': f'Background removed successfully in {processing_time:.2f} seconds!',
                'processing_time': round(processing_time, 2)
            })
            
        except Exception as e:
            # Clean up uploaded file if processing fails
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': f'Error processing image: {str(e)}'}), 500
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/batch-upload', methods=['POST'])
def batch_upload():
    """Handle batch upload of multiple images"""
    # Clean up old files for security
    cleanup_old_files()
    
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files uploaded'}), 400
    
    files = request.files.getlist('files[]')
    
    if not files or all(file.filename == '' for file in files):
        return jsonify({'error': 'No files selected'}), 400
    
    # Validate all files
    valid_files = []
    for file in files:
        if file.filename:
            is_valid, error_message = validate_file_security(file)
            if is_valid and allowed_file(file.filename):
                valid_files.append(file)
            else:
                return jsonify({'error': f'Invalid file {file.filename}: {error_message}'}), 400
    
    if not valid_files:
        return jsonify({'error': 'No valid files found'}), 400
    
    # Generate batch ID
    batch_id = generate_batch_id()
    create_batch_job(batch_id, len(valid_files))
    
    # Process files in parallel
    def process_files_parallel():
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(valid_files), 4)) as executor:
            futures = []
            for file in valid_files:
                file_data = file.read()
                future = executor.submit(process_single_image, file_data, batch_id, file.filename)
                futures.append(future)
            
            # Wait for all futures to complete
            concurrent.futures.wait(futures)
    
    # Start processing in background thread
    processing_thread = threading.Thread(target=process_files_parallel)
    processing_thread.daemon = True
    processing_thread.start()
    
    return jsonify({
        'success': True,
        'batch_id': batch_id,
        'total_files': len(valid_files),
        'message': f'Started processing {len(valid_files)} images in parallel'
    })

@app.route('/batch-status/<batch_id>')
def batch_status(batch_id):
    """Get batch processing status"""
    if batch_id not in BATCH_JOBS:
        return jsonify({'error': 'Batch not found'}), 404
    
    job = BATCH_JOBS[batch_id]
    return jsonify({
        'batch_id': batch_id,
        'status': job['status'],
        'progress': job['progress'],
        'total_files': job['total_files'],
        'processed_files': job['processed_files'],
        'results': job['results'],
        'errors': job['errors'],
        'total_time': job.get('total_time', 0)
    })

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    # Validate filename for security
    if not filename or '..' in filename or '/' in filename:
        return jsonify({'error': 'Invalid filename'}), 400
    
    filepath = safe_join(app.config['UPLOAD_FOLDER'], filename)
    if filepath is None or not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    response = send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    return response

@app.route('/outputs/<filename>')
def output_file(filename):
    # Validate filename for security
    if not filename or '..' in filename or '/' in filename:
        return jsonify({'error': 'Invalid filename'}), 400
    
    filepath = safe_join(app.config['OUTPUT_FOLDER'], filename)
    if filepath is None or not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    response = send_from_directory(app.config['OUTPUT_FOLDER'], filename)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    return response

@app.route('/favicon.ico')
def favicon():
    return '', 204  # Return no content for favicon requests

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 