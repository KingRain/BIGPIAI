#!/usr/bin/env python3
"""
Production Server Runner
Run this script to start the Flask application in production mode.
"""
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def setup_production_environment():
    """Set up environment variables for production."""
    # Load production environment file first
    from dotenv import load_dotenv
    
    # Try to load .env.production first, then fall back to .env
    env_files = ['.env.production', '.env']
    env_loaded = False
    
    for env_file in env_files:
        if Path(env_file).exists():
            load_dotenv(env_file, override=True)
            print(f"✓ Loaded environment from: {env_file}")
            env_loaded = True
            break
    
    if not env_loaded:
        print("⚠️  No environment file found, using defaults")
    
    # Set production defaults
    os.environ.setdefault('FLASK_APP', 'run.py')
    os.environ.setdefault('FLASK_ENV', 'production')
    os.environ.setdefault('FLASK_DEBUG', '0')
    os.environ.setdefault('PRODUCTION', 'true')
    os.environ.setdefault('USE_WAITRESS', 'true')
    
    # Windows VM specific defaults
    os.environ.setdefault('HOST', '0.0.0.0')
    os.environ.setdefault('PORT', '80')
    os.environ.setdefault('WORKERS', '4')
    
    # Create necessary directories
    directories = [
        'uploads/phase1',
        'uploads/phase2', 
        'uploads/phase3',
        'outputs/phase1',
        'outputs/phase2',
        'outputs/phase3',
        'instance',
        'logs'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def check_production_dependencies():
    """Check if production dependencies are installed."""
    required_packages = [
        ('flask', 'Flask'),
        ('flask_cors', 'CORS'),
        ('flask_jwt_extended', 'JWTManager'),
        ('docx', 'Document'),
        ('dotenv', 'load_dotenv'),
        ('waitress', 'serve'),
        ('gunicorn', None)
    ]
    
    optional_packages = [
        ('docxtpl', 'DocxTemplate'),
        ('pdf2docx', 'Converter'),
        ('jinja2', 'Environment'),
        ('google.generativeai', None),
        ('openai', 'OpenAI')
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
            print(f"⚠️  {package} - MISSING (Some features may not work)")
            missing_optional.append(package)
        except AttributeError:
            if attr:
                print(f"⚠️  {package}.{attr} - MISSING ATTRIBUTE (Some features may not work)")
                missing_optional.append(package)
            else:
                print(f"✓ {package} - OK")
    
    if missing_packages:
        print(f"\n❌ Missing required packages:")
        for pkg in missing_packages:
            print(f"   - {pkg}")
        print(f"\n💡 Install missing packages with:")
        print(f"   pip install flask flask-cors flask-jwt-extended python-docx python-dotenv waitress gunicorn")
        print(f"   or: pip install -r requirements.txt")
        return False
    
    if missing_optional:
        print(f"\n⚠️  Optional packages missing:")
        for pkg in missing_optional:
            print(f"   - {pkg}")
        print(f"\n💡 Install optional packages with:")
        print(f"   pip install docxtpl pdf2docx jinja2 google-generativeai openai")
    
    print(f"\n✓ All required packages are installed")
    return True

def check_environment_variables():
    """Check if required environment variables are set."""
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = [
        'SECRET_KEY',
        'JWT_SECRET_KEY'
    ]
    
    recommended_vars = [
        'OPENAI_API_KEY',
        'GEMINI_API_KEY'
    ]
    
    missing_required = []
    missing_recommended = []
    
    print("\n📋 Checking environment variables...")
    
    for var in required_vars:
        if os.getenv(var):
            print(f"✓ {var} - SET")
        else:
            print(f"❌ {var} - NOT SET")
            missing_required.append(var)
    
    for var in recommended_vars:
        if os.getenv(var):
            print(f"✓ {var} - SET")
        else:
            print(f"⚠️  {var} - NOT SET (Some features may not work)")
            missing_recommended.append(var)
    
    if missing_required:
        print(f"\n❌ Missing required environment variables:")
        for var in missing_required:
            print(f"   - {var}")
        print(f"\n💡 Please set these variables in your .env file")
        return False
    
    if missing_recommended:
        print(f"\n⚠️  Missing recommended environment variables:")
        for var in missing_recommended:
            print(f"   - {var}")
        print(f"\n💡 Set these variables in your .env file for full functionality")
    
    return True

def get_server_config():
    """Get server configuration from environment variables."""
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', '5000'))
    workers = int(os.getenv('WORKERS', '4'))
    
    return host, port, workers

def run_with_waitress(app, host, port):
    """Run the application with Waitress server."""
    try:
        from waitress import serve
        print(f"🚀 Starting Waitress production server...")
        print(f"📍 Server will be available at: http://{host}:{port}")
        if port == 80:
            print(f"🌐 External access: http://4.147.177.22")
        else:
            print(f"🌐 External access: http://4.147.177.22:{port}")
        print(f"🔒 Production mode enabled")
        print(f"⚠️  Press Ctrl+C to stop the server")
        print("=" * 50)
        
        serve(app, host=host, port=port, threads=6)
        
    except ImportError:
        print("❌ Waitress not installed. Install with: pip install waitress")
        return False
    except PermissionError:
        print(f"❌ Permission denied to bind to port {port}")
        if port == 80:
            print("💡 Port 80 requires administrator privileges on Windows")
            print("💡 Try running as administrator or use a different port (e.g., 8080)")
        return False
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {port} is already in use")
            print("💡 Try stopping other services or use a different port")
        else:
            print(f"❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error starting Waitress server: {e}")
        return False
    
    return True

def run_with_gunicorn(host, port, workers):
    """Run the application with Gunicorn server."""
    try:
        import subprocess
        import shutil
        
        # Check if gunicorn is available
        if not shutil.which('gunicorn'):
            print("❌ Gunicorn not found. Install with: pip install gunicorn")
            return False
        
        print(f"🚀 Starting Gunicorn production server...")
        print(f"📍 Server will be available at: http://{host}:{port}")
        print(f"👥 Workers: {workers}")
        print(f"🔒 Production mode enabled")
        print(f"⚠️  Press Ctrl+C to stop the server")
        print("=" * 50)
        
        # Gunicorn command
        cmd = [
            'gunicorn',
            '--bind', f'{host}:{port}',
            '--workers', str(workers),
            '--worker-class', 'sync',
            '--timeout', '120',
            '--keep-alive', '5',
            '--max-requests', '1000',
            '--max-requests-jitter', '100',
            '--preload',
            '--access-logfile', '-',  # Log to stdout
            '--error-logfile', '-',   # Log to stderr
            'run:app'
        ]
        
        # Run Gunicorn
        subprocess.run(cmd, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Gunicorn exited with error code: {e.returncode}")
        return False
    except FileNotFoundError:
        print("❌ Gunicorn not installed. Install with: pip install gunicorn")
        return False
    except KeyboardInterrupt:
        print("\n👋 Gunicorn server stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error starting Gunicorn server: {e}")
        return False
    
    return True

def main():
    """Main function to run the production server."""
    print("🚀 Starting BIGPIAI Production Server")
    print("=" * 50)
    
    # Setup environment
    print("📁 Setting up production environment...")
    setup_production_environment()
    
    # Check dependencies
    print("\n📦 Checking dependencies...")
    if not check_production_dependencies():
        sys.exit(1)
    
    # Check environment variables
    if not check_environment_variables():
        sys.exit(1)
    
    # Get server configuration
    host, port, workers = get_server_config()
    
    # Import and create the app
    print("\n🌐 Starting production server...")
    try:
        from app import create_app
        app = create_app()
        
        # Choose server based on USE_WAITRESS environment variable
        use_waitress = os.getenv('USE_WAITRESS', 'true').lower() == 'true'
        
        if use_waitress:
            success = run_with_waitress(app, host, port)
        else:
            success = run_with_gunicorn(host, port, workers)
        
        if not success:
            print("\n💡 Trying alternative server...")
            if use_waitress:
                success = run_with_gunicorn(host, port, workers)
            else:
                success = run_with_waitress(app, host, port)
        
        if not success:
            print("\n❌ Failed to start production server with both Waitress and Gunicorn")
            print("💡 Try installing production dependencies: pip install waitress gunicorn")
            sys.exit(1)
        
    except ImportError as e:
        print(f"❌ Error importing application: {e}")
        print("💡 Make sure all dependencies are installed: pip install -r requirements.txt")
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