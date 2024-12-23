import pandas as pd
import numpy as np
import streamlit as st
from mplsoccer import PyPizza
import matplotlib.pyplot as plt

# Chargement des données depuis le fichier CSV
@st.cache_data
def load_data():
    df = pd.read_csv('df_Big5.csv')  # Remplacez par le chemin correct de votre fichier CSV
    return df

data = load_data()

# Pré-traitement des données
# Filtrage des joueurs ayant joué plus de 900 minutes et exclure les gardiens
data = data[data['Minutes jouees'] > 900]
data = data[data['Position'] != "Goalkeeper"]  # Exclusion des gardiens

# Calcul des métriques par 90 minutes
metrics_columns = ['Buts par 90 minutes', 'Passes decisives par 90 minutes', 
                   'Buts + Passes decisives par 90 minutes', 'Buts hors penalty par 90 minutes',
                   'xG par 90 minutes', 'xAG par 90 minutes']

# Normalisation des métriques
def normalize_series(series):
    return (series - series.min()) / (series.max() - series.min()) if series.max() > series.min() else series

# Normalisation des colonnes pertinentes
for col in metrics_columns:
    if col in data.columns:
        data[f'{col}_normalized'] = normalize_series(data[col])

# Traduction des positions en français
positions_fr = {
    "FW": "Attaquant",
    "MF": "Milieu",
    "DF": "Défenseur"
}

data['Position'] = data['Position'].map(positions_fr)

# Critères pertinents par position
criteria_by_position = {
    "Attaquant": ['Buts par 90 minutes', 'Passes decisives par 90 minutes', 'Buts + Passes decisives par 90 minutes', 'xG par 90 minutes'],
    "Milieu": ['Passes decisives par 90 minutes', 'Buts + Passes decisives par 90 minutes', 'xAG par 90 minutes', 'Courses progressives'],
    "Défenseur": ['Buts par 90 minutes', 'Tacles reussis', 'Interceptions', 'Buts + Passes decisives par 90 minutes']
}

# Fonction pour le radar PyPizza
def create_pizza_chart(player_name, data, valid_criteria_by_position):
    player_data = data[data['Joueur'] == player_name]
    
    # Assurez-vous que le joueur existe dans les données
    if player_data.empty:
        st.error(f"Le joueur {player_name} n'est pas trouvé dans les données.")
        return None

    position = player_data['Position'].iloc[0]
    criteria = valid_criteria_by_position.get(position, [])
    
    # Vérifiez que le joueur a des données pour les critères
    if not all([f'{c}_normalized' in player_data.columns for c in criteria]):
        st.error(f"Le joueur {player_name} n'a pas toutes les données nécessaires pour le radar.")
        return None
    
    radar_values = player_data[[f'{c}_normalized' for c in criteria]].iloc[0].values

    # Création du plot
    pizza = PyPizza(
        params=criteria,
        background_color="#1A1A1D",
        straight_line_color="white",
        straight_line_lw=1,
    )
    fig, ax = pizza.make_pizza(
        values=radar_values,
        figsize=(8, 8),
        kwargs_slices=dict(facecolor="#6CABDD", edgecolor="black", linewidth=1),
        kwargs_params=dict(color="#FFFFFF", fontsize=10, fontweight="bold")
    )
    ax.text(0.5, 1.1, f"{player_name}", ha="center", fontsize=16, color="white")
    return fig

# Interface utilisateur Streamlit
st.title("Analyse des performances des joueurs de football - Big 5")

st.write("Aperçu des données :")
st.dataframe(data.head())

# Sélection du joueur
player_name = st.selectbox("Choisissez un joueur :", data["Joueur"].unique())

# Génération du radar PyPizza
if player_name:
    st.subheader("Visualisation Radar avec PyPizza")
    pizza_fig = create_pizza_chart(player_name, data, criteria_by_position)
    if pizza_fig is not None:
        st.pyplot(pizza_fig)
