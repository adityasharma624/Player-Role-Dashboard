"""
Data loading and preprocessing utilities for the Player Role Dashboard.
"""
import pandas as pd
import numpy as np
from pathlib import Path


def load_players_data(data_dir="data"):
    """Load the players CSV file."""
    data_path = Path(__file__).parent.parent / data_dir / "players_with_role_clusters_k5_v1.csv"
    df = pd.read_csv(data_path)
    return df


def load_centroids_data(data_dir="data"):
    """Load the cluster centroids CSV file."""
    data_path = Path(__file__).parent.parent / data_dir / "cluster_centroids_k5.csv"
    df = pd.read_csv(data_path)
    return df


def get_centroids_dict(centroids_df):
    """
    Convert centroids DataFrame to a nested dictionary.
    Returns: {cluster_id: {attr_name: z_score, ...}, ...}
    """
    centroids_dict = {}
    for cluster_id in centroids_df['cluster'].unique():
        cluster_data = centroids_df[centroids_df['cluster'] == cluster_id]
        centroids_dict[cluster_id] = dict(zip(cluster_data['attr'], cluster_data['z']))
    return centroids_dict


def find_similar_players(player_row, players_df, n=5):
    """
    Find similar players based on same cluster and Euclidean distance in PCA space.
    
    Args:
        player_row: Series or dict with player data
        players_df: DataFrame with all players
        n: Number of similar players to return
    
    Returns:
        DataFrame with similar players (excluding the player itself)
    """
    player_cluster = player_row['role_cluster']
    player_pc1 = player_row['pc1']
    player_pc2 = player_row['pc2']
    
    # Filter by same cluster
    same_cluster = players_df[players_df['role_cluster'] == player_cluster].copy()
    
    # Calculate Euclidean distance in PCA space
    same_cluster['distance'] = np.sqrt(
        (same_cluster['pc1'] - player_pc1)**2 + 
        (same_cluster['pc2'] - player_pc2)**2
    )
    
    # Exclude the player itself if present
    if 'Name' in player_row:
        same_cluster = same_cluster[same_cluster['Name'] != player_row['Name']]
    
    # Sort by distance and return top n
    similar = same_cluster.nsmallest(n, 'distance')
    
    return similar[['Name', 'Club', 'CA', 'PA', 'role_cluster', 'distance']]


def get_top_cluster_probabilities(player_row):
    """
    Get top 3 cluster probabilities for a player.
    
    Returns:
        List of tuples: [(cluster_id, probability), ...] sorted by probability descending
    """
    prob_cols = [f'cluster_{i}_prob' for i in range(5)]
    probs = [(i, player_row[col]) for i, col in enumerate(prob_cols)]
    probs.sort(key=lambda x: x[1], reverse=True)
    return probs[:3]

