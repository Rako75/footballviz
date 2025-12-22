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

# --- CONFIGURATION INITIALE ---
st.set_page_config(
    page_title="Football Shotmaps Pro",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CHARGEMENT DES POLICES ---
# Utilisation d'une fonction mise en cache pour éviter les rechargements inutiles
@st.cache_resource
def load_fonts():
    font_url = "https://github.com/googlefonts/Montserrat/raw/main/fonts/ttf/Montserrat-Regular.ttf"
    font_path = 'Montserrat-Regular.ttf'
    if not os.path.exists(font_path):
        urllib.request.urlretrieve(font_url, font_path)
    fm.fontManager.addfont(font_path)
    prop = fm.FontProperties(fname=font_path)
    # Configuration globale Matplotlib
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = [prop.get_name()]
    return prop

font_prop = load_fonts()

# --- DESIGN SYSTEM & CSS (Style "Linear/Vercel" Dark Mode) ---
st.markdown("""
<style>
    /* Import Inter font pour l'interface */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Reset & Base */
    .stApp {
        background-color: #0E1117; /* Fond très sombre, quasi noir */
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        letter-spacing: -0.02em;
    }
    
    /* Titres */
    h1 { color: #FFFFFF; font-weight: 700; font-size: 2.2rem; margin-bottom: 0.5rem; }
    h2 { color: #E0E0E0; font-weight: 600; font-size: 1.5rem; margin-top: 2rem; margin-bottom: 1rem; }
    h3 { color: #A0A0A0; font-weight: 500; font-size: 1.1rem; }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #161B22;
        border-right: 1px solid #30363D;
    }
    
    /* Widgets (Inputs) */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #21262D;
        border: 1px solid #30363D;
        color: white;
        border-radius: 6px;
    }
    
    /* Cartes de métriques (Style Dashboard) */
    div[data-testid="metric-container"] {
        background-color: #161B22;
        border: 1px solid #30363D;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s;
    }
    div[data-testid="metric-container"]:hover {
        border-color: #58A6FF;
    }
    
    div[data-testid="stMetricLabel"] { font-size: 0.8rem; color: #8B949E; text-transform: uppercase; letter-spacing: 0.05em; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; color: #FFFFFF; font-weight: 600; }
    
    /* Boutons */
    .stButton > button {
        background-color: #238636;
        color: white;
        border: 1px solid rgba(27, 31, 35, 0.15);
        border-radius: 6px;
        font-weight: 600;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background-color: #2ea043;
        border-color: rgba(27, 31, 35, 0.15);
    }
    
    /* Custom Info Box */
    .info-box {
        background: #161B22;
        border: 1px solid #30363D;
        border-left: 4px solid #58A6FF;
        padding: 1rem;
        border-radius: 6px;
        color: #C9D1D9;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }
    
    /* Header Divider */
    hr { border-color: #30363D; margin: 2rem 0; }
    
</style>
""", unsafe_allow_html=True)

# --- CONFIGURATION DONNÉES ---
LEAGUE_THEMES = {
    'LIGUE 1': {
        'id': 53, 'slug': 'ligue1',
        'background': '#0E1117', # Match Streamlit BG
        'accent': '#DAE018',     # Jaune fluo Ligue 1 moderne
        'text': '#FFFFFF',
        'cmap_colors': ['#0E1117', '#1a2c32', '#2a4c54', '#DAE018', '#ffffff'] # Dégradé sombre vers accent
    },
    'PREMIER LEAGUE': {
        'id': 47, 'slug': 'premier_league',
        'background': '#0E1117',
        'accent': '#04f5ff',     # Cyan PL
        'text': '#FFFFFF',
        'cmap_colors': ['#0E1117', '#180824', '#3d195b', '#04f5ff', '#ffffff']
    },
    'LA LIGA': {
        'id': 87, 'slug': 'la_liga',
        'background': '#0E1117',
        'accent': '#ff4b44',
        'text': '#FFFFFF',
        'cmap_colors': ['#0E1117', '#2b0c0b', '#7a1815', '#ff4b44', '#ffffff']
    },
    'BUNDESLIGA': {
        'id': 54, 'slug': 'bundesliga',
        'background': '#0E1117',
        'accent': '#d20515',
        'text': '#FFFFFF',
        'cmap_colors': ['#0E1117', '#260505', '#8a0d13', '#d20515', '#ffffff']
    },
    'SERIE A': {
        'id': 55, 'slug': 'serie_a',
        'background': '#0E1117',
        'accent': '#0057b8',     # Bleu Serie A
        'text': '#FFFFFF',
        'cmap_colors': ['#0E1117', '#031836', '#003a7d', '#0057b8', '#ffffff']
    },
    'CHAMPIONS LEAGUE': {
        'id': 42, 'slug': 'ucl',
        'background': '#0E1117',
        'accent': '#38bdf8',
        'text': '#FFFFFF',
        'cmap_colors': ['#0E1117', '#081c4a', '#1e3a8a', '#38bdf8', '#ffffff']
    }
}

SEASONS_CONFIG = {
    '2024/2025': '2024/2025',
    '2023/2024': '2023/2024',
    '2022/2023': '2022/2023'
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'sec-ch-ua-mobile': '?0'
}

# --- FONCTIONS UTILITAIRES ---

def get_filename(league_slug, season):
    return f"data_tirs_{league_slug}_{season.replace('/', '_')}.csv"

@st.cache_data(ttl=3600)
def fetch_finished_match_ids(league_id, season):
    """Récupère les IDs des matchs via l'API FotMob (avec cache)"""
    season_url = season.replace('/', '%2F')
    url = f'https://www.fotmob.com/api/data/leagues?id={league_id}&ccode3=FRA&season={season_url}'
    try:
        r = requests.get(url, headers=HEADERS, timeout=5)
        r.raise_for_status()
        matches = r.json().get('fixtures', {}).get('allMatches', [])
        return [str(m['id']) for m in matches if m.get('status', {}).get('finished')]
    except:
        return []

def extract_match_shots(match_id, league_name, season):
    """Extrait les données brutes d'un match"""
    url = f'https://www.fotmob.com/api/data/matchDetails?matchId={match_id}'
    try:
        r = requests.get(url, headers=HEADERS, timeout=5)
        if r.status_code != 200: return []
        
        data = r.json()
        general = data.get('general', {})
        content = data.get('content', {})
        
        if not content or 'shotmap' not in content or not content['shotmap']:
            return []
            
        home = general.get('homeTeam', {}).get('name', 'Home')
        away = general.get('awayTeam', {}).get('name', 'Away')
        
        shots = []
        for s in content['shotmap'].get('shots', []):
            shots.append({
                'match_id': match_id,
                'ligue': league_name,
                'saison': season,
                'date': general.get('matchTimeUTC'),
                'type_evenement': s.get('eventType'),
                'equipe_id': s.get('teamId'),
                'joueur': s.get('playerName'),
                'equipe_joueur': home if s.get('teamId') == general.get('homeTeam', {}).get('id') else away,
                'joueur_id': s.get('playerId'),
                'xg': s.get('expectedGoals'),
                'situation': s.get('situation'),
                'position_x': s.get('x'),
                'position_y': s.get('y'),
            })
        return shots
    except:
        return []

def run_scraping_process(league_conf, season):
    filename = get_filename(league_conf['slug'], season)
    
    with st.status(f"📥 Récupération des données : {league_conf['slug']} ({season})", expanded=True) as status:
        st.write("🔍 Recherche des matchs terminés...")
        ids = fetch_finished_match_ids(league_conf['id'], season)
        
        if not ids:
            status.update(label="❌ Aucun match trouvé", state="error")
            return None
            
        st.write(f"✅ {len(ids)} matchs identifiés. Extraction des tirs...")
        progress = st.progress(0)
        all_data = []
        
        # Limit scraping for demo performance/anti-ban, remove slicing [0:20] for full production
        ids_to_process = ids 
        
        for i, mid in enumerate(ids_to_process):
            all_data.extend(extract_match_shots(mid, league_conf['slug'], season))
            progress.progress((i + 1) / len(ids_to_process))
            time.sleep(0.05) # Respectful delay
            
        if all_data:
            df = pd.DataFrame(all_data)
            df.to_csv(filename, index=False)
            status.update(label=f"🎉 Succès ! {len(all_data)} tirs collectés.", state="complete")
            return filename
        else:
            status.update(label="⚠️ Aucune donnée de tir trouvée.", state="error")
            return None

@st.cache_data
def load_data(path):
    if not os.path.exists(path): return None
    df = pd.read_csv(path)
    # Filter penalties
    return df[df['situation'] != 'Penalty']

# --- VIZ GENERATION ---

def create_pro_shotmap(data, player_id, theme, player_info):
    """Génère une shotmap au style épuré et professionnel"""
    
    # Filtrage joueur
    df_player = data[data['joueur_id'] == player_id]
    if df_player.empty: return None

    # Configuration Figure
    fig, ax = plt.subplots(figsize=(7, 9), facecolor=theme['background'])
    # Suppression des bordures matplotlib pour intégration seamless
    fig.patch.set_facecolor(theme['background'])
    ax.set_facecolor(theme['background'])

    # Pitch Setup (Mplsoccer)
    pitch = VerticalPitch(
        pitch_type='uefa', 
        half=True,
        goal_type='box',
        line_color='#30363D', # Gris très subtil pour les lignes
        linewidth=1.2,
        pad_bottom=-5, 
        pad_top=15, 
        pitch_color=theme['background']
    )
    pitch.draw(ax=ax)

    # Création de la Colormap personnalisée (du fond vers l'accent)
    cmap = mcolors.LinearSegmentedColormap.from_list('ThemeMap', theme['cmap_colors'], N=100)

    # Hexbins (Style moderne : moins d'opacité, bordures fines)
    pitch.hexbin(
        x=df_player['position_x'], 
        y=df_player['position_y'], 
        ax=ax, 
        cmap=cmap, 
        gridsize=(16, 16), 
        zorder=2, 
        edgecolors=theme['background'], # Bordure couleur fond pour effet "découpe"
        linewidths=0.5, 
        alpha=0.9, 
        mincnt=1
    )

    # Stats Calculation
    stats = {
        'Tirs': len(df_player),
        'Buts': len(df_player[df_player['type_evenement'] == 'Goal']),
        'xG': df_player['xg'].sum(),
        'xG/Tir': df_player['xg'].mean()
    }
    
    # Annotations Stats (En haut, minimaliste)
    stat_str = f"{stats['Tirs']} Tirs  •  {stats['Buts']} Buts  •  {stats['xG']:.2f} xG"
    ax.text(34, 116, stat_str, 
            ha='center', va='center', fontsize=9, color='#8B949E', fontfamily='Montserrat')
            
    # Nom du joueur
    ax.text(34, 122, player_info['joueur'].upper(), 
            ha='center', va='center', fontsize=14, color=theme['text'], 
            weight='bold', fontfamily='Montserrat', letter_spacing=1)

    # Sous-titre Équipe
    ax.text(34, 119, f"{player_info['equipe_joueur']} | {player_info['saison']}", 
            ha='center', va='center', fontsize=8, color=theme['accent'], 
            weight='medium', fontfamily='Montserrat')

    # Ligne décorative subtile
    ax.plot([25, 43], [113, 113], color='#30363D', lw=1)

    # Insertion Image Joueur (Rond)
    try:
        url_img = f'https://images.fotmob.com/image_resources/playerimages/{player_id}.png'
        # On place l'image en haut à droite, plus discrète
        ax_img = ax.inset_axes([0.82, 0.88, 0.13, 0.13])
        img = Image.open(urllib.request.urlopen(url_img))
        ax_img.imshow(img)
        ax_img.axis('off')
    except:
        pass # Pas d'image, pas grave

    plt.tight_layout()
    return fig

# --- MAIN APP ---

def main():
    # Sidebar
    with st.sidebar:
        st.markdown("## ⚙️ Paramètres")
        
        mode = st.segmented_control("Mode", ["Visualisation", "Data Mining"], default="Visualisation")
        
        st.markdown("---")
        
        selected_league = st.selectbox("Compétition", list(LEAGUE_THEMES.keys()))
        theme = LEAGUE_THEMES[selected_league]
        
        # Petit indicateur visuel de la ligue
        st.markdown(
            f"<div style='background:{theme['accent']}; height:4px; width:100%; border-radius:2px; margin-top:-10px; margin-bottom:20px; opacity:0.8;'></div>", 
            unsafe_allow_html=True
        )
        
        selected_season = st.selectbox("Saison", list(SEASONS_CONFIG.keys()))
        
        if mode == "Data Mining":
            st.warning("Le mining peut prendre plusieurs minutes.")
            if st.button("Lancer l'extraction", use_container_width=True):
                run_scraping_process(theme, selected_season)

        st.markdown("---")
        st.markdown("""
        <div style='font-size:0.75rem; color:#8B949E; text-align:center'>
        Football Shotmaps Pro v2.0<br>
        Designed for Performance
        </div>
        """, unsafe_allow_html=True)

    # Main Content
    st.title("Performance & Shotmaps")
    st.markdown(f"Analyse tactique • {selected_league} • {selected_season}")
    
    filename = get_filename(theme['slug'], selected_season)
    
    if not os.path.exists(filename):
        if mode == "Visualisation":
            st.info("👋 Bienvenue. Aucune donnée locale détectée pour cette configuration. Veuillez passer en mode **Data Mining** via la barre latérale pour télécharger les données.")
        return

    df = load_data(filename)
    if df is None or df.empty:
        st.error("Fichier de données corrompu ou vide.")
        return

    # Filtres Zone
    col_filter_1, col_filter_2, col_filter_3 = st.columns([2, 1, 1])
    with col_filter_1:
        teams = ['Toutes les équipes'] + sorted(df['equipe_joueur'].unique())
        selected_team = st.selectbox("Filtrer par équipe", teams)
    
    with col_filter_2:
        top_n = st.slider("Joueurs affichés", 3, 12, 6)

    # Filtrage Data
    df_filtered = df.copy()
    if selected_team != 'Toutes les équipes':
        df_filtered = df_filtered[df_filtered['equipe_joueur'] == selected_team]

    # KPIs Globaux (Dashboard Style)
    st.markdown("### 📊 Métriques Clés")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    total_goals = len(df_filtered[df_filtered['type_evenement'] == 'Goal'])
    total_shots = len(df_filtered)
    total_xg = df_filtered['xg'].sum()
    xg_per_shot = df_filtered['xg'].mean()
    
    kpi1.metric("Total Tirs", f"{total_shots:,}")
    kpi2.metric("Buts Marqués", f"{total_goals:,}")
    kpi3.metric("xG Cumulé", f"{total_xg:.2f}")
    kpi4.metric("xG / Tir", f"{xg_per_shot:.3f}")

    st.divider()

    # Logique de tri pour l'affichage des cartes
    # On groupe par joueur et on trie par xG total pour avoir les joueurs les plus dangereux
    grouped = df_filtered.groupby(['joueur_id', 'joueur', 'equipe_joueur']).agg({
        'xg': 'sum',
        'match_id': 'count' # Count shots
    }).reset_index().sort_values('xg', ascending=False).head(top_n)

    st.markdown("### 🎯 Analyse des Zones de Danger")
    
    # Grid Layout pour les shotmaps
    cols = st.columns(3) # Grille de 3 colonnes
    
    for idx, row in grouped.iterrows():
        player_id = row['joueur_id']
        col_idx = list(grouped.index).index(idx) % 3
        
        player_info = {
            'joueur': row['joueur'],
            'equipe_joueur': row['equipe_joueur'],
            'saison': selected_season
        }
        
        with cols[col_idx]:
            # Conteneur visuel pour chaque graphique
            with st.container():
                fig = create_pro_shotmap(df_filtered, player_id, theme, player_info)
                if fig:
                    st.pyplot(fig, use_container_width=True)
                    plt.close(fig)

if __name__ == "__main__":
    main()
