import streamlit as st
import wikipedia
import requests
from PIL import Image
from io import BytesIO

def get_wikipedia_image(player_name):
    try:
        # Recherche de la page Wikipedia du joueur
        page = wikipedia.page(player_name)
        # Prend la première image trouvée sur la page
        image_url = page.images[0]  
        
        # Télécharge l'image
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
        return img
    except Exception as e:
        st.error(f"Erreur lors de la récupération de l'image : {e}")
        return None

st.title("Récupération de l'image d'un joueur")

# Sélection du joueur
player_name = st.text_input("Entrez le nom du joueur :", "Cole Palmer")

if st.button("Rechercher l'image"):
    player_img = get_wikipedia_image(player_name)
    if player_img:
        st.image(player_img, caption=player_name, width=250)
    else:
        st.error("Image non trouvée.")
