import streamlit as st
from streamlit_timeline import timeline as st_timeline
import pandas as pd
import os

# 1. Page Config
st.set_page_config(layout="wide", page_title="Scholarly Evolution Timeline")

# 2. Load Data (CSV is the stable option for tonight)
try:
    # Ensure this file is pushed to your GitHub in this exact folder
    data_path = os.path.join("UI", "static", "all_sentiment_analysis.csv")
    df = pd.read_csv(data_path)
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Ensure proper types for analysis
df['Year'] = df['Year'].astype(int)
df['Sentiment_Score'] = df['Sentiment_Score'].astype(float)

# 3. Helpers
def get_sentiment_color(score):
    if score > 0.3: return "#00ad5c"  # Green
    elif score < -0.3: return "#e74c3c" # Red
    else: return "#3498db" # Blue

def normalize_sentiment(score):
    return (score + 1) / 2

# 4. Prepare Timeline Items
items = []
for _, row in df.iterrows():
    score = row['Sentiment_Score']
    color = get_sentiment_color(score)

    # Styling moved inside the HTML to bypass the iframe CSS boundary
    display_html = f"""
        <div style="
            border-radius: 10px; 
            background-color: #1e1e1e; 
            color: white; 
            font-family: sans-serif; 
            border: 2px solid {color}; 
            padding: 10px;
            max-width: 220px;
            word-wrap: break-word;">
            <div style="color: {color}; font-size: 0.8em; font-weight: bold; margin-bottom: 4px;">{row['Era']}</div>
            <div style="font-weight: bold; font-size: 0.85em; margin-bottom: 4px;">{row['Title']}</div>
            <div style="font-size: 0.75em; opacity: 0.8;">{row['Author']}</div>
            <div style="font-size: 0.75em; opacity: 0.8;">Score: {score:.2f}</div>
        </div>
    """

    items.append({
        "id": str(row['File_Name']),
        "content": display_html,
        "start": f"{row['Year']}-01-01",
    })

# 5. Dashboard Tabs
tab_home, tab_timeline, tab_visuals, tab_analysis, tab_data = st.tabs(
    ["🏠 Home", "📅 Timeline View", "📊 Lexical Analysis", "📈 Statistical Analysis", "📋 Raw Dataset"])

with tab_home: 
    st.title("Amazonian Scholarly Discourse Evolution Analysis")
    st.markdown("### Project Overview")
    st.write("This project explores how scholarly writing regarding Indigenous Amazonanians has evolved over time.")

# --- TIMELINE TAB ---
with tab_timeline:
    st.title("Scholarly Timeline by Era")
    
    # Legend replaces the 'groups' functionality
    st.markdown("**Era Legend:** <span style='color:#00ad5c'>● Modern</span> | <span style='color:#e74c3c'>● Historical</span>", unsafe_allow_html=True)
    
    # Stable Timeline Call
    selected = st_timeline(items, height=550)
    
    st.caption("Tip: Drag to navigate years. Click a paper to view analysis in the sidebar.")

# --- SIDEBAR (Hardened Logic) ---
if selected:
    paper_id = None
    
    # Extract ID safely without using .get() to avoid Streamlit Proxy errors
    if isinstance(selected, list) and len(selected) > 0:
        val = selected[0]
        paper_id = val['id'] if isinstance(val, dict) else val
    elif isinstance(selected, dict):
        if 'id' in selected: paper_id = selected['id']
    elif isinstance(selected, str):
        paper_id = selected

    if paper_id:
        try:
            # Filter the dataframe for the selected paper
            details = df[df['File_Name'] == str(paper_id)].iloc[0]
            
            st.sidebar.header("Selected Paper Analysis")
            st.sidebar.subheader(details['Title'])
            st.sidebar.divider()
            st.sidebar.write(f"**Author:** {details['Author']}")
            st.sidebar.write(f"**Year:** {details['Year']}")
            
            # Sentiment Progress Bar
            score = float(details['Sentiment_Score'])
            st.sidebar.progress(normalize_sentiment(score), text=f"Sentiment: {score:.2f}")
            
            st.sidebar.write("### Summary")
            st.sidebar.write(details['Final_Sentiment_Summary'])
        except Exception:
            st.sidebar.info("Select a paper on the timeline to see details.")
else:
    st.sidebar.info("Select a paper on the timeline to see details.")

# --- REMAINING TABS (Simplified for speed) ---
with tab_visuals:
    st.header("Lexical Analysis Visuals")
    # Add your image paths here as you had them before

with tab_analysis:
    st.header("Statistical Analysis")
    # Add your chart logic here as you had it before

with tab_data:
    st.header("Project Database")
    st.dataframe(df)
