import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import os
from datetime import datetime

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

def normalize_coordinates(x, y):
    """Normalise les coordonnées pour la surface de réparation (40.3m x 16.5m)"""
    # Dimensions de la surface de réparation
    penalty_width = 40.3  # Largeur de la surface de réparation
    penalty_depth = 16.5  # Profondeur de la surface de réparation
    
    # Détecter le système de coordonnées
    if x <= 1.0 and y <= 1.0:
        # Système normalisé (0-1)
        # X semble représenter la distance au but (1 = très proche du but)
        # Y semble représenter la position latérale (0-1 = largeur de la surface)
        
        # Convertir en coordonnées de la surface de réparation
        x_penalty = y * penalty_width  # Position latérale
        y_penalty = (1 - x) * penalty_depth  # Distance au but (0 = ligne de but, 16.5 = limite de surface)
        
    else:
        # Système en yards/mètres
        if x > 50:  # Système yards
            # Normaliser et ajuster pour la surface de réparation
            x_normalized = min(max((120 - x) / 16.5, 0), 1)  # Distance normalisée au but
            y_normalized = min(max(y / 80, 0), 1)  # Position latérale normalisée
        else:
            # Valeurs plus petites
            x_normalized = min(max(x / 16.5, 0), 1)
            y_normalized = min(max(y / 40, 0), 1)
        
        x_penalty = y_normalized * penalty_width
        y_penalty = x_normalized * penalty_depth
    
    return x_penalty, y_penalty

