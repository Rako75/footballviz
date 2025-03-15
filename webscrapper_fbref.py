import requests
from bs4 import BeautifulSoup
import pandas as pd
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
        headers = [header.text.strip() for header in table.find_all('th')]  # Récupérer les titres des colonnes
        rows = table.find_all('tr')
        
        # Récupérer les données des lignes
        data = []
        for row in rows:
            columns = row.find_all('td')
            if columns:
                data.append([column.text.strip() for column in columns])
        
        return headers, data
    except Exception as e:
        return str(e), []

# Fonction pour convertir les données en DataFrame Pandas
def create_dataframe(headers, data):
    df = pd.DataFrame(data, columns=headers)
    
    # Nettoyer les noms des colonnes en supprimant les suffixes après '_'
    df.columns = df.columns.str.split('_').str[0]  # Supprimer le suffixe après '_'
    
    # Supprimer les doublons de colonnes
    df = df.loc[:, ~df.columns.duplicated()]  # Supprimer les doublons de colonnes
    
    return df

# Interface Streamlit
st.title('Web Scraper pour les Statistiques des Joueurs')

# Bouton pour scraper toutes les données
if st.button('Charger les données et sauvegarder dans un fichier CSV'):
    all_data = pd.DataFrame()  # Initialiser un DataFrame vide pour accumuler toutes les données

    for page_choice, url in urls.items():
        st.write(f"Scraping des données pour : {page_choice}")
        headers, data = scrape_data(url)
        
        if data:
            # Créer le DataFrame à partir des données récupérées
            df = create_dataframe(headers, data)
            
            # Ajouter les données au DataFrame global
            all_data = pd.concat([all_data, df], ignore_index=True)
        else:
            st.error(f"Erreur lors du scraping des données de {page_choice}")
    
    # Sauvegarder dans un fichier CSV
    if not all_data.empty:
        all_data.to_csv('df_BIG2025.csv', index=False)
        st.success("Toutes les données ont été sauvegardées dans df_BIG2025.csv")
    else:
        st.error("Aucune donnée n'a été récupérée.")
