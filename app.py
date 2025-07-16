import sys
import pysqlite3
sys.modules["sqlite3"] = pysqlite3

import streamlit as st
import pandas as pd
from crew import create_crew_with_file

# Page configuration
st.set_page_config(layout="wide", page_title="Support Report Generator")
st.title("🛠️ Support Report Generator")

# --- Sidebar: OpenAI API Key ---
st.sidebar.header("🔑 OpenAI API Key")

# Initialize session state variables
if "api_key" not in st.session_state:
    st.session_state.api_key = None
if "api_key_entered" not in st.session_state:
    st.session_state.api_key_entered = False

# API key input logic
if not st.session_state.api_key_entered:
    api_input = st.sidebar.text_input(
        "Enter your OpenAI API key",
        type="password",
        placeholder="sk-...",
        help="Required to run the AI agents"
    )
    submit_key = st.sidebar.button("✅ Submit API Key")

    if submit_key and api_input:
        st.session_state.api_key = api_input
        st.session_state.api_key_entered = True
        st.sidebar.success("🔐 API key saved securely.")
elif st.session_state.api_key:
    st.sidebar.success("✅ API key stored for this session.")

# --- Sidebar: CSV Upload ---
st.sidebar.header("📤 Upload Your CSV")
uploaded_file = st.sidebar.file_uploader(
    "Upload your support tickets CSV", type="csv")

# === Main Logic ===
if not st.session_state.api_key_entered:
    st.warning("🔑 Please enter your OpenAI API key in the sidebar to continue.")
elif not uploaded_file:
    st.info("👈 Please upload a CSV file to get started.")
else:
    openai_api_key = st.session_state.api_key
    # Save file locally
    temp_csv_path = './uploaded_support_data.csv'
    with open(temp_csv_path, 'wb') as f:
        f.write(uploaded_file.read())

    # Load DataFrame
    @st.cache_data
    def load_dataframe(path):
        return pd.read_csv(path)

    df = load_dataframe(temp_csv_path)

    with st.expander("👀 Preview Uploaded Data", expanded=False):
        st.dataframe(df.head(10), use_container_width=True)

    # Report Generation
    with st.status("⏳ Running AI agents... generating report. Please wait.", expanded=False):
        openai_api_key = st.session_state.api_key
        crew = create_crew_with_file(temp_csv_path, openai_api_key)
        result = crew.kickoff()

    # Parse result
    if isinstance(result, dict) and 'final_output' in result:
        final_report = result['final_output']
    elif isinstance(result, str) and "Final Answer:" in result:
        final_report = result.split("Final Answer:")[-1].strip()
    else:
        final_report = str(result).strip()

    # === Display Sections ===
    with st.expander("📄 Final Report", expanded=True):
        st.markdown(final_report, unsafe_allow_html=True)

    # Download Report
    st.download_button(
        "📥 Download Report",
        data=final_report,
        file_name="support_final_report.txt",
        mime="text/plain"
    )
