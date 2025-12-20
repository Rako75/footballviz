# -*- coding: utf-8 -*-
"""
Application Streamlit - Shotmap Multi-Ligues Professionnel
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import matplotlib.colors as mcolors
import matplotlib.font_manager as fm
from matplotlib.patches import RegularPolygon
from mplsoccer import VerticalPitch
from PIL import Image
from highlight_text import fig_text
import urllib.request
import numpy as np
import os
import io

# Configuration de la page
st.set_page_config(
    page_title="Shotmap Analytics Pro",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour un design moderne
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .stSelectbox, .stMultiSelect, .stSlider {
        color: #ffffff;
    }
    .css-1d391kg {
        padding-top: 2rem;
    }
    h1 {
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .stButton>button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(59, 130, 246, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------
# CONFIGURATION DES THÈMES & LIGUES
# -----------------------------------------------------------

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

# Postes disponibles
POSITIONS = {
    'Tous': None,
    'Attaquants': ['CF', 'ST', 'FW', 'LW', 'RW'],
    'Milieux': ['CM', 'CAM', 'CDM', 'LM', 'RM', 'AM'],
    'Défenseurs': ['CB', 'LB', 'RB', 'LWB', 'RWB', 'DF']
}

# -----------------------------------------------------------
# FONCTIONS UTILITAIRES
# -----------------------------------------------------------

@st.cache_data
def load_data(csv_file):
    """Charge et prépare les données"""
    if os.path.exists(csv_file):
        data = pd.read_csv(csv_file)
    else:
        # Données de démo
        st.warning(f"⚠️ Fichier '{csv_file}' introuvable. Mode démo activé.")
        data = pd.DataFrame({
            'joueur_id': [1]*50 + [2]*50 + [3]*50,
            'joueur': ['Demo Player A']*50 + ['Demo Player B']*50 + ['Demo Player C']*50,
            'equipe_id': [9825]*150,
            'minute': list(range(50)) * 3,
            'situation': ['Open Play']*150,
            'position_x': np.random.uniform(70, 100, 150),
            'position_y': np.random.uniform(20, 50, 150),
            'xg': np.random.uniform(0.02, 0.5, 150),
            'type_evenement': np.random.choice(['Goal', 'Miss'], 150),
            'poste': np.random.choice(['CF', 'LW', 'RW'], 150)
        })
    
    # Filtrer les penalties
    data = data[data['situation'] != 'Penalty'].reset_index(drop=True)
    
    # Ajouter colonne is_in_box
    def is_inside_box(x, y):
        return (x >= 13.84) & (x <= 54.16) & (y >= 88.5)
    
    data['is_in_box'] = [is_inside_box(y, x) for x, y in zip(data['position_x'], data['position_y'])]
    
    return data

def filter_by_position(data, positions):
    """Filtre les données par poste"""
    if positions is None:
        return data
    if 'poste' not in data.columns:
        return data
    return data[data['poste'].isin(positions)]

def prepare_top_players(data, n_players=6):
    """Prépare les données des meilleurs joueurs"""
    data_groupped = data.groupby(['joueur_id', 'joueur', 'equipe_id', 'is_in_box'])['minute'].count().reset_index()
    data_groupped = data_groupped.pivot(
        columns='is_in_box',
        index=['joueur_id', 'joueur', 'equipe_id'],
        values='minute'
    ).reset_index()
    
    if True not in data_groupped.columns:
        data_groupped[True] = 0
    if False not in data_groupped.columns:
        data_groupped[False] = 0
    
    data_groupped.rename(columns={False: 'False', True: 'True'}, inplace=True)
    data_groupped.fillna(0, inplace=True)
    data_groupped['total'] = data_groupped['False'] + data_groupped['True']
    
    return data_groupped.sort_values(by='total', ascending=False).head(n_players)

def semicircle(r, h, k):
    """Calcule un demi-cercle"""
    x0 = h - r
    x1 = h + r
    x = np.linspace(x0, x1, 500)
    y = k - np.sqrt(r**2 - (x - h)**2)
    return x, y

def plot_hexbin_shot(ax, data, playerId, theme):
    """Génère un hexbin shotmap pour un joueur"""
    BACKGROUND_COLOR = theme['background']
    ACCENT_COLOR = theme['accent']
    TEXT_COLOR = theme['text']
    SUBTEXT_COLOR = mcolors.to_hex(mcolors.to_rgba(TEXT_COLOR, alpha=0.7))
    LINE_COLOR = mcolors.to_hex(mcolors.to_rgba(TEXT_COLOR, alpha=0.15))
    
    # Créer le terrain
    pitch = VerticalPitch(
        pitch_type='uefa', half=True, goal_type='box',
        linewidth=1.2, line_color=LINE_COLOR,
        pad_bottom=-10, pad_top=15, pitch_color=BACKGROUND_COLOR
    )
    pitch.draw(ax=ax)
    
    aux_data = data[data['joueur_id'] == playerId]
    
    # Créer colormap
    pro_cmap = mcolors.LinearSegmentedColormap.from_list('LeagueTheme', theme['gradient'], N=100)
    
    # Hexbin
    bins = pitch.hexbin(
        x=aux_data['position_x'], y=aux_data['position_y'],
        ax=ax, cmap=pro_cmap, gridsize=(14, 14),
        zorder=2, edgecolors='None', alpha=0.9, mincnt=1
    )
    
    # Distance médiane
    median_x = aux_data['position_x'].median()
    x_circle, y_circle = semicircle(104.8 - median_x, 34, 104.8)
    ax.plot(x_circle, y_circle, ls=':', color=SUBTEXT_COLOR, lw=1, alpha=0.7, zorder=3)
    
    # Statistiques
    stats_data = {
        'Tirs': aux_data.shape[0],
        'Buts': aux_data[aux_data['type_evenement'] == 'Goal'].shape[0],
        'xG': aux_data['xg'].sum(),
        'xG/Tir': aux_data['xg'].mean()
    }
    
    stat_y_pos = 73
    start_x = 10
    gap = 16
    
    for i, (label, value) in enumerate(stats_data.items()):
        current_x = start_x + (i * gap)
        label_spaced = " ".join(list(label.upper()))
        ax.text(current_x, stat_y_pos, label_spaced, ha='center', va='bottom',
                fontsize=5, color=SUBTEXT_COLOR, weight='bold')
        val_fmt = f"{value:.0f}" if label in ['Tirs', 'Buts'] else f"{value:.2f}"
        ax.text(current_x, stat_y_pos - 2, val_fmt, ha='center', va='top',
                fontsize=9, color=TEXT_COLOR, weight='bold')
    
    # Distance
    dist_yds = ((105 - median_x) * 18) / 16.5
    ax.text(34, 108, f"Dist. Médiane: {dist_yds:.1f} yds",
            ha='center', va='center', fontsize=6,
            color=ACCENT_COLOR, weight='bold',
            bbox=dict(facecolor=BACKGROUND_COLOR, edgecolor=LINE_COLOR,
                     boxstyle='round,pad=0.3', alpha=0.8))
    
    # Nom du joueur
    player_name = aux_data['joueur'].iloc[0]
    ax.text(34, 116, player_name.upper(), ha='center', va='center',
            fontsize=10, color=TEXT_COLOR, weight='heavy')
    
    ax.plot([24, 44], [113, 113], color=ACCENT_COLOR, lw=1.5, alpha=0.8)
    
    return ax, aux_data['equipe_id'].iloc[0]

def generate_shotmap(data, top_players, theme, n_players):
    """Génère la figure complète"""
    BACKGROUND_COLOR = theme['background']
    ACCENT_COLOR = theme['accent']
    TEXT_COLOR = theme['text']
    SUBTEXT_COLOR = mcolors.to_hex(mcolors.to_rgba(TEXT_COLOR, alpha=0.7))
    
    # Calculer dimensions de la grille
    if n_players <= 3:
        nrows, ncols = 1, n_players
        figsize = (10, 5)
    elif n_players <= 6:
        nrows, ncols = 2, 3
        figsize = (10, 8)
    else:
        nrows, ncols = 3, 3
        figsize = (10, 10)
    
    fig, axs = plt.subplots(nrows=nrows, ncols=ncols, figsize=figsize, facecolor=BACKGROUND_COLOR)
    
    if n_players == 1:
        axs = np.array([axs])
    axs = np.array(axs).reshape(-1)
    
    for index, ax in enumerate(axs):
        ax.set_facecolor(BACKGROUND_COLOR)
        if index < len(top_players):
            player_id = top_players['joueur_id'].iloc[index]
            _, team_id = plot_hexbin_shot(ax, data, player_id, theme)
            
            # Logo équipe
            fotmob_url = 'https://images.fotmob.com/image_resources/logo/teamlogo/'
            try:
                logo_ax = ax.inset_axes([0.05, 0.88, 0.12, 0.12])
                icon = Image.open(urllib.request.urlopen(f'{fotmob_url}{team_id:.0f}.png'))
                logo_ax.imshow(icon)
                logo_ax.axis('off')
            except:
                pass
        else:
            ax.axis('off')
    
    plt.subplots_adjust(wspace=0.1, hspace=0.1)
    
    # Logo ligue
    league_id = theme['id']
    fotmob_league_url = f'https://images.fotmob.com/image_resources/logo/leaguelogo/{league_id}.png'
    
    league_logo_ax = fig.add_axes([0.075, 0.915, 0.045, 0.045])
    league_logo_ax.set_facecolor(BACKGROUND_COLOR)
    league_logo_ax.axis('off')
    
    try:
        league_icon = Image.open(urllib.request.urlopen(fotmob_league_url))
        league_logo_ax.imshow(league_icon)
    except:
        pass
    
    # Titre
    fig_text(
        x=0.13, y=0.96,
        s=f"ANALYSE DES TIRS | <{theme['name']}>",
        highlight_textprops=[{"color": ACCENT_COLOR, "weight": "bold"}],
        va="bottom", ha="left", fontsize=20, color=TEXT_COLOR, weight="bold"
    )
    
    fig_text(
        x=0.13, y=0.935,
        s="Comparaison des zones de tir et efficacité (hors penalties) | Saison 2024/2025",
        va="bottom", ha="left", fontsize=9, color=SUBTEXT_COLOR
    )
    
    fig.text(
        0.9, 0.02, "Data: FotMob | Viz: @AlexRakotomalala",
        ha='right', fontsize=6, color=SUBTEXT_COLOR, alpha=0.6
    )
    
    return fig

# -----------------------------------------------------------
# INTERFACE STREAMLIT
# -----------------------------------------------------------

# En-tête
st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1 style='font-size: 3rem; margin-bottom: 0.5rem;'>⚽ SHOTMAP ANALYTICS PRO</h1>
        <p style='font-size: 1.2rem; color: #64748b;'>Analyse avancée des zones de tir multi-ligues</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ CONFIGURATION")
    
    # Sélection ligue
    selected_league = st.selectbox(
        "🏆 Ligue",
        options=list(LEAGUE_THEMES.keys()),
        index=1
    )
    
    st.markdown("---")
    
    # Sélection postes
    selected_positions = st.selectbox(
        "👤 Poste",
        options=list(POSITIONS.keys()),
        index=0
    )
    
    # Nombre de joueurs
    n_players = st.slider(
        "📊 Nombre de joueurs",
        min_value=1,
        max_value=9,
        value=6,
        step=1
    )
    
    st.markdown("---")
    
    # Bouton génération
    generate_btn = st.button("🚀 GÉNÉRER SHOTMAP", use_container_width=True)
    
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; padding: 1rem; background: #1e293b; border-radius: 8px;'>
            <p style='font-size: 0.8rem; color: #94a3b8; margin: 0;'>
                📊 Data: FotMob<br>
                💻 Viz: @AlexRakotomalala
            </p>
        </div>
    """, unsafe_allow_html=True)

