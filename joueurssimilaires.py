import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
import difflib
import streamlit as st

# Chargement des données
@st.cache_data
def load_data():
    return pd.read_csv("df_Big5.csv")

df = load_data()

# Vérification des colonnes nécessaires
if 'Joueur' not in df.columns or 'Position' not in df.columns or 'Ligue' not in df.columns:
    raise ValueError("Les colonnes 'Joueur', 'Position' ou 'Ligue' sont absentes du fichier CSV.")

# Liste des features sélectionnées
selected_features = [
    'Matchs joues', 'Titularisations', 'Minutes jouees', 'Matches equivalents 90 minutes', 'Buts',
    'Passes decisives', 'Buts + Passes decisives', 'Buts hors penalty', 'Penalty marques', 'Penalty tentes',
    'Cartons jaunes', 'Cartons rouges', 'Buts attendus (xG)', 'Buts attendus hors penalty (npxG)',
    'Passes decisives attendues (xAG)', 'xG + xAG hors penalty', 'Passes progressives', 'Courses progressives',
    'Receptions progressives', 'Buts par 90 minutes', 'Passes decisives par 90 minutes', 'Buts + Passes decisives par 90 minutes',
    'Buts hors penalty par 90 minutes', 'Buts + Passes decisives hors penalty par 90 min', 'xG par 90 minutes', 'xAG par 90 minutes',
    'xG + xAG par 90 minutes', 'npxG par 90 minutes', 'npxG + xAG par 90 minutes', 'Actions menant a un tir',
    'Actions menant a un tir par 90 minutes', 'Passes vivantes menant a un tir', 'Passes arretees menant a un tir',
    'Ballons perdus menant a un tir', 'Tirs menant a un tir', 'Fautes subies menant a un tir', 'Actions defensives menant a un tir',
    'Actions menant a un but', 'Actions menant a un but par 90 minutes', 'Passes vivantes menant a un but',
    'Passes arretees menant a un but', 'Ballons perdus menant a un but', 'Tirs menant a un but', 'Fautes subies menant a un but',
    'Actions defensives menant a un but', 'Passes reussies totales', 'Passes tentees totales',
    'Pourcentage de reussite des passes', 'Distance totale des passes', 'Distance progressive des passes',
    'Passes courtes reussies', 'Passes courtes tentees', 'Pourcentage de reussite des passes courtes',
    'Passes moyennes reussies', 'Passes moyennes tentees', 'Pourcentage de reussite des passes moyennes',
    'Passes longues reussies', 'Passes longues tentees', 'Pourcentage de reussite des passes longues', 'Passes attendues',
    'Difference entre passes attendues et xAG', 'Passes cles', 'Passes vers le dernier tiers', 'Passes dans la surface adverse',
    'Centres dans la surface adverse', 'Deuxieme carton jaune', 'Fautes commises', 'Fautes subies', 'Hors-jeux', 'Centres',
    'Tacles reussis', 'Penalty obtenus', 'Penalty concedes', 'Buts contre son camp',
    'Ballons recuperes', 'Duels aeriens gagnes', 'Duels aeriens perdus', 'Pourcentage de duels aeriens gagnes', 'Tirs',
    'Tirs cadres', 'Pourcentage de tirs cadres', 'Tirs par 90 minutes', 'Tirs cadres par 90 minutes', 'Buts par tir',
    'Buts par tir cadre', 'Distance moyenne des tirs', 'Coups francs', 'npxG par tir', 'Difference entre buts reels et xG',
    'Difference entre buts reels hors penalty et npxG', 'Tacles', 'Tacles dans le tiers defensif', 'Tacles dans le tiers median',
    'Tacles dans le tiers offensif', 'Tacles dans les duels', 'Duels tentes', 'Pourcentage de tacles reussis Tkl%', 'Duels perdus',
    'Contres', 'Tirs contres', 'Passes contrees', 'Interceptions', 'Tacles + Interceptions', 'Degagements',
    'Erreurs ayant conduit a un tir adverse', 'Minutes par match', 'Pourcentage de minutes jouees', 'Minutes par titularisation ',
    'Matches completes', 'Remplacants', 'Minutes par entree', 'Matches non remplace', 'Points par match', 'Buts marques avec le joueur',
    'Buts encaisses avec le joueur', 'Difference de buts avec le joueur', 'Difference de buts par 90 minutes',
    'Difference avec/sans le joueur', 'xG marques avec le joueur ', 'xG encaisses avec le joueur', 'Difference de xG avec le joueur',
    'Difference de xG par 90 minutes', 'Difference de xG avec/sans le joueur', 'Touches', 'Touches dans la surface defensive',
    'Touches dans le tiers defensif', 'Touches dans le tier median', 'Touches dans le tiers offensif',
    'Touches dans la surface offensive', 'Ballons en jeu', 'Dribbles tentes', 'Dribbles reussis', 'Pourcentage de dribbles reussis',
    'Ballons perdus apres dribble', 'Pourcentage de ballons perdus apres dribble', 'Portees de balle',
    'Distance totale parcourue avec le ballon', 'Distance progressive parcourue avec le ballon',
    'Courses vers le dernier tiers', 'Courses dans la surface adverse'
]

