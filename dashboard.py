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
    position_stats = {
        "Attaquant Central": ['Buts p/90 min', 'Passes déc. p/90 min', 'Buts + passes déc. p/90min', 'Distance progressive', 'Passes progressives', 'Réceptions progressives', 'xG p/90 min', 'xAG p/90 min'],
        "Défenseur Central": ['Interceptions', 'Tacles', 'Dégagements', 'Duels aériens gagnés', 'Passes progressives', 'Contres'],
        "Milieu Central": ['Passes clés', 'Actions créant un tir p/90 min', 'xG + xAG p/90 min', 'Passes vers le dernier tiers', 'Passes progressives', 'Courses progressives'],
        "Ailier Droit": ['Dribbles réussis', 'Passes progressives', 'Centres réussis', 'xG p/90 min', 'xAG p/90 min'],
        "Ailier Gauche": ['Dribbles réussis', 'Passes progressives', 'Centres réussis', 'xG p/90 min', 'xAG p/90 min'],
        "Milieu Offensif": ['Passes clés', 'Passes progressives', 'Dribbles réussis', 'xG p/90 min', 'xAG p/90 min'],
        "Milieu Défensif Central": ['Interceptions', 'Tacles', 'Passes progressives', 'Courses progressives', 'Passes clés'],
        "Arrière Droit": ['Tacles', 'Interceptions', 'Passes progressives', 'Centres réussis', 'Courses progressives'],
        "Arrière Gauche": ['Tacles', 'Interceptions', 'Passes progressives', 'Centres réussis', 'Courses progressives'],
        "Gardien de But": ['Arrêts', 'Taux d’arrêts', 'Passes longues réussies', 'Relances réussies', 'xG encaissés évités'],
        "Milieu Droit": ['Passes clés', 'Dribbles réussis', 'Passes progressives', 'Centres réussis', 'Courses progressives'],
        "Milieu Gauche": ['Passes clés', 'Dribbles réussis', 'Passes progressives', 'Centres réussis', 'Courses progressives'],
        "Deuxième Attaquant": ['Buts p/90 min', 'Passes déc. p/90 min', 'Dribbles réussis', 'Passes progressives', 'xG p/90 min', 'xAG p/90 min']
    }

    if position not in position_stats:
        raise ValueError("Position non reconnue")

    stats_cols = position_stats[position]

    data = data.rename(columns={
        'Distance progressive parcourue avec le ballon': 'Distance progressive',
        'Buts par 90 minutes': 'Buts p/90 min',
        'Passes decisives par 90 minutes': 'Passes déc. p/90 min',
        'Buts + Passes decisives par 90 minutes': 'Buts + passes déc. p/90min',
        'xG par 90 minutes': 'xG p/90 min',
        'xAG par 90 minutes': 'xAG p/90 min',
        'Actions menant a un tir par 90 minutes': 'Actions créant un tir p/90 min',
        'xG + xAG par 90 minutes': 'xG + xAG p/90 min'
    })
    
    for col in stats_cols:
        if col in data.columns:
            data[col] = data[col].astype(float) / data['Matches equivalents 90 minutes']
            data[col] = (data[col].rank(pct=True) * 100).astype(int)

    return data, stats_cols

# Fonction pour afficher le radar chart
def plot_radar_chart(player_data, stats_cols, player_name):
    values = player_data[stats_cols].values.flatten().tolist()
    ranges = [(0, 100) for _ in stats_cols]
    radar = Radar()
    fig, ax = radar.plot_radar(
        ranges=ranges,
        params=stats_cols,
        values=values,
        title=player_name,
        compare=False
    )
    st.pyplot(fig)

# Streamlit UI
st.title("Analyse des performances des joueurs de football")
file_path = st.file_uploader("Téléchargez le fichier CSV des données des joueurs", type=["csv"])

if file_path:
    position = st.selectbox("Sélectionnez une position", [
        "Attaquant Central", "Défenseur Central", "Milieu Central", "Ailier Droit", "Ailier Gauche", "Milieu Offensif", "Milieu Défensif Central", "Arrière Droit", "Arrière Gauche", "Gardien de But", "Milieu Droit", "Milieu Gauche", "Deuxième Attaquant"
    ])
    
    data, stats_cols = load_and_preprocess_data(file_path, position)
    player_name = st.selectbox("Sélectionnez un joueur", data['Nom'].unique())
    player_data = data[data['Nom'] == player_name]
    
    if not player_data.empty:
        st.write("### Statistiques du joueur")
        st.dataframe(player_data[stats_cols])
        plot_radar_chart(player_data, stats_cols, player_name)
