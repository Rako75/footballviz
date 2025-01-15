import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Charger le fichier CSV
df = pd.read_csv("df_Big5.csv")

# Filtrer les attaquants (Position = "Forward")
df_forwards = df[df["Position"].str.contains("Forward", case=False, na=False)]

# Calculer une métrique combinée pour la création d'occasions
df_forwards["Création totale"] = (
    df_forwards["Passes cles"] +
    df_forwards["Actions menant a un tir par 90 minutes"] +
    df_forwards["Actions menant a un but par 90 minutes"]
)

top_20_forwards = df_forwards.nlargest(20, "Création totale")

# Extraire les métriques nécessaires
top_20_forwards = top_20_forwards[
    ["Joueur", "Age", "Passes cles", "Actions menant a un tir par 90 minutes", "Actions menant a un but par 90 minutes"]
]

# Configurer le style du graphique avec un fond noir
sns.set_style("white")
plt.style.use("dark_background")

# Créer le nuage de points
plt.figure(figsize=(14, 10))
scatter = plt.scatter(
    top_20_forwards["Passes cles"],
    top_20_forwards["Actions menant a un tir par 90 minutes"],
    s=top_20_forwards["Age"] * 10,  # Taille des points (proportionnelle à l'âge)
    c=top_20_forwards["Actions menant a un but par 90 minutes"],  # Couleur des points (actions menant à un but)
    cmap="coolwarm",
    alpha=0.7,
    edgecolors="w"
)

# Ajouter un colorbar
cbar = plt.colorbar(scatter)
cbar.set_label("Actions menant à un but par 90 minutes", rotation=270, labelpad=15, color="white")
cbar.ax.yaxis.set_tick_params(color="white")
plt.setp(plt.getp(cbar.ax.axes, "yticklabels"), color="white")

# Ajouter les étiquettes et le titre
plt.title("Création d'occasion par 90 min", fontsize=16, color="white")
plt.xlabel("Passes clés", fontsize=12, color="white")
plt.ylabel("Actions menant à un tir par 90 minutes", fontsize=12, color="white")

# Définir les limites des axes
plt.xlim(top_20_forwards["Passes cles"].min() - 1, top_20_forwards["Passes cles"].max() + 1)
plt.ylim(top_20_forwards["Actions menant a un tir par 90 minutes"].min() - 0.1,
         top_20_forwards["Actions menant a un tir par 90 minutes"].max() + 0.1)

# Ajouter les noms des joueurs juste au-dessus des points
for i, row in top_20_forwards.iterrows():
    plt.text(
        row["Passes cles"],
        row["Actions menant a un tir par 90 minutes"] + 0.05,  # Décalage vertical pour placer les noms au-dessus des points
        row["Joueur"],
        fontsize=10,
        alpha=0.9,
        color="white",
        fontname="Arial",
        weight="bold",
        ha='center',
        va='bottom'
    )

# Ajouter les lignes des axes X et Y
plt.axhline(0, color="white", linewidth=1, linestyle="--", alpha=0.7)  # Axe X
plt.axvline(0, color="white", linewidth=1, linestyle="--", alpha=0.7)  # Axe Y

# Ajouter des lignes au centre
x_median = (top_20_forwards["Passes cles"].min() + top_20_forwards["Passes cles"].max()) / 2
y_median = (top_20_forwards["Actions menant a un tir par 90 minutes"].min() + top_20_forwards["Actions menant a un tir par 90 minutes"].max()) / 2

plt.axvline(x_median, color="yellow", linewidth=1.5, linestyle="--", alpha=0.7)  # Ligne verticale au centre
plt.axhline(y_median, color="yellow", linewidth=1.5, linestyle="--", alpha=0.7)  # Ligne horizontale au centre

# Supprimer la grille et les bordures
plt.grid(False)
plt.gca().spines["top"].set_visible(False)
plt.gca().spines["right"].set_visible(False)
plt.gca().spines["left"].set_visible(False)
plt.gca().spines["bottom"].set_visible(False)

# Ajuster les couleurs des ticks
plt.gca().tick_params(colors="white")

plt.tight_layout()
plt.show()
