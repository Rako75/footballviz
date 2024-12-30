import pandas as pd
import numpy as np
import streamlit as st
from soccerplots.radar_chart import Radar

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
params = [
    'Buts par 90 minutes', 'Passes decisives par 90 minutes',
    'Buts + Passes decisives par 90 minutes', 'Distance progressive',
    'Passes progressives', 'Receptions progressives', 'xG par 90 minutes', 'xAG par 90 minutes'
]

ranges = [(0, 100)] * len(params)  # Les valeurs sont des pourcentages (0 à 100)

# Streamlit application
st.title("Comparaison de Joueurs - Premier League 2023")

# Sélection des joueurs
player1 = st.selectbox("Sélectionnez le premier joueur", options=data['Joueur'].unique())
player2 = st.selectbox("Sélectionnez le deuxième joueur", options=data['Joueur'].unique())

# Données des joueurs sélectionnés
player1_data = data[data['Joueur'] == player1].iloc[0][params].tolist()
player2_data = data[data['Joueur'] == player2].iloc[0][params].tolist()

# Configuration des titres
title = dict(
    title_name=player1,
    title_color='#9B3647',
    subtitle_name='Premier League',
    subtitle_color='#ABCDEF',
    title_name_2=player2,
    title_color_2='#3282b8',
    subtitle_name_2='Premier League',
    subtitle_color_2='#ABCDEF',
    title_fontsize=18,
    subtitle_fontsize=15,
)

# Note de bas de page
endnote = "Source : FBref | Auteur : Alex Rakotomalala

# Instanciation de l'objet Radar
radar = Radar(background_color="#121212", patch_color="#28252C", label_color="#F0FFF0", range_color="#F0FFF0")

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

# Affichage du radar dans Streamlit
st.pyplot(fig)
