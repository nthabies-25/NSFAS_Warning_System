"""
Analyze risk assessment results.
"""
import pandas as pd
from pathlib import Path

def analyze_results():
    """Analyze the latest risk report."""
    # Find the latest report
    processed_dir = Path("data/processed")
    reports = list(processed_dir.glob("risk_report_*.csv"))
    
    if not reports:
        print("❌ No risk reports found in data/processed/")
        return
    
    latest = max(reports, key=lambda x: x.stat().st_mtime)
    print(f"📊 Analyzing: {latest.name}\n")
    
    # Load data
    df = pd.read_csv(latest)
    
    # Summary
    print("=" * 60)
    print("NSFAS RISK ANALYSIS REPORT")
    print("=" * 60)
    print(f"\n📈 OVERALL STATISTICS:")
    print(f"  Total Students: {len(df):,}")
    print(f"  Average Risk Score: {df['risk_score'].mean():.2f}")
    print(f"  Median Risk Score: {df['risk_score'].median():.2f}")
    print(f"  Highest Risk Score: {df['risk_score'].max():.0f}")
    print(f"  Lowest Risk Score: {df['risk_score'].min():.0f}")
    
    print(f"\n📊 RISK LEVEL DISTRIBUTION:")
    risk_counts = df['risk_level'].value_counts()
    for level in ['HIGH', 'MEDIUM', 'LOW']:
        count = risk_counts.get(level, 0)
        pct = count / len(df) * 100
        print(f"  {level}: {count:,} ({pct:.1f}%)")
    
    print(f"\n🏫 RISK BY UNIVERSITY:")
    uni_risk = df.groupby('university')['risk_level'].value_counts().unstack(fill_value=0)
    uni_risk['total'] = uni_risk.sum(axis=1)
    uni_risk['high_risk_pct'] = uni_risk['HIGH'] / uni_risk['total'] * 100
    print(uni_risk[['HIGH', 'MEDIUM', 'LOW', 'total', 'high_risk_pct']].sort_values('high_risk_pct', ascending=False).head(10))
    
    print(f"\n⚠️ TOP 10 HIGHEST RISK STUDENTS:")
    top_10 = df.nlargest(10, 'risk_score')[['student_id', 'name', 'university', 'average_mark', 'attendance', 'failed_modules', 'risk_score', 'risk_level']]
    print(top_10.to_string(index=False))
    
    print(f"\n📁 Report saved to: {latest}")
    
    return df

if __name__ == "__main__":
    analyze_results()
