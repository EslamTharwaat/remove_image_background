# 🔌 Background Remover API Documentation

## Overview

The Background Remover API provides programmatic access to AI-powered background removal functionality optimized for human segmentation. The API supports both single image processing and batch processing via ZIP files, specifically designed for removing backgrounds from photos of people wearing clothes.

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

Process a single image to remove its background using optimized human segmentation.

**Request Formats:**

#### Option 1: File Upload (multipart/form-data)
```
POST /api/v1/process
Content-Type: multipart/form-data

Form Data:
- image: [image file]
```

#### Option 2: Base64 Image (application/x-www-form-urlencoded)
```
POST /api/v1/process
Content-Type: application/x-www-form-urlencoded

Form Data:
- image_data: [base64 encoded image]
```

**Response:**
```json
{
  "success": true,
  "message": "Image processed successfully in 2.5 seconds",
  "processing_time": 2.5,
  "ai_model": "u2net_human_seg",
  "original_filename": "example.jpg",
  "processed_image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "download_url": "/api/v1/download/no_bg_example.jpg"
}
```

### 3. Process ZIP File

**POST** `/process-zip`

Process multiple images from a ZIP file using human segmentation.

**Request:**
```
POST /api/v1/process-zip
Content-Type: multipart/form-data

Form Data:
- zip_file: [ZIP file containing images]
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
      "ai_model": "u2net_human_seg",
      "download_url": "/api/v1/download/no_bg_image1.jpg"
    }
  ],
  "errors": [
    {
      "filename": "image2.jpg",
      "error": "Invalid image format"
    }
  ],
  "ai_model": "u2net_human_seg"
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

Get information about the AI model used for processing.

**Response:**
```json
{
  "models": ["u2net_human_seg"],
  "default_model": "u2net_human_seg",
  "description": "Optimized for human background removal"
}
```

### 6. Get Settings Information

**GET** `/settings`

Get processing settings and limits.

**Response:**
```json
{
  "alpha_matting": false,
  "ai_model": "u2net_human_seg",
  "description": "Fixed settings optimized for human background removal",
  "max_file_size": 16777216,
  "allowed_extensions": ["jpg", "gif", "bmp", "png", "jpeg", "tiff"]
}
```

### 7. Test S3 Connection

**POST** `/test-s3`

Test S3 connection with provided credentials (used by the web interface).

**Request:**
```json
{
  "enable_s3_upload": true,
  "s3_bucket_name": "your-bucket",
  "s3_access_key_id": "your-access-key",
  "s3_secret_access_key": "your-secret-key",
  "s3_region_name": "us-east-1"
}
```

**Response:**
```json
{
  "success": true,
  "message": "S3 connection successful"
}
```

## AI Model

The API uses a fixed AI model optimized for human background removal:

| Model | Description | Optimized For |
|-------|-------------|---------------|
| `u2net_human_seg` | Human Segmentation | People wearing clothes, fashion photos |

**Key Features:**
- Specialized for human subjects
- Optimized for clothing and fashion
- No quality settings needed - works out of the box
- Fast processing with excellent results for people

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

# Process single image (simplified - no quality settings needed)
with open('person_photo.jpg', 'rb') as f:
    files = {'image': f}
    response = requests.post('http://localhost:5000/api/v1/process', 
                           files=files)
    result = response.json()
    print(result['message'])

# Process ZIP file
with open('fashion_photos.zip', 'rb') as f:
    files = {'zip_file': f}
    response = requests.post('http://localhost:5000/api/v1/process-zip', 
                           files=files)
    result = response.json()
    print(f"Processed {result['successful']} images")

# Base64 image processing
with open('portrait.jpg', 'rb') as f:
    image_data = base64.b64encode(f.read()).decode('utf-8')
    data = {'image_data': image_data}
    response = requests.post('http://localhost:5000/api/v1/process', 
                           data=data)
    result = response.json()
    print(result['message'])
```

### cURL Examples

```bash
# Process single image
curl -X POST http://localhost:5000/api/v1/process \
  -F "image=@person_photo.jpg"

# Process ZIP file
curl -X POST http://localhost:5000/api/v1/process-zip \
  -F "zip_file=@fashion_photos.zip"

# Health check
curl http://localhost:5000/api/v1/health

# Get model information
curl http://localhost:5000/api/v1/models
```

### JavaScript Example

```javascript
// Process single image (simplified - no settings needed)
const formData = new FormData();
formData.append('image', fileInput.files[0]);

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
    body: `image_data=${encodeURIComponent(imageData)}`
})
.then(response => response.json())
.then(data => {
    console.log(data.message);
});
```

## Rate Limiting

Currently, no rate limiting is implemented. However, processing is resource-intensive, so consider implementing appropriate delays between requests in your applications.

## Best Practices

1. **Use for human subjects** - API is optimized for people wearing clothes
2. **Use ZIP files** for batch processing multiple images
3. **Handle errors gracefully** and implement retry logic
4. **Monitor processing times** and adjust expectations accordingly
5. **Clean up downloaded files** after processing
6. **Ideal for fashion and portrait photography**

## Use Cases

This API is specifically designed for:
- **Fashion photography**: Remove backgrounds from clothing photos
- **Portrait photography**: Clean backgrounds from people photos
- **E-commerce**: Product photos with human models
- **Social media**: Profile pictures and content creation
- **Marketing materials**: Professional-looking human subjects

## Support

For API support and questions:
- Check the error messages for specific issues
- Verify file formats and sizes
- Ensure the service is running and accessible
- Review the health check endpoint for service status
- API is optimized for human subjects - best results with people wearing clothes