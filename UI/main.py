import streamlit as st
from streamlit_timeline import timeline as st_timeline
import pandas as pd
import os

DF_DISPLAY_COLUMNS = ["Title", "Author", "Year", "Era", "Sentiment_Score", "Sentiment_Hits", "Token_Count", "Tokens"]

st.set_page_config(layout="wide", page_title="Scholarly Evolution Timeline")

# 1. Custom CSS (For the main page UI, not the timeline items)
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# 2. Load Data
try:
    df = pd.read_parquet(os.path.join("UI", "static", "all_sentiment_analysis.parquet"))
except FileNotFoundError:
    st.error("Data file not found. Please check UI/static/all_sentiment_analysis.parquet")
    st.stop()

# Ensure proper types
df['Year'] = df['Year'].astype(int)
df['Sentiment_Score'] = df['Sentiment_Score'].astype(float)

# 3. Helpers
def get_sentiment_color(score):
    if score > 0.3:
        return "#00ad5c"  # Green
    elif score < -0.3:
        return "#e74c3c"  # Red
    else:
        return "#3498db"  # Blue

def normalize_sentiment(score):
    return (score + 1) / 2

# 4. Timeline Items
items = []
for _, row in df.iterrows():
    score = row['Sentiment_Score']
    color = get_sentiment_color(score)

    # PORTED CSS: Styles are moved directly into the HTML because of the iframe boundary
    display_html = f"""
        <div style="
            border-radius: 10px; 
            background-color: #1e1e1e; 
            color: black; 
            font-family: 'Inter', sans-serif; 
            border: 2px solid {color}; 
            padding: 8px;
            max-width: 230px; 
            word-wrap: break-word;">
            <div style="color: {color}; font-size: 0.8em; font-weight: bold; margin-bottom: 4px;">{row['Era']}</div>
            <div style="font-weight: bold; font-size: 0.85em; margin-bottom: 4px;">{row['Title']}</div>
            <div style="font-size: 0.75em; opacity: 0.8;">Author: {row['Author']}</div>
            <div style="font-size: 0.75em; opacity: 0.8;">Sentiment: {score:.2f}</div>
        </div>
    """

    items.append({
        "id": row['File_Name'],
        "content": display_html,
        "start": f"{row['Year']}-01-01",
    })

# 5. Options (Numeric values for pixels)
options = {
    "stack": True,
    "showCurrentTime": True,
    "zoomKey": "ctrlKey",
    "maxHeight": 500,
    "verticalScroll": True,
    "horizontalScroll": True
}

# 6. Tabs
tab_home, tab_timeline, tab_visuals, tab_analysis, tab_data = st.tabs(
    ["🏠 Home", "📅 Timeline View", "📊 Lexical Analysis", "📈 Statistical Analysis", "📋 Raw Dataset"])

with tab_home: 
    st.title("Amazonian Scholarly Discourse Evolution Analysis")
    
    st.markdown("""
    ### Overview
    This project explores how scholarly writing regarding Indigenous Amazonanians has evolved over time using **sentiment analysis and lexical trends**.
    
    ### How to Use This Dashboard
    1. Start with the **Timeline View**
    2. Click on a paper to inspect its sentiment and metadata in the sidebar
    3. Use **Statistical Analysis** to understand broader trends
    """)
    st.info("Tip: Use Ctrl + Scroll in the timeline to zoom.")

# --- TIMELINE TAB ---
# --- TIMELINE TAB ---
with tab_timeline:
    st.title("Scholarly Timeline by Era")
    
    # NOTE: This version of the library ONLY accepts (items, height)
    # Any extra arguments like 'options' or 'groups' will cause a TypeError
    selected = st_timeline(items, height=550)
    
    st.caption("Tip: Hold Ctrl + Scroll to zoom. Drag to navigate years.")

with tab_visuals:
    st.header("Lexical Analysis Visuals")
    image_base_path = os.path.join("UI", "static")
    
    st.subheader("Old Dataset")
    col1, col2, col3 = st.columns(3)
    with col1: st.image(os.path.join(image_base_path, "top_15_keywords_historical.png"), caption="Word Count")
    with col2: st.image(os.path.join(image_base_path, "word_bubble_historical.png"), caption="Word Bubble")
    with col3: st.image(os.path.join(image_base_path, "top_15_common_word_pairs_historical.png"), caption="Bigram Graph")

    st.markdown("---") 

    st.subheader("Modern Dataset")
    col1, col2, col3 = st.columns(3)
    with col1: st.image(os.path.join(image_base_path, "top_15_keywords_modern.png"), caption="Word Count")
    with col2: st.image(os.path.join(image_base_path, "word_bubble_modern.png"), caption="Word Bubble")
    with col3: st.image(os.path.join(image_base_path, "top_15_common_word_pairs_historical.png"), caption="Bigram Graph")

# --- CHARTS ---
with tab_analysis:
    st.header("📈 Modern vs Historical Dataset Comparison")
    old_df = df[df['Era'] == "Historical"]
    modern_df = df[df['Era'] == "Modern"]

    st.subheader("Summary Statistics (Sentiment Score)")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Historical")
        st.write(old_df['Sentiment_Score'].describe())
    with col2:
        st.markdown("### Modern")
        st.write(modern_df['Sentiment_Score'].describe())

    st.markdown("---")
    st.subheader("Average Sentiment Comparison")
    mean_df = pd.DataFrame({
        "Dataset": ["Historical", "Modern"],
        "Mean Sentiment": [old_df['Sentiment_Score'].mean(), modern_df['Sentiment_Score'].mean()]
    }).set_index("Dataset")
    st.bar_chart(mean_df)

# --- DATA ---
with tab_data:
    st.header("Project Database")
    st.dataframe(df[DF_DISPLAY_COLUMNS])

# --- SIDEBAR (Updated to check return value from timeline) ---
if selected:
    # Handle both dict and list returns depending on library behavior
    if isinstance(selected, list):
        selected = selected[0] if len(selected) > 0 else None
    
    if selected:
        # The library returns the item ID as the 'selected' variable or inside it
        paper_id = selected if isinstance(selected, str) else selected.get('id')
        
        try:
            details = df[df['File_Name'] == paper_id].iloc[0]
            score = float(details['Sentiment_Score'])
            normalized_score = normalize_sentiment(score)

            st.sidebar.header("Selected Paper Analysis")
            st.sidebar.subheader(details['Title'])
            st.sidebar.divider()

            st.sidebar.write(f"**Author:** {details['Author']}")
            st.sidebar.write(f"**Year:** {details['Year']}")
            st.sidebar.write(f"**Era:** {details['Era']}")

            st.sidebar.progress(normalized_score, text=f"Sentiment: {score:.2f}")
            st.sidebar.write("### Sentiment Summary")
            st.sidebar.write(details['Final_Sentiment_Summary'])
        except (IndexError, KeyError):
            st.sidebar.info("Select a paper on the timeline to view its analysis.")
else:
    st.sidebar.info("Select a paper on the timeline to view its analysis.")
