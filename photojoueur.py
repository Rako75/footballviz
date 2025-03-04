import wikipediaapi
import requests
from PIL import Image
from io import BytesIO

def get_player_image(player_name):
    wiki = wikipediaapi.Wikipedia('fr')  # 'fr' pour la version française
    page = wiki.page(player_name)

    if not page.exists():
        print(f"La page Wikipedia de {player_name} n'existe pas.")
        return None

    # Trouver l'URL de la première image
    for img in page.images:
        if img.endswith(".jpg") or img.endswith(".png"):
            return img  # Retourne la première image trouvée

    print(f"Aucune image trouvée pour {player_name}.")
    return None

def download_and_show_image(image_url):
    response = requests.get(image_url)
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
