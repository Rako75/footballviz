import streamlit as st
import pandas as pd
import plotly.express as px

# Charger les données
file_path = "Meilleurs buteurs du PSG.xlsx"
df = pd.read_excel(file_path, sheet_name="Feuil1")

df = df.sort_values("Saison")
df["Noms"] = df["Noms"].astype(str)

def generate_chart():
    fig = px.bar(df, x="Buts", y="Saison", orientation="h", 
                 text="Noms", title="Meilleurs buteurs du PSG par saison",
                 animation_frame="Saison", range_x=[0, df["Buts"].max() + 5])
    st.plotly_chart(fig)

st.title("🏆 Racing Bar Chart : Meilleurs Buteurs du PSG")
if st.button("Afficher le graphique"):
    generate_chart()
