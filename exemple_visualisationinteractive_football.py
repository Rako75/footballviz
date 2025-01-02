import pandas as pd
import numpy as np
import streamlit as st
from soccerplots.radar_chart import Radar

# Fonction pour charger et prétraiter les données
def load_and_preprocess_data(file_path, position):
    data = pd.read_csv(file_path)
    data = data[data['Matchs joues'].astype(int) > 10]
    
    # Normalisation des colonnes en fonction de la position
    if position == "Attaquant":
        stats_cols = ['Buts par 90 minutes', 'Passes decisives par 90 minutes',
                      'Buts + Passes decisives par 90 minutes', 'Distance progressive',
                      'Passes progressives', 'Receptions progressives', 'xG par 90 minutes', 'xAG par 90 minutes']
    elif position == "Défenseur":
        stats_cols = ['Interceptions', 'Tacles', 'Degagements',
                      'Duels aeriens gagnes', 'Passes progressives', 'Contres']
    elif position == "Milieu":
        stats_cols = ['Passes cles', 'Actions menant a un tir par 90 minutes', 
                      'xG + xAG par 90 minutes', 'Passes vers le dernier tiers',
                      'Passes progressives', 'Courses progressives']
    else:
        raise ValueError("Position non reconnue")
    
    data = data.rename(columns={'Distance progressive parcourue avec le ballon': 'Distance progressive'})
    for col in stats_cols:
        if col in data.columns:
            data[col] = data[col].astype(float) / data['Matches equivalents 90 minutes']

    for col in stats_cols:
        if col in data.columns:
            data[col] = (data[col].rank(pct=True) * 100).astype(int)

    return data, stats_cols

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

# Ajouter un fond personnalisé depuis GitHub
st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://raw.githubusercontent.com/Rako75/footballviz/fb5a03683bf8a158475070c0d0dfdd04169c980a/PSG.jpg");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    </style>
    """, unsafe_allow_html=True
)

# Streamlit application
st.title("Comparaison de Joueurs - Football 2023")

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

# Configuration des titres avec club et âge sous le nom du joueur
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

# Affichage du radar dans Streamlit
st.pyplot(fig)
