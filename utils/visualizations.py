"""
Visualization utilities using Plotly.
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Optional, Dict, List
from utils.cluster_mapping import get_cluster_name
import streamlit as st


def get_plotly_template():
    """Get Plotly template - use 'plotly' which adapts to page background."""
    # Use 'plotly' template which will adapt to transparent backgrounds
    # The page background will show through, making it theme-aware
    return 'plotly'


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
        
        cluster_name = get_cluster_name(cluster_id)
        
        fig.add_trace(go.Scatter(
            x=cluster_data['pc1'],
            y=cluster_data['pc2'],
            mode='markers',
            name=f'{cluster_name} (C{cluster_id})',
            marker=dict(
                color=cluster_colors.get(cluster_id, '#888888'),
                size=10,
                opacity=opacity,
                line=dict(width=1, color='white'),
                symbol='circle'
            ),
            text=cluster_data.apply(
                lambda row: f"<b>{row['Name']}</b><br>Club: {row.get('Club', 'N/A')}<br>Role: {cluster_name}",
                axis=1
            ),
            hovertemplate='%{text}<extra></extra>',
            customdata=cluster_data['Name'],
            hoverinfo='text'
        ))
    
    # Highlight selected player if provided
    if selected_player:
        player_data = players_df[players_df['Name'] == selected_player]
        if not player_data.empty:
            player_row = player_data.iloc[0]
            fig.add_trace(go.Scatter(
                x=[player_row['pc1']],
                y=[player_row['pc2']],
                mode='markers+text',
                name='Selected Player',
                marker=dict(
                    color='gold',
                    size=25,
                    symbol='star',
                    line=dict(width=2.5, color='#FFD700')
                ),
                text=['⭐'],
                textposition='middle center',
                textfont=dict(size=16),
                hovertemplate=f'<b>{selected_player}</b><extra></extra>'
            ))
            
            # Zoom to player (with some padding)
            pc1_range = [player_row['pc1'] - 2, player_row['pc1'] + 2]
            pc2_range = [player_row['pc2'] - 2, player_row['pc2'] + 2]
            fig.update_xaxes(range=pc1_range)
            fig.update_yaxes(range=pc2_range)
    
    # Use plotly template - will be updated by JavaScript if dark mode detected
    fig.update_layout(
        title=None,
        xaxis_title='PC1',
        yaxis_title='PC2',
        hovermode='closest',
        template='plotly',  # Base template, JavaScript will update if needed
        height=600,
        font=dict(size=12, family='Arial, sans-serif'),
        margin=dict(l=60, r=40, t=50, b=60),
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent - adapts to theme
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent - adapts to theme
        legend=dict(
            orientation="v",
            yanchor="bottom",
            y=0.01,
            xanchor="right",
            x=0.99,
            bgcolor='rgba(255, 255, 255, 0.85)',
            bordercolor='#1f77b4',
            borderwidth=2,
            font=dict(size=10)
        ),
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            zeroline=False,
            showline=True,
            linewidth=2,
            mirror=True
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            zeroline=False,
            showline=True,
            linewidth=2,
            mirror=True
        ),
        hoverlabel=dict(
            font_size=13,
            font_family='Arial'
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
            ),
            angularaxis=dict(),
            bgcolor='rgba(0,0,0,0)'  # Transparent - adapts to theme
        ),
        template='plotly',  # Base template, JavaScript will update if needed
        showlegend=True,
        title=dict(
            text=title,
            font=dict(size=14)
        ),
        height=400,
        font=dict(size=11),
        margin=dict(l=50, r=50, t=60, b=50),
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent - adapts to theme
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent - adapts to theme
        legend=dict(
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor='#e0e0e0',
            borderwidth=1
        )
    )
    
    return fig


def create_cluster_scatter_snippet(players_df: pd.DataFrame, cluster_id: int) -> go.Figure:
    """Create a small scatter plot snippet for a specific cluster."""
    cluster_data = players_df[players_df['role_cluster'] == cluster_id]
    
    fig = go.Figure()
    
    cluster_name = get_cluster_name(cluster_id)
    
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
        title=dict(
            text=f'{cluster_name} Players',
            font=dict(size=12)
        ),
        xaxis_title='PC1',
        yaxis_title='PC2',
        height=250,
        margin=dict(l=40, r=40, t=40, b=40),
        template='plotly',  # Base template, JavaScript will update if needed
        font=dict(size=10),
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent - adapts to theme
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent - adapts to theme
        xaxis=dict(
            showgrid=True,
            gridwidth=1
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1
        )
    )
    
    return fig

