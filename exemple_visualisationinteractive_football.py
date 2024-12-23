import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

# Chargement des données
@st.cache_data
def load_data():
    # Remplacez 'df_Big5.csv' par le chemin de votre fichier
    df = pd.read_csv('df_Big5.csv')
    return df

data = load_data()

# Traduction des positions en français
positions_fr = {
    "Forward": "Attaquant",
    "Midfielder": "Milieu",
    "Defender": "Défenseur",
    "Goalkeeper": "Gardien"
}
data['Position'] = data['Position'].map(positions_fr)

# Critères pertinents par position
criteria_by_position = {
    "Attaquant": ["Buts", "Passes decisives", "Buts + Passes decisives", "Buts hors penalty", 
                  "Tirs", "Touches dans la surface adverse", "Passes progressives", "Courses progressives"],
    "Milieu": ["Passes progressives", "Passes vers le dernier tiers", "Passes dans la surface adverse", 
               "Touches", "Interceptions", "Tacles reussis", "Touches dans le tiers défensif"],
    "Défenseur": ["Interceptions", "Tacles reussis", "Passes progressives", "Touches dans le tiers défensif",
                  "Passes longues reussies", "Pourcentage de duels aériens gagnés"]
}

# Vérification des colonnes disponibles
available_columns = data.columns
valid_criteria_by_position = {}

for position, criteria_list in criteria_by_position.items():
    valid_criteria = [col for col in criteria_list if col in available_columns]
    valid_criteria_by_position[position] = valid_criteria

# Normalisation des colonnes pertinentes
def normalize_series(series):
    return (series - series.min()) / (series.max() - series.min()) if series.max() > series.min() else series

for criteria_list in valid_criteria_by_position.values():
    for col in criteria_list:
        if col in data.columns:
            data[col + "_normalized"] = normalize_series(data[col])

# Création de la fonction pour le radarchart
def create_radarchart(player_name, data, valid_criteria_by_position):
    # Filtrer les données pour le joueur sélectionné
    player_data = data[data["Joueur"] == player_name].iloc[0]
    position = player_data["Position"]

    # Critères pertinents pour la position
    criteria = valid_criteria_by_position.get(position, [])
    criteria_normalized = [col + "_normalized" for col in criteria]

    # Vérification que les critères normalisés existent
    criteria_normalized = [col for col in criteria_normalized if col in data.columns]

    # Extraire les valeurs et les critères
    stats = player_data[criteria_normalized].values
    radar_data = pd.DataFrame({
        "Critères": criteria,
        "Valeurs": stats
    })

    # Création du radar avec Plotly
    fig = px.line_polar(radar_data, r="Valeurs", theta="Critères", line_close=True)
    fig.update_traces(fill="toself")
    fig.update_layout(title=f"Radarchart de {player_name} ({position})", polar=dict(radialaxis=dict(visible=True)))

    return fig

# Interface utilisateur Streamlit
st.title("Radarchart interactif des joueurs de football - Big 5")

# Aperçu des données
st.write("Aperçu des données :")
st.dataframe(data.head())

# Menu déroulant pour choisir un joueur
player_name = st.selectbox("Choisissez un joueur :", data["Joueur"].unique())

# Génération du radar pour le joueur sélectionné
if player_name:
    fig = create_radarchart(player_name, data, valid_criteria_by_position)
    st.plotly_chart(fig)
