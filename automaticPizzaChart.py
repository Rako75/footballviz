import streamlit as st
import pandas as pd
import numpy as np
from mplsoccer import PyPizza, FontManager
import matplotlib.pyplot as plt

# ---------------------- Paramètres radar ----------------------

RAW_STATS = {
    "Buts\nsans pénalty": "Buts (sans penalty)",
    "Passes déc.": "Passes décisives",
    "Buts +\nPasses déc.": "Buts + Passes D",
    "Cartons\njaunes": "Cartons jaunes",
    "Cartons\nrouges": "Cartons rouges",
    "Passes\ntentées": "Passes tentées",
    "Passes\nclés": "Passes clés",
    "Passes\nprogressives": "Passes progressives",
    "Passes\ndernier 1/3": "Passes dans le dernier tiers",
    "Passes\ndans la surface": "Passes dans la surface",
    "Touches": "Touches de balle",
    "Dribbles\ntentés": "Dribbles tentés",
    "Dribbles\nréussis": "Dribbles réussis",
    "Ballons perdus\nsous pression": "Ballons perdus sous la pression d’un adversaire",
    "Ballons perdus\nen conduite": "Ballons perdus en conduite",
    "Tacles\ngagnants": "Tacles gagnants",
    "Tirs\nbloqués": "Tirs bloqués",
    "Duels\ngagnés": "Duels défensifs gagnés",
    "Interceptions": "Interceptions",
    "Dégagements": "Dégagements"
}

SLICE_COLORS = ["#bbEE90"] * 5 + ["#FF93ff"] * 5 + ["#FFCCCB"] * 5 + ["#87CEEB"] * 5
TEXT_COLORS = ["#000000"] * 20

# ---------------------- Fonction de calcul des percentiles ----------------------

def calculate_percentiles(joueur_nom, df):
    player = df[df["Joueur"] == joueur_nom].iloc[0]
    params, values = [], []

    for label, col in RAW_STATS.items():
        try:
            if "par 90 minutes" in col or "%" in col:
                player_value = player[col]
                dist = df[col]
            else:
                player_value = player[col] / player["Matchs en 90 min"]
                dist = df[col] / df["Matchs en 90 min"]

            percentile = np.round((dist < player_value).mean() * 100, 1)
        except:
            percentile = 0

        params.append(label)
        values.append(percentile)

    return values

# ---------------------- Radar individuel ----------------------

def plot_radar(joueur_nom, values, color="#FF69B4"):
    font_normal = FontManager()
    font_bold = FontManager()

    baker = PyPizza(
        params=list(RAW_STATS.keys()),
        background_color="#132257",
        straight_line_color="#000000",
        straight_line_lw=1,
        last_circle_color="#000000",
        last_circle_lw=1,
        other_circle_lw=0,
        inner_circle_size=11
    )

    fig, ax = baker.make_pizza(
        values,
        figsize=(10, 12),
        param_location=110,
        color_blank_space="same",
        slice_colors=SLICE_COLORS,
        value_colors=TEXT_COLORS,
        value_bck_colors=SLICE_COLORS,
        blank_alpha=0.4,
        kwargs_slices=dict(edgecolor="#000000", zorder=1, linewidth=1, alpha=0.7),
        kwargs_params=dict(color="#ffffff", fontsize=13, fontproperties=font_bold.prop, va="center"),
        kwargs_values=dict(color="#ffffff", fontsize=11, fontproperties=font_normal.prop, zorder=2,
                           bbox=dict(edgecolor="#000000", facecolor=color, boxstyle="round,pad=0.2", lw=1))
    )

    fig.text(0.515, 0.95, joueur_nom, size=24, ha="center", fontproperties=font_bold.prop, color="#ffffff")
    fig.text(0.515, 0.925, "Stats par 90 min - FBRef | Saison 2024-25", size=13,
             ha="center", fontproperties=font_bold.prop, color="#ffffff")

    st.pyplot(fig)

