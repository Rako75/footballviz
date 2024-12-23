import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

# Chargement des données
@st.cache
def load_data():
    # Remplacez 'df_Big5.csv' par votre fichier de données
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

# Critères par position
criteria = {
    "Attaquant": ["Buts", "Passes decisives", "Buts + Passes decisives", "Buts hors penalty", 
                  "xG", "xAG", "Tirs", "Touches dans la surface adverse", "Passes progressives", "Courses progressives"],
    "Milieu": ["Passes progressives", "Passes vers le dernier tiers", "Passes dans la surface adverse", 
               "xAG", "Touches", "Interceptions", "Tacles reussis", "Touches dans le tiers defensif"],
    "Défenseur": ["Interceptions", "Tacles reussis", "Dégagements", "Duels aériens gagnés (%)", 
                  "Passes progressives", "Passes longues reussies", "Touches dans le tiers defensif"]
}

# Création de la fonction pour le radarchart
def create_radarchart(player_name, data, criteria):
    # Filtrer les données pour le joueur sélectionné
    player_data = data[data["Joueur"] == player_name].iloc[0]
    position = player_data["Position"]

    # Sélection des critères pour la position
    selected_criteria = criteria[position]
    stats = player_data[selected_criteria].values
    normalized_stats = stats / max(stats)  # Normalisation entre 0 et 1

    # Création du DataFrame pour le radar
    radar_data = pd.DataFrame({
        "Critères": selected_criteria,
        "Valeurs": normalized_stats
    })

    # Création du radar avec Plotly
    fig = px.line_polar(radar_data, r="Valeurs", theta="Critères", line_close=True)
    fig.update_traces(fill="toself")
    fig.update_layout(title=f"Radarchart de {player_name} ({position})", polar=dict(radialaxis=dict(visible=True)))

    return fig

# Interface utilisateur Streamlit
st.title("Radarchart interactif des joueurs de football")

# Menu déroulant pour choisir un joueur
player_name = st.selectbox("Choisissez un joueur :", data["Player"].unique())

# Génération du radar pour le joueur sélectionné
if player_name:
    fig = create_radarchart(player_name, data, criteria)
    st.plotly_chart(fig)
