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
        
        table = soup.find('table', {'class': 'stats_table'})  # Le tableau des statistiques
        headers = [header.text.strip() for header in table.find_all('th')]  # Récupérer les titres des colonnes
        rows = table.find_all('tr')
        
        # Récupérer les données des lignes
        data = []
        for row in rows:
            columns = row.find_all('td')
            if columns:
                row_data = [column.text.strip() for column in columns]
                if len(row_data) == len(headers):
                    data.append(row_data)
                else:
                    print(f"Erreur dans la ligne, nombre de colonnes non correspondant : {row_data}")
        
        return headers, data
    except Exception as e:
        return str(e), []

# Fonction pour convertir les données en DataFrame Pandas
def create_dataframe(headers, data):
    if len(data) > 0:
        # Vérification de la correspondance des colonnes
        if len(headers) == len(data[0]):
            df = pd.DataFrame(data, columns=headers)
        else:
            raise ValueError("Le nombre de colonnes dans les données ne correspond pas à celui des en-têtes.")
        
        # Nettoyer les noms des colonnes en supprimant les suffixes après '_'
        df.columns = df.columns.str.split('_').str[0]  # Supprimer le suffixe après '_'
        
        # Supprimer les doublons de colonnes
        df = df.loc[:, ~df.columns.duplicated()]  # Supprimer les doublons de colonnes
        
        return df
    else:
        raise ValueError("Aucune donnée trouvée pour créer le DataFrame.")
