import pandas as pd
import numpy as np
import streamlit as st
from soccerplots.radar_chart import Radar
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import requests
from io import BytesIO
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity

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
    response = requests.get(logo_url)
    image = plt.imread(BytesIO(response.content), format='png')
    return image

# Fonction pour trouver des joueurs similaires
def find_similar_players(data, player_data, selected_features, top_n=5):
    feature_data = data[selected_features]
    similarity = cosine_similarity(feature_data, [player_data])
    similarity_scores = pd.Series(similarity.flatten(), index=data['Joueur'])
    similar_players = similarity_scores.sort_values(ascending=False)[:top_n]
    return list(zip(similar_players.index, similar_players.values))

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
st.title("Analyse et Recherche de Joueurs - Saison 23/24")

# --- Radar Chart et Comparaison ---
st.header("Radar Chart : Comparaison de Joueurs")

# Sélection des paramètres pour le radar
selected_position = st.selectbox("Choisissez la position", options=["Attaquant", "Défenseur", "Milieu"])
league1 = st.selectbox("Sélectionnez la ligue du premier joueur", options=list(league_files.keys()))
league2 = st.selectbox("Sélectionnez la ligue du deuxième joueur", options=list(league_files.keys()))

data1, params1 = load_and_preprocess_data(league_files[league1][selected_position], selected_position)
data2, params2 = load_and_preprocess_data(league_files[league2][selected_position], selected_position)

player1 = st.selectbox("Sélectionnez le premier joueur", options=data1['Joueur'].unique())
player2 = st.selectbox("Sélectionnez le deuxième joueur", options=data2['Joueur'].unique())

player1_data = data1[data1['Joueur'] == player1].iloc[0][params1].tolist()
player2_data = data2[data2['Joueur'] == player2].iloc[0][params2].tolist()

club1 = data1[data1['Joueur'] == player1].iloc[0]['Equipe']
club2 = data2[data2['Joueur'] == player2].iloc[0]['Equipe']
age1 = int(data1[data1['Joueur'] == player1].iloc[0]['Age'])
age2 = int(data2[data2['Joueur'] == player2].iloc[0]['Age'])

club1_logo_url = f"{logo_directories[league1]}/{club1}.png"
club2_logo_url = f"{logo_directories[league2]}/{club2}.png"

club1_logo = load_logo(club1_logo_url)
club2_logo = load_logo(club2_logo_url)

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

endnote = "Source : FBref | Auteur : Alex Rakotomalala"

radar = Radar(background_color="#121212", patch_color="#28252C", label_color="#F0FFF0", range_color="#F0FFF0")

fig, ax = radar.plot_radar(
    ranges=[(0, 100)] * len(params1),
    params=params1,
    values=[player1_data, player2_data],
    radar_color=['#9B3647', '#3282b8'],
    title=title,
    endnote=endnote,
    alphas=[0.55, 0.5],
    compare=True
)

zoom_factor = 0.03
image1 = OffsetImage(club1_logo, zoom=zoom_factor)
annotation_box1 = AnnotationBbox(image1, (-19, 18), frameon=False)
ax.add_artist(annotation_box1)

image2 = OffsetImage(club2_logo, zoom=zoom_factor)
annotation_box2 = AnnotationBbox(image2, (19, 18), frameon=False)
ax.add_artist(annotation_box2)

st.pyplot(fig)

# --- Recherche de Joueurs Similaires ---
st.header("Recherche de Joueurs Similaires")

comparison_league = st.selectbox("Choisissez la ligue pour la recherche", options=list(league_files.keys()))
comparison_data, comparison_features = load_and_preprocess_data(league_files[comparison_league][selected_position], selected_position)

player_base = st.selectbox("Choisissez le joueur de référence", options=data1['Joueur'].unique())
player_base_data = data1[data1['Joueur'] == player_base][params1].iloc[0].tolist()

similar_players = find_similar_players(comparison_data, player_base_data, comparison_features)

st.write(f"Joueurs similaires à **{player_base}** dans **{comparison_league}** :")
for player, score in similar_players:
    st.write(f"- {player}: {score:.2f}")
