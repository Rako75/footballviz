import streamlit as st
import pandas as pd
import plotly.express as px
import time

# Charger les données
file_path = "Meilleurs buteurs du PSG (1).xlsx"
df = pd.read_excel(file_path, sheet_name="Feuil1")

df = df.sort_values("Saison")

def animate_chart():
    fig = None
    for i in range(1, len(df) + 1):
        temp_df = df.iloc[:i]
        fig = px.bar(temp_df, x="Buts", y="Noms", orientation="h", 
                     text="Buts", title="Meilleurs buteurs du PSG par saison",
                     animation_frame="Saison", range_x=[0, df["Buts"].max() + 5])
        st.plotly_chart(fig)
        time.sleep(0.5)

st.title("🏆 Racing Bar Chart : Meilleurs Buteurs du PSG")
if st.button("Lancer l'animation"):
    animate_chart()
