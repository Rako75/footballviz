# -*- coding: utf-8 -*-
# Exemple de comparaison de joueurs avec Radar Chart (soccerplots)

import pandas as pd
import streamlit as st
from soccerplots.radar_chart import Radar

# Chargement des données
data = pd.read_csv('Premier_League_Attaquant.csv')
data = data[data['Matchs joues'].astype(int) > 10]
data = data.rename(columns={'Distance progressive parcourue avec le ballon': 'Distance progressive'})

# Conversion des colonnes pertinentes
cols_to_int = ['Buts', 'Passes decisives', 'Buts + Passes decisives',
               'Distance progressive', 'Passes progressives', 'Receptions progressives']
data[cols_to_int] = data[cols_to_int].astype(int)

# Calcul des percentiles
percentile_cols = [
    'Buts par 90 minutes', 'Passes decisives par 90 minutes',
    'Buts + Passes decisives par 90 minutes', 'Distance progressive',
    'Passes progressives', 'Receptions progressives', 'xG par 90 minutes', 'xAG par 90 minutes'
]
for col in percentile_cols:
    data[col] = (data[col].rank(pct=True) * 100).astype(int)

# Paramètres pour le radar
params = [
    'Buts par 90 minutes', 'Passes decisives par 90 minutes',
    'Buts + Passes decisives par 90 minutes', 'Distance progressive',
    'Passes progressives', 'Receptions progressives', 'xG par 90 minutes', 'xAG par 90 minutes'
]
ranges = [(0, 100) for _ in params]

# Streamlit App
st.title("Comparaison de Joueurs - Premier League 2023")

# Sélection des joueurs
player1 = st.selectbox("Sélectionnez le premier joueur", options=data['Joueur'].unique())
player2 = st.selectbox("Sélectionnez le deuxième joueur", options=data['Joueur'].unique())

# Données des joueurs sélectionnés
player1_data = data[data['Joueur'] == player1].iloc[0]
player2_data = data[data['Joueur'] == player2].iloc[0]

values = [
    player1_data[params].values.tolist(),
    player2_data[params].values.tolist()
]

# Titre du graphique
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

# Note de bas de page vide
endnote = ""

# Génération du Radar Chart
radar = Radar(background_color="#121212", patch_color="#28252C", label_color="#F0FFF0", range_color="#F0FFF0")
fig, ax = radar.plot_radar(ranges=ranges, params=params, values=values,
                           radar_color=['#9B3647', '#3282b8'], title=title,
                           endnote=endnote, alphas=[0.55, 0.5], compare=True)

# Affichage dans Streamlit
st.pyplot(fig)

# Ajout d'une note de bas de page pour les données
st.markdown(
    """
    **Source des données :** FBref.  
    Cette application permet de visualiser et comparer les performances des attaquants ayant joué au moins 10 matchs en Premier League.
    """
)
