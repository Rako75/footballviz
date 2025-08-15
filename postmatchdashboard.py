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
    if pd.isna(full_name):
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
        xT_url = 'https://raw.githubusercontent.com/mckayjohns/youtube-videos/main/data/xT_Grid.csv'
        xT = pd.read_csv(xT_url, header=None)
        xT = np.array(xT)
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
            
            # Garder seulement la colonne xT
            dfxT_minimal = dfxT[['xT']].copy()
            df = df.merge(dfxT_minimal, left_index=True, right_index=True, how='left')
    except:
        df['xT'] = 0
    
    # Ajout des noms d'équipes
    df['teamName'] = df['teamId'].map(teams_dict)
    
    # Redimensionnement des coordonnées
    df['x'] = df['x'] * 1.05
    df['y'] = df['y'] * 0.68
    df['endX'] = df['endX'] * 1.05
    df['endY'] = df['endY'] * 0.68
    
    # Nettoyage du DataFrame des joueurs
    columns_to_drop = ['height', 'weight', 'age', 'isManOfTheMatch', 'field', 'stats', 
                      'subbedInPlayerId', 'subbedOutPeriod', 'subbedOutExpandedMinute',
                      'subbedInPeriod', 'subbedInExpandedMinute', 'subbedOutPlayerId']
    players_df = players_df.drop(columns=[col for col in columns_to_drop if col in players_df.columns])
    
    # Fusion avec les données des joueurs
    df = df.merge(players_df, on='playerId', how='left').query("period != 'PenaltyShootout'")
    
    # Calcul des passes progressives
    df['pro'] = np.where((df['type'] == 'Pass') & (df['outcomeType'] == 'Successful') & (df['x'] > 42),
                        np.sqrt((105 - df['x'])**2 + (34 - df['y'])**2) - 
                        np.sqrt((105 - df['endX'])**2 + (34 - df['endY'])**2), 0)
    
    # Ajout des noms courts
    df['shortName'] = df['name'].apply(get_short_name)
    
    return df

def create_basic_dashboard(df, teams_dict, match_info=None):
    """Crée un dashboard basique avec les statistiques principales"""
    try:
        hteamID = list(teams_dict.keys())[0]
        ateamID = list(teams_dict.keys())[1]
        hteamName = teams_dict[hteamID]
        ateamName = teams_dict[ateamID]
        
        homedf = df[df['teamId'] == hteamID]
        awaydf = df[df['teamId'] == ateamID]
        
        # Calcul des statistiques de base
        hgoal_count = len(homedf[(homedf['type'] == 'Goal') & 
                                (~homedf['qualifiers'].str.contains('OwnGoal', na=False))])
        agoal_count = len(awaydf[(awaydf['type'] == 'Goal') & 
                                (~awaydf['qualifiers'].str.contains('OwnGoal', na=False))])
        
        # Possession
        hposs_passes = len(homedf[homedf['type'] == 'Pass'])
        aposs_passes = len(awaydf[awaydf['type'] == 'Pass'])
        total_passes = hposs_passes + aposs_passes
        
        if total_passes > 0:
            hposs = round((hposs_passes / total_passes) * 100, 1)
            aposs = round((aposs_passes / total_passes) * 100, 1)
        else:
            hposs = aposs = 50.0
        
        # Tirs
        hshots = len(homedf[homedf['type'].isin(['Goal', 'MissedShots', 'SavedShot', 'ShotOnPost'])])
        ashots = len(awaydf[awaydf['type'].isin(['Goal', 'MissedShots', 'SavedShot', 'ShotOnPost'])])
        
        # Création d'un graphique simple
        fig, ax = plt.subplots(1, 1, figsize=(12, 8), facecolor='white')
        
        # Configuration de base
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')
        
        # Titre principal
        if match_info:
            title = f"{hteamName} {hgoal_count} - {agoal_count} {ateamName}"
            subtitle = f"{match_info.get('league', 'Match')} | {match_info.get('date', '')}"
        else:
            title = f"{hteamName} {hgoal_count} - {agoal_count} {ateamName}"
            subtitle = "Football Match Dashboard"
        
        ax.text(5, 9, title, fontsize=24, fontweight='bold', ha='center', va='center')
        ax.text(5, 8.5, subtitle, fontsize=16, ha='center', va='center', color='gray')
        
        # Statistiques
        stats_y = 7
        stats = [
            ("Possession", f"{hposs}%", f"{aposs}%"),
            ("Tirs", str(hshots), str(ashots)),
            ("Buts", str(hgoal_count), str(agoal_count)),
        ]
        
        for i, (stat, home_val, away_val) in enumerate(stats):
            y_pos = stats_y - i * 0.8
            ax.text(2.5, y_pos, home_val, fontsize=16, ha='center', va='center', 
                   color=col1, fontweight='bold')
            ax.text(5, y_pos, stat, fontsize=14, ha='center', va='center')
            ax.text(7.5, y_pos, away_val, fontsize=16, ha='center', va='center', 
                   color=col2, fontweight='bold')
        
        # Équipes
        ax.text(2.5, 4, hteamName, fontsize=18, ha='center', va='center', 
               color=col1, fontweight='bold')
        ax.text(7.5, 4, ateamName, fontsize=18, ha='center', va='center', 
               color=col2, fontweight='bold')
        
        plt.tight_layout()
        
        # Sauvegarder dans un buffer
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        buf.seek(0)
        plt.close()
        
        return buf
        
    except Exception as e:
        st.error(f"Erreur lors de la création du dashboard: {e}")
        return None

def main():
    st.title("⚽ Football Match Dashboard Generator")
    st.markdown("---")
    
    # Sidebar pour la configuration
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # Informations sur le match (optionnel)
        st.subheader("Informations du match")
        league = st.text_input("Championnat", placeholder="ex: Ligue 1")
        gameweek = st.text_input("Journée", placeholder="ex: Journée 15")
        match_date = st.date_input("Date du match")
        
        st.markdown("---")
        st.subheader("📊 Options du dashboard")
        dashboard_type = st.selectbox(
            "Type de dashboard",
            ["Dashboard complet", "Dashboard basique", "Les deux"]
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
                                    'date': match_date.strftime('%d %B %Y') if match_date else ''
                                }
                                
                                with st.spinner("⚽ Génération en cours..."):
                                    # Dashboard basique
                                    basic_dashboard = create_basic_dashboard(df, teams_dict, match_info)
                                    
                                    if basic_dashboard:
                                        st.success("🎉 Dashboard généré avec succès!")
                                        
                                        # Affichage du dashboard
                                        st.subheader("📈 Dashboard du match")
                                        st.image(basic_dashboard, use_column_width=True)
                                        
                                        # Bouton de téléchargement
                                        filename = f"{hteamName}_vs_{ateamName}_dashboard.png"
                                        st.download_button(
                                            label="💾 Télécharger le dashboard",
                                            data=basic_dashboard,
                                            file_name=filename,
                                            mime="image/png"
                                        )
                                        
                                        # Note pour le dashboard complet
                                        if dashboard_type in ["Dashboard complet", "Les deux"]:
                                            st.info("""
                                            ℹ️ **Note**: Le dashboard complet nécessite des bibliothèques additionnelles 
                                            et plus de temps de traitement. Cette version simplifiée vous donne 
                                            un aperçu des statistiques principales du match.
                                            """)
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
