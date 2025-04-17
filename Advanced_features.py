import streamlit as st
import pandas as pd
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import os
from langchain.callbacks import get_openai_callback
import json
from datetime import datetime
import re
import plotly.express as px
from utils import get_saved_fact_checks, parse_verdict, highlight_document_references

st.set_page_config(
    page_title="Advanced Fact-Checking Features",
    page_icon="🔬",
    layout="wide"
)

# Initialize OpenAI API key from secrets
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

# Initialize session state
if 'tokens_used' not in st.session_state:
    st.session_state.tokens_used = 0

st.title("🔬 Advanced Fact-Checking Features")
st.markdown("""
Explore additional capabilities of the fact-checking system.
""")

# Create tabs for different features
tab1, tab2, tab3 = st.tabs(["📊 Trend Analysis", "🧠 Claim Generation", "🔄 Batch Processing"])

with tab1:
    st.header("Fact-Checking Trend Analysis")
    st.markdown("""
    This tool analyzes patterns across multiple fact-checks to identify common themes, 
    sources of misinformation, and narrative trends.
    """)
    
    # Load saved fact checks
    fact_checks = get_saved_fact_checks()
    
    if not fact_checks:
        st.warning("No fact checks have been saved yet. Start fact-checking to use this feature.")
    else:
        # Prepare data for analysis
        trend_prompt = PromptTemplate(
            input_variables=["fact_checks"],
            template="""You are an expert in analyzing patterns of misinformation. 
            Please analyze the following collection of fact-checks to identify:

            1. Common themes or topics that appear across multiple claims
            2. Patterns in types of misinformation (e.g., misrepresentation, out-of-context, fabrication)
            3. Potential sources or origins of these claims
            4. Recommendations for areas where preventive education would be most valuable

            Fact checks:
            {fact_checks}

            Format your response as follows:
            ## Common Themes
            - [Theme 1]
            - [Theme 2]
            ...

            ## Misinformation Patterns
            - [Pattern 1]: [Brief explanation]
            - [Pattern 2]: [Brief explanation]
            ...

            ## Likely Origins
            - [Origin 1]: [Evidence and reasoning]
            - [Origin 2]: [Evidence and reasoning]
            ...

            ## Educational Recommendations
            - [Recommendation 1]
            - [Recommendation 2]
            ...
            """
        )
        
        # Prepare the fact checks in a condensed format
        fact_check_summaries = []
        for i, fc in enumerate(fact_checks[:10]):  # Limit to 
