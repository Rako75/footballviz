import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Charger le fichier CSV
df = pd.read_csv("df_Big5.csv")

# Appliquer un style de fond noir
plt.style.use('dark_background')

# Créer une fonction pour filtrer les données
def filter_players(position, league):
    if position == "Attaquant":
        df_filtered = df[df["Position"].str.contains("Forward", case=False, na=False)]
        # Calculer une métrique combinée pour la création d'occasions
        df_filtered["Création totale"] = (
            df_filtered["Passes cles"] +
            df_filtered["Actions menant a un tir par 90 minutes"] +
            df_filtered["Actions menant a un but par 90 minutes"]
        )
    else:  # Position == "Milieu"
        df_filtered = df[df["Position"].str.contains("Midfielder", case=False, na=False)]
        # Calculer une métrique pour les milieux
        df_filtered["Endurance et Défense"] = (
            df_filtered["Distance totale parcourue avec le ballon"] +
            df_filtered["Tacles"] +
            df_filtered["Interceptions"]
        )
    
    # Filtrer par ligue
    if league != "Toutes les ligues":
        df_filtered = df_filtered[df_filtered["Ligue"] == league]

    return df_filtered

# Créer une fonction pour générer les graphiques
def plot_graph(df, position):
    # Créer une figure
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_facecolor("black")  # Fond des axes

    if position == "Attaquant":
        scatter = ax.scatter(
            df["Passes cles"],
            df["Actions menant a un tir par 90 minutes"],
            s=df["Age"] * 10,  # Taille des points proportionnelle à l'âge
            c=df["Actions menant a un but par 90 minutes"],  # Couleur des points
            cmap="coolwarm",
            alpha=0.7,
            edgecolors="white"
        )
        ax.set_title("Création d'occasion par 90 min (Attaquants)", fontsize=16, color="white")
        ax.set_xlabel("Passes clés", fontsize=12, color="white")
        ax.set_ylabel("Actions menant à un tir par 90 minutes", fontsize=12, color="white")

    else:  # position == "Milieu"
        scatter = ax.scatter(
            df["Distance totale parcourue avec le ballon"],
            df["Tacles"] + df["Interceptions"],
            s=df["Age"] * 10,  # Taille des points proportionnelle à l'âge
            c=df["Passes progressives"],  # Couleur des points
            cmap="coolwarm",
            alpha=0.7,
            edgecolors="white"
        )
        ax.set_title("Endurance et Activité Défensive (Milieux Box-to-Box)", fontsize=16, color="white")
        ax.set_xlabel("Distance totale parcourue avec le ballon", fontsize=12, color="white")
        ax.set_ylabel("Actions défensives (Tacles + Interceptions)", fontsize=12, color="white")

    # Ajouter les noms des joueurs à côté des points
    for i, row in df.iterrows():
        ax.text(
            row.iloc[0],
            row.iloc[1] + 0.1,
            row["Joueur"],
            fontsize=10,
            color="white",
            ha="center"
        )

    # Ajouter un colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label("Valeur selon métrique", rotation=270, labelpad=15, color="white")
    cbar.ax.yaxis.set_tick_params(color="white")
    plt.setp(plt.getp(cbar.ax.axes, "yticklabels"), color="white")

    # Ajuster les couleurs des ticks
    ax.tick_params(colors="white")

    return fig

# Interface utilisateur Streamlit
st.title("Analyse des Joueurs - Attaquants et Milieux")
position = st.selectbox("Sélectionnez un poste:", ["Attaquant", "Milieu"])
league = st.selectbox("Sélectionnez une ligue:", ["Toutes les ligues", "Premier League", "Bundesliga", "La Liga", "Ligue 1", "Serie A"])

# Filtrer les joueurs
df_filtered = filter_players(position, league)

# Limiter aux 20 meilleurs joueurs selon la métrique pertinente
if position == "Attaquant":
    df_top = df_filtered.nlargest(20, "Création totale")
else:  # Milieu
    df_top = df_filtered.nlargest(20, "Endurance et Défense")

# Afficher les données filtrées et le graphique
st.write(f"Top 20 des {position}s selon la métrique sélectionnée ({league})")
fig = plot_graph(df_top, position)
st.pyplot(fig)

# CSS pour Streamlit
st.markdown(
    """
    <style>
    body {
        background-color: black;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)
