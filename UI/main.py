from setuptools import extentions
import setuptools.extern.packaging # This often forces the namespace to load
import streamlit as st
from streamlit_timeline import st_timeline
import pandas as pd
import os

DF_DISPLAY_COLUMNS = ["Title", "Author", "Year", "Era", "Sentiment_Score", "Sentiment_Hits", "Token_Count", "Tokens"]

st.set_page_config(layout="wide", page_title="Scholarly Evolution Timeline")

# 1. Custom CSS
st.markdown("""
<style>
    .vis-item {
        border-radius: 10px !important;
        background-color: #1e1e1e !important;
        color: white !important;
        font-family: 'Inter', sans-serif;
        border-width: 2px !important;
        padding: 8px !important;
    }
    .vis-item.vis-selected {
        background-color: #333 !important;
        border-color: #ffff00 !important;
        box-shadow: 0 0 15px #ffff0055 !important;
    }
    .vis-group {
        background-color: #0e1117 !important;
        border-bottom: 1px solid #333 !important;
    }
</style>
""", unsafe_allow_html=True)

# 2. Load Data
try:
    df = pd.read_parquet(os.path.join("UI", "static", "all_sentiment_analysis.parquet"))
except FileNotFoundError:
    st.stop()

# Ensure proper types
df['Year'] = df['Year'].astype(int)
df['Sentiment_Score'] = df['Sentiment_Score'].astype(float)

# 3. Sentiment Color Helper (NOW SUPPORTS NEGATIVE VALUES)
def get_sentiment_color(score):
    if score > 0.3:
        return "#00ad5c"  # Green (positive)
    elif score < -0.3:
        return "#e74c3c"  # Red (negative)
    else:
        return "#3498db"  # Blue (neutral)

# Normalize [-1,1] → [0,1] for progress bar
def normalize_sentiment(score):
    return (score + 1) / 2

# 4. Create Era Groups
unique_eras = sorted(df['Era'].dropna().unique())
era_to_id = {era: i for i, era in enumerate(unique_eras)}
groups = [{"id": era_to_id[era], "content": era} for era in unique_eras]

# 5. Timeline Items
items = []
for _, row in df.iterrows():
    score = row['Sentiment_Score']
    color = get_sentiment_color(score)


    display_html = f"""
                        <div style="border-left: 3px solid {color}; padding-left: 6px; color: black; display: block; white-space: normal;
                                    max-width: 230px; word-wrap: break-word; overflow-wrap: break-word; ">
                            <div style="color: {color}; font-size: 0.7em;">{row['Era']}</div>
                            <div style="font-weight: bold; font-size: 0.75em;">{row['Title']}</div>
                            <div style="font-size: 0.7em;">Author: {row['Author']}</div>
                            <div style="font-size: 0.7em;">Sentiment: {score:.2f}</div>
                        </div>
                    """

    items.append({
        "id": row['File_Name'],
        "group": era_to_id.get(row['Era'], 0),
        "content": display_html,
        "start": f"{row['Year']}-01-01",
    })

