"""
app.py - MMJ World Cup Simulator · Entrada manual de resultados
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

st.set_page_config(page_title="MMJ World Cup", page_icon="⚽", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow:wght@400;600;700&family=Barlow+Condensed:wght@400;600;700&display=swap');
:root{--g:#00E5A0;--g2:#00B87A;--acc:#FF5722;--dark:#080D14;--card:#0F1623;--card2:#16202E;--border:rgba(0,229,160,.15);--txt:#DDE4EF;--muted:#6B7A99;}
*{box-sizing:border-box;}
html,body,[class*="css"]{font-family:'Barlow',sans-serif;background:var(--dark)!important;color:var(--txt)!important;}
.stApp{background:var(--dark)!important;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0A1020 0%,#0F1825 100%)!important;border-right:1px solid var(--border);}
[data-testid="stSidebar"] *{color:var(--txt)!important;}
.stButton>button{background:linear-gradient(135deg,var(--g),var(--g2))!important;color:#080D14!important;font-family:'Bebas Neue',cursive!important;font-size:15px!important;letter-spacing:2px!important;border:none!important;border-radius:4px!important;padding:7px 20px!important;transition:all .2s!important;width:100%!important;}
.stButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 6px 20px rgba(0,229,160,.35)!important;}
h1,h2,h3,h4{font-family:'Bebas Neue',cursive!important;letter-spacing:3px!important;color:var(--txt)!important;}
.card{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:16px;margin:6px 0;}
.card-g{border-left:4px solid var(--g)!important;}
.card-acc{border-left:4px solid var(--acc)!important;}
.card-gold{border-left:4px solid #FFD700!important;}
.hero{font-family:'Bebas Neue',cursive;font-size:68px;letter-spacing:8px;background:linear-gradient(135deg,#00E5A0,#FFD700);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;text-align:center;line-height:1;}
.sub{font-family:'Barlow Condensed',sans-serif;font-size:14px;letter-spacing:5px;color:var(--muted);text-align:center;text-transform:uppercase;margin-bottom:24px;}
.badge{display:inline-block;padding:2px 10px;border-radius:12px;font-size:11px;font-weight:700;letter-spacing:1px;}
.badge-g{background:rgba(0,229,160,.15);color:var(--g);border:1px solid var(--g);}
.badge-acc{background:rgba(255,87,34,.15);color:var(--acc);border:1px solid var(--acc);}
.badge-gold{background:rgba(255,215,0,.15);color:#FFD700;border:1px solid #FFD700;}
.match-row{background:var(--card2);border:1px solid var(--border);border-radius:6px;padding:10px 14px;margin:4px 0;display:flex;align-items:center;gap:8px;}
thead tr th{background:rgba(0,229,160,.08)!important;color:var(--g)!important;font-family:'Bebas Neue',cursive!important;letter-spacing:1.5px!important;}
.stTabs [data-baseweb="tab"]{font-family:'Bebas Neue',cursive!important;letter-spacing:2px!important;font-size:15px!important;}
.stSelectbox>label,.stMultiSelect>label,.stNumberInput>label{font-family:'Barlow Condensed',sans-serif!important;font-size:13px!important;letter-spacing:2px!important;color:var(--muted)!important;text-transform:uppercase!important;}
hr{border-color:var(--border)!important;}
[data-testid="metric-container"]{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:14px;}
</style>
""", unsafe_allow_html=True)

init_state()

# ─────────────────────────────────────────────
# HELPERS GLOBALES
# ─────────────────────────────────────────────

def fl(team): return FLAG_MAP.get(team, "🏳️")

POS_COLOR = {"GK":"#F0A500","DF":"#2196F3","MF":"#4CAF50","FW":"#F44336"}

def standings_df(standings, highlight=0, repechaje_pos=None):
    rows = []
    for s in standings:
        pos = s["pos"]; team = s["team"]
        if pos <= highlight:
            st_txt = "✅ Clasifica"
        elif repechaje_pos and pos == repechaje_pos:
            st_txt = "🔄 Repechaje"
        else:
            st_txt = "❌"
        last = "".join(
            f"<span style='color:{'#00E5A0' if r=='W' else '#F44336' if r=='L' else '#888'};font-size:11px;margin:0 1px;'>{r}</span>"
            for r in s.get("results",[])[-5:]
        )
        rows.append({"Pos":pos,"Equipo":f"{fl(team)} {team}",
                     "Pts":s["pts"],"PJ":s["played"],"G":s["w"],"E":s["d"],"P":s["l"],
                     "GF":s["gf"],"GC":s["ga"],"GD":s["gd"],"Estado":st_txt})
    return pd.DataFrame(rows)


def render_standings(standings, title="", highlight=0, repechaje_pos=None):
    if title: st.markdown(f"#### {title}")
    if not standings:
        st.info("Sin datos aún.")
        return
    df = standings_df(standings, highlight, repechaje_pos)
    st.dataframe(df, hide_index=True, use_container_width=True)


