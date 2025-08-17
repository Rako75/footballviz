import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import os
from pathlib import Path

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
        font-size: 3.5rem;
        font-weight: bold;
        text-align: center;
        color: #FF4444;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .sub-header {
        font-size: 1.8rem;
        text-align: center;
        color: #4ECDC4;
        margin-bottom: 2rem;
        font-weight: 500;
    }
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        text-align: center;
    }
    .video-container {
        border: 3px solid #4ECDC4;
        border-radius: 15px;
        padding: 1.5rem;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    .goal-info {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .stats-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid #FF4444;
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
                    if len(df.columns) > 5:
                        break
                except:
                    continue
            else:
                continue
            break
        else:
            st.error("Impossible de charger le fichier CSV")
            return None
        
        # Traitement des données
        df_goals = df.copy()
        
        # Conversion sécurisée des coordonnées
        df_goals['X'] = pd.to_numeric(df_goals['X'], errors='coerce')
        df_goals['Y'] = pd.to_numeric(df_goals['Y'], errors='coerce')
        df_goals['xG'] = pd.to_numeric(df_goals['xG'], errors='coerce')
        
        # Normalisation des coordonnées
        if df_goals['X'].max() <= 1:
            df_goals['X'] = df_goals['X'] * 120
        if df_goals['Y'].max() <= 1:
            df_goals['Y'] = df_goals['Y'] * 80
        
        # Orientation vers le but adverse
        goals_in_attacking_half = len(df_goals[df_goals['X'] > 60])
        goals_in_defensive_half = len(df_goals[df_goals['X'] <= 60])
        
        if goals_in_defensive_half > goals_in_attacking_half:
            df_goals['X'] = 120 - df_goals['X']
        
        # Calculs supplémentaires
        df_goals['distance_but'] = np.sqrt((120 - df_goals['X'])**2 + (40 - df_goals['Y'])**2) * 0.9144
        
        # Définition des zones
        df_goals['zone'] = df_goals['X'].apply(lambda x: 
            'Surface de réparation' if x > 103.5 else 
            'Zone dangereuse (16-30m)' if x > 90 else 
            'Milieu offensif (30-60m)' if x > 60 else 
            'Loin du but (>60m)')
        
        # Créer un ID si manquant
        if 'id' not in df_goals.columns:
            df_goals['id'] = range(1, len(df_goals) + 1)
        
        # Ajouter une saison par défaut si manquante
        if 'season' not in df_goals.columns:
            df_goals['season'] = '2013-2017'
        
        return df_goals
        
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {e}")
        return None

def scan_video_folder(video_folder="Neymar_LaLiga_Buts"):
    """Scanne le dossier vidéo et retourne la liste des fichiers disponibles"""
    video_files = []
    
    if os.path.exists(video_folder):
        for file in os.listdir(video_folder):
            if file.lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.webm')):
                video_files.append(file)
    
    return video_files

def find_video_file(goal_data, video_folder="Neymar_LaLiga_Buts", available_videos=None):
    """Recherche le fichier vidéo correspondant au but"""
    
    if not os.path.exists(video_folder):
        return None
    
    if available_videos is None:
        available_videos = scan_video_folder(video_folder)
    
    # Utiliser la colonne 'video_but' si disponible
    if 'video_but' in goal_data and pd.notna(goal_data['video_but']) and str(goal_data['video_but']).strip():
        video_filename = str(goal_data['video_but']).strip()
        
        if video_filename in available_videos:
            return os.path.join(video_folder, video_filename)
        
        base_name = os.path.splitext(video_filename)[0]
        for video in available_videos:
            if os.path.splitext(video)[0] == base_name:
                return os.path.join(video_folder, video)
    
    # Utiliser l'ID du but
    goal_id = goal_data.get('id', '')
    if goal_id:
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
    
    # Recherche par index
    if isinstance(goal_id, int) and 1 <= goal_id <= len(available_videos):
        return os.path.join(video_folder, available_videos[goal_id - 1])
    
    return None

def create_custom_pitch_figure(df_goals, selected_goal_id=None, season_colors=None):
    """Crée le terrain de football personnalisé avec style professionnel"""
    fig = go.Figure()
    
    # Dimensions du terrain
    pitch_length, pitch_width = 120, 80
    
    # Couleurs par saison
    if season_colors is None:
        season_colors = {
            '2013-14': '#FF4444',
            '2014-15': '#4ECDC4', 
            '2015-16': '#45B7D1',
            '2016-17': '#96CEB4',
            '2017-18': '#FFEAA7',
            '2013-2017': '#FF4444'
        }
    
    # Fond du terrain avec dégradé
    fig.add_shape(
        type="rect",
        x0=0, y0=0, x1=pitch_length, y1=pitch_width,
        line=dict(color="white", width=3),
        fillcolor="rgba(45, 90, 45, 0.9)"
    )
    
    # Ligne médiane
    fig.add_shape(
        type="line",
        x0=pitch_length/2, y0=0, x1=pitch_length/2, y1=pitch_width,
        line=dict(color="white", width=2)
    )
    
    # Cercle central
    fig.add_shape(
        type="circle",
        x0=pitch_length/2-9.15, y0=pitch_width/2-9.15,
        x1=pitch_length/2+9.15, y1=pitch_width/2+9.15,
        line=dict(color="white", width=2),
        fillcolor="rgba(0,0,0,0)"
    )
    
    # Point central
    fig.add_trace(go.Scatter(
        x=[pitch_length/2], y=[pitch_width/2],
        mode='markers',
        marker=dict(color='white', size=6),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Surfaces de réparation
    penalty_box_length = 16.5
    penalty_box_width = 40.32
    penalty_box_y_start = (pitch_width - penalty_box_width) / 2
    
    # Surface droite (attaque)
    fig.add_shape(
        type="rect",
        x0=pitch_length-penalty_box_length, y0=penalty_box_y_start,
        x1=pitch_length, y1=penalty_box_y_start + penalty_box_width,
        line=dict(color="white", width=2),
        fillcolor="rgba(255, 68, 68, 0.1)"
    )
    
    # Surface gauche (défense)
    fig.add_shape(
        type="rect",
        x0=0, y0=penalty_box_y_start,
        x1=penalty_box_length, y1=penalty_box_y_start + penalty_box_width,
        line=dict(color="white", width=2),
        fillcolor="rgba(255,255,255,0.05)"
    )
    
    # Surfaces de but (6 yards)
    goal_box_length = 5.5
    goal_box_width = 18.32
    goal_box_y_start = (pitch_width - goal_box_width) / 2
    
    # Surface de but droite
    fig.add_shape(
        type="rect",
        x0=pitch_length-goal_box_length, y0=goal_box_y_start,
        x1=pitch_length, y1=goal_box_y_start + goal_box_width,
        line=dict(color="white", width=2),
        fillcolor="rgba(255, 68, 68, 0.15)"
    )
    
    # Surface de but gauche
    fig.add_shape(
        type="rect",
        x0=0, y0=goal_box_y_start,
        x1=goal_box_length, y1=goal_box_y_start + goal_box_width,
        line=dict(color="white", width=2),
        fillcolor="rgba(255,255,255,0.05)"
    )
    
    # Buts
    goal_width = 7.32
    goal_y_start = (pitch_width - goal_width) / 2
    
    # But droit (où Neymar marque)
    fig.add_shape(
        type="line",
        x0=pitch_length, y0=goal_y_start,
        x1=pitch_length, y1=goal_y_start + goal_width,
        line=dict(color="#FFD700", width=8)
    )
    
    # But gauche
    fig.add_shape(
        type="line",
        x0=0, y0=goal_y_start,
        x1=0, y1=goal_y_start + goal_width,
        line=dict(color="white", width=4)
    )
    
    # Points de penalty
    fig.add_trace(go.Scatter(
        x=[pitch_length-11, 11], y=[pitch_width/2, pitch_width/2],
        mode='markers',
        marker=dict(color='white', size=8),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Arcs de penalty
    theta_right = np.linspace(-np.pi/2, np.pi/2, 50)
    arc_x_right = pitch_length - 11 + 9.15 * np.cos(theta_right)
    arc_y_right = pitch_width/2 + 9.15 * np.sin(theta_right)
    valid_right = arc_x_right <= pitch_length - penalty_box_length
    
    fig.add_trace(go.Scatter(
        x=arc_x_right[valid_right],
        y=arc_y_right[valid_right],
        mode='lines',
        line=dict(color='white', width=2),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    theta_left = np.linspace(np.pi/2, 3*np.pi/2, 50)
    arc_x_left = 11 + 9.15 * np.cos(theta_left)
    arc_y_left = pitch_width/2 + 9.15 * np.sin(theta_left)
    valid_left = arc_x_left >= penalty_box_length
    
    fig.add_trace(go.Scatter(
        x=arc_x_left[valid_left],
        y=arc_y_left[valid_left],
        mode='lines',
        line=dict(color='white', width=2),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Affichage des buts par saison
    unique_seasons = sorted(df_goals['season'].unique()) if 'season' in df_goals.columns else ['2013-2017']
    
    # Générer des couleurs automatiquement si nécessaire
    if len(unique_seasons) > len(season_colors):
        colors = px.colors.qualitative.Set3
        for i, season in enumerate(unique_seasons):
            if season not in season_colors:
                season_colors[season] = colors[i % len(colors)]
    
    for season in unique_seasons:
        season_data = df_goals[df_goals['season'] == season] if 'season' in df_goals.columns else df_goals
        
        if season_data.empty:
            continue
        
        colors = []
        sizes = []
        texts = []
        
        for _, goal in season_data.iterrows():
            goal_id = goal['id']
            
            if selected_goal_id and goal_id == selected_goal_id:
                colors.append('#FFD700')  # Or pour le but sélectionné
                sizes.append(max(20, 40 * goal['xG']) * 1.8)
            else:
                colors.append(season_colors.get(season, '#FF4444'))
                sizes.append(max(12, 25 * goal['xG']))
            
            texts.append(
                f"<b>But #{goal_id}</b><br>"
                f"Minute: {goal['minute']}'<br>"
                f"xG: {goal['xG']:.3f}<br>"
                f"Distance: {goal['distance_but']:.1f}m<br>"
                f"Zone: {goal['zone']}"
            )
        
        fig.add_trace(go.Scatter(
            x=season_data['X'],
            y=season_data['Y'],
            mode='markers',
            marker=dict(
                color=colors,
                size=sizes,
                line=dict(color='white', width=2),
                opacity=0.9
            ),
            text=texts,
            hovertemplate='%{text}<extra></extra>',
            customdata=season_data['id'],
            name=season,
            visible=True
        ))
    
    # Configuration du graphique
    fig.update_layout(
        title=dict(
            text="<b>Neymar Jr - Buts en LaLiga</b><br><sub>🥅 Cliquez sur un but pour voir la vidéo</sub>",
            x=0.5,
            font=dict(size=24, color="#2c3e50"),
            pad=dict(t=20)
        ),
        xaxis=dict(
            range=[-8, 128],
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            title=""
        ),
        yaxis=dict(
            range=[-8, 88],
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            title="",
            scaleanchor="x",
            scaleratio=1
        ),
        plot_bgcolor='rgba(30, 60, 30, 0.8)',
        paper_bgcolor='white',
        height=700,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=12)
        ),
        margin=dict(l=50, r=50, t=100, b=50)
    )
    
    return fig

def display_video(video_path):
    """Affiche une vidéo avec gestion d'erreur"""
    try:
        if not os.path.exists(video_path):
            st.warning("Vidéo introuvable")
            return False
            
        file_size = os.path.getsize(video_path)
        if file_size == 0:
            st.warning("Fichier vidéo vide")
            return False
            
        st.info(f"📁 {os.path.basename(video_path)} ({file_size / (1024*1024):.1f} MB)")
        
        with open(video_path, 'rb') as video_file:
            video_bytes = video_file.read()
        
        if len(video_bytes) > 0:
            st.video(video_bytes)
            return True
        else:
            st.warning("Impossible de lire le contenu du fichier")
            return False
            
    except Exception as e:
        st.error(f"Erreur lors de l'affichage : {e}")
        return False

def main():
    # Titre principal
    st.markdown('<h1 class="main-header">⚽ Neymar Jr</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="sub-header">Cartographie complète de ses buts en LaLiga</h2>', unsafe_allow_html=True)
    
    # Couleurs de saisons
    season_colors = {
        '2013-14': '#FF4444',
        '2014-15': '#4ECDC4', 
        '2015-16': '#45B7D1',
        '2016-17': '#96CEB4',
        '2017-18': '#FFEAA7',
        '2013-2017': '#FF4444'
    }
    
    # Chargement des données
    df_goals = load_data()
    
    if df_goals is None:
        st.stop()
    
    # Scanner les vidéos disponibles
    available_videos = scan_video_folder()
    
    # Sidebar avec filtres
    st.sidebar.header("🎯 Filtres")
    
    # Filtre par saison
    if 'season' in df_goals.columns and len(df_goals['season'].unique()) > 1:
        seasons = sorted(df_goals['season'].unique())
        selected_seasons = st.sidebar.multiselect(
            "Sélectionner les saisons",
            seasons,
            default=seasons
        )
        if selected_seasons:
            df_goals = df_goals[df_goals['season'].isin(selected_seasons)]
    
    # Filtre par type de tir
    if 'shotType' in df_goals.columns:
        shot_types = df_goals['shotType'].unique()
        selected_shot_types = st.sidebar.multiselect(
            "Type de tir",
            shot_types,
            default=shot_types
        )
        if selected_shot_types:
            df_goals = df_goals[df_goals['shotType'].isin(selected_shot_types)]
    
    # Filtre par xG
    if not df_goals.empty:
        min_xg = st.sidebar.slider(
            "xG minimum",
            min_value=0.0,
            max_value=float(df_goals['xG'].max()),
            value=0.0,
            step=0.1
        )
        
        # Application des filtres
        filtered_df = df_goals[df_goals['xG'] >= min_xg].copy()
    else:
        filtered_df = df_goals
    
    if filtered_df.empty:
        st.warning("⚠️ Aucun but ne correspond aux critères sélectionnés.")
        st.stop()
    
    # Métriques principales
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown("""
        <div class="metric-container">
            <h3 style="margin:0; font-size:2rem;">⚽</h3>
            <h2 style="margin:0;">{}</h2>
            <p style="margin:0;">Buts marqués</p>
        </div>
        """.format(len(filtered_df)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-container">
            <h3 style="margin:0; font-size:2rem;">🎯</h3>
            <h2 style="margin:0;">{:.2f}</h2>
            <p style="margin:0;">xG Total</p>
        </div>
        """.format(filtered_df['xG'].sum()), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-container">
            <h3 style="margin:0; font-size:2rem;">📏</h3>
            <h2 style="margin:0;">{:.1f}m</h2>
            <p style="margin:0;">Distance moy.</p>
        </div>
        """.format(filtered_df['distance_but'].mean()), unsafe_allow_html=True)
    
    with col4:
        goals_in_box = len(filtered_df[filtered_df['X'] > 103.5])
        st.markdown("""
        <div class="metric-container">
            <h3 style="margin:0; font-size:2rem;">🏟️</h3>
            <h2 style="margin:0;">{}</h2>
            <p style="margin:0;">Dans la surface</p>
        </div>
        """.format(goals_in_box), unsafe_allow_html=True)
    
    with col5:
        st.markdown("""
        <div class="metric-container">
            <h3 style="margin:0; font-size:2rem;">🎥</h3>
            <h2 style="margin:0;">{}</h2>
            <p style="margin:0;">Vidéos disponibles</p>
        </div>
        """.format(len(available_videos)), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Interface principale
    col_main, col_info = st.columns([3, 1])
    
    with col_main:
        st.subheader("🟢 Terrain Interactif")
        
        # Initialiser la session state
        if 'selected_goal' not in st.session_state:
            st.session_state.selected_goal = None
        
        # Créer le graphique
        fig = create_custom_pitch_figure(filtered_df, st.session_state.selected_goal, season_colors)
        
        # Sélecteur de but
        if not filtered_df.empty:
            goal_options = []
            for _, row in filtered_df.iterrows():
                season_info = f" ({row['season']})" if 'season' in row else ""
                goal_options.append(f"But #{row['id']}{season_info} - Minute {row['minute']}")
            
            selected_option = st.selectbox(
                "Sélectionner un but:",
                ["Aucune sélection"] + goal_options,
                index=0
            )
            
            if selected_option != "Aucune sélection":
                goal_id = int(selected_option.split('#')[1].split(' ')[0])
                st.session_state.selected_goal = goal_id
        
        # Afficher le graphique
        selected_points = st.plotly_chart(fig, use_container_width=True, on_select="rerun")
        
        # Gérer les clics
        if selected_points and 'selection' in selected_points:
            selection = selected_points['selection']
            if 'points' in selection and len(selection['points']) > 0:
                point_data = selection['points'][0]
                if 'customdata' in point_data:
                    selected_goal_id = point_data['customdata']
                    st.session_state.selected_goal = selected_goal_id
                    st.rerun()
    
    with col_info:
        st.subheader("📊 Statistiques")
        
        if not filtered_df.empty:
            # Statistiques par zone
            zone_stats = filtered_df.groupby('zone').agg({
                'id': 'count',
                'xG': 'mean'
            }).round(3)
            zone_stats.columns = ['Buts', 'xG moyen']
            
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            st.markdown("**Répartition par zone:**")
            st.dataframe(zone_stats, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Graphique des zones
            if len(zone_stats) > 0:
                fig_pie = px.pie(
                    values=zone_stats['Buts'],
                    names=zone_stats.index,
                    title="Répartition par zone",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_pie.update_layout(height=300, showlegend=True)
                st.plotly_chart(fig_pie, use_container_width=True)
    
    # Section vidéo
    if st.session_state.selected_goal and not filtered_df.empty:
        selected_goal_data = filtered_df[filtered_df['id'] == st.session_state.selected_goal]
        
        if not selected_goal_data.empty:
            selected_goal_data = selected_goal_data.iloc[0]
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader(f"🎥 But #{st.session_state.selected_goal}")
            
            col_video, col_details = st.columns([2, 1])
            
            with col_video:
                video_file = find_video_file(selected_goal_data, available_videos=available_videos)
                
                if video_file:
                    st.markdown('<div class="video-container">', unsafe_allow_html=True)
                    success = display_video(video_file)
                    if success:
                        st.success("✅ Vidéo chargée avec succès!")
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.info("📹 Vidéo en cours de chargement...")
            
            with col_details:
                st.markdown('<div class="goal-info">', unsafe_allow_html=True)
                st.markdown(f"**⏱️ Minute :** {selected_goal_data['minute']}'")
                st.markdown(f"**🎯 xG :** {selected_goal_data['xG']:.3f}")
                st.markdown(f"**📏 Distance :** {selected_goal_data['distance_but']:.1f}m")
                st.markdown(f"**🏟️ Zone :** {selected_goal_data['zone']}")
                
                if 'shotType' in selected_goal_data and pd.notna(selected_goal_data['shotType']):
                    st.markdown(f"**⚽ Type :** {selected_goal_data['shotType']}")
                
                if 'season' in selected_goal_data and pd.notna(selected_goal_data['season']):
                    st.markdown(f"**📅 Saison :** {selected_goal_data['season']}")
                
                if 'h_team' in selected_goal_data and 'a_team' in selected_goal_data:
                    if pd.notna(selected_goal_data['h_team']) and pd.notna(selected_goal_data['a_team']):
                        st.markdown(f"**🏆 Match :** {selected_goal_data['h_team']} vs {selected_goal_data['a_team']}")
                
                if 'player_assisted' in selected_goal_data and pd.notna(selected_goal_data['player_assisted']):
                    st.markdown(f"**🤝 Passeur :** {selected_goal_data['player_assisted']}")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Boutons de navigation
            st.markdown("<br>", unsafe_allow_html=True)
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            
            with col_btn1:
                if st.button("🔄 Retour à la vue générale", use_container_width=True):
                    st.session_state.selected_goal = None
                    st.rerun()
            
            with col_btn2:
                # Navigation vers le but précédent
                current_index = filtered_df[filtered_df['id'] == st.session_state.selected_goal].index
                if len(current_index) > 0:
                    current_index = current_index[0]
                    prev_indices = filtered_df.index[filtered_df.index < current_index]
                    if len(prev_indices) > 0:
                        prev_goal_id = filtered_df.loc[prev_indices.max(), 'id']
                        if st.button("⬅️ But précédent", use_container_width=True):
                            st.session_state.selected_goal = prev_goal_id
                            st.rerun()
            
            with col_btn3:
                # Navigation vers le but suivant
                current_index = filtered_df[filtered_df['id'] == st.session_state.selected_goal].index
                if len(current_index) > 0:
                    current_index = current_index[0]
                    next_indices = filtered_df.index[filtered_df.index > current_index]
                    if len(next_indices) > 0:
                        next_goal_id = filtered_df.loc[next_indices.min(), 'id']
                        if st.button("➡️ But suivant", use_container_width=True):
                            st.session_state.selected_goal = next_goal_id
                            st.rerun()
    
    # Tableau détaillé
    if not filtered_df.empty:
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("📋 Liste complète des buts")
        
        # Préparer les données pour affichage
        display_columns = ['id', 'minute', 'xG', 'zone', 'distance_but']
        
        # Ajouter les colonnes optionnelles si elles existent
        optional_columns = ['season', 'shotType', 'h_team', 'a_team', 'player_assisted']
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
            'shotType': 'Type de tir',
            'h_team': 'Équipe dom.',
            'a_team': 'Équipe ext.',
            'player_assisted': 'Passeur'
        }
        
        display_df = display_df.rename(columns=column_names)
        
        # Arrondir les valeurs numériques
        if 'xG' in display_df.columns:
            display_df['xG'] = display_df['xG'].round(3)
        if 'Distance (m)' in display_df.columns:
            display_df['Distance (m)'] = display_df['Distance (m)'].round(1)
        
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
    
    # Footer avec informations
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; padding: 2rem; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);'>
        <h3 style='margin: 0 0 1rem 0;'>⚽ Neymar Jr - LaLiga Legacy</h3>
        <p style='margin: 0; font-size: 1.1rem;'>
            🎯 {} buts analysés • 🎥 {} vidéos disponibles • 📊 Données xG Opta
        </p>
        <p style='margin: 0.5rem 0 0 0; opacity: 0.8;'>
            Application interactive développée pour l'analyse des performances de Neymar Jr au FC Barcelone
        </p>
    </div>
    """.format(
        len(df_goals) if not df_goals.empty else 0,
        len(available_videos)
    ), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
