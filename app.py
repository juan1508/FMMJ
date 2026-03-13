"""
app.py - FMMJ Nations Competitions
Entrada manual de resultados · Diseño mejorado v3
"""
import streamlit as st
import pandas as pd
from itertools import combinations
from data import (
    UEFA_TEAMS, CONMEBOL_TEAMS, CAF_TEAMS, CONCACAF_TEAMS, AFC_TEAMS,
    PLAYOFF_TEAMS, PLAYERS, FLAG_MAP, INITIAL_FIFA_RANKING,
    ALL_TEAMS, COPA_AMERICA_GUESTS_POOL
)
from state import (
    init_state, flag, compute_standings, generate_group_matches,
    get_match_result, update_scorer, update_ranking_from_standings
)

st.set_page_config(
    page_title="FMMJ Nations",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
  --primary:   #6C63FF;
  --primary2:  #4B44CC;
  --accent:    #FF6B6B;
  --gold:      #FFD166;
  --green:     #06D6A0;
  --dark:      #0A0E1A;
  --card:      #111827;
  --card2:     #1A2235;
  --border:    rgba(108,99,255,0.18);
  --border2:   rgba(255,255,255,0.07);
  --txt:       #E8EBF4;
  --muted:     #6B7A99;
  --conf-uefa:    #4A90D9;
  --conf-conmebol:#27AE60;
  --conf-caf:     #F39C12;
  --conf-concacaf:#E74C3C;
  --conf-afc:     #9B59B6;
  --conf-mundial: #FFD166;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"] {
  font-family: 'Inter', sans-serif;
  background: var(--dark) !important;
  color: var(--txt) !important;
}

.stApp { background: var(--dark) !important; }
.block-container { padding-top: 1.5rem !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0D1220 0%, #111827 100%) !important;
  border-right: 1px solid var(--border2);
}
[data-testid="stSidebar"] * { color: var(--txt) !important; }

/* ── Buttons ── */
.stButton > button {
  background: linear-gradient(135deg, var(--primary), var(--primary2)) !important;
  color: #fff !important;
  font-family: 'Space Grotesk', sans-serif !important;
  font-size: 13px !important;
  font-weight: 600 !important;
  letter-spacing: 0.5px !important;
  border: none !important;
  border-radius: 8px !important;
  padding: 9px 20px !important;
  transition: all .2s ease !important;
  width: 100% !important;
}
.stButton > button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 24px rgba(108,99,255,.4) !important;
}

/* ── Headings ── */
h1, h2, h3, h4 {
  font-family: 'Space Grotesk', sans-serif !important;
  font-weight: 700 !important;
  color: var(--txt) !important;
}

/* ── Cards ── */
.card {
  background: var(--card);
  border: 1px solid var(--border2);
  border-radius: 12px;
  padding: 16px 20px;
  margin: 6px 0;
  transition: border-color .2s;
}
.card:hover { border-color: var(--border); }

