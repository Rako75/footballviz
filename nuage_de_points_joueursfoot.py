# Créer le graphique avec matplotlib
def plot_graph(df):
    # Utiliser les paramètres par défaut de Matplotlib (sans style spécifique)
    fig, ax = plt.subplots(figsize=(16, 12))  # Augmenter la taille du graphique

    # Créer le nuage de points
    scatter = ax.scatter(
        df["Passes cles"],
        df["Actions menant a un tir par 90 minutes"],
        s=df["Age"] * 10,  # Taille des points proportionnelle à l'âge
        c=df["Actions menant a un but par 90 minutes"],  # Couleur des points
        cmap="coolwarm",
        alpha=0.7,
        edgecolors="w"
    )

    # Ajouter les noms des joueurs à côté des points
    for i, row in df.iterrows():
        ax.text(
            row["Passes cles"],
            row["Actions menant a un tir par 90 minutes"] + 0.1,  # Décalage pour que le texte soit au-dessus du point
            row["Joueur"],
            fontsize=12,  # Augmenter la taille de la police pour la lisibilité
            color="white",  # Nom du joueur en blanc pour mieux ressortir sur un fond sombre
            ha="center",  # Alignement horizontal centré par rapport au point
            va="center",   # Alignement vertical centré
            fontweight="bold",  # Texte en gras pour plus de lisibilité
            fontname="Arial"  # Police claire et lisible
        )

    # Ajouter un colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label("Actions menant à un but par 90 minutes", rotation=270, labelpad=15, color="white")
    cbar.ax.yaxis.set_tick_params(color="white")
    plt.setp(plt.getp(cbar.ax.axes, "yticklabels"), color="white")

    # Ajouter les étiquettes et le titre
    ax.set_title("Création d'occasion par 90 min", fontsize=16, color="white")
    ax.set_xlabel("Passes clés", fontsize=14, color="white")
    ax.set_ylabel("Actions menant à un tir par 90 minutes", fontsize=14, color="white")

    # Ajuster les limites des axes
    ax.set_xlim(df["Passes cles"].min() - 1, df["Passes cles"].max() + 1)
    ax.set_ylim(df["Actions menant a un tir par 90 minutes"].min() - 0.5,
                df["Actions menant a un tir par 90 minutes"].max() + 0.5)

    # Supprimer la grille et ajuster les couleurs des ticks
    ax.grid(True, linestyle='-', color='gray', alpha=0.5)
    ax.tick_params(colors="white")

    # Ajouter les axes du centre
    ax.axhline(0, color='white', linewidth=1)
    ax.axvline(0, color='white', linewidth=1)

    return fig
