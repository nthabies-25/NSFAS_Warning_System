from typing import Dict, Any

def calculate_risk(student: Dict[str, Any]) -> int:
    """
    Calculates risk score for a single student dictionary.
    """
    
    score = 0
    
    # attendance rule
    if student["attendance"] < 70:
        score += 40
    
    
    # average mark rule
    if student["average_mark"] < 50:
        score += 40
    
    # failed modules rule
    if student["failed_modules"] > 2:
        score += 20
    
    return score

def get_risk_level(score):
    if score >= 60:
        return "HIGH"
    
    elif score >= 30:
        return "MEDIUM"
    
    else:
        return "LOW"
    
def process_studemt(student: Dict[str, Any]) -> Dict[str, Any]:
    """
    The main handler that enriches a student record with risk data.
    """
    
    risk_score = calculate_risk(student)
    risk_level = get_risk_level(risk_score)
    
    #Return a new enriched dictionary (immutability is good)
    return {
        **student,
        "risk_score": risk_score,
        "risk_level": risk_level
    }