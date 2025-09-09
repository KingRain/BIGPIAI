from flask import Flask, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager  # Import JWTManager
from .routes.upload_phase2 import upload_phase2
from .routes.upload_phase1 import upload_phase1
from .routes.home import home  # Import your home route
from .routes.login import login  # Import your login route
from .routes.logout import logout  # Import your logout route
from flask_socketio import SocketIO
from .routes.socket_manager import createSocketManager
import os
from dotenv import load_dotenv

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure SocketIO based on environment
is_production = os.getenv('PRODUCTION', 'false').lower() == 'true'
use_waitress = os.getenv('USE_WAITRESS', 'false').lower() == 'true'

if use_waitress:
    # For Waitress deployment - use threading mode
    socketio = SocketIO(async_mode='threading', 
                        ping_interval=60000,   
                        ping_timeout=60000,   
                        cors_allowed_origins="*")
else:
    # For eventlet deployment (recommended)
    socketio = SocketIO(async_mode='eventlet', 
                        ping_interval=60000,   
                        ping_timeout=60000,   
                        cors_allowed_origins="*")

def create_app():
    app = Flask(__name__)
    
    CORS(app, supports_credentials=True)  # Enable CORS for all routes

    # Add these two lines to set the secret keys
    # Required for sessions/flash messages
    app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    # For JWT tokens
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')

    # Other JWT configurations
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config['JWT_COOKIE_SECURE'] = False
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False  # For simplicity
    JWTManager(app)  # Initialize JWTManager with your app

    # Register routes
    app.add_url_rule('/', view_func=home)  # Add the home route
    app.add_url_rule('/upload-phase1', view_func=upload_phase1,
                     methods=['POST'])  # Add the upload route
    app.add_url_rule('/upload-phase2', view_func=upload_phase2,
                     methods=['POST'])  # Add the upload route
    app.add_url_rule('/login', view_func=login,
                     methods=['GET', 'POST'])  # Add the login route
    app.add_url_rule('/logout', view_func=logout)  # Add the logout route

    createSocketManager(socketio=socketio)
    socketio.init_app(app)
    return app

