import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import os

# Configuration de la page
st.set_page_config(
    page_title="Neymar Jr. - Buts LaLiga",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour le design professionnel
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #FF4B4B;
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .sub-header {
        font-size: 1.5rem;
        color: #666666;
        text-align: center;
        margin-bottom: 2rem;
        font-style: italic;
    }
    .metric-container {
        background: linear-gradient(135deg, #f0f2f6 0%, #e8eaf0 100%);
        padding: 1.2rem;
        border-radius: 0.8rem;
        border-left: 5px solid #FF4B4B;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .video-container {
        background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        margin-top: 2rem;
        border: 2px solid #FF4B4B;
        box-shadow: 0 4px 8px rgba(255,75,75,0.2);
    }
    .stSelectbox > div > div > select {
        background-color: white;
        border-radius: 0.5rem;
    }
    .goal-info {
        background: rgba(255, 255, 255, 0.05);
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Charge les données des buts de Neymar"""
    try:
        # Essai de chargement depuis un fichier local
        if os.path.exists('Neymar_Buts_LaLiga.csv'):
            df = pd.read_csv('Neymar_Buts_LaLiga.csv', sep=";", encoding='cp1252')
        else:
            st.error("❌ Fichier 'Neymar_Buts_LaLiga.csv' non trouvé dans le répertoire courant.")
            return None
        
        # Nettoyage et transformation des données
        df_clean = df.copy()
        
        # Normalisation des coordonnées si nécessaire
        df_clean.loc[df_clean['X'] < 10, 'X'] = df_clean.loc[df_clean['X'] < 10, 'X'] * 120
        df_clean.loc[df_clean['Y'] < 10, 'Y'] = df_clean.loc[df_clean['Y'] < 10, 'Y'] * 80
        
        # Formatage de la saison
        df_clean['season'] = df_clean['season'].astype(str)
        season_mapping = {
            '2013': '2013-14',
            '2014': '2014-15', 
            '2015': '2015-16',
            '2016': '2016-17',
            '2017': '2016-17'
        }
        df_clean['season'] = df_clean['season'].map(season_mapping).fillna(df_clean['season'])
        
        # Mapping des situations en français
        situation_mapping = {
            'OpenPlay': 'Jeu ouvert',
            'Penalty': 'Penalty',
            'FreeKick': 'Coup franc',
            'Corner': 'Corner',
            'SetPiece': 'Coup de pied arrêté'
        }
        df_clean['situation'] = df_clean['situation'].map(situation_mapping).fillna(df_clean['situation'])
        
        # Mapping des types de tir en français
        shot_mapping = {
            'RightFoot': 'Pied droit',
            'LeftFoot': 'Pied gauche',
            'Head': 'Tête'
        }
        df_clean['shotType'] = df_clean['shotType'].map(shot_mapping).fillna(df_clean['shotType'])
        
        # Nettoyage des noms d'équipes
        df_clean['h_team'] = df_clean['h_team'].fillna('Barcelona')
        df_clean['a_team'] = df_clean['a_team'].fillna('Équipe inconnue')
        
        # Nettoyage des passeurs
        df_clean['player_assisted'] = df_clean['player_assisted'].fillna('')
        
        return df_clean
        
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement des données: {e}")
        return None

def create_pitch():
    """Crée le terrain de football avec Plotly"""
    fig = go.Figure()
    
    # Dimensions du terrain
    pitch_length = 120
    pitch_width = 80
    
    # Couleur du terrain avec dégradé
    fig.add_shape(
        type="rect",
        x0=0, y0=0, x1=pitch_length, y1=pitch_width,
        fillcolor="rgba(34, 139, 34, 0.8)",
        line=dict(color="white", width=3)
    )
    
    # Ligne médiane
    fig.add_shape(
        type="line",
        x0=pitch_length/2, y0=0, x1=pitch_length/2, y1=pitch_width,
        line=dict(color="white", width=3)
    )
    
    # Cercle central
    fig.add_shape(
        type="circle",
        xref="x", yref="y",
        x0=pitch_length/2-9.15, y0=pitch_width/2-9.15,
        x1=pitch_length/2+9.15, y1=pitch_width/2+9.15,
        line=dict(color="white", width=3),
        fillcolor="rgba(255,255,255,0.1)"
    )
    
    # Point central
    fig.add_trace(go.Scatter(
        x=[pitch_length/2], y=[pitch_width/2],
        mode='markers',
        marker=dict(color='white', size=8),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Surface de réparation droite (zone d'attaque de Neymar)
    penalty_area_width = 40.32
    penalty_area_length = 16.5
    penalty_y = (pitch_width - penalty_area_width) / 2
    
    fig.add_shape(
        type="rect",
        x0=pitch_length-penalty_area_length, y0=penalty_y,
        x1=pitch_length, y1=penalty_y+penalty_area_width,
        line=dict(color="white", width=3),
        fillcolor="rgba(255, 75, 75, 0.15)"
    )
    
    # Surface de but droite
    goal_area_width = 18.32
    goal_area_length = 5.5
    goal_y = (pitch_width - goal_area_width) / 2
    
    fig.add_shape(
        type="rect",
        x0=pitch_length-goal_area_length, y0=goal_y,
        x1=pitch_length, y1=goal_y+goal_area_width,
        line=dict(color="white", width=3),
        fillcolor="rgba(255, 75, 75, 0.25)"
    )
    
    # Buts
    goal_width = 7.32
    goal_y_pos = (pitch_width - goal_width) / 2
    
    # But droit (attaque)
    fig.add_shape(
        type="line",
        x0=pitch_length, y0=goal_y_pos,
        x1=pitch_length, y1=goal_y_pos+goal_width,
        line=dict(color="white", width=6)
    )
    
    # Point de penalty droit
    fig.add_trace(go.Scatter(
        x=[pitch_length-11], y=[pitch_width/2],
        mode='markers',
        marker=dict(color='white', size=10, symbol='circle'),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Arc de penalty droit
    theta = np.linspace(0.6, 2.54, 50)  # Approximation de l'arc
    arc_x = pitch_length - 11 + 9.15 * np.cos(theta)
    arc_y = pitch_width/2 + 9.15 * np.sin(theta)
    
    fig.add_trace(go.Scatter(
        x=arc_x, y=arc_y,
        mode='lines',
        line=dict(color='white', width=3),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Surface de réparation gauche
    fig.add_shape(
        type="rect",
        x0=0, y0=penalty_y,
        x1=penalty_area_length, y1=penalty_y+penalty_area_width,
        line=dict(color="white", width=3),
        fillcolor="rgba(255,255,255,0.05)"
    )
    
    # Surface de but gauche
    fig.add_shape(
        type="rect",
        x0=0, y0=goal_y,
        x1=goal_area_length, y1=goal_y+goal_area_width,
        line=dict(color="white", width=3)
    )
    
    # But gauche
    fig.add_shape(
        type="line",
        x0=0, y0=goal_y_pos,
        x1=0, y1=goal_y_pos+goal_width,
        line=dict(color="white", width=6)
    )
    
    # Point de penalty gauche
    fig.add_trace(go.Scatter(
        x=[11], y=[pitch_width/2],
        mode='markers',
        marker=dict(color='white', size=10),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    return fig

def display_goal_video(video_name, goal_info):
    """Affiche la vidéo du but sélectionné"""
    st.markdown(f'<div class="video-container">', unsafe_allow_html=True)
    
    # En-tête de la section vidéo
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 1rem;">
        <h2 style="color: #FF4B4B; margin: 0;">🎬 But #{goal_info['id']} - {goal_info['season']}</h2>
        <p style="color: #cccccc; font-size: 1.2rem; margin: 0.5rem 0;">
            {goal_info['h_team']} vs {goal_info['a_team']} | {goal_info['date']}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Construire le chemin complet vers la vidéo
        video_file = f"Neymar_LaLiga_Buts/{video_name}.mp4"
        
        # Vérifier si le fichier existe localement
        if os.path.exists(video_file):
            try:
                st.video(video_file)
                st.success("✅ Vidéo chargée avec succès")
            except Exception as e:
                st.error(f"❌ Erreur lors du chargement de la vidéo: {e}")
                st.info(f"📂 Fichier: {video_file}")
        else:
            st.warning("⚠️ Fichier vidéo non trouvé")
            st.info(f"📂 Chemin recherché: `{video_file}`")
            st.markdown("""
            **💡 Vérifiez que :**
            - Le dossier `Neymar_LaLiga_Buts/` existe
            - Le fichier vidéo est présent avec le bon nom
            - L'extension `.mp4` est correcte
            """)
        
        # Informations sur le match
        st.markdown('<div class="goal-info">', unsafe_allow_html=True)
        
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            st.markdown(f"""
            **⚽ Match**  
            {goal_info['h_team']} vs {goal_info['a_team']}
            
            **📅 Date**  
            {goal_info['date']}
            """)
        
        with col_b:
            st.markdown(f"""
            **🏟️ Terrain**  
            {'🏠 Domicile' if goal_info['h_a'] == 'h' else '✈️ Extérieur'}
            
            **🥅 Score final**  
            {goal_info['h_goals']} - {goal_info['a_goals']}
            """)
        
        with col_c:
            st.markdown(f"""
            **📂 Fichier**  
            `{video_name}.mp4`
            
            **📍 Chemin**  
            `{video_file}`
            """)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        
        # Métriques du but
        st.metric("⏱️ Minute", f"{goal_info['minute']}'", help="Minute du but")
        st.metric("🎯 xG (Expected Goals)", f"{goal_info['xG']:.3f}", 
                 help="Probabilité de marquer ce but")
        st.metric("🦶 Type de tir", goal_info['shotType'])
        st.metric("🎮 Situation", goal_info['situation'])
        
        if goal_info['player_assisted'] and goal_info['player_assisted'].strip():
            st.metric("🤝 Passeur décisif", goal_info['player_assisted'])
        
        # Calculs avancés
        distance_to_goal = ((120 - goal_info['X'])**2 + (40 - goal_info['Y'])**2)**0.5 * 0.9144
        st.metric("📏 Distance du but", f"{distance_to_goal:.1f}m")
        
        # Zone du terrain
        if goal_info['X'] > 103.5:
            zone = "🎯 Surface de réparation"
            zone_color = "#FF4B4B"
        elif goal_info['X'] > 90:
            zone = "⚡ Zone dangereuse"
            zone_color = "#FFA500"
        elif goal_info['X'] > 60:
            zone = "📊 Milieu offensif"
            zone_color = "#FFD700"
        else:
            zone = "🚀 Loin du but"
            zone_color = "#87CEEB"
        
        st.markdown(f"""
        <div style="background: {zone_color}20; padding: 0.8rem; border-radius: 0.5rem; 
                    border-left: 4px solid {zone_color}; margin: 1rem 0;">
            <strong style="color: {zone_color};">🗺️ Zone de tir</strong><br>
            <span style="font-size: 1.1rem;">{zone}</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    # En-tête de l'application
    st.markdown('<div class="main-header">⚽ Neymar Jr.</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Tous ses buts en LaLiga (2013-2017)</div>', unsafe_allow_html=True)
    
    # Chargement des données
    df = load_data()
    
    if df is None:
        st.stop()
    
    # Affichage des informations de chargement
    st.success(f"✅ Données chargées avec succès: **{len(df)} buts** de Neymar Jr.")
    
    # Affichage d'un échantillon de données
    with st.expander("🔍 Aperçu des données chargées", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🎯 Total buts", len(df))
            st.metric("🏆 Saisons", len(df['season'].unique()))
            
        with col2:
            st.metric("🥅 xG total", f"{df['xG'].sum():.1f}")
            st.metric("⚡ xG moyen", f"{df['xG'].mean():.3f}")
            
        with col3:
            st.metric("👥 Adversaires", len(df['a_team'].unique()))
            buts_surface = len(df[df['X'] > 103.5])
            st.metric("🎯 Buts en surface", f"{buts_surface} ({buts_surface/len(df)*100:.1f}%)")
        
        st.markdown("**📝 Échantillon des noms de vidéos:**")
        sample_videos = df['video_but'].head(8).tolist()
        for i, video in enumerate(sample_videos, 1):
            st.write(f"{i}. `{video}`")
    
    # Utilisation des données nettoyées
    df_goals = df.copy()
    
    # Sidebar avec filtres
    st.sidebar.markdown("## 🎯 Filtres de sélection")
    st.sidebar.markdown("---")
    
    # Filtre par saison
    seasons = sorted(df_goals['season'].unique())
    selected_seasons = st.sidebar.multiselect(
        "🏆 Sélectionner les saisons",
        seasons,
        default=seasons,
        help="Choisissez les saisons à afficher sur le terrain"
    )
    
    # Filtre par type de tir
    shot_types = sorted(df_goals['shotType'].unique())
    selected_shot_types = st.sidebar.multiselect(
        "🦶 Type de tir",
        shot_types,
        default=shot_types,
        help="Filtrer par le type de tir utilisé"
    )
    
    # Filtre par situation
    situations = sorted(df_goals['situation'].unique())
    selected_situations = st.sidebar.multiselect(
        "🎮 Situation de jeu",
        situations,
        default=situations,
        help="Filtrer par la situation dans laquelle le but a été marqué"
    )
    
    # Filtre par adversaire
    teams = sorted(df_goals['a_team'].unique())
    selected_teams = st.sidebar.multiselect(
        "👥 Équipes adverses",
        teams,
        default=teams,
        help="Sélectionner les équipes adverses"
    )
    
    # Filtre par xG
    min_xg, max_xg = st.sidebar.slider(
        "🎯 Probabilité xG",
        min_value=0.0,
        max_value=1.0,
        value=(0.0, 1.0),
        step=0.01,
        format="%.2f",
        help="Filtrer par la probabilité Expected Goals"
    )
    
    # Filtre par minute
    min_minute, max_minute = st.sidebar.slider(
        "⏱️ Minute du match",
        min_value=1,
        max_value=90,
        value=(1, 90),
        help="Filtrer par la minute du but"
    )
    
    # Application des filtres
    filtered_df = df_goals[
        (df_goals['season'].isin(selected_seasons)) &
        (df_goals['shotType'].isin(selected_shot_types)) &
        (df_goals['situation'].isin(selected_situations)) &
        (df_goals['a_team'].isin(selected_teams)) &
        (df_goals['xG'] >= min_xg) &
        (df_goals['xG'] <= max_xg) &
        (df_goals['minute'] >= min_minute) &
        (df_goals['minute'] <= max_minute)
    ]
    
    # Statistiques dans la sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("## 📊 Statistiques filtrées")
    
    if len(filtered_df) > 0:
        st.sidebar.metric("🎯 Buts sélectionnés", len(filtered_df))
        st.sidebar.metric("📈 xG Total", f"{filtered_df['xG'].sum():.1f}")
        st.sidebar.metric("⚡ xG Moyen", f"{filtered_df['xG'].mean():.3f}")
        avg_distance = (120 - filtered_df['X'].mean()) * 0.9144
        st.sidebar.metric("📏 Distance moyenne", f"{avg_distance:.1f}m")
        
        # Répartition par saison
        st.sidebar.markdown("### 📅 Répartition par saison")
        season_counts = filtered_df['season'].value_counts().sort_index()
        for season, count in season_counts.items():
            percentage = (count / len(filtered_df)) * 100
            st.sidebar.write(f"**{season}:** {count} buts ({percentage:.1f}%)")
    else:
        st.sidebar.warning("⚠️ Aucun but ne correspond aux filtres")
    
    # Layout principal
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.markdown("### 🏟️ Terrain - Cliquez sur un but pour voir la vidéo")
        
        # Création du terrain
        fig = create_pitch()
        
        # Ajout des buts sur le terrain
        if len(filtered_df) > 0:
            # Taille basée sur xG (plus visible)
            sizes = [max(15, 50 * row['xG']) for _, row in filtered_df.iterrows()]
            
            # Couleurs basées sur la saison
            season_colors = {
                '2013-14': '#FF6B6B',
                '2014-15': '#4ECDC4', 
                '2015-16': '#45B7D1',
                '2016-17': '#FFA07A'
            }
            
            colors = [season_colors.get(row['season'], '#FF4B4B') for _, row in filtered_df.iterrows()]
            
            # Texte de hover personnalisé
            hover_text = []
            for _, row in filtered_df.iterrows():
                text = f"<b>🎯 But #{row['id']}</b><br>"
                text += f"⏱️ Minute: {row['minute']}'<br>"
                text += f"🎯 xG: {row['xG']:.3f}<br>"
                text += f"🏆 Saison: {row['season']}<br>"
                text += f"🦶 Type: {row['shotType']}<br>"
                text += f"🎮 Situation: {row['situation']}<br>"
                text += f"👥 vs {row['a_team']}<br>"
                if row['player_assisted']:
                    text += f"🤝 Passeur: {row['player_assisted']}<br>"
                text += f"<i>🖱️ Cliquez pour voir la vidéo</i>"
                hover_text.append(text)
            
            # Scatter plot des buts
            fig.add_trace(go.Scatter(
                x=filtered_df['X'],
                y=filtered_df['Y'],
                mode='markers',
                marker=dict(
                    size=sizes,
                    color=colors,
                    opacity=0.8,
                    line=dict(width=2, color='white'),
                    symbol='circle'
                ),
                text=hover_text,
                hovertemplate='%{text}<extra></extra>',
                customdata=filtered_df.index,
                name="Buts de Neymar"
            ))
        
        # Configuration du layout
        fig.update_layout(
            plot_bgcolor='rgba(20, 20, 20, 1)',
            paper_bgcolor='rgba(20, 20, 20, 1)',
            xaxis=dict(
                range=[-5, 125],
                showgrid=False,
                showticklabels=False,
                zeroline=False
            ),
            yaxis=dict(
                range=[-5, 85],
                showgrid=False,
                showticklabels=False,
                zeroline=False,
                scaleanchor="x",
                scaleratio=1
            ),
            height=650,
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=False
        )
        
        # Affichage du terrain avec événements de sélection
        event = st.plotly_chart(fig, use_container_width=True, key="pitch", on_select="rerun")
    
    with col2:
        st.markdown("### 📊 Statistiques en temps réel")
        
        if len(filtered_df) > 0:
            # Métriques principales dans un container stylé
            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            
            total_goals = len(filtered_df)
            total_xg = filtered_df['xG'].sum()
            goals_in_box = len(filtered_df[filtered_df['X'] > 103.5])
            
            st.metric("🎯 Buts totaux", total_goals)
            st.metric("📈 xG Total", f"{total_xg:.1f}")
            st.metric("🥅 Buts en surface", f"{goals_in_box}")
            
            surface_pct = (goals_in_box / total_goals) * 100
            st.metric("📊 % en surface", f"{surface_pct:.1f}%")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Mini graphiques
            st.markdown("#### 📅 Distribution par saison")
            season_counts = filtered_df['season'].value_counts().sort_index()
            
            fig_season = px.bar(
                x=season_counts.index,
                y=season_counts.values,
                color=season_counts.values,
                color_continuous_scale='Reds',
                title=""
            )
            fig_season.update_layout(
                height=200,
                showlegend=False,
                xaxis_title="",
                yaxis_title="Buts",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=10),
                margin=dict(l=0, r=0, t=0, b=20)
            )
            st.plotly_chart(fig_season, use_container_width=True)
            
            # Distribution xG
            st.markdown("#### 🎯 Distribution xG")
            fig_xg = px.histogram(
                filtered_df,
                x='xG',
                nbins=8,
                color_discrete_sequence=['#FF4B4B'],
                title=""
            )
            fig_xg.update_layout(
                height=200,
                showlegend=False,
                xaxis_title="xG",
                yaxis_title="Freq.",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=10),
                margin=dict(l=0, r=0, t=0, b=20)
            )
            st.plotly_chart(fig_xg, use_container_width=True)
            
        else:
            st.info("ℹ️ Aucune donnée à afficher avec les filtres actuels")
    
    # Gestion des clics sur le terrain
    if event and event.selection and len(event.selection.points) > 0:
        selected_point = event.selection.points[0]
        if 'customdata' in selected_point:
            point_index = selected_point['customdata']
            st.session_state.selected_goal = point_index
    
    # Section vidéo (affichage conditionnel)
    if 'selected_goal' in st.session_state and st.session_state.selected_goal in filtered_df.index:
        goal_info = filtered_df.loc[st.session_state.selected_goal]
        display_goal_video(goal_info['video_but'], goal_info)
    
    # Tableau des buts filtrés
    st.markdown("---")
    st.markdown("### 📋 Liste complète des buts")
    
    if len(filtered_df) > 0:
        # Préparation des données pour l'affichage
        display_df = filtered_df[[
            'id', 'minute', 'season', 'shotType', 'situation', 
            'xG', 'player_assisted', 'a_team', 'video_but'
        ]].copy()
        
        display_df.columns = [
            '#', 'Min', 'Saison', 'Type tir', 'Situation', 
            'xG', 'Passeur', 'Adversaire', 'Vidéo'
        ]
        
        # Formatage de la colonne vidéo
        display_df['Vidéo'] = display_df['Vidéo'].apply(
            lambda x: (x[:40] + "...") if len(x) > 40 else x
        )
        
        # Formatage des valeurs xG
        display_df['xG'] = display_df['xG'].apply(lambda x: f"{x:.3f}")
        
        # Sélection d'un but dans le tableau
        selected_row = st.dataframe(
            display_df,
            use_container_width=True,
            height=400,
            on_select="rerun",
            selection_mode="single-row"
        )
        
        if selected_row.selection and len(selected_row.selection.rows) > 0:
            selected_index = selected_row.selection.rows[0]
            goal_index = filtered_df.iloc[selected_index].name
            st.session_state.selected_goal = goal_index
    else:
        st.info("ℹ️ Aucun but ne correspond aux critères sélectionnés.")
    
    # Instructions d'utilisation
    st.markdown("---")
    st.markdown("### 📖 Guide d'utilisation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🎯 Pour voir une vidéo de but :**
        1. 🖱️ **Cliquez sur un point rouge** sur le terrain
        2. 📋 **OU sélectionnez une ligne** dans le tableau
        3. 🎬 **La vidéo s'affichera** automatiquement
        
        **🎨 Légende des couleurs :**
        - 🔴 **2013-14** : Rouge
        - 🔵 **2014-15** : Bleu turquoise  
        - 🟡 **2015-16** : Bleu clair
        - 🟠 **2016-17** : Orange
        """)
    
    with col2:
        st.markdown("""
        **📁 Structure des fichiers requise :**
        ```
        votre_projet/
        ├── 📄 Neymar_Buts_LaLiga.csv
        ├── 📄 neymar_app.py
        └── 📁 Neymar_LaLiga_Buts/
            ├── vs Real Sociedad 24 Sept 2013.mp4
            ├── vs 1er But Celta Vigo 26 Mar 2014.mp4
            └── ... (autres vidéos)
        ```
        
        **🚀 Lancement :**
        ```bash
        streamlit run neymar_app.py
        ```
        """)
    
    # Analyse détaillée des données
    if len(filtered_df) > 0:
        st.markdown("---")
        st.markdown("### 📊 Analyse détaillée")
        
        # Tabs pour différentes analyses
        tab1, tab2, tab3, tab4 = st.tabs(["🎯 Zones de tir", "⏱️ Chronologie", "🤝 Passeurs", "🎮 Situations"])
        
        with tab1:
            st.markdown("#### 🗺️ Répartition par zones du terrain")
            
            # Calcul des zones
            zones_analysis = {
                'Surface de réparation (X > 103.5)': len(filtered_df[filtered_df['X'] > 103.5]),
                'Zone dangereuse (90 < X ≤ 103.5)': len(filtered_df[(filtered_df['X'] > 90) & (filtered_df['X'] <= 103.5)]),
                'Milieu offensif (60 < X ≤ 90)': len(filtered_df[(filtered_df['X'] > 60) & (filtered_df['X'] <= 90)]),
                'Loin du but (X ≤ 60)': len(filtered_df[filtered_df['X'] <= 60])
            }
            
            col1, col2, col3, col4 = st.columns(4)
            
            for i, (zone, count) in enumerate(zones_analysis.items()):
                percentage = (count / len(filtered_df)) * 100 if len(filtered_df) > 0 else 0
                
                with [col1, col2, col3, col4][i]:
                    st.metric(
                        zone.split('(')[0].strip(),
                        f"{count} buts",
                        f"{percentage:.1f}%"
                    )
            
            # Graphique en secteurs
            if sum(zones_analysis.values()) > 0:
                fig_zones = px.pie(
                    values=list(zones_analysis.values()),
                    names=[zone.split('(')[0].strip() for zone in zones_analysis.keys()],
                    title="Répartition des buts par zone",
                    color_discrete_sequence=['#FF4B4B', '#FFA500', '#FFD700', '#87CEEB']
                )
                fig_zones.update_layout(height=400)
                st.plotly_chart(fig_zones, use_container_width=True)
        
        with tab2:
            st.markdown("#### ⏱️ Distribution des buts par minute")
            
            # Grouper par tranches de 15 minutes
            filtered_df['minute_range'] = pd.cut(
                filtered_df['minute'], 
                bins=[0, 15, 30, 45, 60, 75, 90], 
                labels=['1-15', '16-30', '31-45', '46-60', '61-75', '76-90']
            )
            
            minute_counts = filtered_df['minute_range'].value_counts().sort_index()
            
            fig_minutes = px.bar(
                x=minute_counts.index.astype(str),
                y=minute_counts.values,
                title="Nombre de buts par tranche de 15 minutes",
                labels={'x': 'Minutes', 'y': 'Nombre de buts'},
                color=minute_counts.values,
                color_continuous_scale='Reds'
            )
            fig_minutes.update_layout(height=400)
            st.plotly_chart(fig_minutes, use_container_width=True)
            
            # Statistiques temporelles
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("⏰ But le plus précoce", f"{filtered_df['minute'].min()}'")
            with col2:
                st.metric("🕰️ But le plus tardif", f"{filtered_df['minute'].max()}'")
            with col3:
                st.metric("📊 Minute moyenne", f"{filtered_df['minute'].mean():.1f}'")
        
        with tab3:
            st.markdown("#### 🤝 Top des passeurs décisifs")
            
            # Analyse des passeurs (en excluant les valeurs vides)
            passeurs = filtered_df[filtered_df['player_assisted'].str.strip() != '']['player_assisted'].value_counts()
            
            if len(passeurs) > 0:
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    fig_passeurs = px.bar(
                        x=passeurs.values[:10],
                        y=passeurs.index[:10],
                        orientation='h',
                        title="Top 10 des passeurs décisifs",
                        labels={'x': 'Nombre de passes décisives', 'y': 'Joueur'},
                        color=passeurs.values[:10],
                        color_continuous_scale='Blues'
                    )
                    fig_passeurs.update_layout(height=400)
                    st.plotly_chart(fig_passeurs, use_container_width=True)
                
                with col2:
                    st.markdown("**🏆 Classement des passeurs :**")
                    for i, (passeur, count) in enumerate(passeurs.head(5).items(), 1):
                        st.write(f"{i}. **{passeur}** : {count} passes")
                    
                    total_assists = passeurs.sum()
                    buts_sans_passe = len(filtered_df) - len(filtered_df[filtered_df['player_assisted'].str.strip() != ''])
                    
                    st.metric("🎯 Total passes décisives", total_assists)
                    st.metric("🚀 Buts sans passe répertoriée", buts_sans_passe)
            else:
                st.info("Aucune donnée de passeur disponible pour cette sélection.")
        
        with tab4:
            st.markdown("#### 🎮 Analyse par situation de jeu")
            
            # Analyse des situations
            situations_count = filtered_df['situation'].value_counts()
            situations_xg = filtered_df.groupby('situation')['xG'].agg(['mean', 'sum']).round(3)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_situations = px.bar(
                    x=situations_count.values,
                    y=situations_count.index,
                    orientation='h',
                    title="Nombre de buts par situation",
                    color=situations_count.values,
                    color_continuous_scale='Greens'
                )
                fig_situations.update_layout(height=350)
                st.plotly_chart(fig_situations, use_container_width=True)
            
            with col2:
                st.markdown("**📊 Statistiques par situation :**")
                
                for situation in situations_count.index:
                    count = situations_count[situation]
                    avg_xg = situations_xg.loc[situation, 'mean']
                    total_xg = situations_xg.loc[situation, 'sum']
                    
                    st.markdown(f"""
                    **{situation}**
                    - 🎯 Buts : {count}
                    - 📈 xG moyen : {avg_xg:.3f}
                    - 📊 xG total : {total_xg:.3f}
                    """)
            
            # Efficacité par type de tir
            st.markdown("#### 🦶 Efficacité par type de tir")
            
            shot_analysis = filtered_df.groupby('shotType').agg({
                'id': 'count',
                'xG': ['mean', 'sum']
            }).round(3)
            
            shot_analysis.columns = ['Nombre', 'xG_moyen', 'xG_total']
            shot_analysis = shot_analysis.reset_index()
            
            fig_shots = px.scatter(
                shot_analysis,
                x='xG_moyen',
                y='Nombre',
                size='xG_total',
                color='shotType',
                title="Efficacité par type de tir (taille = xG total)",
                labels={
                    'xG_moyen': 'xG moyen par tir',
                    'Nombre': 'Nombre de buts'
                }
            )
            fig_shots.update_layout(height=400)
            st.plotly_chart(fig_shots, use_container_width=True)
    
    # Footer avec informations
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666666; padding: 2rem;">
        <p><strong>⚽ Application d'analyse des buts de Neymar Jr. en LaLiga</strong></p>
        <p>Données : 2013-2017 | Développé avec Streamlit et Plotly</p>
        <p><em>Cliquez sur un but pour voir sa vidéo !</em></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
