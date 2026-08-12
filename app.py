import os
import streamlit as st
import pandas as pd
import plotly.express as px
from google import genai

st.set_page_config(
    page_title="SAU Lead Analytics | Google AI Studio",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Clean, Modern Studio Styling
st.markdown("""
<style>
    .main { background-color: #fafafa; }
    
    .studio-header {
        display: flex;
        align-items: center;
        gap: 12px;
        padding-bottom: 12px;
        border-bottom: 1px solid #e0e0e0;
        margin-bottom: 24px;
    }
    .studio-badge {
        background-color: #e8f0fe;
        color: #1a73e8;
        font-size: 11px;
        font-weight: 700;
        padding: 4px 8px;
        border-radius: 4px;
        letter-spacing: 0.5px;
    }
    
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 14px 18px;
        border-radius: 8px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    div[data-testid="stMetricLabel"] {
        font-size: 12px !important;
        color: #5f6368 !important;
        font-weight: 600;
    }
    div[data-testid="stMetricValue"] {
        color: #202124 !important;
        font-size: 22px !important;
    }
    
    .stButton>button {
        background-color: #1a73e8;
        color: white;
        border-radius: 4px;
        border: none;
        padding: 8px 20px;
        font-weight: 500;
    }
    .stButton>button:hover { background-color: #1557b0; }
</style>
""", unsafe_allow_html=True)

# Studio Header
st.markdown("""
<div class="studio-header">
    <span class="studio-badge">GEMINI 2.5 FLASH</span>
    <h2 style="margin:0; font-size: 22px; font-weight: 600; color: #202124;">SAU Lead Analytics Studio</h2>
</div>
""", unsafe_allow_html=True)

csv_file = "parsed_leads.csv"
if not os.path.exists(csv_file):
    st.error(f"'{csv_file}' not found. Please run 'python3 parse_emails.py' first.")
    st.stop()

df = pd.read_csv(csv_file)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Filters")
    programs = ["All Programs"] + sorted([p for p in df["Program of Interest"].dropna().unique() if p])
    selected_program = st.selectbox("Academic Program", programs)
    
    st.divider()
    st.markdown("### 🔑 API Key")
    api_key = os.environ.get("GEMINI_API_KEY") or st.text_input("Gemini API Key", type="password")

filtered_df = df if selected_program == "All Programs" else df[df["Program of Interest"] == selected_program]

# Top Key Performance Indicators
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Inquiries", f"{len(filtered_df):,}")
m2.metric("Active Programs", df["Program of Interest"].nunique())
m3.metric("Primary Channel", df["Lead Source"].mode()[0] if not df["Lead Source"].empty else "N/A")
m4.metric("Conversion Status", "Active Target")

st.markdown("<br>", unsafe_allow_html=True)

# Main Visualizations Panel
tab1, tab2 = st.tabs(["📊 Analytics Overview", "📄 Raw Dataset Explorer"])

with tab1:
    col_chart1, col_chart2 = st.columns([3, 2])
    
    with col_chart1:
        st.markdown("##### Inquiry Volume by Program")
        prog_counts = filtered_df["Program of Interest"].value_counts().reset_index()
        prog_counts.columns = ["Program", "Count"]
        
        fig_prog = px.bar(
            prog_counts,
            x="Program",
            y="Count",
            text="Count",
            color_discrete_sequence=["#1a73e8"]
        )
        fig_prog.update_layout(
            height=380,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=20, b=80),
            xaxis=dict(title="", tickangle=-25, showgrid=False),
            yaxis=dict(title="Leads", showgrid=True, gridcolor="#eeeeee")
        )
        st.plotly_chart(fig_prog, use_container_width=True)

    with col_chart2:
        st.markdown("##### Acquisition Channel Breakdown")
        source_counts = filtered_df["Lead Source"].value_counts().reset_index()
        source_counts.columns = ["Lead Source", "Count"]
        
        fig_source = px.pie(
            source_counts,
            names="Lead Source",
            values="Count",
            hole=0.55,
            color_discrete_sequence=["#1a73e8", "#4285f4", "#8ab4f8", "#aecbfa"]
        )
        fig_source.update_layout(
            height=380,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=20, b=20)
        )
        st.plotly_chart(fig_source, use_container_width=True)

with tab2:
    st.dataframe(filtered_df, use_container_width=True, height=380)

# Gemini AI Prompt Console Section
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### 🤖 Gemini AI Studio Console")

user_query = st.text_area(
    "Query Console",
    placeholder="e.g., Analyze program demand patterns and suggest candidate follow-up strategies.",
    height=100
)

if st.button("✨ Run Prompt"):
    if not user_query:
        st.warning("Please enter a query in the prompt box.")
    elif not api_key:
        st.error("Missing GEMINI_API_KEY.")
    else:
        try:
            client = genai.Client(api_key=api_key)
            summary_context = f"""
            Scope: {selected_program}
            Total Leads: {len(filtered_df)}
            Program Demand: {filtered_df['Program of Interest'].value_counts().to_dict()}
            Sources: {filtered_df['Lead Source'].value_counts().to_dict()}
            """
            prompt = f"{summary_context}\n\nTask: Provide executive response for university leadership.\nUser Query: {user_query}"
            
            with st.spinner("Processing request with Gemini 2.5 Flash..."):
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                )
                st.success("Analysis Generated")
                st.markdown(response.text)
        except Exception as e:
            st.error(f"Error: {e}")
