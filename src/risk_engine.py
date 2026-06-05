def calculate_risk(student):
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