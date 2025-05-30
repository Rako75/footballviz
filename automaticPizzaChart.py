import streamlit as st
import pandas as pd
import os
import re
import time
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import openpyxl
from mplsoccer import PyPizza
from highlight_text import fig_text
import matplotlib.pyplot as plt

# Mapping des ligues
LEAGUE_URLS = {
    "La Liga": "https://fbref.com/en/comps/12/stats/La-Liga-Stats",
    "Serie A": "https://fbref.com/en/comps/11/stats/Serie-A-Stats",
    "Bundesliga": "https://fbref.com/en/comps/20/stats/Bundesliga-Stats",
    "Ligue 1": "https://fbref.com/en/comps/13/stats/Ligue-1-Stats",
    "Premier League": "https://fbref.com/en/comps/9/stats/Premier-League-Stats"
}

# Télécharger les profils une seule fois
def scrape_all_profiles():
    os.makedirs("profiles", exist_ok=True)
    all_rows = []
    headers = {"User-Agent": "Mozilla/5.0"}

    for league, url in LEAGUE_URLS.items():
        print(f"Scraping {league}")
        req = Request(url, headers=headers)
        html = urlopen(req).read()
        time.sleep(1)

        soup = BeautifulSoup(html, "html.parser")
        usable_html = str(soup).replace("<!--", "").replace("-->", "")
        bs_clean = BeautifulSoup(usable_html, 'html.parser')

        tables = bs_clean.find_all("table")
        for table in tables:
            links = table.find_all('a', href=re.compile(r"^/en/players/[a-f0-9]{8}/[A-Za-z0-9-]+$"))
            for link in links:
                name = link.text.strip().lower()
                href = link['href']
                all_rows.append([name, href, league])

    df = pd.DataFrame(all_rows, columns=["Name", "Link", "League"])
    df.drop_duplicates(subset=["Name", "League"], inplace=True)
    df.to_excel("profiles/all_profiles.xlsx", index=False)
    print("✅ Fichier créé avec succès.")

@st.cache_data
def load_profiles():
    if not os.path.exists("profiles/all_profiles.xlsx"):
        scrape_all_profiles()
    return pd.read_excel("profiles/all_profiles.xlsx")

def get_players_data(link_suffix):
    try:
        url = "https://fbref.com" + link_suffix
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        html = urlopen(req).read()
        soup = BeautifulSoup(html, 'html.parser')
        scout_link = soup.find('div', class_="section_heading_text").find('a')['href']

        time.sleep(1)
        scout_url = "https://fbref.com" + scout_link
        scout_html = urlopen(Request(scout_url, headers={"User-Agent": "Mozilla/5.0"})).read()
        scout_soup = BeautifulSoup(scout_html, 'html.parser')

        table = scout_soup.find("div", id=re.compile(r"div_scout_full_")).find("table")

        stat_keys, stat_values = [], []
        for row in table.find_all('tr'):
            th = row.find('th')
            tds = row.find_all('td')
            if th and tds and len(tds) > 1:
                stat_keys.append(th.text.strip())
                stat_values.append(tds[1].text.strip())

        return stat_keys, stat_values
    except Exception as e:
        raise RuntimeError(f"Erreur lors du chargement des stats : {e}")

def show_radar(df, labels):
    values = df[labels].values.flatten().tolist()
    name = df["Player"].values[0]

    baker = PyPizza(params=labels, background_color="#EBEBE9", straight_line_color="#222222")
    fig, ax = baker.make_pizza(
        values, figsize=(10, 10),
        kwargs_slices=dict(facecolor="#1A78CF", edgecolor="#222222"),
        kwargs_params=dict(color="#000000", fontsize=12),
        kwargs_values=dict(color="#000000", fontsize=10,
                           bbox=dict(edgecolor="#000", facecolor="cornflowerblue", boxstyle="round,pad=0.2"))
    )
    fig_text(0.515, 0.99, f"<{name.title()}>", size=17, fig=fig, ha="center", color="#000")
    st.pyplot(fig)

