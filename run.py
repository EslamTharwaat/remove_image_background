#!/usr/bin/env python3
"""
Background Remover Flask Application
Startup script for easy execution
"""

import os
import sys
import subprocess

def main():
    # Check if virtual environment exists
    if not os.path.exists('venv'):
        print("Creating virtual environment...")
        subprocess.run([sys.executable, '-m', 'venv', 'venv'])
    
    # Activate virtual environment and run the app
    if os.name == 'nt':  # Windows
        python_path = os.path.join('venv', 'Scripts', 'python.exe')
    else:  # Unix/Linux/Mac
        python_path = os.path.join('venv', 'bin', 'python')
    
    # Install requirements if needed
    print("Installing dependencies...")
    subprocess.run([python_path, '-m', 'pip', 'install', '-r', 'requirements.txt'])
    
    # Run the Flask application
    print("Starting Background Remover application...")
    print("Open your browser and go to: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    
    subprocess.run([python_path, 'app.py'])

if __name__ == '__main__':
    main() 