import pandas as pd
import numpy as np
import streamlit as st
from soccerplots.radar_chart import Radar

# Importation des données des ligues
pl_data = pd.read_csv('Premier_League_Attaquant.csv')
bundesliga_data = pd.read_csv('Bundesliga_Attaquant.csv')
laliga_data = pd.read_csv('La_Liga_Attaquant.csv')
ligue1_data = pd.read_csv('Ligue_1_Attaquant.csv')
seriea_data = pd.read_csv('Serie_A_Attaquant.csv')

# Filtrer les données pour les joueurs ayant joué plus de 10 matchs
def preprocess_data(data):
    data = data[data['Matchs joues'].astype(int) > 10]
    data = data.rename(columns={'Distance progressive parcourue avec le ballon': 'Distance progressive'})
    cols_to_int = ['Buts', 'Passes decisives', 'Buts + Passes decisives', 'Distance progressive', 'Passes progressives', 'Receptions progressives']
    data[cols_to_int] = data[cols_to_int].astype(int)
    
    for col in ['Distance progressive', 'Passes progressives', 'Receptions progressives']:
        data[col] = data[col] / data['Matches equivalents 90 minutes']

    percentile_cols = [
        'Buts par 90 minutes', 'Passes decisives par 90 minutes',
        'Buts + Passes decisives par 90 minutes', 'Distance progressive',
        'Passes progressives', 'Receptions progressives', 'xG par 90 minutes', 'xAG par 90 minutes'
    ]
    for col in percentile_cols:
        data[col] = (data[col].rank(pct=True) * 100).astype(int)
    return data

# Prétraiter les données de chaque ligue
pl_data = preprocess_data(pl_data)
bundesliga_data = preprocess_data(bundesliga_data)
laliga_data = preprocess_data(laliga_data)
ligue1_data = preprocess_data(ligue1_data)
seriea_data = preprocess_data(seriea_data)

# Liste des paramètres
params = [
    'Buts par 90 minutes', 'Passes decisives par 90 minutes',
    'Buts + Passes decisives par 90 minutes', 'Distance progressive',
    'Passes progressives', 'Receptions progressives', 'xG par 90 minutes', 'xAG par 90 minutes'
]

# Calcul des valeurs maximales pour chaque paramètre parmi toutes les ligues
def calculate_max_values():
    all_data = pd.concat([pl_data, bundesliga_data, laliga_data, ligue1_data, seriea_data], axis=0)
    max_values = {param: all_data[param].max() for param in params}
    return max_values

max_values = calculate_max_values()

# Streamlit application
st.title("Comparaison de Joueurs - Football 2023")

# Sélection de la ligue et des joueurs
league1 = st.selectbox("Sélectionnez la ligue du premier joueur", options=["Premier League", "Bundesliga", "La Liga", "Ligue 1", "Serie A"])
league2 = st.selectbox("Sélectionnez la ligue du deuxième joueur", options=["Premier League", "Bundesliga", "La Liga", "Ligue 1", "Serie A"])

# Sélection des joueurs en fonction de la ligue
if league1 == "Premier League":
    player1 = st.selectbox("Sélectionnez le premier joueur", options=pl_data['Joueur'].unique())
elif league1 == "Bundesliga":
    player1 = st.selectbox("Sélectionnez le premier joueur", options=bundesliga_data['Joueur'].unique())
elif league1 == "La Liga":
    player1 = st.selectbox("Sélectionnez le premier joueur", options=laliga_data['Joueur'].unique())
elif league1 == "Ligue 1":
    player1 = st.selectbox("Sélectionnez le premier joueur", options=ligue1_data['Joueur'].unique())
else:
    player1 = st.selectbox("Sélectionnez le premier joueur", options=seriea_data['Joueur'].unique())

if league2 == "Premier League":
    player2 = st.selectbox("Sélectionnez le deuxième joueur", options=pl_data['Joueur'].unique())
