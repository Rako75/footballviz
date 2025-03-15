import requests
from bs4 import BeautifulSoup
import streamlit as st

# Liste des URLs
urls = {
    "stats": 'https://fbref.com/en/comps/Big5/stats/players/Big-5-European-Leagues-Stats',
    "shooting": 'https://fbref.com/en/comps/Big5/shooting/players/Big-5-European-Leagues-Stats',
    "passing": 'https://fbref.com/en/comps/Big5/passing/players/Big-5-European-Leagues-Stats',
    "defense": 'https://fbref.com/en/comps/Big5/defense/players/Big-5-European-Leagues-Stats',
    "gca": 'https://fbref.com/en/comps/Big5/gca/players/Big-5-European-Leagues-Stats',
    "misc": 'https://fbref.com/en/comps/Big5/misc/players/Big-5-European-Leagues-Stats',
    "possession": 'https://fbref.com/en/comps/Big5/possession/players/Big-5-European-Leagues-Stats',
    "playtime": 'https://fbref.com/en/comps/Big5/playingtime/players/Big-5-European-Leagues-Stats'
}

# Fonction pour scraper les données d'une page
def scrape_data(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Exemple de récupération d'un tableau avec des stats
        table = soup.find('table', {'class': 'stats_table'})  # Le tableau des statistiques
        headers = [header.text for header in table.find_all('th')]  # Récupérer les titres des colonnes
        rows = table.find_all('tr')
        
        # Récupérer les données des lignes
        data = []
        for row in rows:
            columns = row.find_all('td')
            if columns:
                data.append([column.text for column in columns])
        
        return headers, data
    except Exception as e:
        return str(e), []

# Interface Streamlit
st.title('Web Scraper pour les Statistiques des Joueurs')

# Sélection de la page à scraper
page_choice = st.selectbox("Choisissez une catégorie de statistiques", list(urls.keys()))

# Afficher les résultats
if st.button('Scraper les données'):
    url = urls[page_choice]
    headers, data = scrape_data(url)
    
    if data:
        st.write(f"### Statistiques pour {page_choice}")
        st.write("**Colonnes**: ", headers)
        st.write("**Données**: ", data[:10])  # Affiche les 10 premières lignes pour la démonstration
    else:
        st.error(f"Erreur lors du scraping des données de {page_choice}")
