import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import os
from datetime import datetime
import numpy as np

# Configuration de la page
st.set_page_config(
    page_title="⚽ Neymar Jr. - Visualisateur de Buts",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styles CSS personnalisés
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    
    .stats-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }
    
    .filter-section {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 4px solid #1f77b4;
    }
    
    .goal-info {
        background: #fff;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 4px solid #28a745;
    }
    
    .video-container {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Charge et prépare les données des buts de Neymar"""
    try:
        # Charger le CSV avec le bon séparateur et encoding
        df = pd.read_csv('Neymar_Buts_LaLiga.csv', sep=';', encoding='cp1252')
        
        # Nettoyer les données
        df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y')
        df['season_label'] = df['season'].astype(str) + '-' + (df['season'] + 1).astype(str)
        
        # Créer des labels plus lisibles
        df['shot_type_fr'] = df['shotType'].map({
            'RightFoot': 'Pied droit',
            'LeftFoot': 'Pied gauche', 
            'Head': 'Tête'
        })
        
        df['situation_fr'] = df['situation'].map({
            'OpenPlay': 'Jeu ouvert',
            'SetPiece': 'Coup de pied arrêté'
        }).fillna(df['situation'])
        
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {e}")
        return pd.DataFrame()

def normalize_coordinates_vertical_half(x, y):
    """Normalise les coordonnées pour un terrain vertical demi-terrain (comme mplsoccer VerticalPitch half=True)"""
    # Dimensions pour demi-terrain vertical (mplsoccer style)
    # X va de 0 à 68 (largeur du terrain)
    # Y va de 52.5 à 105 (moitié offensive du terrain)
    
    pitch_width = 68
    half_pitch_length = 52.5  # Demi-terrain
    
    # Détecter le système de coordonnées
    if x <= 1.0 and y <= 1.0:
        # Système normalisé (0-1)
        # Pour un demi-terrain, on veut montrer seulement la moitié offensive
        
        # X: largeur du terrain (0 = côté gauche, 1 = côté droit)
        x_terrain = x * pitch_width
        
        # Y: profondeur, mais seulement la moitié offensive
        # y=0 correspond à la ligne médiane (52.5), y=1 correspond à la ligne de but (105)
        y_terrain = 52.5 + y * half_pitch_length
        
    else:
        # Système en yards/mètres
        if x > 50:  # Système yards
            # Convertir et ajuster pour demi-terrain
            x_terrain = y * pitch_width / 80
            # Pour la profondeur, on mappe vers la moitié offensive
            y_terrain = 52.5 + (x - 60) * half_pitch_length / 60  # 60-120 yards -> 52.5-105m
        else:
            # Système différent
            x_terrain = y * pitch_width / 80
            y_terrain = 52.5 + x * half_pitch_length / 60
    
    return x_terrain, y_terrain

def create_vertical_half_pitch(df_filtered, selected_goal=None):
    """Crée un terrain vertical demi-terrain style mplsoccer"""
    
    # Dimensions du demi-terrain vertical
    pitch_width = 68
    pitch_start = 52.5  # Ligne médiane
    pitch_end = 105     # Ligne de but
    
    fig = go.Figure()
    
    # Couleur de fond du terrain (vert foncé)
    fig.add_shape(
        type="rect",
        x0=0, y0=pitch_start, x1=pitch_width, y1=pitch_end,
        line=dict(color="white", width=2),
        fillcolor="rgba(34, 139, 34, 1)"
    )
    
    # Ligne médiane (en bas)
    fig.add_shape(
        type="line",
        x0=0, y0=pitch_start, x1=pitch_width, y1=pitch_start,
        line=dict(color="white", width=2)
    )
    
    # Cercle central (demi-cercle)
    fig.add_shape(
        type="path",
        path=f"M 24.85 {pitch_start} A 9.15 9.15 0 0 1 43.15 {pitch_start}",
        line=dict(color="white", width=2),
        fillcolor="rgba(255,255,255,0)"
    )
    
    # Surface de réparation
    penalty_area_width = 40.3
    penalty_area_start = (pitch_width - penalty_area_width) / 2
    penalty_area_end = penalty_area_start + penalty_area_width
    
    fig.add_shape(
        type="rect",
        x0=penalty_area_start, y0=pitch_end-16.5, 
        x1=penalty_area_end, y1=pitch_end,
        line=dict(color="white", width=2),
        fillcolor="rgba(255,255,255,0.05)"
    )
    
    # Surface de but
    goal_area_width = 18.3
    goal_area_start = (pitch_width - goal_area_width) / 2
    goal_area_end = goal_area_start + goal_area_width
    
    fig.add_shape(
        type="rect",
        x0=goal_area_start, y0=pitch_end-5.5,
        x1=goal_area_end, y1=pitch_end,
        line=dict(color="white", width=2),
        fillcolor="rgba(255,255,255,0.05)"
    )
    
    # Ligne de but (poteaux)
    goal_width = 7.32
    goal_start = (pitch_width - goal_width) / 2
    goal_end = goal_start + goal_width
    
    fig.add_shape(
        type="line",
        x0=goal_start, y0=pitch_end, x1=goal_end, y1=pitch_end,
        line=dict(color="white", width=6)
    )
    
    # Point de penalty
    fig.add_shape(
        type="circle",
        x0=pitch_width/2-0.5, y0=pitch_end-11-0.5,
        x1=pitch_width/2+0.5, y1=pitch_end-11+0.5,
        line=dict(color="white", width=2),
        fillcolor="white"
    )
    
    # Arc de cercle du point de penalty
    fig.add_shape(
        type="path",
        path=f"M 24.85 {pitch_end-16.5} A 9.15 9.15 0 0 1 43.15 {pitch_end-16.5}",
        line=dict(color="white", width=2),
        fillcolor="rgba(255,255,255,0)"
    )
    
    if not df_filtered.empty:
        # Normaliser les coordonnées
        x_coords = []
        y_coords = []
        
        for _, row in df_filtered.iterrows():
            x_norm, y_norm = normalize_coordinates_vertical_half(row['X'], row['Y'])
            x_coords.append(x_norm)
            y_coords.append(y_norm)
        
        # Couleurs selon le type de tir (style plus proche de votre exemple)
        color_map = {
            'RightFoot': '#ff4444',  # Rouge pour pied droit
            'LeftFoot': '#4444ff',   # Bleu pour pied gauche
            'Head': '#44ff44'        # Vert pour tête
        }
        
        colors = [color_map.get(shot_type, '#ff4444') for shot_type in df_filtered['shotType']]
        
        # Tailles basées sur xG (comme dans votre exemple: xG*300+100)
        sizes = df_filtered['xG'] * 300 + 100
        sizes = np.clip(sizes / 8, 8, 50)  # Ajuster pour Plotly
        
        # Ajouter les points des buts (tous sont des buts, donc remplis)
        fig.add_trace(go.Scatter(
            x=x_coords,
            y=y_coords,
            mode='markers',
            marker=dict(
                size=sizes,
                color=colors,
                opacity=0.8,
                line=dict(width=2, color='white'),
                symbol='circle'
            ),
            text=[f"⚽ vs {row['a_team']}<br>📅 {row['date'].strftime('%d/%m/%Y')}<br>⏱️ {row['minute']}'<br>📊 xG: {row['xG']:.3f}<br>🦶 {row['shot_type_fr']}<br>🎯 Passeur: {row['player_assisted'] if pd.notna(row['player_assisted']) else 'Aucun'}" 
                  for _, row in df_filtered.iterrows()],
            hovertemplate='<b>%{text}</b><extra></extra>',
            customdata=df_filtered.index,
            name='Buts de Neymar',
            showlegend=False
        ))
        
        # Mettre en évidence le but sélectionné
        if selected_goal is not None and selected_goal < len(df_filtered):
            selected_row = df_filtered.iloc[selected_goal]
            x_sel, y_sel = normalize_coordinates_vertical_half(selected_row['X'], selected_row['Y'])
            fig.add_trace(go.Scatter(
                x=[x_sel],
                y=[y_sel],
                mode='markers',
                marker=dict(
                    size=30,
                    color='yellow',
                    symbol='star',
                    line=dict(width=3, color='black')
                ),
                name='But sélectionné',
                showlegend=False
            ))
    
    # Configuration du layout (style mplsoccer)
    fig.update_layout(
        title=dict(
            text="Neymar Jr. - Carte des Buts<br><span style='font-size:14px'>FC Barcelona - La Liga</span>",
            x=0.05,
            xanchor='left',
            font=dict(size=22, color='black', family='Arial Black')
        ),
        xaxis=dict(
            range=[-2, pitch_width+2],
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            fixedrange=True
        ),
        yaxis=dict(
            range=[pitch_start-2, pitch_end+2],
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            scaleanchor="x",
            scaleratio=1,
            fixedrange=True
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.05,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="rgba(0,0,0,0.3)",
            borderwidth=1
        ),
        height=600,
        margin=dict(l=20, r=20, t=80, b=60)
    )
    
    return fig

def display_goal_video(video_name, goal_info):
    """Affiche la vidéo du but avec les informations"""
    
    st.markdown('<div class="goal-info">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown(f"### ⚽ {goal_info['a_team']}")
        st.markdown(f"**📅 Date:** {goal_info['date'].strftime('%d/%m/%Y')}")
        st.markdown(f"**⏱️ Minute:** {goal_info['minute']}'")
        st.markdown(f"**🦶 Type de tir:** {goal_info['shot_type_fr']}")
        st.markdown(f"**📊 xG:** {goal_info['xG']:.3f}")
        if pd.notna(goal_info['player_assisted']):
            st.markdown(f"**🎯 Passeur:** {goal_info['player_assisted']}")
        st.markdown(f"**🏆 Score:** {goal_info['h_team']} {goal_info['h_goals']}-{goal_info['a_goals']} {goal_info['a_team']}")
    
    with col2:
        # Chercher le fichier vidéo
        video_extensions = ['.mp4', '.mov']
        video_path = None
        
        for ext in video_extensions:
            potential_path = f"Neymar_LaLiga_Buts/{video_name}{ext}"
            if os.path.exists(potential_path):
                video_path = potential_path
                break
        
        if video_path:
            st.markdown('<div class="video-container">', unsafe_allow_html=True)
            try:
                st.video(video_path)
            except Exception as e:
                st.error(f"Erreur lors du chargement de la vidéo : {e}")
                st.info(f"Chemin recherché : {video_path}")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning(f"⚠️ Vidéo non trouvée : {video_name}")
            st.info("Vérifiez que le fichier existe dans le dossier 'Neymar_LaLiga_Buts'")
    
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    # En-tête principal
    st.markdown('<h1 class="main-header">⚽ Neymar Jr. - Visualisateur de Buts FC Barcelone</h1>', 
                unsafe_allow_html=True)
    
    # Charger les données
    df = load_data()
    
    if df.empty:
        st.error("Impossible de charger les données. Vérifiez que le fichier 'Neymar_Buts_LaLiga.csv' est présent.")
        return
    
    # Sidebar pour les filtres
    st.sidebar.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.sidebar.markdown("### 🔍 Filtres de Sélection")
    
    # Filtre par saison
    seasons = sorted(df['season'].unique())
    selected_seasons = st.sidebar.multiselect(
        "🗓️ Saisons",
        options=seasons,
        default=seasons,
        format_func=lambda x: f"{x}-{x+1}"
    )
    
    # Filtre par adversaire
    teams = sorted(df['a_team'].unique())
    selected_teams = st.sidebar.multiselect(
        "🏟️ Adversaires",
        options=teams,
        default=teams
    )
    
    # Filtre par type de tir
    shot_types = df['shotType'].unique()
    selected_shot_types = st.sidebar.multiselect(
        "🦶 Partie du corps",
        options=shot_types,
        default=shot_types,
        format_func=lambda x: {'RightFoot': 'Pied droit', 'LeftFoot': 'Pied gauche', 'Head': 'Tête'}[x]
    )
    
    # Filtre par passeur
    assistants = sorted([x for x in df['player_assisted'].unique() if pd.notna(x)])
    selected_assistants = st.sidebar.multiselect(
        "🎯 Passeurs",
        options=assistants,
        default=assistants
    )
    
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # Appliquer les filtres
    df_filtered = df[
        (df['season'].isin(selected_seasons)) &
        (df['a_team'].isin(selected_teams)) &
        (df['shotType'].isin(selected_shot_types)) &
        ((df['player_assisted'].isin(selected_assistants)) | (df['player_assisted'].isna()))
    ].reset_index(drop=True)
    
    # Statistiques en temps réel
    if not df_filtered.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="stats-container">
                <h3>{len(df_filtered)}</h3>
                <p>Buts Total</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            avg_xg = df_filtered['xG'].mean()
            st.markdown(f"""
            <div class="stats-container">
                <h3>{avg_xg:.3f}</h3>
                <p>xG Moyen</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            most_common_opponent = df_filtered['a_team'].value_counts().index[0] if not df_filtered.empty else "N/A"
            st.markdown(f"""
            <div class="stats-container">
                <h3>{most_common_opponent}</h3>
                <p>Adversaire Favori</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            avg_minute = df_filtered['minute'].mean()
            st.markdown(f"""
            <div class="stats-container">
                <h3>{avg_minute:.0f}'</h3>
                <p>Minute Moyenne</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Layout principal
    col_pitch, col_video = st.columns([3, 2])
    
    with col_pitch:
        if not df_filtered.empty:
            # Créer la visualisation du terrain style mplsoccer
            fig = create_vertical_half_pitch(df_filtered)
            
            # Afficher le graphique avec sélection
            selected_points = st.plotly_chart(
                fig, 
                use_container_width=True,
                key="pitch",
                on_select="rerun"
            )
            
            # Gérer la sélection de points
            if hasattr(st.session_state, 'pitch') and st.session_state.pitch:
                if 'selection' in st.session_state.pitch and st.session_state.pitch['selection']:
                    if 'points' in st.session_state.pitch['selection']:
                        selected_indices = [point['customdata'] for point in st.session_state.pitch['selection']['points']]
                        if selected_indices:
                            selected_goal = selected_indices[0]
                            st.session_state['selected_goal'] = selected_goal
        else:
            st.warning("Aucun but ne correspond aux filtres sélectionnés.")
    
    with col_video:
        st.markdown("### 📹 Vidéo du But")
        
        # Vérifier s'il y a un but sélectionné
        if 'selected_goal' in st.session_state and not df_filtered.empty:
            if st.session_state['selected_goal'] < len(df_filtered):
                goal_info = df_filtered.iloc[st.session_state['selected_goal']]
                video_name = goal_info['video_but']
                display_goal_video(video_name, goal_info)
            else:
                st.info("🎯 Cliquez sur un but sur le terrain pour voir la vidéo")
        else:
            st.info("🎯 Cliquez sur un but sur le terrain pour voir la vidéo")
    
    # Tableau des buts filtrés
    if not df_filtered.empty:
        st.markdown("### 📊 Liste des Buts")
        display_df = df_filtered[[
            'date', 'minute', 'a_team', 'shot_type_fr', 'xG', 'player_assisted'
        ]].copy()
        display_df.columns = ['Date', 'Minute', 'Adversaire', 'Type de tir', 'xG', 'Passeur']
        display_df['Date'] = display_df['Date'].dt.strftime('%d/%m/%Y')
        st.dataframe(display_df, use_container_width=True, height=300)

if __name__ == "__main__":
    main()
