# 🎨 AI Background Remover

A modern Flask web application that removes backgrounds from images using advanced AI models. Built with clean architecture, comprehensive security features, and an intuitive user interface.

## ✨ Features

### 🖼️ **Core Functionality**
- **AI-Powered Background Removal**: Uses state-of-the-art U²-Net models
- **Multiple AI Models**: Choose from 4 different AI models for optimal results
- **Quality Settings**: Fine-tune processing parameters for best results
- **Batch Processing**: Process multiple images in parallel
- **Reprocess Feature**: Experiment with different settings without re-uploading

### 🚀 **Performance & Optimization**
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
- **Modern UI**: Clean, responsive design inspired by modern e-commerce
- **Drag & Drop**: Intuitive file upload interface
- **Real-time Progress**: Live progress tracking for batch processing
- **Quality Presets**: Quick settings for Fast, Balanced, and High Quality
- **Individual Progress**: Per-image progress tracking in batch mode

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
│   │   └── main.py              # Main application routes
│   ├── services/                # Business logic services
│   │   ├── __init__.py
│   │   ├── background_remover.py # Background removal service
│   │   └── batch_processor.py   # Batch processing service
│   ├── utils/                   # Utility functions
│   │   ├── __init__.py
│   │   └── file_utils.py        # File handling utilities
│   ├── static/                  # Static assets
│   │   ├── css/
│   │   │   └── style.css        # Application styles
│   │   ├── js/
│   │   │   └── script.js        # Frontend JavaScript
│   │   └── images/              # Static images
│   └── templates/               # HTML templates
│       └── index.html           # Main application template
├── uploads/                     # Uploaded images (auto-created)
├── outputs/                     # Processed images (auto-created)
├── venv/                        # Virtual environment (auto-created)
├── requirements.txt             # Python dependencies
├── run.py                       # Application entry point
├── start.sh                     # Startup script for Unix/Linux
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

The application uses a flexible configuration system with environment-specific settings:

### Environment Variables
- `FLASK_ENV`: Set to `development`, `production`, or `testing`
- `SECRET_KEY`: Custom secret key for enhanced security

### Configuration Options
All settings are defined in `app/config/settings.py`:

```python
# Performance settings
ENABLE_IMAGE_OPTIMIZATION = True
MAX_IMAGE_SIZE = 1024
ENABLE_MODEL_CACHING = True

# AI Model settings
AVAILABLE_MODELS = ['u2net', 'u2netp', 'u2net_human_seg', 'u2net_cloth_seg']
DEFAULT_MODEL = 'u2net'

# Quality settings
DEFAULT_ALPHA_MATTING = False
DEFAULT_ALPHA_MATTING_FOREGROUND_THRESHOLD = 240
DEFAULT_ALPHA_MATTING_BACKGROUND_THRESHOLD = 10
```

## 🎨 Usage Guide

### Single Image Processing
1. **Upload Image**: Drag & drop or click to select an image
2. **Choose AI Model**: Select the best model for your image type
3. **Adjust Quality**: Fine-tune settings or use presets
4. **Process**: Click "Remove Background" to start processing
5. **Download**: Download the processed image
6. **Reprocess**: Try different settings with the "Reprocess" button

### Batch Processing
1. **Upload Multiple Images**: Select multiple images at once
2. **Configure Settings**: Set AI model and quality parameters
3. **Start Processing**: Images are processed in parallel
4. **Monitor Progress**: Real-time progress for each image
5. **Download Results**: Download individual or all processed images

### AI Models Available
- **U²-Net (General Purpose)**: Best for most image types
- **U²-Net+ (Faster)**: Optimized for speed
- **U²-Net Human Segmentation**: Specialized for human subjects
- **U²-Net Clothing Segmentation**: Best for clothing and fashion items

### Quality Settings
- **Alpha Matting**: Improves edge quality (slower processing)
- **Foreground Threshold**: Controls foreground detection sensitivity
- **Background Threshold**: Controls background removal sensitivity
- **Erode Size**: Affects edge refinement
- **Base Size**: Controls processing resolution

## 🔧 Development

### Project Architecture

The application follows clean architecture principles:

- **Routes Layer**: HTTP request handling and response formatting
- **Services Layer**: Business logic and external service integration
- **Utils Layer**: Reusable utility functions
- **Config Layer**: Application configuration management

### Adding New Features

1. **New Routes**: Add to `app/routes/main.py`
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

- **U²-Net Models**: For the excellent background removal AI models
- **Flask Community**: For the robust web framework
- **Pillow**: For image processing capabilities
- **Otrium**: For UI design inspiration

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the code comments

---

**Made with ❤️ by Eslam Tharwat** 