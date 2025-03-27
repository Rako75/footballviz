import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Charger le fichier CSV
file_path = "Bundesliga Top5 Points every match.csv"  # Mettez le bon chemin ici
df = pd.read_csv(file_path, encoding="ISO-8859-1", sep=";")

# Extraire les noms des équipes
teams = df["Equipe"]

# Extraire les journées et les classements
rank_days = [col for col in df.columns if "Rank_Journée" in col]
rank_data = df[rank_days].T  # Transposer pour avoir les journées en ligne

# Renommer les colonnes pour correspondre aux équipes
rank_data.columns = teams
rank_data.index = range(1, len(rank_data) + 1)  # Convertir en journées numériques

# Interface Streamlit
st.title("Bump Chart - Classement des 5 meilleures équipes de Bundesliga")
st.write("Ce graphique montre l'évolution du classement des équipes à chaque journée.")

# Tracer le bump chart
fig, ax = plt.subplots(figsize=(12, 8))
sns.set_style("whitegrid")

for team in teams:
    ax.plot(rank_data.index, rank_data[team], marker="o", label=team, linewidth=2.5)

ax.invert_yaxis()  # Inverser l'axe des y pour que le rang 1 soit en haut
ax.set_title("Classement des 5 meilleures équipes de Bundesliga par journée", fontsize=14, fontweight='bold')
ax.set_xlabel("Journée", fontsize=12)
ax.set_ylabel("Classement", fontsize=12)
ax.set_xticks(rank_data.index)
ax.set_xticklabels(rank_data.index, rotation=45)
ax.set_yticks(range(1, len(teams) + 1))
ax.legend(title="Équipe", bbox_to_anchor=(1.05, 1), loc='upper left')
ax.grid(True, linestyle='--', alpha=0.7)

# Afficher le graphique dans Streamlit
st.pyplot(fig)
