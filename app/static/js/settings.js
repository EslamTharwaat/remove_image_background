/**
 * Settings Page JavaScript
 * Handles AI model and quality settings configuration
 */

// Quality presets configuration
const QUALITY_PRESETS = {
    'fast': {
        alpha_matting: false,
        foreground_threshold: 240,
        background_threshold: 10,
        erode_size: 10,
        base_size: 500
    },
    'balanced': {
        alpha_matting: false,
        foreground_threshold: 240,
        background_threshold: 10,
        erode_size: 10,
        base_size: 1000
    },
    'high': {
        alpha_matting: true,
        foreground_threshold: 240,
        background_threshold: 10,
        erode_size: 10,
        base_size: 1500
    }
};

// Default settings
const DEFAULT_SETTINGS = {
    ai_model: 'u2net',
    alpha_matting: false,
    foreground_threshold: 240,
    background_threshold: 10,
    erode_size: 10,
    base_size: 1000,
    // S3 settings
    enable_s3_upload: false,
    s3_bucket_name: '',
    s3_access_key_id: '',
    s3_secret_access_key: '',
    s3_region_name: 'us-east-1',
    s3_folder_prefix: 'background-remover/'
};

// Initialize settings page
document.addEventListener('DOMContentLoaded', function() {
    initializeSettings();
    setupEventListeners();
    setupS3EventListeners();
});

function initializeSettings() {
    // Load saved settings from localStorage
    loadSettings();
    
    // Initialize S3 UI state
    updateS3UI();
}

function setupEventListeners() {
    // No general event listeners needed for simplified settings page
    // All S3-specific listeners are handled in setupS3EventListeners()
}

// updateSliderValues function removed - no longer needed for simplified settings page

function validateS3Settings() {
    const enableS3Checkbox = document.getElementById('enableS3Upload');
    
    // If S3 upload is not enabled, no validation needed
    if (!enableS3Checkbox.checked) {
        return true;
    }
    
    // Required S3 fields when S3 upload is enabled
    const requiredFields = [
        { id: 's3BucketName', name: 'S3 Bucket Name' },
        { id: 's3AccessKeyId', name: 'Access Key ID' },
        { id: 's3SecretAccessKey', name: 'Secret Access Key' },
        { id: 's3RegionName', name: 'Region' }
    ];
    
    const emptyFields = [];
    
    // Check each required field
    requiredFields.forEach(field => {
        const element = document.getElementById(field.id);
        if (element && (!element.value || element.value.trim() === '')) {
            emptyFields.push(field.name);
            // Add visual indication of error
            element.style.borderColor = '#dc3545';
            element.style.boxShadow = '0 0 0 3px rgba(220, 53, 69, 0.1)';
        } else if (element) {
            // Remove error styling if field is now filled
            element.style.borderColor = '#e9ecef';
            element.style.boxShadow = '';
        }
    });
    
    // If there are empty fields, show error and prevent saving
    if (emptyFields.length > 0) {
        const message = `Please fill in all required S3 fields: ${emptyFields.join(', ')}`;
        showNotification(message, 'error');
        return false;
    }
    
    return true;
}

function setQualityPreset(preset) {
    const settings = QUALITY_PRESETS[preset];
    if (!settings) return;
    
    // Apply preset values
    document.getElementById('alphaMatting').checked = settings.alpha_matting;
    document.getElementById('foregroundThreshold').value = settings.foreground_threshold;
    document.getElementById('backgroundThreshold').value = settings.background_threshold;
    document.getElementById('erodeSize').value = settings.erode_size;
    document.getElementById('baseSize').value = settings.base_size;
    
    // Update display values
    updateSliderValues();
    
    // Show feedback
    showNotification(`Quality preset "${preset}" applied successfully!`, 'success');
}

function getCurrentSettings() {
    return {
        // S3 settings only (AI model settings removed as they don't exist in current template)
        enable_s3_upload: document.getElementById('enableS3Upload').checked,
        s3_bucket_name: document.getElementById('s3BucketName').value,
        s3_access_key_id: document.getElementById('s3AccessKeyId').value,
        s3_secret_access_key: document.getElementById('s3SecretAccessKey').value,
        s3_region_name: document.getElementById('s3RegionName').value,
        s3_folder_prefix: document.getElementById('s3FolderPrefix').value
    };
}

function saveSettings() {
    // Validate S3 settings if S3 upload is enabled
    if (!validateS3Settings()) {
        return; // Don't save if validation fails
    }
    
    const settings = getCurrentSettings();
    
    // Save to localStorage
    localStorage.setItem('backgroundRemoverSettings', JSON.stringify(settings));
    
    // Show success message
    showNotification('Settings saved successfully!', 'success');
    
    // Update main page settings if it exists
    updateMainPageSettings(settings);
}

function loadSettings() {
    const savedSettings = localStorage.getItem('backgroundRemoverSettings');
    
    if (savedSettings) {
        const settings = JSON.parse(savedSettings);
        
        // Load S3 settings only (AI model settings removed)
        document.getElementById('enableS3Upload').checked = settings.enable_s3_upload || DEFAULT_SETTINGS.enable_s3_upload;
        document.getElementById('s3BucketName').value = settings.s3_bucket_name || DEFAULT_SETTINGS.s3_bucket_name;
        document.getElementById('s3AccessKeyId').value = settings.s3_access_key_id || DEFAULT_SETTINGS.s3_access_key_id;
        document.getElementById('s3SecretAccessKey').value = settings.s3_secret_access_key || DEFAULT_SETTINGS.s3_secret_access_key;
        document.getElementById('s3RegionName').value = settings.s3_region_name || DEFAULT_SETTINGS.s3_region_name;
        document.getElementById('s3FolderPrefix').value = settings.s3_folder_prefix || DEFAULT_SETTINGS.s3_folder_prefix;
        
        // Update UI based on S3 settings
        updateS3UI();
    } else {
        // Apply default settings
        applyDefaultSettings();
    }
}