options = {
    "stack": True,
    "showCurrentTime": True,
    "zoomKey": "ctrlKey",
    "maxHeight": "500px",
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

    ### What You Can Explore
    - 📅 **Timeline View**: Browse papers chronologically and by semantic clusters
    - 📊 **Lexical Visuals**: Compare word usage (Old vs Modern)
    - 📈 **Statistical Analysis**: Track sentiment trends over time
    - 📋 **Dataset Comparison**: Analyze differences between historical and modern discourse

    ### How to Use This Dashboard
    1. Start with the **Timeline View**
    2. Click on a paper to inspect its sentiment and metadata
    3. Use **Dataset Comparison** to understand broader trends

    ### Dataset
    - Collection of scholarly texts across multiple eras
    - Each document processed for:
    - Sentiment score (-1 to 1)
    - Token statistics
    - Semantic clustering

    ### Key Insight
    Preliminary analysis suggests that **modern scholarly discourse differs in tone and lexical structure compared to historical texts**, indicating a shift in framing and narrative style.
    """)
    
    st.info("Tip: Use Ctrl + Scroll in the timeline to zoom and explore different time periods.")

# --- TIMELINE ---
with tab_timeline:
    st.title("Scholarly Timeline by Era")
    selected = st_timeline(items, groups=groups, options=options, height="550px")
    st.caption("Tip: Hold Ctrl + Scroll to zoom. Drag to navigate years.")

with tab_visuals:
    st.header("Lexical Analysis Visuals")

    image_base_path = os.path.join("UI", "static")
    # --- OLD DATASET VISUALS ---
    st.subheader("Old Dataset")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image(os.path.join(image_base_path, "top_15_keywords_historical.png"), caption="Word Count")
    with col2:
        st.image(os.path.join(image_base_path, "word_bubble_historical.png"), caption="Word Bubble")
    with col3:
        st.image(os.path.join(image_base_path, "top_15_common_word_pairs_historical.png"), caption="Bigram Graph")

    st.markdown("---")  # separator

    # --- MODERN DATASET VISUALS ---
    st.subheader("Modern Dataset")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image(os.path.join(image_base_path, "top_15_keywords_modern.png"), caption="Word Count")
    with col2:
        st.image(os.path.join(image_base_path, "word_bubble_modern.png"), caption="Word Bubble")
    with col3:
        st.image(os.path.join(image_base_path, "top_15_common_word_pairs_historical.png"), caption="Bigram Graph")

# --- CHARTS ---
with tab_analysis:
    st.header("📈 Modern vs Historical Dataset Comparison")

    # Split datasets
    old_df = df[df['Era'] == "Historical"]
    modern_df = df[df['Era'] == "Modern"]

    # --- SUMMARY STATS ---
    st.subheader("Summary Statistics (Sentiment Score)")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Historical Dataset")
        st.write(old_df['Sentiment_Score'].describe())

    with col2:
        st.markdown("### Modern Dataset")
        st.write(modern_df['Sentiment_Score'].describe())

    st.markdown("---")

    # --- MEAN COMPARISON ---
    st.subheader("Average Sentiment Comparison")

    mean_df = pd.DataFrame({
        "Dataset": ["Historical", "Modern"],
        "Mean Sentiment": [
            old_df['Sentiment_Score'].mean(),
            modern_df['Sentiment_Score'].mean()
        ]
    }).set_index("Dataset")

    st.bar_chart(mean_df)

    st.markdown("---")

    # --- DISTRIBUTION COMPARISON ---
    st.subheader("Sentiment Distribution Comparison")

    dist_df = pd.DataFrame({
        "Historical": old_df['Sentiment_Score'],
        "Modern": modern_df['Sentiment_Score']
    })

    st.line_chart(dist_df, x_label="Article Number", y_label="Sentiment Score")

    st.markdown("---")

    # --- INTERPRETATION ---
    st.subheader("Key Insights")

    mean_old = old_df['Sentiment_Score'].mean()
    mean_mod = modern_df['Sentiment_Score'].mean()

    if mean_mod > mean_old:
        trend = "more positive"
    elif mean_mod < mean_old:
        trend = "more negative"
    else:
        trend = "similar"

    st.info(f"""
    • The **modern dataset** is overall **{trend}** than the historical dataset.  
    • Historical Mean: {mean_old:.3f}  
    • Modern Mean: {mean_mod:.3f}  
    • Difference: {(mean_mod - mean_old):.3f}  

    Interpretation:
    This suggests a shift in discourse sentiment over time, potentially reflecting
    changes in framing, narrative tone, or research focus.
    """)

# --- DATA ---
with tab_data:
    st.header("Project Database")
    st.dataframe(df[DF_DISPLAY_COLUMNS])
    
  

# --- SIDEBAR ---
if 'selected' in locals() and selected:
    paper_id = selected['id']
    details = df[df['File_Name'] == paper_id].iloc[0]

    score = float(details['Sentiment_Score'])
    normalized_score = normalize_sentiment(score)

    st.sidebar.header("Selected Paper Analysis")
    st.sidebar.subheader(details['Title'])
    st.sidebar.divider()

    st.sidebar.write(f"**Author:** {details['Author']}")
    st.sidebar.write(f"**Year:** {details['Year']}")
    st.sidebar.write(f"**Era:** {details['Era']}")

    st.sidebar.progress(
        normalized_score,
        text=f"Sentiment: {score:.2f} (-1 to 1)"
    )
    score = float(details['Sentiment_Score'])

    st.sidebar.write("### Sentiment Summary")
    st.sidebar.write(details['Final_Sentiment_Summary'])


else:
    st.sidebar.info("Select a paper on the timeline to view its analysis.")
