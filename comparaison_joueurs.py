import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import requests
from io import BytesIO
import matplotlib.pyplot as plt

# Fonction pour charger et prétraiter les données
def load_and_preprocess_data(file_path, position):
    data = pd.read_csv(file_path)
    data = data[data['Matchs joués'].astype(int) > 10]

    # Normalisation des colonnes en fonction de la position
    if position == "Attaquant":
        stats_cols = ['Buts p/90 min', 'Passes déc. p/90 min',
                      'Buts + passes déc. p/90min', 'Distance progressive',
                      'Passes progressives', 'Réceptions progressives', 'xG p/90 min', 'xAG p/90 min']
    elif position == "Défenseur":
        stats_cols = ['Interceptions', 'Tacles gagnants', 'Dégagements',
                      'Duels défensifs gagnés', 'Passes progressives', 'Duels aériens gagnés']
    elif position == "Milieu":
        stats_cols = ['Passes clés', 'Actions créant un tir p/90 min', 
                      'xG + xAG p/90 min', 'Passes dans le dernier tiers',
                      'Passes progressives', 'Courses progressives']
    else:
        raise ValueError("Position non reconnue")

    data = data.rename(columns={
        'Distance progressive parcourue avec le ballon': 'Distance progressive',
        'Buts par 90 minutes':'Buts p/90 min',
        'Passes décisives par 90 minutes': 'Passes déc. p/90 min',
        'Buts + Passes décisives par 90 minutes': 'Buts + passes déc. p/90min',
        'Buts attendus par 90 minutes': 'xG p/90 min',
        'Passes décisives attendues par 90 minutes': 'xAG p/90 min',
        'Actions menant à un tir par 90 minutes':'Actions créant un tir p/90 min',
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
# Utilisation de la barre latérale pour les sélections
st.sidebar.title("Radarchart - Saison 24/25")

selected_position = st.sidebar.selectbox("Choisissez la position", options=["Attaquant", "Défenseur", "Milieu"])
league1 = st.sidebar.selectbox("Sélectionnez la ligue du premier joueur", options=list(league_files.keys()))
league2 = st.sidebar.selectbox("Sélectionnez la ligue du deuxième joueur", options=list(league_files.keys()))

# Chargement des données et des joueurs
data1, params1 = load_and_preprocess_data(league_files[league1][selected_position], selected_position)
data2, params2 = load_and_preprocess_data(league_files[league2][selected_position], selected_position)

player1 = st.sidebar.selectbox("Sélectionnez le premier joueur", options=data1['Joueur'].unique())
player2 = st.sidebar.selectbox("Sélectionnez le deuxième joueur", options=data2['Joueur'].unique())

# Extraction des données des joueurs
player1_data = data1[data1['Joueur'] == player1].iloc[0][params1].tolist()
player2_data = data2[data2['Joueur'] == player2].iloc[0][params2].tolist()

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

# Création du radar chart avec Plotly pour permettre l'interaction et le zoom
fig = go.Figure()

fig.add_trace(go.Scatterpolar(
    r=player1_data,
    theta=params1,
    fill='toself',
    name=player1,
    line=dict(color='#9B3647')
))

fig.add_trace(go.Scatterpolar(
    r=player2_data,
    theta=params2,
    fill='toself',
    name=player2,
    line=dict(color='#3282b8')
))

# Mise en forme
fig.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[0, 100]  # Plage de valeurs des axes
        )
    ),
    showlegend=True,
    title="Comparaison des Joueurs",
    title_x=0.5,
    template="plotly_dark"
)

# Affichage du graphique interactif avec zoom
st.plotly_chart(fig)
