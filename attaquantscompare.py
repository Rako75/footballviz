import streamlit as st
import pandas as pd
import plotly.express as px

# Chargement des données
@st.cache_data
def load_data():
    df = pd.read_csv("df_BIG2025.csv")  # Remplacez par votre fichier
    return df

df = load_data()

# Interface utilisateur Streamlit
st.title("Analyse des Attaquants en Football")

# Sélection d'un attaquant
attaquants = df[df["Position"] == "Attaquant Central"]["Joueur"].unique()
joueur_selectionne = st.selectbox("Sélectionnez un attaquant", attaquants)

# Afficher ses stats principales
joueur_stats = df[df["Joueur"] == joueur_selectionne].iloc[0]

st.write(f"### Statistiques de {joueur_selectionne}")
st.metric(label="Buts", value=joueur_stats["Buts"])
st.metric(label="Passes décisives", value=joueur_stats["Passes décisives"])
st.metric(label="xG", value=joueur_stats["Buts attendus (xG)"])

# Comparaison avec d'autres attaquants
fig = px.box(df[df["Position"] == "Attaquant Central"], x="Position", y="Buts", title="Répartition des buts des attaquants")
st.plotly_chart(fig)

# Ajout d'une comparaison en radar chart
import plotly.graph_objects as go

stats_comparaison = ["Buts", "Passes décisives", "Buts attendus (xG)", "Passes progressives", "Tirs"]
moyennes_attaquants = df[df["Position"] == "Attaquant Central"][stats_comparaison].mean()

fig_radar = go.Figure()
fig_radar.add_trace(go.Scatterpolar(
    r=joueur_stats[stats_comparaison].values,
    theta=stats_comparaison,
    fill='toself',
    name=f"{joueur_selectionne}"
))
fig_radar.add_trace(go.Scatterpolar(
    r=moyennes_attaquants.values,
    theta=stats_comparaison,
    fill='toself',
    name="Moyenne des attaquants"
))
fig_radar.update_layout(title="Comparaison avec la moyenne des attaquants")
st.plotly_chart(fig_radar)
