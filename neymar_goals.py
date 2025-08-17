import streamlit as st
import pandas as pd
import plotly.graph_objects as go
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
        
        # Correction des noms d'équipes - Fix pour les matchs à l'extérieur
        df_clean['opponent'] = df_clean.apply(lambda row: 
            row['h_team'] if row['h_a'] == 'a' else row['a_team'], axis=1)
        
        # Nettoyage des passeurs
        df_clean['player_assisted'] = df_clean['player_assisted'].fillna('')
        
        return df_clean
        
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement des données: {e}")
        return None

def create_pitch():
    """Crée le terrain de football avec un contraste élevé"""
    fig = go.Figure()
    
    # Dimensions du terrain
    pitch_length = 120
    pitch_width = 80
    
    # Terrain avec contraste élevé - vert foncé
    fig.add_shape(
        type="rect",
        x0=0, y0=0, x1=pitch_length, y1=pitch_width,
        fillcolor="rgba(15, 80, 15, 1)",  # Vert très foncé
        line=dict(color="white", width=4)
    )
    
    # Ligne médiane
    fig.add_shape(
        type="line",
        x0=pitch_length/2, y0=0, x1=pitch_length/2, y1=pitch_width,
        line=dict(color="white", width=4)
    )
    
    # Cercle central
    fig.add_shape(
        type="circle",
        xref="x", yref="y",
        x0=pitch_length/2-9.15, y0=pitch_width/2-9.15,
        x1=pitch_length/2+9.15, y1=pitch_width/2+9.15,
        line=dict(color="white", width=4),
        fillcolor="rgba(0,0,0,0)"
    )
    
    # Point central
    fig.add_trace(go.Scatter(
        x=[pitch_length/2], y=[pitch_width/2],
        mode='markers',
        marker=dict(color='white', size=12),
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
        line=dict(color="white", width=4),
        fillcolor="rgba(0,0,0,0)"
    )
    
    # Surface de but droite
    goal_area_width = 18.32
    goal_area_length = 5.5
    goal_y = (pitch_width - goal_area_width) / 2
    
    fig.add_shape(
        type="rect",
        x0=pitch_length-goal_area_length, y0=goal_y,
        x1=pitch_length, y1=goal_y+goal_area_width,
        line=dict(color="white", width=4),
        fillcolor="rgba(0,0,0,0)"
    )
    
    # Buts
    goal_width = 7.32
    goal_y_pos = (pitch_width - goal_width) / 2
    
    # But droit (attaque)
    fig.add_shape(
        type="line",
        x0=pitch_length, y0=goal_y_pos,
        x1=pitch_length, y1=goal_y_pos+goal_width,
        line=dict(color="white", width=8)
    )
    
    # Point de penalty droit
    fig.add_trace(go.Scatter(
        x=[pitch_length-11], y=[pitch_width/2],
        mode='markers',
        marker=dict(color='white', size=12, symbol='circle'),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Arc de penalty droit
    theta = np.linspace(0.6, 2.54, 50)
    arc_x = pitch_length - 11 + 9.15 * np.cos(theta)
    arc_y = pitch_width/2 + 9.15 * np.sin(theta)
    
    fig.add_trace(go.Scatter(
        x=arc_x, y=arc_y,
        mode='lines',
        line=dict(color='white', width=4),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Surface de réparation gauche
    fig.add_shape(
        type="rect",
        x0=0, y0=penalty_y,
        x1=penalty_area_length, y1=penalty_y+penalty_area_width,
        line=dict(color="white", width=4),
        fillcolor="rgba(0,0,0,0)"
    )
    
    # Surface de but gauche
    fig.add_shape(
        type="rect",
        x0=0, y0=goal_y,
        x1=goal_area_length, y1=goal_y+goal_area_width,
        line=dict(color="white", width=4)
    )
    
    # But gauche
    fig.add_shape(
        type="line",
        x0=0, y0=goal_y_pos,
        x1=0, y1=goal_y_pos+goal_width,
        line=dict(color="white", width=8)
    )
    
    # Point de penalty gauche
    fig.add_trace(go.Scatter(
        x=[11], y=[pitch_width/2],
        mode='markers',
        marker=dict(color='white', size=12),
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
            Barcelona vs {goal_info['opponent']} | {goal_info['date']}
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
        else:
            st.warning("⚠️ Fichier vidéo non trouvé")
            st.info(f"📂 Chemin recherché: `{video_file}`")
        
        # Informations sur le match
        st.markdown('<div class="goal-info">', unsafe_allow_html=True)
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown(f"""
            **⚽ Match**  
            Barcelona vs {goal_info['opponent']}
            
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
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        
        # Métriques du but
        st.metric("⏱️ Minute", f"{goal_info['minute']}'")
        st.metric("🎯 xG", f"{goal_info['xG']:.3f}")
        st.metric("🦶 Type de tir", goal_info['shotType'])
        st.metric("🎮 Situation", goal_info['situation'])
        
        if goal_info['player_assisted'] and goal_info['player_assisted'].strip():
            st.metric("🤝 Passeur", goal_info['player_assisted'])
        
        # Calculs avancés
        distance_to_goal = ((120 - goal_info['X'])**2 + (40 - goal_info['Y'])**2)**0.5 * 0.9144
        st.metric("📏 Distance", f"{distance_to_goal:.1f}m")
        
        # Zone du terrain
        if goal_info['X'] > 103.5:
            zone = "🎯 Surface"
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
            <strong style="color: {zone_color};">🗺️ Zone</strong><br>
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
    
    # Affichage du nombre de buts chargés
    st.success(f"✅ **{len(df)} buts** de Neymar Jr. chargés")
    
    # Utilisation des données nettoyées
    df_goals = df.copy()
    
    # Sidebar avec filtres
    st.sidebar.markdown("## 🎯 Filtres")
    st.sidebar.markdown("---")
    
    # Filtre par saison
    seasons = sorted(df_goals['season'].unique())
    selected_seasons = st.sidebar.multiselect(
        "🏆 Saisons",
        seasons,
        default=seasons
    )
    
    # Filtre par type de tir
    shot_types = sorted(df_goals['shotType'].unique())
    selected_shot_types = st.sidebar.multiselect(
        "🦶 Type de tir",
        shot_types,
        default=shot_types
    )
    
    # Filtre par situation
    situations = sorted(df_goals['situation'].unique())
    selected_situations = st.sidebar.multiselect(
        "🎮 Situation",
        situations,
        default=situations
    )
    
    # Filtre par adversaire
    teams = sorted(df_goals['opponent'].unique())
    selected_teams = st.sidebar.multiselect(
        "👥 Adversaires",
        teams,
        default=teams
    )
    
    # Filtre par xG
    min_xg, max_xg = st.sidebar.slider(
        "🎯 xG",
        min_value=0.0,
        max_value=1.0,
        value=(0.0, 1.0),
        step=0.01,
        format="%.2f"
    )
    
    # Application des filtres
    filtered_df = df_goals[
        (df_goals['season'].isin(selected_seasons)) &
        (df_goals['shotType'].isin(selected_shot_types)) &
        (df_goals['situation'].isin(selected_situations)) &
        (df_goals['opponent'].isin(selected_teams)) &
        (df_goals['xG'] >= min_xg) &
        (df_goals['xG'] <= max_xg)
    ]
    
    # Statistiques dans la sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("## 📊 Statistiques")
    
    if len(filtered_df) > 0:
        st.sidebar.metric("🎯 Buts sélectionnés", len(filtered_df))
        st.sidebar.metric("📈 xG Total", f"{filtered_df['xG'].sum():.1f}")
        st.sidebar.metric("⚡ xG Moyen", f"{filtered_df['xG'].mean():.3f}")
        goals_in_box = len(filtered_df[filtered_df['X'] > 103.5])
        st.sidebar.metric("🥅 Buts en surface", f"{goals_in_box}")
    else:
        st.sidebar.warning("⚠️ Aucun but correspondant")
    
    # Terrain au centre et plus grand
    st.markdown("### 🏟️ Terrain - Cliquez sur un but pour voir la vidéo")
    
    # Création du terrain
    fig = create_pitch()
    
    # Ajout des buts sur le terrain avec meilleur contraste
    if len(filtered_df) > 0:
        # Taille basée sur xG (plus visible)
        sizes = [max(20, 80 * row['xG']) for _, row in filtered_df.iterrows()]
        
        # Couleurs vives avec fort contraste
        season_colors = {
            '2013-14': '#FF1744',  # Rouge vif
            '2014-15': '#00E676',  # Vert vif
            '2015-16': '#2196F3',  # Bleu vif
            '2016-17': '#FF9800'   # Orange vif
        }
        
        colors = [season_colors.get(row['season'], '#FF1744') for _, row in filtered_df.iterrows()]
        
        # Texte de hover personnalisé
        hover_text = []
        for _, row in filtered_df.iterrows():
            text = f"<b>🎯 But #{row['id']}</b><br>"
            text += f"⏱️ Minute: {row['minute']}'<br>"
            text += f"🎯 xG: {row['xG']:.3f}<br>"
            text += f"🏆 Saison: {row['season']}<br>"
            text += f"🦶 Type: {row['shotType']}<br>"
            text += f"🎮 Situation: {row['situation']}<br>"
            text += f"👥 vs {row['opponent']}<br>"
            if row['player_assisted']:
                text += f"🤝 Passeur: {row['player_assisted']}<br>"
            text += f"<i>🖱️ Cliquez pour voir la vidéo</i>"
            hover_text.append(text)
        
        # Scatter plot des buts avec meilleur contraste
        fig.add_trace(go.Scatter(
            x=filtered_df['X'],
            y=filtered_df['Y'],
            mode='markers',
            marker=dict(
                size=sizes,
                color=colors,
                opacity=0.9,
                line=dict(width=3, color='white'),
                symbol='circle'
            ),
            text=hover_text,
            hovertemplate='%{text}<extra></extra>',
            customdata=filtered_df.index,
            name="Buts"
        ))
    
    # Configuration du layout pour un terrain plus grand et centré
    fig.update_layout(
        plot_bgcolor='rgba(0, 0, 0, 1)',  # Fond noir pour contraste
        paper_bgcolor='rgba(0, 0, 0, 1)',
        xaxis=dict(
            range=[-3, 123],
            showgrid=False,
            showticklabels=False,
            zeroline=False
        ),
        yaxis=dict(
            range=[-3, 83],
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            scaleanchor="x",
            scaleratio=1
        ),
        height=700,  # Plus grand
        margin=dict(l=20, r=20, t=20, b=20),
        showlegend=False
    )
    
    # Affichage du terrain avec événements de sélection
    event = st.plotly_chart(fig, use_container_width=True, key="pitch", on_select="rerun")
    
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
            'xG', 'player_assisted', 'opponent', 'video_but'
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
        
        # Ajout d'un index pour le mapping
        display_df_with_index = display_df.reset_index()
        
        # Sélection d'un but dans le tableau
        selected_indices = st.dataframe(
            display_df,
            use_container_width=True,
            height=400,
            on_select="rerun",
            selection_mode="single-row"
        )
        
        # Correction de la gestion de sélection
        if hasattr(selected_indices, 'selection') and selected_indices.selection and len(selected_indices.selection['rows']) > 0:
            selected_row_idx = selected_indices.selection['rows'][0]
            # Récupérer l'index original du DataFrame filtré
            original_index = filtered_df.iloc[selected_row_idx].name
            st.session_state.selected_goal = original_index
            st.rerun()
    else:
        st.info("ℹ️ Aucun but ne correspond aux critères sélectionnés.")

if __name__ == "__main__":
    main()
