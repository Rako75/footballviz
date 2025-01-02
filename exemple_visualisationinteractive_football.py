import pandas as pd
import numpy as np
import streamlit as st
from soccerplots.radar_chart import Radar

# Fonction pour charger et prétraiter les données
def load_and_preprocess_data(file_path, position):
    data = pd.read_csv(file_path)
    data = data[data['Matchs joues'].astype(int) > 10]
    
    # Normalisation des colonnes en fonction de la position
    if position == "Attaquant":
        stats_cols = ['Buts par 90 minutes', 'Passes decisives par 90 minutes',
                      'Buts + Passes decisives par 90 minutes', 'Distance progressive',
                      'Passes progressives', 'Receptions progressives', 'xG par 90 minutes', 'xAG par 90 minutes']
    elif position == "Défenseur":
        stats_cols = ['Interceptions', 'Tacles', 'Degagements',
                      'Duels aeriens gagnes', 'Passes progressives', 'Contres']
    elif position == "Milieu":
        stats_cols = ['Passes cles', 'Actions menant a un tir par 90 minutes', 
                      'xG + xAG par 90 minutes', 'Passes vers le dernier tiers',
                      'Passes progressives', 'Courses progressives']
    else:
        raise ValueError("Position non reconnue")
    
    data = data.rename(columns={'Distance progressive parcourue avec le ballon': 'Distance progressive'})
    for col in stats_cols:
        if col in data.columns:
            data[col] = data[col].astype(float) / data['Matches equivalents 90 minutes']

    for col in stats_cols:
        if col in data.columns:
            data[col] = (data[col].rank(pct=True) * 100).astype(int)

    return data, stats_cols

# Dictionnaire des fichiers par ligue et position
league_files = {
    "Premier League": {
        "Attaquant": "Premier_League_Attaquant.csv",
        "Défenseur": "Premier_League_Défenseur.csv",
        "Milieu": "Premier_League_Milieu.csv",
    },
    "Bundesliga": {
        "Attaquant": "Bundesliga_Attaquant.csv",
        "Défenseur": "Bundesliga_Défenseur.csv",
        "Milieu": "Bundesliga_Milieu.csv",
    },
    "La Liga": {
        "Attaquant": "La_Liga_Attaquant.csv",
        "Défenseur": "La_Liga_Défenseur.csv",
        "Milieu": "La_Liga_Milieu.csv",
    },
    "Ligue 1": {
        "Attaquant": "Ligue_1_Attaquant.csv",
        "Défenseur": "Ligue_1_Défenseur.csv",
        "Milieu": "Ligue_1_Milieu.csv",
    },
    "Serie A": {
        "Attaquant": "Serie_A_Attaquant.csv",
        "Défenseur": "Serie_A_Défenseur.csv",
        "Milieu": "Serie_A_Milieu.csv",
    },
}

