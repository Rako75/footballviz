import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import matplotlib.colors as mcolors
import matplotlib.font_manager as fm
from matplotlib.patches import RegularPolygon
from mplsoccer import VerticalPitch
from PIL import Image
import urllib.request
import numpy as np
import io

# Configuration de la page
st.set_page_config(
    page_title="Analyse des Tirs - Football",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour un design moderne
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%);
    }
    h1 {
        color: #38bdf8;
        font-weight: 700;
        text-align: center;
        padding: 1rem 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    h2, h3 {
        color: #e2e8f0;
    }
    .stSelectbox, .stMultiselect {
        color: #e2e8f0;
    }
    .css-1d391kg, .css-18e3th9 {
        padding-top: 2rem;
    }
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
</style>
""", unsafe_allow_html=True)

# Configuration des thèmes de ligues
LEAGUE_THEMES = {
    'LIGUE 1': {
        'name': 'LIGUE 1',
        'id': 53,
        'file': 'tirs_ligue1_2024_2025.csv',
        'background': '#000d24', 
        'accent': '#085eff',     
        'text': '#ffffff',
        'gradient': ['#000d24', '#042a70', '#085eff', '#5c95ff', '#ffffff']
    },
    'PREMIER LEAGUE': {
        'name': 'PREMIER LEAGUE',
        'id': 47,
        'file': 'tirs_premier_league_2024_2025.csv',
        'background': '#360d3a', 
        'accent': '#e90052',     
        'text': '#ffffff',
        'gradient': ['#360d3a', '#6a1b6e', '#963cff', '#e90052', '#ffffff'] 
    },
    'LA LIGA': {
        'name': 'LA LIGA',
        'id': 87,
        'file': 'tirs_la_liga_2024_2025.csv',
        'background': '#140505', 
        'accent': '#FF4B44',     
        'text': '#ffeaea',
        'gradient': ['#140505', '#5c1210', '#b92b27', '#FF4B44', '#ffffff']
    },
    'BUNDESLIGA': {
        'name': 'BUNDESLIGA',
        'id': 54,
        'file': 'tirs_bundesliga_2024_2025.csv',
        'background': '#120203', 
        'accent': '#D3010C',     
        'text': '#ffffff',
        'gradient': ['#120203', '#4a0508', '#9e0b12', '#D3010C', '#ffffff']
    },
    'SERIE A': {
        'name': 'SERIE A',
        'id': 55,
        'file': 'tirs_serie_a_2024_2025.csv',
        'background': '#020914', 
        'accent': '#0578FF',     
        'text': '#f0f9ff',
        'gradient': ['#020914', '#032d66', '#0578FF', '#66adff', '#ffffff']
    },
    'CHAMPIONS LEAGUE': {
        'name': 'CHAMPIONS LEAGUE',
        'id': 42,
        'file': 'tirs_ucl_2024_2025.csv',
        'background': '#001967', 
        'accent': '#38bdf8',     
        'text': '#ffffff',
        'gradient': ['#001967', '#0f3da8', '#38bdf8', '#a5f3fc', '#ffffff']
    },
    'EUROPA LEAGUE': {
        'name': 'EUROPA LEAGUE',
        'id': 73,
        'file': 'tirs_uel_2024_2025.csv',
        'background': '#170f00', 
        'accent': '#f8ad09',     
        'text': '#fffbeb',
        'gradient': ['#170f00', '#5c3d02', '#b47b05', '#f8ad09', '#ffffff']
    }
}

@st.cache_data
def load_data(file_path):
    """Charge les données depuis un fichier CSV ou génère des données de démonstration"""
    try:
        data = pd.read_csv(file_path)
    except:
        # Données de démonstration
        np.random.seed(42)
        data = pd.DataFrame({
            'joueur_id': [1]*50 + [2]*50 + [3]*50 + [4]*50 + [5]*50 + [6]*50,
            'joueur': ['Kylian Mbappé']*50 + ['Erling Haaland']*50 + ['Harry Kane']*50 + 
                      ['Robert Lewandowski']*50 + ['Victor Osimhen']*50 + ['Mohamed Salah']*50,
            'equipe_id': [9825]*50 + [8456]*50 + [9823]*50 + [8634]*50 + [9875]*50 + [8650]*50,
            'minute': np.tile(range(50), 6),
            'situation': ['Open Play']*300,
            'position_x': np.random.uniform(60, 100, 300),
            'position_y': np.random.uniform(15, 55, 300),
            'xg': np.random.uniform(0.02, 0.6, 300),
            'type_evenement': np.random.choice(['Goal', 'Miss', 'SavedShot'], 300, p=[0.15, 0.5, 0.35])
        })
    
    # Filtrer les penalties
    data = data[data['situation'] != 'Penalty'].reset_index(drop=True)
    return data

def is_inside_box(x, y):
    """Vérifie si un tir est dans la surface"""
    return (x >= 13.84) & (x <= 54.16) & (y >= 88.5)

def semicircle(r, h, k):
    """Génère un demi-cercle pour la distance médiane"""
    x0, x1 = h - r, h + r
    x = np.linspace(x0, x1, 500)
    y = k - np.sqrt(r**2 - (x - h)**2)
    return x, y

def create_shotmap(data, player_id, theme):
    """Crée une carte de tirs pour un joueur"""
    fig, ax = plt.subplots(figsize=(6, 8), facecolor=theme['background'])
    ax.set_facecolor(theme['background'])
    
    # Configuration du terrain
    pitch = VerticalPitch(
        pitch_type='uefa', half=True, goal_type='box',
        linewidth=1.2, line_color=mcolors.to_hex(mcolors.to_rgba(theme['text'], alpha=0.15)),
        pad_bottom=-10, pad_top=15, pitch_color=theme['background']
    )
    pitch.draw(ax=ax)
    
    # Données du joueur
    player_data = data[data['joueur_id'] == player_id]
    
    # Colormap personnalisée
    cmap = mcolors.LinearSegmentedColormap.from_list('LeagueTheme', theme['gradient'], N=100)
    
    # Hexbin des tirs
    pitch.hexbin(
        x=player_data['position_x'], 
        y=player_data['position_y'], 
        ax=ax, 
        cmap=cmap, 
        gridsize=(14, 14), 
        zorder=2, 
        edgecolors='None', 
        alpha=0.9, 
        mincnt=1
    )
    
    # Distance médiane
    median_x = player_data['position_x'].median()
    x_circle, y_circle = semicircle(104.8 - median_x, 34, 104.8)
    ax.plot(x_circle, y_circle, ls=':', color=theme['text'], lw=1, alpha=0.4, zorder=3)
    
    # Statistiques
    stats = {
        'Tirs': player_data.shape[0],
        'Buts': player_data[player_data['type_evenement'] == 'Goal'].shape[0],
        'xG': player_data['xg'].sum(),
        'xG/Tir': player_data['xg'].mean()
    }
    
    for i, (label, value) in enumerate(stats.items()):
        x_pos = 10 + (i * 16)
        ax.text(x_pos, 73, " ".join(list(label.upper())), 
                ha='center', va='bottom', fontsize=6, 
                color=mcolors.to_hex(mcolors.to_rgba(theme['text'], alpha=0.7)), 
                weight='bold')
        val_fmt = f"{value:.0f}" if label in ['Tirs', 'Buts'] else f"{value:.2f}"
        ax.text(x_pos, 71, val_fmt, 
                ha='center', va='top', fontsize=10, 
                color=theme['text'], weight='bold')
    
    # Distance médiane en mètres
    dist_yds = ((105 - median_x) * 18) / 16.5
    dist_m = dist_yds * 0.9144
    ax.text(34, 108, f"Dist. Médiane: {dist_m:.1f} m",
            ha='center', va='center', fontsize=7,
            color=theme['accent'], weight='bold',
            bbox=dict(facecolor=theme['background'], 
                     edgecolor=mcolors.to_hex(mcolors.to_rgba(theme['text'], alpha=0.15)), 
                     boxstyle='round,pad=0.4', alpha=0.9))
    
    # Nom du joueur
    player_name = player_data['joueur'].iloc[0].upper()
    ax.text(34, 116, player_name, 
            ha='center', va='center', fontsize=12, 
            color=theme['text'], weight='heavy')
    ax.plot([24, 44], [113, 113], color=theme['accent'], lw=2, alpha=0.8)
    
    # Logo de l'équipe
    team_id = player_data["equipe_id"].iloc[0]
    try:
        logo_ax = ax.inset_axes([0.05, 0.88, 0.12, 0.12])
        icon = Image.open(urllib.request.urlopen(
            f'https://images.fotmob.com/image_resources/logo/teamlogo/{team_id:.0f}.png'
        ))
        logo_ax.imshow(icon)
        logo_ax.axis('off')
    except:
        pass
    
    plt.tight_layout()
    return fig

def main():
    # En-tête
    st.markdown("# ⚽ Analyse des Tirs - Football Européen")
    st.markdown("### Comparaison des zones de tir et efficacité | Saison 2024/2025")
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/000000/soccer-ball.png", width=80)
        st.markdown("## 🎯 Configuration")
        
        # Sélection de la ligue
        selected_league = st.selectbox(
            "Sélectionner une ligue",
            options=list(LEAGUE_THEMES.keys()),
            index=5  # Champions League par défaut
        )
        
        theme = LEAGUE_THEMES[selected_league]
        
        # Afficher le logo de la ligue
        try:
            league_url = f'https://images.fotmob.com/image_resources/logo/leaguelogo/{theme["id"]}.png'
            st.image(league_url, width=150)
        except:
            st.markdown(f"## {theme['name']}")
        
        st.markdown("---")
        st.markdown("**📊 Filtres d'analyse**")
        
        # Nombre de joueurs à afficher
        num_players = st.slider("Nombre de joueurs", 1, 6, 6)
        
        st.markdown("---")
        st.markdown("**ℹ️ À propos**")
        st.info("Cette application analyse les zones de tir des meilleurs buteurs en excluant les penalties.")
        
    # Charger les données
    with st.spinner("Chargement des données..."):
        data = load_data(theme['file'])
    
    # Préparation des données
    data['is_in_box'] = [is_inside_box(y, x) for x, y in zip(data['position_x'], data['position_y'])]
    data_grouped = data.groupby(['joueur_id', 'joueur', 'equipe_id', 'is_in_box'])['minute'].count().reset_index()
    data_grouped = data_grouped.pivot(
        columns='is_in_box', 
        index=['joueur_id', 'joueur', 'equipe_id'], 
        values='minute'
    ).reset_index()
    
    if True not in data_grouped.columns:
        data_grouped[True] = 0
    if False not in data_grouped.columns:
        data_grouped[False] = 0
    
    data_grouped.rename(columns={False: 'Hors surface', True: 'Dans surface'}, inplace=True)
    data_grouped.fillna(0, inplace=True)
    data_grouped['Total'] = data_grouped['Hors surface'] + data_grouped['Dans surface']
    data_grouped = data_grouped.sort_values(by='Total', ascending=False).head(num_players)
    
    # Statistiques globales
    st.markdown("## 📈 Statistiques Globales")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_shots = len(data)
    total_goals = len(data[data['type_evenement'] == 'Goal'])
    avg_xg = data['xg'].mean()
    conversion_rate = (total_goals / total_shots * 100) if total_shots > 0 else 0
    
    with col1:
        st.metric("Tirs totaux", f"{total_shots}")
    with col2:
        st.metric("Buts marqués", f"{total_goals}")
    with col3:
        st.metric("xG moyen", f"{avg_xg:.2f}")
    with col4:
        st.metric("Taux de conversion", f"{conversion_rate:.1f}%")
    
    st.markdown("---")
    
    # Tableau des meilleurs buteurs
    st.markdown("## 🏆 Classement des Buteurs")
    
    display_df = data_grouped[['joueur', 'Total', 'Dans surface', 'Hors surface']].copy()
    display_df.columns = ['Joueur', 'Total Tirs', 'Dans Surface', 'Hors Surface']
    
    st.dataframe(
        display_df.style.background_gradient(cmap='Blues', subset=['Total Tirs']),
        use_container_width=True,
        height=250
    )
    
    st.markdown("---")
    
    # Cartes de tirs
    st.markdown("## 🗺️ Cartes de Tirs")
    
    # Afficher les cartes en grille
    cols_per_row = 3
    rows = (num_players + cols_per_row - 1) // cols_per_row
    
    for row in range(rows):
        cols = st.columns(cols_per_row)
        for col_idx in range(cols_per_row):
            player_idx = row * cols_per_row + col_idx
            if player_idx < len(data_grouped):
                player_id = data_grouped['joueur_id'].iloc[player_idx]
                with cols[col_idx]:
                    with st.spinner(f"Génération..."):
                        fig = create_shotmap(data, player_id, theme)
                        st.pyplot(fig)
                        plt.close(fig)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #94a3b8; font-size: 0.8rem;'>"
        "Data: FotMob | Application: Streamlit | 2024/2025"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
