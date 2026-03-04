import streamlit as st
import pandas as pd
import json
import streamlit.components.v1 as components

# Configuration de la page
st.set_page_config(page_title="Dashboard Milieux PL", layout="wide", initial_sidebar_state="expanded")

# --- Données et configurations statiques ---
TEAM_LOGOS = {
    "Arsenal": "https://resources.premierleague.com/premierleague25/badges-alt/3.svg",
    "Aston Villa": "https://resources.premierleague.com/premierleague/badges/t7.svg",
    "Bournemouth": "https://resources.premierleague.com/premierleague/badges/t91.svg",
    "Brentford": "https://resources.premierleague.com/premierleague25/badges-alt/94.svg",
    "Brighton": "https://resources.premierleague.com/premierleague/badges/t36.svg",
    "Burnley": "https://resources.premierleague.com/premierleague/badges/t90.svg",
    "Chelsea": "https://resources.premierleague.com/premierleague25/badges-alt/8.svg",
    "Crystal Palace": "https://resources.premierleague.com/premierleague/badges/t31.svg",
    "Everton": "https://resources.premierleague.com/premierleague/badges/t11.svg",
    "Fulham": "https://resources.premierleague.com/premierleague/badges/t54.svg",
    "Leeds": "https://resources.premierleague.com/premierleague/badges/t2.svg",
    "Liverpool": "https://resources.premierleague.com/premierleague/badges/t14.svg",
    "Man City": "https://resources.premierleague.com/premierleague25/badges-alt/43.svg",
    "Man Utd": "https://resources.premierleague.com/premierleague25/badges-alt/1.svg",
    "Newcastle": "https://resources.premierleague.com/premierleague/badges/t4.svg",
    "Nottingham Forest": "https://resources.premierleague.com/premierleague25/badges-alt/17.svg",
    "Sunderland": "https://resources.premierleague.com/premierleague/badges/t56.svg",
    "Tottenham": "https://resources.premierleague.com/premierleague/badges/t6.svg",
    "West Ham": "https://resources.premierleague.com/premierleague/badges/t21.svg",
    "Wolves": "https://resources.premierleague.com/premierleague/badges/t39.svg"
}

TEAM_COLORS = {
    "Arsenal": "#E20613", "Aston Villa": "#480024", "Bournemouth": "#CE0A17",
    "Brentford": "#C10000", "Brighton": "#0054A5", "Burnley": "#81204C", "Chelsea": "#001489",
    "Crystal Palace": "#EE2E24", "Everton": "#014593", "Fulham": "#000000",
    "Leeds": "#FFD600", "Liverpool": "#D10011", 
    "Man City": "#7AB2E1", "Man Utd": "#B90006", "Newcastle": "#231F20", 
    "Nottingham Forest": "#EB0024", 
    "Sunderland": "#DC0714", "Tottenham": "#000A3C", "West Ham": "#7C2C3B", "Wolves": "#FAB900"
}

DEFAULT_AVATAR = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iIzhCOTQ5RSI+PHBhdGggZD0iTTEyIDEyYzIuMjEgMCA0LTEuNzkgNC00cy0xLjc5LTQtNC00LTQgMS43OS00IDQgMS43OSA0IDQgNHptMCAyYy0yLjY3IDAtOCAxLjM0LTggNHYyaDE2di0yYzAtMi42Ni01LjMzLTQtOC00eiIvPjwvc3ZnPg=="

# Fonction pour calculer la luminance et adapter la couleur du texte
def get_luminance(hex_color):
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3: hex_color = ''.join([c*2 for c in hex_color])
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255

