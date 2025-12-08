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
st.title("📊 Cluster Information & Role Documentation")
st.markdown("Learn about each player role cluster and their characteristics")

# Get all clusters
all_clusters = sorted(players_df['role_cluster'].unique())

# Create tabs for each cluster
tabs = st.tabs([f"Cluster {c}" for c in all_clusters])

for idx, cluster_id in enumerate(all_clusters):
    with tabs[idx]:
        cluster_name = get_cluster_name(cluster_id)
        cluster_desc = get_cluster_description(cluster_id)
        
        # Header
        st.header(f"{cluster_name} (Cluster {cluster_id})")
        st.markdown(f"*{cluster_desc}*")
        
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
                st.markdown("**Top 5 Attributes:**")
                metric_cols = st.columns(5)
                for i, (attr, z_score) in enumerate(top_attrs[:5]):
                    with metric_cols[i]:
                        st.metric(attr, f"{z_score:.2f}")
                
                # Show all attributes in expander
                with st.expander("View all attributes"):
                    st.dataframe(attrs_df, width='stretch', hide_index=True)
            
            st.divider()
            
            # Top players in cluster
            st.subheader("Top Players by CA")
            cluster_players = players_df[players_df['role_cluster'] == cluster_id].copy()
            top_players = cluster_players.nlargest(10, 'CA')[['Name', 'Club', 'CA', 'PA']]
            
            if not top_players.empty:
                st.dataframe(
                    top_players,
                    width='stretch',
                    hide_index=True,
                    column_config={
                        "Name": st.column_config.TextColumn("Player Name", width="medium"),
                        "Club": st.column_config.TextColumn("Club", width="small"),
                        "CA": st.column_config.NumberColumn("CA", format="%d"),
                        "PA": st.column_config.NumberColumn("PA", format="%d")
                    }
                )
            else:
                st.write("No players found in this cluster.")
        
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
        
        st.divider()
        
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

