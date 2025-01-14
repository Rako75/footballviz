import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Charger le fichier CSV
df = pd.read_csv("df_Big5.csv")

# Filtrer les attaquants ou milieux de terrain selon la sélection de l'utilisateur
def filter_players(position, league):
    if position == "Attaquant":
        df_filtered = df[df["Position"].str.contains("Forward", case=False, na=False)]
    else:
        df_filtered = df[df["Position"].str.contains("Midfielder", case=False, na=False)]

    # Filtrer selon la ligue
    if league != "Toutes les ligues":
        df_filtered = df_filtered[df_filtered["Ligue"] == league]
    
    return df_filtered

# Fonction pour le nuage de points des attaquants
def plot_forwards(df):
    # Créer le graphique
    fig, ax = plt.subplots(figsize=(14, 10))

    # Créer le nuage de points pour les attaquants
    scatter = ax.scatter(
        df["Passes cles"],
        df["Actions menant a un tir par 90 minutes"],
        s=df["Age"] * 10,
        c=df["Actions menant a un but par 90 minutes"],  # Couleur des points
        cmap="coolwarm",
        alpha=0.7,
        edgecolors="w"
    )

    # Ajouter les noms des joueurs
    for i, row in df.iterrows():
        ax.text(
            row["Passes cles"],
            row["Actions menant a un tir par 90 minutes"] + 0.1,
            row["Joueur"],
            fontsize=10,
            color="black",
            ha="center"
        )

    # Ajouter un colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label("Actions menant à un but par 90 minutes", rotation=270, labelpad=15)

    # Ajouter les étiquettes et le titre
    ax.set_title("Création d'occasion par 90 min (Attaquants)", fontsize=16, color="black")
    ax.set_xlabel("Passes clés", fontsize=12, color="black")
    ax.set_ylabel("Actions menant à un tir par 90 minutes", fontsize=12, color="black")

    # Ajouter les axes du centre
    ax.axhline(0, color='black', linewidth=1)
    ax.axvline(0, color='black', linewidth=1)

    # Supprimer la grille
    ax.grid(False)

    return fig

# Fonction pour le nuage de points des milieux de terrain
def plot_midfielders(df):
    # Créer le graphique
    fig, ax = plt.subplots(figsize=(14, 10))

    # Créer le nuage de points pour les milieux de terrain
    scatter = ax.scatter(
        df["Distance totale parcourue avec le ballon"],
        df["Tacles"] + df["Interceptions"],  # Activité défensive
        s=df["Actions menant a un but"] * 10,
        c=df["Passes progressives"],  # Couleur basée sur la capacité à progresser
        cmap="coolwarm",
        alpha=0.7,
        edgecolors="w"
    )

    # Ajouter les noms des joueurs
    for i, row in df.iterrows():
        ax.text(
            row["Distance totale parcourue avec le ballon"],
            row["Tacles"] + row["Interceptions"] + 0.1,
            row["Joueur"],
            fontsize=10,
            color="black",
            ha="center"
        )

    # Ajouter un colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label("Passes progressives", rotation=270, labelpad=15)

    # Ajouter les étiquettes et le titre
    ax.set_title("Endurance et Activité Défensive (Milieux Box-to-Box)", fontsize=16, color="black")
    ax.set_xlabel("Distance totale parcourue avec le ballon", fontsize=12, color="black")
    ax.set_ylabel("Actions défensives (Tacles + Interceptions)", fontsize=12, color="black")

    # Ajouter les axes du centre
    ax.axhline(0, color='black', linewidth=1)
    ax.axvline(0, color='black', linewidth=1)

    # Supprimer la grille
    ax.grid(False)

    return fig

# Interface utilisateur avec Streamlit
st.title("Analyse des Joueurs - Attaquants ou Milieux Box-to-Box")

# Sélecteur de poste (Attaquant ou Milieu)
position = st.selectbox("Sélectionnez un poste", ["Attaquant", "Milieu"])

# Sélecteur de ligue
league = st.selectbox(
    "Sélectionnez une ligue:",
    options=["Toutes les ligues", "Premier League", "Bundesliga", "La Liga", "Ligue 1", "Serie A"]
)

# Filtrer les joueurs en fonction de la sélection
df_filtered = filter_players(position, league)

# Prendre les 20 meilleurs joueurs selon une métrique pertinente
if position == "Attaquant":
    df_filtered["Création totale"] = (
        df_filtered["Passes cles"] +
        df_filtered["Actions menant a un tir par 90 minutes"] +
        df_filtered["Actions menant a un but par 90 minutes"]
    )
    top_20 = df_filtered.nlargest(20, "Création totale")
    st.write(f"Top 20 des {position}s par création totale ({league})")
    fig = plot_forwards(top_20)
else:
    top_20 = df_filtered.nlargest(20, "Distance totale parcourue avec le ballon")
    st.write(f"Top 20 des {position}s par endurance et activité défensive ({league})")
    fig = plot_midfielders(top_20)

# Afficher le graphique
st.pyplot(fig)