/* ── Hero Banner ── */
.hero-wrap {
  background: linear-gradient(135deg, #0D1220 0%, #1a1040 50%, #0f1a2e 100%);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 48px 32px;
  text-align: center;
  margin-bottom: 24px;
  position: relative;
  overflow: hidden;
}
.hero-wrap::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle at 30% 50%, rgba(108,99,255,0.08) 0%, transparent 50%),
              radial-gradient(circle at 70% 50%, rgba(6,214,160,0.06) 0%, transparent 50%);
  pointer-events: none;
}
.hero-title {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 52px;
  font-weight: 900;
  letter-spacing: -1px;
  background: linear-gradient(135deg, #fff 0%, var(--primary) 50%, var(--green) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1;
}
.hero-sub {
  font-size: 13px;
  letter-spacing: 4px;
  color: var(--muted);
  text-transform: uppercase;
  margin-top: 8px;
}

/* ── Conf Header ── */
.conf-header {
  display: flex;
  align-items: center;
  gap: 14px;
  background: var(--card);
  border: 1px solid var(--border2);
  border-radius: 14px;
  padding: 18px 24px;
  margin-bottom: 20px;
}
.conf-icon {
  font-size: 36px;
  line-height: 1;
  flex-shrink: 0;
}
.conf-title {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 24px;
  font-weight: 700;
}
.conf-sub {
  font-size: 12px;
  color: var(--muted);
  margin-top: 2px;
  letter-spacing: 0.5px;
}

/* ── Match Row ── */
.match-row {
  background: var(--card2);
  border: 1px solid var(--border2);
  border-radius: 10px;
  padding: 12px 16px;
  margin: 4px 0;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: border-color .2s;
}
.match-row:hover { border-color: var(--border); }

/* ── Tables ── */
thead tr th {
  background: rgba(108,99,255,0.1) !important;
  color: var(--primary) !important;
  font-family: 'Space Grotesk', sans-serif !important;
  font-weight: 600 !important;
  font-size: 12px !important;
  letter-spacing: 0.5px !important;
}
tbody tr:hover td { background: rgba(108,99,255,0.04) !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab"] {
  font-family: 'Space Grotesk', sans-serif !important;
  font-weight: 600 !important;
  font-size: 14px !important;
}

/* ── Inputs ── */
.stSelectbox > label,
.stMultiSelect > label,
.stNumberInput > label {
  font-family: 'Inter', sans-serif !important;
  font-size: 12px !important;
  letter-spacing: 0.5px !important;
  color: var(--muted) !important;
  text-transform: uppercase !important;
  font-weight: 500 !important;
}

hr { border-color: var(--border2) !important; }

[data-testid="metric-container"] {
  background: var(--card);
  border: 1px solid var(--border2);
  border-radius: 12px;
  padding: 14px 18px;
}

/* ── Champion Banner ── */
.champ-banner {
  background: linear-gradient(135deg, #1a1508 0%, #2a1f00 50%, #1a1508 100%);
  border: 1px solid rgba(255,209,102,0.3);
  border-radius: 16px;
  text-align: center;
  padding: 36px 24px;
  margin: 12px 0;
}
.champ-flag  { font-size: 72px; line-height: 1; display: block; }
.champ-label { font-family:'Space Grotesk',sans-serif; font-size:13px; letter-spacing:4px; color:var(--gold); text-transform:uppercase; margin-top:16px; }
.champ-name  { font-family:'Space Grotesk',sans-serif; font-size:32px; font-weight:800; color:#fff; margin-top:4px; }

/* ── Team cards ── */
.team-chip {
  background: var(--card2);
  border: 1px solid var(--border2);
  border-radius: 10px;
  text-align: center;
  padding: 12px 8px;
  transition: border-color .2s;
}
.team-chip:hover { border-color: var(--border); }
.team-chip-flag { font-size: 28px; line-height: 1; display: block; }
.team-chip-name { font-size: 11px; color: var(--muted); margin-top: 5px; }

/* ── Badges ── */
.badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.5px;
}
.badge-green  { background: rgba(6,214,160,.12); color: var(--green); border: 1px solid rgba(6,214,160,.3); }
.badge-red    { background: rgba(255,107,107,.12); color: var(--accent); border: 1px solid rgba(255,107,107,.3); }
.badge-gold   { background: rgba(255,209,102,.12); color: var(--gold); border: 1px solid rgba(255,209,102,.3); }
.badge-purple { background: rgba(108,99,255,.12); color: var(--primary); border: 1px solid rgba(108,99,255,.3); }

/* ── Cup Status Cards ── */
.cup-card {
  background: var(--card);
  border: 1px solid var(--border2);
  border-radius: 12px;
  padding: 16px;
  text-align: center;
  transition: border-color .2s;
}
.cup-card:hover { border-color: var(--border); }
.cup-card-conf { font-size: 10px; letter-spacing: 2px; text-transform: uppercase; font-weight: 600; margin-bottom: 6px; }
.cup-card-name { font-size: 13px; font-weight: 600; margin-bottom: 10px; }
.cup-card-result { font-size: 13px; }

/* ── Sidebar nav buttons ── */
[data-testid="stSidebar"] .stButton > button {
  background: transparent !important;
  border: 1px solid var(--border2) !important;
  color: var(--txt) !important;
  text-align: left !important;
  justify-content: flex-start !important;
  font-size: 13px !important;
  font-weight: 500 !important;
  padding: 8px 12px !important;
  transition: all .2s !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background: rgba(108,99,255,0.12) !important;
  border-color: var(--primary) !important;
  transform: translateX(3px) !important;
  box-shadow: none !important;
}

/* ── Player cards ── */
.player-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(130px,1fr)); gap: 10px; margin-top: 10px; }
.player-card {
  background: var(--card2);
  border: 1px solid var(--border2);
  border-radius: 10px;
  padding: 12px 8px 10px;
  text-align: center;
  position: relative;
  transition: border-color .2s, transform .2s;
}
.player-card:hover { border-color: var(--primary); transform: translateY(-2px); }
.player-card::after {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  border-radius: 10px 10px 0 0;
}
.pos-GK::after { background: #F0A500; }
.pos-DF::after { background: #2196F3; }
.pos-MF::after { background: #4CAF50; }
.pos-FW::after { background: #F44336; }
.player-pos { display:inline-block; padding:2px 8px; border-radius:20px; font-size:10px; font-weight:700; margin-bottom:6px; }
.pos-GK-badge { background:rgba(240,165,0,.15); color:#F0A500; }
.pos-DF-badge { background:rgba(33,150,243,.15); color:#2196F3; }
.pos-MF-badge { background:rgba(76,175,80,.15); color:#4CAF50; }
.pos-FW-badge { background:rgba(244,67,54,.15); color:#F44336; }
.player-name { font-size: 12px; font-weight: 600; color: var(--txt); line-height: 1.3; min-height: 32px; display: flex; align-items: center; justify-content: center; }
.player-link { font-size: 10px; color: var(--primary); text-decoration: none; margin-top: 6px; display: block; opacity: .7; }
.player-link:hover { opacity: 1; }
.pos-section-title { font-family:'Space Grotesk',sans-serif; font-size:14px; font-weight:700; letter-spacing:2px; color:var(--muted); margin: 18px 0 8px; padding-bottom: 6px; border-bottom: 1px solid var(--border2); text-transform: uppercase; }

/* ── Squad header ── */
.squad-header {
  background: var(--card);
  border: 1px solid var(--border2);
  border-radius: 14px;
  padding: 20px 24px;
  margin-bottom: 18px;
  display: flex;
  align-items: center;
  gap: 18px;
}
.squad-flag { font-size: 60px; line-height: 1; }
.squad-name { font-family:'Space Grotesk',sans-serif; font-size: 28px; font-weight: 800; }
.squad-ranking { font-size: 12px; color: var(--muted); letter-spacing: 1px; margin-top: 2px; }
.squad-stats { display: flex; gap: 16px; margin-top: 10px; }
.squad-stat { text-align: center; }
.squad-stat-val { font-family:'Space Grotesk',sans-serif; font-size: 22px; font-weight: 700; color: var(--primary); }
.squad-stat-lbl { font-size: 10px; letter-spacing: 1px; color: var(--muted); text-transform: uppercase; margin-top: 2px; }

/* ── Progress bar (qualified) ── */
.progress-bar-wrap { background: var(--card2); border-radius: 8px; height: 8px; overflow: hidden; margin: 4px 0 2px; }
.progress-bar-fill { height: 100%; border-radius: 8px; background: linear-gradient(90deg, var(--primary), var(--green)); transition: width .5s ease; }
</style>
""", unsafe_allow_html=True)

init_state()

# ─── GLOBALS ───────────────────────────────────────────────────────────────

def fl(team):
    """Return flag emoji for a team, with fallback."""
    return FLAG_MAP.get(team, "🏳")

POS_COLOR = {"GK": "#F0A500", "DF": "#2196F3", "MF": "#4CAF50", "FW": "#F44336"}
POS_ICON  = {"GK": "🧤", "DF": "🛡", "MF": "⚡", "FW": "🔥"}
POS_LABEL = {"GK": "PORTEROS", "DF": "DEFENSAS", "MF": "CENTROCAMPISTAS", "FW": "DELANTEROS"}

CONF_COLORS = {
    "UEFA": "#4A90D9", "CONMEBOL": "#27AE60",
    "CAF": "#F39C12", "CONCACAF": "#E74C3C", "AFC": "#9B59B6"
}


def conf_team_map():
    return {
        "UEFA": UEFA_TEAMS, "CONMEBOL": CONMEBOL_TEAMS,
        "CAF": CAF_TEAMS, "CONCACAF": CONCACAF_TEAMS, "AFC": AFC_TEAMS
    }


# ─── STANDINGS ─────────────────────────────────────────────────────────────

def standings_df(standings, highlight=0, repechaje_pos=None):
    rows = []
    for s in standings:
        pos = s["pos"]
        team = s["team"]
        if pos <= highlight:
            st_txt = "✅ Clasifica"
        elif repechaje_pos and pos == repechaje_pos:
            st_txt = "🔄 Repechaje"
        else:
            st_txt = "❌"
        rows.append({
            "Pos": pos,
            "Equipo": f"{fl(team)} {team}",
            "Pts": s["pts"], "PJ": s["played"],
            "G": s["w"], "E": s["d"], "P": s["l"],
            "GF": s["gf"], "GC": s["ga"], "GD": s["gd"],
            "Estado": st_txt,
        })
    return pd.DataFrame(rows)


def render_standings(standings, title="", highlight=0, repechaje_pos=None):
    if title:
        st.markdown(f"#### {title}")
    if not standings:
        st.info("Sin datos aún.")
        return
    df = standings_df(standings, highlight, repechaje_pos)
    st.dataframe(df, hide_index=True, use_container_width=True)


# ─── MATCH HELPERS ─────────────────────────────────────────────────────────

def match_input_form(prefix, t1, t2, players_t1, players_t2, key_suffix=""):
    key_base = f"{prefix}_{t1}_{t2}_{key_suffix}"
    with st.expander(f"{fl(t1)} {t1}  vs  {fl(t2)} {t2}", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            hg = st.number_input(f"Goles {t1}", min_value=0, max_value=20, step=1, key=f"{key_base}_hg")
        with col2:
            ag = st.number_input(f"Goles {t2}", min_value=0, max_value=20, step=1, key=f"{key_base}_ag")

        scorers_h, scorers_a = [], []
        if hg > 0 and players_t1:
            st.markdown(f"<small style='color:var(--muted)'>⚽ Goleadores {t1}</small>", unsafe_allow_html=True)
            pnames = [p["name"] for p in players_t1]
            for g in range(int(hg)):
                scorer = st.selectbox(f"Gol {g+1}", ["(sin registrar)"] + pnames, key=f"{key_base}_sh_{g}")
                if scorer != "(sin registrar)":
                    scorers_h.append(scorer)

        if ag > 0 and players_t2:
            st.markdown(f"<small style='color:var(--muted)'>⚽ Goleadores {t2}</small>", unsafe_allow_html=True)
            pnames2 = [p["name"] for p in players_t2]
            for g in range(int(ag)):
                scorer = st.selectbox(f"Gol {g+1}", ["(sin registrar)"] + pnames2, key=f"{key_base}_sa_{g}")
                if scorer != "(sin registrar)":
                    scorers_a.append(scorer)

        if st.button("💾 Guardar resultado", key=f"{key_base}_save"):
            return int(hg), int(ag), scorers_h, scorers_a
    return None


def render_match_result(t1, t2, res):
    flag1 = fl(t1)
    flag2 = fl(t2)
    if res is None:
        st.markdown(
            f"<div class='match-row'>"
            f"<span style='font-size:20px'>{flag1}</span> "
            f"<span style='font-weight:600'>{t1}</span>"
            f"<span style='color:var(--muted);margin:0 8px'>vs</span>"
            f"<span style='font-weight:600'>{t2}</span> "
            f"<span style='font-size:20px'>{flag2}</span>"
            f"<span style='color:var(--muted);font-size:11px;margin-left:auto;letter-spacing:1px'>⏳ PENDIENTE</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
    else:
        hg = res.get("hg", 0)
        ag = res.get("ag", 0)
        hcolor = "#06D6A0" if hg > ag else "#FF6B6B" if hg < ag else "#888"
        acolor = "#06D6A0" if ag > hg else "#FF6B6B" if ag < hg else "#888"
        sh = " ".join(f"<span style='font-size:10px;color:var(--muted)'>⚽ {s}</span>" for s in res.get("scorers_h", []))
        sa = " ".join(f"<span style='font-size:10px;color:var(--muted)'>⚽ {s}</span>" for s in res.get("scorers_a", []))
        st.markdown(
            f"<div class='match-row'>"
            f"<span style='font-size:20px'>{flag1}</span> "
            f"<span style='color:{hcolor};font-weight:700'>{t1}</span>"
            f"<span style='background:var(--card);padding:4px 14px;border-radius:8px;"
            f"font-family:Space Grotesk;font-size:20px;font-weight:800;margin:0 12px;border:1px solid var(--border2);'>"
            f"{hg} – {ag}</span>"
            f"<span style='color:{acolor};font-weight:700'>{t2}</span> "
            f"<span style='font-size:20px'>{flag2}</span>"
            f"<span style='margin-left:auto;display:flex;gap:4px;flex-wrap:wrap;'>{sh} {sa}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )


def knockout_input(prefix, t1, t2, players_t1, players_t2, allow_draw=False):
    flag1 = fl(t1)
    flag2 = fl(t2)
    key_base = f"ko_{prefix}_{t1}_{t2}"
    with st.expander(f"⚔️ {flag1} {t1}  vs  {flag2} {t2}", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            hg = st.number_input(f"Goles {t1}", 0, 20, 0, key=f"{key_base}_hg")
        with col2:
            ag = st.number_input(f"Goles {t2}", 0, 20, 0, key=f"{key_base}_ag")

        winner = None
        penalty_winner = None
        if hg == ag and not allow_draw:
            st.markdown("<small style='color:#F0A500'>⚠️ Empate → definir por penaltis</small>", unsafe_allow_html=True)
            penalty_winner = st.selectbox("Ganador en penaltis", [t1, t2], key=f"{key_base}_pen")
            winner = penalty_winner
        elif hg > ag:
            winner = t1
        elif ag > hg:
            winner = t2

        scorers_h, scorers_a = [], []
        if hg > 0 and players_t1:
            pn = [p["name"] for p in players_t1]
            for g in range(int(hg)):
                s = st.selectbox(f"⚽ Gol {g+1} ({t1})", ["(sin registrar)"] + pn, key=f"{key_base}_sh{g}")
                if s != "(sin registrar)":
                    scorers_h.append(s)
        if ag > 0 and players_t2:
            pn2 = [p["name"] for p in players_t2]
            for g in range(int(ag)):
                s = st.selectbox(f"⚽ Gol {g+1} ({t2})", ["(sin registrar)"] + pn2, key=f"{key_base}_sa{g}")
                if s != "(sin registrar)":
                    scorers_a.append(s)

        if st.button("💾 Guardar", key=f"{key_base}_save"):
            if winner is None and hg == ag and not allow_draw:
                st.error("Debes elegir ganador en penaltis")
                return None
            if winner is None:
                winner = t1 if hg >= ag else t2
            return {
                "hg": int(hg), "ag": int(ag), "winner": winner,
                "penalty_winner": penalty_winner,
                "scorers_h": scorers_h, "scorers_a": scorers_a,
            }
    return None


def champ_banner(team, title="CAMPEÓN"):
    flag_emoji = fl(team)
    st.markdown(
        f"<div class='champ-banner'>"
        f"<span class='champ-flag'>{flag_emoji}</span>"
        f"<div class='champ-label'>🏆 {title}</div>"
        f"<div class='champ-name'>{team}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )


def conf_header(emoji, name, color, info=""):
    st.markdown(
        f"<div class='conf-header' style='border-left:4px solid {color};'>"
        f"<div class='conf-icon'>{emoji}</div>"
        f"<div>"
        f"<div class='conf-title' style='color:{color};'>{name}</div>"
        f"<div class='conf-sub'>{info}</div>"
        f"</div></div>",
        unsafe_allow_html=True,
    )


# ─── SIDEBAR ───────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(
        "<div style='text-align:center;padding:20px 0 12px;'>"
        "<div style='font-family:Space Grotesk;font-size:28px;font-weight:900;"
        "background:linear-gradient(135deg,#6C63FF,#06D6A0);-webkit-background-clip:text;"
        "-webkit-text-fill-color:transparent;background-clip:text;letter-spacing:-0.5px;'>FMMJ</div>"
        "<div style='font-size:9px;letter-spacing:4px;color:#6B7A99;margin-top:2px;'>NATIONS COMPETITION</div>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.divider()

    # Progress bar
    nq = len(st.session_state.wc_qualified)
    pct = int(nq / 32 * 100)
    st.markdown(
        f"<div style='margin:0 0 12px;'>"
        f"<div style='display:flex;justify-content:space-between;font-size:11px;color:var(--muted);margin-bottom:4px;'>"
        f"<span>Clasificados al Mundial</span><span style='color:var(--green);font-weight:700;'>{nq}/32</span></div>"
        f"<div class='progress-bar-wrap'><div class='progress-bar-fill' style='width:{pct}%'></div></div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # Navigation sections
    NAV_SECTIONS = [
        ("", [
            ("🏠", "Inicio"),
        ]),
        ("COPAS CONTINENTALES", [
            ("🌍", "Eurocopa UEFA"),
            ("🌎", "Copa América CONMEBOL"),
            ("🌍", "Copa África CAF"),
            ("🌎", "Copa Oro CONCACAF"),
            ("🌏", "Copa Asia AFC"),
        ]),
        ("PLAYOFFS MUNDIALISTAS", [
            ("🔢", "Playoffs UEFA"),
            ("🔢", "Playoffs CONMEBOL"),
            ("🔢", "Playoffs CAF"),
            ("🔢", "Playoffs CONCACAF"),
            ("🔢", "Playoffs AFC"),
            ("🔄", "Repechaje Internacional"),
        ]),
        ("MUNDIAL", [
            ("🏆", "Copa del Mundo"),
        ]),
        ("ESTADÍSTICAS", [
            ("📊", "Ranking FIFA"),
            ("⚽", "Goleadores"),
            ("👥", "Plantillas"),
        ]),
    ]

    for section_title, items in NAV_SECTIONS:
        if section_title:
            st.markdown(
                f"<div style='font-size:9px;letter-spacing:2px;color:var(--muted);font-weight:700;"
                f"text-transform:uppercase;margin:12px 0 6px 4px;'>{section_title}</div>",
                unsafe_allow_html=True,
            )
        for emoji, label in items:
            page_key = f"{emoji} {label}"
            if st.button(f"{emoji} {label}", key=f"nav_{page_key}", use_container_width=True):
                st.session_state.active_page = page_key
                st.rerun()

    st.divider()
    st.markdown(
        f"<div style='text-align:center;font-size:11px;color:var(--muted);'>Temporada {st.session_state.season}</div>",
        unsafe_allow_html=True,
    )

page = st.session_state.active_page


# ══════════════════════════════════════════════════════════════════════════════
# INICIO
# ══════════════════════════════════════════════════════════════════════════════
if page == "🏠 Inicio":
    st.markdown(
        "<div class='hero-wrap'>"
        "<div class='hero-title'>FMMJ NATIONS</div>"
        f"<div class='hero-sub'>Competencias de Naciones · Temporada {st.session_state.season}</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Clasificados", f"{len(st.session_state.wc_qualified)}/32")
    champ = st.session_state.wc_champion or "—"
    c2.metric("🏆 Campeón", champ)
    rnk1 = max(st.session_state.fifa_ranking, key=st.session_state.fifa_ranking.get)
    c3.metric("Ranking #1", f"{fl(rnk1)} {rnk1}")
    c4.metric("Temporada", st.session_state.season)

    st.divider()
    st.markdown("### 🏟️ Estado de Copas Continentales")

    cups = [
        ("Eurocopa", "euro_champion", "UEFA", "#4A90D9", "🌍"),
        ("Copa América", "ca_champion", "CONMEBOL", "#27AE60", "🌎"),
        ("Copa África", "af_champion", "CAF", "#F39C12", "🌍"),
        ("Copa Oro", "co_champion", "CONCACAF", "#E74C3C", "🌎"),
        ("Copa Asia", "as_champion", "AFC", "#9B59B6", "🌏"),
    ]
    cols = st.columns(5)
    for col, (name, key, conf, color, em) in zip(cols, cups):
        champ_val = st.session_state.get(key)
        with col:
            if champ_val:
                result_html = f"<div style='font-size:28px;'>{fl(champ_val)}</div><div style='font-size:12px;font-weight:600;color:#fff;margin-top:4px;'>{champ_val}</div>"
            else:
                result_html = f"<div style='color:var(--muted);font-size:12px;'>⏳ Pendiente</div>"
            st.markdown(
                f"<div class='cup-card' style='border-top:3px solid {color};'>"
                f"<div class='cup-card-conf' style='color:{color};'>{em} {conf}</div>"
                f"<div class='cup-card-name'>{name}</div>"
                f"<div class='cup-card-result'>{result_html}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    # Classified teams
    if st.session_state.wc_qualified:
        st.divider()
        st.markdown("### ✅ Clasificados al Mundial")
        teams = st.session_state.wc_qualified
        cols_per_row = 8
        for i in range(0, len(teams), cols_per_row):
            row_teams = teams[i:i+cols_per_row]
            cols = st.columns(cols_per_row)
            for j, t in enumerate(row_teams):
                with cols[j]:
                    st.markdown(
                        f"<div class='team-chip'>"
                        f"<span class='team-chip-flag'>{fl(t)}</span>"
                        f"<div class='team-chip-name'>{t}</div>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

    if st.session_state.wc_champion:
        st.divider()
        champ_banner(st.session_state.wc_champion, "CAMPEÓN DEL MUNDO")
        if st.button("🔄 Nueva Temporada"):
            st.session_state.season_history.append({
                "season": st.session_state.season,
                "champion": st.session_state.wc_champion,
                "ranking": dict(st.session_state.fifa_ranking),
            })
            st.session_state.season += 1
            keys_reset = [k for k in st.session_state if k not in
                          ["fifa_ranking", "season", "season_history", "active_page", "top_scorers"]]
            for k in keys_reset:
                del st.session_state[k]
            init_state()
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# EUROCOPA
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🌍 Eurocopa UEFA":
    conf_header("🌍", "EUROCOPA UEFA", "#4A90D9",
                "24 equipos · 6 grupos de 4 · Pasan 2 por grupo + 4 mejores 3ros → R16")

    tab_setup, tab_groups, tab_ko, tab_result = st.tabs(["⚙️ Configurar", "📊 Grupos", "🎯 Eliminatorias", "🏆 Resultado"])

    with tab_setup:
        st.markdown("#### Selecciona y arma los 6 grupos (4 equipos c/u)")
        _euro_default = [t for t in (st.session_state.euro_teams or UEFA_TEAMS[:24]) if t in UEFA_TEAMS]
        selected = st.multiselect("Elige 24 equipos UEFA", UEFA_TEAMS,
                          default=_euro_default, max_selections=24)
        if len(selected) == 24:
            st.session_state.euro_teams = selected
            st.markdown("---")
            st.markdown("**Asigna equipos a cada grupo:**")
            cols = st.columns(3)
            group_labels = ["A", "B", "C", "D", "E", "F"]
            new_groups = {}
            for i, gl in enumerate(group_labels):
                with cols[i % 3]:
                    st.markdown(f"**Grupo {gl}**")
                    default_g = [t for t in st.session_state.euro_groups.get(gl, selected[i*4:(i+1)*4]) if t in selected]
                    chosen = st.multiselect(f"Grupo {gl}", selected, default=default_g,
                                            max_selections=4, key=f"euro_grp_{gl}")
                    new_groups[gl] = chosen

            if st.button("💾 Guardar grupos"):
                all_assigned = sum(new_groups.values(), [])
                if len(all_assigned) != len(set(all_assigned)):
                    st.error("Un equipo está en más de un grupo.")
                elif any(len(v) != 4 for v in new_groups.values()):
                    st.error("Cada grupo debe tener exactamente 4 equipos.")
                else:
                    st.session_state.euro_groups = new_groups
                    all_matches = {}
                    for gl, teams in new_groups.items():
                        all_matches.update(generate_group_matches(teams))
                    st.session_state.euro_matches = all_matches
                    st.success("✅ Grupos guardados.")
                    st.rerun()
        else:
            st.info(f"Selecciona exactamente 24 equipos. Tienes {len(selected)}.")

    with tab_groups:
        if not st.session_state.euro_groups:
            st.info("Configura los grupos primero.")
        else:
            group_labels = ["A", "B", "C", "D", "E", "F"]
            for gl in group_labels:
                teams = st.session_state.euro_groups.get(gl, [])
                if not teams:
                    continue
                flags_str = " · ".join(f"{fl(t)} {t}" for t in teams)
                with st.expander(f"🗂️ Grupo {gl} — {flags_str}", expanded=True):
                    col_m, col_t = st.columns([3, 2])
                    with col_m:
                        st.markdown("**Partidos**")
                        for t1, t2 in combinations(teams, 2):
                            key = (t1, t2) if (t1, t2) in st.session_state.euro_matches else (t2, t1)
                            res = st.session_state.euro_matches.get(key)
                            render_match_result(t1, t2, res)
                            if res is None:
                                r = match_input_form("euro", t1, t2,
                                                     PLAYERS.get(t1, []), PLAYERS.get(t2, []), key_suffix=gl)
                                if r:
                                    hg, ag, sh, sa = r
                                    st.session_state.euro_matches[key] = {"hg": hg, "ag": ag, "scorers_h": sh, "scorers_a": sa}
                                    for s in sh: update_scorer(s, t1, 1, "euro_")
                                    for s in sa: update_scorer(s, t2, 1, "euro_")
                                    st.rerun()
                    with col_t:
                        st.markdown("**Posiciones**")
                        group_m = {k: v for k, v in st.session_state.euro_matches.items()
                                   if k[0] in teams and k[1] in teams and v is not None}
                        standings = compute_standings(teams, group_m)
                        st.session_state.euro_standings[gl] = standings
                        render_standings(standings, highlight=2)

            st.divider()
            st.markdown("#### 📋 Clasificados al R16")
            all_standings = st.session_state.euro_standings
            if len(all_standings) == 6:
                qualifiers_r16 = []
                third_places = []
                for gl in group_labels:
                    s = all_standings.get(gl, [])
                    if len(s) >= 2:
                        qualifiers_r16.append((f"{gl}1", s[0]["team"]))
                        qualifiers_r16.append((f"{gl}2", s[1]["team"]))
                    if len(s) >= 3:
                        third_places.append((gl, s[2]))

                third_sorted = sorted(third_places, key=lambda x: (x[1]["pts"], x[1]["gd"], x[1]["gf"]), reverse=True)
                best_thirds = [(f"{gl}3*", s["team"]) for gl, s in third_sorted[:4]]
                all_r16 = qualifiers_r16 + best_thirds

                cols = st.columns(4)
                for i, (lbl, t) in enumerate(all_r16):
                    with cols[i % 4]:
                        st.markdown(
                            f"<div class='team-chip'>"
                            f"<span style='font-size:10px;color:var(--muted);'>{lbl}</span><br>"
                            f"<span style='font-size:24px;'>{fl(t)}</span><br>"
                            f"<span style='font-size:11px;'>{t}</span></div>",
                            unsafe_allow_html=True,
                        )

                if st.button("➡️ Generar R16") and len(all_r16) == 16:
                    by_slot = {lbl: t for lbl, t in all_r16}
                    r16_pairs = [
                        (by_slot.get("A1","?"), by_slot.get("C2","?")),
                        (by_slot.get("D1","?"), by_slot.get("F2","?")),
                        (by_slot.get("B1","?"), by_slot.get("E2","?")),
                        (by_slot.get("A2","?"), by_slot.get("B2","?")),
                        (by_slot.get("C1","?"), by_slot.get("D2","?")),
                        (by_slot.get("E1","?"), by_slot.get("F1","?")),
                        (best_thirds[0][1] if best_thirds else "?", best_thirds[1][1] if len(best_thirds)>1 else "?"),
                        (best_thirds[2][1] if len(best_thirds)>2 else "?", best_thirds[3][1] if len(best_thirds)>3 else "?"),
                    ]
                    st.session_state.euro_r16 = r16_pairs
                    st.session_state.euro_r16_results = {}
                    st.success("✅ R16 generado.")
                    st.rerun()

    with tab_ko:
        if not st.session_state.euro_r16:
            st.info("Completa los grupos y genera el R16 primero.")
        else:
            st.markdown("### ⚔️ Octavos de Final (R16)")
            r16_winners = []
            for i, (t1, t2) in enumerate(st.session_state.euro_r16):
                res = st.session_state.euro_r16_results.get(i)
                if res:
                    render_match_result(t1, t2, res)
                    r16_winners.append(res["winner"])
                else:
                    r = knockout_input(f"euro_r16_{i}", t1, t2, PLAYERS.get(t1,[]), PLAYERS.get(t2,[]))
                    if r:
                        st.session_state.euro_r16_results[i] = r
                        for s in r.get("scorers_h",[]): update_scorer(s, t1, 1, "euro_")
                        for s in r.get("scorers_a",[]): update_scorer(s, t2, 1, "euro_")
                        st.rerun()
                    r16_winners.append(None)

            if all(r16_winners) and len(r16_winners) == 8:
                if not st.session_state.euro_qf:
                    st.session_state.euro_qf = [(r16_winners[i], r16_winners[i+1]) for i in range(0, 8, 2)]

                st.markdown("### ⚔️ Cuartos de Final")
                qf_winners = []
                for i, (t1, t2) in enumerate(st.session_state.euro_qf):
                    if t1 is None or t2 is None: continue
                    res = st.session_state.euro_qf_results.get(i)
                    if res:
                        render_match_result(t1, t2, res)
                        qf_winners.append(res["winner"])
                    else:
                        r = knockout_input(f"euro_qf_{i}", t1, t2, PLAYERS.get(t1,[]), PLAYERS.get(t2,[]))
                        if r:
                            st.session_state.euro_qf_results[i] = r
                            for s in r.get("scorers_h",[]): update_scorer(s, t1, 1, "euro_")
                            for s in r.get("scorers_a",[]): update_scorer(s, t2, 1, "euro_")
                            st.rerun()
                        qf_winners.append(None)

                if all(qf_winners) and len(qf_winners) == 4:
                    if not st.session_state.euro_sf:
                        st.session_state.euro_sf = [(qf_winners[0], qf_winners[1]), (qf_winners[2], qf_winners[3])]

                    st.markdown("### ⚔️ Semifinales")
                    sf_winners = []
                    sf_losers = []
                    for i, (t1, t2) in enumerate(st.session_state.euro_sf):
                        if t1 is None or t2 is None: continue
                        res = st.session_state.euro_sf_results.get(i)
                        if res:
                            render_match_result(t1, t2, res)
                            sf_winners.append(res["winner"])
                            sf_losers.append(t2 if res["winner"] == t1 else t1)
                        else:
                            r = knockout_input(f"euro_sf_{i}", t1, t2, PLAYERS.get(t1,[]), PLAYERS.get(t2,[]))
                            if r:
                                st.session_state.euro_sf_results[i] = r
                                for s in r.get("scorers_h",[]): update_scorer(s, t1, 1, "euro_")
                                for s in r.get("scorers_a",[]): update_scorer(s, t2, 1, "euro_")
                                st.rerun()
                            sf_winners.append(None)

                    if all(sf_winners) and len(sf_winners) == 2:
                        if st.session_state.euro_final is None:
                            st.session_state.euro_final = (sf_winners[0], sf_winners[1])

                        st.markdown("### 🏆 FINAL")
                        t1, t2 = st.session_state.euro_final
                        res = st.session_state.euro_final_result
                        if res:
                            render_match_result(t1, t2, res)
                            champ_banner(res["winner"], "CAMPEÓN DE EUROPA")
                        else:
                            r = knockout_input("euro_final", t1, t2, PLAYERS.get(t1,[]), PLAYERS.get(t2,[]))
                            if r:
                                st.session_state.euro_final_result = r
                                st.session_state.euro_champion = r["winner"]
                                for s in r.get("scorers_h",[]): update_scorer(s, t1, 1, "euro_")
                                for s in r.get("scorers_a",[]): update_scorer(s, t2, 1, "euro_")
                                champion = r["winner"]
                                runner = t2 if champion == t1 else t1
                                fs = [{"pos": 1, "team": champion}, {"pos": 2, "team": runner}]
                                pos = 3
                                for lsr in (sf_losers or []):
                                    if lsr:
                                        fs.append({"pos": pos, "team": lsr}); pos += 1
                                for i_, res_ in st.session_state.euro_qf_results.items():
                                    lsr = (st.session_state.euro_qf[i_][0] if res_["winner"] == st.session_state.euro_qf[i_][1]
                                           else st.session_state.euro_qf[i_][1]) if i_ < len(st.session_state.euro_qf) else None
                                    if lsr and lsr not in [e["team"] for e in fs]:
                                        fs.append({"pos": pos, "team": lsr}); pos += 1
                                for i_, res_ in st.session_state.euro_r16_results.items():
                                    t1_, t2_ = st.session_state.euro_r16[i_]
                                    lsr = t2_ if res_["winner"] == t1_ else t1_
                                    if lsr and lsr not in [e["team"] for e in fs]:
                                        fs.append({"pos": pos, "team": lsr}); pos += 1
                                placed = {e["team"] for e in fs}
                                for gl, s in st.session_state.euro_standings.items():
                                    for entry in s:
                                        if entry["team"] not in placed:
                                            fs.append({"pos": pos, "team": entry["team"]}); pos += 1; placed.add(entry["team"])
                                st.session_state.euro_final_standings = fs
                                update_ranking_from_standings(fs, 80, 4)
                                if champion not in st.session_state.wc_qualified:
                                    st.session_state.wc_qualified.append(champion)
                                st.rerun()

    with tab_result:
        if st.session_state.euro_champion:
            champ_banner(st.session_state.euro_champion, "CAMPEÓN DE EUROPA")
            st.markdown("#### 📊 Clasificación Final")
            render_standings(st.session_state.euro_final_standings[:10], highlight=5)
            st.info(f"El campeón **{st.session_state.euro_champion}** va directo al Mundial.")
        else:
            st.info("La Eurocopa aún no tiene resultado final.")


# ══════════════════════════════════════════════════════════════════════════════
# UEFA PLAYOFFS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔢 Playoffs UEFA":
    conf_header("🔢", "UEFA · ELIMINATORIAS MUNDIALISTAS", "#4A90D9",
                "Puestos 6-21 Eurocopa → 4 grupos de 4 · Top 2 c/u → Mundial")

    if not st.session_state.euro_final_standings:
        st.warning("Primero completa la Eurocopa.")
    else:
        fs = st.session_state.euro_final_standings
        pool = [e["team"] for e in fs[5:21]]

        tab1, tab2 = st.tabs(["⚙️ Grupos", "📊 Resultados"])
        with tab1:
            st.markdown("**Equipos disponibles (puestos 6-21 Eurocopa):**")
            flags_str = " · ".join(f"{fl(t)} {t}" for t in pool)
            st.markdown(f"<div style='font-size:13px;color:var(--muted);'>{flags_str}</div>", unsafe_allow_html=True)
            st.markdown("---")
            cols = st.columns(4)
            new_groups = {}
            for i, gl in enumerate(["A", "B", "C", "D"]):
                with cols[i]:
                    st.markdown(f"**Grupo {gl}**")
                    default_g = st.session_state.euro_playoff_groups.get(gl, pool[i*4:(i+1)*4])
                    chosen = st.multiselect(f"Grupo {gl}", pool, default=default_g, max_selections=4, key=f"ep_grp_{gl}")
                    new_groups[gl] = chosen

            if st.button("💾 Guardar grupos playoff"):
                all_a = sum(new_groups.values(), [])
                if len(all_a) != len(set(all_a)):
                    st.error("Duplicados.")
                elif any(len(v) != 4 for v in new_groups.values()):
                    st.error("Cada grupo necesita 4 equipos.")
                else:
                    st.session_state.euro_playoff_groups = new_groups
                    all_m = {}
                    for gl, teams in new_groups.items():
                        all_m.update(generate_group_matches(teams))
                    st.session_state.euro_playoff_matches = all_m
                    st.success("✅ Grupos guardados.")
                    st.rerun()

        with tab2:
            if not st.session_state.euro_playoff_groups:
                st.info("Arma los grupos primero.")
            else:
                for gl in ["A", "B", "C", "D"]:
                    teams = st.session_state.euro_playoff_groups.get(gl, [])
                    if not teams: continue
                    with st.expander(f"Grupo {gl}", expanded=True):
                        col_m, col_t = st.columns([3, 2])
                        with col_m:
                            for t1, t2 in combinations(teams, 2):
                                key = (t1, t2) if (t1, t2) in st.session_state.euro_playoff_matches else (t2, t1)
                                res = st.session_state.euro_playoff_matches.get(key)
                                render_match_result(t1, t2, res)
                                if res is None:
                                    r = match_input_form("ep", t1, t2, PLAYERS.get(t1,[]), PLAYERS.get(t2,[]), key_suffix=gl)
                                    if r:
                                        hg, ag, sh, sa = r
                                        st.session_state.euro_playoff_matches[key] = {"hg": hg, "ag": ag, "scorers_h": sh, "scorers_a": sa}
                                        st.rerun()
                        with col_t:
                            gm = {k: v for k, v in st.session_state.euro_playoff_matches.items()
                                  if k[0] in teams and k[1] in teams and v is not None}
                            s = compute_standings(teams, gm)
                            st.session_state.euro_playoff_standings[gl] = s
                            render_standings(s, highlight=2)

                st.divider()
                qualified = []
                for gl in ["A", "B", "C", "D"]:
                    s = st.session_state.euro_playoff_standings.get(gl, [])
                    qualified.extend([e["team"] for e in s[:2]])

                st.markdown(f"#### ✅ Clasificados al Mundial via Playoffs UEFA ({len(qualified)})")
                for t in qualified:
                    st.markdown(f"✅ {fl(t)} **{t}**")

                if st.button("💾 Confirmar clasificados UEFA al Mundial"):
                    euro_direct = [e["team"] for e in st.session_state.euro_final_standings[:5]]
                    all_uefa = list(set(euro_direct + qualified))
                    for t in all_uefa:
                        if t not in st.session_state.wc_qualified:
                            st.session_state.wc_qualified.append(t)
                    st.session_state.euro_playoff_qualified = all_uefa
                    st.success(f"✅ {len(all_uefa)} equipos UEFA confirmados al Mundial.")


# ══════════════════════════════════════════════════════════════════════════════
# COPA AMERICA
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🌎 Copa América CONMEBOL":
    conf_header("🌎", "COPA AMÉRICA", "#27AE60",
                "10 equipos CONMEBOL + 6 invitados · 4 grupos de 4 · 2 pasan por grupo")

    tab_setup, tab_groups, tab_ko, tab_result = st.tabs(["⚙️ Config", "📊 Grupos", "🎯 Bracket", "🏆 Resultado"])

    with tab_setup:
        st.markdown("#### Equipos invitados (6, no UEFA)")
        guests = st.multiselect("Selecciona 6 invitados", COPA_AMERICA_GUESTS_POOL,
                                default=st.session_state.ca_teams[10:] if len(st.session_state.ca_teams)==16 else [],
                                max_selections=6)
        all_ca = CONMEBOL_TEAMS + guests
        st.markdown(f"**Total: {len(all_ca)}/16 equipos**")
        if len(all_ca) == 16:
            st.markdown("---")
            cols = st.columns(4)
            new_groups = {}
            for i, gl in enumerate(["A", "B", "C", "D"]):
                with cols[i]:
                    st.markdown(f"**Grupo {gl}**")
                    default_g = st.session_state.ca_groups.get(gl, all_ca[i*4:(i+1)*4])
                    chosen = st.multiselect(f"Grupo {gl}", all_ca, default=default_g, max_selections=4, key=f"ca_grp_{gl}")
                    new_groups[gl] = chosen

            if st.button("💾 Guardar grupos Copa América"):
                all_a = sum(new_groups.values(), [])
                if len(all_a) != len(set(all_a)):
                    st.error("Duplicados.")
                elif any(len(v) != 4 for v in new_groups.values()):
                    st.error("4 equipos por grupo.")
                else:
                    st.session_state.ca_teams = all_ca
                    st.session_state.ca_groups = new_groups
                    all_m = {}
                    for gl, teams in new_groups.items():
                        all_m.update(generate_group_matches(teams))
                    st.session_state.ca_matches = all_m
                    st.success("✅ Grupos guardados.")
                    st.rerun()

    with tab_groups:
        if not st.session_state.ca_groups:
            st.info("Configura los grupos primero.")
        else:
            for gl in ["A", "B", "C", "D"]:
                teams = st.session_state.ca_groups.get(gl, [])
                if not teams: continue
                flags_str = " · ".join(f"{fl(t)} {t}" for t in teams)
                with st.expander(f"Grupo {gl} — {flags_str}", expanded=True):
                    col_m, col_t = st.columns([3, 2])
                    with col_m:
                        for t1, t2 in combinations(teams, 2):
                            key = (t1, t2) if (t1, t2) in st.session_state.ca_matches else (t2, t1)
                            res = st.session_state.ca_matches.get(key)
                            render_match_result(t1, t2, res)
                            if res is None:
                                r = match_input_form("ca", t1, t2, PLAYERS.get(t1,[]), PLAYERS.get(t2,[]), key_suffix=gl)
                                if r:
                                    hg, ag, sh, sa = r
                                    st.session_state.ca_matches[key] = {"hg": hg, "ag": ag, "scorers_h": sh, "scorers_a": sa}
                                    for s in sh: update_scorer(s, t1, 1, "ca_")
                                    for s in sa: update_scorer(s, t2, 1, "ca_")
                                    st.rerun()
                    with col_t:
                        gm = {k: v for k, v in st.session_state.ca_matches.items()
                              if k[0] in teams and k[1] in teams and v is not None}
                        s = compute_standings(teams, gm)
                        st.session_state.ca_standings[gl] = s
                        render_standings(s, highlight=2)

            st.divider()
            by_slot = {}
            for gl in ["A", "B", "C", "D"]:
                s = st.session_state.ca_standings.get(gl, [])
                if len(s) >= 2:
                    by_slot[f"{gl}1"] = s[0]["team"]
                    by_slot[f"{gl}2"] = s[1]["team"]

            if len(by_slot) == 8:
                ca_r16 = [
                    (by_slot.get("A1","?"), by_slot.get("D2","?")),
                    (by_slot.get("C1","?"), by_slot.get("B2","?")),
                    (by_slot.get("B1","?"), by_slot.get("C2","?")),
                    (by_slot.get("D1","?"), by_slot.get("A2","?")),
                ]
                st.markdown("#### Bracket QF Copa América")
                for t1, t2 in ca_r16:
                    st.markdown(f"- {fl(t1)} **{t1}** vs {fl(t2)} **{t2}**")

                if st.button("➡️ Generar Bracket QF/SF/Final"):
                    st.session_state.ca_r16 = ca_r16
                    st.session_state.ca_r16_results = {}
                    st.success("✅ Bracket generado.")
                    st.rerun()

    with tab_ko:
        if not st.session_state.ca_r16:
            st.info("Completa grupos y genera bracket primero.")
        else:
            st.markdown("### ⚔️ Cuartos de Final")
            r16_winners = []
            for i, (t1, t2) in enumerate(st.session_state.ca_r16):
                res = st.session_state.ca_r16_results.get(i)
                if res:
                    render_match_result(t1, t2, res)
                    r16_winners.append(res["winner"])
                else:
                    r = knockout_input(f"ca_r16_{i}", t1, t2, PLAYERS.get(t1,[]), PLAYERS.get(t2,[]))
                    if r:
                        st.session_state.ca_r16_results[i] = r
                        for s in r.get("scorers_h",[]): update_scorer(s, t1, 1, "ca_")
                        for s in r.get("scorers_a",[]): update_scorer(s, t2, 1, "ca_")
                        st.rerun()
                    r16_winners.append(None)

            if all(r16_winners) and len(r16_winners) == 4:
                if not st.session_state.ca_sf:
                    st.session_state.ca_sf = [(r16_winners[0], r16_winners[1]), (r16_winners[2], r16_winners[3])]

                st.markdown("### ⚔️ Semifinales")
                sf_winners = []
                for i, (t1, t2) in enumerate(st.session_state.ca_sf):
                    res = st.session_state.ca_sf_results.get(i)
                    if res:
                        render_match_result(t1, t2, res)
                        sf_winners.append(res["winner"])
                    else:
                        r = knockout_input(f"ca_sf_{i}", t1, t2, PLAYERS.get(t1,[]), PLAYERS.get(t2,[]))
                        if r:
                            st.session_state.ca_sf_results[i] = r
                            for s in r.get("scorers_h",[]): update_scorer(s, t1, 1, "ca_")
                            for s in r.get("scorers_a",[]): update_scorer(s, t2, 1, "ca_")
                            st.rerun()
                        sf_winners.append(None)

                if all(sf_winners) and len(sf_winners) == 2:
                    if st.session_state.ca_final is None:
                        st.session_state.ca_final = (sf_winners[0], sf_winners[1])

                    st.markdown("### 🏆 FINAL")
                    t1, t2 = st.session_state.ca_final
                    res = st.session_state.ca_final_result
                    if res:
                        render_match_result(t1, t2, res)
                        champ_banner(res["winner"], "CAMPEÓN DE AMÉRICA")
                    else:
                        r = knockout_input("ca_final", t1, t2, PLAYERS.get(t1,[]), PLAYERS.get(t2,[]))
                        if r:
                            st.session_state.ca_final_result = r
                            champ = r["winner"]
                            st.session_state.ca_champion = champ
                            for s in r.get("scorers_h",[]): update_scorer(s, t1, 1, "ca_")
                            for s in r.get("scorers_a",[]): update_scorer(s, t2, 1, "ca_")
                            runner = t2 if champ == t1 else t1
                            fs = [{"pos": 1, "team": champ}, {"pos": 2, "team": runner}]
                            pos = 3
                            for i_, (ta, tb) in enumerate(st.session_state.ca_sf):
                                res_ = st.session_state.ca_sf_results.get(i_)
                                if res_:
                                    lsr = tb if res_["winner"] == ta else ta
                                    fs.append({"pos": pos, "team": lsr}); pos += 1
                            placed = {e["team"] for e in fs}
                            for gl, s in st.session_state.ca_standings.items():
                                for entry in s:
                                    if entry["team"] not in placed:
                                        fs.append({"pos": pos, "team": entry["team"]}); pos += 1; placed.add(entry["team"])
                            st.session_state.ca_final_standings = fs
                            update_ranking_from_standings(fs, 80, 5)
                            if champ not in st.session_state.wc_qualified:
                                st.session_state.wc_qualified.append(champ)
                            st.rerun()

    with tab_result:
        if st.session_state.ca_champion:
            champ_banner(st.session_state.ca_champion, "CAMPEÓN DE AMÉRICA")
            render_standings(st.session_state.ca_final_standings[:10], highlight=1)
        else:
            st.info("Copa América sin resultado aún.")


# ══════════════════════════════════════════════════════════════════════════════
# CONMEBOL PLAYOFFS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔢 Playoffs CONMEBOL":
    conf_header("🔢", "CONMEBOL · PLAYOFFS MUNDIALISTAS", "#27AE60",
                "Puestos 2-7 → todos vs todos · Top 3 → Mundial · 4to → Repechaje")

    if not st.session_state.ca_final_standings:
        st.warning("Completa la Copa América primero.")
    else:
        fs = st.session_state.ca_final_standings
        conmebol_in_ca = [e for e in fs if e["team"] in CONMEBOL_TEAMS]
        pool = [e["team"] for e in conmebol_in_ca[1:7]]
        st.markdown(f"**Equipos:** {' · '.join(fl(t)+' '+t for t in pool)}")

        if not st.session_state.conmebol_playoff_teams:
            if st.button("▶️ Iniciar eliminatoria CONMEBOL"):
                st.session_state.conmebol_playoff_teams = pool
                st.session_state.conmebol_playoff_matches = generate_group_matches(pool)
                st.rerun()
        else:
            teams = st.session_state.conmebol_playoff_teams
            for t1, t2 in combinations(teams, 2):
                key = (t1, t2) if (t1, t2) in st.session_state.conmebol_playoff_matches else (t2, t1)
                res = st.session_state.conmebol_playoff_matches.get(key)
                render_match_result(t1, t2, res)
                if res is None:
                    r = match_input_form("cmp", t1, t2, PLAYERS.get(t1,[]), PLAYERS.get(t2,[]))
                    if r:
                        hg, ag, sh, sa = r
                        st.session_state.conmebol_playoff_matches[key] = {"hg": hg, "ag": ag, "scorers_h": sh, "scorers_a": sa}
                        st.rerun()

            st.divider()
            played = {k: v for k, v in st.session_state.conmebol_playoff_matches.items() if v is not None}
            standings = compute_standings(teams, played)
            st.session_state.conmebol_playoff_standings = standings
            render_standings(standings, highlight=3, repechaje_pos=4)

            qualified = [s["team"] for s in standings[:3]]
            repechaje = standings[3]["team"] if len(standings) > 3 else None
            st.markdown(f"**✅ Clasificados:** {' · '.join(fl(t)+' '+t for t in qualified)}")
            if repechaje:
                st.markdown(f"**🔄 Repechaje:** {fl(repechaje)} {repechaje}")

            if st.button("💾 Confirmar clasificados CONMEBOL"):
                for t in qualified:
                    if t not in st.session_state.wc_qualified:
                        st.session_state.wc_qualified.append(t)
                st.session_state.conmebol_playoff_qualified = qualified
                st.session_state.conmebol_playoff_repechaje = repechaje
                st.success("✅ Confirmados.")


# ══════════════════════════════════════════════════════════════════════════════
# COPA AFRICA
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🌍 Copa África CAF":
    conf_header("🌍", "COPA ÁFRICA CAF", "#F39C12",
                "10 equipos · 2 grupos de 5 · 2 primeros → Semis")

    tab_setup, tab_groups, tab_ko, tab_result = st.tabs(["⚙️ Config", "📊 Grupos", "🎯 Eliminatorias", "🏆 Resultado"])

    with tab_setup:
        selected = st.multiselect("Elige 10 equipos CAF", CAF_TEAMS,
                                  default=st.session_state.af_teams or CAF_TEAMS, max_selections=10)
        if len(selected) == 10:
            col1, col2 = st.columns(2)
            with col1:
                gA = st.multiselect("Grupo A", selected, default=st.session_state.af_groups.get("A", selected[:5]), max_selections=5, key="af_gA")
            with col2:
                gB = st.multiselect("Grupo B", selected, default=st.session_state.af_groups.get("B", selected[5:]), max_selections=5, key="af_gB")

            if st.button("💾 Guardar grupos África"):
                if len(gA) != 5 or len(gB) != 5:
                    st.error("5 equipos por grupo.")
                elif len(set(gA + gB)) != 10:
                    st.error("Duplicados.")
                else:
                    st.session_state.af_teams = selected
                    st.session_state.af_groups = {"A": gA, "B": gB}
                    st.session_state.af_matches = {**generate_group_matches(gA), **generate_group_matches(gB)}
                    st.success("✅ Grupos guardados.")
                    st.rerun()

    with tab_groups:
        if not st.session_state.af_groups:
            st.info("Configura primero.")
        else:
            for gl in ["A", "B"]:
                teams = st.session_state.af_groups.get(gl, [])
                with st.expander(f"Grupo {gl}", expanded=True):
                    col_m, col_t = st.columns([3, 2])
                    with col_m:
                        for t1, t2 in combinations(teams, 2):
                            key = (t1, t2) if (t1, t2) in st.session_state.af_matches else (t2, t1)
                            res = st.session_state.af_matches.get(key)
                            render_match_result(t1, t2, res)
                            if res is None:
                                r = match_input_form("af", t1, t2, PLAYERS.get(t1,[]), PLAYERS.get(t2,[]), key_suffix=gl)
                                if r:
                                    hg, ag, sh, sa = r
                                    st.session_state.af_matches[key] = {"hg": hg, "ag": ag, "scorers_h": sh, "scorers_a": sa}
                                    for s in sh: update_scorer(s, t1, 1, "af_")
                                    for s in sa: update_scorer(s, t2, 1, "af_")
                                    st.rerun()
                    with col_t:
                        gm = {k: v for k, v in st.session_state.af_matches.items()
                              if k[0] in teams and k[1] in teams and v is not None}
                        s = compute_standings(teams, gm)
                        st.session_state.af_standings[gl] = s
                        render_standings(s, highlight=2)

            sA = st.session_state.af_standings.get("A", [])
            sB = st.session_state.af_standings.get("B", [])
            if len(sA) >= 2 and len(sB) >= 2:
                sf1 = (sA[0]["team"], sB[1]["team"])
                sf2 = (sB[0]["team"], sA[1]["team"])
                st.markdown(f"**SF1:** {fl(sf1[0])} {sf1[0]} vs {fl(sf1[1])} {sf1[1]}")
                st.markdown(f"**SF2:** {fl(sf2[0])} {sf2[0]} vs {fl(sf2[1])} {sf2[1]}")
                if st.button("➡️ Generar Semis"):
                    st.session_state.af_sf = [sf1, sf2]
                    st.session_state.af_sf_results = {}
                    st.success("✅ Semis generadas.")
                    st.rerun()

    with tab_ko:
        if not st.session_state.af_sf:
            st.info("Completa grupos primero.")
        else:
            st.markdown("### ⚔️ Semifinales")
            sf_winners = []
            for i, (t1, t2) in enumerate(st.session_state.af_sf):
                res = st.session_state.af_sf_results.get(i)
                if res:
                    render_match_result(t1, t2, res)
                    sf_winners.append(res["winner"])
                else:
                    r = knockout_input(f"af_sf_{i}", t1, t2, PLAYERS.get(t1,[]), PLAYERS.get(t2,[]))
                    if r:
                        st.session_state.af_sf_results[i] = r
                        for s in r.get("scorers_h",[]): update_scorer(s, t1, 1, "af_")
                        for s in r.get("scorers_a",[]): update_scorer(s, t2, 1, "af_")
                        st.rerun()
                    sf_winners.append(None)

            if all(sf_winners) and len(sf_winners) == 2:
                if st.session_state.af_final is None:
                    st.session_state.af_final = (sf_winners[0], sf_winners[1])
                st.markdown("### 🏆 FINAL")
                t1, t2 = st.session_state.af_final
                res = st.session_state.af_final_result
                if res:
                    render_match_result(t1, t2, res)
                    champ_banner(res["winner"], "CAMPEÓN DE ÁFRICA")
                else:
                    r = knockout_input("af_final", t1, t2, PLAYERS.get(t1,[]), PLAYERS.get(t2,[]))
                    if r:
                        st.session_state.af_final_result = r
                        champ = r["winner"]
                        runner = t2 if champ == t1 else t1
                        st.session_state.af_champion = champ
                        for s in r.get("scorers_h",[]): update_scorer(s, t1, 1, "af_")
                        for s in r.get("scorers_a",[]): update_scorer(s, t2, 1, "af_")
                        fs = [{"pos": 1, "team": champ}, {"pos": 2, "team": runner}]
                        pos = 3
                        placed = {champ, runner}
                        for gl, s_ in st.session_state.af_standings.items():
                            for e in s_:
                                if e["team"] not in placed:
                                    fs.append({"pos": pos, "team": e["team"]}); pos += 1; placed.add(e["team"])
                        st.session_state.af_final_standings = fs
                        update_ranking_from_standings(fs, 70, 5)
                        for t in [champ, runner]:
                            if t not in st.session_state.wc_qualified:
                                st.session_state.wc_qualified.append(t)
                        st.rerun()

    with tab_result:
        if st.session_state.af_champion:
            champ_banner(st.session_state.af_champion, "CAMPEÓN DE ÁFRICA")
            render_standings(st.session_state.af_final_standings[:6], highlight=2)
        else:
            st.info("Sin resultado aún.")


# ══════════════════════════════════════════════════════════════════════════════
# CAF PLAYOFFS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔢 Playoffs CAF":
    conf_header("🔢", "CAF · PLAYOFFS MUNDIALISTAS", "#F39C12",
                "Puestos 3-7 → todos vs todos · Top 3 → Mundial")

    if not st.session_state.af_final_standings:
        st.warning("Completa la Copa África primero.")
    else:
        pool = [e["team"] for e in st.session_state.af_final_standings[2:7]]
        st.markdown(f"**Equipos:** {' · '.join(fl(t)+' '+t for t in pool)}")

        if not st.session_state.caf_playoff_teams:
            if st.button("▶️ Iniciar playoff CAF"):
                st.session_state.caf_playoff_teams = pool
                st.session_state.caf_playoff_matches = generate_group_matches(pool)
                st.rerun()
        else:
            teams = st.session_state.caf_playoff_teams
            for t1, t2 in combinations(teams, 2):
                key = (t1, t2) if (t1, t2) in st.session_state.caf_playoff_matches else (t2, t1)
                res = st.session_state.caf_playoff_matches.get(key)
                render_match_result(t1, t2, res)
                if res is None:
                    r = match_input_form("cafp", t1, t2, PLAYERS.get(t1,[]), PLAYERS.get(t2,[]))
                    if r:
                        hg, ag, sh, sa = r
                        st.session_state.caf_playoff_matches[key] = {"hg": hg, "ag": ag, "scorers_h": sh, "scorers_a": sa}
                        st.rerun()

            st.divider()
            played = {k: v for k, v in st.session_state.caf_playoff_matches.items() if v is not None}
            standings = compute_standings(teams, played)
            st.session_state.caf_playoff_standings = standings
            render_standings(standings, highlight=3)

            qualified = [s["team"] for s in standings[:3]]
            st.markdown(f"**✅ Clasificados:** {' · '.join(fl(t)+' '+t for t in qualified)}")

            if st.button("💾 Confirmar clasificados CAF"):
                for t in qualified:
                    if t not in st.session_state.wc_qualified:
                        st.session_state.wc_qualified.append(t)
                st.session_state.caf_playoff_qualified = qualified
                st.success("✅ Confirmados.")


# ══════════════════════════════════════════════════════════════════════════════
# COPA ORO
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🌎 Copa Oro CONCACAF":
    conf_header("🌎", "COPA ORO CONCACAF", "#E74C3C",
                "6 equipos · 2 grupos de 3 · A1vB2 y B1vA2 → Final")

    tab_setup, tab_groups, tab_ko, tab_result = st.tabs(["⚙️ Config", "📊 Grupos", "🎯 Eliminatorias", "🏆 Resultado"])

    with tab_setup:
        selected = st.multiselect("Elige 6 equipos CONCACAF", CONCACAF_TEAMS,
                                  default=st.session_state.co_teams or CONCACAF_TEAMS, max_selections=6)
        if len(selected) == 6:
            col1, col2 = st.columns(2)
            with col1:
                gA = st.multiselect("Grupo A", selected, default=st.session_state.co_groups.get("A", selected[:3]), max_selections=3, key="co_gA")
            with col2:
                gB = st.multiselect("Grupo B", selected, default=st.session_state.co_groups.get("B", selected[3:]), max_selections=3, key="co_gB")

            if st.button("💾 Guardar grupos Copa Oro"):
                if len(gA) != 3 or len(gB) != 3 or len(set(gA + gB)) != 6:
                    st.error("3 equipos por grupo sin duplicados.")
                else:
                    st.session_state.co_teams = selected
                    st.session_state.co_groups = {"A": gA, "B": gB}
                    st.session_state.co_matches = {**generate_group_matches(gA), **generate_group_matches(gB)}
                    st.success("✅ Guardados.")
                    st.rerun()

    with tab_groups:
        if not st.session_state.co_groups:
            st.info("Configura primero.")
        else:
            for gl in ["A", "B"]:
                teams = st.session_state.co_groups.get(gl, [])
                with st.expander(f"Grupo {gl}", expanded=True):
                    col_m, col_t = st.columns([3, 2])
                    with col_m:
                        for t1, t2 in combinations(teams, 2):
                            key = (t1, t2) if (t1, t2) in st.session_state.co_matches else (t2, t1)
                            res = st.session_state.co_matches.get(key)
                            render_match_result(t1, t2, res)
                            if res is None:
                                r = match_input_form("co", t1, t2, PLAYERS.get(t1,[]), PLAYERS.get(t2,[]), key_suffix=gl)
                                if r:
                                    hg, ag, sh, sa = r
                                    st.session_state.co_matches[key] = {"hg": hg, "ag": ag, "scorers_h": sh, "scorers_a": sa}
                                    for s in sh: update_scorer(s, t1, 1, "co_")
                                    for s in sa: update_scorer(s, t2, 1, "co_")
                                    st.rerun()
                    with col_t:
                        gm = {k: v for k, v in st.session_state.co_matches.items()
                              if k[0] in teams and k[1] in teams and v is not None}
                        s = compute_standings(teams, gm)
                        st.session_state.co_standings[gl] = s
                        render_standings(s, highlight=2)

            sA = st.session_state.co_standings.get("A", [])
            sB = st.session_state.co_standings.get("B", [])
            if len(sA) >= 2 and len(sB) >= 2:
                sf1 = (sA[0]["team"], sB[1]["team"])
                sf2 = (sB[0]["team"], sA[1]["team"])
                st.markdown(f"**SF1:** {fl(sf1[0])} {sf1[0]} vs {fl(sf1[1])} {sf1[1]}")
                st.markdown(f"**SF2:** {fl(sf2[0])} {sf2[0]} vs {fl(sf2[1])} {sf2[1]}")
                if st.button("➡️ Generar Semis Copa Oro"):
                    st.session_state.co_sf = [sf1, sf2]
                    st.session_state.co_sf_results = {}
                    st.rerun()

    with tab_ko:
        if not st.session_state.co_sf:
            st.info("Completa grupos primero.")
        else:
            st.markdown("### ⚔️ Semifinales")
            sf_winners = []
            for i, (t1, t2) in enumerate(st.session_state.co_sf):
                res = st.session_state.co_sf_results.get(i)
                if res:
                    render_match_result(t1, t2, res)
                    sf_winners.append(res["winner"])
                else:
                    r = knockout_input(f"co_sf_{i}", t1, t2, PLAYERS.get(t1,[]), PLAYERS.get(t2,[]))
                    if r:
                        st.session_state.co_sf_results[i] = r
                        for s in r.get("scorers_h",[]): update_scorer(s, t1, 1, "co_")
                        for s in r.get("scorers_a",[]): update_scorer(s, t2, 1, "co_")
                        st.rerun()
                    sf_winners.append(None)

            if all(sf_winners) and len(sf_winners) == 2:
                if st.session_state.co_final is None:
                    st.session_state.co_final = (sf_winners[0], sf_winners[1])
                st.markdown("### 🏆 FINAL")
                t1, t2 = st.session_state.co_final
                res = st.session_state.co_final_result
                if res:
                    render_match_result(t1, t2, res)
                    champ_banner(res["winner"], "CAMPEÓN COPA ORO")
                else:
                    r = knockout_input("co_final", t1, t2, PLAYERS.get(t1,[]), PLAYERS.get(t2,[]))
                    if r:
                        st.session_state.co_final_result = r
                        champ = r["winner"]
                        st.session_state.co_champion = champ
                        for s in r.get("scorers_h",[]): update_scorer(s, t1, 1, "co_")
                        for s in r.get("scorers_a",[]): update_scorer(s, t2, 1, "co_")
                        runner = t2 if champ == t1 else t1
                        fs = [{"pos": 1, "team": champ}, {"pos": 2, "team": runner}]
                        pos = 3
                        placed = {champ, runner}
                        for i_, (ta, tb) in enumerate(st.session_state.co_sf):
                            res_ = st.session_state.co_sf_results.get(i_)
                            if res_:
                                lsr = tb if res_["winner"] == ta else ta
                                if lsr not in placed:
                                    fs.append({"pos": pos, "team": lsr}); pos += 1; placed.add(lsr)
                        for gl, s_ in st.session_state.co_standings.items():
                            for e in s_:
                                if e["team"] not in placed:
                                    fs.append({"pos": pos, "team": e["team"]}); pos += 1; placed.add(e["team"])
                        st.session_state.co_final_standings = fs
                        update_ranking_from_standings(fs, 60, 6)
                        if champ not in st.session_state.wc_qualified:
                            st.session_state.wc_qualified.append(champ)
                        st.rerun()

    with tab_result:
        if st.session_state.co_champion:
            champ_banner(st.session_state.co_champion, "CAMPEÓN COPA ORO")
            render_standings(st.session_state.co_final_standings, highlight=1)
        else:
            st.info("Sin resultado aún.")


# ══════════════════════════════════════════════════════════════════════════════
# CONCACAF PLAYOFFS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔢 Playoffs CONCACAF":
    conf_header("🔢", "CONCACAF · PLAYOFFS", "#E74C3C",
                "Puestos 2-5 → todos vs todos · Top 2 → Mundial · 3ro → Repechaje")

    if not st.session_state.co_final_standings:
        st.warning("Completa la Copa Oro primero.")
    else:
        pool = [e["team"] for e in st.session_state.co_final_standings[1:5]]
        st.markdown(f"**Equipos:** {' · '.join(fl(t)+' '+t for t in pool)}")

        if not st.session_state.concacaf_playoff_teams:
            if st.button("▶️ Iniciar playoff CONCACAF"):
                st.session_state.concacaf_playoff_teams = pool
                st.session_state.concacaf_playoff_matches = generate_group_matches(pool)
                st.rerun()
        else:
            teams = st.session_state.concacaf_playoff_teams
            for t1, t2 in combinations(teams, 2):
                key = (t1, t2) if (t1, t2) in st.session_state.concacaf_playoff_matches else (t2, t1)
                res = st.session_state.concacaf_playoff_matches.get(key)
                render_match_result(t1, t2, res)
                if res is None:
                    r = match_input_form("ccp", t1, t2, PLAYERS.get(t1,[]), PLAYERS.get(t2,[]))
                    if r:
                        hg, ag, sh, sa = r
                        st.session_state.concacaf_playoff_matches[key] = {"hg": hg, "ag": ag, "scorers_h": sh, "scorers_a": sa}
                        st.rerun()

            st.divider()
            played = {k: v for k, v in st.session_state.concacaf_playoff_matches.items() if v is not None}
            standings = compute_standings(teams, played)
            st.session_state.concacaf_playoff_standings = standings
            render_standings(standings, highlight=2, repechaje_pos=3)

            qualified = [s["team"] for s in standings[:2]]
            repechaje = standings[2]["team"] if len(standings) > 2 else None
            st.markdown(f"**✅ Clasificados:** {' · '.join(fl(t)+' '+t for t in qualified)}")
            if repechaje:
                st.markdown(f"**🔄 Repechaje:** {fl(repechaje)} {repechaje}")

            if st.button("💾 Confirmar CONCACAF"):
                for t in qualified:
                    if t not in st.session_state.wc_qualified:
                        st.session_state.wc_qualified.append(t)
                st.session_state.concacaf_playoff_qualified = qualified
                st.session_state.concacaf_playoff_repechaje = repechaje
                st.success("✅ Confirmados.")


# ══════════════════════════════════════════════════════════════════════════════
# COPA ASIA
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🌏 Copa Asia AFC":
    conf_header("🌏", "COPA ASIA AFC", "#9B59B6",
                "6 equipos (Australia incluida) · 2 grupos de 3 · A1vB2 y B1vA2 → Final")

    tab_setup, tab_groups, tab_ko, tab_result = st.tabs(["⚙️ Config", "📊 Grupos", "🎯 Eliminatorias", "🏆 Resultado"])

    with tab_setup:
        selected = st.multiselect("Elige 6 equipos AFC", AFC_TEAMS,
                                  default=st.session_state.as_teams or AFC_TEAMS, max_selections=6)
        if "Australia" not in selected:
            st.warning("⚠️ Australia debe estar incluida (juega en AFC).")
        if len(selected) == 6:
            col1, col2 = st.columns(2)
            with col1:
                gA = st.multiselect("Grupo A", selected, default=st.session_state.as_groups.get("A", selected[:3]), max_selections=3, key="as_gA")
            with col2:
                gB = st.multiselect("Grupo B", selected, default=st.session_state.as_groups.get("B", selected[3:]), max_selections=3, key="as_gB")

            if st.button("💾 Guardar grupos Copa Asia"):
                if len(gA) != 3 or len(gB) != 3 or len(set(gA + gB)) != 6:
                    st.error("3 por grupo sin duplicados.")
                else:
                    st.session_state.as_teams = selected
                    st.session_state.as_groups = {"A": gA, "B": gB}
                    st.session_state.as_matches = {**generate_group_matches(gA), **generate_group_matches(gB)}
                    st.success("✅ Guardados.")
                    st.rerun()

    with tab_groups:
        if not st.session_state.as_groups:
            st.info("Configura primero.")
        else:
            for gl in ["A", "B"]:
                teams = st.session_state.as_groups.get(gl, [])
                with st.expander(f"Grupo {gl}", expanded=True):
                    col_m, col_t = st.columns([3, 2])
                    with col_m:
                        for t1, t2 in combinations(teams, 2):
                            key = (t1, t2) if (t1, t2) in st.session_state.as_matches else (t2, t1)
                            res = st.session_state.as_matches.get(key)
                            render_match_result(t1, t2, res)
                            if res is None:
                                r = match_input_form("as", t1, t2, PLAYERS.get(t1,[]), PLAYERS.get(t2,[]), key_suffix=gl)
                                if r:
                                    hg, ag, sh, sa = r
                                    st.session_state.as_matches[key] = {"hg": hg, "ag": ag, "scorers_h": sh, "scorers_a": sa}
                                    for s in sh: update_scorer(s, t1, 1, "as_")
                                    for s in sa: update_scorer(s, t2, 1, "as_")
                                    st.rerun()
                    with col_t:
                        gm = {k: v for k, v in st.session_state.as_matches.items()
                              if k[0] in teams and k[1] in teams and v is not None}
                        s = compute_standings(teams, gm)
                        st.session_state.as_standings[gl] = s
                        render_standings(s, highlight=2)

            sA = st.session_state.as_standings.get("A", [])
            sB = st.session_state.as_standings.get("B", [])
            if len(sA) >= 2 and len(sB) >= 2:
                sf1 = (sA[0]["team"], sB[1]["team"])
                sf2 = (sB[0]["team"], sA[1]["team"])
                st.markdown(f"**SF1:** {fl(sf1[0])} {sf1[0]} vs {fl(sf1[1])} {sf1[1]}")
                st.markdown(f"**SF2:** {fl(sf2[0])} {sf2[0]} vs {fl(sf2[1])} {sf2[1]}")
                if st.button("➡️ Generar Semis Copa Asia"):
                    st.session_state.as_sf = [sf1, sf2]
                    st.session_state.as_sf_results = {}
                    st.rerun()

    with tab_ko:
        if not st.session_state.as_sf:
            st.info("Completa grupos primero.")
        else:
            st.markdown("### ⚔️ Semifinales")
            sf_winners = []
            for i, (t1, t2) in enumerate(st.session_state.as_sf):
                res = st.session_state.as_sf_results.get(i)
                if res:
                    render_match_result(t1, t2, res)
                    sf_winners.append(res["winner"])
                else:
                    r = knockout_input(f"as_sf_{i}", t1, t2, PLAYERS.get(t1,[]), PLAYERS.get(t2,[]))
                    if r:
                        st.session_state.as_sf_results[i] = r
                        for s in r.get("scorers_h",[]): update_scorer(s, t1, 1, "as_")
                        for s in r.get("scorers_a",[]): update_scorer(s, t2, 1, "as_")
                        st.rerun()
                    sf_winners.append(None)

            if all(sf_winners) and len(sf_winners) == 2:
                if st.session_state.as_final is None:
                    st.session_state.as_final = (sf_winners[0], sf_winners[1])
                st.markdown("### 🏆 FINAL")
                t1, t2 = st.session_state.as_final
                res = st.session_state.as_final_result
                if res:
                    render_match_result(t1, t2, res)
                    champ_banner(res["winner"], "CAMPEÓN DE ASIA")
                else:
                    r = knockout_input("as_final", t1, t2, PLAYERS.get(t1,[]), PLAYERS.get(t2,[]))
                    if r:
                        st.session_state.as_final_result = r
                        champ = r["winner"]
                        st.session_state.as_champion = champ
                        for s in r.get("scorers_h",[]): update_scorer(s, t1, 1, "as_")
                        for s in r.get("scorers_a",[]): update_scorer(s, t2, 1, "as_")
                        runner = t2 if champ == t1 else t1
                        fs = [{"pos": 1, "team": champ}, {"pos": 2, "team": runner}]
                        pos = 3
                        placed = {champ, runner}
                        for i_, (ta, tb) in enumerate(st.session_state.as_sf):
                            res_ = st.session_state.as_sf_results.get(i_)
                            if res_:
                                lsr = tb if res_["winner"] == ta else ta
                                if lsr not in placed:
                                    fs.append({"pos": pos, "team": lsr}); pos += 1; placed.add(lsr)
                        for gl, s_ in st.session_state.as_standings.items():
                            for e in s_:
                                if e["team"] not in placed:
                                    fs.append({"pos": pos, "team": e["team"]}); pos += 1; placed.add(e["team"])
                        st.session_state.as_final_standings = fs
                        update_ranking_from_standings(fs, 60, 6)
                        if champ not in st.session_state.wc_qualified:
                            st.session_state.wc_qualified.append(champ)
                        st.rerun()

    with tab_result:
        if st.session_state.as_champion:
            champ_banner(st.session_state.as_champion, "CAMPEÓN DE ASIA")
            render_standings(st.session_state.as_final_standings, highlight=1)
        else:
            st.info("Sin resultado aún.")


# ══════════════════════════════════════════════════════════════════════════════
# AFC PLAYOFFS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔢 Playoffs AFC":
    conf_header("🔢", "AFC · PLAYOFFS", "#9B59B6",
                "Puestos 2-5 → todos vs todos · Top 3 → Mundial · 4to → Repechaje")

    if not st.session_state.as_final_standings:
        st.warning("Completa la Copa Asia primero.")
    else:
        pool = [e["team"] for e in st.session_state.as_final_standings[1:5]]
        st.markdown(f"**Equipos:** {' · '.join(fl(t)+' '+t for t in pool)}")

        if not st.session_state.afc_playoff_teams:
            if st.button("▶️ Iniciar playoff AFC"):
                st.session_state.afc_playoff_teams = pool
                st.session_state.afc_playoff_matches = generate_group_matches(pool)
                st.rerun()
        else:
            teams = st.session_state.afc_playoff_teams
            for t1, t2 in combinations(teams, 2):
                key = (t1, t2) if (t1, t2) in st.session_state.afc_playoff_matches else (t2, t1)
                res = st.session_state.afc_playoff_matches.get(key)
                render_match_result(t1, t2, res)
                if res is None:
                    r = match_input_form("afcp", t1, t2, PLAYERS.get(t1,[]), PLAYERS.get(t2,[]))
                    if r:
                        hg, ag, sh, sa = r
                        st.session_state.afc_playoff_matches[key] = {"hg": hg, "ag": ag, "scorers_h": sh, "scorers_a": sa}
                        st.rerun()

            st.divider()
            played = {k: v for k, v in st.session_state.afc_playoff_matches.items() if v is not None}
            standings = compute_standings(teams, played)
            st.session_state.afc_playoff_standings = standings
            render_standings(standings, highlight=3, repechaje_pos=4)

            qualified = [s["team"] for s in standings[:3]]
            repechaje = standings[3]["team"] if len(standings) > 3 else None
            st.markdown(f"**✅ Clasificados:** {' · '.join(fl(t)+' '+t for t in qualified)}")
            if repechaje:
                st.markdown(f"**🔄 Repechaje:** {fl(repechaje)} {repechaje}")

            if st.button("💾 Confirmar AFC"):
                for t in qualified:
                    if t not in st.session_state.wc_qualified:
                        st.session_state.wc_qualified.append(t)
                st.session_state.afc_playoff_qualified = qualified
                st.session_state.afc_playoff_repechaje = repechaje
                st.success("✅ Confirmados.")


# ══════════════════════════════════════════════════════════════════════════════
# REPECHAJE INTERNACIONAL
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔄 Repechaje Internacional":
    conf_header("🔄", "REPECHAJE INTERNACIONAL", "#FF6B6B",
                "CONCACAF 3ro vs AFC 4to · CONMEBOL 4to vs Nueva Zelanda")

    cc3 = st.session_state.concacaf_playoff_repechaje
    afc4 = st.session_state.afc_playoff_repechaje
    cm4  = st.session_state.conmebol_playoff_repechaje

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f"<div class='card' style='border-left:3px solid #E74C3C;'>"
            f"<div style='font-size:11px;color:var(--muted);letter-spacing:1px;margin-bottom:4px;'>CONCACAF 3RO</div>"
            f"<div style='font-size:16px;font-weight:600;'>{'✅ '+fl(cc3)+' '+cc3 if cc3 else '⏳ Pendiente'}</div>"
            f"</div>", unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            f"<div class='card' style='border-left:3px solid #9B59B6;'>"
            f"<div style='font-size:11px;color:var(--muted);letter-spacing:1px;margin-bottom:4px;'>AFC 4TO</div>"
            f"<div style='font-size:16px;font-weight:600;'>{'✅ '+fl(afc4)+' '+afc4 if afc4 else '⏳ Pendiente'}</div>"
            f"</div>", unsafe_allow_html=True
        )
    with c3:
        st.markdown(
            f"<div class='card' style='border-left:3px solid #27AE60;'>"
            f"<div style='font-size:11px;color:var(--muted);letter-spacing:1px;margin-bottom:4px;'>CONMEBOL 4TO</div>"
            f"<div style='font-size:16px;font-weight:600;'>{'✅ '+fl(cm4)+' '+cm4 if cm4 else '⏳ Pendiente'}</div>"
            f"</div>", unsafe_allow_html=True
        )

    st.markdown("---")
    st.markdown("#### ✏️ Configuración Manual")
    all_pool = ALL_TEAMS + ["New Zealand"]
    c1, c2, c3 = st.columns(3)
    with c1: m1t1 = st.selectbox("CONCACAF 3ro", all_pool, index=all_pool.index(cc3) if cc3 in all_pool else 0)
    with c2: m1t2 = st.selectbox("AFC 4to", all_pool, index=all_pool.index(afc4) if afc4 in all_pool else 0)
    with c3: m2t1 = st.selectbox("CONMEBOL 4to", all_pool, index=all_pool.index(cm4) if cm4 in all_pool else 0)

    st.markdown("---")
    st.markdown("### ⚽ Partido 1: CONCACAF 3ro vs AFC 4to")
    res1 = st.session_state.int_playoff_match1
    if res1:
        render_match_result(m1t1, m1t2, res1)
        st.markdown(f"**Clasificado: {fl(res1['winner'])} {res1['winner']}**")
    else:
        r = knockout_input("int1", m1t1, m1t2, PLAYERS.get(m1t1,[]), PLAYERS.get(m1t2,[]))
        if r:
            st.session_state.int_playoff_match1 = r
            st.rerun()

    st.markdown("### ⚽ Partido 2: CONMEBOL 4to vs Nueva Zelanda 🇳🇿")
    res2 = st.session_state.int_playoff_match2
    if res2:
        render_match_result(m2t1, "New Zealand", res2)
        st.markdown(f"**Clasificado: {fl(res2['winner'])} {res2['winner']}**")
    else:
        r = knockout_input("int2", m2t1, "New Zealand", PLAYERS.get(m2t1,[]), PLAYERS.get("New Zealand",[]))
        if r:
            st.session_state.int_playoff_match2 = r
            st.rerun()

    if res1 and res2:
        st.divider()
        qualified = [res1["winner"], res2["winner"]]
        st.markdown("#### ✅ Clasificados al Mundial via Repechaje")
        for t in qualified:
            st.markdown(f"✅ {fl(t)} **{t}**")
        if st.button("💾 Confirmar repechaje"):
            for t in qualified:
                if t not in st.session_state.wc_qualified:
                    st.session_state.wc_qualified.append(t)
            st.session_state.int_playoff_qualified = qualified
            st.success("✅ Clasificados confirmados.")


# ══════════════════════════════════════════════════════════════════════════════
# MUNDIAL
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🏆 Copa del Mundo":
    conf_header("🏆", "COPA DEL MUNDO FMMJ", "#FFD166", "32 equipos · 8 grupos · Modelo FIFA oficial")

    tab_config, tab_groups, tab_ko, tab_result = st.tabs(["⚙️ Config", "📊 Grupos", "🎯 Eliminatorias", "🏆 Resultado"])

    with tab_config:
        nq = len(st.session_state.wc_qualified)
        pct = int(nq/32*100)
        st.markdown(
            f"<div style='margin-bottom:16px;'>"
            f"<div style='display:flex;justify-content:space-between;font-size:12px;color:var(--muted);margin-bottom:6px;'>"
            f"<span>Clasificados</span><span style='color:var(--green);font-weight:700;'>{nq}/32</span></div>"
            f"<div class='progress-bar-wrap'><div class='progress-bar-fill' style='width:{pct}%'></div></div>"
            f"</div>",
            unsafe_allow_html=True
        )
        cols_t = st.columns(8)
        for i, t in enumerate(st.session_state.wc_qualified):
            with cols_t[i % 8]:
                st.markdown(f"<div style='text-align:center;font-size:20px;'>{fl(t)}</div>"
                            f"<div style='text-align:center;font-size:9px;color:var(--muted);'>{t[:8]}</div>",
                            unsafe_allow_html=True)

        st.markdown("---")
        host = st.selectbox("🏟️ País Anfitrión", ALL_TEAMS + ["New Zealand"],
                            index=ALL_TEAMS.index(st.session_state.wc_host) if st.session_state.wc_host in ALL_TEAMS else 0)

        st.markdown("---")
        st.markdown("#### Arma los 8 grupos (4 equipos c/u)")
        pool32 = list(dict.fromkeys(st.session_state.wc_qualified + [host]))[:32]
        if len(pool32) < 32:
            remaining = ALL_TEAMS + ["New Zealand"]
            for t in remaining:
                if t not in pool32 and len(pool32) < 32:
                    pool32.append(t)

        new_groups = {}
        group_labels = ["A","B","C","D","E","F","G","H"]
        cols1 = st.columns(4)
        cols2 = st.columns(4)
        for i, gl in enumerate(group_labels):
            col = cols1[i] if i < 4 else cols2[i-4]
            with col:
                st.markdown(f"**Grupo {gl}**")
                default_g = st.session_state.wc_groups.get(gl, pool32[i*4:(i+1)*4])
                chosen = st.multiselect(f"Grupo {gl}", pool32, default=default_g, max_selections=4, key=f"wc_grp_{gl}")
                new_groups[gl] = chosen

        if st.button("💾 Guardar grupos del Mundial"):
            all_a = sum(new_groups.values(), [])
            if len(all_a) != len(set(all_a)):
                st.error("Duplicados.")
            elif any(len(v) != 4 for v in new_groups.values()):
                st.error("4 por grupo.")
            else:
                st.session_state.wc_host = host
                st.session_state.wc_groups = new_groups
                all_m = {}
                for gl, teams in new_groups.items():
                    all_m.update(generate_group_matches(teams))
                st.session_state.wc_matches = all_m
                st.success("✅ Grupos del Mundial guardados.")
                st.rerun()

    with tab_groups:
        if not st.session_state.wc_groups:
            st.info("Configura los grupos primero.")
        else:
            for gl in ["A","B","C","D","E","F","G","H"]:
                teams = st.session_state.wc_groups.get(gl, [])
                if not teams: continue
                flags_str = " · ".join(f"{fl(t)} {t}" for t in teams)
                with st.expander(f"Grupo {gl} — {flags_str}", expanded=False):
                    col_m, col_t = st.columns([3, 2])
                    with col_m:
                        for t1, t2 in combinations(teams, 2):
                            key = (t1, t2) if (t1, t2) in st.session_state.wc_matches else (t2, t1)
                            res = st.session_state.wc_matches.get(key)
                            render_match_result(t1, t2, res)
                            if res is None:
                                r = match_input_form("wc", t1, t2, PLAYERS.get(t1,[]), PLAYERS.get(t2,[]), key_suffix=gl)
                                if r:
                                    hg, ag, sh, sa = r
                                    st.session_state.wc_matches[key] = {"hg": hg, "ag": ag, "scorers_h": sh, "scorers_a": sa}
                                    for s in sh: update_scorer(s, t1, 1, "wc_")
                                    for s in sa: update_scorer(s, t2, 1, "wc_")
                                    st.rerun()
                    with col_t:
                        gm = {k: v for k, v in st.session_state.wc_matches.items()
                              if k[0] in teams and k[1] in teams and v is not None}
                        s = compute_standings(teams, gm)
                        st.session_state.wc_standings[gl] = s
                        render_standings(s, highlight=2)

            st.divider()
            by_slot = {}
            for gl in ["A","B","C","D","E","F","G","H"]:
                s = st.session_state.wc_standings.get(gl, [])
                if len(s) >= 2:
                    by_slot[f"{gl}1"] = s[0]["team"]
                    by_slot[f"{gl}2"] = s[1]["team"]

            if len(by_slot) == 16:
                wc_r16 = [
                    (by_slot.get("A1","?"), by_slot.get("B2","?")),
                    (by_slot.get("C1","?"), by_slot.get("D2","?")),
                    (by_slot.get("E1","?"), by_slot.get("F2","?")),
                    (by_slot.get("G1","?"), by_slot.get("H2","?")),
                    (by_slot.get("B1","?"), by_slot.get("A2","?")),
                    (by_slot.get("D1","?"), by_slot.get("C2","?")),
                    (by_slot.get("F1","?"), by_slot.get("E2","?")),
                    (by_slot.get("H1","?"), by_slot.get("G2","?")),
                ]
                st.markdown("#### Bracket R16")
                cols = st.columns(4)
                for i, (t1, t2) in enumerate(wc_r16):
                    with cols[i % 4]:
                        st.markdown(
                            f"<div class='team-chip' style='padding:10px 6px;'>"
                            f"<span style='font-size:20px;'>{fl(t1)}</span>"
                            f"<div style='font-size:11px;color:var(--muted);margin:3px 0;'>vs</div>"
                            f"<span style='font-size:20px;'>{fl(t2)}</span>"
                            f"</div>",
                            unsafe_allow_html=True,
                        )

                if st.button("➡️ Generar R16 del Mundial"):
                    st.session_state.wc_r16 = wc_r16
                    st.session_state.wc_r16_results = {}
                    st.success("✅ R16 generado.")
                    st.rerun()

    with tab_ko:
        if not st.session_state.wc_r16:
            st.info("Completa los grupos y genera el R16 primero.")
        else:
            st.markdown("### ⚔️ Octavos de Final")
            r16w = []
            for i, (t1, t2) in enumerate(st.session_state.wc_r16):
                res = st.session_state.wc_r16_results.get(i)
                if res:
                    render_match_result(t1, t2, res); r16w.append(res["winner"])
                else:
                    r = knockout_input(f"wc_r16_{i}", t1, t2, PLAYERS.get(t1,[]), PLAYERS.get(t2,[]))
                    if r:
                        st.session_state.wc_r16_results[i] = r
                        for s in r.get("scorers_h",[]): update_scorer(s, t1, 1, "wc_")
                        for s in r.get("scorers_a",[]): update_scorer(s, t2, 1, "wc_")
                        st.rerun()
                    r16w.append(None)

            if all(r16w) and len(r16w) == 8:
                if not st.session_state.wc_qf:
                    st.session_state.wc_qf = [
                        (r16w[0], r16w[4]), (r16w[2], r16w[6]),
                        (r16w[1], r16w[5]), (r16w[3], r16w[7]),
                    ]

                st.markdown("### ⚔️ Cuartos de Final")
                qfw = []
                for i, (t1, t2) in enumerate(st.session_state.wc_qf):
                    res = st.session_state.wc_qf_results.get(i)
                    if res:
                        render_match_result(t1, t2, res); qfw.append(res["winner"])
                    else:
                        r = knockout_input(f"wc_qf_{i}", t1, t2, PLAYERS.get(t1,[]), PLAYERS.get(t2,[]))
                        if r:
                            st.session_state.wc_qf_results[i] = r
                            for s in r.get("scorers_h",[]): update_scorer(s, t1, 1, "wc_")
                            for s in r.get("scorers_a",[]): update_scorer(s, t2, 1, "wc_")
                            st.rerun()
                        qfw.append(None)

                if all(qfw) and len(qfw) == 4:
                    if not st.session_state.wc_sf:
                        st.session_state.wc_sf = [(qfw[0], qfw[1]), (qfw[2], qfw[3])]

                    st.markdown("### ⚔️ Semifinales")
                    sfw = []; sfl = []
                    for i, (t1, t2) in enumerate(st.session_state.wc_sf):
                        res = st.session_state.wc_sf_results.get(i)
                        if res:
                            render_match_result(t1, t2, res)
                            sfw.append(res["winner"]); sfl.append(t2 if res["winner"] == t1 else t1)
                        else:
                            r = knockout_input(f"wc_sf_{i}", t1, t2, PLAYERS.get(t1,[]), PLAYERS.get(t2,[]))
                            if r:
                                st.session_state.wc_sf_results[i] = r
                                for s in r.get("scorers_h",[]): update_scorer(s, t1, 1, "wc_")
                                for s in r.get("scorers_a",[]): update_scorer(s, t2, 1, "wc_")
                                st.rerun()
                            sfw.append(None)

                    if all(sfw) and len(sfw) == 2:
                        st.markdown("### 🥉 Tercer Puesto")
                        if len(sfl) == 2:
                            t3a, t3b = sfl[0], sfl[1]
                            res3 = st.session_state.wc_third_result
                            if res3:
                                render_match_result(t3a, t3b, res3)
                                st.markdown(f"🥉 **{fl(res3['winner'])} {res3['winner']}**")
                            else:
                                r = knockout_input("wc_3rd", t3a, t3b, PLAYERS.get(t3a,[]), PLAYERS.get(t3b,[]))
                                if r:
                                    st.session_state.wc_third = (t3a, t3b)
                                    st.session_state.wc_third_result = r
                                    st.rerun()

                        st.markdown("### 🏆 FINAL DEL MUNDIAL")
                        if st.session_state.wc_final is None:
                            st.session_state.wc_final = (sfw[0], sfw[1])
                        t1, t2 = st.session_state.wc_final
                        resf = st.session_state.wc_final_result
                        if resf:
                            render_match_result(t1, t2, resf)
                            champ_banner(resf["winner"], "CAMPEÓN DEL MUNDO 🌍")
                        else:
                            r = knockout_input("wc_final", t1, t2, PLAYERS.get(t1,[]), PLAYERS.get(t2,[]))
                            if r:
                                st.session_state.wc_final_result = r
                                champ = r["winner"]
                                st.session_state.wc_champion = champ
                                for s in r.get("scorers_h",[]): update_scorer(s, t1, 1, "wc_")
                                for s in r.get("scorers_a",[]): update_scorer(s, t2, 1, "wc_")
                                runner = t2 if champ == t1 else t1
                                fs_wc = [{"pos": 1, "team": champ}, {"pos": 2, "team": runner}]
                                update_ranking_from_standings(fs_wc, 200, 10)
                                st.rerun()

    with tab_result:
        if st.session_state.wc_champion:
            champ_banner(st.session_state.wc_champion, "🌍 CAMPEÓN DEL MUNDO")
            if st.session_state.wc_final_result:
                t1, t2 = st.session_state.wc_final
                r = st.session_state.wc_final_result
                render_match_result(t1, t2, r)
        else:
            st.info("El Mundial aún no tiene campeón.")


# ══════════════════════════════════════════════════════════════════════════════
# RANKING FIFA
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Ranking FIFA":
    conf_header("📊", "RANKING FIFA", "#6C63FF",
                "Se actualiza con cada torneo · Persiste entre temporadas")

    ranking = st.session_state.fifa_ranking
    sorted_r = sorted(ranking.items(), key=lambda x: x[1], reverse=True)

    c1, c2, c3 = st.columns(3)
    medals = ["🥇", "🥈", "🥉"]
    for col, (team, pts), medal in zip([c1,c2,c3], sorted_r[:3], medals):
        with col:
            st.markdown(
                f"<div class='card' style='text-align:center;border-top:3px solid var(--gold);padding:20px;'>"
                f"<div style='font-size:32px;'>{medal}</div>"
                f"<div style='font-size:48px;margin:6px 0;'>{fl(team)}</div>"
                f"<div style='font-family:Space Grotesk;font-size:18px;font-weight:700;'>{team}</div>"
                f"<div style='color:var(--primary);font-size:22px;font-weight:700;margin-top:6px;'>{pts}</div>"
                f"<div style='font-size:10px;color:var(--muted);letter-spacing:1px;'>PUNTOS FIFA</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    conf_teams_map = conf_team_map()
    filt = st.selectbox("Filtrar por confederación", ["Todas","UEFA","CONMEBOL","CAF","CONCACAF","AFC"])

    rows = []
    for pos, (t, pts) in enumerate(sorted_r, 1):
        if filt != "Todas" and t not in conf_teams_map.get(filt, []):
            continue
        conf = "—"
        for c, tl in conf_teams_map.items():
            if t in tl: conf = c; break
        rows.append({"Pos": pos, "Equipo": f"{fl(t)} {t}", "Conf": conf, "Puntos": pts})

    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

    if st.button("🔄 Resetear ranking inicial"):
        st.session_state.fifa_ranking = dict(INITIAL_FIFA_RANKING)
        st.success("✅ Reseteado.")
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# GOLEADORES
# ══════════════════════════════════════════════════════════════════════════════
elif page == "⚽ Goleadores":
    conf_header("⚽", "TABLA DE GOLEADORES", "#FF6B6B",
                "Registrados durante todos los torneos")

    scorers = st.session_state.top_scorers
    if not scorers:
        st.info("No hay goles registrados aún.")
    else:
        TOUR_PREFIX = {
            "euro_": "🌍 Eurocopa",
            "ca_":   "🌎 Copa América",
            "af_":   "🌍 Copa África",
            "co_":   "🌎 Copa Oro",
            "as_":   "🌏 Copa Asia",
            "wc_":   "🏆 Mundial",
        }
        filt_tour = st.selectbox("Torneo", ["Todos"] + list(TOUR_PREFIX.values()))

        rows = []
        for key, goals in sorted(scorers.items(), key=lambda x: x[1], reverse=True):
            parts = key.split("|")
            if len(parts) != 2: continue
            raw_key, team = parts[0], parts[1]
            tour = "—"; player = raw_key
            for pref, name in TOUR_PREFIX.items():
                if raw_key.startswith(pref):
                    tour = name; player = raw_key[len(pref):]
                    break
            if filt_tour != "Todos" and tour != filt_tour: continue
            rows.append({
                "Goles": goals,
                "Jugador": player,
                "Selección": f"{fl(team)} {team}",
                "Torneo": tour,
            })

        if rows:
            df = pd.DataFrame(rows)
            df.insert(0, "Pos", range(1, len(df)+1))
            st.dataframe(df, hide_index=True, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PLANTILLAS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "👥 Plantillas":
    conf_header("👥", "PLANTILLAS", "#06D6A0",
                "Jugadores por selección con link a SoFifa")

    conf_opts = {
        "UEFA 🌍":      UEFA_TEAMS,
        "CONMEBOL 🌎":  CONMEBOL_TEAMS,
        "CAF 🌍":       CAF_TEAMS,
        "CONCACAF 🌎":  CONCACAF_TEAMS,
        "AFC 🌏":       AFC_TEAMS,
        "Repechaje 🔄": ["New Zealand"],
    }

    c1, c2 = st.columns([1, 2])
    with c1:
        conf_sel = st.selectbox("Confederación", list(conf_opts.keys()))
    with c2:
        team_sel = st.selectbox("Selección", conf_opts[conf_sel])

    players = PLAYERS.get(team_sel, [])
    total = len(players)
    pos_counts = {}
    for p in players:
        pos_counts[p["pos"]] = pos_counts.get(p["pos"], 0) + 1

    ranking_pts = st.session_state.fifa_ranking.get(team_sel, "—")
    flag_emoji = fl(team_sel)

    _ps_html = ""
    for _pos in ["GK","DF","MF","FW"]:
        _c = POS_COLOR.get(_pos,"#aaa")
        _n = pos_counts.get(_pos, 0)
        _ps_html += (f"<div class='squad-stat'>"
                     f"<div class='squad-stat-val' style='color:{_c};'>{_n}</div>"
                     f"<div class='squad-stat-lbl'>{_pos}</div>"
                     f"</div>")

    st.markdown(
        f"<div class='squad-header'>"
        f"<div class='squad-flag'>{flag_emoji}</div>"
        f"<div>"
        f"<div class='squad-name'>{team_sel}</div>"
        f"<div class='squad-ranking'>FIFA RANKING — {ranking_pts} PTS</div>"
        f"<div class='squad-stats'>"
        f"<div class='squad-stat'><div class='squad-stat-val'>{total}</div><div class='squad-stat-lbl'>Total</div></div>"
        f"{_ps_html}"
        f"</div></div></div>",
        unsafe_allow_html=True,
    )

    if not players:
        st.info("Sin datos de jugadores para esta selección.")
    else:
        pos_filt = st.radio("Filtrar", ["Todas","GK","DF","MF","FW"], horizontal=True)
        filtered = [p for p in players if pos_filt == "Todas" or p["pos"] == pos_filt]

        if pos_filt == "Todas":
            html = ""
            num = 1
            for grp_pos in ["GK","DF","MF","FW"]:
                grp = [p for p in players if p["pos"] == grp_pos]
                if not grp: continue
                gc = POS_COLOR.get(grp_pos,"#aaa")
                html += (f"<div class='pos-section-title' style='color:{gc};'>"
                         f"{POS_ICON.get(grp_pos,'')} {POS_LABEL.get(grp_pos,grp_pos)} "
                         f"<span style='font-size:12px;opacity:.5;font-weight:400;'>({len(grp)})</span></div>"
                         f"<div class='player-grid'>")
                for p in grp:
                    name = p["name"]; pos = p["pos"]
                    sofifa_url = f"https://sofifa.com/players?keyword={name.replace(' ','+')}"
                    html += (f"<div class='player-card pos-{pos}'>"
                             f"<div class='player-pos pos-{pos}-badge'>{pos}</div>"
                             f"<div class='player-name'>{name}</div>"
                             f"<a class='player-link' href='{sofifa_url}' target='_blank'>🔗 SoFifa</a>"
                             f"</div>")
                    num += 1
                html += "</div>"
            st.markdown(html, unsafe_allow_html=True)
        else:
            html = "<div class='player-grid'>"
            for p in filtered:
                name = p["name"]; pos = p["pos"]
                sofifa_url = f"https://sofifa.com/players?keyword={name.replace(' ','+')}"
                html += (f"<div class='player-card pos-{pos}'>"
                         f"<div class='player-pos pos-{pos}-badge'>{pos}</div>"
                         f"<div class='player-name'>{name}</div>"
                         f"<a class='player-link' href='{sofifa_url}' target='_blank'>🔗 SoFifa</a>"
                         f"</div>")
            html += "</div>"
            st.markdown(html, unsafe_allow_html=True)
