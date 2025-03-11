import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

df = pd.read_csv("df_BIG2025.csv")  # Remplacez par votre fichier

st.title("Football Statistics Dashboard")


selected_league = st.selectbox("Selectionnez une ligue:", df['Compétition'].unique())
filtered_df = df[df['Compétition'] == selected_league]


# Visualization 1: Bar graph showing highest goal scorers (top 20)
top_scorers = filtered_df.nlargest(20, 'Buts')
fig1 = px.bar(top_scorers, x='Joueur', y='Buts', title='Top 20 meilleurs buteurs', labels={'Buts': 'Nombre de buts'})
fig1.update_traces(hovertemplate='Joueur: %{x}<br>Buts: %{y}')
st.plotly_chart(fig1)
