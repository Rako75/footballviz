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
    data = pd.read_csv("df_BIG2025.csv")

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

    # Vérifier que la position est valide
    if position not in position_stats:
        raise ValueError(f"Position non reconnue : {position}")

    stats_cols = position_stats[position]

    # Convertir toutes les colonnes sauf celles en string
    for col in data.columns:
        if col not in string_cols:
            try:
                data[col] = data[col].astype(str).str.replace(",", "").str.replace("+", "").str.replace("-", "").astype(float).astype(int)
            except ValueError:
                pass  # Ignore les erreurs de conversion pour éviter de crasher le script

    return data, stats_cols

    data = data[data['Matchs joués'].astype(int) > 10]

    # Normalisation des colonnes en fonction de la position
    if position == "FW":
        stats_cols = ['Buts p/90 min', 'Passes déc. p/90 min',
                      'Buts + passes déc. p/90min', 'Distance progressive',
                      'Passes progressives', 'Receptions progressives', 'xG p/90 min', 'xAG p/90 min']
    elif position == "DF":
        stats_cols = ['Interceptions', 'Tacles gagnants', 'Dégagements',
                      'Duels aériens gagnés', 'Passes progressives', 'Contres']
    elif position == "MF":
        stats_cols = ['Passes clés', 'Actions créant un tir p/90 min', 
                      'xG + xAG p/90 min', 'Passes vers le dernier tiers',
                      'Passes progressives', 'Courses progressives']
    else:
        raise ValueError("Position non reconnue")

    data = data.rename(columns={
        'Distance progressive parcourue avec le ballon': 'Distance progressive',
        'Buts par 90 minutes':'Buts p/90 min',
        'Passes decisives par 90 minutes': 'Passes déc. p/90 min',
        'Buts + Passes decisives par 90 minutes': 'Buts + passes déc. p/90min',
        'Buts attendus par 90 minutes': 'xG p/90 min',
        'Passes décisives attendues par 90 minutes': 'xAG p/90 min',
        'Actions menant a un tir par 90 minutes':'Actions créant un tir p/90 min',
        'Somme des buts et passes attendues par 90 minutes':'xG + xAG p/90 min'
    })
    for col in stats_cols:
        if col in data.columns:
            data[col] = data[col].astype(float) / data['Matchs en 90 min']

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

# URL des répertoires de logos par ligue
logo_directories = {
    "Premier League": "https://raw.githubusercontent.com/Rako75/footballviz/main/Premier%20League%20Logos",
    "Bundliga": "https://raw.githubusercontent.com/Rako75/footballviz/main/Bundesliga%20Logos",
    "La Liga": "https://raw.githubusercontent.com/Rako75/footballviz/main/La%20Liga%20Logos",
    "Ligue 1": "https://raw.githubusercontent.com/Rako75/footballviz/main/Ligue%201%20Logos",
    "Serie A": "https://raw.githubusercontent.com/Rako75/footballviz/main/Serie%20A%20Logos",
}

# Streamlit application
# Utilisation de la barre latérale pour les sélections
st.sidebar.title("Radarchart - Saison 24/25")

selected_position = st.sidebar.selectbox("Choisissez la position", options=["FW", "DF", "MF"])
data, stats_cols = load_and_preprocess_data(selected_position)
league1 = st.sidebar.selectbox("Sélectionnez la ligue du premier joueur", options=data['Compétition'].unique())
league2 = st.sidebar.selectbox("Sélectionnez la ligue du deuxième joueur", options=data['Compétition'].unique())

# Chargement des données et des joueurs
data, params1 = load_and_preprocess_data(league1[selected_position], selected_position)
data, params2 = load_and_preprocess_data(league2[selected_position], selected_position)

player1 = st.sidebar.selectbox("Sélectionnez le premier joueur", options=data1['Joueur'].unique())
player2 = st.sidebar.selectbox("Sélectionnez le deuxième joueur", options=data2['Joueur'].unique())

