"""
app.py - MMJ World Cup Simulator
Entrada manual de resultados · Mejoras visuales v2
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
    page_title="MMJ World Cup",
    page_icon="\u26BD",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow:wght@400;600;700&family=Barlow+Condensed:wght@400;600;700&display=swap');

:root {
  --g:    #00E5A0;
  --g2:   #00B87A;
  --acc:  #FF5722;
  --dark: #080D14;
  --card: #0F1623;
  --card2:#16202E;
  --border: rgba(0,229,160,.15);
  --txt:  #DDE4EF;
  --muted:#6B7A99;
}
*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
  font-family: 'Barlow', sans-serif;
  background: var(--dark) !important;
  color: var(--txt) !important;
}
.stApp { background: var(--dark) !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg,#0A1020 0%,#0F1825 100%) !important;
  border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] * { color: var(--txt) !important; }

/* ── Buttons ── */
.stButton > button {
  background: linear-gradient(135deg, var(--g), var(--g2)) !important;
  color: #080D14 !important;
  font-family: 'Bebas Neue', cursive !important;
  font-size: 15px !important;
  letter-spacing: 2px !important;
  border: none !important;
  border-radius: 6px !important;
  padding: 8px 22px !important;
  transition: all .2s !important;
  width: 100% !important;
}
.stButton > button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 20px rgba(0,229,160,.35) !important;
}

/* ── Headings ── */
h1, h2, h3, h4 {
  font-family: 'Bebas Neue', cursive !important;
  letter-spacing: 3px !important;
  color: var(--txt) !important;
}

/* ── Cards ── */
.card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 16px;
  margin: 6px 0;
}
.card-g    { border-left: 4px solid var(--g)      !important; }
.card-acc  { border-left: 4px solid var(--acc)     !important; }
.card-gold { border-left: 4px solid #FFD700        !important; }
.card-blue { border-left: 4px solid #4A90D9        !important; }
.card-green{ border-left: 4px solid #27AE60        !important; }

/* ── Hero ── */
.hero {
  font-family: 'Bebas Neue', cursive;
  font-size: 72px;
  letter-spacing: 10px;
  background: linear-gradient(135deg, #00E5A0, #FFD700);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-align: center;
  line-height: 1;
}
.sub {
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 14px;
  letter-spacing: 6px;
  color: var(--muted);
  text-align: center;
  text-transform: uppercase;
  margin-bottom: 28px;
}

/* ── Badges ── */
.badge { display:inline-block; padding:2px 10px; border-radius:12px; font-size:11px; font-weight:700; letter-spacing:1px; }
.badge-g    { background:rgba(0,229,160,.15);  color:var(--g);   border:1px solid var(--g);   }
.badge-acc  { background:rgba(255,87,34,.15);  color:var(--acc); border:1px solid var(--acc); }
.badge-gold { background:rgba(255,215,0,.15);  color:#FFD700;    border:1px solid #FFD700;     }

/* ── Match row ── */
.match-row {
  background: var(--card2);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 10px 14px;
  margin: 4px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* ── Tables ── */
thead tr th {
  background: rgba(0,229,160,.08) !important;
  color: var(--g) !important;
  font-family: 'Bebas Neue', cursive !important;
  letter-spacing: 1.5px !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab"] {
  font-family: 'Bebas Neue', cursive !important;
  letter-spacing: 2px !important;
  font-size: 15px !important;
}

/* ── Inputs ── */
.stSelectbox > label,
.stMultiSelect > label,
.stNumberInput > label {
  font-family: 'Barlow Condensed', sans-serif !important;
  font-size: 13px !important;
  letter-spacing: 2px !important;
  color: var(--muted) !important;
  text-transform: uppercase !important;
}

hr { border-color: var(--border) !important; }

[data-testid="metric-container"] {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 14px;
}

/* ── Player Card Grid ── */
.player-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 12px;
  margin-top: 12px;
}
.player-card {
  background: linear-gradient(145deg, var(--card2) 0%, rgba(0,0,0,0.3) 100%);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 14px 10px 10px;
  text-align: center;
  transition: border-color .25s, transform .25s, box-shadow .25s;
  cursor: default;
  position: relative;
  overflow: hidden;
}
.player-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  border-radius: 12px 12px 0 0;
}
.player-card.pos-GK-card::before { background: #F0A500; }
.player-card.pos-DF-card::before { background: #2196F3; }
.player-card.pos-MF-card::before { background: #4CAF50; }
.player-card.pos-FW-card::before { background: #F44336; }
.player-card:hover {
  border-color: var(--g);
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(0,229,160,0.15);
}
.player-card .pos-badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 1.5px;
  margin: 0 0 8px;
}
.player-card .picon {
  font-size: 24px;
  line-height: 1;
  margin-bottom: 6px;
  display: block;
}
.player-card .pname {
  font-family: 'Barlow Condensed', sans-serif;
  font-weight: 700;
  font-size: 13px;
  line-height: 1.3;
  color: var(--txt);
  min-height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.player-card .pnum {
  font-family: 'Bebas Neue', cursive;
  font-size: 28px;
  line-height: 1;
  color: rgba(255,255,255,0.08);
  position: absolute;
  top: 6px; right: 10px;
}
.player-card a {
  font-size: 10px;
  color: var(--g);
  text-decoration: none;
  letter-spacing: 1px;
  opacity: 0.7;
  transition: opacity .2s;
}
.player-card a:hover { opacity: 1; text-decoration: underline; }
.pos-section-title {
  font-family: 'Bebas Neue', cursive;
  font-size: 18px;
  letter-spacing: 4px;
  color: var(--muted);
  margin: 20px 0 8px;
  padding-left: 4px;
  border-bottom: 1px solid var(--border);
  padding-bottom: 6px;
}

/* Position colors */
.pos-GK { background: rgba(240,165,0,.18);  color:#F0A500; border:1px solid #F0A500; }
.pos-DF { background: rgba(33,150,243,.18); color:#2196F3; border:1px solid #2196F3; }
.pos-MF { background: rgba(76,175,80,.18);  color:#4CAF50; border:1px solid #4CAF50; }
.pos-FW { background: rgba(244,67,54,.18);  color:#F44336; border:1px solid #F44336; }

/* ── Squad header ── */
.squad-header {
  display: flex;
  align-items: center;
  gap: 16px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px 24px;
  margin-bottom: 20px;
}
.squad-flag  { font-size: 64px; line-height: 1; }
.squad-info  { flex: 1; }
.squad-name  { font-family:'Bebas Neue',cursive; font-size:36px; letter-spacing:4px; }
.squad-sub   { color: var(--muted); font-size:13px; letter-spacing:2px; margin-top:2px; }
.squad-stats { display:flex; gap:20px; margin-top:10px; }
.squad-stat  { text-align:center; }
.squad-stat-val { font-family:'Bebas Neue',cursive; font-size:26px; color:var(--g); }
.squad-stat-lbl { font-size:10px; letter-spacing:2px; color:var(--muted); text-transform:uppercase; }

/* ── Position filter pills ── */
.pos-filter { display:flex; gap:8px; flex-wrap:wrap; margin:12px 0; }

/* ── Conf header ── */
.conf-hdr {
  border-left: 4px solid #00E5A0;
  padding: 8px 16px;
  margin-bottom: 20px;
}
.conf-hdr-title { font-family:'Bebas Neue',cursive; font-size:34px; letter-spacing:4px; }
.conf-hdr-sub   { color:var(--muted); font-size:12px; letter-spacing:2px; margin-top:2px; }
</style>
""", unsafe_allow_html=True)

init_state()

# ─────────────────────────────────────────────
# HELPERS GLOBALES
# ─────────────────────────────────────────────

def fl(team):
    return FLAG_MAP.get(team, "\U0001F3F3\uFE0F")

POS_COLOR = {"GK": "#F0A500", "DF": "#2196F3", "MF": "#4CAF50", "FW": "#F44336"}


