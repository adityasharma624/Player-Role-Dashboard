"""
Cluster Information and Documentation Page.
"""
import streamlit as st
import pandas as pd
from utils.data_loader import load_players_data, load_centroids_data, get_centroids_dict
from utils.cluster_mapping import (
    get_cluster_name, 
    get_cluster_description,
    get_top_attributes_for_cluster
)
from utils.visualizations import create_cluster_scatter_snippet, create_radar_chart


# Page configuration
st.set_page_config(
    page_title="Cluster Info - Player Role Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for consistent styling
st.markdown("""
    <style>
    /* Consistent styling with main page - compact */
    .main {
        padding-top: 0.5rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    .element-container {
        margin-bottom: 0.5rem;
    }
    
    .stMarkdown {
        margin-bottom: 0.5rem;
    }
    
    h1 {
        color: #1f77b4;
        margin-bottom: 0.5rem;
        font-size: 1.8rem;
    }
    
    h2 {
        color: #1f77b4;
        padding-bottom: 0.3rem;
        border-bottom: 2px solid #e0e0e0;
        margin-top: 1rem;
        margin-bottom: 0.3rem;
        font-weight: 600;
        font-size: 1.3rem;
    }
    
    h3 {
        color: #333;
        margin-top: 0.8rem;
        margin-bottom: 0.3rem;
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    /* Metric styling */
    [data-testid="metric-container"] {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 4px 4px 0 0;
        padding: 10px 20px;
    }
    
    /* Hide Streamlit menu and footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# Load data (cached)
@st.cache_data
def load_data():
    """Load and cache data."""
    players_df = load_players_data()
    centroids_df = load_centroids_data()
    centroids_dict = get_centroids_dict(centroids_df)
    return players_df, centroids_df, centroids_dict


players_df, centroids_df, centroids_dict = load_data()

# Title
st.markdown("""
    <div style='margin-bottom: 1rem;'>
        <h1 style='color: #1f77b4; margin-bottom: 0.3rem; font-size: 1.8rem;'>📊 Cluster Information & Role Documentation</h1>
        <p style='color: #666; font-size: 0.95rem;'>Learn about each player role cluster and their characteristics</p>
    </div>
    """, unsafe_allow_html=True)

# Get all clusters
all_clusters = sorted(players_df['role_cluster'].unique())

# Create tabs for each cluster
tabs = st.tabs([f"Cluster {c}" for c in all_clusters])

for idx, cluster_id in enumerate(all_clusters):
    with tabs[idx]:
        cluster_name = get_cluster_name(cluster_id)
        cluster_desc = get_cluster_description(cluster_id)
        
        # Header
        st.markdown(f"<h2 style='color: #1f77b4; margin-top: 0;'>{cluster_name} <span style='color: #999; font-size: 0.8em; font-weight: normal;'>(Cluster {cluster_id})</span></h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #666; font-size: 1.05rem; font-style: italic; margin-bottom: 1.5rem;'>{cluster_desc}</p>", unsafe_allow_html=True)
        
        # Layout: Two columns
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Top attributes
            st.subheader("Key Attributes")
            top_attrs = get_top_attributes_for_cluster(centroids_dict, cluster_id, n=10)
            
            if top_attrs:
                # Display as metrics or table
                attrs_df = pd.DataFrame(top_attrs, columns=['Attribute', 'Z-Score'])
                attrs_df['Z-Score'] = attrs_df['Z-Score'].round(3)
                attrs_df = attrs_df.sort_values('Z-Score', key=abs, ascending=False)
                
                # Show top 5 as metrics
                st.markdown("<b style='font-size: 1.1rem; color: #333;'>Top 5 Attributes:</b>", unsafe_allow_html=True)
                metric_cols = st.columns(5)
                for i, (attr, z_score) in enumerate(top_attrs[:5]):
                    with metric_cols[i]:
                        st.metric(attr, f"{z_score:.2f}")
                
                # Show all attributes in expander
                with st.expander("View all attributes"):
                    st.dataframe(attrs_df, width='stretch', hide_index=True)
            
            st.markdown("<div style='margin: 0.5rem 0;'></div>", unsafe_allow_html=True)
            
            # Top players in cluster
            st.markdown("<h3 style='color: #333; margin-top: 1.5rem;'>⭐ Top Players by CA</h3>", unsafe_allow_html=True)
            cluster_players = players_df[players_df['role_cluster'] == cluster_id].copy()
            top_players = cluster_players.nlargest(10, 'CA')[['Name', 'Club', 'CA', 'PA']]
            
            if not top_players.empty:
                # Style the dataframe
                st.dataframe(
                    top_players,
                    width='stretch',
                    hide_index=True,
                    column_config={
                        "Name": st.column_config.TextColumn("Player Name", width="medium"),
                        "Club": st.column_config.TextColumn("Club", width="small"),
                        "CA": st.column_config.NumberColumn("CA", format="%d"),
                        "PA": st.column_config.NumberColumn("PA", format="%d")
                    },
                    use_container_width=True
                )
            else:
                st.info("No players found in this cluster.")
        
        with col2:
            # Cluster scatter snippet
            st.subheader("Cluster Visualization")
            cluster_scatter = create_cluster_scatter_snippet(players_df, cluster_id)
            st.plotly_chart(cluster_scatter, width='stretch')
            
            # Cluster statistics
            st.subheader("Statistics")
            cluster_size = len(cluster_players)
            avg_ca = cluster_players['CA'].mean()
            avg_pa = cluster_players['PA'].mean()
            
            st.metric("Players", cluster_size)
            st.metric("Avg CA", f"{avg_ca:.1f}")
            st.metric("Avg PA", f"{avg_pa:.1f}")
        
        st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)
        
        # Radar chart for cluster centroid
        st.subheader("Role Profile (Cluster Centroid)")
        
        cluster_attrs = centroids_dict.get(cluster_id, {})
        if cluster_attrs:
            # Select key attributes for radar chart
            key_attrs = [
                'Pas', 'Tec', 'Vis', 'Dec', 'Fir', 'Dri', 'Fin',
                'Tck', 'Mar', 'Pos', 'Ant', 'Cmp', 'Cnt', 'Det',
                'Wor', 'Sta', 'Pac', 'Str'
            ]
            
            # Filter to available attributes
            available_attrs = {k: v for k, v in cluster_attrs.items() if k in key_attrs}
            
            if available_attrs:
                radar_fig = create_radar_chart(
                    available_attrs,
                    cluster_attrs=None,  # Don't compare, just show cluster
                    title=f"{cluster_name} Role Profile"
                )
                st.plotly_chart(radar_fig, width='stretch')
            else:
                st.info("Attribute data not available for radar chart.")
        else:
            st.warning("Cluster centroid data not found.")

# Footer
st.markdown("---")
st.caption("Navigate back to the main page to explore individual players")

