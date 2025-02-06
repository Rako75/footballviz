import streamlit as st
import pandas as pd
import time

# Charger les données
file_path = "Meilleurs buteurs du PSG.xlsx"
df = pd.read_excel(file_path, sheet_name="Feuil1")

df = df.sort_values("Saison")
df["Noms"] = df["Noms"].astype(str)

def get_image_url(nom):
    formatted_name = nom.replace(" ", "%20")
    return f"https://github.com/Rako75/footballviz/blob/main/PSG%20Buteurs/{formatted_name}.jpg?raw=true"

def animate_names():
    placeholder = st.empty()
    for i in range(len(df)):
        saison = df.iloc[i]["Saison"]
        nom = df.iloc[i]["Noms"]
        buts = df.iloc[i]["Buts"]
        image_url = get_image_url(nom)
        with placeholder.container():
            st.markdown(f"## {saison} : {nom} ({buts} buts)")
            st.image(image_url, caption=nom, use_container_width=True)
        time.sleep(5)

st.title("🏆 Meilleurs Buteurs du PSG par Saison")
if st.button("Lancer l'animation"):
    animate_names()