def show_comparison(df1, df2, labels):
    values1 = df1[labels].values.flatten().tolist()
    values2 = df2[labels].values.flatten().tolist()
    name1, name2 = df1["Player"].values[0], df2["Player"].values[0]

    baker = PyPizza(params=labels, background_color="#EBEBE9", straight_line_color="#222222")
    fig, ax = baker.make_pizza(
        values1, compare_values=values2, figsize=(10, 10),
        kwargs_slices=dict(facecolor="#1A78CF", edgecolor="#222222"),
        kwargs_compare=dict(facecolor="#FF9300", edgecolor="#222222"),
        kwargs_params=dict(color="#000000", fontsize=12),
        kwargs_values=dict(color="#000000", fontsize=10,
                           bbox=dict(edgecolor="#000", facecolor="cornflowerblue", boxstyle="round,pad=0.2")),
        kwargs_compare_values=dict(color="#000000", fontsize=10,
                                   bbox=dict(edgecolor="#000", facecolor="#FF9300", boxstyle="round,pad=0.2"))
    )
    fig_text(0.515, 0.99, f"<{name1.title()}> vs <{name2.title()}>", size=17, fig=fig, ha="center", color="#000")
    st.pyplot(fig)

# Statistiques à utiliser
stats = ['Non-Penalty Goals', 'Assists', 'Goals + Assists', 'Yellow Cards', 'Red Cards',
         'Passes Attempted', 'Pass Completion %', 'Progressive Passes', 'Through Balls', 'Key Passes',
         'Touches', 'Take-Ons Attempted', 'Successful Take-Ons', 'Miscontrols', 'Dispossessed',
         'Tackles', 'Tackles Won', 'Shots Blocked', 'Interceptions', 'Clearances']
labels = ['Non-Penalty\nGoals', 'Assists', 'Goals +\nAssists', 'Yellow\nCards', 'Red\nCards',
          'Passes\nAttempted', 'Pass\nCompletion %', 'Progressive\nPasses', 'Through\nBalls', 'Key\nPasses',
          'Touches', 'Take-Ons\nAttempted', 'Successful\nTake-Ons', 'Miscontrols', 'Dispossessed',
          'Tackles', 'Tackles\nWon', 'Shots\nBlocked', 'Interceptions', 'Clearances']

# Interface Streamlit
st.set_page_config(page_title="Radar FBRef", layout="centered")
st.title("🎯 Comparateur de joueurs - Top 5 ligues")

df_profiles = load_profiles()
selected_league = st.selectbox("Sélectionnez une ligue", sorted(df_profiles['League'].unique()))
filtered_players = df_profiles[df_profiles["League"] == selected_league]

player1 = st.selectbox("Joueur principal", filtered_players["Name"].unique())
compare_mode = st.checkbox("Comparer avec un second joueur")

if compare_mode:
    player2 = st.selectbox("Joueur à comparer", df_profiles["Name"].unique())
    if st.button("Générer le radar"):
        try:
            l1 = df_profiles[df_profiles["Name"] == player1]["Link"].values[0]
            l2 = df_profiles[df_profiles["Name"] == player2]["Link"].values[0]

            keys1, vals1 = get_players_data(l1)
            d1 = dict(zip(keys1, vals1))
            stats1 = [float(d1.get(s, "0").replace("%", "").strip() or 0) for s in stats]
            df1 = pd.DataFrame([stats1], columns=labels)
            df1["Player"] = player1

            keys2, vals2 = get_players_data(l2)
            d2 = dict(zip(keys2, vals2))
            stats2 = [float(d2.get(s, "0").replace("%", "").strip() or 0) for s in stats]
            df2 = pd.DataFrame([stats2], columns=labels)
            df2["Player"] = player2

            show_comparison(df1, df2, labels)
        except Exception as e:
            st.error(e)
else:
    if st.button("Générer le radar"):
        try:
            link = df_profiles[df_profiles["Name"] == player1]["Link"].values[0]
            keys, vals = get_players_data(link)
            d = dict(zip(keys, vals))
            data = [float(d.get(s, "0").replace("%", "").strip() or 0) for s in stats]
            df = pd.DataFrame([data], columns=labels)
            df["Player"] = player1
            show_radar(df, labels)
        except Exception as e:
            st.error(e)
