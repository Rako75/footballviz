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
    
    # Sélection des statistiques en fonction de la position
    stats_cols = get_stats_by_position(position)
    
    for col in stats_cols:
        if col in data.columns:
            data[col] = data[col].astype(float) / data['Matches equivalents 90 minutes']

    for col in stats_cols:
        if col in data.columns:
            data[col] = (data[col].rank(pct=True) * 100).astype(int)

    return data, stats_cols

# Fonction pour récupérer les statistiques par position
def get_stats_by_position(position):
    stats_by_position = {
        "Gardien de But": ["Arrêts (%)", "Buts encaissés par 90 min", "Arrêts sur tirs cadrés (%)", "Sorties réussies (%)", "Passes réussies (%)"],
        "Défenseur Central": ["Duels aériens gagnés (%)", "Interceptions par 90 min", "Tacles réussis (%)", "Passes progressives par 90 min", "Duels défensifs gagnés (%)"],
        "Arrière Droit": ["Centres réussis (%)", "Passes progressives par 90 min", "Tacles réussis (%)", "Courses progressives par 90 min", "Passes clés par 90 min"],
        "Arrière Gauche": ["Centres réussis (%)", "Passes progressives par 90 min", "Tacles réussis (%)", "Courses progressives par 90 min", "Passes clés par 90 min"],
        "Milieu Défensif Central": ["Interceptions par 90 min", "Tacles réussis (%)", "Passes réussies (%)", "Pressing réussi (%)", "Passes progressives par 90 min"],
        "Milieu Central": ["Passes réussies (%)", "Passes clés par 90 min", "Pressing réussi (%)", "Dribbles réussis (%)", "Ballons récupérés par 90 min"],
        "Milieu Offensif": ["Passes clés par 90 min", "Dribbles réussis (%)", "Passes progressives par 90 min", "Buts par 90 min", "xA par 90 min"],
        "Ailier Droit": ["Dribbles réussis (%)", "Passes clés par 90 min", "Buts par 90 min", "xA par 90 min", "Courses progressives par 90 min"],
        "Ailier Gauche": ["Dribbles réussis (%)", "Passes clés par 90 min", "Buts par 90 min", "xA par 90 min", "Courses progressives par 90 min"],
        "Attaquant Central": ["Buts par 90 min", "xG par 90 min", "Tirs cadrés (%)", "Duels aériens gagnés (%)", "Passes clés par 90 min"],
        "Deuxième Attaquant": ["Buts par 90 min", "Passes clés par 90 min", "Dribbles réussis (%)", "Pressing réussi (%)", "xA par 90 min"]
    }
    return stats_by_position.get(position, [])

# Streamlit application
st.title("Comparaison de joueurs - Saison 23/24")

# Sélection de la position
positions = ["Gardien de But", "Défenseur Central", "Arrière Droit", "Arrière Gauche", "Milieu Défensif Central", "Milieu Central", "Milieu Offensif", "Ailier Droit", "Ailier Gauche", "Attaquant Central", "Deuxième Attaquant"]
selected_position = st.selectbox("Choisissez la position", options=positions)

# Chargement des données
file_path = "df_BIG2025.csv"
data, params = load_and_preprocess_data(file_path, selected_position)

# Sélection des joueurs
player1 = st.selectbox("Sélectionnez le premier joueur", options=data['Joueur'].unique())
player2 = st.selectbox("Sélectionnez le deuxième joueur", options=data['Joueur'].unique())

# Extraction des données des joueurs
player1_data = data[data['Joueur'] == player1].iloc[0][params].tolist()
player2_data = data[data['Joueur'] == player2].iloc[0][params].tolist()

# Tracé du radar
radar = Radar(background_color="#121212", patch_color="#28252C", label_color="#F0FFF0", range_color="#F0FFF0")
fig, ax = radar.plot_radar(
    ranges=[(0, 100)] * len(params),  # Les valeurs sont des pourcentages (0 à 100)
    params=params,
    values=[player1_data, player2_data],
    radar_color=['#9B3647', '#3282b8'],
    compare=True
)

# Affichage du radar dans Streamlit
st.pyplot(fig)
