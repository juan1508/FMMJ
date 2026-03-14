import streamlit as st
import json
import os
from data import (
    TEAM_COMPOSITIONS, ZONE_TO_CODE, PLAYER_DATA,
    POS_COLORS, get_player_photo
)

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

# ─── TEAM LOOKUPS ─────────────────────────────────────────────────────────────
def get_code(display_name):
    return ZONE_TO_CODE.get(display_name, display_name)

def get_logo_url(display_name):
    code = get_code(display_name)
    return TEAM_COMPOSITIONS.get(code, {}).get("logo", "")

def get_team_players(display_name):
    code = get_code(display_name)
    return TEAM_COMPOSITIONS.get(code, {}).get("players", [])

def get_full_name(display_name):
    code = get_code(display_name)
    return TEAM_COMPOSITIONS.get(code, {}).get("name", display_name)

def logo_img(display_name, size=32):
    url = get_logo_url(display_name)
    if url:
        return f'<img src="{url}" width="{size}" height="{size}" style="object-fit:contain;vertical-align:middle;" onerror="this.style.display=\'none\'">'
    return ""

# ─── ZONES ────────────────────────────────────────────────────────────────────
ZONES = {
    "WEST ZONE":     {"teams": ["LAFC","LA Galaxy","San Jose","San Diego FC","Portland","RSL","Seattle","Colorado"],     "format":"groups",    "advance":2},
    "MIDWEST ZONE":  {"teams": ["Minnesota","Sporting KC","St. Louis","Chicago","Cincinnati","Columbus"],                "format":"groups",    "advance":2},
    "SOUTH ZONE":    {"teams": ["Dallas","Austin","Houston","Nashville","Charlotte","Atlanta","Orlando","Miami"],         "format":"groups",    "advance":2},
    "NORTH ZONE":    {"teams": ["DC United","Philadelphia","NYCFC","NY Red Bulls","New England"],                        "format":"roundrobin","advance":2},
    "CANADIAN ZONE": {"teams": ["Montreal","Toronto","Vancouver"],                                                       "format":"roundrobin","advance":1},
}

ZONE_COLORS = {
    "WEST ZONE":"#E67E22","MIDWEST ZONE":"#3498DB","SOUTH ZONE":"#2ECC71",
    "NORTH ZONE":"#9B59B6","CANADIAN ZONE":"#E74C3C",
}

ALL_DISPLAY = list(ZONE_TO_CODE.keys())

