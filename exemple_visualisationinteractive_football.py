import pandas as pd
import numpy as np
import streamlit as st
from mplsoccer import Radar
from mplsoccer import PyPizza
import matplotlib.pyplot as plt

# Charger les données
data = pd.read_csv('Premier_League_Attaquant.csv')
data = data[data['Matchs joues'].astype(int) > 10]
data = data.rename(columns={'Distance progressive parcourue avec le ballon': 'Distance progressive'})
data[['Buts', 'Passes decisives', 'Buts + Passes decisives', 'Distance progressive', 'Passes progressives', 'Receptions progressives']] = data[['Buts', 'Passes decisives', 'Buts + Passes decisives', 'Distance progressive', 'Passes progressives', 'Receptions progressives']].astype(int)

# Normaliser les colonnes
columns_to_normalize = [
    'Distance progressive', 'Passes progressives', 'Receptions progressives',
    'Buts par 90 minutes', 'Passes decisives par 90 minutes', 'Buts + Passes decisives par 90 minutes',
    'xG par 90 minutes', 'xAG par 90 minutes'
]
for col in columns_to_normalize:
    data[col] = (data[col].rank(pct=True) * 100).astype(int)

# Colonnes pour radar
columns_to_plot = [
    'Buts', 'Passes decisives', 'Buts + Passes decisives',
    'Distance progressive', 'Passes progressives', 'Receptions progressives',
    'xG par 90 minutes', 'xAG par 90 minutes'
]

# Définir la fonction de génération du graphique radar
def generate_radar(player_data, player_name, title_color):
    radar = PyPizza(
        params=columns_to_plot,
        background_color='#1A1A1D',
        straight_line_color='white',
        straight_line_lw=1,
        last_circle_lw=0,
        other_circle_color='white',
        other_circle_ls='-',
        other_circle_lw=1
    )
    
    values = list(player_data[columns_to_plot].values.flatten())
    fig, ax = radar.make_pizza(
        figsize=(8, 8),
        values=values,
        kwargs_values=dict(
            color='#FFFFFF', fontsize=9,
            bbox={
                'edgecolor': 'black', 'facecolor': '#00B2A9', "boxstyle": 'round, pad= .2', "lw": 1
            }
        ),
        kwargs_slices=dict(facecolor="#C8102E", edgecolor="black", linewidth=1),
        kwargs_params=dict(color='#FFFFFF', fontsize=10)
    )

    ax.text(
        x=.5, y=1.1,
        s=player_name,
        fontsize=20,
        c=title_color,
        ha='center', va='center', transform=ax.transAxes
    )
    return fig

# Application Streamlit
st.title("Comparaison de joueurs - Premier League")

# Sélection des joueurs
player_list = data['Joueur'].unique()
player1 = st.selectbox("Choisissez le premier joueur", player_list)
player2 = st.selectbox("Choisissez le second joueur", player_list)

# Comparaison
if player1 != player2:
    player1_data = data[data['Joueur'] == player1]
    player2_data = data[data['Joueur'] == player2]

    st.subheader(f"Comparaison entre {player1} et {player2}")

    # Générer les radars
    st.write(f"**{player1}**")
    fig1 = generate_radar(player1_data, player1, title_color="#C8102E")
    st.pyplot(fig1)

    st.write(f"**{player2}**")
    fig2 = generate_radar(player2_data, player2, title_color="#005BAC")
    st.pyplot(fig2)

else:
    st.warning("Veuillez choisir deux joueurs différents pour effectuer la comparaison.")
