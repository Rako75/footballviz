import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime

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
    }
    .sub-header {
        font-size: 1.5rem;
        color: #666666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #FF4B4B;
    }
    .video-container {
        background-color: #1e1e1e;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-top: 1rem;
    }
    .stSelectbox > div > div > select {
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Charge les données des buts de Neymar"""
    try:
        # URL du fichier CSV sur GitHub
        csv_url = "https://raw.githubusercontent.com/your-username/Neymar_LaLiga_Buts/main/Neymar_Buts_LaLiga.csv"
        
        # Pour la démo, on va simuler les données basées sur le fichier fourni
        # En production, remplacer par: df = pd.read_csv(csv_url, sep=";", encoding='cp1252')
        
        # Simulation des données basée sur l'analyse du code Python
        np.random.seed(42)  # Pour la reproductibilité
        
        data = []
        seasons = ['2013-14', '2014-15', '2015-16', '2016-17']
        teams = ['Real Madrid', 'Atletico Madrid', 'Valencia', 'Sevilla', 'Athletic Bilbao', 
                'Real Sociedad', 'Villarreal', 'Espanyol', 'Getafe', 'Levante']
        
        for i in range(65):  # 65 buts selon le code
            season = np.random.choice(seasons)
            x_coord = np.random.uniform(60, 120)  # Plus de buts près du but
            if x_coord > 100:
                x_coord = np.random.uniform(100, 120)
            y_coord = np.random.uniform(10, 70)
            
            # xG basé sur la distance au but
            distance_to_goal = np.sqrt((120-x_coord)**2 + (40-y_coord)**2)
            xg = max(0.05, min(0.95, 1 - (distance_to_goal/50)))
            xg += np.random.uniform(-0.2, 0.2)
            xg = max(0.05, min(0.95, xg))
            
            data.append({
                'id': i+1,
                'minute': np.random.randint(1, 90),
                'X': x_coord,
                'Y': y_coord,
                'xG': round(xg, 3),
                'h_a': np.random.choice(['h', 'a']),
                'situation': np.random.choice(['open_play', 'penalty', 'free_kick', 'corner']),
                'season': season,
                'shotType': np.random.choice(['right_foot', 'left_foot', 'head']),
                'h_team': 'FC Barcelona',
                'a_team': np.random.choice(teams),
                'h_goals': np.random.randint(1, 5),
                'a_goals': np.random.randint(0, 3),
                'date': f"2{season.split('-')[0][-1]}{np.random.randint(10, 12)}-{np.random.randint(1, 28):02d}",
                'player_assisted': np.random.choice(['Messi', 'Suarez', 'Iniesta', 'Xavi', '', 'Alba']),
                'video_but': f"neymar_goal_{i+1:03d}.mp4"
            })
        
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {e}")
        return None

def create_pitch():
    """Crée le terrain de football avec Plotly"""
    fig = go.Figure()
    
    # Dimensions du terrain
    pitch_length = 120
    pitch_width = 80
    
    # Couleur du terrain
    fig.add_shape(
        type="rect",
        x0=0, y0=0, x1=pitch_length, y1=pitch_width,
        fillcolor="rgba(45, 90, 45, 0.8)",
        line=dict(color="white", width=2)
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
        xref="x", yref="y",
        x0=pitch_length/2-9.15, y0=pitch_width/2-9.15,
        x1=pitch_length/2+9.15, y1=pitch_width/2+9.15,
        line=dict(color="white", width=2),
    )
    
    # Surface de réparation droite
    penalty_area_width = 40.32
    penalty_area_length = 16.5
    penalty_y = (pitch_width - penalty_area_width) / 2
    
    fig.add_shape(
        type="rect",
        x0=pitch_length-penalty_area_length, y0=penalty_y,
        x1=pitch_length, y1=penalty_y+penalty_area_width,
        line=dict(color="white", width=2),
        fillcolor="rgba(255, 0, 0, 0.1)"
    )
    
    # Surface de but droite
    goal_area_width = 18.32
    goal_area_length = 5.5
    goal_y = (pitch_width - goal_area_width) / 2
    
    fig.add_shape(
        type="rect",
        x0=pitch_length-goal_area_length, y0=goal_y,
        x1=pitch_length, y1=goal_y+goal_area_width,
        line=dict(color="white", width=2)
    )
    
    # But droit
    goal_width = 7.32
    goal_y_pos = (pitch_width - goal_width) / 2
    fig.add_shape(
        type="line",
        x0=pitch_length, y0=goal_y_pos,
        x1=pitch_length, y1=goal_y_pos+goal_width,
        line=dict(color="white", width=4)
    )
    
    # Point de penalty
    fig.add_trace(go.Scatter(
        x=[pitch_length-11], y=[pitch_width/2],
        mode='markers',
        marker=dict(color='white', size=8),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Surface de réparation gauche
    fig.add_shape(
        type="rect",
        x0=0, y0=penalty_y,
        x1=penalty_area_length, y1=penalty_y+penalty_area_width,
        line=dict(color="white", width=2)
    )
    
    # Surface de but gauche
    fig.add_shape(
        type="rect",
        x0=0, y0=goal_y,
        x1=goal_area_length, y1=goal_y+goal_area_width,
        line=dict(color="white", width=2)
    )
    
    # But gauche
    fig.add_shape(
        type="line",
        x0=0, y0=goal_y_pos,
        x1=0, y1=goal_y_pos+goal_width,
        line=dict(color="white", width=4)
    )
    
    # Point de penalty gauche
    fig.add_trace(go.Scatter(
        x=[11], y=[pitch_width/2],
        mode='markers',
        marker=dict(color='white', size=8),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    return fig

def display_goal_video(video_name, goal_info):
    """Affiche la vidéo du but sélectionné"""
    st.markdown(f'<div class="video-container">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"### 🎬 Vidéo du but")
        
        # URL de la vidéo sur GitHub
        video_url = f"https://raw.githubusercontent.com/your-username/Neymar_LaLiga_Buts/main/{video_name}"
        
        # Pour la démo, on affiche une image placeholder
        st.info(f"📹 Vidéo: {video_name}")
        st.markdown(f"*En production, la vidéo serait chargée depuis: {video_url}*")
        
        # Placeholder pour la vidéo
        st.image("https://via.placeholder.com/640x360/FF4B4B/FFFFFF?text=Neymar+Goal+Video", 
                caption=f"But #{goal_info['id']} - {goal_info['season']}")
    
    with col2:
        st.markdown("### 📊 Détails du but")
        st.metric("Minute", f"{goal_info['minute']}'")
        st.metric("xG", f"{goal_info['xG']:.3f}")
        st.metric("Type de tir", goal_info['shotType'])
        st.metric("Situation", goal_info['situation'])
        if goal_info['player_assisted']:
            st.metric("Passeur", goal_info['player_assisted'])
    
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    # En-tête de l'application
    st.markdown('<div class="main-header">⚽ Neymar Jr.</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Tous ses buts en LaLiga (2013-2017)</div>', unsafe_allow_html=True)
    
    # Chargement des données
    df = load_data()
    
    if df is None:
        st.stop()
    
    # Normalisation des coordonnées (comme dans le code original)
    df_goals = df.copy()
    df_goals.loc[df_goals['X'] < 10, 'X'] = df_goals.loc[df_goals['X'] < 10, 'X'] * 120
    df_goals.loc[df_goals['Y'] < 10, 'Y'] = df_goals.loc[df_goals['Y'] < 10, 'Y'] * 80
    
    # Sidebar avec filtres
    st.sidebar.markdown("## 🎯 Filtres de sélection")
    
    # Filtre par saison
    seasons = sorted(df_goals['season'].unique())
    selected_seasons = st.sidebar.multiselect(
        "Sélectionner les saisons",
        seasons,
        default=seasons,
        help="Choisissez les saisons à afficher"
    )
    
    # Filtre par type de tir
    shot_types = sorted(df_goals['shotType'].unique())
    selected_shot_types = st.sidebar.multiselect(
        "Type de tir",
        shot_types,
        default=shot_types
    )
    
    # Filtre par situation
    situations = sorted(df_goals['situation'].unique())
    selected_situations = st.sidebar.multiselect(
        "Situation de jeu",
        situations,
        default=situations
    )
    
    # Filtre par xG
    min_xg, max_xg = st.sidebar.slider(
        "Probabilité xG",
        min_value=float(df_goals['xG'].min()),
        max_value=float(df_goals['xG'].max()),
        value=(float(df_goals['xG'].min()), float(df_goals['xG'].max())),
        step=0.01,
        format="%.3f"
    )
    
    # Application des filtres
    filtered_df = df_goals[
        (df_goals['season'].isin(selected_seasons)) &
        (df_goals['shotType'].isin(selected_shot_types)) &
        (df_goals['situation'].isin(selected_situations)) &
        (df_goals['xG'] >= min_xg) &
        (df_goals['xG'] <= max_xg)
    ]
    
    # Statistiques dans la sidebar
    st.sidebar.markdown("## 📈 Statistiques")
    st.sidebar.metric("Buts sélectionnés", len(filtered_df))
    if len(filtered_df) > 0:
        st.sidebar.metric("xG Total", f"{filtered_df['xG'].sum():.1f}")
        st.sidebar.metric("xG Moyen", f"{filtered_df['xG'].mean():.3f}")
        st.sidebar.metric("Distance moy.", f"{(120 - filtered_df['X'].mean()) * 0.9144:.1f}m")
    
    # Layout principal
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 🏟️ Terrain - Cliquez sur un but pour voir la vidéo")
        
        # Création du terrain
        fig = create_pitch()
        
        # Ajout des buts sur le terrain
        if len(filtered_df) > 0:
            # Taille basée sur xG
            sizes = [max(10, 30 * row['xG']) for _, row in filtered_df.iterrows()]
            
            # Couleurs basées sur la saison
            colors = []
            season_colors = {
                '2013-14': '#FF6B6B',
                '2014-15': '#4ECDC4', 
                '2015-16': '#45B7D1',
                '2016-17': '#FFA07A'
            }
            
            for _, row in filtered_df.iterrows():
                colors.append(season_colors.get(row['season'], '#FF4B4B'))
            
            # Texte de hover personnalisé
            hover_text = []
            for _, row in filtered_df.iterrows():
                text = f"<b>But #{row['id']}</b><br>"
                text += f"Minute: {row['minute']}'<br>"
                text += f"xG: {row['xG']:.3f}<br>"
                text += f"Saison: {row['season']}<br>"
                text += f"Type: {row['shotType']}<br>"
                text += f"Situation: {row['situation']}<br>"
                if row['player_assisted']:
                    text += f"Passeur: {row['player_assisted']}<br>"
                text += f"<i>Cliquez pour voir la vidéo</i>"
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
                    line=dict(width=2, color='white')
                ),
                text=hover_text,
                hovertemplate='%{text}<extra></extra>',
                customdata=filtered_df.index,
                name="Buts"
            ))
        
        # Configuration du layout
        fig.update_layout(
            plot_bgcolor='rgba(12, 13, 14, 1)',
            paper_bgcolor='rgba(12, 13, 14, 1)',
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
            height=600,
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=False
        )
        
        # Affichage du terrain avec gestion des clics
        clicked_point = st.plotly_chart(fig, use_container_width=True, key="pitch")
    
    with col2:
        st.markdown("### 📊 Statistiques détaillées")
        
        if len(filtered_df) > 0:
            # Métriques principales
            total_goals = len(filtered_df)
            total_xg = filtered_df['xG'].sum()
            goals_in_box = len(filtered_df[filtered_df['X'] > 103.5])
            
            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            st.metric("🎯 Buts totaux", total_goals)
            st.metric("📈 xG Total", f"{total_xg:.1f}")
            st.metric("🥅 Buts surface", f"{goals_in_box} ({goals_in_box/total_goals*100:.1f}%)")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Graphiques de distribution
            st.markdown("#### Distribution par saison")
            season_counts = filtered_df['season'].value_counts().sort_index()
            fig_season = px.bar(
                x=season_counts.index,
                y=season_counts.values,
                color=season_counts.values,
                color_continuous_scale='Reds'
            )
            fig_season.update_layout(
                height=200,
                showlegend=False,
                xaxis_title="",
                yaxis_title="Buts",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_season, use_container_width=True)
            
            # Distribution xG
            st.markdown("#### Distribution xG")
            fig_xg = px.histogram(
                filtered_df,
                x='xG',
                nbins=10,
                color_discrete_sequence=['#FF4B4B']
            )
            fig_xg.update_layout(
                height=200,
                showlegend=False,
                xaxis_title="xG",
                yaxis_title="Fréquence",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_xg, use_container_width=True)
    
    # Section vidéo (affichage conditionnel)
    if 'selected_goal' in st.session_state:
        goal_info = filtered_df.iloc[st.session_state.selected_goal]
        display_goal_video(goal_info['video_but'], goal_info)
    
    # Gestion des clics sur le terrain
    if clicked_point and clicked_point.get('points'):
        point_index = clicked_point['points'][0].get('customdata')
        if point_index is not None:
            st.session_state.selected_goal = point_index
            st.rerun()
    
    # Tableau des buts filtrés
    st.markdown("### 📋 Liste des buts")
    if len(filtered_df) > 0:
        display_df = filtered_df[['id', 'minute', 'season', 'shotType', 'situation', 'xG', 'player_assisted']].copy()
        display_df.columns = ['#', 'Min', 'Saison', 'Type tir', 'Situation', 'xG', 'Passeur']
        
        # Sélection d'un but dans le tableau
        selected_row = st.dataframe(
            display_df,
            use_container_width=True,
            height=300,
            on_select="rerun",
            selection_mode="single-row"
        )
        
        if len(selected_row.selection.rows) > 0:
            selected_index = selected_row.selection.rows[0]
            st.session_state.selected_goal = filtered_df.iloc[selected_index].name
            st.rerun()
    else:
        st.info("Aucun but ne correspond aux critères sélectionnés.")

if __name__ == "__main__":
    main()
