import pandas as pd
import numpy as np
import mplsoccer
import matplotlib.pyplot as plt
from mplsoccer import Radar
import matplotlib.font_manager as font_manager

# Importer la police (facultatif, à ajuster si nécessaire)
font_path = 'Arvo-Regular.ttf'  # Remplacez par le chemin correct vers la police
font_props = font_manager.FontProperties(fname=font_path)

# Chargement des données
data = pd.read_csv('Premier_League_Attaquant.csv')

# Filtrer les joueurs ayant joué au moins 10 matchs
data = data[data['Matchs joues'].astype(int) > 10]

# Renommer certaines colonnes pour simplifier l'accès
data = data.rename(columns={'Distance progressive parcourue avec le ballon': 'Distance progressive'})

# Conversion des colonnes en entiers
data[['Buts', 'Passes decisives', 'Buts + Passes decisives', 'Distance progressive', 'Passes progressives', 'Receptions progressives']] = data[['Buts', 'Passes decisives', 'Buts + Passes decisives', 'Distance progressive', 'Passes progressives', 'Receptions progressives']].astype(int)

# Calcul du percentile pour chaque statistique
data['Distance progressive'] = data['Distance progressive'] / data['Matches equivalents 90 minutes']
data['Passes progressives'] = data['Passes progressives'] / data['Matches equivalents 90 minutes']
data['Receptions progressives'] = data['Receptions progressives'] / data['Matches equivalents 90 minutes']

# Calcul des percentiles pour les autres colonnes
percentiles = [
    'Buts par 90 minutes', 'Passes decisives par 90 minutes', 'Buts + Passes decisives par 90 minutes', 
    'Distance progressive', 'Passes progressives', 'Receptions progressives', 'xG par 90 minutes', 'xAG par 90 minutes'
]
for col in percentiles:
    data[col] = (data[col].rank(pct=True) * 100).astype(int)

# Fonction pour sélectionner les joueurs à comparer
def select_players(player1, player2):
    # Vérifier si les joueurs existent dans les données
    if player1 not in data['Joueur'].values or player2 not in data['Joueur'].values:
        raise ValueError("L'un des joueurs n'existe pas dans les données.")
    
    player1_data = data[data['Joueur'] == player1]
    player2_data = data[data['Joueur'] == player2]
    
    return player1_data, player2_data

# Exemple : Demander à l'utilisateur de saisir les noms des joueurs
player1_name = input("Entrez le nom du premier joueur: ")
player2_name = input("Entrez le nom du deuxième joueur: ")

try:
    # Sélectionner les joueurs à comparer
    player1, player2 = select_players(player1_name, player2_name)

    # Choisir les colonnes à utiliser pour le radar
    columns_to_plot = [
        'Buts', 'Passes decisives', 'Buts + Passes decisives',
        'Distance progressive', 'Passes progressives', 'Receptions progressives',
        'xG par 90 minutes', 'xAG par 90 minutes'
    ]

    # Initialisation du radar
    radar = Radar(
        params=columns_to_plot,
        min_range=[0 for _ in columns_to_plot],
        max_range=[100 for _ in columns_to_plot]
    )

    # Initialisation de la figure avec la grille
    fig, axs = mplsoccer.grid(figheight=14, grid_height=0.915, title_height=0.06, endnote_height=0.025,
                              title_space=0, endnote_space=0, grid_key='radar', axis=False)

    # Configuration du radar
    radar.setup_axis(ax=axs['radar'])  # Formatage de l'axe radar
    rings_inner = radar.draw_circles(ax=axs['radar'], facecolor='#ffb2b2', edgecolor='#fc5f5f')

    # Tracer la comparaison entre les deux joueurs
    radar_output = radar.draw_radar_compare(
        list(player1[columns_to_plot].values.flatten()), 
        list(player2[columns_to_plot].values.flatten()), 
        ax=axs['radar'],
        kwargs_radar={'facecolor': '#00f2c1', 'alpha': 0.6},  # Couleur du premier joueur
        kwargs_compare={'facecolor': '#d80499', 'alpha': 0.6}  # Couleur du deuxième joueur
    )
    radar_poly, radar_poly2, vertices1, vertices2 = radar_output

    # Ajouter des étiquettes de plage
    range_labels = radar.draw_range_labels(ax=axs['radar'], fontsize=25, fontproperties=font_props)
    param_labels = radar.draw_param_labels(ax=axs['radar'], fontsize=25, fontproperties=font_props)

    # Tracer les points des joueurs
    axs['radar'].scatter(vertices1[:, 0], vertices1[:, 1], c='#00f2c1', edgecolors='#6d6c6d', marker='o', s=150, zorder=2)  # Premier joueur
    axs['radar'].scatter(vertices2[:, 0], vertices2[:, 1], c='#d80499', edgecolors='#6d6c6d', marker='o', s=150, zorder=2)  # Deuxième joueur

    # Ajouter des textes de titre et d'annotation
    endnote_text = axs['endnote'].text(0.99, 0.5, 'Inspired By: StatsBomb / Rami Moghadam', fontsize=15,
                                       fontproperties=font_props, ha='right', va='center')

    title1_text = axs['title'].text(0.01, 0.65, player1_name, fontsize=25, color='#01c49d',
                                    fontproperties=font_props, ha='left', va='center')
    title2_text = axs['title'].text(0.01, 0.25, 'Club de ' + player1_name, fontsize=20, fontproperties=font_props,
                                    ha='left', va='center', color='#01c49d')

    title3_text = axs['title'].text(0.99, 0.65, player2_name, fontsize=25,
                                    fontproperties=font_props, ha='right', va='center', color='#d80499')
    title4_text = axs['title'].text(0.99, 0.25, 'Club de ' + player2_name, fontsize=20,
                                    fontproperties=font_props, ha='right', va='center', color='#d80499')

    # Affichage de la figure
    plt.show()

except ValueError as e:
    print(e)