def create_penalty_area_visualization(df_filtered, selected_goal=None):
    """Crée la visualisation de la surface de réparation avec les buts"""
    
    # Dimensions de la surface de réparation (en mètres)
    penalty_width = 40.3
    penalty_depth = 16.5
    goal_width = 7.32
    six_yard_width = 18.32
    six_yard_depth = 5.5
    
    # Créer la figure
    fig = go.Figure()
    
    # Fond de la surface de réparation
    fig.add_shape(
        type="rect",
        x0=0, y0=0, x1=penalty_width, y1=penalty_depth,
        line=dict(color="white", width=4),
        fillcolor="rgba(34, 139, 34, 0.9)"
    )
    
    # Surface de but (6 yards)
    goal_area_x0 = (penalty_width - six_yard_width) / 2
    goal_area_x1 = goal_area_x0 + six_yard_width
    fig.add_shape(
        type="rect",
        x0=goal_area_x0, y0=0, x1=goal_area_x1, y1=six_yard_depth,
        line=dict(color="white", width=3),
        fillcolor="rgba(255, 215, 0, 0.3)"
    )
    
    # Ligne de but avec poteaux
    goal_x0 = (penalty_width - goal_width) / 2
    goal_x1 = goal_x0 + goal_width
    fig.add_shape(
        type="line",
        x0=goal_x0, y0=0, x1=goal_x1, y1=0,
        line=dict(color="white", width=8)
    )
    
    # Poteaux de but
    fig.add_shape(
        type="circle",
        x0=goal_x0-0.3, y0=-0.3, x1=goal_x0+0.3, y1=0.3,
        line=dict(color="white", width=3),
        fillcolor="white"
    )
    fig.add_shape(
        type="circle",
        x0=goal_x1-0.3, y0=-0.3, x1=goal_x1+0.3, y1=0.3,
        line=dict(color="white", width=3),
        fillcolor="white"
    )
    
    # Point de penalty
    penalty_spot_x = penalty_width / 2
    penalty_spot_y = 11
    fig.add_shape(
        type="circle",
        x0=penalty_spot_x-0.3, y0=penalty_spot_y-0.3, 
        x1=penalty_spot_x+0.3, y1=penalty_spot_y+0.3,
        line=dict(color="white", width=2),
        fillcolor="white"
    )
    
    # Arc de penalty (approximation avec un demi-cercle)
    import numpy as np
    theta = np.linspace(0, np.pi, 100)
    arc_radius = 9.15
    arc_x = penalty_spot_x + arc_radius * np.cos(theta)
    arc_y = penalty_spot_y + arc_radius * np.sin(theta)
    
    # Filtrer les points qui sont dans la surface
    valid_points = arc_y <= penalty_depth
    arc_x_filtered = arc_x[valid_points]
    arc_y_filtered = arc_y[valid_points]
    
    fig.add_trace(go.Scatter(
        x=arc_x_filtered,
        y=arc_y_filtered,
        mode='lines',
        line=dict(color='white', width=3),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Lignes de côté
    fig.add_shape(
        type="line",
        x0=0, y0=penalty_depth, x1=penalty_width, y1=penalty_depth,
        line=dict(color="white", width=3, dash="dash")
    )
    
    if not df_filtered.empty:
        # Normaliser les coordonnées pour la surface de réparation
        x_coords = []
        y_coords = []
        
        for _, row in df_filtered.iterrows():
            x_norm, y_norm = normalize_coordinates(row['X'], row['Y'])
            x_coords.append(x_norm)
            y_coords.append(y_norm)
        
        # Couleurs selon le type de tir
        colors = df_filtered['shotType'].map({
            'RightFoot': '#1f77b4',  # Bleu
            'LeftFoot': '#ff7f0e',   # Orange
            'Head': '#2ca02c'        # Vert
        })
        
        # Tailles selon xG (plus grande pour xG élevé)
        sizes = df_filtered['xG'] * 50 + 15
        
        # Ajouter les points des buts
        fig.add_trace(go.Scatter(
            x=x_coords,
            y=y_coords,
            mode='markers',
            marker=dict(
                size=sizes,
                color=colors,
                opacity=0.9,
                line=dict(width=3, color='white'),
                symbol='circle'
            ),
            text=[f"⚽ vs {row['a_team']}<br>📅 {row['date'].strftime('%d/%m/%Y')}<br>⏱️ {row['minute']}'<br>📊 xG: {row['xG']:.3f}<br>🦶 {row['shot_type_fr']}<br>🎯 Passeur: {row['player_assisted'] if pd.notna(row['player_assisted']) else 'Aucun'}" 
                  for _, row in df_filtered.iterrows()],
            hovertemplate='<b>%{text}</b><extra></extra>',
            customdata=df_filtered.index,
            name='Buts de Neymar'
        ))
        
        # Mettre en évidence le but sélectionné
        if selected_goal is not None and selected_goal < len(df_filtered):
            selected_row = df_filtered.iloc[selected_goal]
            x_sel, y_sel = normalize_coordinates(selected_row['X'], selected_row['Y'])
            fig.add_trace(go.Scatter(
                x=[x_sel],
                y=[y_sel],
                mode='markers',
                marker=dict(
                    size=60,
                    color='red',
                    symbol='star',
                    line=dict(width=5, color='yellow')
                ),
                name='But sélectionné',
                showlegend=False
            ))
    
    # Ajouter des annotations
    fig.add_annotation(
        x=penalty_width/2, y=-2,
        text="🥅 BUT ADVERSE",
        showarrow=False,
        font=dict(size=14, color="white", family="Arial Black"),
        bgcolor="rgba(255,0,0,0.7)",
        bordercolor="white",
        borderwidth=2
    )
    
    fig.add_annotation(
        x=penalty_width/2, y=penalty_depth + 1,
        text="🏃‍♂️ LIMITE DE LA SURFACE",
        showarrow=False,
        font=dict(size=12, color="white", family="Arial"),
        bgcolor="rgba(0,0,255,0.7)",
        bordercolor="white",
        borderwidth=1
    )
    
    # Configuration du layout
    fig.update_layout(
        title=dict(
            text="🎯 Surface de Réparation - Position des Buts de Neymar",
            x=0.5,
            font=dict(size=20, color='white')
        ),
        xaxis=dict(
            range=[-3, penalty_width+3],
            showgrid=False,
            showticklabels=True,
            zeroline=False,
            fixedrange=True,
            title="Largeur du terrain (m)",
            title_font=dict(color='white'),
            tickfont=dict(color='white')
        ),
        yaxis=dict(
            range=[-3, penalty_depth+3],
            showgrid=False,
            showticklabels=True,
            zeroline=False,
            scaleanchor="x",
            scaleratio=1,
            fixedrange=True,
            title="Distance au but (m)",
            title_font=dict(color='white'),
            tickfont=dict(color='white')
        ),
        plot_bgcolor='rgba(34, 139, 34, 1)',
        paper_bgcolor='rgba(34, 139, 34, 1)',
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="rgba(0,0,0,0.2)",
            borderwidth=1,
            font=dict(color='black')
        ),
        height=600,
        margin=dict(l=50, r=50, t=80, b=50)
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
    st.markdown('<h1 class="main-header">⚽ Neymar Jr. - Surface de Réparation FC Barcelone</h1>', 
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
        st.markdown("### 🎯 Surface de Réparation")
        
        if not df_filtered.empty:
            # Créer la visualisation de la surface de réparation
            fig = create_penalty_area_visualization(df_filtered)
            
            # Afficher le graphique avec sélection
            selected_points = st.plotly_chart(
                fig, 
                use_container_width=True,
                key="penalty_area",
                on_select="rerun"
            )
            
            # Gérer la sélection de points
            if hasattr(st.session_state, 'penalty_area') and st.session_state.penalty_area:
                if 'selection' in st.session_state.penalty_area and st.session_state.penalty_area['selection']:
                    if 'points' in st.session_state.penalty_area['selection']:
                        selected_indices = [point['customdata'] for point in st.session_state.penalty_area['selection']['points']]
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
                st.info("🎯 Cliquez sur un but dans la surface pour voir la vidéo")
        else:
            st.info("🎯 Cliquez sur un but dans la surface pour voir la vidéo")
    
    # Légende des couleurs
    st.markdown("### 🎨 Légende")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("🔵 **Pied droit**")
    with col2:
        st.markdown("🟠 **Pied gauche**")
    with col3:
        st.markdown("🟢 **Tête**")
    
    st.markdown("*La taille des points représente la valeur xG (plus grand = plus probable de marquer)*")
    
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