# Zone principale
if generate_btn or 'first_run' not in st.session_state:
    st.session_state.first_run = True
    
    with st.spinner('🔄 Chargement des données...'):
        # Charger thème et données
        theme = LEAGUE_THEMES[selected_league]
        data = load_data(theme['file'])
        
        # Filtrer par poste
        position_filter = POSITIONS[selected_positions]
        filtered_data = filter_by_position(data, position_filter)
        
        if len(filtered_data) == 0:
            st.error("❌ Aucune donnée disponible pour cette sélection.")
        else:
            # Préparer top joueurs
            top_players = prepare_top_players(filtered_data, n_players)
            
            # Afficher métriques
            col1, col2, col3, col4 = st.columns(4)
            
            total_shots = len(filtered_data)
            total_goals = len(filtered_data[filtered_data['type_evenement'] == 'Goal'])
            avg_xg = filtered_data['xg'].mean()
            total_xg = filtered_data['xg'].sum()
            
            with col1:
                st.metric("🎯 Total Tirs", f"{total_shots:,}")
            with col2:
                st.metric("⚽ Total Buts", f"{total_goals}")
            with col3:
                st.metric("📈 xG Moyen", f"{avg_xg:.2f}")
            with col4:
                st.metric("💯 Total xG", f"{total_xg:.1f}")
            
            st.markdown("---")
            
            # Générer visualisation
            with st.spinner('🎨 Génération de la visualisation...'):
                filtered_data = filtered_data[filtered_data['joueur_id'].isin(top_players['joueur_id'])]
                fig = generate_shotmap(filtered_data, top_players, theme, n_players)
                
                # Afficher
                st.pyplot(fig)
                
                # Téléchargement
                buf = io.BytesIO()
                fig.savefig(buf, format='png', dpi=300, facecolor=theme['background'], bbox_inches='tight')
                buf.seek(0)
                
                st.download_button(
                    label="📥 Télécharger PNG",
                    data=buf,
                    file_name=f"shotmap_{selected_league.lower().replace(' ', '_')}.png",
                    mime="image/png",
                    use_container_width=True
                )
                
                plt.close(fig)
            
            # Tableau des joueurs
            st.markdown("### 📋 Top Joueurs")
            display_df = top_players[['joueur', 'total']].copy()
            display_df.columns = ['Joueur', 'Total Tirs']
            st.dataframe(display_df, use_container_width=True, hide_index=True)

else:
    st.info("👈 Configurez vos paramètres dans la barre latérale et cliquez sur 'GÉNÉRER SHOTMAP'")
    
    # Afficher preview des ligues
    st.markdown("### 🏆 Ligues Disponibles")
    
    cols = st.columns(4)
    for idx, (league_name, theme) in enumerate(list(LEAGUE_THEMES.items())[:4]):
        with cols[idx]:
            st.markdown(f"""
                <div style='
                    background: linear-gradient(135deg, {theme['background']} 0%, {theme['accent']}40 100%);
                    padding: 1.5rem;
                    border-radius: 12px;
                    text-align: center;
                    border: 2px solid {theme['accent']}40;
                '>
                    <h3 style='color: {theme['text']}; margin: 0;'>{league_name}</h3>
                </div>
            """, unsafe_allow_html=True)
