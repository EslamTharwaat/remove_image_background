import os
import uuid
import threading
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from backgroundremover import bg
from PIL import Image
import io
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Performance optimization settings
app.config['ENABLE_IMAGE_OPTIMIZATION'] = True
app.config['MAX_IMAGE_SIZE'] = 1024  # Maximum dimension for processing
app.config['ENABLE_ALPHA_MATTING'] = False  # Disable for speed
app.config['ENABLE_MODEL_CACHING'] = True

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}

# Create directories if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Global variables for optimization
MODEL_CACHE = None
MODEL_LOCK = threading.Lock()

def get_optimized_model():
    """Get or create a cached model instance for faster processing"""
    global MODEL_CACHE
    with MODEL_LOCK:
        if MODEL_CACHE is None:
            # Initialize the model once and cache it
            MODEL_CACHE = bg.get_model('u2net')
        return MODEL_CACHE

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        # Generate unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Save the uploaded file
        file.save(filepath)
        
        try:
            start_time = time.time()
            
            # Optimize image size for faster processing
            optimized_filepath = optimize_image_size(filepath)
            
            # Remove background
            output_filename = f"no_bg_{unique_filename}"
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
            
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
                'original_image': f'/uploads/{unique_filename}',
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

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/outputs/<filename>')
def output_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

@app.route('/favicon.ico')
def favicon():
    return '', 204  # Return no content for favicon requests

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 