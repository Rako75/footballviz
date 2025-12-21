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
    '2025/2026':'2025/2026',
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
        st.success(f"🎉 Données collectées: ({len(all_data)} tirs)")
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

def create_shotmap(data, player_id, theme, player_info, size='normal'):
    """Crée une carte de tirs avec photo du joueur et barre de densité"""
    if size == 'large':
        figsize = (10, 13)
        font_sizes = {'title': 14, 'stats_label': 8, 'stats_value': 14, 'distance': 9}
    else:
        figsize = (6, 8)
        font_sizes = {'title': 10, 'stats_label': 6, 'stats_value': 10, 'distance': 7}
    
    fig, ax = plt.subplots(figsize=figsize, facecolor=theme['background'])
    ax.set_facecolor(theme['background'])
    
    pitch = VerticalPitch(
        pitch_type='uefa', half=True, goal_type='box',
        linewidth=1.5, line_color=mcolors.to_hex(mcolors.to_rgba(theme['text'], alpha=0.2)),
        pad_bottom=-10, pad_top=15, pitch_color=theme['background']
    )
    pitch.draw(ax=ax)
    
    player_data = data[data['joueur_id'] == player_id]
    cmap = mcolors.LinearSegmentedColormap.from_list('LeagueTheme', theme['gradient'], N=100)
    
    # Hexbins améliorés avec bordures blanches épaisses et alpha élevé
    hexbin = pitch.hexbin(
        x=player_data['position_x'], y=player_data['position_y'], 
        ax=ax, cmap=cmap, gridsize=(16, 16), zorder=2, 
        edgecolors='white', linewidths=1.8, alpha=1.0, mincnt=1
    )
    
    median_x = player_data['position_x'].median()
    x_circle, y_circle = semicircle(104.8 - median_x, 34, 104.8)
    ax.plot(x_circle, y_circle, ls='--', color=theme['accent'], lw=2, alpha=0.6, zorder=3)
    
    stats = {
        'TIRS': player_data.shape[0],
        'BUTS': player_data[player_data['type_evenement'] == 'Goal'].shape[0],
        'xG': player_data['xg'].sum(),
        'xG/TIR': player_data['xg'].mean()
    }
    
    on_target = player_data[player_data['type_evenement'].isin(['Goal', 'SavedShot'])].shape[0]
    accuracy = (on_target / stats['TIRS'] * 100) if stats['TIRS'] > 0 else 0
    
    stat_y_start = 60
    for i, (label, value) in enumerate(stats.items()):
        x_pos = 10 + (i * 14.5)
        ax.text(x_pos, stat_y_start, label, 
                ha='center', va='bottom', fontsize=font_sizes['stats_label'], 
                color=mcolors.to_hex(mcolors.to_rgba(theme['text'], alpha=0.6)), 
                weight='bold', fontfamily='Montserrat')
        val_fmt = f"{value:.0f}" if label in ['TIRS', 'BUTS'] else f"{value:.2f}"
        ax.text(x_pos, stat_y_start - 2, val_fmt, 
                ha='center', va='top', fontsize=font_sizes['stats_value'], 
                color=theme['accent'], weight='heavy', fontfamily='Montserrat')
    
    dist_yds = ((105 - median_x) * 18) / 16.5
    dist_m = dist_yds * 0.9144
    
    info_text = f"Distance Médiane: {dist_m:.1f}m  |  Précision: {accuracy:.0f}%"
    ax.text(34, 108, info_text,
            ha='center', va='center', fontsize=font_sizes['distance'],
            color=theme['text'], weight='bold', fontfamily='Montserrat',
            bbox=dict(facecolor=theme['background'], edgecolor=theme['accent'], 
                     boxstyle='round,pad=0.5', alpha=0.9, linewidth=2))
    
    # Titre avec nom du joueur
    player_name = player_info['joueur'].upper()
    ax.text(34, 120, player_name, 
            ha='center', va='center', fontsize=font_sizes['title'], 
            color=theme['text'], weight='black', fontfamily='Montserrat',
            bbox=dict(facecolor=theme['background'], edgecolor='none', 
                     boxstyle='round,pad=0.7', alpha=0.8))
    
    # Sous-titre avec équipe et saison
    team_name = player_info['equipe_joueur']
    season = player_info['saison']
    subtitle_text = f"{team_name} | {season}"
    ax.text(34, 115, subtitle_text, 
            ha='center', va='center', fontsize=font_sizes['distance'], 
            color=mcolors.to_hex(mcolors.to_rgba(theme['text'], alpha=0.7)), 
            weight='semibold', fontfamily='Montserrat')
    
    ax.plot([20, 48], [112, 112], color=theme['accent'], lw=3, alpha=0.9)
    
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
    
    # Photo du joueur
    try:
        player_logo_ax = ax.inset_axes([0.80, 0.88, 0.15, 0.15])
        player_icon_url = f'https://images.fotmob.com/image_resources/playerimages/{player_id}.png'
        player_icon = Image.open(urllib.request.urlopen(player_icon_url))
        player_logo_ax.imshow(player_icon)
        player_logo_ax.axis('off')
    except Exception as e:
        pass
    
    # Description des hexbins en bas de la shotmap
    density_text = "Hexbins : plus la couleur est claire, plus la fréquence de tirs est élevée"
    ax.text(34, 50, density_text,
            ha='center', va='center', fontsize=font_sizes['distance']-1,
            color=mcolors.to_hex(mcolors.to_rgba(theme['text'], alpha=0.7)), 
            style='italic', fontfamily='Montserrat')
    
    plt.tight_layout()
    return fig

