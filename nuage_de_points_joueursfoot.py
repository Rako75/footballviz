import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import streamlit as st
import requests
from io import BytesIO

# Directoires des logos
logo_directories = {
    "Premier League": "https://raw.githubusercontent.com/Rako75/footballviz/main/Premier%20League%20Logos",
    "Bundesliga": "https://raw.githubusercontent.com/Rako75/footballviz/main/Bundesliga%20Logos",
    "La Liga": "https://raw.githubusercontent.com/Rako75/footballviz/main/La%20Liga%20Logos",
    "Ligue 1": "https://raw.githubusercontent.com/Rako75/footballviz/main/Ligue%201%20Logos",
    "Serie A": "https://raw.githubusercontent.com/Rako75/footballviz/main/Serie%20A%20Logos",
}

# Charger le fichier CSV
df = pd.read_csv("df_Big5.csv")

# Ajouter des colonnes pertinentes pour l'analyse
df["Actions Défensives"] = df["Tacles"] + df["Interceptions"]
df["Création Off."] = (
    df["Passes cles"]
    + df["Actions menant a un tir par 90 minutes"]
    + df["Actions menant a un but par 90 minutes"]
)
df["Création totale"] = df["Création Off."]

# Fonction pour charger les images à partir d'URL
def load_image(url):
    response = requests.get(url)
    img = plt.imread(BytesIO(response.content))
    return OffsetImage(img, zoom=0.05)  # Ajuster le zoom pour redimensionner les images

# Fonction pour tracer les graphiques avec les logos
def plot_with_logos(df, x_col, y_col, league):
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_facecolor("black")
    ax.grid(True, linestyle=":", color="white", alpha=0.5)
    
    for _, row in df.iterrows():
        # Construire l'URL du logo
        logo_url = f"{logo_directories[league]}/{row['Club']}.png"
        try:
            # Ajouter le logo
            image = load_image(logo_url)
            ab = AnnotationBbox(
                image,
                (row[x_col], row[y_col]),
                frameon=False,
                pad=0.5,
            )
            ax.add_artist(ab)
        except Exception:
            # Si le logo ne peut pas être chargé, afficher un point
            ax.scatter(row[x_col], row[y_col], s=100, c="white", edgecolors="w", alpha=0.7)

    ax.set_xlabel(x_col, fontsize=12, color="white")
    ax.set_ylabel(y_col, fontsize=12, color="white")
    ax.spines["top"].set_color("white")
    ax.spines["right"].set_color("white")
    ax.spines["left"].set_color("white")
    ax.spines["bottom"].set_color("white")
    ax.tick_params(axis="x", colors="white")
    ax.tick_params(axis="y", colors="white")
    
    ax.set_title(f"Analyse des joueurs : {x_col} vs {y_col}", fontsize=16, color="white")
    return fig

# Interface utilisateur avec Streamlit
st.title("Analyse des joueurs avec les logos des clubs")

# Sélecteur de position et de ligue
position_option = st.selectbox("Sélectionnez une position:", ["Milieu", "Attaquant", "Défenseur"])
league_option = st.selectbox(
    "Sélectionnez une ligue:",
    ["Premier League", "Bundesliga", "La Liga", "Ligue 1", "Serie A"],
)

# Filtrer les joueurs en fonction de la position
if position_option == "Milieu":
    df_position = df[df["Position"].str.contains("Midfielder", case=False, na=False)]
    x_col = "Distance totale parcourue avec le ballon"
    y_col = "Actions Défensives"
elif position_option == "Attaquant":
    df_position = df[df["Position"].str.contains("Forward", case=False, na=False)]
    x_col = "Passes cles"
    y_col = "Actions menant a un tir par 90 minutes"
else:  # Défenseur
    df_position = df[df["Position"].str.contains("Defender", case=False, na=False)]
    x_col = "Tacles"
    y_col = "Interceptions"

# Filtrer par ligue
df_league = df_position[df_position["Ligue"] == league_option]

# Prendre les 20 meilleurs joueurs selon la métrique sélectionnée
top_20_players = df_league.nlargest(20, y_col)

# Afficher le graphique avec les logos
fig = plot_with_logos(top_20_players, x_col, y_col, league_option)
st.pyplot(fig)
