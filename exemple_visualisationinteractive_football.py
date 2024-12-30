import pandas as pd
import numpy as np
import streamlit as st
from mplsoccer import Radar
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
def generate_combined_radar(player1_data, player2_data, player1_name, player2_name):
    radar = Radar(
        params=columns_to_plot,
        min_range=[0 for _ in columns_to_plot],
        max_range=[100 for _ in columns_to_plot]
    )

    values1 = list(player1_data[columns_to_plot].values.flatten())
    values2 = list(player2_data[columns_to_plot].values.flatten())

    # Créer le graphique radar
    fig, ax = radar.draw_radar(
        values=[values1, values2],
        titles=[player1_name, player2_name],
        colors=["#C8102E", "#005BAC"],
        figsize=(8, 8),
        alpha_fill=0.2
    )

    # Ajouter une légende et un titre
    ax[0].legend(
        [player1_name, player2_name],
        loc="upper right", bbox_to_anchor=(1.3, 1), fontsize=10
    )
    ax[0].set_title(
        f"Comparaison entre {player1_name} et {player2_name}",
        fontsize=16,
        color="black",
        pad=20
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

    # Générer le radar combiné
    fig = generate_combined_radar(player1_data, player2_data, player1, player2)
    st.pyplot(fig)

else:
    st.warning("Veuillez choisir deux joueurs différents pour effectuer la comparaison.")
