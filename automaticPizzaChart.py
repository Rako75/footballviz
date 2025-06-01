import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mplsoccer import PyPizza, FontManager
from matplotlib import font_manager
from highlight_text import fig_text

# ---------------------- Données ----------------------

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

SLICE_COLORS = ["#1A78CF"] * 20
COMPARE_COLORS = ["#FF9300"] * 20
TEXT_COLORS = ["#000000"] * 20

# ---------------------- Chargement et préparation ----------------------

@st.cache_data
def load_and_prepare_data():
    df = pd.read_csv("df_BIG2025.csv")

    # Calcul des per 90 minutes et percentiles
    for label, col in RAW_STATS.items():
        per90_col = f"{col}_per_90"
        if per90_col not in df.columns:
            df[per90_col] = df[col] / df["Matchs en 90 min"]
        df[f"{col}_percentile"] = (df[per90_col].rank(pct=True) * 100).astype(int)

    return df

# ---------------------- Affichage radar ----------------------

def draw_individual_radar(player_name, df):
    player = df[df["Joueur"] == player_name].iloc[0]
    values = [player[f"{col}_percentile"] for col in RAW_STATS.values()]
    values_display = [f"{v}%" for v in values]

    font_normal = FontManager()
    font_bold = FontManager()

    baker = PyPizza(params=list(RAW_STATS.keys()), background_color="#132257")

    fig, ax = baker.make_pizza(
        values,
        figsize=(9, 9),
        color_blank_space="same",
        slice_colors=SLICE_COLORS,
        value_colors=TEXT_COLORS,
        value_bck_colors=SLICE_COLORS,
        kwargs_slices=dict(edgecolor="#000000", zorder=2, linewidth=1),
        kwargs_params=dict(color="#ffffff", fontsize=10, fontproperties=font_bold.prop),
        kwargs_values=dict(values=values_display, color="#ffffff", fontsize=9, fontproperties=font_normal.prop, bbox=dict(edgecolor="#000000", facecolor="cornflowerblue", boxstyle="round,pad=0.2", lw=1))
    )

    fig.text(0.5, 0.97, f"{player_name} - Radar Individuel", size=16, ha="center", fontproperties=font_bold.prop, color="#ffffff")
    st.pyplot(fig)


def draw_comparison_radar(player1, player2, df):
    p1 = df[df["Joueur"] == player1].iloc[0]
    p2 = df[df["Joueur"] == player2].iloc[0]

    values1 = [p1[f"{col}_percentile"] for col in RAW_STATS.values()]
    values2 = [p2[f"{col}_percentile"] for col in RAW_STATS.values()]

    values1_display = [f"{v}%" for v in values1]
    values2_display = [f"{v}%" for v in values2]

    font_normal = FontManager()
    font_bold = FontManager()

    baker = PyPizza(params=list(RAW_STATS.keys()), background_color="#ffffff")

    fig, ax = baker.make_pizza(
        values1,
        compare_values=values2,
        figsize=(9, 9),
        kwargs_slices=dict(facecolor="#1A78CF", edgecolor="#222222", linewidth=1, zorder=2),
        kwargs_compare=dict(facecolor="#FF9300", edgecolor="#222222", linewidth=1, zorder=2),
        kwargs_params=dict(color="#000000", fontsize=10, fontproperties=font_bold.prop),
        kwargs_values=dict(values=values1_display, color="#000000", fontsize=9, fontproperties=font_normal.prop, bbox=dict(edgecolor="#000000", facecolor="#1A78CF", boxstyle="round,pad=0.2", lw=1)),
        kwargs_compare_values=dict(values=values2_display, color="#000000", fontsize=9, fontproperties=font_normal.prop, bbox=dict(edgecolor="#000000", facecolor="#FF9300", boxstyle="round,pad=0.2", lw=1))
    )

    fig_text(0.5, 0.975, f"< {player1} > vs < {player2} >", size=15, fig=fig,
              highlight_textprops=[{"color": '#1A78CF'}, {"color": '#FF9300'}], ha="center",
              fontproperties=font_bold.prop, color="#000000")

    st.pyplot(fig)

# ---------------------- Streamlit UI ----------------------

def main():
    st.set_page_config(page_title="Radar Stats", layout="wide")
    st.title("📊 Radar de performance des joueurs")

    df = load_and_prepare_data()
    mode = st.radio("Choisissez un mode :", ["Radar individuel", "Radar comparatif"])

    if mode == "Radar individuel":
        player = st.selectbox("Choisissez un joueur :", df["Joueur"].unique())
        draw_individual_radar(player, df)

    elif mode == "Radar comparatif":
        col1, col2 = st.columns(2)
        with col1:
            player1 = st.selectbox("Joueur 1", df["Joueur"].unique(), key="p1")
        with col2:
            player2 = st.selectbox("Joueur 2", df["Joueur"].unique(), key="p2")

        if player1 != player2:
            draw_comparison_radar(player1, player2, df)
        else:
            st.warning("Veuillez choisir deux joueurs différents pour la comparaison.")

if __name__ == "__main__":
    main()
