# pip install streamlit mplsoccer pandas numpy matplotlib seaborn plotly

import streamlit as st
import pandas as pd
from mplsoccer import Radar
import matplotlib.pyplot as plt

# Charger les données
data = pd.read_csv('Premier_League_Attaquant.csv')
data = data[data['Matchs joues'].astype(int) > 10]
data = data.rename(columns={'Distance progressive parcourue avec le ballon': 'Distance progressive'})

# Normalisation des statistiques
columns_to_normalize = [
    'Buts', 'Passes decisives', 'Buts + Passes decisives',
    'Distance progressive', 'Passes progressives', 'Receptions progressives',
    'xG par 90 minutes', 'xAG par 90 minutes'
]
for col in columns_to_normalize:
    data[col] = data[col] / data['Matches equivalents 90 minutes']
    data[col] = (data[col].rank(pct=True) * 100).astype(int)

# Définir les paramètres pour le radar
columns_to_plot = [
    'Buts', 'Passes decisives', 'Buts + Passes decisives',
    'Distance progressive', 'Passes progressives', 'Receptions progressives',
    'xG par 90 minutes', 'xAG par 90 minutes'
]
radar = Radar(
    params=columns_to_plot,
    min_range=[0] * len(columns_to_plot),
    max_range=[100] * len(columns_to_plot)
)

# Interface utilisateur avec Streamlit
st.title("Comparaison interactive de joueurs")
st.write("Choisissez deux joueurs à comparer.")

# Sélection des joueurs
joueurs = data['Joueur'].unique()
joueur1 = st.selectbox("Joueur 1", joueurs)
joueur2 = st.selectbox("Joueur 2", joueurs)

if joueur1 and joueur2:
    stats_joueur1 = data[data['Joueur'] == joueur1][columns_to_plot].values.flatten()
    stats_joueur2 = data[data['Joueur'] == joueur2][columns_to_plot].values.flatten()

    # Création des graphiques radar
    fig, ax = radar.plot(
        values=[stats_joueur1, stats_joueur2],
        labels=[joueur1, joueur2],
        cmap='coolwarm',
        alpha=0.6,
        figsize=(8, 8)
    )
    ax.set_title(f"Comparaison : {joueur1} vs {joueur2}", fontsize=16)

    # Affichage du graphique
    st.pyplot(fig)