elif league2 == "Bundesliga":
    player2 = st.selectbox("Sélectionnez le deuxième joueur", options=bundesliga_data['Joueur'].unique())
elif league2 == "La Liga":
    player2 = st.selectbox("Sélectionnez le deuxième joueur", options=laliga_data['Joueur'].unique())
elif league2 == "Ligue 1":
    player2 = st.selectbox("Sélectionnez le deuxième joueur", options=ligue1_data['Joueur'].unique())
else:
    player2 = st.selectbox("Sélectionnez le deuxième joueur", options=seriea_data['Joueur'].unique())

# Données des joueurs sélectionnés
if league1 == "Premier League":
    player1_data = pl_data[pl_data['Joueur'] == player1].iloc[0][params].tolist()
elif league1 == "Bundesliga":
    player1_data = bundesliga_data[bundesliga_data['Joueur'] == player1].iloc[0][params].tolist()
elif league1 == "La Liga":
    player1_data = laliga_data[laliga_data['Joueur'] == player1].iloc[0][params].tolist()
elif league1 == "Ligue 1":
    player1_data = ligue1_data[ligue1_data['Joueur'] == player1].iloc[0][params].tolist()
else:
    player1_data = seriea_data[seriea_data['Joueur'] == player1].iloc[0][params].tolist()

if league2 == "Premier League":
    player2_data = pl_data[pl_data['Joueur'] == player2].iloc[0][params].tolist()
elif league2 == "Bundesliga":
    player2_data = bundesliga_data[bundesliga_data['Joueur'] == player2].iloc[0][params].tolist()
elif league2 == "La Liga":
    player2_data = laliga_data[laliga_data['Joueur'] == player2].iloc[0][params].tolist()
elif league2 == "Ligue 1":
    player2_data = ligue1_data[ligue1_data['Joueur'] == player2].iloc[0][params].tolist()
else:
    player2_data = seriea_data[seriea_data['Joueur'] == player2].iloc[0][params].tolist()

# Configuration des titres
title = dict(
    title_name=player1,
    title_color='#9B3647',
    subtitle_name=league1,
    subtitle_color='#ABCDEF',
    title_name_2=player2,
    title_color_2='#3282b8',
    subtitle_name_2=league2,
    subtitle_color_2='#ABCDEF',
    title_fontsize=18,
    subtitle_fontsize=15,
)

# Note de bas de page
endnote = "Source : FBref | Auteur : Alex Rakotomalala"

# Instanciation de l'objet Radar
radar = Radar(background_color="#121212", patch_color="#28252C", label_color="#F0FFF0", range_color="#F0FFF0")

# Ajustement des plages pour chaque axe en fonction des valeurs maximales
ranges = [(0, max_values[param]) for param in params]

# Tracé du radar
fig, ax = radar.plot_radar(
    ranges=ranges,
    params=params,
    values=[player1_data, player2_data],
    radar_color=['#9B3647', '#3282b8'],
    title=title,
    endnote=endnote,
    alphas=[0.55, 0.5],
    compare=True
)

# Ajouter les valeurs sur le radar à l'intérieur du graphique
for i, param in enumerate(params):
    for j, player_data in enumerate([player1_data, player2_data]):
        # Normaliser les coordonnées pour être à l'intérieur du radar (0.8 fois la valeur)
        value = player_data[i] / max_values[param]  # Valeur normalisée
        radius = value * 0.8  # Ajuster la distance pour que les textes restent à l'intérieur
        angle = np.radians(360 * i / len(params))  # Calculer l'angle pour chaque paramètre
        
        # Calcul des coordonnées X et Y à partir de l'angle et du rayon
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        
        # Ajouter la valeur comme annotation dans le graphique
        ax.text(
            x, y, f'{player_data[i]}', horizontalalignment='center',
            verticalalignment='center', fontsize=10, color='white'
        )

# Affichage du radar dans Streamlit
st.pyplot(fig)
