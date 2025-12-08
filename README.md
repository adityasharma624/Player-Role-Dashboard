# ⚽ Player Role Dashboard

An interactive Streamlit dashboard for visualizing and exploring football player role clusters using Principal Component Analysis (PCA) and clustering techniques. Built with Football Manager 24 data, this tool helps analyze player roles, compare attributes, and discover similar players across Europe's top leagues.

## 🎯 Features

### Main Dashboard (`app.py`)
- **Interactive PCA Scatter Plot**: Visualize players in 2D PCA space, colored by role clusters
- **Smart Player Search**: 
  - Autocomplete search with accent-insensitive matching (e.g., "odegaard" finds "Ødegaard")
  - Clickable suggestion buttons
  - Auto-zoom to selected player
- **Player Information Card**:
  - Current Ability (CA) and Potential Ability (PA)
  - Club information
  - Primary role and cluster membership probabilities
  - Top 5 similar players based on PCA distance
  - Attribute radar chart comparing player vs cluster centroid
- **Cluster Filtering**: Filter players by role clusters via sidebar

### Cluster Information Page (`pages/2_Cluster_Info.py`)
- **Role Documentation**: Detailed information for each of the 5 player role clusters
- **Key Attributes**: Top attributes for each cluster with z-scores
- **Top Players**: Top 10 players by CA for each cluster
- **Cluster Statistics**: Player count, average CA/PA
- **Visualizations**: 
  - Cluster-specific scatter plots
  - Role profile radar charts

## 📊 Player Role Clusters

The dashboard identifies 5 distinct player role clusters:

1. **Deep-Lying Playmaker** (Cluster 0)
   - Deep-lying midfielders who control tempo from deeper positions
   - Strong positioning, tackling, passing, and composure
   - Examples: Kimmich, Koke, Tonali

2. **Creative Playmaker** (Cluster 1)
   - Highly technical creative players with exceptional passing, vision, and decision-making
   - Low physicality but elite technical skills
   - Examples: Modrić, Ødegaard, de Jong

3. **Defensive Anchor** (Cluster 2)
   - Defensive specialists who anchor the team
   - Exceptional marking, tackling, bravery, strength, and positioning
   - Examples: Rice, Casemiro, Camavinga

4. **Box-to-Box Midfielder** (Cluster 3)
   - Dynamic, energetic midfielders with pace and work rate
   - High off-the-ball movement but lower decision-making and composure
   - Examples: Bellingham, Valverde, Barella

5. **Attacking Playmaker** (Cluster 4)
   - Advanced attacking players with high flair, dribbling, technique, and creativity
   - Excellent at free kicks, corners, and set pieces
   - Examples: Bruno Fernandes, Sané, Nkunku

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Player-Role-Dashboard
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 💻 Usage

### Running the Dashboard

**Option 1: Using the run script** (easiest)
```bash
./run.sh
```

**Option 2: Manual command**
```bash
source venv/bin/activate  # Activate virtual environment first
streamlit run app.py
```

**Option 3: One-liner**
```bash
source venv/bin/activate && streamlit run app.py
```

The dashboard will automatically open in your browser at `http://localhost:8501`

### Important Notes
- **Always use `streamlit run app.py`** - do not run `python app.py` directly
- Make sure the virtual environment is activated before running
- The sidebar can be toggled using the hamburger menu icon in the top-left corner

## 📁 Project Structure

```
Player-Role-Dashboard/
├── app.py                      # Main Streamlit application
├── pages/
│   └── 2_Cluster_Info.py      # Cluster documentation page
├── utils/
│   ├── data_loader.py          # CSV loading and preprocessing utilities
│   ├── cluster_mapping.py      # Cluster ID to role name mappings
│   └── visualizations.py       # Plotly visualization functions
├── data/
│   ├── players_with_role_clusters_k5_v1.csv    # Player data with clusters
│   └── cluster_centroids_k5.csv                # Cluster centroid attributes
├── requirements.txt            # Python dependencies
├── run.sh                      # Quick start script
└── README.md                   # This file
```

## 📊 Data

### Dataset Information
- **Source**: Football Manager 24 (FM24)
- **Players**: ~683 players from Europe's top leagues
- **Filtering**: Age ≥ 18, Current Ability ≥ 120
- **Attributes**: 40+ Football Manager attributes including:
  - Physical: Pace, Strength, Stamina, Jumping, etc.
  - Technical: Passing, Dribbling, Finishing, Technique, etc.
  - Mental: Vision, Decisions, Composure, Anticipation, etc.
  - Defensive: Tackling, Marking, Positioning, etc.

### Data Files
- `players_with_role_clusters_k5_v1.csv`: Main player dataset with:
  - Player information (Name, Club, CA, PA, etc.)
  - FM24 attributes (normalized z-scores)
  - Cluster assignments (`role_cluster`: 0-4)
  - Cluster probabilities (`cluster_0_prob` through `cluster_4_prob`)
  - PCA coordinates (`pc1`, `pc2`)

- `cluster_centroids_k5.csv`: Cluster centroid attributes with z-scores for each attribute

## 🛠️ Technologies Used

- **Streamlit**: Web framework for building the dashboard
- **Plotly**: Interactive visualizations (scatter plots, radar charts)
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computations
- **Python 3.8+**: Programming language

## 🎨 Features in Detail

### Search Functionality
- **Accent-insensitive search**: Type "odegaard" to find "Martin Ødegaard"
- **Case-insensitive**: Works with any capitalization
- **Partial matching**: Finds players with matching substrings
- **Visual suggestions**: Clickable buttons showing matching players

### Visualizations
- **PCA Scatter Plot**: 
  - Color-coded by cluster
  - Hover tooltips with player info
  - Auto-zoom to selected player
  - Interactive legend
  
- **Radar Charts**:
  - Compare player attributes vs cluster centroid
  - Key FM24 attributes displayed
  - Normalized to 0-20 scale

### Similar Players Algorithm
- Finds players in the same cluster
- Calculates Euclidean distance in PCA space
- Returns top 5 most similar players
- Shows distance metric for comparison

## 📝 Notes

- The CSV data is static and final - no model retraining is performed
- All visualizations are client-side using Streamlit and Plotly
- The dashboard is optimized for laptop/desktop screens
- Data is cached for performance using Streamlit's `@st.cache_data`

## 🔧 Customization

### Adding New Fields
The player card is designed to be easily extensible. To add new fields (e.g., Nation):

1. Ensure the field exists in `players_with_role_clusters_k5_v1.csv`
2. Add display logic in `app.py` in the player card section
3. The field will automatically appear for all players

### Modifying Cluster Names
Edit `utils/cluster_mapping.py` to update cluster names and descriptions.

## 📄 License

See [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Data sourced from Football Manager 24
- Player role clustering based on PCA and Gaussian Mixture Models
- Built with Streamlit and Plotly

---

**Enjoy exploring player roles!** ⚽📊
