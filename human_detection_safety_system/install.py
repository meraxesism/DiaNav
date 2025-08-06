#!/usr/bin/env python3
"""
Installation Script for Human Detection Safety System
Automates environment setup, dependency installation, and system verification
"""

import os
import sys
import subprocess
import platform
import urllib.request
import shutil
from pathlib import Path
import yaml

def print_banner():
    """Print installation banner"""
    print("="*70)
    print("🚨 HUMAN DETECTION SAFETY SYSTEM - INSTALLATION 🚨")
    print("="*70)
    print("Setting up your assembly line safety monitoring system...")
    print("="*70)

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ ERROR: Python 3.8 or higher is required!")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        print("   Please upgrade Python and try again.")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
    return True

def install_system_dependencies():
    """Install system-level dependencies"""
    print("\n📦 Installing system dependencies...")
    
    system = platform.system().lower()
    
    try:
        if system == "linux":
            # Check if we have apt (Debian/Ubuntu)
            if shutil.which("apt"):
                print("   Installing Linux dependencies via apt...")
                subprocess.run([
                    "sudo", "apt", "update"
                ], check=False)
                subprocess.run([
                    "sudo", "apt", "install", "-y",
                    "python3-pip", "python3-dev", "python3-venv",
                    "libgl1-mesa-glx", "libglib2.0-0", "libsm6", 
                    "libxext6", "libxrender-dev", "libgomp1",
                    "ffmpeg", "libavcodec-dev", "libavformat-dev",
                    "libswscale-dev", "libv4l-dev", "libxvidcore-dev",
                    "libx264-dev", "libjpeg-dev", "libpng-dev",
                    "libtiff-dev", "libatlas-base-dev", "gfortran"
                ], check=False)
            
            # Check if we have yum (CentOS/RHEL)
            elif shutil.which("yum"):
                print("   Installing Linux dependencies via yum...")
                subprocess.run([
                    "sudo", "yum", "install", "-y",
                    "python3-pip", "python3-devel",
                    "mesa-libGL", "glib2", "libSM", "libXext",
                    "libXrender", "libgomp", "ffmpeg-devel"
                ], check=False)
        
        elif system == "darwin":  # macOS
            print("   macOS detected - checking for Homebrew...")
            if not shutil.which("brew"):
                print("   Installing Homebrew...")
                subprocess.run([
                    "/bin/bash", "-c",
                    "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
                ], check=False)
            
            print("   Installing macOS dependencies...")
            subprocess.run([
                "brew", "install", "python", "opencv", "ffmpeg"
            ], check=False)
        
        elif system == "windows":
            print("   Windows detected - dependencies will be installed via pip")
            
        print("✅ System dependencies installation completed")
        return True
        
    except Exception as e:
        print(f"⚠️  Warning: Could not install some system dependencies: {e}")
        print("   You may need to install them manually")
        return True  # Continue anyway

def create_virtual_environment():
    """Create and activate virtual environment"""
    print("\n🔧 Setting up virtual environment...")
    
    venv_path = Path("venv")
    
    try:
        if venv_path.exists():
            print("   Virtual environment already exists")
        else:
            print("   Creating virtual environment...")
            subprocess.run([
                sys.executable, "-m", "venv", "venv"
            ], check=True)
        
        # Determine activation script path
        if platform.system().lower() == "windows":
            activate_script = venv_path / "Scripts" / "activate"
            pip_path = venv_path / "Scripts" / "pip"
        else:
            activate_script = venv_path / "bin" / "activate"
            pip_path = venv_path / "bin" / "pip"
        
        print(f"✅ Virtual environment ready at: {venv_path}")
        print(f"   Activation script: {activate_script}")
        
        return str(pip_path)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return None

