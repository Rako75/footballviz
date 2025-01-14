import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Charger le fichier CSV
df = pd.read_csv("df_Big5.csv")

# Filtrer les milieux de terrain (Position = "Midfielder")
df_midfielders = df[df["Position"].str.contains("Midfielder", case=False, na=False)]

# Calculer des métriques pour les milieux box-to-box
df_midfielders["Actions Défensives"] = df_midfielders["Tacles"] + df_midfielders["Interceptions"]
df_midfielders["Création Off."] = (
    df_midfielders["Passes cles"] +
    df_midfielders["Actions menant a un tir par 90 minutes"] +
    df_midfielders["Actions menant a un but par 90 minutes"]
)

# Fonction pour créer le nuage de points
def plot_box_to_box(df):
    fig, ax = plt.subplots(figsize=(14, 10))

    # Créer le nuage de points
    scatter = ax.scatter(
        df["Distance Parcourue"],
        df["Actions Défensives"],
        s=df["Création Off."] * 10,  # Taille proportionnelle à la création offensive
        c=df["Passes Progressives"],  # Couleur proportionnelle aux passes progressives
        cmap="plasma",
        alpha=0.7,
        edgecolors="w"
    )

    # Ajouter les noms des joueurs à côté des points
    for i, row in df.iterrows():
        ax.text(
            row["Distance Parcourue"],
            row["Actions Défensives"] + 0.1,  # Décalage pour le texte
            row["Joueur"],
            fontsize=10,
            color="black",  # Nom des joueurs en noir
            ha="center"
        )

    # Ajouter un colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label("Passes Progressives", rotation=270, labelpad=15)
    cbar.ax.yaxis.set_tick_params(color="black")
    plt.setp(plt.getp(cbar.ax.axes, "yticklabels"), color="black")

    # Ajouter les étiquettes et le titre
    ax.set_title("Analyse des Milieux Box-to-Box", fontsize=16, color="black")
    ax.set_xlabel("Distance Parcourue (km)", fontsize=12, color="black")
    ax.set_ylabel("Actions Défensives (Tacles + Interceptions)", fontsize=12, color="black")

    # Ajuster les limites
    ax.set_xlim(df["Distance Parcourue"].min() - 1, df["Distance Parcourue"].max() + 1)
    ax.set_ylim(df["Actions Défensives"].min() - 1, df["Actions Défensives"].max() + 1)

    # Ajouter des lignes horizontale et verticale au centre
    ax.axhline(0, color='black', linewidth=1)
    ax.axvline(0, color='black', linewidth=1)

    return fig

# Interface utilisateur avec Streamlit
st.title("Analyse des Milieux Box-to-Box")

# Sélecteur de ligue
league_option = st.selectbox(
    "Sélectionnez une ligue :",
    options=["Toutes les ligues", "Premier League", "Bundesliga", "La Liga", "Ligue 1", "Serie A"]
)

# Filtrer les joueurs en fonction de la ligue choisie
if league_option != "Toutes les ligues":
    df_midfielders = df_midfielders[df_midfielders["Ligue"] == league_option]

# Afficher le graphique
fig = plot_box_to_box(df_midfielders)
st.pyplot(fig)
