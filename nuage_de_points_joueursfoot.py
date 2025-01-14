import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Charger le fichier CSV
df = pd.read_csv("df_Big5.csv")

# Fonction pour analyser les milieux de terrain
def analyze_midfielders(df, league_option):
    # Filtrer les milieux
    df_midfielders = df[df["Position"].str.contains("Midfielder", case=False, na=False)]
    if league_option != "Toutes les ligues":
        df_midfielders = df_midfielders[df_midfielders["Ligue"] == league_option]

    # Ajouter des métriques combinées
    df_midfielders["Actions Défensives"] = df_midfielders["Tacles"] + df_midfielders["Interceptions"]
    df_midfielders["Création Off."] = (
        df_midfielders["Passes cles"] +
        df_midfielders["Actions menant a un tir par 90 minutes"] +
        df_midfielders["Actions menant a un but par 90 minutes"]
    )
    df_midfielders["Score Total"] = df_midfielders["Actions Défensives"] + df_midfielders["Création Off."]

    # Prendre les 20 meilleurs
    top_20_midfielders = df_midfielders.nlargest(20, "Score Total")

    # Fonction pour tracer les graphiques
    def plot_midfielders(df):
        fig, ax = plt.subplots(figsize=(14, 10))
        scatter = ax.scatter(
            df["Distance totale parcourue avec le ballon"],
            df["Actions Défensives"],
            s=df["Création Off."] * 10,
            c=df["Passes progressives"],
            cmap="coolwarm",
            alpha=0.7,
            edgecolors="w"
        )

        # Ajouter les noms des joueurs
        for i, row in df.iterrows():
            ax.text(
                row["Distance totale parcourue avec le ballon"],
                row["Actions Défensives"] + 0.1,
                row["Joueur"],
                fontsize=10,
                color="white",  # Texte en blanc
                ha="center"
            )

        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label("Passes progressives", rotation=270, labelpad=15, color="black")
        ax.set_title("Top 20 Milieux Box-to-Box : Endurance et Activité Défensive", fontsize=16, color="black")
        ax.set_xlabel("Distance totale parcourue avec le ballon", fontsize=12, color="black")
        ax.set_ylabel("Actions Défensives (Tacles + Interceptions)", fontsize=12, color="black")
        ax.axhline(0, color='black', linewidth=1)
        ax.axvline(0, color='black', linewidth=1)
        ax.grid(False)
        return fig

    return plot_midfielders(top_20_midfielders)

# Interface utilisateur
st.title("Analyse des meilleurs milieux de terrain - Milieux Box-to-Box")

# Sélecteur de ligue
league_option = st.selectbox(
    "Sélectionnez une ligue :",
    options=["Toutes les ligues", "Premier League", "Bundesliga", "La Liga", "Ligue 1", "Serie A"]
)

st.write(f"Top 20 des meilleurs milieux ({league_option})")
fig = analyze_midfielders(df, league_option)
st.pyplot(fig)
