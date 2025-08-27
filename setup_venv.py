#!/usr/bin/env python3
"""
Virtual Environment Setup Script for Job Automation System
This script helps you set up a virtual environment and install all dependencies.
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} is not supported.")
        print("   Please install Python 3.8 or higher.")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def create_virtual_environment():
    """Create a virtual environment named 'venv'"""
    print("\n🔧 Creating virtual environment...")
    
    venv_path = "venv"
    
    # Check if venv already exists
    if os.path.exists(venv_path):
        print(f"⚠️  Virtual environment '{venv_path}' already exists")
        response = input("Do you want to recreate it? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            print("Removing existing virtual environment...")
            if platform.system() == "Windows":
                subprocess.run(["rmdir", "/s", "/q", venv_path], shell=True)
            else:
                subprocess.run(["rm", "-rf", venv_path])
        else:
            print("Using existing virtual environment")
            return True
    
    try:
        # Create virtual environment
        subprocess.check_call([sys.executable, "-m", "venv", venv_path])
        print(f"✅ Virtual environment created: {venv_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False

def get_venv_python_path():
    """Get the path to the virtual environment's Python executable"""
    if platform.system() == "Windows":
        return os.path.join("venv", "Scripts", "python.exe")
    else:
        return os.path.join("venv", "bin", "python")

def get_venv_pip_path():
    """Get the path to the virtual environment's pip executable"""
    if platform.system() == "Windows":
        return os.path.join("venv", "Scripts", "pip.exe")
    else:
        return os.path.join("venv", "bin", "pip")

def upgrade_pip():
    """Upgrade pip in the virtual environment"""
    print("\n📦 Upgrading pip...")
    
    try:
        pip_path = get_venv_pip_path()
        subprocess.check_call([pip_path, "install", "--upgrade", "pip"])
        print("✅ Pip upgraded successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to upgrade pip: {e}")
        return False

def install_dependencies():
    """Install all required dependencies in the virtual environment"""
    print("\n📦 Installing dependencies...")
    
    try:
        pip_path = get_venv_pip_path()
        subprocess.check_call([pip_path, "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_env_file():
    """Create the .env file"""
    print("\n🔧 Creating .env file...")
    
    try:
        from environment_config import create_env_file
        if create_env_file():
            print("✅ .env file created successfully")
            return True
        else:
            return False
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def display_activation_instructions():
    """Display instructions for activating the virtual environment"""
    print("\n" + "="*60)
    print("🎉 VIRTUAL ENVIRONMENT SETUP COMPLETE!")
    print("="*60)
    
    print("\n📋 Next Steps:")
    print("1. Activate the virtual environment:")
    
    if platform.system() == "Windows":
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    
    print("\n2. Configure your API keys:")
    print("   - Edit the .env file with your actual API keys")
    print("   - At minimum, add your GROQ_API_KEY")
    
    print("\n3. Test the system:")
    print("   python test_system.py")
    
    print("\n4. Run the main application:")
    print("   python main.py")
    
    print("\n📚 API Key Sources:")
    print("   - Groq: https://console.groq.com/")
    print("   - LinkedIn: https://developer.linkedin.com/")
    print("   - OpenAI: https://platform.openai.com/")
    print("   - Anthropic: https://console.anthropic.com/")
    print("   - Google AI: https://makersuite.google.com/")

def main():
    """Main setup function"""
    print("🚀 Job Automation System - Virtual Environment Setup")
    print("="*60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create virtual environment
    if not create_virtual_environment():
        print("\n❌ Virtual environment setup failed.")
        sys.exit(1)
    
    # Upgrade pip
    if not upgrade_pip():
        print("\n⚠️  Pip upgrade failed, but continuing...")
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Dependency installation failed.")
        sys.exit(1)
    
    # Create .env file
    create_env_file()
    
    # Display instructions
    display_activation_instructions()

if __name__ == "__main__":
    main() 