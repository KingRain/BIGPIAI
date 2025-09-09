
import eventlet
eventlet.monkey_patch()

print("🔧 Starting BIGPIAI application...")

from app import create_app, socketio
print("✅ App modules imported successfully")

app = create_app()
print("✅ Flask app created successfully")

if __name__ == '__main__':
    import os
    
    # Check if running in production mode
    is_production = os.getenv('PRODUCTION', 'false').lower() == 'true'
    
    if is_production:
        print("🚀 Starting PRODUCTION SocketIO server with eventlet...")
        print("   Host: 0.0.0.0")
        print("   Port: 80")
        print("   Debug: False")
        print("=" * 50)
        
        # For production deployment with eventlet
        socketio.run(app, host='0.0.0.0', port=80, debug=False, use_reloader=False)
    else:
        print("🚀 Starting DEVELOPMENT SocketIO server...")
        print("   Host: 127.0.0.1")
        print("   Port: 5000")
        print("   Debug: True")
        print("   Access at: http://127.0.0.1:5000")
        print("=" * 50)
        
        # For local development - enable debug mode but disable reloader for testing
        socketio.run(app, host='127.0.0.1', port=5000, debug=True, use_reloader=False)

# PRODUCTION USAGE:
# Set environment variable: PRODUCTION=true
# Then run: python run.py
# 
# ALTERNATIVE: Use gunicorn with eventlet worker for production:
# gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:80 run:app
