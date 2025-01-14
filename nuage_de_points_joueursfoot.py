import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Charger le fichier CSV
df = pd.read_csv("df_Big5.csv")

# Fonction pour préparer les données en fonction de la position
def prepare_data(df, position, league):
    # Filtrer par position
    df_filtered = df[df["Position"].str.contains(position, case=False, na=False)]
    
    # Filtrer par ligue
    if league != "Toutes les ligues":
        df_filtered = df_filtered[df_filtered["Ligue"] == league]
    
    # Calculer les métriques spécifiques
    if position == "Midfielder":
        df_filtered["Actions Défensives"] = df_filtered["Tacles"] + df_filtered["Interceptions"]
        df_filtered["Création Off."] = (
            df_filtered["Passes cles"] +
            df_filtered["Actions menant a un tir par 90 minutes"] +
            df_filtered["Actions menant a un but par 90 minutes"]
        )
        df_filtered["Score Total"] = df_filtered["Actions Défensives"] + df_filtered["Création Off."]
    elif position == "Forward":
        df_filtered["Création totale"] = (
            df_filtered["Passes cles"] +
            df_filtered["Actions menant a un tir par 90 minutes"] +
            df_filtered["Actions menant a un but par 90 minutes"]
        )
        df_filtered["Score Total"] = df_filtered["Création totale"]
    
    # Retourner les 20 meilleurs joueurs
    return df_filtered.nlargest(20, "Score Total")

# Fonction pour tracer le graphique
def plot_graph(df, position):
    fig, ax = plt.subplots(figsize=(14, 10))
    
    if position == "Midfielder":
        scatter = ax.scatter(
            df["Distance totale parcourue avec le ballon"],
            df["Actions Défensives"],
            s=df["Création Off."] * 10,  # Taille proportionnelle à la création offensive
            c=df["Passes progressives"],  # Couleur basée sur les passes progressives
            cmap="coolwarm",
            alpha=0.7,
            edgecolors="w"
        )
        ax.set_xlabel("Distance totale parcourue avec le ballon", fontsize=12)
        ax.set_ylabel("Actions Défensives (Tacles + Interceptions)", fontsize=12)
        ax.set_title("Top 20 Milieux Box-to-Box", fontsize=16)
    elif position == "Forward":
        scatter = ax.scatter(
            df["Passes cles"],
            df["Actions menant a un tir par 90 minutes"],
            s=df["Age"] * 10,  # Taille proportionnelle à l'âge
            c=df["Actions menant a un but par 90 minutes"],  # Couleur basée sur actions décisives
            cmap="coolwarm",
            alpha=0.7,
            edgecolors="w"
        )
        ax.set_xlabel("Passes clés", fontsize=12)
        ax.set_ylabel("Actions menant à un tir par 90 minutes", fontsize=12)
        ax.set_title("Top 20 Attaquants", fontsize=16)
    
    # Ajouter les noms des joueurs
    for i, row in df.iterrows():
        ax.text(
            row.iloc[0],  # X (première colonne correspondant à X selon la position)
            row.iloc[1] + 0.1,  # Y (décalage léger pour affichage)
            row["Joueur"],
            fontsize=10,
            color="white" if position == "Forward" else "black",
            ha="center"
        )
    
    # Ajouter une colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label("Valeur de la couleur", rotation=270, labelpad=15)
    
    return fig

# Interface utilisateur Streamlit
st.title("Analyse des joueurs par position et ligue")

# Sélecteurs pour la position et la ligue
position_option = st.selectbox("Sélectionnez la position :", ["Milieu", "Attaquant"])
league_option = st.selectbox("Sélectionnez une ligue :", ["Toutes les ligues", "Premier League", "Bundesliga", "La Liga", "Ligue 1", "Serie A"])

# Préparer les données en fonction des choix
filtered_data = prepare_data(df, position_option, league_option)

# Afficher le graphique
st.write(f"Top 20 {position_option.lower()}s par performance ({league_option})")
fig = plot_graph(filtered_data, position_option)
st.pyplot(fig)
