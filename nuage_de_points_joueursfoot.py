def prepare_data(df, position, league):
    # Filtrer par position
    df_filtered = df[df["Position"].str.contains(position, case=False, na=False)]
    
    # Filtrer par ligue
    if league != "Toutes les ligues":
        df_filtered = df_filtered[df_filtered["Ligue"] == league]
    
    # Calculer les métriques spécifiques
    if position == "Midfielder":
        df_filtered["Actions Défensives"] = df_filtered["Tacles"] + df_filtered["Interceptions"]
        df_filtered["Création Off."] = (
            df_filtered["Passes cles"] +
            df_filtered["Actions menant a un tir par 90 minutes"] +
            df_filtered["Actions menant a un but par 90 minutes"]
        )
        df_filtered["Score Total"] = df_filtered["Actions Défensives"] + df_filtered["Création Off."]
    elif position == "Forward":
        df_filtered["Création totale"] = (
            df_filtered["Passes cles"] +
            df_filtered["Actions menant a un tir par 90 minutes"] +
            df_filtered["Actions menant a un but par 90 minutes"]
        )
        df_filtered["Score Total"] = df_filtered["Création totale"]
    
    # Vérification : La colonne "Score Total" existe-t-elle ?
    if "Score Total" not in df_filtered.columns:
        raise ValueError(f"Erreur : La colonne 'Score Total' n'a pas été créée pour la position {position}.")
    
    # Retourner les 20 meilleurs joueurs
    return df_filtered.nlargest(20, "Score Total")
