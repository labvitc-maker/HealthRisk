from models.user import db
from datetime import datetime

class Notification(db.Model):
    """
    Notification model storing risk alerts with scores
    """
    
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Notification content
    risk_type = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    risk_level = db.Column(db.String(20), nullable=False)  # 'Low', 'Moderate', 'High'
    risk_score = db.Column(db.Float, default=0)  # Numerical score 0-100
    
    is_sent = db.Column(db.Boolean, default=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Notification {self.risk_type} ({self.risk_score}/100) for User {self.user_id}>'
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'risk_type': self.risk_type,
            'message': self.message,
            'risk_level': self.risk_level,
            'risk_score': self.risk_score,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }