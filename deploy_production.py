#!/usr/bin/env python3
"""
Production deployment script for BIGPIAI
Provides multiple deployment options for production environment
"""

import os
import sys
import subprocess

def run_with_eventlet():
    """Run with eventlet server (recommended for SocketIO)"""
    print("🚀 Starting production server with eventlet...")
    os.environ['PRODUCTION'] = 'true'
    os.environ['USE_WAITRESS'] = 'false'
    
    try:
        subprocess.run([sys.executable, 'run.py'], check=True)
    except KeyboardInterrupt:
        print("\n✅ Server stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")

def run_with_gunicorn():
    """Run with gunicorn and eventlet worker"""
    print("🚀 Starting production server with gunicorn + eventlet...")
    
    try:
        cmd = [
            'gunicorn',
            '--worker-class', 'eventlet',
            '-w', '1',  # Use 1 worker for SocketIO
            '--bind', '0.0.0.0:80',
            '--timeout', '120',
            '--keep-alive', '2',
            'run:app'
        ]
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n✅ Server stopped by user")
    except FileNotFoundError:
        print("❌ Gunicorn not found. Install with: pip install gunicorn")
    except Exception as e:
        print(f"❌ Error: {e}")

def run_with_waitress():
    """Run with waitress (requires threading mode for SocketIO)"""
    print("🚀 Starting production server with waitress...")
    os.environ['PRODUCTION'] = 'true'
    os.environ['USE_WAITRESS'] = 'true'
    
    try:
        cmd = [
            'waitress-serve',
            '--listen=0.0.0.0:80',
            '--threads=10',
            '--connection-limit=1000',
            'run:app'
        ]
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n✅ Server stopped by user")
    except FileNotFoundError:
        print("❌ Waitress not found. Install with: pip install waitress")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main deployment function"""
    print("BIGPIAI Production Deployment")
    print("=" * 40)
    print("Choose deployment method:")
    print("1. Eventlet server (recommended for SocketIO)")
    print("2. Gunicorn with eventlet worker (production grade)")
    print("3. Waitress with threading mode")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == '1':
        run_with_eventlet()
    elif choice == '2':
        run_with_gunicorn()
    elif choice == '3':
        run_with_waitress()
    elif choice == '4':
        print("👋 Goodbye!")
        sys.exit(0)
    else:
        print("❌ Invalid choice. Please try again.")
        main()

if __name__ == '__main__':
    main()
