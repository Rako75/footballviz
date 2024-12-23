def create_radarchart(player_name, data, valid_criteria_by_position):
    # Filtrer les données pour le joueur sélectionné
    player_data = data[data["Joueur"] == player_name].iloc[0]
    position = player_data["Position"]

    # Critères pertinents pour la position
    criteria = valid_criteria_by_position.get(position, [])
    criteria_normalized = [col + "_normalized" for col in criteria]

    # Vérification que les critères normalisés existent
    criteria_normalized = [col for col in criteria_normalized if col in data.columns]

    # Extraire les valeurs et les critères
    stats = player_data[criteria_normalized].values
    radar_data = pd.DataFrame({
        "Critères": criteria,
        "Valeurs": stats
    })

    # Création du radar avec Plotly
    fig = px.line_polar(radar_data, r="Valeurs", theta="Critères", line_close=True)
    fig.update_traces(fill="toself", line_color="blue")  # Ligne bleue pour une meilleure visibilité
    fig.update_layout(
        title=f"<b>Radarchart de {player_name} ({position})</b>",
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1]),  # Normalisation entre 0 et 1
            angularaxis=dict(tickfont=dict(size=14))      # Agrandir les labels
        ),
        template="plotly_dark"  # Option de style pour un fond sombre
    )

    return fig
