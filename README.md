# 🎨 Otrium AI Background Remover

A modern Flask web application specialized in removing backgrounds from human photos using advanced AI. Optimized for fashion photography and portrait images with clean architecture, comprehensive security features, and an intuitive user interface.

## ✨ Features

### 🖼️ **Core Functionality**
- **AI-Powered Human Background Removal**: Uses specialized U²-Net human segmentation model
- **Optimized for Fashion**: Perfect for clothing, portrait, and fashion photography
- **Batch Processing**: Process multiple images in parallel
- **S3 Integration**: Optional upload to AWS S3 for cloud storage

### 🚀 **Performance & Optimization**
- **Human-Focused AI**: Specialized model for people wearing clothes
- **Image Optimization**: Automatic resizing for faster processing
- **Model Caching**: Intelligent caching for improved performance
- **Parallel Processing**: Multi-threaded batch processing
- **Memory Management**: Efficient resource utilization

### 🔒 **Security Features**
- **CSRF Protection**: Built-in cross-site request forgery protection
- **Secure File Handling**: SHA256 filename hashing and path validation
- **Input Validation**: Comprehensive file and data validation
- **Security Headers**: X-Content-Type-Options, X-Frame-Options
- **Automatic Cleanup**: Secure file cleanup and management

### 🎯 **User Experience**
- **Modern UI**: Clean, responsive design with Otrium branding
- **Drag & Drop**: Intuitive file upload interface
- **Real-time Progress**: Live progress tracking for batch processing
- **Individual Progress**: Per-image progress tracking in batch mode
- **ZIP File Support**: Upload multiple images in ZIP format

## 🏗️ Project Structure

```
remove_image_background/
├── app/                          # Main application package
│   ├── __init__.py              # Application factory
│   ├── config/                  # Configuration management
│   │   ├── __init__.py
│   │   └── settings.py          # Application settings
│   ├── routes/                  # Route definitions
│   │   ├── __init__.py
│   │   ├── main.py              # Main application routes
│   │   └── api.py               # REST API routes
│   ├── services/                # Business logic services
│   │   ├── __init__.py
│   │   ├── background_remover.py # Background removal service
│   │   ├── batch_processor.py   # Batch processing service
│   │   └── s3_service.py        # AWS S3 integration
│   ├── utils/                   # Utility functions
│   │   ├── __init__.py
│   │   └── file_utils.py        # File handling utilities
│   ├── static/                  # Static assets
│   │   ├── css/
│   │   │   └── style.css        # Application styles
│   │   ├── js/
│   │   │   ├── script.js        # Main frontend JavaScript
│   │   │   └── settings.js      # Settings page JavaScript
│   │   └── images/              # Static images
│   └── templates/               # HTML templates
│       ├── index.html           # Main application template
│       └── settings.html        # Settings page template
├── uploads/                     # Uploaded images (auto-created)
├── outputs/                     # Processed images (auto-created)
├── venv/                        # Virtual environment (auto-created)
├── requirements.txt             # Python dependencies
├── run.py                       # Application entry point
├── start.sh                     # Startup script for Unix/Linux
├── API_DOCUMENTATION.md         # REST API documentation
├── .gitignore                   # Git ignore rules
└── README.md                    # Project documentation
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/EslamTharwaat/remove_image_background.git
   cd remove_image_background
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python run.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:5000`

### Alternative: Using the startup script
```bash
chmod +x start.sh
./start.sh
```

## 🎛️ Configuration

The application uses a streamlined configuration system optimized for human background removal:

### Environment Variables
- `FLASK_ENV`: Set to `development`, `production`, or `testing`
- `SECRET_KEY`: Custom secret key for enhanced security

### Key Settings
Settings are defined in `app/config/settings.py`:

```python
# AI Model (fixed for human segmentation)
AVAILABLE_MODELS = ['u2net_human_seg']
DEFAULT_MODEL = 'u2net_human_seg'
DEFAULT_ALPHA_MATTING = False

# Performance settings
ENABLE_IMAGE_OPTIMIZATION = True
MAX_IMAGE_SIZE = 1024
ENABLE_MODEL_CACHING = True

# S3 Integration (optional)
ENABLE_S3_UPLOAD = False
S3_BUCKET_NAME = ''
S3_REGION_NAME = 'us-east-1'
```

## 🎨 Usage Guide

### Single Image Processing
1. **Upload Image**: Drag & drop or click to upload a photo of a person
2. **Automatic Processing**: Uses optimized human segmentation model
3. **Download**: Download the processed image with transparent background
4. **Perfect for**: Portraits, fashion photos, people wearing clothes

### Batch Processing
1. **Upload Multiple Images**: Select multiple images or upload a ZIP file
2. **Parallel Processing**: All images processed simultaneously
3. **Monitor Progress**: Real-time progress for each image
4. **Download Results**: Download individual or all processed images

### S3 Integration (Optional)
1. **Configure S3**: Go to Settings page to configure AWS credentials
2. **Automatic Upload**: Processed images can be automatically uploaded to S3
3. **Cloud Storage**: Access your processed images from anywhere

### Best Results
- **Human subjects**: Optimized for people wearing clothes
- **Fashion photography**: Excellent for clothing and fashion items
- **Portrait photography**: Great for profile pictures and portraits
- **E-commerce**: Perfect for product photos with human models

## 📡 REST API

The application includes a comprehensive REST API for programmatic access:

### Base URL
`http://localhost:5000/api/v1`

### Key Endpoints
- `POST /process` - Process single image
- `POST /process-zip` - Process ZIP file with multiple images
- `GET /health` - Health check
- `GET /models` - Get available models
- `GET /settings` - Get API settings

### Documentation
See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for complete API documentation with examples.

## 🔧 Development

### Project Architecture

The application follows clean architecture principles:

- **Routes Layer**: HTTP request handling and response formatting
- **Services Layer**: Business logic and external service integration
- **Utils Layer**: Reusable utility functions
- **Config Layer**: Application configuration management

### Adding New Features

1. **New Routes**: Add to `app/routes/main.py` or `app/routes/api.py`
2. **New Services**: Create in `app/services/`
3. **New Utils**: Add to `app/utils/`
4. **Configuration**: Update `app/config/settings.py`

### Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings for all functions and classes
- Keep functions small and focused

## 🧪 Testing

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-flask

# Run tests
pytest
```

### Test Structure
```
tests/
├── test_routes.py      # Route testing
├── test_services.py    # Service testing
├── test_utils.py       # Utility testing
└── conftest.py         # Test configuration
```

## 🚀 Deployment

### Production Deployment
1. Set `FLASK_ENV=production`
2. Configure `SECRET_KEY` environment variable
3. Use a production WSGI server (Gunicorn, uWSGI)
4. Set up reverse proxy (Nginx, Apache)
5. Enable HTTPS
6. Configure S3 credentials if using cloud storage

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "run.py"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **U²-Net Models**: For the excellent human segmentation AI model
- **Flask Community**: For the robust web framework
- **Pillow**: For image processing capabilities
- **Otrium**: For branding and UI design inspiration
- **backgroundremover**: For the AI model integration

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the API documentation
- Review the code comments

---

**© 2025 Otrium.com - Professional AI Image Processing**