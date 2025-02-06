import streamlit as st
import pandas as pd
import plotly.express as px
import time

# Charger les données
file_path = "Meilleurs buteurs du PSG.xlsx"
df = pd.read_excel(file_path, sheet_name="Feuil1")

df = df.sort_values("Saison")
df["Noms"] = df["Noms"].astype(str)

def animate_chart():
    for i in range(1, len(df) + 1):
        temp_df = df.iloc[:i]
        fig = px.bar(temp_df, x="Saison", y="Buts", text="Noms", 
                     title="Meilleurs buteurs du PSG par saison",
                     animation_frame="Saison", range_y=[0, df["Buts"].max() + 5])
        st.plotly_chart(fig)
        time.sleep(0.5)

st.title("🏆 Racing Bar Chart : Meilleurs Buteurs du PSG")
if st.button("Lancer l'animation"):
    animate_chart()
