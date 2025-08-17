import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, date
import random

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
    .goal-details {
        background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        margin-top: 2rem;
        border: 2px solid #FF4B4B;
        box-shadow: 0 4px 8px rgba(255,75,75,0.2);
        color: white;
    }
    .goal-info {
        background: rgba(255, 255, 255, 0.05);
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 0.8rem;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def generate_neymar_goals_data():
    """Génère les données complètes des buts de Neymar en LaLiga"""
    
    # Équipes de LaLiga 2013-2017
    teams = [
        'Atletico Madrid', 'Athletic Bilbao', 'Celta Vigo', 'Deportivo La Coruna',
        'Espanyol', 'Getafe', 'Granada', 'Las Palmas', 'Levante', 'Malaga',
        'Real Madrid', 'Real Sociedad', 'Sevilla', 'Valencia', 'Villarreal',
        'Osasuna', 'Rayo Vallecano', 'Real Betis', 'Alaves', 'Eibar',
        'Leganes', 'Sporting Gijon'
    ]
    
    # Types de tir
    shot_types = ['Pied droit', 'Pied gauche', 'Tête']
    situations = ['Jeu ouvert', 'Penalty', 'Coup franc', 'Corner', 'Coup de pied arrêté']
    
    # Passeurs possibles (coéquipiers de Neymar au Barça)
    assisters = [
        'Lionel Messi', 'Luis Suarez', 'Andres Iniesta', 'Xavi Hernandez',
        'Ivan Rakitic', 'Sergio Busquets', 'Jordi Alba', 'Dani Alves',
        'Pedro Rodriguez', 'Rafinha', 'Sergi Roberto', 'Marc Bartra',
        'Gerard Pique', '', '', ''  # Quelques valeurs vides pour les buts sans passe
    ]
    
    goals_data = []
    goal_id = 1
    
    # Génération des buts par saison
    seasons_goals = {
        '2013-14': 9,   # Première demi-saison
        '2014-15': 10,  # Saison complète
        '2015-16': 11,  # Bonne saison
        '2016-17': 13   # Dernière saison, meilleure
    }
    
    for season, num_goals in seasons_goals.items():
        for i in range(num_goals):
            # Génération des coordonnées réalistes pour les buts
            # Zone de tir probable (surface et près de la surface)
            if random.random() < 0.6:  # 60% des buts dans la surface
                x = random.uniform(104, 120)
                y = random.uniform(25, 55)
            elif random.random() < 0.8:  # 20% près de la surface
                x = random.uniform(95, 104)
                y = random.uniform(20, 60)
            else:  # 20% plus loin
                x = random.uniform(80, 95)
                y = random.uniform(15, 65)
            
            # Calcul de xG basé sur la position
            distance_to_goal = ((120 - x)**2 + (40 - y)**2)**0.5
            angle = np.arctan2(7.32/2, 120 - x)  # Angle de tir
            
            # xG basé sur distance et angle (simplifié)
            base_xg = max(0.02, 1.2 - (distance_to_goal / 30))
            angle_factor = min(1, angle / 0.5)
            xg = min(0.99, base_xg * angle_factor * random.uniform(0.8, 1.2))
            
            # Génération d'une date aléatoire dans la saison
            if season == '2013-14':
                start_date = date(2014, 1, 1)
                end_date = date(2014, 5, 31)
            elif season == '2014-15':
                start_date = date(2014, 8, 1)
                end_date = date(2015, 5, 31)
            elif season == '2015-16':
                start_date = date(2015, 8, 1)
                end_date = date(2016, 5, 31)
            else:  # 2016-17
                start_date = date(2016, 8, 1)
                end_date = date(2017, 5, 31)
            
            random_date = start_date + (end_date - start_date) * random.random()
            
            goal_data = {
                'id': goal_id,
                'season': season,
                'date': random_date.strftime('%Y-%m-%d'),
                'minute': random.randint(1, 90),
                'X': round(x, 1),
                'Y': round(y, 1),
                'xG': round(xg, 3),
                'shotType': random.choice(shot_types),
                'situation': random.choice(situations),
                'opponent': random.choice(teams),
                'h_a': random.choice(['h', 'a']),
                'h_goals': random.randint(1, 5),
                'a_goals': random.randint(0, 4),
                'h_team': 'Barcelona',
                'a_team': random.choice(teams),
                'player_assisted': random.choice(assisters),
                'video_but': f'neymar_goal_{goal_id:03d}'
            }
            
            goals_data.append(goal_data)
            goal_id += 1
    
    df = pd.DataFrame(goals_data)
    
    # Post-traitement pour corriger les équipes
    for idx, row in df.iterrows():
        if row['h_a'] == 'h':  # Match à domicile
            df.loc[idx, 'opponent'] = row['a_team']
        else:  # Match à l'extérieur
            df.loc[idx, 'opponent'] = row['h_team']
            df.loc[idx, 'h_team'] = row['opponent']
            df.loc[idx, 'a_team'] = 'Barcelona'
    
    return df

def create_football_pitch():
    """Crée un terrain de football professionnel avec tous les détails"""
    fig = go.Figure()
    
    # Dimensions FIFA (en mètres, converties en unités terrain)
    pitch_length = 120  # 120 mètres
    pitch_width = 80    # 80 mètres
    
    # Couleur de fond du terrain - vert professionnel
    fig.add_shape(
        type="rect",
        x0=0, y0=0, x1=pitch_length, y1=pitch_width,
        fillcolor="rgba(34, 139, 34, 1)",  # Vert terrain professionnel
        line=dict(color="white", width=4)
    )
    
    # Ligne de touche complète
    fig.add_shape(
        type="rect",
        x0=0, y0=0, x1=pitch_length, y1=pitch_width,
        line=dict(color="white", width=4),
        fillcolor="rgba(0,0,0,0)"
    )
    
    # Ligne médiane
    fig.add_shape(
        type="line",
        x0=pitch_length/2, y0=0, x1=pitch_length/2, y1=pitch_width,
        line=dict(color="white", width=4)
    )
    
    # Cercle central (rayon 9.15m)
    center_x, center_y = pitch_length/2, pitch_width/2
    fig.add_shape(
        type="circle",
        xref="x", yref="y",
        x0=center_x-9.15, y0=center_y-9.15,
        x1=center_x+9.15, y1=center_y+9.15,
        line=dict(color="white", width=4),
        fillcolor="rgba(0,0,0,0)"
    )
    
    # Point central
    fig.add_trace(go.Scatter(
        x=[center_x], y=[center_y],
        mode='markers',
        marker=dict(color='white', size=15),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # === CÔTÉ DROIT (Zone d'attaque de Neymar) ===
    
    # Surface de réparation droite (16.5m x 40.32m)
    penalty_length = 16.5
    penalty_width = 40.32
    penalty_y = (pitch_width - penalty_width) / 2
    
    fig.add_shape(
        type="rect",
        x0=pitch_length-penalty_length, y0=penalty_y,
        x1=pitch_length, y1=penalty_y+penalty_width,
        line=dict(color="white", width=4),
        fillcolor="rgba(0,0,0,0)"
    )
    
    # Surface de but droite (5.5m x 18.32m)
    goal_area_length = 5.5
    goal_area_width = 18.32
    goal_area_y = (pitch_width - goal_area_width) / 2
    
    fig.add_shape(
        type="rect",
        x0=pitch_length-goal_area_length, y0=goal_area_y,
        x1=pitch_length, y1=goal_area_y+goal_area_width,
        line=dict(color="white", width=4),
        fillcolor="rgba(0,0,0,0)"
    )
    
    # Point de penalty droit (11m du but)
    penalty_spot_x = pitch_length - 11
    fig.add_trace(go.Scatter(
        x=[penalty_spot_x], y=[center_y],
        mode='markers',
        marker=dict(color='white', size=15),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Arc de penalty droit
    theta = np.linspace(np.pi/3, 2*np.pi/3, 30)
    arc_radius = 9.15
    arc_x = penalty_spot_x + arc_radius * np.cos(theta)
    arc_y = center_y + arc_radius * np.sin(theta)
    
    # Filtrer les points en dehors de la surface
    valid_points = arc_x >= (pitch_length - penalty_length)
    arc_x_filtered = arc_x[valid_points]
    arc_y_filtered = arc_y[valid_points]
    
    fig.add_trace(go.Scatter(
        x=arc_x_filtered, y=arc_y_filtered,
        mode='lines',
        line=dict(color='white', width=4),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # But droit (7.32m de largeur)
    goal_width = 7.32
    goal_y1 = center_y - goal_width/2
    goal_y2 = center_y + goal_width/2
    
    fig.add_shape(
        type="line",
        x0=pitch_length, y0=goal_y1,
        x1=pitch_length, y1=goal_y2,
        line=dict(color="white", width=8)
    )
    
    # Poteaux de but droits
    fig.add_trace(go.Scatter(
        x=[pitch_length, pitch_length],
        y=[goal_y1, goal_y2],
        mode='markers',
        marker=dict(color='white', size=20, symbol='square'),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # === CÔTÉ GAUCHE (Zone défensive) ===
    
    # Surface de réparation gauche
    fig.add_shape(
        type="rect",
        x0=0, y0=penalty_y,
        x1=penalty_length, y1=penalty_y+penalty_width,
        line=dict(color="white", width=4),
        fillcolor="rgba(0,0,0,0)"
    )
    
    # Surface de but gauche
    fig.add_shape(
        type="rect",
        x0=0, y0=goal_area_y,
        x1=goal_area_length, y1=goal_area_y+goal_area_width,
        line=dict(color="white", width=4),
        fillcolor="rgba(0,0,0,0)"
    )
    
    # Point de penalty gauche
    fig.add_trace(go.Scatter(
        x=[11], y=[center_y],
        mode='markers',
        marker=dict(color='white', size=15),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Arc de penalty gauche
    theta_left = np.linspace(np.pi/3, 2*np.pi/3, 30)
    arc_x_left = 11 - arc_radius * np.cos(theta_left)
    arc_y_left = center_y + arc_radius * np.sin(theta_left)
    
    # Filtrer les points en dehors de la surface
    valid_points_left = arc_x_left <= penalty_length
    arc_x_left_filtered = arc_x_left[valid_points_left]
    arc_y_left_filtered = arc_y_left[valid_points_left]
    
    fig.add_trace(go.Scatter(
        x=arc_x_left_filtered, y=arc_y_left_filtered,
        mode='lines',
        line=dict(color='white', width=4),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # But gauche
    fig.add_shape(
        type="line",
        x0=0, y0=goal_y1,
        x1=0, y1=goal_y2,
        line=dict(color="white", width=8)
    )
    
    # Poteaux de but gauches
    fig.add_trace(go.Scatter(
        x=[0, 0],
        y=[goal_y1, goal_y2],
        mode='markers',
        marker=dict(color='white', size=20, symbol='square'),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Coins du terrain (arcs de cercle dans les coins)
    corner_radius = 1
    
    # Coin en bas à gauche
    theta_corner = np.linspace(0, np.pi/2, 20)
    corner_x = corner_radius * np.cos(theta_corner)
    corner_y = corner_radius * np.sin(theta_corner)
    
    fig.add_trace(go.Scatter(
        x=corner_x, y=corner_y,
        mode='lines',
        line=dict(color='white', width=3),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Coin en haut à gauche
    fig.add_trace(go.Scatter(
        x=corner_x, y=pitch_width - corner_y,
        mode='lines',
        line=dict(color='white', width=3),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Coin en bas à droite
    fig.add_trace(go.Scatter(
        x=pitch_length - corner_x, y=corner_y,
        mode='lines',
        line=dict(color='white', width=3),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Coin en haut à droite
    fig.add_trace(go.Scatter(
        x=pitch_length - corner_x, y=pitch_width - corner_y,
        mode='lines',
        line=dict(color='white', width=3),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    return fig

def calculate_goal_stats(row):
    """Calcule les statistiques avancées d'un but"""
    # Distance au but
    distance = ((120 - row['X'])**2 + (40 - row['Y'])**2)**0.5
    
    # Zone du terrain
    if row['X'] > 103.5:
        zone = "🎯 Surface de réparation"
        zone_color = "#FF1744"
    elif row['X'] > 94:
        zone = "⚡ Entrée de surface"
        zone_color = "#FF5722"
    elif row['X'] > 80:
        zone = "📊 Milieu offensif"
        zone_color = "#FF9800"
    elif row['X'] > 60:
        zone = "🏃 Centre du terrain"
        zone_color = "#FFC107"
    else:
        zone = "🚀 Terrain défensif"
        zone_color = "#4CAF50"
    
    # Angle de tir
    goal_center_y = 40
    angle = np.arctan2(7.32/2, abs(120 - row['X'])) * 180 / np.pi
    
    # Difficulté du but
    if row['xG'] > 0.5:
        difficulty = "🟢 Facile"
    elif row['xG'] > 0.2:
        difficulty = "🟡 Moyen"
    elif row['xG'] > 0.1:
        difficulty = "🟠 Difficile"
    else:
        difficulty = "🔴 Exceptionnel"
    
    return {
        'distance': distance,
        'zone': zone,
        'zone_color': zone_color,
        'angle': angle,
        'difficulty': difficulty
    }

def display_goal_details(goal_info):
    """Affiche les détails complets d'un but sélectionné"""
    st.markdown('<div class="goal-details">', unsafe_allow_html=True)
    
    # En-tête
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 1.5rem;">
        <h2 style="color: #FF4B4B; margin: 0; font-size: 2.5rem;">
            ⚽ But #{goal_info['id']} - Saison {goal_info['season']}
        </h2>
        <p style="color: #cccccc; font-size: 1.3rem; margin: 0.5rem 0;">
            FC Barcelona vs {goal_info['opponent']}
        </p>
        <p style="color: #aaaaaa; font-size: 1.1rem;">
            📅 {goal_info['date']} | ⏱️ {goal_info['minute']}ème minute
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Statistiques avancées
    stats = calculate_goal_stats(goal_info)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="stats-card">
            <h3 style="margin: 0; color: white;">🎯 Précision</h3>
            <p style="font-size: 1.5rem; margin: 0.5rem 0;">xG: {goal_info['xG']:.3f}</p>
            <p style="margin: 0;">{stats['difficulty']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stats-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
            <h3 style="margin: 0; color: white;">📏 Distance</h3>
            <p style="font-size: 1.5rem; margin: 0.5rem 0;">{stats['distance']:.1f}m</p>
            <p style="margin: 0;">Angle: {stats['angle']:.1f}°</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stats-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <h3 style="margin: 0; color: white;">🗺️ Position</h3>
            <p style="font-size: 1.2rem; margin: 0.5rem 0;">{stats['zone']}</p>
            <p style="margin: 0;">X: {goal_info['X']}m, Y: {goal_info['Y']}m</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Détails du match et du but
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown(f"""
        <div class="goal-info">
            <h4 style="color: #FF4B4B; margin-top: 0;">⚽ Détails du but</h4>
            <p><strong>🦶 Type de tir:</strong> {goal_info['shotType']}</p>
            <p><strong>🎮 Situation:</strong> {goal_info['situation']}</p>
            {f"<p><strong>🤝 Passeur:</strong> {goal_info['player_assisted']}</p>" if goal_info['player_assisted'] else ""}
            <p><strong>🏟️ Terrain:</strong> {'🏠 Camp Nou (Domicile)' if goal_info['h_a'] == 'h' else '✈️ Extérieur'}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_b:
        st.markdown(f"""
        <div class="goal-info">
            <h4 style="color: #FF4B4B; margin-top: 0;">🏆 Informations du match</h4>
            <p><strong>🥅 Score final:</strong> {goal_info['h_goals']} - {goal_info['a_goals']}</p>
            <p><strong>👥 Adversaire:</strong> {goal_info['opponent']}</p>
            <p><strong>📊 Impact xG:</strong> {goal_info['xG']:.1%} de chance de but</p>
            <p><strong>🎬 Vidéo:</strong> {goal_info['video_but']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def create_statistics_dashboard(df):
    """Crée un tableau de bord avec les statistiques complètes"""
    
    st.markdown("### 📊 Tableau de bord statistiques")
    
    # Métriques principales
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("🎯 Total buts", len(df))
    with col2:
        st.metric("📈 xG Total", f"{df['xG'].sum():.1f}")
    with col3:
        st.metric("⚡ xG Moyen", f"{df['xG'].mean():.3f}")
    with col4:
        goals_in_box = len(df[df['X'] > 103.5])
        st.metric("🥅 Buts en surface", goals_in_box)
    with col5:
        st.metric("🚀 But le plus loin", f"{((120 - df['X'].min())**2 + (40 - df['Y'].mean())**2)**0.5:.1f}m")
    
    # Graphiques de distribution
    col_graph1, col_graph2 = st.columns(2)
    
    with col_graph1:
        # Distribution par saison
        season_counts = df['season'].value_counts().sort_index()
        fig_seasons = go.Figure(data=[
            go.Bar(x=season_counts.index, y=season_counts.values,
                   marker_color='#FF4B4B', text=season_counts.values,
                   textposition='auto')
        ])
        fig_seasons.update_layout(
            title="Buts par saison", 
            xaxis_title="Saison", 
            yaxis_title="Nombre de buts",
            height=400
        )
        st.plotly_chart(fig_seasons, use_container_width=True)
    
    with col_graph2:
        # Distribution par type de tir
        shot_counts = df['shotType'].value_counts()
        fig_shots = go.Figure(data=[
            go.Pie(labels=shot_counts.index, values=shot_counts.values,
                   marker_colors=['#FF4B4B', '#FF7F7F', '#FFB3B3'])
        ])
        fig_shots.update_layout(title="Répartition par type de tir", height=400)
        st.plotly_chart(fig_shots, use_container_width=True)

def main():
    # En-tête principal
    st.markdown('<div class="main-header">⚽ Neymar Jr. - Statistiques LaLiga</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Analyse complète de tous ses buts (2013-2017)</div>', unsafe_allow_html=True)
    
    # Chargement des données
    df = generate_neymar_goals_data()
    
    # Message de succès avec informations
    st.success(f"✅ **{len(df)} buts** de Neymar Jr. analysés sur **4 saisons** en LaLiga")
    
    # Sidebar avec filtres
    st.sidebar.markdown("## 🎯 Filtres d'analyse")
    st.sidebar.markdown("---")
    
    # Filtres
    seasons = sorted(df['season'].unique())
    selected_seasons = st.sidebar.multiselect(
        "🏆 Saisons", seasons, default=seasons
    )
    
    shot_types = sorted(df['shotType'].unique())
    selected_shot_types = st.sidebar.multiselect(
        "🦶 Type de tir", shot_types, default=shot_types
    )
    
    situations = sorted(df['situation'].unique())
    selected_situations = st.sidebar.multiselect(
        "🎮 Situation de jeu", situations, default=situations
    )
    
    teams = sorted(df['opponent'].unique())
    selected_teams = st.sidebar.multiselect(
        "👥 Adversaires", teams, default=teams
    )
    
    # Slider pour xG
    min_xg, max_xg = st.sidebar.slider(
        "🎯 Expected Goals (xG)",
        min_value=0.0, max_value=1.0,
        value=(0.0, 1.0), step=0.01
    )
    
    # Application des filtres
    filtered_df = df[
        (df['season'].isin(selected_seasons)) &
        (df['shotType'].isin(selected_shot_types)) &
        (df['situation'].isin(selected_situations)) &
        (df['opponent'].isin(selected_teams)) &
        (df['xG'] >= min_xg) &
        (df['xG'] <= max_xg)
    ]
    
    # Statistiques filtrées dans la sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("## 📈 Résultats du filtre")
    
    if len(filtered_df) > 0:
        st.sidebar.metric("🎯 Buts filtrés", len(filtered_df))
        st.sidebar.metric("📊 xG Total", f"{filtered_df['xG'].sum():.2f}")
        st.sidebar.metric("⚡ xG Moyen", f"{filtered_df['xG'].mean():.3f}")
        
        # Meilleur but (xG le plus faible)
        best_goal = filtered_df.loc[filtered_df['xG'].idxmin()]
        st.sidebar.metric("🌟 But exceptionnel", f"#{best_goal['id']} (xG: {best_goal['xG']:.3f})")
    else:
        st.sidebar.warning("⚠️ Aucun but correspondant")
    
    # === TERRAIN PRINCIPAL ===
    st.markdown("---")
    st.markdown("### 🏟️ Terrain - Visualisation des buts")
    st.markdown("*Cliquez sur un point pour voir les détails du but*")
    
    # Création du terrain
    fig = create_football_pitch()
    
    # Ajout des buts sur le terrain
    if len(filtered_df) > 0:
        # Taille des points basée sur xG
        sizes = [max(15, 60 * row['xG']) for _, row in filtered_df.iterrows()]
        
        # Couleurs par saison
        season_colors = {
            '2013-14': '#FF1744',  # Rouge
            '2014-15': '#4CAF50',  # Vert
            '2015-16': '#2196F3',  # Bleu
            '2016-17': '#FF9800'   # Orange
        }
        
        colors = [season_colors.get(row['season'], '#FF1744') for _, row in filtered_df.iterrows()]
        
        # Texte de survol détaillé
        hover_texts = []
        for _, row in filtered_df.iterrows():
            stats = calculate_goal_stats(row)
            text = f"<b>⚽ But #{row['id']} - {row['season']}</b><br>"
            text += f"<br><b>📍 Match</b><br>"
            text += f"Barcelona vs {row['opponent']}<br>"
            text += f"📅 {row['date']} | ⏱️ {row['minute']}'<br>"
            text += f"🏟️ {'Domicile' if row['h_a'] == 'h' else 'Extérieur'}<br>"
            text += f"<br><b>🎯 Caractéristiques</b><br>"
            text += f"xG: {row['xG']:.3f} ({stats['difficulty']})<br>"
            text += f"🦶 {row['shotType']}<br>"
            text += f"🎮 {row['situation']}<br>"
            if row['player_assisted']:
                text += f"🤝 Passé par {row['player_assisted']}<br>"
            text += f"<br><b>📊 Position</b><br>"
            text += f"📏 Distance: {stats['distance']:.1f}m<br>"
            text += f"📐 Angle: {stats['angle']:.1f}°<br>"
            text += f"🗺️ {stats['zone']}<br>"
            text += f"<br><i>🖱️ Cliquez pour plus de détails</i>"
            hover_texts.append(text)
        
        # Ajout des points sur le terrain
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
            text=hover_texts,
            hovertemplate='%{text}<extra></extra>',
            customdata=filtered_df.index,
            name="Buts de Neymar",
            showlegend=False
        ))
        
        # Légende des saisons
        for season, color in season_colors.items():
            if season in selected_seasons:
                season_goals = len(filtered_df[filtered_df['season'] == season])
                fig.add_trace(go.Scatter(
                    x=[None], y=[None],
                    mode='markers',
                    marker=dict(size=15, color=color),
                    name=f"{season} ({season_goals} buts)",
                    showlegend=True
                ))
    
    # Configuration du terrain
    fig.update_layout(
        plot_bgcolor='rgba(0, 0, 0, 1)',
        paper_bgcolor='rgba(240, 242, 246, 1)',
        xaxis=dict(
            range=[-5, 125],
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            fixedrange=True
        ),
        yaxis=dict(
            range=[-5, 85],
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            scaleanchor="x",
            scaleratio=1,
            fixedrange=True
        ),
        height=600,
        margin=dict(l=20, r=20, t=50, b=20),
        title=dict(
            text=f"Tous les buts de Neymar en LaLiga ({len(filtered_df)} buts affichés)",
            x=0.5,
            font=dict(size=16, color='#333333')
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        )
    )
    
    # Affichage du terrain avec gestion des clics
    event = st.plotly_chart(fig, use_container_width=True, key="football_pitch", on_select="rerun")
    
    # Gestion de la sélection d'un but
    if event and event.selection and len(event.selection.points) > 0:
        selected_point = event.selection.points[0]
        if 'customdata' in selected_point:
            point_index = selected_point['customdata']
            st.session_state.selected_goal = point_index
    
    # Affichage des détails du but sélectionné
    if 'selected_goal' in st.session_state and st.session_state.selected_goal in filtered_df.index:
        goal_info = filtered_df.loc[st.session_state.selected_goal]
        st.markdown("---")
        display_goal_details(goal_info)
    
    # === TABLEAU DE BORD STATISTIQUES ===
    st.markdown("---")
    create_statistics_dashboard(filtered_df)
    
    # === ANALYSES AVANCÉES ===
    st.markdown("---")
    st.markdown("### 🔍 Analyses avancées")
    
    tab1, tab2, tab3 = st.tabs(["📊 Heatmap des buts", "📈 Évolution temporelle", "🎯 Analyse xG"])
    
    with tab1:
        if len(filtered_df) > 0:
            # Heatmap des positions de but
            st.markdown("#### Zones de prédilection de Neymar")
            
            # Créer une grille pour la heatmap
            x_bins = np.linspace(0, 120, 25)
            y_bins = np.linspace(0, 80, 17)
            
            # Calculer la heatmap
            hist, x_edges, y_edges = np.histogram2d(
                filtered_df['X'], filtered_df['Y'], 
                bins=[x_bins, y_bins]
            )
            
            # Créer la heatmap
            fig_heatmap = go.Figure(data=go.Heatmap(
                z=hist.T,
                x=x_edges[:-1],
                y=y_edges[:-1],
                colorscale='Reds',
                showscale=True,
                hoverongaps=False
            ))
            
            fig_heatmap.update_layout(
                title="Heatmap des positions de but",
                xaxis_title="Position X (mètres)",
                yaxis_title="Position Y (mètres)",
                height=400
            )
            
            st.plotly_chart(fig_heatmap, use_container_width=True)
        else:
            st.info("Aucune donnée à afficher pour cette sélection")
    
    with tab2:
        if len(filtered_df) > 0:
            # Évolution des buts par date
            st.markdown("#### Évolution des performances dans le temps")
            
            # Convertir les dates et trier
            df_temporal = filtered_df.copy()
            df_temporal['date'] = pd.to_datetime(df_temporal['date'])
            df_temporal = df_temporal.sort_values('date')
            
            # Calculer la moyenne mobile de xG
            df_temporal['xG_cumsum'] = df_temporal['xG'].cumsum()
            df_temporal['goal_number'] = range(1, len(df_temporal) + 1)
            df_temporal['avg_xG'] = df_temporal['xG_cumsum'] / df_temporal['goal_number']
            
            fig_temporal = go.Figure()
            
            # xG par but
            fig_temporal.add_trace(go.Scatter(
                x=df_temporal['date'],
                y=df_temporal['xG'],
                mode='markers+lines',
                name='xG par but',
                marker=dict(size=8, color='#FF4B4B'),
                line=dict(width=2)
            ))
            
            # Moyenne mobile
            fig_temporal.add_trace(go.Scatter(
                x=df_temporal['date'],
                y=df_temporal['avg_xG'],
                mode='lines',
                name='xG moyen cumulé',
                line=dict(width=3, color='#2196F3', dash='dash')
            ))
            
            fig_temporal.update_layout(
                title="Évolution de la qualité des buts (xG) dans le temps",
                xaxis_title="Date",
                yaxis_title="Expected Goals (xG)",
                height=400,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_temporal, use_container_width=True)
        else:
            st.info("Aucune donnée à afficher pour cette sélection")
    
    with tab3:
        if len(filtered_df) > 0:
            # Analyse détaillée des xG
            st.markdown("#### Distribution et analyse des Expected Goals")
            
            col_xg1, col_xg2 = st.columns(2)
            
            with col_xg1:
                # Histogramme des xG
                fig_xg_hist = go.Figure(data=[
                    go.Histogram(
                        x=filtered_df['xG'],
                        nbinsx=20,
                        marker_color='#FF4B4B',
                        opacity=0.7
                    )
                ])
                
                fig_xg_hist.update_layout(
                    title="Distribution des valeurs xG",
                    xaxis_title="Expected Goals",
                    yaxis_title="Nombre de buts",
                    height=350
                )
                
                st.plotly_chart(fig_xg_hist, use_container_width=True)
            
            with col_xg2:
                # xG par type de tir
                xg_by_shot = filtered_df.groupby('shotType')['xG'].agg(['mean', 'count']).reset_index()
                
                fig_xg_shot = go.Figure(data=[
                    go.Bar(
                        x=xg_by_shot['shotType'],
                        y=xg_by_shot['mean'],
                        text=[f"{row['mean']:.3f}<br>({row['count']} buts)" 
                              for _, row in xg_by_shot.iterrows()],
                        textposition='auto',
                        marker_color=['#FF4B4B', '#4CAF50', '#2196F3']
                    )
                ])
                
                fig_xg_shot.update_layout(
                    title="xG moyen par type de tir",
                    xaxis_title="Type de tir",
                    yaxis_title="xG moyen",
                    height=350
                )
                
                st.plotly_chart(fig_xg_shot, use_container_width=True)
            
            # Métriques xG avancées
            st.markdown("#### Métriques xG avancées")
            
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            
            with col_m1:
                overperformance = len(filtered_df) - filtered_df['xG'].sum()
                st.metric(
                    "🎯 Surperformance", 
                    f"{overperformance:+.1f}",
                    help="Différence entre buts marqués et xG total"
                )
            
            with col_m2:
                difficult_goals = len(filtered_df[filtered_df['xG'] < 0.1])
                st.metric(
                    "🌟 Buts exceptionnels",
                    f"{difficult_goals}",
                    help="Buts avec xG < 0.1"
                )
            
            with col_m3:
                easy_goals = len(filtered_df[filtered_df['xG'] > 0.5])
                st.metric(
                    "🎯 Buts faciles",
                    f"{easy_goals}",
                    help="Buts avec xG > 0.5"
                )
            
            with col_m4:
                best_goal_xg = filtered_df['xG'].min()
                st.metric(
                    "💎 Meilleur but",
                    f"{best_goal_xg:.3f}",
                    help="Plus faible xG (but le plus difficile)"
                )
        else:
            st.info("Aucune donnée à afficher pour cette sélection")
    
    # === TABLEAU DÉTAILLÉ ===
    st.markdown("---")
    st.markdown("### 📋 Tableau détaillé des buts")
    
    if len(filtered_df) > 0:
        # Préparer le tableau d'affichage
        display_df = filtered_df.copy()
        
        # Ajouter les statistiques calculées
        for idx, row in display_df.iterrows():
            stats = calculate_goal_stats(row)
            display_df.loc[idx, 'Distance'] = f"{stats['distance']:.1f}m"
            display_df.loc[idx, 'Zone'] = stats['zone']
            display_df.loc[idx, 'Difficulté'] = stats['difficulty']
        
        # Sélectionner les colonnes à afficher
        columns_to_show = [
            'id', 'season', 'date', 'minute', 'opponent', 'h_a',
            'shotType', 'situation', 'xG', 'Distance', 'Zone', 'Difficulté',
            'player_assisted'
        ]
        
        display_table = display_df[columns_to_show].copy()
        display_table.columns = [
            'ID', 'Saison', 'Date', 'Min', 'Adversaire', 'Lieu',
            'Type tir', 'Situation', 'xG', 'Distance', 'Zone', 'Difficulté',
            'Passeur'
        ]
        
        # Formater les colonnes
        display_table['Lieu'] = display_table['Lieu'].map({'h': '🏠', 'a': '✈️'})
        display_table['xG'] = display_table['xG'].apply(lambda x: f"{x:.3f}")
        display_table['Passeur'] = display_table['Passeur'].fillna('Aucun')
        
        # Affichage du tableau avec sélection
        selected_rows = st.dataframe(
            display_table,
            use_container_width=True,
            height=400,
            on_select="rerun",
            selection_mode="single-row",
            column_config={
                "ID": st.column_config.NumberColumn("ID", width="small"),
                "xG": st.column_config.NumberColumn("xG", format="%.3f"),
                "Zone": st.column_config.TextColumn("Zone", width="medium"),
            }
        )
        
        # Gestion de la sélection dans le tableau
        if hasattr(selected_rows, 'selection') and selected_rows.selection and len(selected_rows.selection['rows']) > 0:
            selected_row_idx = selected_rows.selection['rows'][0]
            original_index = filtered_df.iloc[selected_row_idx].name
            st.session_state.selected_goal = original_index
            st.rerun()
        
        # Options d'export
        st.markdown("#### 📥 Export des données")
        
        col_export1, col_export2 = st.columns(2)
        
        with col_export1:
            # Export CSV
            csv_data = filtered_df.to_csv(index=False)
            st.download_button(
                label="📊 Télécharger en CSV",
                data=csv_data,
                file_name=f"neymar_buts_laliga_filtered_{len(filtered_df)}.csv",
                mime="text/csv"
            )
        
        with col_export2:
            # Résumé statistique
            summary_text = f"""
Résumé des buts de Neymar Jr. en LaLiga
======================================

Période: 2013-2017
Buts analysés: {len(filtered_df)}
xG Total: {filtered_df['xG'].sum():.2f}
xG Moyen: {filtered_df['xG'].mean():.3f}

Répartition par saison:
{filtered_df['season'].value_counts().sort_index().to_string()}

Répartition par type de tir:
{filtered_df['shotType'].value_counts().to_string()}

Répartition par situation:
{filtered_df['situation'].value_counts().to_string()}
            """
            
            st.download_button(
                label="📋 Télécharger le résumé",
                data=summary_text,
                file_name=f"neymar_resume_statistiques.txt",
                mime="text/plain"
            )
    else:
        st.info("Aucune donnée à afficher avec les filtres actuels.")
    
    # === FOOTER ===
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666666; padding: 2rem;">
        <p><strong>⚽ Application d'analyse des buts de Neymar Jr. en LaLiga</strong></p>
        <p>Données générées pour démonstration | Période: 2013-2017 | Total: {total_goals} buts</p>
        <p><em>Cliquez sur les points du terrain ou les lignes du tableau pour explorer les détails de chaque but</em></p>
    </div>
    """.format(total_goals=len(df)), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
