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
    base_size: 1000
};

// Initialize settings page
document.addEventListener('DOMContentLoaded', function() {
    initializeSettings();
    setupEventListeners();
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
        base_size: parseInt(document.getElementById('baseSize').value)
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
    
    updateSliderValues();
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

// Listen for messages from main page
window.addEventListener('message', function(event) {
    if (event.data.type === 'LOAD_SETTINGS') {
        loadSettings();
    }
}); 