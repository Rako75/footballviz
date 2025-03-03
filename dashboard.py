import pandas as pd
import numpy as np
import streamlit as st
from soccerplots.radar_chart import Radar
import matplotlib.pyplot as plt

# Fonction pour charger les données depuis un fichier CSV
def load_dataset(file_path):
    return pd.read_csv(file_path)

# Spécifier le chemin du fichier CSV
file_path = "df_BIG2025.csv"
data = load_dataset(file_path)

def load_and_preprocess_data(position):
    filtered_data = data[data['Position'] == position]
    stats_cols = ['Buts par 90 minutes', 'Passes décisives par 90 minutes', 'Buts attendus par 90 minutes',
                  'Passes décisives attendues par 90 minutes']
    for col in stats_cols:
        filtered_data[col] = (filtered_data[col].rank(pct=True) * 100).astype(int)
    return filtered_data, stats_cols

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

st.title("Analyse des performances des joueurs de football")
position = st.selectbox("Sélectionnez une position", data['Position'].unique())
filtered_data, stats_cols = load_and_preprocess_data(position)
player_name = st.selectbox("Sélectionnez un joueur", filtered_data['Nom'].unique())
player_data = filtered_data[filtered_data['Nom'] == player_name]

if not player_data.empty:
    st.write("### Statistiques du joueur")
    st.dataframe(player_data[stats_cols])
    plot_radar_chart(player_data, stats_cols, player_name)
