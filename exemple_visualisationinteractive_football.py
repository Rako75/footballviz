# -*- coding: utf-8 -*-
# Exemple avec Streamlit pour comparer deux joueurs

import pandas as pd
import numpy as np
import streamlit as st
from mplsoccer import Radar
from mplsoccer import PyPizza
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager

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

# Fonction pour tracer un radar pour un joueur
def plot_radar(player_data, player_name, color):
    pizza = PyPizza(
        params=columns_to_plot,
        background_color='#1A1A1D',
        straight_line_color='white',
        straight_line_lw=1,
        last_circle_lw=0,
        other_circle_color='white',
        other_circle_ls='-',
        other_circle_lw=1
    )
    fig, ax = pizza.make_pizza(
        figsize=(8, 8),
        values=list(player_data[columns_to_plot].values.flatten()),
        kwargs_values=dict(color='#FFFFFF', fontsize=9, bbox={
            'edgecolor': 'black',
            'facecolor': color,
            "boxstyle": 'round, pad= .2',
            "lw": 1
        }),
        kwargs_slices=dict(facecolor=color, edgecolor="black", linewidth=1),
        kwargs_params=dict(color='#FFFFFF', fontsize=10, fontproperties='monospace')
    )
    ax.text(x=0.5, y=1.1, s=player_name, fontsize=20, c=color, ha='center', va='center', transform=ax.transAxes)
    return fig

# Streamlit application
st.title("Comparaison de Joueurs - Premier League 2023")

# Sélection des joueurs
player1 = st.selectbox("Sélectionnez le premier joueur", options=data['Joueur'].unique())
player2 = st.selectbox("Sélectionnez le deuxième joueur", options=data['Joueur'].unique())

# Données des joueurs sélectionnés
player1_data = data[data['Joueur'] == player1]
player2_data = data[data['Joueur'] == player2]

# Affichage des radars
st.subheader(f"Comparaison entre {player1} et {player2}")

col1, col2 = st.columns(2)

with col1:
    st.write(f"Radar de {player1}")
    fig1 = plot_radar(player1_data, player1, color="#C8102E")
    st.pyplot(fig1)

with col2:
    st.write(f"Radar de {player2}")
    fig2 = plot_radar(player2_data, player2, color="#00B2A9")
    st.pyplot(fig2)

# Ajout d'une note de bas de page
st.markdown(
    """
    **Source des données :** FBref.  
    Cette application permet de visualiser et comparer les performances des attaquants ayant joué au moins 10 matchs en Premier League.
    """
)
