import pandas as pd
import plotly.express as px
import streamlit as st

# Charger les données
@st.cache_data
def load_data():
    # Charger le fichier CSV
    df = pd.read_csv('df_Big5.csv')  # Remplacez par le chemin correct vers votre fichier CSV
    return df

# Charger les données
data = load_data()

# Traduction des positions en français
positions_fr = {
    "Forward": "Attaquant",
    "Midfielder": "Milieu",
    "Defender": "Défenseur",
    "Goalkeeper": "Gardien"
}
data['Position'] = data['Position'].map(positions_fr)

# Catégories et critères pour le Pizza Chart
categories = {
    "Attaquant": {
        "Attacking": ["Buts", "Passes décisives", "Buts + Passes décisives", "Tirs"],
        "Possession": ["Passes progressives", "Courses progressives", "Touches dans la surface adverse"],
    },
    "Milieu": {
        "Possession": ["Passes progressives", "Passes vers le dernier tiers", "Passes dans la surface adverse"],
        "Defending": ["Interceptions", "Tacles réussis"],
    },
    "Défenseur": {
        "Defending": ["Interceptions", "Tacles réussis", "Pourcentage de duels aériens gagnés"],
        "Possession": ["Passes progressives", "Passes longues réussies"],
    }
}

# Normalisation des données pour chaque critère
for position, metrics_by_category in categories.items():
    for category, metrics in metrics_by_category.items():
        for metric in metrics:
            if metric in data.columns:
                normalized_col = metric + "_normalized"
                data[normalized_col] = data[metric] / data[metric].max()

# Création du Pizza Chart avec remplissage
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
st.subheader("Aperçu des données :")
st.dataframe(data[["Joueur", "Age", "Position", "Ligue", "Equipe", "Matchs joues", "Titularisations"]].head())

# Menu déroulant pour sélectionner un joueur
player_name = st.selectbox("Choisissez un joueur :", data["Joueur"].unique())

# Génération du graphique Pizza Chart pour le joueur sélectionné
if player_name:
    fig = create_filled_pizzachart(player_name, data, categories)
    st.plotly_chart(fig)
