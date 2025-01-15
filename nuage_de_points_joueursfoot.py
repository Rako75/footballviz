import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from adjustText import adjust_text

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

# Fonction pour tracer les graphiques avec amélioration
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
    
    # Ajouter les noms des joueurs avec ajustement pour éviter les chevauchements
    texts = []
    for i, row in df.iterrows():
        texts.append(ax.text(
            row["Passes cles"],
            row["Actions menant a un tir par 90 minutes"] + 0.1,
            row["Joueur"],
            fontsize=9,
            color="white",
            ha="center",
            va="bottom"
        ))
    adjust_text(texts, arrowprops=dict(arrowstyle="-", color='white'))

    # Barre de couleur
    cbar = plt.colorbar(scatter, ax=ax, aspect=30, pad=0.02)
    cbar.set_label("Actions menant à un but par 90 minutes", rotation=270, labelpad=15, color="white")
    cbar.ax.yaxis.set_tick_params(color="white")
    plt.setp(plt.getp(cbar.ax.axes, "yticklabels"), color="white")

    # Titres et axes
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

# Interface utilisateur avec Streamlit
st.title("Analyse des joueurs - Attaquants")

# Filtrer les attaquants et afficher les 20 meilleurs
df_forwards = df[df["Position"].str.contains("Forward", case=False, na=False)]
top_20_players = df_forwards.nlargest(20, "Création totale")

# Afficher le graphique dans Streamlit
fig = plot_forwards(top_20_players)
st.pyplot(fig)
