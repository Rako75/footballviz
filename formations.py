import streamlit as st
import numpy as np
import pandas as pd
from mplsoccer import Pitch
import matplotlib.pyplot as plt
from statsbombpy import sb
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from scipy.spatial.distance import pdist
import warnings
warnings.filterwarnings('ignore')

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Analyse des Formations - Football",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    .team-header {
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

class StreamlitFormationAnalyzer:
    def __init__(self):
        self.events_df = None
        self.positions_timeline = {}
        self.window_size = 10
        
        # Couleurs par poste
        self.position_colors = {
            'Goalkeeper': '#FF6B6B',
            'Center Back': '#4ECDC4',
            'Left Back': '#45B7D1',
            'Right Back': '#96CEB4',
            'Defensive Midfield': '#FFEAA7',
            'Central Midfield': '#DDA0DD',
            'Attacking Midfield': '#98D8C8',
            'Left Midfield': '#F7DC6F',
            'Right Midfield': '#BB8FCE',
            'Left Wing': '#85C1E9',
            'Right Wing': '#F8C471',
            'Center Forward': '#EC7063',
            'Left Center Forward': '#AF7AC5',
            'Right Center Forward': '#7FB3D3'
        }
    
    @st.cache_data
    def load_data(_self, match_id):
        """Charge les données StatsBomb avec cache"""
        try:
            df = sb.events(match_id)
            return df
        except Exception as e:
            st.error(f"Erreur lors du chargement des données: {e}")
            return None
    
    def prepare_data(self, events_df):
        """Prépare les données pour l'analyse"""
        self.events_df = events_df.copy()
        
        # Extraction des coordonnées avec vérification
        def extract_coordinate(loc, index):
            if isinstance(loc, (list, tuple)) and len(loc) > index:
                return loc[index]
            elif pd.notna(loc):
                try:
                    return float(loc)
                except:
                    return np.nan
            return np.nan
        
        self.events_df['x'] = self.events_df['location'].apply(lambda loc: extract_coordinate(loc, 0))
        self.events_df['y'] = self.events_df['location'].apply(lambda loc: extract_coordinate(loc, 1))
        
        # Filtrage des données valides
        valid_mask = (
            (self.events_df['x'].notna()) & 
            (self.events_df['y'].notna()) &
            (self.events_df['player'].notna()) &
            (self.events_df['x'] >= 0) &
            (self.events_df['x'] <= 120) &
            (self.events_df['y'] >= 0) &
            (self.events_df['y'] <= 80)
        )
        
        self.events_df = self.events_df[valid_mask].copy()
        
        if len(self.events_df) == 0:
            st.error("❌ Aucune donnée de position valide trouvée!")
            return False
        
        # Plage des minutes
        self.min_minute = int(self.events_df['minute'].min())
        self.max_minute = int(self.events_df['minute'].max())
        
        st.sidebar.success(f"✅ {len(self.events_df)} événements avec positions valides")
        st.sidebar.info(f"📅 Minutes disponibles: {self.min_minute} à {self.max_minute}")
        
        return True
    
    @st.cache_data
    def precompute_positions(_self, events_df, window_size):
        """Pré-calcule toutes les positions (avec cache)"""
        positions_timeline = {}
        
        min_minute = int(events_df['minute'].min())
        max_minute = int(events_df['minute'].max())
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total_minutes = max_minute - min_minute + 1
        
        for i, minute in enumerate(range(min_minute, max_minute + 1)):
            # Mise à jour de la barre de progression
            progress = (i + 1) / total_minutes
            progress_bar.progress(progress)
            status_text.text(f'Calcul des positions... Minute {minute}/{max_minute}')
            
            # Fenêtre temporelle
            start_minute = max(min_minute, minute - window_size // 2)
            end_minute = min(max_minute, minute + window_size // 2)
            
            window_data = events_df[
                (events_df['minute'] >= start_minute) & 
                (events_df['minute'] <= end_minute)
            ].copy()
            
            if len(window_data) == 0:
                continue
            
            positions_timeline[minute] = {}
            
            for team_id in window_data['team_id'].unique():
                team_data = window_data[window_data['team_id'] == team_id]
                team_name = team_data['team'].iloc[0]
                
                # Positions moyennes
                avg_pos = team_data.groupby('player').agg({
                    'x': 'mean',
                    'y': 'mean',
                    'player_id': 'count'
                }).rename(columns={'player_id': 'actions'})
                
                avg_pos = avg_pos[avg_pos['actions'] >= 3]
                
                # Positions des joueurs
                positions = team_data.groupby('player')['position'].first()
                avg_pos = avg_pos.join(positions)
                
                # Top 11 joueurs
                if len(avg_pos) > 11:
                    avg_pos = avg_pos.nlargest(11, 'actions')
                
                formation = _self.get_formation_from_positions(avg_pos)
                compactness = _self.calculate_team_compactness(avg_pos)[0]
                
                positions_timeline[minute][team_id] = {
                    'team_name': team_name,
                    'positions': avg_pos,
                    'formation': formation,
                    'compactness': compactness
                }
        
        progress_bar.empty()
        status_text.empty()
        
        return positions_timeline
    
    def get_formation_from_positions(self, positions_df):
        """Détecte la formation"""
        if len(positions_df) < 10:
            return "Incomplète"
        
        field_players = positions_df[~positions_df['position'].str.contains('Goalkeeper', na=False)]
        
        if len(field_players) < 10:
            return "Incomplète"
        
        x_positions = field_players['x'].values
        def_threshold = np.percentile(x_positions, 30)
        mid_threshold = np.percentile(x_positions, 70)
        
        defenders = len(field_players[field_players['x'] <= def_threshold])
        midfielders = len(field_players[
            (field_players['x'] > def_threshold) & 
            (field_players['x'] <= mid_threshold)
        ])
        attackers = len(field_players[field_players['x'] > mid_threshold])
        
        total = defenders + midfielders + attackers
        if total != 10:
            if total > 10:
                if midfielders > 3:
                    midfielders -= (total - 10)
                else:
                    defenders -= (total - 10)
            else:
                midfielders += (10 - total)
        
        return f"{defenders}-{midfielders}-{attackers}"
    
    def calculate_team_compactness(self, positions_df):
        """Calcule la compacité"""
        if len(positions_df) < 2:
            return 0, 0
        
        # Vérifier que les colonnes x et y existent
        if 'x' not in positions_df.columns or 'y' not in positions_df.columns:
            return 0, 0
        
        coords = positions_df[['x', 'y']].values
        distances = pdist(coords)
        avg_distance = np.mean(distances)
        
        x_range = positions_df['x'].max() - positions_df['x'].min()
        y_range = positions_df['y'].max() - positions_df['y'].min()
        area = x_range * y_range
        
        return avg_distance, area
    
    def create_pitch_plot(self, team_data, team_name):
        """Crée un graphique de terrain avec matplotlib"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Terrain
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#f8f8f8', 
                     line_color='white', linewidth=2)
        pitch.draw(ax=ax)
        
        positions = team_data['positions']
        formation = team_data['formation']
        compactness = team_data['compactness']
        
        # Tracé des joueurs
        for player, data in positions.iterrows():
            x, y = data['x'], data['y']
            pos = data['position']
            actions = data['actions']
            
            color = self.position_colors.get(pos, '#95A5A6')
            size = min(max(actions * 15, 150), 400)
            
            # Joueurs
            ax.scatter(x, y, c='white', s=size+50, 
                      edgecolors='black', linewidth=2, zorder=4)
            ax.scatter(x, y, c=color, s=size, alpha=0.9, 
                      edgecolors='black', linewidth=1.5, zorder=5)
            
            # Noms
            player_name = player.split()[-1] if ' ' in player else player
            ax.annotate(player_name, (x, y-4), ha='center', va='top', 
                       fontsize=8, fontweight='bold', color='black', zorder=6)
            ax.annotate(f'({int(actions)})', (x, y+4), ha='center', va='bottom', 
                       fontsize=7, color='gray', zorder=6)
        
        # Lignes de formation
        self.draw_formation_lines(ax, positions)
        
        ax.set_title(f'{team_name}\nFormation: {formation} | Compacité: {compactness:.1f}m', 
                    fontsize=14, fontweight='bold')
        
        return fig
    
    def draw_formation_lines(self, ax, positions):
        """Dessine les lignes tactiques"""
        field_players = positions[~positions['position'].str.contains('Goalkeeper', na=False)]
        
        if len(field_players) < 4:
            return
        
        x_positions = field_players['x'].values
        def_threshold = np.percentile(x_positions, 33)
        att_threshold = np.percentile(x_positions, 67)
        
        defenders = field_players[field_players['x'] <= def_threshold]
        midfielders = field_players[
            (field_players['x'] > def_threshold) & 
            (field_players['x'] <= att_threshold)
        ]
        attackers = field_players[field_players['x'] > att_threshold]
        
        for group in [defenders, midfielders, attackers]:
            if len(group) >= 2:
                y_sorted = group.sort_values('y')
                for i in range(len(y_sorted) - 1):
                    x1, y1 = y_sorted.iloc[i][['x', 'y']]
                    x2, y2 = y_sorted.iloc[i + 1][['x', 'y']]
                    ax.plot([x1, x2], [y1, y2], 'k--', alpha=0.4, linewidth=1.5)
    
    def create_timeline_plot(self, current_minute):
        """Crée le graphique timeline avec Plotly"""
        fig = go.Figure()
        
        teams = list(self.events_df['team_id'].unique())
        colors = ['blue', 'red']
        
        for i, team_id in enumerate(teams):
            team_name = self.events_df[self.events_df['team_id'] == team_id]['team'].iloc[0]
            
            minutes = []
            compactness_values = []
            formations = []
            
            for minute in sorted(self.positions_timeline.keys()):
                if team_id in self.positions_timeline[minute]:
                    minutes.append(minute)
                    compactness_values.append(self.positions_timeline[minute][team_id]['compactness'])
                    formations.append(self.positions_timeline[minute][team_id]['formation'])
            
            if minutes:
                # Ligne de compacité
                fig.add_trace(go.Scatter(
                    x=minutes, y=compactness_values,
                    mode='lines+markers',
                    name=f'{team_name}',
                    line=dict(color=colors[i], width=3),
                    hovertemplate=f'<b>{team_name}</b><br>' +
                                 'Minute: %{x}<br>' +
                                 'Compacité: %{y:.1f}m<br>' +
                                 '<extra></extra>'
                ))
        
        # Ligne verticale pour la minute actuelle
        fig.add_vline(x=current_minute, line_dash="dash", line_color="black", 
                     annotation_text=f"Minute {current_minute}")
        
        fig.update_layout(
            title="Évolution de la Compacité des Équipes",
            xaxis_title="Minute du match",
            yaxis_title="Compacité (m)",
            height=400,
            showlegend=True
        )
        
        return fig

def main():
    """Fonction principale de l'application Streamlit"""
    
    # Titre principal
    st.markdown('<h1 class="main-header">⚽ Analyse des Formations - Football Interactif</h1>', 
                unsafe_allow_html=True)
    
    # Initialisation de l'analyseur
    analyzer = StreamlitFormationAnalyzer()
    
    # Sidebar pour les paramètres
    st.sidebar.header("⚙️ Paramètres")
    
    # Sélection du match
    match_id = st.sidebar.number_input(
        "ID du match StatsBomb", 
        value=3941019, 
        help="Entrez l'ID du match à analyser"
    )
    
    # Paramètres d'analyse
    window_size = st.sidebar.slider(
        "Fenêtre d'analyse (minutes)", 
        min_value=5, max_value=20, value=10,
        help="Taille de la fenêtre glissante pour calculer les positions moyennes"
    )
    
    # Chargement des données
    if st.sidebar.button("🔄 Charger le match"):
        with st.spinner("Chargement des données..."):
            events_df = analyzer.load_data(match_id)
            
            if events_df is not None:
                st.session_state['events_df'] = events_df
                st.session_state['data_loaded'] = True
                st.sidebar.success("✅ Données chargées avec succès!")
                
                # Affichage des informations du match
                teams = events_df['team'].unique()
                st.sidebar.write(f"**Équipes:** {teams[0]} vs {teams[1]}")
                st.sidebar.write(f"**Événements totaux:** {len(events_df)}")
                
                # Test des coordonnées
                events_with_coords = events_df[events_df['location'].notna()]
                st.sidebar.write(f"**Événements avec position:** {len(events_with_coords)}")
            else:
                st.sidebar.error("❌ Erreur lors du chargement des données")
    
    # Vérification si les données sont chargées
    if 'data_loaded' not in st.session_state:
        st.info("👆 Veuillez charger un match dans la sidebar pour commencer l'analyse.")
        st.stop()
    
    events_df = st.session_state['events_df']
    
    # Préparation des données
    if analyzer.prepare_data(events_df):
        
        # Pré-calcul des positions (avec cache)
        if 'positions_timeline' not in st.session_state:
            st.info("🔄 Pré-calcul des positions pour toutes les minutes...")
            analyzer.positions_timeline = analyzer.precompute_positions(events_df, window_size)
            st.session_state['positions_timeline'] = analyzer.positions_timeline
            st.success("✅ Positions calculées!")
        else:
            analyzer.positions_timeline = st.session_state['positions_timeline']
        
        # Slider principal pour la navigation
        st.markdown("---")
        st.markdown("### 🎛️ Navigation Temporelle")
        
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col2:
            current_minute = st.slider(
                "Minute du match", 
                min_value=analyzer.min_minute,
                max_value=analyzer.max_minute,
                value=analyzer.min_minute,
                key="minute_slider"
            )
        
        # Boutons de navigation rapide
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            if st.button("⏪ Début"):
                st.session_state.minute_slider = analyzer.min_minute
                st.experimental_rerun()
        with col2:
            if st.button("⏮️ -10min"):
                new_val = max(analyzer.min_minute, current_minute - 10)
                st.session_state.minute_slider = new_val
                st.experimental_rerun()
        with col3:
            if st.button("⏸️ Mi-temps"):
                st.session_state.minute_slider = 45
                st.experimental_rerun()
        with col4:
            if st.button("⏭️ +10min"):
                new_val = min(analyzer.max_minute, current_minute + 10)
                st.session_state.minute_slider = new_val
                st.experimental_rerun()
        with col5:
            if st.button("⏩ Fin"):
                st.session_state.minute_slider = analyzer.max_minute
                st.experimental_rerun()
        
        # Affichage des formations pour la minute sélectionnée
        if current_minute in analyzer.positions_timeline:
            teams = list(analyzer.positions_timeline[current_minute].keys())
            
            # Timeline de la compacité
            st.markdown("---")
            st.markdown("### 📈 Évolution de la Compacité")
            timeline_fig = analyzer.create_timeline_plot(current_minute)
            st.plotly_chart(timeline_fig, use_container_width=True)
            
            # Formations actuelles
            st.markdown("---")
            st.markdown(f"### 🏟️ Formations à la minute {current_minute}")
            
            col1, col2 = st.columns(2)
            
            for i, team_id in enumerate(teams):
                team_data = analyzer.positions_timeline[current_minute][team_id]
                team_name = team_data['team_name']
                
                with col1 if i == 0 else col2:
                    st.markdown(f'<div class="team-header">{team_name}</div>', 
                               unsafe_allow_html=True)
                    
                    # Métriques
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("Formation", team_data['formation'])
                    with col_b:
                        st.metric("Compacité", f"{team_data['compactness']:.1f}m")
                    with col_c:
                        st.metric("Joueurs", len(team_data['positions']))
                    
                    # Terrain
                    fig = analyzer.create_pitch_plot(team_data, team_name)
                    st.pyplot(fig, use_container_width=True)
                    plt.close(fig)  # Éviter les fuites mémoire
            
            # Statistiques détaillées
            st.markdown("---")
            st.markdown("### 📊 Statistiques Détaillées")
            
            stats_data = []
            for team_id in teams:
                team_data = analyzer.positions_timeline[current_minute][team_id]
                stats_data.append({
                    'Équipe': team_data['team_name'],
                    'Formation': team_data['formation'],
                    'Compacité (m)': round(team_data['compactness'], 1),
                    'Joueurs analysés': len(team_data['positions']),
                    'Actions totales': int(team_data['positions']['actions'].sum())
                })
            
            stats_df = pd.DataFrame(stats_data)
            st.dataframe(stats_df, use_container_width=True)
            
        else:
            st.warning(f"❌ Pas de données disponibles pour la minute {current_minute}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
        🔬 Analysé avec StatsBomb | 🏗️ Construit avec Streamlit | ⚽ Visualisations interactives
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
