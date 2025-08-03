# 🔌 Background Remover API Documentation

## Overview

The Background Remover API provides programmatic access to AI-powered background removal functionality. The API supports both single image processing and batch processing via ZIP files.

**Base URL**: `http://localhost:5000/api/v1`

## Authentication

Currently, the API does not require authentication. All endpoints are publicly accessible.

## Endpoints

### 1. Health Check

**GET** `/health`

Check if the API service is running.

**Response:**
```json
{
  "status": "healthy",
  "service": "background-remover",
  "version": "1.0.0"
}
```

### 2. Process Single Image

**POST** `/process`

Process a single image to remove its background.

**Request Formats:**

#### Option 1: File Upload (multipart/form-data)
```
POST /api/v1/process
Content-Type: multipart/form-data

Form Data:
- image: [image file]
- ai_model: [optional] u2net|u2netp|u2net_human_seg|u2net_cloth_seg
- alpha_matting: [optional] true|false
- foreground_threshold: [optional] 0-255
- background_threshold: [optional] 0-255
- erode_size: [optional] 1-20
- base_size: [optional] 500-2000
```

#### Option 2: Base64 Image (application/x-www-form-urlencoded)
```
POST /api/v1/process
Content-Type: application/x-www-form-urlencoded

Form Data:
- image_data: [base64 encoded image]
- ai_model: [optional] u2net|u2netp|u2net_human_seg|u2net_cloth_seg
- alpha_matting: [optional] true|false
- foreground_threshold: [optional] 0-255
- background_threshold: [optional] 0-255
- erode_size: [optional] 1-20
- base_size: [optional] 500-2000
```

**Response:**
```json
{
  "success": true,
  "message": "Image processed successfully in 2.5 seconds",
  "processing_time": 2.5,
  "ai_model": "u2net",
  "original_filename": "example.jpg",
  "processed_image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "download_url": "/api/v1/download/no_bg_example.jpg"
}
```

### 3. Process ZIP File

**POST** `/process-zip`

Process multiple images from a ZIP file.

**Request:**
```
POST /api/v1/process-zip
Content-Type: multipart/form-data

Form Data:
- zip_file: [ZIP file containing images]
- ai_model: [optional] u2net|u2netp|u2net_human_seg|u2net_cloth_seg
- alpha_matting: [optional] true|false
- foreground_threshold: [optional] 0-255
- background_threshold: [optional] 0-255
- erode_size: [optional] 1-20
- base_size: [optional] 500-2000
```

**Response:**
```json
{
  "success": true,
  "message": "Processed 5 images from ZIP file",
  "total_images": 5,
  "successful": 4,
  "failed": 1,
  "results": [
    {
      "original_filename": "image1.jpg",
      "processed_filename": "no_bg_image1.jpg",
      "processing_time": 2.1,
      "ai_model": "u2net",
      "download_url": "/api/v1/download/no_bg_image1.jpg"
    }
  ],
  "errors": [
    {
      "filename": "image2.jpg",
      "error": "Invalid image format"
    }
  ],
  "quality_settings": {
    "alpha_matting": false,
    "foreground_threshold": 240,
    "background_threshold": 10,
    "erode_size": 10,
    "base_size": 1000
  },
  "ai_model": "u2net"
}
```

### 4. Download Processed Image

**GET** `/download/{filename}`

Download a processed image by filename.

**Request:**
```
GET /api/v1/download/no_bg_example.jpg
```

**Response:**
- File download (image/png)

### 5. Get Available Models

**GET** `/models`

Get list of available AI models.

**Response:**
```json
{
  "models": ["u2net", "u2netp", "u2net_human_seg", "u2net_cloth_seg"],
  "default_model": "u2net"
}
```

### 6. Get Default Settings

**GET** `/settings`

Get default quality settings and limits.

**Response:**
```json
{
  "default_alpha_matting": false,
  "default_foreground_threshold": 240,
  "default_background_threshold": 10,
  "default_erode_size": 10,
  "default_base_size": 1000,
  "max_file_size": 16777216,
  "allowed_extensions": ["png", "jpg", "jpeg", "gif", "bmp", "tiff"]
}
```

## Parameters

### AI Models

