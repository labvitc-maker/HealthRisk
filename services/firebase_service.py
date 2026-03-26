import requests
import json
from config import Config

class FirebaseService:
    """
    Simplified Firebase service using REST API with database secret
    """
    
    def __init__(self, database_url):
        self.database_url = database_url.rstrip('/')
        # For legacy token authentication, append .json to URLs
        # Example: https://your-db.firebaseio.com/path.json?auth=SECRET
    
    def get_latest_sensor_data(self, bus_stop_id='bus_stop_001'):
        """
        Fetch latest sensor data using REST API
        """
        try:
            # Construct URL with .json endpoint
            url = f"{self.database_url}/bus_stops/{bus_stop_id}.json"
            
            # Make request
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                if data:
                    return {
                        'temperature': float(data.get('temperature', 0)),
                        'humidity': float(data.get('humidity', 0)),
                        'air_quality': int(data.get('air_quality', 0)),
                        'noise': int(data.get('noise', 0)),
                        'crowd': int(data.get('crowd', 0)),
                        'distance': float(data.get('distance', 0)),
                        'timestamp': int(data.get('timestamp', 0))
                    }
            return None
            
        except Exception as e:
            print(f"Error fetching sensor data: {e}")
            return None
    
    def get_sensor_history(self, bus_stop_id='bus_stop_001', limit=10):
        """
        Get historical data - in a real implementation, you'd need to store history
        For now, we'll create simulated history based on current reading
        """
        latest = self.get_latest_sensor_data(bus_stop_id)
        
        if not latest:
            return []
        
        # Create simulated history
        history = []
        import random
        from datetime import datetime, timedelta
        
        base_time = datetime.now()
        
        for i in range(limit):
            time_point = base_time - timedelta(minutes=(limit - i) * 5)
            historical_point = {
                'temperature': latest['temperature'] + random.uniform(-2, 2),
                'humidity': latest['humidity'] + random.uniform(-5, 5),
                'air_quality': latest['air_quality'] + random.randint(-50, 50),
                'noise': latest['noise'] + random.randint(-20, 20),
                'crowd': 1 if i % 3 == 0 else 0,
                'distance': latest['distance'] + random.uniform(-5, 5),
                'timestamp': int(time_point.timestamp() * 1000)
            }
            history.append(historical_point)
        
        return history