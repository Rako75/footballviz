import pandas as pd
import numpy as np
import streamlit as st
from soccerplots.radar_chart import Radar
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import requests
from io import BytesIO

# Fonction pour charger et prétraiter les données
def load_and_preprocess_data(position):
    data = pd.read_csv('df_BIG2025.csv', sep=',', encoding='utf-8')

    # Sélection des colonnes à garder en string
    string_cols = ["Joueur", "Nationalité", "Position", "Équipe", "Compétition"]

    # Définition des stats en fonction de la position
    position_stats = {
        "FW": ['Buts p/90 min', 'Passes déc. p/90 min', 'Buts + passes déc. p/90min',
               'Distance progressive', 'Passes progressives', 'Receptions progressives', 'xG p/90 min', 'xAG p/90 min'],
        "DF": ['Interceptions', 'Tacles gagnants', 'Dégagements', 'Duels aériens gagnés', 'Passes progressives', 'Contres'],
        "MF": ['Passes clés', 'Actions créant un tir p/90 min', 'xG + xAG p/90 min',
               'Passes vers le dernier tiers', 'Passes progressives', 'Courses progressives']
    }

    if position not in position_stats:
        raise ValueError(f"Position non reconnue : {position}")

    stats_cols = position_stats[position]


    # Filtrer les joueurs avec plus de 10 matchs
    data = data[data['Matchs joués'].astype(int) > 10]

    # Renommage des colonnes
    data = data.rename(columns={
        'Distance progressive parcourue avec le ballon': 'Distance progressive',
        'Buts par 90 minutes': 'Buts p/90 min',
        'Passes decisives par 90 minutes': 'Passes déc. p/90 min',
        'Buts + Passes decisives par 90 minutes': 'Buts + passes déc. p/90min',
        'Buts attendus par 90 minutes': 'xG p/90 min',
        'Passes décisives attendues par 90 minutes': 'xAG p/90 min',
        'Actions menant a un tir par 90 minutes': 'Actions créant un tir p/90 min',
        'Somme des buts et passes attendues par 90 minutes': 'xG + xAG p/90 min'
    })
    
    # Normalisation et ranking des statistiques
    for col in stats_cols:
        if col in data.columns:
            data[col] = data[col].astype(float) / data['Matchs en 90 min']
            data[col] = (data[col].rank(pct=True) * 100).astype(int)

    return data, stats_cols

# Fonction pour charger un logo à partir d'une URL
def load_logo(logo_url):
    response = requests.get(logo_url)
    image = plt.imread(BytesIO(response.content), format='png')
    return image

# URL des répertoires de logos par ligue
logo_directories = {
    "Premier League": "https://raw.githubusercontent.com/Rako75/footballviz/main/Premier%20League%20Logos",
    "Bundesliga": "https://raw.githubusercontent.com/Rako75/footballviz/main/Bundesliga%20Logos",
    "La Liga": "https://raw.githubusercontent.com/Rako75/footballviz/main/La%20Liga%20Logos",
    "Ligue 1": "https://raw.githubusercontent.com/Rako75/footballviz/main/Ligue%201%20Logos",
    "Serie A": "https://raw.githubusercontent.com/Rako75/footballviz/main/Serie%20A%20Logos",
}

# Streamlit Application
st.sidebar.title("Radarchart - Saison 24/25")

selected_position = st.sidebar.selectbox("Choisissez la position", options=["FW", "DF", "MF"])
data, stats_cols = load_and_preprocess_data(selected_position)

league1 = st.sidebar.selectbox("Sélectionnez la ligue du premier joueur", options=data['Compétition'].unique())
league2 = st.sidebar.selectbox("Sélectionnez la ligue du deuxième joueur", options=data['Compétition'].unique())

data1 = data[data['Compétition'] == league1]
data2 = data[data['Compétition'] == league2]

player1 = st.sidebar.selectbox("Sélectionnez le premier joueur", options=data1['Joueur'].unique())
player2 = st.sidebar.selectbox("Sélectionnez le deuxième joueur", options=data2['Joueur'].unique())

# Extraction des données des joueurs
player1_data = data1[data1['Joueur'] == player1].iloc[0][stats_cols].tolist()
player2_data = data2[data2['Joueur'] == player2].iloc[0][stats_cols].tolist()

# Extraction du club et de l'âge des joueurs
club1 = data1[data1['Joueur'] == player1].iloc[0]['Équipe']
club2 = data2[data2['Joueur'] == player2].iloc[0]['Équipe']

# Génération des URL des logos des clubs
club1_logo_url = f"{logo_directories[league1]}/{club1}.png"
club2_logo_url = f"{logo_directories[league2]}/{club2}.png"

# Charger les logos
club1_logo = load_logo(club1_logo_url)
club2_logo = load_logo(club2_logo_url)

# Radar Chart
endnote = "Source : FBref | Auteur : Alex Rakotomalala"
radar = Radar(background_color="#121212", patch_color="#28252C", label_color="#F0FFF0", range_color="#F0FFF0")

fig, ax = radar.plot_radar(
    ranges=[(0, 100)] * len(stats_cols),  
    params=stats_cols,
    values=[player1_data, player2_data],
    radar_color=['#9B3647', '#3282b8'],
    endnote=endnote,
    alphas=[0.55, 0.5],
    compare=True
)

st.pyplot(fig)

# Affichage des infos des joueurs
col1, col2 = st.columns(2)

with col1:
    st.image(club1_logo, width=100)
    st.subheader(f"{player1} (rouge)")

with col2:
    st.image(club2_logo, width=100)
    st.subheader(f"{player2} (bleu)")
