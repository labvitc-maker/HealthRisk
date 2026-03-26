from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Create database instance (will be initialized in app.py)
db = SQLAlchemy()

class User(UserMixin, db.Model):
    """
    User model for authentication and basic information
    
    UserMixin provides default implementations for Flask-Login:
    - is_authenticated()
    - is_active()
    - is_anonymous()
    - get_id()
    """
    
    __tablename__ = 'users'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Authentication fields
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Flag for first-time login
    profile_completed = db.Column(db.Boolean, default=False)
    
    # Relationship with Profile (one-to-one)
    # cascade='all, delete-orphan' means if user is deleted, profile is also deleted
    profile = db.relationship('Profile', backref='user', uselist=False, cascade='all, delete-orphan')
    
    # Relationship with Notifications (one-to-many)
    notifications = db.relationship('Notification', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """
        Hash the password and store it
        Uses werkzeug's generate_password_hash with default settings (pbkdf2:sha256)
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """
        Verify the password against the stored hash
        Returns True if password matches
        """
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        """String representation of the User object (for debugging)"""
        return f'<User {self.email}>'