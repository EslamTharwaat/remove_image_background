"""
File utility functions for handling file operations
"""
import os
import hashlib
import time
import zipfile
from pathlib import Path
from werkzeug.utils import secure_filename
from werkzeug.security import safe_join
from PIL import Image
import io


def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def is_zip_file(filename):
    """Check if file is a ZIP file"""
    return filename.lower().endswith('.zip')


def extract_images_from_zip(zip_file, extract_to_folder):
    """
    Extract images from ZIP file
    
    Args:
        zip_file: FileStorage object containing ZIP file
        extract_to_folder: Folder to extract images to
    
    Returns:
        list: List of extracted image file paths
    """
    extracted_files = []
    
    try:
        # Create extraction folder if it doesn't exist
        Path(extract_to_folder).mkdir(parents=True, exist_ok=True)
        
        # Read ZIP file
        zip_data = zip_file.read()
        zip_file.seek(0)  # Reset file pointer
        
        # Open ZIP file
        with zipfile.ZipFile(io.BytesIO(zip_data), 'r') as zip_ref:
            # Get list of files in ZIP
            file_list = zip_ref.namelist()
            
            # Filter for image files
            image_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}
            image_files = [
                f for f in file_list 
                if not f.endswith('/') and  # Skip directories
                '.' in f and  # Has extension
                f.rsplit('.', 1)[1].lower() in image_extensions
            ]
            
            if not image_files:
                raise ValueError("No image files found in ZIP")
            
            # Extract each image file
            for image_file in image_files:
                try:
                    # Generate secure filename
                    original_filename = os.path.basename(image_file)
                    secure_filename_gen = generate_secure_filename(original_filename)
                    extract_path = safe_join(extract_to_folder, secure_filename_gen)
                    
                    if extract_path is None:
                        continue
                    
                    # Extract file
                    zip_ref.extract(image_file, extract_to_folder)
                    
                    # Rename to secure filename
                    temp_path = os.path.join(extract_to_folder, image_file)
                    if os.path.exists(temp_path):
                        os.rename(temp_path, extract_path)
                        extracted_files.append(extract_path)
                    
                except Exception as e:
                    print(f"Error extracting {image_file}: {e}")
                    continue
        
        return extracted_files
        
    except Exception as e:
        raise ValueError(f"Error processing ZIP file: {str(e)}")


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
    
    if file_size > 50 * 1024 * 1024:  # 50MB limit for ZIP files
        return False, "File size exceeds 50MB limit"
    
    # Check for null bytes in filename
    if '\x00' in file.filename:
        return False, "Invalid filename contains null bytes"
    
    # Check for path traversal attempts
    if '..' in file.filename or '/' in file.filename:
        return False, "Invalid filename contains path traversal characters"
    
    return True, "File is valid"


def validate_zip_file(zip_file):
    """Validate ZIP file for security and content"""
    if not zip_file or not zip_file.filename:
        return False, "No ZIP file provided"
    
    # Check if it's actually a ZIP file
    if not is_zip_file(zip_file.filename):
        return False, "File is not a valid ZIP file"
    
    # Basic security validation
    is_valid, error_message = validate_file_security(zip_file)
    if not is_valid:
        return False, error_message
    
    try:
        # Read ZIP file
        zip_data = zip_file.read()
        zip_file.seek(0)  # Reset file pointer
        
        # Try to open as ZIP
        with zipfile.ZipFile(io.BytesIO(zip_data), 'r') as zip_ref:
            # Check for zip bomb (too many files)
            if len(zip_ref.namelist()) > 100:
                return False, "ZIP file contains too many files (max 100)"
            
            # Check total uncompressed size
            total_size = sum(info.file_size for info in zip_ref.filelist)
            if total_size > 100 * 1024 * 1024:  # 100MB limit
                return False, "ZIP file uncompressed size exceeds 100MB limit"
            
            # Check for image files
            image_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}
            image_files = [
                f for f in zip_ref.namelist() 
                if not f.endswith('/') and '.' in f and 
                f.rsplit('.', 1)[1].lower() in image_extensions
            ]
            
            if not image_files:
                return False, "No image files found in ZIP"
            
            if len(image_files) > 50:
                return False, "Too many images in ZIP file (max 50)"
        
        return True, "ZIP file is valid"
        
    except zipfile.BadZipFile:
        return False, "Invalid ZIP file format"
    except Exception as e:
        return False, f"Error validating ZIP file: {str(e)}"


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