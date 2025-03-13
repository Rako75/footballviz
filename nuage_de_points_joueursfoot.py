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

# Sélectionner les meilleurs joueurs pour les labels (Top 10 pour chaque variable)
top_10_x = filtered_df.nlargest(10, x_axis)
top_10_y = filtered_df.nlargest(10, y_axis)

# Fonction pour gérer le jitter sur les deux axes
def jitter(x_value, y_value, x_scale=0.02, y_scale=0.02):
    x_jittered = x_value + np.random.uniform(-x_scale, x_scale) * (filtered_df[x_axis].max() - filtered_df[x_axis].min())
    y_jittered = y_value + np.random.uniform(-y_scale, y_scale) * (filtered_df[y_axis].max() - filtered_df[y_axis].min())
    return x_jittered, y_jittered

# Création du graphique vide sans points
fig = px.scatter()

# Ajouter des annotations avec les labels et les classements pour Top 10 X et Y
for rank, (i, row) in enumerate(top_10_x.iterrows(), 1):
    x_jittered, y_jittered = jitter(row[x_axis], row[y_axis], x_scale=0.05, y_scale=0.05)
    fig.add_annotation(
        x=x_jittered,  
        y=y_jittered,  
        text=f"{row['Joueur']} ({rank})",  # Afficher le nom et le classement
        showarrow=False, 
        font=dict(size=label_size),
        bgcolor="rgba(0,0,0,0)"  # Fond complètement transparent
    )

for rank, (i, row) in enumerate(top_10_y.iterrows(), 1):
    x_jittered, y_jittered = jitter(row[x_axis], row[y_axis], x_scale=0.05, y_scale=0.05)
    fig.add_annotation(
        x=x_jittered,  
        y=y_jittered,  
        text=f"{row['Joueur']} ({rank})",  # Afficher le nom et le classement
        showarrow=False, 
        font=dict(size=label_size),
        bgcolor="rgba(0,0,0,0)"  # Fond complètement transparent
    )

# Ajuster le layout
fig.update_layout(
    title=f"Classement des joueurs ({x_axis} vs {y_axis})",
    xaxis_title=x_axis,
    yaxis_title=y_axis,
    showlegend=False  # Ne pas afficher la légende
)

# Affichage du graphique
st.plotly_chart(fig)

# Affichage des Top 10 joueurs pour X et Y
st.write(f"### Top 10 des meilleurs joueurs selon la variable {x_axis}")
st.dataframe(top_10_x[['Joueur', 'Équipe', 'Compétition', x_axis]])

st.write(f"### Top 10 des meilleurs joueurs selon la variable {y_axis}")
st.dataframe(top_10_y[['Joueur', 'Équipe', 'Compétition', y_axis]])