# --- Chargement des données ---
@st.cache_data
def load_data():
    try:
        with open('milieux_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return pd.DataFrame(data['stats'])
    except FileNotFoundError:
        st.warning("Fichier 'milieux_data.json' non trouvé. Utilisation de données de démonstration.")
        # Données de démonstration basées sur votre prompt
        return pd.DataFrame([
            {"name": "Bruno Guimarães", "team": "Newcastle", "Passes_90": 55.1, "Pass_Acc": 83.9, "Prog_Carries_90": 2.3, "Prog_Passes_90": 4.8, "Final_Third_90": 5.6, "Def_Actions_90": 9.1, "player_photo_b64": "https://resources.premierleague.com/premierleague25/photos/players/110x140/208706.png"},
            {"name": "Joelinton", "team": "Newcastle", "Passes_90": 33.8, "Pass_Acc": 83.4, "Prog_Carries_90": 1.2, "Prog_Passes_90": 1.5, "Final_Third_90": 3.0, "Def_Actions_90": 9.4, "player_photo_b64": "https://resources.premierleague.com/premierleague25/photos/players/110x140/180974.png"},
            {"name": "Alexis Mac Allister", "team": "Liverpool", "Passes_90": 43.1, "Pass_Acc": 85.5, "Prog_Carries_90": 1.9, "Prog_Passes_90": 2.6, "Final_Third_90": 4.0, "Def_Actions_90": 6.4, "player_photo_b64": ""},
            {"name": "Kyle Walker", "team": "Burnley", "Passes_90": 41.3, "Pass_Acc": 66.4, "Prog_Carries_90": 1.1, "Prog_Passes_90": 4.6, "Final_Third_90": 4.1, "Def_Actions_90": 7.0, "player_photo_b64": ""}
        ])

df = load_data()

# --- Composant D3.js encapsulé ---
def render_beeswarm(data_json, metric, xlabel, target_player, text_color, other_color, is_percent=False):
    html_code = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <script src="https://d3js.org/d3.v7.min.js"></script>
        <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            body {{ margin: 0; padding: 0; font-family: 'Montserrat', sans-serif; background-color: transparent; }}
            .x-axis-label {{ font-size: 11px; fill: {text_color}; opacity: 0.9; }}
            .tick text {{ fill: {text_color}; opacity: 0.7; font-size: 10px; font-family: 'Montserrat', sans-serif; }}
            .tick line {{ stroke: {text_color}; opacity: 0.2; stroke-dasharray: 4, 4; }}
            .domain {{ display: block; stroke: {text_color}; opacity: 0.2; }}
            #tooltip {{
                position: absolute; opacity: 0; background: rgba(15, 23, 42, 0.95);
                border: 1px solid rgba(255,255,255,0.2); color: #fff; padding: 8px 12px;
                border-radius: 6px; pointer-events: none; font-size: 0.85rem; transition: opacity 0.2s; z-index: 100;
            }}
            .tt-name {{ font-weight: bold; margin-bottom: 4px; }}
        </style>
    </head>
    <body>
        <div id="chart"></div>
        <div id="tooltip"></div>
        <script>
            const data = {data_json};
            const metric = "{metric}";
            const xlabel = "{xlabel}";
            const targetPlayer = "{target_player}";
            const isPercent = {"true" if is_percent else "false"};
            const textColor = "{text_color}";
            const otherColor = "{other_color}";

            data.forEach(d => d.Is_Target = (d.name === targetPlayer));

            const width = 450;
            const height = 240;
            const margin = {{ top: 30, right: 30, bottom: 40, left: 30 }};
            const innerWidth = width - margin.left - margin.right;
            const innerHeight = height - margin.top - margin.bottom;

            const svg = d3.select("#chart").append("svg")
                .attr("viewBox", `0 0 ${{width}} ${{height}}`)
                .attr("preserveAspectRatio", "xMidYMid meet");

            const g = svg.append("g").attr("transform", `translate(${{margin.left}},${{margin.top}})`);

            const xExtent = d3.extent(data, d => d[metric]);
            const padding = (xExtent[1] - xExtent[0]) * 0.1; 
            const x = d3.scaleLinear().domain([Math.max(0, xExtent[0] - padding), xExtent[1] + padding]).range([0, innerWidth]);

            const xAxis = d3.axisBottom(x).ticks(6).tickSizeInner(-innerHeight - 20).tickSizeOuter(0).tickPadding(10);
            const xAxisGroup = g.append("g").attr("transform", `translate(0, ${{innerHeight}})`).call(xAxis);
            xAxisGroup.selectAll(".tick line").attr("transform", "translate(0, 15)"); 

            g.append("text").attr("class", "x-axis-label").attr("x", innerWidth / 2).attr("y", innerHeight + 35)
                .attr("text-anchor", "middle").text(xlabel);

            const medianVal = d3.median(data, d => d[metric]);
            const medianStr = d3.format(".1f")(medianVal) + (isPercent ? "%" : "");

            g.append("line").attr("x1", x(medianVal)).attr("x2", x(medianVal))
                .attr("y1", -20).attr("y2", innerHeight)
                .attr("stroke", textColor).attr("stroke-width", 1).attr("stroke-dasharray", "5,5").attr("opacity", 0.7);

            g.append("text").attr("x", x(medianVal)).attr("y", -25).attr("text-anchor", "middle")
                .attr("fill", textColor).style("font-size", "9px").style("opacity", 0.9).text(`Médiane: ${{medianStr}}`);

            const simulation = d3.forceSimulation(data)
                .force("x", d3.forceX(d => x(d[metric])).strength(2.5)) 
                .force("y", d3.forceY(innerHeight / 2).strength(0.2)) 
                .force("collide", d3.forceCollide(d => d.Is_Target ? 4.5 : 3.2).iterations(2)).stop();

            for (let i = 0; i < 300; ++i) simulation.tick();

            const tooltip = d3.select("#tooltip");

            const nodes = g.selectAll("circle.point").data(data).enter().append("circle")
                .attr("class", "point").attr("cx", d => d.x).attr("cy", d => d.y)
                .attr("r", d => d.Is_Target ? 4 : 3)
                .attr("fill", d => d.Is_Target ? "#FDE047" : otherColor)
                .attr("opacity", d => d.Is_Target ? 1 : 0.4) 
                .attr("stroke", d => d.Is_Target ? "rgba(0,0,0,0.4)" : "none") 
                .attr("stroke-width", d => d.Is_Target ? 1 : 0);

            nodes.on("mouseover", function(event, d) {{
                d3.select(this).attr("stroke", textColor).attr("stroke-width", 1).attr("opacity", 1);
                tooltip.transition().duration(200).style("opacity", 1);
                const valStr = d3.format(".1f")(d[metric]) + (isPercent ? "%" : "");
                tooltip.html(`<div class="tt-name" style="color: ${{d.Is_Target ? '#FDE047' : '#fff'}}">${{d.name}}</div><div class="tt-val">${{valStr}}</div>`)
                       .style("left", (event.pageX + 10) + "px").style("top", (event.pageY - 28) + "px");
            }}).on("mouseout", function(event, d) {{
                d3.select(this).attr("stroke", d.Is_Target ? "rgba(0,0,0,0.4)" : "none").attr("stroke-width", d.Is_Target ? 1 : 0).attr("opacity", d.Is_Target ? 1 : 0.4);
                tooltip.transition().duration(500).style("opacity", 0);
            }});

            d3.selectAll("circle").filter(d => d && d.Is_Target).raise();
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=270)


