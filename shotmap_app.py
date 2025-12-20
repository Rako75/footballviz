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
    page_title="⚽ Football Shotmaps Pro",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé ultra moderne
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        padding: 0rem 2rem;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #16213e 50%, #0f3460 100%);
    }
    
    h1 {
        background: linear-gradient(135deg, #00d4ff 0%, #00ff88 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        text-align: center;
        padding: 1.5rem 0;
        font-size: 3rem;
        letter-spacing: -1px;
        text-shadow: 0 0 30px rgba(0,212,255,0.3);
    }
    
    h2 {
        color: #00d4ff;
        font-weight: 700;
        margin-top: 2rem;
        font-size: 1.8rem;
    }
    
    h3 {
        color: #e2e8f0;
        font-weight: 600;
        font-size: 1.2rem;
    }
    
    .stSelectbox label, .stSlider label, .stRadio label {
        color: #00d4ff !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }
    
    .metric-card {
        background: rgba(0, 212, 255, 0.05);
        padding: 1.5rem;
        border-radius: 15px;
        border: 2px solid rgba(0, 212, 255, 0.2);
        backdrop-filter: blur(20px);
        box-shadow: 0 8px 32px rgba(0, 212, 255, 0.1);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        border-color: rgba(0, 212, 255, 0.5);
        box-shadow: 0 12px 48px rgba(0, 212, 255, 0.2);
        transform: translateY(-2px);
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 2.5rem;
        font-weight: 700;
        color: #00ff88;
    }
    
    div[data-testid="stMetricLabel"] {
        font-size: 0.9rem;
        color: #94a3b8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stDataFrame {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 10px;
        border: 1px solid rgba(0, 212, 255, 0.1);
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0e27 0%, #1a1f3a 100%);
        border-right: 2px solid rgba(0, 212, 255, 0.2);
    }
    
    .sidebar-title {
        color: #00d4ff;
        font-weight: 700;
        font-size: 1.3rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #00d4ff 0%, #00ff88 100%);
        color: #0a0e27;
        font-weight: 700;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 2rem;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 24px rgba(0, 212, 255, 0.4);
    }
    
    .info-box {
        background: rgba(0, 212, 255, 0.1);
        border-left: 4px solid #00d4ff;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #e2e8f0;
    }
    
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(0, 212, 255, 0.5), transparent);
        margin: 2rem 0;
    }
    
    .subtitle {
        text-align: center;
        color: #94a3b8;
        font-size: 1.1rem;
        font-weight: 400;
        margin-bottom: 2rem;
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
        # Données de démonstration enrichies
        np.random.seed(42)
        players = [
            ('Kylian Mbappé', 9825), ('Erling Haaland', 8456), ('Harry Kane', 9823),
            ('Robert Lewandowski', 8634), ('Victor Osimhen', 9875), ('Mohamed Salah', 8650),
            ('Vinicius Jr', 8650), ('Bukayo Saka', 8456), ('Lautaro Martínez', 9875),
            ('Antoine Griezmann', 9825)
        ]
        
        data_list = []
        for idx, (player, team_id) in enumerate(players, 1):
            n_shots = np.random.randint(40, 80)
            data_list.append(pd.DataFrame({
                'joueur_id': [idx] * n_shots,
                'joueur': [player] * n_shots,
                'equipe_id': [team_id] * n_shots,
                'minute': np.random.randint(1, 90, n_shots),
                'situation': np.random.choice(['Open Play', 'Set Piece', 'Counter'], n_shots, p=[0.7, 0.2, 0.1]),
                'position_x': np.random.uniform(60, 100, n_shots),
                'position_y': np.random.uniform(15, 55, n_shots),
                'xg': np.random.uniform(0.02, 0.65, n_shots),
                'type_evenement': np.random.choice(['Goal', 'Miss', 'SavedShot', 'Blocked'], 
                                                   n_shots, p=[0.12, 0.45, 0.30, 0.13])
            }))
        
        data = pd.concat(data_list, ignore_index=True)
    
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

def create_shotmap(data, player_id, theme, size='large'):
    """Crée une carte de tirs pour un joueur"""
    if size == 'large':
        figsize = (10, 13)
        font_sizes = {'title': 16, 'stats_label': 8, 'stats_value': 14, 'distance': 9}
    else:
        figsize = (6, 8)
        font_sizes = {'title': 12, 'stats_label': 6, 'stats_value': 10, 'distance': 7}
    
    fig, ax = plt.subplots(figsize=figsize, facecolor=theme['background'])
    ax.set_facecolor(theme['background'])
    
    # Configuration du terrain
    pitch = VerticalPitch(
        pitch_type='uefa', half=True, goal_type='box',
        linewidth=1.5, line_color=mcolors.to_hex(mcolors.to_rgba(theme['text'], alpha=0.2)),
        pad_bottom=-10, pad_top=15, pitch_color=theme['background']
    )
    pitch.draw(ax=ax)
    
    # Données du joueur
    player_data = data[data['joueur_id'] == player_id]
    
    # Colormap personnalisée
    cmap = mcolors.LinearSegmentedColormap.from_list('LeagueTheme', theme['gradient'], N=100)
    
    # Hexbin des tirs avec effet de glow
    pitch.hexbin(
        x=player_data['position_x'], 
        y=player_data['position_y'], 
        ax=ax, 
        cmap=cmap, 
        gridsize=(16, 16), 
        zorder=2, 
        edgecolors='None', 
        alpha=0.95, 
        mincnt=1
    )
    
    # Distance médiane avec style amélioré
    median_x = player_data['position_x'].median()
    x_circle, y_circle = semicircle(104.8 - median_x, 34, 104.8)
    ax.plot(x_circle, y_circle, ls='--', color=theme['accent'], lw=2, alpha=0.6, zorder=3)
    
    # Statistiques avec design moderne
    stats = {
        'TIRS': player_data.shape[0],
        'BUTS': player_data[player_data['type_evenement'] == 'Goal'].shape[0],
        'xG': player_data['xg'].sum(),
        'xG/TIR': player_data['xg'].mean()
    }
    
    # Calculer la précision
    on_target = player_data[player_data['type_evenement'].isin(['Goal', 'SavedShot'])].shape[0]
    accuracy = (on_target / stats['TIRS'] * 100) if stats['TIRS'] > 0 else 0
    
    # Afficher les stats en haut
    stat_y_start = 74
    for i, (label, value) in enumerate(stats.items()):
        x_pos = 10 + (i * 14.5)
        ax.text(x_pos, stat_y_start, label, 
                ha='center', va='bottom', fontsize=font_sizes['stats_label'], 
                color=mcolors.to_hex(mcolors.to_rgba(theme['text'], alpha=0.6)), 
                weight='bold')
        val_fmt = f"{value:.0f}" if label in ['TIRS', 'BUTS'] else f"{value:.2f}"
        ax.text(x_pos, stat_y_start - 2, val_fmt, 
                ha='center', va='top', fontsize=font_sizes['stats_value'], 
                color=theme['accent'], weight='heavy')
    
    # Distance médiane et précision
    dist_yds = ((105 - median_x) * 18) / 16.5
    dist_m = dist_yds * 0.9144
    
    info_text = f"Distance Médiane: {dist_m:.1f}m  |  Précision: {accuracy:.0f}%"
    ax.text(34, 108, info_text,
            ha='center', va='center', fontsize=font_sizes['distance'],
            color=theme['text'], weight='bold',
            bbox=dict(facecolor=theme['background'], 
                     edgecolor=theme['accent'], 
                     boxstyle='round,pad=0.5', alpha=0.9, linewidth=2))
    
    # Nom du joueur avec style impact
    player_name = player_data['joueur'].iloc[0].upper()
    ax.text(34, 118, player_name, 
            ha='center', va='center', fontsize=font_sizes['title'], 
            color=theme['text'], weight='black',
            bbox=dict(facecolor=theme['background'], 
                     edgecolor='none', 
                     boxstyle='round,pad=0.7', alpha=0.8))
    
    # Ligne décorative
    ax.plot([20, 48], [114, 114], color=theme['accent'], lw=3, alpha=0.9)
    
    # Logo de l'équipe
    team_id = player_data["equipe_id"].iloc[0]
    try:
        logo_ax = ax.inset_axes([0.05, 0.88, 0.15, 0.15])
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
    # En-tête avec animation
    st.markdown("# ⚽ FOOTBALL SHOTMAPS PRO")
    st.markdown("<p class='subtitle'>🎯 Analyse Avancée des Zones de Tir • Saison 2024/2025</p>", 
                unsafe_allow_html=True)
    
    # Sidebar moderne
    with st.sidebar:
        st.markdown("<h2 class='sidebar-title'>⚙️ CONFIGURATION</h2>", unsafe_allow_html=True)
        
        # Sélection de la ligue
        selected_league = st.selectbox(
            "🏆 Sélectionner une Ligue",
            options=list(LEAGUE_THEMES.keys()),
            index=0
        )
        
        theme = LEAGUE_THEMES[selected_league]
        
        # Logo de la ligue centré
        try:
            league_url = f'https://images.fotmob.com/image_resources/logo/leaguelogo/{theme["id"]}.png'
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                st.image(league_url, use_container_width=True)
        except:
            st.markdown(f"### {theme['name']}")
        
        st.markdown("---")
        
        # Type d'affichage
        display_type = st.radio(
            "📊 Type d'Affichage",
            ["Top Tireurs", "Meilleurs Buteurs", "Meilleur xG", "Plus Efficaces"],
            index=0
        )
        
        # Nombre de joueurs
        num_players = st.slider(
            "👥 Nombre de Joueurs",
            min_value=1,
            max_value=10,
            value=6,
            help="Sélectionnez le nombre de joueurs à afficher"
        )
        
        # Taille d'affichage
        display_size = st.radio(
            "📐 Taille des Shotmaps",
            ["Large (1 par ligne)", "Compact (2 par ligne)", "Grille (3 par ligne)"],
            index=2
        )
        
        st.markdown("---")
        
        # Info box
        st.markdown("""
        <div class='info-box'>
        <strong>ℹ️ À PROPOS</strong><br>
        Application d'analyse avancée des zones de tir des meilleurs joueurs.
        Données hors penalties pour une analyse précise.
        </div>
        """, unsafe_allow_html=True)
    
    # Charger les données
    with st.spinner("🔄 Chargement des données..."):
        data = load_data(theme['file'])
    
    # Préparation des données selon le type d'affichage
    if display_type == "Top Tireurs":
        sort_col = 'Total'
        data_grouped = data.groupby(['joueur_id', 'joueur', 'equipe_id']).size().reset_index(name='Total')
    elif display_type == "Meilleurs Buteurs":
        goals_data = data[data['type_evenement'] == 'Goal']
        data_grouped = goals_data.groupby(['joueur_id', 'joueur', 'equipe_id']).size().reset_index(name='Total')
    elif display_type == "Meilleur xG":
        data_grouped = data.groupby(['joueur_id', 'joueur', 'equipe_id'])['xg'].sum().reset_index(name='Total')
    else:  # Plus Efficaces
        player_stats = data.groupby(['joueur_id', 'joueur', 'equipe_id']).agg({
            'type_evenement': lambda x: (x == 'Goal').sum(),
            'joueur_id': 'count'
        }).reset_index()
        player_stats.columns = ['joueur_id', 'joueur', 'equipe_id', 'goals', 'shots']
        player_stats = player_stats[player_stats['shots'] >= 10]  # Minimum 10 tirs
        player_stats['Total'] = (player_stats['goals'] / player_stats['shots'] * 100)
        data_grouped = player_stats
    
    data_grouped = data_grouped.sort_values(by='Total', ascending=False).head(num_players)
    
    # Statistiques globales avec cards modernes
    st.markdown("## 📈 STATISTIQUES GLOBALES")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_shots = len(data)
    total_goals = len(data[data['type_evenement'] == 'Goal'])
    avg_xg = data['xg'].mean()
    conversion_rate = (total_goals / total_shots * 100) if total_shots > 0 else 0
    
    with col1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("🎯 Tirs Totaux", f"{total_shots:,}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("⚽ Buts Marqués", f"{total_goals:,}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("📊 xG Moyen", f"{avg_xg:.3f}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col4:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("🎖️ Taux Conversion", f"{conversion_rate:.1f}%")
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tableau des statistiques
    st.markdown(f"## 🏆 CLASSEMENT - {display_type.upper()}")
    
    display_df = data_grouped[['joueur', 'Total']].copy()
    if display_type == "Top Tireurs":
        display_df.columns = ['Joueur', 'Total Tirs']
    elif display_type == "Meilleurs Buteurs":
        display_df.columns = ['Joueur', 'Nombre de Buts']
    elif display_type == "Meilleur xG":
        display_df.columns = ['Joueur', 'xG Total']
        display_df['xG Total'] = display_df['xG Total'].round(2)
    else:
        display_df.columns = ['Joueur', 'Taux de Conversion (%)']
        display_df['Taux de Conversion (%)'] = display_df['Taux de Conversion (%)'].round(1)
    
    st.dataframe(
        display_df.style.background_gradient(cmap='viridis', subset=display_df.columns[1]),
        use_container_width=True,
        height=300
    )
    
    st.markdown("---")
    
    # Cartes de tirs avec affichage adaptatif
    st.markdown("## 🗺️ SHOTMAPS DÉTAILLÉES")
    
    # Déterminer le nombre de colonnes
    if "Large" in display_size:
        cols_per_row = 1
        size = 'large'
    elif "Compact" in display_size:
        cols_per_row = 2
        size = 'normal'
    else:
        cols_per_row = 3
        size = 'normal'
    
    rows = (num_players + cols_per_row - 1) // cols_per_row
    
    for row in range(rows):
        cols = st.columns(cols_per_row)
        for col_idx in range(cols_per_row):
            player_idx = row * cols_per_row + col_idx
            if player_idx < len(data_grouped):
                player_id = data_grouped['joueur_id'].iloc[player_idx]
                with cols[col_idx]:
                    with st.spinner(f"🎨 Génération..."):
                        fig = create_shotmap(data, player_id, theme, size=size)
                        st.pyplot(fig, use_container_width=True)
                        plt.close(fig)
    
    # Footer moderne
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <p style='color: #00d4ff; font-size: 0.9rem; font-weight: 600;'>
                ⚡ POWERED BY FOTMOB DATA • STREAMLIT • MPLSOCCER
            </p>
            <p style='color: #64748b; font-size: 0.8rem; margin-top: 0.5rem;'>
                Saison 2024/2025 • Analyse Professionnelle des Performances
            </p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
