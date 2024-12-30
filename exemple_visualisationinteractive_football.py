# -*- coding: utf-8 -*-
# Exemple avec Streamlit pour comparer deux joueurs sur un même graphique radar

import pandas as pd
import numpy as np
import streamlit as st
from mplsoccer import Radar, FontManager
import matplotlib.pyplot as plt

# Importation des données
data = pd.read_csv('Premier_League_Attaquant.csv')
data = data[data['Matchs joues'].astype(int) > 10]
data = data.rename(columns={'Distance progressive parcourue avec le ballon': 'Distance progressive'})

# Conversion des colonnes pertinentes
cols_to_int = ['Buts', 'Passes decisives', 'Buts + Passes decisives',
               'Distance progressive', 'Passes progressives', 'Receptions progressives']
data[cols_to_int] = data[cols_to_int].astype(int)

# Calcul des percentiles
for col in ['Distance progressive', 'Passes progressives', 'Receptions progressives']:
    data[col] = data[col] / data['Matches equivalents 90 minutes']

percentile_cols = [
    'Buts par 90 minutes', 'Passes decisives par 90 minutes',
    'Buts + Passes decisives par 90 minutes', 'Distance progressive',
    'Passes progressives', 'Receptions progressives', 'xG par 90 minutes', 'xAG par 90 minutes'
]
for col in percentile_cols:
    data[col] = (data[col].rank(pct=True) * 100).astype(int)

# Paramètres du radar
columns_to_plot = [
    'Buts par 90 minutes', 'Passes decisives par 90 minutes',
    'Buts + Passes decisives par 90 minutes', 'Distance progressive',
    'Passes progressives', 'Receptions progressives', 'xG par 90 minutes', 'xAG par 90 minutes'
]
radar = Radar(params=columns_to_plot, min_range=[0] * len(columns_to_plot), max_range=[100] * len(columns_to_plot))

# Configuration de la police
font_path = 'https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Regular.ttf'
font_manager = FontManager(font_path)

# Fonction pour tracer un radar comparatif
def plot_combined_radar(player1_data, player2_data, player1_name, player2_name, color1, color2):
    # Création de la figure et des axes
    fig, ax = radar.setup_axis(figsize=(8, 8))

    # Tracer les radars pour chaque joueur
    radar.draw_radar(player1_data[columns_to_plot].values.flatten(), ax=ax,
                     kwargs_radar={'facecolor': color1, 'alpha': 0.6}, label=player1_name)
    radar.draw_radar(player2_data[columns_to_plot].values.flatten(), ax=ax,
                     kwargs_radar={'facecolor': color2, 'alpha': 0.4}, label=player2_name)

    # Ajout de la légende
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.2), ncol=2, fontsize=12, frameon=False)
    return fig

# Streamlit application
st.title("Comparaison de Joueurs - Premier League 2023")

# Sélection des joueurs
player1 = st.selectbox("Sélectionnez le premier joueur", options=data['Joueur'].unique())
player2 = st.selectbox("Sélectionnez le deuxième joueur", options=data['Joueur'].unique())

# Données des joueurs sélectionnés
player1_data = data[data['Joueur'] == player1]
player2_data = data[data['Joueur'] == player2]

# Affichage du radar comparatif
st.subheader(f"Comparaison entre {player1} et {player2}")
fig = plot_combined_radar(player1_data, player2_data, player1, player2, color1="#C8102E", color2="#00B2A9")
st.pyplot(fig)

# Ajout d'une note de bas de page
st.markdown(
    """
    **Source des données :** FBref.  
    Cette application permet de visualiser et comparer les performances des attaquants ayant joué au moins 10 matchs en Premier League.
    """
)
