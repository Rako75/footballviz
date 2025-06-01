import streamlit as st
import pandas as pd
import numpy as np
from mplsoccer import PyPizza, FontManager
import matplotlib.pyplot as plt
from matplotlib import font_manager
from highlight_text import fig_text

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

SLICE_COLORS = ["#1A78CF"] * 10 + ["#FF9300"] * 10
TEXT_COLORS = ["#000000"] * 20

# ---------------------- Fonctions ----------------------

def calculate_percentiles(df, raw_stats):
    df_percentiles = df.copy()
    for label, col in raw_stats.items():
        try:
            stat_per_90 = df[col] / df["Matchs en 90 min"]
            df_percentiles[label] = (stat_per_90.rank(pct=True) * 100).astype(int)
        except:
            df_percentiles[label] = 0
    return df_percentiles

def get_player_percentiles(player_name, df_percentiles):
    player = df_percentiles[df_percentiles["Joueur"] == player_name].iloc[0]
    return [player[label] for label in RAW_STATS.keys()]

def plot_individual_radar(player_name, percentiles):
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

    font_normal = FontManager()
    font_bold = FontManager()

    fig, ax = baker.make_pizza(
        percentiles,
        figsize=(10, 12),
        color_blank_space="same",
        slice_colors=SLICE_COLORS,
        value_colors=["#ffffff"] * len(percentiles),
        value_bck_colors=SLICE_COLORS,
        blank_alpha=0.4,
        kwargs_slices=dict(edgecolor="#000000", zorder=2, linewidth=1),
        kwargs_params=dict(color="#ffffff", fontsize=13, fontproperties=font_bold.prop, va="center"),
        kwargs_values=dict(color="#ffffff", fontsize=11, fontproperties=font_normal.prop, zorder=3,
                           bbox=dict(edgecolor="#000000", facecolor="cornflowerblue", boxstyle="round,pad=0.2", lw=1))
    )

    fig.text(0.515, 0.945, player_name, size=27, ha="center", fontproperties=font_bold.prop, color="#ffffff")
    fig.text(0.515, 0.925, "Stats en percentile par 90 min - FBRef | Saison 2024-25", size=13,
             ha="center", fontproperties=font_bold.prop, color="#ffffff")

    st.pyplot(fig)

def plot_comparison_radar(player1, player2, percentiles1, percentiles2):
    baker = PyPizza(
        params=list(RAW_STATS.keys()),
        background_color="#EBEBE9",
        straight_line_color="#222222",
        straight_line_lw=1,
        last_circle_lw=1,
        last_circle_color="#222222",
        other_circle_ls="-.",
        other_circle_lw=1
    )

    font_normal = FontManager()
    font_bold = FontManager()
    font_italic = FontManager()

    fig, ax = baker.make_pizza(
        percentiles1,
        compare_values=percentiles2,
        figsize=(10, 10),
        kwargs_slices=dict(facecolor="#1A78CF", edgecolor="#222222", zorder=2, linewidth=1),
        kwargs_compare=dict(facecolor="#FF9300", edgecolor="#222222", zorder=2, linewidth=1),
        kwargs_params=dict(color="#000000", fontsize=12, fontproperties=font_normal.prop, va="center"),
        kwargs_values=dict(color="#000000", fontsize=12, fontproperties=font_normal.prop, zorder=3,
                           bbox=dict(edgecolor="#000000", facecolor="#1A78CF", boxstyle="round,pad=0.2", lw=1)),
        kwargs_compare_values=dict(color="#000000", fontsize=12, fontproperties=font_normal.prop, zorder=3,
                                   bbox=dict(edgecolor="#000000", facecolor="#FF9300", boxstyle="round,pad=0.2", lw=1))
    )

    baker.adjust_texts([False]*20, offset=-0.17, adj_comp_values=True)

    fig_text(0.515, 0.99, f"<{player1}> vs <{player2}>", size=17, fig=fig,
             highlight_textprops=[{"color": '#1A78CF'}, {"color": '#FF9300'}],
             ha="center", fontproperties=font_bold.prop, color="#000000")

    fig.text(0.515, 0.942, "Stats en percentile par 90 min - FBRef | Saison 2024-25", size=15,
             ha="center", fontproperties=font_bold.prop, color="#000000")

    # Légende
    fig.text(0.05, 0.02, f"{player1} = 🔵", fontsize=12, fontproperties=font_normal.prop, color="#1A78CF")
    fig.text(0.05, 0.00, f"{player2} = 🟠", fontsize=12, fontproperties=font_normal.prop, color="#FF9300")

    st.pyplot(fig)

# ---------------------- Interface Streamlit ----------------------

df = pd.read_csv("df_BIG2025.csv")
df_percentiles = calculate_percentiles(df, RAW_STATS)

st.title("📊 Radar Stats - Saison 2024-2025")
mode = st.radio("Choisissez le type de radar:", ["Radar individuel", "Radar comparatif"])

if mode == "Radar individuel":
    joueur = st.selectbox("Sélectionnez un joueur", df["Joueur"].unique())
    if joueur:
        percentiles = get_player_percentiles(joueur, df_percentiles)
        plot_individual_radar(joueur, percentiles)

elif mode == "Radar comparatif":
    col1, col2 = st.columns(2)
    with col1:
        joueur1 = st.selectbox("Joueur 1", df["Joueur"].unique(), key="joueur1")
    with col2:
        joueur2 = st.selectbox("Joueur 2", df["Joueur"].unique(), key="joueur2")

    if joueur1 and joueur2 and joueur1 != joueur2:
        percentiles1 = get_player_percentiles(joueur1, df_percentiles)
        percentiles2 = get_player_percentiles(joueur2, df_percentiles)
        plot_comparison_radar(joueur1, joueur2, percentiles1, percentiles2)
