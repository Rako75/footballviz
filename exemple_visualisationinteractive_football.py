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

# Définir la fonction de génération du graphique radar avec les nouvelles méthodes
def generate_combined_radar(player1_data, player2_data, player1_name, player2_name):
    # Définir les plages pour les paramètres (min et max)
    min_range = [0 for _ in columns_to_plot]  # Valeur minimale pour chaque paramètre
    max_range = [100 for _ in columns_to_plot]  # Valeur maximale pour chaque paramètre
    
    # Valeurs des deux joueurs pour la comparaison
    val_comp = player1_data[columns_to_plot].values.flatten(), player2_data[columns_to_plot].values.flatten()
    
    # Paramètres (colonnes)
    params = columns_to_plot
    
    # Titres et couleurs pour les joueurs
    title_comp = dict(
        title_name=player1_name,
        title_color='#D00027',
        subtitle_name='Premier League',
        subtitle_color='#000000',
        title_name_2=player2_name,
        title_color_2='#00A398',
        subtitle_name_2='Premier League',
        subtitle_color_2='#000000',
        title_fontsize=18,
        subtitle_fontsize=15,
    )
    
    # Initialiser le radar avec les bons paramètres
    radar = Radar(params=params, min_range=min_range, max_range=max_range)
    
    # Tracer le graphique radar avec les deux joueurs
    fig, ax = radar.draw_radar(
        values=[val_comp[0], val_comp[1]],
        titles=[player1_name, player2_name],
        colors=['#D00027', '#00A398'],
        alpha_fill=0.2,
        figsize=(8, 8)
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
