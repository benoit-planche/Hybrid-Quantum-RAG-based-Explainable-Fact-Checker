import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from utils import get_saved_fact_checks, parse_verdict

st.set_page_config(
    page_title="Fact-Checker Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Fact-Checker Dashboard")
st.markdown("""
This dashboard provides analytics and insights about the fact-checks performed.
""")

# Load all saved fact checks
fact_checks = get_saved_fact_checks()

if not fact_checks:
    st.warning("No fact checks have been saved yet. Start fact-checking to populate this dashboard.")
    st.stop()

# Convert to DataFrame for analytics
facts_df = pd.DataFrame([
    {
        'id': fc['id'],
        'timestamp': datetime.strptime(fc['timestamp'], "%Y-%m-%d %H:%M:%S"),
        'claim': fc['claim'],
        'verdict': fc['verdict'],
        'source_count': len(fc['sources']) if 'sources' in fc else 0,
    }
    for fc in fact_checks
])

# Top metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Fact Checks", len(facts_df))

with col2:
    st.metric("Fact Checks Today", len(facts_df[facts_df['timestamp'].dt.date == datetime.now().date()]))

with col3:
    if not facts_df.empty:
        true_pct = len(facts_df[facts_df['verdict'].isin(['TRUE', 'MOSTLY TRUE'])]) / len(facts_df) * 100
        st.metric("Truth Rate", f"{true_pct:.1f}%")
    else:
        st.metric("Truth Rate", "N/A")

with col4:
    if not facts_df.empty:
        avg_sources = facts_df['source_count'].mean()
        st.metric("Avg. Sources Per Check", f"{avg_sources:.1f}")
    else:
        st.metric("Avg. Sources Per Check", "N/A")

# Verdict distribution
st.subheader("Verdict Distribution")
verdict_counts = facts_df['verdict'].value_counts().reset_index()
verdict_counts.columns = ['Verdict', 'Count']

# Define custom colors for each verdict
verdict_colors = {
    "TRUE": "#2ecc71",
    "MOSTLY TRUE": "#a0d995", 
    "MIXED": "#f4d03f",
    "MOSTLY FALSE": "#e67e22",
    "FALSE": "#e74c3c",
    "UNVERIFIABLE": "#95a5a6"
}

fig = px.bar(
    verdict_counts,
    x='Verdict',
    y='Count',
    color='Verdict',
    color_discrete_map=verdict_colors,
    title="Distribution of Fact-Check Verdicts"
)
st.plotly_chart(fig, use_container_width=True)

# Fact checks over time
st.subheader("Fact Checks Over Time")

# Create a date range from the first fact check to today
if not facts_df.empty:
    date_range = pd.date_range(
        start=facts_df['timestamp'].min().date(),
        end=datetime.now().date()
    )
    
    # Count fact checks by date
    facts_by_date = facts_df.groupby(facts_df['timestamp'].dt.date).size().reset_index()
    facts_by_date.columns = ['date', 'count']
    
    # Create a complete date range with zeros for missing dates
    date_df = pd.DataFrame({'date': date_range})
    date_df = date_df.merge(facts_by_date, on='date', how='left').fillna(0)
    
    fig = px.line(
        date_df,
        x='date',
        y='count',
        title="Fact Checks Per Day",
        markers=True
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.write("No data available for timeline chart.")

# Recent fact checks
st.subheader("Recent Fact Checks")
recent_facts = facts_df.sort_values('timestamp', ascending=False).head(10)
recent_facts['timestamp'] = recent_facts['timestamp'].dt.strftime("%Y-%m-%d %H:%M")

# Format the DataFrame for display
display_df = recent_facts[['timestamp', 'claim', 'verdict']]
display_df = display_df.rename(columns={
    'timestamp': 'Date & Time',
    'claim': 'Claim',
    'verdict': 'Verdict'
})

# Apply custom styling to the verdict column
def color_verdicts(val):
    colors = {
        "TRUE": "background-color: #d5f5e3; color: #196f3d",
        "MOSTLY TRUE": "background-color: #e9f7ef; color: #196f3d",
        "MIXED": "background-color: #fcf3cf; color: #7d6608",
        "MOSTLY FALSE": "background-color: #fae5d3; color: #943126",
        "FALSE": "background-color: #f5b7b1; color: #943126",
        "UNVERIFIABLE": "background-color: #eaecee; color: #566573"
    }
    return colors.get(val, "")

styled_df = display_df.style.applymap(color_verdicts, subset=['Verdict'])
st.dataframe(styled_df, use_container_width=True)

# Export to CSV option
if st.button("Export Data to CSV"):
    csv = facts_df.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="fact_checks_export.csv",
        mime="text/csv",
    )
