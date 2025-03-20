import pandas as pd

URLS = {
    "stats": "https://fbref.com/en/comps/Big5/stats/players/Big-5-European-Leagues-Stats",
    "shooting": "https://fbref.com/en/comps/Big5/shooting/players/Big-5-European-Leagues-Stats",
    "passing": "https://fbref.com/en/comps/Big5/passing/players/Big-5-European-Leagues-Stats",
    "defense": "https://fbref.com/en/comps/Big5/defense/players/Big-5-European-Leagues-Stats",
    "gca": "https://fbref.com/en/comps/Big5/gca/players/Big-5-European-Leagues-Stats",
    "misc": "https://fbref.com/en/comps/Big5/misc/players/Big-5-European-Leagues-Stats",
    "possession": "https://fbref.com/en/comps/Big5/possession/players/Big-5-European-Leagues-Stats",
    "playing_time": "https://fbref.com/en/comps/Big5/playingtime/players/Big-5-European-Leagues-Stats",
}

def clean_dataframe(df):
    """Nettoie un DataFrame en supprimant les multi-index et en standardisant les colonnes."""
    df.columns = [' '.join(col).strip() for col in df.columns]
    df = df.reset_index(drop=True)
    
    new_columns = [col.split()[-1] if 'level_0' in col else col for col in df.columns]
    df.columns = new_columns

    if 'Age' in df.columns:
        df['Age'] = df['Age'].astype(str).str[:2]
    
    if 'Pos' in df.columns:
        df['Pos'] = df['Pos'].astype(str).str[:2]

    if 'Nation' in df.columns:
        df['Nation'] = df['Nation'].str.split(' ').str.get(1)

    if 'Comp' in df.columns:
        df['Comp'] = df['Comp'].str.replace("eng|es|it|fr|de", "", regex=True).str.strip()
    
    df = df.drop(columns=['Rk', 'Matches'], errors='ignore')
    df = df.dropna().reset_index(drop=True)
    
    return df

def get_data():
    """Récupère et nettoie les données depuis les URLs définies."""
    data = {}
    for key, url in URLS.items():
        try:
            df = pd.read_html(url)[0]
            data[key] = clean_dataframe(df)
        except Exception as e:
            print(f"Erreur lors du chargement de {key}: {e}")
            data[key] = None
    return data
