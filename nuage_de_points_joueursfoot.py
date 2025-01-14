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
    
    # Lignes pointillées
    ax.grid(True, linestyle=':', color='white', alpha=0.5)
    
    # Afficher les meilleurs joueurs avec des points plus grands
    top_15_midfielders = df.nlargest(15, "Actions Défensives")
    scatter_top = ax.scatter(
        top_15_midfielders["Distance totale parcourue avec le ballon"],
        top_15_midfielders["Actions Défensives"],
        s=top_15_midfielders["Age"] * 20,  # Taille des points proportionnelle à l'âge
        c=top_15_midfielders["Passes progressives"],
        cmap="coolwarm",
        alpha=0.7,
        edgecolors="w"
    )

    # Afficher les autres joueurs avec de petits points
    other_midfielders = df[~df["Joueur"].isin(top_15_midfielders["Joueur"])]
    scatter_other = ax.scatter(
        other_midfielders["Distance totale parcourue avec le ballon"],
        other_midfielders["Actions Défensives"],
        s=other_midfielders["Age"] * 5,  # Taille des points plus petits
        c=other_midfielders["Passes progressives"],
        cmap="coolwarm",
        alpha=0.3,
        edgecolors="w"
    )

    for i, row in top_15_midfielders.iterrows():
        ax.text(
            row["Distance totale parcourue avec le ballon"],
            row["Actions Défensives"] + 0.1,
            row["Joueur"],
            fontsize=10,
            color="white",  # Noms en blanc
            ha="center",
            va="bottom"  # Éviter le chevauchement en positionnant les noms légèrement au-dessus
        )

    cbar = plt.colorbar(scatter_top, ax=ax)
    cbar.set_label("Passes progressives", rotation=270, labelpad=15, color="white")
    cbar.ax.yaxis.set_tick_params(color="white")
    plt.setp(plt.getp(cbar.ax.axes, "yticklabels"), color="white")

    ax.set_title("Endurance et Activité Défensive des Milieux", fontsize=16, color="white")
    ax.set_xlabel("Distance totale parcourue avec le ballon", fontsize=12, color="white")
    ax.set_ylabel("Actions Défensives (Tacles + Interceptions)", fontsize=12, color="white")

    # Personnalisation des axes (lignes pointillées)
    ax.spines['top'].set_color('white')
    ax.spines['top'].set_linewidth(1)
    ax.spines['right'].set_color('white')
    ax.spines['right'].set_linewidth(1)
    ax.spines['left'].set_color('white')
    ax.spines['left'].set_linewidth(1)
    ax.spines['bottom'].set_color('white')
    ax.spines['bottom'].set_linewidth(1)

    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')

    return fig

def plot_forwards(df):
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_facecolor("black")

    # Lignes pointillées
    ax.grid(True, linestyle=':', color='white', alpha=0.5)

    # Afficher les meilleurs joueurs avec des points plus grands
    top_15_forwards = df.nlargest(15, "Création totale")
    scatter_top = ax.scatter(
        top_15_forwards["Passes cles"],
        top_15_forwards["Actions menant a un tir par 90 minutes"],
        s=top_15_forwards["Age"] * 20,  # Taille des points proportionnelle à l'âge
        c=top_15_forwards["Actions menant a un but par 90 minutes"],
        cmap="coolwarm",
        alpha=0.7,
        edgecolors="white"
    )

    # Afficher les autres joueurs avec de petits points
    other_forwards = df[~df["Joueur"].isin(top_15_forwards["Joueur"])]
    scatter_other = ax.scatter(
        other_forwards["Passes cles"],
        other_forwards["Actions menant a un tir par 90 minutes"],
        s=other_forwards["Age"] * 5,  # Taille des points plus petits
        c=other_forwards["Actions menant a un but par 90 minutes"],
        cmap="coolwarm",
        alpha=0.3,
        edgecolors="w"
    )

    for i, row in top_15_forwards.iterrows():
        ax.text(
            row["Passes cles"],
            row["Actions menant a un tir par 90 minutes"] + 0.1,
            row["Joueur"],
            fontsize=10,
            color="white",  # Noms en blanc
            ha="center",
            va="bottom"  # Éviter le chevauchement en positionnant les noms légèrement au-dessus
        )

    cbar = plt.colorbar(scatter_top, ax=ax)
    cbar.set_label("Actions menant à un but par 90 minutes", rotation=270, labelpad=15, color="white")
    cbar.ax.yaxis.set_tick_params(color="white")
    plt.setp(plt.getp(cbar.ax.axes, "yticklabels"), color="white")

    ax.set_title("Création d'occasion par 90 min", fontsize=16, color="white")
    ax.set_xlabel("Passes clés", fontsize=12, color="white")
    ax.set_ylabel("Actions menant à un tir par 90 minutes", fontsize=12, color="white")

    # Personnalisation des axes (lignes pointillées)
    ax.spines['top'].set_color('white')
    ax.spines['top'].set_linewidth(1)
    ax.spines['right'].set_color('white')
    ax.spines['right'].set_linewidth(1)
    ax.spines['left'].set_color('white')
    ax.spines['left'].set_linewidth(1)
    ax.spines['bottom'].set_color('white')
    ax.spines['bottom'].set_linewidth(1)

    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')

    return fig

# Interface utilisateur avec Streamlit
st.title("Analyse des joueurs - Milieux et Attaquants")

# Sélecteur de position et de ligue
position_option = st.selectbox("Sélectionnez une position:", ["Milieu", "Attaquant"])
league_option = st.selectbox(
    "Sélectionnez une ligue:",
    ["Toutes les ligues", "Premier League", "Bundesliga", "La Liga", "Ligue 1", "Serie A"]
)

# Filtrer les joueurs en fonction de la position et de la ligue
if position_option == "Milieu":
    df_position = df[df["Position"].str.contains("Midfielder", case=False, na=False)]
    metric = "Actions Défensives"
    plot_function = plot_midfielders
else:
    df_position = df[df["Position"].str.contains("Forward", case=False, na=False)]
    metric = "Création totale"
    plot_function = plot_forwards

if league_option != "Toutes les ligues":
    df_position = df_position[df_position["Ligue"] == league_option]

# Prendre les 100 premiers joueurs selon la métrique sélectionnée
top_100_players = df_position.nlargest(100, metric)

# Afficher le graphique dans Streamlit
st.write(f"Top 100 des {position_option.lower()}s ({league_option})")
fig = plot_function(top_100_players)
st.pyplot(fig)
