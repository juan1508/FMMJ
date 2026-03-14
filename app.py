import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config(
    page_title="MMJ Tournament Hub",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── PERSISTENCE ──────────────────────────────────────────────────────────────
DATA_FILE = "tournament_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

if "data" not in st.session_state:
    st.session_state.data = load_data()

# ─── CONSTANTS ────────────────────────────────────────────────────────────────
ZONES = {
    "WEST ZONE": {
        "teams": ["LAFC", "LA Galaxy", "San Jose", "San Diego FC", "Portland", "RSL", "Seattle", "Colorado"],
        "groups": 2,
        "advance": 2,
        "format": "groups"
    },
    "MIDWEST ZONE": {
        "teams": ["Minnesota", "Sporting KC", "St. Louis", "Chicago", "Cincinnati", "Columbus"],
        "groups": 2,
        "advance": 2,
        "format": "groups"
    },
    "SOUTH ZONE": {
        "teams": ["Dallas", "Austin", "Houston", "Nashville", "Charlotte", "Atlanta", "Orlando", "Miami"],
        "groups": 2,
        "advance": 2,
        "format": "groups"
    },
    "NORTH ZONE": {
        "teams": ["DC United", "Philadelphia", "NYCFC", "NY Red Bulls", "New England"],
        "groups": 1,
        "advance": 2,
        "format": "roundrobin"
    },
    "CANADIAN ZONE": {
        "teams": ["Montreal", "Toronto", "Vancouver"],
        "groups": 1,
        "advance": 1,
        "format": "roundrobin"
    }
}

MLS_TEAMS = sorted([
    "LAFC", "LA Galaxy", "San Jose", "San Diego FC", "Portland", "RSL", "Seattle", "Colorado",
    "Minnesota", "Sporting KC", "St. Louis", "Chicago", "Cincinnati", "Columbus",
    "Dallas", "Austin", "Houston", "Nashville", "Charlotte", "Atlanta", "Orlando", "Miami",
    "DC United", "Philadelphia", "NYCFC", "NY Red Bulls", "New England",
    "Montreal", "Toronto", "Vancouver"
])

ZONE_COLORS = {
    "WEST ZONE": "#E67E22",
    "MIDWEST ZONE": "#3498DB",
    "SOUTH ZONE": "#2ECC71",
    "NORTH ZONE": "#9B59B6",
    "CANADIAN ZONE": "#E74C3C"
}

# ─── STYLES ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow:wght@300;400;600;700&family=Barlow+Condensed:wght@600;700&display=swap');
:root {
    --gold: #F5C518; --gold2: #E8A800; --dark: #0A0A0F; --dark2: #111118;
    --dark3: #1A1A24; --card: #16161F; --border: #2A2A3A;
    --text: #E8E8F0; --muted: #8888AA; --green: #2ECC71; --red: #E74C3C;
    --blue: #3498DB; --purple: #9B59B6; --orange: #E67E22;
}
* { font-family: 'Barlow', sans-serif; }
.stApp { background: var(--dark); color: var(--text); }
[data-testid="stSidebar"] { background: var(--dark2) !important; border-right: 1px solid var(--border); }
[data-testid="stSidebar"] * { color: var(--text) !important; }
.hero-title {
    font-family: 'Bebas Neue', sans-serif; font-size: 3.5rem; letter-spacing: 4px;
    background: linear-gradient(135deg, var(--gold), var(--gold2), #fff);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    text-align: center; margin: 0; line-height: 1;
}
.hero-sub {
    font-family: 'Barlow Condensed', sans-serif; font-size: 0.85rem;
    letter-spacing: 6px; color: var(--muted); text-align: center; text-transform: uppercase; margin-top: 4px;
}
.section-title {
    font-family: 'Bebas Neue', sans-serif; font-size: 2rem; letter-spacing: 3px;
    color: var(--gold); border-bottom: 2px solid var(--border); padding-bottom: 8px; margin-bottom: 20px;
}
.match-card {
    background: var(--card); border: 1px solid var(--border); border-radius: 8px;
    padding: 16px; margin: 8px 0;
}
.stats-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
.stats-table th {
    background: var(--dark3); color: var(--gold); font-family: 'Barlow Condensed', sans-serif;
    font-size: 0.8rem; letter-spacing: 2px; padding: 10px 12px; text-align: left;
    border-bottom: 2px solid var(--border);
}
.stats-table td { padding: 10px 12px; border-bottom: 1px solid var(--border); color: var(--text); }
.stats-table tr:hover td { background: var(--dark3); }
.info-box {
    background: var(--card); border-left: 3px solid var(--gold);
    border-radius: 0 6px 6px 0; padding: 12px 16px; margin: 8px 0;
    font-size: 0.9rem; color: var(--muted);
}
.scorer-chip {
    display: inline-flex; align-items: center; gap: 6px; background: var(--dark3);
    border: 1px solid var(--border); border-radius: 20px; padding: 4px 12px; margin: 3px; font-size: 0.82rem;
}
.scorer-chip .min { color: var(--gold); font-weight: 700; }
.stButton > button {
    background: var(--gold) !important; color: #000 !important;
    font-family: 'Barlow Condensed', sans-serif !important; font-weight: 700 !important;
    letter-spacing: 2px !important; border: none !important; border-radius: 4px !important;
}
.stButton > button:hover { background: var(--gold2) !important; }
.stTextInput input, .stNumberInput input {
    background: var(--dark3) !important; color: var(--text) !important;
    border: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab-list"] { background: var(--dark2) !important; border-bottom: 1px solid var(--border) !important; }
.stTabs [data-baseweb="tab"] {
    background: transparent !important; color: var(--muted) !important;
    font-family: 'Barlow Condensed', sans-serif !important; font-weight: 600 !important;
    letter-spacing: 1px !important; border-bottom: 2px solid transparent !important;
}
.stTabs [aria-selected="true"] { color: var(--gold) !important; border-bottom-color: var(--gold) !important; }
div[data-testid="stExpander"] { background: var(--card); border: 1px solid var(--border); border-radius: 8px; }
hr { border-color: var(--border) !important; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def get_key(tournament, *parts):
    return f"{tournament}__{'__'.join(str(p) for p in parts)}"

def d_get(key, default=None):
    return st.session_state.data.get(key, default)

def d_set(key, value):
    st.session_state.data[key] = value
    save_data(st.session_state.data)

def render_scorers(match_key):
    scorers = d_get(match_key + "__scorers", [])
    st.markdown("**⚽ Goleadores del partido**")
    cols = st.columns([2, 1, 1, 0.5])
    with cols[0]:
        player = st.text_input("Jugador", key=match_key + "_sp", placeholder="Nombre del jugador")
    with cols[1]:
        team = st.selectbox("Equipo", [""] + MLS_TEAMS, key=match_key + "_st")
    with cols[2]:
        minute = st.number_input("Min", 1, 120, 45, key=match_key + "_sm")
    with cols[3]:
        st.write("")
        st.write("")
        if st.button("➕", key=match_key + "_sb"):
            if player and team:
                scorers.append({"player": player, "team": team, "minute": minute})
                d_set(match_key + "__scorers", scorers)
                st.rerun()

    if scorers:
        html = ""
        for s in scorers:
            html += f'<span class="scorer-chip">⚽ {s["player"]} ({s["team"]}) <span class="min">{s["minute"]}\'</span></span>'
        st.markdown(html, unsafe_allow_html=True)
        del_idx = st.selectbox(
            "Eliminar goleador",
            range(len(scorers)),
            format_func=lambda i: f"{scorers[i]['player']} {scorers[i]['minute']}'",
            key=match_key + "_del"
        )
        if st.button("🗑️ Eliminar", key=match_key + "_delb"):
            scorers.pop(del_idx)
            d_set(match_key + "__scorers", scorers)
            st.rerun()


def render_match_result(t1, t2, match_key, prefix=""):
    result = d_get(match_key, {})
    st.markdown(f"""
    <div class="match-card">
        <div style="font-family:'Barlow Condensed',sans-serif;font-size:0.72rem;letter-spacing:2px;color:var(--muted);margin-bottom:10px">{prefix}</div>
        <div style="display:flex;align-items:center;gap:12px;justify-content:center;font-weight:700;font-size:1.1rem;">
            <span style="flex:1;text-align:right">{t1}</span>
            <span style="color:var(--gold);font-family:'Bebas Neue',sans-serif;font-size:1.3rem">VS</span>
            <span style="flex:1;text-align:left">{t2}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns([2, 1, 1, 2])
    with cols[1]:
        g1 = st.number_input(f"Goles {t1[:10]}", 0, 20, result.get("g1", 0), key=match_key + "_g1")
    with cols[2]:
        g2 = st.number_input(f"Goles {t2[:10]}", 0, 20, result.get("g2", 0), key=match_key + "_g2")

    col_save, col_status = st.columns([1, 1])
    with col_save:
        if st.button("💾 Guardar resultado", key=match_key + "_save"):
            d_set(match_key, {"g1": g1, "g2": g2, "played": True, "t1": t1, "t2": t2})
            st.rerun()
    with col_status:
        if result.get("played"):
            st.success(f"✅ {t1} {result.get('g1', 0)} - {result.get('g2', 0)} {t2}")

    render_scorers(match_key)
    return result.get("g1", 0), result.get("g2", 0), result.get("played", False)


def get_match_winner(match_key, t1, t2):
    r = d_get(match_key, {})
    if not r.get("played"):
        return "TBD"
    g1, g2 = r.get("g1", 0), r.get("g2", 0)
    if g1 > g2:
        return t1
    elif g2 > g1:
        return t2
    return t1


def compute_standings(teams, tournament, phase_prefix):
    table = {t: {"PJ": 0, "G": 0, "E": 0, "P": 0, "GF": 0, "GC": 0, "DG": 0, "PTS": 0} for t in teams}
    for key, result in st.session_state.data.items():
        if not key.startswith(phase_prefix):
            continue
        if not result.get("played"):
            continue
        t1, t2 = result.get("t1"), result.get("t2")
        if t1 not in table or t2 not in table:
            continue
        g1, g2 = result["g1"], result["g2"]
        table[t1]["PJ"] += 1
        table[t2]["PJ"] += 1
        table[t1]["GF"] += g1
        table[t1]["GC"] += g2
        table[t2]["GF"] += g2
        table[t2]["GC"] += g1
        table[t1]["DG"] = table[t1]["GF"] - table[t1]["GC"]
        table[t2]["DG"] = table[t2]["GF"] - table[t2]["GC"]
        if g1 > g2:
            table[t1]["G"] += 1
            table[t1]["PTS"] += 3
            table[t2]["P"] += 1
        elif g2 > g1:
            table[t2]["G"] += 1
            table[t2]["PTS"] += 3
            table[t1]["P"] += 1
        else:
            table[t1]["E"] += 1
            table[t1]["PTS"] += 1
            table[t2]["E"] += 1
            table[t2]["PTS"] += 1
    sorted_teams = sorted(table.keys(), key=lambda t: (-table[t]["PTS"], -table[t]["DG"], -table[t]["GF"]))
    return sorted_teams, table


def render_standings_table(teams_sorted, table, highlight=2):
    html = '<table class="stats-table"><thead><tr>'
    for col in ["#", "EQUIPO", "PJ", "G", "E", "P", "GF", "GC", "DG", "PTS"]:
        html += f"<th>{col}</th>"
    html += "</tr></thead><tbody>"
    colors = ["var(--gold)", "var(--blue)", "var(--green)"]
    for i, team in enumerate(teams_sorted):
        s = table[team]
        rank_color = colors[min(i, 2)] if i < highlight else "var(--muted)"
        qualifier = "✓ " if i < highlight else ""
        dg_color = "var(--green)" if s["DG"] >= 0 else "var(--red)"
        dg_str = f"+{s['DG']}" if s["DG"] > 0 else str(s["DG"])
        html += f"""<tr>
            <td style="color:{rank_color};font-weight:700">{i+1}</td>
            <td style="font-weight:600">{qualifier}{team}</td>
            <td>{s['PJ']}</td><td>{s['G']}</td><td>{s['E']}</td><td>{s['P']}</td>
            <td>{s['GF']}</td><td>{s['GC']}</td>
            <td style="color:{dg_color}">{dg_str}</td>
            <td style="color:var(--gold);font-weight:700">{s['PTS']}</td>
        </tr>"""
    html += "</tbody></table>"
    st.markdown(html, unsafe_allow_html=True)


def get_all_scorers(tournament):
    all_scorers = {}
    for key, val in st.session_state.data.items():
        if key.startswith(tournament) and key.endswith("__scorers"):
            for s in val:
                k = f"{s['player']}|{s['team']}"
                if k not in all_scorers:
                    all_scorers[k] = {"player": s["player"], "team": s["team"], "goals": 0, "minutes": []}
                all_scorers[k]["goals"] += 1
                all_scorers[k]["minutes"].append(s["minute"])
    return sorted(all_scorers.values(), key=lambda x: -x["goals"])


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:20px 0 10px">
        <div style="font-family:'Bebas Neue',sans-serif;font-size:2.2rem;color:var(--gold);letter-spacing:3px">MMJ</div>
        <div style="font-family:'Barlow Condensed',sans-serif;font-size:0.7rem;letter-spacing:4px;color:var(--muted)">TOURNAMENT HUB</div>
    </div><hr>
    """, unsafe_allow_html=True)

    tournament = st.selectbox(
        "🏆 Seleccionar Torneo",
        [
            "🏟️ Papa Johns Leagues Cup",
            "🥤 Cisco Super Cup",
            "🍔 McDonald's Community Cup"
        ]
    )

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("""<div style="font-size:0.75rem;color:var(--muted);text-align:center">
    MMJ Soccer League<br><span style="color:var(--gold)">Season 2025</span></div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE HEADER
# ═══════════════════════════════════════════════════════════════════════════════
TOURNAMENT_INFO = {
    "🏟️ Papa Johns Leagues Cup": ("MMJ PAPA JOHNS", "LEAGUES CUP", "30 TEAMS · 5 ZONES · PHASE FINAL"),
    "🥤 Cisco Super Cup": ("MMJ CISCO", "SUPER CUP", "STREAMLIT LEAGUE CHAMPION VS EMIRATES CUP CHAMPION"),
    "🍔 McDonald's Community Cup": ("MMJ McDONALD'S", "COMMUNITY CUP", "4 TEAMS · 2 SEMIFINALES · GRAN FINAL"),
}

info = TOURNAMENT_INFO[tournament]
st.markdown(f"""
<div style="padding:30px 0 20px;border-bottom:1px solid var(--border);margin-bottom:30px">
    <div class="hero-sub" style="margin-bottom:4px">{info[2]}</div>
    <div class="hero-title">{info[0]}<br>{info[1]}</div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAPA JOHNS LEAGUES CUP
# ═══════════════════════════════════════════════════════════════════════════════
if tournament == "🏟️ Papa Johns Leagues Cup":
    T = "pjlc"
    tabs = st.tabs(["🌍 PHASE ZONE", "🏆 PHASE FINAL", "📊 ESTADÍSTICAS"])

    # ── PHASE ZONE ──────────────────────────────────────────────────────────────
    with tabs[0]:
        zone_tabs = st.tabs(list(ZONES.keys()))

        for z_idx, (zone_name, zone_data) in enumerate(ZONES.items()):
            with zone_tabs[z_idx]:
                color = ZONE_COLORS[zone_name]
                teams = zone_data["teams"]
                fmt = zone_data["format"]

                st.markdown(f"""
                <div style="background:var(--card);border-left:4px solid {color};
                     padding:12px 16px;border-radius:0 8px 8px 0;margin-bottom:20px">
                    <div style="font-family:'Bebas Neue',sans-serif;font-size:1.8rem;color:{color};letter-spacing:2px">{zone_name}</div>
                    <div style="font-size:0.8rem;color:var(--muted)">{len(teams)} equipos · {"2 grupos" if fmt=="groups" else "Round Robin"}</div>
                </div>
                """, unsafe_allow_html=True)

                if fmt == "groups":
                    half = len(teams) // 2
                    groups = [teams[:half], teams[half:]]
                    group_cols = st.columns(2)

                    for g_idx, group_teams in enumerate(groups):
                        with group_cols[g_idx]:
                            label = "A" if g_idx == 0 else "B"
                            st.markdown(f"### GRUPO {label}")
                            prefix = get_key(T, zone_name, f"G{g_idx}")
                            teams_sorted, table = compute_standings(group_teams, T, prefix)
                            render_standings_table(teams_sorted, table, highlight=1)
                            with st.expander(f"📋 Partidos Grupo {label}"):
                                for i, t1 in enumerate(group_teams):
                                    for j, t2 in enumerate(group_teams):
                                        if i < j:
                                            mk = get_key(T, zone_name, f"G{g_idx}", t1, t2)
                                            render_match_result(t1, t2, mk, f"Grupo {label} · {zone_name}")

                    st.markdown("---")
                    st.markdown(f"### 🏅 ZONA FINAL — {zone_name}")
                    st.markdown("<div class='info-box'>Ganador Grupo A vs Ganador Grupo B → Campeón y Sub-Campeón avanzan a Phase Final</div>", unsafe_allow_html=True)

                    pfx_a = get_key(T, zone_name, "G0")
                    pfx_b = get_key(T, zone_name, "G1")
                    s_a, _ = compute_standings(groups[0], T, pfx_a)
                    s_b, _ = compute_standings(groups[1], T, pfx_b)
                    def_a = s_a[0] if s_a else groups[0][0]
                    def_b = s_b[0] if s_b else groups[1][0]

                    c1, c2 = st.columns(2)
                    with c1:
                        za = st.selectbox(f"Representante Grupo A", groups[0],
                                           index=groups[0].index(def_a) if def_a in groups[0] else 0,
                                           key=f"{zone_name}_za")
                    with c2:
                        zb = st.selectbox(f"Representante Grupo B", groups[1],
                                           index=groups[1].index(def_b) if def_b in groups[1] else 0,
                                           key=f"{zone_name}_zb")

                    zf_key = get_key(T, zone_name, "ZF")
                    render_match_result(za, zb, zf_key, f"ZONA FINAL · {zone_name}")
                    zf_r = d_get(zf_key, {})
                    if zf_r.get("played"):
                        zc = za if zf_r.get("g1", 0) >= zf_r.get("g2", 0) else zb
                        zs = zb if zf_r.get("g1", 0) >= zf_r.get("g2", 0) else za
                        d_set(get_key(T, zone_name, "champion"), zc)
                        d_set(get_key(T, zone_name, "runner_up"), zs)
                        st.success(f"🥇 Campeón: **{zc}** | 🥈 Sub-Campeón: **{zs}**")

                else:  # roundrobin
                    prefix = get_key(T, zone_name, "RR")
                    teams_sorted, table = compute_standings(teams, T, prefix)
                    render_standings_table(teams_sorted, table, highlight=zone_data["advance"])

                    with st.expander("📋 Todos los Partidos"):
                        for i, t1 in enumerate(teams):
                            for j, t2 in enumerate(teams):
                                if i < j:
                                    mk = get_key(T, zone_name, "RR", t1, t2)
                                    render_match_result(t1, t2, mk, f"{zone_name} · Round Robin")

                    st.markdown("---")
                    st.markdown(f"### 🏅 ZONA FINAL — {zone_name}")
                    advance = zone_data["advance"]
                    top = teams_sorted[:advance] if len(teams_sorted) >= advance else teams[:advance]

                    if advance >= 2:
                        st.markdown("<div class='info-box'>Los 2 mejores del Round Robin juegan la Zona Final</div>", unsafe_allow_html=True)
                        c1, c2 = st.columns(2)
                        with c1:
                            t1_s = st.selectbox("Finalista 1", teams,
                                                 index=teams.index(top[0]) if top[0] in teams else 0,
                                                 key=f"{zone_name}_f1")
                        with c2:
                            t2_s = st.selectbox("Finalista 2", teams,
                                                 index=teams.index(top[1]) if len(top) > 1 and top[1] in teams else 1,
                                                 key=f"{zone_name}_f2")
                        zf_key = get_key(T, zone_name, "ZF")
                        render_match_result(t1_s, t2_s, zf_key, f"ZONA FINAL · {zone_name}")
                        zf_r = d_get(zf_key, {})
                        if zf_r.get("played"):
                            zc = t1_s if zf_r.get("g1", 0) >= zf_r.get("g2", 0) else t2_s
                            zs = t2_s if zf_r.get("g1", 0) >= zf_r.get("g2", 0) else t1_s
                            d_set(get_key(T, zone_name, "champion"), zc)
                            d_set(get_key(T, zone_name, "runner_up"), zs)
                            if zone_name == "CANADIAN ZONE":
                                st.success(f"🥇 Campeón CZ: **{zc}** → Avanza a Phase Final")
                            else:
                                st.success(f"🥇 Campeón: **{zc}** | 🥈 Sub-Campeón: **{zs}**")
                    else:
                        st.markdown("<div class='info-box'>Solo el Campeón de Canadian Zone avanza a Phase Final</div>", unsafe_allow_html=True)
                        c1, c2 = st.columns(2)
                        with c1:
                            t1_s = st.selectbox("Finalista 1", teams,
                                                 index=0, key=f"{zone_name}_f1")
                        with c2:
                            t2_s = st.selectbox("Finalista 2", teams,
                                                 index=1, key=f"{zone_name}_f2")
                        zf_key = get_key(T, zone_name, "ZF")
                        render_match_result(t1_s, t2_s, zf_key, f"ZONA FINAL · {zone_name}")
                        zf_r = d_get(zf_key, {})
                        if zf_r.get("played"):
                            zc = t1_s if zf_r.get("g1", 0) >= zf_r.get("g2", 0) else t2_s
                            d_set(get_key(T, zone_name, "champion"), zc)
                            st.success(f"🥇 Campeón CZ: **{zc}** → Avanza a Phase Final")

    # ── PHASE FINAL ─────────────────────────────────────────────────────────────
    with tabs[1]:
        st.markdown('<div class="section-title">🏆 PHASE FINAL</div>', unsafe_allow_html=True)

        WZ_C = d_get(get_key(T, "WEST ZONE", "champion"), "WZ Champion")
        WZ_S = d_get(get_key(T, "WEST ZONE", "runner_up"), "WZ Sub-Champ")
        MZ_C = d_get(get_key(T, "MIDWEST ZONE", "champion"), "MZ Champion")
        MZ_S = d_get(get_key(T, "MIDWEST ZONE", "runner_up"), "MZ Sub-Champ")
        SZ_C = d_get(get_key(T, "SOUTH ZONE", "champion"), "SZ Champion")
        SZ_S = d_get(get_key(T, "SOUTH ZONE", "runner_up"), "SZ Sub-Champ")
        NZ_C = d_get(get_key(T, "NORTH ZONE", "champion"), "NZ Champion")
        CZ_C = d_get(get_key(T, "CANADIAN ZONE", "champion"), "CZ Champion")

        st.markdown("#### Clasificados — Selección Manual")
        st.markdown("<div class='info-box'>Puedes seleccionar los clasificados manualmente si las fases de zona aún no están completas</div>", unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            WZ_C = st.selectbox("WZ Campeón", MLS_TEAMS, index=MLS_TEAMS.index(WZ_C) if WZ_C in MLS_TEAMS else 0, key="pf_wzc")
            WZ_S = st.selectbox("WZ Sub-Campeón", MLS_TEAMS, index=MLS_TEAMS.index(WZ_S) if WZ_S in MLS_TEAMS else 1, key="pf_wzs")
        with c2:
            MZ_C = st.selectbox("MZ Campeón", MLS_TEAMS, index=MLS_TEAMS.index(MZ_C) if MZ_C in MLS_TEAMS else 0, key="pf_mzc")
            MZ_S = st.selectbox("MZ Sub-Campeón", MLS_TEAMS, index=MLS_TEAMS.index(MZ_S) if MZ_S in MLS_TEAMS else 1, key="pf_mzs")
        with c3:
            SZ_C = st.selectbox("SZ Campeón", MLS_TEAMS, index=MLS_TEAMS.index(SZ_C) if SZ_C in MLS_TEAMS else 0, key="pf_szc")
            SZ_S = st.selectbox("SZ Sub-Campeón", MLS_TEAMS, index=MLS_TEAMS.index(SZ_S) if SZ_S in MLS_TEAMS else 1, key="pf_szs")
        with c4:
            NZ_C = st.selectbox("NZ Campeón", MLS_TEAMS, index=MLS_TEAMS.index(NZ_C) if NZ_C in MLS_TEAMS else 0, key="pf_nzc")
            CZ_C = st.selectbox("CZ Campeón", MLS_TEAMS, index=MLS_TEAMS.index(CZ_C) if CZ_C in MLS_TEAMS else 0, key="pf_czc")

        st.markdown("---")

        # Bracket summary
        st.markdown(f"""
        <div style="background:var(--card);border:1px solid var(--border);border-radius:8px;padding:20px;margin-bottom:20px">
            <div style="font-family:'Bebas Neue',sans-serif;font-size:1.3rem;letter-spacing:3px;color:var(--gold);margin-bottom:12px">BRACKET CUARTOS DE FINAL</div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;font-size:0.9rem">
                <div>
                    <div style="font-family:'Barlow Condensed';font-size:0.75rem;letter-spacing:2px;color:var(--muted);margin-bottom:8px">LLAVE F1</div>
                    <div style="margin:4px 0"><span style="color:var(--gold)">A1:</span> {WZ_C} <span style="color:var(--muted)">vs</span> {SZ_S}</div>
                    <div style="margin:4px 0"><span style="color:var(--gold)">B1:</span> {NZ_C} <span style="color:var(--muted)">vs</span> {MZ_C}</div>
                </div>
                <div>
                    <div style="font-family:'Barlow Condensed';font-size:0.75rem;letter-spacing:2px;color:var(--muted);margin-bottom:8px">LLAVE F2</div>
                    <div style="margin:4px 0"><span style="color:var(--gold)">C1:</span> {CZ_C} <span style="color:var(--muted)">vs</span> {WZ_S}</div>
                    <div style="margin:4px 0"><span style="color:var(--gold)">D1:</span> {SZ_C} <span style="color:var(--muted)">vs</span> {MZ_S}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-title" style="font-size:1.4rem">CUARTOS DE FINAL</div>', unsafe_allow_html=True)

        qf1, qf2 = st.columns(2)
        with qf1:
            st.markdown("**F1 · A1 — WZ Campeón vs SZ Sub-Campeón**")
            mk_a1 = get_key(T, "PF", "A1")
            render_match_result(WZ_C, SZ_S, mk_a1, "Cuartos F1·A1")

            st.markdown("**F2 · C1 — CZ Campeón vs WZ Sub-Campeón**")
            mk_c1 = get_key(T, "PF", "C1")
            render_match_result(CZ_C, WZ_S, mk_c1, "Cuartos F2·C1")

        with qf2:
            st.markdown("**F1 · B1 — NZ Campeón vs MZ Campeón**")
            mk_b1 = get_key(T, "PF", "B1")
            render_match_result(NZ_C, MZ_C, mk_b1, "Cuartos F1·B1")

            st.markdown("**F2 · D1 — SZ Campeón vs MZ Sub-Campeón**")
            mk_d1 = get_key(T, "PF", "D1")
            render_match_result(SZ_C, MZ_S, mk_d1, "Cuartos F2·D1")

        a1_w = get_match_winner(mk_a1, WZ_C, SZ_S)
        b1_w = get_match_winner(mk_b1, NZ_C, MZ_C)
        c1_w = get_match_winner(mk_c1, CZ_C, WZ_S)
        d1_w = get_match_winner(mk_d1, SZ_C, MZ_S)

        st.markdown("---")
        st.markdown('<div class="section-title" style="font-size:1.4rem">SEMIFINALES</div>', unsafe_allow_html=True)

        sf1, sf2 = st.columns(2)
        with sf1:
            st.markdown(f"**SEMIFINAL F1: {a1_w} vs {b1_w}**")
            mk_sf1 = get_key(T, "PF", "SF1")
            render_match_result(a1_w, b1_w, mk_sf1, "Semifinal F1 (A1 vs B1)")
        with sf2:
            st.markdown(f"**SEMIFINAL F2: {c1_w} vs {d1_w}**")
            mk_sf2 = get_key(T, "PF", "SF2")
            render_match_result(c1_w, d1_w, mk_sf2, "Semifinal F2 (C1 vs D1)")

        sf1_w = get_match_winner(mk_sf1, a1_w, b1_w)
        sf2_w = get_match_winner(mk_sf2, c1_w, d1_w)

        st.markdown("---")
        st.markdown('<div class="section-title" style="font-size:1.8rem">🏆 GRAN FINAL</div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background:linear-gradient(135deg,var(--card),var(--dark3));
                    border:1px solid var(--border);border-radius:12px;padding:24px;text-align:center;margin:16px 0">
            <div style="font-family:'Barlow Condensed';font-size:0.8rem;letter-spacing:4px;color:var(--muted);margin-bottom:12px">GRAN FINAL · PAPA JOHNS LEAGUES CUP</div>
            <div style="display:flex;align-items:center;justify-content:center;gap:24px">
                <div><div style="font-size:0.7rem;color:var(--muted)">SEMIFINAL F1</div>
                     <div style="font-family:'Bebas Neue';font-size:1.8rem;color:var(--text)">{sf1_w}</div></div>
                <div style="font-family:'Bebas Neue';font-size:1.4rem;color:var(--gold)">VS</div>
                <div><div style="font-size:0.7rem;color:var(--muted)">SEMIFINAL F2</div>
                     <div style="font-family:'Bebas Neue';font-size:1.8rem;color:var(--text)">{sf2_w}</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        mk_gf = get_key(T, "PF", "GF")
        render_match_result(sf1_w, sf2_w, mk_gf, "🏆 GRAN FINAL · Papa Johns Leagues Cup")
        gf_r = d_get(mk_gf, {})
        if gf_r.get("played"):
            champion = get_match_winner(mk_gf, sf1_w, sf2_w)
            d_set(get_key(T, "champion"), champion)
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,rgba(245,197,24,0.18),rgba(245,197,24,0.04));
                        border:2px solid var(--gold);border-radius:12px;padding:30px;text-align:center;margin-top:20px">
                <div style="font-size:3rem">🏆</div>
                <div style="font-family:'Bebas Neue';font-size:1rem;letter-spacing:4px;color:var(--muted)">MMJ PAPA JOHNS LEAGUES CUP CHAMPION</div>
                <div style="font-family:'Bebas Neue';font-size:3rem;color:var(--gold);letter-spacing:4px">{champion}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── ESTADÍSTICAS ────────────────────────────────────────────────────────────
    with tabs[2]:
        st.markdown('<div class="section-title">📊 ESTADÍSTICAS DEL TORNEO</div>', unsafe_allow_html=True)

        scorers = get_all_scorers(T)
        if scorers:
            st.markdown("### ⚽ Tabla de Goleadores")
            html = '<table class="stats-table"><thead><tr><th>#</th><th>JUGADOR</th><th>EQUIPO</th><th>GOLES</th><th>MINUTOS</th></tr></thead><tbody>'
            for i, s in enumerate(scorers):
                mins = ", ".join(str(m) + "'" for m in sorted(s["minutes"]))
                medal = "🥇" if i == 0 else ("🥈" if i == 1 else ("🥉" if i == 2 else str(i + 1)))
                html += f"<tr><td>{medal}</td><td style='font-weight:600'>{s['player']}</td><td>{s['team']}</td><td style='color:var(--gold);font-weight:700'>{s['goals']}</td><td style='color:var(--muted);font-size:0.85rem'>{mins}</td></tr>"
            html += "</tbody></table>"
            st.markdown(html, unsafe_allow_html=True)
        else:
            st.info("No hay goleadores registrados aún. Registra los resultados de los partidos para ver estadísticas.")

        st.markdown("---")
        st.markdown("### 🗺️ Estado de las Zonas")
        zone_cols = st.columns(5)
        for i, (zname, _) in enumerate(ZONES.items()):
            with zone_cols[i]:
                champ = d_get(get_key(T, zname, "champion"), "TBD")
                sub = d_get(get_key(T, zname, "runner_up"), "TBD")
                color = ZONE_COLORS[zname]
                st.markdown(f"""
                <div style="background:var(--card);border-top:3px solid {color};border-radius:0 0 8px 8px;padding:14px;text-align:center">
                    <div style="font-family:'Barlow Condensed';font-size:0.7rem;letter-spacing:2px;color:{color};margin-bottom:8px">{zname}</div>
                    <div style="font-weight:700;font-size:0.95rem;margin:4px 0">🥇 {champ}</div>
                    <div style="font-size:0.82rem;color:var(--muted)">🥈 {sub}</div>
                </div>
                """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# CISCO SUPER CUP
# ═══════════════════════════════════════════════════════════════════════════════
elif tournament == "🥤 Cisco Super Cup":
    T = "csc"

    st.markdown("""
    <div class="info-box" style="font-size:0.95rem;margin-bottom:24px">
        La MMJ Cisco Super Cup enfrenta al <strong>Campeón de la MMJ Streamlit League</strong>
        contra el <strong>Campeón de la MMJ Emirates Cup</strong> en un partido único.
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🏆 Campeón Streamlit League")
        sl_champ = st.selectbox(
            "Seleccionar equipo", MLS_TEAMS,
            index=MLS_TEAMS.index(d_get(get_key(T, "sl_champ"), MLS_TEAMS[0])) if d_get(get_key(T, "sl_champ")) in MLS_TEAMS else 0,
            key="csc_sl"
        )
        d_set(get_key(T, "sl_champ"), sl_champ)

    with col2:
        st.markdown("#### 🏆 Campeón Emirates Cup")
        ec_champ = st.selectbox(
            "Seleccionar equipo", MLS_TEAMS,
            index=MLS_TEAMS.index(d_get(get_key(T, "ec_champ"), MLS_TEAMS[1])) if d_get(get_key(T, "ec_champ")) in MLS_TEAMS else 1,
            key="csc_ec"
        )
        d_set(get_key(T, "ec_champ"), ec_champ)

    st.markdown("---")

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,var(--card),var(--dark3));
                border:1px solid var(--border);border-radius:12px;padding:30px;text-align:center;margin:16px 0">
        <div style="font-family:'Barlow Condensed';font-size:0.8rem;letter-spacing:4px;color:var(--muted);margin-bottom:16px">MMJ CISCO SUPER CUP · GRAN FINAL</div>
        <div style="display:flex;align-items:center;justify-content:center;gap:30px">
            <div>
                <div style="font-size:0.7rem;color:var(--muted);letter-spacing:2px">STREAMLIT LEAGUE</div>
                <div style="font-family:'Bebas Neue';font-size:2.2rem;letter-spacing:2px">{sl_champ}</div>
            </div>
            <div style="font-family:'Bebas Neue';font-size:1.5rem;color:var(--gold)">VS</div>
            <div>
                <div style="font-size:0.7rem;color:var(--muted);letter-spacing:2px">EMIRATES CUP</div>
                <div style="font-family:'Bebas Neue';font-size:2.2rem;letter-spacing:2px">{ec_champ}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    mk_final = get_key(T, "final")
    render_match_result(sl_champ, ec_champ, mk_final, "MMJ Cisco Super Cup · Gran Final")
    gf_r = d_get(mk_final, {})
    if gf_r.get("played"):
        g1, g2 = gf_r.get("g1", 0), gf_r.get("g2", 0)
        champion = sl_champ if g1 > g2 else (ec_champ if g2 > g1 else sl_champ)
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,rgba(245,197,24,0.15),rgba(245,197,24,0.03));
                    border:2px solid var(--gold);border-radius:12px;padding:30px;text-align:center;margin-top:20px">
            <div style="font-size:3rem">🏆</div>
            <div style="font-family:'Bebas Neue';font-size:1rem;letter-spacing:4px;color:var(--muted)">MMJ CISCO SUPER CUP CHAMPION</div>
            <div style="font-family:'Bebas Neue';font-size:3rem;color:var(--gold);letter-spacing:4px">{champion}</div>
            <div style="font-size:1rem;color:var(--muted);margin-top:8px">{g1} - {g2}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📊 Goleadores")
    scorers = get_all_scorers(T)
    if scorers:
        html = '<table class="stats-table"><thead><tr><th>#</th><th>JUGADOR</th><th>EQUIPO</th><th>GOLES</th><th>MINUTOS</th></tr></thead><tbody>'
        for i, s in enumerate(scorers):
            mins = ", ".join(str(m) + "'" for m in sorted(s["minutes"]))
            medal = "🥇" if i == 0 else ("🥈" if i == 1 else str(i + 1))
            html += f"<tr><td>{medal}</td><td style='font-weight:600'>{s['player']}</td><td>{s['team']}</td><td style='color:var(--gold);font-weight:700'>{s['goals']}</td><td style='color:var(--muted);font-size:0.85rem'>{mins}</td></tr>"
        html += "</tbody></table>"
        st.markdown(html, unsafe_allow_html=True)
    else:
        st.info("No hay goleadores registrados aún.")


# ═══════════════════════════════════════════════════════════════════════════════
# McDONALD'S COMMUNITY CUP
# ═══════════════════════════════════════════════════════════════════════════════
elif tournament == "🍔 McDonald's Community Cup":
    T = "mcc"

    st.markdown("#### ⚙️ Configuración de Equipos")
    st.markdown("<div class='info-box'>Selecciona los equipos participantes. Los clasificados dependerán de los resultados de otros torneos MMJ.</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div style="background:var(--card);border-top:3px solid var(--green);border-radius:0 0 8px 8px;padding:12px 16px;margin-bottom:12px">
            <div style="font-family:'Barlow Condensed';font-size:0.75rem;letter-spacing:2px;color:var(--green)">SEMIFINAL A</div>
            <div style="font-size:0.82rem;color:var(--muted)">Campeón Streamlit League vs Último lugar de la Liga</div>
        </div>
        """, unsafe_allow_html=True)
        sl_champ = st.selectbox(
            "🏆 Campeón Streamlit League", MLS_TEAMS,
            index=MLS_TEAMS.index(d_get(get_key(T, "sl_champ"), MLS_TEAMS[0])) if d_get(get_key(T, "sl_champ")) in MLS_TEAMS else 0,
            key="mcc_sl"
        )
        d_set(get_key(T, "sl_champ"), sl_champ)
        last_place = st.selectbox(
            "📉 Último lugar de la Liga", MLS_TEAMS,
            index=MLS_TEAMS.index(d_get(get_key(T, "last_place"), MLS_TEAMS[-1])) if d_get(get_key(T, "last_place")) in MLS_TEAMS else len(MLS_TEAMS) - 1,
            key="mcc_lp"
        )
        d_set(get_key(T, "last_place"), last_place)

    with col2:
        st.markdown("""
        <div style="background:var(--card);border-top:3px solid var(--orange);border-radius:0 0 8px 8px;padding:12px 16px;margin-bottom:12px">
            <div style="font-family:'Barlow Condensed';font-size:0.75rem;letter-spacing:2px;color:var(--orange)">SEMIFINAL B</div>
            <div style="font-size:0.82rem;color:var(--muted)">Campeón Papa Johns Leagues Cup vs Campeón Emirates Cup</div>
        </div>
        """, unsafe_allow_html=True)
        pjlc_champ = st.selectbox(
            "🏟️ Campeón Papa Johns Leagues Cup", MLS_TEAMS,
            index=MLS_TEAMS.index(d_get(get_key(T, "pjlc_champ"), MLS_TEAMS[0])) if d_get(get_key(T, "pjlc_champ")) in MLS_TEAMS else 0,
            key="mcc_pj"
        )
        d_set(get_key(T, "pjlc_champ"), pjlc_champ)
        ec_champ = st.selectbox(
            "🏆 Campeón Emirates Cup", MLS_TEAMS,
            index=MLS_TEAMS.index(d_get(get_key(T, "ec_champ"), MLS_TEAMS[1])) if d_get(get_key(T, "ec_champ")) in MLS_TEAMS else 1,
            key="mcc_ec"
        )
        d_set(get_key(T, "ec_champ"), ec_champ)

    st.markdown("---")
    st.markdown('<div class="section-title">⚽ SEMIFINALES</div>', unsafe_allow_html=True)

    sf_col1, sf_col2 = st.columns(2)
    with sf_col1:
        st.markdown(f"### 🟢 SEMIFINAL A")
        mk_sfa = get_key(T, "SFA")
        render_match_result(sl_champ, last_place, mk_sfa, f"Semifinal A · {sl_champ} vs {last_place}")
        sfa_r = d_get(mk_sfa, {})
        sfa_w = "TBD"
        if sfa_r.get("played"):
            sfa_w = get_match_winner(mk_sfa, sl_champ, last_place)
            st.success(f"✅ Pasa a la Final: **{sfa_w}**")

    with sf_col2:
        st.markdown(f"### 🟠 SEMIFINAL B")
        mk_sfb = get_key(T, "SFB")
        render_match_result(pjlc_champ, ec_champ, mk_sfb, f"Semifinal B · {pjlc_champ} vs {ec_champ}")
        sfb_r = d_get(mk_sfb, {})
        sfb_w = "TBD"
        if sfb_r.get("played"):
            sfb_w = get_match_winner(mk_sfb, pjlc_champ, ec_champ)
            st.success(f"✅ Pasa a la Final: **{sfb_w}**")

    st.markdown("---")
    st.markdown('<div class="section-title">🏆 GRAN FINAL</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,var(--card),var(--dark3));
                border:1px solid var(--border);border-radius:12px;padding:28px;text-align:center;margin:16px 0">
        <div style="font-family:'Barlow Condensed';font-size:0.8rem;letter-spacing:4px;color:var(--muted);margin-bottom:14px">
            MMJ McDONALD'S COMMUNITY CUP · GRAN FINAL
        </div>
        <div style="display:flex;align-items:center;justify-content:center;gap:28px">
            <div><div style="font-size:0.7rem;color:var(--muted);letter-spacing:2px">SEMIFINAL A</div>
                 <div style="font-family:'Bebas Neue';font-size:2rem;letter-spacing:2px;color:var(--text)">{sfa_w}</div></div>
            <div style="font-family:'Bebas Neue';font-size:1.4rem;color:var(--gold)">VS</div>
            <div><div style="font-size:0.7rem;color:var(--muted);letter-spacing:2px">SEMIFINAL B</div>
                 <div style="font-family:'Bebas Neue';font-size:2rem;letter-spacing:2px;color:var(--text)">{sfb_w}</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    mk_gf = get_key(T, "GF")
    render_match_result(sfa_w, sfb_w, mk_gf, "🏆 Gran Final · McDonald's Community Cup")
    gf_r = d_get(mk_gf, {})
    if gf_r.get("played"):
        champion = get_match_winner(mk_gf, sfa_w, sfb_w)
        g1, g2 = gf_r.get("g1", 0), gf_r.get("g2", 0)
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,rgba(245,197,24,0.15),rgba(245,197,24,0.03));
                    border:2px solid var(--gold);border-radius:12px;padding:30px;text-align:center;margin-top:20px">
            <div style="font-size:3rem">🏆</div>
            <div style="font-family:'Bebas Neue';font-size:1rem;letter-spacing:4px;color:var(--muted)">MMJ McDONALD'S COMMUNITY CUP CHAMPION</div>
            <div style="font-family:'Bebas Neue';font-size:3rem;color:var(--gold);letter-spacing:4px">{champion}</div>
            <div style="font-size:1rem;color:var(--muted);margin-top:8px">{g1} - {g2}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📊 Goleadores del Torneo")
    scorers = get_all_scorers(T)
    if scorers:
        html = '<table class="stats-table"><thead><tr><th>#</th><th>JUGADOR</th><th>EQUIPO</th><th>GOLES</th><th>MINUTOS</th></tr></thead><tbody>'
        for i, s in enumerate(scorers):
            mins = ", ".join(str(m) + "'" for m in sorted(s["minutes"]))
            medal = "🥇" if i == 0 else ("🥈" if i == 1 else str(i + 1))
            html += f"<tr><td>{medal}</td><td style='font-weight:600'>{s['player']}</td><td>{s['team']}</td><td style='color:var(--gold);font-weight:700'>{s['goals']}</td><td style='color:var(--muted);font-size:0.85rem'>{mins}</td></tr>"
        html += "</tbody></table>"
        st.markdown(html, unsafe_allow_html=True)
    else:
        st.info("No hay goleadores registrados aún.")