def install_python_dependencies(pip_path=None):
    """Install Python dependencies"""
    print("\n📚 Installing Python dependencies...")
    
    # Use system pip if virtual environment pip not available
    pip_cmd = pip_path if pip_path and Path(pip_path).exists() else "pip"
    
    # Core dependencies
    dependencies = [
        "opencv-python==4.8.1.78",
        "ultralytics==8.0.196", 
        "mediapipe==0.10.7",
        "torch>=2.0.0",
        "torchvision>=0.15.0",
        "numpy>=1.24.0",
        "Pillow>=10.0.0",
        "pygame>=2.5.0",
        "PyYAML>=6.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
        "pandas>=1.5.0",
        "scikit-learn>=1.3.0"
    ]
    
    try:
        # Upgrade pip first
        print("   Upgrading pip...")
        subprocess.run([pip_cmd, "install", "--upgrade", "pip"], check=True)
        
        # Install dependencies
        for dep in dependencies:
            print(f"   Installing {dep}...")
            result = subprocess.run([pip_cmd, "install", dep], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"⚠️  Warning: Failed to install {dep}")
                print(f"      Error: {result.stderr}")
            else:
                print(f"   ✅ {dep} installed successfully")
        
        print("✅ Python dependencies installation completed")
        return True
        
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def download_yolo_models():
    """Download YOLO models"""
    print("\n🤖 Downloading YOLO models...")
    
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    models = [
        ("yolov8n.pt", "https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt"),
        ("yolov8s.pt", "https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8s.pt"),
        ("yolov8m.pt", "https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8m.pt")
    ]
    
    try:
        for model_name, model_url in models:
            model_path = models_dir / model_name
            
            if model_path.exists():
                print(f"   ✅ {model_name} already exists")
                continue
            
            print(f"   Downloading {model_name}...")
            try:
                urllib.request.urlretrieve(model_url, model_path)
                print(f"   ✅ {model_name} downloaded successfully")
            except Exception as e:
                print(f"   ⚠️  Failed to download {model_name}: {e}")
                print(f"      Model will be downloaded automatically on first use")
        
        print("✅ YOLO models setup completed")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up models: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directory structure...")
    
    directories = [
        "logs",
        "logs/screenshots", 
        "audio",
        "config",
        "models"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ Created: {directory}")
    
    print("✅ Directory structure created")

def create_sample_alarm():
    """Create a sample alarm sound"""
    print("\n🔊 Creating sample alarm sound...")
    
    try:
        import numpy as np
        import wave
        
        # Generate a simple beep sound
        sample_rate = 22050
        duration = 1.0
        frequency = 800
        
        # Generate sine wave
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        wave_data = np.sin(frequency * 2 * np.pi * t)
        
        # Convert to 16-bit integers
        wave_data = (wave_data * 32767).astype(np.int16)
        
        # Save as WAV file
        alarm_path = Path("audio") / "alarm.wav"
        with wave.open(str(alarm_path), 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(wave_data.tobytes())
        
        print(f"   ✅ Sample alarm created: {alarm_path}")
        return True
        
    except Exception as e:
        print(f"   ⚠️  Could not create sample alarm: {e}")
        return False

def verify_installation():
    """Verify that installation was successful"""
    print("\n🔍 Verifying installation...")
    
    # Test imports
    test_modules = [
        ("cv2", "OpenCV"),
        ("ultralytics", "Ultralytics YOLO"),
        ("mediapipe", "MediaPipe"),
        ("torch", "PyTorch"),
        ("pygame", "Pygame"),
        ("yaml", "PyYAML"),
        ("numpy", "NumPy"),
        ("PIL", "Pillow")
    ]
    
    failed_imports = []
    
    for module, name in test_modules:
        try:
            __import__(module)
            print(f"   ✅ {name} - OK")
        except ImportError as e:
            print(f"   ❌ {name} - FAILED: {e}")
            failed_imports.append(name)
    
    # Check configuration file
    config_path = Path("config/safety_config.yaml")
    if config_path.exists():
        print("   ✅ Configuration file - OK")
        
        # Try to load configuration
        try:
            with open(config_path) as f:
                config = yaml.safe_load(f)
            print("   ✅ Configuration parsing - OK")
        except Exception as e:
            print(f"   ⚠️  Configuration parsing - Warning: {e}")
    else:
        print("   ❌ Configuration file - MISSING")
        failed_imports.append("Configuration")
    
    # Check camera availability
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("   ✅ Camera access - OK")
            cap.release()
        else:
            print("   ⚠️  Camera access - No camera detected (this is OK if using IP camera)")
    except Exception as e:
        print(f"   ⚠️  Camera test - Warning: {e}")
    
    if failed_imports:
        print(f"\n❌ Installation verification failed. Missing: {', '.join(failed_imports)}")
        return False
    else:
        print("\n✅ Installation verification successful!")
        return True

def create_startup_script():
    """Create startup scripts for different platforms"""
    print("\n🚀 Creating startup scripts...")
    
    # Create run script for Unix-like systems
    run_script_content = """#!/bin/bash
# Human Detection Safety System Startup Script

echo "🚨 Starting Human Detection Safety System..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
fi

# Run the system
python main.py "$@"
"""
    
    # Create Windows batch file
    run_bat_content = """@echo off
REM Human Detection Safety System Startup Script

echo 🚨 Starting Human Detection Safety System...

REM Activate virtual environment if it exists
if exist "venv\\Scripts\\activate.bat" (
    call venv\\Scripts\\activate.bat
    echo ✅ Virtual environment activated
)

REM Run the system
python main.py %*
"""
    
    try:
        # Unix script
        with open("run.sh", "w") as f:
            f.write(run_script_content)
        os.chmod("run.sh", 0o755)
        print("   ✅ Created run.sh (Unix/Linux/macOS)")
        
        # Windows script
        with open("run.bat", "w") as f:
            f.write(run_bat_content)
        print("   ✅ Created run.bat (Windows)")
        
        return True
        
    except Exception as e:
        print(f"   ⚠️  Could not create startup scripts: {e}")
        return False

def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "="*70)
    print("🎉 INSTALLATION COMPLETE!")
    print("="*70)
    
    print("\n📋 NEXT STEPS:")
    print("1. Review and customize config/safety_config.yaml for your setup")
    print("2. Position your camera to cover the assembly line area")
    print("3. Test the system with: python main.py")
    print("   Or use the startup scripts: ./run.sh (Unix) or run.bat (Windows)")
    
    print("\n🎯 QUICK START:")
    print("   python main.py                    # Run with default settings")
    print("   python main.py --config my.yaml  # Use custom configuration")
    print("   python main.py --verbose         # Enable detailed logging")
    
    print("\n🔧 CONFIGURATION:")
    print("   Edit config/safety_config.yaml to:")
    print("   - Set your camera device ID or IP camera URL")
    print("   - Define safety zones for your assembly line")
    print("   - Adjust detection sensitivity and alert settings")
    
    print("\n📖 DOCUMENTATION:")
    print("   See README.md for detailed usage instructions")
    print("   Check logs/ directory for system logs and incident reports")
    
    print("\n⚠️  SAFETY REMINDER:")
    print("   This system enhances safety but should not be the only safety measure.")
    print("   Always maintain proper physical barriers and emergency procedures.")
    
    print("\n" + "="*70)

def main():
    """Main installation function"""
    print_banner()
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    # Installation steps
    steps = [
        ("Installing system dependencies", install_system_dependencies),
        ("Creating directories", create_directories),
        ("Setting up virtual environment", create_virtual_environment),
        ("Installing Python dependencies", lambda: install_python_dependencies()),
        ("Downloading YOLO models", download_yolo_models),
        ("Creating sample alarm", create_sample_alarm),
        ("Creating startup scripts", create_startup_script),
        ("Verifying installation", verify_installation)
    ]
    
    pip_path = None
    
    for step_name, step_func in steps:
        try:
            if step_name == "Setting up virtual environment":
                pip_path = step_func()
                if pip_path is None:
                    print("⚠️  Continuing with system pip...")
            elif step_name == "Installing Python dependencies":
                if not install_python_dependencies(pip_path):
                    print("⚠️  Some dependencies may not be installed correctly")
            else:
                step_func()
                
        except KeyboardInterrupt:
            print("\n\n❌ Installation interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Error in {step_name}: {e}")
            response = input("Continue anyway? (y/N): ").strip().lower()
            if response != 'y':
                sys.exit(1)
    
    print_next_steps()

if __name__ == "__main__":
    main()