#!/usr/bin/env python3
"""
Micro-Climate Aware Personalized Health Risk Prediction & Notification System
Main application entry point
"""

import os
import sys
from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, current_user
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import configurations
from config import config

# Import database
from models.user import db, User

# Import blueprints
from routes.auth import auth_bp
from routes.profile import profile_bp
from routes.dashboard import dashboard_bp
from routes.notifications import notifications_bp

def create_app(config_name=None):
    """
    Application factory function
    Creates and configures the Flask application
    """
    
    # Create Flask app instance
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    app.config.from_object(config[config_name])
    
    # Initialize database
    db.init_app(app)
    
    # Initialize login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for Flask-Login"""
        return User.query.get(int(user_id))
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(notifications_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        print("✅ Database tables created/verified")
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors"""
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    # Home route
    @app.route('/')
    def index():
        """Landing page"""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index'))
        return render_template('index.html')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Health check for monitoring"""
        return {'status': 'healthy', 'environment': config_name}
    
    print(f"✅ Application created in {config_name} mode")
    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    # Run the application
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print("\n" + "="*50)
    print("🚀 Starting Micro-Climate Health Risk System")
    print("="*50)
    print(f"🌐 Server: http://localhost:{port}")
    print(f"🔧 Debug mode: {'ON' if debug else 'OFF'}")
    print(f"📁 Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print("="*50 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=debug)