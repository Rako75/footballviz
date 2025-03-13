import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Charger les données
df = pd.read_csv("df_BIG2025.csv")

# Filtrer les colonnes numériques
numerical_columns = df.select_dtypes(include=['number']).columns.tolist()

# Interface Streamlit
st.title("Analyse des joueurs de football")

# Widgets de sélection des axes
x_axis = st.sidebar.selectbox("Sélectionner la variable pour l'axe X", numerical_columns)
y_axis = st.sidebar.selectbox("Sélectionner la variable pour l'axe Y", numerical_columns)

# Sélection des compétitions
competitions = ["Premier League", "La Liga", "Ligue 1", "Bundliga", "Serie A"]
selected_competitions = st.sidebar.multiselect("Sélectionner les compétitions", competitions, default=competitions)

# Filtrer par minutes jouées
min_minutes = st.sidebar.slider("Nombre minimum de minutes jouées", min_value=0, max_value=int(df["Minutes jouées"].max()), value=500)

# Nombre de labels de joueurs
num_labels = st.sidebar.slider("Nombre de labels à afficher", min_value=0, max_value=50, value=10)
label_size = st.sidebar.slider("Taille de texte des labels", min_value=2, max_value=8, value=5)

# Filtrer les données
filtered_df = df[(df["Compétition"].isin(selected_competitions)) & (df["Minutes jouées"] >= min_minutes)]

# Convertir en numérique pour éviter les erreurs
filtered_df[x_axis] = pd.to_numeric(filtered_df[x_axis], errors='coerce')
filtered_df[y_axis] = pd.to_numeric(filtered_df[y_axis], errors='coerce')

# Sélectionner les meilleurs joueurs pour les labels
labeled_players = filtered_df.nlargest(num_labels, y_axis) if num_labels > 0 else pd.DataFrame()

# Fonction pour gérer le jitter sur les deux axes
def jitter(x_value, y_value, x_scale=0.02, y_scale=0.02):
    x_jittered = x_value + np.random.uniform(-x_scale, x_scale) * (filtered_df[x_axis].max() - filtered_df[x_axis].min())
    y_jittered = y_value + np.random.uniform(-y_scale, y_scale) * (filtered_df[y_axis].max() - filtered_df[y_axis].min())
    return x_jittered, y_jittered

# Création du scatterplot
fig = px.scatter(filtered_df, x=x_axis, y=y_axis, hover_data=["Joueur", "Équipe", "Compétition"], color="Compétition")

# Ajouter des labels avec gestion du jitter
for i, row in labeled_players.iterrows():
    x_jittered, y_jittered = jitter(row[x_axis], row[y_axis], x_scale=0.05, y_scale=0.05)  # Augmentation du jitter
    fig.add_annotation(
        x=x_jittered,  
        y=y_jittered,  
        text=row["Joueur"], 
        showarrow=False, 
        font=dict(size=label_size),
        bgcolor="rgba(0,0,0,0)"  # Fond complètement transparent
    )

fig.update_layout(title=f"Comparaison des joueurs ({x_axis} vs {y_axis})")

# Affichage du scatterplot
st.plotly_chart(fig)

# Affichage du classement top 5
if x_axis != y_axis:
    top_5 = filtered_df.nlargest(5, y_axis)[["Joueur", "Équipe", "Compétition", x_axis, y_axis]]
    st.write("### Top 5 joueurs selon la variable choisie")
    st.dataframe(top_5)
else:
    st.write("### Veuillez sélectionner deux variables différentes pour afficher le classement")
