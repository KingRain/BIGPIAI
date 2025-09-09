#!/usr/bin/env python3
"""
Test script to verify the application setup
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_environment():
    """Test if all required environment variables are set"""
    print("🔍 Testing environment setup...")
    
    # Check OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key != "your_openai_api_key_here":
        print("✅ OpenAI API key is configured")
    else:
        print("❌ OpenAI API key is missing or not set properly")
        print("   Please update your .env file with a valid OPENAI_API_KEY")
        return False
    
    return True

def test_imports():
    """Test if all required packages can be imported"""
    print("\n🔍 Testing package imports...")
    
    required_packages = [
        'flask',
        'flask_cors',
        'flask_jwt_extended',
        'openai',
        'docx',
        'dotenv',
        'PyPDF2',
        'thefuzz',
        'flask_socketio',
        'eventlet',
        'openpyxl'
    ]
    
    failed_imports = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError as e:
            print(f"❌ {package} - {e}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        print("   Please install missing packages using: pip install -r requirements.txt")
        return False
    
    print("✅ All packages imported successfully")
    return True

def test_app_creation():
    """Test if the Flask app can be created"""
    print("\n🔍 Testing Flask app creation...")
    
    try:
        # Add the project root to Python path
        project_root = os.path.dirname(os.path.abspath(__file__))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        from app import create_app
        app = create_app()
        print("✅ Flask app created successfully")
        print(f"   App name: {app.name}")
        print(f"   Debug mode: {app.debug}")
        return True
    except Exception as e:
        print(f"❌ Failed to create Flask app: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 BIGPIAI Local Setup Test\n")
    
    tests = [
        test_environment,
        test_imports,
        test_app_creation
    ]
    
    all_passed = True
    for test in tests:
        if not test():
            all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("🎉 All tests passed! Your application is ready to run.")
        print("\nTo start the application, run:")
        print("   python run.py")
        print("\nThe app will be available at: http://127.0.0.1:5000")
    else:
        print("❌ Some tests failed. Please fix the issues above before running the application.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
