#!/usr/bin/env python3
"""
WSGI Entry Point for Production Deployment
This file is used by production servers like Gunicorn and Waitress.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to Python path
project_root = Path(__file__).parent
import sys
sys.path.insert(0, str(project_root))

# Create Flask application
from app import create_app

app = create_app()

if __name__ == '__main__':
    # This is for direct execution (development only)
    app.run(host='0.0.0.0', port=5000, debug=False)