import streamlit as st
import pandas as pd
import plotly.express as px

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

# Création du scatterplot
fig = px.scatter(filtered_df, x=x_axis, y=y_axis, text="Joueur", hover_data=["Équipe", "Compétition"], color="Compétition")

# Affichage des labels
fig.update_traces(textposition='top center', textfont_size=label_size)
fig.update_layout(title=f"Comparaison des joueurs ({x_axis} vs {y_axis})")

# Affichage du scatterplot
st.plotly_chart(fig)

# Affichage du classement top 5
filtered_df[y_axis] = pd.to_numeric(filtered_df[y_axis], errors='coerce')
top_5 = filtered_df[["Joueur", "Équipe", "Compétition", x_axis, y_axis]].nlargest(5, y_axis)
st.write("### Top 5 joueurs selon la variable choisie")
st.dataframe(top_5)