function resetSettings() {
    // Apply default settings
    applyDefaultSettings();
    
    // Clear localStorage
    localStorage.removeItem('backgroundRemoverSettings');
    
    // Show feedback
    showNotification('Settings reset to defaults!', 'info');
}

function applyDefaultSettings() {
    // Apply default S3 settings only (AI model settings removed)
    document.getElementById('enableS3Upload').checked = DEFAULT_SETTINGS.enable_s3_upload;
    document.getElementById('s3BucketName').value = DEFAULT_SETTINGS.s3_bucket_name;
    document.getElementById('s3AccessKeyId').value = DEFAULT_SETTINGS.s3_access_key_id;
    document.getElementById('s3SecretAccessKey').value = DEFAULT_SETTINGS.s3_secret_access_key;
    document.getElementById('s3RegionName').value = DEFAULT_SETTINGS.s3_region_name;
    document.getElementById('s3FolderPrefix').value = DEFAULT_SETTINGS.s3_folder_prefix;
    
    updateS3UI();
}

function updateMainPageSettings(settings) {
    // Try to update settings on the main page if it's open
    try {
        if (window.opener && !window.opener.closed) {
            // If settings page was opened from main page
            window.opener.postMessage({
                type: 'SETTINGS_UPDATED',
                settings: settings
            }, '*');
        }
    } catch (e) {
        // Ignore errors if main page is not available
    }
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        <span>${message}</span>
        <button onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 3000);
}

// S3 Settings Functions
function setupS3EventListeners() {
    const enableS3Checkbox = document.getElementById('enableS3Upload');
    const s3Credentials = document.getElementById('s3Credentials');
    
    // Check if S3 elements exist
    if (!enableS3Checkbox) {
        console.log('Enable S3 checkbox not found');
        return;
    }
    
    // Toggle S3 credentials visibility
    enableS3Checkbox.addEventListener('change', function() {
        console.log('S3 checkbox changed:', this.checked);
        updateS3UI();
    });
    
    // Test S3 connection and validate when credentials change
    const s3Inputs = ['s3BucketName', 's3AccessKeyId', 's3SecretAccessKey', 's3RegionName'];
    s3Inputs.forEach(inputId => {
        const input = document.getElementById(inputId);
        if (input) {
            // Validate on blur (when user leaves the field)
            input.addEventListener('blur', function() {
                if (enableS3Checkbox.checked) {
                    validateS3Settings(); // Real-time validation
                    testS3Connection();
                }
            });
            
            // Clear error styling on input (when user starts typing)
            input.addEventListener('input', function() {
                if (enableS3Checkbox.checked && this.value.trim() !== '') {
                    this.style.borderColor = '#e9ecef';
                    this.style.boxShadow = '';
                }
            });
        }
    });
}

function updateS3UI() {
    const enableS3Checkbox = document.getElementById('enableS3Upload');
    const s3Credentials = document.getElementById('s3Credentials');
    const s3Status = document.getElementById('s3Status');
    
    // Check if elements exist
    if (!enableS3Checkbox || !s3Credentials) {
        console.log('S3 elements not found');
        return;
    }
    
    if (enableS3Checkbox.checked) {
        s3Credentials.style.display = 'block';
        console.log('S3 credentials shown');
        if (s3Status) {
            testS3Connection();
        }
    } else {
        s3Credentials.style.display = 'none';
        console.log('S3 credentials hidden');
        if (s3Status) {
            updateS3Status('disabled', 'S3 upload disabled');
        }
    }
}

function updateS3Status(status, message) {
    const statusIndicator = document.querySelector('.status-indicator');
    const statusIcon = statusIndicator.querySelector('.status-icon');
    const statusText = statusIndicator.querySelector('.status-text');
    
    // Remove existing status classes
    statusIcon.classList.remove('connected', 'error', 'disabled');
    
    // Add new status class
    statusIcon.classList.add(status);
    statusText.textContent = message;
}

function testS3Connection() {
    const settings = getCurrentSettings();
    
    // Check if required fields are filled
    if (!settings.s3_bucket_name || !settings.s3_access_key_id || !settings.s3_secret_access_key) {
        updateS3Status('error', 'Please fill in all required S3 fields');
        return;
    }
    
    updateS3Status('disabled', 'Testing S3 connection...');
    
    // Send test request to backend
    fetch('/api/v1/test-s3', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateS3Status('connected', `Connected to S3 bucket: ${data.bucket_name}`);
        } else {
            updateS3Status('error', `S3 connection failed: ${data.error}`);
        }
    })
    .catch(error => {
        updateS3Status('error', 'Failed to test S3 connection');
        console.error('S3 test error:', error);
    });
}

// Listen for messages from main page
window.addEventListener('message', function(event) {
    if (event.data.type === 'LOAD_SETTINGS') {
        loadSettings();
    }
}); 