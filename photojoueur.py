import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO

def get_sofascore_player_image(player_name):
    """Récupère l'URL de l'image du joueur depuis SofaScore"""
    search_url = f"https://www.sofascore.com/search/{player_name.replace(' ', '%20')}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    }
    
    search_response = requests.get(search_url, headers=headers)
    if search_response.status_code != 200:
        print("Erreur lors de la récupération des résultats de recherche.")
        return None
    
    soup = BeautifulSoup(search_response.text, "html.parser")
    player_links = soup.find_all("a", href=True)

    for link in player_links:
        if "/player/" in link["href"]:
            player_page_url = "https://www.sofascore.com" + link["href"]
            break
    else:
        print(f"Aucun joueur trouvé pour {player_name}.")
        return None

    # Accéder à la page du joueur
    player_response = requests.get(player_page_url, headers=headers)
    if player_response.status_code != 200:
        print("Erreur lors de la récupération de la page du joueur.")
        return None
    
    player_soup = BeautifulSoup(player_response.text, "html.parser")
    img_tag = player_soup.find("img", {"class": "sc-1gdsjwe-1"})

    if img_tag and "src" in img_tag.attrs:
        return img_tag["src"]

    print("Aucune image trouvée.")
    return None

def download_and_show_image(image_url):
    """Télécharge et affiche l'image du joueur"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    }
    
    response = requests.get(image_url, headers=headers)
    
    if response.status_code == 200:
        img = Image.open(BytesIO(response.content))
        img.show()
    else:
        print("Erreur lors du téléchargement de l'image.")

# Exemple avec Cole Palmer
player_name = "Cole Palmer"
image_url = get_sofascore_player_image(player_name)

if image_url:
    print(f"Image trouvée : {image_url}")
    download_and_show_image(image_url)
