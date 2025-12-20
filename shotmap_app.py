import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from mplsoccer import VerticalPitch
from PIL import Image
import urllib.request
import numpy as np

# --- 1. CONFIGURATION & DESIGN ---
st.set_page_config(
    page_title="ShotMap Pro | Analytics",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Avancé pour un look "Dark Football Analytics"
st.markdown("""
<style>
    /* Fond global */
    .stApp {
        background-color: #0e1117;
        background-image: radial-gradient(#1c202b 20%, #0e1117 80%);
    }
    
    /* Titres */
    h1, h2, h3 {
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 800;
        letter-spacing: -1px;
    }
    h1 {
        background: -webkit-linear-gradient(45deg, #00d2ff, #3a7bd5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding-bottom: 20px;
    }
    
    /* Cards (Métriques) */
    div[data-testid="metric-container"] {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 10px;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        border-color: #3a7bd5;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0b0e13;
        border-right: 1px solid #1f2937;
    }
    
    /* Plot styling */
    .plot-container {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 10px 20px rgba(0,0,0,0.5);
    }
</style>
""", unsafe_allow_html=True)

# --- 2. DONNÉES & CONFIGURATION ---

LEAGUE_THEMES = {
    'LIGUE 1': {'id': 53, 'color': '#dae025', 'gradient': ['#0f1923', '#203c25', '#dae025']},
    'PREMIER LEAGUE': {'id': 47, 'color': '#3d195b', 'gradient': ['#180824', '#3d195b', '#e90052', '#00ff85']},
    'LA LIGA': {'id': 87, 'color': '#ff4b44', 'gradient': ['#140505', '#7a1815', '#ff4b44']},
    'BUNDESLIGA': {'id': 54, 'color': '#d3010c', 'gradient': ['#120203', '#5e060a', '#d3010c']},
    'SERIE A': {'id': 55, 'color': '#008fd7', 'gradient': ['#020914', '#004569', '#008fd7']},
    'CHAMPIONS LEAGUE': {'id': 42, 'color': '#38bdf8', 'gradient': ['#001967', '#0f3da8', '#38bdf8']}
}

@st.cache_data
def load_mock_data():
    """Génère des données réalistes si pas de CSV"""
    np.random.seed(42)
    # Création de profils de joueurs fictifs
    players = [
        {'name': 'Kylian Mbappé', 'team_id': 9825, 'volume': 120, 'accuracy': 0.18, 'role': 'Striker'},
        {'name': 'Erling Haaland', 'team_id': 8456, 'volume': 110, 'accuracy': 0.22, 'role': 'Striker'},
        {'name': 'Harry Kane', 'team_id': 9823, 'volume': 100, 'accuracy': 0.20, 'role': 'Striker'},
        {'name': 'Vinícius Jr', 'team_id': 8633, 'volume': 90, 'accuracy': 0.15, 'role': 'Winger'},
        {'name': 'Mohamed Salah', 'team_id': 8650, 'volume': 95, 'accuracy': 0.17, 'role': 'Winger'},
        {'name': 'Lautaro Martínez', 'team_id': 8636, 'volume': 85, 'accuracy': 0.16, 'role': 'Striker'},
        {'name': 'Ousmane Dembélé', 'team_id': 9847, 'volume': 60, 'accuracy': 0.08, 'role': 'Winger'},
        {'name': 'Jude Bellingham', 'team_id': 8633, 'volume': 70, 'accuracy': 0.19, 'role': 'Midfield'}
    ]
    
    all_shots = []
    for p in players:
        n_shots = int(p['volume'])
        # Simulation positions (plus de tirs proches du but et au centre)
        x_locs = np.random.beta(5, 2, n_shots) * 50 + 70 # Tirs entre 70m et 120m
        y_locs = np.random.normal(34, 12, n_shots) # Centré sur 34 (milieu largeur)
        y_locs = np.clip(y_locs, 0, 68)
        
        # Simulation xG basé sur la distance
        dist_to_goal = np.sqrt((120 - x_locs)**2 + (34 - y_locs)**2)
        xgs = 0.8 * np.exp(-0.06 * dist_to_goal) + np.random.uniform(0, 0.1, n_shots)
        
        # Simulation Buts
        is_goal = np.random.rand(n_shots) < (xgs * (1 + np.random.uniform(-0.1, 0.1)))
        events = ['Goal' if g else 'Miss' for g in is_goal]
        
        df_p = pd.DataFrame({
            'joueur': p['name'],
            'joueur_id': hash(p['name']),
            'equipe_id': p['team_id'],
            'position_x': x_locs, # Standard StatsBomb/Opta souvent 100x100 ou 120x80, ici on adapte pour mplsoccer vertical
            'position_y': y_locs,
            'xg': xgs,
            'type_evenement': events
        })
        all_shots.append(df_p)
        
    return pd.concat(all_shots).reset_index(drop=True)

# --- 3. MOTEUR GRAPHIQUE ---

def create_pro_shotmap(data, player_name, theme, is_solo=False):
    """Crée une shotmap haute définition"""
    player_data = data[data['joueur'] == player_name]
    
    # Couleurs
    bg_color = theme['gradient'][0]
    line_color = "white"
    cmap = mcolors.LinearSegmentedColormap.from_list("Heat", theme['gradient'], N=100)
    
    # Configuration taille selon le mode
    figsize = (10, 12) if is_solo else (6, 8)
    
    fig, ax = plt.subplots(figsize=figsize, facecolor=bg_color)
    ax.set_facecolor(bg_color)
    
    # Terrain Vertical (UEFA dims: 105x68)
    pitch = VerticalPitch(
        pitch_type='custom', 
        pitch_length=105, 
        pitch_width=68,
        half=True, 
        goal_type='box',
        line_color=line_color,
        linewidth=1.5,
        spot_scale=0.00
    )
    pitch.draw(ax=ax)
    
    # 1. Hexbin (Densité)
    # On inverse X et Y pour VerticalPitch si nécessaire selon la source de données
    # Ici on assume que position_x est la longueur (0-105) et y la largeur (0-68)
    pitch.hexbin(
        x=player_data['position_x'], 
        y=player_data['position_y'], 
        ax=ax, 
        edgecolors='none', 
        gridsize=(16, 16), 
        cmap=cmap, 
        alpha=0.7,
        zorder=1
    )
    
    # 2. Scatter plot pour les BUTS (Étoiles)
    goals = player_data[player_data['type_evenement'] == 'Goal']
    pitch.scatter(
        goals['position_x'], 
        goals['position_y'],
        ax=ax,
        s=150 if is_solo else 80,
        marker='*',
        color='#00ff00',
        edgecolor='black',
        linewidth=1,
        zorder=2,
        label='Buts'
    )
    
    # Stats dans le graphique
    total_shots = len(player_data)
    total_goals = len(goals)
    total_xg = player_data['xg'].sum()
    
    # En-tête du graphique
    ax.text(34, 112, player_name.upper(), ha='center', fontsize=20 if is_solo else 14, 
            fontweight='bold', color='white')
            
    stats_text = f"Tirs: {total_shots} | Buts: {total_goals} | xG: {total_xg:.2f}"
    ax.text(34, 108, stats_text, ha='center', fontsize=10 if is_solo else 8, 
            color=theme['color'], fontweight='bold')

    return fig

# --- 4. APPLICATION PRINCIPALE ---

def main():
    st.title("🚀 FOOTBALL SHOTMAP PRO")
    
    # --- SIDEBAR ---
    with st.sidebar:
        st.header("⚙️ Paramètres")
        
        selected_league = st.selectbox("Ligue", list(LEAGUE_THEMES.keys()), index=1)
        theme = LEAGUE_THEMES[selected_league]
        
        st.divider()
        
        ranking_mode = st.radio(
            "Trier les joueurs par :",
            ("Meilleurs Buteurs (Buts)", "Volume de Tirs", "Dangerousity (xG Total)")
        )
        
        st.divider()
        
        view_mode = st.selectbox(
            "Mode d'affichage",
            ("Vue Grille (Top Joueurs)", "Duel (1 vs 1)", "Focus Solo")
        )

        # Filtre Slider
        if view_mode == "Vue Grille (Top Joueurs)":
            num_players = st.slider("Nombre de joueurs à afficher", 2, 8, 4)
    
    # Chargement Data
    df = load_mock_data()
    
    # Logique de Tri
    df_grouped = df.groupby('joueur').agg({
        'type_evenement': lambda x: (x == 'Goal').sum(),
        'xg': 'sum',
        'joueur_id': 'count' # Count total rows = total shots
    }).rename(columns={'joueur_id': 'shots', 'type_evenement': 'goals', 'xg': 'total_xg'})
    
    if "Buts" in ranking_mode:
        sorted_players = df_grouped.sort_values('goals', ascending=False).index.tolist()
    elif "Tirs" in ranking_mode:
        sorted_players = df_grouped.sort_values('shots', ascending=False).index.tolist()
    else:
        sorted_players = df_grouped.sort_values('total_xg', ascending=False).index.tolist()

    # --- AFFICHAGE PRINCIPAL ---
    
    # 1. MODE FOCUS SOLO
    if view_mode == "Focus Solo":
        col_select, col_space = st.columns([1, 2])
        with col_select:
            selected_player = st.selectbox("Choisir un joueur", sorted_players)
        
        # Stats Cards
        p_stats = df_grouped.loc[selected_player]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Buts", p_stats['goals'])
        c2.metric("xG Total", f"{p_stats['total_xg']:.2f}")
        c3.metric("Tirs", p_stats['shots'])
        c4.metric("Ratio xG/Tir", f"{(p_stats['total_xg']/p_stats['shots']):.2f}")
        
        # Grand Plot
        st.markdown("---")
        c_plot, c_info = st.columns([3, 1])
        with c_plot:
            fig = create_pro_shotmap(df, selected_player, theme, is_solo=True)
            st.pyplot(fig, use_container_width=True)
        with c_info:
            st.info("ℹ️ Les étoiles vertes représentent les buts marqués. La densité de couleur indique les zones de tir préférentielles.")
            st.warning(f"Ligue sélectionnée : {selected_league}")

    # 2. MODE DUEL
    elif view_mode == "Duel (1 vs 1)":
        c1, c2 = st.columns(2)
        with c1:
            p1 = st.selectbox("Joueur A", sorted_players, index=0)
        with c2:
            p2 = st.selectbox("Joueur B", sorted_players, index=1)
            
        st.markdown("---")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown(f"<h3 style='text-align: center; color: {theme['color']}'>{p1}</h3>", unsafe_allow_html=True)
            # Stats comparatives
            s1 = df_grouped.loc[p1]
            st.markdown(f"**Buts:** {s1['goals']} | **xG:** {s1['total_xg']:.1f}")
            fig1 = create_pro_shotmap(df, p1, theme, is_solo=False)
            st.pyplot(fig1)
            
        with col_b:
            st.markdown(f"<h3 style='text-align: center; color: {theme['color']}'>{p2}</h3>", unsafe_allow_html=True)
            # Stats comparatives
            s2 = df_grouped.loc[p2]
            st.markdown(f"**Buts:** {s2['goals']} | **xG:** {s2['total_xg']:.1f}")
            fig2 = create_pro_shotmap(df, p2, theme, is_solo=False)
            st.pyplot(fig2)

    # 3. MODE GRILLE
    else:
        top_n = sorted_players[:num_players]
        
        # Layout dynamique (2 colonnes)
        cols = st.columns(2)
        
        for i, player in enumerate(top_n):
            col = cols[i % 2]
            with col:
                st.markdown(f"#### {i+1}. {player}")
                fig = create_pro_shotmap(df, player, theme, is_solo=False)
                st.pyplot(fig)
                st.markdown("---")

    # Footer
    st.markdown("<br><br><div style='text-align: center; color: gray; font-size: 0.8em;'>Developed with ❤️ & Python | Data Science Football</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
