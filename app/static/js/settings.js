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
    
    // Update slider values display
    updateSliderValues();
}

function setupEventListeners() {
    // Add event listeners for sliders
    const sliders = ['foregroundThreshold', 'backgroundThreshold', 'erodeSize', 'baseSize'];
    sliders.forEach(id => {
        const slider = document.getElementById(id);
        if (slider) {
            slider.addEventListener('input', updateSliderValues);
        }
    });
}

function updateSliderValues() {
    // Update all slider value displays
    document.getElementById('foregroundThresholdValue').textContent = document.getElementById('foregroundThreshold').value;
    document.getElementById('backgroundThresholdValue').textContent = document.getElementById('backgroundThreshold').value;
    document.getElementById('erodeSizeValue').textContent = document.getElementById('erodeSize').value;
    document.getElementById('baseSizeValue').textContent = document.getElementById('baseSize').value;
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
        ai_model: document.getElementById('aiModel').value,
        alpha_matting: document.getElementById('alphaMatting').checked,
        foreground_threshold: parseInt(document.getElementById('foregroundThreshold').value),
        background_threshold: parseInt(document.getElementById('backgroundThreshold').value),
        erode_size: parseInt(document.getElementById('erodeSize').value),
        base_size: parseInt(document.getElementById('baseSize').value),
        // S3 settings
        enable_s3_upload: document.getElementById('enableS3Upload').checked,
        s3_bucket_name: document.getElementById('s3BucketName').value,
        s3_access_key_id: document.getElementById('s3AccessKeyId').value,
        s3_secret_access_key: document.getElementById('s3SecretAccessKey').value,
        s3_region_name: document.getElementById('s3RegionName').value,
        s3_folder_prefix: document.getElementById('s3FolderPrefix').value
    };
}

function saveSettings() {
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
        
        // Apply saved settings
        document.getElementById('aiModel').value = settings.ai_model || DEFAULT_SETTINGS.ai_model;
        document.getElementById('alphaMatting').checked = settings.alpha_matting || DEFAULT_SETTINGS.alpha_matting;
        document.getElementById('foregroundThreshold').value = settings.foreground_threshold || DEFAULT_SETTINGS.foreground_threshold;
        document.getElementById('backgroundThreshold').value = settings.background_threshold || DEFAULT_SETTINGS.background_threshold;
        document.getElementById('erodeSize').value = settings.erode_size || DEFAULT_SETTINGS.erode_size;
        document.getElementById('baseSize').value = settings.base_size || DEFAULT_SETTINGS.base_size;
        
        // Load S3 settings
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
    document.getElementById('aiModel').value = DEFAULT_SETTINGS.ai_model;
    document.getElementById('alphaMatting').checked = DEFAULT_SETTINGS.alpha_matting;
    document.getElementById('foregroundThreshold').value = DEFAULT_SETTINGS.foreground_threshold;
    document.getElementById('backgroundThreshold').value = DEFAULT_SETTINGS.background_threshold;
    document.getElementById('erodeSize').value = DEFAULT_SETTINGS.erode_size;
    document.getElementById('baseSize').value = DEFAULT_SETTINGS.base_size;
    
    // Apply default S3 settings
    document.getElementById('enableS3Upload').checked = DEFAULT_SETTINGS.enable_s3_upload;
    document.getElementById('s3BucketName').value = DEFAULT_SETTINGS.s3_bucket_name;
    document.getElementById('s3AccessKeyId').value = DEFAULT_SETTINGS.s3_access_key_id;
    document.getElementById('s3SecretAccessKey').value = DEFAULT_SETTINGS.s3_secret_access_key;
    document.getElementById('s3RegionName').value = DEFAULT_SETTINGS.s3_region_name;
    document.getElementById('s3FolderPrefix').value = DEFAULT_SETTINGS.s3_folder_prefix;
    
    updateSliderValues();
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
    
    // Toggle S3 credentials visibility
    enableS3Checkbox.addEventListener('change', function() {
        updateS3UI();
    });
    
    // Test S3 connection when credentials change
    const s3Inputs = ['s3BucketName', 's3AccessKeyId', 's3SecretAccessKey', 's3RegionName'];
    s3Inputs.forEach(inputId => {
        const input = document.getElementById(inputId);
        if (input) {
            input.addEventListener('blur', function() {
                if (enableS3Checkbox.checked) {
                    testS3Connection();
                }
            });
        }
    });
}

function updateS3UI() {
    const enableS3Checkbox = document.getElementById('enableS3Upload');
    const s3Credentials = document.getElementById('s3Credentials');
    const s3Status = document.getElementById('s3Status');
    
    if (enableS3Checkbox.checked) {
        s3Credentials.classList.remove('hidden');
        testS3Connection();
    } else {
        s3Credentials.classList.add('hidden');
        updateS3Status('disabled', 'S3 upload disabled');
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