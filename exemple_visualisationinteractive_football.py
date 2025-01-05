import pandas as pd
import numpy as np
import streamlit as st
from soccerplots.radar_chart import Radar
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity

# Dictionnaire des fichiers par ligue et position
league_files = {
    "Premier League": {
        "Attaquant": "Premier_League_Attaquant.csv",
        "Défenseur": "Premier_League_Défenseur.csv",
        "Milieu": "Premier_League_Milieu.csv",
    },
    "Bundesliga": {
        "Attaquant": "Bundesliga_Attaquant.csv",
        "Défenseur": "Bundesliga_Défenseur.csv",
        "Milieu": "Bundesliga_Milieu.csv",
    },
    "La Liga": {
        "Attaquant": "La_Liga_Attaquant.csv",
        "Défenseur": "La_Liga_Défenseur.csv",
        "Milieu": "La_Liga_Milieu.csv",
    },
    "Ligue 1": {
        "Attaquant": "Ligue_1_Attaquant.csv",
        "Défenseur": "Ligue_1_Défenseur.csv",
        "Milieu": "Ligue_1_Milieu.csv",
    },
    "Serie A": {
        "Attaquant": "Serie_A_Attaquant.csv",
        "Défenseur": "Serie_A_Défenseur.csv",
        "Milieu": "Serie_A_Milieu.csv",
    },
}

# Fonction pour charger et prétraiter les données
def load_and_preprocess_data(file_path, selected_features):
    data = pd.read_csv(file_path)
    data = data[data['Matchs joues'].astype(int) > 10]  # Minimum de 10 matchs joués
    data = data.drop(['Matches (equivalents 90 minutes)', 'Performance Interceptions '], axis=1, errors='ignore')
    data = data.loc[:, ~data.columns.str.contains(r"\.1")]
    data = data.dropna(subset=selected_features)
    scaler = MinMaxScaler()
    data[selected_features] = scaler.fit_transform(data[selected_features])
    return data

# Fonction pour trouver les joueurs similaires
def find_similar_players(data, player_data, selected_features, top_n=5):
    feature_data = data[selected_features]
    similarity = cosine_similarity(feature_data, [player_data])
    similarity_scores = pd.Series(similarity.flatten(), index=data['Joueur'])
    similar_players = similarity_scores.sort_values(ascending=False)[:top_n]
    return list(zip(similar_players.index, similar_players.values))

# Fonction pour créer un radar chart (inchangé par rapport à l'original)
def create_radar_chart(player1_data, player2_data, features, player1_name, player2_name):
    radar = Radar()
    ranges = [(0, 1)] * len(features)
    fig, ax = radar.plot_radar(
        ranges=ranges,
        params=features,
        values=[player1_data, player2_data],
        radar_color=["blue", "red"],
        alphas=[0.6, 0.6],
        title={
            "title_name": player1_name,
            "title_color": "blue",
            "subtitle_name": player2_name,
            "subtitle_color": "red",
        },
        compare=True,
    )
    return fig

# Streamlit application
st.title("Comparaison de joueurs et recherche de similitudes")

# Sélection des paramètres
selected_position = st.selectbox("Choisissez la position", options=["Attaquant", "Défenseur", "Milieu"])
base_league = st.selectbox("Choisissez la ligue du joueur de base", options=list(league_files.keys()))
comparison_league = st.selectbox("Choisissez la ligue pour trouver des joueurs similaires", options=list(league_files.keys()))

