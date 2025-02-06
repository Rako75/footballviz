import streamlit as st
import pandas as pd
import time

# Charger les données
file_path = "Meilleurs buteurs du PSG.xlsx"
df = pd.read_excel(file_path, sheet_name="Feuil1")

df = df.sort_values("Saison")
df["Noms"] = df["Noms"].astype(str)

def animate_names():
    placeholder = st.empty()
    for i in range(len(df)):
        saison = df.iloc[i]["Saison"]
        nom = df.iloc[i]["Noms"]
        buts = df.iloc[i]["Buts"]
        placeholder.markdown(f"## {saison} : {nom} ({buts} buts)")
        time.sleep(1)

st.title("🏆 Meilleurs Buteurs du PSG par Saison")
if st.button("Lancer l'animation"):
    animate_names()
