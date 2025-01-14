import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Charger le fichier CSV
df = pd.read_csv("df_Big5.csv")

# Fonction pour analyser les milieux de terrain
def analyze_midfielders(df, league_option):
    df_midfielders = df[df["Position"].str.contains("Midfielder", case=False, na=False)]
    if league_option != "Toutes les ligues":
        df_midfielders = df_midfielders[df_midfielders["Ligue"] == league_option]

    df_midfielders["Actions Défensives"] = df_midfielders["Tacles"] + df_midfielders["Interceptions"]
    df_midfielders["Création Off."] = (
        df_midfielders["Passes cles"] +
        df_midfielders["Actions menant a un tir par 90 minutes"] +
        df_midfielders["Actions menant a un but par 90 minutes"]
    )

    def plot_midfielders(df):
        fig, ax = plt.subplots(figsize=(14, 10))
        scatter = ax.scatter(
            df["Distance totale parcourue avec le ballon"],
            df["Actions Défensives"],
            s=df["Actions menant a un but"] * 10,
            c=df["Passes progressives"],
            cmap="coolwarm",
            alpha=0.7,
            edgecolors="w"
        )

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
        ax.set_title("Endurance et Activité Défensive des Milieux Box-to-Box", fontsize=16, color="black")
        ax.set_xlabel("Distance totale parcourue avec le ballon", fontsize=12, color="black")
        ax.set_ylabel("Actions Défensives (Tacles + Interceptions)", fontsize=12, color="black")
        ax.axhline(0, color='black', linewidth=1)
        ax.axvline(0, color='black', linewidth=1)
        ax.grid(False)
        return fig

    return plot_midfielders(df_midfielders)

# Interface utilisateur
st.title("Analyse des joueurs de football - Milieux et Attaquants")

position_option = st.selectbox("Choisissez la position :", ["Milieu"])
league_option = st.selectbox(
    "Sélectionnez une ligue :",
    options=["Toutes les ligues", "Premier League", "Bundesliga", "La Liga", "Ligue 1", "Serie A"]
)

if position_option == "Milieu":
    st.write(f"Analyse des milieux de terrain ({league_option})")
    fig = analyze_midfielders(df, league_option)
    st.pyplot(fig)
