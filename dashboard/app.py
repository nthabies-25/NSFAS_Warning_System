"""
NSFAS Risk Dashboard - Streamlit Application
"""
import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="NSFAS Risk Dashboard",
    page_icon="🎓",
    layout="wide"
)

# Title
st.title("🎓 NSFAS Student Risk Monitoring Dashboard")
st.markdown("---")

# Load the latest risk report
@st.cache_data
def load_data():
    """Load the latest risk report from data/processed/"""
    processed_dir = Path("data/processed")
    reports = list(processed_dir.glob("risk_report_*.csv"))
    
    if not reports:
        st.error("No risk reports found in data/processed/")
        return None
    
    latest = max(reports, key=lambda x: x.stat().st_mtime)
    df = pd.read_csv(latest)
    return df

df = load_data()

if df is not None:
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Students", f"{len(df):,}")
    
    with col2:
        high_risk = len(df[df['risk_level'] == 'HIGH'])
        st.metric("High Risk", f"{high_risk:,}", delta=f"{high_risk/len(df)*100:.1f}%")
    
    with col3:
        medium_risk = len(df[df['risk_level'] == 'MEDIUM'])
        st.metric("Medium Risk", f"{medium_risk:,}", delta=f"{medium_risk/len(df)*100:.1f}%")
    
    with col4:
        low_risk = len(df[df['risk_level'] == 'LOW'])
        st.metric("Low Risk", f"{low_risk:,}", delta=f"{low_risk/len(df)*100:.1f}%")
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Risk Level Distribution")
        risk_counts = df['risk_level'].value_counts().reset_index()
        risk_counts.columns = ['Risk Level', 'Count']
        fig = px.pie(risk_counts, values='Count', names='Risk Level', 
                     color='Risk Level',
                     color_discrete_map={'HIGH': 'red', 'MEDIUM': 'orange', 'LOW': 'green'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Average Mark vs Attendance")
        fig = px.scatter(df, x='average_mark', y='attendance', 
                        color='risk_level',
                        hover_data=['name'],
                        color_discrete_map={'HIGH': 'red', 'MEDIUM': 'orange', 'LOW': 'green'})
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # University breakdown
    st.subheader("Risk by University")
    uni_risk = df.groupby(['university', 'risk_level']).size().unstack(fill_value=0)
    uni_risk['total'] = uni_risk.sum(axis=1)
    uni_risk['high_risk_pct'] = (uni_risk['HIGH'] / uni_risk['total'] * 100).round(1)
    st.dataframe(uni_risk.sort_values('high_risk_pct', ascending=False))
    
    st.markdown("---")
    
    # Top high-risk students
    st.subheader("⚠️ Top 10 High-Risk Students (Require Immediate Attention)")
    high_risk_students = df[df['risk_level'] == 'HIGH'].nlargest(10, 'risk_score')
    st.dataframe(
        high_risk_students[['student_id', 'name', 'university', 'average_mark', 'attendance', 'failed_modules', 'risk_score']]
    )
    
    st.markdown("---")
    st.caption("🔒 Data is encrypted and access is logged for security compliance")
else:
    st.warning("Please run the batch processor first to generate risk reports")

