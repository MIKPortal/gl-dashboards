import streamlit as st
import pandas as pd
import plotly.express as px
import os

# streamlit run nrdc_missing_anchors_new.py
# 1. Page Configuration (VEGAS Professional Theme)
st.set_page_config(page_title="NRDC Missing Anchors Monitor", layout="wide")

# 2. Data Loading with Caching

@st.cache_data
def load_data():
    # This finds the absolute path of the folder containing THIS script
    base_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_path, '../nrdc_missing_anchors.csv')
    
    # Debug info to help us see where it's looking
    st.sidebar.write(f"Looking for file at: {file_path}")
    
    if os.path.exists(file_path):
        st.sidebar.success("✅ File Found!")
        df = pd.read_csv(file_path)
        df['Distance'] = pd.to_numeric(df['Distance'], errors='coerce')
        return df
    else:
        st.sidebar.error("❌ File Still Not Found")
        # List files in the folder to help troubleshoot
        st.sidebar.write("Files in this folder:", os.listdir(base_path))
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.error("Dataset 'nrdc_missing_anchors.csv' not found. Please ensure the file is in the same directory.")
else:
    st.title("📡 NRDC Missing Anchors Dashboard")
    st.info("Use the sidebar to filter data by distance and market. Data updates automatically.")

    # --- SIDEBAR: FILTERS ---
    st.sidebar.header("Filter Controls")
    
    # Drag Filter for Distance
    min_dist = float(df['Distance'].min())
    max_dist = float(df['Distance'].max())
    dist_range = st.sidebar.slider(
        "Select Distance Range (Drag Filter)",
        min_value=min_dist,
        max_value=max_dist,
        value=(min_dist, max_dist),
        step=0.01
    )

    # Market Multi-select
    all_markets = sorted(df['Market'].unique())
    selected_markets = st.sidebar.multiselect(
        "Select Markets",
        options=all_markets,
        default=all_markets
    )

    # Apply Filters
    filtered_df = df[
        (df['Distance'] >= dist_range[0]) & 
        (df['Distance'] <= dist_range[1]) &
        (df['Market'].isin(selected_markets))
    ]

    # --- TOP ROW: METRICS ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Records", len(filtered_df))
    m2.metric("Unique Markets", filtered_df['Market'].nunique())
    m3.metric("Avg Distance", f"{filtered_df['Distance'].mean():.2f}")
    m4.metric("Max Distance", filtered_df['Distance'].max())

    # --- MIDDLE ROW: CHARTS ---
    st.markdown("### 📊 Visual Analytics")
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        # Market Distribution Chart
        market_counts = filtered_df['Market'].value_counts().reset_index()
        market_counts.columns = ['Market', 'Count']
        fig_market = px.bar(
            market_counts, x='Market', y='Count', 
            color='Market', title="Issues per Market",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig_market, use_container_width=True)

    with col_chart2:
        # Distance Distribution Histogram
        fig_dist = px.histogram(
            filtered_df, x='Distance', nbins=20,
            title="Distance Spread (Source to Target)",
            color_discrete_sequence=['#636EFA']
        )
        st.plotly_chart(fig_dist, use_container_width=True)

    # --- BOTTOM SECTION: DATA TABLE & DOWNLOADS ---
    st.markdown("### 📋 Filtered Data Table")
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

    st.markdown("### 📥 Download Reports")
    dl_col1, dl_col2 = st.columns(2)

    with dl_col1:
        # Download the current filtered view
        csv_filtered = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Filtered Results (CSV)",
            data=csv_filtered,
            file_name="nrdc_filtered_view.csv",
            mime="text/csv",
            help="Downloads only the data currently visible based on your filters."
        )

    with dl_col2:
        # Targeted Market Download
        market_to_export = st.selectbox("Select a specific Market to export:", options=all_markets)
        market_csv = df[df['Market'] == market_to_export].to_csv(index=False).encode('utf-8')
        st.download_button(
            label=f"Download Market {market_to_export} Full Report",
            data=market_csv,
            file_name=f"market_{market_to_export}_report.csv",
            mime="text/csv"
        )
