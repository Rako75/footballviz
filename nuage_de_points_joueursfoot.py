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
    
    scatter = ax.scatter(
        df["Distance totale parcourue avec le ballon"],
        df["Actions Défensives"],
        s=df["Age"] * 20,  # Taille des points proportionnelle à l'âge
        c=df["Passes progressives"],
        cmap="coolwarm",
        alpha=0.7,
        edgecolors="w"
    )

    # Ajouter des numéros aux joueurs pour éviter les chevauchements
    for i, row in df.iterrows():
        ax.text(
            row["Distance totale parcourue avec le ballon"],
            row["Actions Défensives"] + 0.1,
            str(i + 1),  # Numéro du joueur
            fontsize=10,
            color="white",  # Noms en blanc
            ha="center",
            va="bottom"  # Éviter le chevauchement
        )

    # Ajouter une légende avec les noms des joueurs
    legend_labels = [f"{i + 1}: {row['Joueur']}" for i, row in df.iterrows()]
    plt.legend(legend_labels, loc='upper left', fontsize=8, title="Joueurs", title_fontsize=10)

    cbar = plt.colorbar(scatter, ax=ax)
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

    scatter = ax.scatter(
        df["Passes cles"],
        df["Actions menant a un tir par 90 minutes"],
        s=df["Age"] * 20,  # Taille des points proportionnelle à l'âge
        c=df["Actions menant a un but par 90 minutes"],
        cmap="coolwarm",
        alpha=0.7,
        edgecolors="white"
    )

    # Ajouter des numéros aux joueurs pour éviter les chevauchements
    for i, row in df.iterrows():
        ax.text(
            row["Passes cles"],
            row["Actions menant a un tir par 90 minutes"] + 0.1,
            str(i + 1),  # Numéro du joueur
            fontsize=10,
            color="white",  # Noms en blanc
            ha="center",
            va="bottom"  # Éviter le chevauchement
        )

    # Ajouter une légende avec les noms des joueurs
    legend_labels = [f"{i + 1}: {row['Joueur']}" for i, row in df.iterrows()]
    plt.legend(legend_labels, loc='upper left', fontsize=8, title="Joueurs", title_fontsize=10)

    cbar = plt.colorbar(scatter, ax=ax)
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

# Prendre les 20 meilleurs joueurs selon la métrique sélectionnée
top_20_players = df_position.nlargest(20, metric)

# Afficher le graphique dans Streamlit
st.write(f"Top 20 des {position_option.lower()}s ({league_option})")
fig = plot_function(top_20_players)
st.pyplot(fig)
