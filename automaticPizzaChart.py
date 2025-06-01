import streamlit as st
import pandas as pd
import numpy as np
from mplsoccer import PyPizza, FontManager
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ---------------------- PARAMÈTRES DU RADAR ----------------------

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

# ---------------------- COULEURS ----------------------

COLOR_1 = "#1A78CF"
COLOR_2 = "#FF9300"
SLICE_COLORS = [COLOR_1] * len(RAW_STATS)

# ---------------------- FONCTIONS ----------------------

def calculate_percentiles(player_name, df):
    player = df[df["Joueur"] == player_name].iloc[0]
    percentiles = []

    for label, col in RAW_STATS.items():
        try:
            if "par 90 minutes" in col or "%" in col:
                val = player[col]
                dist = df[col]
            else:
                val = player[col] / player["Matchs en 90 min"]
                dist = df[col] / df["Matchs en 90 min"]
            percentile = round((dist < val).mean() * 100, 1)
        except:
            percentile = 0
        percentiles.append(percentile)

    return percentiles

# ---------------------- APP STREAMLIT ----------------------

st.set_page_config(layout="wide", page_title="Radar de joueurs")
st.title("📊 Radar de performances - Saison 2024/25")

# Charger les données
df = pd.read_csv("df_BIG2025.csv", sep=",")
ligues = df["Compétition"].unique()

# Choix du mode
mode = st.radio("Mode de visualisation", ["Radar individuel", "Radar comparatif"], horizontal=True)

font_normal = FontManager()
font_bold = FontManager()
font_italic = FontManager()

# ---------------------- MODE INDIVIDUEL ----------------------

if mode == "Radar individuel":
    col1, _ = st.columns([2, 1])
    with col1:
        ligue1 = st.selectbox("Compétition", ligues, key="ligue_ind")
        joueur1 = st.selectbox("Joueur", df[df["Compétition"] == ligue1]["Joueur"].sort_values(), key="joueur_ind")

    if joueur1:
        st.subheader(f"🎯 Radar individuel : {joueur1}")
        df_j1 = df[df["Compétition"] == ligue1]
        values1 = calculate_percentiles(joueur1, df_j1)

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
            value_colors=["#ffffff"] * len(values1),
            value_bck_colors=SLICE_COLORS,
            kwargs_slices=dict(edgecolor="#000000", zorder=2, linewidth=1),
            kwargs_params=dict(color="#ffffff", fontsize=13, fontproperties=font_bold.prop),
            kwargs_values=dict(color="#ffffff", fontsize=11, fontproperties=font_normal.prop,
                               bbox=dict(edgecolor="#000000", facecolor=COLOR_1, boxstyle="round,pad=0.2", lw=1))
        )

        fig.text(0.515, 0.95, joueur1, size=24, ha="center", fontproperties=font_bold.prop, color="#ffffff")
        fig.text(0.515, 0.925, "Stats par 90 min - FBRef | Saison 2024-25", size=13,
                 ha="center", fontproperties=font_bold.prop, color="#ffffff")
        st.pyplot(fig)

# ---------------------- MODE COMPARATIF ----------------------

elif mode == "Radar comparatif":
    col1, col2 = st.columns(2)
    with col1:
        ligue1 = st.selectbox("Ligue Joueur 1", ligues, key="ligue1")
        joueur1 = st.selectbox("Joueur 1", df[df["Compétition"] == ligue1]["Joueur"].sort_values(), key="joueur1")

    with col2:
        ligue2 = st.selectbox("Ligue Joueur 2", ligues, key="ligue2")
        joueur2 = st.selectbox("Joueur 2", df[df["Compétition"] == ligue2]["Joueur"].sort_values(), key="joueur2")

    if joueur1 and joueur2:
        st.subheader(f"⚔️ Radar comparatif : {joueur1} vs {joueur2}")
        df_j1 = df[df["Compétition"] == ligue1]
        df_j2 = df[df["Compétition"] == ligue2]
        values1 = calculate_percentiles(joueur1, df_j1)
        values2 = calculate_percentiles(joueur2, df_j2)

        params_offset = [False] * len(RAW_STATS)
        params_offset[9] = True
        params_offset[10] = True

        baker = PyPizza(
            params=list(RAW_STATS.keys()),
            background_color="#ffffff",
            straight_line_color="#000000",
            straight_line_lw=1,
            last_circle_color="#000000",
            last_circle_lw=1,
            other_circle_ls="-.",
            other_circle_lw=1
        )

        fig, ax = baker.make_pizza(
            values1,
            compare_values=values2,
            figsize=(10, 10),
            kwargs_slices=dict(facecolor=COLOR_1, edgecolor="#222222", linewidth=1, zorder=2),
            kwargs_compare=dict(facecolor=COLOR_2, edgecolor="#222222", linewidth=1, zorder=2),
            kwargs_params=dict(color="#000000", fontsize=12, fontproperties=font_bold.prop),
            kwargs_values=dict(
                color="#000000", fontsize=12, fontproperties=font_normal.prop, zorder=3,
                bbox=dict(edgecolor="#000000", facecolor=COLOR_1, boxstyle="round,pad=0.2", lw=1)
            ),
            kwargs_compare_values=dict(
                color="#000000", fontsize=12, fontproperties=font_normal.prop, zorder=3,
                bbox=dict(edgecolor="#000000", facecolor=COLOR_2, boxstyle="round,pad=0.2", lw=1)
            )
        )

        baker.adjust_texts(params_offset, offset=-0.17, adj_comp_values=True)

        fig.text(0.515, 0.99, f"{joueur1} vs {joueur2}", size=18, ha="center",
                 fontproperties=font_bold.prop, color="#000000")
        fig.text(0.515, 0.955, "Radar comparatif - Stats par 90 min | FBRef | Saison 2024-25",
                 size=13, ha="center", fontproperties=font_bold.prop, color="#444444")

        legend_p1 = mpatches.Patch(color=COLOR_1, label=joueur1)
        legend_p2 = mpatches.Patch(color=COLOR_2, label=joueur2)
        ax.legend(handles=[legend_p1, legend_p2], loc="upper right", bbox_to_anchor=(1.3, 1.0))

        fig.text(0.99, 0.01, "Source: FBRef\nInspiration: @Worville, @FootballSlices",
                 size=8, ha="right", fontproperties=font_italic.prop, color="#888888")
        st.pyplot(fig)