# --- Interface Streamlit ---

# Sidebar
st.sidebar.markdown("### ⚙️ Filtres")
teams = sorted(df['team'].unique())
selected_team = st.sidebar.selectbox("CLUB :", ["Tous les clubs..."] + teams)

if selected_team != "Tous les clubs...":
    players = sorted(df[df['team'] == selected_team]['name'].unique())
    selected_player = st.sidebar.selectbox("JOUEUR :", players)
else:
    selected_player = None
    st.sidebar.selectbox("JOUEUR :", ["Sélectionnez d'abord un club"], disabled=True)

# Traitement Principal
if selected_player:
    player_data = df[df['name'] == selected_player].iloc[0]

    # Injection dynamique du fond basé sur la couleur de l'équipe
    bg_color = player_data.get('player_bg_color')
    if not bg_color:
        bg_color = TEAM_COLORS.get(player_data['team'], "#0E1117")

    luminance = get_luminance(bg_color)
    text_color = "#FFFFFF" if luminance < 0.55 else "#000000"
    other_color = "#F8FAFC" if luminance < 0.55 else "#0F172A"

    st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color}; transition: background-color 0.4s ease; }}
    h1, h2, h3, h4, p, span, div {{ color: {text_color} !important; }}
    .block-container {{ padding-top: 2rem; }}
    </style>
    """, unsafe_allow_html=True)

    # Header : Logo, Photo et Informations
    col_logo, col_photo, col_text, col_stats = st.columns([1, 1.5, 6, 3])
    
    with col_logo:
        logo_url = TEAM_LOGOS.get(player_data['team'], player_data.get('team_logo_b64', ''))
        if logo_url: st.image(logo_url, width=80)
            
    with col_photo:
        photo_url = player_data.get('player_photo_b64')
        if not photo_url: photo_url = DEFAULT_AVATAR
        st.image(photo_url, width=120)
            
    with col_text:
        st.markdown(f"<h1 style='margin:0; font-size: 3.2rem; font-weight: 300; text-transform: uppercase;'>{selected_player}</h1>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 1.1rem; opacity:0.8;'>Profil Analytique & Comparaison Sectorielle - Premier League</p>", unsafe_allow_html=True)

    with col_stats:
        st.markdown(f"<h2 style='text-align: right; font-weight: 300; margin: 0;'>{len(df)}</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: right; opacity:0.8;'>Milieux analysés (p90)</p>", unsafe_allow_html=True)

    st.markdown("---")

    # Génération du JSON pour D3
    json_data = df.to_json(orient="records")

    # Grille 3x2 de graphiques Beeswarm
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown(f"<h4 style='font-weight: 300; font-size:1.1rem;'>VOLUME DE JEU</h4>", unsafe_allow_html=True)
        render_beeswarm(json_data, 'Passes_90', 'Passes tentées par match', selected_player, text_color, other_color)
        
        st.markdown(f"<h4 style='font-weight: 300; font-size:1.1rem;'>PASSES PROGRESSIVES</h4>", unsafe_allow_html=True)
        render_beeswarm(json_data, 'Prog_Passes_90', "Passes vers l'avant (>15% terrain)", selected_player, text_color, other_color)

    with c2:
        st.markdown(f"<h4 style='font-weight: 300; font-size:1.1rem;'>SÉCURITÉ TECHNIQUE (%)</h4>", unsafe_allow_html=True)
        render_beeswarm(json_data, 'Pass_Acc', 'Pourcentage de passes réussies', selected_player, text_color, other_color, is_percent=True)
        
        st.markdown(f"<h4 style='font-weight: 300; font-size:1.1rem;'>IMPACT 30 DERNIERS MÈTRES</h4>", unsafe_allow_html=True)
        render_beeswarm(json_data, 'Final_Third_90', 'Passes entrant dans le dernier tiers', selected_player, text_color, other_color)

    with c3:
        st.markdown(f"<h4 style='font-weight: 300; font-size:1.1rem;'>COURSES PROGRESSIVES</h4>", unsafe_allow_html=True)
        render_beeswarm(json_data, 'Prog_Carries_90', "Courses vers l'avant (>10m) par match", selected_player, text_color, other_color)
        
        st.markdown(f"<h4 style='font-weight: 300; font-size:1.1rem;'>VOLUME DÉFENSIF</h4>", unsafe_allow_html=True)
        render_beeswarm(json_data, 'Def_Actions_90', 'Tacles, Interceptions & Récupérations', selected_player, text_color, other_color)

else:
    # État initial
    st.markdown("""
    <div style="text-align: center; margin-top: 100px;">
        <h1 style="color: #C9D1D9;">Tableau de bord Statistique</h1>
        <p style="color: #8B949E; font-size: 1.2rem;">Veuillez sélectionner un club et un joueur dans le panneau latéral pour commencer l'analyse.</p>
    </div>
    """, unsafe_allow_html=True)
