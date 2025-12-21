import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.font_manager as fm
from mplsoccer import VerticalPitch
from PIL import Image
import urllib.request
import numpy as np
import requests
import csv
import time
from pathlib import Path
import os

# Configuration de la police Montserrat
font_url = "https://github.com/googlefonts/Montserrat/raw/main/fonts/ttf/Montserrat-Regular.ttf"
font_path = 'Montserrat-Regular.ttf'
if not os.path.exists(font_path):
    urllib.request.urlretrieve(font_url, font_path)

fm.fontManager.addfont(font_path)
prop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = prop.get_name()

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
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    }
    
    h1 {
        color: #f8fafc;
        font-weight: 700;
        text-align: center;
        padding: 2rem 0 0.5rem 0;
        font-size: 2.5rem;
        letter-spacing: -0.5px;
    }
    
    h2 {
        color: #94a3b8;
        font-weight: 600;
        margin-top: 2rem;
        font-size: 1.5rem;
    }
    
    h3 {
        color: #cbd5e1;
        font-weight: 500;
        font-size: 1.1rem;
    }
    
    .stSelectbox label, .stSlider label, .stRadio label {
        color: #94a3b8 !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
    }
    
    .metric-card {
        background: rgba(148, 163, 184, 0.03);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid rgba(148, 163, 184, 0.1);
        backdrop-filter: blur(20px);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        border-color: rgba(148, 163, 184, 0.2);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
        transform: translateY(-2px);
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 600;
        color: #e2e8f0;
    }
    
    div[data-testid="stMetricLabel"] {
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stDataFrame {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 8px;
        border: 1px solid rgba(148, 163, 184, 0.1);
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        border-right: 1px solid rgba(148, 163, 184, 0.1);
    }
    
    .sidebar-title {
        color: #cbd5e1;
        font-weight: 600;
        font-size: 1.1rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .stButton>button {
        background: #475569;
        color: #f8fafc;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton>button:hover {
        background: #64748b;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
    
    .info-box {
        background: rgba(148, 163, 184, 0.08);
        border-left: 3px solid #64748b;
        padding: 1rem;
        border-radius: 6px;
        margin: 1rem 0;
        color: #cbd5e1;
    }
    
    hr {
        border: none;
        height: 1px;
        background: rgba(148, 163, 184, 0.2);
        margin: 2rem 0;
    }
    
    .subtitle {
        text-align: center;
        color: #64748b;
        font-size: 1rem;
        font-weight: 400;
        margin-bottom: 2rem;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# Configuration des ligues
LEAGUE_THEMES = {
    'LIGUE 1': {
        'name': 'LIGUE 1', 'id': 53, 'slug': 'ligue1',
        'background': '#000d24', 'accent': '#085eff', 'text': '#ffffff',
        'gradient': ['#000d24', '#042a70', '#085eff', '#5c95ff', '#ffffff']
    },
    'PREMIER LEAGUE': {
        'name': 'PREMIER LEAGUE', 'id': 47, 'slug': 'premier_league',
        'background': '#360d3a', 'accent': '#e90052', 'text': '#ffffff',
        'gradient': ['#360d3a', '#6a1b6e', '#963cff', '#e90052', '#ffffff']
    },
    'LA LIGA': {
        'name': 'LA LIGA', 'id': 87, 'slug': 'la_liga',
        'background': '#140505', 'accent': '#FF4B44', 'text': '#ffeaea',
        'gradient': ['#140505', '#5c1210', '#b92b27', '#FF4B44', '#ffffff']
    },
    'BUNDESLIGA': {
        'name': 'BUNDESLIGA', 'id': 54, 'slug': 'bundesliga',
        'background': '#120203', 'accent': '#D3010C', 'text': '#ffffff',
        'gradient': ['#120203', '#4a0508', '#9e0b12', '#D3010C', '#ffffff']
    },
    'SERIE A': {
        'name': 'SERIE A', 'id': 55, 'slug': 'serie_a',
        'background': '#020914', 'accent': '#0578FF', 'text': '#f0f9ff',
        'gradient': ['#020914', '#032d66', '#0578FF', '#66adff', '#ffffff']
    },
    'CHAMPIONS LEAGUE': {
        'name': 'CHAMPIONS LEAGUE', 'id': 42, 'slug': 'ucl',
        'background': '#001967', 'accent': '#38bdf8', 'text': '#ffffff',
        'gradient': ['#001967', '#0f3da8', '#38bdf8', '#a5f3fc', '#ffffff']
    },
    'EUROPA LEAGUE': {
        'name': 'EUROPA LEAGUE', 'id': 73, 'slug': 'uel',
        'background': '#170f00', 'accent': '#f8ad09', 'text': '#fffbeb',
        'gradient': ['#170f00', '#5c3d02', '#b47b05', '#f8ad09', '#ffffff']
    }
}

SEASONS_CONFIG = {
    '2024/2025': '2024/2025',
    '2023/2024': '2023/2024',
    '2022/2023': '2022/2023',
    '2021/2022': '2021/2022',
    '2020/2021': '2020/2021'
}

HEADERS = {
    'sec-ch-ua-platform': '"Windows"',
    'Referer': 'https://www.fotmob.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'x-mas': 'eyJib2R5Ijp7InVybCI6Ii9hcGkvZGF0YS9sZWFndWVzP2lkPTUzJmNjb2RlMz1GUkEmc2Vhc29uPTIwMjQlMkYyMDI1IiwiY29kZSI6MTc2NTU0MTU0MzgyOSwiZm9vIjoicHJvZHVjdGlvbjo2YzZiN2M5M2Y1OTE0MDg0ZmYwM2IzMzIwMzRlMzE3MThkZWRjYjYzIn0sInNpZ25hdHVyZSI6IjRFOUZFRjA4RDYwNEM3NERCMkQxMDgzQ0YwMDEzNUI3In0=',
    'sec-ch-ua': '"Chromium";v="122", "Google Chrome";v="122"',
    'sec-ch-ua-mobile': '?0'
}

def get_filename(league_slug, season):
    """Génère le nom de fichier pour une ligue et saison"""
    season_clean = season.replace('/', '_')
    return f"tirs_{league_slug}_{season_clean}.csv"

def recuperer_ids_matchs_termines(league_id, season):
    """Récupère les IDs des matchs terminés"""
    season_url = season.replace('/', '%2F')
    url = f'https://www.fotmob.com/api/data/leagues?id={league_id}&ccode3=FRA&season={season_url}'
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        all_matches = data.get('fixtures', {}).get('allMatches', [])
        ids_termines = [str(m.get('id')) for m in all_matches if m.get('status', {}).get('finished')]
        return ids_termines
    except Exception as e:
        st.error(f"❌ Erreur API: {str(e)}")
        return []

def extraire_tirs_match(match_id, league_name, season):
    """Extrait les tirs d'un match"""
    url = f'https://www.fotmob.com/api/data/matchDetails?matchId={match_id}'
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            return []
        
        data = response.json()
        general = data.get('general', {})
        home = general.get('homeTeam', {}).get('name', 'Domicile')
        away = general.get('awayTeam', {}).get('name', 'Extérieur')
        
        shots = []
        content = data.get('content', {})
        
        if content and 'shotmap' in content and content['shotmap']:
            for shot in content['shotmap'].get('shots', []):
                shots.append({
                    'match_id': match_id,
                    'ligue': league_name,
                    'saison': season,
                    'date': general.get('matchTimeUTC'),
                    'type_evenement': shot.get('eventType'),
                    'equipe_id': shot.get('teamId'),
                    'joueur': shot.get('playerName'),
                    'equipe_joueur': home if shot.get('teamId') == general.get('homeTeam', {}).get('id') else away,
                    'joueur_id': shot.get('playerId'),
                    'minute': shot.get('min'),
                    'xg': shot.get('expectedGoals'),
                    'situation': shot.get('situation'),
                    'position_x': shot.get('x'),
                    'position_y': shot.get('y'),
                })
        return shots
    except:
        return []

def lancer_scraping(league_conf, season_str):
    """Orchestre le scraping avec interface Streamlit"""
    filename = get_filename(league_conf['slug'], season_str)
    
    st.info(f"🔄 Récupération des matchs pour {league_conf['name']} ({season_str})...")
    ids = recuperer_ids_matchs_termines(league_conf['id'], season_str)
    
    if not ids:
        st.warning("⚠️ Aucun match trouvé. Vérifiez les headers ou la disponibilité.")
        return None
    
    st.success(f"✅ {len(ids)} matchs terminés trouvés")
    
    all_data = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, mid in enumerate(ids, 1):
        match_shots = extraire_tirs_match(mid, league_conf['name'], season_str)
        all_data.extend(match_shots)
        progress_bar.progress(i / len(ids))
        status_text.text(f"⏳ Progression: {i}/{len(ids)} | Tirs cumulés: {len(all_data)}")
        time.sleep(0.3)
    
    progress_bar.empty()
    status_text.empty()
    
    if all_data:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=all_data[0].keys())
            writer.writeheader()
            writer.writerows(all_data)
        st.success(f"🎉 Fichier généré: {filename} ({len(all_data)} tirs)")
        return filename
    else:
        st.error("❌ Aucun tir récupéré")
        return None

@st.cache_data
def load_data(file_path):
    """Charge les données depuis CSV"""
    try:
        data = pd.read_csv(file_path)
        data = data[data['situation'] != 'Penalty'].reset_index(drop=True)
        return data
    except:
        return None

def semicircle(r, h, k):
    """Génère un demi-cercle"""
    x0, x1 = h - r, h + r
    x = np.linspace(x0, x1, 500)
    y = k - np.sqrt(r**2 - (x - h)**2)
    return x, y

def create_shotmap(data, player_id, theme, size='normal'):
    """Crée une carte de tirs avec hexbins visibles et informations enrichies"""
    if size == 'large':
        figsize = (10, 14)
        font_sizes = {
            'title': 18, 'stats_label': 9, 'stats_value': 16, 
            'info': 10, 'subtitle': 8, 'legend': 7
        }
    else:
        figsize = (6, 9)
        font_sizes = {
            'title': 13, 'stats_label': 7, 'stats_value': 12, 
            'info': 8, 'subtitle': 6.5, 'legend': 6
        }
    
    fig, ax = plt.subplots(figsize=figsize, facecolor=theme['background'])
    ax.set_facecolor(theme['background'])
    
    pitch = VerticalPitch(
        pitch_type='uefa', half=True, goal_type='box',
        linewidth=2, line_color=mcolors.to_hex(mcolors.to_rgba(theme['text'], alpha=0.3)),
        pad_bottom=-10, pad_top=18, pitch_color=theme['background']
    )
    pitch.draw(ax=ax)
    
    player_data = data[data['joueur_id'] == player_id]
    
    # Création d'une colormap plus visible avec meilleur contraste
    gradient_colors = theme['gradient'].copy()
    # Ajuster l'opacité pour plus de visibilité
    cmap = mcolors.LinearSegmentedColormap.from_list('LeagueTheme', gradient_colors, N=256)
    
    # Hexbins avec paramètres optimisés pour la visibilité
    hexbin = pitch.hexbin(
        x=player_data['position_x'], y=player_data['position_y'], 
        ax=ax, cmap=cmap, gridsize=(14, 14), zorder=2, 
        edgecolors=mcolors.to_hex(mcolors.to_rgba(theme['text'], alpha=0.4)),
        linewidths=1.2, alpha=1.0, mincnt=1
    )
    
    # Colorbar pour légende des hexbins
    cbar = plt.colorbar(hexbin, ax=ax, fraction=0.035, pad=0.02)
    cbar.set_label('Densité de tirs', color=theme['text'], 
                   fontsize=font_sizes['legend'], weight='bold')
    cbar.ax.tick_params(colors=theme['text'], labelsize=font_sizes['legend']-1)
    cbar.outline.set_edgecolor(mcolors.to_hex(mcolors.to_rgba(theme['text'], alpha=0.3)))
    
    # Demi-cercle de distance médiane
    median_x = player_data['position_x'].median()
    x_circle, y_circle = semicircle(104.8 - median_x, 34, 104.8)
    ax.plot(x_circle, y_circle, ls='--', color=theme['accent'], lw=2.5, alpha=0.8, zorder=3)
    
    # STATISTIQUES PRINCIPALES - Ligne 1
    stats_main = {
        'TIRS': player_data.shape[0],
        'BUTS': player_data[player_data['type_evenement'] == 'Goal'].shape[0],
        'xG': player_data['xg'].sum(),
        'xG/TIR': player_data['xg'].mean()
    }
    
    stat_y_start = 76
    for i, (label, value) in enumerate(stats_main.items()):
        x_pos = 10 + (i * 14.5)
        ax.text(x_pos, stat_y_start, label, 
                ha='center', va='bottom', fontsize=font_sizes['stats_label'], 
                color=mcolors.to_hex(mcolors.to_rgba(theme['text'], alpha=0.7)), 
                weight='bold', fontfamily='Montserrat')
        val_fmt = f"{value:.0f}" if label in ['TIRS', 'BUTS'] else f"{value:.2f}"
        ax.text(x_pos, stat_y_start - 2.5, val_fmt, 
                ha='center', va='top', fontsize=font_sizes['stats_value'], 
                color=theme['accent'], weight='heavy', fontfamily='Montserrat')
    
    # STATISTIQUES SECONDAIRES - Ligne 2
    on_target = player_data[player_data['type_evenement'].isin(['Goal', 'SavedShot'])].shape[0]
    accuracy = (on_target / stats_main['TIRS'] * 100) if stats_main['TIRS'] > 0 else 0
    
    blocked = player_data[player_data['type_evenement'] == 'BlockedShot'].shape[0]
    off_target = player_data[player_data['type_evenement'] == 'MissedShots'].shape[0]
    
    # Calcul de la différence buts vs xG
    goals_vs_xg = stats_main['BUTS'] - stats_main['xG']
    
    stats_secondary = {
        'CADRÉS': on_target,
        'PRÉCISION': f"{accuracy:.0f}%",
        'CONTRÉS': blocked,
        'BUTS vs xG': f"{goals_vs_xg:+.1f}"
    }
    
    stat_y_secondary = 84
    for i, (label, value) in enumerate(stats_secondary.items()):
        x_pos = 10 + (i * 14.5)
        ax.text(x_pos, stat_y_secondary, label, 
                ha='center', va='bottom', fontsize=font_sizes['subtitle'], 
                color=mcolors.to_hex(mcolors.to_rgba(theme['text'], alpha=0.6)), 
                weight='bold', fontfamily='Montserrat')
        val_str = str(value) if isinstance(value, str) else f"{value:.0f}"
        val_color = '#22c55e' if 'vs xG' in label and goals_vs_xg > 0 else (
            '#ef4444' if 'vs xG' in label and goals_vs_xg < 0 else theme['text']
        )
        ax.text(x_pos, stat_y_secondary - 2, val_str, 
                ha='center', va='top', fontsize=font_sizes['info'], 
                color=val_color, weight='bold', fontfamily='Montserrat')
    
    # INFORMATIONS DISTANCE ET SITUATIONS
    dist_yds = ((105 - median_x) * 18) / 16.5
    dist_m = dist_yds * 0.9144
    
    # Situations de tir
    situations = player_data['situation'].value_counts()
    top_situation = situations.index[0] if len(situations) > 0 else "N/A"
    situation_count = situations.iloc[0] if len(situations) > 0 else 0
    
    info_text = f"Distance Médiane: {dist_m:.1f}m  |  Situation: {top_situation} ({situation_count})"
    ax.text(34, 93, info_text,
            ha='center', va='center', fontsize=font_sizes['info'],
            color=theme['text'], weight='bold', fontfamily='Montserrat',
            bbox=dict(facecolor=mcolors.to_hex(mcolors.to_rgba(theme['accent'], alpha=0.2)), 
                     edgecolor=theme['accent'], 
                     boxstyle='round,pad=0.6', alpha=0.95, linewidth=2))
    
    # PIED PRÉFÉRÉ (si disponible dans les données)
    left_foot = player_data[player_data.get('bodyPart', '') == 'left-foot'].shape[0] if 'bodyPart' in player_data.columns else 0
    right_foot = player_data[player_data.get('bodyPart', '') == 'right-foot'].shape[0] if 'bodyPart' in player_data.columns else 0
    
    # NOM DU JOUEUR
    player_name = player_data['joueur'].iloc[0].upper()
    team_name = player_data['equipe_joueur'].iloc[0]
    
    ax.text(34, 102, player_name, 
            ha='center', va='center', fontsize=font_sizes['title'], 
            color=theme['text'], weight='black', fontfamily='Montserrat',
            bbox=dict(facecolor=mcolors.to_hex(mcolors.to_rgba(theme['background'], alpha=0.9)), 
                     edgecolor='none', boxstyle='round,pad=0.8', alpha=0.95))
    
    # ÉQUIPE
    ax.text(34, 97.5, team_name, 
            ha='center', va='center', fontsize=font_sizes['subtitle'], 
            color=mcolors.to_hex(mcolors.to_rgba(theme['text'], alpha=0.7)), 
            weight='600', fontfamily='Montserrat')
    
    # Ligne décorative
    ax.plot([18, 50], [106, 106], color=theme['accent'], lw=3.5, alpha=0.9, solid_capstyle='round')
    
    # Logo de l'équipe
    team_id = player_data["equipe_id"].iloc[0]
    try:
        logo_ax = ax.inset_axes([0.04, 0.895, 0.16, 0.16])
        icon = Image.open(urllib.request.urlopen(
            f'https://images.fotmob.com/image_resources/logo/teamlogo/{team_id:.0f}.png'
        ))
        logo_ax.imshow(icon)
        logo_ax.axis('off')
    except:
        pass
    
    # Photo du joueur
    try:
        player_logo_ax = ax.inset_axes([0.80, 0.895, 0.16, 0.16])
        player_icon_url = f'https://images.fotmob.com/image_resources/playerimages/{player_id}.png'
        player_icon = Image.open(urllib.request.urlopen(player_icon_url))
        player_logo_ax.imshow(player_icon)
        player_logo_ax.axis('off')
    except:
        pass
    
    plt.tight_layout()
    return fig

def main():
    st.markdown("# Analyse des Zones de Tir")
    st.markdown("""<p class='subtitle'>
        Outil professionnel de visualisation et d'analyse des shotmaps<br>
        Hexbins haute visibilité • Métriques xG avancées • Analyse détaillée des situations
    </p>""", unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("<h2 class='sidebar-title'>⚙️ Configuration</h2>", unsafe_allow_html=True)
        
        # Mode de l'application
        mode = st.radio("Mode d'utilisation", ["📊 Visualisation", "🔄 Scraping"], index=0)
        
        st.markdown("---")
        
        # Sélection Ligue
        selected_league_name = st.selectbox(
            "Compétition",
            options=list(LEAGUE_THEMES.keys()),
            index=0
        )
        theme = LEAGUE_THEMES[selected_league_name]
        
        # Logo de la ligue
        try:
            league_url = f'https://images.fotmob.com/image_resources/logo/leaguelogo/{theme["id"]}.png'
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                st.image(league_url, use_container_width=True)
        except:
            st.markdown(f"### {theme['name']}")
        
        st.markdown("---")
        
        if mode == "🔄 Scraping":
            # Options de scraping
            selected_season = st.selectbox(
                "Saison",
                options=list(SEASONS_CONFIG.keys()),
                index=0
            )
            
            if st.button("🚀 Lancer le scraping"):
                with st.spinner("Scraping en cours..."):
                    filename = lancer_scraping(theme, selected_season)
                    if filename:
                        st.session_state['last_scraped_file'] = filename
        
        else:
            # Options de visualisation
            selected_season = st.selectbox(
                "Saison",
                options=list(SEASONS_CONFIG.keys()),
                index=0
            )
            
            display_type = st.radio(
                "Type d'analyse",
                ["Top Tireurs", "Meilleurs Buteurs", "Meilleur xG"],
                index=0
            )
            
            num_players = st.slider("Nombre de joueurs", 1, 10, 6,
                                   help="Sélectionnez le nombre de joueurs à afficher")
            
            display_size = st.radio(
                "Taille d'affichage",
                ["Large (1 par ligne)", "Compact (2 par ligne)", "Grille (3 par ligne)"],
                index=2
            )
        
        st.markdown("---")
        
        # Info box
        st.markdown("""
        <div class='info-box'>
        <strong>✨ Améliorations !</strong><br>
        • Hexbins plus visibles avec bordures<br>
        • Colorbar légende ajoutée<br>
        • Stats enrichies (cadrés, contrés, buts vs xG)<br>
        • Situations de tir principales<br>
        • Penalties exclus de l'analyse
        </div>
        """, unsafe_allow_html=True)
    
    # Affichage selon le mode
    if mode == "📊 Visualisation":
        filename = get_filename(theme['slug'], selected_season)
        
        if not Path(filename).exists():
            st.warning(f"⚠️ Fichier {filename} non trouvé. Lancez d'abord le scraping.")
            return
        
        data = load_data(filename)
        
        if data is None or len(data) == 0:
            st.error("❌ Impossible de charger les données")
            return
        
        # Stats globales
        st.markdown("## 📈 Statistiques Globales")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        total_shots = len(data)
        total_goals = len(data[data['type_evenement'] == 'Goal'])
        avg_xg = data['xg'].mean()
        conversion_rate = (total_goals / total_shots * 100) if total_shots > 0 else 0
        total_xg = data['xg'].sum()
        
        with col1:
            st.metric("Tirs totaux", f"{total_shots:,}")
        with col2:
            st.metric("Buts marqués", f"{total_goals:,}")
        with col3:
            st.metric("xG total", f"{total_xg:.1f}")
        with col4:
            st.metric("xG moyen", f"{avg_xg:.3f}")
        with col5:
            st.metric("Taux conversion", f"{conversion_rate:.1f}%")
        
        st.markdown("---")
        
        # Shotmaps
        st.markdown("## 🎯 Shotmaps Détaillées")
        
        # Préparation données pour shotmaps
        if display_type == "Top Tireurs":
            data_grouped = data.groupby(['joueur_id', 'joueur', 'equipe_id']).size().reset_index(name='Total')
        elif display_type == "Meilleurs Buteurs":
            goals_data = data[data['type_evenement'] == 'Goal']
            data_grouped = goals_data.groupby(['joueur_id', 'joueur', 'equipe_id']).size().reset_index(name='Total')
        else:
            data_grouped = data.groupby(['joueur_id', 'joueur', 'equipe_id'])['xg'].sum().reset_index(name='Total')
        
        data_grouped = data_grouped.sort_values(by='Total', ascending=False).head(num_players)
        
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
        
        # Footer
        st.markdown("---")
        st.markdown("""
            <div style='text-align: center; padding: 1.5rem 0;'>
                <p style='color: #64748b; font-size: 0.85rem;'>
                    📊 Données FotMob • 🎨 Visualisation mplsoccer • 🔥 Hexbins haute visibilité
                </p>
            </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
