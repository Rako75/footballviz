import wikipediaapi
import requests
from PIL import Image
from io import BytesIO

# Définition du User-Agent spécifique
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"

def get_player_image(player_name):
    """Récupère l'URL de l'image principale du joueur depuis Wikipedia"""
    wiki = wikipediaapi.Wikipedia(user_agent=USER_AGENT, language='fr')  # Définit l'User-Agent ici
    page = wiki.page(player_name)

    if not page.exists():
        print(f"La page Wikipedia de {player_name} n'existe pas.")
        return None

    # Trouver la première image en .jpg ou .png
    for img in page.images:
        if img.lower().endswith((".jpg", ".png")):
            return img  # Retourne l'URL de l'image trouvée

    print(f"Aucune image trouvée pour {player_name}.")
    return None

def download_and_show_image(image_url):
    """Télécharge et affiche l'image du joueur"""
    headers = {"User-Agent": USER_AGENT}  # Ajout du User-Agent dans la requête
    response = requests.get(image_url, headers=headers)
    
    if response.status_code == 200:
        img = Image.open(BytesIO(response.content))
        img.show()  # Ouvre l'image
    else:
        print("Erreur lors du téléchargement de l'image.")

# Exemple avec Cole Palmer
player_name = "Cole Palmer"
image_url = get_player_image(player_name)

if image_url:
    print(f"Image trouvée : {image_url}")
    download_and_show_image(image_url)
