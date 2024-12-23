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

# Catégories et critères par position
categories = {
    "Attaquant": {
        "Attacking": ["Buts", "Passes decisives", "Buts + Passes decisives", "Tirs"],
        "Possession": ["Touches dans la surface adverse", "Passes progressives", "Courses progressives"],
        "Defending": []
    },
    "Milieu": {
        "Attacking": ["Passes dans la surface adverse", "xAG"],
        "Possession": ["Passes progressives", "Passes vers le dernier tiers", "Touches"],
        "Defending": ["Interceptions", "Tacles reussis"]
    },
    "Défenseur": {
        "Attacking": [],
        "Possession": ["Passes progressives", "Touches dans le tiers défensif", "Passes longues reussies"],
        "Defending": ["Interceptions", "Tacles reussis", "Pourcentage de duels aériens gagnés"]
    }
}

# Normalisation des données
def normalize_series(series):
    return (series - series.min()) / (series.max() - series.min()) if series.max() > series.min() else series

for position, metrics in categories.items():
    for category, criteria in metrics.items():
        for col in criteria:
            if col in data.columns:
                data[col + "_normalized"] = normalize_series(data[col])

# Création du pizza chart avec remplissage
def create_filled_pizzachart(player_name, data, categories):
    # Filtrer les données pour le joueur sélectionné
    player_data = data[data["Joueur"] == player_name].iloc[0]
    position = player_data["Position"]

    # Critères et catégories pour la position
    metrics_by_category = categories.get(position, {})
    pizza_data = []

    for category, metrics in metrics_by_category.items():
        for metric in metrics:
            normalized_col = metric + "_normalized"
            if normalized_col in player_data:
                pizza_data.append({
                    "Critère": metric,
                    "Valeur": player_data[normalized_col],
                    "Catégorie": category
                })

    pizza_df = pd.DataFrame(pizza_data)

    # Création du graphique avec sections remplies
    fig = px.bar_polar(
        pizza_df,
        r="Valeur",
        theta="Critère",
        color="Catégorie",
        template="plotly_white",
        color_discrete_map={
            "Attacking": "blue",
            "Possession": "red",
            "Defending": "orange"
        }
    )
    fig.update_traces(opacity=0.8)  # Ajouter de l'opacité pour l'effet visuel
    fig.update_layout(
        title=f"Pizza Chart de {player_name} ({position})",
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=True
    )

    return fig


# Interface utilisateur Streamlit
st.title("Pizza Chart interactif des joueurs de football - Big 5")

# Aperçu des données
st.write("Aperçu des données :")
st.dataframe(data.head())

# Menu déroulant pour choisir un joueur
player_name = st.selectbox("Choisissez un joueur :", data["Joueur"].unique())

# Génération du pizza chart pour le joueur sélectionné
if player_name:
    fig = create_pizzachart(player_name, data, categories)
    st.plotly_chart(fig)
