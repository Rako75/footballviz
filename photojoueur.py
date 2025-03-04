import wikipediaapi
import requests
from PIL import Image
from io import BytesIO

# Définition du User-Agent
USER_AGENT = "MonApplicationFootball/1.0 (contact@email.com)"

def get_player_image(player_name):
    wiki = wikipediaapi.Wikipedia('fr', user_agent=USER_AGENT)  # Spécification du User-Agent
    page = wiki.page(player_name)

    if not page.exists():
        print(f"La page Wikipedia de {player_name} n'existe pas.")
        return None

    # Trouver la première image correcte (jpg ou png)
    for img in page.images:
        if img.lower().endswith((".jpg", ".png")):
            return img  # Retourne l'URL de l'image trouvée

    print(f"Aucune image trouvée pour {player_name}.")
    return None

def download_and_show_image(image_url):
    response = requests.get(image_url, headers={"User-Agent": USER_AGENT})  # Ajout du User-Agent ici aussi
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
