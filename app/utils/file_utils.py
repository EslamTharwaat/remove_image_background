"""
File utility functions for handling file operations
"""
import os
import hashlib
import time
from pathlib import Path
from werkzeug.utils import secure_filename
from werkzeug.security import safe_join
from PIL import Image
import io


def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def generate_secure_filename(original_filename):
    """Generate a secure filename using SHA256 hash"""
    if not original_filename:
        return None
    
    # Get file extension
    file_ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
    
    # Generate hash from filename and timestamp
    hash_input = f"{original_filename}_{time.time()}"
    filename_hash = hashlib.sha256(hash_input.encode()).hexdigest()
    
    # Return filename with original extension
    return f"{filename_hash}.{file_ext}" if file_ext else filename_hash


def validate_file_security(file):
    """Validate file for security issues"""
    if not file or not file.filename:
        return False, "No file provided"
    
    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # Reset file pointer
    
    if file_size > 16 * 1024 * 1024:  # 16MB limit
        return False, "File size exceeds 16MB limit"
    
    # Check for null bytes in filename
    if '\x00' in file.filename:
        return False, "Invalid filename contains null bytes"
    
    # Check for path traversal attempts
    if '..' in file.filename or '/' in file.filename:
        return False, "Invalid filename contains path traversal characters"
    
    return True, "File is valid"


def optimize_image_size(image_path, max_size=None):
    """Optimize image size for faster processing"""
    if max_size is None:
        max_size = 1024
    
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Check if resizing is needed
            if max(img.size) <= max_size:
                return image_path
            
            # Calculate new dimensions
            ratio = max_size / max(img.size)
            new_size = tuple(int(dim * ratio) for dim in img.size)
            
            # Resize image
            img_resized = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # Save optimized image
            optimized_path = f"{image_path}_optimized.jpg"
            img_resized.save(optimized_path, 'JPEG', quality=85, optimize=True)
            
            return optimized_path
            
    except Exception as e:
        print(f"Error optimizing image {image_path}: {e}")
        return image_path


def cleanup_old_files(upload_folder, output_folder, max_age=3600):
    """Clean up old uploaded and processed files"""
    current_time = time.time()
    
    for folder in [upload_folder, output_folder]:
        if not os.path.exists(folder):
            continue
            
        for filename in os.listdir(folder):
            filepath = os.path.join(folder, filename)
            if os.path.isfile(filepath):
                file_age = current_time - os.path.getmtime(filepath)
                if file_age > max_age:
                    try:
                        os.remove(filepath)
                    except OSError:
                        pass


def ensure_directories_exist(*directories):
    """Ensure that all specified directories exist"""
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)


def get_file_info(filepath):
    """Get file information"""
    if not os.path.exists(filepath):
        return None
    
    stat = os.stat(filepath)
    return {
        'size': stat.st_size,
        'modified': stat.st_mtime,
        'created': stat.st_ctime
    } 