def match_input_form(prefix, t1, t2, players_t1, players_t2, key_suffix=""):
    """
    Formulario para ingresar resultado de un partido.
    Retorna (hg, ag, scorers_h, scorers_a) o None si no se ingresó.
    """
    key_base = f"{prefix}_{t1}_{t2}_{key_suffix}"
    with st.expander(f"{fl(t1)} {t1}  vs  {fl(t2)} {t2}", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            hg = st.number_input(f"Goles {t1}", min_value=0, max_value=20, step=1, key=f"{key_base}_hg")
        with col2:
            ag = st.number_input(f"Goles {t2}", min_value=0, max_value=20, step=1, key=f"{key_base}_ag")

        # Goleadores
        scorers_h = []
        scorers_a = []
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
    if res is None:
        st.markdown(f"<div class='match-row'>{fl(t1)} {t1} <span style='color:var(--muted)'>vs</span> {fl(t2)} {t2} <span style='color:var(--muted);font-size:12px;margin-left:auto;'>⏳ Pendiente</span></div>", unsafe_allow_html=True)
    else:
        hg=res.get("hg",0); ag=res.get("ag",0)
        hcolor="#00E5A0" if hg>ag else "#F44336" if hg<ag else "#888"
        acolor="#00E5A0" if ag>hg else "#F44336" if ag<hg else "#888"
        sh=" ".join(f"<span style='font-size:10px;color:#aaa'>⚽{s}</span>" for s in res.get("scorers_h",[]))
        sa=" ".join(f"<span style='font-size:10px;color:#aaa'>⚽{s}</span>" for s in res.get("scorers_a",[]))
        st.markdown(
            f"<div class='match-row'>"
            f"<span style='color:{hcolor};font-weight:700'>{fl(t1)} {t1}</span>"
            f"<span style='background:var(--card);padding:2px 10px;border-radius:4px;font-family:Bebas Neue;font-size:18px;margin:0 8px;'>{hg} - {ag}</span>"
            f"<span style='color:{acolor};font-weight:700'>{fl(t2)} {t2}</span>"
            f"{sh} &nbsp; {sa}"
            f"</div>",
            unsafe_allow_html=True
        )


def knockout_input(prefix, t1, t2, players_t1, players_t2, allow_draw=False):
    """
    Input para partido de eliminatoria directa.
    Si empate muestra opción penaltis.
    Retorna dict result o None.
    """
    key_base = f"ko_{prefix}_{t1}_{t2}"
    with st.expander(f"⚔️ {fl(t1)} {t1}  vs  {fl(t2)} {t2}", expanded=False):
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
                s = st.selectbox(f"⚽ Gol {g+1} ({t1})", ["(sin registrar)"]+pn, key=f"{key_base}_sh{g}")
                if s != "(sin registrar)": scorers_h.append(s)
        if ag > 0 and players_t2:
            pn2 = [p["name"] for p in players_t2]
            for g in range(int(ag)):
                s = st.selectbox(f"⚽ Gol {g+1} ({t2})", ["(sin registrar)"]+pn2, key=f"{key_base}_sa{g}")
                if s != "(sin registrar)": scorers_a.append(s)

        if st.button("💾 Guardar", key=f"{key_base}_save"):
            if winner is None and hg == ag and not allow_draw:
                st.error("Debes elegir ganador en penaltis")
                return None
            if winner is None:
                winner = t1 if hg >= ag else t2
            return {"hg":int(hg),"ag":int(ag),"winner":winner,
                    "penalty_winner":penalty_winner,
                    "scorers_h":scorers_h,"scorers_a":scorers_a}
    return None


def champ_banner(team, title="CAMPEÓN"):
    st.markdown(f"""
    <div class='card card-gold' style='text-align:center;padding:28px;margin:12px 0;'>
      <div style='font-size:52px;'>{fl(team)}</div>
      <div style='font-family:Bebas Neue;font-size:40px;letter-spacing:5px;color:#FFD700;'>🏆 {title}</div>
      <div style='font-family:Bebas Neue;font-size:28px;letter-spacing:3px;'>{team}</div>
    </div>""", unsafe_allow_html=True)


def conf_header(emoji, name, color, info=""):
    st.markdown(f"""
    <div style='border-left:4px solid {color};padding:8px 16px;margin-bottom:16px;'>
      <div style='font-family:Bebas Neue;font-size:32px;letter-spacing:4px;'>{emoji} {name}</div>
      <div style='color:var(--muted);font-size:12px;letter-spacing:2px;'>{info}</div>
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:12px 0 8px;'>
      <div style='font-family:Bebas Neue;font-size:30px;letter-spacing:5px;color:#00E5A0;'>⚽ MMJ</div>
      <div style='font-size:10px;letter-spacing:4px;color:#6B7A99;'>WORLD CUP SIMULATOR</div>
    </div>""", unsafe_allow_html=True)
    st.divider()

    PAGES = [
        "🏠 Inicio",
        "🌍 UEFA · Eurocopa",
        "🔢 UEFA · Playoffs Mundial",
        "🌎 CONMEBOL · Copa América",
        "🔢 CONMEBOL · Playoffs",
        "🌍 CAF · Copa África",
        "🔢 CAF · Playoffs",
        "🌎 CONCACAF · Copa Oro",
        "🔢 CONCACAF · Playoffs",
        "🌏 AFC · Copa Asia",
        "🔢 AFC · Playoffs",
        "🔄 Repechaje Internacional",
        "🏆 Mundial",
        "📊 Ranking FIFA",
        "⚽ Goleadores",
        "👥 Plantillas",
    ]
    for p in PAGES:
        if st.button(p, key=f"nav_{p}", use_container_width=True):
            st.session_state.active_page = p
            st.rerun()

    st.divider()
    st.markdown(f"<div style='text-align:center;font-size:12px;color:var(--muted);'>Temporada {st.session_state.season}</div>", unsafe_allow_html=True)
    nq = len(st.session_state.wc_qualified)
    st.markdown(f"<div style='text-align:center;font-size:13px;color:var(--g);'>{nq}/32 clasificados</div>", unsafe_allow_html=True)

page = st.session_state.active_page

# ══════════════════════════════════════════════
# INICIO
# ══════════════════════════════════════════════
if page == "🏠 Inicio":
    st.markdown("<div class='hero'>MMJ WORLD CUP</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub'>Simulador Manual · Temporada {st.session_state.season}</div>", unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Clasificados", f"{len(st.session_state.wc_qualified)}/32")
    champ = st.session_state.wc_champion or "—"
    c2.metric("🏆 Campeón", champ)
    rnk1 = max(st.session_state.fifa_ranking, key=st.session_state.fifa_ranking.get)
    c3.metric("Ranking #1", f"{fl(rnk1)} {rnk1}")
    c4.metric("Temporada", st.session_state.season)

    st.divider()
    st.markdown("### 📋 Estado de torneos")
    cups = [
        ("🌍 Eurocopa","euro_champion","UEFA","#4A90D9"),
        ("🌎 Copa América","ca_champion","CONMEBOL","#27AE60"),
        ("🌍 Copa África","af_champion","CAF","#F39C12"),
        ("🌎 Copa Oro","co_champion","CONCACAF","#E74C3C"),
        ("🌏 Copa Asia","as_champion","AFC","#9B59B6"),
    ]
    cols = st.columns(5)
    for col,(name,key,conf,color) in zip(cols,cups):
        champ = st.session_state.get(key)
        with col:
            st.markdown(f"""
            <div class='card' style='border-left:4px solid {color};text-align:center;'>
              <div style='font-size:10px;color:{color};letter-spacing:2px;'>{conf}</div>
              <div style='font-weight:700;font-size:13px;'>{name}</div>
              {"<div style='color:#FFD700;font-size:12px;'>🏆 "+fl(champ)+" "+champ+"</div>" if champ else "<div style='color:var(--muted);font-size:12px;'>⏳ Pendiente</div>"}
            </div>""", unsafe_allow_html=True)

    if st.session_state.wc_qualified:
        st.divider()
        st.markdown("### ✅ Clasificados al Mundial")
        teams = st.session_state.wc_qualified
        for i in range(0, len(teams), 6):
            cols = st.columns(6)
            for j, t in enumerate(teams[i:i+6]):
                with cols[j]:
                    st.markdown(f"<div class='card' style='text-align:center;padding:8px;'><div style='font-size:22px;'>{fl(t)}</div><div style='font-size:11px;'>{t}</div></div>", unsafe_allow_html=True)

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
                          ["fifa_ranking","season","season_history","active_page","top_scorers"]]
            for k in keys_reset:
                del st.session_state[k]
            init_state()
            st.rerun()


# ══════════════════════════════════════════════
# EUROCOPA
# ══════════════════════════════════════════════
elif page == "🌍 UEFA · Eurocopa":
    conf_header("🌍","EUROCOPA UEFA","#4A90D9","24 equipos · 6 grupos de 4 · Pasan 2 por grupo + 4 mejores 3ros → R16")

    tab_setup, tab_groups, tab_ko, tab_result = st.tabs(["⚙️ Configurar","📊 Grupos","🎯 Eliminatorias","🏆 Resultado"])

    # ── SETUP ──
    with tab_setup:
        st.markdown("#### Selecciona y arma los 6 grupos (4 equipos c/u)")
        selected = st.multiselect("Elige 24 equipos UEFA", UEFA_TEAMS, default=st.session_state.euro_teams or UEFA_TEAMS[:24], max_selections=24)

        if len(selected) == 24:
            st.session_state.euro_teams = selected
            st.markdown("---")
            st.markdown("**Arrastra (asigna) equipos a cada grupo:**")
            cols = st.columns(3)
            group_labels = ["A","B","C","D","E","F"]
            new_groups = {}
            for i, gl in enumerate(group_labels):
                with cols[i % 3]:
                    st.markdown(f"**Grupo {gl}**")
                    default_g = st.session_state.euro_groups.get(gl, selected[i*4:(i+1)*4])
                    chosen = st.multiselect(f"Grupo {gl}", selected, default=default_g, max_selections=4, key=f"euro_grp_{gl}")
                    new_groups[gl] = chosen

            if st.button("💾 Guardar grupos"):
                # Validate no duplicates
                all_assigned = sum(new_groups.values(), [])
                if len(all_assigned) != len(set(all_assigned)):
                    st.error("Un equipo está en más de un grupo.")
                elif any(len(v) != 4 for v in new_groups.values()):
                    st.error("Cada grupo debe tener exactamente 4 equipos.")
                else:
                    st.session_state.euro_groups = new_groups
                    # Init matches
                    all_matches = {}
                    for gl, teams in new_groups.items():
                        m = generate_group_matches(teams)
                        all_matches.update(m)
                    st.session_state.euro_matches = all_matches
                    st.success("✅ Grupos guardados. Ve a la pestaña Grupos para ingresar resultados.")
                    st.rerun()
        else:
            st.info(f"Selecciona exactamente 24 equipos. Tienes {len(selected)}.")

    # ── GRUPOS ──
    with tab_groups:
        if not st.session_state.euro_groups:
            st.info("Configura los grupos primero.")
        else:
            group_labels = ["A","B","C","D","E","F"]
            # Render cada grupo
            for gl in group_labels:
                teams = st.session_state.euro_groups.get(gl, [])
                if not teams: continue
                with st.expander(f"🗂️ Grupo {gl} — {' · '.join(fl(t)+' '+t for t in teams)}", expanded=True):
                    col_m, col_t = st.columns([3,2])
                    with col_m:
                        st.markdown("**Partidos**")
                        for t1, t2 in combinations(teams, 2):
                            key = (t1,t2) if (t1,t2) in st.session_state.euro_matches else (t2,t1)
                            res = st.session_state.euro_matches.get(key)
                            render_match_result(t1, t2, res)
                            if res is None:
                                r = match_input_form("euro", t1, t2,
                                                     PLAYERS.get(t1,[]), PLAYERS.get(t2,[]),
                                                     key_suffix=gl)
                                if r:
                                    hg,ag,sh,sa = r
                                    st.session_state.euro_matches[key] = {"hg":hg,"ag":ag,"scorers_h":sh,"scorers_a":sa}
                                    for s in sh: update_scorer(s, t1, 1, "euro_")
                                    for s in sa: update_scorer(s, t2, 1, "euro_")
                                    st.rerun()
                    with col_t:
                        st.markdown("**Posiciones**")
                        group_m = {k:v for k,v in st.session_state.euro_matches.items()
                                   if k[0] in teams and k[1] in teams and v is not None}
                        standings = compute_standings(teams, group_m)
                        st.session_state.euro_standings[gl] = standings
                        render_standings(standings, highlight=2)

            # Calcular quién pasa (top2 + 4 mejores 3ros)
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
                for i,(lbl,t) in enumerate(all_r16):
                    with cols[i%4]:
                        st.markdown(f"<div class='card' style='text-align:center;padding:8px;'><span style='font-size:10px;color:var(--muted);'>{lbl}</span><br><span style='font-size:20px;'>{fl(t)}</span><br><span style='font-size:12px;'>{t}</span></div>", unsafe_allow_html=True)

                if st.button("➡️ Generar R16 con estos clasificados") and len(all_r16) == 16:
                    # R16 modelo Eurocopa real: 1A-2C, 1B-3ADEF, 1C-3ABDE, 1E-3BCD, 1F-3ABD, 1D-2F, 1H-2G, etc.
                    # Simplificado por posición: 1A v 2B, 1C v 2D, 1E v 2F, 1B v 2A/3*, etc.
                    # Usamos el orden de all_r16 para armar 8 partidos:
                    by_slot = {lbl: t for lbl,t in all_r16}
                    # Eurocopa real R16 fixture (usando slots fijos)
                    # Slots: A1,A2,B1,B2,C1,C2,D1,D2,E1,E2,F1,F2 + 4x3*
                    # bracket oficial UEFA: 1A v 2C, 1B v 3*, 1C v 2D, 1D v 2F, 1E v 3*, 1F v 3*, 1A2 v 2B, etc.
                    # Para simplicidad organizamos por ranking de grupo:
                    r16_pairs = [
                        (by_slot.get("A1","?"), by_slot.get("C2","?")),
                        (by_slot.get("D1","?"), by_slot.get("F2","?")),
                        (by_slot.get("B1","?"), by_slot.get("E2","?")),
                        (by_slot.get("A2","?"), by_slot.get("B2","?")),
                        (by_slot.get("C1","?"), by_slot.get("D2","?")),
                        (by_slot.get("E1","?"), by_slot.get("F1","?")),
                        (list(best_thirds)[0][1] if best_thirds else "?", list(best_thirds)[1][1] if len(best_thirds)>1 else "?"),
                        (list(best_thirds)[2][1] if len(best_thirds)>2 else "?", list(best_thirds)[3][1] if len(best_thirds)>3 else "?"),
                    ]
                    st.session_state.euro_r16 = r16_pairs
                    st.session_state.euro_r16_results = {}
                    st.success("✅ R16 generado. Ve a Eliminatorias.")
                    st.rerun()

    # ── ELIMINATORIAS ──
    with tab_ko:
        if not st.session_state.euro_r16:
            st.info("Completa los grupos y genera el R16 primero.")
        else:
            # R16
            st.markdown("### ⚔️ Octavos de Final (R16)")
            r16_winners = []
            for i,(t1,t2) in enumerate(st.session_state.euro_r16):
                res = st.session_state.euro_r16_results.get(i)
                if res:
                    render_match_result(t1, t2, res)
                    r16_winners.append(res["winner"])
                else:
                    r = knockout_input(f"euro_r16_{i}", t1, t2, PLAYERS.get(t1,[]), PLAYERS.get(t2,[]))
                    if r:
                        st.session_state.euro_r16_results[i] = r
                        for s in r.get("scorers_h",[]): update_scorer(s,t1,1,"euro_")
                        for s in r.get("scorers_a",[]): update_scorer(s,t2,1,"euro_")
                        st.rerun()
                    r16_winners.append(None)

            # QF si R16 completo
            if all(r16_winners) and len(r16_winners) == 8:
                if not st.session_state.euro_qf:
                    st.session_state.euro_qf = [(r16_winners[i],r16_winners[i+1]) for i in range(0,8,2)]

                st.markdown("### ⚔️ Cuartos de Final")
                qf_winners = []
                for i,(t1,t2) in enumerate(st.session_state.euro_qf):
                    if t1 is None or t2 is None: continue
                    res = st.session_state.euro_qf_results.get(i)
                    if res:
                        render_match_result(t1, t2, res)
                        qf_winners.append(res["winner"])
                    else:
                        r = knockout_input(f"euro_qf_{i}", t1, t2, PLAYERS.get(t1,[]), PLAYERS.get(t2,[]))
                        if r:
                            st.session_state.euro_qf_results[i] = r
                            for s in r.get("scorers_h",[]): update_scorer(s,t1,1,"euro_")
                            for s in r.get("scorers_a",[]): update_scorer(s,t2,1,"euro_")
                            st.rerun()
                        qf_winners.append(None)

                # SF
                if all(qf_winners) and len(qf_winners) == 4:
                    if not st.session_state.euro_sf:
                        st.session_state.euro_sf = [(qf_winners[0],qf_winners[1]),(qf_winners[2],qf_winners[3])]

                    st.markdown("### ⚔️ Semifinales")
                    sf_winners = []
                    sf_losers = []
                    for i,(t1,t2) in enumerate(st.session_state.euro_sf):
                        if t1 is None or t2 is None: continue
                        res = st.session_state.euro_sf_results.get(i)
                        if res:
                            render_match_result(t1, t2, res)
                            sf_winners.append(res["winner"])
                            sf_losers.append(t2 if res["winner"]==t1 else t1)
                        else:
                            r = knockout_input(f"euro_sf_{i}", t1, t2, PLAYERS.get(t1,[]), PLAYERS.get(t2,[]))
                            if r:
                                st.session_state.euro_sf_results[i] = r
                                for s in r.get("scorers_h",[]): update_scorer(s,t1,1,"euro_")
                                for s in r.get("scorers_a",[]): update_scorer(s,t2,1,"euro_")
                                st.rerun()
                            sf_winners.append(None)

                    # FINAL
                    if all(sf_winners) and len(sf_winners) == 2:
                        if st.session_state.euro_final is None:
                            st.session_state.euro_final = (sf_winners[0], sf_winners[1])

                        st.markdown("### 🏆 FINAL")
                        t1,t2 = st.session_state.euro_final
                        res = st.session_state.euro_final_result
                        if res:
                            render_match_result(t1, t2, res)
                            champ_banner(res["winner"], "CAMPEÓN DE EUROPA")
                        else:
                            r = knockout_input("euro_final", t1, t2, PLAYERS.get(t1,[]), PLAYERS.get(t2,[]))
                            if r:
                                st.session_state.euro_final_result = r
                                st.session_state.euro_champion = r["winner"]
                                for s in r.get("scorers_h",[]): update_scorer(s,t1,1,"euro_")
                                for s in r.get("scorers_a",[]): update_scorer(s,t2,1,"euro_")
                                # build final standings
                                champion = r["winner"]
                                runner = t2 if champion==t1 else t1
                                # Ordenar: 1=champ, 2=runner, 3-4=SF losers, 5-8=QF losers, etc.
                                fs = [{"pos":1,"team":champion},{"pos":2,"team":runner}]
                                pos = 3
                                for lsr in (sf_losers if sf_losers else []):
                                    if lsr: fs.append({"pos":pos,"team":lsr}); pos+=1
                                for i_,res_ in st.session_state.euro_qf_results.items():
                                    lsr = res_["t1"] if res_["winner"]!=res_.get("t1") else res_.get("t2")
                                    lsr = (st.session_state.euro_qf[i_][0] if res_["winner"]==st.session_state.euro_qf[i_][1]
                                           else st.session_state.euro_qf[i_][1]) if i_ < len(st.session_state.euro_qf) else None
                                    if lsr and lsr not in [e["team"] for e in fs]:
                                        fs.append({"pos":pos,"team":lsr}); pos+=1
                                for i_, res_ in st.session_state.euro_r16_results.items():
                                    t1_,t2_ = st.session_state.euro_r16[i_]
                                    lsr = t2_ if res_["winner"]==t1_ else t1_
                                    if lsr and lsr not in [e["team"] for e in fs]:
                                        fs.append({"pos":pos,"team":lsr}); pos+=1
                                # Add group stage eliminees
                                placed = {e["team"] for e in fs}
                                for gl,s in st.session_state.euro_standings.items():
                                    for entry in s:
                                        if entry["team"] not in placed:
                                            fs.append({"pos":pos,"team":entry["team"]}); pos+=1; placed.add(entry["team"])
                                st.session_state.euro_final_standings = fs
                                update_ranking_from_standings(fs, 80, 4)
                                # Add champion to WC qualified
                                if champion not in st.session_state.wc_qualified:
                                    st.session_state.wc_qualified.append(champion)
                                st.rerun()

    with tab_result:
        if st.session_state.euro_champion:
            champ_banner(st.session_state.euro_champion, "CAMPEÓN DE EUROPA")
            st.markdown("#### 📊 Clasificación Final")
            render_standings(st.session_state.euro_final_standings[:10], highlight=5)
            st.info(f"El campeón **{st.session_state.euro_champion}** va directo al Mundial. Los puestos 2-5 también van directos. Del puesto 6 al 21 van a las Eliminatorias UEFA.")
        else:
            st.info("La Eurocopa aún no tiene resultado final.")


# ══════════════════════════════════════════════
# UEFA PLAYOFFS
# ══════════════════════════════════════════════
elif page == "🔢 UEFA · Playoffs Mundial":
    conf_header("🔢","UEFA · ELIMINATORIAS MUNDIALISTAS","#4A90D9","Puestos 6-21 Eurocopa → 4 grupos de 4 · Top 2 c/u → Mundial")

    if not st.session_state.euro_final_standings:
        st.warning("Primero completa la Eurocopa.")
    else:
        fs = st.session_state.euro_final_standings
        pool = [e["team"] for e in fs[5:21]]  # puestos 6-21

        tab1, tab2 = st.tabs(["⚙️ Grupos","📊 Resultados"])
        with tab1:
            st.markdown("**Equipos disponibles (puestos 6-21 Eurocopa):**")
            st.write(" · ".join(f"{fl(t)} {t}" for t in pool))
            st.markdown("---")
            st.markdown("**Arma los 4 grupos (4 equipos c/u):**")
            cols = st.columns(4)
            new_groups = {}
            for i, gl in enumerate(["A","B","C","D"]):
                with cols[i]:
                    st.markdown(f"**Grupo {gl}**")
                    default_g = st.session_state.euro_playoff_groups.get(gl, pool[i*4:(i+1)*4])
                    chosen = st.multiselect(f"Grupo {gl}", pool, default=default_g, max_selections=4, key=f"ep_grp_{gl}")
                    new_groups[gl] = chosen

            if st.button("💾 Guardar grupos playoff"):
                all_a = sum(new_groups.values(),[])
                if len(all_a)!=len(set(all_a)):
                    st.error("Duplicados.")
                elif any(len(v)!=4 for v in new_groups.values()):
                    st.error("Cada grupo necesita 4 equipos.")
                else:
                    st.session_state.euro_playoff_groups = new_groups
                    all_m = {}
                    for gl,teams in new_groups.items():
                        all_m.update(generate_group_matches(teams))
                    st.session_state.euro_playoff_matches = all_m
                    st.success("✅ Grupos guardados.")
                    st.rerun()

        with tab2:
            if not st.session_state.euro_playoff_groups:
                st.info("Arma los grupos primero.")
            else:
                for gl in ["A","B","C","D"]:
                    teams = st.session_state.euro_playoff_groups.get(gl,[])
                    if not teams: continue
                    with st.expander(f"Grupo {gl}", expanded=True):
                        col_m, col_t = st.columns([3,2])
                        with col_m:
                            for t1,t2 in combinations(teams,2):
                                key = (t1,t2) if (t1,t2) in st.session_state.euro_playoff_matches else (t2,t1)
                                res = st.session_state.euro_playoff_matches.get(key)
                                render_match_result(t1,t2,res)
                                if res is None:
                                    r = match_input_form("ep",t1,t2,PLAYERS.get(t1,[]),PLAYERS.get(t2,[]),key_suffix=gl)
                                    if r:
                                        hg,ag,sh,sa = r
                                        st.session_state.euro_playoff_matches[key]={"hg":hg,"ag":ag,"scorers_h":sh,"scorers_a":sa}
                                        st.rerun()
                        with col_t:
                            gm = {k:v for k,v in st.session_state.euro_playoff_matches.items()
                                  if k[0] in teams and k[1] in teams and v is not None}
                            s = compute_standings(teams, gm)
                            st.session_state.euro_playoff_standings[gl] = s
                            render_standings(s, highlight=2)

                # Clasificados
                st.divider()
                qualified = []
                for gl in ["A","B","C","D"]:
                    s = st.session_state.euro_playoff_standings.get(gl,[])
                    qualified.extend([e["team"] for e in s[:2]])

                st.markdown(f"#### ✅ Clasificados al Mundial via Playoffs UEFA ({len(qualified)})")
                for t in qualified:
                    st.markdown(f"✅ {fl(t)} **{t}**")

                if st.button("💾 Confirmar clasificados UEFA al Mundial"):
                    # Direct top 5 eurocopa + 8 playoff
                    euro_direct = [e["team"] for e in st.session_state.euro_final_standings[:5]]
                    all_uefa = list(set(euro_direct + qualified))
                    for t in all_uefa:
                        if t not in st.session_state.wc_qualified:
                            st.session_state.wc_qualified.append(t)
                    st.session_state.euro_playoff_qualified = all_uefa
                    st.success(f"✅ {len(all_uefa)} equipos UEFA confirmados al Mundial.")


# ══════════════════════════════════════════════
# COPA AMERICA
# ══════════════════════════════════════════════
elif page == "🌎 CONMEBOL · Copa América":
    conf_header("🌎","COPA AMÉRICA","#27AE60","10 equipos CONMEBOL + 6 invitados · 4 grupos de 4 · 2 pasan por grupo")

    tab_setup, tab_groups, tab_ko, tab_result = st.tabs(["⚙️ Config","📊 Grupos","🎯 Bracket","🏆 Resultado"])

    with tab_setup:
        st.markdown("#### Equipos invitados (6, no UEFA)")
        guests = st.multiselect("Selecciona 6 invitados", COPA_AMERICA_GUESTS_POOL,
                                default=st.session_state.ca_teams[10:] if len(st.session_state.ca_teams)==16 else [],
                                max_selections=6)
        all_ca = CONMEBOL_TEAMS + guests
        st.markdown(f"**Total: {len(all_ca)}/16 equipos**")
        if len(all_ca) == 16:
            st.markdown("---")
            st.markdown("**Arma 4 grupos de 4:**")
            cols = st.columns(4)
            new_groups = {}
            for i,gl in enumerate(["A","B","C","D"]):
                with cols[i]:
                    st.markdown(f"**Grupo {gl}**")
                    default_g = st.session_state.ca_groups.get(gl, all_ca[i*4:(i+1)*4])
                    chosen = st.multiselect(f"Grupo {gl}", all_ca, default=default_g, max_selections=4, key=f"ca_grp_{gl}")
                    new_groups[gl] = chosen

            if st.button("💾 Guardar grupos Copa América"):
                all_a = sum(new_groups.values(),[])
                if len(all_a)!=len(set(all_a)):
                    st.error("Duplicados.")
                elif any(len(v)!=4 for v in new_groups.values()):
                    st.error("4 equipos por grupo.")
                else:
                    st.session_state.ca_teams = all_ca
                    st.session_state.ca_groups = new_groups
                    all_m = {}
                    for gl,teams in new_groups.items():
                        all_m.update(generate_group_matches(teams))
                    st.session_state.ca_matches = all_m
                    st.success("✅ Grupos guardados.")
                    st.rerun()

    with tab_groups:
        if not st.session_state.ca_groups:
            st.info("Configura los grupos primero.")
        else:
            for gl in ["A","B","C","D"]:
                teams = st.session_state.ca_groups.get(gl,[])
                if not teams: continue
                with st.expander(f"Grupo {gl}", expanded=True):
                    col_m, col_t = st.columns([3,2])
                    with col_m:
                        for t1,t2 in combinations(teams,2):
                            key=(t1,t2) if (t1,t2) in st.session_state.ca_matches else (t2,t1)
                            res=st.session_state.ca_matches.get(key)
                            render_match_result(t1,t2,res)
                            if res is None:
                                r=match_input_form("ca",t1,t2,PLAYERS.get(t1,[]),PLAYERS.get(t2,[]),key_suffix=gl)
                                if r:
                                    hg,ag,sh,sa=r
                                    st.session_state.ca_matches[key]={"hg":hg,"ag":ag,"scorers_h":sh,"scorers_a":sa}
                                    for s in sh: update_scorer(s,t1,1,"ca_")
                                    for s in sa: update_scorer(s,t2,1,"ca_")
                                    st.rerun()
                    with col_t:
                        gm={k:v for k,v in st.session_state.ca_matches.items()
                            if k[0] in teams and k[1] in teams and v is not None}
                        s=compute_standings(teams,gm)
                        st.session_state.ca_standings[gl]=s
                        render_standings(s, highlight=2)

            # Generar R16 bracket
            st.divider()
            by_slot = {}
            for gl in ["A","B","C","D"]:
                s = st.session_state.ca_standings.get(gl,[])
                if len(s)>=2:
                    by_slot[f"{gl}1"]=s[0]["team"]
                    by_slot[f"{gl}2"]=s[1]["team"]

            if len(by_slot)==8:
                st.markdown("#### Bracket R16 Copa América")
                # Bracket definido: A1vD2, C1vB2 → SF izq; B1vC2, D1vA2 → SF der
                ca_r16 = [
                    (by_slot.get("A1","?"), by_slot.get("D2","?")),
                    (by_slot.get("C1","?"), by_slot.get("B2","?")),
                    (by_slot.get("B1","?"), by_slot.get("C2","?")),
                    (by_slot.get("D1","?"), by_slot.get("A2","?")),
                ]
                for t1,t2 in ca_r16:
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
            # QF (4 partidos R16 → 4 ganadores directo a SF por bracket)
            st.markdown("### ⚔️ Cuartos de Final")
            r16_winners = []
            for i,(t1,t2) in enumerate(st.session_state.ca_r16):
                res = st.session_state.ca_r16_results.get(i)
                if res:
                    render_match_result(t1,t2,res)
                    r16_winners.append(res["winner"])
                else:
                    r=knockout_input(f"ca_r16_{i}",t1,t2,PLAYERS.get(t1,[]),PLAYERS.get(t2,[]))
                    if r:
                        st.session_state.ca_r16_results[i]=r
                        for s in r.get("scorers_h",[]): update_scorer(s,t1,1,"ca_")
                        for s in r.get("scorers_a",[]): update_scorer(s,t2,1,"ca_")
                        st.rerun()
                    r16_winners.append(None)

            # SF bracket: ganador partido 1 vs ganador partido 2 (izq), ganador 3 vs ganador 4 (der)
            if all(r16_winners) and len(r16_winners)==4:
                if not st.session_state.ca_sf:
                    st.session_state.ca_sf = [(r16_winners[0],r16_winners[1]),(r16_winners[2],r16_winners[3])]

                st.markdown("### ⚔️ Semifinales")
                sf_winners=[]
                for i,(t1,t2) in enumerate(st.session_state.ca_sf):
                    res=st.session_state.ca_sf_results.get(i)
                    if res:
                        render_match_result(t1,t2,res)
                        sf_winners.append(res["winner"])
                    else:
                        r=knockout_input(f"ca_sf_{i}",t1,t2,PLAYERS.get(t1,[]),PLAYERS.get(t2,[]))
                        if r:
                            st.session_state.ca_sf_results[i]=r
                            for s in r.get("scorers_h",[]): update_scorer(s,t1,1,"ca_")
                            for s in r.get("scorers_a",[]): update_scorer(s,t2,1,"ca_")
                            st.rerun()
                        sf_winners.append(None)

                if all(sf_winners) and len(sf_winners)==2:
                    if st.session_state.ca_final is None:
                        st.session_state.ca_final=(sf_winners[0],sf_winners[1])

                    st.markdown("### 🏆 FINAL")
                    t1,t2=st.session_state.ca_final
                    res=st.session_state.ca_final_result
                    if res:
                        render_match_result(t1,t2,res)
                        champ_banner(res["winner"],"CAMPEÓN DE AMÉRICA")
                    else:
                        r=knockout_input("ca_final",t1,t2,PLAYERS.get(t1,[]),PLAYERS.get(t2,[]))
                        if r:
                            st.session_state.ca_final_result=r
                            champ=r["winner"]
                            st.session_state.ca_champion=champ
                            for s in r.get("scorers_h",[]): update_scorer(s,t1,1,"ca_")
                            for s in r.get("scorers_a",[]): update_scorer(s,t2,1,"ca_")
                            # Final standings
                            runner=t2 if champ==t1 else t1
                            fs=[{"pos":1,"team":champ},{"pos":2,"team":runner}]
                            pos=3
                            for i_,(ta,tb) in enumerate(st.session_state.ca_sf):
                                res_=st.session_state.ca_sf_results.get(i_)
                                if res_:
                                    lsr=tb if res_["winner"]==ta else ta
                                    fs.append({"pos":pos,"team":lsr}); pos+=1
                            placed={e["team"] for e in fs}
                            for gl,s in st.session_state.ca_standings.items():
                                for entry in s:
                                    if entry["team"] not in placed:
                                        fs.append({"pos":pos,"team":entry["team"]}); pos+=1; placed.add(entry["team"])
                            st.session_state.ca_final_standings=fs
                            update_ranking_from_standings(fs,80,5)
                            if champ not in st.session_state.wc_qualified:
                                st.session_state.wc_qualified.append(champ)
                            st.rerun()

    with tab_result:
        if st.session_state.ca_champion:
            champ_banner(st.session_state.ca_champion,"CAMPEÓN DE AMÉRICA")
            render_standings(st.session_state.ca_final_standings[:10], highlight=1)
        else:
            st.info("Copa América sin resultado aún.")


# ══════════════════════════════════════════════
# CONMEBOL PLAYOFFS
# ══════════════════════════════════════════════
elif page == "🔢 CONMEBOL · Playoffs":
    conf_header("🔢","CONMEBOL · PLAYOFFS MUNDIALISTAS","#27AE60","Puestos 2-7 → todos vs todos · Top 3 → Mundial · 4to → Repechaje")

    if not st.session_state.ca_final_standings:
        st.warning("Completa la Copa América primero.")
    else:
        fs = st.session_state.ca_final_standings
        # Solo equipos CONMEBOL en puestos 2-7
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
            for t1,t2 in combinations(teams,2):
                key=(t1,t2) if (t1,t2) in st.session_state.conmebol_playoff_matches else (t2,t1)
                res=st.session_state.conmebol_playoff_matches.get(key)
                render_match_result(t1,t2,res)
                if res is None:
                    r=match_input_form("cmp",t1,t2,PLAYERS.get(t1,[]),PLAYERS.get(t2,[]))
                    if r:
                        hg,ag,sh,sa=r
                        st.session_state.conmebol_playoff_matches[key]={"hg":hg,"ag":ag,"scorers_h":sh,"scorers_a":sa}
                        st.rerun()

            st.divider()
            played={k:v for k,v in st.session_state.conmebol_playoff_matches.items() if v is not None}
            standings=compute_standings(teams,played)
            st.session_state.conmebol_playoff_standings=standings
            render_standings(standings, highlight=3, repechaje_pos=4)

            qualified=[s["team"] for s in standings[:3]]
            repechaje=standings[3]["team"] if len(standings)>3 else None

            st.markdown(f"**✅ Clasificados:** {' · '.join(fl(t)+' '+t for t in qualified)}")
            if repechaje: st.markdown(f"**🔄 Repechaje:** {fl(repechaje)} {repechaje}")

            if st.button("💾 Confirmar clasificados CONMEBOL"):
                for t in qualified:
                    if t not in st.session_state.wc_qualified:
                        st.session_state.wc_qualified.append(t)
                st.session_state.conmebol_playoff_qualified=qualified
                st.session_state.conmebol_playoff_repechaje=repechaje
                st.success("✅ Confirmados.")


# ══════════════════════════════════════════════
# COPA AFRICA
# ══════════════════════════════════════════════
elif page == "🌍 CAF · Copa África":
    conf_header("🌍","COPA ÁFRICA CAF","#F39C12","10 equipos · 2 grupos de 5 · 1 ronda · 2 primeros → Semis")

    tab_setup,tab_groups,tab_ko,tab_result = st.tabs(["⚙️ Config","📊 Grupos","🎯 Eliminatorias","🏆 Resultado"])

    with tab_setup:
        selected=st.multiselect("Elige 10 equipos CAF",CAF_TEAMS,default=st.session_state.af_teams or CAF_TEAMS,max_selections=10)
        if len(selected)==10:
            st.markdown("**Arma 2 grupos de 5:**")
            col1,col2=st.columns(2)
            with col1:
                st.markdown("**Grupo A**")
                gA=st.multiselect("Grupo A",selected,default=st.session_state.af_groups.get("A",selected[:5]),max_selections=5,key="af_gA")
            with col2:
                st.markdown("**Grupo B**")
                gB=st.multiselect("Grupo B",selected,default=st.session_state.af_groups.get("B",selected[5:]),max_selections=5,key="af_gB")

            if st.button("💾 Guardar grupos África"):
                if len(gA)!=5 or len(gB)!=5:
                    st.error("5 equipos por grupo.")
                elif len(set(gA+gB))!=10:
                    st.error("Duplicados.")
                else:
                    st.session_state.af_teams=selected
                    st.session_state.af_groups={"A":gA,"B":gB}
                    st.session_state.af_matches={**generate_group_matches(gA),**generate_group_matches(gB)}
                    st.success("✅ Grupos guardados.")
                    st.rerun()

    with tab_groups:
        if not st.session_state.af_groups:
            st.info("Configura primero.")
        else:
            for gl in ["A","B"]:
                teams=st.session_state.af_groups.get(gl,[])
                with st.expander(f"Grupo {gl}",expanded=True):
                    col_m,col_t=st.columns([3,2])
                    with col_m:
                        for t1,t2 in combinations(teams,2):
                            key=(t1,t2) if (t1,t2) in st.session_state.af_matches else (t2,t1)
                            res=st.session_state.af_matches.get(key)
                            render_match_result(t1,t2,res)
                            if res is None:
                                r=match_input_form("af",t1,t2,PLAYERS.get(t1,[]),PLAYERS.get(t2,[]),key_suffix=gl)
                                if r:
                                    hg,ag,sh,sa=r
                                    st.session_state.af_matches[key]={"hg":hg,"ag":ag,"scorers_h":sh,"scorers_a":sa}
                                    for s in sh: update_scorer(s,t1,1,"af_")
                                    for s in sa: update_scorer(s,t2,1,"af_")
                                    st.rerun()
                    with col_t:
                        gm={k:v for k,v in st.session_state.af_matches.items()
                            if k[0] in teams and k[1] in teams and v is not None}
                        s=compute_standings(teams,gm)
                        st.session_state.af_standings[gl]=s
                        render_standings(s, highlight=2)

            st.divider()
            sA=st.session_state.af_standings.get("A",[])
            sB=st.session_state.af_standings.get("B",[])
            if len(sA)>=2 and len(sB)>=2:
                sf1=(sA[0]["team"],sB[1]["team"])
                sf2=(sB[0]["team"],sA[1]["team"])
                st.markdown(f"**SF1:** {fl(sf1[0])} {sf1[0]} vs {fl(sf1[1])} {sf1[1]}")
                st.markdown(f"**SF2:** {fl(sf2[0])} {sf2[0]} vs {fl(sf2[1])} {sf2[1]}")
                if st.button("➡️ Generar Semis"):
                    st.session_state.af_sf=[sf1,sf2]
                    st.session_state.af_sf_results={}
                    st.success("✅ Semis generadas.")
                    st.rerun()

    with tab_ko:
        if not st.session_state.af_sf:
            st.info("Completa grupos primero.")
        else:
            st.markdown("### ⚔️ Semifinales")
            sf_winners=[]
            for i,(t1,t2) in enumerate(st.session_state.af_sf):
                res=st.session_state.af_sf_results.get(i)
                if res:
                    render_match_result(t1,t2,res)
                    sf_winners.append(res["winner"])
                else:
                    r=knockout_input(f"af_sf_{i}",t1,t2,PLAYERS.get(t1,[]),PLAYERS.get(t2,[]))
                    if r:
                        st.session_state.af_sf_results[i]=r
                        for s in r.get("scorers_h",[]): update_scorer(s,t1,1,"af_")
                        for s in r.get("scorers_a",[]): update_scorer(s,t2,1,"af_")
                        st.rerun()
                    sf_winners.append(None)

            if all(sf_winners) and len(sf_winners)==2:
                if st.session_state.af_final is None:
                    st.session_state.af_final=(sf_winners[0],sf_winners[1])
                st.markdown("### 🏆 FINAL")
                t1,t2=st.session_state.af_final
                res=st.session_state.af_final_result
                if res:
                    render_match_result(t1,t2,res)
                    champ_banner(res["winner"],"CAMPEÓN DE ÁFRICA")
                else:
                    r=knockout_input("af_final",t1,t2,PLAYERS.get(t1,[]),PLAYERS.get(t2,[]))
                    if r:
                        st.session_state.af_final_result=r
                        champ=r["winner"]
                        runner=t2 if champ==t1 else t1
                        st.session_state.af_champion=champ
                        for s in r.get("scorers_h",[]): update_scorer(s,t1,1,"af_")
                        for s in r.get("scorers_a",[]): update_scorer(s,t2,1,"af_")
                        fs=[{"pos":1,"team":champ},{"pos":2,"team":runner}]
                        pos=3
                        placed={champ,runner}
                        for gl,s_ in st.session_state.af_standings.items():
                            for e in s_:
                                if e["team"] not in placed:
                                    fs.append({"pos":pos,"team":e["team"]}); pos+=1; placed.add(e["team"])
                        st.session_state.af_final_standings=fs
                        update_ranking_from_standings(fs,70,5)
                        for t in [champ,runner]:
                            if t not in st.session_state.wc_qualified:
                                st.session_state.wc_qualified.append(t)
                        st.rerun()

    with tab_result:
        if st.session_state.af_champion:
            champ_banner(st.session_state.af_champion,"CAMPEÓN DE ÁFRICA")
            render_standings(st.session_state.af_final_standings[:6], highlight=2)
        else:
            st.info("Sin resultado aún.")


# ══════════════════════════════════════════════
# CAF PLAYOFFS
# ══════════════════════════════════════════════
elif page == "🔢 CAF · Playoffs":
    conf_header("🔢","CAF · PLAYOFFS MUNDIALISTAS","#F39C12","Puestos 3-7 → todos vs todos · Top 3 → Mundial")

    if not st.session_state.af_final_standings:
        st.warning("Completa la Copa África primero.")
    else:
        pool=[e["team"] for e in st.session_state.af_final_standings[2:7]]
        st.markdown(f"**Equipos:** {' · '.join(fl(t)+' '+t for t in pool)}")

        if not st.session_state.caf_playoff_teams:
            if st.button("▶️ Iniciar playoff CAF"):
                st.session_state.caf_playoff_teams=pool
                st.session_state.caf_playoff_matches=generate_group_matches(pool)
                st.rerun()
        else:
            teams=st.session_state.caf_playoff_teams
            for t1,t2 in combinations(teams,2):
                key=(t1,t2) if (t1,t2) in st.session_state.caf_playoff_matches else (t2,t1)
                res=st.session_state.caf_playoff_matches.get(key)
                render_match_result(t1,t2,res)
                if res is None:
                    r=match_input_form("cafp",t1,t2,PLAYERS.get(t1,[]),PLAYERS.get(t2,[]))
                    if r:
                        hg,ag,sh,sa=r
                        st.session_state.caf_playoff_matches[key]={"hg":hg,"ag":ag,"scorers_h":sh,"scorers_a":sa}
                        st.rerun()

            st.divider()
            played={k:v for k,v in st.session_state.caf_playoff_matches.items() if v is not None}
            standings=compute_standings(teams,played)
            st.session_state.caf_playoff_standings=standings
            render_standings(standings, highlight=3)

            qualified=[s["team"] for s in standings[:3]]
            st.markdown(f"**✅ Clasificados:** {' · '.join(fl(t)+' '+t for t in qualified)}")

            if st.button("💾 Confirmar clasificados CAF"):
                for t in qualified:
                    if t not in st.session_state.wc_qualified:
                        st.session_state.wc_qualified.append(t)
                st.session_state.caf_playoff_qualified=qualified
                st.success("✅ Confirmados.")


# ══════════════════════════════════════════════
# COPA ORO
# ══════════════════════════════════════════════
elif page == "🌎 CONCACAF · Copa Oro":
    conf_header("🌎","COPA ORO CONCACAF","#E74C3C","6 equipos · 2 grupos de 3 · todos vs todos · A1vB2 y B1vA2 → Final")

    tab_setup,tab_groups,tab_ko,tab_result=st.tabs(["⚙️ Config","📊 Grupos","🎯 Eliminatorias","🏆 Resultado"])

    with tab_setup:
        selected=st.multiselect("Elige 6 equipos CONCACAF",CONCACAF_TEAMS,default=st.session_state.co_teams or CONCACAF_TEAMS,max_selections=6)
        if len(selected)==6:
            col1,col2=st.columns(2)
            with col1:
                st.markdown("**Grupo A**")
                gA=st.multiselect("Grupo A",selected,default=st.session_state.co_groups.get("A",selected[:3]),max_selections=3,key="co_gA")
            with col2:
                st.markdown("**Grupo B**")
                gB=st.multiselect("Grupo B",selected,default=st.session_state.co_groups.get("B",selected[3:]),max_selections=3,key="co_gB")

            if st.button("💾 Guardar grupos Copa Oro"):
                if len(gA)!=3 or len(gB)!=3 or len(set(gA+gB))!=6:
                    st.error("3 equipos por grupo sin duplicados.")
                else:
                    st.session_state.co_teams=selected
                    st.session_state.co_groups={"A":gA,"B":gB}
                    st.session_state.co_matches={**generate_group_matches(gA),**generate_group_matches(gB)}
                    st.success("✅ Guardados.")
                    st.rerun()

    with tab_groups:
        if not st.session_state.co_groups:
            st.info("Configura primero.")
        else:
            for gl in ["A","B"]:
                teams=st.session_state.co_groups.get(gl,[])
                with st.expander(f"Grupo {gl}",expanded=True):
                    col_m,col_t=st.columns([3,2])
                    with col_m:
                        for t1,t2 in combinations(teams,2):
                            key=(t1,t2) if (t1,t2) in st.session_state.co_matches else (t2,t1)
                            res=st.session_state.co_matches.get(key)
                            render_match_result(t1,t2,res)
                            if res is None:
                                r=match_input_form("co",t1,t2,PLAYERS.get(t1,[]),PLAYERS.get(t2,[]),key_suffix=gl)
                                if r:
                                    hg,ag,sh,sa=r
                                    st.session_state.co_matches[key]={"hg":hg,"ag":ag,"scorers_h":sh,"scorers_a":sa}
                                    for s in sh: update_scorer(s,t1,1,"co_")
                                    for s in sa: update_scorer(s,t2,1,"co_")
                                    st.rerun()
                    with col_t:
                        gm={k:v for k,v in st.session_state.co_matches.items()
                            if k[0] in teams and k[1] in teams and v is not None}
                        s=compute_standings(teams,gm)
                        st.session_state.co_standings[gl]=s
                        render_standings(s, highlight=2)

            sA=st.session_state.co_standings.get("A",[])
            sB=st.session_state.co_standings.get("B",[])
            if len(sA)>=2 and len(sB)>=2:
                sf1=(sA[0]["team"],sB[1]["team"])
                sf2=(sB[0]["team"],sA[1]["team"])
                st.markdown(f"**SF1:** {fl(sf1[0])} {sf1[0]} vs {fl(sf1[1])} {sf1[1]}")
                st.markdown(f"**SF2:** {fl(sf2[0])} {sf2[0]} vs {fl(sf2[1])} {sf2[1]}")
                if st.button("➡️ Generar Semis Copa Oro"):
                    st.session_state.co_sf=[sf1,sf2]
                    st.session_state.co_sf_results={}
                    st.rerun()

    with tab_ko:
        if not st.session_state.co_sf:
            st.info("Completa grupos primero.")
        else:
            st.markdown("### ⚔️ Semifinales")
            sf_winners=[]
            for i,(t1,t2) in enumerate(st.session_state.co_sf):
                res=st.session_state.co_sf_results.get(i)
                if res:
                    render_match_result(t1,t2,res)
                    sf_winners.append(res["winner"])
                else:
                    r=knockout_input(f"co_sf_{i}",t1,t2,PLAYERS.get(t1,[]),PLAYERS.get(t2,[]))
                    if r:
                        st.session_state.co_sf_results[i]=r
                        for s in r.get("scorers_h",[]): update_scorer(s,t1,1,"co_")
                        for s in r.get("scorers_a",[]): update_scorer(s,t2,1,"co_")
                        st.rerun()
                    sf_winners.append(None)

            if all(sf_winners) and len(sf_winners)==2:
                if st.session_state.co_final is None:
                    st.session_state.co_final=(sf_winners[0],sf_winners[1])
                st.markdown("### 🏆 FINAL")
                t1,t2=st.session_state.co_final
                res=st.session_state.co_final_result
                if res:
                    render_match_result(t1,t2,res)
                    champ_banner(res["winner"],"CAMPEÓN COPA ORO")
                else:
                    r=knockout_input("co_final",t1,t2,PLAYERS.get(t1,[]),PLAYERS.get(t2,[]))
                    if r:
                        st.session_state.co_final_result=r
                        champ=r["winner"]
                        st.session_state.co_champion=champ
                        for s in r.get("scorers_h",[]): update_scorer(s,t1,1,"co_")
                        for s in r.get("scorers_a",[]): update_scorer(s,t2,1,"co_")
                        runner=t2 if champ==t1 else t1
                        fs=[{"pos":1,"team":champ},{"pos":2,"team":runner}]
                        pos=3
                        placed={champ,runner}
                        for i_,(ta,tb) in enumerate(st.session_state.co_sf):
                            res_=st.session_state.co_sf_results.get(i_)
                            if res_:
                                lsr=tb if res_["winner"]==ta else ta
                                if lsr not in placed:
                                    fs.append({"pos":pos,"team":lsr}); pos+=1; placed.add(lsr)
                        for gl,s_ in st.session_state.co_standings.items():
                            for e in s_:
                                if e["team"] not in placed:
                                    fs.append({"pos":pos,"team":e["team"]}); pos+=1; placed.add(e["team"])
                        st.session_state.co_final_standings=fs
                        update_ranking_from_standings(fs,60,6)
                        if champ not in st.session_state.wc_qualified:
                            st.session_state.wc_qualified.append(champ)
                        st.rerun()

    with tab_result:
        if st.session_state.co_champion:
            champ_banner(st.session_state.co_champion,"CAMPEÓN COPA ORO")
            render_standings(st.session_state.co_final_standings, highlight=1)
        else:
            st.info("Sin resultado aún.")


# ══════════════════════════════════════════════
# CONCACAF PLAYOFFS
# ══════════════════════════════════════════════
elif page == "🔢 CONCACAF · Playoffs":
    conf_header("🔢","CONCACAF · PLAYOFFS","#E74C3C","Puestos 2-5 → todos vs todos · Top 2 → Mundial · 3ro → Repechaje")

    if not st.session_state.co_final_standings:
        st.warning("Completa la Copa Oro primero.")
    else:
        pool=[e["team"] for e in st.session_state.co_final_standings[1:5]]
        st.markdown(f"**Equipos:** {' · '.join(fl(t)+' '+t for t in pool)}")

        if not st.session_state.concacaf_playoff_teams:
            if st.button("▶️ Iniciar playoff CONCACAF"):
                st.session_state.concacaf_playoff_teams=pool
                st.session_state.concacaf_playoff_matches=generate_group_matches(pool)
                st.rerun()
        else:
            teams=st.session_state.concacaf_playoff_teams
            for t1,t2 in combinations(teams,2):
                key=(t1,t2) if (t1,t2) in st.session_state.concacaf_playoff_matches else (t2,t1)
                res=st.session_state.concacaf_playoff_matches.get(key)
                render_match_result(t1,t2,res)
                if res is None:
                    r=match_input_form("ccp",t1,t2,PLAYERS.get(t1,[]),PLAYERS.get(t2,[]))
                    if r:
                        hg,ag,sh,sa=r
                        st.session_state.concacaf_playoff_matches[key]={"hg":hg,"ag":ag,"scorers_h":sh,"scorers_a":sa}
                        st.rerun()

            st.divider()
            played={k:v for k,v in st.session_state.concacaf_playoff_matches.items() if v is not None}
            standings=compute_standings(teams,played)
            st.session_state.concacaf_playoff_standings=standings
            render_standings(standings, highlight=2, repechaje_pos=3)

            qualified=[s["team"] for s in standings[:2]]
            repechaje=standings[2]["team"] if len(standings)>2 else None
            st.markdown(f"**✅ Clasificados:** {' · '.join(fl(t)+' '+t for t in qualified)}")
            if repechaje: st.markdown(f"**🔄 Repechaje:** {fl(repechaje)} {repechaje}")

            if st.button("💾 Confirmar CONCACAF"):
                for t in qualified:
                    if t not in st.session_state.wc_qualified:
                        st.session_state.wc_qualified.append(t)
                st.session_state.concacaf_playoff_qualified=qualified
                st.session_state.concacaf_playoff_repechaje=repechaje
                st.success("✅ Confirmados.")


# ══════════════════════════════════════════════
# COPA ASIA
# ══════════════════════════════════════════════
elif page == "🌏 AFC · Copa Asia":
    conf_header("🌏","COPA ASIA AFC","#9B59B6","6 equipos (🇦🇺 Australia incluida) · 2 grupos de 3 · A1vB2 y B1vA2 → Final")

    tab_setup,tab_groups,tab_ko,tab_result=st.tabs(["⚙️ Config","📊 Grupos","🎯 Eliminatorias","🏆 Resultado"])

    with tab_setup:
        selected=st.multiselect("Elige 6 equipos AFC",AFC_TEAMS,default=st.session_state.as_teams or AFC_TEAMS,max_selections=6)
        if "Australia" not in selected:
            st.warning("⚠️ Australia debe estar incluida (juega en AFC, no OFC).")
        if len(selected)==6:
            col1,col2=st.columns(2)
            with col1:
                st.markdown("**Grupo A**")
                gA=st.multiselect("Grupo A",selected,default=st.session_state.as_groups.get("A",selected[:3]),max_selections=3,key="as_gA")
            with col2:
                st.markdown("**Grupo B**")
                gB=st.multiselect("Grupo B",selected,default=st.session_state.as_groups.get("B",selected[3:]),max_selections=3,key="as_gB")

            if st.button("💾 Guardar grupos Copa Asia"):
                if len(gA)!=3 or len(gB)!=3 or len(set(gA+gB))!=6:
                    st.error("3 por grupo sin duplicados.")
                else:
                    st.session_state.as_teams=selected
                    st.session_state.as_groups={"A":gA,"B":gB}
                    st.session_state.as_matches={**generate_group_matches(gA),**generate_group_matches(gB)}
                    st.success("✅ Guardados.")
                    st.rerun()

    with tab_groups:
        if not st.session_state.as_groups:
            st.info("Configura primero.")
        else:
            for gl in ["A","B"]:
                teams=st.session_state.as_groups.get(gl,[])
                with st.expander(f"Grupo {gl}",expanded=True):
                    col_m,col_t=st.columns([3,2])
                    with col_m:
                        for t1,t2 in combinations(teams,2):
                            key=(t1,t2) if (t1,t2) in st.session_state.as_matches else (t2,t1)
                            res=st.session_state.as_matches.get(key)
                            render_match_result(t1,t2,res)
                            if res is None:
                                r=match_input_form("as",t1,t2,PLAYERS.get(t1,[]),PLAYERS.get(t2,[]),key_suffix=gl)
                                if r:
                                    hg,ag,sh,sa=r
                                    st.session_state.as_matches[key]={"hg":hg,"ag":ag,"scorers_h":sh,"scorers_a":sa}
                                    for s in sh: update_scorer(s,t1,1,"as_")
                                    for s in sa: update_scorer(s,t2,1,"as_")
                                    st.rerun()
                    with col_t:
                        gm={k:v for k,v in st.session_state.as_matches.items()
                            if k[0] in teams and k[1] in teams and v is not None}
                        s=compute_standings(teams,gm)
                        st.session_state.as_standings[gl]=s
                        render_standings(s, highlight=2)

            sA=st.session_state.as_standings.get("A",[])
            sB=st.session_state.as_standings.get("B",[])
            if len(sA)>=2 and len(sB)>=2:
                sf1=(sA[0]["team"],sB[1]["team"])
                sf2=(sB[0]["team"],sA[1]["team"])
                st.markdown(f"**SF1:** {fl(sf1[0])} {sf1[0]} vs {fl(sf1[1])} {sf1[1]}")
                st.markdown(f"**SF2:** {fl(sf2[0])} {sf2[0]} vs {fl(sf2[1])} {sf2[1]}")
                if st.button("➡️ Generar Semis Copa Asia"):
                    st.session_state.as_sf=[sf1,sf2]
                    st.session_state.as_sf_results={}
                    st.rerun()

    with tab_ko:
        if not st.session_state.as_sf:
            st.info("Completa grupos primero.")
        else:
            st.markdown("### ⚔️ Semifinales")
            sf_winners=[]
            for i,(t1,t2) in enumerate(st.session_state.as_sf):
                res=st.session_state.as_sf_results.get(i)
                if res:
                    render_match_result(t1,t2,res)
                    sf_winners.append(res["winner"])
                else:
                    r=knockout_input(f"as_sf_{i}",t1,t2,PLAYERS.get(t1,[]),PLAYERS.get(t2,[]))
                    if r:
                        st.session_state.as_sf_results[i]=r
                        for s in r.get("scorers_h",[]): update_scorer(s,t1,1,"as_")
                        for s in r.get("scorers_a",[]): update_scorer(s,t2,1,"as_")
                        st.rerun()
                    sf_winners.append(None)

            if all(sf_winners) and len(sf_winners)==2:
                if st.session_state.as_final is None:
                    st.session_state.as_final=(sf_winners[0],sf_winners[1])
                st.markdown("### 🏆 FINAL")
                t1,t2=st.session_state.as_final
                res=st.session_state.as_final_result
                if res:
                    render_match_result(t1,t2,res)
                    champ_banner(res["winner"],"CAMPEÓN DE ASIA")
                else:
                    r=knockout_input("as_final",t1,t2,PLAYERS.get(t1,[]),PLAYERS.get(t2,[]))
                    if r:
                        st.session_state.as_final_result=r
                        champ=r["winner"]
                        st.session_state.as_champion=champ
                        for s in r.get("scorers_h",[]): update_scorer(s,t1,1,"as_")
                        for s in r.get("scorers_a",[]): update_scorer(s,t2,1,"as_")
                        runner=t2 if champ==t1 else t1
                        fs=[{"pos":1,"team":champ},{"pos":2,"team":runner}]
                        pos=3
                        placed={champ,runner}
                        for i_,(ta,tb) in enumerate(st.session_state.as_sf):
                            res_=st.session_state.as_sf_results.get(i_)
                            if res_:
                                lsr=tb if res_["winner"]==ta else ta
                                if lsr not in placed:
                                    fs.append({"pos":pos,"team":lsr}); pos+=1; placed.add(lsr)
                        for gl,s_ in st.session_state.as_standings.items():
                            for e in s_:
                                if e["team"] not in placed:
                                    fs.append({"pos":pos,"team":e["team"]}); pos+=1; placed.add(e["team"])
                        st.session_state.as_final_standings=fs
                        update_ranking_from_standings(fs,60,6)
                        if champ not in st.session_state.wc_qualified:
                            st.session_state.wc_qualified.append(champ)
                        st.rerun()

    with tab_result:
        if st.session_state.as_champion:
            champ_banner(st.session_state.as_champion,"CAMPEÓN DE ASIA")
            render_standings(st.session_state.as_final_standings, highlight=1)
        else:
            st.info("Sin resultado aún.")


# ══════════════════════════════════════════════
# AFC PLAYOFFS
# ══════════════════════════════════════════════
elif page == "🔢 AFC · Playoffs":
    conf_header("🔢","AFC · PLAYOFFS","#9B59B6","Puestos 2-5 → todos vs todos · Top 3 → Mundial · 4to → Repechaje")

    if not st.session_state.as_final_standings:
        st.warning("Completa la Copa Asia primero.")
    else:
        pool=[e["team"] for e in st.session_state.as_final_standings[1:5]]
        st.markdown(f"**Equipos:** {' · '.join(fl(t)+' '+t for t in pool)}")

        if not st.session_state.afc_playoff_teams:
            if st.button("▶️ Iniciar playoff AFC"):
                st.session_state.afc_playoff_teams=pool
                st.session_state.afc_playoff_matches=generate_group_matches(pool)
                st.rerun()
        else:
            teams=st.session_state.afc_playoff_teams
            for t1,t2 in combinations(teams,2):
                key=(t1,t2) if (t1,t2) in st.session_state.afc_playoff_matches else (t2,t1)
                res=st.session_state.afc_playoff_matches.get(key)
                render_match_result(t1,t2,res)
                if res is None:
                    r=match_input_form("afcp",t1,t2,PLAYERS.get(t1,[]),PLAYERS.get(t2,[]))
                    if r:
                        hg,ag,sh,sa=r
                        st.session_state.afc_playoff_matches[key]={"hg":hg,"ag":ag,"scorers_h":sh,"scorers_a":sa}
                        st.rerun()

            st.divider()
            played={k:v for k,v in st.session_state.afc_playoff_matches.items() if v is not None}
            standings=compute_standings(teams,played)
            st.session_state.afc_playoff_standings=standings
            render_standings(standings, highlight=3, repechaje_pos=4)

            qualified=[s["team"] for s in standings[:3]]
            repechaje=standings[3]["team"] if len(standings)>3 else None
            st.markdown(f"**✅ Clasificados:** {' · '.join(fl(t)+' '+t for t in qualified)}")
            if repechaje: st.markdown(f"**🔄 Repechaje:** {fl(repechaje)} {repechaje}")

            if st.button("💾 Confirmar AFC"):
                for t in qualified:
                    if t not in st.session_state.wc_qualified:
                        st.session_state.wc_qualified.append(t)
                st.session_state.afc_playoff_qualified=qualified
                st.session_state.afc_playoff_repechaje=repechaje
                st.success("✅ Confirmados.")


# ══════════════════════════════════════════════
# REPECHAJE INTERNACIONAL
# ══════════════════════════════════════════════
elif page == "🔄 Repechaje Internacional":
    conf_header("🔄","REPECHAJE INTERNACIONAL","#FF5722","CONCACAF 3ro vs AFC 4to · CONMEBOL 4to vs Nueva Zelanda")

    cc3=st.session_state.concacaf_playoff_repechaje
    afc4=st.session_state.afc_playoff_repechaje
    cm4=st.session_state.conmebol_playoff_repechaje

    c1,c2,c3=st.columns(3)
    c1.markdown(f"<div class='card card-acc'><b>CONCACAF 3ro</b><br>{'✅ '+fl(cc3)+' '+cc3 if cc3 else '⏳ Pendiente'}</div>",unsafe_allow_html=True)
    c2.markdown(f"<div class='card card-acc'><b>AFC 4to</b><br>{'✅ '+fl(afc4)+' '+afc4 if afc4 else '⏳ Pendiente'}</div>",unsafe_allow_html=True)
    c3.markdown(f"<div class='card card-acc'><b>CONMEBOL 4to</b><br>{'✅ '+fl(cm4)+' '+cm4 if cm4 else '⏳ Pendiente'}</div>",unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### ✏️ Configuración Manual")
    all_pool=ALL_TEAMS+["New Zealand"]
    c1,c2,c3=st.columns(3)
    with c1: m1t1=st.selectbox("CONCACAF 3ro",all_pool,index=all_pool.index(cc3) if cc3 in all_pool else 0)
    with c2: m1t2=st.selectbox("AFC 4to",all_pool,index=all_pool.index(afc4) if afc4 in all_pool else 0)
    with c3: m2t1=st.selectbox("CONMEBOL 4to",all_pool,index=all_pool.index(cm4) if cm4 in all_pool else 0)

    st.markdown("---")
    st.markdown("### ⚽ Partido 1: CONCACAF 3ro vs AFC 4to")
    res1=st.session_state.int_playoff_match1
    if res1:
        render_match_result(m1t1,m1t2,res1)
        st.markdown(f"**Clasificado: {fl(res1['winner'])} {res1['winner']}**")
    else:
        r=knockout_input("int1",m1t1,m1t2,PLAYERS.get(m1t1,[]),PLAYERS.get(m1t2,[]))
        if r:
            st.session_state.int_playoff_match1=r
            st.rerun()

    st.markdown("### ⚽ Partido 2: CONMEBOL 4to vs Nueva Zelanda 🇳🇿")
    res2=st.session_state.int_playoff_match2
    if res2:
        render_match_result(m2t1,"New Zealand",res2)
        st.markdown(f"**Clasificado: {fl(res2['winner'])} {res2['winner']}**")
    else:
        r=knockout_input("int2",m2t1,"New Zealand",PLAYERS.get(m2t1,[]),PLAYERS.get("New Zealand",[]))
        if r:
            st.session_state.int_playoff_match2=r
            st.rerun()

    if res1 and res2:
        st.divider()
        qualified=[res1["winner"],res2["winner"]]
        st.markdown("#### ✅ Clasificados al Mundial via Repechaje")
        for t in qualified:
            st.markdown(f"✅ {fl(t)} **{t}**")
        if st.button("💾 Confirmar repechaje"):
            for t in qualified:
                if t not in st.session_state.wc_qualified:
                    st.session_state.wc_qualified.append(t)
            st.session_state.int_playoff_qualified=qualified
            st.success("✅ Clasificados confirmados.")


# ══════════════════════════════════════════════
# MUNDIAL
# ══════════════════════════════════════════════
elif page == "🏆 Mundial":
    conf_header("🏆","COPA DEL MUNDO","#FFD700","32 equipos · 8 grupos · Modelo FIFA oficial")

    tab_config,tab_groups,tab_ko,tab_result=st.tabs(["⚙️ Config","📊 Grupos","🎯 Eliminatorias","🏆 Resultado"])

    with tab_config:
        st.markdown(f"**Clasificados actuales: {len(st.session_state.wc_qualified)}/32**")
        for t in st.session_state.wc_qualified:
            st.markdown(f"- {fl(t)} {t}")

        st.markdown("---")
        host=st.selectbox("🏟️ País Anfitrión",ALL_TEAMS+["New Zealand"],
                          index=ALL_TEAMS.index(st.session_state.wc_host) if st.session_state.wc_host in ALL_TEAMS else 0)

        st.markdown("---")
        st.markdown("#### Arma los 8 grupos (4 equipos c/u)")
        pool32=list(dict.fromkeys(st.session_state.wc_qualified+[host]))[:32]
        if len(pool32)<32:
            remaining=ALL_TEAMS+["New Zealand"]
            for t in remaining:
                if t not in pool32 and len(pool32)<32:
                    pool32.append(t)

        new_groups={}
        group_labels=["A","B","C","D","E","F","G","H"]
        cols1=st.columns(4); cols2=st.columns(4)
        for i,gl in enumerate(group_labels):
            col=cols1[i] if i<4 else cols2[i-4]
            with col:
                st.markdown(f"**Grupo {gl}**")
                default_g=st.session_state.wc_groups.get(gl,pool32[i*4:(i+1)*4])
                chosen=st.multiselect(f"Grupo {gl}",pool32,default=default_g,max_selections=4,key=f"wc_grp_{gl}")
                new_groups[gl]=chosen

        if st.button("💾 Guardar grupos del Mundial"):
            all_a=sum(new_groups.values(),[])
            if len(all_a)!=len(set(all_a)):
                st.error("Duplicados.")
            elif any(len(v)!=4 for v in new_groups.values()):
                st.error("4 por grupo.")
            else:
                st.session_state.wc_host=host
                st.session_state.wc_groups=new_groups
                all_m={}
                for gl,teams in new_groups.items():
                    all_m.update(generate_group_matches(teams))
                st.session_state.wc_matches=all_m
                st.success("✅ Grupos del Mundial guardados.")
                st.rerun()

    with tab_groups:
        if not st.session_state.wc_groups:
            st.info("Configura los grupos primero.")
        else:
            for gl in ["A","B","C","D","E","F","G","H"]:
                teams=st.session_state.wc_groups.get(gl,[])
                if not teams: continue
                with st.expander(f"Grupo {gl}",expanded=False):
                    col_m,col_t=st.columns([3,2])
                    with col_m:
                        for t1,t2 in combinations(teams,2):
                            key=(t1,t2) if (t1,t2) in st.session_state.wc_matches else (t2,t1)
                            res=st.session_state.wc_matches.get(key)
                            render_match_result(t1,t2,res)
                            if res is None:
                                r=match_input_form("wc",t1,t2,PLAYERS.get(t1,[]),PLAYERS.get(t2,[]),key_suffix=gl)
                                if r:
                                    hg,ag,sh,sa=r
                                    st.session_state.wc_matches[key]={"hg":hg,"ag":ag,"scorers_h":sh,"scorers_a":sa}
                                    for s in sh: update_scorer(s,t1,1,"wc_")
                                    for s in sa: update_scorer(s,t2,1,"wc_")
                                    st.rerun()
                    with col_t:
                        gm={k:v for k,v in st.session_state.wc_matches.items()
                            if k[0] in teams and k[1] in teams and v is not None}
                        s=compute_standings(teams,gm)
                        st.session_state.wc_standings[gl]=s
                        render_standings(s, highlight=2)

            # Generar R16
            st.divider()
            by_slot={}
            for gl in ["A","B","C","D","E","F","G","H"]:
                s=st.session_state.wc_standings.get(gl,[])
                if len(s)>=2:
                    by_slot[f"{gl}1"]=s[0]["team"]
                    by_slot[f"{gl}2"]=s[1]["team"]

            if len(by_slot)==16:
                st.markdown("#### Bracket R16 (Modelo Mundial FIFA)")
                # Modelo oficial: 1A-2B, 1C-2D, 1E-2F, 1G-2H, 1B-2A, 1D-2C, 1F-2E, 1H-2G
                wc_r16=[
                    (by_slot.get("A1","?"),by_slot.get("B2","?")),
                    (by_slot.get("C1","?"),by_slot.get("D2","?")),
                    (by_slot.get("E1","?"),by_slot.get("F2","?")),
                    (by_slot.get("G1","?"),by_slot.get("H2","?")),
                    (by_slot.get("B1","?"),by_slot.get("A2","?")),
                    (by_slot.get("D1","?"),by_slot.get("C2","?")),
                    (by_slot.get("F1","?"),by_slot.get("E2","?")),
                    (by_slot.get("H1","?"),by_slot.get("G2","?")),
                ]
                cols=st.columns(4)
                for i,(t1,t2) in enumerate(wc_r16):
                    with cols[i%4]:
                        st.markdown(f"<div class='card' style='text-align:center;padding:8px;font-size:12px;'>{fl(t1)} {t1}<br><span style='color:var(--muted)'>vs</span><br>{fl(t2)} {t2}</div>",unsafe_allow_html=True)

                if st.button("➡️ Generar R16 del Mundial"):
                    st.session_state.wc_r16=wc_r16
                    st.session_state.wc_r16_results={}
                    st.success("✅ R16 generado.")
                    st.rerun()

    with tab_ko:
        if not st.session_state.wc_r16:
            st.info("Completa los grupos y genera el R16 primero.")
        else:
            st.markdown("### ⚔️ Octavos de Final")
            r16w=[]
            for i,(t1,t2) in enumerate(st.session_state.wc_r16):
                res=st.session_state.wc_r16_results.get(i)
                if res:
                    render_match_result(t1,t2,res); r16w.append(res["winner"])
                else:
                    r=knockout_input(f"wc_r16_{i}",t1,t2,PLAYERS.get(t1,[]),PLAYERS.get(t2,[]))
                    if r:
                        st.session_state.wc_r16_results[i]=r
                        for s in r.get("scorers_h",[]): update_scorer(s,t1,1,"wc_")
                        for s in r.get("scorers_a",[]): update_scorer(s,t2,1,"wc_")
                        st.rerun()
                    r16w.append(None)

            if all(r16w) and len(r16w)==8:
                if not st.session_state.wc_qf:
                    # QF bracket: 1v2, 3v4, 5v6, 7v8 (por cuadro)
                    st.session_state.wc_qf=[(r16w[0],r16w[4]),(r16w[2],r16w[6]),(r16w[1],r16w[5]),(r16w[3],r16w[7])]

                st.markdown("### ⚔️ Cuartos de Final")
                qfw=[]
                for i,(t1,t2) in enumerate(st.session_state.wc_qf):
                    res=st.session_state.wc_qf_results.get(i)
                    if res:
                        render_match_result(t1,t2,res); qfw.append(res["winner"])
                    else:
                        r=knockout_input(f"wc_qf_{i}",t1,t2,PLAYERS.get(t1,[]),PLAYERS.get(t2,[]))
                        if r:
                            st.session_state.wc_qf_results[i]=r
                            for s in r.get("scorers_h",[]): update_scorer(s,t1,1,"wc_")
                            for s in r.get("scorers_a",[]): update_scorer(s,t2,1,"wc_")
                            st.rerun()
                        qfw.append(None)

                if all(qfw) and len(qfw)==4:
                    if not st.session_state.wc_sf:
                        st.session_state.wc_sf=[(qfw[0],qfw[1]),(qfw[2],qfw[3])]

                    st.markdown("### ⚔️ Semifinales")
                    sfw=[]; sfl=[]
                    for i,(t1,t2) in enumerate(st.session_state.wc_sf):
                        res=st.session_state.wc_sf_results.get(i)
                        if res:
                            render_match_result(t1,t2,res)
                            sfw.append(res["winner"]); sfl.append(t2 if res["winner"]==t1 else t1)
                        else:
                            r=knockout_input(f"wc_sf_{i}",t1,t2,PLAYERS.get(t1,[]),PLAYERS.get(t2,[]))
                            if r:
                                st.session_state.wc_sf_results[i]=r
                                for s in r.get("scorers_h",[]): update_scorer(s,t1,1,"wc_")
                                for s in r.get("scorers_a",[]): update_scorer(s,t2,1,"wc_")
                                st.rerun()
                            sfw.append(None)

                    # 3rd place + Final
                    if all(sfw) and len(sfw)==2:
                        # 3er puesto
                        st.markdown("### 🥉 Tercer Puesto")
                        if len(sfl)==2:
                            t3a,t3b=sfl[0],sfl[1]
                            res3=st.session_state.wc_third_result
                            if res3:
                                render_match_result(t3a,t3b,res3)
                                st.markdown(f"🥉 **{fl(res3['winner'])} {res3['winner']}**")
                            else:
                                r=knockout_input("wc_3rd",t3a,t3b,PLAYERS.get(t3a,[]),PLAYERS.get(t3b,[]))
                                if r:
                                    st.session_state.wc_third=(t3a,t3b)
                                    st.session_state.wc_third_result=r
                                    st.rerun()

                        st.markdown("### 🏆 FINAL MUNDIAL")
                        if st.session_state.wc_final is None:
                            st.session_state.wc_final=(sfw[0],sfw[1])
                        t1,t2=st.session_state.wc_final
                        resf=st.session_state.wc_final_result
                        if resf:
                            render_match_result(t1,t2,resf)
                            champ_banner(resf["winner"],"CAMPEÓN DEL MUNDO 🌍")
                        else:
                            r=knockout_input("wc_final",t1,t2,PLAYERS.get(t1,[]),PLAYERS.get(t2,[]))
                            if r:
                                st.session_state.wc_final_result=r
                                champ=r["winner"]
                                st.session_state.wc_champion=champ
                                for s in r.get("scorers_h",[]): update_scorer(s,t1,1,"wc_")
                                for s in r.get("scorers_a",[]): update_scorer(s,t2,1,"wc_")
                                # Update ranking
                                runner=t2 if champ==t1 else t1
                                fs_wc=[{"pos":1,"team":champ},{"pos":2,"team":runner}]
                                update_ranking_from_standings(fs_wc,200,10)
                                st.rerun()

    with tab_result:
        if st.session_state.wc_champion:
            champ_banner(st.session_state.wc_champion,"🌍 CAMPEÓN DEL MUNDO")
            if st.session_state.wc_final_result:
                t1,t2=st.session_state.wc_final
                r=st.session_state.wc_final_result
                render_match_result(t1,t2,r)
        else:
            st.info("El Mundial aún no tiene campeón.")


# ══════════════════════════════════════════════
# RANKING FIFA
# ══════════════════════════════════════════════
elif page == "📊 Ranking FIFA":
    conf_header("📊","RANKING FIFA","#00E5A0","Se actualiza con cada torneo · Persiste entre temporadas")

    ranking=st.session_state.fifa_ranking
    sorted_r=sorted(ranking.items(),key=lambda x:x[1],reverse=True)

    c1,c2,c3=st.columns(3)
    for col,(team,pts),medal in zip([c1,c2,c3],sorted_r[:3],["🥇","🥈","🥉"]):
        with col:
            st.markdown(f"<div class='card card-gold' style='text-align:center;padding:20px;'><div style='font-size:36px;'>{medal}</div><div style='font-size:32px;'>{fl(team)}</div><div style='font-family:Bebas Neue;font-size:20px;'>{team}</div><div style='color:var(--g);font-size:22px;font-weight:700;'>{pts}</div></div>",unsafe_allow_html=True)

    st.markdown("<br>",unsafe_allow_html=True)
    conf_teams={"UEFA":UEFA_TEAMS,"CONMEBOL":CONMEBOL_TEAMS,"CAF":CAF_TEAMS,"CONCACAF":CONCACAF_TEAMS,"AFC":AFC_TEAMS}
    filt=st.selectbox("Filtrar",["Todas","UEFA","CONMEBOL","CAF","CONCACAF","AFC"])

    rows=[]
    for pos,(t,pts) in enumerate(sorted_r,1):
        if filt!="Todas" and t not in conf_teams.get(filt,[]):
            continue
        conf="—"
        for c,tl in conf_teams.items():
            if t in tl: conf=c; break
        rows.append({"Pos":pos,"Equipo":f"{fl(t)} {t}","Conf":conf,"Puntos":pts})
    st.dataframe(pd.DataFrame(rows),hide_index=True,use_container_width=True)

    if st.button("🔄 Resetear ranking inicial"):
        st.session_state.fifa_ranking=dict(INITIAL_FIFA_RANKING)
        st.success("✅ Reseteado.")
        st.rerun()


# ══════════════════════════════════════════════
# GOLEADORES
# ══════════════════════════════════════════════
elif page == "⚽ Goleadores":
    conf_header("⚽","TABLA DE GOLEADORES","#FF5722","Registrados durante todos los torneos")

    scorers=st.session_state.top_scorers
    if not scorers:
        st.info("No hay goles registrados aún.")
    else:
        TOUR_PREFIX={"euro_":"🌍 Eurocopa","ca_":"🌎 Copa América","af_":"🌍 Copa África",
                     "co_":"🌎 Copa Oro","as_":"🌏 Copa Asia","wc_":"🏆 Mundial"}

        filt_tour=st.selectbox("Torneo",["Todos"]+list(TOUR_PREFIX.values()))

        rows=[]
        for key,goals in sorted(scorers.items(),key=lambda x:x[1],reverse=True):
            parts=key.split("|")
            if len(parts)!=2: continue
            raw_key,team=parts[0],parts[1]
            tour="—"; player=raw_key
            for pref,name in TOUR_PREFIX.items():
                if raw_key.startswith(pref):
                    tour=name; player=raw_key[len(pref):]
                    break
            if filt_tour!="Todos" and tour!=filt_tour: continue
            rows.append({"Goles":goals,"Jugador":player,"Selección":f"{fl(team)} {team}","Torneo":tour})

        if rows:
            df=pd.DataFrame(rows)
            df.insert(0,"Pos",range(1,len(df)+1))
            st.dataframe(df,hide_index=True,use_container_width=True)


# ══════════════════════════════════════════════
# PLANTILLAS
# ══════════════════════════════════════════════
elif page == "👥 Plantillas":
    conf_header("👥","PLANTILLAS","#00E5A0","Jugadores por selección con link a SoFifa")

    conf_opts={"UEFA 🌍":UEFA_TEAMS,"CONMEBOL 🌎":CONMEBOL_TEAMS,"CAF 🌍":CAF_TEAMS,
               "CONCACAF 🌎":CONCACAF_TEAMS,"AFC 🌏":AFC_TEAMS,"Repechaje 🔄":["New Zealand"]}
    c1,c2=st.columns(2)
    with c1: conf_sel=st.selectbox("Confederación",list(conf_opts.keys()))
    with c2: team_sel=st.selectbox("Selección",conf_opts[conf_sel])

    st.markdown(f"""
    <div class='card card-g' style='text-align:center;padding:20px;'>
      <div style='font-size:56px;'>{fl(team_sel)}</div>
      <div style='font-family:Bebas Neue;font-size:28px;letter-spacing:3px;'>{team_sel}</div>
      <div style='color:var(--muted);'>FIFA Ranking: <b style='color:var(--g);'>{st.session_state.fifa_ranking.get(team_sel,"—")}</b> pts</div>
    </div>""",unsafe_allow_html=True)

    players=PLAYERS.get(team_sel,[])
    if not players:
        st.info("Sin datos de jugadores.")
    else:
        pos_filt=st.selectbox("Posición",["Todas","GK","DF","MF","FW"])
        filtered=[p for p in players if pos_filt=="Todas" or p["position"]==pos_filt]

        cols_per_row=4
        for i in range(0,len(filtered),cols_per_row):
            cols=st.columns(cols_per_row)
            for j,player in enumerate(filtered[i:i+cols_per_row]):
                with cols[j]:
                    name=player["name"]; pos=player["position"]
                    pc=POS_COLOR.get(pos,"#666")
                    sofifa_url=f"https://sofifa.com/players?keyword={name.replace(' ','+')}"
                    st.markdown(f"""
                    <div class='card' style='text-align:center;padding:12px;'>
                      <div style='font-size:28px;'>{fl(team_sel)}</div>
                      <div style='background:{pc};color:#fff;border-radius:3px;font-size:10px;padding:1px 8px;display:inline-block;margin:4px 0;'>{pos}</div>
                      <div style='font-weight:700;font-size:13px;'>{name}</div>
                      <a href='{sofifa_url}' target='_blank' style='color:var(--g);font-size:11px;'>🔗 SoFifa</a>
                    </div>""",unsafe_allow_html=True)
