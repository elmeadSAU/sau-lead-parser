import os
import streamlit as st
import pandas as pd
import plotly.express as px
from google import genai

st.set_page_config(page_title="SAU Lead Analytics Dashboard", layout="wide")

st.title("🎓 SAU Graduate Admissions Lead Analytics")
st.markdown("Interactive dashboard and AI insights powered by Google AI Studio & Gemini.")

# Load parsed data
csv_file = "parsed_leads.csv"

if not os.path.exists(csv_file):
    st.error(f"'{csv_file}' not found. Please run 'python3 parse_emails.py' first to generate lead data.")
    st.stop()

df = pd.read_csv(csv_file)

# Sidebar - Key Filters
st.sidebar.header("Filter Leads")
programs = ["All"] + sorted([p for p in df["Program of Interest"].dropna().unique() if p])
selected_program = st.sidebar.selectbox("Program of Interest", programs)

if selected_program != "All":
    filtered_df = df[df["Program of Interest"] == selected_program]
else:
    filtered_df = df

# Metrics Row
col1, col2, col3 = st.columns(3)
col1.metric("Total Leads Processed", len(filtered_df))
col2.metric("Programs Represented", df["Program of Interest"].nunique())
col3.metric("Top Lead Source", df["Lead Source"].mode()[0] if not df["Lead Source"].empty else "N/A")

st.divider()

# Visualizations
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Leads by Program of Interest")
    prog_counts = filtered_df["Program of Interest"].value_counts().reset_index()
    prog_counts.columns = ["Program", "Count"]
    fig_prog = px.bar(prog_counts, x="Count", y="Program", orientation="h", color="Count", color_continuous_scale="Blues")
    st.plotly_chart(fig_prog, use_container_width=True)

with col_right:
    st.subheader("Leads by Source Channel")
    source_counts = filtered_df["Lead Source"].value_counts().reset_index()
    source_counts.columns = ["Lead Source", "Count"]
    fig_source = px.pie(source_counts, names="Lead Source", values="Count", hole=0.4)
    st.plotly_chart(fig_source, use_container_width=True)

st.divider()

# Interactive Gemini AI Assistant Section
st.subheader("🤖 Ask Google AI Studio / Gemini About This Lead Data")

api_key = os.environ.get("GEMINI_API_KEY") or st.sidebar.text_input("Enter GEMINI_API_KEY", type="password")

user_query = st.text_input("Ask a question about the lead dataset (e.g., 'Summarize key recruitment opportunities from these leads'):")

if user_query:
    if not api_key:
        st.warning("Please set GEMINI_API_KEY in your environment or enter it in the sidebar.")
    else:
        try:
            client = genai.Client(api_key=api_key)
            
            # Prepare summary context for Gemini
            summary_context = f"""
            Here is a summary of the current admissions leads dataset:
            - Total Leads: {len(df)}
            - Program Breakdown: {df['Program of Interest'].value_counts().to_dict()}
            - Lead Source Breakdown: {df['Lead Source'].value_counts().to_dict()}
            - Prospective Student Types: {df['Prospective Student Type'].value_counts().to_dict()}
            """
            
            prompt = f"{summary_context}\n\nUser Question: {user_query}\n\nProvide a concise, professional analysis for university administration."
            
            with st.spinner("Analyzing with Gemini..."):
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                )
                st.markdown(f"**Gemini Analysis:**\n{response.text}")
        except Exception as e:
            st.error(f"Error querying Gemini API: {e}")

st.divider()
st.subheader("Raw Data Preview")
st.dataframe(filtered_df, use_container_width=True)
