import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image
import requests
from io import BytesIO
import streamlit as st

# Dictionnaire des répertoires de logos
logo_directories = {
    "Premier League": "https://raw.githubusercontent.com/Rako75/footballviz/main/Premier%20League%20Logos",
    "Bundesliga": "https://raw.githubusercontent.com/Rako75/footballviz/main/Bundesliga%20Logos",
    "La Liga": "https://raw.githubusercontent.com/Rako75/footballviz/main/La%20Liga%20Logos",
    "Ligue 1": "https://raw.githubusercontent.com/Rako75/footballviz/main/Ligue%201%20Logos",
    "Serie A": "https://raw.githubusercontent.com/Rako75/footballviz/main/Serie%20A%20Logos",
}

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

# Fonction pour récupérer les logos des équipes depuis GitHub
def get_team_logo(team_name, league_name):
    base_url = logo_directories.get(league_name)
    if base_url:
        logo_url = f"{base_url}/{team_name}.png"
        try:
            response = requests.get(logo_url)
            if response.status_code == 200:
                return Image.open(BytesIO(response.content))
        except Exception as e:
            st.error(f"Erreur en récupérant le logo pour {team_name}: {e}")
    return None

# Créer le graphique avec matplotlib
def plot_graph(df):
    # Utiliser un fond blanc pour le graphique
    plt.style.use("seaborn-whitegrid")  # Un fond blanc avec une grille légère

    fig, ax = plt.subplots(figsize=(14, 10))

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

    # Ajouter les logos des équipes
    for i, row in df.iterrows():
        team_name = row["Equipe"]
        league_name = row["Ligue"]
        logo = get_team_logo(team_name, league_name)
        if logo:
            # Créer un OffsetImage
            imagebox = OffsetImage(logo, zoom=0.05)
            ab = AnnotationBbox(
                imagebox,
                (row["Passes cles"], row["Actions menant a un tir par 90 minutes"]),
                frameon=False,
                pad=0.5
            )
            ax.add_artist(ab)
        # Ajouter les noms des joueurs juste au-dessus des points
        ax.text(
            row["Passes cles"],
            row["Actions menant a un tir par 90 minutes"] + 0.1,
            row["Joueur"],
            fontsize=10,
            color="black",  # Nom du joueur en noir pour bien ressortir sur fond blanc
            ha="center"
        )

    # Ajouter un colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label("Actions menant à un but par 90 minutes", rotation=270, labelpad=15, color="black")
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

# Afficher le graphique dans Streamlit
st.write("Top 20 des attaquants par création totale (Passes clés, Actions menant à un tir et Actions menant à un but).")
fig = plot_graph(top_20_forwards)
st.pyplot(fig)
