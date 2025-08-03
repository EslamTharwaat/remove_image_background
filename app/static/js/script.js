// Global variables
let currentProcessedImageUrl = '';
let currentOriginalImageUrl = '';
let currentBatchId = null;
let batchStatusInterval = null;
let isSingleMode = false;

// Default settings (fallback if no settings are saved)
const DEFAULT_SETTINGS = {
    ai_model: 'u2net',
    alpha_matting: false,
    foreground_threshold: 240,
    background_threshold: 10,
    erode_size: 10,
    base_size: 1000
};

// DOM elements (will be initialized when DOM is loaded)
let uploadArea, fileInput, uploadSection, processingSection, batchProcessingSection, resultsSection, batchResultsSection, errorSection, originalImage, processedImage, errorMessage;

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    initializeElements();
    setupEventListeners();
});

function initializeElements() {
    // Initialize DOM elements
    uploadArea = document.getElementById('uploadArea');
    fileInput = document.getElementById('fileInput');
    uploadSection = document.getElementById('uploadSection');
    processingSection = document.getElementById('processingSection');
    batchProcessingSection = document.getElementById('batchProcessingSection');
    resultsSection = document.getElementById('resultsSection');
    batchResultsSection = document.getElementById('batchResultsSection');
    errorSection = document.getElementById('errorSection');
    originalImage = document.getElementById('originalImage');
    processedImage = document.getElementById('processedImage');
    errorMessage = document.getElementById('errorMessage');
    
    // Check if all elements are found
    if (!uploadArea || !fileInput || !uploadSection || !processingSection || !batchProcessingSection || !resultsSection || !batchResultsSection || !errorSection || !originalImage || !processedImage || !errorMessage) {
        console.error('Some DOM elements could not be found. Please check the HTML structure.');
        return false;
    }
    return true;
}

function setupEventListeners() {
    // Check if elements are initialized
    if (!initializeElements()) {
        return;
    }
    
    // File input change
    fileInput.addEventListener('change', handleFileSelect);
    
    // Drag and drop events
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    
    // Click to upload
    uploadArea.addEventListener('click', () => fileInput.click());
    
    // Setup quality settings
    setupQualitySettings();
}

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        processFile(file);
    }
}

function handleDragOver(event) {
    event.preventDefault();
    if (uploadArea) {
        uploadArea.classList.add('dragover');
    }
}

function handleDragLeave(event) {
    event.preventDefault();
    if (uploadArea) {
        uploadArea.classList.remove('dragover');
    }
}

function handleDrop(event) {
    event.preventDefault();
    if (uploadArea) {
        uploadArea.classList.remove('dragover');
    }
    
    const files = event.dataTransfer.files;
    if (files.length > 0) {
        const file = files[0];
        if (file.type.startsWith('image/')) {
            processFile(file);
        } else {
            showError('Please select a valid image file.');
        }
    }
}

function processFile(file) {
    // Check if we're in single mode or batch mode
    if (isSingleMode) {
        processSingleFile(file);
    } else {
        // For batch mode, we'll handle multiple files
        if (fileInput.files.length === 1) {
            processSingleFile(file);
        } else {
            processBatchFiles();
        }
    }
}

function processSingleFile(file) {
    // Check if it's a ZIP file - if so, treat as batch processing
    const isZipFile = file.name.toLowerCase().endsWith('.zip');
    if (isZipFile) {
        // For ZIP files, use batch processing
        processBatchFiles();
        return;
    }
    
    // Validate file type for single images
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/bmp', 'image/tiff'];
    if (!allowedTypes.includes(file.type)) {
        showError('Please select a valid image file (JPG, PNG, GIF, BMP, TIFF) or ZIP file.');
        return;
    }
    
    // Validate file size (16MB max)
    if (file.size > 16 * 1024 * 1024) {
        showError('File size must be less than 16MB.');
        return;
    }
    
    // Show processing section
    showProcessing();
    
    // Create FormData and send to server
    const formData = new FormData();
    formData.append('file', file);
    
    // Add CSRF token
    formData.append('csrf_token', csrfToken);
    
    // Add quality settings
    const qualitySettings = getQualitySettings();
    formData.append('alpha_matting', qualitySettings.alpha_matting);
    formData.append('foreground_threshold', qualitySettings.foreground_threshold);
    formData.append('background_threshold', qualitySettings.background_threshold);
    formData.append('erode_size', qualitySettings.erode_size);
    formData.append('base_size', qualitySettings.base_size);
    formData.append('ai_model', qualitySettings.ai_model);
    
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showResults(data.original_image, data.processed_image);
            currentProcessedImageUrl = data.processed_image;
            currentOriginalImageUrl = data.original_image;
        } else {
            showError(data.error || 'An error occurred while processing the image.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showError('Network error. Please check your connection and try again.');
    });
}

