import pandas as pd
import numpy as np
import streamlit as st
from soccerplots.radar_chart import Radar
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import requests
from io import BytesIO

# Fonction pour charger et prétraiter les données
def load_and_preprocess_data(file_path, competition, position):
    data = pd.read_csv(file_path)
    data = data[(data['Matchs joués'].astype(int) > 10) & (data['Compétition'] == competition)]

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
    
    stats_cols = get_stats_by_position(position)

    return data, stats_cols

# Fonction pour charger un logo à partir d'une URL
def load_logo(logo_url):
    response = requests.get(logo_url)
    image = plt.imread(BytesIO(response.content), format='png')
    return image

# Streamlit application
st.title("Comparaison de joueurs - Saison 23/24")

# Sélection de la compétition
competitions = ["Ligue 1", "Premier League", "La Liga", "Serie A", "Bundesliga"]
selected_competition = st.selectbox("Choisissez la compétition", options=competitions)

# Sélection des paramètres
selected_position = st.selectbox("Choisissez la position", options=[
    "Défenseur Central", "Arrière Droit", "Arrière Gauche", "Milieu Défensif Central", "Milieu Central",
    "Milieu Offensif", "Ailier Droit", "Ailier Gauche", "Attaquant Central", "Deuxième Attaquant"
])

# Chargement des données et des joueurs
data, params = load_and_preprocess_data("df_BIG2025.csv", selected_competition, selected_position)

player1 = st.selectbox("Sélectionnez le premier joueur", options=data['Joueur'].unique())
player2 = st.selectbox("Sélectionnez le deuxième joueur", options=data['Joueur'].unique())

# Extraction des données des joueurs
player1_data = data[data['Joueur'] == player1].iloc[0][params].tolist()
player2_data = data[data['Joueur'] == player2].iloc[0][params].tolist()

# Extraction du club et de l'âge des joueurs
club1 = data[data['Joueur'] == player1].iloc[0]['Équipe']
club2 = data[data['Joueur'] == player2].iloc[0]['Équipe']
age1 = int(data[data['Joueur'] == player1].iloc[0]['Âge'])
age2 = int(data[data['Joueur'] == player2].iloc[0]['Âge'])

# Génération des URL des logos des clubs
club1_logo_url = f"https://raw.githubusercontent.com/Rako75/footballviz/main/{club1}.png"
club2_logo_url = f"https://raw.githubusercontent.com/Rako75/footballviz/main/{club2}.png"

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
    ranges=[(0, 100)] * len(params),
    params=params,
    values=[player1_data, player2_data],
    radar_color=['#9B3647', '#3282b8'],
    title=title,
    endnote=endnote,
    alphas=[0.55, 0.5],
    compare=True
)

# Ajout des logos des clubs
zoom_factor = 0.03  # Taille adaptée
image1 = OffsetImage(club1_logo, zoom=zoom_factor)
annotation_box1 = AnnotationBbox(image1, (-19, 18), frameon=False)
ax.add_artist(annotation_box1)
image2 = OffsetImage(club2_logo, zoom=zoom_factor)
annotation_box2 = AnnotationBbox(image2, (19, 18), frameon=False)
ax.add_artist(annotation_box2)

# Affichage du radar dans Streamlit
st.pyplot(fig)
