import boto3
import pandas as pd
import streamlit as st

st.set_page_config(page_title="NSFAS Risk Dashboard", layout="wide")

# Change region if your DynamoDB table is elsewhere
dynamodb = boto3.resource('dynamodb', region_name='af-south-1')
table = dynamodb.Table('StudentRisk')


@st.cache_data(ttl=60)
def load_data():
    response = table.scan()
    items = response.get('Items', [])
    # Handle pagination for larger tables
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response.get('Items', []))
    return pd.DataFrame(items)


st.title("NSFAS Student Risk Dashboard")
st.caption("Synthetic data — for demonstration purposes only")

df = load_data()

if df.empty:
    st.warning("No data found. Upload a CSV to the S3 raw bucket to trigger processing.")
else:
    df['average_mark'] = pd.to_numeric(df['average_mark'], errors='coerce')
    df['risk_score'] = pd.to_numeric(df['risk_score'], errors='coerce')
    df['attendance'] = pd.to_numeric(df['attendance'], errors='coerce')

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Students", len(df))
    col2.metric("High Risk", int((df['risk_level'] == 'HIGH').sum()))
    col3.metric("Medium Risk", int((df['risk_level'] == 'MEDIUM').sum()))
    col4.metric("Low Risk", int((df['risk_level'] == 'LOW').sum()))

    st.divider()

    # Risk distribution chart
    st.subheader("Risk Level Distribution")
    risk_counts = df['risk_level'].value_counts().reindex(['HIGH', 'MEDIUM', 'LOW']).fillna(0)
    st.bar_chart(risk_counts)

    st.divider()

    # Filterable student table
    st.subheader("Student Records")
    risk_filter = st.multiselect(
        "Filter by risk level",
        options=['HIGH', 'MEDIUM', 'LOW'],
        default=['HIGH', 'MEDIUM', 'LOW']
    )
    filtered = df[df['risk_level'].isin(risk_filter)].sort_values('risk_score', ascending=False)
    st.dataframe(
        filtered[['student_id', 'name', 'average_mark', 'attendance', 'risk_score', 'risk_level']],
        use_container_width=True,
        hide_index=True
    )

    if st.button("Refresh data"):
        st.cache_data.clear()
        st.rerun()
