import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Charger le fichier CSV
df = pd.read_csv("df_Big5.csv")

# Ajouter des colonnes pertinentes pour l'analyse
df["Actions Défensives"] = df["Tacles"] + df["Interceptions"]
df["Création Off."] = (
    df["Passes cles"] +
    df["Actions menant a un tir par 90 minutes"] +
    df["Actions menant a un but par 90 minutes"]
)
df["Création totale"] = df["Création Off."]

# Fonctions pour tracer les graphiques
def plot_midfielders(df):
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_facecolor("black")
    
    ax.grid(True, linestyle=':', color='white', alpha=0.5)
    scatter = ax.scatter(
        df["Distance totale parcourue avec le ballon"],
        df["Actions Défensives"],
        s=df["Age"] * 20,
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
            color="white",
            ha="center",
            va="bottom"
        )

    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label("Passes progressives", rotation=270, labelpad=15, color="white")
    cbar.ax.yaxis.set_tick_params(color="white")
    plt.setp(plt.getp(cbar.ax.axes, "yticklabels"), color="white")

    ax.set_title("Endurance et Activité Défensive des Milieux", fontsize=16, color="white")
    ax.set_xlabel("Distance totale parcourue avec le ballon", fontsize=12, color="white")
    ax.set_ylabel("Actions Défensives (Tacles + Interceptions)", fontsize=12, color="white")
    ax.spines['top'].set_color('black')
    ax.spines['right'].set_color('black')
    ax.spines['left'].set_color('black')
    ax.spines['bottom'].set_color('black')
    ax.tick_params(axis='x', colors='black')
    ax.tick_params(axis='y', colors='black')

    return fig

def plot_forwards(df):
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_facecolor("black")
    
    ax.grid(True, linestyle=':', color='white', alpha=0.5)
    scatter = ax.scatter(
        df["Passes cles"],
        df["Actions menant a un tir par 90 minutes"],
        s=df["Age"] * 20,
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
            ha="center",
            va="bottom"
        )

    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label("Actions menant à un but par 90 minutes", rotation=270, labelpad=15, color="white")
    cbar.ax.yaxis.set_tick_params(color="white")
    plt.setp(plt.getp(cbar.ax.axes, "yticklabels"), color="white")

    ax.set_title("Création d'occasion par 90 min", fontsize=16, color="white")
    ax.set_xlabel("Passes clés", fontsize=12, color="white")
    ax.set_ylabel("Actions menant à un tir par 90 minutes", fontsize=12, color="white")
    ax.spines['top'].set_color('white')
    ax.spines['right'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.spines['bottom'].set_color('white')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')

    return fig

def plot_defenders(df):
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_facecolor("black")
    
    ax.grid(True, linestyle=':', color='white', alpha=0.5)
    scatter = ax.scatter(
        df["Tacles"],
        df["Interceptions"],
        s=df["Duels aeriens gagnes"] * 10,
        c=df["Duels aeriens gagnes"],
        cmap="viridis",
        alpha=0.7,
        edgecolors="w"
    )

    for i, row in df.iterrows():
        ax.text(
            row["Tacles"],
            row["Interceptions"] + 0.1,
            row["Joueur"],
            fontsize=10,
            color="white",
            ha="center",
            va="bottom"
        )

    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label("Duels aériens gagnés", rotation=270, labelpad=15, color="white")
    cbar.ax.yaxis.set_tick_params(color="white")
    plt.setp(plt.getp(cbar.ax.axes, "yticklabels"), color="white")

    ax.set_title("Performance Défensive : Tacles et Interceptions", fontsize=16, color="white")
    ax.set_xlabel("Tacles", fontsize=12, color="white")
    ax.set_ylabel("Interceptions", fontsize=12, color="white")
    ax.spines['top'].set_color('white')
    ax.spines['right'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.spines['bottom'].set_color('white')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')

    return fig

# Interface utilisateur avec Streamlit
st.title("Analyse des joueurs - Milieux, Attaquants et Défenseurs")

# Sélecteur de position et de ligue
position_option = st.selectbox("Sélectionnez une position:", ["Milieu", "Attaquant", "Défenseur"])
league_option = st.selectbox(
    "Sélectionnez une ligue:",
    ["Toutes les ligues", "Premier League", "Bundesliga", "La Liga", "Ligue 1", "Serie A"]
)

# Filtrer les joueurs en fonction de la position et de la ligue
if position_option == "Milieu":
    df_position = df[df["Position"].str.contains("Midfielder", case=False, na=False)]
    plot_function = plot_midfielders
elif position_option == "Attaquant":
    df_position = df[df["Position"].str.contains("Forward", case=False, na=False)]
    plot_function = plot_forwards
else:  # Défenseur
    df_position = df[df["Position"].str.contains("Defender", case=False, na=False)]
    plot_function = plot_defenders

if league_option != "Toutes les ligues":
    df_position = df_position[df_position["Ligue"] == league_option]

# Afficher le graphique dans Streamlit
st.write(f"Analyse des {position_option.lower()}s ({league_option})")
fig = plot_function(df_position)
st.pyplot(fig)
