#!/usr/bin/env python3
"""
Local Development Server Runner
Run this script to start the Flask application in development mode.
"""
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def setup_environment():
    """Set up environment variables for local development."""
    os.environ.setdefault('FLASK_APP', 'run.py')
    os.environ.setdefault('FLASK_ENV', 'development')
    os.environ.setdefault('FLASK_DEBUG', '1')
    os.environ.setdefault('PRODUCTION', 'false')
    os.environ.setdefault('USE_WAITRESS', 'false')
    
    # Create necessary directories
    directories = [
        'uploads/phase3',
        'outputs/phase3',
        'instance',
        'logs'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        ('flask', 'Flask'),
        ('flask_cors', 'CORS'),
        ('flask_jwt_extended', 'JWTManager'),
        ('docx', 'Document'),
        ('dotenv', 'load_dotenv')
    ]
    
    optional_packages = [
        ('docxtpl', 'DocxTemplate'),
        ('pdf2docx', 'Converter'),
        ('jinja2', 'Environment'),
        ('google.generativeai', None)
    ]
    
    missing_packages = []
    missing_optional = []
    
    # Check required packages
    for package, attr in required_packages:
        try:
            imported = __import__(package)
            if attr:
                getattr(imported, attr)
            print(f"✓ {package} - OK")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
        except AttributeError:
            if attr:
                print(f"❌ {package}.{attr} - MISSING ATTRIBUTE")
                missing_packages.append(package)
            else:
                print(f"✓ {package} - OK")
    
    # Check optional packages
    for package, attr in optional_packages:
        try:
            imported = __import__(package)
            if attr:
                getattr(imported, attr)
            print(f"✓ {package} - OK")
        except ImportError:
            print(f"⚠️  {package} - MISSING (Phase 3 features may not work)")
            missing_optional.append(package)
        except AttributeError:
            if attr:
                print(f"⚠️  {package}.{attr} - MISSING ATTRIBUTE (Phase 3 features may not work)")
                missing_optional.append(package)
            else:
                print(f"✓ {package} - OK")
    
    if missing_packages:
        print(f"\n❌ Missing required packages:")
        for pkg in missing_packages:
            print(f"   - {pkg}")
        print(f"\n💡 Install missing packages with:")
        print(f"   pip install flask flask-cors flask-jwt-extended flask-socketio python-docx eventlet python-dotenv")
        print(f"   or: pip install -r requirements.txt")
        return False
    
    if missing_optional:
        print(f"\n⚠️  Optional packages missing (for Phase 3):")
        for pkg in missing_optional:
            print(f"   - {pkg}")
        print(f"\n💡 Install Phase 3 packages with:")
        print(f"   pip install docxtpl pdf2docx jinja2 google-generativeai")
    
    print(f"\n✓ All required packages are installed")
    return True

def check_environment_variables():
    """Check if environment variables are properly set."""
    from dotenv import load_dotenv
    load_dotenv()
    
    print("\n📋 Checking environment variables...")
    
    # Check if .env file exists
    env_file = Path('.env')
    if not env_file.exists():
        print("⚠️  .env file not found. Creating from .env.example...")
        example_file = Path('.env.example')
        if example_file.exists():
            import shutil
            shutil.copy('.env.example', '.env')
            print("✓ Created .env file from .env.example")
            print("💡 Please edit .env file with your API keys")
        else:
            print("❌ .env.example file not found")
            return False
    
    # Check critical environment variables
    required_vars = ['SECRET_KEY', 'JWT_SECRET_KEY']
    optional_vars = ['OPENAI_API_KEY', 'GEMINI_API_KEY']
    
    for var in required_vars:
        value = os.getenv(var, '')
        if value and not value.startswith('your-') and not value.startswith('dev-'):
            print(f"✓ {var} - SET")
        else:
            print(f"⚠️  {var} - USING DEFAULT/PLACEHOLDER")
    
    missing_optional = []
    for var in optional_vars:
        value = os.getenv(var, '')
        if value and not value.startswith('your-') and value != 'placeholder-key':
            print(f"✓ {var} - SET")
        else:
            print(f"⚠️  {var} - NOT SET (Some features may not work)")
            missing_optional.append(var)
    
    if missing_optional:
        print(f"\n💡 To enable all features, set these variables in your .env file:")
        for var in missing_optional:
            print(f"   - {var}")
    
    return True

def main():
    """Main function to run the local development server."""
    print("🚀 Starting BIGPIAI Local Development Server")
    print("=" * 50)
    
    # Setup environment
    print("📁 Setting up environment...")
    setup_environment()
    
    # Check environment variables first
    check_environment_variables()
    
    # Check dependencies
    print("\n📦 Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    
    # Import and start the app
    print("🌐 Starting Flask development server...")
    print("📍 Server will be available at: http://localhost:5000")
    print("🔄 Auto-reload enabled for development")
    print("⚠️  Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Import Flask app without SocketIO for Python 3.13 compatibility
        import sys
        sys.path.insert(0, '.')
        
        from app import create_app
        app = create_app()
        
        # Use built-in Flask development server
        app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False)
        
    except ImportError as e:
        print(f"❌ Error importing application: {e}")
        print("💡 Make sure run.py exists and is properly configured")
        print("💡 Try installing missing dependencies: pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
