from models.notification import Notification
from models.user import db, User
from services.risk_engine import RiskEngine
from datetime import datetime, timedelta

class NotificationService:
    """
    Service to generate and manage notifications based on risk assessments
    """
    
    def __init__(self):
        self.risk_engine = RiskEngine()
    
    def generate_notifications_for_user(self, user, sensor_data, risk_result):
        """
        Generate personalized notifications based on risk scores
        Only sends disease-specific notifications to users with that condition
        """
        created_notifications = []
        risk_factors = risk_result.get('risk_factors', {})
        
        # Track which notifications we've already created for this session
        recent_notifications = self.get_recent_notifications(user, minutes=5)
        recent_types = [n.risk_type for n in recent_notifications]
        
        print(f"\n🔍 Checking personalized risks for {user.email}")
        print(f"   Overall risk score: {risk_result['overall_score']}/100")
        
        for risk_type, risk_data in risk_factors.items():
            # Skip if risk is Low (score < 40)
            if risk_data['level'] == 'Low':
                continue
            
            # Skip if we've sent this type recently
            if risk_type in recent_types:
                print(f"   ⏭️ Skipping {risk_type} - sent recently")
                continue
            
            # Check if this risk should generate a notification for THIS user
            should_notify = False
            reason = ""
            
            # Global risks - notify ALL users
            if risk_type in ['heat_risk', 'air_quality_risk', 'stress_risk', 
                           'dehydration_risk', 'infection_risk', 'fainting_risk']:
                should_notify = True
                reason = "global health risk"
            
            # Respiratory distress - notify all (general health)
            elif risk_type == 'respiratory_distress':
                should_notify = True
                reason = "respiratory risk affects everyone"
            
            # Asthma risk - ONLY for users with asthma
            elif risk_type == 'asthma_risk' and user.profile.asthma:
                should_notify = True
                reason = "user has asthma"
            
            # Heart risk - ONLY for users with heart conditions
            elif risk_type == 'heart_risk' and user.profile.heart_risk:
                should_notify = True
                reason = "user has heart condition"
            
            # Elderly vulnerability - ONLY for elderly users
            elif risk_type == 'elderly_vulnerability' and user.profile.is_elderly:
                should_notify = True
                reason = "user is elderly"
            
            # Generate notification if needed
            if should_notify:
                score = risk_data['score']
                message = self.risk_engine.get_notification_message(
                    risk_type, risk_data['level'], score, sensor_data
                )
                
                print(f"   ✅ Creating {risk_type} notification for {reason} (score: {score}/100)")
                
                # Create and save notification
                notification = Notification(
                    user_id=user.id,
                    risk_type=risk_type,
                    risk_level=risk_data['level'],
                    risk_score=score,
                    message=message
                )
                
                db.session.add(notification)
                created_notifications.append(notification)
            else:
                print(f"   ⏭️ Skipping {risk_type} - not applicable for this user")
        
        # Commit all notifications to database
        if created_notifications:
            db.session.commit()
            print(f"   ✅ Saved {len(created_notifications)} new notifications")
        
        return created_notifications
    
    def get_user_notifications(self, user, limit=50):
        """Get notification history for a user"""
        return Notification.query.filter_by(user_id=user.id)\
            .order_by(Notification.timestamp.desc())\
            .limit(limit)\
            .all()
    
    def get_recent_notifications(self, user, minutes=5):
        """Get notifications from last X minutes"""
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        return Notification.query.filter(
            Notification.user_id == user.id,
            Notification.timestamp > cutoff
        ).all()
    
    def get_unread_count(self, user):
        """Get count of recent notifications"""
        return len(self.get_recent_notifications(user, minutes=60))