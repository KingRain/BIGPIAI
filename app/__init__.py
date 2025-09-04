from flask import Flask, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .routes.upload_phase2 import upload_phase2
from .routes.upload_phase1 import upload_phase1
from .routes.home import home
from .routes.login import login
from .routes.logout import logout
from .routes.phase3 import phase3_bp

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_app():
    """Create Flask app for Python 3.13 compatibility."""
    app = Flask(__name__)
    
    CORS(app, supports_credentials=True)

    # Set secret keys
    app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-string-change-in-production')
    
    # JWT configuration
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config['JWT_COOKIE_SECURE'] = False
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False
    jwt = JWTManager(app)

    # Register routes
    app.add_url_rule('/', view_func=home)
    app.add_url_rule('/upload-phase1', view_func=upload_phase1, methods=['POST'])
    app.add_url_rule('/upload-phase2', view_func=upload_phase2, methods=['POST'])
    app.add_url_rule('/login', view_func=login, methods=['GET', 'POST'])
    app.add_url_rule('/logout', view_func=logout)
    
    # Register Phase 3 blueprint
    app.register_blueprint(phase3_bp)

    return app