# Vérification des colonnes sélectionnées
missing_features = [feature for feature in selected_features if feature not in df.columns]
if missing_features:
    st.warning(f"Les colonnes suivantes sont absentes : {missing_features}")
    selected_features = [feature for feature in selected_features if feature in df.columns]

# Remplacement des valeurs manquantes par la moyenne
df[selected_features] = df[selected_features].fillna(df[selected_features].mean())

# Normalisation des données
scaler = MinMaxScaler()
df[selected_features] = scaler.fit_transform(df[selected_features])

# Calcul de la similarité cosinus
similarity_matrix = cosine_similarity(df[selected_features])

# Fonction pour trouver les joueurs similaires
def find_similar_players(player_name, league, top_n=10):
    # Recherche des correspondances proches
    list_of_all_players = df['Joueur'].tolist()
    find_close_match = difflib.get_close_matches(player_name.lower(), [p.lower() for p in list_of_all_players], cutoff=0.4)
    if not find_close_match:
        st.warning(f"Aucun joueur trouvé pour '{player_name}'. Veuillez vérifier l'orthographe.")
        return []

    # Correspondance exacte (avec casse correcte)
    close_match = next(p for p in list_of_all_players if p.lower() == find_close_match[0])

    # Filtrer par position et ligue
    player_position = df[df['Joueur'] == close_match]['Position'].values[0]
    filtered_df = df[(df['Position'] == player_position) & (df['Ligue'] == league)]

    if filtered_df.empty:
        st.warning(f"Aucun joueur similaire trouvé dans la ligue '{league}' pour la position '{player_position}'.")
        return []

    # Index du joueur trouvé
    player_index = df[df['Joueur'] == close_match].index[0]

    # Calcul de la similarité pour les joueurs filtrés
    filtered_indices = filtered_df.index
    similarity_scores = [(i, similarity_matrix[player_index][i]) for i in filtered_indices]

    # Tri par score décroissant
    sorted_similar_players = sorted(similarity_scores, key=lambda x: x[1], reverse=True)

    # Récupération des joueurs similaires
    similar_players = []
    for i, (index, score) in enumerate(sorted_similar_players[:top_n]):
        similar_players.append((filtered_df.loc[index, 'Joueur'], score))

    return similar_players

# Interface utilisateur avec Streamlit
st.title("Recherche de joueurs similaires")

# Saisie utilisateur
player_name = st.text_input("Entrez le nom d'un joueur :").strip()
league = st.selectbox("Choisissez une ligue :", df['Ligue'].unique())

if player_name and league:
    similar_players = find_similar_players(player_name, league)
    if similar_players:
        st.subheader(f"Joueurs similaires à {player_name} dans la ligue {league} :")
        for i, (player, score) in enumerate(similar_players, 1):
            st.write(f"{i}. {player} (Score: {score:.2f})")
