import streamlit as st
import pandas as pd
import os
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import openpyxl
from mplsoccer import PyPizza
from highlight_text import fig_text
import matplotlib.pyplot as plt
import wikipedia
import requests
from PIL import Image
from io import BytesIO

# Mapping des ligues
LEAGUE_URLS = {
    "La Liga": "https://fbref.com/en/comps/12/stats/La-Liga-Stats",
    "Serie A": "https://fbref.com/en/comps/11/stats/Serie-A-Stats",
    "Bundesliga": "https://fbref.com/en/comps/20/stats/Bundesliga-Stats",
    "Ligue 1": "https://fbref.com/en/comps/13/stats/Ligue-1-Stats",
    "Premier League": "https://fbref.com/en/comps/9/stats/Premier-League-Stats"
}

@st.cache_data(show_spinner=False)
def getReports(url, league_name):
    html = urlopen(url)
    bs = BeautifulSoup(html, 'html.parser')
    usable_bs = str(bs).replace("<!--", "").replace("-->", "")
    bs_clean = BeautifulSoup(usable_bs, 'html.parser')
    table_contents = bs_clean.find_all('table')

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.append(["Name", "Link"])

    for content in table_contents:
        links = content.find_all('a', href=re.compile(r"^/en/players/[a-f0-9]{8}/[A-Za-z0-9-]+$"))
        for link in links:
            name = link.text.strip().lower().replace('-', ' ')
            href = link['href']
            sheet.append([name, href])

    path = f'player_profiles_{league_name.replace(" ", "_")}.xlsx'
    workbook.save(path)
    return path

def name_updater(path):
    df = pd.read_excel(path)

    for i in range(len(df)):
        if isinstance(df.loc[i, 'Link'], str):
            name_from_url = df.loc[i, 'Link'].split('/')[-1].replace('-', ' ').lower()
            df.loc[i, 'Name'] = name_from_url

    df.drop_duplicates(subset='Name', keep='first', inplace=True)
    df.to_excel(path, index=False)
    return df

def load_profiles(selected_leagues):
    all_profiles = []
    for league in selected_leagues:
        path = f'player_profiles_{league.replace(" ", "_")}.xlsx'
        if not os.path.exists(path):
            getReports(LEAGUE_URLS[league], league)
            name_updater(path)
        df = pd.read_excel(path)
        df['League'] = league
        all_profiles.append(df)
    return pd.concat(all_profiles, ignore_index=True)

def link_generator(player_name, df):
    matches = df[df['Name'].str.lower() == player_name.lower()]
    if not matches.empty:
        return matches.iloc[0]['Link']
    else:
        raise ValueError(f"Nom du joueur introuvable : {player_name}")

def get_players_data(player_name, df):
    link_to_player_profile = link_generator(player_name, df)
    html = urlopen("https://fbref.com" + link_to_player_profile)
    bs = BeautifulSoup(html, 'html.parser')

    scout_link = bs.find('div', {'class': 'section_heading_text'}).find('a')['href']
    scout_html = urlopen("https://fbref.com" + scout_link)
    bs_scout_all = BeautifulSoup(scout_html, 'html.parser')
    bs_scout = bs_scout_all.find('div', {'id': re.compile(r'div_scout_full_')})
    table = bs_scout.find("table", {'id': re.compile(r'scout_full_')})

    stat_keys, stat_values = [], []
    for row in table.find_all('tr'):
        th = row.find('th')
        tds = row.find_all('td')
        if th and tds and len(tds) > 1:
            stat_keys.append(th.text.strip())
            stat_values.append(tds[1].text.strip())

    return stat_keys, stat_values

