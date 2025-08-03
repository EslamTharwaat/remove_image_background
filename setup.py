#!/usr/bin/env python3
"""
Setup script for AI Background Remover
"""
import os
import sys
import subprocess
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


def main():
    """Main setup function"""
    print("🚀 Setting up AI Background Remover...")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Create virtual environment
    if not os.path.exists('venv'):
        if not run_command('python3 -m venv venv', 'Creating virtual environment'):
            sys.exit(1)
    else:
        print("✅ Virtual environment already exists")
    
    # Determine Python path
    if os.name == 'nt':  # Windows
        python_path = os.path.join('venv', 'Scripts', 'python.exe')
        pip_path = os.path.join('venv', 'Scripts', 'pip.exe')
    else:  # Unix/Linux/Mac
        python_path = os.path.join('venv', 'bin', 'python')
        pip_path = os.path.join('venv', 'bin', 'pip')
    
    # Upgrade pip
    run_command(f'"{pip_path}" install --upgrade pip', 'Upgrading pip')
    
    # Install requirements
    if not run_command(f'"{pip_path}" install -r requirements.txt', 'Installing dependencies'):
        sys.exit(1)
    
    # Create necessary directories
    directories = ['uploads', 'outputs', 'app/static/images']
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Activate virtual environment:")
    if os.name == 'nt':  # Windows
        print("   venv\\Scripts\\activate")
    else:  # Unix/Linux/Mac
        print("   source venv/bin/activate")
    print("2. Run the application:")
    print("   python run.py")
    print("3. Open your browser to: http://localhost:5000")
    print("\n🚀 Happy coding!")


if __name__ == '__main__':
    main() 