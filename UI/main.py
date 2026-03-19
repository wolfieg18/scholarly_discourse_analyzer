import streamlit as st
from streamlit_timeline import timeline as st_timeline
import pandas as pd
import os

DF_DISPLAY_COLUMNS = ["Title", "Author", "Year", "Era", "Sentiment_Score", "Sentiment_Hits", "Token_Count", "Tokens"]

st.set_page_config(layout="wide", page_title="Scholarly Evolution Timeline")

# 1. Custom CSS (Main page UI only)
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 2. Load Data
try:
    # Adjust path if needed, assuming run from root
    data_path = os.path.join("UI", "static", "all_sentiment_analysis.csv")
    df = pd.read_csv(data_path)
except FileNotFoundError:
    st.error(f"Data file not found at {data_path}. Ensure it's pushed to GitHub.")
    st.stop()

# Ensure proper types
df['Year'] = df['Year'].astype(int)
df['Sentiment_Score'] = df['Sentiment_Score'].astype(float)

# 3. Helpers
def get_sentiment_color(score):
    if score > 0.3: return "#00ad5c"  # Green
    elif score < -0.3: return "#e74c3c" # Red
    else: return "#3498db" # Blue

def normalize_sentiment(score):
    return (score + 1) / 2

# 4. Timeline Items 
# Note: Styles moved here because CSS classes don't work inside the iframe
items = []
for _, row in df.iterrows():
    score = row['Sentiment_Score']
    color = get_sentiment_color(score)

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

# 5. Tabs
tab_home, tab_timeline, tab_visuals, tab_analysis, tab_data = st.tabs(
    ["🏠 Home", "📅 Timeline View", "📊 Lexical Analysis", "📈 Statistical Analysis", "📋 Raw Dataset"])

with tab_home: 
    st.title("Amazonian Scholarly Discourse Evolution Analysis")
    st.markdown("""
    ### Overview
    This project explores how scholarly writing regarding Indigenous Amazonanians has evolved over time using **sentiment analysis and lexical trends**.
    """)
    st.info("Tip: Use Ctrl + Scroll in the timeline to zoom.")

# --- TIMELINE TAB ---
with tab_timeline:
    st.title("Scholarly Timeline by Era")
    
    # Legend because we can't use the 'groups' parameter
    st.markdown("**Era Legend:** <span style='color:#00ad5c'>● Modern</span> | <span style='color:#e74c3c'>● Historical</span>", unsafe_allow_html=True)
    
    # STABLE CALL: Only items and height. Options/Groups will crash this version.
    selected = st_timeline(items, height=550)
    
    st.caption("Tip: Drag to navigate years. Click a paper to view analysis in the sidebar.")

with tab_visuals:
    st.header("Lexical Analysis Visuals")
    image_base_path = os.path.join("UI", "static")
    st.subheader("Comparative Analysis")
    col1, col2 = st.columns(2)
    # Visuals logic remains same as yours
    with col1: st.image(os.path.join(image_base_path, "top_15_keywords_historical.png"), caption="Historical Keywords")
    with col2: st.image(os.path.join(image_base_path, "top_15_keywords_modern.png"), caption="Modern Keywords")

with tab_analysis:
    st.header("📈 Modern vs Historical Dataset Comparison")
    old_df = df[df['Era'] == "Historical"]
    modern_df = df[df['Era'] == "Modern"]
    st.bar_chart(pd.DataFrame({
        "Mean Sentiment": [old_df['Sentiment_Score'].mean(), modern_df['Sentiment_Score'].mean()]
    }, index=["Historical", "Modern"]))

with tab_data:
    st.header("Project Database")
    st.dataframe(df[DF_DISPLAY_COLUMNS])

# --- SIDEBAR ---
if selected:
    # The return value might be a string (id) or a dict depending on the event
    paper_id = selected if isinstance(selected, str) else selected.get('id')
    
    try:
        details = df[df['File_Name'] == paper_id].iloc[0]
        score = float(details['Sentiment_Score'])
        
        st.sidebar.header("Selected Paper Analysis")
        st.sidebar.subheader(details['Title'])
        st.sidebar.divider()
        st.sidebar.write(f"**Author:** {details['Author']}")
        st.sidebar.write(f"**Year:** {details['Year']}")
        st.sidebar.progress(normalize_sentiment(score), text=f"Sentiment: {score:.2f}")
        st.sidebar.write("### Summary")
        st.sidebar.write(details['Final_Sentiment_Summary'])
    except:
        st.sidebar.info("Select a paper on the timeline.")
else:
    st.sidebar.info("Select a paper on the timeline.")
