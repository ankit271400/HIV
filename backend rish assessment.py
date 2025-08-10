
```python
from typing import List, Dict, Any, Optional
import json
from datetime import datetime, timedelta

class RiskCalculator:
    """Advanced HIV risk assessment calculator with thermal integration"""
    
    def __init__(self):
        self.base_weights = {
            'age': {
                '18-25': 10,
                '26-35': 15,
                '36-45': 12,
                '46-55': 8,
                '55+': 5
            },
            'exposure': {
                'unprotected_sex': 30,
                'needle_sharing': 50,
                'blood_contact': 40,
                'protected_sex': 5,
                'no_exposure': 0
            },
            'timeframe': {
                '0-72h': 20,
                '3-7days': 15,
                '1-2weeks': 12,
                '2-4weeks': 10,
                'over_month': 5
            },
            'symptoms': {
                'fever': 25,
                'fatigue': 15,
                'rash': 20,
                'swollen_lymph': 18,
                'night_sweats': 16,
                'muscle_aches': 12,
                'sore_throat': 10
            },
            'thermal': {
                'high_fever': 30,
                'moderate_fever': 20,
                'normal_temp': 0
            }
        }

def calculate_risk_score(
    age: str,
    exposure_history: str,
    symptoms: List[str],
    timeframe: str,
    risk_factors: List[str],
    thermal_data: Optional[Dict[str, Any]] = None
) -> int:
    """Calculate comprehensive HIV risk score including thermal analysis"""
    
    calculator = RiskCalculator()
    score = 0
    
    # Age factor
    score += calculator.base_weights['age'].get(age, 0)
    
    # Exposure type
    score += calculator.base_weights['exposure'].get(exposure_history, 0)
    
    # Timeframe factor
    score += calculator.base_weights['timeframe'].get(timeframe, 0)
    
    # Symptoms
    for symptom in symptoms:
        score += calculator.base_weights['symptoms'].get(symptom, 0)
    
    # Additional risk factors
    for factor in risk_factors:
        if factor == 'multiple_partners':
            score += 15
        elif factor == 'drug_use':
            score += 20
        elif factor == 'previous_sti':
            score += 12
        elif factor == 'immunocompromised':
            score += 25
    
    # Thermal analysis integration
    if thermal_data:
        thermal_score = calculate_thermal_risk_score(thermal_data)
        score += thermal_score
    
    # Cap the score at 100
    return min(score, 100)

def calculate_thermal_risk_score(thermal_data: Dict[str, Any]) -> int:
    """Calculate risk score contribution from thermal analysis"""
    score = 0
    
    if thermal_data.get('fever_detected'):
        fever_severity = thermal_data.get('fever_severity', 'none')
        max_temp = thermal_data.get('max_temperature', 0)
        
        if fever_severity == 'high' or max_temp > 38.5:
            score += 30
        elif fever_severity == 'moderate' or max_temp > 37.5:
            score += 20
        
        # Additional factors
        hotspot_count = thermal_data.get('hotspot_count', 0)
        if hotspot_count > 3:
            score += 5
        
        confidence = thermal_data.get('confidence_score', 0)
        if confidence < 0.7:
            score = int(score * 0.8)  # Reduce score if low confidence
    
    return score

def generate_recommendations(
    risk_level: str, 
    timeframe: str, 
    symptoms: List[str],
    thermal_data: Optional[Dict[str, Any]] = None
) -> List[str]:
    """Generate personalized recommendations based on assessment"""
    
    recommendations = []
    
    # Base recommendations by risk level
    if risk_level == "low":
        recommendations.extend([
            "Continue practicing safe sexual behaviors",
            "Consider regular HIV testing if sexually active",
            "Learn about PrEP (pre-exposure prophylaxis) if at ongoing risk",
            "Maintain overall good health practices"
        ])
    elif risk_level == "moderate":
        recommendations.extend([
            "Get tested for HIV as soon as possible",
            "Consider speaking with a healthcare provider about your exposure",
            "Review and improve risk reduction strategies",
            "Consider PEP (post-exposure prophylaxis) if within 72 hours of exposure"
        ])
    else:  # high risk
        recommendations.extend([
            "Seek immediate medical attention and HIV testing",
            "Discuss PEP (post-exposure prophylaxis) with healthcare provider urgently",
            "Contact emergency services if experiencing severe symptoms",
            "Follow up with infectious disease specialist"
        ])
    
    # Timeframe-specific recommendations
    if timeframe in ["0-72h", "3-7days"]:
        recommendations.append("Time-sensitive: PEP is most effective when started within 72 hours")
    
    # Symptom-specific recommendations
    if "fever" in symptoms:
        recommendations.append("Monitor temperature regularly and seek medical care for high fever")
    
    if "fatigue" in symptoms or "muscle_aches" in symptoms:
        recommendations.append("Get adequate rest and stay hydrated")
    
    # Thermal-specific recommendations
    if thermal_data and thermal_data.get('fever_detected'):
        fever_severity = thermal_data.get('fever_severity', 'none')
        max_temp = thermal_data.get('max_temperature', 0)
        
        if fever_severity == 'high':
            recommendations.append(f"High fever detected ({max_temp:.1f}°C). Seek immediate medical attention")
        elif fever_severity == 'moderate':
            recommendations.append(f"Moderate fever detected ({max_temp:.1f}°C). Monitor closely and consider medical consultation")
        
        recommendations.append("Continue temperature monitoring and document trends")
    
    return recommendations

def get_urgency_level(
    risk_level: str, 
    timeframe: str, 
    thermal_data: Optional[Dict[str, Any]] = None
) -> str:
    """Determine urgency level for medical consultation"""
    
    # High fever always increases urgency
    if thermal_data and thermal_data.get('fever_severity') == 'high':
        return "immediate"
    
    if risk_level == "high":
        if timeframe in ["0-72h", "3-7days"]:
            return "immediate"
        else:
            return "urgent"
    elif risk_level == "moderate":
        if thermal_data and thermal_data.get('fever_detected'):
            return "urgent"
        else:
            return "soon"
    else:
        return "routine"

def generate_medical_advice(
    risk_score: int,
    risk_level: str,
    symptoms: List[str],
    thermal_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Generate comprehensive medical advice"""
    
    advice = {
        "immediate_actions": [],
        "testing_recommendations": [],
        "prevention_strategies": [],
        "follow_up_care": [],
        "emergency_signs": []
    }
    
    # Immediate actions
    if risk_level == "high":
        advice["immediate_actions"].extend([
            "Contact healthcare provider immediately",
            "Consider emergency room visit if severe symptoms present",
            "Do not delay seeking medical care"
        ])
    
    # Testing recommendations
    if risk_score > 30:
        advice["testing_recommendations"].extend([
            "HIV antibody/antigen test (4th generation)",
            "Complete STI panel screening",
            "Hepatitis B and C testing"
        ])
    
    # Thermal-specific advice
    if thermal_data and thermal_data.get('fever_detected'):
        max_temp = thermal_data.get('max_temperature', 0)
        advice["immediate_actions"].append(f"Temperature monitoring shows {max_temp:.1f}°C - seek medical evaluation")
        advice["emergency_signs"].append("Temperature above 39°C (102.2°F)")
    
    # Prevention strategies
    advice["prevention_strategies"].extend([
        "Use barrier protection during sexual activity",
        "Avoid sharing needles or injection equipment",
        "Regular HIV testing if at ongoing risk",
        "Consider PrEP consultation if high-risk behavior continues"
    ])
    
    # Follow-up care
    advice["follow_up_care"].extend([
        "Schedule follow-up testing as recommended",
        "Monitor for symptoms development",
        "Maintain regular healthcare provider relationship"
    ])
    
    # Emergency warning signs
    advice["emergency_signs"].extend([
        "Severe fever (>39°C/102.2°F)",
        "Difficulty breathing",
        "Persistent vomiting",
        "Severe headache or confusion",
        "Signs of severe illness"
    ])
    
    return advice

class RiskTrendAnalyzer:
    """Analyze risk trends over time for users with multiple assessments"""
    
    @staticmethod
    def analyze_risk_progression(assessment_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze how risk levels change over time"""
        if len(assessment_history) < 2:
            return {"trend": "insufficient_data", "analysis": "Need more assessments for trend analysis"}
        
        risk_scores = [a['risk_score'] for a in assessment_history]
        dates = [datetime.fromisoformat(a['timestamp']) for a in assessment_history]
        
        # Calculate trend
        if risk_scores[-1] > risk_scores[0]:
            trend = "increasing"
        elif risk_scores[-1] < risk_scores[0]:
            trend = "decreasing"
        else:
            trend = "stable"
        
        # Calculate average change
        score_change = risk_scores[-1] - risk_scores[0]
        time_span = (dates[-1] - dates[0]).days
        
        analysis = {
            "trend": trend,
            "score_change": score_change,
            "time_span_days": time_span,
            "current_score": risk_scores[-1],
            "previous_score": risk_scores[0],
            "recommendations": []
        }
        
        # Generate trend-based recommendations
        if trend == "increasing":
            analysis["recommendations"].extend([
                "Risk factors appear to be increasing over time",
                "Consider comprehensive risk reduction counseling",
                "Evaluate recent behavioral changes"
            ])
        elif trend == "decreasing":
            analysis["recommendations"].extend([
                "Positive trend in risk reduction observed",
                "Continue current prevention strategies",
                "Maintain regular monitoring"
            ])
        
        return analysis
```
