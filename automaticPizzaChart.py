import streamlit as st
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import pandas as pd
import openpyxl
import unicodedata
from mplsoccer import PyPizza, FontManager, add_image
from PIL import Image, ImageDraw, ImageOps
import matplotlib.pyplot as plt
import io

st.set_page_config(layout="wide")

@st.cache_data
def getReports():
    url = 'https://fbref.com/en/comps/12/stats/La-Liga-Stats'
    html = urlopen(url)
    bs = BeautifulSoup(html, 'html.parser')
    usable_bs = str(bs).replace("<!--", "").replace("-->", "")
    bs3 = BeautifulSoup(usable_bs, 'html.parser')
    table_contents = bs3.find_all('table')

    data = []
    for content in table_contents:
        links = content.find_all('a', href=re.compile(r"^/en/players/[a-f0-9]{8}/[A-Za-z0-9-]+$"))
        for link in links:
            name = link.text.strip().lower().replace('-', ' ')
            href = link['href']
            data.append((name, href))
    
    df = pd.DataFrame(data, columns=["Name", "Link"])
    df["Name"] = df["Link"].apply(lambda x: x.split('/')[-1].replace('-', ' ').lower())
    df.drop_duplicates(subset='Name', keep='first', inplace=True)
    return df

@st.cache_data
def link_generator(df, player_name):
    matches = df[df['Name'].str.lower() == player_name.lower()]
    if not matches.empty:
        return matches.iloc[0]['Link']
    else:
        st.error("Nom du joueur introuvable.")
        st.stop()

@st.cache_data
def get_players_data(df, player_name):
    stat_keys = []
    stat_values = []

    link_to_player_profile = link_generator(df, player_name)
    html = urlopen("https://fbref.com" + link_to_player_profile)
    bs = BeautifulSoup(html, 'html.parser')

    player_image_url = bs.find('div', {'class': 'media-item'}).find('img')['src']
    scout_link = bs.find('div', {'class': 'section_heading_text'}).find('a')['href']

    scout_html = urlopen("https://fbref.com" + scout_link)
    bs_scout = BeautifulSoup(scout_html, 'html.parser')
    table = bs_scout.find("table", {'id': re.compile(r'scout_full_')})

    for row in table.find_all('tr'):
        th = row.find('th')
        tds = row.find_all('td')
        if th and tds and len(tds) > 1:
            stat_keys.append(th.text.strip())
            stat_values.append(tds[1].text.strip())

    return stat_keys, stat_values, player_image_url

def show_picture(params, values, name_of_player, img_url):
    font_normal = FontManager()
    font_bold = FontManager()
    image = Image.open(urlopen(img_url))

    # Circular crop
    mask = Image.new('L', image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + image.size, fill=255)
    masked_img = ImageOps.fit(image, mask.size, centering=(0.5, 0.5))
    masked_img.putalpha(mask)

    slice_colors = ["#bbEE90"] * 5 + ["#FF93ff"] * 5 + ["#FFCCCB"] * 5 + ["#87CEEB"] * 5
    text_colors = ["#000000"] * 20

    baker = PyPizza(
        params=params,
        background_color="#000000",  # Fond noir
        straight_line_color="#ffffff",
        straight_line_lw=1,
        last_circle_color="#ffffff",
        last_circle_lw=1,
        other_circle_lw=0,
        inner_circle_size=11
    )

    fig, ax = baker.make_pizza(
        values,
        figsize=(10, 12),
        color_blank_space="same",
        slice_colors=slice_colors,
        value_colors=text_colors,
        value_bck_colors=slice_colors,
        blank_alpha=0.4,
        kwargs_slices=dict(edgecolor="#ffffff", zorder=2, linewidth=1),
        kwargs_params=dict(color="#ffffff", fontsize=13, fontproperties=font_bold.prop, va="center"),
        kwargs_values=dict(color="#ffffff", fontsize=11, fontproperties=font_normal.prop, zorder=3,
                           bbox=dict(edgecolor="#ffffff", facecolor="#222222", boxstyle="round,pad=0.2", lw=1))
    )

    fig.patch.set_facecolor('black')  # Fond noir pour toute la figure

    fig.text(0.515, 0.945, name_of_player.title(), size=27,
             ha="center", fontproperties=font_bold.prop, color="#ffffff")

    fig.text(0.515, 0.925,
             "Percentile Rank vs Top-Five League Players (last 365 days)",
             size=13, ha="center", fontproperties=font_bold.prop, color="#bbbbbb")

    add_image(masked_img, fig, left=0.472, bottom=0.457, width=0.086, height=0.08, zorder=-1)

    buf = io.BytesIO()
    plt.savefig(buf, format="png", facecolor=fig.get_facecolor(), bbox_inches="tight")
    buf.seek(0)
    return buf



# ==== STREAMLIT UI ====

st.title("📊 Visualisation Radar des Joueurs (La Liga - FBref)")
df = getReports()

with st.sidebar:
    st.subheader("Sélection du joueur")
    player_list = df['Name'].sort_values().unique()
    selected_player = st.selectbox("Choisissez un joueur", player_list)

if selected_player:
    with st.spinner("Chargement des données du joueur..."):
        keys, values, img_url = get_players_data(df, selected_player)

        selected_stats = ['Non-Penalty Goals', 'Assists', 'Goals + Assists', 'Yellow Cards', 'Red Cards',
                          'Passes Attempted', 'Pass Completion %', 'Progressive Passes', 'Through Balls', 'Key Passes',
                          'Touches', 'Take-Ons Attempted', 'Successful Take-Ons', 'Miscontrols', 'Dispossessed',
                          'Tackles', 'Tackles Won', 'Shots Blocked', 'Interceptions', 'Clearances']

        params = ['Non-Penalty\nGoals', 'Assists', 'Goals +\nAssists', 'Yellow\nCards', 'Red\nCards',
                  'Passes\nAttempted', 'Pass\nCompletion %', 'Progressive\nPasses', 'Through\nBalls', 'Key\nPasses',
                  'Touches', 'Take-Ons\nAttempted', 'Successful\nTake-Ons', 'Miscontrols', 'Dispossessed',
                  'Tackles', 'Tackles\nWon', 'Shots\nBlocked', 'Interceptions', 'Clearances']

        values_dict = dict(zip(keys, values))
        plot_values = []
        for stat in selected_stats:
            val = values_dict.get(stat, "0").replace("%", "").strip()
            try:
                plot_values.append(float(val))
            except:
                plot_values.append(0)

        img = show_picture(params, plot_values, selected_player, img_url)
        st.image(img, caption=f"Radar chart de {selected_player.title()}", use_column_width=True)
