"""
Visualization utilities using Plotly.
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Optional, Dict, List


def create_scatter_plot(players_df: pd.DataFrame, 
                        selected_player: Optional[str] = None,
                        highlight_cluster: Optional[int] = None) -> go.Figure:
    """
    Create interactive scatter plot of players in PCA space.
    
    Args:
        players_df: DataFrame with player data
        selected_player: Name of player to highlight/zoom to
        highlight_cluster: Optional cluster ID to highlight
    
    Returns:
        Plotly figure
    """
    # Color mapping for clusters
    cluster_colors = {
        0: '#1f77b4',  # Blue
        1: '#ff7f0e',  # Orange
        2: '#2ca02c',  # Green
        3: '#d62728',  # Red
        4: '#9467bd'   # Purple
    }
    
    fig = go.Figure()
    
    # Create traces for each cluster
    for cluster_id in sorted(players_df['role_cluster'].unique()):
        cluster_data = players_df[players_df['role_cluster'] == cluster_id]
        
        # Determine if this cluster should be highlighted
        is_selected = (highlight_cluster is not None and cluster_id == highlight_cluster)
        opacity = 1.0 if is_selected else 0.6
        
        fig.add_trace(go.Scatter(
            x=cluster_data['pc1'],
            y=cluster_data['pc2'],
            mode='markers',
            name=f'Cluster {cluster_id}',
            marker=dict(
                color=cluster_colors.get(cluster_id, '#888888'),
                size=8,
                opacity=opacity,
                line=dict(width=0.5, color='white')
            ),
            text=cluster_data.apply(
                lambda row: f"<b>{row['Name']}</b><br>Club: {row.get('Club', 'N/A')}<br>Cluster: {row['role_cluster']}",
                axis=1
            ),
            hovertemplate='%{text}<extra></extra>',
            customdata=cluster_data['Name']
        ))
    
    # Highlight selected player if provided
    if selected_player:
        player_data = players_df[players_df['Name'] == selected_player]
        if not player_data.empty:
            player_row = player_data.iloc[0]
            fig.add_trace(go.Scatter(
                x=[player_row['pc1']],
                y=[player_row['pc2']],
                mode='markers',
                name='Selected Player',
                marker=dict(
                    color='yellow',
                    size=20,
                    symbol='star',
                    line=dict(width=2, color='black')
                ),
                hovertemplate=f'<b>{selected_player}</b><extra></extra>'
            ))
            
            # Zoom to player (with some padding)
            pc1_range = [player_row['pc1'] - 2, player_row['pc1'] + 2]
            pc2_range = [player_row['pc2'] - 2, player_row['pc2'] + 2]
            fig.update_xaxes(range=pc1_range)
            fig.update_yaxes(range=pc2_range)
    
    fig.update_layout(
        title='Player Role Clusters in PCA Space',
        xaxis_title='PC1',
        yaxis_title='PC2',
        hovermode='closest',
        template='plotly_white',
        height=600,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig


def create_radar_chart(player_attrs: Dict[str, float],
                      cluster_attrs: Optional[Dict[str, float]] = None,
                      title: str = "Player Attributes") -> go.Figure:
    """
    Create a radar chart comparing player attributes vs cluster centroid.
    
    Args:
        player_attrs: Dictionary of {attr_name: value} for player (z-scores)
        cluster_attrs: Optional dictionary of cluster centroid attributes (z-scores)
        title: Chart title
    
    Returns:
        Plotly figure
    """
    # FM attribute columns - key technical and mental attributes
    key_attrs = ['Pas', 'Tec', 'Vis', 'Dec', 'Fir', 'Dri', 'Fin', 'Tck', 'Mar', 'Pos', 'Ant', 'Cmp']
    
    # Filter to available attributes
    available_attrs = [attr for attr in key_attrs if attr in player_attrs]
    
    if not available_attrs:
        # Fallback to any available attributes (limit to 12 for readability)
        available_attrs = list(player_attrs.keys())[:12]
    
    if not available_attrs:
        # Return empty figure if no attributes
        fig = go.Figure()
        fig.add_annotation(text="No attribute data available", showarrow=False)
        return fig
    
    theta = available_attrs
    player_values = [player_attrs.get(attr, 0) for attr in theta]
    
    fig = go.Figure()
    
    # Normalize z-scores to 0-20 scale (FM attribute scale)
    # Z-scores typically range from -3 to +3, map to 0-20 scale
    # Formula: normalized = 10 + (z_score * 3.33) clamped to [0, 20]
    player_values_normalized = [max(0, min(20, 10 + v * 3.33)) for v in player_values]
    
    fig.add_trace(go.Scatterpolar(
        r=player_values_normalized,
        theta=theta,
        fill='toself',
        name='Player',
        line_color='#1f77b4',
        fillcolor='rgba(31, 119, 180, 0.3)'
    ))
    
    if cluster_attrs:
        cluster_values = [cluster_attrs.get(attr, 0) for attr in theta]
        cluster_values_normalized = [max(0, min(20, 10 + v * 3.33)) for v in cluster_values]
        
        fig.add_trace(go.Scatterpolar(
            r=cluster_values_normalized,
            theta=theta,
            fill='toself',
            name='Cluster Centroid',
            line_color='#ff7f0e',
            fillcolor='rgba(255, 127, 14, 0.3)'
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 20],
                tickmode='linear',
                tick0=0,
                dtick=5
            )),
        showlegend=True,
        title=title,
        height=400
    )
    
    return fig


def create_cluster_scatter_snippet(players_df: pd.DataFrame, cluster_id: int) -> go.Figure:
    """Create a small scatter plot snippet for a specific cluster."""
    cluster_data = players_df[players_df['role_cluster'] == cluster_id]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=cluster_data['pc1'],
        y=cluster_data['pc2'],
        mode='markers',
        marker=dict(
            color='#1f77b4',
            size=6,
            opacity=0.7
        ),
        text=cluster_data['Name'],
        hovertemplate='%{text}<extra></extra>'
    ))
    
    fig.update_layout(
        title=f'Cluster {cluster_id} Players',
        xaxis_title='PC1',
        yaxis_title='PC2',
        height=250,
        margin=dict(l=40, r=40, t=40, b=40),
        template='plotly_white'
    )
    
    return fig