# Dictionnaire des logos des clubs avec les liens directs GitHub
club_logos = {
    # Serie A
    'Roma': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Serie%20A%20Logos/Roma.png',
    'Inter': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Serie%20A%20Logos/Inter.png',
    'Milan': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Serie%20A%20Logos/Milan.png',
    'Bologna': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Serie%20A%20Logos/Bologna.png',
    'Udinese': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Serie%20A%20Logos/Udinese.png',
    'Monza': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Serie%20A%20Logos/Monza.png',
    'Genoa': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Serie%20A%20Logos/Genoa.png',
    'Lazio': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Serie%20A%20Logos/Lazio.png',
    'Juventus': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Serie%20A%20Logos/Juventus.png',
    'Lecce': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Serie%20A%20Logos/Lecce.png',
    'Fiorentina': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Serie%20A%20Logos/Fiorentina.png',
    'Hellas Verona': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Serie%20A%20Logos/Hellas Verona.png',
    'Cagliari': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Serie%20A%20Logos/Cagliari.png',
    'Frosinone': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Serie%20A%20Logos/Frosinone.png',
    'Sassuolo': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Serie%20A%20Logos/Sassuolo.png',
    'Atalanta': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Serie%20A%20Logos/Atalanta.png',
    'Empoli': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Serie%20A%20Logos/Empoli.png',
    'Salernitana': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Serie%20A%20Logos/Salernitana.png',
    'Torino': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Serie%20A%20Logos/Torino.png',
    'Napoli': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Serie%20A%20Logos/Napoli.png',
    
    # Premier League
    'Bournemouth': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Premier%20League%20Logos/Bournemouth.png',
    'Chelsea': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Premier%20League%20Logos/Chelsea.png',
    'Fulham': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Premier%20League%20Logos/Fulham.png',
    'Luton Town': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Premier%20League%20Logos/Luton Town.png',
    'Brighton': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Premier%20League%20Logos/Brighton.png',
    'West Ham': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Premier%20League%20Logos/West Ham.png',
    'Nott\'ham Forest': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Premier%20League%20Logos/Nott\'ham Forest.png',
    'Crystal Palace': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Premier%20League%20Logos/Crystal Palace.png',
    'Sheffield Utd': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Premier%20League%20Logos/Sheffield Utd.png',
    'Wolves': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Premier%20League%20Logos/Wolves.png',
    'Brentford': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Premier%20League%20Logos/Brentford.png',
    'Manchester City': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Premier%20League%20Logos/Manchester City.png',
    'Liverpool': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Premier%20League%20Logos/Liverpool.png',
    'Newcastle Utd': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Premier%20League%20Logos/Newcastle Utd.png',
    'Burnley': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Premier%20League%20Logos/Burnley.png',
    'Manchester Utd': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Premier%20League%20Logos/Manchester Utd.png',
    'Aston Villa': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Premier%20League%20Logos/Aston Villa.png',
    'Tottenham': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Premier%20League%20Logos/Tottenham.png',
    'Everton': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Premier%20League%20Logos/Everton.png',
    'Arsenal': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Premier%20League%20Logos/Arsenal.png',
    
    # La Liga
    'Getafe': 'https://raw.githubusercontent.com/Rako75/footballviz/main/La%20Liga%20Logos/Getafe.png',
    'Betis': 'https://raw.githubusercontent.com/Rako75/footballviz/main/La%20Liga%20Logos/Betis.png',
    'Alavés': 'https://raw.githubusercontent.com/Rako75/footballviz/main/La%20Liga%20Logos/Alavés.png',
    'Sevilla': 'https://raw.githubusercontent.com/Rako75/footballviz/main/La%20Liga%20Logos/Sevilla.png',
    'Athletic Club': 'https://raw.githubusercontent.com/Rako75/footballviz/main/La%20Liga%20Logos/Athletic Club.png',
    'Celta Vigo': 'https://raw.githubusercontent.com/Rako75/footballviz/main/La%20Liga%20Logos/Celta Vigo.png',
    'Villarreal': 'https://raw.githubusercontent.com/Rako75/footballviz/main/La%20Liga%20Logos/Villarreal.png',
    'Almería': 'https://raw.githubusercontent.com/Rako75/footballviz/main/La%20Liga%20Logos/Almería.png',
    'Real Madrid': 'https://raw.githubusercontent.com/Rako75/footballviz/main/La%20Liga%20Logos/Real Madrid.png',
    'Cádiz': 'https://raw.githubusercontent.com/Rako75/footballviz/main/La%20Liga%20Logos/Cádiz.png',
    'Real Sociedad': 'https://raw.githubusercontent.com/Rako75/footballviz/main/La%20Liga%20Logos/Real Sociedad.png',
    'Valencia': 'https://raw.githubusercontent.com/Rako75/footballviz/main/La%20Liga%20Logos/Valencia.png',
    'Barcelona': 'https://raw.githubusercontent.com/Rako75/footballviz/main/La%20Liga%20Logos/Barcelona.png',
    'Mallorca': 'https://raw.githubusercontent.com/Rako75/footballviz/main/La%20Liga%20Logos/Mallorca.png',
    'Granada': 'https://raw.githubusercontent.com/Rako75/footballviz/main/La%20Liga%20Logos/Granada.png',
    'Las Palmas': 'https://raw.githubusercontent.com/Rako75/footballviz/main/La%20Liga%20Logos/Las Palmas.png',
    'Osasuna': 'https://raw.githubusercontent.com/Rako75/footballviz/main/La%20Liga%20Logos/Osasuna.png',
    'Atlético Madrid': 'https://raw.githubusercontent.com/Rako75/footballviz/main/La%20Liga%20Logos/Atlético Madrid.png',
    'Rayo Vallecano': 'https://raw.githubusercontent.com/Rako75/footballviz/main/La%20Liga%20Logos/Rayo Vallecano.png',
    'Girona': 'https://raw.githubusercontent.com/Rako75/footballviz/main/La%20Liga%20Logos/Girona.png',
    
    # Ligue 1
    'Marseille': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Ligue%201%20Logos/Marseille.png',
    'Reims': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Ligue%201%20Logos/Reims.png',
    'Lens': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Ligue%201%20Logos/Lens.png',
    'Lorient': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Ligue%201%20Logos/Lorient.png',
    'Nantes': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Ligue%201%20Logos/Nantes.png',
    'Toulouse': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Ligue%201%20Logos/Toulouse.png',
    'Montpellier': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Ligue%201%20Logos/Montpellier.png',
    'Lyon': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Ligue%201%20Logos/Lyon.png',
    'Monaco': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Ligue%201%20Logos/Monaco.png',
    'Strasbourg': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Ligue%201%20Logos/Strasbourg.png',
    'Nice': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Ligue%201%20Logos/Nice.png',
    'Le Havre': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Ligue%201%20Logos/Le Havre.png',
    'Clermont Foot': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Ligue%201%20Logos/Clermont Foot.png',
    'Metz': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Ligue%201%20Logos/Metz.png',
    'Brest': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Ligue%201%20Logos/Brest.png',
    'Lille': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Ligue%201%20Logos/Lille.png',
    'Paris S-G': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Ligue%201%20Logos/Paris S-G.png',
    'Rennes': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Ligue%201%20Logos/Rennes.png',
    
    # Bundesliga
    'Union Berlin': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Bundesliga%20Logos/Union Berlin.png',
    'Eint Frankfurt': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Bundesliga%20Logos/Eintracht Frankfurt.png',
    'Freiburg': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Bundesliga%20Logos/Freiburg.png',
    'Köln': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Bundesliga%20Logos/Köln.png',
    'Dortmund': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Bundesliga%20Logos/Dortmund.png',
    'Leverkusen': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Bundesliga%20Logos/Leverkusen.png',
    'Werder Bremen': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Bundesliga%20Logos/Werder Bremen.png',
    'Mainz 05': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Bundesliga%20Logos/Mainz 05.png',
    'Hoffenheim': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Bundesliga%20Logos/Hoffenheim.png',
    'Wolfsburg': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Bundesliga%20Logos/Wolfsburg.png',
    'Stuttgart': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Bundesliga%20Logos/Stuttgart.png',
    'Bochum': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Bundesliga%20Logos/Bochum.png',
    'Darmstadt 98': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Bundesliga%20Logos/Darmstadt 98.png',
    'Bayern Munich': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Bundesliga%20Logos/Bayern Munich.png',
    'Augsburg': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Bundesliga%20Logos/Augsburg.png',
    'RB Leipzig': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Bundesliga%20Logos/RB Leipzig.png',
    'Heidenheim': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Bundesliga%20Logos/Heidenheim.png',
    'Gladbach': 'https://raw.githubusercontent.com/Rako75/footballviz/main/Bundesliga%20Logos/Gladbach.png',
}
# Interface Streamlit pour afficher les résultats
def show_radar_chart(position, league):
    # Sélectionner le fichier de données correspondant à la ligue et à la position
    file_path = league_files[league][position]
    data, stats_cols = load_and_preprocess_data(file_path, position)
    
    # Sélectionner le joueur avec les meilleures statistiques
    best_player = data.loc[data[stats_cols[0]].idxmax()]
    
    # Identifier l'équipe du joueur
    team_name = best_player['Equipe']
    
    # Charger le logo de l'équipe
    logo_url = club_logos.get(team_name, None)
    
    # Créer et afficher le radar
    radar = Radar(stats=stats_cols, stats_order=stats_cols)
    fig = radar.plot(best_player[stats_cols], color='blue', label=best_player['Player'])
    
    # Afficher le logo à côté du joueur
    if logo_url:
        st.image(logo_url, width=50, caption=f"Logo de {team_name}")
    
    st.pyplot(fig)

# Paramètres Streamlit pour l'interface
st.title("Football Radar")
position = st.selectbox("Sélectionnez la position", ["Attaquant", "Milieu", "Défenseur"])
league = st.selectbox("Sélectionnez la ligue", ["Premier League", "Bundesliga", "La Liga", "Ligue 1", "Serie A"])

show_radar_chart(position, league)