# Extraction des données des joueurs
player1_data = data[data['Joueur'] == player1].iloc[0][params1].tolist()
player2_data = data[data['Joueur'] == player2].iloc[0][params2].tolist()

# Extraction du club et de l'âge des joueurs
club1 = data1[data1['Joueur'] == player1].iloc[0]['Équipe']
club2 = data2[data2['Joueur'] == player2].iloc[0]['Équipe']
age1 = int(data1[data1['Joueur'] == player1].iloc[0]['Âge'])
age2 = int(data2[data2['Joueur'] == player2].iloc[0]['Âge'])

# Génération des URL des logos des clubs
club1_logo_url = f"{logo_directories[league1]}/{club1}.png"
club2_logo_url = f"{logo_directories[league2]}/{club2}.png"

# Charger les logos
club1_logo = load_logo(club1_logo_url)
club2_logo = load_logo(club2_logo_url)



# Note de bas de page
endnote = "Source : FBref | Auteur : Alex Rakotomalala"

# Instanciation de l'objet Radar
radar = Radar(background_color="#121212", patch_color="#28252C", label_color="#F0FFF0", range_color="#F0FFF0")

# Tracé du radar
fig, ax = radar.plot_radar(
    ranges=[(0, 100)] * len(params1),  
    params=params1,
    values=[player1_data, player2_data],
    radar_color=['#9B3647', '#3282b8'],
    endnote=endnote,  # 👈 Supprime la note de bas de page
    alphas=[0.55, 0.5],
    compare=True
)

# Modifier la taille du radar chart
fig.set_size_inches(100, 8)  # Largeur x Hauteur


# Création des colonnes pour afficher les informations des joueurs
col1, col2 = st.columns(2)

# Sélection des statistiques importantes par poste
key_stat = {
    "FW": "xG p/90 min",
    "DF": "Interceptions",
    "MF": "Passes progressives"
}

# Extraction des informations du premier joueur
player1_info = data1[data1['Joueur'] == player1].iloc[0]
player1_age = int(player1_info['Age'])
player1_titularisations = int(player1_info['Titularisations'])
player1_buts = int(player1_info['Buts'])  # Prend directement la valeur réelle des buts
player1_passes = int(player1_info['Passes decisives'])  # Prend directement la valeur réelle des passes décisives
player1_stat_key = player1_info[key_stat[selected_position]]

# Extraction des informations du deuxième joueur
player2_info = data2[data2['Joueur'] == player2].iloc[0]
player2_age = int(player2_info['Age'])
player2_titularisations = int(player2_info['Titularisations'])
player2_buts = int(player2_info['Buts'])  # Valeur réelle des buts
player2_passes = int(player2_info['Passes décisives'])  # Valeur réelle des passes décisives
player2_stat_key = player2_info[key_stat[selected_position]]




# Organisation de la mise en page
col1, col2, col3 = st.columns([6, 15, 6])  # Colonnes gauche, centre (radar), droite

# Colonne 1 : Infos du joueur 1
with col1:
    st.image(club1_logo, width=100)
    st.subheader(f"{player1} (rouge)")  # Nom de la couleur en français
    st.write(f"**Âge :** {player1_age}")
    st.write(f"**Titularisations :** {player1_titularisations}")
    st.write(f"**Buts :** {player1_buts}")
    st.write(f"**Passes déc. :** {player1_passes}")
    st.write(f"**{key_stat[selected_position]} :** {player1_stat_key}")

# Colonne 2 : Radar Chart (plein centre)
with col2:
    st.pyplot(fig)  # Affiche le radar chart au centre

# Colonne 3 : Infos du joueur 2
with col3:
    st.image(club2_logo, width=100)
    st.subheader(f"{player2} (bleu)")  # Nom de la couleur en français
    st.write(f"**Âge :** {player2_age}")
    st.write(f"**Titularisations :** {player2_titularisations}")
    st.write(f"**Buts :** {player2_buts}")
    st.write(f"**Passes déc. :** {player2_passes}")
    st.write(f"**{key_stat[selected_position]} :** {player2_stat_key}")

