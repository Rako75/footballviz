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

# Top 10 des meilleurs joueurs selon la variable X
top_10_x = filtered_df.nlargest(10, x_axis)

# Top 10 des meilleurs joueurs selon la variable Y
top_10_y = filtered_df.nlargest(10, y_axis)

# Affichage des Top 10
st.write(f"### Top 10 des meilleurs joueurs selon la variable {x_axis}")
st.dataframe(top_10_x[['Joueur', 'Club', 'Compétition', x_axis]])

st.write(f"### Top 10 des meilleurs joueurs selon la variable {y_axis}")
st.dataframe(top_10_y[['Joueur', 'Club', 'Compétition', y_axis]])

# Création du graphique de classement pour X
fig_x = px.bar(top_10_x, x='Joueur', y=x_axis, title=f"Top 10 des joueurs selon {x_axis}", labels={x_axis: x_axis})
st.plotly_chart(fig_x)

# Création du graphique de classement pour Y
fig_y = px.bar(top_10_y, x='Joueur', y=y_axis, title=f"Top 10 des joueurs selon {y_axis}", labels={y_axis: y_axis})
st.plotly_chart(fig_y)
