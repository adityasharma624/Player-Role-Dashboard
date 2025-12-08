"""
Cluster ID to role name mappings and descriptions.
"""
from typing import Dict, Tuple


CLUSTER_NAMES: Dict[int, str] = {
    0: "Deep Controller",
    1: "Final-Third Creator",
    2: "Defensive Anchor",
    3: "Wide Attacker",
    4: "Box-to-Box Engine"
}

CLUSTER_DESCRIPTIONS: Dict[int, str] = {
    0: "Deep-lying playmakers who control the tempo from deeper positions. Strong passing, vision, and positioning.",
    1: "Creative players who operate in the final third. Excellent passing, vision, and technical ability.",
    2: "Defensive specialists who anchor the team. Strong physical attributes, tackling, marking, and positioning.",
    3: "Wide attacking players with pace, dribbling, and finishing ability. Operate in wide areas and attack spaces.",
    4: "Dynamic midfielders who cover ground. Balance of defensive and attacking attributes with good stamina."
}


def get_cluster_name(cluster_id: int) -> str:
    """Get human-readable cluster name."""
    return CLUSTER_NAMES.get(cluster_id, f"Cluster {cluster_id}")


def get_cluster_description(cluster_id: int) -> str:
    """Get cluster description."""
    return CLUSTER_DESCRIPTIONS.get(cluster_id, "No description available.")


def get_top_attributes_for_cluster(centroids_dict: Dict[int, Dict[str, float]], 
                                   cluster_id: int, 
                                   n: int = 5) -> list:
    """
    Get top N attributes for a cluster based on z-scores.
    
    Returns:
        List of tuples: [(attr_name, z_score), ...] sorted by z-score descending
    """
    if cluster_id not in centroids_dict:
        return []
    
    attrs = centroids_dict[cluster_id]
    # Sort by absolute z-score (high positive or high negative both matter)
    sorted_attrs = sorted(attrs.items(), key=lambda x: abs(x[1]), reverse=True)
    return sorted_attrs[:n]

