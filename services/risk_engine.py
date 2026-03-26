"""
Advanced Risk Computation Engine
Implements scientific formulas for environmental health risk assessment
Based on CDC, NOAA, and clinical guidance
"""

import math
from config import Config

class RiskEngine:
    """
    Advanced risk computation engine using validated formulas
    Calculates 0-100 risk scores for various health conditions
    """
    
    def __init__(self, use_ml=False):
        """
        Initialize risk engine
        
        Args:
            use_ml: If True, use ML model (scaffolded for future)
        """
        self.use_ml = use_ml
        
        # Heat Index constants (Rothfusz regression)
        self.HI_CONSTANTS = {
            'c1': -42.379,
            'c2': 2.04901523,
            'c3': 10.14333127,
            'c4': -0.22475541,
            'c5': -0.00683783,
            'c6': -0.05481717,
            'c7': 0.00122874,
            'c8': 0.00085282,
            'c9': -0.00000199
        }
        
        # Risk thresholds
        self.HI_THRESHOLD_C = 30  # Comfort zone limit in °C
        self.HI_MAX_C = 55  # Extreme risk in °C
        self.AQI_MAX = 500  # Maximum AQI value
        
        # Age factors for different demographics
        self.AGE_FACTORS = {
            'child': 1.2,      # Children more vulnerable
            'adult': 1.0,       # Baseline
            'elderly': 1.8,     # Elderly much more vulnerable
            'pregnant': 1.5     # Pregnant women more vulnerable
        }
        
        # If using ML, load model here
        if self.use_ml:
            self.load_ml_model()
    
    def load_ml_model(self):
        """Load pre-trained ML model (scaffold)"""
        print("ML mode enabled - model loading scaffold")
        pass
    
    def celsius_to_fahrenheit(self, temp_c):
        """Convert Celsius to Fahrenheit"""
        return (temp_c * 9/5) + 32
    
    def fahrenheit_to_celsius(self, temp_f):
        """Convert Fahrenheit to Celsius"""
        return (temp_f - 32) * 5/9
    
    def calculate_heat_index(self, temperature_c, humidity):
        """
        Calculate Heat Index using Rothfusz regression formula
        
        Args:
            temperature_c: Temperature in Celsius
            humidity: Relative humidity (0-100%)
        
        Returns:
            Heat Index in Celsius
        """
        # Convert to Fahrenheit for formula
        T = self.celsius_to_fahrenheit(temperature_c)
        RH = humidity
        
        # Rothfusz regression formula
        HI_F = (
            self.HI_CONSTANTS['c1'] +
            self.HI_CONSTANTS['c2'] * T +
            self.HI_CONSTANTS['c3'] * RH +
            self.HI_CONSTANTS['c4'] * T * RH +
            self.HI_CONSTANTS['c5'] * T * T +
            self.HI_CONSTANTS['c6'] * RH * RH +
            self.HI_CONSTANTS['c7'] * T * T * RH +
            self.HI_CONSTANTS['c8'] * T * RH * RH +
            self.HI_CONSTANTS['c9'] * T * T * RH * RH
        )
        
        # Apply adjustments if needed
        if RH < 13 and 80 < T < 112:
            adjustment = ((13 - RH) / 4) * math.sqrt((17 - abs(T - 95)) / 17)
            HI_F -= adjustment
        elif RH > 85 and 80 < T < 87:
            adjustment = ((RH - 85) / 10) * ((87 - T) / 5)
            HI_F += adjustment
        
        # Convert back to Celsius
        HI_C = self.fahrenheit_to_celsius(HI_F)
        
        # Ensure HI is at least the actual temperature
        return max(HI_C, temperature_c)
    
    def calculate_heat_risk_score(self, temperature_c, humidity):
        """
        Calculate Heat Risk Score (HRS) 0-100
        
        Formula: HRS = min(100, ((HI - HI_threshold) / (HI_max - HI_threshold)) * 100)
        """
        # Calculate Heat Index
        hi = self.calculate_heat_index(temperature_c, humidity)
        
        # Calculate HRS
        if hi <= self.HI_THRESHOLD_C:
            hrs = 0
        elif hi >= self.HI_MAX_C:
            hrs = 100
        else:
            hrs = ((hi - self.HI_THRESHOLD_C) / (self.HI_MAX_C - self.HI_THRESHOLD_C)) * 100
        
        return round(min(100, max(0, hrs)), 2)
    
    def calculate_air_quality_risk_score(self, air_quality_raw):
        """
        Calculate Air Quality Risk Score (AQRS) 0-100
        
        Maps raw sensor value to AQI-like scale
        Note: MQ135 raw values need calibration - this is a simplified mapping
        """
        # Simple mapping of raw value to 0-500 scale (adjust based on your sensor calibration)
        # Typical MQ135 clean air ~350-400, polluted >800
        if air_quality_raw <= 400:
            aqi = air_quality_raw * 0.5  # Good range
        elif air_quality_raw <= 600:
            aqi = 100 + (air_quality_raw - 400) * 0.5  # Moderate
        elif air_quality_raw <= 800:
            aqi = 200 + (air_quality_raw - 600) * 0.5  # Unhealthy for sensitive
        elif air_quality_raw <= 1000:
            aqi = 300 + (air_quality_raw - 800) * 0.25  # Unhealthy
        else:
            aqi = 400 + (air_quality_raw - 1000) * 0.2  # Hazardous
        
        # Convert to 0-100 score
        aqrs = (aqi / self.AQI_MAX) * 100
        return round(min(100, max(0, aqrs)), 2)
    
    def calculate_respiratory_distress_risk(self, aqrs, hrs, crowd):
        """
        Calculate Respiratory Distress Risk (RDR) 0-100
        
        RDR = 0.5 × AQRS + 0.3 × HRS + 0.2 × CrowdIndex
        """
        crowd_index = 100 if crowd == 1 else 0  # Convert binary to percentage
        
        rdr = (0.5 * aqrs) + (0.3 * hrs) + (0.2 * crowd_index)
        return round(min(100, max(0, rdr)), 2)
    
    def calculate_asthma_risk_score(self, aqrs, hrs, noise):
        """
        Calculate Asthma Risk Score (ARS) 0-100
        
        ARS = 0.7 × AQRS + 0.2 × HRS + 0.1 × NoiseLevel
        """
        # Normalize noise to 0-100 scale (adjust based on your sensor)
        noise_normalized = min(100, (noise / 1024) * 100)
        
        ars = (0.7 * aqrs) + (0.2 * hrs) + (0.1 * noise_normalized)
        return round(min(100, max(0, ars)), 2)
    
    def calculate_dehydration_risk_score(self, hrs, age, is_elderly=False, is_pregnant=False):
        """
        Calculate Dehydration Risk Score (DRS) 0-100
        
        DRS = HRS × (1 + AgeFactor/10)
        """
        # Determine age factor
        if is_elderly or age >= 60:
            age_factor = self.AGE_FACTORS['elderly']
        elif is_pregnant:
            age_factor = self.AGE_FACTORS['pregnant']
        elif age < 18:
            age_factor = self.AGE_FACTORS['child']
        else:
            age_factor = self.AGE_FACTORS['adult']
        
        drs = hrs * (1 + (age_factor - 1) / 2)  # Scale factor appropriately
        return round(min(100, max(0, drs)), 2)
    
    def calculate_heart_risk_score(self, hrs, aqrs, noise):
        """
        Calculate Heart Risk Score (HRS2) 0-100
        
        HeartRisk = 0.4 × HRS + 0.4 × AQRS + 0.2 × NoiseLevel
        """
        noise_normalized = min(100, (noise / 1024) * 100)
        
        heart_risk = (0.4 * hrs) + (0.4 * aqrs) + (0.2 * noise_normalized)
        return round(min(100, max(0, heart_risk)), 2)
    
    def calculate_stress_risk_score(self, noise, hrs, crowd):
        """
        Calculate Stress Risk Score (SRS) 0-100
        
        SRS = 0.5 × NoiseLevel + 0.3 × HRS + 0.2 × CrowdIndex
        """
        noise_normalized = min(100, (noise / 1024) * 100)
        crowd_index = 100 if crowd == 1 else 0
        
        srs = (0.5 * noise_normalized) + (0.3 * hrs) + (0.2 * crowd_index)
        return round(min(100, max(0, srs)), 2)
    
    def calculate_infection_spread_risk(self, crowd, aqrs, hrs):
        """
        Calculate Infection Spread Risk Score (ISRS) 0-100
        
        ISRS = 0.6 × CrowdIndex + 0.3 × (1 - AQRS/100) + 0.1 × HRS
        """
        crowd_index = 100 if crowd == 1 else 0
        air_quality_benefit = (1 - aqrs/100) * 100  # Poor air quality increases risk
        
        isrs = (0.6 * crowd_index) + (0.3 * air_quality_benefit) + (0.1 * hrs)
        return round(min(100, max(0, isrs)), 2)
    
    def calculate_fainting_risk_score(self, hrs, drs):
        """
        Calculate Fainting Risk Score (FRS) 0-100
        
        FRS = 0.6 × HRS + 0.4 × DRS
        """
        frs = (0.6 * hrs) + (0.4 * drs)
        return round(min(100, max(0, frs)), 2)
    
    def calculate_elderly_vulnerability_score(self, hrs, aqrs, crowd):
        """
        Calculate Elderly Vulnerability Score (EVS) 0-100
        
        EVS = 0.4 × HRS + 0.4 × AQRS + 0.2 × CrowdIndex
        """
        crowd_index = 100 if crowd == 1 else 0
        
        evs = (0.4 * hrs) + (0.4 * aqrs) + (0.2 * crowd_index)
        return round(min(100, max(0, evs)), 2)
    
    def get_risk_level(self, score):
        """
        Convert numerical score (0-100) to risk level
        """
        if score >= 70:
            return 'High'
        elif score >= 40:
            return 'Moderate'
        else:
            return 'Low'
    
    def compute_all_risks(self, sensor_data, user_profile):
        """
        Compute all risk scores based on sensor data and user profile
        
        Returns dictionary with all risk scores and levels
        """
        # Extract sensor data
        temp = sensor_data.get('temperature', 25)
        humidity = sensor_data.get('humidity', 50)
        air_quality = sensor_data.get('air_quality', 400)
        noise = sensor_data.get('noise', 300)
        crowd = sensor_data.get('crowd', 0)
        
        # Calculate base scores
        hrs = self.calculate_heat_risk_score(temp, humidity)
        aqrs = self.calculate_air_quality_risk_score(air_quality)
        
        # Calculate all risk scores
        risks = {
            # Base environmental risks
            'heat_risk': {
                'score': hrs,
                'level': self.get_risk_level(hrs)
            },
            'air_quality_risk': {
                'score': aqrs,
                'level': self.get_risk_level(aqrs)
            },
            
            # Derived risks (always calculated)
            'respiratory_distress': {
                'score': self.calculate_respiratory_distress_risk(aqrs, hrs, crowd),
                'level': None  # Will set level after calculation
            },
            'stress_risk': {
                'score': self.calculate_stress_risk_score(noise, hrs, crowd),
                'level': None
            },
            'dehydration_risk': {
                'score': self.calculate_dehydration_risk_score(hrs, user_profile.age, 
                                                              user_profile.is_elderly),
                'level': None
            },
            'infection_risk': {
                'score': self.calculate_infection_spread_risk(crowd, aqrs, hrs),
                'level': None
            },
            'fainting_risk': {
                'score': None,  # Will calculate after dehydration
                'level': None
            },
            
            # Disease-specific risks (only relevant for users with conditions)
            'asthma_risk': {
                'score': self.calculate_asthma_risk_score(aqrs, hrs, noise) if user_profile.asthma else 0,
                'level': None,
                'active': user_profile.asthma
            },
            'heart_risk': {
                'score': self.calculate_heart_risk_score(hrs, aqrs, noise) if user_profile.heart_risk else 0,
                'level': None,
                'active': user_profile.heart_risk
            },
            
            # Elderly specific
            'elderly_vulnerability': {
                'score': self.calculate_elderly_vulnerability_score(hrs, aqrs, crowd) if user_profile.is_elderly else 0,
                'level': None,
                'active': user_profile.is_elderly
            }
        }
        
        # Calculate fainting risk (depends on dehydration)
        dehydration_score = risks['dehydration_risk']['score']
        risks['fainting_risk']['score'] = self.calculate_fainting_risk_score(hrs, dehydration_score)
        
        # Set levels for all risks
        for risk_name, risk_data in risks.items():
            if 'score' in risk_data and risk_data['score'] is not None:
                risk_data['level'] = self.get_risk_level(risk_data['score'])
        
        # Calculate composite overall risk (weighted average of active risks)
        overall_score = self.calculate_composite_risk(risks, user_profile)
        
        return {
            'overall_risk': self.get_risk_level(overall_score),
            'overall_score': overall_score,
            'risk_factors': risks,
            'sensor_data': sensor_data
        }
    
    def calculate_composite_risk(self, risks, user_profile):
        """
        Calculate personalized composite risk score
        Weights are adjusted based on user's medical conditions
        """
        weights = {
            'heat_risk': 0.15,
            'air_quality_risk': 0.15,
            'respiratory_distress': 0.1,
            'stress_risk': 0.1,
            'dehydration_risk': 0.1,
            'infection_risk': 0.1,
            'fainting_risk': 0.1
        }
        
        # Adjust weights based on user conditions
        if user_profile.asthma or user_profile.respiratory_distress:
            weights['air_quality_risk'] += 0.1
            weights['respiratory_distress'] += 0.1
        
        if user_profile.heart_risk:
            weights['heat_risk'] += 0.1
            weights['stress_risk'] += 0.1
        
        if user_profile.is_elderly:
            weights['dehydration_risk'] += 0.1
            weights['fainting_risk'] += 0.1
        
        if user_profile.heat_sensitivity:
            weights['heat_risk'] += 0.15
        
        # Normalize weights to sum to 1
        total_weight = sum(weights.values())
        for key in weights:
            weights[key] /= total_weight
        
        # Calculate weighted average
        composite_score = 0
        for risk_name, weight in weights.items():
            if risk_name in risks:
                composite_score += risks[risk_name]['score'] * weight
        
        return round(composite_score, 2)
    
    def get_notification_message(self, risk_type, risk_level, score, sensor_data):
        """
        Generate personalized notification message based on risk type and level
        """
        temp = sensor_data.get('temperature', 0)
        aq = sensor_data.get('air_quality', 0)
        
        messages = {
            'heat_risk': {
                'High': f"🔥 CRITICAL HEAT RISK ({score}/100): Temperature {temp}°C with high humidity. Risk of heat exhaustion! Stay indoors, hydrate frequently.",
                'Moderate': f"⚠️ ELEVATED HEAT RISK ({score}/100): Temperature {temp}°C. Take breaks in shade, drink water.",
                'Low': f"✅ Low heat risk ({score}/100): Conditions are comfortable."
            },
            'air_quality_risk': {
                'High': f"😮‍💨 CRITICAL AIR QUALITY ({score}/100): AQI equivalent {aq}. Severe respiratory risk! Wear N95 mask, avoid outdoors.",
                'Moderate': f"🌫️ MODERATE AIR QUALITY RISK ({score}/100): Air quality is reduced. Limit exertion, keep medication handy.",
                'Low': f"✅ Good air quality ({score}/100): Safe for outdoor activities."
            },
            'respiratory_distress': {
                'High': f"⚠️ SEVERE RESPIRATORY DISTRESS RISK ({score}/100): Poor air quality and heat. Use inhaler if prescribed, seek cool clean air.",
                'Moderate': f"🌬️ ELEVATED RESPIRATORY RISK ({score}/100): Monitor breathing, avoid strenuous activity.",
                'Low': f"✅ Low respiratory risk ({score}/100): Breathing conditions are favorable."
            },
            'asthma_risk': {
                'High': f"🫁 ASTHMA ALERT ({score}/100): High trigger levels detected! Keep inhaler ready, avoid outdoor exposure.",
                'Moderate': f"💨 Asthma triggers elevated ({score}/100): Take precautions, consider wearing mask.",
                'Low': f"✅ Asthma conditions stable ({score}/100)."
            },
            'heart_risk': {
                'High': f"❤️ CARDIAC ALERT ({score}/100): Extreme environmental stress on heart! Rest, avoid heat, keep medications accessible.",
                'Moderate': f"💓 Elevated cardiac risk ({score}/100): Monitor heart rate, stay cool.",
                'Low': f"✅ Low cardiac stress ({score}/100)."
            },
            'dehydration_risk': {
                'High': f"💧 SEVERE DEHYDRATION RISK ({score}/100): Drink water immediately! Avoid caffeine, find cool area.",
                'Moderate': f"🥤 Moderate dehydration risk ({score}/100): Increase fluid intake.",
                'Low': f"✅ Hydration levels safe ({score}/100)."
            },
            'stress_risk': {
                'High': f"😰 HIGH STRESS LOAD ({score}/100): High noise, heat, and crowding. Find quiet space, practice deep breathing.",
                'Moderate': f"😐 Elevated stress ({score}/100): Take breaks, use calming techniques.",
                'Low': f"😌 Low environmental stress ({score}/100)."
            },
            'infection_risk': {
                'High': f"🦠 HIGH INFECTION RISK ({score}/100): Crowded with poor air quality! Wear mask, maintain distance.",
                'Moderate': f"😷 Moderate infection risk ({score}/100): Consider mask in crowds.",
                'Low': f"✅ Low infection spread risk ({score}/100)."
            },
            'fainting_risk': {
                'High': f"⚡ FAINTING RISK CRITICAL ({score}/100): Heat and dehydration severe! Sit down immediately, find cool shade.",
                'Moderate': f"🌀 Elevated fainting risk ({score}/100): Be cautious, don't stand for long.",
                'Low': f"✅ Low fainting risk ({score}/100)."
            },
            'elderly_vulnerability': {
                'High': f"👴 ELDERLY HIGH RISK ({score}/100): Extreme conditions! Please stay indoors, check on elderly neighbors.",
                'Moderate': f"👵 Elderly moderate risk ({score}/100): Take breaks, stay hydrated.",
                'Low': f"✅ Safe conditions for elderly ({score}/100)."
            }
        }
        
        # Get message for this risk type, or return default
        risk_messages = messages.get(risk_type, {})
        return risk_messages.get(risk_level, f"{risk_type.replace('_', ' ').title()}: {risk_level} risk ({score}/100)")

def compute_risk(self, sensor_data, user_profile):
    """
    Backward compatibility method - calls compute_all_risks
    """
    print("⚠️ Warning: compute_risk() is deprecated, use compute_all_risks() instead")
    return self.compute_all_risks(sensor_data, user_profile)