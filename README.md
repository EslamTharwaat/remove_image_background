# Background Remover - Flask Web Application

A beautiful web application that removes backgrounds from images using AI-powered technology. Built with Flask and the `backgroundremover` library.

## Features

- 🎨 **Beautiful Modern UI** - Clean, responsive design with smooth animations
- 📁 **Drag & Drop Upload** - Easy file upload with drag and drop support
- 🖼️ **Multiple Format Support** - Supports JPG, PNG, GIF, BMP, and TIFF formats
- ⚡ **Real-time Processing** - Live progress indication during background removal
- 📱 **Responsive Design** - Works perfectly on desktop, tablet, and mobile devices
- 💾 **Download Results** - Easy download of processed images
- 🔄 **Batch Processing** - Process multiple images one after another

## Screenshots

The application features a modern gradient background with a clean white interface for uploading and processing images. Users can drag and drop images or click to browse, and the results are displayed in a side-by-side comparison view.

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd remove_image_background
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:5000`

## Usage

1. **Upload an Image**
   - Drag and drop an image onto the upload area, or
   - Click the upload area to browse and select a file

2. **Wait for Processing**
   - The application will show a loading spinner while processing
   - Processing time depends on image size and complexity

3. **View Results**
   - See the original and processed images side by side
   - Download the background-removed image

4. **Process Another Image**
   - Click "Process Another Image" to start over

## Supported File Formats

- **Input**: JPG, JPEG, PNG, GIF, BMP, TIFF
- **Output**: PNG (with transparent background)

## File Size Limits

- Maximum file size: 16MB
- Recommended resolution: Up to 4K (3840x2160)

## Technical Details

### Backend
- **Framework**: Flask 2.3.3
- **Background Removal**: backgroundremover 0.2.9
- **Image Processing**: Pillow 10.0.1
- **File Handling**: Werkzeug 2.3.7

### Frontend
- **HTML5**: Semantic markup with modern features
- **CSS3**: Flexbox, Grid, animations, and responsive design
- **JavaScript**: ES6+ with fetch API for AJAX requests
- **Icons**: Font Awesome 6.0.0
- **Fonts**: Inter (Google Fonts)

### Project Structure
```
remove_image_background/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/
│   └── index.html        # Main HTML template
├── static/
│   ├── css/
│   │   └── style.css     # Stylesheets
│   └── js/
│       └── script.js     # JavaScript functionality
├── uploads/              # Temporary uploaded files
└── outputs/              # Processed images
```

## API Endpoints

- `GET /` - Main application page
- `POST /upload` - Upload and process image
- `GET /uploads/<filename>` - Serve uploaded images
- `GET /outputs/<filename>` - Serve processed images

## Error Handling

The application includes comprehensive error handling for:
- Invalid file types
- File size limits
- Network errors
- Processing failures
- Server errors

## Performance Considerations

- Images are processed server-side using the `backgroundremover` library
- Temporary files are automatically cleaned up
- Unique filenames prevent conflicts
- Responsive design ensures good performance on all devices

## Troubleshooting

### Common Issues

1. **"Module not found" errors**
   - Make sure you've installed all dependencies: `pip install -r requirements.txt`

2. **Background removal not working**
   - Ensure the image has a clear subject with good contrast
   - Try with different image formats
   - Check that the image file is not corrupted

3. **Slow processing**
   - Large images take longer to process
   - Consider resizing very large images before upload

4. **Port already in use**
   - Change the port in `app.py` or kill the process using the port

### System Requirements

- **RAM**: Minimum 4GB (8GB recommended for large images)
- **Storage**: At least 1GB free space for temporary files
- **CPU**: Any modern processor (faster CPU = faster processing)

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the application.

## License

This project is open source and available under the MIT License.

## Acknowledgments

- [backgroundremover](https://pypi.org/project/backgroundremover/) - The core background removal library
- [Flask](https://flask.palletsprojects.com/) - The web framework
- [Font Awesome](https://fontawesome.com/) - Icons
- [Google Fonts](https://fonts.google.com/) - Typography 