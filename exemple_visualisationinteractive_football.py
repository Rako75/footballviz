import pandas as pd
import numpy as np
import streamlit as st
from soccerplots.radar_chart import Radar
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import requests
from io import BytesIO

# Fonction pour charger et prétraiter les données
def load_and_preprocess_data(file_path, position):
    data = pd.read_csv(file_path)
    data = data[data['Matchs joues'].astype(int) > 10]

    # Normalisation des colonnes en fonction de la position
    if position == "Attaquant":
        stats_cols = ['Buts p/90 min', 'Passes déc. p/90 min',
                      'Buts + passes déc. p/90min', 'Distance progressive',
                      'Passes progressives', 'Receptions progressives', 'xG p/90 min', 'xAG p/90 min']
    elif position == "Défenseur":
        stats_cols = ['Interceptions', 'Tacles', 'Degagements',
                      'Duels aeriens gagnes', 'Passes progressives', 'Contres']
    elif position == "Milieu":
        stats_cols = ['Passes cles', 'Actions créant un tir p/90 min', 
                      'xG + xAG p/90 min', 'Passes vers le dernier tiers',
                      'Passes progressives', 'Courses progressives']
    else:
        raise ValueError("Position non reconnue")

    data = data.rename(columns={
        'Distance progressive parcourue avec le ballon': 'Distance progressive',
        'Buts par 90 minutes':'Buts p/90 min',
        'Passes decisives par 90 minutes': 'Passes déc. p/90 min',
        'Buts + Passes decisives par 90 minutes': 'Buts + passes déc. p/90min',
        'xG par 90 minutes': 'xG p/90 min',
        'xAG par 90 minutes': 'xAG p/90 min',
        'Actions menant a un tir par 90 minutes':'Actions créant un tir p/90 min',
        'xG + xAG par 90 minutes':'xG + xAG p/90 min'
    })
    for col in stats_cols:
        if col in data.columns:
            data[col] = data[col].astype(float) / data['Matches equivalents 90 minutes']

    for col in stats_cols:
        if col in data.columns:
            data[col] = (data[col].rank(pct=True) * 100).astype(int)

    return data, stats_cols

# Fonction pour charger un logo à partir d'une URL
def load_logo(logo_url):
    """Charge un logo depuis une URL."""
    response = requests.get(logo_url)
    image = plt.imread(BytesIO(response.content), format='png')
    return image

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

# URL des répertoires de logos par ligue
logo_directories = {
    "Premier League": "https://raw.githubusercontent.com/Rako75/footballviz/main/Premier%20League%20Logos",
    "Bundesliga": "https://raw.githubusercontent.com/Rako75/footballviz/main/Bundesliga%20Logos",
    "La Liga": "https://raw.githubusercontent.com/Rako75/footballviz/main/La%20Liga%20Logos",
    "Ligue 1": "https://raw.githubusercontent.com/Rako75/footballviz/main/Ligue%201%20Logos",
    "Serie A": "https://raw.githubusercontent.com/Rako75/footballviz/main/Serie%20A%20Logos",
}

# Streamlit application
st.title("Comparaison de joueurs - Saison 23/24")

# Sélection des paramètres
selected_position = st.selectbox("Choisissez la position", options=["Attaquant", "Défenseur", "Milieu"])
league1 = st.selectbox("Sélectionnez la ligue du premier joueur", options=list(league_files.keys()))
league2 = st.selectbox("Sélectionnez la ligue du deuxième joueur", options=list(league_files.keys()))

# Chargement des données et des joueurs
data1, params1 = load_and_preprocess_data(league_files[league1][selected_position], selected_position)
data2, params2 = load_and_preprocess_data(league_files[league2][selected_position], selected_position)

player1 = st.selectbox("Sélectionnez le premier joueur", options=data1['Joueur'].unique())
player2 = st.selectbox("Sélectionnez le deuxième joueur", options=data2['Joueur'].unique())

# Extraction des données des joueurs
player1_data = data1[data1['Joueur'] == player1].iloc[0][params1].tolist()
player2_data = data2[data2['Joueur'] == player2].iloc[0][params2].tolist()

# Extraction du club et de l'âge des joueurs
club1 = data1[data1['Joueur'] == player1].iloc[0]['Equipe']
club2 = data2[data2['Joueur'] == player2].iloc[0]['Equipe']
age1 = int(data1[data1['Joueur'] == player1].iloc[0]['Age'])
age2 = int(data2[data2['Joueur'] == player2].iloc[0]['Age'])

# Génération des URL des logos des clubs
club1_logo_url = f"{logo_directories[league1]}/{club1}.png"
club2_logo_url = f"{logo_directories[league2]}/{club2}.png"

# Charger les logos
club1_logo = load_logo(club1_logo_url)
club2_logo = load_logo(club2_logo_url)

# Configuration des titres avec club, logo et âge sous le nom du joueur
title = dict(
    title_name=f"{player1}",
    title_color='#9B3647',
    subtitle_name=f"{club1}, {age1} ans",
    subtitle_color='#ABCDEF',
    title_name_2=f"{player2}",
    title_color_2='#3282b8',
    subtitle_name_2=f"{club2}, {age2} ans",
    subtitle_color_2='#ABCDEF',
    title_fontsize=18,
    subtitle_fontsize=15,
)

# Note de bas de page
endnote = "Source : FBref | Auteur : Alex Rakotomalala"

# Instanciation de l'objet Radar
radar = Radar(background_color="#121212", patch_color="#28252C", label_color="#F0FFF0", range_color="#F0FFF0")

# Tracé du radar
fig, ax = radar.plot_radar(
    ranges=[(0, 100)] * len(params1),  # Les valeurs sont des pourcentages (0 à 100)
    params=params1,
    values=[player1_data, player2_data],
    radar_color=['#9B3647', '#3282b8'],
    title=title,
    endnote=endnote,
    alphas=[0.55, 0.5],
    compare=True
)

# Ajout des logos des clubs avec taille ajustée
zoom_factor = 0.03  # Réduction du zoom pour une taille appropriée
# Logo du club 1 (haut gauche)
image1 = OffsetImage(club1_logo, zoom=zoom_factor)
annotation_box1 = AnnotationBbox(image1, (-19, 18), frameon=False)  # Ajustement de la position
ax.add_artist(annotation_box1)
# Logo du club 2 (haut droite)
image2 = OffsetImage(club2_logo, zoom=zoom_factor)
annotation_box2 = AnnotationBbox(image2, (19, 18), frameon=False)  # Ajustement de la position
ax.add_artist(annotation_box2)
# Affichage du radar dans Streamlit
st.pyplot(fig)




# Streamlit application
st.title("Comparaison de joueurs et recherche de similitudes")

# Sélection des paramètres
selected_position = st.selectbox("Choisissez la position", options=["Attaquant", "Défenseur", "Milieu"])
base_league = st.selectbox("Choisissez la ligue du joueur de base", options=list(league_files.keys()))
comparison_league = st.selectbox("Choisissez la ligue pour trouver des joueurs similaires", options=list(league_files.keys()))

# Caractéristiques sélectionnées
selected_features = [
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
