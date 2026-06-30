"""
Batch processor for NSFAS risk assessment.
"""
import pandas as pd
from pathlib import Path
from datetime import datetime
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from engine.risk_engine import RiskEngine

def main():
    """Main entry point for batch processing."""
    input_path = "data/raw/students.csv"
    output_dir = "data/processed"
    
    # Check if input exists
    if not Path(input_path).exists():
        print(f"❌ Input file not found: {input_path}")
        print("💡 Run 'python scripts/generate_data.py' to generate sample data")
        return
    
    # Load data
    print(f"📥 Loading data from {input_path}")
    df = pd.read_csv(input_path)
    
    # Handle missing values
    df['attendance'] = df['attendance'].fillna(0)
    df['average_mark'] = df['average_mark'].fillna(0)
    df['failed_modules'] = df['failed_modules'].fillna(0)
    
    print(f"✅ Loaded {len(df)} records")
    
    # Process
    print("🔄 Processing risk assessment...")
    students = df.to_dict('records')
    enriched = RiskEngine.bulk_process(students)
    result_df = pd.DataFrame(enriched)
    
    # Save
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = Path(output_dir) / f"risk_report_{timestamp}.csv"
    result_df.to_csv(output_path, index=False)
    
    # Summary
    high_risk = len(result_df[result_df['risk_level'] == 'HIGH'])
    medium_risk = len(result_df[result_df['risk_level'] == 'MEDIUM'])
    low_risk = len(result_df[result_df['risk_level'] == 'LOW'])
    
    print(f"\n{'='*50}")
    print("NSFAS RISK ASSESSMENT SUMMARY")
    print('='*50)
    print(f"Total Students: {len(result_df)}")
    print(f"High Risk: {high_risk} ({high_risk/len(result_df)*100:.1f}%)")
    print(f"Medium Risk: {medium_risk} ({medium_risk/len(result_df)*100:.1f}%)")
    print(f"Low Risk: {low_risk} ({low_risk/len(result_df)*100:.1f}%)")
    print(f"\n📁 Report saved to: {output_path}")
    
    # Show top high-risk students
    if high_risk > 0:
        print("\n⚠️ TOP 5 HIGH-RISK STUDENTS:")
        top_5 = result_df.nlargest(5, 'risk_score')[['name', 'risk_score', 'risk_level']]
        print(top_5.to_string(index=False))
    
    return result_df

if __name__ == "__main__":
    main()
