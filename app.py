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
    Handles special cases like Ø, ø, and other non-ASCII characters.
    """
    if pd.isna(text) or text == "":
        return ""
    
    text_str = str(text)
    
    # Manual mapping for common special characters that don't decompose properly
    special_char_map = {
        'Ø': 'O', 'ø': 'o',
        'Ö': 'O', 'ö': 'o',
        'Ü': 'U', 'ü': 'u',
        'Ä': 'A', 'ä': 'a',
        'Å': 'A', 'å': 'a',
        'É': 'E', 'é': 'e',
        'È': 'E', 'è': 'e',
        'Ê': 'E', 'ê': 'e',
        'Ë': 'E', 'ë': 'e',
        'Í': 'I', 'í': 'i',
        'Ì': 'I', 'ì': 'i',
        'Î': 'I', 'î': 'i',
        'Ï': 'I', 'ï': 'i',
        'Ó': 'O', 'ó': 'o',
        'Ò': 'O', 'ò': 'o',
        'Ô': 'O', 'ô': 'o',
        'Õ': 'O', 'õ': 'o',
        'Ú': 'U', 'ú': 'u',
        'Ù': 'U', 'ù': 'u',
        'Û': 'U', 'û': 'u',
        'Ç': 'C', 'ç': 'c',
        'Ñ': 'N', 'ñ': 'n',
        'Ş': 'S', 'ş': 's',
        'İ': 'I', 'ı': 'i',
        'Ğ': 'G', 'ğ': 'g',
    }
    
    # Replace special characters
    for special, replacement in special_char_map.items():
        text_str = text_str.replace(special, replacement)
    
    # Normalize unicode characters (NFD = Normalization Form Decomposed)
    nfd = unicodedata.normalize('NFD', text_str)
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
        border-bottom: 2px solid #e0e0e0;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    
    h3 {
        color: #333;
        margin-top: 1rem;
        font-weight: 600;
    }
    
    /* Metric styling */
    [data-testid="metric-container"] {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.15);
    }
    
    /* Improve input spacing */
    .stTextInput, .stSelectbox, .stMultiSelect {
        margin-bottom: 1rem;
    }
    
    /* Autocomplete button styling */
    .stButton > button {
        border-radius: 6px;
        border: 1px solid #ddd;
        transition: all 0.2s;
        font-weight: 500;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-color: #1f77b4;
    }
    
    /* Sidebar improvements */
    .css-1d391kg {
        padding-top: 1rem;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        font-weight: 500;
        color: #1f77b4;
    }
    
    /* Info boxes */
    .stInfo {
        border-left: 4px solid #1f77b4;
        padding: 1rem;
        border-radius: 4px;
    }
    
    /* Warning boxes */
    .stWarning {
        border-left: 4px solid #ff9800;
    }
    
    /* Footer styling */
    footer {
        visibility: hidden;
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

# Pages heading
st.markdown("<h1 style='color: #1f77b4; margin-bottom: 0.5rem; font-size: 1.8rem;'>Pages</h1>", unsafe_allow_html=True)

# Main title and subtitle
st.markdown("""<div style='text-align: center; margin-bottom: 0.5rem;'>
    <h2 style='color: #1f77b4; margin-bottom: 0.2rem; font-size: 1.5rem;'>⚽ Player Role Dashboard</h2>
    <p style='color: #666; font-size: 0.95rem; margin-bottom: 0.3rem;'>Explore player roles and clusters in PCA space</p>
    <p style='color: #999; font-size: 0.85rem;'><em>Dataset: FM24 • Filtered: Age ≥ 18 • Current Ability ≥ 120</em></p>