function processBatchFiles() {
    const files = Array.from(fileInput.files);
    
    if (files.length === 0) {
        showError('No files selected.');
        return;
    }
    
    // Validate all files
    for (let file of files) {
        const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/bmp', 'image/tiff'];
        const allowedExtensions = ['.zip'];
        
        // Check if it's a ZIP file
        const isZipFile = file.name.toLowerCase().endsWith('.zip');
        
        if (!allowedTypes.includes(file.type) && !isZipFile) {
            showError(`Invalid file type: ${file.name}. Please select valid image files or ZIP files.`);
            return;
        }
        
        // Different size limits for ZIP files vs images
        const maxSize = isZipFile ? 50 * 1024 * 1024 : 16 * 1024 * 1024; // 50MB for ZIP, 16MB for images
        const maxSizeText = isZipFile ? '50MB' : '16MB';
        
        if (file.size > maxSize) {
            showError(`File too large: ${file.name}. Maximum size is ${maxSizeText}.`);
            return;
        }
    }
    
    // Show batch processing section
    showBatchProcessing();
    
    // Create FormData for batch upload
    const formData = new FormData();
    files.forEach(file => {
        formData.append('files[]', file);
    });
    
    // Add CSRF token
    formData.append('csrf_token', csrfToken);
    
    // Add quality settings
    const qualitySettings = getQualitySettings();
    formData.append('alpha_matting', qualitySettings.alpha_matting);
    formData.append('foreground_threshold', qualitySettings.foreground_threshold);
    formData.append('background_threshold', qualitySettings.background_threshold);
    formData.append('erode_size', qualitySettings.erode_size);
    formData.append('base_size', qualitySettings.base_size);
    formData.append('ai_model', qualitySettings.ai_model);
    
    fetch('/batch-upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            currentBatchId = data.batch_id;
            startBatchStatusPolling();
        } else {
            showError(data.error || 'An error occurred while starting batch processing.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showError('Network error. Please check your connection and try again.');
    });
}

function startBatchStatusPolling() {
    if (batchStatusInterval) {
        clearInterval(batchStatusInterval);
    }
    
    batchStatusInterval = setInterval(() => {
        fetch(`/batch-status/${currentBatchId}`)
        .then(response => response.json())
        .then(data => {
            updateBatchProgress(data);
            
            if (data.status === 'completed') {
                clearInterval(batchStatusInterval);
                showBatchResults(data);
            }
        })
        .catch(error => {
            console.error('Error polling batch status:', error);
        });
    }, 1000); // Poll every second
}

function updateBatchProgress(data) {
    const progressFill = document.getElementById('batchProgressFill');
    const progressText = document.getElementById('batchProgressText');
    const totalFiles = document.getElementById('batchTotalFiles');
    const processedFiles = document.getElementById('batchProcessedFiles');
    const errors = document.getElementById('batchErrors');
    const status = document.getElementById('batchStatus');
    const individualProgress = document.getElementById('individualProgress');
    
    if (progressFill) progressFill.style.width = `${data.progress}%`;
    if (progressText) progressText.textContent = `${Math.round(data.progress)}%`;
    if (totalFiles) totalFiles.textContent = data.total_files;
    if (processedFiles) processedFiles.textContent = data.processed_files;
    if (errors) errors.textContent = data.errors.length;
    
    if (status) {
        if (data.status === 'processing') {
            status.innerHTML = `<p>Processing ${data.processed_files}/${data.total_files} images...</p>`;
        } else if (data.status === 'completed') {
            status.innerHTML = `<p>✅ Batch processing completed!</p>`;
        }
    }
    
    // Update individual progress
    if (individualProgress && data.individual_progress) {
        updateIndividualProgress(individualProgress, data.individual_progress);
    }
}

