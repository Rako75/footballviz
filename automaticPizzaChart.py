import streamlit as st
import pandas as pd
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
from mplsoccer import PyPizza
from highlight_text import fig_text
import matplotlib.pyplot as plt

# 📌 Ligues supportées
LEAGUES = {
    "Premier League": "https://fbref.com/en/comps/9/stats/Premier-League-Stats",
    "La Liga": "https://fbref.com/en/comps/12/stats/La-Liga-Stats",
    "Serie A": "https://fbref.com/en/comps/11/stats/Serie-A-Stats",
    "Bundesliga": "https://fbref.com/en/comps/20/stats/Bundesliga-Stats",
    "Ligue 1": "https://fbref.com/en/comps/13/stats/Ligue-1-Stats"
}

# 🎯 Stats ciblées
STATS = [
    "Non-Penalty Goals", "Assists", "Goals + Assists",
    "Passes Attempted", "Pass Completion %", "Key Passes",
    "Touches", "Take-Ons Attempted", "Successful Take-Ons",
    "Tackles", "Interceptions", "Clearances"
]

LABELS = [
    "Non-Penalty\nGoals", "Assists", "Goals +\nAssists",
    "Passes\nAttempted", "Pass\nCompletion %", "Key\nPasses",
    "Touches", "Take-Ons\nAttempted", "Successful\nTake-Ons",
    "Tackles", "Interceptions", "Clearances"
]

# 📥 Fonction pour récupérer tous les joueurs d'une ligue
@st.cache_data
def load_players(league_url):
    html = urlopen(league_url)
    bs = BeautifulSoup(html, 'html.parser')
    usable_html = str(bs).replace("<!--", "").replace("-->", "")
    bs_clean = BeautifulSoup(usable_html, 'html.parser')
    table = bs_clean.find("table")
    rows = table.find("tbody").find_all("tr")

    players = []
    for row in rows:
        name_tag = row.find("th", {"data-stat": "player"})
        if not name_tag:
            continue
        name = name_tag.text.strip()
        href = name_tag.find("a")["href"] if name_tag.find("a") else None
        position = row.find("td", {"data-stat": "position"}).text.strip()
        if href:
            players.append({"name": name, "link": href, "position": position})
    return pd.DataFrame(players)

# 📊 Récupère les stats d’un joueur
def get_player_stats(link):
    html = urlopen("https://fbref.com" + link)
    bs = BeautifulSoup(html, 'html.parser')
    scout_link = bs.find('div', {'class': 'section_heading_text'}).find('a')['href']
    scout_html = urlopen("https://fbref.com" + scout_link)
    scout_bs = BeautifulSoup(scout_html, 'html.parser')
    table_div = scout_bs.find('div', {'id': re.compile(r'div_scout_full_')})
    table = table_div.find("table", {'id': re.compile(r'scout_full_')})

    stats = {}
    for row in table.find_all('tr'):
        th = row.find('th')
        tds = row.find_all('td')
        if th and len(tds) > 1:
            stat = th.text.strip()
            value = tds[1].text.strip().replace("%", "")
            if stat in STATS:
                stats[stat] = float(value) if value else 0
    return stats

# 📈 Radar comparatif
def plot_comparison(player_name, p_stats, avg_stats):
    player_values = [p_stats.get(s, 0) for s in STATS]
    avg_values = [avg_stats.get(s, 0) for s in STATS]

    pizza = PyPizza(params=LABELS, background_color="#EFEFEF", straight_line_color="#222", last_circle_color="#222")

    fig, ax = pizza.make_pizza(
        player_values,
        compare_values=avg_values,
        figsize=(10, 10),
        kwargs_slices=dict(facecolor="#1A78CF", edgecolor="#222", lw=1),
        kwargs_compare=dict(facecolor="#FF9300", edgecolor="#222", lw=1),
        kwargs_params=dict(color="#000", fontsize=10),
        kwargs_values=dict(color="#000", fontsize=9,
                           bbox=dict(facecolor="cornflowerblue", edgecolor="none", boxstyle="round,pad=0.2")),
        kwargs_compare_values=dict(color="#000", fontsize=9,
                                   bbox=dict(facecolor="#FF9300", edgecolor="none", boxstyle="round,pad=0.2")),
    )

    pizza.adjust_texts(offset=[False]*len(STATS), offset_compare=4.2)
    fig_text(0.5, 0.99, f"<{player_name}> vs Moyenne poste", size=16, fig=fig, ha="center",
             highlight_textprops=[{"color": '#1A78CF'}])
    fig.text(0.5, 0.94, "Radar comparatif — Stats normalisées", ha="center", size=13)
    fig.text(0.99, 0.01, "Source : FBRef / Opta", size=9, ha="right")
    st.pyplot(fig)

# 🚀 Interface principale
def main():
    st.title("📊 Radar Football (FBref)")

    league_name = st.selectbox("Sélectionne une ligue :", list(LEAGUES.keys()))
    df_players = load_players(LEAGUES[league_name])

    positions = df_players["position"].unique()
    selected_position = st.selectbox("Choisis une position :", positions)

    players_pos = df_players[df_players["position"] == selected_position]
    selected_player = st.selectbox("Choisis un joueur :", players_pos["name"])

    if st.button("Afficher le radar"):
        player_row = players_pos[players_pos["name"] == selected_player].iloc[0]
        player_stats = get_player_stats(player_row["link"])

        # Moyenne des autres joueurs à la même position
        comp_stats = []
        for _, row in players_pos.iterrows():
            if row["name"] == selected_player:
                continue
            try:
                stats = get_player_stats(row["link"])
                comp_stats.append(stats)
            except:
                continue

        # Moyenne des stats
        avg_stats = {}
        for stat in STATS:
            values = [d[stat] for d in comp_stats if stat in d]
            avg_stats[stat] = sum(values) / len(values) if values else 0

        plot_comparison(selected_player, player_stats, avg_stats)

# 🎬 Lancer app
if __name__ == "__main__":
    main()
