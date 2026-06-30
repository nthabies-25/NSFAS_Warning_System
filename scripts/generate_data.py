"""
Generate synthetic South African student data.
"""
import pandas as pd
import numpy as np
from faker import Faker
import random
from pathlib import Path

def generate_students(num_students=10000):
    """Generate synthetic student data."""
    # Use en_US instead of en_ZA (more widely available)
    fake = Faker('en_US')
    
    first_names = ['Thabo', 'Lindiwe', 'Sipho', 'Nomsa', 'Kagiso', 'Zanele', 
                   'Andile', 'Busisiwe', 'Sibusiso', 'Nokuthula', 'Themba',
                   'Phumzile', 'Mpho', 'Lerato', 'Tshepo']
    
    last_names = ['Nkosi', 'Mthembu', 'Dlamini', 'Mkhize', 'Khumalo', 'Zulu',
                  'Mahlangu', 'Mokoena', 'Mabaso', 'Mthethwa', 'Ngcobo',
                  'Mhlongo', 'Molefe']
    
    universities = ['University of Cape Town', 'University of Johannesburg',
                    'University of KwaZulu-Natal', 'University of Pretoria',
                    'University of Stellenbosch', 'University of the Witwatersrand',
                    'North-West University', 'University of the Free State']
    
    faculties = ['Engineering', 'Science', 'Commerce', 'Education', 'Arts', 'Law']
    
    students = []
    for i in range(1, num_students + 1):
        # Generate realistic marks using beta distribution
        base_mark = np.random.beta(a=2, b=2) * 100
        
        # Create realistic grade distribution
        if random.random() < 0.15:  # Struggling students
            avg_mark = max(30, min(49, base_mark - 20))
        elif random.random() < 0.10:  # Top performers
            avg_mark = max(75, min(95, base_mark + 15))
        else:  # Average students
            avg_mark = max(40, min(75, base_mark))
        
        # Attendance correlated with marks
        if avg_mark > 70:
            attendance = min(95, random.randint(75, 100))
        elif avg_mark > 50:
            attendance = random.randint(55, 85)
        else:
            attendance = random.randint(20, 65)
        
        # Failed modules correlated with attendance and marks
        if attendance < 60 or avg_mark < 45:
            failed = random.randint(1, 4)
        else:
            failed = random.randint(0, 1)
        
        students.append({
            'student_id': f"NSFAS{i:06d}",
            'name': f"{random.choice(first_names)} {random.choice(last_names)}",
            'university': random.choice(universities),
            'faculty': random.choice(faculties),
            'year_of_study': random.randint(1, 4),
            'average_mark': round(avg_mark, 2),
            'attendance': round(attendance, 2),
            'failed_modules': failed,
            'missed_assignments': random.randint(0, 5)
        })
    
    df = pd.DataFrame(students)
    
    # Add some missing values (realism)
    missing_idx = np.random.choice(df.index, size=int(len(df)*0.02), replace=False)
    df.loc[missing_idx, 'attendance'] = np.nan
    
    # Save to CSV
    output_path = Path("data/raw/students.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    
    print(f"✅ Generated {num_students} student records")
    print(f"📁 Saved to: {output_path}")
    print(f"\n📊 Sample data (first 5 records):")
    print(df.head())
    print(f"\n📈 Summary Statistics:")
    print(f"  Average mark: {df['average_mark'].mean():.2f}%")
    print(f"  Average attendance: {df['attendance'].mean():.2f}%")
    print(f"  Students with failed modules > 2: {len(df[df['failed_modules'] > 2])}")
    
    return df

if __name__ == "__main__":
    generate_students(10000)