function updateIndividualProgress(container, individualProgress) {
    // Clear existing items
    container.innerHTML = '';
    
    // Create progress items for each file
    Object.entries(individualProgress).forEach(([filename, progress]) => {
        const progressItem = document.createElement('div');
        progressItem.className = 'individual-progress-item';
        
        let status = 'processing';
        let statusText = 'Processing';
        
        if (progress === 100) {
            status = 'completed';
            statusText = 'Completed';
        } else if (progress === 0) {
            status = 'error';
            statusText = 'Error';
        }
        
        progressItem.innerHTML = `
            <div class="individual-progress-filename">${filename}</div>
            <div class="individual-progress-bar">
                <div class="individual-progress-fill" style="width: ${progress}%"></div>
            </div>
            <div class="individual-progress-percentage">${progress}%</div>
            <div class="individual-progress-status ${status}">${statusText}</div>
        `;
        
        container.appendChild(progressItem);
    });
}

function showBatchResults(data) {
    // Update summary stats
    document.getElementById('batchSuccessCount').textContent = data.results.length;
    document.getElementById('batchErrorCount').textContent = data.errors.length;
    document.getElementById('batchTotalTime').textContent = Math.round(data.total_time);
    
    // Populate batch images
    const batchImages = document.getElementById('batchImages');
    batchImages.innerHTML = '';
    
    data.results.forEach(result => {
        const imageItem = document.createElement('div');
        imageItem.className = 'batch-image-item';
        imageItem.innerHTML = `
            <div class="batch-image-header">
                <span class="batch-image-name">${result.filename}</span>
                <span class="batch-image-time">${result.processing_time}s</span>
            </div>
            <div class="batch-image-comparison">
                <div class="batch-image-original">
                    <img src="${result.original_image}" alt="Original">
                </div>
                <div class="batch-image-arrow">
                    <i class="fas fa-arrow-right"></i>
                </div>
                <div class="batch-image-processed">
                    <img src="${result.processed_image}" alt="Processed">
                </div>
            </div>
            <div class="batch-image-download">
                <button class="btn btn-success" onclick="downloadBatchImage('${result.processed_image}', '${result.filename}')">
                    <i class="fas fa-download"></i>
                    Download
                </button>
            </div>
        `;
        batchImages.appendChild(imageItem);
    });
    
    // Show batch results section
    showBatchResultsSection();
}

