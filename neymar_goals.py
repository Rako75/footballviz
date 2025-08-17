# streamlit_app.py
# -------------------------------------------------------------
# Application: Neymar JR — Visualisation interactive des buts (LaLiga)
# Auteur: (généré)
# Description:
#   - Affichage d'un terrain vertical (Plotly) avec les buts cliquables
#   - Lecture vidéo (.mp4/.mov) associée à chaque but (colonne `video_but`)
#   - Filtres: Saison, Adversaire, Partie du corps, Passeurs
#   - Disposition: terrain à gauche, vidéo à droite
#   - Compatible GitHub / Streamlit Cloud (placer les vidéos dans ./Neymar_LaLiga_Buts/)
# -------------------------------------------------------------

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

# Pour la capture des clics Plotly
from streamlit_plotly_events import plotly_events
import plotly.graph_objects as go

# -----------------------------
# CONFIG & STYLES
# -----------------------------
st.set_page_config(
    page_title="Buts de Neymar (FC Barcelona) — LaLiga",
    page_icon="⚽",
    layout="wide"
)

CUSTOM_CSS = """
<style>
/* Hide Streamlit default footer */
footer {visibility: hidden;}
/* App header styling */
.app-title { 
  font-weight: 800; 
  font-size: 1.6rem;
  letter-spacing: 0.2px;
}
.subtle {
  color: rgba(0,0,0,0.6);
  font-size: 0.9rem;
}
.stat-badge {
  display: inline-block;
  padding: 6px 10px;
  border-radius: 999px;
  background: #f3f4f6;
  margin-right: 8px;
  font-weight: 600;
  font-size: 0.85rem;
}
.sidebar-note {
  font-size: 0.82rem;
  color: rgba(0,0,0,0.65);
}
.video-card {
  border-radius: 14px; 
  background: #ffffff;
  padding: 16px; 
  box-shadow: 0 10px 25px rgba(0,0,0,0.06);
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------
# DATA LOADING
# -----------------------------
@st.cache_data(show_spinner=False)
def load_data(csv_path: str) -> pd.DataFrame:
    # Supporte les CSV avec ; et encodage latin
    try:
        df = pd.read_csv(csv_path, sep=";", encoding="ISO-8859-1")
    except Exception:
        df = pd.read_csv(csv_path, sep=";")
    # Normalisation colonnes attendues
    expected_cols = ['id','minute','X','Y','xG','h_a','situation','season',
                     'shotType','h_team','a_team','h_goals','a_goals','date',
                     'player_assisted','video_but']
    # Si les colonnes ne correspondent pas, on essaie un fallback léger
    missing = [c for c in expected_cols if c not in df.columns]
    if missing:
        # Ne fait que renommer à la marge si possible (sécurité)
        pass
    # Opposant en fonction du domicile/extérieur de Barcelone
    # Hypothèse: le dataset ne contient que les buts de Neymar pour le Barça
    df["opponent"] = np.where(df["h_a"].astype(str).str.lower().str.startswith("h"),
                              df["a_team"], df["h_team"])
    # Nettoyage des chemins vidéo (aucun traitement de nom — déjà exacts selon l'énoncé)
    df["video_but"] = df["video_but"].astype(str).str.strip()
    # Tri par date si possible
    try:
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")
    except Exception:
        pass
    return df

CSV_PATH = "Neymar_Buts_LaLiga.csv"  # placé à la racine du repo
VIDEOS_DIR = Path("Neymar_LaLiga_Buts")  # dossier des vidéos

df = load_data(CSV_PATH)

# -----------------------------
# SIDEBAR — Filtres
# -----------------------------
st.sidebar.header("🎛️ Filtres")
st.sidebar.markdown(
    "<p class='sidebar-note'>Affinez les buts de Neymar par saison, adversaire, partie du corps et passeur.</p>",
    unsafe_allow_html=True,
)

seasons = sorted(df["season"].dropna().unique().tolist())
opponents = sorted(df["opponent"].dropna().unique().tolist())
body_parts = sorted(df["shotType"].dropna().unique().tolist())
assisters = sorted(df["player_assisted"].fillna("Sans passeur").unique().tolist())

sel_seasons = st.sidebar.multiselect("Saison", seasons, default=seasons)
sel_opponents = st.sidebar.multiselect("Adversaire", opponents, default=opponents)
sel_body = st.sidebar.multiselect("Partie du corps", body_parts, default=body_parts)
sel_assister = st.sidebar.multiselect("Passeur", assisters, default=assisters)

autoplay = st.sidebar.toggle("Lecture auto", value=True)
mute = st.sidebar.toggle("Muet", value=False)

# Appliquer filtres
mask = (
    df["season"].isin(sel_seasons) &
    df["opponent"].isin(sel_opponents) &
    df["shotType"].isin(sel_body) &
    df["player_assisted"].fillna("Sans passeur").isin(sel_assister)
)
filtered = df.loc[mask].copy()

# -----------------------------
# HEADER
# -----------------------------
total_goals = len(df)
filtered_goals = len(filtered)

colh1, colh2 = st.columns([0.75, 0.25])
with colh1:
    st.markdown("<div class='app-title'>⚽ Neymar JR — Buts LaLiga (FC Barcelona)</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtle'>Cliquez sur un point sur le terrain pour afficher la vidéo correspondante.</div>", unsafe_allow_html=True)
with colh2:
    st.markdown(
        f"<span class='stat-badge'>Total: {total_goals}</span>"
        f"<span class='stat-badge'>Après filtres: {filtered_goals}</span>",
        unsafe_allow_html=True
    )

st.divider()

# -----------------------------
# FONCTIONS PLOTLY — Terrain vertical et points
# -----------------------------
def make_vertical_pitch():
    # Pitch standard 120x80 ramené à 100x100 (coordonnées du CSV semblent en 0-100)
    # On affiche vertical: axe Y = longueur (0 -> 100 vers le haut), axe X = largeur (0 -> 100)
    fig = go.Figure()
    # Herbe
    fig.add_shape(type="rect", x0=0, y0=0, x1=100, y1=100, line=dict(color="#2c7a7b"), fillcolor="#e8f5e9", layer="below")
    # Lignes
    line_color = "#1f2937"
    lw = 2
    # Bords
    fig.add_shape(type="rect", x0=0, y0=0, x1=100, y1=100, line=dict(color=line_color, width=lw), fillcolor="rgba(0,0,0,0)")
    # Surface de réparation bas (défense) — côté 0
    fig.add_shape(type="rect", x0=18, y0=0, x1=82, y1=18, line=dict(color=line_color, width=lw))
    # Surface haute (attaque) — côté 100
    fig.add_shape(type="rect", x0=18, y0=82, x1=82, y1=100, line=dict(color=line_color, width=lw))
    # Zone de but
    fig.add_shape(type="rect", x0=36, y0=0, x1=64, y1=6, line=dict(color=line_color, width=lw))
    fig.add_shape(type="rect", x0=36, y0=94, x1=64, y1=100, line=dict(color=line_color, width=lw))
    # Surface centrale
    fig.add_shape(type="line", x0=0, y0=50, x1=100, y1=50, line=dict(color=line_color, width=lw))
    fig.add_shape(type="circle", x0=40, y0=40, x1=60, y1=60, line=dict(color=line_color, width=lw))
    # Points de penalty
    fig.add_trace(go.Scatter(
        x=[50, 50], y=[12, 88], mode="markers",
        marker=dict(size=6, symbol="x"),
        hoverinfo="skip",
        showlegend=False
    ))
    fig.update_xaxes(visible=False, range=[-2, 102])
    fig.update_yaxes(visible=False, range=[-2, 102], scaleanchor="x", scaleratio=1)
    fig.update_layout(
        margin=dict(l=10,r=10,t=10,b=10),
        height=700,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff"
    )
    return fig

def add_goals_scatter(fig, dff):
    # On suppose X = longueur (0-100), Y = largeur (0-100)
    # Pour un affichage vertical (but adverse en haut), on place y = X, x = Y
    custom = np.stack([
        dff.index.values,
        dff["season"].astype(str).values,
        dff["opponent"].astype(str).values,
        dff["minute"].astype(str).values,
        dff["shotType"].astype(str).values,
        dff["player_assisted"].fillna("Sans passeur").astype(str).values,
        dff["xG"].astype(float).round(3).astype(str).values,
        dff["date"].astype(str).values,
        dff["video_but"].astype(str).values
    ], axis=1)

    fig.add_trace(go.Scatter(
        x=dff["Y"], y=dff["X"],
        mode="markers",
        marker=dict(size=14, line=dict(width=1), symbol="circle-open"),
        hovertemplate=(
            "<b>%{customdata[1]}</b> — vs %{customdata[2]}<br>"
            "Minute: %{customdata[3]}<br>"
            "Type: %{customdata[4]}<br>"
            "Passeur: %{customdata[5]}<br>"
            "xG: %{customdata[6]}<br>"
            "Date: %{customdata[7]}<extra></extra>"
        ),
        customdata=custom,
        name="Buts"
    ))
    return fig

# -----------------------------
# LAYOUT PRINCIPAL
# -----------------------------
left, right = st.columns([1.1, 1])

with left:
    fig = make_vertical_pitch()
    fig = add_goals_scatter(fig, filtered)
    click_result = plotly_events(fig, click_event=True, hover_event=False, select_event=False, override_height=700, override_width="100%")

with right:
    st.markdown("### 🎬 Vidéo du but")
    if filtered.empty:
        st.info("Aucun but ne correspond aux filtres sélectionnés.")
    else:
        # Déterminer l'élément sélectionné
        selected_row = None
        if click_result:
            # click_result est une liste de dicts ; on récupère l'index via customdata[0]
            point = click_result[0]
            # plotly_events renvoie customdata dans point["customdata"]
            try:
                idx = int(point["customdata"][0])
                selected_row = filtered.loc[idx]
            except Exception:
                selected_row = filtered.iloc[-1]
        else:
            # par défaut: le plus récent du filtre
            try:
                selected_row = filtered.sort_values("date").iloc[-1]
            except Exception:
                selected_row = filtered.iloc[-1]
        
        if selected_row is not None:
            meta_cols = st.columns(2)
            with meta_cols[0]:
                st.caption("Contexte")
                st.write(f"**Saison:** {selected_row['season']}")
                st.write(f"**Adversaire:** {selected_row['opponent']}")
                st.write(f"**Minute:** {selected_row['minute']}")
                st.write(f"**xG:** {round(float(selected_row['xG']),3) if pd.notna(selected_row['xG']) else '—'}")
            with meta_cols[1]:
                st.caption("Détails")
                st.write(f\"\"\"**Type:** {selected_row['shotType']}  
**Passeur:** {selected_row['player_assisted'] if pd.notna(selected_row['player_assisted']) else 'Sans passeur'}  
**Date:** {selected_row['date']}\"\"\")
            
            st.markdown("<div class='video-card'>", unsafe_allow_html=True)
            video_file = (VIDEOS_DIR / str(selected_row["video_but"])).as_posix()
            # Streamlit gère mp4/mov
            st.video(video_file, autoplay=autoplay, muted=mute)
            st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# NOTE D'UTILISATION
# -----------------------------
with st.expander("ℹ️ Guide rapide"):
    st.markdown(
        """
        - **Cliquez** sur un point sur le terrain pour **ouvrir la vidéo** du but correspondant.
        - Utilisez les filtres à gauche pour **affiner par saison, adversaire, partie du corps** (pied gauche/droit, tête, etc.) et **passeur**.
        - Assurez-vous que vos vidéos sont placées dans le dossier **`Neymar_LaLiga_Buts/`** à la racine du projet, et que les **noms correspondent exactement** à la colonne `video_but` du CSV.
        - La colonne `X`/`Y` est interprétée comme des coordonnées **0–100** (longueur/largeur). L'orientation est **verticale** (le but adverse en haut).
        """
    )
