from models.user import db
from datetime import datetime

class Profile(db.Model):
    """
    User profile model containing demographic and medical information
    This is linked one-to-one with User
    """
    
    __tablename__ = 'profiles'
    
    # Primary key - also foreign key to User
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    
    # Demographic fields
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    occupation = db.Column(db.String(100), nullable=False)
    
    # Medical conditions (boolean flags)
    # These will be stored as 0 (False) or 1 (True) in database
    asthma = db.Column(db.Boolean, default=False)
    heart_risk = db.Column(db.Boolean, default=False)
    respiratory_distress = db.Column(db.Boolean, default=False)
    allergies = db.Column(db.Boolean, default=False)
    heat_sensitivity = db.Column(db.Boolean, default=False)
    diabetes = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def is_elderly(self):
        """Property that returns True if age >= 60"""
        from config import Config
        return self.age >= Config.ELDERLY_AGE_THRESHOLD
    
    def get_medical_conditions_list(self):
        """
        Returns a list of active medical conditions
        Useful for display and risk calculation
        """
        conditions = []
        if self.asthma:
            conditions.append('asthma')
        if self.heart_risk:
            conditions.append('heart_risk')
        if self.respiratory_distress:
            conditions.append('respiratory_distress')
        if self.allergies:
            conditions.append('allergies')
        if self.heat_sensitivity:
            conditions.append('heat_sensitivity')
        if self.diabetes:
            conditions.append('diabetes')
        return conditions
    
    def __repr__(self):
        return f'<Profile for User {self.id}: {self.name}>'