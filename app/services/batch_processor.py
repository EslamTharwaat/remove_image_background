"""
Batch processing service for handling multiple images
"""
import os
import time
import threading
import concurrent.futures
from app.services.background_remover import BackgroundRemoverService
from app.utils.file_utils import generate_secure_filename, safe_join


class BatchProcessor:
    """Service for processing multiple images in parallel"""
    
    def __init__(self, config, background_remover_service):
        self.config = config
        self.background_remover = background_remover_service
        self.batch_jobs = {}
        self.batch_counter = 0
        self.batch_lock = threading.Lock()
    
    def generate_batch_id(self):
        """Generate unique batch ID"""
        with self.batch_lock:
            self.batch_counter += 1
            return f"batch_{self.batch_counter}_{int(time.time())}"
    
    def create_batch_job(self, batch_id, total_files):
        """Create a new batch job"""
        self.batch_jobs[batch_id] = {
            'total_files': total_files,
            'processed_files': 0,
            'results': [],
            'errors': [],
            'status': 'processing',
            'start_time': time.time(),
            'progress': 0,
            'individual_progress': {}
        }
    
    def update_batch_progress(self, batch_id, filename, status, result=None, error=None, individual_progress=None):
        """Update batch processing progress"""
        if batch_id not in self.batch_jobs:
            return
        
        job = self.batch_jobs[batch_id]
        
        # Update individual progress
        if individual_progress is not None:
            job['individual_progress'][filename] = individual_progress
        
        if status in ['completed', 'error']:
            job['processed_files'] += 1
            job['progress'] = (job['processed_files'] / job['total_files']) * 100
        
        if result:
            job['results'].append({
                'filename': filename,
                'original_image': result['original_image'],
                'processed_image': result['processed_image'],
                'processing_time': result['processing_time'],
                'ai_model': result.get('ai_model', self.config.DEFAULT_MODEL)
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
    
    def process_single_image(self, file_data, batch_id, original_filename, quality_settings, ai_model=None):
        """Process a single image in batch mode"""
        try:
            # Update progress - starting
            self.update_batch_progress(batch_id, original_filename, 'processing', individual_progress=10)
            
            # Generate secure filename
            secure_filename_gen = generate_secure_filename(original_filename)
            filepath = safe_join(self.config.UPLOAD_FOLDER, secure_filename_gen)
            
            if filepath is None:
                raise Exception("Invalid file path")
            
            # Update progress - file saved
            self.update_batch_progress(batch_id, original_filename, 'processing', individual_progress=20)
            
            # Save the uploaded file
            with open(filepath, 'wb') as f:
                f.write(file_data)
            
            # Update progress - optimizing image
            self.update_batch_progress(batch_id, original_filename, 'processing', individual_progress=30)
            
            # Remove background
            output_filename = f"no_bg_{secure_filename_gen}"
            output_path = safe_join(self.config.OUTPUT_FOLDER, output_filename)
            
            if output_path is None:
                raise Exception("Invalid output path")
            
            # Update progress - AI processing starting
            self.update_batch_progress(batch_id, original_filename, 'processing', individual_progress=50)
            
            # Process image
            result = self.background_remover.process_image(
                filepath, 
                output_path, 
                quality_settings, 
                ai_model
            )
            
            # Update progress - AI processing complete
            self.update_batch_progress(batch_id, original_filename, 'processing', individual_progress=80)
            
            # Update progress - saving result
            self.update_batch_progress(batch_id, original_filename, 'processing', individual_progress=90)
            
            # Add URL paths to result
            result['original_image'] = f'/uploads/{secure_filename_gen}'
            result['processed_image'] = f'/outputs/{output_filename}'
            
            # Update batch progress - completed
            self.update_batch_progress(batch_id, original_filename, 'completed', result=result, individual_progress=100)
            
            return result
            
        except Exception as e:
            # Update batch progress with error
            self.update_batch_progress(batch_id, original_filename, 'error', error=str(e), individual_progress=0)
            
            # Clean up uploaded file if processing fails
            if 'filepath' in locals() and os.path.exists(filepath):
                os.remove(filepath)
            
            raise e
    
    def process_batch(self, files, quality_settings, ai_model=None):
        """Process multiple files in parallel"""
        if ai_model is None:
            ai_model = self.config.DEFAULT_MODEL
        
        # Generate batch ID
        batch_id = self.generate_batch_id()
        self.create_batch_job(batch_id, len(files))
        
        # Process files in parallel
        def process_files_parallel():
            max_workers = min(len(files), self.config.MAX_BATCH_WORKERS)
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = []
                for file in files:
                    # Handle both regular FileStorage objects and our MockFile objects
                    if hasattr(file, '_data'):
                        # MockFile object - data is already loaded
                        file_data = file._data
                    else:
                        # Regular FileStorage object - read the data
                        file_data = file.read()
                    
                    future = executor.submit(
                        self.process_single_image, 
                        file_data, 
                        batch_id, 
                        file.filename, 
                        quality_settings, 
                        ai_model
                    )
                    futures.append(future)
                
                # Wait for all futures to complete
                concurrent.futures.wait(futures)
        
        # Start processing in background thread
        processing_thread = threading.Thread(target=process_files_parallel)
        processing_thread.daemon = True
        processing_thread.start()
        
        return batch_id
    
    def get_batch_status(self, batch_id):
        """Get batch processing status"""
        if batch_id not in self.batch_jobs:
            return None
        
        job = self.batch_jobs[batch_id]
        return {
            'batch_id': batch_id,
            'status': job['status'],
            'progress': job['progress'],
            'total_files': job['total_files'],
            'processed_files': job['processed_files'],
            'results': job['results'],
            'errors': job['errors'],
            'total_time': job.get('total_time', 0),
            'individual_progress': job.get('individual_progress', {})
        }
    
    def cleanup_old_batches(self, max_age=3600):
        """Clean up old batch jobs"""
        current_time = time.time()
        jobs_to_remove = []
        
        for batch_id, job in self.batch_jobs.items():
            if current_time - job['start_time'] > max_age:
                jobs_to_remove.append(batch_id)
        
        for batch_id in jobs_to_remove:
            del self.batch_jobs[batch_id] 