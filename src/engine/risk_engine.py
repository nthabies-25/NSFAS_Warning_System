"""
Risk Engine - Core business logic for NSFAS student risk assessment.
"""
from typing import Dict, Any

class RiskEngine:
    """Main risk calculation engine."""
    
    ATTENDANCE_THRESHOLD = 70
    MARK_THRESHOLD = 50
    FAILED_MODULES_THRESHOLD = 2
    HIGH_RISK_THRESHOLD = 60
    MEDIUM_RISK_THRESHOLD = 30
    
    @classmethod
    def calculate_risk(cls, student: Dict[str, Any]) -> int:
        """Calculate risk score for a single student."""
        score = 0
        
        attendance = student.get('attendance', 0)
        if attendance < cls.ATTENDANCE_THRESHOLD:
            score += 40
        
        avg_mark = student.get('average_mark', 0)
        if avg_mark < cls.MARK_THRESHOLD:
            score += 40
        
        failed = student.get('failed_modules', 0)
        if failed > cls.FAILED_MODULES_THRESHOLD:
            score += 20
        
        return min(score, 100)
    
    @classmethod
    def get_risk_level(cls, score: int) -> str:
        """Convert risk score to risk level."""
        if score >= cls.HIGH_RISK_THRESHOLD:
            return "HIGH"
        elif score >= cls.MEDIUM_RISK_THRESHOLD:
            return "MEDIUM"
        else:
            return "LOW"
    
    @classmethod
    def process_student(cls, student: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich a student record with risk score and level."""
        risk_score = cls.calculate_risk(student)
        risk_level = cls.get_risk_level(risk_score)
        
        return {
            **student,
            'risk_score': risk_score,
            'risk_level': risk_level
        }
    
    @classmethod
    def bulk_process(cls, students: list) -> list:
        """Process multiple students efficiently."""
        return [cls.process_student(s) for s in students]
