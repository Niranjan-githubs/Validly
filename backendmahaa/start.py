#!/usr/bin/env python3
"""
Startup script for FoundrScan Backend
"""

import os
import sys
import uvicorn
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed."""
    try:
        import fastapi
        import pydantic
        import uvicorn
        print("✅ All core dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_structure():
    """Check if the backend structure is correct."""
    required_files = [
        "api/main.py",
        "api/models/chat.py",
        "api/models/analysis.py",
        "core/pipeline.py",
        "agents/idea_agent.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    
    print("✅ Backend structure is correct")
    return True

def run_tests():
    """Run backend tests."""
    print("\n🧪 Running backend tests...")
    
    try:
        from test_backend import main as run_tests
        result = run_tests()
        if result == 0:
            print("✅ All tests passed!")
            return True
        else:
            print("❌ Some tests failed!")
            return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def start_server():
    """Start the FastAPI server."""
    print("\n🚀 Starting FoundrScan Backend...")
    
    # Get configuration from environment or use defaults
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    print(f"📍 Server will run on: http://{host}:{port}")
    print(f"🔧 Debug mode: {debug}")
    print("📖 API documentation: http://localhost:8000/docs")
    print("🔄 Auto-reload: Enabled")
    print("\n" + "="*50)
    
    try:
        uvicorn.run(
            "api.main:app",
            host=host,
            port=port,
            reload=debug,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False
    
    return True

def main():
    """Main startup function."""
    print("🎯 FoundrScan Backend Startup")
    print("="*50)
    
    # Check if we're in the right directory
    if not os.path.exists("api/main.py"):
        print("❌ Please run this script from the backend directory")
        print("   cd backend && python start.py")
        return 1
    
    # Run checks
    if not check_dependencies():
        return 1
    
    if not check_structure():
        return 1
    
    # Run tests (optional - can be skipped with --no-tests)
    if "--no-tests" not in sys.argv:
        if not run_tests():
            print("\n⚠️ Tests failed, but continuing...")
            response = input("Continue anyway? (y/N): ")
            if response.lower() != 'y':
                return 1
    
    # Start the server
    return 0 if start_server() else 1

if __name__ == "__main__":
    sys.exit(main()) 