# ─── STYLES ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow:wght@300;400;600;700&family=Barlow+Condensed:wght@600;700&display=swap');
:root{--gold:#F5C518;--gold2:#E8A800;--dark:#0A0A0F;--dark2:#111118;--dark3:#1A1A24;--card:#16161F;--border:#2A2A3A;--text:#E8E8F0;--muted:#8888AA;--green:#2ECC71;--red:#E74C3C;--blue:#3498DB;--purple:#9B59B6;--orange:#E67E22;}
*{font-family:'Barlow',sans-serif;}
.stApp{background:var(--dark);color:var(--text);}
[data-testid="stSidebar"]{background:var(--dark2)!important;border-right:1px solid var(--border);}
[data-testid="stSidebar"] *{color:var(--text)!important;}
.hero-title{font-family:'Bebas Neue',sans-serif;font-size:3.5rem;letter-spacing:4px;background:linear-gradient(135deg,var(--gold),var(--gold2),#fff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;text-align:center;margin:0;line-height:1;}
.hero-sub{font-family:'Barlow Condensed',sans-serif;font-size:0.85rem;letter-spacing:6px;color:var(--muted);text-align:center;text-transform:uppercase;margin-top:4px;}
.section-title{font-family:'Bebas Neue',sans-serif;font-size:2rem;letter-spacing:3px;color:var(--gold);border-bottom:2px solid var(--border);padding-bottom:8px;margin-bottom:20px;}
.match-card{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:16px;margin:8px 0;}
.stats-table{width:100%;border-collapse:collapse;font-size:0.9rem;}
.stats-table th{background:var(--dark3);color:var(--gold);font-family:'Barlow Condensed',sans-serif;font-size:0.8rem;letter-spacing:2px;padding:10px 12px;text-align:left;border-bottom:2px solid var(--border);}
.stats-table td{padding:10px 12px;border-bottom:1px solid var(--border);color:var(--text);}
.stats-table tr:hover td{background:var(--dark3);}
.info-box{background:var(--card);border-left:3px solid var(--gold);border-radius:0 6px 6px 0;padding:12px 16px;margin:8px 0;font-size:0.9rem;color:var(--muted);}
.scorer-chip{display:inline-flex;align-items:center;gap:6px;background:var(--dark3);border:1px solid var(--border);border-radius:20px;padding:4px 10px;margin:3px;font-size:0.82rem;}
.scorer-chip .min{color:var(--gold);font-weight:700;}
.pos-badge{display:inline-block;padding:2px 7px;border-radius:3px;font-size:0.65rem;font-weight:700;font-family:'Barlow Condensed',sans-serif;letter-spacing:1px;}
.stButton>button{background:var(--gold)!important;color:#000!important;font-family:'Barlow Condensed',sans-serif!important;font-weight:700!important;letter-spacing:2px!important;border:none!important;border-radius:4px!important;}
.stButton>button:hover{background:var(--gold2)!important;}
.stTextInput input,.stNumberInput input{background:var(--dark3)!important;color:var(--text)!important;border:1px solid var(--border)!important;}
.stTabs [data-baseweb="tab-list"]{background:var(--dark2)!important;border-bottom:1px solid var(--border)!important;}
.stTabs [data-baseweb="tab"]{background:transparent!important;color:var(--muted)!important;font-family:'Barlow Condensed',sans-serif!important;font-weight:600!important;letter-spacing:1px!important;border-bottom:2px solid transparent!important;}
.stTabs [aria-selected="true"]{color:var(--gold)!important;border-bottom-color:var(--gold)!important;}
div[data-testid="stExpander"]{background:var(--card);border:1px solid var(--border);border-radius:8px;}
hr{border-color:var(--border)!important;}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# CORE HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def gk(tournament, *parts):
    return f"{tournament}__{'__'.join(str(p) for p in parts)}"

def d_get(key, default=None):
    return st.session_state.data.get(key, default)

def d_set(key, value):
    st.session_state.data[key] = value
    save_data(st.session_state.data)

def get_match_winner(match_key, t1, t2):
    r = d_get(match_key, {})
    if not r.get("played"):
        return "TBD"
    return t1 if r.get("g1", 0) >= r.get("g2", 0) else t2


def render_scorers(match_key, t1, t2):
    scorers = d_get(match_key + "__scorers", [])
    st.markdown("**⚽ Registrar Goleador**")

    t1_players = get_team_players(t1)
    t2_players = get_team_players(t2)
    all_players = [""] + t1_players + t2_players

    cols = st.columns([2, 1, 1, 0.6])
    with cols[0]:
        player = st.selectbox("Jugador", all_players, key=match_key + "_sp")
    with cols[1]:
        auto_team = t1 if player in t1_players else (t2 if player in t2_players else t1)
        team_opts = [t1, t2]
        team = st.selectbox("Equipo", team_opts, index=team_opts.index(auto_team), key=match_key + "_st")
    with cols[2]:
        minute = st.number_input("Min", 1, 120, 45, key=match_key + "_sm")
    with cols[3]:
        st.write(""); st.write("")
        if st.button("➕", key=match_key + "_sb"):
            if player:
                scorers.append({"player": player, "team": team, "minute": minute})
                d_set(match_key + "__scorers", scorers)
                st.rerun()

    if scorers:
        html = ""
        for s in scorers:
            pdata = PLAYER_DATA.get(s["player"], {})
            photo = get_player_photo(s["player"], pdata.get("sofifa", 0))
            html += f'<span class="scorer-chip"><img src="{photo}" width="26" height="26" style="border-radius:50%;object-fit:cover;" onerror="this.style.display=\'none\'"> <b>{s["player"]}</b> {logo_img(s["team"],14)} <span class="min">{s["minute"]}\'</span></span>'
        st.markdown(html, unsafe_allow_html=True)

        del_idx = st.selectbox("Eliminar", range(len(scorers)),
                               format_func=lambda i: f"{scorers[i]['player']} {scorers[i]['minute']}'",
                               key=match_key + "_del")
        if st.button("🗑️ Eliminar gol", key=match_key + "_delb"):
            scorers.pop(del_idx)
            d_set(match_key + "__scorers", scorers)
            st.rerun()


def render_match(t1, t2, match_key, label=""):
    result = d_get(match_key, {})
    st.markdown(f"""
    <div class="match-card">
        <div style="font-family:'Barlow Condensed';font-size:0.72rem;letter-spacing:2px;color:var(--muted);margin-bottom:12px">{label}</div>
        <div style="display:flex;align-items:center;justify-content:center;gap:16px">
            <div style="flex:1;text-align:right;display:flex;align-items:center;justify-content:flex-end;gap:10px">
                <span style="font-weight:700;font-size:1rem">{t1}</span>{logo_img(t1,40)}
            </div>
            <span style="font-family:'Bebas Neue';font-size:1.5rem;color:var(--gold);min-width:30px;text-align:center">VS</span>
            <div style="flex:1;text-align:left;display:flex;align-items:center;justify-content:flex-start;gap:10px">
                {logo_img(t2,40)}<span style="font-weight:700;font-size:1rem">{t2}</span>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        g1 = st.number_input(f"⚽ {t1}", 0, 20, result.get("g1", 0), key=match_key + "_g1")
    with c2:
        g2 = st.number_input(f"⚽ {t2}", 0, 20, result.get("g2", 0), key=match_key + "_g2")

    cs, cr = st.columns([1, 1])
    with cs:
        if st.button("💾 Guardar resultado", key=match_key + "_save"):
            d_set(match_key, {"g1": g1, "g2": g2, "played": True, "t1": t1, "t2": t2})
            st.rerun()
    with cr:
        if result.get("played"):
            st.success(f"✅ {t1} {result.get('g1',0)}–{result.get('g2',0)} {t2}")

    render_scorers(match_key, t1, t2)


def compute_standings(teams, prefix):
    table = {t: {"PJ":0,"G":0,"E":0,"P":0,"GF":0,"GC":0,"DG":0,"PTS":0} for t in teams}
    for key, result in st.session_state.data.items():
        if not key.startswith(prefix) or not result.get("played"):
            continue
        t1, t2 = result.get("t1"), result.get("t2")
        if not t1 or not t2 or t1 not in table or t2 not in table:
            continue
        g1, g2 = result["g1"], result["g2"]
        table[t1]["PJ"] += 1; table[t2]["PJ"] += 1
        table[t1]["GF"] += g1; table[t1]["GC"] += g2
        table[t2]["GF"] += g2; table[t2]["GC"] += g1
        table[t1]["DG"] = table[t1]["GF"] - table[t1]["GC"]
        table[t2]["DG"] = table[t2]["GF"] - table[t2]["GC"]
        if g1 > g2:   table[t1]["G"]+=1; table[t1]["PTS"]+=3; table[t2]["P"]+=1
        elif g2 > g1: table[t2]["G"]+=1; table[t2]["PTS"]+=3; table[t1]["P"]+=1
        else:
            table[t1]["E"]+=1; table[t1]["PTS"]+=1
            table[t2]["E"]+=1; table[t2]["PTS"]+=1
    return sorted(table.keys(), key=lambda t: (-table[t]["PTS"],-table[t]["DG"],-table[t]["GF"])), table


def render_standings(teams_sorted, table, highlight=2):
    html = '<table class="stats-table"><thead><tr>'
    for col in ["#","EQUIPO","PJ","G","E","P","GF","GC","DG","PTS"]:
        html += f"<th>{col}</th>"
    html += "</tr></thead><tbody>"
    rcolors = ["var(--gold)","var(--blue)","var(--green)"]
    for i, team in enumerate(teams_sorted):
        s = table[team]
        rc = rcolors[min(i,2)] if i < highlight else "var(--muted)"
        tick = "✓ " if i < highlight else ""
        dg = f"+{s['DG']}" if s["DG"]>0 else str(s["DG"])
        dgc = "var(--green)" if s["DG"]>=0 else "var(--red)"
        html += f"""<tr>
            <td style="color:{rc};font-weight:700">{i+1}</td>
            <td style="font-weight:600">{logo_img(team,22)}&nbsp;{tick}{team}</td>
            <td>{s['PJ']}</td><td>{s['G']}</td><td>{s['E']}</td><td>{s['P']}</td>
            <td>{s['GF']}</td><td>{s['GC']}</td>
            <td style="color:{dgc}">{dg}</td>
            <td style="color:var(--gold);font-weight:700">{s['PTS']}</td>
        </tr>"""
    html += "</tbody></table>"
    st.markdown(html, unsafe_allow_html=True)


def get_all_scorers(tournament):
    agg = {}
    for key, val in st.session_state.data.items():
        if key.startswith(tournament) and key.endswith("__scorers"):
            for s in val:
                k = f"{s['player']}|{s['team']}"
                if k not in agg:
                    agg[k] = {"player":s["player"],"team":s["team"],"goals":0,"minutes":[]}
                agg[k]["goals"] += 1
                agg[k]["minutes"].append(s["minute"])
    return sorted(agg.values(), key=lambda x: -x["goals"])


def render_scorers_table(scorers):
    if not scorers:
        st.info("No hay goleadores registrados aún.")
        return
    html = '<table class="stats-table"><thead><tr><th>#</th><th>FOTO</th><th>JUGADOR</th><th>EQUIPO</th><th>GOLES</th><th>MINUTOS</th></tr></thead><tbody>'
    for i, s in enumerate(scorers):
        pdata = PLAYER_DATA.get(s["player"], {})
        photo = get_player_photo(s["player"], pdata.get("sofifa", 0))
        pos = pdata.get("pos", "")
        poc = POS_COLORS.get(pos, "#888")
        medal = "🥇" if i==0 else ("🥈" if i==1 else ("🥉" if i==2 else str(i+1)))
        mins = ", ".join(str(m)+"'" for m in sorted(s["minutes"]))
        html += f"""<tr>
            <td>{medal}</td>
            <td><img src="{photo}" width="38" height="38" style="border-radius:50%;object-fit:cover;" onerror="this.style.display=\'none\'"></td>
            <td style="font-weight:600">{s['player']}<br><span class="pos-badge" style="background:{poc}22;color:{poc};border:1px solid {poc}44">{pos}</span></td>
            <td>{logo_img(s['team'],22)}&nbsp;{s['team']}</td>
            <td style="color:var(--gold);font-weight:700;font-size:1.2rem">{s['goals']}</td>
            <td style="color:var(--muted);font-size:0.85rem">{mins}</td>
        </tr>"""
    html += "</tbody></table>"
    st.markdown(html, unsafe_allow_html=True)


def big_match_card(t1, t2, subtitle=""):
    return f"""
    <div style="background:linear-gradient(135deg,var(--card),var(--dark3));border:1px solid var(--border);border-radius:12px;padding:28px;text-align:center;margin:12px 0">
        <div style="font-family:'Barlow Condensed';font-size:0.8rem;letter-spacing:4px;color:var(--muted);margin-bottom:16px">{subtitle}</div>
        <div style="display:flex;align-items:center;justify-content:center;gap:40px">
            <div style="text-align:center">
                <div style="margin-bottom:8px">{logo_img(t1,60)}</div>
                <div style="font-family:'Bebas Neue';font-size:1.6rem;letter-spacing:2px">{t1}</div>
                <div style="font-size:0.72rem;color:var(--muted)">{get_full_name(t1)}</div>
            </div>
            <div style="font-family:'Bebas Neue';font-size:1.5rem;color:var(--gold)">VS</div>
            <div style="text-align:center">
                <div style="margin-bottom:8px">{logo_img(t2,60)}</div>
                <div style="font-family:'Bebas Neue';font-size:1.6rem;letter-spacing:2px">{t2}</div>
                <div style="font-size:0.72rem;color:var(--muted)">{get_full_name(t2)}</div>
            </div>
        </div>
    </div>"""


def champion_card(champ, tournament_name):
    return f"""
    <div style="background:linear-gradient(135deg,rgba(245,197,24,0.18),rgba(245,197,24,0.04));border:2px solid var(--gold);border-radius:12px;padding:30px;text-align:center;margin-top:20px">
        <div style="font-size:3rem">🏆</div>
        <div style="font-family:'Bebas Neue';font-size:1rem;letter-spacing:4px;color:var(--muted)">{tournament_name} CHAMPION</div>
        <div style="margin:14px 0">{logo_img(champ,80)}</div>
        <div style="font-family:'Bebas Neue';font-size:3rem;color:var(--gold);letter-spacing:4px">{champ}</div>
        <div style="font-size:0.9rem;color:var(--muted);margin-top:4px">{get_full_name(champ)}</div>
    </div>"""


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:20px 0 10px">
        <div style="font-family:'Bebas Neue';font-size:2.2rem;color:var(--gold);letter-spacing:3px">MMJ</div>
        <div style="font-family:'Barlow Condensed';font-size:0.7rem;letter-spacing:4px;color:var(--muted)">TOURNAMENT HUB</div>
    </div><hr>""", unsafe_allow_html=True)

    tournament = st.selectbox("🏆 Seleccionar Torneo", [
        "🏟️ Papa Johns Leagues Cup",
        "🥤 Cisco Super Cup",
        "🍔 McDonald's Community Cup"
    ])

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.75rem;color:var(--muted);text-align:center">MMJ Soccer League<br><span style="color:var(--gold)">Season 2025</span></div>', unsafe_allow_html=True)


# ─── HEADER ───────────────────────────────────────────────────────────────────
TINFO = {
    "🏟️ Papa Johns Leagues Cup":   ("MMJ PAPA JOHNS","LEAGUES CUP",   "30 TEAMS · 5 ZONES · PHASE FINAL"),
    "🥤 Cisco Super Cup":          ("MMJ CISCO","SUPER CUP",           "STREAMLIT LEAGUE CHAMP VS EMIRATES CUP CHAMP"),
    "🍔 McDonald's Community Cup": ("MMJ McDONALD'S","COMMUNITY CUP", "4 TEAMS · 2 SEMIFINALES · GRAN FINAL"),
}
info = TINFO[tournament]
st.markdown(f"""
<div style="padding:30px 0 20px;border-bottom:1px solid var(--border);margin-bottom:30px">
    <div class="hero-sub" style="margin-bottom:4px">{info[2]}</div>
    <div class="hero-title">{info[0]}<br>{info[1]}</div>
</div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAPA JOHNS LEAGUES CUP
# ═══════════════════════════════════════════════════════════════════════════════
if tournament == "🏟️ Papa Johns Leagues Cup":
    T = "pjlc"
    tabs = st.tabs(["🌍 PHASE ZONE", "🏆 PHASE FINAL", "📊 ESTADÍSTICAS"])

    with tabs[0]:
        zone_tabs = st.tabs(list(ZONES.keys()))
        for z_idx, (zone_name, zone_data) in enumerate(ZONES.items()):
            with zone_tabs[z_idx]:
                color = ZONE_COLORS[zone_name]
                teams = zone_data["teams"]
                fmt   = zone_data["format"]

                logos_html = "".join(logo_img(t,28) for t in teams)
                st.markdown(f"""
                <div style="background:var(--card);border-left:4px solid {color};padding:14px 18px;border-radius:0 8px 8px 0;margin-bottom:20px">
                    <div style="font-family:'Bebas Neue';font-size:1.8rem;color:{color};letter-spacing:2px">{zone_name}</div>
                    <div style="font-size:0.8rem;color:var(--muted);margin-bottom:10px">{len(teams)} equipos · {"2 grupos" if fmt=="groups" else "Round Robin"}</div>
                    <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center">{logos_html}</div>
                </div>""", unsafe_allow_html=True)

                if fmt == "groups":
                    half   = len(teams) // 2
                    groups = [teams[:half], teams[half:]]
                    gcols  = st.columns(2)

                    for g_idx, grp in enumerate(groups):
                        with gcols[g_idx]:
                            lbl = "A" if g_idx == 0 else "B"
                            st.markdown(f"### GRUPO {lbl}")
                            pfx = gk(T, zone_name, f"G{g_idx}")
                            ts, tbl = compute_standings(grp, pfx)
                            render_standings(ts, tbl, highlight=1)
                            with st.expander(f"📋 Partidos Grupo {lbl}"):
                                for i, t1 in enumerate(grp):
                                    for j, t2 in enumerate(grp):
                                        if i < j:
                                            mk = gk(T, zone_name, f"G{g_idx}", t1, t2)
                                            render_match(t1, t2, mk, f"Grupo {lbl} · {zone_name}")
                                            st.markdown("---")

                    st.markdown("---")
                    st.markdown(f"### 🏅 ZONA FINAL — {zone_name}")
                    st.markdown("<div class='info-box'>Ganador Grupo A vs Ganador Grupo B → Campeón y Sub-Campeón avanzan a Phase Final</div>", unsafe_allow_html=True)

                    sa, _ = compute_standings(groups[0], gk(T, zone_name, "G0"))
                    sb, _ = compute_standings(groups[1], gk(T, zone_name, "G1"))
                    def_a  = sa[0] if sa else groups[0][0]
                    def_b  = sb[0] if sb else groups[1][0]

                    ca, cb = st.columns(2)
                    with ca:
                        za = st.selectbox("Rep. Grupo A", groups[0], index=groups[0].index(def_a) if def_a in groups[0] else 0, key=f"{zone_name}_za")
                    with cb:
                        zb = st.selectbox("Rep. Grupo B", groups[1], index=groups[1].index(def_b) if def_b in groups[1] else 0, key=f"{zone_name}_zb")

                    zf_key = gk(T, zone_name, "ZF")
                    st.markdown(big_match_card(za, zb, f"ZONA FINAL · {zone_name}"), unsafe_allow_html=True)
                    render_match(za, zb, zf_key, f"Zona Final · {zone_name}")
                    zf_r = d_get(zf_key, {})
                    if zf_r.get("played"):
                        zc = za if zf_r.get("g1",0) >= zf_r.get("g2",0) else zb
                        zs = zb if zc == za else za
                        d_set(gk(T, zone_name, "champion"), zc)
                        d_set(gk(T, zone_name, "runner_up"), zs)
                        st.success(f"🥇 Campeón: **{zc}** | 🥈 Sub-Campeón: **{zs}**")

                else:  # roundrobin
                    pfx = gk(T, zone_name, "RR")
                    ts, tbl = compute_standings(teams, pfx)
                    render_standings(ts, tbl, highlight=zone_data["advance"])

                    with st.expander("📋 Todos los partidos"):
                        for i, t1 in enumerate(teams):
                            for j, t2 in enumerate(teams):
                                if i < j:
                                    mk = gk(T, zone_name, "RR", t1, t2)
                                    render_match(t1, t2, mk, f"{zone_name} · Round Robin")
                                    st.markdown("---")

                    st.markdown("---")
                    st.markdown(f"### 🏅 ZONA FINAL — {zone_name}")
                    adv = zone_data["advance"]
                    top = ts[:adv] if len(ts) >= adv else teams[:adv]

                    cf1, cf2 = st.columns(2)
                    with cf1:
                        f1 = st.selectbox("Finalista 1", teams, index=teams.index(top[0]) if top[0] in teams else 0, key=f"{zone_name}_f1")
                    with cf2:
                        f2 = st.selectbox("Finalista 2", teams, index=teams.index(top[1]) if len(top)>1 and top[1] in teams else min(1,len(teams)-1), key=f"{zone_name}_f2")

                    zf_key = gk(T, zone_name, "ZF")
                    st.markdown(big_match_card(f1, f2, f"ZONA FINAL · {zone_name}"), unsafe_allow_html=True)
                    render_match(f1, f2, zf_key, f"Zona Final · {zone_name}")
                    zf_r = d_get(zf_key, {})
                    if zf_r.get("played"):
                        zc = f1 if zf_r.get("g1",0) >= zf_r.get("g2",0) else f2
                        zs = f2 if zc == f1 else f1
                        d_set(gk(T, zone_name, "champion"), zc)
                        d_set(gk(T, zone_name, "runner_up"), zs)
                        label_txt = f"🥇 Campeón CZ: **{zc}** → Avanza a Phase Final" if zone_name=="CANADIAN ZONE" else f"🥇 Campeón: **{zc}** | 🥈 Sub-Campeón: **{zs}**"
                        st.success(label_txt)

    with tabs[1]:
        st.markdown('<div class="section-title">🏆 PHASE FINAL</div>', unsafe_allow_html=True)

        WZ_C = d_get(gk(T,"WEST ZONE","champion"),    "LAFC")
        WZ_S = d_get(gk(T,"WEST ZONE","runner_up"),   "LA Galaxy")
        MZ_C = d_get(gk(T,"MIDWEST ZONE","champion"), "Minnesota")
        MZ_S = d_get(gk(T,"MIDWEST ZONE","runner_up"),"Sporting KC")
        SZ_C = d_get(gk(T,"SOUTH ZONE","champion"),   "Dallas")
        SZ_S = d_get(gk(T,"SOUTH ZONE","runner_up"),  "Austin")
        NZ_C = d_get(gk(T,"NORTH ZONE","champion"),   "DC United")
        CZ_C = d_get(gk(T,"CANADIAN ZONE","champion"),"Montreal")

        st.markdown("#### Clasificados — Selección Manual")
        st.markdown("<div class='info-box'>Los clasificados se actualizan automáticamente con los resultados de zona. Puedes ajustarlos manualmente aquí.</div>", unsafe_allow_html=True)

        c1,c2,c3,c4 = st.columns(4)
        with c1:
            WZ_C = st.selectbox("WZ Campeón",  ALL_DISPLAY, index=ALL_DISPLAY.index(WZ_C) if WZ_C in ALL_DISPLAY else 0, key="pf_wzc")
            WZ_S = st.selectbox("WZ Sub-Cam.", ALL_DISPLAY, index=ALL_DISPLAY.index(WZ_S) if WZ_S in ALL_DISPLAY else 1, key="pf_wzs")
        with c2:
            MZ_C = st.selectbox("MZ Campeón",  ALL_DISPLAY, index=ALL_DISPLAY.index(MZ_C) if MZ_C in ALL_DISPLAY else 0, key="pf_mzc")
            MZ_S = st.selectbox("MZ Sub-Cam.", ALL_DISPLAY, index=ALL_DISPLAY.index(MZ_S) if MZ_S in ALL_DISPLAY else 1, key="pf_mzs")
        with c3:
            SZ_C = st.selectbox("SZ Campeón",  ALL_DISPLAY, index=ALL_DISPLAY.index(SZ_C) if SZ_C in ALL_DISPLAY else 0, key="pf_szc")
            SZ_S = st.selectbox("SZ Sub-Cam.", ALL_DISPLAY, index=ALL_DISPLAY.index(SZ_S) if SZ_S in ALL_DISPLAY else 1, key="pf_szs")
        with c4:
            NZ_C = st.selectbox("NZ Campeón",  ALL_DISPLAY, index=ALL_DISPLAY.index(NZ_C) if NZ_C in ALL_DISPLAY else 0, key="pf_nzc")
            CZ_C = st.selectbox("CZ Campeón",  ALL_DISPLAY, index=ALL_DISPLAY.index(CZ_C) if CZ_C in ALL_DISPLAY else 0, key="pf_czc")

        st.markdown("---")
        st.markdown(f"""
        <div style="background:var(--card);border:1px solid var(--border);border-radius:10px;padding:20px;margin-bottom:20px">
            <div style="font-family:'Bebas Neue';font-size:1.3rem;letter-spacing:3px;color:var(--gold);margin-bottom:14px">BRACKET</div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px">
                <div>
                    <div style="font-family:'Barlow Condensed';font-size:0.75rem;letter-spacing:2px;color:var(--muted);margin-bottom:10px">LLAVE F1</div>
                    <div style="display:flex;align-items:center;gap:6px;margin:8px 0"><b style="color:var(--gold);min-width:24px">A1</b>{logo_img(WZ_C,20)}{WZ_C}<span style="color:var(--muted);margin:0 6px">vs</span>{logo_img(SZ_S,20)}{SZ_S}</div>
                    <div style="display:flex;align-items:center;gap:6px;margin:8px 0"><b style="color:var(--gold);min-width:24px">B1</b>{logo_img(NZ_C,20)}{NZ_C}<span style="color:var(--muted);margin:0 6px">vs</span>{logo_img(MZ_C,20)}{MZ_C}</div>
                </div>
                <div>
                    <div style="font-family:'Barlow Condensed';font-size:0.75rem;letter-spacing:2px;color:var(--muted);margin-bottom:10px">LLAVE F2</div>
                    <div style="display:flex;align-items:center;gap:6px;margin:8px 0"><b style="color:var(--gold);min-width:24px">C1</b>{logo_img(CZ_C,20)}{CZ_C}<span style="color:var(--muted);margin:0 6px">vs</span>{logo_img(WZ_S,20)}{WZ_S}</div>
                    <div style="display:flex;align-items:center;gap:6px;margin:8px 0"><b style="color:var(--gold);min-width:24px">D1</b>{logo_img(SZ_C,20)}{SZ_C}<span style="color:var(--muted);margin:0 6px">vs</span>{logo_img(MZ_S,20)}{MZ_S}</div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="section-title" style="font-size:1.4rem">CUARTOS DE FINAL</div>', unsafe_allow_html=True)
        q1, q2 = st.columns(2)

        with q1:
            st.markdown("**F1 · A1 — WZ Campeón vs SZ Sub-Cam.**")
            mk_a1 = gk(T,"PF","A1")
            st.markdown(big_match_card(WZ_C, SZ_S, "F1 · A1"), unsafe_allow_html=True)
            render_match(WZ_C, SZ_S, mk_a1, "Cuartos F1·A1")
            st.markdown("---")
            st.markdown("**F2 · C1 — CZ Campeón vs WZ Sub-Cam.**")
            mk_c1 = gk(T,"PF","C1")
            st.markdown(big_match_card(CZ_C, WZ_S, "F2 · C1"), unsafe_allow_html=True)
            render_match(CZ_C, WZ_S, mk_c1, "Cuartos F2·C1")

        with q2:
            st.markdown("**F1 · B1 — NZ Campeón vs MZ Campeón**")
            mk_b1 = gk(T,"PF","B1")
            st.markdown(big_match_card(NZ_C, MZ_C, "F1 · B1"), unsafe_allow_html=True)
            render_match(NZ_C, MZ_C, mk_b1, "Cuartos F1·B1")
            st.markdown("---")
            st.markdown("**F2 · D1 — SZ Campeón vs MZ Sub-Cam.**")
            mk_d1 = gk(T,"PF","D1")
            st.markdown(big_match_card(SZ_C, MZ_S, "F2 · D1"), unsafe_allow_html=True)
            render_match(SZ_C, MZ_S, mk_d1, "Cuartos F2·D1")

        a1_w = get_match_winner(mk_a1, WZ_C, SZ_S)
        b1_w = get_match_winner(mk_b1, NZ_C, MZ_C)
        c1_w = get_match_winner(mk_c1, CZ_C, WZ_S)
        d1_w = get_match_winner(mk_d1, SZ_C, MZ_S)

        st.markdown("---")
        st.markdown('<div class="section-title" style="font-size:1.4rem">SEMIFINALES</div>', unsafe_allow_html=True)
        sf1c, sf2c = st.columns(2)

        with sf1c:
            st.markdown("**SEMIFINAL F1 · A1 vs B1**")
            mk_sf1 = gk(T,"PF","SF1")
            st.markdown(big_match_card(a1_w, b1_w, "Semifinal F1"), unsafe_allow_html=True)
            render_match(a1_w, b1_w, mk_sf1, "Semifinal F1")

        with sf2c:
            st.markdown("**SEMIFINAL F2 · C1 vs D1**")
            mk_sf2 = gk(T,"PF","SF2")
            st.markdown(big_match_card(c1_w, d1_w, "Semifinal F2"), unsafe_allow_html=True)
            render_match(c1_w, d1_w, mk_sf2, "Semifinal F2")

        sf1_w = get_match_winner(mk_sf1, a1_w, b1_w)
        sf2_w = get_match_winner(mk_sf2, c1_w, d1_w)

        st.markdown("---")
        st.markdown('<div class="section-title" style="font-size:1.8rem">🏆 GRAN FINAL</div>', unsafe_allow_html=True)
        st.markdown(big_match_card(sf1_w, sf2_w, "GRAN FINAL · MMJ PAPA JOHNS LEAGUES CUP"), unsafe_allow_html=True)
        mk_gf = gk(T,"PF","GF")
        render_match(sf1_w, sf2_w, mk_gf, "🏆 Gran Final · Papa Johns Leagues Cup")
        gf_r = d_get(mk_gf, {})
        if gf_r.get("played"):
            champ = get_match_winner(mk_gf, sf1_w, sf2_w)
            d_set(gk(T,"champion"), champ)
            st.markdown(champion_card(champ, "MMJ PAPA JOHNS LEAGUES CUP"), unsafe_allow_html=True)

    with tabs[2]:
        st.markdown('<div class="section-title">📊 ESTADÍSTICAS DEL TORNEO</div>', unsafe_allow_html=True)
        st.markdown("### ⚽ Tabla de Goleadores")
        render_scorers_table(get_all_scorers(T))

        st.markdown("---")
        st.markdown("### 🗺️ Campeones por Zona")
        zcols = st.columns(5)
        for i, (zname, _) in enumerate(ZONES.items()):
            with zcols[i]:
                champ = d_get(gk(T,zname,"champion"), "TBD")
                sub   = d_get(gk(T,zname,"runner_up"), "TBD")
                color = ZONE_COLORS[zname]
                st.markdown(f"""
                <div style="background:var(--card);border-top:3px solid {color};border-radius:0 0 8px 8px;padding:14px;text-align:center">
                    <div style="font-family:'Barlow Condensed';font-size:0.7rem;letter-spacing:2px;color:{color};margin-bottom:8px">{zname}</div>
                    <div style="margin:8px 0">{logo_img(champ,40)}</div>
                    <div style="font-weight:700;font-size:0.9rem">🥇 {champ}</div>
                    <div style="margin-top:8px">{logo_img(sub,28)}</div>
                    <div style="font-size:0.82rem;color:var(--muted)">🥈 {sub}</div>
                </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# CISCO SUPER CUP
# ═══════════════════════════════════════════════════════════════════════════════
elif tournament == "🥤 Cisco Super Cup":
    T = "csc"

    st.markdown("<div class='info-box' style='font-size:0.95rem;margin-bottom:24px'>La MMJ Cisco Super Cup enfrenta al <strong>Campeón de la MMJ Streamlit League</strong> contra el <strong>Campeón de la MMJ Emirates Cup</strong> en un partido único.</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 🏆 Campeón Streamlit League")
        sl_champ = st.selectbox("Equipo", ALL_DISPLAY,
            index=ALL_DISPLAY.index(d_get(gk(T,"sl_champ"), ALL_DISPLAY[0])) if d_get(gk(T,"sl_champ")) in ALL_DISPLAY else 0,
            key="csc_sl")
        d_set(gk(T,"sl_champ"), sl_champ)
        st.markdown(f'<div style="text-align:center;padding:12px">{logo_img(sl_champ,72)}<br><span style="font-family:\'Bebas Neue\';font-size:1.1rem">{get_full_name(sl_champ)}</span></div>', unsafe_allow_html=True)

    with c2:
        st.markdown("#### 🏆 Campeón Emirates Cup")
        ec_champ = st.selectbox("Equipo", ALL_DISPLAY,
            index=ALL_DISPLAY.index(d_get(gk(T,"ec_champ"), ALL_DISPLAY[1])) if d_get(gk(T,"ec_champ")) in ALL_DISPLAY else 1,
            key="csc_ec")
        d_set(gk(T,"ec_champ"), ec_champ)
        st.markdown(f'<div style="text-align:center;padding:12px">{logo_img(ec_champ,72)}<br><span style="font-family:\'Bebas Neue\';font-size:1.1rem">{get_full_name(ec_champ)}</span></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(big_match_card(sl_champ, ec_champ, "MMJ CISCO SUPER CUP · GRAN FINAL"), unsafe_allow_html=True)
    mk_f = gk(T,"final")
    render_match(sl_champ, ec_champ, mk_f, "MMJ Cisco Super Cup · Gran Final")
    gf_r = d_get(mk_f, {})
    if gf_r.get("played"):
        champ = get_match_winner(mk_f, sl_champ, ec_champ)
        st.markdown(champion_card(champ, "MMJ CISCO SUPER CUP"), unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📊 Goleadores")
    render_scorers_table(get_all_scorers(T))


# ═══════════════════════════════════════════════════════════════════════════════
# McDONALD'S COMMUNITY CUP
# ═══════════════════════════════════════════════════════════════════════════════
elif tournament == "🍔 McDonald's Community Cup":
    T = "mcc"

    st.markdown("#### ⚙️ Configuración de Equipos")
    st.markdown("<div class='info-box'>Selecciona los equipos participantes.</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div style="background:var(--card);border-top:3px solid var(--green);border-radius:0 0 8px 8px;padding:12px 16px;margin-bottom:12px"><div style="font-family:\'Barlow Condensed\';font-size:0.75rem;letter-spacing:2px;color:var(--green)">SEMIFINAL A</div><div style="font-size:0.82rem;color:var(--muted)">Campeón Streamlit League vs Último lugar</div></div>', unsafe_allow_html=True)
        sl_champ = st.selectbox("🏆 Campeón Streamlit League", ALL_DISPLAY,
            index=ALL_DISPLAY.index(d_get(gk(T,"sl_champ"), ALL_DISPLAY[0])) if d_get(gk(T,"sl_champ")) in ALL_DISPLAY else 0,
            key="mcc_sl")
        d_set(gk(T,"sl_champ"), sl_champ)
        last_place = st.selectbox("📉 Último lugar de la Liga", ALL_DISPLAY,
            index=ALL_DISPLAY.index(d_get(gk(T,"last_place"), ALL_DISPLAY[-1])) if d_get(gk(T,"last_place")) in ALL_DISPLAY else len(ALL_DISPLAY)-1,
            key="mcc_lp")
        d_set(gk(T,"last_place"), last_place)

    with c2:
        st.markdown('<div style="background:var(--card);border-top:3px solid var(--orange);border-radius:0 0 8px 8px;padding:12px 16px;margin-bottom:12px"><div style="font-family:\'Barlow Condensed\';font-size:0.75rem;letter-spacing:2px;color:var(--orange)">SEMIFINAL B</div><div style="font-size:0.82rem;color:var(--muted)">Campeón Papa Johns Leagues Cup vs Campeón Emirates Cup</div></div>', unsafe_allow_html=True)
        pjlc_champ = st.selectbox("🏟️ Campeón Papa Johns Leagues Cup", ALL_DISPLAY,
            index=ALL_DISPLAY.index(d_get(gk(T,"pjlc_champ"), ALL_DISPLAY[0])) if d_get(gk(T,"pjlc_champ")) in ALL_DISPLAY else 0,
            key="mcc_pj")
        d_set(gk(T,"pjlc_champ"), pjlc_champ)
        ec_champ = st.selectbox("🏆 Campeón Emirates Cup", ALL_DISPLAY,
            index=ALL_DISPLAY.index(d_get(gk(T,"ec_champ"), ALL_DISPLAY[1])) if d_get(gk(T,"ec_champ")) in ALL_DISPLAY else 1,
            key="mcc_ec")
        d_set(gk(T,"ec_champ"), ec_champ)

    st.markdown("---")
    st.markdown('<div class="section-title">⚽ SEMIFINALES</div>', unsafe_allow_html=True)

    sf1c, sf2c = st.columns(2)
    with sf1c:
        st.markdown("### 🟢 SEMIFINAL A")
        mk_sfa = gk(T,"SFA")
        st.markdown(big_match_card(sl_champ, last_place, "Semifinal A"), unsafe_allow_html=True)
        render_match(sl_champ, last_place, mk_sfa, "Semifinal A")
        sfa_r = d_get(mk_sfa, {})
        sfa_w = get_match_winner(mk_sfa, sl_champ, last_place) if sfa_r.get("played") else "TBD"
        if sfa_r.get("played"):
            st.success(f"✅ Pasa a la Final: **{sfa_w}**")

    with sf2c:
        st.markdown("### 🟠 SEMIFINAL B")
        mk_sfb = gk(T,"SFB")
        st.markdown(big_match_card(pjlc_champ, ec_champ, "Semifinal B"), unsafe_allow_html=True)
        render_match(pjlc_champ, ec_champ, mk_sfb, "Semifinal B")
        sfb_r = d_get(mk_sfb, {})
        sfb_w = get_match_winner(mk_sfb, pjlc_champ, ec_champ) if sfb_r.get("played") else "TBD"
        if sfb_r.get("played"):
            st.success(f"✅ Pasa a la Final: **{sfb_w}**")

    st.markdown("---")
    st.markdown('<div class="section-title">🏆 GRAN FINAL</div>', unsafe_allow_html=True)
    st.markdown(big_match_card(sfa_w, sfb_w, "MMJ McDONALD'S COMMUNITY CUP · GRAN FINAL"), unsafe_allow_html=True)
    mk_gf = gk(T,"GF")
    render_match(sfa_w, sfb_w, mk_gf, "🏆 Gran Final · McDonald's Community Cup")
    gf_r = d_get(mk_gf, {})
    if gf_r.get("played"):
        champ = get_match_winner(mk_gf, sfa_w, sfb_w)
        st.markdown(champion_card(champ, "MMJ McDONALD'S COMMUNITY CUP"), unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📊 Goleadores")
    render_scorers_table(get_all_scorers(T))
