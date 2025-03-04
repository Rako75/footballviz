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
    data = data[data['Matchs joués'].astype(int) > 10]
    
    # Sélection des statistiques en fonction de la position
    stats_cols = get_stats_by_position(position)
    
    for col in stats_cols:
        if col in data.columns:
            data[col] = data[col].astype(float) / data['Matchs en 90 min']

    for col in stats_cols:
        if col in data.columns:
            data[col] = (data[col].rank(pct=True) * 100).astype(int)

    return data, stats_cols

# Fonction pour récupérer les statistiques par position
def get_stats_by_position(position):
    stats_by_position = {
        "Défenseur Central": ["Duels aériens gagnés", "Interceptions", "Tacles réussis", "Passes progressives", "Duels défensifs gagnés"],
        "Arrière Droit": ["Centres dans la surface", "Passes progressives", "Tacles réussis", "Courses progressives", "Passes clés"],
        "Arrière Gauche": ["Centres dans la surface", "Passes progressives", "Tacles réussis", "Courses progressives", "Passes clés"],
        "Milieu Défensif Central": ["Interceptions", "Tacles réussis", "Passes réussies", "Duels défensifs gagnés", "Passes progressives"],
        "Milieu Central": ["Passes réussies", "Passes clés", "Duels défensifs gagnés", "Dribbles réussis", "Ballons récupérés"],
        "Milieu Offensif": ["Passes clés", "Dribbles réussis", "Passes progressives", "Buts", "Passes attendues (xA)"],
        "Ailier Droit": ["Dribbles réussis", "Passes clés", "Buts", "Passes attendues (xA)", "Courses progressives"],
        "Ailier Gauche": ["Dribbles réussis", "Passes clés", "Buts", "Passes attendues (xA)", "Courses progressives"],
        "Attaquant Central": ["Buts", "Buts attendus (xG)", "Tirs cadrés", "Duels aériens gagnés", "Passes clés"],
        "Deuxième Attaquant": ["Buts", "Passes clés", "Dribbles réussis", "Duels défensifs gagnés", "Passes attendues (xA)"]
    }
    return stats_by_position.get(position, [])

# Streamlit application
st.title("Comparaison de joueurs - Saison 23/24")

# Sélection de la position
positions = ["Défenseur Central", "Arrière Droit", "Arrière Gauche", "Milieu Défensif Central", "Milieu Central", "Milieu Offensif", "Ailier Droit", "Ailier Gauche", "Attaquant Central", "Deuxième Attaquant"]
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
