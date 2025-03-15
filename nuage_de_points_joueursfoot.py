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
competitions = ["Premier League", "La Liga", "Ligue 1", "Bundesliga", "Serie A"]
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
top_10_x = filtered_df.nlargest(num_labels, x_axis)
top_10_y = filtered_df.nlargest(num_labels, y_axis)

# Fusionner les deux top 10 (éviter doublons)
top_10_combined = pd.concat([top_10_x, top_10_y]).drop_duplicates(subset="Joueur")

# S'assurer que le nombre de labels affichés correspond au nombre sélectionné
top_10_combined = top_10_combined.head(num_labels)

# Création du graphique avec **TOUS** les joueurs
fig = px.scatter(filtered_df, x=x_axis, y=y_axis, hover_data=["Joueur", "Équipe", "Compétition"], color="Compétition")

# Ajouter des annotations juste au-dessus des points
for i, row in top_10_combined.iterrows():
    fig.add_annotation(
        x=row[x_axis],  
        y=row[y_axis] + (filtered_df[y_axis].max() - filtered_df[y_axis].min()) * 0.02,  # Décalage vers le haut
        text=row["Joueur"],  
        showarrow=False,  
        font=dict(size=label_size, color="black"),
        bgcolor="rgba(0,0,0,0)"  # Fond transparent
    )

# Ajuster le layout
fig.update_layout(
    title=f"Analyse des joueurs ({x_axis} vs {y_axis})",
    xaxis_title=x_axis,
    yaxis_title=y_axis,
    showlegend=True  # Affichage des couleurs par compétition
)

# Affichage du graphique
st.plotly_chart(fig)

# Affichage des deux Top 10 séparés
st.write(f"### Top {num_labels} des meilleurs joueurs selon la variable {x_axis}")
st.dataframe(top_10_x[['Joueur', 'Équipe', 'Compétition', x_axis]])

st.write(f"### Top {num_labels} des meilleurs joueurs selon la variable {y_axis}")
st.dataframe(top_10_y[['Joueur', 'Équipe', 'Compétition', y_axis]])
