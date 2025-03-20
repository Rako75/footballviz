import streamlit as st
import pandas as pd
import plotly.express as px
from scraping import process_data  # Importation de la fonction de scraping

# Interface Streamlit
st.title("Nuage de points - Saison 2024/2025")

# Bouton pour recharger les données depuis le web
if st.button("Charger les données depuis le web"):
    # Appeler le processus de scraping pour récupérer les données
    df = process_data()  # Cette fonction va récupérer et nettoyer les données à chaque clic
    if df is not None:
        # Si les données sont récupérées avec succès, les enregistrer et afficher un message de succès
        df.to_csv("df_2025.csv", index=False)
        st.success("Données mises à jour avec succès !")
    else:
        st.error("Erreur lors de la récupération des données.")
else:
    try:
        # Si le bouton n'est pas cliqué, charge le fichier local existant
        df = pd.read_csv("df_2025.csv")
        st.success("Données chargées depuis le fichier local.")
    except FileNotFoundError:
        st.warning("Aucune donnée trouvée, veuillez charger les données.")
        
# Vérifier si df existe
if 'df' in locals():
    # Filtrer les colonnes numériques
    numerical_columns = df.select_dtypes(include=['number']).columns.tolist()

    # Widgets de sélection des axes
    x_axis = st.sidebar.selectbox("Sélectionner la variable pour l'axe X", numerical_columns)
    y_axis = st.sidebar.selectbox("Sélectionner la variable pour l'axe Y", numerical_columns)

    # Sélection des compétitions
    competitions = ["Premier League", "La Liga", "Ligue 1", "Bundliga", "Serie A"]
    selected_competitions = st.sidebar.multiselect("Sélectionner les compétitions", competitions, default=competitions)

    # Filtrer par minutes jouées
    min_minutes = st.sidebar.slider("Nombre minimum de minutes jouées", min_value=0, max_value=int(df["Minutes jouées"].max()), value=500)

    # Nombre de labels de joueurs
    num_labels = st.sidebar.slider("Nombre de labels à afficher", min_value=0, max_value=50, value=10)
    label_size = st.sidebar.slider("Taille de texte des labels", min_value=2, max_value=8, value=5)

    # Filtrer les données
    filtered_df = df[(df["Compétition"].isin(selected_competitions)) & (df["Minutes jouées"] >= min_minutes)]

    # Convertir en numérique pour éviter les erreurs
    filtered_df[x_axis] = pd.to_numeric(filtered_df[x_axis], errors='coerce')
    filtered_df[y_axis] = pd.to_numeric(filtered_df[y_axis], errors='coerce')

    # Sélectionner les meilleurs joueurs pour les labels
    top_10_x = filtered_df.nlargest(num_labels, x_axis)
    top_10_y = filtered_df.nlargest(num_labels, y_axis)

    # Fusionner les deux top 10 (éviter doublons)
    top_10_combined = pd.concat([top_10_x, top_10_y]).drop_duplicates(subset="Joueur")

    # S'assurer que le nombre de labels affichés correspond au nombre sélectionné
    top_10_combined = top_10_combined.head(num_labels)

    # Création du graphique avec **TOUS** les joueurs
    fig = px.scatter(filtered_df, x=x_axis, y=y_axis, hover_data=["Joueur", "Équipe", "Compétition"], color="Compétition")

    # Dictionnaire pour suivre le nombre d'occurrences de chaque X
    x_counts = top_10_combined[x_axis].value_counts().to_dict()
    x_positions = {}  # Suivi des positions pour alterner à gauche/droite

    # Ajouter des annotations avec alternance des labels à gauche et à droite si nécessaire
    for i, row in top_10_combined.iterrows():
        x_val = row[x_axis]
        y_val = row[y_axis]

        # Déterminer si on met le label à gauche ou à droite
        if x_counts[x_val] > 1:
            if x_val in x_positions:
                x_positions[x_val] += 1
            else:
                x_positions[x_val] = 0
            shift = (-0.02 if x_positions[x_val] % 2 == 0 else 0.02) * (filtered_df[x_axis].max() - filtered_df[x_axis].min())
        else:
            shift = 0

        fig.add_annotation(
            x=x_val + shift,  # Déplacement horizontal des labels si besoin
            y=y_val + (filtered_df[y_axis].max() - filtered_df[y_axis].min()) * 0.02,  # Décalage léger vers le haut
            text=row["Joueur"],  
            showarrow=False,  
            font=dict(size=label_size, color="white"),
            bgcolor="rgba(0,0,0,0)"  # Fond transparent
        )

    # Ajuster le layout
    fig.update_layout(
        title=f"Analyse des joueurs ({x_axis} vs {y_axis})",
        xaxis_title=x_axis,
        yaxis_title=y_axis,
        showlegend=True  # Affichage des couleurs par compétition
    )

    # Affichage du graphique
    st.plotly_chart(fig)

    # Affichage des deux Top 10 séparés
    st.write(f"### Top {num_labels} des meilleurs joueurs selon la variable {x_axis}")
    st.dataframe(top_10_x[['Joueur', 'Équipe', 'Compétition', x_axis]])

    st.write(f"### Top {num_labels} des meilleurs joueurs selon la variable {y_axis}")
    st.dataframe(top_10_y[['Joueur', 'Équipe', 'Compétition', y_axis]])
