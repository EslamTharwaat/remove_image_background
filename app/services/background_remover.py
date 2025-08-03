"""
Background removal service using AI models
"""
import os
import time
import threading
from backgroundremover import bg
from app.utils.file_utils import optimize_image_size
from werkzeug.security import safe_join


class BackgroundRemoverService:
    """Service for removing backgrounds from images using AI models"""
    
    def __init__(self, config):
        self.config = config
        self.model_cache = {}
        self.model_lock = threading.Lock()
    
    def get_model(self, model_name):
        """Get or create a cached model instance"""
        if model_name not in self.model_cache:
            with self.model_lock:
                if model_name not in self.model_cache:
                    self.model_cache[model_name] = bg.get_model(model_name)
        return self.model_cache[model_name]
    
    def process_image(self, input_path, output_path, quality_settings, ai_model=None):
        """
        Process a single image to remove background
        
        Args:
            input_path: Path to input image
            output_path: Path to save processed image
            quality_settings: Dictionary of quality settings
            ai_model: AI model to use (default from config)
        
        Returns:
            dict: Processing result with timing and metadata
        """
        if ai_model is None:
            ai_model = self.config.DEFAULT_MODEL
        
        if ai_model not in self.config.AVAILABLE_MODELS:
            raise ValueError(f"Invalid AI model: {ai_model}")
        
        start_time = time.time()
        
        try:
            # Optimize image size for faster processing
            if self.config.ENABLE_IMAGE_OPTIMIZATION:
                optimized_path = optimize_image_size(input_path, self.config.MAX_IMAGE_SIZE)
            else:
                optimized_path = input_path
            
            # Read input data
            with open(optimized_path, 'rb') as input_file:
                input_data = input_file.read()
            
            # Remove background using AI model
            output_data = bg.remove(
                input_data,
                model_name=ai_model,
                alpha_matting=quality_settings.get('alpha_matting', self.config.DEFAULT_ALPHA_MATTING),
                alpha_matting_foreground_threshold=quality_settings.get('foreground_threshold', self.config.DEFAULT_ALPHA_MATTING_FOREGROUND_THRESHOLD),
                alpha_matting_background_threshold=quality_settings.get('background_threshold', self.config.DEFAULT_ALPHA_MATTING_BACKGROUND_THRESHOLD),
                alpha_matting_erode_structure_size=quality_settings.get('erode_size', self.config.DEFAULT_ALPHA_MATTING_ERODE_SIZE),
                alpha_matting_base_size=quality_settings.get('base_size', self.config.DEFAULT_ALPHA_MATTING_BASE_SIZE)
            )
            
            # Save processed image
            with open(output_path, 'wb') as output_file:
                output_file.write(output_data)
            
            # Clean up optimized file if it was created
            if optimized_path != input_path and os.path.exists(optimized_path):
                os.remove(optimized_path)
            
            processing_time = time.time() - start_time
            
            return {
                'success': True,
                'processing_time': round(processing_time, 2),
                'ai_model': ai_model,
                'input_path': input_path,
                'output_path': output_path
            }
            
        except Exception as e:
            # Clean up optimized file if processing fails
            if 'optimized_path' in locals() and optimized_path != input_path and os.path.exists(optimized_path):
                os.remove(optimized_path)
            raise e
    
    def validate_quality_settings(self, quality_settings):
        """Validate quality settings"""
        required_fields = ['alpha_matting', 'foreground_threshold', 'background_threshold', 'erode_size', 'base_size']
        
        for field in required_fields:
            if field not in quality_settings:
                raise ValueError(f"Missing required quality setting: {field}")
        
        # Validate ranges
        if not 0 <= quality_settings['foreground_threshold'] <= 255:
            raise ValueError("Foreground threshold must be between 0 and 255")
        
        if not 0 <= quality_settings['background_threshold'] <= 255:
            raise ValueError("Background threshold must be between 0 and 255")
        
        if not 1 <= quality_settings['erode_size'] <= 20:
            raise ValueError("Erode size must be between 1 and 20")
        
        if not 500 <= quality_settings['base_size'] <= 2000:
            raise ValueError("Base size must be between 500 and 2000")
        
        return True 