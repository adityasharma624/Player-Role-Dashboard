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

# Custom CSS for better styling
st.markdown("""
    <style>
    /* Main content padding - reduced top padding */
    .main {
        padding-top: 0.5rem;
    }
    
    /* Improve spacing between sections */
    .element-container {
        margin-bottom: 1rem;
    }
    
    /* Card-like appearance for subheaders */
    h2 {
        color: #1f77b4;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #e0e0e0;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
    }
    
    h3 {
        color: #333;
        margin-top: 1rem;
    }
    
    /* Metric styling */
    [data-testid="metric-container"] {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
    }
    
    /* Improve input spacing */
    .stTextInput, .stSelectbox, .stMultiSelect {
        margin-bottom: 1rem;
    }
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

# Sidebar
st.sidebar.header("🔍 Filters")

# Cluster filter
all_clusters = sorted(players_df['role_cluster'].unique())
selected_clusters = st.sidebar.multiselect(
    "Filter by Cluster",
    options=all_clusters,
    default=all_clusters,
    format_func=lambda x: f"{get_cluster_name(x)} (C{x})"
)

# Filter players by selected clusters
filtered_players_df = players_df[players_df['role_cluster'].isin(selected_clusters)]

# Main title and subtitle
st.markdown("""<div style='text-align: center; margin-bottom: 1rem;'>
    <h1 style='color: #1f77b4; margin-bottom: 0.3rem;'>⚽ Player Role Dashboard</h1>
    <p style='color: #666; font-size: 1.1rem; margin-bottom: 0.5rem;'>Explore player roles and clusters in PCA space</p>
    <p style='color: #999; font-size: 0.9rem;'><em>Dataset: FM24 • Filtered: Age ≥ 18 • Current Ability ≥ 120</em></p>
</div>""", unsafe_allow_html=True)

# Search bar with autocomplete
st.markdown("<h2 style='margin-top: 2rem; margin-bottom: 1rem;'>🔎 Search Player</h2>", unsafe_allow_html=True)
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
    st.markdown("<h2 style='margin-bottom: 1.5rem;'>📊 Player Clusters in PCA Space</h2>", unsafe_allow_html=True)
    
    # Create scatter plot
    fig = create_scatter_plot(
        filtered_players_df,
        selected_player=st.session_state.selected_player
    )
    
    st.plotly_chart(fig, width='stretch', config={'displayModeBar': True})
    
    # Note about clicking (Plotly click events can be added later)
    st.markdown("<p style='text-align: center; color: #666; margin-top: 1rem;'>💡 Use the search bar above to find and zoom to a player</p>", unsafe_allow_html=True)

with col2:
    st.markdown("<h2 style='margin-bottom: 1.5rem;'>👤 Player Information</h2>", unsafe_allow_html=True)
    
    if st.session_state.selected_player:
        # Get player data
        player_data = filtered_players_df[filtered_players_df['Name'] == st.session_state.selected_player]
        
        if not player_data.empty:
            player_row = player_data.iloc[0]
            
            # Player card
            st.markdown(f"<h3 style='color: #1f77b4; margin-bottom: 1.5rem;'>{player_row['Name']}</h3>", unsafe_allow_html=True)
            
            # Basic info
            col_info1, col_info2 = st.columns(2)
            with col_info1:
                st.metric("Current Ability", int(player_row['CA']))
            with col_info2:
                st.metric("Potential Ability", int(player_row['PA']))
            
            st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)
            
            # Club
            if pd.notna(player_row.get('Club')):
                st.markdown(f"<p style='font-size: 1rem; margin: 0.5rem 0;'><b>🏢 Club:</b> {player_row['Club']}</p>", unsafe_allow_html=True)
            
            # Primary cluster
            primary_cluster = int(player_row['role_cluster'])
            cluster_name = get_cluster_name(primary_cluster)
            st.markdown(f"<p style='font-size: 1rem; margin: 0.5rem 0;'><b>⚙️ Primary Role:</b> {cluster_name}</p>", unsafe_allow_html=True)
            
            st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)
            
            # Top 3 cluster probabilities
            st.markdown("<b style='font-size: 1.1rem;'>📈 Cluster Memberships</b>", unsafe_allow_html=True)
            top_probs = get_top_cluster_probabilities(player_row)
            prob_text = ""
            for cluster_id, prob in top_probs:
                cluster_label = get_cluster_name(cluster_id)
                prob_text += f"<p style='margin: 0.3rem 0; padding-left: 1rem;'>• <b>{cluster_label}</b>: {prob*100:.1f}%</p>"
            st.markdown(prob_text, unsafe_allow_html=True)
            
            st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
            
            # Similar players
            st.markdown("<h3 style='color: #333;'>🎯 Similar Players</h3>", unsafe_allow_html=True)
            similar = find_similar_players(player_row, filtered_players_df, n=5)
            
            if not similar.empty:
                for idx, sim_player in similar.iterrows():
                    with st.expander(f"⭐ {sim_player['Name']} ({sim_player.get('Club', 'N/A')})"):
                        col_sim1, col_sim2, col_sim3 = st.columns(3)
                        with col_sim1:
                            st.metric("CA", int(sim_player['CA']))
                        with col_sim2:
                            st.metric("PA", int(sim_player['PA']))
                        with col_sim3:
                            st.metric("Distance", f"{sim_player['distance']:.2f}")
            else:
                st.info("No similar players found.")
            
            st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
            
            # Player attributes radar chart
            st.markdown("<h3 style='color: #333;'>📉 Player Attributes</h3>", unsafe_allow_html=True)
            
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
st.markdown("<p style='text-align: center; color: #999; font-size: 0.9rem; margin-top: 2rem;'>Data: Player role clusters with PCA coordinates | Navigate to <b>'Cluster Info'</b> page for role documentation</p>", unsafe_allow_html=True)