# ---------------------- App Streamlit ----------------------

def main():
    st.set_page_config(page_title="Radar Comparatif Joueurs", layout="wide")
    st.title("⚽ Radar de performances - Saison 2024-2025")

    df = pd.read_csv("df_BIG2025.csv")

    ligues = df["Compétition"].dropna().unique()

    col1, col2 = st.columns(2)

    with col1:
        ligue1 = st.selectbox("Ligue du Joueur 1", ligues, key="ligue1")
        joueurs1 = df[df["Compétition"] == ligue1]["Joueur"].unique()
        joueur1 = st.selectbox("Joueur 1", joueurs1)

    with col2:
        ligue2 = st.selectbox("Ligue du Joueur 2 (optionnel)", ligues, key="ligue2")
        joueurs2 = df[df["Compétition"] == ligue2]["Joueur"].unique()
        joueur2 = st.selectbox("Joueur 2", [""] + list(joueurs2))

    if joueur1 and not joueur2:
        st.subheader(f"🎯 Radar individuel : {joueur1}")
        df_j1 = df[df["Compétition"] == ligue1]
        values1 = calculate_percentiles(joueur1, df_j1)
        plot_radar(joueur1, values1, color="#1f77b4")

    elif joueur1 and joueur2:
        st.subheader(f"⚔️ Radar comparatif fusionné : {joueur1} vs {joueur2}")

        df_j1 = df[df["Compétition"] == ligue1]
        df_j2 = df[df["Compétition"] == ligue2]

        values1 = calculate_percentiles(joueur1, df_j1)
        values2 = calculate_percentiles(joueur2, df_j2)

        font_normal = FontManager()
        font_bold = FontManager()

        baker = PyPizza(
            params=list(RAW_STATS.keys()),
            background_color="#132257",
            straight_line_color="#000000",
            straight_line_lw=1,
            last_circle_color="#000000",
            last_circle_lw=1,
            other_circle_lw=0,
            inner_circle_size=11
        )

        fig, ax = baker.make_pizza(
            values1,
            figsize=(10, 12),
            param_location=110,
            color_blank_space="same",
            slice_colors=SLICE_COLORS,
            value_colors=TEXT_COLORS,
            value_bck_colors=SLICE_COLORS,
            blank_alpha=0.4,
            kwargs_slices=dict(edgecolor="#000000", zorder=1, linewidth=1, alpha=0.7),
            kwargs_params=dict(color="#ffffff", fontsize=13, fontproperties=font_bold.prop, va="center"),
            kwargs_values=dict(color="#ffffff", fontsize=11, fontproperties=font_normal.prop, zorder=2,
                               bbox=dict(edgecolor="#000000", facecolor="#FF69B4", boxstyle="round,pad=0.2", lw=1))
        )

        angles = np.linspace(0, 2 * np.pi, len(values2), endpoint=False).tolist()
        values2_extended = values2 + values2[:1]
        angles_extended = angles + angles[:1]
        ax.plot(angles_extended, values2_extended, color="#00CED1", linewidth=2.5, linestyle="--", zorder=5, label=joueur2)

        fig.text(0.515, 0.95, f"{joueur1} vs {joueur2}", size=24, ha="center", fontproperties=font_bold.prop, color="#ffffff")
        fig.text(0.515, 0.925, "Radar comparatif - Stats par 90 min - FBRef | Saison 2024-25", size=13,
                 ha="center", fontproperties=font_bold.prop, color="#ffffff")

        legend_elements = [
            plt.Line2D([0], [0], color="#FF69B4", lw=10, label=joueur1),
            plt.Line2D([0], [0], color="#00CED1", lw=3, linestyle='--', label=joueur2)
        ]
        ax.legend(handles=legend_elements, loc='lower center', bbox_to_anchor=(0.5, -0.05), ncol=2, frameon=False, fontsize=12)

        st.pyplot(fig)


if __name__ == "__main__":
    main()
