import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
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
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Charge et traite les données des buts de Neymar"""
    try:
        df = pd.read_csv('Neymar_Buts_LaLiga.csv', sep=";", encoding='cp1252')
        
        # Normalisation des coordonnées si nécessaire
        df_goals = df.copy()
        df_goals.loc[df_goals['X'] < 10, 'X'] = df_goals.loc[df_goals['X'] < 10, 'X'] * 120
        df_goals.loc[df_goals['Y'] < 10, 'Y'] = df_goals.loc[df_goals['Y'] < 10, 'Y'] * 80
        
        # Ajout d'informations supplémentaires
        df_goals['distance_but'] = np.sqrt((120 - df_goals['X'])**2 + (40 - df_goals['Y'])**2) * 0.9144
        df_goals['zone'] = df_goals['X'].apply(lambda x: 
            'Surface' if x > 103.5 else 
            'Zone dangereuse' if x > 90 else 
            'Milieu offensif' if x > 60 else 'Autres')
        
        return df_goals
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {e}")
        return None

def find_video_file(goal_data, video_folder="Neymar_LaLiga_Buts"):
    """Recherche le fichier vidéo correspondant au but en utilisant la colonne 'video_but'"""
    
    # Si video_but est disponible et non vide
    if 'video_but' in goal_data and pd.notna(goal_data['video_but']) and str(goal_data['video_but']).strip():
        video_filename = str(goal_data['video_but']).strip()
        video_path = os.path.join(video_folder, video_filename)
        
        if os.path.exists(video_path):
            return video_path
        
        # Si le fichier exact n'existe pas, essayer sans extension puis rajouter .mov ou .mp4
        base_name = os.path.splitext(video_filename)[0]
        for ext in ['.mov', '.mp4', '.MOV', '.MP4']:
            video_path_alt = os.path.join(video_folder, base_name + ext)
            if os.path.exists(video_path_alt):
                return video_path_alt
    
    # Fallback : essayer avec l'ID du but si video_but n'est pas disponible
    goal_id = goal_data['id'] if 'id' in goal_data else goal_data.get('goal_id', '')
    
    if os.path.exists(video_folder) and goal_id:
        video_extensions = ['.mp4', '.mov', '.MP4', '.MOV']
        
        for ext in video_extensions:
            # Essayer différents formats de nommage
            possible_names = [
                f"{goal_id}{ext}",
                f"but_{goal_id}{ext}",
                f"goal_{goal_id}{ext}",
                f"neymar_{goal_id}{ext}"
            ]
            
            for name in possible_names:
                video_path = os.path.join(video_folder, name)
                if os.path.exists(video_path):
                    return video_path
    
    return None

def create_pitch_figure(df_goals, selected_goal_id=None):
    """Crée le terrain de football avec les buts de Neymar"""
    fig = go.Figure()
    
    # Dimensions du terrain
    pitch_length, pitch_width = 120, 80
    
    # Dessin du terrain
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
    # Surface droite (attaque)
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
        lambda row: find_video_file(row) is not None, axis=1
    )
    
    # Séparer les buts avec et sans vidéos pour différents affichages
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
            
            texts_no_video.append(f"But #{goal_id} ❌ SANS VIDÉO<br>Minute: {goal['minute']}<br>xG: {goal['xG']:.3f}<br>Adversaire: {goal['a_team'] if goal['h_a'] == 'h' else goal['h_team']}")
        
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
    
    # Affichage des buts AVEC vidéo (vert/rouge/doré)
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
                colors_with_video.append('limegreen')  # Vert pour les buts avec vidéo
                sizes_with_video.append(max(10, 20 * goal['xG']))
            
            texts_with_video.append(f"But #{goal_id} 🎥 AVEC VIDÉO<br>Minute: {goal['minute']}<br>xG: {goal['xG']:.3f}<br>Adversaire: {goal['a_team'] if goal['h_a'] == 'h' else goal['h_team']}")
        
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

def main():
    # Titre principal
    st.markdown('<h1 class="main-header">⚽ Neymar Jr</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="sub-header">Tous ses buts en LaLiga (2013-2017)</h2>', unsafe_allow_html=True)
    
    # Chargement des données
    df_goals = load_data()
    
    if df_goals is None:
        st.error("Impossible de charger les données. Vérifiez que le fichier 'Neymar_Buts_LaLiga.csv' est présent.")
        return
    
    # Sidebar avec filtres
    st.sidebar.header("🎯 Filtres et Options")
    
    # Filtre par saison
    seasons = sorted(df_goals['season'].unique())
    selected_seasons = st.sidebar.multiselect(
        "Sélectionner les saisons",
        seasons,
        default=seasons
    )
    
    # Filtre par type de tir
    shot_types = df_goals['shotType'].unique()
    selected_shot_types = st.sidebar.multiselect(
        "Type de tir",
        shot_types,
        default=shot_types
    )
    
    # Filtre par disponibilité vidéo
    video_filter = st.sidebar.selectbox(
        "🎥 Disponibilité vidéo",
        ["Tous les buts", "Avec vidéo uniquement", "Sans vidéo uniquement"]
    )
    
    # Filtre par xG
    min_xg = st.sidebar.slider(
        "xG minimum",
        min_value=0.0,
        max_value=1.0,
        value=0.0,
        step=0.1
    )
    
    # Application des filtres
    filtered_df = df_goals[
        (df_goals['season'].isin(selected_seasons)) &
        (df_goals['shotType'].isin(selected_shot_types)) &
        (df_goals['xG'] >= min_xg)
    ]
    
    # Appliquer le filtre vidéo
    if video_filter != "Tous les buts":
        filtered_df['has_video'] = filtered_df.apply(
            lambda row: find_video_file(row) is not None, axis=1
        )
        
        if video_filter == "Avec vidéo uniquement":
            filtered_df = filtered_df[filtered_df['has_video']]
        elif video_filter == "Sans vidéo uniquement":
            filtered_df = filtered_df[~filtered_df['has_video']]
    
    if filtered_df.empty:
        st.warning("Aucun but ne correspond aux critères sélectionnés.")
        return
    
    # Vérifier les vidéos disponibles pour les statistiques
    filtered_df_with_videos = filtered_df.copy()
    filtered_df_with_videos['has_video'] = filtered_df_with_videos.apply(
        lambda row: find_video_file(row) is not None, axis=1
    )
    
    goals_with_videos = filtered_df_with_videos[filtered_df_with_videos['has_video']]
    goals_without_videos = filtered_df_with_videos[~filtered_df_with_videos['has_video']]
    
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
        
        # Initialiser la session state pour le but sélectionné
        if 'selected_goal' not in st.session_state:
            st.session_state.selected_goal = None
        
        # Créer et afficher le graphique
        fig = create_pitch_figure(filtered_df, st.session_state.selected_goal)
        
        # Gérer les clics sur le graphique
        selected_points = st.plotly_chart(fig, use_container_width=True, on_select="rerun")
        
        # Traitement des points sélectionnés
        if selected_points and 'selection' in selected_points:
            selection = selected_points['selection']
            if 'points' in selection and len(selection['points']) > 0:
                # Récupérer l'index du point cliqué
                point_index = selection['points'][0]['point_index']
                curve_number = selection['points'][0]['curve_number']
                
                # Déterminer quel dataset a été cliqué (avec ou sans vidéo)
                if curve_number == 1:  # Buts sans vidéo (premier trace ajouté)
                    goals_subset = goals_without_videos
                elif curve_number == 2:  # Buts avec vidéo (deuxième trace ajouté)
                    goals_subset = goals_with_videos
                else:
                    goals_subset = filtered_df  # Fallback
                
                if point_index < len(goals_subset):
                    selected_goal_id = goals_subset.iloc[point_index]['id']
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
        
        # Statistiques vidéos
        st.subheader("🎥 État des Vidéos")
        video_stats = pd.DataFrame({
            'Statut': ['Avec vidéo', 'Sans vidéo'],
            'Nombre': [len(goals_with_videos), len(goals_without_videos)],
            'Pourcentage': [
                f"{len(goals_with_videos)/len(filtered_df)*100:.1f}%",
                f"{len(goals_without_videos)/len(filtered_df)*100:.1f}%"
            ]
        })
        st.dataframe(video_stats, hide_index=True)
        
        # Graphique en secteurs des zones
        fig_pie = px.pie(
            values=zone_stats['Nombre'],
            names=zone_stats.index,
            title="Répartition par zone",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Section vidéo
    if st.session_state.selected_goal:
        selected_goal_data = filtered_df[filtered_df['id'] == st.session_state.selected_goal].iloc[0]
        
        st.divider()
        st.subheader(f"🎥 But #{st.session_state.selected_goal}")
        
        col_video, col_details = st.columns([2, 1])
        
        with col_video:
            # Rechercher le fichier vidéo en utilisant les données complètes de la ligne
            video_file = find_video_file(selected_goal_data)
            
            if video_file:
                st.markdown('<div class="video-container">', unsafe_allow_html=True)
                st.success(f"🎥 Vidéo trouvée : {os.path.basename(video_file)}")
                try:
                    with open(video_file, 'rb') as video_file_obj:
                        video_bytes = video_file_obj.read()
                    st.video(video_bytes)
                except Exception as e:
                    st.error(f"Erreur lors de la lecture de la vidéo : {e}")
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning(f"Vidéo non trouvée pour le but #{st.session_state.selected_goal}")
                if pd.notna(selected_goal_data.get('video_but')):
                    st.info(f"Nom attendu : {selected_goal_data['video_but']}")
                else:
                    st.info("Aucun nom de vidéo spécifié dans la colonne 'video_but'")
                st.info("Vérifiez que le dossier 'Neymar_LaLiga_Buts' contient le fichier vidéo correspondant")
        
        with col_details:
            st.markdown('<div class="goal-info">', unsafe_allow_html=True)
            st.write(f"**Minute :** {selected_goal_data['minute']}'")
            st.write(f"**xG :** {selected_goal_data['xG']:.3f}")
            st.write(f"**Distance :** {selected_goal_data['distance_but']:.1f}m")
            st.write(f"**Zone :** {selected_goal_data['zone']}")
            st.write(f"**Type de tir :** {selected_goal_data['shotType']}")
            st.write(f"**Saison :** {selected_goal_data['season']}")
            st.write(f"**Match :** {selected_goal_data['h_team']} vs {selected_goal_data['a_team']}")
            st.write(f"**Score :** {selected_goal_data['h_goals']}-{selected_goal_data['a_goals']}")
            if pd.notna(selected_goal_data['player_assisted']):
                st.write(f"**Passeur :** {selected_goal_data['player_assisted']}")
            if pd.notna(selected_goal_data.get('video_but')):
                st.write(f"**Fichier vidéo :** {selected_goal_data['video_but']}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Bouton pour désélectionner
        if st.button("🔄 Retour à la vue générale"):
            st.session_state.selected_goal = None
            st.rerun()
    
    # Tableau détaillé
    st.divider()
    st.subheader("📋 Liste détaillée des buts")
    
    # Préparer les données pour affichage
    display_df = filtered_df[['id', 'minute', 'season', 'h_team', 'a_team', 'xG', 'shotType', 'zone', 'distance_but', 'video_but']].copy()
    display_df.columns = ['ID', 'Minute', 'Saison', 'Équipe dom.', 'Équipe ext.', 'xG', 'Type tir', 'Zone', 'Distance (m)', 'Fichier vidéo']
    display_df = display_df.round({'xG': 3, 'Distance (m)': 1})
    
    st.dataframe(
        display_df,
        use_container_width=True,
        on_select="rerun",
        selection_mode="single-row"
    )
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: gray; font-size: 0.9rem;'>
        <p>📊 Analyse interactive des buts de Neymar Jr en LaLiga (2013-2017)</p>
        <p>Données xG et coordonnées Opta • Vidéos incluses</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
