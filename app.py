"""
Main Streamlit app for Player Role Dashboard.
"""
import streamlit as st
import pandas as pd
import numpy as np
import unicodedata
from utils.data_loader import (
    load_players_data, 
    load_centroids_data, 
    get_centroids_dict,
    find_similar_players,
    get_top_cluster_probabilities
)
from utils.cluster_mapping import get_cluster_name, get_cluster_description
from utils.visualizations import create_scatter_plot, create_radar_chart


def normalize_text(text):
    """
    Normalize text by removing accents and special characters.
    Converts 'Ødegaard' to 'Odegaard', 'José' to 'Jose', etc.
    """
    if pd.isna(text) or text == "":
        return ""
    # Normalize unicode characters (NFD = Normalization Form Decomposed)
    nfd = unicodedata.normalize('NFD', str(text))
    # Remove combining characters (accents)
    normalized = ''.join(c for c in nfd if unicodedata.category(c) != 'Mn')
    return normalized.lower()


# Page configuration
st.set_page_config(
    page_title="Player Role Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
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

# Sidebar title
st.sidebar.title("⚽ Player Role Dashboard")
st.sidebar.markdown("---")
st.sidebar.header("Filters")

# Cluster filter
all_clusters = sorted(players_df['role_cluster'].unique())
selected_clusters = st.sidebar.multiselect(
    "Filter by Cluster",
    options=all_clusters,
    default=all_clusters,
    format_func=lambda x: f"Cluster {x}"
)

# Filter players by selected clusters
filtered_players_df = players_df[players_df['role_cluster'].isin(selected_clusters)]

# Main title
st.title("⚽ Player Role Dashboard")
st.markdown("Explore player roles and clusters in PCA space")

# Search bar with autocomplete
st.subheader("Search Player")
player_names = sorted(filtered_players_df['Name'].tolist())

# Create normalized search index (name -> normalized_name)
search_index = {name: normalize_text(name) for name in player_names}

# Text input for search
search_query = st.text_input(
    "Type player name to search:",
    value="",
    key="player_search_input",
    placeholder="Start typing a player name..."
)

# Initialize session state for selected player
if 'selected_player' not in st.session_state:
    st.session_state.selected_player = None

# Filter and show suggestions
selected_player_name = None
if search_query:
    # Normalize search query
    normalized_query = normalize_text(search_query)
    
    # Filter names that match the normalized search query
    matching_players = [
        name for name in player_names 
        if normalized_query in search_index[name]
    ]
    
    if matching_players:
        # Always show dropdown with suggestions (even if only one match)
        # This makes it clearer what was selected
        selected_player_name = st.selectbox(
            f"Select from {len(matching_players)} match{'es' if len(matching_players) > 1 else ''}:",
            options=matching_players,
            key="player_autocomplete",
            index=0  # Auto-select first match
        )
        st.session_state.selected_player = selected_player_name
    else:
        st.info(f"No players found matching '{search_query}'")
        st.session_state.selected_player = None
else:
    st.session_state.selected_player = None

# Main layout: Scatter plot and player card
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Player Clusters in PCA Space")
    
    # Create scatter plot
    fig = create_scatter_plot(
        filtered_players_df,
        selected_player=st.session_state.selected_player
    )
    
    st.plotly_chart(fig, width='stretch', config={'displayModeBar': True})
    
    # Note about clicking (Plotly click events can be added later)
    st.caption("💡 Use the search bar above to find and zoom to a player")

with col2:
    st.subheader("Player Information")
    
    if st.session_state.selected_player:
        # Get player data
        player_data = filtered_players_df[filtered_players_df['Name'] == st.session_state.selected_player]
        
        if not player_data.empty:
            player_row = player_data.iloc[0]
            
            # Player card
            st.markdown("### " + player_row['Name'])
            
            # Basic info
            col_info1, col_info2 = st.columns(2)
            with col_info1:
                st.metric("CA", int(player_row['CA']))
            with col_info2:
                st.metric("PA", int(player_row['PA']))
            
            # Club
            if pd.notna(player_row.get('Club')):
                st.write(f"**Club:** {player_row['Club']}")
            
            # Primary cluster
            primary_cluster = int(player_row['role_cluster'])
            cluster_name = get_cluster_name(primary_cluster)
            st.write(f"**Primary Role:** {cluster_name} (Cluster {primary_cluster})")
            
            # Top 3 cluster probabilities
            st.markdown("**Cluster Memberships:**")
            top_probs = get_top_cluster_probabilities(player_row)
            for cluster_id, prob in top_probs:
                cluster_label = get_cluster_name(cluster_id)
                st.write(f"- {cluster_label}: {prob*100:.1f}%")
            
            st.divider()
            
            # Similar players
            st.markdown("### Similar Players")
            similar = find_similar_players(player_row, filtered_players_df, n=5)
            
            if not similar.empty:
                for idx, sim_player in similar.iterrows():
                    with st.expander(f"{sim_player['Name']} ({sim_player.get('Club', 'N/A')})"):
                        st.write(f"**CA:** {int(sim_player['CA'])}")
                        st.write(f"**PA:** {int(sim_player['PA'])}")
                        st.write(f"**Distance:** {sim_player['distance']:.2f}")
            else:
                st.write("No similar players found.")
            
            st.divider()
            
            # Player attributes radar chart
            st.markdown("### Player Attributes")
            
            # Get player attributes (FM attributes)
            fm_attrs = [
                'Pas', 'Tec', 'Vis', 'Dec', 'Fir', 'Dri', 'Fin', 
                'Tck', 'Mar', 'Pos', 'Ant', 'Cmp', 'Cnt', 'Det', 
                'Wor', 'Sta', 'Pac', 'Str'
            ]
            
            player_attrs = {attr: player_row.get(attr, 0) for attr in fm_attrs if attr in player_row}
            
            # Get cluster centroid attributes
            cluster_attrs = centroids_dict.get(primary_cluster, {})
            
            # Create radar chart
            radar_fig = create_radar_chart(
                player_attrs,
                cluster_attrs=cluster_attrs,
                title=f"{player_row['Name']} vs {cluster_name} Centroid"
            )
            
            st.plotly_chart(radar_fig, width='stretch')
            
        else:
            st.warning("Player not found in filtered data.")
    else:
        st.info("👆 Search for a player above to see their details here")
        st.markdown("""
        **Player Card will show:**
        - Basic info (CA, PA, Club)
        - Primary role and cluster memberships
        - Similar players
        - Attribute radar chart
        """)

# Footer
st.markdown("---")
st.caption("Data: Player role clusters with PCA coordinates | Navigate to 'Cluster Info' page for role documentation")