# Caractéristiques sélectionnées
selected_features = selected_features = [
    'Matchs joues', 'Titularisations', 'Minutes jouees', 'Matches equivalents 90 minutes', 'Buts', 
    'Passes decisives', 'Buts + Passes decisives', 'Buts hors penalty', 'Penalty marques', 'Penalty tentes', 
    'Cartons jaunes', 'Cartons rouges', 'Buts attendus (xG)', 'Buts attendus hors penalty (npxG)', 
    'Passes decisives attendues (xAG)', 'xG + xAG hors penalty', 'Passes progressives', 'Courses progressives', 
    'Receptions progressives', 'Buts par 90 minutes', 'Passes decisives par 90 minutes', 'Buts + Passes decisives par 90 minutes', 
    'Buts hors penalty par 90 minutes', 'Buts + Passes decisives hors penalty par 90 min', 'xG par 90 minutes', 'xAG par 90 minutes', 
    'xG + xAG par 90 minutes', 'npxG par 90 minutes', 'npxG + xAG par 90 minutes', 'Actions menant a un tir', 
    'Actions menant a un tir par 90 minutes', 'Passes vivantes menant a un tir', 'Passes arretees menant a un tir', 
    'Ballons perdus menant a un tir', 'Tirs menant a un tir', 'Fautes subies menant a un tir', 'Actions defensives menant a un tir', 
    'Actions menant a un but', 'Actions menant a un but par 90 minutes', 'Passes vivantes menant a un but', 
    'Passes arretees menant a un but', 'Ballons perdus menant a un but', 'Tirs menant a un but', 'Fautes subies menant a un but', 
    'Actions defensives menant a un but', 'Passes reussies totales', 'Passes tentees totales', 
    'Pourcentage de reussite des passes', 'Distance totale des passes', 'Distance progressive des passes', 
    'Passes courtes reussies', 'Passes courtes tentees', 'Pourcentage de reussite des passes courtes', 
    'Passes moyennes reussies', 'Passes moyennes tentees', 'Pourcentage de reussite des passes moyennes', 
    'Passes longues reussies', 'Passes longues tentees', 'Pourcentage de reussite des passes longues', 'Passes attendues', 
    'Difference entre passes attendues et xAG', 'Passes cles', 'Passes vers le dernier tiers', 'Passes dans la surface adverse', 
    'Centres dans la surface adverse', 'Deuxieme carton jaune', 'Fautes commises', 'Fautes subies', 'Hors-jeux', 'Centres',
    'Tacles reussis', 'Penalty obtenus', 'Penalty concedes', 'Buts contre son camp', 
    'Ballons recuperes', 'Duels aeriens gagnes', 'Duels aeriens perdus', 'Pourcentage de duels aeriens gagnes', 'Tirs', 
    'Tirs cadres', 'Pourcentage de tirs cadres', 'Tirs par 90 minutes', 'Tirs cadres par 90 minutes', 'Buts par tir', 
    'Buts par tir cadre', 'Distance moyenne des tirs', 'Coups francs', 'npxG par tir', 'Difference entre buts reels et xG', 
    'Difference entre buts reels hors penalty et npxG', 'Tacles', 'Tacles dans le tiers defensif', 'Tacles dans le tiers median', 
    'Tacles dans le tiers offensif', 'Tacles dans les duels', 'Duels tentes', 'Pourcentage de tacles reussis Tkl%', 'Duels perdus', 
    'Contres', 'Tirs contres', 'Passes contrees', 'Interceptions', 'Tacles + Interceptions', 'Degagements', 
    'Erreurs ayant conduit a un tir adverse', 'Minutes par match', 'Pourcentage de minutes jouees', 'Minutes par titularisation ', 
    'Matches completes', 'Remplacants', 'Minutes par entree', 'Matches non remplace', 'Points par match', 'Buts marques avec le joueur', 
    'Buts encaisses avec le joueur', 'Difference de buts avec le joueur', 'Difference de buts par 90 minutes', 
    'Difference avec/sans le joueur', 'xG marques avec le joueur ', 'xG encaisses avec le joueur', 'Difference de xG avec le joueur', 
    'Difference de xG par 90 minutes', 'Difference de xG avec/sans le joueur', 'Touches', 'Touches dans la surface defensive', 
    'Touches dans le tiers defensif', 'Touches dans le tier median', 'Touches dans le tiers offensif', 
    'Touches dans la surface offensive', 'Ballons en jeu', 'Dribbles tentes', 'Dribbles reussis', 'Pourcentage de dribbles reussis', 
    'Ballons perdus apres dribble', 'Pourcentage de ballons perdus apres dribble', 'Portees de balle', 
    'Distance totale parcourue avec le ballon', 'Distance progressive parcourue avec le ballon', 
    'Courses vers le dernier tiers', 'Courses dans la surface adverse'
]
# Chargement des données
base_data = load_and_preprocess_data(league_files[base_league][selected_position], selected_features)
comparison_data = load_and_preprocess_data(league_files[comparison_league][selected_position], selected_features)

# Sélection du joueur de base
player_base = st.selectbox("Choisissez le joueur de base", options=base_data['Joueur'].unique())

# Extraction des données du joueur de base
player_base_data = base_data[base_data['Joueur'] == player_base][selected_features].iloc[0].tolist()

# Recherche de joueurs similaires
similar_players = find_similar_players(comparison_data, player_base_data, selected_features)

# Affichage des joueurs similaires
st.write(f"Joueurs similaires à **{player_base}** dans **{comparison_league} - {selected_position}** :")
for player, score in similar_players:
    st.write(f"- {player}: {score:.2f}")

# Sélection d'un joueur pour le radar chart
player_to_compare = st.selectbox("Choisissez un joueur à comparer", options=comparison_data['Joueur'].unique())

# Extraction des données pour le radar chart
player_to_compare_data = comparison_data[comparison_data['Joueur'] == player_to_compare][selected_features].iloc[0].tolist()

# Tracé du radar chart
st.write("**Radar Chart Comparatif :**")
fig = create_radar_chart(player_base_data, player_to_compare_data, selected_features, player_base, player_to_compare)
st.pyplot(fig)
