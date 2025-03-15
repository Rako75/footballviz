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

        # Affichage de la structure de la page pour débogage
        print(f"Scraping URL : {url}")
        print(f"Code HTML de la page : {response.text[:500]}...")  # Affiche les 500 premiers caractères du HTML pour déboguer

        table = soup.find('table', {'class': 'stats_table'})  # Cherche le tableau avec la classe 'stats_table'
        if not table:
            print("Table non trouvée, vérifiez la classe ou la structure HTML de la page.")
            return [], []  # Si aucune table n'est trouvée, retour vide
        
        headers = [header.text.strip() for header in table.find_all('th')]  # Récupérer les en-têtes
        rows = table.find_all('tr')

        # Vérification de la structure des données et du nombre de colonnes
        data = []
        for row in rows:
            columns = row.find_all('td')
            if columns:
                row_data = [column.text.strip() for column in columns]
                if len(row_data) == len(headers):
                    data.append(row_data)
                else:
                    print(f"Erreur dans la ligne (colonnes non correspondant) : {row_data}")
        
        if not data:
            print("Aucune donnée extraite pour cette page.")
        
        return headers, data
    except Exception as e:
        print(f"Erreur lors du scraping de l'URL {url}: {e}")
        return [], []

# Fonction pour créer le DataFrame et nettoyer les colonnes
def create_dataframe(headers, data):
    if len(data) > 0:
        if len(headers) == len(data[0]):
            df = pd.DataFrame(data, columns=headers)
        else:
            raise ValueError("Le nombre de colonnes dans les données ne correspond pas à celui des en-têtes.")
        
        df.columns = df.columns.str.split('_').str[0]  # Supprimer le suffixe après '_'
        df = df.loc[:, ~df.columns.duplicated()]  # Supprimer les doublons de colonnes
        
        return df
    else:
        raise ValueError("Aucune donnée trouvée pour créer le DataFrame.")

# Interface Streamlit
st.title('Web Scraper pour les Statistiques des Joueurs')

# Bouton pour charger toutes les données
if st.button('Charger les données et sauvegarder dans un fichier CSV'):
    all_data = pd.DataFrame()  # Initialiser un DataFrame vide pour accumuler toutes les données

    # Itération sur les URLs et récupération des données
    for page_choice, url in urls.items():
        st.write(f"Scraping des données pour : {page_choice}")
        headers, data = scrape_data(url)
        
        if data:
            try:
                # Créer le DataFrame pour chaque page
                df = create_dataframe(headers, data)
                
                # Ajouter les données au DataFrame global
                all_data = pd.concat([all_data, df], ignore_index=True)
            except Exception as e:
                st.error(f"Erreur lors de la création du DataFrame pour {page_choice}: {e}")
        else:
            st.error(f"Aucune donnée récupérée pour {page_choice}.")
    
    # Sauvegarde des données dans un fichier CSV
    if not all_data.empty:
        all_data.to_csv('df_BIG2025.csv', index=False)
        st.success("Toutes les données ont été sauvegardées dans df_BIG2025.csv")
    else:
        st.error("Aucune donnée n'a été récupérée.")
