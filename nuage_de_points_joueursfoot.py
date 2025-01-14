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
                color="black",
                ha="center"
            )

        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label("Passes progressives", rotation=270, labelpad=15)
        ax.set_title("Endurance et Activité Défensive des Milieux Box-to-Box", fontsize=16)
        ax.set_xlabel("Distance totale parcourue avec le ballon", fontsize=12)
        ax.set_ylabel("Actions Défensives (Tacles + Interceptions)", fontsize=12)
        ax.axhline(0, color='black', linewidth=1)
        ax.axvline(0, color='black', linewidth=1)
        ax.grid(False)
        return fig

    return plot_midfielders(df_midfielders)

# Fonction pour analyser les attaquants
def analyze_forwards(df, league_option):
    df_forwards = df[df["Position"].str.contains("Forward", case=False, na=False)]
    if league_option != "Toutes les ligues":
        df_forwards = df_forwards[df_forwards["Ligue"] == league_option]

    df_forwards["Création totale"] = (
        df_forwards["Passes cles"] +
        df_forwards["Actions menant a un tir par 90 minutes"] +
        df_forwards["Actions menant a un but par 90 minutes"]
    )

    top_20_forwards = df_forwards.nlargest(20, "Création totale")

    def plot_forwards(df):
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(14, 10))
        ax.set_facecolor("black")

        scatter = ax.scatter(
            df["Passes cles"],
            df["Actions menant a un tir par 90 minutes"],
            s=df["Age"] * 10,
            c=df["Actions menant a un but par 90 minutes"],
            cmap="coolwarm",
            alpha=0.7,
            edgecolors="white"
        )

        for i, row in df.iterrows():
            ax.text(
                row["Passes cles"],
                row["Actions menant a un tir par 90 minutes"] + 0.1,
                row["Joueur"],
                fontsize=10,
                color="white",
                ha="center"
            )

        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label("Actions menant à un but par 90 minutes", rotation=270, labelpad=15, color="white")
        cbar.ax.yaxis.set_tick_params(color="white")
        plt.setp(plt.getp(cbar.ax.axes, "yticklabels"), color="white")
        ax.set_title("Création d'occasion par 90 min", fontsize=16, color="white")
        ax.set_xlabel("Passes clés", fontsize=12, color="white")
        ax.set_ylabel("Actions menant à un tir par 90 minutes", fontsize=12, color="white")
        ax.tick_params(colors="white")
        ax.axhline(0, color='white', linestyle='--', linewidth=1)
        ax.axvline(0, color='white', linestyle='--', linewidth=1)
        return fig

    return plot_forwards(top_20_forwards)

# Interface utilisateur
st.title("Analyse des joueurs de football - Milieux et Attaquants")

position_option = st.selectbox("Choisissez la position :", ["Milieu", "Attaquant"])
league_option = st.selectbox(
    "Sélectionnez une ligue :",
    options=["Toutes les ligues", "Premier League", "Bundesliga", "La Liga", "Ligue 1", "Serie A"]
)

if position_option == "Milieu":
    st.write(f"Analyse des milieux de terrain ({league_option})")
    fig = analyze_midfielders(df, league_option)
elif position_option == "Attaquant":
    st.write(f"Analyse des attaquants ({league_option})")
    fig = analyze_forwards(df, league_option)

st.pyplot(fig)