function downloadBatchImage(imageUrl, filename) {
    const link = document.createElement('a');
    link.href = imageUrl;
    link.download = `no_bg_${filename}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function toggleUploadMode() {
    isSingleMode = !isSingleMode;
    const button = document.querySelector('.btn-secondary');
    
    if (isSingleMode) {
        button.innerHTML = '<i class="fas fa-images"></i> Batch Mode';
        fileInput.removeAttribute('multiple');
        uploadArea.querySelector('h3').textContent = 'Drop your image here';
        uploadArea.querySelector('p').textContent = 'or click to browse';
    } else {
        button.innerHTML = '<i class="fas fa-single-image"></i> Single Image Mode';
        fileInput.setAttribute('multiple', '');
        uploadArea.querySelector('h3').textContent = 'Drop your images here';
        uploadArea.querySelector('p').textContent = 'or click to browse (supports multiple files)';
    }
}

function getQualitySettings() {
    // Load settings from localStorage
    const savedSettings = localStorage.getItem('backgroundRemoverSettings');
    
    if (savedSettings) {
        const settings = JSON.parse(savedSettings);
        return {
            alpha_matting: settings.alpha_matting || DEFAULT_SETTINGS.alpha_matting,
            foreground_threshold: settings.foreground_threshold || DEFAULT_SETTINGS.foreground_threshold,
            background_threshold: settings.background_threshold || DEFAULT_SETTINGS.background_threshold,
            erode_size: settings.erode_size || DEFAULT_SETTINGS.erode_size,
            base_size: settings.base_size || DEFAULT_SETTINGS.base_size,
            ai_model: settings.ai_model || DEFAULT_SETTINGS.ai_model
        };
    }
    
    // Return default settings if none saved
    return {
        alpha_matting: DEFAULT_SETTINGS.alpha_matting,
        foreground_threshold: DEFAULT_SETTINGS.foreground_threshold,
        background_threshold: DEFAULT_SETTINGS.background_threshold,
        erode_size: DEFAULT_SETTINGS.erode_size,
        base_size: DEFAULT_SETTINGS.base_size,
        ai_model: DEFAULT_SETTINGS.ai_model
    };
}

function setupQualitySettings() {
    // This function is kept for compatibility but no longer needed
    // Settings are now handled in the dedicated settings page
}

function showReprocessModal() {
    if (!currentOriginalImageUrl) {
        showError('No image available for reprocessing.');
        return;
    }
    
    // Set the preview image
    document.getElementById('reprocessPreview').src = currentOriginalImageUrl;
    
    // Copy current settings to reprocess modal
    copyCurrentSettingsToReprocess();
    
    // Show the modal
    document.getElementById('reprocessModal').style.display = 'flex';
}

function hideReprocessModal() {
    document.getElementById('reprocessModal').style.display = 'none';
}

function copyCurrentSettingsToReprocess() {
    // Get current settings from localStorage
    const currentSettings = getQualitySettings();
    
    // Copy AI model
    document.getElementById('reprocessAiModel').value = currentSettings.ai_model;
    
    // Copy quality settings
    document.getElementById('reprocessAlphaMatting').checked = currentSettings.alpha_matting;
    document.getElementById('reprocessForegroundThreshold').value = currentSettings.foreground_threshold;
    document.getElementById('reprocessBackgroundThreshold').value = currentSettings.background_threshold;
    document.getElementById('reprocessErodeSize').value = currentSettings.erode_size;
    document.getElementById('reprocessBaseSize').value = currentSettings.base_size;
    
    // Update reprocess slider values
    updateReprocessSliderValues();
}

function updateReprocessSliderValues() {
    document.getElementById('reprocessForegroundThresholdValue').textContent = document.getElementById('reprocessForegroundThreshold').value;
    document.getElementById('reprocessBackgroundThresholdValue').textContent = document.getElementById('reprocessBackgroundThreshold').value;
    document.getElementById('reprocessErodeSizeValue').textContent = document.getElementById('reprocessErodeSize').value;
    document.getElementById('reprocessBaseSizeValue').textContent = document.getElementById('reprocessBaseSize').value;
}

function setReprocessQualityPreset(preset) {
    const settings = QUALITY_PRESETS[preset];
    if (!settings) return;
    
    document.getElementById('reprocessAlphaMatting').checked = settings.alpha_matting;
    document.getElementById('reprocessForegroundThreshold').value = settings.foreground_threshold;
    document.getElementById('reprocessBackgroundThreshold').value = settings.background_threshold;
    document.getElementById('reprocessErodeSize').value = settings.erode_size;
    document.getElementById('reprocessBaseSize').value = settings.base_size;
    
    // Update display values
    updateReprocessSliderValues();
    
    // Show feedback
    showSuccessNotification(`Quality preset "${preset}" applied`);
}

function reprocessImage() {
    if (!currentOriginalImageUrl) {
        showError('No image available for reprocessing.');
        return;
    }
    
    // Show processing section
    showProcessing();
    hideReprocessModal();
    
    // Get reprocess settings
    const qualitySettings = {
        alpha_matting: document.getElementById('reprocessAlphaMatting').checked,
        foreground_threshold: parseInt(document.getElementById('reprocessForegroundThreshold').value),
        background_threshold: parseInt(document.getElementById('reprocessBackgroundThreshold').value),
        erode_size: parseInt(document.getElementById('reprocessErodeSize').value),
        base_size: parseInt(document.getElementById('reprocessBaseSize').value),
        ai_model: document.getElementById('reprocessAiModel').value
    };
    
    // Create FormData for reprocessing
    const formData = new FormData();
    formData.append('image_path', currentOriginalImageUrl);
    formData.append('csrf_token', csrfToken);
    formData.append('alpha_matting', qualitySettings.alpha_matting);
    formData.append('foreground_threshold', qualitySettings.foreground_threshold);
    formData.append('background_threshold', qualitySettings.background_threshold);
    formData.append('erode_size', qualitySettings.erode_size);
    formData.append('base_size', qualitySettings.base_size);
    formData.append('ai_model', qualitySettings.ai_model);
    
    fetch('/reprocess', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showResults(data.original_image, data.processed_image);
            currentProcessedImageUrl = data.processed_image;
            showSuccessNotification(`Image reprocessed successfully with ${data.ai_model} model!`);
        } else {
            showError(data.error || 'An error occurred while reprocessing the image.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showError('Network error. Please check your connection and try again.');
    });
}

function showProcessing() {
    if (!uploadSection || !processingSection || !batchProcessingSection || !resultsSection || !batchResultsSection || !errorSection) {
        console.error('DOM elements not initialized');
        return;
    }
    uploadSection.style.display = 'none';
    processingSection.style.display = 'block';
    batchProcessingSection.style.display = 'none';
    resultsSection.style.display = 'none';
    batchResultsSection.style.display = 'none';
    errorSection.style.display = 'none';
}

function showResults(originalImageUrl, processedImageUrl) {
    if (!uploadSection || !processingSection || !batchProcessingSection || !resultsSection || !batchResultsSection || !errorSection || !originalImage || !processedImage) {
        console.error('DOM elements not initialized');
        return;
    }
    
    // Set image sources
    originalImage.src = originalImageUrl;
    processedImage.src = processedImageUrl;
    
    // Show results section
    uploadSection.style.display = 'none';
    processingSection.style.display = 'none';
    batchProcessingSection.style.display = 'none';
    batchResultsSection.style.display = 'none';
    resultsSection.style.display = 'block';
    errorSection.style.display = 'none';
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function showBatchProcessing() {
    if (!uploadSection || !processingSection || !batchProcessingSection || !resultsSection || !batchResultsSection || !errorSection) {
        console.error('DOM elements not initialized');
        return;
    }
    
    // Show batch processing section
    uploadSection.style.display = 'none';
    processingSection.style.display = 'none';
    resultsSection.style.display = 'none';
    batchResultsSection.style.display = 'none';
    errorSection.style.display = 'none';
    batchProcessingSection.style.display = 'block';
    
    // Scroll to batch processing
    batchProcessingSection.scrollIntoView({ behavior: 'smooth' });
}

function showBatchResultsSection() {
    if (!uploadSection || !processingSection || !batchProcessingSection || !resultsSection || !batchResultsSection || !errorSection) {
        console.error('DOM elements not initialized');
        return;
    }
    
    // Show batch results section
    uploadSection.style.display = 'none';
    processingSection.style.display = 'none';
    batchProcessingSection.style.display = 'none';
    resultsSection.style.display = 'none';
    errorSection.style.display = 'none';
    batchResultsSection.style.display = 'block';
    
    // Scroll to batch results
    batchResultsSection.scrollIntoView({ behavior: 'smooth' });
}

function showError(message) {
    if (!uploadSection || !processingSection || !batchProcessingSection || !resultsSection || !batchResultsSection || !errorSection || !errorMessage) {
        console.error('DOM elements not initialized');
        return;
    }
    
    errorMessage.textContent = message;
    
    uploadSection.style.display = 'none';
    processingSection.style.display = 'none';
    batchProcessingSection.style.display = 'none';
    resultsSection.style.display = 'none';
    batchResultsSection.style.display = 'none';
    errorSection.style.display = 'block';
}

function resetApp() {
    if (!uploadSection || !processingSection || !batchProcessingSection || !resultsSection || !batchResultsSection || !errorSection || !fileInput) {
        console.error('DOM elements not initialized');
        return;
    }
    
    // Reset file input
    fileInput.value = '';
    
    // Reset current processed image URL and batch ID
    currentProcessedImageUrl = '';
    currentOriginalImageUrl = '';
    currentBatchId = null;
    
    // Clear batch status interval
    if (batchStatusInterval) {
        clearInterval(batchStatusInterval);
        batchStatusInterval = null;
    }
    
    // Reset to batch mode
    isSingleMode = false;
    if (fileInput) fileInput.setAttribute('multiple', '');
    
    // Show upload section
    uploadSection.style.display = 'block';
    processingSection.style.display = 'none';
    batchProcessingSection.style.display = 'none';
    resultsSection.style.display = 'none';
    batchResultsSection.style.display = 'none';
    errorSection.style.display = 'none';
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function downloadImage() {
    if (!currentProcessedImageUrl) {
        showError('No processed image available for download.');
        return;
    }
    
    // Create a temporary link element
    const link = document.createElement('a');
    link.href = currentProcessedImageUrl;
    link.download = 'background_removed_image.png';
    
    // Append to body, click, and remove
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Add some visual feedback for better UX
function addLoadingState(element) {
    element.style.opacity = '0.7';
    element.style.pointerEvents = 'none';
}

function removeLoadingState(element) {
    element.style.opacity = '1';
    element.style.pointerEvents = 'auto';
}

// Add success notification
function showSuccessNotification(message) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = 'notification success';
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #28a745;
        color: white;
        padding: 15px 20px;
        border-radius: 10px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        z-index: 1000;
        transform: translateX(100%);
        transition: transform 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Add error notification
function showErrorNotification(message) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = 'notification error';
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #dc3545;
        color: white;
        padding: 15px 20px;
        border-radius: 10px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        z-index: 1000;
        transform: translateX(100%);
        transition: transform 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Remove after 5 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 5000);
} 