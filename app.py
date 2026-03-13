"""
app.py - Simulador de Copa del Mundo MMJ
Aplicación principal de Streamlit
"""
import streamlit as st
import pandas as pd
import random
from data import (
    UEFA_TEAMS, CONMEBOL_TEAMS, CAF_TEAMS, CONCACAF_TEAMS, AFC_TEAMS,
    PLAYERS, INITIAL_FIFA_RANKING, PLAYOFF_TEAMS
)
from state import (
    init_state, simulate_euro, simulate_euro_playoffs,
    simulate_copa_america, simulate_conmebol_playoffs,
    simulate_copa_africa, simulate_caf_playoffs,
    simulate_copa_oro, simulate_concacaf_playoffs,
    simulate_copa_asia, simulate_afc_playoffs,
    simulate_int_playoff, build_world_cup, simulate_world_cup,
    update_ranking_from_tournament
)

# ============================================================
# CONFIG
# ============================================================
st.set_page_config(
    page_title="MMJ World Cup Simulator",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Rajdhani:wght@400;600;700&family=Inter:wght@300;400;600&display=swap');

:root {
    --primary: #00D4AA;
    --secondary: #FF6B35;
    --dark: #0A0E1A;
    --dark2: #111827;
    --card: #1A2035;
    --text: #E8EAF0;
    --muted: #8892A4;
    --gold: #FFD700;
    --silver: #C0C0C0;
    --bronze: #CD7F32;
}

html, body, [class*="css"] {
    font-family: 'Rajdhani', sans-serif;
    background-color: var(--dark) !important;
    color: var(--text) !important;
}

.main { background-color: var(--dark) !important; }
.stApp { background-color: var(--dark) !important; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0D1321 0%, #111827 100%) !important;
    border-right: 1px solid rgba(0,212,170,0.2);
}

[data-testid="stSidebar"] * { color: var(--text) !important; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, var(--primary), #00A882) !important;
    color: #0A0E1A !important;
    font-family: 'Bebas Neue', cursive !important;
    font-size: 16px !important;
    letter-spacing: 2px !important;
    border: none !important;
    border-radius: 4px !important;
    padding: 8px 24px !important;
    transition: all 0.3s ease !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(0,212,170,0.4) !important;
}

/* Cards */
.card {
    background: var(--card);
    border: 1px solid rgba(0,212,170,0.15);
    border-radius: 8px;
    padding: 20px;
    margin: 8px 0;
}

.card-gold { border-left: 4px solid var(--gold) !important; }
.card-silver { border-left: 4px solid var(--silver) !important; }
.card-bronze { border-left: 4px solid var(--bronze) !important; }
.card-primary { border-left: 4px solid var(--primary) !important; }

/* Headers */
h1, h2, h3 {
    font-family: 'Bebas Neue', cursive !important;
    letter-spacing: 3px !important;
    color: var(--text) !important;
}

/* Title hero */
.hero-title {
    font-family: 'Bebas Neue', cursive;
    font-size: 72px;
    letter-spacing: 8px;
    background: linear-gradient(135deg, #00D4AA, #FFD700);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-align: center;
    line-height: 1;
    margin-bottom: 4px;
}

.hero-sub {
    font-family: 'Rajdhani', sans-serif;
    font-size: 16px;
    letter-spacing: 6px;
    color: var(--muted);
    text-align: center;
    text-transform: uppercase;
}

/* Tables */
.stDataFrame { background: var(--card) !important; }
thead tr th {
    background: rgba(0,212,170,0.1) !important;
    color: var(--primary) !important;
    font-family: 'Bebas Neue', cursive !important;
    letter-spacing: 2px !important;
}

/* Metrics */
[data-testid="metric-container"] {
    background: var(--card);
    border: 1px solid rgba(0,212,170,0.2);
    border-radius: 8px;
    padding: 16px;
}

/* Badge styles */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 1px;
}
.badge-green { background: rgba(0,212,170,0.2); color: var(--primary); border: 1px solid var(--primary); }
.badge-orange { background: rgba(255,107,53,0.2); color: var(--secondary); border: 1px solid var(--secondary); }
.badge-gold { background: rgba(255,215,0,0.2); color: var(--gold); border: 1px solid var(--gold); }

/* Tabs */
.stTabs [data-baseweb="tab"] {
    font-family: 'Bebas Neue', cursive !important;
    letter-spacing: 2px !important;
    font-size: 16px !important;
}

/* Flag emoji size */
.flag { font-size: 24px; }

/* Match card */
.match-card {
    background: var(--card);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 8px;
    padding: 12px 16px;
    margin: 4px 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.selectbox label, .stSelectbox label {
    font-family: 'Bebas Neue', cursive !important;
    letter-spacing: 2px !important;
    color: var(--muted) !important;
}

/* Dividers */
hr { border-color: rgba(0,212,170,0.15) !important; }
</style>
""", unsafe_allow_html=True)

init_state()

# ============================================================
# HELPERS UI
# ============================================================

FLAG_MAP = {
    "France": "🇫🇷", "Spain": "🇪🇸", "England": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "Germany": "🇩🇪",
    "Portugal": "🇵🇹", "Italy": "🇮🇹", "Netherlands": "🇳🇱", "Belgium": "🇧🇪",
    "Croatia": "🇭🇷", "Denmark": "🇩🇰", "Switzerland": "🇨🇭", "Norway": "🇳🇴",
    "Austria": "🇦🇹", "Sweden": "🇸🇪", "Poland": "🇵🇱", "Serbia": "🇷🇸",
    "Turkey": "🇹🇷", "Ukraine": "🇺🇦", "Czech Republic": "🇨🇿", "Greece": "🇬🇷",
    "Scotland": "🏴󠁧󠁢󠁳󠁣󠁴󠁿", "Wales": "🏴󠁧󠁢󠁷󠁬󠁳󠁿", "Iceland": "🇮🇸", "Russia": "🇷🇺",
    "Argentina": "🇦🇷", "Brazil": "🇧🇷", "Colombia": "🇨🇴", "Uruguay": "🇺🇾",
    "Chile": "🇨🇱", "Ecuador": "🇪🇨", "Paraguay": "🇵🇾", "Peru": "🇵🇪",
    "Bolivia": "🇧🇴", "Venezuela": "🇻🇪",
    "Senegal": "🇸🇳", "Morocco": "🇲🇦", "Tunisia": "🇹🇳", "Ghana": "🇬🇭",
    "Egypt": "🇪🇬", "Ivory Coast": "🇨🇮", "Nigeria": "🇳🇬", "Cameroon": "🇨🇲",
    "South Africa": "🇿🇦", "Algeria": "🇩🇿",
    "Mexico": "🇲🇽", "USA": "🇺🇸", "Canada": "🇨🇦", "Costa Rica": "🇨🇷",
    "Panama": "🇵🇦", "Jamaica": "🇯🇲",
    "Japan": "🇯🇵", "Korea": "🇰🇷", "Australia": "🇦🇺", "Saudi Arabia": "🇸🇦",
    "Iran": "🇮🇷", "Qatar": "🇶🇦",
    "New Zealand": "🇳🇿",
}

CONF_COLORS = {
    "UEFA": "#4A90D9",
    "CONMEBOL": "#27AE60",
    "CAF": "#F39C12",
    "CONCACAF": "#E74C3C",
    "AFC": "#9B59B6",
}

CONF_CUPS = {
    "UEFA": "🏆 EUROCOPA",
    "CONMEBOL": "🏆 COPA AMÉRICA",
    "CAF": "🏆 COPA ÁFRICA",
    "CONCACAF": "🏆 COPA ORO",
    "AFC": "🏆 COPA ASIA",
}


def flag(team: str) -> str:
    return FLAG_MAP.get(team, "🏳️")


def render_standings_table(standings: list, title: str = "", highlight_n: int = 0,
                            repechaje_pos: int = None):
    """Renderiza una tabla de posiciones estilizada."""
    if title:
        st.markdown(f"### {title}")

    rows = []
    for entry in standings:
        pos = entry.get("pos", entry.get("position", ""))
        team = entry.get("team", "")
        pts = entry.get("pts", "-")
        played = entry.get("played", "-")
        w = entry.get("w", "-")
        d = entry.get("d", "-")
        l = entry.get("l", "-")
        gf = entry.get("gf", "-")
        ga = entry.get("ga", "-")
        gd = entry.get("gd", "-")

        # Status badge
        if isinstance(pos, int) and pos <= highlight_n:
            status = "✅ Clasifica"
        elif repechaje_pos and isinstance(pos, int) and pos == repechaje_pos:
            status = "🔄 Repechaje"
        else:
            status = "❌ Elimina"

        rows.append({
            "Pos": f"{pos}",
            "": f"{flag(team)} {team}",
            "Pts": pts,
            "PJ": played,
            "G": w,
            "E": d,
            "P": l,
            "GF": gf,
            "GC": ga,
            "GD": f"+{gd}" if isinstance(gd, int) and gd > 0 else str(gd),
            "Estado": status,
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)


def render_bracket(bracket: dict):
    """Renderiza el bracket de eliminatorias."""
    st.markdown("#### 🏆 Bracket Eliminatorio")
    cols = st.columns(len([k for k in bracket if k not in ["Champion"]]))
    rounds = [k for k in ["R16", "SF", "QF", "Final", "Third"] if k in bracket]

    for i, round_name in enumerate(rounds):
        matches = bracket[round_name]
        if isinstance(matches, list):
            with cols[min(i, len(cols)-1)]:
                st.markdown(f"**{round_name}**")
                for m in matches:
                    w = m.get("winner", "")
                    t1 = m.get("t1", "")
                    t2 = m.get("t2", "")
                    st.markdown(
                        f"<div class='card' style='padding:8px;margin:4px 0;'>"
                        f"<span style='color:{'#00D4AA' if w==t1 else '#666'}'>{flag(t1)} {t1}</span><br>"
                        f"<span style='color:#666;font-size:11px;'>vs</span><br>"
                        f"<span style='color:{'#00D4AA' if w==t2 else '#666'}'>{flag(t2)} {t2}</span>"
                        f"</div>", unsafe_allow_html=True
                    )
        elif isinstance(matches, dict):
            with cols[min(i, len(cols)-1)]:
                st.markdown(f"**{round_name}**")
                m = matches
                w = m.get("winner", "")
                t1 = m.get("t1", "")
                t2 = m.get("t2", "")
                st.markdown(
                    f"<div class='card card-gold' style='padding:8px;'>"
                    f"<span style='color:{'#00D4AA' if w==t1 else '#666'}'>{flag(t1)} {t1}</span><br>"
                    f"<span style='color:#666;font-size:11px;'>vs</span><br>"
                    f"<span style='color:{'#00D4AA' if w==t2 else '#666'}'>{flag(t2)} {t2}</span><br>"
                    f"<b style='color:#FFD700'>🏆 {flag(w)} {w}</b>"
                    f"</div>", unsafe_allow_html=True
                )


def get_sofifa_url(player_name: str, team: str) -> str:
    """Genera URL de búsqueda de Sofifa para un jugador."""
    search_name = player_name.replace(" ", "+")
    return f"https://sofifa.com/players?keyword={search_name}"


def render_player_card(player: dict, team: str):
    """Renderiza una tarjeta de jugador estilo Sofifa."""
    name = player.get("name", "")
    position = player.get("position", "")
    sofifa_url = get_sofifa_url(name, team)

    pos_color = {"GK": "#F39C12", "DF": "#2980B9", "MF": "#27AE60", "FW": "#E74C3C"}.get(position, "#666")

    st.markdown(
        f"""<div class='card' style='padding:12px;text-align:center;'>
        <div style='font-size:32px;'>{flag(team)}</div>
        <div style='font-size:10px;background:{pos_color};color:white;border-radius:3px;
                    padding:1px 6px;display:inline-block;margin:4px 0;'>{position}</div>
        <div style='font-weight:700;font-size:14px;'>{name}</div>
        <a href='{sofifa_url}' target='_blank' style='color:#00D4AA;font-size:11px;'>🔗 SoFifa</a>
        </div>""",
        unsafe_allow_html=True
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:10px 0;'>
        <div style='font-family:Bebas Neue;font-size:28px;letter-spacing:4px;color:#00D4AA;'>⚽ MMJ</div>
        <div style='font-size:11px;letter-spacing:3px;color:#8892A4;'>WORLD CUP SIMULATOR</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    pages = [
        "🏠 Inicio",
        "🌍 UEFA - Eurocopa",
        "🌎 CONMEBOL - Copa América",
        "🌍 CAF - Copa África",
        "🌎 CONCACAF - Copa Oro",
        "🌏 AFC - Copa Asia",
        "🔄 Repechaje Internacional",
        "🏆 Mundial",
        "📊 Ranking FIFA",
        "👥 Plantillas",
    ]

    for page in pages:
        if st.button(page, key=f"nav_{page}", use_container_width=True):
            st.session_state.active_page = page
            st.rerun()

    st.divider()
    season = st.session_state.season
    st.markdown(f"<div style='text-align:center;color:#8892A4;font-size:12px;'>Temporada {season}</div>",
                unsafe_allow_html=True)

    qualified_count = len(st.session_state.world_cup_qualified)
    st.markdown(f"<div style='text-align:center;color:#00D4AA;font-size:13px;'>{qualified_count}/32 clasificados</div>",
                unsafe_allow_html=True)

page = st.session_state.active_page

# ============================================================
# PÁGINA: INICIO
# ============================================================

if page == "🏠 Inicio":
    st.markdown("<div class='hero-title'>MMJ WORLD CUP</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-sub'>Simulador de Copa del Mundo · Temporada " +
                str(st.session_state.season) + "</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        qualified = len(st.session_state.world_cup_qualified)
        st.metric("Clasificados al Mundial", f"{qualified}/32")
    with col2:
        champion = st.session_state.world_cup_champion or "—"
        st.metric("🏆 Campeón del Mundo", champion)
    with col3:
        ranking_leader = max(st.session_state.fifa_ranking,
                             key=st.session_state.fifa_ranking.get)
        st.metric("👑 Ranking #1 FIFA", ranking_leader)
    with col4:
        st.metric("Temporada", st.session_state.season)

    st.divider()

    # Estado de torneos
    st.markdown("### 📋 Estado de los Torneos")

    cups = [
        ("🌍 Eurocopa", "euro_standings", "UEFA"),
        ("🌎 Copa América", "copa_america_standings", "CONMEBOL"),
        ("🌍 Copa África", "copa_africa_standings", "CAF"),
        ("🌎 Copa Oro", "copa_oro_standings", "CONCACAF"),
        ("🌏 Copa Asia", "copa_asia_standings", "AFC"),
    ]

    cols = st.columns(len(cups))
    for col, (name, key, conf) in zip(cols, cups):
        with col:
            done = st.session_state[key] is not None
            status = "✅ Jugado" if done else "⏳ Pendiente"
            color = CONF_COLORS.get(conf, "#666")
            champion_text = ""
            if done:
                data = st.session_state[key]
                if isinstance(data, dict):
                    champ = data.get("champion", "")
                    champion_text = f"<br><b style='color:#FFD700'>{flag(champ)} {champ}</b>"

            st.markdown(
                f"<div class='card' style='border-left:4px solid {color};text-align:center;'>"
                f"<div style='font-size:11px;letter-spacing:2px;color:{color};'>{conf}</div>"
                f"<div style='font-weight:700;'>{name}</div>"
                f"<div style='font-size:12px;'>{status}{champion_text}</div>"
                f"</div>",
                unsafe_allow_html=True
            )

    # Clasificados
    if st.session_state.world_cup_qualified:
        st.divider()
        st.markdown("### ✅ Clasificados al Mundial")
        qualified_teams = st.session_state.world_cup_qualified
        cols_per_row = 6
        for i in range(0, len(qualified_teams), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, team in enumerate(qualified_teams[i:i+cols_per_row]):
                with cols[j]:
                    st.markdown(
                        f"<div class='card' style='text-align:center;padding:8px;'>"
                        f"<div style='font-size:24px;'>{flag(team)}</div>"
                        f"<div style='font-size:12px;'>{team}</div>"
                        f"</div>",
                        unsafe_allow_html=True
                    )

    # Reset temporada
    st.divider()
    if st.session_state.world_cup_champion:
        if st.button("🔄 Nueva Temporada (Resetear Torneos)"):
            # Guardar historial
            st.session_state.season_history.append({
                "season": st.session_state.season,
                "champion": st.session_state.world_cup_champion,
                "ranking_snapshot": dict(st.session_state.fifa_ranking),
            })
            st.session_state.season += 1
            # Reset torneos pero mantener ranking
            keys_to_reset = [
                "euro_standings", "copa_america_standings", "copa_africa_standings",
                "copa_oro_standings", "copa_asia_standings",
                "euro_playoff_groups", "euro_playoff_standings",
                "conmebol_playoff", "caf_playoff", "concacaf_playoff", "afc_playoff",
                "int_playoff", "world_cup_qualified", "world_cup_host",
                "world_cup_groups", "world_cup_results", "world_cup_bracket",
                "world_cup_champion",
            ]
            for k in keys_to_reset:
                if k == "world_cup_qualified":
                    st.session_state[k] = []
                else:
                    st.session_state[k] = None
            st.rerun()


# ============================================================
# PÁGINA: UEFA - EUROCOPA
# ============================================================

elif page == "🌍 UEFA - Eurocopa":
    st.markdown("## 🌍 EUROCOPA UEFA")
    st.markdown(f"<span class='badge badge-green'>24 selecciones · Clasifican 13 al Mundial</span>",
                unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🏆 Eurocopa", "🔢 Eliminatorias UEFA", "✅ Clasificados"])

    with tab1:
        if st.session_state.euro_standings is None:
            st.info("🎮 Aún no se ha jugado la Eurocopa. Simúlala aquí.")

            # Selector de equipos
            st.markdown("#### Equipos participantes")
            selected = st.multiselect(
                "Selecciona 24 equipos para la Eurocopa",
                UEFA_TEAMS,
                default=UEFA_TEAMS[:24],
                max_selections=24
            )

            if st.button("⚽ SIMULAR EUROCOPA", use_container_width=True):
                if len(selected) < 24:
                    st.error(f"Necesitas exactamente 24 equipos. Tienes {len(selected)}.")
                else:
                    with st.spinner("Simulando la Eurocopa..."):
                        result = simulate_euro(selected)
                        st.session_state.euro_standings = result
                        update_ranking_from_tournament(result, "confederation")
                        st.success(f"🏆 ¡Eurocopa completada! Campeón: {flag(result['champion'])} {result['champion']}")
                        st.rerun()
        else:
            result = st.session_state.euro_standings

            # Champion banner
            champ = result["champion"]
            runner = result["runner_up"]
            st.markdown(
                f"""<div class='card card-gold' style='text-align:center;padding:24px;'>
                <div style='font-size:48px;'>{flag(champ)}</div>
                <div style='font-family:Bebas Neue;font-size:36px;letter-spacing:4px;color:#FFD700;'>
                    🏆 CAMPEÓN: {champ}</div>
                <div style='color:#C0C0C0;'>Subcampeón: {flag(runner)} {runner}</div>
                </div>""",
                unsafe_allow_html=True
            )
            st.markdown("<br>", unsafe_allow_html=True)

            # Bracket
            render_bracket(result["bracket"])

            st.divider()

            # Tabla final
            render_standings_table(
                result["final_standings"][:12],
                "📊 Clasificación Final",
                highlight_n=5
            )

            # Grupos
            st.markdown("#### 🗂️ Resultados por Grupo")
            group_keys = list(result["group_standings"].keys())
            cols = st.columns(3)
            for i, g_label in enumerate(group_keys):
                with cols[i % 3]:
                    standings = result["group_standings"][g_label]
                    st.markdown(f"**Grupo {g_label}**")
                    df_data = []
                    for s in standings:
                        df_data.append({
                            "": f"{flag(s['team'])} {s['team']}",
                            "Pts": s["pts"],
                            "GD": s["gd"],
                        })
                    st.dataframe(pd.DataFrame(df_data), hide_index=True, use_container_width=True)

            if st.button("🔄 Re-simular Eurocopa"):
                st.session_state.euro_standings = None
                st.session_state.euro_playoff_groups = None
                st.session_state.euro_playoff_standings = None
                st.rerun()

    with tab2:
        st.markdown("### 🔢 Eliminatorias UEFA (Playoffs al Mundial)")
        st.markdown("""
        <div class='card card-primary'>
        📋 <b>Reglas:</b> Puestos 6-21 de la Eurocopa → 4 grupos de 4 equipos.
        Solo se juega 1 ronda (todos vs todos). Los 2 primeros de cada grupo clasifican al Mundial.
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        if st.session_state.euro_standings is None:
            st.warning("⚠️ Primero debes simular la Eurocopa.")
        elif st.session_state.euro_playoff_standings is None:
            if st.button("⚽ SIMULAR ELIMINATORIAS UEFA", use_container_width=True):
                with st.spinner("Simulando eliminatorias..."):
                    playoff_standings, qualified = simulate_euro_playoffs(
                        st.session_state.euro_standings["final_standings"]
                    )
                    st.session_state.euro_playoff_groups = playoff_standings
                    st.session_state.euro_playoff_standings = qualified

                    # Agregar clasificados UEFA al mundial
                    euro_qualified = [st.session_state.euro_standings["final_standings"][i]["team"]
                                      for i in range(5)]
                    all_uefa_qualified = euro_qualified + qualified
                    current = st.session_state.world_cup_qualified
                    for t in all_uefa_qualified:
                        if t not in current:
                            current.append(t)
                    st.session_state.world_cup_qualified = current
                    st.success(f"✅ {len(all_uefa_qualified)} equipos UEFA clasificados al Mundial!")
                    st.rerun()
        else:
            playoff_groups = st.session_state.euro_playoff_groups
            playoff_qualified = st.session_state.euro_playoff_standings

            st.markdown("#### Grupos de Eliminatoria")
            cols = st.columns(4)
            for i, (g_label, standings) in enumerate(playoff_groups.items()):
                with cols[i]:
                    render_standings_table(standings, f"Grupo {g_label}", highlight_n=2)

            st.divider()
            st.markdown("#### ✅ Clasificados al Mundial via Playoffs")
            for t in playoff_qualified:
                st.markdown(f"- {flag(t)} **{t}**")

    with tab3:
        st.markdown("### ✅ Clasificados UEFA al Mundial")

        euro_direct = []
        if st.session_state.euro_standings:
            euro_direct = [st.session_state.euro_standings["final_standings"][i]["team"]
                           for i in range(5)]

        euro_playoff_q = st.session_state.euro_playoff_standings or []

        cols = st.columns(2)
        with cols[0]:
            st.markdown("**Directos (Top 5 Eurocopa)**")
            for pos, t in enumerate(euro_direct, 1):
                medal = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][pos-1]
                st.markdown(f"{medal} {flag(t)} {t}")

        with cols[1]:
            st.markdown("**Via Playoffs (8 equipos)**")
            for t in euro_playoff_q:
                st.markdown(f"✅ {flag(t)} {t}")


# ============================================================
# PÁGINA: CONMEBOL - COPA AMÉRICA
# ============================================================

elif page == "🌎 CONMEBOL - Copa América":
    st.markdown("## 🌎 COPA AMÉRICA CONMEBOL")
    st.markdown(f"<span class='badge badge-green'>10 selecciones · Clasifican 4+1 repechaje</span>",
                unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🏆 Copa América", "🔢 Eliminatorias CONMEBOL"])

    with tab1:
        if st.session_state.copa_america_standings is None:
            st.info("🎮 Aún no se ha jugado la Copa América.")

            selected = st.multiselect(
                "Equipos (10)",
                CONMEBOL_TEAMS,
                default=CONMEBOL_TEAMS,
                max_selections=10
            )

            if st.button("⚽ SIMULAR COPA AMÉRICA", use_container_width=True):
                if len(selected) != 10:
                    st.error("Necesitas exactamente 10 equipos.")
                else:
                    with st.spinner("Simulando Copa América..."):
                        result = simulate_copa_america(selected)
                        st.session_state.copa_america_standings = result
                        update_ranking_from_tournament(result, "confederation")

                        # Campeón clasifica directamente
                        champ = result["champion"]
                        if champ not in st.session_state.world_cup_qualified:
                            st.session_state.world_cup_qualified.append(champ)

                        st.success(f"🏆 Campeón: {flag(champ)} {champ}")
                        st.rerun()
        else:
            result = st.session_state.copa_america_standings
            champ = result["champion"]
            runner = result["runner_up"]

            st.markdown(
                f"""<div class='card card-gold' style='text-align:center;padding:24px;'>
                <div style='font-size:48px;'>{flag(champ)}</div>
                <div style='font-family:Bebas Neue;font-size:36px;letter-spacing:4px;color:#FFD700;'>
                    🏆 CAMPEÓN: {champ}</div>
                <div style='color:#C0C0C0;'>Subcampeón: {flag(runner)} {runner}</div>
                </div>""",
                unsafe_allow_html=True
            )

            st.markdown("<br>", unsafe_allow_html=True)
            render_bracket(result["bracket"])
            st.divider()

            cols = st.columns(2)
            with cols[0]:
                render_standings_table(result["group_a"], "Grupo A")
            with cols[1]:
                render_standings_table(result["group_b"], "Grupo B")

            render_standings_table(result["final_standings"], "Clasificación Final", highlight_n=1)

            if st.button("🔄 Re-simular Copa América"):
                st.session_state.copa_america_standings = None
                st.session_state.conmebol_playoff = None
                st.rerun()

    with tab2:
        st.markdown("### 🔢 Eliminatorias CONMEBOL")
        st.markdown("""
        <div class='card card-primary'>
        📋 <b>Reglas:</b> Puestos 2-7 → todos vs todos (1 ronda).
        Top 3 → Mundial directo · 4to puesto → Repechaje Internacional.
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.copa_america_standings is None:
            st.warning("⚠️ Primero simula la Copa América.")
        elif st.session_state.conmebol_playoff is None:
            if st.button("⚽ SIMULAR ELIMINATORIAS CONMEBOL", use_container_width=True):
                with st.spinner("Simulando..."):
                    standings, qualified, repechaje = simulate_conmebol_playoffs(
                        st.session_state.copa_america_standings["final_standings"]
                    )
                    st.session_state.conmebol_playoff = {
                        "standings": standings,
                        "qualified": qualified,
                        "repechaje": repechaje
                    }
                    for t in qualified:
                        if t not in st.session_state.world_cup_qualified:
                            st.session_state.world_cup_qualified.append(t)
                    st.success(f"✅ Clasificados: {', '.join(qualified)}")
                    if repechaje:
                        st.info(f"🔄 Repechaje: {flag(repechaje)} {repechaje}")
                    st.rerun()
        else:
            data = st.session_state.conmebol_playoff
            render_standings_table(data["standings"], "Eliminatoria CONMEBOL",
                                   highlight_n=3, repechaje_pos=4)

            st.markdown("#### ✅ Clasificados")
            for t in data["qualified"]:
                st.markdown(f"✅ {flag(t)} **{t}** → Mundial")
            if data.get("repechaje"):
                st.markdown(f"🔄 {flag(data['repechaje'])} **{data['repechaje']}** → Repechaje Internacional")


# ============================================================
# PÁGINA: CAF - COPA ÁFRICA
# ============================================================

elif page == "🌍 CAF - Copa África":
    st.markdown("## 🌍 COPA ÁFRICA CAF")
    st.markdown(f"<span class='badge badge-gold'>10 selecciones · Clasifican 5 al Mundial</span>",
                unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🏆 Copa África", "🔢 Eliminatorias CAF"])

    with tab1:
        if st.session_state.copa_africa_standings is None:
            st.info("🎮 Aún no se ha jugado la Copa África.")
            selected = st.multiselect("Equipos (10)", CAF_TEAMS, default=CAF_TEAMS)
            if st.button("⚽ SIMULAR COPA ÁFRICA", use_container_width=True):
                if len(selected) != 10:
                    st.error("Necesitas 10 equipos.")
                else:
                    with st.spinner("Simulando..."):
                        result = simulate_copa_africa(selected)
                        st.session_state.copa_africa_standings = result
                        update_ranking_from_tournament(result, "confederation")
                        champ = result["champion"]
                        runner = result["runner_up"]
                        for t in [champ, runner]:
                            if t not in st.session_state.world_cup_qualified:
                                st.session_state.world_cup_qualified.append(t)
                        st.success(f"🏆 Campeón: {flag(champ)} {champ}")
                        st.rerun()
        else:
            result = st.session_state.copa_africa_standings
            champ = result["champion"]
            runner = result["runner_up"]
            st.markdown(
                f"""<div class='card card-gold' style='text-align:center;padding:24px;'>
                <div style='font-size:48px;'>{flag(champ)}</div>
                <div style='font-family:Bebas Neue;font-size:36px;letter-spacing:4px;color:#FFD700;'>
                    🏆 CAMPEÓN: {champ}</div>
                <div style='color:#C0C0C0;'>Subcampeón: {flag(runner)} {runner} (también clasifica)</div>
                </div>""",
                unsafe_allow_html=True
            )
            render_bracket(result["bracket"])
            render_standings_table(result["final_standings"], "Clasificación Final", highlight_n=2)

            if st.button("🔄 Re-simular Copa África"):
                st.session_state.copa_africa_standings = None
                st.session_state.caf_playoff = None
                st.rerun()

    with tab2:
        st.markdown("### 🔢 Eliminatorias CAF")
        st.markdown("""
        <div class='card card-primary'>
        📋 Puestos 3-7 (5 equipos) → todos vs todos · Top 3 → Mundial
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.copa_africa_standings is None:
            st.warning("⚠️ Primero simula la Copa África.")
        elif st.session_state.caf_playoff is None:
            if st.button("⚽ SIMULAR ELIMINATORIAS CAF", use_container_width=True):
                with st.spinner("Simulando..."):
                    standings, qualified = simulate_caf_playoffs(
                        st.session_state.copa_africa_standings["final_standings"]
                    )
                    st.session_state.caf_playoff = {"standings": standings, "qualified": qualified}
                    for t in qualified:
                        if t not in st.session_state.world_cup_qualified:
                            st.session_state.world_cup_qualified.append(t)
                    st.success(f"✅ Clasificados: {', '.join(qualified)}")
                    st.rerun()
        else:
            data = st.session_state.caf_playoff
            render_standings_table(data["standings"], "Eliminatoria CAF", highlight_n=3)
            for t in data["qualified"]:
                st.markdown(f"✅ {flag(t)} **{t}** → Mundial")


# ============================================================
# PÁGINA: CONCACAF - COPA ORO
# ============================================================

elif page == "🌎 CONCACAF - Copa Oro":
    st.markdown("## 🌎 COPA ORO CONCACAF")
    st.markdown(f"<span class='badge badge-orange'>6 selecciones · Clasifican 3+1 repechaje</span>",
                unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🏆 Copa Oro", "🔢 Eliminatorias CONCACAF"])

    with tab1:
        if st.session_state.copa_oro_standings is None:
            st.info("🎮 Aún no se ha jugado la Copa Oro.")
            selected = st.multiselect("Equipos (6)", CONCACAF_TEAMS, default=CONCACAF_TEAMS)
            if st.button("⚽ SIMULAR COPA ORO", use_container_width=True):
                if len(selected) != 6:
                    st.error("Necesitas 6 equipos.")
                else:
                    with st.spinner("Simulando..."):
                        result = simulate_copa_oro(selected)
                        st.session_state.copa_oro_standings = result
                        update_ranking_from_tournament(result, "confederation")
                        champ = result["champion"]
                        if champ not in st.session_state.world_cup_qualified:
                            st.session_state.world_cup_qualified.append(champ)
                        st.success(f"🏆 Campeón: {flag(champ)} {champ}")
                        st.rerun()
        else:
            result = st.session_state.copa_oro_standings
            champ = result["champion"]
            st.markdown(
                f"""<div class='card card-gold' style='text-align:center;padding:24px;'>
                <div style='font-size:48px;'>{flag(champ)}</div>
                <div style='font-family:Bebas Neue;font-size:36px;letter-spacing:4px;color:#FFD700;'>
                    🏆 CAMPEÓN: {champ}</div>
                </div>""",
                unsafe_allow_html=True
            )
            render_bracket(result["bracket"])
            render_standings_table(result["final_standings"], "Clasificación", highlight_n=1)
            if st.button("🔄 Re-simular Copa Oro"):
                st.session_state.copa_oro_standings = None
                st.session_state.concacaf_playoff = None
                st.rerun()

    with tab2:
        st.markdown("### 🔢 Eliminatorias CONCACAF")
        st.markdown("""
        <div class='card card-primary'>
        📋 Puestos 2-5 → todos vs todos · Top 2 → Mundial · 3ro → Repechaje Internacional
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.copa_oro_standings is None:
            st.warning("⚠️ Primero simula la Copa Oro.")
        elif st.session_state.concacaf_playoff is None:
            if st.button("⚽ SIMULAR ELIMINATORIAS CONCACAF", use_container_width=True):
                with st.spinner("Simulando..."):
                    standings, qualified, repechaje = simulate_concacaf_playoffs(
                        st.session_state.copa_oro_standings["final_standings"]
                    )
                    st.session_state.concacaf_playoff = {
                        "standings": standings,
                        "qualified": qualified,
                        "repechaje": repechaje
                    }
                    for t in qualified:
                        if t not in st.session_state.world_cup_qualified:
                            st.session_state.world_cup_qualified.append(t)
                    st.success(f"✅ Clasificados: {', '.join(qualified)}")
                    if repechaje:
                        st.info(f"🔄 Repechaje: {repechaje}")
                    st.rerun()
        else:
            data = st.session_state.concacaf_playoff
            render_standings_table(data["standings"], "Eliminatoria CONCACAF",
                                   highlight_n=2, repechaje_pos=3)
            for t in data["qualified"]:
                st.markdown(f"✅ {flag(t)} **{t}** → Mundial")
            if data.get("repechaje"):
                st.markdown(f"🔄 {flag(data['repechaje'])} **{data['repechaje']}** → Repechaje Internacional")


# ============================================================
# PÁGINA: AFC - COPA ASIA
# ============================================================

elif page == "🌏 AFC - Copa Asia":
    st.markdown("## 🌏 COPA ASIA AFC")
    st.markdown(f"<span class='badge badge-green'>6 selecciones (Australia incluida) · Clasifican 4+1 repechaje</span>",
                unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🏆 Copa Asia", "🔢 Eliminatorias AFC"])

    with tab1:
        if st.session_state.copa_asia_standings is None:
            st.info("🎮 Aún no se ha jugado la Copa Asia. 🇦🇺 Australia compite en AFC.")
            selected = st.multiselect("Equipos (6)", AFC_TEAMS, default=AFC_TEAMS)
            if st.button("⚽ SIMULAR COPA ASIA", use_container_width=True):
                if len(selected) != 6:
                    st.error("Necesitas 6 equipos.")
                else:
                    with st.spinner("Simulando..."):
                        result = simulate_copa_asia(selected)
                        st.session_state.copa_asia_standings = result
                        update_ranking_from_tournament(result, "confederation")
                        champ = result["champion"]
                        if champ not in st.session_state.world_cup_qualified:
                            st.session_state.world_cup_qualified.append(champ)
                        st.success(f"🏆 Campeón: {flag(champ)} {champ}")
                        st.rerun()
        else:
            result = st.session_state.copa_asia_standings
            champ = result["champion"]
            st.markdown(
                f"""<div class='card card-gold' style='text-align:center;padding:24px;'>
                <div style='font-size:48px;'>{flag(champ)}</div>
                <div style='font-family:Bebas Neue;font-size:36px;letter-spacing:4px;color:#FFD700;'>
                    🏆 CAMPEÓN: {champ}</div>
                </div>""",
                unsafe_allow_html=True
            )
            render_bracket(result["bracket"])
            render_standings_table(result["final_standings"], "Clasificación", highlight_n=1)
            if st.button("🔄 Re-simular Copa Asia"):
                st.session_state.copa_asia_standings = None
                st.session_state.afc_playoff = None
                st.rerun()

    with tab2:
        st.markdown("### 🔢 Eliminatorias AFC")
        st.markdown("""
        <div class='card card-primary'>
        📋 Puestos 2-5 → todos vs todos · Top 3 → Mundial · 4to → Repechaje Internacional
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.copa_asia_standings is None:
            st.warning("⚠️ Primero simula la Copa Asia.")
        elif st.session_state.afc_playoff is None:
            if st.button("⚽ SIMULAR ELIMINATORIAS AFC", use_container_width=True):
                with st.spinner("Simulando..."):
                    standings, qualified, repechaje = simulate_afc_playoffs(
                        st.session_state.copa_asia_standings["final_standings"]
                    )
                    st.session_state.afc_playoff = {
                        "standings": standings,
                        "qualified": qualified,
                        "repechaje": repechaje
                    }
                    for t in qualified:
                        if t not in st.session_state.world_cup_qualified:
                            st.session_state.world_cup_qualified.append(t)
                    st.success(f"✅ Clasificados: {', '.join(qualified)}")
                    if repechaje:
                        st.info(f"🔄 Repechaje: {repechaje}")
                    st.rerun()
        else:
            data = st.session_state.afc_playoff
            render_standings_table(data["standings"], "Eliminatoria AFC",
                                   highlight_n=3, repechaje_pos=4)
            for t in data["qualified"]:
                st.markdown(f"✅ {flag(t)} **{t}** → Mundial")
            if data.get("repechaje"):
                st.markdown(f"🔄 {flag(data['repechaje'])} **{data['repechaje']}** → Repechaje Internacional")


# ============================================================
# PÁGINA: REPECHAJE INTERNACIONAL
# ============================================================

elif page == "🔄 Repechaje Internacional":
    st.markdown("## 🔄 REPECHAJE INTERNACIONAL")
    st.markdown("""
    <div class='card card-orange' style='border-left:4px solid #FF6B35;'>
    <b>🔄 Partidos de Repechaje:</b><br>
    🟠 CONCACAF 3ro vs AFC 4to → 1 clasificado al Mundial<br>
    🟢 CONMEBOL 4to vs Nueva Zelanda 🇳🇿 → 1 clasificado al Mundial
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Verificar si tenemos los equipos de repechaje
    concacaf_data = st.session_state.concacaf_playoff
    afc_data = st.session_state.afc_playoff
    conmebol_data = st.session_state.conmebol_playoff

    concacaf_3rd = concacaf_data.get("repechaje") if concacaf_data else None
    afc_4th = afc_data.get("repechaje") if afc_data else None
    conmebol_4th = conmebol_data.get("repechaje") if conmebol_data else None

    # Mostrar estado
    col1, col2, col3 = st.columns(3)
    with col1:
        status = f"✅ {flag(concacaf_3rd)} {concacaf_3rd}" if concacaf_3rd else "⏳ Pendiente (simula CONCACAF)"
        st.markdown(f"<div class='card'><b>CONCACAF 3ro</b><br>{status}</div>", unsafe_allow_html=True)
    with col2:
        status = f"✅ {flag(afc_4th)} {afc_4th}" if afc_4th else "⏳ Pendiente (simula AFC)"
        st.markdown(f"<div class='card'><b>AFC 4to</b><br>{status}</div>", unsafe_allow_html=True)
    with col3:
        status = f"✅ {flag(conmebol_4th)} {conmebol_4th}" if conmebol_4th else "⏳ Pendiente (simula CONMEBOL)"
        st.markdown(f"<div class='card'><b>CONMEBOL 4to</b><br>{status}</div>", unsafe_allow_html=True)

    # Permitir override manual si no hay datos
    st.markdown("#### ✏️ Configuración Manual (opcional)")
    col1, col2, col3 = st.columns(3)
    all_teams = list(INITIAL_FIFA_RANKING.keys()) + ["New Zealand"]

    with col1:
        concacaf_3rd_sel = st.selectbox("CONCACAF 3ro", all_teams,
                                         index=all_teams.index(concacaf_3rd) if concacaf_3rd in all_teams else 0)
    with col2:
        afc_4th_sel = st.selectbox("AFC 4to", all_teams,
                                    index=all_teams.index(afc_4th) if afc_4th in all_teams else 0)
    with col3:
        conmebol_4th_sel = st.selectbox("CONMEBOL 4to", all_teams,
                                         index=all_teams.index(conmebol_4th) if conmebol_4th in all_teams else 0)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.session_state.int_playoff is None:
        if st.button("⚽ SIMULAR REPECHAJE INTERNACIONAL", use_container_width=True):
            with st.spinner("Simulando repechaje..."):
                result = simulate_int_playoff(concacaf_3rd_sel, afc_4th_sel, conmebol_4th_sel)
                st.session_state.int_playoff = result

                for t in result["qualified"]:
                    if t not in st.session_state.world_cup_qualified:
                        st.session_state.world_cup_qualified.append(t)

                st.success(f"✅ Clasificados: {', '.join(result['qualified'])}")
                st.rerun()
    else:
        result = st.session_state.int_playoff

        st.markdown("### ⚽ Resultados del Repechaje")
        cols = st.columns(2)

        for i, (match_key, title) in enumerate([
            ("match1", "CONCACAF vs AFC"),
            ("match2", "CONMEBOL vs Nueva Zelanda")
        ]):
            match = result[match_key]
            with cols[i]:
                winner = match["winner"]
                t1 = match["t1"]
                t2 = match["t2"]
                st.markdown(
                    f"""<div class='card card-gold' style='text-align:center;padding:20px;'>
                    <div style='font-size:13px;color:#8892A4;letter-spacing:2px;'>{title}</div>
                    <div style='font-size:28px;margin:8px 0;'>
                        <span style='color:{"#00D4AA" if winner==t1 else "#444"}'>{flag(t1)} {t1}</span>
                        <span style='color:#8892A4;margin:0 8px;'>vs</span>
                        <span style='color:{"#00D4AA" if winner==t2 else "#444"}'>{flag(t2)} {t2}</span>
                    </div>
                    <div style='color:#FFD700;font-family:Bebas Neue;font-size:20px;'>
                        🏆 CLASIFICADO: {flag(winner)} {winner}</div>
                    </div>""",
                    unsafe_allow_html=True
                )

        st.divider()
        st.markdown("#### ✅ Clasificados al Mundial via Repechaje")
        for t in result["qualified"]:
            st.markdown(f"✅ {flag(t)} **{t}**")

        if st.button("🔄 Re-simular Repechaje"):
            st.session_state.int_playoff = None
            qualified = [t for t in st.session_state.world_cup_qualified
                         if t not in result["qualified"]]
            st.session_state.world_cup_qualified = qualified
            st.rerun()


# ============================================================
# PÁGINA: MUNDIAL
# ============================================================

elif page == "🏆 Mundial":
    st.markdown("## 🏆 COPA DEL MUNDO")
    st.markdown("<br>", unsafe_allow_html=True)

    qualified = st.session_state.world_cup_qualified
    n_qualified = len(qualified)

    if n_qualified < 30:
        st.warning(f"⚠️ Solo hay {n_qualified} equipos clasificados. Se necesitan al menos 30.")
        st.info("Completa las eliminatorias de todas las confederaciones primero.")
    else:
        tab1, tab2, tab3 = st.tabs(["⚙️ Configuración", "🏆 Fase de Grupos", "🎯 Eliminatorias"])

        with tab1:
            st.markdown("### ⚙️ Configuración del Mundial")

            all_teams_list = list(INITIAL_FIFA_RANKING.keys())
            host = st.selectbox(
                "🏟️ Selecciona el país anfitrión (Host)",
                all_teams_list,
                help="El host se coloca automáticamente en el Grupo A"
            )

            st.markdown(f"""
            <div class='card card-primary'>
            <b>📋 Reglas del Mundial:</b><br>
            • 32 equipos en 8 grupos de 4<br>
            • El anfitrión va al Grupo A<br>
            • Top 2 de cada grupo pasan a R16<br>
            • Eliminación directa hasta la final<br>
            • Si el host es campeón de su confederación y ya está clasificado, su cupo lo hereda el siguiente
            </div>
            """, unsafe_allow_html=True)

            # Listar clasificados
            st.markdown("#### Equipos Clasificados")
            cols = st.columns(4)
            for i, team in enumerate(qualified[:32]):
                with cols[i % 4]:
                    st.markdown(f"{flag(team)} {team}")

            if len(qualified) < 32 and host not in qualified:
                qualified_wc = qualified + [host]
            else:
                qualified_wc = qualified[:32]
                if host not in qualified_wc:
                    qualified_wc[31] = host

            if st.button("🏆 ARMAR GRUPOS DEL MUNDIAL", use_container_width=True):
                with st.spinner("Armando el mundial..."):
                    groups = build_world_cup(qualified_wc, host)
                    st.session_state.world_cup_host = host
                    st.session_state.world_cup_groups = groups
                    st.success("✅ Grupos armados!")
                    st.rerun()

        with tab2:
            if st.session_state.world_cup_groups is None:
                st.warning("⚠️ Primero configura y arma los grupos del Mundial.")
            else:
                groups = st.session_state.world_cup_groups

                if st.session_state.world_cup_results is None:
                    # Mostrar grupos
                    st.markdown("### 🗂️ Grupos del Mundial")
                    cols = st.columns(4)
                    for i, (g_label, teams) in enumerate(groups.items()):
                        with cols[i % 4]:
                            st.markdown(f"**Grupo {g_label}**")
                            for t in teams:
                                host_badge = " 🏟️" if t == st.session_state.world_cup_host else ""
                                st.markdown(f"{flag(t)} {t}{host_badge}")

                    if st.button("⚽ SIMULAR FASE DE GRUPOS", use_container_width=True):
                        with st.spinner("Jugando la fase de grupos..."):
                            results = simulate_world_cup(groups)
                            st.session_state.world_cup_results = results
                            st.rerun()
                else:
                    results = st.session_state.world_cup_results

                    st.markdown("### 📊 Fase de Grupos - Resultados")
                    cols = st.columns(4)
                    for i, (g_label, g_data) in enumerate(results["group_results"].items()):
                        with cols[i % 4]:
                            st.markdown(f"**Grupo {g_label}**")
                            df_data = []
                            for j, s in enumerate(g_data["standings"]):
                                status = "✅" if j < 2 else "❌"
                                df_data.append({
                                    "": f"{status} {flag(s['team'])} {s['team']}",
                                    "Pts": s["pts"],
                                    "GD": s["gd"],
                                })
                            st.dataframe(pd.DataFrame(df_data), hide_index=True, use_container_width=True)

        with tab3:
            if st.session_state.world_cup_results is None:
                st.warning("⚠️ Primero simula la fase de grupos.")
            else:
                results = st.session_state.world_cup_results

                # Si ya hay campeón, mostrar
                if st.session_state.world_cup_champion:
                    champ = st.session_state.world_cup_champion
                    st.markdown(
                        f"""<div class='card card-gold' style='text-align:center;padding:32px;'>
                        <div style='font-size:72px;'>{flag(champ)}</div>
                        <div style='font-family:Bebas Neue;font-size:52px;letter-spacing:6px;color:#FFD700;'>
                            🏆 CAMPEÓN DEL MUNDO</div>
                        <div style='font-family:Bebas Neue;font-size:36px;'>{champ}</div>
                        </div>""",
                        unsafe_allow_html=True
                    )
                    st.markdown("<br>", unsafe_allow_html=True)

                if not st.session_state.world_cup_champion:
                    if st.button("⚽ SIMULAR ELIMINATORIAS DEL MUNDIAL", use_container_width=True):
                        st.success("✅ La fase de grupos ya fue simulada. Mostrando resultados...")
                        # Los resultados ya están completos en simulate_world_cup
                        champion = results["Champion"]
                        st.session_state.world_cup_champion = champion
                        update_ranking_from_tournament(results, "world_cup")
                        st.rerun()

                # Bracket eliminatorio
                bracket_data = {
                    "R16": results.get("R16", []),
                    "QF": results.get("QF", []),
                    "SF": results.get("SF", []),
                    "Final": results.get("Final", {}),
                }
                render_bracket(bracket_data)

                # 3er puesto
                if "Third" in results:
                    third = results["Third"]
                    st.markdown(
                        f"**🥉 3er Puesto:** {flag(third['winner'])} {third['winner']}"
                    )


# ============================================================
# PÁGINA: RANKING FIFA
# ============================================================

elif page == "📊 Ranking FIFA":
    st.markdown("## 📊 RANKING FIFA")
    st.markdown("""
    <div class='card card-primary'>
    El ranking se actualiza automáticamente al finalizar cada torneo.
    Se resetean los torneos al nueva temporada pero el ranking se mantiene.
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    ranking = st.session_state.fifa_ranking
    sorted_ranking = sorted(ranking.items(), key=lambda x: x[1], reverse=True)

    # Top 3 destacado
    cols = st.columns(3)
    medals = ["🥇", "🥈", "🥉"]
    for i, (team, pts) in enumerate(sorted_ranking[:3]):
        with cols[i]:
            st.markdown(
                f"""<div class='card {"card-gold" if i==0 else "card-silver" if i==1 else "card-bronze"}' 
                    style='text-align:center;padding:20px;'>
                <div style='font-size:36px;'>{medals[i]}</div>
                <div style='font-size:32px;'>{flag(team)}</div>
                <div style='font-family:Bebas Neue;font-size:20px;letter-spacing:2px;'>{team}</div>
                <div style='color:#00D4AA;font-size:24px;font-weight:700;'>{pts}</div>
                <div style='color:#8892A4;font-size:11px;'>PUNTOS FIFA</div>
                </div>""",
                unsafe_allow_html=True
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # Filtro por confederación
    conf_filter = st.selectbox(
        "Filtrar por Confederación",
        ["Todas", "UEFA", "CONMEBOL", "CAF", "CONCACAF", "AFC"]
    )

    conf_teams = {
        "UEFA": UEFA_TEAMS,
        "CONMEBOL": CONMEBOL_TEAMS,
        "CAF": CAF_TEAMS,
        "CONCACAF": CONCACAF_TEAMS,
        "AFC": AFC_TEAMS,
    }

    # Tabla completa
    rows = []
    for pos, (team, pts) in enumerate(sorted_ranking, 1):
        if conf_filter != "Todas":
            if team not in conf_teams.get(conf_filter, []):
                continue

        # Determinar confederación
        team_conf = "—"
        for c, teams_list in conf_teams.items():
            if team in teams_list:
                team_conf = c
                break

        rows.append({
            "Pos": pos,
            "Equipo": f"{flag(team)} {team}",
            "Confederación": team_conf,
            "Puntos": pts,
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Reset ranking
    st.divider()
    if st.button("🔄 Resetear Ranking al inicial"):
        st.session_state.fifa_ranking = dict(INITIAL_FIFA_RANKING)
        st.success("✅ Ranking reseteado.")
        st.rerun()


# ============================================================
# PÁGINA: PLANTILLAS
# ============================================================

elif page == "👥 Plantillas":
    st.markdown("## 👥 PLANTILLAS POR SELECCIÓN")
    st.markdown("<br>", unsafe_allow_html=True)

    # Selector de confederación y equipo
    conf_options = {
        "UEFA 🌍": UEFA_TEAMS,
        "CONMEBOL 🌎": CONMEBOL_TEAMS,
        "CAF 🌍": CAF_TEAMS,
        "CONCACAF 🌎": CONCACAF_TEAMS,
        "AFC 🌏": AFC_TEAMS,
        "Repechaje 🔄": ["New Zealand"],
    }

    col1, col2 = st.columns(2)
    with col1:
        conf_sel = st.selectbox("Confederación", list(conf_options.keys()))
    with col2:
        team_list = conf_options[conf_sel]
        team_sel = st.selectbox("Selección", team_list)

    st.markdown("<br>", unsafe_allow_html=True)

    # Header del equipo
    st.markdown(
        f"""<div class='card' style='text-align:center;padding:20px;'>
        <div style='font-size:64px;'>{flag(team_sel)}</div>
        <div style='font-family:Bebas Neue;font-size:32px;letter-spacing:4px;'>{team_sel}</div>
        <div style='color:#8892A4;'>Ranking FIFA: 
            <b style='color:#00D4AA;'>{st.session_state.fifa_ranking.get(team_sel, "—")}</b> pts
        </div>
        </div>""",
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    players = PLAYERS.get(team_sel, [])
    if not players:
        st.info("No hay datos de jugadores para este equipo.")
    else:
        # Filtrar por posición
        positions = ["Todas"] + sorted(set(p.get("position", "") for p in players))
        pos_filter = st.selectbox("Filtrar por posición", positions)

        filtered = players if pos_filter == "Todas" else [
            p for p in players if p.get("position") == pos_filter
        ]

        # Grid de tarjetas
        cols_per_row = 4
        for i in range(0, len(filtered), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, player in enumerate(filtered[i:i+cols_per_row]):
                with cols[j]:
                    render_player_card(player, team_sel)