</div>""", unsafe_allow_html=True)

# Search bar with autocomplete
st.markdown("<h2 style='margin-top: 2rem; margin-bottom: 1rem;'>🔎 Search Player</h2>", unsafe_allow_html=True)
player_names = sorted(filtered_players_df['Name'].tolist())

# Create normalized search index (name -> normalized_name)
search_index = {name: normalize_text(name) for name in player_names}

# Initialize session state
if 'selected_player' not in st.session_state:
    st.session_state.selected_player = None
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""

# Text input for search
search_query = st.text_input(
    "Type player name to search:",
    value=st.session_state.search_query,
    key="player_search_input",
    placeholder="Start typing a player name (e.g., 'odegaard' finds 'Ødegaard')..."
)

# Update session state
st.session_state.search_query = search_query

# Filter and show suggestions
selected_player_name = None
matching_players = []

if search_query:
    # Normalize search query
    normalized_query = normalize_text(search_query)
    
    # Filter names that match the normalized search query
    matching_players = [
        name for name in player_names 
        if normalized_query in search_index[name]
    ]
    
    if matching_players:
        # Show autocomplete suggestions as clickable buttons
        st.markdown(f"<p style='color: #666; font-size: 0.9rem; margin-top: 0.5rem; margin-bottom: 0.5rem;'><b>{len(matching_players)}</b> match{'es' if len(matching_players) > 1 else ''} found:</p>", unsafe_allow_html=True)
        
        # Display suggestions in a grid
        cols_per_row = 3
        for i in range(0, min(len(matching_players), 9), cols_per_row):  # Show max 9 suggestions
            cols = st.columns(cols_per_row)
            for j, col in enumerate(cols):
                if i + j < len(matching_players):
                    player_name = matching_players[i + j]
                    with col:
                        # Highlight if this is the selected player
                        is_selected = (st.session_state.selected_player == player_name)
                        button_style = "background-color: #1f77b4; color: white;" if is_selected else "background-color: #f0f0f0; color: #333;"
                        if st.button(
                            player_name,
                            key=f"player_btn_{i+j}",
                            use_container_width=True
                        ):
                            st.session_state.selected_player = player_name
                            st.session_state.search_query = player_name
                            st.rerun()
        
        # If more than 9 matches, show message
        if len(matching_players) > 9:
            st.info(f"... and {len(matching_players) - 9} more. Type more characters to narrow down.")
        
        # Auto-select first match if only one result
        if len(matching_players) == 1:
            st.session_state.selected_player = matching_players[0]
            selected_player_name = matching_players[0]
        elif st.session_state.selected_player in matching_players:
            selected_player_name = st.session_state.selected_player
        else:
            # Clear selection if current selection is not in matches
            st.session_state.selected_player = None
    else:
        st.info(f"No players found matching '{search_query}'. Try typing 'odegaard' to find 'Ødegaard'.")
        st.session_state.selected_player = None
else:
    st.session_state.selected_player = None

# Set selected player
if st.session_state.selected_player:
    selected_player_name = st.session_state.selected_player

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
    st.markdown("<p style='text-align: center; color: #666; margin-top: 1rem;'>🎯 Hover over clusters to explore • Search above to zoom to a player</p>", unsafe_allow_html=True)

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
            st.markdown("<h3 style='color: #333; margin-top: 1.5rem;'>🎯 Similar Players</h3>", unsafe_allow_html=True)
            st.markdown("<p style='color: #666; font-size: 0.9rem; margin-bottom: 1rem;'>Players in the same cluster with closest PCA distance</p>", unsafe_allow_html=True)
            similar = find_similar_players(player_row, filtered_players_df, n=5)
            
            if not similar.empty:
                for idx, sim_player in similar.iterrows():
                    cluster_id = int(sim_player['role_cluster'])
                    cluster_label = get_cluster_name(cluster_id)
                    with st.expander(f"⭐ {sim_player['Name']} ({sim_player.get('Club', 'N/A')}) - {cluster_label}"):
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
        st.markdown("""
        <div style='background-color: #f8f9fa; padding: 2rem; border-radius: 8px; border-left: 4px solid #1f77b4; text-align: center;'>
            <p style='font-size: 1.2rem; color: #666; margin-bottom: 1rem;'>👆 Search for a player above</p>
            <p style='color: #999; font-size: 0.95rem;'>The player card will display:</p>
            <ul style='text-align: left; color: #666; margin-top: 1rem; padding-left: 2rem;'>
                <li>Basic info (CA, PA, Club)</li>
                <li>Primary role and cluster memberships</li>
                <li>Similar players in PCA space</li>
                <li>Attribute radar chart vs cluster centroid</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: #999; font-size: 0.9rem; margin-top: 2rem;'>Data: Player role clusters with PCA coordinates | Navigate to <b>'Cluster Info'</b> page for role documentation</p>", unsafe_allow_html=True)

