import pandas as pd
import numpy as np
import streamlit as st
from mplsoccer import PyPizza
import matplotlib.pyplot as plt
import requests
from io import BytesIO

# Fonction pour charger et prétraiter les données
def load_and_preprocess_data(file_path, position):
    data = pd.read_csv(file_path)
    data = data[data['Matchs joués'].astype(int) > 10]

    if position == "Attaquant":
        stats_cols = ['Buts + passes déc. p/90min', 'Distance progressive',
                      'Passes progressives', 'Réceptions progressives', 'xG p/90 min', 'xAG p/90 min']
    elif position == "Défenseur":
        stats_cols = ['Interceptions', 'Tacles gagnants', 'Dégagements',
                      'Duels défensifs gagnés', 'Passes progressives', 'Duels aériens gagnés']
    elif position == "Milieu":
        stats_cols = ['Passes clés', 'Actions créant un tir p/90 min', 
                      'xG + xAG p/90 min', 'Passes dans le dernier tiers',
                      'Passes progressives', 'Courses progressives']
    else:
        raise ValueError("Position non reconnue")

    data = data.rename(columns={
        'Distance progressive parcourue avec le ballon': 'Distance progressive',
        'Buts par 90 minutes':'Buts p/90 min',
        'Passes décisives par 90 minutes': 'Passes déc. p/90 min',
        'Buts + Passes décisives par 90 minutes': 'Buts + passes déc. p/90min',
        'Buts attendus par 90 minutes': 'xG p/90 min',
        'Passes décisives attendues par 90 minutes': 'xAG p/90 min',
        'Actions menant à un tir par 90 minutes':'Actions créant un tir p/90 min',
        'Somme des buts et passes attendues par 90 minutes':'xG + xAG p/90 min'
    })
    for col in stats_cols:
        if col in data.columns:
            data[col] = data[col].astype(float) / data['Matchs en 90 min']

    for col in stats_cols:
        if col in data.columns:
            data[col] = (data[col].rank(pct=True) * 100).astype(int)

    return data, stats_cols

def load_logo(logo_url):
    response = requests.get(logo_url)
    image = plt.imread(BytesIO(response.content), format='png')
    return image

league_files = {
    "Premier League": {"Attaquant": "Premier_League_Attaquant.csv", "Défenseur": "Premier_League_Défenseur.csv", "Milieu": "Premier_League_Milieu.csv"},
    "Bundesliga": {"Attaquant": "Bundesliga_Attaquant.csv", "Défenseur": "Bundesliga_Défenseur.csv", "Milieu": "Bundesliga_Milieu.csv"},
    "La Liga": {"Attaquant": "La_Liga_Attaquant.csv", "Défenseur": "La_Liga_Défenseur.csv", "Milieu": "La_Liga_Milieu.csv"},
    "Ligue 1": {"Attaquant": "Ligue_1_Attaquant.csv", "Défenseur": "Ligue_1_Défenseur.csv", "Milieu": "Ligue_1_Milieu.csv"},
    "Serie A": {"Attaquant": "Serie_A_Attaquant.csv", "Défenseur": "Serie_A_Défenseur.csv", "Milieu": "Serie_A_Milieu.csv"},
}

logo_directories = {
    "Premier League": "https://raw.githubusercontent.com/Rako75/footballviz/main/Premier%20League%20Logos",
    "Bundesliga": "https://raw.githubusercontent.com/Rako75/footballviz/main/Bundesliga%20Logos",
    "La Liga": "https://raw.githubusercontent.com/Rako75/footballviz/main/La%20Liga%20Logos",
    "Ligue 1": "https://raw.githubusercontent.com/Rako75/footballviz/main/Ligue%201%20Logos",
    "Serie A": "https://raw.githubusercontent.com/Rako75/footballviz/main/Serie%20A%20Logos",
}

# Streamlit app
st.sidebar.title("Radarchart - Saison 24/25")

selected_position = st.sidebar.selectbox("Choisissez la position", options=["Attaquant", "Défenseur", "Milieu"])
league1 = st.sidebar.selectbox("Sélectionnez la ligue du premier joueur", options=list(league_files.keys()))
league2 = st.sidebar.selectbox("Sélectionnez la ligue du deuxième joueur", options=list(league_files.keys()))