def standings_df(standings, highlight=0, repechaje_pos=None):
    rows = []
    for s in standings:
        pos = s["pos"]
        team = s["team"]
        if pos <= highlight:
            st_txt = "\u2705 Clasifica"
        elif repechaje_pos and pos == repechaje_pos:
            st_txt = "\U0001F504 Repechaje"
        else:
            st_txt = "\u274C"
        rows.append({
            "Pos": pos,
            "Equipo": f"{fl(team)} {team}",
            "Pts": s["pts"],
            "PJ": s["played"],
            "G": s["w"],
            "E": s["d"],
            "P": s["l"],
            "GF": s["gf"],
            "GC": s["ga"],
            "GD": s["gd"],
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


def match_input_form(prefix, t1, t2, players_t1, players_t2, key_suffix=""):
    key_base = f"{prefix}_{t1}_{t2}_{key_suffix}"
    with st.expander(f"{fl(t1)} {t1}  vs  {fl(t2)} {t2}", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            hg = st.number_input(f"Goles {t1}", min_value=0, max_value=20, step=1, key=f"{key_base}_hg")
        with col2:
            ag = st.number_input(f"Goles {t2}", min_value=0, max_value=20, step=1, key=f"{key_base}_ag")

        scorers_h = []
        scorers_a = []
        if hg > 0 and players_t1:
            st.markdown(f"<small style='color:var(--muted)'>\u26BD Goleadores {t1}</small>", unsafe_allow_html=True)
            pnames = [p["name"] for p in players_t1]
            for g in range(int(hg)):
                scorer = st.selectbox(f"Gol {g+1}", ["(sin registrar)"] + pnames, key=f"{key_base}_sh_{g}")
                if scorer != "(sin registrar)":
                    scorers_h.append(scorer)

        if ag > 0 and players_t2:
            st.markdown(f"<small style='color:var(--muted)'>\u26BD Goleadores {t2}</small>", unsafe_allow_html=True)
            pnames2 = [p["name"] for p in players_t2]
            for g in range(int(ag)):
                scorer = st.selectbox(f"Gol {g+1}", ["(sin registrar)"] + pnames2, key=f"{key_base}_sa_{g}")
                if scorer != "(sin registrar)":
                    scorers_a.append(scorer)

        if st.button("\U0001F4BE Guardar resultado", key=f"{key_base}_save"):
            return int(hg), int(ag), scorers_h, scorers_a
    return None


def render_match_result(t1, t2, res):
    if res is None:
        st.markdown(
            f"<div class='match-row'>{fl(t1)} {t1} "
            f"<span style='color:var(--muted)'>vs</span> {fl(t2)} {t2} "
            f"<span style='color:var(--muted);font-size:12px;margin-left:auto;'>\u23F3 Pendiente</span></div>",
            unsafe_allow_html=True,
        )
    else:
        hg = res.get("hg", 0)
        ag = res.get("ag", 0)
        hcolor = "#00E5A0" if hg > ag else "#F44336" if hg < ag else "#888"
        acolor = "#00E5A0" if ag > hg else "#F44336" if ag < hg else "#888"
        sh = " ".join(f"<span style='font-size:10px;color:#aaa'>\u26BD{s}</span>" for s in res.get("scorers_h", []))
        sa = " ".join(f"<span style='font-size:10px;color:#aaa'>\u26BD{s}</span>" for s in res.get("scorers_a", []))
        st.markdown(
            f"<div class='match-row'>"
            f"<span style='color:{hcolor};font-weight:700'>{fl(t1)} {t1}</span>"
            f"<span style='background:var(--card);padding:2px 12px;border-radius:6px;"
            f"font-family:Bebas Neue;font-size:20px;margin:0 10px;'>{hg} \u2013 {ag}</span>"
            f"<span style='color:{acolor};font-weight:700'>{fl(t2)} {t2}</span>"
            f"<span style='margin-left:auto;'>{sh} &nbsp; {sa}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )


def knockout_input(prefix, t1, t2, players_t1, players_t2, allow_draw=False):
    key_base = f"ko_{prefix}_{t1}_{t2}"
    with st.expander(f"\u2694\uFE0F {fl(t1)} {t1}  vs  {fl(t2)} {t2}", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            hg = st.number_input(f"Goles {t1}", 0, 20, 0, key=f"{key_base}_hg")
        with col2:
            ag = st.number_input(f"Goles {t2}", 0, 20, 0, key=f"{key_base}_ag")

        winner = None
        penalty_winner = None
        if hg == ag and not allow_draw:
            st.markdown("<small style='color:#F0A500'>\u26A0\uFE0F Empate \u2192 definir por penaltis</small>", unsafe_allow_html=True)
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
                s = st.selectbox(f"\u26BD Gol {g+1} ({t1})", ["(sin registrar)"] + pn, key=f"{key_base}_sh{g}")
                if s != "(sin registrar)":
                    scorers_h.append(s)
        if ag > 0 and players_t2:
            pn2 = [p["name"] for p in players_t2]
            for g in range(int(ag)):
                s = st.selectbox(f"\u26BD Gol {g+1} ({t2})", ["(sin registrar)"] + pn2, key=f"{key_base}_sa{g}")
                if s != "(sin registrar)":
                    scorers_a.append(s)

        if st.button("\U0001F4BE Guardar", key=f"{key_base}_save"):
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


def champ_banner(team, title="CAMPE\u00D3N"):
    st.markdown(f"""
    <div class='card card-gold' style='text-align:center;padding:32px;margin:16px 0;'>
      <div style='font-size:60px;'>{fl(team)}</div>
      <div style='font-family:Bebas Neue;font-size:44px;letter-spacing:6px;color:#FFD700;'>\U0001F3C6 {title}</div>
      <div style='font-family:Bebas Neue;font-size:30px;letter-spacing:4px;margin-top:4px;'>{team}</div>
    </div>""", unsafe_allow_html=True)


def conf_header(emoji, name, color, info=""):
    st.markdown(f"""
    <div class='conf-hdr' style='border-left-color:{color};'>
      <div class='conf-hdr-title'>{emoji} {name}</div>
      <div class='conf-hdr-sub'>{info}</div>
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:16px 0 10px;'>
      <div style='font-family:Bebas Neue;font-size:32px;letter-spacing:6px;color:#00E5A0;'>\u26BD MMJ</div>
      <div style='font-size:10px;letter-spacing:4px;color:#6B7A99;'>WORLD CUP SIMULATOR</div>
    </div>""", unsafe_allow_html=True)
    st.divider()

    PAGES = [
        "\U0001F3E0 Inicio",
        "\U0001F30D UEFA \u00B7 Eurocopa",
        "\U0001F522 UEFA \u00B7 Playoffs Mundial",
        "\U0001F30E CONMEBOL \u00B7 Copa Am\u00E9rica",
        "\U0001F522 CONMEBOL \u00B7 Playoffs",
        "\U0001F30D CAF \u00B7 Copa \u00C1frica",
        "\U0001F522 CAF \u00B7 Playoffs",
        "\U0001F30E CONCACAF \u00B7 Copa Oro",
        "\U0001F522 CONCACAF \u00B7 Playoffs",
        "\U0001F30F AFC \u00B7 Copa Asia",
        "\U0001F522 AFC \u00B7 Playoffs",
        "\U0001F504 Repechaje Internacional",
        "\U0001F3C6 Mundial",
        "\U0001F4CA Ranking FIFA",
        "\u26BD Goleadores",
        "\U0001F465 Plantillas",
    ]
    for p in PAGES:
        if st.button(p, key=f"nav_{p}", use_container_width=True):
            st.session_state.active_page = p
            st.rerun()

    st.divider()
    st.markdown(f"<div style='text-align:center;font-size:12px;color:var(--muted);'>Temporada {st.session_state.season}</div>", unsafe_allow_html=True)
    nq = len(st.session_state.wc_qualified)
    st.markdown(f"<div style='text-align:center;font-size:14px;color:var(--g);font-weight:700;'>{nq}/32 clasificados</div>", unsafe_allow_html=True)

page = st.session_state.active_page

# ══════════════════════════════════════════════
# INICIO
# ══════════════════════════════════════════════
if page == "\U0001F3E0 Inicio":
    st.markdown("<div class='hero'>MMJ WORLD CUP</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub'>Simulador Manual \u00B7 Temporada {st.session_state.season}</div>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Clasificados", f"{len(st.session_state.wc_qualified)}/32")
    champ = st.session_state.wc_champion or "\u2014"
    c2.metric("\U0001F3C6 Campe\u00F3n", champ)
    rnk1 = max(st.session_state.fifa_ranking, key=st.session_state.fifa_ranking.get)
    c3.metric("Ranking #1", f"{fl(rnk1)} {rnk1}")
    c4.metric("Temporada", st.session_state.season)

    st.divider()
    st.markdown("### \U0001F4CB Estado de Torneos")
    cups = [
        ("\U0001F30D Eurocopa",   "euro_champion", "UEFA",     "#4A90D9"),
        ("\U0001F30E Copa Am\u00E9rica", "ca_champion",  "CONMEBOL", "#27AE60"),
        ("\U0001F30D Copa \u00C1frica", "af_champion",  "CAF",      "#F39C12"),
        ("\U0001F30E Copa Oro",   "co_champion",  "CONCACAF", "#E74C3C"),
        ("\U0001F30F Copa Asia",  "as_champion",  "AFC",      "#9B59B6"),
    ]
    cols = st.columns(5)
    for col, (name, key, conf, color) in zip(cols, cups):
        champ_val = st.session_state.get(key)
        with col:
            st.markdown(f"""
            <div class='card' style='border-left:4px solid {color};text-align:center;padding:14px;'>
              <div style='font-size:10px;color:{color};letter-spacing:2px;text-transform:uppercase;'>{conf}</div>
              <div style='font-weight:700;font-size:13px;margin:4px 0;'>{name}</div>
              {"<div style='color:#FFD700;font-size:13px;'>\U0001F3C6 "+fl(champ_val)+" "+champ_val+"</div>"
               if champ_val else
               "<div style='color:var(--muted);font-size:12px;'>\u23F3 Pendiente</div>"}
            </div>""", unsafe_allow_html=True)

    if st.session_state.wc_qualified:
        st.divider()
        st.markdown("### \u2705 Clasificados al Mundial")
        teams = st.session_state.wc_qualified
        for i in range(0, len(teams), 6):
            cols = st.columns(6)
            for j, t in enumerate(teams[i:i+6]):
                with cols[j]:
                    st.markdown(
                        f"<div class='card' style='text-align:center;padding:10px;'>"
                        f"<div style='font-size:26px;'>{fl(t)}</div>"
                        f"<div style='font-size:11px;margin-top:4px;'>{t}</div></div>",
                        unsafe_allow_html=True,
                    )

    if st.session_state.wc_champion:
        st.divider()
        champ_banner(st.session_state.wc_champion, "CAMPE\u00D3N DEL MUNDO")
        if st.button("\U0001F504 Nueva Temporada"):
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

# ══════════════════════════════════════════════
# EUROCOPA
# ══════════════════════════════════════════════
elif page == "\U0001F30D UEFA \u00B7 Eurocopa":
    conf_header("\U0001F30D", "EUROCOPA UEFA", "#4A90D9", "24 equipos \u00B7 6 grupos de 4 \u00B7 Pasan 2 por grupo + 4 mejores 3ros \u2192 R16")

    tab_setup, tab_groups, tab_ko, tab_result = st.tabs(["\u2699\uFE0F Configurar", "\U0001F4CA Grupos", "\U0001F3AF Eliminatorias", "\U0001F3C6 Resultado"])

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

            if st.button("\U0001F4BE Guardar grupos"):
                all_assigned = sum(new_groups.values(), [])
                if len(all_assigned) != len(set(all_assigned)):
                    st.error("Un equipo est\u00E1 en m\u00E1s de un grupo.")
                elif any(len(v) != 4 for v in new_groups.values()):
                    st.error("Cada grupo debe tener exactamente 4 equipos.")
                else:
                    st.session_state.euro_groups = new_groups
                    all_matches = {}
                    for gl, teams in new_groups.items():
                        m = generate_group_matches(teams)
                        all_matches.update(m)
                    st.session_state.euro_matches = all_matches
                    st.success("\u2705 Grupos guardados. Ve a la pesta\u00F1a Grupos para ingresar resultados.")
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
                with st.expander(f"\U0001F5C2\uFE0F Grupo {gl} \u2014 {' \u00B7 '.join(fl(t)+' '+t for t in teams)}", expanded=True):
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
            st.markdown("#### \U0001F4CB Clasificados al R16")
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
                            f"<div class='card' style='text-align:center;padding:8px;'>"
                            f"<span style='font-size:10px;color:var(--muted);'>{lbl}</span><br>"
                            f"<span style='font-size:22px;'>{fl(t)}</span><br>"
                            f"<span style='font-size:12px;'>{t}</span></div>",
                            unsafe_allow_html=True,
                        )

                if st.button("\u27A1\uFE0F Generar R16 con estos clasificados") and len(all_r16) == 16:
                    by_slot = {lbl: t for lbl, t in all_r16}
                    r16_pairs = [
                        (by_slot.get("A1", "?"), by_slot.get("C2", "?")),
                        (by_slot.get("D1", "?"), by_slot.get("F2", "?")),
                        (by_slot.get("B1", "?"), by_slot.get("E2", "?")),
                        (by_slot.get("A2", "?"), by_slot.get("B2", "?")),
                        (by_slot.get("C1", "?"), by_slot.get("D2", "?")),
                        (by_slot.get("E1", "?"), by_slot.get("F1", "?")),
                        (best_thirds[0][1] if best_thirds else "?", best_thirds[1][1] if len(best_thirds) > 1 else "?"),
                        (best_thirds[2][1] if len(best_thirds) > 2 else "?", best_thirds[3][1] if len(best_thirds) > 3 else "?"),
                    ]
                    st.session_state.euro_r16 = r16_pairs
                    st.session_state.euro_r16_results = {}
                    st.success("\u2705 R16 generado. Ve a Eliminatorias.")
                    st.rerun()

    with tab_ko:
        if not st.session_state.euro_r16:
            st.info("Completa los grupos y genera el R16 primero.")
        else:
            st.markdown("### \u2694\uFE0F Octavos de Final (R16)")
            r16_winners = []
            for i, (t1, t2) in enumerate(st.session_state.euro_r16):
                res = st.session_state.euro_r16_results.get(i)
                if res:
                    render_match_result(t1, t2, res)
                    r16_winners.append(res["winner"])
                else:
                    r = knockout_input(f"euro_r16_{i}", t1, t2, PLAYERS.get(t1, []), PLAYERS.get(t2, []))
                    if r:
                        st.session_state.euro_r16_results[i] = r
                        for s in r.get("scorers_h", []): update_scorer(s, t1, 1, "euro_")
                        for s in r.get("scorers_a", []): update_scorer(s, t2, 1, "euro_")
                        st.rerun()
                    r16_winners.append(None)

            if all(r16_winners) and len(r16_winners) == 8:
                if not st.session_state.euro_qf:
                    st.session_state.euro_qf = [(r16_winners[i], r16_winners[i+1]) for i in range(0, 8, 2)]

                st.markdown("### \u2694\uFE0F Cuartos de Final")
                qf_winners = []
                for i, (t1, t2) in enumerate(st.session_state.euro_qf):
                    if t1 is None or t2 is None:
                        continue
                    res = st.session_state.euro_qf_results.get(i)
                    if res:
                        render_match_result(t1, t2, res)
                        qf_winners.append(res["winner"])
                    else:
                        r = knockout_input(f"euro_qf_{i}", t1, t2, PLAYERS.get(t1, []), PLAYERS.get(t2, []))
                        if r:
                            st.session_state.euro_qf_results[i] = r
                            for s in r.get("scorers_h", []): update_scorer(s, t1, 1, "euro_")
                            for s in r.get("scorers_a", []): update_scorer(s, t2, 1, "euro_")
                            st.rerun()
                        qf_winners.append(None)

                if all(qf_winners) and len(qf_winners) == 4:
                    if not st.session_state.euro_sf:
                        st.session_state.euro_sf = [(qf_winners[0], qf_winners[1]), (qf_winners[2], qf_winners[3])]

                    st.markdown("### \u2694\uFE0F Semifinales")
                    sf_winners = []
                    sf_losers = []
                    for i, (t1, t2) in enumerate(st.session_state.euro_sf):
                        if t1 is None or t2 is None:
                            continue
                        res = st.session_state.euro_sf_results.get(i)
                        if res:
                            render_match_result(t1, t2, res)
                            sf_winners.append(res["winner"])
                            sf_losers.append(t2 if res["winner"] == t1 else t1)
                        else:
                            r = knockout_input(f"euro_sf_{i}", t1, t2, PLAYERS.get(t1, []), PLAYERS.get(t2, []))
                            if r:
                                st.session_state.euro_sf_results[i] = r
                                for s in r.get("scorers_h", []): update_scorer(s, t1, 1, "euro_")
                                for s in r.get("scorers_a", []): update_scorer(s, t2, 1, "euro_")
                                st.rerun()
                            sf_winners.append(None)

                    if all(sf_winners) and len(sf_winners) == 2:
                        if st.session_state.euro_final is None:
                            st.session_state.euro_final = (sf_winners[0], sf_winners[1])

                        st.markdown("### \U0001F3C6 FINAL")
                        t1, t2 = st.session_state.euro_final
                        res = st.session_state.euro_final_result
                        if res:
                            render_match_result(t1, t2, res)
                            champ_banner(res["winner"], "CAMPE\u00D3N DE EUROPA")
                        else:
                            r = knockout_input("euro_final", t1, t2, PLAYERS.get(t1, []), PLAYERS.get(t2, []))
                            if r:
                                st.session_state.euro_final_result = r
                                st.session_state.euro_champion = r["winner"]
                                for s in r.get("scorers_h", []): update_scorer(s, t1, 1, "euro_")
                                for s in r.get("scorers_a", []): update_scorer(s, t2, 1, "euro_")
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
            champ_banner(st.session_state.euro_champion, "CAMPE\u00D3N DE EUROPA")
            st.markdown("#### \U0001F4CA Clasificaci\u00F3n Final")
            render_standings(st.session_state.euro_final_standings[:10], highlight=5)
            st.info(f"El campe\u00F3n **{st.session_state.euro_champion}** va directo al Mundial.")
        else:
            st.info("La Eurocopa a\u00FAn no tiene resultado final.")

# ══════════════════════════════════════════════
# UEFA PLAYOFFS
# ══════════════════════════════════════════════
elif page == "\U0001F522 UEFA \u00B7 Playoffs Mundial":
    conf_header("\U0001F522", "UEFA \u00B7 ELIMINATORIAS MUNDIALISTAS", "#4A90D9",
                "Puestos 6-21 Eurocopa \u2192 4 grupos de 4 \u00B7 Top 2 c/u \u2192 Mundial")

    if not st.session_state.euro_final_standings:
        st.warning("Primero completa la Eurocopa.")
    else:
        fs = st.session_state.euro_final_standings
        pool = [e["team"] for e in fs[5:21]]

        tab1, tab2 = st.tabs(["\u2699\uFE0F Grupos", "\U0001F4CA Resultados"])
        with tab1:
            st.markdown("**Equipos disponibles (puestos 6-21 Eurocopa):**")
            st.write(" \u00B7 ".join(f"{fl(t)} {t}" for t in pool))
            st.markdown("---")
            st.markdown("**Arma los 4 grupos (4 equipos c/u):**")
            cols = st.columns(4)
            new_groups = {}
            for i, gl in enumerate(["A", "B", "C", "D"]):
                with cols[i]:
                    st.markdown(f"**Grupo {gl}**")
                    default_g = st.session_state.euro_playoff_groups.get(gl, pool[i*4:(i+1)*4])
                    chosen = st.multiselect(f"Grupo {gl}", pool, default=default_g, max_selections=4, key=f"ep_grp_{gl}")
                    new_groups[gl] = chosen

            if st.button("\U0001F4BE Guardar grupos playoff"):
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
                    st.success("\u2705 Grupos guardados.")
                    st.rerun()

        with tab2:
            if not st.session_state.euro_playoff_groups:
                st.info("Arma los grupos primero.")
            else:
                for gl in ["A", "B", "C", "D"]:
                    teams = st.session_state.euro_playoff_groups.get(gl, [])
                    if not teams:
                        continue
                    with st.expander(f"Grupo {gl}", expanded=True):
                        col_m, col_t = st.columns([3, 2])
                        with col_m:
                            for t1, t2 in combinations(teams, 2):
                                key = (t1, t2) if (t1, t2) in st.session_state.euro_playoff_matches else (t2, t1)
                                res = st.session_state.euro_playoff_matches.get(key)
                                render_match_result(t1, t2, res)
                                if res is None:
                                    r = match_input_form("ep", t1, t2, PLAYERS.get(t1, []), PLAYERS.get(t2, []), key_suffix=gl)
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

                st.markdown(f"#### \u2705 Clasificados al Mundial via Playoffs UEFA ({len(qualified)})")
                for t in qualified:
                    st.markdown(f"\u2705 {fl(t)} **{t}**")

                if st.button("\U0001F4BE Confirmar clasificados UEFA al Mundial"):
                    euro_direct = [e["team"] for e in st.session_state.euro_final_standings[:5]]
                    all_uefa = list(set(euro_direct + qualified))
                    for t in all_uefa:
                        if t not in st.session_state.wc_qualified:
                            st.session_state.wc_qualified.append(t)
                    st.session_state.euro_playoff_qualified = all_uefa
                    st.success(f"\u2705 {len(all_uefa)} equipos UEFA confirmados al Mundial.")

# ══════════════════════════════════════════════
# COPA AMERICA
# ══════════════════════════════════════════════
elif page == "\U0001F30E CONMEBOL \u00B7 Copa Am\u00E9rica":
    conf_header("\U0001F30E", "COPA AM\u00C9RICA", "#27AE60",
                "10 equipos CONMEBOL + 6 invitados \u00B7 4 grupos de 4 \u00B7 2 pasan por grupo")

    tab_setup, tab_groups, tab_ko, tab_result = st.tabs(["\u2699\uFE0F Config", "\U0001F4CA Grupos", "\U0001F3AF Bracket", "\U0001F3C6 Resultado"])

    with tab_setup:
        st.markdown("#### Equipos invitados (6, no UEFA)")
        guests = st.multiselect("Selecciona 6 invitados", COPA_AMERICA_GUESTS_POOL,
                                default=st.session_state.ca_teams[10:] if len(st.session_state.ca_teams) == 16 else [],
                                max_selections=6)
        all_ca = CONMEBOL_TEAMS + guests
        st.markdown(f"**Total: {len(all_ca)}/16 equipos**")
        if len(all_ca) == 16:
            st.markdown("---")
            st.markdown("**Arma 4 grupos de 4:**")
            cols = st.columns(4)
            new_groups = {}
            for i, gl in enumerate(["A", "B", "C", "D"]):
                with cols[i]:
                    st.markdown(f"**Grupo {gl}**")
                    default_g = st.session_state.ca_groups.get(gl, all_ca[i*4:(i+1)*4])
                    chosen = st.multiselect(f"Grupo {gl}", all_ca, default=default_g, max_selections=4, key=f"ca_grp_{gl}")
                    new_groups[gl] = chosen

            if st.button("\U0001F4BE Guardar grupos Copa Am\u00E9rica"):
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
                    st.success("\u2705 Grupos guardados.")
                    st.rerun()

    with tab_groups:
        if not st.session_state.ca_groups:
            st.info("Configura los grupos primero.")
        else:
            for gl in ["A", "B", "C", "D"]:
                teams = st.session_state.ca_groups.get(gl, [])
                if not teams:
                    continue
                with st.expander(f"Grupo {gl}", expanded=True):
                    col_m, col_t = st.columns([3, 2])
                    with col_m:
                        for t1, t2 in combinations(teams, 2):
                            key = (t1, t2) if (t1, t2) in st.session_state.ca_matches else (t2, t1)
                            res = st.session_state.ca_matches.get(key)
                            render_match_result(t1, t2, res)
                            if res is None:
                                r = match_input_form("ca", t1, t2, PLAYERS.get(t1, []), PLAYERS.get(t2, []), key_suffix=gl)
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
                st.markdown("#### Bracket R16 Copa Am\u00E9rica")
                ca_r16 = [
                    (by_slot.get("A1", "?"), by_slot.get("D2", "?")),
                    (by_slot.get("C1", "?"), by_slot.get("B2", "?")),
                    (by_slot.get("B1", "?"), by_slot.get("C2", "?")),
                    (by_slot.get("D1", "?"), by_slot.get("A2", "?")),
                ]
                for t1, t2 in ca_r16:
                    st.markdown(f"- {fl(t1)} **{t1}** vs {fl(t2)} **{t2}**")

                if st.button("\u27A1\uFE0F Generar Bracket QF/SF/Final"):
                    st.session_state.ca_r16 = ca_r16
                    st.session_state.ca_r16_results = {}
                    st.success("\u2705 Bracket generado.")
                    st.rerun()

    with tab_ko:
        if not st.session_state.ca_r16:
            st.info("Completa grupos y genera bracket primero.")
        else:
            st.markdown("### \u2694\uFE0F Cuartos de Final")
            r16_winners = []
            for i, (t1, t2) in enumerate(st.session_state.ca_r16):
                res = st.session_state.ca_r16_results.get(i)
                if res:
                    render_match_result(t1, t2, res)
                    r16_winners.append(res["winner"])
                else:
                    r = knockout_input(f"ca_r16_{i}", t1, t2, PLAYERS.get(t1, []), PLAYERS.get(t2, []))
                    if r:
                        st.session_state.ca_r16_results[i] = r
                        for s in r.get("scorers_h", []): update_scorer(s, t1, 1, "ca_")
                        for s in r.get("scorers_a", []): update_scorer(s, t2, 1, "ca_")
                        st.rerun()
                    r16_winners.append(None)

            if all(r16_winners) and len(r16_winners) == 4:
                if not st.session_state.ca_sf:
                    st.session_state.ca_sf = [(r16_winners[0], r16_winners[1]), (r16_winners[2], r16_winners[3])]

                st.markdown("### \u2694\uFE0F Semifinales")
                sf_winners = []
                for i, (t1, t2) in enumerate(st.session_state.ca_sf):
                    res = st.session_state.ca_sf_results.get(i)
                    if res:
                        render_match_result(t1, t2, res)
                        sf_winners.append(res["winner"])
                    else:
                        r = knockout_input(f"ca_sf_{i}", t1, t2, PLAYERS.get(t1, []), PLAYERS.get(t2, []))
                        if r:
                            st.session_state.ca_sf_results[i] = r
                            for s in r.get("scorers_h", []): update_scorer(s, t1, 1, "ca_")
                            for s in r.get("scorers_a", []): update_scorer(s, t2, 1, "ca_")
                            st.rerun()
                        sf_winners.append(None)

                if all(sf_winners) and len(sf_winners) == 2:
                    if st.session_state.ca_final is None:
                        st.session_state.ca_final = (sf_winners[0], sf_winners[1])

                    st.markdown("### \U0001F3C6 FINAL")
                    t1, t2 = st.session_state.ca_final
                    res = st.session_state.ca_final_result
                    if res:
                        render_match_result(t1, t2, res)
                        champ_banner(res["winner"], "CAMPE\u00D3N DE AM\u00C9RICA")
                    else:
                        r = knockout_input("ca_final", t1, t2, PLAYERS.get(t1, []), PLAYERS.get(t2, []))
                        if r:
                            st.session_state.ca_final_result = r
                            champ = r["winner"]
                            st.session_state.ca_champion = champ
                            for s in r.get("scorers_h", []): update_scorer(s, t1, 1, "ca_")
                            for s in r.get("scorers_a", []): update_scorer(s, t2, 1, "ca_")
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
            champ_banner(st.session_state.ca_champion, "CAMPE\u00D3N DE AM\u00C9RICA")
            render_standings(st.session_state.ca_final_standings[:10], highlight=1)
        else:
            st.info("Copa Am\u00E9rica sin resultado a\u00FAn.")

# ══════════════════════════════════════════════
# CONMEBOL PLAYOFFS
# ══════════════════════════════════════════════
elif page == "\U0001F522 CONMEBOL \u00B7 Playoffs":
    conf_header("\U0001F522", "CONMEBOL \u00B7 PLAYOFFS MUNDIALISTAS", "#27AE60",
                "Puestos 2-7 \u2192 todos vs todos \u00B7 Top 3 \u2192 Mundial \u00B7 4to \u2192 Repechaje")

    if not st.session_state.ca_final_standings:
        st.warning("Completa la Copa Am\u00E9rica primero.")
    else:
        fs = st.session_state.ca_final_standings
        conmebol_in_ca = [e for e in fs if e["team"] in CONMEBOL_TEAMS]
        pool = [e["team"] for e in conmebol_in_ca[1:7]]

        st.markdown(f"**Equipos:** {' \u00B7 '.join(fl(t)+' '+t for t in pool)}")

        if not st.session_state.conmebol_playoff_teams:
            if st.button("\u25B6\uFE0F Iniciar eliminatoria CONMEBOL"):
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
                    r = match_input_form("cmp", t1, t2, PLAYERS.get(t1, []), PLAYERS.get(t2, []))
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

            st.markdown(f"**\u2705 Clasificados:** {' \u00B7 '.join(fl(t)+' '+t for t in qualified)}")
            if repechaje:
                st.markdown(f"**\U0001F504 Repechaje:** {fl(repechaje)} {repechaje}")

            if st.button("\U0001F4BE Confirmar clasificados CONMEBOL"):
                for t in qualified:
                    if t not in st.session_state.wc_qualified:
                        st.session_state.wc_qualified.append(t)
                st.session_state.conmebol_playoff_qualified = qualified
                st.session_state.conmebol_playoff_repechaje = repechaje
                st.success("\u2705 Confirmados.")

# ══════════════════════════════════════════════
# COPA AFRICA
# ══════════════════════════════════════════════
elif page == "\U0001F30D CAF \u00B7 Copa \u00C1frica":
    conf_header("\U0001F30D", "COPA \u00C1FRICA CAF", "#F39C12",
                "10 equipos \u00B7 2 grupos de 5 \u00B7 2 primeros \u2192 Semis")

    tab_setup, tab_groups, tab_ko, tab_result = st.tabs(["\u2699\uFE0F Config", "\U0001F4CA Grupos", "\U0001F3AF Eliminatorias", "\U0001F3C6 Resultado"])

    with tab_setup:
        selected = st.multiselect("Elige 10 equipos CAF", CAF_TEAMS,
                                  default=st.session_state.af_teams or CAF_TEAMS, max_selections=10)
        if len(selected) == 10:
            st.markdown("**Arma 2 grupos de 5:**")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Grupo A**")
                gA = st.multiselect("Grupo A", selected, default=st.session_state.af_groups.get("A", selected[:5]), max_selections=5, key="af_gA")
            with col2:
                st.markdown("**Grupo B**")
                gB = st.multiselect("Grupo B", selected, default=st.session_state.af_groups.get("B", selected[5:]), max_selections=5, key="af_gB")

            if st.button("\U0001F4BE Guardar grupos \u00C1frica"):
                if len(gA) != 5 or len(gB) != 5:
                    st.error("5 equipos por grupo.")
                elif len(set(gA + gB)) != 10:
                    st.error("Duplicados.")
                else:
                    st.session_state.af_teams = selected
                    st.session_state.af_groups = {"A": gA, "B": gB}
                    st.session_state.af_matches = {**generate_group_matches(gA), **generate_group_matches(gB)}
                    st.success("\u2705 Grupos guardados.")
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
                                r = match_input_form("af", t1, t2, PLAYERS.get(t1, []), PLAYERS.get(t2, []), key_suffix=gl)
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

            st.divider()
            sA = st.session_state.af_standings.get("A", [])
            sB = st.session_state.af_standings.get("B", [])
            if len(sA) >= 2 and len(sB) >= 2:
                sf1 = (sA[0]["team"], sB[1]["team"])
                sf2 = (sB[0]["team"], sA[1]["team"])
                st.markdown(f"**SF1:** {fl(sf1[0])} {sf1[0]} vs {fl(sf1[1])} {sf1[1]}")
                st.markdown(f"**SF2:** {fl(sf2[0])} {sf2[0]} vs {fl(sf2[1])} {sf2[1]}")
                if st.button("\u27A1\uFE0F Generar Semis"):
                    st.session_state.af_sf = [sf1, sf2]
                    st.session_state.af_sf_results = {}
                    st.success("\u2705 Semis generadas.")
                    st.rerun()

    with tab_ko:
        if not st.session_state.af_sf:
            st.info("Completa grupos primero.")
        else:
            st.markdown("### \u2694\uFE0F Semifinales")
            sf_winners = []
            for i, (t1, t2) in enumerate(st.session_state.af_sf):
                res = st.session_state.af_sf_results.get(i)
                if res:
                    render_match_result(t1, t2, res)
                    sf_winners.append(res["winner"])
                else:
                    r = knockout_input(f"af_sf_{i}", t1, t2, PLAYERS.get(t1, []), PLAYERS.get(t2, []))
                    if r:
                        st.session_state.af_sf_results[i] = r
                        for s in r.get("scorers_h", []): update_scorer(s, t1, 1, "af_")
                        for s in r.get("scorers_a", []): update_scorer(s, t2, 1, "af_")
                        st.rerun()
                    sf_winners.append(None)

            if all(sf_winners) and len(sf_winners) == 2:
                if st.session_state.af_final is None:
                    st.session_state.af_final = (sf_winners[0], sf_winners[1])
                st.markdown("### \U0001F3C6 FINAL")
                t1, t2 = st.session_state.af_final
                res = st.session_state.af_final_result
                if res:
                    render_match_result(t1, t2, res)
                    champ_banner(res["winner"], "CAMPE\u00D3N DE \u00C1FRICA")
                else:
                    r = knockout_input("af_final", t1, t2, PLAYERS.get(t1, []), PLAYERS.get(t2, []))
                    if r:
                        st.session_state.af_final_result = r
                        champ = r["winner"]
                        runner = t2 if champ == t1 else t1
                        st.session_state.af_champion = champ
                        for s in r.get("scorers_h", []): update_scorer(s, t1, 1, "af_")
                        for s in r.get("scorers_a", []): update_scorer(s, t2, 1, "af_")
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
            champ_banner(st.session_state.af_champion, "CAMPE\u00D3N DE \u00C1FRICA")
            render_standings(st.session_state.af_final_standings[:6], highlight=2)
        else:
            st.info("Sin resultado a\u00FAn.")

# ══════════════════════════════════════════════
# CAF PLAYOFFS
# ══════════════════════════════════════════════
elif page == "\U0001F522 CAF \u00B7 Playoffs":
    conf_header("\U0001F522", "CAF \u00B7 PLAYOFFS MUNDIALISTAS", "#F39C12",
                "Puestos 3-7 \u2192 todos vs todos \u00B7 Top 3 \u2192 Mundial")

    if not st.session_state.af_final_standings:
        st.warning("Completa la Copa \u00C1frica primero.")
    else:
        pool = [e["team"] for e in st.session_state.af_final_standings[2:7]]
        st.markdown(f"**Equipos:** {' \u00B7 '.join(fl(t)+' '+t for t in pool)}")

        if not st.session_state.caf_playoff_teams:
            if st.button("\u25B6\uFE0F Iniciar playoff CAF"):
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
                    r = match_input_form("cafp", t1, t2, PLAYERS.get(t1, []), PLAYERS.get(t2, []))
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
            st.markdown(f"**\u2705 Clasificados:** {' \u00B7 '.join(fl(t)+' '+t for t in qualified)}")

            if st.button("\U0001F4BE Confirmar clasificados CAF"):
                for t in qualified:
                    if t not in st.session_state.wc_qualified:
                        st.session_state.wc_qualified.append(t)
                st.session_state.caf_playoff_qualified = qualified
                st.success("\u2705 Confirmados.")

# ══════════════════════════════════════════════
# COPA ORO
# ══════════════════════════════════════════════
elif page == "\U0001F30E CONCACAF \u00B7 Copa Oro":
    conf_header("\U0001F30E", "COPA ORO CONCACAF", "#E74C3C",
                "6 equipos \u00B7 2 grupos de 3 \u00B7 A1vB2 y B1vA2 \u2192 Final")

    tab_setup, tab_groups, tab_ko, tab_result = st.tabs(["\u2699\uFE0F Config", "\U0001F4CA Grupos", "\U0001F3AF Eliminatorias", "\U0001F3C6 Resultado"])

    with tab_setup:
        selected = st.multiselect("Elige 6 equipos CONCACAF", CONCACAF_TEAMS,
                                  default=st.session_state.co_teams or CONCACAF_TEAMS, max_selections=6)
        if len(selected) == 6:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Grupo A**")
                gA = st.multiselect("Grupo A", selected, default=st.session_state.co_groups.get("A", selected[:3]), max_selections=3, key="co_gA")
            with col2:
                st.markdown("**Grupo B**")
                gB = st.multiselect("Grupo B", selected, default=st.session_state.co_groups.get("B", selected[3:]), max_selections=3, key="co_gB")

            if st.button("\U0001F4BE Guardar grupos Copa Oro"):
                if len(gA) != 3 or len(gB) != 3 or len(set(gA + gB)) != 6:
                    st.error("3 equipos por grupo sin duplicados.")
                else:
                    st.session_state.co_teams = selected
                    st.session_state.co_groups = {"A": gA, "B": gB}
                    st.session_state.co_matches = {**generate_group_matches(gA), **generate_group_matches(gB)}
                    st.success("\u2705 Guardados.")
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
                                r = match_input_form("co", t1, t2, PLAYERS.get(t1, []), PLAYERS.get(t2, []), key_suffix=gl)
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
                if st.button("\u27A1\uFE0F Generar Semis Copa Oro"):
                    st.session_state.co_sf = [sf1, sf2]
                    st.session_state.co_sf_results = {}
                    st.rerun()

    with tab_ko:
        if not st.session_state.co_sf:
            st.info("Completa grupos primero.")
        else:
            st.markdown("### \u2694\uFE0F Semifinales")
            sf_winners = []
            for i, (t1, t2) in enumerate(st.session_state.co_sf):
                res = st.session_state.co_sf_results.get(i)
                if res:
                    render_match_result(t1, t2, res)
                    sf_winners.append(res["winner"])
                else:
                    r = knockout_input(f"co_sf_{i}", t1, t2, PLAYERS.get(t1, []), PLAYERS.get(t2, []))
                    if r:
                        st.session_state.co_sf_results[i] = r
                        for s in r.get("scorers_h", []): update_scorer(s, t1, 1, "co_")
                        for s in r.get("scorers_a", []): update_scorer(s, t2, 1, "co_")
                        st.rerun()
                    sf_winners.append(None)

            if all(sf_winners) and len(sf_winners) == 2:
                if st.session_state.co_final is None:
                    st.session_state.co_final = (sf_winners[0], sf_winners[1])
                st.markdown("### \U0001F3C6 FINAL")
                t1, t2 = st.session_state.co_final
                res = st.session_state.co_final_result
                if res:
                    render_match_result(t1, t2, res)
                    champ_banner(res["winner"], "CAMPE\u00D3N COPA ORO")
                else:
                    r = knockout_input("co_final", t1, t2, PLAYERS.get(t1, []), PLAYERS.get(t2, []))
                    if r:
                        st.session_state.co_final_result = r
                        champ = r["winner"]
                        st.session_state.co_champion = champ
                        for s in r.get("scorers_h", []): update_scorer(s, t1, 1, "co_")
                        for s in r.get("scorers_a", []): update_scorer(s, t2, 1, "co_")
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
            champ_banner(st.session_state.co_champion, "CAMPE\u00D3N COPA ORO")
            render_standings(st.session_state.co_final_standings, highlight=1)
        else:
            st.info("Sin resultado a\u00FAn.")

# ══════════════════════════════════════════════
# CONCACAF PLAYOFFS
# ══════════════════════════════════════════════
elif page == "\U0001F522 CONCACAF \u00B7 Playoffs":
    conf_header("\U0001F522", "CONCACAF \u00B7 PLAYOFFS", "#E74C3C",
                "Puestos 2-5 \u2192 todos vs todos \u00B7 Top 2 \u2192 Mundial \u00B7 3ro \u2192 Repechaje")

    if not st.session_state.co_final_standings:
        st.warning("Completa la Copa Oro primero.")
    else:
        pool = [e["team"] for e in st.session_state.co_final_standings[1:5]]
        st.markdown(f"**Equipos:** {' \u00B7 '.join(fl(t)+' '+t for t in pool)}")

        if not st.session_state.concacaf_playoff_teams:
            if st.button("\u25B6\uFE0F Iniciar playoff CONCACAF"):
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
                    r = match_input_form("ccp", t1, t2, PLAYERS.get(t1, []), PLAYERS.get(t2, []))
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
            st.markdown(f"**\u2705 Clasificados:** {' \u00B7 '.join(fl(t)+' '+t for t in qualified)}")
            if repechaje:
                st.markdown(f"**\U0001F504 Repechaje:** {fl(repechaje)} {repechaje}")

            if st.button("\U0001F4BE Confirmar CONCACAF"):
                for t in qualified:
                    if t not in st.session_state.wc_qualified:
                        st.session_state.wc_qualified.append(t)
                st.session_state.concacaf_playoff_qualified = qualified
                st.session_state.concacaf_playoff_repechaje = repechaje
                st.success("\u2705 Confirmados.")

# ══════════════════════════════════════════════
# COPA ASIA
# ══════════════════════════════════════════════
elif page == "\U0001F30F AFC \u00B7 Copa Asia":
    conf_header("\U0001F30F", "COPA ASIA AFC", "#9B59B6",
                "6 equipos (Australia incluida) \u00B7 2 grupos de 3 \u00B7 A1vB2 y B1vA2 \u2192 Final")

    tab_setup, tab_groups, tab_ko, tab_result = st.tabs(["\u2699\uFE0F Config", "\U0001F4CA Grupos", "\U0001F3AF Eliminatorias", "\U0001F3C6 Resultado"])

    with tab_setup:
        selected = st.multiselect("Elige 6 equipos AFC", AFC_TEAMS,
                                  default=st.session_state.as_teams or AFC_TEAMS, max_selections=6)
        if "Australia" not in selected:
            st.warning("\u26A0\uFE0F Australia debe estar incluida (juega en AFC, no OFC).")
        if len(selected) == 6:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Grupo A**")
                gA = st.multiselect("Grupo A", selected, default=st.session_state.as_groups.get("A", selected[:3]), max_selections=3, key="as_gA")
            with col2:
                st.markdown("**Grupo B**")
                gB = st.multiselect("Grupo B", selected, default=st.session_state.as_groups.get("B", selected[3:]), max_selections=3, key="as_gB")

            if st.button("\U0001F4BE Guardar grupos Copa Asia"):
                if len(gA) != 3 or len(gB) != 3 or len(set(gA + gB)) != 6:
                    st.error("3 por grupo sin duplicados.")
                else:
                    st.session_state.as_teams = selected
                    st.session_state.as_groups = {"A": gA, "B": gB}
                    st.session_state.as_matches = {**generate_group_matches(gA), **generate_group_matches(gB)}
                    st.success("\u2705 Guardados.")
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
                                r = match_input_form("as", t1, t2, PLAYERS.get(t1, []), PLAYERS.get(t2, []), key_suffix=gl)
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
                if st.button("\u27A1\uFE0F Generar Semis Copa Asia"):
                    st.session_state.as_sf = [sf1, sf2]
                    st.session_state.as_sf_results = {}
                    st.rerun()

    with tab_ko:
        if not st.session_state.as_sf:
            st.info("Completa grupos primero.")
        else:
            st.markdown("### \u2694\uFE0F Semifinales")
            sf_winners = []
            for i, (t1, t2) in enumerate(st.session_state.as_sf):
                res = st.session_state.as_sf_results.get(i)
                if res:
                    render_match_result(t1, t2, res)
                    sf_winners.append(res["winner"])
                else:
                    r = knockout_input(f"as_sf_{i}", t1, t2, PLAYERS.get(t1, []), PLAYERS.get(t2, []))
                    if r:
                        st.session_state.as_sf_results[i] = r
                        for s in r.get("scorers_h", []): update_scorer(s, t1, 1, "as_")
                        for s in r.get("scorers_a", []): update_scorer(s, t2, 1, "as_")
                        st.rerun()
                    sf_winners.append(None)

            if all(sf_winners) and len(sf_winners) == 2:
                if st.session_state.as_final is None:
                    st.session_state.as_final = (sf_winners[0], sf_winners[1])
                st.markdown("### \U0001F3C6 FINAL")
                t1, t2 = st.session_state.as_final
                res = st.session_state.as_final_result
                if res:
                    render_match_result(t1, t2, res)
                    champ_banner(res["winner"], "CAMPE\u00D3N DE ASIA")
                else:
                    r = knockout_input("as_final", t1, t2, PLAYERS.get(t1, []), PLAYERS.get(t2, []))
                    if r:
                        st.session_state.as_final_result = r
                        champ = r["winner"]
                        st.session_state.as_champion = champ
                        for s in r.get("scorers_h", []): update_scorer(s, t1, 1, "as_")
                        for s in r.get("scorers_a", []): update_scorer(s, t2, 1, "as_")
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
            champ_banner(st.session_state.as_champion, "CAMPE\u00D3N DE ASIA")
            render_standings(st.session_state.as_final_standings, highlight=1)
        else:
            st.info("Sin resultado a\u00FAn.")

# ══════════════════════════════════════════════
# AFC PLAYOFFS
# ══════════════════════════════════════════════
elif page == "\U0001F522 AFC \u00B7 Playoffs":
    conf_header("\U0001F522", "AFC \u00B7 PLAYOFFS", "#9B59B6",
                "Puestos 2-5 \u2192 todos vs todos \u00B7 Top 3 \u2192 Mundial \u00B7 4to \u2192 Repechaje")

    if not st.session_state.as_final_standings:
        st.warning("Completa la Copa Asia primero.")
    else:
        pool = [e["team"] for e in st.session_state.as_final_standings[1:5]]
        st.markdown(f"**Equipos:** {' \u00B7 '.join(fl(t)+' '+t for t in pool)}")

        if not st.session_state.afc_playoff_teams:
            if st.button("\u25B6\uFE0F Iniciar playoff AFC"):
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
                    r = match_input_form("afcp", t1, t2, PLAYERS.get(t1, []), PLAYERS.get(t2, []))
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
            st.markdown(f"**\u2705 Clasificados:** {' \u00B7 '.join(fl(t)+' '+t for t in qualified)}")
            if repechaje:
                st.markdown(f"**\U0001F504 Repechaje:** {fl(repechaje)} {repechaje}")

            if st.button("\U0001F4BE Confirmar AFC"):
                for t in qualified:
                    if t not in st.session_state.wc_qualified:
                        st.session_state.wc_qualified.append(t)
                st.session_state.afc_playoff_qualified = qualified
                st.session_state.afc_playoff_repechaje = repechaje
                st.success("\u2705 Confirmados.")

# ══════════════════════════════════════════════
# REPECHAJE INTERNACIONAL
# ══════════════════════════════════════════════
elif page == "\U0001F504 Repechaje Internacional":
    conf_header("\U0001F504", "REPECHAJE INTERNACIONAL", "#FF5722",
                "CONCACAF 3ro vs AFC 4to \u00B7 CONMEBOL 4to vs Nueva Zelanda")

    cc3 = st.session_state.concacaf_playoff_repechaje
    afc4 = st.session_state.afc_playoff_repechaje
    cm4 = st.session_state.conmebol_playoff_repechaje

    c1, c2, c3 = st.columns(3)
    c1.markdown(f"<div class='card card-acc'><b>CONCACAF 3ro</b><br>{'✅ '+fl(cc3)+' '+cc3 if cc3 else '⏳ Pendiente'}</div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='card card-acc'><b>AFC 4to</b><br>{'✅ '+fl(afc4)+' '+afc4 if afc4 else '⏳ Pendiente'}</div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='card card-acc'><b>CONMEBOL 4to</b><br>{'✅ '+fl(cm4)+' '+cm4 if cm4 else '⏳ Pendiente'}</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### \u270F\uFE0F Configuraci\u00F3n Manual")
    all_pool = ALL_TEAMS + ["New Zealand"]
    c1, c2, c3 = st.columns(3)
    with c1: m1t1 = st.selectbox("CONCACAF 3ro", all_pool, index=all_pool.index(cc3) if cc3 in all_pool else 0)
    with c2: m1t2 = st.selectbox("AFC 4to", all_pool, index=all_pool.index(afc4) if afc4 in all_pool else 0)
    with c3: m2t1 = st.selectbox("CONMEBOL 4to", all_pool, index=all_pool.index(cm4) if cm4 in all_pool else 0)

    st.markdown("---")
    st.markdown("### \u26BD Partido 1: CONCACAF 3ro vs AFC 4to")
    res1 = st.session_state.int_playoff_match1
    if res1:
        render_match_result(m1t1, m1t2, res1)
        st.markdown(f"**Clasificado: {fl(res1['winner'])} {res1['winner']}**")
    else:
        r = knockout_input("int1", m1t1, m1t2, PLAYERS.get(m1t1, []), PLAYERS.get(m1t2, []))
        if r:
            st.session_state.int_playoff_match1 = r
            st.rerun()

    st.markdown("### \u26BD Partido 2: CONMEBOL 4to vs Nueva Zelanda \U0001F1F3\U0001F1FF")
    res2 = st.session_state.int_playoff_match2
    if res2:
        render_match_result(m2t1, "New Zealand", res2)
        st.markdown(f"**Clasificado: {fl(res2['winner'])} {res2['winner']}**")
    else:
        r = knockout_input("int2", m2t1, "New Zealand", PLAYERS.get(m2t1, []), PLAYERS.get("New Zealand", []))
        if r:
            st.session_state.int_playoff_match2 = r
            st.rerun()

    if res1 and res2:
        st.divider()
        qualified = [res1["winner"], res2["winner"]]
        st.markdown("#### \u2705 Clasificados al Mundial via Repechaje")
        for t in qualified:
            st.markdown(f"\u2705 {fl(t)} **{t}**")
        if st.button("\U0001F4BE Confirmar repechaje"):
            for t in qualified:
                if t not in st.session_state.wc_qualified:
                    st.session_state.wc_qualified.append(t)
            st.session_state.int_playoff_qualified = qualified
            st.success("\u2705 Clasificados confirmados.")

# ══════════════════════════════════════════════
# MUNDIAL
# ══════════════════════════════════════════════
elif page == "\U0001F3C6 Mundial":
    conf_header("\U0001F3C6", "COPA DEL MUNDO", "#FFD700", "32 equipos \u00B7 8 grupos \u00B7 Modelo FIFA oficial")

    tab_config, tab_groups, tab_ko, tab_result = st.tabs(["\u2699\uFE0F Config", "\U0001F4CA Grupos", "\U0001F3AF Eliminatorias", "\U0001F3C6 Resultado"])

    with tab_config:
        st.markdown(f"**Clasificados actuales: {len(st.session_state.wc_qualified)}/32**")
        for t in st.session_state.wc_qualified:
            st.markdown(f"- {fl(t)} {t}")

        st.markdown("---")
        host = st.selectbox("\U0001F3DF\uFE0F Pa\u00EDs Anfitri\u00F3n", ALL_TEAMS + ["New Zealand"],
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
        group_labels = ["A", "B", "C", "D", "E", "F", "G", "H"]
        cols1 = st.columns(4)
        cols2 = st.columns(4)
        for i, gl in enumerate(group_labels):
            col = cols1[i] if i < 4 else cols2[i-4]
            with col:
                st.markdown(f"**Grupo {gl}**")
                default_g = st.session_state.wc_groups.get(gl, pool32[i*4:(i+1)*4])
                chosen = st.multiselect(f"Grupo {gl}", pool32, default=default_g, max_selections=4, key=f"wc_grp_{gl}")
                new_groups[gl] = chosen

        if st.button("\U0001F4BE Guardar grupos del Mundial"):
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
                st.success("\u2705 Grupos del Mundial guardados.")
                st.rerun()

    with tab_groups:
        if not st.session_state.wc_groups:
            st.info("Configura los grupos primero.")
        else:
            for gl in ["A", "B", "C", "D", "E", "F", "G", "H"]:
                teams = st.session_state.wc_groups.get(gl, [])
                if not teams:
                    continue
                with st.expander(f"Grupo {gl}", expanded=False):
                    col_m, col_t = st.columns([3, 2])
                    with col_m:
                        for t1, t2 in combinations(teams, 2):
                            key = (t1, t2) if (t1, t2) in st.session_state.wc_matches else (t2, t1)
                            res = st.session_state.wc_matches.get(key)
                            render_match_result(t1, t2, res)
                            if res is None:
                                r = match_input_form("wc", t1, t2, PLAYERS.get(t1, []), PLAYERS.get(t2, []), key_suffix=gl)
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
            for gl in ["A", "B", "C", "D", "E", "F", "G", "H"]:
                s = st.session_state.wc_standings.get(gl, [])
                if len(s) >= 2:
                    by_slot[f"{gl}1"] = s[0]["team"]
                    by_slot[f"{gl}2"] = s[1]["team"]

            if len(by_slot) == 16:
                st.markdown("#### Bracket R16 (Modelo Mundial FIFA)")
                wc_r16 = [
                    (by_slot.get("A1", "?"), by_slot.get("B2", "?")),
                    (by_slot.get("C1", "?"), by_slot.get("D2", "?")),
                    (by_slot.get("E1", "?"), by_slot.get("F2", "?")),
                    (by_slot.get("G1", "?"), by_slot.get("H2", "?")),
                    (by_slot.get("B1", "?"), by_slot.get("A2", "?")),
                    (by_slot.get("D1", "?"), by_slot.get("C2", "?")),
                    (by_slot.get("F1", "?"), by_slot.get("E2", "?")),
                    (by_slot.get("H1", "?"), by_slot.get("G2", "?")),
                ]
                cols = st.columns(4)
                for i, (t1, t2) in enumerate(wc_r16):
                    with cols[i % 4]:
                        st.markdown(
                            f"<div class='card' style='text-align:center;padding:8px;font-size:12px;'>"
                            f"{fl(t1)} {t1}<br><span style='color:var(--muted)'>vs</span><br>"
                            f"{fl(t2)} {t2}</div>",
                            unsafe_allow_html=True,
                        )

                if st.button("\u27A1\uFE0F Generar R16 del Mundial"):
                    st.session_state.wc_r16 = wc_r16
                    st.session_state.wc_r16_results = {}
                    st.success("\u2705 R16 generado.")
                    st.rerun()

    with tab_ko:
        if not st.session_state.wc_r16:
            st.info("Completa los grupos y genera el R16 primero.")
        else:
            st.markdown("### \u2694\uFE0F Octavos de Final")
            r16w = []
            for i, (t1, t2) in enumerate(st.session_state.wc_r16):
                res = st.session_state.wc_r16_results.get(i)
                if res:
                    render_match_result(t1, t2, res); r16w.append(res["winner"])
                else:
                    r = knockout_input(f"wc_r16_{i}", t1, t2, PLAYERS.get(t1, []), PLAYERS.get(t2, []))
                    if r:
                        st.session_state.wc_r16_results[i] = r
                        for s in r.get("scorers_h", []): update_scorer(s, t1, 1, "wc_")
                        for s in r.get("scorers_a", []): update_scorer(s, t2, 1, "wc_")
                        st.rerun()
                    r16w.append(None)

            if all(r16w) and len(r16w) == 8:
                if not st.session_state.wc_qf:
                    st.session_state.wc_qf = [
                        (r16w[0], r16w[4]), (r16w[2], r16w[6]),
                        (r16w[1], r16w[5]), (r16w[3], r16w[7]),
                    ]

                st.markdown("### \u2694\uFE0F Cuartos de Final")
                qfw = []
                for i, (t1, t2) in enumerate(st.session_state.wc_qf):
                    res = st.session_state.wc_qf_results.get(i)
                    if res:
                        render_match_result(t1, t2, res); qfw.append(res["winner"])
                    else:
                        r = knockout_input(f"wc_qf_{i}", t1, t2, PLAYERS.get(t1, []), PLAYERS.get(t2, []))
                        if r:
                            st.session_state.wc_qf_results[i] = r
                            for s in r.get("scorers_h", []): update_scorer(s, t1, 1, "wc_")
                            for s in r.get("scorers_a", []): update_scorer(s, t2, 1, "wc_")
                            st.rerun()
                        qfw.append(None)

                if all(qfw) and len(qfw) == 4:
                    if not st.session_state.wc_sf:
                        st.session_state.wc_sf = [(qfw[0], qfw[1]), (qfw[2], qfw[3])]

                    st.markdown("### \u2694\uFE0F Semifinales")
                    sfw = []; sfl = []
                    for i, (t1, t2) in enumerate(st.session_state.wc_sf):
                        res = st.session_state.wc_sf_results.get(i)
                        if res:
                            render_match_result(t1, t2, res)
                            sfw.append(res["winner"]); sfl.append(t2 if res["winner"] == t1 else t1)
                        else:
                            r = knockout_input(f"wc_sf_{i}", t1, t2, PLAYERS.get(t1, []), PLAYERS.get(t2, []))
                            if r:
                                st.session_state.wc_sf_results[i] = r
                                for s in r.get("scorers_h", []): update_scorer(s, t1, 1, "wc_")
                                for s in r.get("scorers_a", []): update_scorer(s, t2, 1, "wc_")
                                st.rerun()
                            sfw.append(None)

                    if all(sfw) and len(sfw) == 2:
                        st.markdown("### \U0001F949 Tercer Puesto")
                        if len(sfl) == 2:
                            t3a, t3b = sfl[0], sfl[1]
                            res3 = st.session_state.wc_third_result
                            if res3:
                                render_match_result(t3a, t3b, res3)
                                st.markdown(f"\U0001F949 **{fl(res3['winner'])} {res3['winner']}**")
                            else:
                                r = knockout_input("wc_3rd", t3a, t3b, PLAYERS.get(t3a, []), PLAYERS.get(t3b, []))
                                if r:
                                    st.session_state.wc_third = (t3a, t3b)
                                    st.session_state.wc_third_result = r
                                    st.rerun()

                        st.markdown("### \U0001F3C6 FINAL MUNDIAL")
                        if st.session_state.wc_final is None:
                            st.session_state.wc_final = (sfw[0], sfw[1])
                        t1, t2 = st.session_state.wc_final
                        resf = st.session_state.wc_final_result
                        if resf:
                            render_match_result(t1, t2, resf)
                            champ_banner(resf["winner"], "CAMPE\u00D3N DEL MUNDO \U0001F30D")
                        else:
                            r = knockout_input("wc_final", t1, t2, PLAYERS.get(t1, []), PLAYERS.get(t2, []))
                            if r:
                                st.session_state.wc_final_result = r
                                champ = r["winner"]
                                st.session_state.wc_champion = champ
                                for s in r.get("scorers_h", []): update_scorer(s, t1, 1, "wc_")
                                for s in r.get("scorers_a", []): update_scorer(s, t2, 1, "wc_")
                                runner = t2 if champ == t1 else t1
                                fs_wc = [{"pos": 1, "team": champ}, {"pos": 2, "team": runner}]
                                update_ranking_from_standings(fs_wc, 200, 10)
                                st.rerun()

    with tab_result:
        if st.session_state.wc_champion:
            champ_banner(st.session_state.wc_champion, "\U0001F30D CAMPE\u00D3N DEL MUNDO")
            if st.session_state.wc_final_result:
                t1, t2 = st.session_state.wc_final
                r = st.session_state.wc_final_result
                render_match_result(t1, t2, r)
        else:
            st.info("El Mundial a\u00FAn no tiene campe\u00F3n.")

# ══════════════════════════════════════════════
# RANKING FIFA
# ══════════════════════════════════════════════
elif page == "\U0001F4CA Ranking FIFA":
    conf_header("\U0001F4CA", "RANKING FIFA", "#00E5A0",
                "Se actualiza con cada torneo \u00B7 Persiste entre temporadas")

    ranking = st.session_state.fifa_ranking
    sorted_r = sorted(ranking.items(), key=lambda x: x[1], reverse=True)

    c1, c2, c3 = st.columns(3)
    for col, (team, pts), medal in zip([c1, c2, c3], sorted_r[:3], ["\U0001F947", "\U0001F948", "\U0001F949"]):
        with col:
            st.markdown(
                f"<div class='card card-gold' style='text-align:center;padding:22px;'>"
                f"<div style='font-size:36px;'>{medal}</div>"
                f"<div style='font-size:40px;margin:4px 0;'>{fl(team)}</div>"
                f"<div style='font-family:Bebas Neue;font-size:22px;'>{team}</div>"
                f"<div style='color:var(--g);font-size:24px;font-weight:700;margin-top:6px;'>{pts}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    conf_teams = {
        "UEFA": UEFA_TEAMS, "CONMEBOL": CONMEBOL_TEAMS,
        "CAF": CAF_TEAMS, "CONCACAF": CONCACAF_TEAMS, "AFC": AFC_TEAMS,
    }
    filt = st.selectbox("Filtrar por confederaci\u00F3n", ["Todas", "UEFA", "CONMEBOL", "CAF", "CONCACAF", "AFC"])

    rows = []
    for pos, (t, pts) in enumerate(sorted_r, 1):
        if filt != "Todas" and t not in conf_teams.get(filt, []):
            continue
        conf = "\u2014"
        for c, tl in conf_teams.items():
            if t in tl:
                conf = c; break
        rows.append({"Pos": pos, "Equipo": f"{fl(t)} {t}", "Conf": conf, "Puntos": pts})

    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

    if st.button("\U0001F504 Resetear ranking inicial"):
        st.session_state.fifa_ranking = dict(INITIAL_FIFA_RANKING)
        st.success("\u2705 Reseteado.")
        st.rerun()

# ══════════════════════════════════════════════
# GOLEADORES
# ══════════════════════════════════════════════
elif page == "\u26BD Goleadores":
    conf_header("\u26BD", "TABLA DE GOLEADORES", "#FF5722",
                "Registrados durante todos los torneos")

    scorers = st.session_state.top_scorers
    if not scorers:
        st.info("No hay goles registrados a\u00FAn.")
    else:
        TOUR_PREFIX = {
            "euro_": "\U0001F30D Eurocopa",
            "ca_":   "\U0001F30E Copa Am\u00E9rica",
            "af_":   "\U0001F30D Copa \u00C1frica",
            "co_":   "\U0001F30E Copa Oro",
            "as_":   "\U0001F30F Copa Asia",
            "wc_":   "\U0001F3C6 Mundial",
        }

        filt_tour = st.selectbox("Torneo", ["Todos"] + list(TOUR_PREFIX.values()))

        rows = []
        for key, goals in sorted(scorers.items(), key=lambda x: x[1], reverse=True):
            parts = key.split("|")
            if len(parts) != 2:
                continue
            raw_key, team = parts[0], parts[1]
            tour = "\u2014"; player = raw_key
            for pref, name in TOUR_PREFIX.items():
                if raw_key.startswith(pref):
                    tour = name; player = raw_key[len(pref):]
                    break
            if filt_tour != "Todos" and tour != filt_tour:
                continue
            rows.append({"Goles": goals, "Jugador": player, "Selecci\u00F3n": f"{fl(team)} {team}", "Torneo": tour})

        if rows:
            df = pd.DataFrame(rows)
            df.insert(0, "Pos", range(1, len(df) + 1))
            st.dataframe(df, hide_index=True, use_container_width=True)

# ══════════════════════════════════════════════
# PLANTILLAS  — DISEÑO MEJORADO
# ══════════════════════════════════════════════
elif page == "\U0001F465 Plantillas":
    conf_header("\U0001F465", "PLANTILLAS", "#00E5A0",
                "Jugadores por selecci\u00F3n con link a SoFifa")

    conf_opts = {
        "UEFA \U0001F30D":       UEFA_TEAMS,
        "CONMEBOL \U0001F30E":   CONMEBOL_TEAMS,
        "CAF \U0001F30D":        CAF_TEAMS,
        "CONCACAF \U0001F30E":   CONCACAF_TEAMS,
        "AFC \U0001F30F":        AFC_TEAMS,
        "Repechaje \U0001F504":  ["New Zealand"],
    }

    c1, c2 = st.columns([1, 2])
    with c1:
        conf_sel = st.selectbox("Confederaci\u00F3n", list(conf_opts.keys()))
    with c2:
        team_sel = st.selectbox("Selecci\u00F3n", conf_opts[conf_sel])

    # ── Squad header ──
    players = PLAYERS.get(team_sel, [])
    total = len(players)
    pos_counts = {}
    for p in players:
        pos_counts[p["pos"]] = pos_counts.get(p["pos"], 0) + 1

    ranking_pts = st.session_state.fifa_ranking.get(team_sel, "\u2014")

    _ps = ""
    for _pos in ["GK", "DF", "MF", "FW"]:
        _c = POS_COLOR.get(_pos, "#aaa")
        _n = pos_counts.get(_pos, 0)
        _ps += f"<div class='squad-stat'><div class='squad-stat-val' style='color:{_c};'>{_n}</div><div class='squad-stat-lbl'>{_pos}</div></div>"
    st.markdown(
        f"<div class='squad-header'>"
        f"<div class='squad-flag'>{fl(team_sel)}</div>"
        f"<div class='squad-info'>"
        f"<div class='squad-name'>{team_sel}</div>"
        f"<div class='squad-sub'>FIFA RANKING &mdash; {ranking_pts} PTS</div>"
        f"<div class='squad-stats'>"
        f"<div class='squad-stat'><div class='squad-stat-val'>{total}</div><div class='squad-stat-lbl'>Jugadores</div></div>"
        f"{_ps}"
        f"</div></div></div>",
        unsafe_allow_html=True,
    )

    if not players:
        st.info("Sin datos de jugadores para esta selecci\u00F3n.")
    else:
        # Position filter
        pos_filt = st.radio(
            "Filtrar por posici\u00F3n",
            ["Todas", "GK", "DF", "MF", "FW"],
            horizontal=True,
        )
        filtered = [p for p in players if pos_filt == "Todas" or p["pos"] == pos_filt]

        # Position icons
        POS_ICON = {"GK": "\U0001F9E4", "DF": "\U0001F6E1\uFE0F", "MF": "\u26A1", "FW": "\U0001F525"}
        POS_LABEL = {"GK": "PORTEROS", "DF": "DEFENSAS", "MF": "CENTROCAMPISTAS", "FW": "DELANTEROS"}

        if pos_filt == "Todas":
            # Group by position in order GK -> DF -> MF -> FW
            pos_order = ["GK", "DF", "MF", "FW"]
            sections_html = ""
            num = 1
            for grp_pos in pos_order:
                grp = [p for p in players if p["position"] == grp_pos]
                if not grp:
                    continue
                gc = POS_COLOR.get(grp_pos, "#aaa")
                icon = POS_ICON.get(grp_pos, "")
                label = POS_LABEL.get(grp_pos, grp_pos)
                sections_html += f"<div class='pos-section-title' style='color:{gc};'>{icon} {label} <span style='font-size:13px;font-family:sans-serif;opacity:.5;'>({len(grp)})</span></div>"
                sections_html += "<div class='player-grid'>"
                for p in grp:
                    name = p["name"]
                    pos  = p["position"]
                    sofifa_url = f"https://sofifa.com/players?keyword={name.replace(' ', '+')}"
                    sections_html += (
                        f"<div class='player-card pos-{pos}-card'>"
                        f"<span class='pnum'>{num}</span>"
                        f"<div class='pos-badge pos-{pos}'>{pos}</div>"
                        f"<div class='pname'>{name}</div>"
                        f"<div style='margin-top:8px;'>"
                        f"<a href='{sofifa_url}' target='_blank'>\U0001F517 SoFifa</a>"
                        f"</div></div>"
                    )
                    num += 1
                sections_html += "</div>"
            st.markdown(sections_html, unsafe_allow_html=True)
        else:
            cards_html = "<div class='player-grid'>"
            num = 1
            for p in filtered:
                name = p["name"]
                pos  = p["position"]
                sofifa_url = f"https://sofifa.com/players?keyword={name.replace(' ', '+')}"
                cards_html += (
                    f"<div class='player-card pos-{pos}-card'>"
                    f"<span class='pnum'>{num}</span>"
                    f"<div class='pos-badge pos-{pos}'>{pos}</div>"
                    f"<div class='pname'>{name}</div>"
                    f"<div style='margin-top:8px;'>"
                    f"<a href='{sofifa_url}' target='_blank'>\U0001F517 SoFifa</a>"
                    f"</div></div>"
                )
                num += 1
            cards_html += "</div>"
            st.markdown(cards_html, unsafe_allow_html=True)

        # Summary bar at bottom
        st.markdown("<br>", unsafe_allow_html=True)
        bar_html = "<div style='display:flex;gap:8px;flex-wrap:wrap;margin-top:4px;'>"
        for pos_key in ["GK", "DF", "MF", "FW"]:
            count = pos_counts.get(pos_key, 0)
            color = POS_COLOR.get(pos_key, "#666")
            icon  = POS_ICON.get(pos_key, "")
            bar_html += (
                f"<div style='background:rgba(0,0,0,.3);border:1px solid {color};"
                f"border-radius:10px;padding:10px 18px;text-align:center;min-width:70px;'>"
                f"<div style='font-size:18px;line-height:1;margin-bottom:4px;'>{icon}</div>"
                f"<div style='color:{color};font-family:Bebas Neue,cursive;font-size:24px;line-height:1;'>{count}</div>"
                f"<div style='color:var(--muted);font-size:10px;letter-spacing:2px;margin-top:2px;'>{pos_key}</div>"
                f"</div>"
            )
        bar_html += f"<div style='background:rgba(0,229,160,.05);border:1px solid var(--g);border-radius:10px;padding:10px 18px;text-align:center;min-width:70px;'><div style='font-size:18px;line-height:1;margin-bottom:4px;'>\U0001F465</div><div style='color:var(--g);font-family:Bebas Neue,cursive;font-size:24px;line-height:1;'>{total}</div><div style='color:var(--muted);font-size:10px;letter-spacing:2px;margin-top:2px;'>TOTAL</div></div>"
        bar_html += "</div>"
        st.markdown(bar_html, unsafe_allow_html=True)
