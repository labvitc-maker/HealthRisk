import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class"""
    
    # Secret key for session security - CHANGE THIS IN PRODUCTION!
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database configuration
    # SQLite database file path
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{os.path.join(BASE_DIR, "database", "app.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Firebase configuration
    FIREBASE_DATABASE_URL = os.environ.get('FIREBASE_DATABASE_URL') or \
        'https://microclimate-health-risk-default-rtdb.firebaseio.com/'
    
    # Application settings
    DEBUG = os.environ.get('FLASK_DEBUG') or False
    
    # Risk calculation settings
    TEMP_HIGH_THRESHOLD = 35  # °C
    TEMP_MODERATE_THRESHOLD = 30  # °C
    HUMIDITY_HIGH_THRESHOLD = 80  # %
    AIR_QUALITY_BAD_THRESHOLD = 800  # MQ135 raw value
    NOISE_HIGH_THRESHOLD = 500  # raw value
    ELDERLY_AGE_THRESHOLD = 60  # years

class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    # In production, always use environment variables for secrets
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # For production, you might want to use PostgreSQL instead of SQLite
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

# Choose configuration based on environment
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}