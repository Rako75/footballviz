import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Charger le fichier CSV
df = pd.read_csv("df_Big5.csv")

# Filtrer les attaquants (Position = "Forward")
df_forwards = df[df["Position"].str.contains("Forward", case=False, na=False)]

# Calculer une métrique combinée pour la création d'occasions
df_forwards["Création totale"] = (
    df_forwards["Passes cles"] +
    df_forwards["Actions menant a un tir par 90 minutes"] +
    df_forwards["Actions menant a un but par 90 minutes"]
)

# Prendre les 20 meilleurs joueurs
top_20_forwards = df_forwards.nlargest(20, "Création totale")

# Créer le graphique avec matplotlib
def plot_graph(df):
    # Utiliser les paramètres par défaut de Matplotlib (sans style spécifique)
    fig, ax = plt.subplots(figsize=(16, 10))

    # Créer le nuage de points
    scatter = ax.scatter(
        df["Passes cles"],
        df["Actions menant a un tir par 90 minutes"],
        s=df["Age"] * 10,  # Taille des points proportionnelle à l'âge
        c=df["Actions menant a un but par 90 minutes"],  # Couleur des points
        cmap="coolwarm",
        alpha=0.7,
        edgecolors="w"
    )

    # Ajouter les noms des joueurs à côté des points
    for i, row in df.iterrows():
        ax.text(
            row["Passes cles"],
            row["Actions menant a un tir par 90 minutes"] + 0.1,  # Décalage pour que le texte soit au-dessus du point
            row["Joueur"],
            fontsize=10,
            color="black",  # Nom du joueur en noir pour bien ressortir
            ha="center",  # Alignement horizontal centré par rapport au point
            va="center"   # Alignement vertical centré
        )

    # Ajouter un colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label("Actions menant à un but par 90 minutes", rotation=270, labelpad=15)
    cbar.ax.yaxis.set_tick_params(color="black")
    plt.setp(plt.getp(cbar.ax.axes, "yticklabels"), color="black")

    # Ajouter les étiquettes et le titre
    ax.set_title("Création d'occasion par 90 min", fontsize=16, color="black")
    ax.set_xlabel("Passes clés", fontsize=12, color="black")
    ax.set_ylabel("Actions menant à un tir par 90 minutes", fontsize=12, color="black")

    # Ajuster les limites des axes
    ax.set_xlim(df["Passes cles"].min() - 1, df["Passes cles"].max() + 1)
    ax.set_ylim(df["Actions menant a un tir par 90 minutes"].min() - 0.5,
                df["Actions menant a un tir par 90 minutes"].max() + 0.5)

    # Supprimer la grille et ajuster les couleurs des ticks
    ax.grid(True, linestyle='-', color='gray', alpha=0.5)
    ax.tick_params(colors="black")

    # Ajouter les axes du centre
    ax.axhline(0, color='black', linewidth=1)
    ax.axvline(0, color='black', linewidth=1)

    return fig

# Titre de l'application
st.title("Analyse des attaquants - Création d'occasions")

# Sélecteur de ligue
league_option = st.selectbox(
    "Sélectionnez une ligue:",
    options=["Toutes les ligues", "Premier League", "Bundesliga", "La Liga", "Ligue 1", "Serie A"]
)

# Filtrer les joueurs en fonction de la ligue choisie
if league_option != "Toutes les ligues":
    df_forwards = df_forwards[df_forwards["Ligue"] == league_option]

# Prendre les 20 meilleurs joueurs selon la création totale
top_20_forwards = df_forwards.nlargest(20, "Création totale")

# Afficher le graphique dans Streamlit
st.write(f"Top 20 des attaquants par création totale ({league_option})")
fig = plot_graph(top_20_forwards)
st.pyplot(fig)
