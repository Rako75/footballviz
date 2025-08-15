import streamlit as st
import json
import re
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import to_rgba
import seaborn as sns
import matplotlib.image as mpimg
import matplotlib.patches as patches
from PIL import Image
from io import BytesIO
import matplotlib as mpl
from matplotlib.gridspec import GridSpec
from matplotlib.markers import MarkerStyle
from mplsoccer import Pitch, VerticalPitch
from matplotlib.font_manager import FontProperties
from matplotlib import rcParams
from matplotlib.patheffects import withStroke, Normal
from matplotlib.colors import LinearSegmentedColormap
from mplsoccer.utils import FontManager
import matplotlib.patheffects as path_effects
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.cbook import get_sample_data
from sklearn.cluster import KMeans
import warnings
from highlight_text import ax_text
from datetime import datetime
import tempfile
import os
import ast

# Configuration des couleurs
green = '#69f900'
red = '#ff4b44'
blue = '#00a0de'
violet = '#a369ff'
bg_color = '#ffffff'
line_color = '#000000'
col1 = '#ff4b44'
col2 = '#00a0de'

# Configuration Streamlit
st.set_page_config(
    page_title="Football Match Dashboard Generator",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styles CSS personnalisés
st.markdown("""
<style>
.main {
    padding-top: 1rem;
}
.stAlert {
    margin-top: 1rem;
}
.metric-container {
    background-color: #f8f9fa;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #007bff;
    margin: 0.5rem 0;
}
.upload-container {
    border: 2px dashed #cccccc;
    border-radius: 10px;
    padding: 2rem;
    text-align: center;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def get_xT_grid():
    """Récupère la grille xT"""
    try:
        xT_url = 'https://raw.githubusercontent.com/mckayjohns/youtube-videos/main/data/xT_Grid.csv'
        xT = pd.read_csv(xT_url, header=None)
        return np.array(xT)
    except:
        # Grille xT par défaut si l'URL ne fonctionne pas
        return np.random.rand(16, 12) * 0.1

def extract_json_from_html(html_content):
    """Extrait les données JSON du fichier HTML de WhoScored"""
    try:
        regex_pattern = r'(?<=require\.config\.params\["args"\].=.)[\s\S]*?;'
        data_txt = re.findall(regex_pattern, html_content)[0]
        
        # Ajout des guillemets pour le parser JSON
        data_txt = data_txt.replace('matchId', '"matchId"')
        data_txt = data_txt.replace('matchCentreData', '"matchCentreData"')
        data_txt = data_txt.replace('matchCentreEventTypeJson', '"matchCentreEventTypeJson"')
        data_txt = data_txt.replace('formationIdNameMappings', '"formationIdNameMappings"')
        data_txt = data_txt.replace('};', '}')
        
        return data_txt
    except Exception as e:
        st.error(f"Erreur lors de l'extraction des données: {e}")
        return None

def extract_data_from_dict(data):
    """Extrait les données nécessaires du dictionnaire"""
    try:
        events_dict = data["matchCentreData"]["events"]
        teams_dict = {
            data["matchCentreData"]['home']['teamId']: data["matchCentreData"]['home']['name'],
            data["matchCentreData"]['away']['teamId']: data["matchCentreData"]['away']['name']
        }
        
        # Création du DataFrame des joueurs
        players_home_df = pd.DataFrame(data["matchCentreData"]['home']['players'])
        players_home_df["teamId"] = data["matchCentreData"]['home']['teamId']
        players_away_df = pd.DataFrame(data["matchCentreData"]['away']['players'])
        players_away_df["teamId"] = data["matchCentreData"]['away']['teamId']
        players_df = pd.concat([players_home_df, players_away_df])
        
        return events_dict, players_df, teams_dict
    except Exception as e:
        st.error(f"Erreur lors de l'extraction des données: {e}")
        return None, None, None

def get_short_name(full_name):
    """Génère un nom court à partir du nom complet"""
    if pd.isna(full_name) or not isinstance(full_name, str):
        return full_name
    parts = full_name.split()
    if len(parts) == 1:
        return full_name
    elif len(parts) == 2:
        return parts[0][0] + ". " + parts[1]
    else:
        return parts[0][0] + ". " + parts[1][0] + ". " + " ".join(parts[2:])

def process_match_data(df, players_df, teams_dict):
    """Traite les données du match"""
    # Nettoyage des colonnes
    df['type'] = df['type'].str.extract(r"'displayName': '([^']+)")
    df['outcomeType'] = df['outcomeType'].str.extract(r"'displayName': '([^']+)")
    df['period'] = df['period'].str.extract(r"'displayName': '([^']+)")
    
    # Ajout xT
    try:
        xT = get_xT_grid()
        xT_rows, xT_cols = xT.shape
        
        dfxT = df.copy()
        dfxT = dfxT[~dfxT['qualifiers'].str.contains('Corner', na=False) & 
                   ~dfxT['qualifiers'].str.contains('ThrowIn', na=False)]
        dfxT = dfxT[(dfxT['type']=='Pass') & (dfxT['outcomeType']=='Successful')]
        
        if not dfxT.empty:
            dfxT['x1_bin_xT'] = pd.cut(dfxT['x'], bins=xT_cols, labels=False)
            dfxT['y1_bin_xT'] = pd.cut(dfxT['y'], bins=xT_rows, labels=False)
            dfxT['x2_bin_xT'] = pd.cut(dfxT['endX'], bins=xT_cols, labels=False)
            dfxT['y2_bin_xT'] = pd.cut(dfxT['endY'], bins=xT_rows, labels=False)
            
            dfxT['start_zone_value_xT'] = dfxT[['x1_bin_xT', 'y1_bin_xT']].apply(
                lambda x: xT[x[1]][x[0]] if pd.notna(x[1]) and pd.notna(x[0]) else 0, axis=1)
            dfxT['end_zone_value_xT'] = dfxT[['x2_bin_xT', 'y2_bin_xT']].apply(
                lambda x: xT[x[1]][x[0]] if pd.notna(x[1]) and pd.notna(x[0]) else 0, axis=1)
            
            dfxT['xT'] = dfxT['end_zone_value_xT'] - dfxT['start_zone_value_xT']
            
            # Merge xT data
            columns_to_drop = ['id', 'eventId', 'minute', 'second', 'teamId', 'x', 'y', 'expandedMinute', 'period', 'type', 'outcomeType', 'qualifiers',
                               'satisfiedEventsTypes', 'isTouch', 'playerId', 'endX', 'endY', 'relatedEventId', 'relatedPlayerId', 'blockedX', 'blockedY',
                               'goalMouthZ', 'goalMouthY', 'isShot']
            dfxT_clean = dfxT.drop(columns=[col for col in columns_to_drop if col in dfxT.columns], errors='ignore')
            df = df.merge(dfxT_clean[['xT']], left_index=True, right_index=True, how='left')
    except:
        df['xT'] = 0
    
    # Ajout des noms d'équipes
    df['teamName'] = df['teamId'].map(teams_dict)
    
    # Redimensionnement des coordonnées
    df['x'] = df['x'] * 1.05
    df['y'] = df['y'] * 0.68
    df['endX'] = df['endX'] * 1.05
    df['endY'] = df['endY'] * 0.68
    df['goalMouthY'] = df['goalMouthY'] * 0.68
    
    # Nettoyage du DataFrame des joueurs
    columns_to_drop = ['height', 'weight', 'age', 'isManOfTheMatch', 'field', 'stats', 
                      'subbedInPlayerId', 'subbedOutPeriod', 'subbedOutExpandedMinute',
                      'subbedInPeriod', 'subbedInExpandedMinute', 'subbedOutPlayerId', 'teamId']
    players_df = players_df.drop(columns=[col for col in columns_to_drop if col in players_df.columns], errors='ignore')
    
    # Fusion avec les données des joueurs
    df = df.merge(players_df, on='playerId', how='left')
    df = df.query("period != 'PenaltyShootout'")
    
    # Calcul des passes progressives
    df['pro'] = np.where((df['type'] == 'Pass') & (df['outcomeType'] == 'Successful') & (df['x'] > 42),
                        np.sqrt((105 - df['x'])**2 + (34 - df['y'])**2) - 
                        np.sqrt((105 - df['endX'])**2 + (34 - df['endY'])**2), 0)
    
    # Ajout des noms courts
    df['shortName'] = df['name'].apply(get_short_name)
    
    return df

def get_passes_df(events_dict):
    """Génère le DataFrame des passes"""
    df = pd.DataFrame(events_dict)
    df['eventType'] = df.apply(lambda row: row['type']['displayName'], axis=1)
    df['outcomeType'] = df.apply(lambda row: row['outcomeType']['displayName'], axis=1)
    df["receiver"] = df["playerId"].shift(-1)
    passes_ids = df.index[df['eventType'] == 'Pass']
    df_passes = df.loc[passes_ids, ["id", "x", "y", "endX", "endY", "teamId", "playerId", "receiver", "eventType", "outcomeType"]]
    return df_passes

def get_passes_between_df(team_id, passes_df, players_df, events_dict):
    """Calcule les passes entre joueurs"""
    passes_df = passes_df[passes_df["teamId"] == team_id]
    df = pd.DataFrame(events_dict)
    dfteam = df[df['teamId'] == team_id]
    
    # Ajouter les informations des joueurs
    passes_df = passes_df.merge(players_df[["playerId", "isFirstEleven"]], on='playerId', how='left')
    
    # Calculer les positions moyennes
    average_locs_and_count_df = (dfteam.groupby('playerId').agg({'x': ['median'], 'y': ['median', 'count']}))
    average_locs_and_count_df.columns = ['pass_avg_x', 'pass_avg_y', 'count']
    average_locs_and_count_df = average_locs_and_count_df.merge(
        players_df[['playerId', 'name', 'shirtNo', 'position', 'isFirstEleven']], 
        on='playerId', how='left')
    average_locs_and_count_df = average_locs_and_count_df.set_index('playerId')
    
    # Calculer les passes entre joueurs
    passes_player_ids_df = passes_df.loc[:, ['id', 'playerId', 'receiver', 'teamId']]
    passes_player_ids_df['pos_max'] = (passes_player_ids_df[['playerId', 'receiver']].max(axis='columns'))
    passes_player_ids_df['pos_min'] = (passes_player_ids_df[['playerId', 'receiver']].min(axis='columns'))
    
    passes_between_df = passes_player_ids_df.groupby(['pos_min', 'pos_max']).id.count().reset_index()
    passes_between_df.rename({'id': 'pass_count'}, axis='columns', inplace=True)
    
    passes_between_df = passes_between_df.merge(average_locs_and_count_df, left_on='pos_min', right_index=True)
    passes_between_df = passes_between_df.merge(average_locs_and_count_df, left_on='pos_max', right_index=True, suffixes=['', '_end'])
    
    return passes_between_df, average_locs_and_count_df

def pass_network_visualization(ax, passes_between_df, average_locs_and_count_df, col, team_id, teams_dict, flipped=False):
    """Visualisation du réseau de passes"""
    MAX_LINE_WIDTH = 15
    MAX_MARKER_SIZE = 3000
    
    if len(passes_between_df) == 0:
        pitch = Pitch(pitch_type='opta', goal_type='box', goal_alpha=.5, corner_arcs=True, 
                     pitch_color=bg_color, line_color=line_color, linewidth=2)
        pitch.draw(ax=ax)
        ax.text(50, 50, "Pas de données de passes", ha='center', va='center', fontsize=16)
        return
    
    passes_between_df['width'] = (passes_between_df.pass_count / passes_between_df.pass_count.max() * MAX_LINE_WIDTH)
    
    MIN_TRANSPARENCY = 0.05
    MAX_TRANSPARENCY = 0.85
    color = np.array(to_rgba(col))
    color = np.tile(color, (len(passes_between_df), 1))
    c_transparency = passes_between_df.pass_count / passes_between_df.pass_count.max()
    c_transparency = (c_transparency * (MAX_TRANSPARENCY - MIN_TRANSPARENCY)) + MIN_TRANSPARENCY
    color[:, 3] = c_transparency

    pitch = Pitch(pitch_type='opta', goal_type='box', goal_alpha=.5, corner_arcs=True, 
                 pitch_color=bg_color, line_color=line_color, linewidth=2)
    pitch.draw(ax=ax)

    # Lignes entre joueurs
    pass_lines = pitch.lines(passes_between_df.pass_avg_x, passes_between_df.pass_avg_y, 
                           passes_between_df.pass_avg_x_end, passes_between_df.pass_avg_y_end,
                           lw=passes_between_df.width, color=color, zorder=1, ax=ax)

    # Noeuds des joueurs
    for index, row in average_locs_and_count_df.iterrows():
        if row['isFirstEleven'] == True:
            pass_nodes = pitch.scatter(row['pass_avg_x'], row['pass_avg_y'], s=1000, marker='o', 
                                     color=bg_color, edgecolor=line_color, linewidth=2, alpha=1, ax=ax)
        else:
            pass_nodes = pitch.scatter(row['pass_avg_x'], row['pass_avg_y'], s=1000, marker='s', 
                                     color=bg_color, edgecolor=line_color, linewidth=2, alpha=0.75, ax=ax)

    # Numéros des joueurs
    for index, row in average_locs_and_count_df.iterrows():
        player_number = row["shirtNo"]
        pitch.annotate(player_number, xy=(row.pass_avg_x, row.pass_avg_y), 
                      c=col, ha='center', va='center', size=18, ax=ax)

    # Ligne médiane
    avgph = average_locs_and_count_df['pass_avg_x'].median()
    avgph_show = round(avgph*1.05, 2)
    ax.axvline(x=avgph, color='gray', linestyle='--', alpha=0.75, linewidth=2)

    team_names = list(teams_dict.values())
    away_team_id = [k for k, v in teams_dict.items() if k != team_id][0]

    if team_id == away_team_id:
        ax.invert_xaxis()
        ax.invert_yaxis()
        ax.text(avgph+1, 105, f"{avgph_show}m", fontsize=15, color=line_color, ha='right')
        ax.text(2, 2, "circle = starter\nbox = sub", color=col, size=12, ha='right', va='top')
        ax.text(-2, 105, "<--- Attacking Direction", color=col, size=15, ha='right', va='center')
        ax.set_title(f"Away team Passing Network", color=line_color, size=30, fontweight='bold')
    else:
        ax.text(avgph+1, -5, f"{avgph_show}m", fontsize=15, color=line_color, ha='left')
        ax.text(2, 98, "circle = starter\nbox = sub", color=col, size=12, ha='left', va='top')
        ax.text(-2, -5, "Attacking Direction --->", color=col, size=15, ha='left', va='center')
        ax.set_title(f"Home team Passing Network", color=line_color, size=30, fontweight='bold')

def plot_shotmap(ax, df, teams_dict, hxg=0, axg=0, hxgot=0, axgot=0):
    """Visualisation de la carte des tirs"""
    path_eff = [path_effects.Stroke(linewidth=3, foreground=bg_color), path_effects.Normal()]
    
    # IDs des équipes
    hteamID = list(teams_dict.keys())[0]
    ateamID = list(teams_dict.keys())[1]
    hteamName = teams_dict[hteamID]
    ateamName = teams_dict[ateamID]
    
    # Filtrer les tirs
    mask4 = (df['type'] == 'Goal') | (df['type'] == 'MissedShots') | (df['type'] == 'SavedShot') | (df['type'] == 'ShotOnPost')
    Shotsdf = df[mask4].copy()
    Shotsdf.reset_index(drop=True, inplace=True)

    # Calcul des buts
    hgoal_count = len(df[(df['teamId']==hteamID) & (df['type']=='Goal') & 
                        (~df['qualifiers'].str.contains('OwnGoal', na=False))])
    agoal_count = len(df[(df['teamId']==ateamID) & (df['type']=='Goal') & 
                        (~df['qualifiers'].str.contains('OwnGoal', na=False))])

    pitch = Pitch(pitch_type='uefa', goal_type='box', goal_alpha=.5, corner_arcs=True, 
                 pitch_color=bg_color, linewidth=2, line_color=line_color)
    pitch.draw(ax=ax)

    # Tirs de l'équipe domicile
    hShotsdf = Shotsdf[Shotsdf['teamId']==hteamID]
    if not hShotsdf.empty:
        # Goals
        hGoalData = hShotsdf[hShotsdf['type'] == 'Goal']
        if not hGoalData.empty:
            sc1 = pitch.scatter((105-hGoalData.x), (68-hGoalData.y), s=350, edgecolors='green', 
                              linewidths=0.6, c='None', marker='football', zorder=3, ax=ax)
        
        # Autres tirs
        hMissData = hShotsdf[hShotsdf['type'] == 'MissedShots']
        if not hMissData.empty:
            sc4 = pitch.scatter((105-hMissData.x), (68-hMissData.y), s=200, edgecolors=col1, 
                              c='None', marker='o', ax=ax)

    # Tirs de l'équipe extérieure
    aShotsdf = Shotsdf[Shotsdf['teamId']==ateamID]
    if not aShotsdf.empty:
        # Goals
        aGoalData = aShotsdf[aShotsdf['type'] == 'Goal']
        if not aGoalData.empty:
            sc5 = pitch.scatter(aGoalData.x, aGoalData.y, s=350, edgecolors='green', 
                              linewidths=0.6, c='None', marker='football', zorder=3, ax=ax)
        
        # Autres tirs
        aMissData = aShotsdf[aShotsdf['type'] == 'MissedShots']
        if not aMissData.empty:
            sc8 = pitch.scatter(aMissData.x, aMissData.y, s=200, edgecolors=col2, 
                              c='None', marker='o', ax=ax)

    # Titre avec score
    highlight_text = [{'color':col1}, {'color':col2}]
    ax_text(52.5, 116, f"<{hteamName} {hgoal_count}> - <{agoal_count} {ateamName}>", 
           color=line_color, fontsize=52, fontweight='bold',
           highlight_textprops=highlight_text, ha='center', va='center', ax=ax)

def create_full_dashboard(df, players_df, events_dict, teams_dict, match_info=None):
    """Crée le dashboard complet avec toutes les visualisations"""
    try:
        # Import des fonctions avancées
        from dashboard_functions import create_complete_dashboard
        
        # Création du dashboard complet
        fig = create_complete_dashboard(df, players_df, events_dict, teams_dict, match_info)
        
        if fig is not None:
            # Ajout du titre principal si des informations de match sont fournies
            if match_info:
                hteamName = list(teams_dict.values())[0]
                ateamName = list(teams_dict.values())[1]
                # Calcul du score
                hteamID = list(teams_dict.keys())[0]
                ateamID = list(teams_dict.keys())[1]
                hgoal_count = len(df[(df['teamId']==hteamID) & (df['type']=='Goal') & 
                                   (~df['qualifiers'].str.contains('OwnGoal', na=False))])
                agoal_count = len(df[(df['teamId']==ateamID) & (df['type']=='Goal') & 
                                   (~df['qualifiers'].str.contains('OwnGoal', na=False))])
                
                fig.suptitle(f"{hteamName} {hgoal_count} - {agoal_count} {ateamName}\n" + 
                           f"{match_info.get('league', '')} | {match_info.get('gameweek', '')} | " + 
                           f"{match_info.get('date', '')}", 
                           fontsize=30, fontweight='bold', y=0.98)
            
            # Sauvegarder
            buf = BytesIO()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            buf.seek(0)
            plt.close()
            
            return buf
        else:
            return None
        
    except ImportError:
        st.error("⚠️ Module dashboard_functions non trouvé. Utilisation du dashboard basique.")
        return create_basic_dashboard(df, teams_dict, match_info)
    except Exception as e:
        st.error(f"Erreur lors de la création du dashboard complet: {e}")
        return create_basic_dashboard(df, teams_dict, match_info)

def create_player_dashboard(df, players_df, events_dict, teams_dict):
    """Crée le dashboard des joueurs"""
    try:
        # Import des fonctions avancées
        from player_dashboard_functions import create_complete_player_dashboard
        
        # Création du dashboard joueurs complet
        fig = create_complete_player_dashboard(df, players_df, events_dict, teams_dict)
        
        if fig is not None:
            # Sauvegarder
            buf = BytesIO()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            buf.seek(0)
            plt.close()
            
            return buf
        else:
            return None
        
    except ImportError:
        st.error("⚠️ Module player_dashboard_functions non trouvé. Utilisation du dashboard basique.")
        return create_basic_player_dashboard(df, players_df, teams_dict)
    except Exception as e:
        st.error(f"Erreur lors de la création du dashboard joueurs: {e}")
        return create_basic_player_dashboard(df, players_df, teams_dict)

def create_basic_player_dashboard(df, players_df, teams_dict):
    """Crée un dashboard joueurs basique"""
    try:
        # Création simple
        fig, axs = plt.subplots(3, 3, figsize=(35, 25), facecolor=bg_color)
        
        for i in range(3):
            for j in range(3):
                pitch = Pitch(pitch_type='uefa', goal_type='box', goal_alpha=.5, corner_arcs=True, 
                             pitch_color=bg_color, line_color=line_color, linewidth=2)
                pitch.draw(ax=axs[i,j])
                axs[i,j].text(52.5, 34, f"Player Stats {i+1}-{j+1}", ha='center', va='center', 
                            fontsize=16, color=line_color)
        
        plt.tight_layout()
        
        # Sauvegarder
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        buf.seek(0)
        plt.close()
        
        return buf
        
    except Exception as e:
        st.error(f"Erreur lors de la création du dashboard joueurs basique: {e}")
        return None

def main():
    st.title("⚽ Football Match Dashboard Generator")
    st.markdown("---")
    
    # Sidebar pour la configuration
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # Informations sur le match
        st.subheader("Informations du match")
        league = st.text_input("Championnat", placeholder="ex: Ligue 1")
        gameweek = st.text_input("Journée", placeholder="ex: Journée 15")
        match_date = st.date_input("Date du match")
        
        # Données xG (optionnel)
        st.subheader("📊 Données xG (optionnel)")
        col_xg1, col_xg2 = st.columns(2)
        with col_xg1:
            hxg = st.number_input("xG Domicile", min_value=0.0, value=0.0, step=0.1)
            hxgot = st.number_input("xGOT Domicile", min_value=0.0, value=0.0, step=0.1)
        with col_xg2:
            axg = st.number_input("xG Extérieur", min_value=0.0, value=0.0, step=0.1)
            axgot = st.number_input("xGOT Extérieur", min_value=0.0, value=0.0, step=0.1)
        
        st.markdown("---")
        st.subheader("📊 Type de dashboard")
        dashboard_type = st.selectbox(
            "Choisir le dashboard",
            ["Dashboard complet", "Dashboard joueurs", "Les deux"]
        )
        
        st.markdown("---")
        st.subheader("ℹ️ Instructions")
        st.markdown("""
        1. Allez sur **whoscored.com**
        2. Sélectionnez un match
        3. Sauvegardez la page en HTML
        4. Uploadez le fichier ici
        """)
    
    # Zone principale
    col1_main, col2_main = st.columns([2, 1])
    
    with col1_main:
        st.subheader("📁 Upload du fichier HTML")
        
        # Zone d'upload
        uploaded_file = st.file_uploader(
            "Sélectionnez le fichier HTML du match (WhoScored.com)",
            type=['html'],
            help="Le fichier doit provenir de whoscored.com et contenir les données du match"
        )
        
        if uploaded_file is not None:
            try:
                # Lecture du fichier
                html_content = uploaded_file.read().decode('utf-8')
                
                # Extraction des données
                with st.spinner("🔄 Extraction des données..."):
                    json_data_txt = extract_json_from_html(html_content)
                    
                    if json_data_txt:
                        data = json.loads(json_data_txt)
                        events_dict, players_df, teams_dict = extract_data_from_dict(data)
                        
                        if events_dict is not None:
                            # Traitement des données
                            df = pd.DataFrame(events_dict)
                            df = process_match_data(df, players_df, teams_dict)
                            
                            # Informations du match
                            hteamName = list(teams_dict.values())[0]
                            ateamName = list(teams_dict.values())[1]
                            
                            st.success(f"✅ Données extraites avec succès!")
                            
                            # Affichage des informations du match
                            with col2_main:
                                st.subheader("🏟️ Informations du match")
                                
                                st.markdown(f"""
                                <div class="metric-container">
                                    <h4>🏠 Équipe domicile</h4>
                                    <p style="font-size: 18px; color: {col1}; font-weight: bold;">{hteamName}</p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                st.markdown(f"""
                                <div class="metric-container">
                                    <h4>✈️ Équipe extérieure</h4>
                                    <p style="font-size: 18px; color: {col2}; font-weight: bold;">{ateamName}</p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                st.markdown(f"""
                                <div class="metric-container">
                                    <h4>📊 Événements analysés</h4>
                                    <p style="font-size: 18px; font-weight: bold;">{len(df):,}</p>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            # Génération des dashboards
                            st.markdown("---")
                            st.subheader("📊 Génération des dashboards")
                            
                            if st.button("🚀 Générer les dashboards", type="primary"):
                                match_info = {
                                    'league': league if league else 'Match de football',
                                    'gameweek': gameweek if gameweek else '',
                                    'date': match_date.strftime('%d %B %Y') if match_date else '',
                                    'hxg': hxg,
                                    'axg': axg,
                                    'hxgot': hxgot,
                                    'axgot': axgot
                                }
                                
                                if dashboard_type in ["Dashboard complet", "Les deux"]:
                                    with st.spinner("⚽ Génération du dashboard complet..."):
                                        main_dashboard = create_full_dashboard(df, players_df, events_dict, teams_dict, match_info)
                                        
                                        if main_dashboard:
                                            st.success("🎉 Dashboard complet généré!")
                                            
                                            # Affichage
                                            st.subheader("📈 Dashboard Principal")
                                            st.image(main_dashboard, use_column_width=True)
                                            
                                            # Téléchargement
                                            filename = f"{hteamName}_vs_{ateamName}_dashboard_complet.png"
                                            st.download_button(
                                                label="💾 Télécharger le dashboard complet",
                                                data=main_dashboard,
                                                file_name=filename,
                                                mime="image/png"
                                            )
                                
                                if dashboard_type in ["Dashboard joueurs", "Les deux"]:
                                    with st.spinner("👥 Génération du dashboard joueurs..."):
                                        player_dashboard = create_player_dashboard(df, players_df, events_dict, teams_dict)
                                        
                                        if player_dashboard:
                                            st.success("🎉 Dashboard joueurs généré!")
                                            
                                            # Affichage
                                            st.subheader("👥 Dashboard Joueurs")
                                            st.image(player_dashboard, use_column_width=True)
                                            
                                            # Téléchargement
                                            filename = f"{hteamName}_vs_{ateamName}_dashboard_joueurs.png"
                                            st.download_button(
                                                label="💾 Télécharger le dashboard joueurs",
                                                data=player_dashboard,
                                                file_name=filename,
                                                mime="image/png"
                                            )
                        else:
                            st.error("❌ Impossible d'extraire les données du match")
                    else:
                        st.error("❌ Format de fichier invalide ou données manquantes")
                        
            except Exception as e:
                st.error(f"❌ Erreur lors du traitement du fichier: {e}")
                st.info("💡 Assurez-vous que le fichier provient bien de whoscored.com et contient les données d'un match")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 14px;">
        Développé pour l'analyse de matchs de football • Données: WhoScored.com
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
