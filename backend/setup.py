#!/usr/bin/env python3
"""
Setup script for FoundrScan Backend
"""

import os
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    import sys
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install required dependencies."""
    print("\n📦 Installing dependencies...")
    
    try:
        import subprocess
        result = subprocess.run([
            "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
            return True
        else:
            print(f"❌ Error installing dependencies: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def setup_environment():
    """Set up environment configuration."""
    print("\n🔧 Setting up environment...")
    
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if env_example.exists():
        try:
            shutil.copy(env_example, env_file)
            print("✅ Created .env file from env.example")
            print("💡 Please edit .env and add your API keys")
            return True
        except Exception as e:
            print(f"❌ Error creating .env file: {e}")
            return False
    else:
        print("⚠️ env.example not found, creating basic .env file")
        try:
            with open(env_file, 'w') as f:
                f.write("# FoundrScan Backend Configuration\n")
                f.write("# Add your API keys here\n\n")
                f.write("API_HOST=0.0.0.0\n")
                f.write("API_PORT=8000\n")
                f.write("DEBUG=True\n\n")
                f.write("# Add your API keys:\n")
                f.write("# TOGETHER_API_KEY=your-key-here\n")
                f.write("# OPENAI_API_KEY=your-key-here\n")
            print("✅ Created basic .env file")
            print("💡 Please edit .env and add your API keys")
            return True
        except Exception as e:
            print(f"❌ Error creating .env file: {e}")
            return False

def run_tests():
    """Run backend tests."""
    print("\n🧪 Running tests...")
    
    try:
        import subprocess
        result = subprocess.run([
            "python", "test_backend.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ All tests passed!")
            return True
        else:
            print("⚠️ Some tests failed, but setup can continue")
            print("💡 This is normal if API keys are not configured")
            return True  # Allow setup to continue even if tests fail
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def main():
    """Main setup function."""
    print("🎯 FoundrScan Backend Setup")
    print("="*50)
    
    # Check if we're in the right directory
    if not os.path.exists("api/main.py"):
        print("❌ Please run this script from the backend directory")
        print("   cd backend && python setup.py")
        return 1
    
    # Run setup steps
    steps = [
        ("Python Version Check", check_python_version),
        ("Install Dependencies", install_dependencies),
        ("Setup Environment", setup_environment),
        ("Run Tests", run_tests)
    ]
    
    for step_name, step_func in steps:
        print(f"\n{'='*30}")
        print(f"Step: {step_name}")
        print(f"{'='*30}")
        
        if not step_func():
            print(f"❌ {step_name} failed")
            return 1
    
    print(f"\n{'='*50}")
    print("🎉 Setup Complete!")
    print(f"{'='*50}")
    print("\nNext steps:")
    print("1. Edit .env file and add your API keys")
    print("2. Run: python start.py")
    print("3. Visit: http://localhost:8000/docs")
    print("\nFor help, see README.md")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main()) 