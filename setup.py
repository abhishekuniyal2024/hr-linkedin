#!/usr/bin/env python3
"""
Setup script for Job Automation System
This script helps users set up the environment and dependencies.
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

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    
    try:
        # Install from requirements.txt
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_env_file():
    """Create a .env file template"""
    print("\n🔧 Creating environment file...")
    
    env_content = """# Job Automation System Environment Variables

# Required: Groq API Key
GROQ_API_KEY=your_groq_api_key_here

# Optional: LinkedIn API Configuration
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token

# Optional: Email SMTP Configuration
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_email_password

# Job posting settings
MIN_APPLICANTS=10
TOP_CANDIDATES_COUNT=5
SALARY_RANGE_MIN=50000
SALARY_RANGE_MAX=100000
"""
    
    try:
        with open(".env", "w") as f:
            f.write(env_content)
        print("✅ .env file created successfully")
        print("   Please edit .env file with your actual API keys and credentials")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def check_groq_api_key():
    """Check if Groq API key is configured"""
    print("\n🔑 Checking Groq API key...")
    
    # Try to load from environment
    groq_key = os.getenv("GROQ_API_KEY")
    
    if groq_key and groq_key != "your_groq_api_key_here":
        print("✅ Groq API key found in environment")
        return True
    
    # Check .env file
    if os.path.exists(".env"):
        try:
            with open(".env", "r") as f:
                content = f.read()
                if "GROQ_API_KEY=your_groq_api_key_here" not in content:
                    print("✅ Groq API key found in .env file")
                    return True
        except:
            pass
    
    print("⚠️  Groq API key not configured")
    print("   Please set GROQ_API_KEY in your environment or .env file")
    return False

def run_tests():
    """Run system tests"""
    print("\n🧪 Running system tests...")
    
    try:
        result = subprocess.run([sys.executable, "test_system.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ System tests passed")
            return True
        else:
            print("❌ System tests failed")
            print("Output:", result.stdout)
            print("Errors:", result.stderr)
            return False
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        return False

def display_next_steps():
    """Display next steps for the user"""
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETE!")
    print("="*60)
    
    print("\n📋 Next Steps:")
    print("1. Configure your Groq API key:")
    print("   - Get your API key from https://console.groq.com/")
    print("   - Add it to your .env file or set as environment variable")
    
    print("\n2. (Optional) Configure LinkedIn API:")
    print("   - Get LinkedIn API credentials")
    print("   - Add them to your .env file")
    
    print("\n3. (Optional) Configure Email SMTP:")
    print("   - Add your email credentials to .env file")
    print("   - For Gmail, you may need to use an app password")
    
    print("\n4. Run the system:")
    print("   python main.py")
    
    print("\n5. Test the system:")
    print("   python test_system.py")
    
    print("\n📚 Documentation:")
    print("   - Read README.md for detailed instructions")
    print("   - Check the example usage in main.py")

def main():
    """Main setup function"""
    print("🚀 Job Automation System - Setup")
    print("="*50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed. Please check the error messages above.")
        sys.exit(1)
    
    # Create .env file
    create_env_file()
    
    # Check Groq API key
    groq_configured = check_groq_api_key()
    
    # Run tests if Groq is configured
    if groq_configured:
        run_tests()
    else:
        print("\n⚠️  Skipping tests - Groq API key not configured")
    
    # Display next steps
    display_next_steps()

if __name__ == "__main__":
    main() 