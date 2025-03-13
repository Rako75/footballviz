import pandas as pd
import plotly.express as px
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

# Filtrer le top 20 des joueurs en fonction d'une statistique clé (par exemple, les passes progressives)
df_top_20 = df.nlargest(20, "Passes progressives")

# Fonction pour tracer le premier graphique scatterplot avec Plotly
def plot_midfielders(df):
    fig = px.scatter(
        df,
        x="Distance totale parcourue avec le ballon",
        y="Actions Défensives",
        size="Age",  # Taille des points basée sur l'âge
        color="Passes progressives",  # Couleur des points basée sur les passes progressives
        hover_name="Joueur",  # Afficher le nom du joueur au survol
        color_continuous_scale="coolwarm",  # Palette de couleurs
        title="Endurance et Activité Défensive des Milieux",
        labels={"Distance totale parcourue avec le ballon": "Distance parcourue avec le ballon",
                "Actions Défensives": "Actions Défensives (Tacles + Interceptions)",
                "Passes progressives": "Passes progressives"},
        template="plotly_dark"
    )
    fig.update_layout(
        showlegend=True,
        plot_bgcolor='black',
        paper_bgcolor='black',
        font=dict(color='white'),
        title_font=dict(size=16),
        xaxis_title_font=dict(size=12),
        yaxis_title_font=dict(size=12),
        margin=dict(l=50, r=50, t=100, b=50)
    )
    return fig

# Fonction pour tracer le graphique des attaquants
def plot_forwards(df):
    fig = px.scatter(
        df,
        x="Passes cles",
        y="Actions menant a un tir par 90 minutes",
        size="Age",
        color="Actions menant a un but par 90 minutes",
        hover_name="Joueur",
        color_continuous_scale="coolwarm",
        title="Création d'occasion par 90 min",
        labels={"Passes cles": "Passes clés",
                "Actions menant a un tir par 90 minutes": "Actions menant à un tir par 90 min",
                "Actions menant a un but par 90 minutes": "Actions menant à un but par 90 min"},
        template="plotly_dark"
    )
    fig.update_layout(
        showlegend=True,
        plot_bgcolor='black',
        paper_bgcolor='black',
        font=dict(color='white'),
        title_font=dict(size=16),
        xaxis_title_font=dict(size=12),
        yaxis_title_font=dict(size=12),
        margin=dict(l=50, r=50, t=100, b=50)
    )
    return fig

# Fonction pour tracer le graphique des défenseurs
def plot_defenders(df):
    fig = px.scatter(
        df,
        x="Tacles",
        y="Interceptions",
        size="Duels aeriens gagnes",
        color="Duels aeriens gagnes",
        hover_name="Joueur",
        color_continuous_scale="viridis",
        title="Performance Défensive : Tacles et Interceptions",
        labels={"Tacles": "Tacles",
                "Interceptions": "Interceptions",
                "Duels aeriens gagnes": "Duels aériens gagnés"},
        template="plotly_dark"
    )
    fig.update_layout(
        showlegend=True,
        plot_bgcolor='black',
        paper_bgcolor='black',
        font=dict(color='white'),
        title_font=dict(size=16),
        xaxis_title_font=dict(size=12),
        yaxis_title_font=dict(size=12),
        margin=dict(l=50, r=50, t=100, b=50)
    )
    return fig

# Nouveau scatterplot comparant les passes clés et les actions menant à un but
def plot_passing_vs_goal_contrib(df):
    fig = px.scatter(
        df,
        x="Passes cles",
        y="Actions menant a un but par 90 minutes",
        size="Duels aeriens gagnes",  # Taille des points basée sur les duels aériens gagnés
        color="Age",  # Couleur des points basée sur l'âge
        hover_name="Joueur",  # Afficher le nom du joueur au survol
        color_continuous_scale="Viridis",  # Palette de couleurs
        title="Passes clés vs Actions menant à un but",
        labels={"Passes cles": "Passes clés",
                "Actions menant a un but par 90 minutes": "Actions menant à un but par 90 min",
                "Duels aeriens gagnes": "Duels aériens gagnés"},
        template="plotly_dark"
    )
    fig.update_layout(
        showlegend=True,
        plot_bgcolor='black',
        paper_bgcolor='black',
        font=dict(color='white'),
        title_font=dict(size=16),
        xaxis_title_font=dict(size=12),
        yaxis_title_font=dict(size=12),
        margin=dict(l=50, r=50, t=100, b=50)
    )
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
    df_position = df_top_20[df_top_20["Position"].str.contains("Midfielder", case=False, na=False)]
    plot_function = plot_midfielders
elif position_option == "Attaquant":
    df_position = df_top_20[df_top_20["Position"].str.contains("Forward", case=False, na=False)]
    plot_function = plot_forwards
else:  # Défenseur
    df_position = df_top_20[df_top_20["Position"].str.contains("Defender", case=False, na=False)]
    plot_function = plot_defenders

if league_option != "Toutes les ligues":
    df_position = df_position[df_position["Ligue"] == league_option]

# Afficher le premier graphique (activité défensive ou offensive)
st.write(f"Analyse des {position_option.lower()}s ({league_option})")
fig = plot_function(df_position)
st.plotly_chart(fig)

# Afficher le nouveau scatterplot Passes clés vs Actions menant à un but
st.write("Passes clés vs Actions menant à un but")
fig2 = plot_passing_vs_goal_contrib(df_top_20)
st.plotly_chart(fig2)
