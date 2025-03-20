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
            df = pd.read_html(url)[0]  # Lis le tableau de la première page HTML
            if df.empty:
                print(f"Pas de données trouvées pour {key}.")
            else:
                data[key] = clean_dataframe(df)
        except Exception as e:
            print(f"Erreur lors du chargement de {key}: {e}")
            data[key] = None
    return data

def process_data():
    """Fusionne les différentes tables et applique les modifications nécessaires."""
    data = get_data()

    # Vérification si des données ont été récupérées
    if not data:
        print("Aucune donnée récupérée, vérifiez les URLs.")
        return None

    df = pd.concat(data.values(), axis=1, join="inner").T.drop_duplicates().T

    rename_columns = {
        "Player": "Joueur",
        "Nation": "Nationalité",
        "Squad": "Équipe",
        "Comp": "Compétition",
        "Age": "Âge",
        "Born": "Année de naissance",
        "Playing Time MP": "Matchs joués",
        "Playing Time Starts": "Titularisations",
        "Playing Time Min": "Minutes jouées",
        "Playing Time 90s": "Matchs en 90 min",
        "Performance Gls": "Buts",
        "Performance Ast": "Passes décisives",
        "Performance G+A": "Buts + Passes D",
        "Performance G-PK": "Buts (sans penalty)",
        "Performance PK": "Pénaltys marqués",
        "Performance PKatt": "Pénaltys tentés",
        "Performance CrdY": "Cartons jaunes",
        "Performance CrdR": "Cartons rouges",
        "Expected xG": "Buts attendus (xG)",
        "Expected npxG": "Buts attendus sans penalty",
        "Expected xAG": "Passes décisives attendues (xAG)",
        "Expected npxG+xAG": "xG + xAG sans penalty",
        "Progression PrgC": "Courses progressives",
        "Progression PrgP": "Passes progressives",
        "Progression PrgR": "Réceptions progressives",
        "Per 90 Minutes Gls": "Buts par 90 minutes",
        "Per 90 Minutes Ast": "Passes décisives par 90 minutes",
        "Per 90 Minutes G+A" : "Buts + Passes décisives par 90 minutes",
        "Per 90 Minutes G-PK": "Buts hors penalty par 90 minutes",
        "Per 90 Minutes G+A-PK":"Buts + Passes décisives hors penalty par 90 minutes",
        "Per 90 Minutes xG": "Buts attendus par 90 minutes",
        "Per 90 Minutes xAG": "Passes décisives attendues par 90 minutes",
        "Per 90 Minutes xG+xAG": "Somme des buts et passes attendues par 90 minutes",
        "Per 90 Minutes npxG" : "Buts attendus hors penalty par 90 minutes",
        "Per 90 Minutes npxG+xAG" : "Somme des buts et passes attendues hors penalty par 90 minutes",
        "90s" : "Équivalents 90 minutes joués",
        "SCA SCA": "Actions menant à un tir",
        "SCA SCA90": "Actions menant à un tir par 90 minutes",
        "SCA Types PassLive": "Passes en jeu menant à un tir",
        "SCA Types PassDead": "Passes arrêtées (coups francs, corners) menant à un tir",
        "SCA Types TO": "Dribbles réussis menant à un tir",
        "SCA Types Sh": "Tirs ayant provoqué un autre tir",
        "SCA Types Fld": "Fautes subies menant à un tir",
        "SCA Types Def": "Actions défensives menant à un tir",
        "GCA GCA": "Actions menant à un but",
        "GCA GCA90": "Actions menant à un but par 90 minutes",
        "GCA Types PassLive" : "Passes en jeu menant à un but",
        "GCA Types PassDead": "Passes arrêtées (coups francs, corners) menant à un but",
        "GCA Types TO" : "Dribbles réussis menant à un but",
        "GCA Types Sh" : "Tirs ayant provoqué un but",
        "GCA Types Fld": "Fautes subies menant à un but",
        "GCA Types Def": "Actions défensives menant à un but",
        "Total Cmp": "Passes réussies",
        "Total Att": "Passes tentées",
        "Total Cmp%" : "Pourcentage de passes réussies",
        "Total TotDist" : "Distance totale des passes",
        "Total PrgDist" : "Distance progressive des passes",
        "Short Cmp" : "Passes courtes réussies",
        "Short Att" : "Passes courtes tentées",
        "Short Cmp%" : "Pourcentage de passes courtes réussies",
        "Medium Cmp" : "Passes moyennes réussies",
        "Medium Att" : "Passes moyennes tentées",
        "Medium Cmp%" : "Pourcentage de passes moyennes réussies",
        "Long Cmp" : "Passes longues réussies",
        "Long Att" : "Passes longues tentées",
        "Long Cmp%" : "Pourcentage de passes longues réussies",
        "Ast" : "Passes décisives",
        "xAG" : "Passes décisives attendues",
        "Expected xA" : "Passes attendues (xA)",
        "Expected A-xAG" : "Diff entre passes décisives réelles et attendues",
        "KP" : "Passes clés",
        "1/3" : "Passes dans le dernier tiers",
        "PPA" : "Passes dans la surface",
        "CrsPA" : "Centres dans la surface",
        "PrgP" : "Passes progressives",
        "Performance 2CrdY" : "Deuxième carton jaune",
        "Performance Fls" : "Fautes commises",
        "Performance Fld" : "Fautes subies",
        "Performance Off" : "Hors-jeux",
        "Performance Crs" : "Centres tentés",
        "Performance Int" : "Interceptions",
        "Performance TklW" : "Tacles gagnants",
        "Performance PKwon" : "Penaltys provoqués",
        "Performance PKcon" : "Penaltys concédés",
        "Performance OG" : "Buts contre son camp",
        "Performance Recov" : "Ballons récupérés",
        "Aerial Duels Won" : "Duels aériens gagnés",
        "Aerial Duels Lost" : "Duels aériens perdus",
        "Aerial Duels Won%" : "Pourcentage de duels aériens gagnés",
        "Standard Gls": "Buts",
        "Standard Sh" : "Tirs",
        "Standard SoT" : "Tirs cadrés",
        "Standard SoT%" : "Pourcentage de tirs cadrés",
        "Standard Sh/90" : "Tirs par 90 minutes",
        "Standard SoT/90" : "Tirs cadrés par 90 minutes",
        "Standard G/Sh" : "Buts par tir",
        "Standard G/SoT" : "Buts par tir cadré",
        "Standard Dist" : "Distance moyenne des tirs",
        "Standard FK" : "Coups francs tentés",
        "Standard PK" : "Penaltys marqués",
        "Standard PKatt" : "Penaltys tentés",
        "Expected npxG/Sh" : "Buts attendus hors penalty par tir",
        "Expected G-xG" : "Diff entre les buts marqués et les buts attendus",
        "Expected np:G-xG" : "Diff entre les buts marqués hors penalty et ceux attendus hors penalty",
        "Tackles Tkl" : "Tacles réussis",
        "Tackles TklW" : "Tacles gagnants",
        "Tackles Def 3rd" : "Tacles réussis dans le tiers défensif",
        "Tackles Mid 3rd" : "Tacles réussis dans le tiers médian",
        "Tackles Att 3rd" : "Tacles réussis dans le tiers offensif",
        "Challenges Tkl" : "Duels défensifs gagnés",
        "Challenges Att" : "Duels défensifs disputés",
        "Challenges Tkl%" : "Pourcentage de duels gagnés",
        "Challenges Lost" : "Duels défensifs perdus",
        "Blocks Blocks" : "Total de blocs (tirs et passes)",
        "Blocks Sh" : "Tirs bloqués",
        "Blocks Pass" : "Passes bloquées",
        "Int" : "Interceptions",
        "Tkl+Int" : "Total de tacles et d’interceptions",
        "Clr" : "Dégagements",
        "Err" : "Erreurs menant à un tir ou un but",
        "Playing Time Mn/MP" : "Minutes jouées par match",
        "Playing Time Min%" : "Pourcentage de minutes jouées",
        "Starts Starts" : "Matches débutés en tant que titulaire",
        "Starts Mn/Start" : "Minutes jouées par titularisation",
        "Starts Compl" : "Matches joués en intégralité",
        "Subs Subs" : "Nombre d’entrées en jeu",
        "Subs Mn/Sub" : "Minutes jouées par entrée en jeu",
        "Subs unSub" : "Matches passés sur le banc sans entrer en jeu",
        "Team Success PPM" : "Points par match (PPM)",
        "Team Success onG" : "Buts marqués par l’équipe lorsque le joueur est sur le terrain",
        "Team Success onGA" : "Buts encaissés par l’équipe lorsque le joueur est sur le terrain",
        "Team Success +/-" : "Diff de buts lorsque le joueur est sur le terrain",
        "Team Success +/-90" : "Différence de buts par 90 minutes",
        "Team Success On-Off" : "Impact du joueur sur la différence de buts par rapport au temps passé sur le terrain",
        "Team Success (xG) onxG" : "xG de l’équipe lorsque le joueur est sur le terrain",
        "Team Success (xG) onxGA" : "xG concédés par l’équipe lorsque le joueur est sur le terrain",
        "Team Success (xG) xG+/-" : "Différence xG lorsque le joueur est sur le terrain",
        "Team Success (xG) xG+/-90" : "Différence xG par 90 minutes",
        "Team Success (xG) On-Off" : "Impact du joueur sur la différence xG lorsqu’il est sur le terrain ou non",
        "Touches Touches": "Touches de balle",
        "Touches Def Pen" : "Touches de balle dans la surface défensive",
        "Touches Def 3rd" : "Touches de balle dans le tiers défensif",
        "Touches Mid 3rd" : "Touches de balle dans le tiers médian",
        "Touches Att 3rd" : "Touches de balle dans le tiers offensif",
        "Touches Att Pen" : "Touches de balle dans la surface offensive",
        "Touches Live" : "Touches de balle en jeu (hors coups de pied arrêtés)",
        "Take-Ons Att" : "Dribbles tentés",
        "Take-Ons Succ" : "Dribbles réussis",
        "Take-Ons Succ%" : "Pourcentage de dribbles réussis",
        "Take-Ons Tkld" : "Dribbles stoppés par l’adversaire",
        "Take-Ons Tkld%" : "Pourcentage de dribbles stoppés",
        "Carries Carries" : "Portées de balle",
        "Carries TotDist" : "Distance totale parcourue avec le ballon (en mètres)",
        "Carries PrgDist" : "Distance progressive parcourue avec le ballon",
        "Carries PrgC" : "Portées de balle progressives",
        "Carries 1/3" : "Portées de balle jusqu’au dernier tiers du terrain",
        "Carries CPA" : "Portées de balle entrant dans la surface adverse",
        "Carries Mis" : "Ballons perdus en conduite",
        "Carries Dis" : "Ballons perdus sous la pression d’un adversaire",
        "Receiving Rec" : "Passes reçues",
        "Receiving PrgR" : "Passes progressives reçues"

    }

    df = df.rename(columns=rename_columns)

    print(df.info())

    df.to_csv('df_2025.csv', sep='\t', encoding='utf-8', index=False)
    print("Données enregistrées sous 'df_2025.csv'.")
    return df  # Retourne les données

if __name__ == "__main__":
    process_data()