data1, params1 = load_and_preprocess_data(league_files[league1][selected_position], selected_position)
data2, params2 = load_and_preprocess_data(league_files[league2][selected_position], selected_position)

player1 = st.sidebar.selectbox("Sélectionnez le premier joueur", options=data1['Joueur'].unique())
player2 = st.sidebar.selectbox("Sélectionnez le deuxième joueur", options=data2['Joueur'].unique())

player1_data = data1[data1['Joueur'] == player1].iloc[0][params1].tolist()
player2_data = data2[data2['Joueur'] == player2].iloc[0][params2].tolist()

club1 = data1[data1['Joueur'] == player1].iloc[0]['Équipe']
club2 = data2[data2['Joueur'] == player2].iloc[0]['Équipe']
age1 = int(data1[data1['Joueur'] == player1].iloc[0]['Âge'])
age2 = int(data2[data2['Joueur'] == player2].iloc[0]['Âge'])

club1_logo_url = f"{logo_directories[league1]}/{club1}.png"
club2_logo_url = f"{logo_directories[league2]}/{club2}.png"
club1_logo = load_logo(club1_logo_url)
club2_logo = load_logo(club2_logo_url)

# PyPizza Radar
slice_colors = ["#1A1A1A"] * len(params1)
text_colors = ["#F0F0F0"] * len(params1)

baker = PyPizza(
    params=params1,
    background_color="#121212",
    straight_line_color="#FFFFFF",
    straight_line_lw=1,
    last_circle_lw=1,
    other_circle_lw=0,
    inner_circle_size=20
)

fig, ax = baker.make_pizza(
    player1_data,
    compare_values=player2_data,
    figsize=(8, 8),
    color_blank_space="same",
    slice_colors=slice_colors,
    value_colors=["#9B3647", "#3282b8"],
    value_bck_colors=["#9B364733", "#3282b833"],
    blank_alpha=0.4,
    param_location=110,
    kwargs_slices=dict(edgecolor="#FFFFFF", zorder=2, linewidth=1),
    kwargs_params=dict(color=text_colors, fontsize=12, va="center"),
    kwargs_values=dict(fontsize=11, color=text_colors, zorder=3, bbox=dict(
        edgecolor="none", facecolor="#000000", boxstyle="round,pad=0.2", lw=0)),
)

fig.suptitle("Comparaison des performances", color="#F0F0F0", fontsize=16)

# Affichage dans Streamlit
col1, col2, col3 = st.columns([6, 15, 6])

key_stat = {
    "Attaquant": "xG p/90 min",
    "Défenseur": "Interceptions",
    "Milieu": "Passes progressives"
}

# Col 1 : joueur 1
with col1:
    st.image(club1_logo, width=100)
    st.subheader(f"{player1} (rouge)")
    st.write(f"**Âge :** {age1}")
    st.write(f"**Titularisations :** {int(data1[data1['Joueur'] == player1].iloc[0]['Titularisations'])}")
    st.write(f"**Buts :** {int(data1[data1['Joueur'] == player1].iloc[0]['Buts'])}")
    st.write(f"**Passes déc. :** {int(data1[data1['Joueur'] == player1].iloc[0]['Passes décisives'])}")
    st.write(f"**{key_stat[selected_position]} :** {data1[data1['Joueur'] == player1].iloc[0][key_stat[selected_position]]}")

# Col 2 : radar
with col2:
    st.pyplot(fig)

# Col 3 : joueur 2
with col3:
    st.image(club2_logo, width=100)
    st.subheader(f"{player2} (bleu)")
    st.write(f"**Âge :** {age2}")
    st.write(f"**Titularisations :** {int(data2[data2['Joueur'] == player2].iloc[0]['Titularisations'])}")
    st.write(f"**Buts :** {int(data2[data2['Joueur'] == player2].iloc[0]['Buts'])}")
    st.write(f"**Passes déc. :** {int(data2[data2['Joueur'] == player2].iloc[0]['Passes décisives'])}")
    st.write(f"**{key_stat[selected_position]} :** {data2[data2['Joueur'] == player2].iloc[0][key_stat[selected_position]]}")
