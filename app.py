import os
import uuid
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from backgroundremover import bg
from PIL import Image
import io

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}

# Create directories if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
            # Remove background
            output_filename = f"no_bg_{unique_filename}"
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
            
            # Use backgroundremover library
            with open(filepath, 'rb') as input_file:
                input_data = input_file.read()
            
            # Remove background using the correct API
            output_data = bg.remove(input_data)
            
            # Save the processed image
            with open(output_path, 'wb') as output_file:
                output_file.write(output_data)
            
            return jsonify({
                'success': True,
                'original_image': f'/uploads/{unique_filename}',
                'processed_image': f'/outputs/{output_filename}',
                'message': 'Background removed successfully!'
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