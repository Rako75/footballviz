import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import os
from pathlib import Path
import base64

# Configuration de la page
st.set_page_config(
    page_title="Neymar Jr - Buts LaLiga",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #FF6B6B;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.5rem;
        text-align: center;
        color: #4ECDC4;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #FF6B6B;
    }
    .video-container {
        border: 2px solid #4ECDC4;
        border-radius: 10px;
        padding: 1rem;
        background-color: #f8f9fa;
    }
    .goal-info {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .video-debug-info {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Charge et traite les données des buts de Neymar"""
    try:
        # Essayer différents encodages et séparateurs
        for encoding in ['cp1252', 'utf-8', 'iso-8859-1', 'latin1']:
            for sep in [';', ',', '\t']:
                try:
                    df = pd.read_csv('Neymar_Buts_LaLiga.csv', sep=sep, encoding=encoding)
                    if len(df.columns) > 5:  # Vérifier que le fichier est correctement parsé
                        st.success(f"✅ Données chargées avec encoding={encoding} et sep='{sep}'")
                        break
                except:
                    continue
            else:
                continue
            break
        else:
            st.error("❌ Impossible de charger le fichier CSV avec les encodages testés")
            return None
        
        # Vérification et traitement des colonnes essentielles
        required_columns = ['X', 'Y', 'xG', 'minute']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.error(f"❌ Colonnes manquantes: {missing_columns}")
            st.info(f"📋 Colonnes disponibles: {list(df.columns)}")
            return None
        
        # Normalisation des coordonnées si nécessaire
        df_goals = df.copy()
        
        # Conversion sécurisée des coordonnées
        df_goals['X'] = pd.to_numeric(df_goals['X'], errors='coerce')
        df_goals['Y'] = pd.to_numeric(df_goals['Y'], errors='coerce')
        df_goals['xG'] = pd.to_numeric(df_goals['xG'], errors='coerce')
        
        # Normalisation des coordonnées (si elles sont en format 0-1, les convertir)
        if df_goals['X'].max() <= 1:
            df_goals['X'] = df_goals['X'] * 120
        if df_goals['Y'].max() <= 1:
            df_goals['Y'] = df_goals['Y'] * 80
        
        # Ajout d'informations supplémentaires
        df_goals['distance_but'] = np.sqrt((120 - df_goals['X'])**2 + (40 - df_goals['Y'])**2) * 0.9144
        df_goals['zone'] = df_goals['X'].apply(lambda x: 
            'Surface' if x > 103.5 else 
            'Zone dangereuse' if x > 90 else 
            'Milieu offensif' if x > 60 else 'Autres')
        
        # Créer un ID si manquant
        if 'id' not in df_goals.columns:
            df_goals['id'] = range(1, len(df_goals) + 1)
        
        return df_goals
        
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement des données : {e}")
        return None

def scan_video_folder(video_folder="Neymar_LaLiga_Buts"):
    """Scanne le dossier vidéo et retourne la liste des fichiers disponibles"""
    video_files = []
    
    if os.path.exists(video_folder):
        for file in os.listdir(video_folder):
            if file.lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.webm')):
                video_files.append(file)
        st.info(f"📁 {len(video_files)} fichiers vidéo trouvés dans le dossier '{video_folder}'")
        
        # Debug: afficher quelques noms de fichiers
        if video_files:
            st.expander("🔍 Aperçu des fichiers vidéo").write(video_files[:10])
    else:
        st.warning(f"📁 Dossier '{video_folder}' introuvable")
    
    return video_files

def find_video_file(goal_data, video_folder="Neymar_LaLiga_Buts", available_videos=None):
    """Recherche le fichier vidéo correspondant au but avec amélioration du matching"""
    
    if not os.path.exists(video_folder):
        return None
    
    if available_videos is None:
        available_videos = scan_video_folder(video_folder)
    
    # Stratégie 1: Utiliser la colonne 'video_but' si disponible
    if 'video_but' in goal_data and pd.notna(goal_data['video_but']) and str(goal_data['video_but']).strip():
        video_filename = str(goal_data['video_but']).strip()
        
        # Correspondance exacte
        if video_filename in available_videos:
            return os.path.join(video_folder, video_filename)
        
        # Correspondance sans extension
        base_name = os.path.splitext(video_filename)[0]
        for video in available_videos:
            if os.path.splitext(video)[0] == base_name:
                return os.path.join(video_folder, video)
    
    # Stratégie 2: Utiliser l'ID du but
    goal_id = goal_data.get('id', '')
    if goal_id:
        # Patterns de recherche plus flexibles
        patterns = [
            str(goal_id),
            f"but_{goal_id}",
            f"goal_{goal_id}",
            f"neymar_{goal_id}",
            f"but{goal_id}",
            f"goal{goal_id}",
            f"neymar{goal_id}"
        ]
        
        for pattern in patterns:
            for video in available_videos:
                video_base = os.path.splitext(video)[0].lower()
                if pattern.lower() in video_base or video_base in pattern.lower():
                    return os.path.join(video_folder, video)
    
    # Stratégie 3: Recherche par index (si l'ID correspond à l'index dans la liste)
    if isinstance(goal_id, int) and 1 <= goal_id <= len(available_videos):
        return os.path.join(video_folder, available_videos[goal_id - 1])
    
    return None

def create_pitch_figure(df_goals, selected_goal_id=None, available_videos=None):
    """Crée le terrain de football avec les buts de Neymar"""
    fig = go.Figure()
    
    # Dimensions du terrain
    pitch_length, pitch_width = 120, 80
    
    # Dessin du terrain (code identique)
    # Contour principal
    fig.add_shape(type="rect", x0=0, y0=0, x1=pitch_length, y1=pitch_width,
                  line=dict(color="white", width=3), fillcolor="green", opacity=0.3)
    
    # Ligne médiane
    fig.add_shape(type="line", x0=pitch_length/2, y0=0, x1=pitch_length/2, y1=pitch_width,
                  line=dict(color="white", width=2))
    
    # Cercle central
    fig.add_shape(type="circle", x0=pitch_length/2-9.15, y0=pitch_width/2-9.15,
                  x1=pitch_length/2+9.15, y1=pitch_width/2+9.15,
                  line=dict(color="white", width=2), fillcolor="rgba(0,0,0,0)")
    
    # Surfaces de réparation
    penalty_box_length = 16.5
    penalty_box_width = 40.32
    penalty_box_y_start = (pitch_width - penalty_box_width) / 2
    
    fig.add_shape(type="rect", 
                  x0=pitch_length-penalty_box_length, y0=penalty_box_y_start,
                  x1=pitch_length, y1=penalty_box_y_start + penalty_box_width,
                  line=dict(color="white", width=2), fillcolor="rgba(255,0,0,0.1)")
    
    # Surface gauche (défense)
    fig.add_shape(type="rect", 
                  x0=0, y0=penalty_box_y_start,
                  x1=penalty_box_length, y1=penalty_box_y_start + penalty_box_width,
                  line=dict(color="white", width=2), fillcolor="rgba(0,0,0,0)")
    
    # Surfaces de but
    goal_box_length = 5.5
    goal_box_width = 18.32
    goal_box_y_start = (pitch_width - goal_box_width) / 2
    
    # Surface de but droite
    fig.add_shape(type="rect", 
                  x0=pitch_length-goal_box_length, y0=goal_box_y_start,
                  x1=pitch_length, y1=goal_box_y_start + goal_box_width,
                  line=dict(color="white", width=2), fillcolor="rgba(0,0,0,0)")
    
    # Surface de but gauche
    fig.add_shape(type="rect", 
                  x0=0, y0=goal_box_y_start,
                  x1=goal_box_length, y1=goal_box_y_start + goal_box_width,
                  line=dict(color="white", width=2), fillcolor="rgba(0,0,0,0)")
    
    # Buts
    goal_width = 7.32
    goal_y_start = (pitch_width - goal_width) / 2
    
    # But droit
    fig.add_shape(type="line", x0=pitch_length, y0=goal_y_start,
                  x1=pitch_length, y1=goal_y_start + goal_width,
                  line=dict(color="white", width=4))
    
    # But gauche
    fig.add_shape(type="line", x0=0, y0=goal_y_start,
                  x1=0, y1=goal_y_start + goal_width,
                  line=dict(color="white", width=4))
    
    # Points de penalty
    fig.add_trace(go.Scatter(x=[pitch_length-11, 11], y=[pitch_width/2, pitch_width/2],
                            mode='markers', marker=dict(color='white', size=8),
                            showlegend=False, hoverinfo='skip'))
    
    # Vérifier quels buts ont des vidéos disponibles
    df_goals_with_videos = df_goals.copy()
    df_goals_with_videos['has_video'] = df_goals_with_videos.apply(
        lambda row: find_video_file(row, available_videos=available_videos) is not None, axis=1
    )
    
    # Séparer les buts avec et sans vidéos
    goals_with_video = df_goals_with_videos[df_goals_with_videos['has_video']]
    goals_without_video = df_goals_with_videos[~df_goals_with_videos['has_video']]
    
    # Affichage des buts SANS vidéo (gris)
    if not goals_without_video.empty:
        colors_no_video = []
        sizes_no_video = []
        texts_no_video = []
        
        for _, goal in goals_without_video.iterrows():
            goal_id = goal['id']
            if selected_goal_id and goal_id == selected_goal_id:
                colors_no_video.append('gold')
                sizes_no_video.append(max(15, 30 * goal['xG']) * 1.5)
            else:
                colors_no_video.append('lightgray')
                sizes_no_video.append(max(10, 20 * goal['xG']))
            
            texts_no_video.append(f"But #{goal_id} ❌ SANS VIDÉO<br>Minute: {goal['minute']}<br>xG: {goal['xG']:.3f}")
        
        fig.add_trace(go.Scatter(
            x=goals_without_video['X'],
            y=goals_without_video['Y'],
            mode='markers',
            marker=dict(
                color=colors_no_video,
                size=sizes_no_video,
                line=dict(color='darkgray', width=1),
                opacity=0.6
            ),
            text=texts_no_video,
            hovertemplate='%{text}<extra></extra>',
            customdata=goals_without_video['id'],
            name='Buts sans vidéo',
            legendgroup='no_video'
        ))
    
    # Affichage des buts AVEC vidéo (vert)
    if not goals_with_video.empty:
        colors_with_video = []
        sizes_with_video = []
        texts_with_video = []
        
        for _, goal in goals_with_video.iterrows():
            goal_id = goal['id']
            if selected_goal_id and goal_id == selected_goal_id:
                colors_with_video.append('gold')
                sizes_with_video.append(max(15, 30 * goal['xG']) * 1.5)
            else:
                colors_with_video.append('limegreen')
                sizes_with_video.append(max(10, 20 * goal['xG']))
            
            texts_with_video.append(f"But #{goal_id} 🎥 AVEC VIDÉO<br>Minute: {goal['minute']}<br>xG: {goal['xG']:.3f}")
        
        fig.add_trace(go.Scatter(
            x=goals_with_video['X'],
            y=goals_with_video['Y'],
            mode='markers',
            marker=dict(
                color=colors_with_video,
                size=sizes_with_video,
                line=dict(color='darkgreen', width=2),
                opacity=0.9
            ),
            text=texts_with_video,
            hovertemplate='%{text}<extra></extra>',
            customdata=goals_with_video['id'],
            name='Buts avec vidéo',
            legendgroup='with_video'
        ))
    
    # Configuration du graphique
    fig.update_layout(
        title=dict(
            text="<b>Neymar Jr - Tous ses buts en LaLiga (2013-2017)</b>",
            x=0.5,
            font=dict(size=24, color="darkblue")
        ),
        xaxis=dict(
            range=[-5, 125],
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            title=""
        ),
        yaxis=dict(
            range=[-5, 85],
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            title="",
            scaleanchor="x",
            scaleratio=1
        ),
        plot_bgcolor='darkgreen',
        paper_bgcolor='white',
        height=600,
        showlegend=True
    )
    
    return fig

def display_video(video_path):
    """Affiche une vidéo avec gestion d'erreur améliorée"""
    try:
        # Vérifier que le fichier existe et est lisible
        if not os.path.exists(video_path):
            st.error(f"❌ Fichier vidéo introuvable : {video_path}")
            return False
            
        file_size = os.path.getsize(video_path)
        if file_size == 0:
            st.error(f"❌ Fichier vidéo vide : {video_path}")
            return False
            
        st.info(f"📁 Fichier: {os.path.basename(video_path)} ({file_size / (1024*1024):.1f} MB)")
        
        # Méthode 1: st.video avec lecture directe
        try:
            with open(video_path, 'rb') as video_file:
                video_bytes = video_file.read()
            
            if len(video_bytes) > 0:
                st.video(video_bytes)
                st.success("✅ Vidéo chargée avec succès!")
                return True
            else:
                st.error("❌ Impossible de lire le contenu du fichier vidéo")
                
        except Exception as e:
            st.error(f"❌ Erreur lors de la lecture : {e}")
            
            # Méthode 2: Essayer avec le chemin direct
            try:
                st.video(video_path)
                st.success("✅ Vidéo chargée avec le chemin direct!")
                return True
            except Exception as e2:
                st.error(f"❌ Erreur avec chemin direct : {e2}")
                
                # Méthode 3: Conversion base64 (pour certains formats)
                try:
                    with open(video_path, "rb") as f:
                        video_b64 = base64.b64encode(f.read()).decode()
                    
                    video_html = f"""
                    <video width="100%" height="400" controls>
                        <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
                        Your browser does not support the video tag.
                    </video>
                    """
                    st.markdown(video_html, unsafe_allow_html=True)
                    st.info("✅ Vidéo affichée en HTML!")
                    return True
                    
                except Exception as e3:
                    st.error(f"❌ Toutes les méthodes ont échoué. Dernière erreur : {e3}")
        
        return False
        
    except Exception as e:
        st.error(f"❌ Erreur générale lors de l'affichage de la vidéo : {e}")
        return False

def main():
    # Titre principal
    st.markdown('<h1 class="main-header">⚽ Neymar Jr</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="sub-header">Tous ses buts en LaLiga (2013-2017)</h2>', unsafe_allow_html=True)
    
    # Section de diagnostic
    with st.expander("🔧 Diagnostic système", expanded=False):
        st.write("**Répertoire de travail actuel:**", os.getcwd())
        st.write("**Fichiers dans le répertoire:**", os.listdir('.'))
        
        # Vérifier la présence du CSV
        csv_exists = os.path.exists('Neymar_Buts_LaLiga.csv')
        st.write(f"**Fichier CSV présent:** {'✅' if csv_exists else '❌'} Neymar_Buts_LaLiga.csv")
        
        # Vérifier la présence du dossier vidéo
        video_folder_exists = os.path.exists('Neymar_LaLiga_Buts')
        st.write(f"**Dossier vidéo présent:** {'✅' if video_folder_exists else '❌'} Neymar_LaLiga_Buts")
        
        if video_folder_exists:
            video_files = [f for f in os.listdir('Neymar_LaLiga_Buts') 
                          if f.lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.webm'))]
            st.write(f"**Nombre de vidéos détectées:** {len(video_files)}")
        else:
            st.warning("Créez le dossier 'Neymar_LaLiga_Buts' et ajoutez vos vidéos")
    
    # Chargement des données
    df_goals = load_data()
    
    if df_goals is None:
        st.stop()
    
    # Scanner les vidéos disponibles
    available_videos = scan_video_folder()
    
    # Sidebar avec filtres
    st.sidebar.header("🎯 Filtres et Options")
    
    # Filtre par saison (si la colonne existe)
    if 'season' in df_goals.columns:
        seasons = sorted(df_goals['season'].unique())
        selected_seasons = st.sidebar.multiselect(
            "Sélectionner les saisons",
            seasons,
            default=seasons
        )
        df_goals = df_goals[df_goals['season'].isin(selected_seasons)]
    
    # Filtre par type de tir (si la colonne existe)
    if 'shotType' in df_goals.columns:
        shot_types = df_goals['shotType'].unique()
        selected_shot_types = st.sidebar.multiselect(
            "Type de tir",
            shot_types,
            default=shot_types
        )
        df_goals = df_goals[df_goals['shotType'].isin(selected_shot_types)]
    
    # Filtre par disponibilité vidéo
    video_filter = st.sidebar.selectbox(
        "🎥 Disponibilité vidéo",
        ["Tous les buts", "Avec vidéo uniquement", "Sans vidéo uniquement"]
    )
    
    # Filtre par xG
    min_xg = st.sidebar.slider(
        "xG minimum",
        min_value=0.0,
        max_value=float(df_goals['xG'].max()),
        value=0.0,
        step=0.1
    )
    
    # Application des filtres
    filtered_df = df_goals[df_goals['xG'] >= min_xg].copy()
    
    # Appliquer le filtre vidéo
    if video_filter != "Tous les buts":
        filtered_df['has_video'] = filtered_df.apply(
            lambda row: find_video_file(row, available_videos=available_videos) is not None, axis=1
        )
        
        if video_filter == "Avec vidéo uniquement":
            filtered_df = filtered_df[filtered_df['has_video']]
        elif video_filter == "Sans vidéo uniquement":
            filtered_df = filtered_df[~filtered_df['has_video']]
    
    if filtered_df.empty:
        st.warning("❌ Aucun but ne correspond aux critères sélectionnés.")
        return
    
    # Statistiques des vidéos
    filtered_df['has_video'] = filtered_df.apply(
        lambda row: find_video_file(row, available_videos=available_videos) is not None, axis=1
    )
    
    goals_with_videos = filtered_df[filtered_df['has_video']]
    goals_without_videos = filtered_df[~filtered_df['has_video']]
    
    # Métriques principales
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Nombre de buts", len(filtered_df))
    
    with col2:
        st.metric("🎥 Avec vidéo", len(goals_with_videos), 
                 delta=f"{len(goals_with_videos)/len(filtered_df)*100:.1f}%")
    
    with col3:
        st.metric("❌ Sans vidéo", len(goals_without_videos))
    
    with col4:
        st.metric("xG Total", f"{filtered_df['xG'].sum():.2f}")
    
    with col5:
        st.metric("Distance moyenne", f"{filtered_df['distance_but'].mean():.1f}m")
    
    st.divider()
    
    # Interface principale
    col_main, col_info = st.columns([3, 1])
    
    with col_main:
        st.subheader("🏟️ Terrain - Cliquez sur un but pour voir la vidéo")
        
        # Légende des couleurs
        st.markdown("""
        <div style='display: flex; justify-content: center; gap: 20px; margin-bottom: 10px; font-size: 0.9rem;'>
            <span style='color: limegreen;'>🟢 <strong>Buts avec vidéo</strong></span>
            <span style='color: lightgray;'>⚪ <strong>Buts sans vidéo</strong></span>
            <span style='color: gold;'>🟡 <strong>But sélectionné</strong></span>
        </div>
        """, unsafe_allow_html=True)
        
        # Initialiser la session state
        if 'selected_goal' not in st.session_state:
            st.session_state.selected_goal = None
        
        # Créer le graphique
        fig = create_pitch_figure(filtered_df, st.session_state.selected_goal, available_videos)
        
        # Sélecteur de but alternatif
        goal_options = [f"But #{row['id']} - Minute {row['minute']} ({'🎥' if row['has_video'] else '❌'})" 
                       for _, row in filtered_df.iterrows()]
        
        selected_option = st.selectbox(
            "Ou sélectionnez un but directement:",
            ["Aucune sélection"] + goal_options,
            index=0
        )
        
        if selected_option != "Aucune sélection":
            goal_id = int(selected_option.split('#')[1].split(' ')[0])
            st.session_state.selected_goal = goal_id
        
        # Afficher le graphique
        selected_points = st.plotly_chart(fig, use_container_width=True, on_select="rerun")
        
        # Gérer les clics (code simplifié)
        if selected_points and 'selection' in selected_points:
            selection = selected_points['selection']
            if 'points' in selection and len(selection['points']) > 0:
                point_index = selection['points'][0]['point_index']
                curve_number = selection['points'][0]['curve_number']
                
                if curve_number == 1 and point_index < len(goals_without_videos):
                    selected_goal_id = goals_without_videos.iloc[point_index]['id']
                    st.session_state.selected_goal = selected_goal_id
                    st.rerun()
                elif curve_number == 2 and point_index < len(goals_with_videos):
                    selected_goal_id = goals_with_videos.iloc[point_index]['id']
                    st.session_state.selected_goal = selected_goal_id
                    st.rerun()
    
    with col_info:
        st.subheader("📊 Statistiques par Zone")
        
        zone_stats = filtered_df.groupby('zone').agg({
            'id': 'count',
            'xG': 'mean'
        }).round(3)
        zone_stats.columns = ['Nombre', 'xG moyen']
        st.dataframe(zone_stats)
        
        # Graphique des zones
        if len(zone_stats) > 0:
            fig_pie = px.pie(
                values=zone_stats['Nombre'],
                names=zone_stats.index,
                title="Répartition par zone"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
    
    # Section vidéo améliorée
    if st.session_state.selected_goal:
        selected_goal_data = filtered_df[filtered_df['id'] == st.session_state.selected_goal].iloc[0]
        
        st.divider()
        st.subheader(f"🎥 But #{st.session_state.selected_goal}")
        
        col_video, col_details = st.columns([2, 1])
        
        with col_video:
            # Rechercher le fichier vidéo
            video_file = find_video_file(selected_goal_data, available_videos=available_videos)
            
            if video_file:
                st.markdown('<div class="video-container">', unsafe_allow_html=True)
                
                # Informations debug
                st.markdown('<div class="video-debug-info">', unsafe_allow_html=True)
                st.write(f"🎥 **Fichier trouvé:** {os.path.basename(video_file)}")
                st.write(f"📁 **Chemin complet:** {video_file}")
                st.write(f"📊 **Taille:** {os.path.getsize(video_file) / (1024*1024):.1f} MB")
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Afficher la vidéo
                success = display_video(video_file)
                
                if not success:
                    st.error("❌ Impossible d'afficher la vidéo")
                    st.info("💡 Vérifiez que le fichier n'est pas corrompu et qu'il s'agit d'un format vidéo supporté (.mp4, .mov, .webm)")
                
                st.markdown('</div>', unsafe_allow_html=True)
                
            else:
                st.warning(f"❌ Vidéo non trouvée pour le but #{st.session_state.selected_goal}")
                
                # Informations de debug pour aider au diagnostic
                st.markdown('<div class="video-debug-info">', unsafe_allow_html=True)
                if 'video_but' in selected_goal_data and pd.notna(selected_goal_data['video_but']):
                    st.write(f"🔍 **Nom attendu (colonne video_but):** {selected_goal_data['video_but']}")
                else:
                    st.write("🔍 **Colonne video_but:** vide ou inexistante")
                
                st.write(f"🆔 **ID du but:** {selected_goal_data['id']}")
                st.write(f"📁 **Dossier recherché:** Neymar_LaLiga_Buts/")
                
                # Suggestions de noms de fichiers
                suggested_names = [
                    f"{selected_goal_data['id']}.mp4",
                    f"but_{selected_goal_data['id']}.mp4",
                    f"goal_{selected_goal_data['id']}.mp4",
                    f"neymar_{selected_goal_data['id']}.mp4"
                ]
                st.write("💡 **Noms suggérés:**")
                for name in suggested_names:
                    st.write(f"   - {name}")
                
                if available_videos:
                    st.write("📋 **Vidéos disponibles dans le dossier:**")
                    for video in available_videos[:5]:  # Afficher les 5 premiers
                        st.write(f"   - {video}")
                    if len(available_videos) > 5:
                        st.write(f"   ... et {len(available_videos) - 5} autres")
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        with col_details:
            st.markdown('<div class="goal-info">', unsafe_allow_html=True)
            st.write(f"**Minute :** {selected_goal_data['minute']}'")
            st.write(f"**xG :** {selected_goal_data['xG']:.3f}")
            st.write(f"**Distance :** {selected_goal_data['distance_but']:.1f}m")
            st.write(f"**Zone :** {selected_goal_data['zone']}")
            
            # Informations supplémentaires si disponibles
            if 'shotType' in selected_goal_data and pd.notna(selected_goal_data['shotType']):
                st.write(f"**Type de tir :** {selected_goal_data['shotType']}")
            
            if 'season' in selected_goal_data and pd.notna(selected_goal_data['season']):
                st.write(f"**Saison :** {selected_goal_data['season']}")
            
            if 'h_team' in selected_goal_data and 'a_team' in selected_goal_data:
                st.write(f"**Match :** {selected_goal_data['h_team']} vs {selected_goal_data['a_team']}")
            
            if 'h_goals' in selected_goal_data and 'a_goals' in selected_goal_data:
                st.write(f"**Score :** {selected_goal_data['h_goals']}-{selected_goal_data['a_goals']}")
            
            if 'player_assisted' in selected_goal_data and pd.notna(selected_goal_data['player_assisted']):
                st.write(f"**Passeur :** {selected_goal_data['player_assisted']}")
            
            if 'video_but' in selected_goal_data and pd.notna(selected_goal_data['video_but']):
                st.write(f"**Fichier vidéo attendu :** {selected_goal_data['video_but']}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Boutons d'action
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        
        with col_btn1:
            if st.button("🔄 Retour à la vue générale"):
                st.session_state.selected_goal = None
                st.rerun()
        
        with col_btn2:
            # Navigation vers le but précédent
            current_index = filtered_df[filtered_df['id'] == st.session_state.selected_goal].index[0]
            if current_index > filtered_df.index[0]:
                prev_goal_id = filtered_df.loc[filtered_df.index[filtered_df.index < current_index].max(), 'id']
                if st.button("⬅️ But précédent"):
                    st.session_state.selected_goal = prev_goal_id
                    st.rerun()
        
        with col_btn3:
            # Navigation vers le but suivant
            current_index = filtered_df[filtered_df['id'] == st.session_state.selected_goal].index[0]
            if current_index < filtered_df.index[-1]:
                next_goal_id = filtered_df.loc[filtered_df.index[filtered_df.index > current_index].min(), 'id']
                if st.button("➡️ But suivant"):
                    st.session_state.selected_goal = next_goal_id
                    st.rerun()
    
    # Tableau détaillé
    st.divider()
    st.subheader("📋 Liste détaillée des buts")
    
    # Préparer les données pour affichage
    display_columns = ['id', 'minute', 'xG', 'zone', 'distance_but']
    
    # Ajouter les colonnes optionnelles si elles existent
    optional_columns = ['season', 'shotType', 'h_team', 'a_team', 'h_goals', 'a_goals', 'video_but']
    for col in optional_columns:
        if col in filtered_df.columns:
            display_columns.append(col)
    
    display_df = filtered_df[display_columns].copy()
    
    # Renommer les colonnes pour l'affichage
    column_names = {
        'id': 'ID',
        'minute': 'Minute',
        'xG': 'xG',
        'zone': 'Zone',
        'distance_but': 'Distance (m)',
        'season': 'Saison',
        'shotType': 'Type tir',
        'h_team': 'Équipe dom.',
        'a_team': 'Équipe ext.',
        'h_goals': 'Buts dom.',
        'a_goals': 'Buts ext.',
        'video_but': 'Fichier vidéo'
    }
    
    display_df = display_df.rename(columns=column_names)
    
    # Arrondir les valeurs numériques
    if 'xG' in display_df.columns:
        display_df['xG'] = display_df['xG'].round(3)
    if 'Distance (m)' in display_df.columns:
        display_df['Distance (m)'] = display_df['Distance (m)'].round(1)
    
    # Ajouter l'indicateur de vidéo
    display_df['🎥'] = filtered_df['has_video'].apply(lambda x: '✅' if x else '❌')
    
    # Réorganiser les colonnes avec l'indicateur vidéo au début
    cols = ['🎥'] + [col for col in display_df.columns if col != '🎥']
    display_df = display_df[cols]
    
    # Afficher le tableau avec possibilité de sélection
    event = st.dataframe(
        display_df,
        use_container_width=True,
        on_select="rerun",
        selection_mode="single-row"
    )
    
    # Gérer la sélection dans le tableau
    if event.selection and 'rows' in event.selection and len(event.selection['rows']) > 0:
        selected_row_index = event.selection['rows'][0]
        selected_goal_id = filtered_df.iloc[selected_row_index]['id']
        st.session_state.selected_goal = selected_goal_id
        st.rerun()
    
    # Section d'aide et conseils
    st.divider()
    
    with st.expander("💡 Conseils pour résoudre les problèmes d'affichage vidéo"):
        st.markdown("""
        ### Problèmes courants et solutions :
        
        **1. Vidéos non trouvées :**
        - Vérifiez que le dossier `Neymar_LaLiga_Buts` existe dans le même répertoire que ce script
        - Vérifiez que les noms de fichiers correspondent aux ID des buts
        - Formats de noms supportés : `1.mp4`, `but_1.mp4`, `goal_1.mp4`, `neymar_1.mp4`
        
        **2. Vidéos ne s'affichent pas :**
        - Vérifiez que les fichiers sont dans un format supporté (.mp4, .mov, .webm)
        - Vérifiez que les fichiers ne sont pas corrompus
        - Réduisez la taille des fichiers si ils sont trop volumineux (>200MB)
        
        **3. Performance :**
        - Utilisez de préférence le format MP4 H.264 pour une meilleure compatibilité
        - Compressez les vidéos si nécessaire
        
        **4. Structure recommandée :**
        ```
        votre_projet/
        ├── app.py (ce script)
        ├── Neymar_Buts_LaLiga.csv
        └── Neymar_LaLiga_Buts/
            ├── 1.mp4
            ├── 2.mp4
            ├── 3.mp4
            └── ...
        ```
        """)
    
    # Footer avec informations
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: gray; font-size: 0.9rem;'>
        <p>📊 Analyse interactive des buts de Neymar Jr en LaLiga (2013-2017)</p>
        <p>Données xG et coordonnées Opta • Vidéos incluses • Version améliorée avec diagnostic</p>
        <p>🎥 {video_count} vidéos détectées • 🎯 {goal_count} buts au total</p>
    </div>
    """.format(
        video_count=len(available_videos),
        goal_count=len(df_goals)
    ), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