@st.cache_data
def get_player_image(player_name):
    try:
        page = wikipedia.page(player_name)
        for img_url in page.images:
            if any(img_url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png']):
                try:
                    response = requests.get(img_url, timeout=5)
                    if response.status_code == 200 and 'image' in response.headers['Content-Type']:
                        return img_url
                except:
                    continue
    except:
        pass
    return None

def show_picture(df, selected_stats):
    values = df[selected_stats].values.flatten().tolist()
    player_name = df["Player"].values[0]
    params_offset = [False if "Touches" not in p and "Press" not in p else True for p in selected_stats]

    baker = PyPizza(
        params=selected_stats,
        background_color="#EBEBE9",
        straight_line_color="#222222",
        straight_line_lw=1,
        last_circle_lw=1,
        last_circle_color="#222222",
        other_circle_ls="-.",
        other_circle_lw=1,
    )

    fig, ax = baker.make_pizza(
        values,
        figsize=(10, 10),
        kwargs_slices=dict(facecolor="#1A78CF", edgecolor="#222222", zorder=2, linewidth=1),
        kwargs_params=dict(color="#000000", fontsize=12, va="center"),
        kwargs_values=dict(color="#000000", fontsize=10, zorder=3,
                           bbox=dict(edgecolor="#000000", facecolor="cornflowerblue", boxstyle="round,pad=0.2", lw=1))
    )

    baker.adjust_texts(params_offset, offset=-0.10)

    fig_text(0.515, 0.99, f"<{player_name}>", size=17, fig=fig,
             highlight_textprops=[{"color": '#1A78CF'}],
             ha="center", color="#000000")

    fig.text(0.515, 0.942, "Radar individuel — Stats normalisées (percentiles)",
             size=15, ha="center", color="#000000")

    fig.text(0.99, 0.005, "Données : FBRef/Opta\nGraphique inspiré de @Worville & @FootballSlices",
             size=9, ha="right", color="#000000")

    st.pyplot(fig)

def show_comparison_picture(df1, df2, selected_stats):
    values_1 = df1[selected_stats].values.flatten().tolist()
    values_2 = df2[selected_stats].values.flatten().tolist()
    player_1 = df1["Player"].values[0]
    player_2 = df2["Player"].values[0]
    params_offset = [False] * len(selected_stats)

    baker = PyPizza(
        params=selected_stats,
        background_color="#EBEBE9",
        straight_line_color="#222222",
        straight_line_lw=1,
        last_circle_lw=1,
        last_circle_color="#222222",
        other_circle_ls="-.",
        other_circle_lw=1,
    )

    fig, ax = baker.make_pizza(
        values_1,
        compare_values=values_2,
        figsize=(10, 10),
        kwargs_slices=dict(facecolor="#1A78CF", edgecolor="#222222", linewidth=1, zorder=2),
        kwargs_compare=dict(facecolor="#FF9300", edgecolor="#222222", linewidth=1, zorder=2),
        kwargs_params=dict(color="#000000", fontsize=11, va="center"),
        kwargs_values=dict(color="#000000", fontsize=10, zorder=3,
                           bbox=dict(edgecolor="#000000", facecolor="cornflowerblue", boxstyle="round,pad=0.2", lw=1)),
        kwargs_compare_values=dict(color="#000000", fontsize=10, zorder=3,
                                   bbox=dict(edgecolor="#000000", facecolor="#FF9300", boxstyle="round,pad=0.2", lw=1))
    )

    baker.adjust_texts(params_offset, offset=4.15, adj_comp_values=True)

    fig_text(0.515, 0.99, f"<{player_1}> vs <{player_2}>", size=17, fig=fig,
             highlight_textprops=[{"color": '#1A78CF'}, {"color": '#FF9300'}],
             ha="center", color="#000000")

    fig.text(0.515, 0.942, "Radar comparatif — Stats (percentiles)",
             size=15, ha="center", color="#000000")

    fig.text(0.99, 0.005, "Données : FBRef/Opta\nGraphique inspiré de @Worville & @FootballSlices",
             size=9, ha="right", color="#000000")

    st.pyplot(fig)

# Interface Streamlit
st.set_page_config(page_title="Radar FBRef", layout="centered")
st.title("🎯 Radar Player - Comparateur FBRef")

selected_leagues = st.multiselect("Choisissez une ou deux ligues", list(LEAGUE_URLS.keys()), max_selections=2)

if selected_leagues:
    df_profiles = load_profiles(selected_leagues)
    all_players = sorted(df_profiles['Name'].unique().tolist())














    col1, col2 = st.columns(2)
    with col1:
        player1 = st.selectbox("🎯 Joueur 1", all_players)
    with col2:
        player2 = st.selectbox("🔁 Joueur 2", all_players)

    # Affichage des images
    if player1:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(player1.title())
            img1_url = get_player_image(player1.title())
            if img1_url:
                response1 = requests.get(img1_url)
                img1 = Image.open(BytesIO(response1.content))
                st.image(img1, width=150)
            else:
                st.text("Image non trouvée")























        if player2:
            with col2:
                st.subheader(player2.title())
                img2_url = get_player_image(player2.title())
                if img2_url:
                    response2 = requests.get(img2_url)
                    img2 = Image.open(BytesIO(response2.content))
                    st.image(img2, width=150)
                else:
                    st.text("Image non trouvée")

    selected_stats = ['Non-Penalty Goals', 'Assists', 'Goals + Assists', 'Yellow Cards', 'Red Cards',
                      'Passes Attempted', 'Pass Completion %', 'Progressive Passes', 'Through Balls', 'Key Passes',
                      'Touches', 'Take-Ons Attempted', 'Successful Take-Ons', 'Miscontrols', 'Dispossessed',
                      'Tackles', 'Tackles Won', 'Shots Blocked', 'Interceptions', 'Clearances']

    radar_labels = ['Non-Penalty\nGoals', 'Assists', 'Goals +\nAssists', 'Yellow\nCards', 'Red\nCards',
                    'Passes\nAttempted', 'Pass\nCompletion %', 'Progressive\nPasses', 'Through\nBalls', 'Key\nPasses',
                    'Touches', 'Take-Ons\nAttempted', 'Successful\nTake-Ons', 'Miscontrols', 'Dispossessed',
                    'Tackles', 'Tackles\nWon', 'Shots\nBlocked', 'Interceptions', 'Clearances']

    if player1:
        try:
            keys1, values1 = get_players_data(player1, df_profiles)
            stats1 = dict(zip(keys1, values1))
            data1 = [float(stats1.get(s, "0").replace("%", "").strip() or 0) for s in selected_stats]
            df1 = pd.DataFrame([data1], columns=radar_labels)
            df1["Player"] = player1.title()

            if player2:
                keys2, values2 = get_players_data(player2, df_profiles)
                stats2 = dict(zip(keys2, values2))
                data2 = [float(stats2.get(s, "0").replace("%", "").strip() or 0) for s in selected_stats]
                df2 = pd.DataFrame([data2], columns=radar_labels)
                df2["Player"] = player2.title()
                show_comparison_picture(df1, df2, radar_labels)
            else:
                show_picture(df1, radar_labels)

        except Exception as e:
            st.error(f"Erreur lors de la génération du radar : {e}")
