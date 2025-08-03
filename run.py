#!/usr/bin/env python3
"""
Main application entry point
"""
import os
from app import create_app

# Create Flask application
app = create_app(os.getenv('FLASK_ENV', 'development'))

if __name__ == '__main__':
    print("🌐 Starting Flask application...")
    print("✅ Application is running at: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server")
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    ) 