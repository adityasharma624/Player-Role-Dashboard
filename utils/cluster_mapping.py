"""
Cluster ID to role name mappings and descriptions.
"""
from typing import Dict, Tuple


CLUSTER_NAMES: Dict[int, str] = {
    0: "Deep-Lying Playmaker",
    1: "Creative Playmaker",
    2: "Defensive Anchor",
    3: "Box-to-Box Midfielder",
    4: "Attacking Playmaker"
}

CLUSTER_DESCRIPTIONS: Dict[int, str] = {
    0: "Deep-lying midfielders who control tempo from deeper positions. Strong positioning, tackling, passing, and composure. Examples: Kimmich, Koke, Tonali.",
    1: "Highly technical creative players with exceptional passing, vision, and decision-making. Low physicality but elite technical skills. Examples: Modrić, Ødegaard, de Jong.",
    2: "Defensive specialists who anchor the team. Exceptional marking, tackling, bravery, strength, and positioning. Low technical/creative attributes. Examples: Rice, Casemiro, Camavinga.",
    3: "Dynamic, energetic midfielders with pace and work rate. High off-the-ball movement but lower decision-making and composure. Examples: Bellingham, Valverde, Barella.",
    4: "Advanced attacking players with high flair, dribbling, technique, and creativity. Excellent at free kicks, corners, and set pieces. Low defensive attributes. Examples: Bruno Fernandes, Sané, Nkunku."
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