| Model | Description | Best For |
|-------|-------------|----------|
| `u2net` | General Purpose | Most image types |
| `u2netp` | Faster Processing | Speed over quality |
| `u2net_human_seg` | Human Segmentation | People and portraits |
| `u2net_cloth_seg` | Clothing Segmentation | Fashion and clothing |

### Quality Settings

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `alpha_matting` | boolean | true/false | false | Improves edge quality (slower) |
| `foreground_threshold` | integer | 0-255 | 240 | Foreground detection sensitivity |
| `background_threshold` | integer | 0-255 | 10 | Background removal sensitivity |
| `erode_size` | integer | 1-20 | 10 | Edge refinement |
| `base_size` | integer | 500-2000 | 1000 | Processing resolution |

## File Limits

### Single Images
- **Max file size**: 16MB
- **Supported formats**: PNG, JPG, JPEG, GIF, BMP, TIFF

### ZIP Files
- **Max ZIP size**: 50MB
- **Max uncompressed size**: 100MB
- **Max files in ZIP**: 100
- **Max images in ZIP**: 50
- **Supported image formats**: PNG, JPG, JPEG, GIF, BMP, TIFF, WEBP

## Error Responses

All endpoints return appropriate HTTP status codes and error messages:

```json
{
  "error": "Error description"
}
```

Common status codes:
- `400 Bad Request`: Invalid input or file format
- `413 Payload Too Large`: File too large
- `415 Unsupported Media Type`: Unsupported file format
- `500 Internal Server Error`: Server processing error

## Examples

### Python Example

```python
import requests
import base64

# Process single image
with open('image.jpg', 'rb') as f:
    files = {'image': f}
    data = {
        'ai_model': 'u2net',
        'alpha_matting': 'false'
    }
    response = requests.post('http://localhost:5000/api/v1/process', 
                           files=files, data=data)
    result = response.json()
    print(result['message'])

# Process ZIP file
with open('images.zip', 'rb') as f:
    files = {'zip_file': f}
    response = requests.post('http://localhost:5000/api/v1/process-zip', 
                           files=files)
    result = response.json()
    print(f"Processed {result['successful']} images")

# Base64 image processing
with open('image.jpg', 'rb') as f:
    image_data = base64.b64encode(f.read()).decode('utf-8')
    data = {
        'image_data': image_data,
        'ai_model': 'u2net_human_seg'
    }
    response = requests.post('http://localhost:5000/api/v1/process', 
                           data=data)
    result = response.json()
    print(result['message'])
```

### cURL Examples

```bash
# Process single image
curl -X POST http://localhost:5000/api/v1/process \
  -F "image=@image.jpg" \
  -F "ai_model=u2net" \
  -F "alpha_matting=false"

# Process ZIP file
curl -X POST http://localhost:5000/api/v1/process-zip \
  -F "zip_file=@images.zip" \
  -F "ai_model=u2net_human_seg"

# Health check
curl http://localhost:5000/api/v1/health

# Get available models
curl http://localhost:5000/api/v1/models
```

### JavaScript Example

```javascript
// Process single image
const formData = new FormData();
formData.append('image', fileInput.files[0]);
formData.append('ai_model', 'u2net');

fetch('http://localhost:5000/api/v1/process', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    console.log(data.message);
    // data.processed_image contains base64 result
});

// Base64 image processing
const canvas = document.createElement('canvas');
const ctx = canvas.getContext('2d');
// ... draw image to canvas ...
const imageData = canvas.toDataURL('image/jpeg');

fetch('http://localhost:5000/api/v1/process', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: `image_data=${encodeURIComponent(imageData)}&ai_model=u2net`
})
.then(response => response.json())
.then(data => {
    console.log(data.message);
});
```

## Rate Limiting

Currently, no rate limiting is implemented. However, processing is resource-intensive, so consider implementing appropriate delays between requests in your applications.

## Best Practices

1. **Use appropriate AI models** for your image type
2. **Enable alpha matting** for better quality when speed isn't critical
3. **Use ZIP files** for batch processing multiple images
4. **Handle errors gracefully** and implement retry logic
5. **Monitor processing times** and adjust quality settings accordingly
6. **Clean up downloaded files** after processing

## Support

For API support and questions:
- Check the error messages for specific issues
- Verify file formats and sizes
- Ensure the service is running and accessible
- Review the health check endpoint for service status 