def main():
    st.markdown("# Analyse des Zones de Tir")
    st.markdown("""<p class='subtitle'>
        Outil professionnel de visualisation et d'analyse des shotmaps<br>
        Collecte automatisée des données • Cartographie des zones de tir
    </p>""", unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("<h2 class='sidebar-title'>⚙️ Configuration</h2>", unsafe_allow_html=True)
        
        # Mode de l'application
        mode = st.radio("Mode d'utilisation", ["📊 Visualisation", "🔄 Collecte"], index=0)
        
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
        
        if mode == "🔄 Collecte":
            # Options de scraping
            selected_season = st.selectbox(
                "Saison",
                options=list(SEASONS_CONFIG.keys()),
                index=0
            )
            
            if st.button("🚀 Lancer la collecte"):
                with st.spinner("Collecte en cours..."):
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
            
            # Chargement préliminaire des données pour les filtres
            filename = get_filename(theme['slug'], selected_season)
            selected_team = 'Toutes les équipes'
            
            if Path(filename).exists():
                temp_data = load_data(filename)
                if temp_data is not None and len(temp_data) > 0:
                    # Filtre par équipe
                    all_teams = ['Toutes les équipes'] + sorted(temp_data['equipe_joueur'].unique().tolist())
                    selected_team = st.selectbox(
                        "Équipe",
                        options=all_teams,
                        index=0
                    )
            else:
                st.selectbox("Équipe", options=['Toutes les équipes'], index=0, disabled=True)
            
            display_type = st.radio(
                "Type d'analyse",
                ["Top Tireurs", "Meilleurs Buteurs", "Meilleur xG"],
                index=0
            )
            
            num_players = st.slider("Nombre de joueurs", 1, 20, 6,
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
        <strong>✨ Fonctionnalités !</strong><br>
        • Filtre par équipe<br>
        • Informations complètes sur les cartes<br>
        • Hexbins avec densité visuelle<br>
        • Photos des joueurs<br>
        • Penalties exclus de l'analyse
        </div>
        """, unsafe_allow_html=True)
    
    # Affichage selon le mode
    if mode == "📊 Visualisation":
        filename = get_filename(theme['slug'], selected_season)
        
        if not Path(filename).exists():
            st.warning(f"⚠️ Les données pour cette saison ne sont pas encore disponibles. Lancez la collecte depuis le menu 'Collecte' pour générer les informations nécessaires.")
            return
        
        data = load_data(filename)
        
        if data is None or len(data) == 0:
            st.error("❌ Impossible de charger les données")
            return
        
        # Application des filtres
        filtered_data = data.copy()
        
        # Ajouter la saison si elle n'existe pas
        if 'saison' not in filtered_data.columns:
            filtered_data['saison'] = selected_season
        
        # Filtre équipe
        if selected_team != 'Toutes les équipes':
            filtered_data = filtered_data[filtered_data['equipe_joueur'] == selected_team]
        
        # Stats globales
        st.markdown("## 📈 Statistiques Globales")
        col1, col2, col3, col4 = st.columns(4)
        
        total_shots = len(filtered_data)
        total_goals = len(filtered_data[filtered_data['type_evenement'] == 'Goal'])
        avg_xg = filtered_data['xg'].mean()
        conversion_rate = (total_goals / total_shots * 100) if total_shots > 0 else 0
        
        with col1:
            st.metric("Tirs totaux", f"{total_shots:,}")
        with col2:
            st.metric("Buts marqués", f"{total_goals:,}")
        with col3:
            st.metric("xG moyen", f"{avg_xg:.3f}")
        with col4:
            st.metric("Taux conversion", f"{conversion_rate:.1f}%")
        
        st.markdown("---")
        
        # Shotmaps
        st.markdown("## 🎯 Shotmaps Détaillées")
        
        # Préparation données pour shotmaps
        if display_type == "Top Tireurs":
            data_grouped = filtered_data.groupby(['joueur_id', 'joueur', 'equipe_id', 'equipe_joueur']).agg({
                'saison': 'first'
            }).reset_index()
            data_grouped['Total'] = filtered_data.groupby(['joueur_id', 'joueur', 'equipe_id', 'equipe_joueur']).size().values
        elif display_type == "Meilleurs Buteurs":
            goals_data = filtered_data[filtered_data['type_evenement'] == 'Goal']
            data_grouped = goals_data.groupby(['joueur_id', 'joueur', 'equipe_id', 'equipe_joueur']).agg({
                'saison': 'first'
            }).reset_index()
            data_grouped['Total'] = goals_data.groupby(['joueur_id', 'joueur', 'equipe_id', 'equipe_joueur']).size().values
        else:
            data_grouped = filtered_data.groupby(['joueur_id', 'joueur', 'equipe_id', 'equipe_joueur']).agg({
                'xg': 'sum',
                'saison': 'first'
            }).reset_index()
            data_grouped.rename(columns={'xg': 'Total'}, inplace=True)
        
        data_grouped = data_grouped.sort_values(by='Total', ascending=False).head(num_players)
        
        if len(data_grouped) == 0:
            st.warning("⚠️ Aucun joueur ne correspond aux critères sélectionnés.")
            return
        
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
                    player_info = {
                        'joueur': data_grouped['joueur'].iloc[player_idx],
                        'equipe_joueur': data_grouped['equipe_joueur'].iloc[player_idx],
                        'saison': data_grouped['saison'].iloc[player_idx]
                    }
                    with cols[col_idx]:
                        with st.spinner(f"🎨 Génération..."):
                            fig = create_shotmap(filtered_data, player_id, theme, player_info, size=size)
                            st.pyplot(fig, use_container_width=True)
                            plt.close(fig)
        
        # Footer
        st.markdown("---")
        st.markdown("""
            <div style='text-align: center; padding: 1.5rem 0;'>
                <p style='color: #64748b; font-size: 0.85rem;'>
                    📊 Données FotMob • 🎨 Visualisation mplsoccer • 👤 Photos des joueurs
                </p>
            </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
