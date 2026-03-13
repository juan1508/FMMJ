"""
state.py - Lógica de estado y helpers del simulador FMMJ Nations
"""
import streamlit as st
from data import INITIAL_FIFA_RANKING, FLAG_MAP


def flag_img(team, size="20x15"):
    """Devuelve una etiqueta <img> con la bandera del país vía flagcdn.com"""
    code = FLAG_MAP.get(team, "")
    if not code:
        return "🏳️"
    return f'<img src="https://flagcdn.com/{size}/{code}.png" style="vertical-align:middle;border-radius:2px;margin-right:4px;" />'


def flag_url(team, size="20x15"):
    """Devuelve solo la URL de la bandera"""
    code = FLAG_MAP.get(team, "")
    if not code:
        return ""
    return f"https://flagcdn.com/{size}/{code}.png"


def flag(team):
    """Compatibilidad: devuelve img HTML inline"""
    return flag_img(team, "20x15")


def init_state():
    defaults = {
        "fifa_ranking": dict(INITIAL_FIFA_RANKING),
        # ---- EUROCOPA ----
        "euro_teams": [],
        "euro_groups": {},
        "euro_matches": {},
        "euro_standings": {},
        "euro_r16": [],
        "euro_r16_results": {},
        "euro_qf": [],
        "euro_qf_results": {},
        "euro_sf": [],
        "euro_sf_results": {},
        "euro_final": None,
        "euro_final_result": None,
        "euro_champion": None,
        "euro_final_standings": [],
        # ---- COPA AMERICA ----
        "ca_teams": [],
        "ca_groups": {},
        "ca_matches": {},
        "ca_standings": {},
        "ca_r16": [],
        "ca_r16_results": {},
        "ca_qf": [],
        "ca_qf_results": {},
        "ca_sf": [],
        "ca_sf_results": {},
        "ca_final": None,
        "ca_final_result": None,
        "ca_champion": None,
        "ca_final_standings": [],
        # ---- COPA AFRICA ----
        "af_teams": [],
        "af_groups": {},
        "af_matches": {},
        "af_standings": {},
        "af_sf": [],
        "af_sf_results": {},
        "af_final": None,
        "af_final_result": None,
        "af_champion": None,
        "af_final_standings": [],
        # ---- COPA ORO ----
        "co_teams": [],
        "co_groups": {},
        "co_matches": {},
        "co_standings": {},
        "co_sf": [],
        "co_sf_results": {},
        "co_final": None,
        "co_final_result": None,
        "co_champion": None,
        "co_final_standings": [],
        # ---- COPA ASIA ----
        "as_teams": [],
        "as_groups": {},
        "as_matches": {},
        "as_standings": {},
        "as_sf": [],
        "as_sf_results": {},
        "as_final": None,
        "as_final_result": None,
        "as_champion": None,
        "as_final_standings": [],
        # ---- ELIMINATORIAS ----
        "euro_playoff_groups": {},
        "euro_playoff_matches": {},
        "euro_playoff_standings": {},
        "euro_playoff_qualified": [],
        "conmebol_playoff_teams": [],
        "conmebol_playoff_matches": {},
        "conmebol_playoff_standings": [],
        "conmebol_playoff_qualified": [],
        "conmebol_playoff_repechaje": None,
        "caf_playoff_teams": [],
        "caf_playoff_matches": {},
        "caf_playoff_standings": [],
        "caf_playoff_qualified": [],
        "concacaf_playoff_teams": [],
        "concacaf_playoff_matches": {},
        "concacaf_playoff_standings": [],
        "concacaf_playoff_qualified": [],
        "concacaf_playoff_repechaje": None,
        "afc_playoff_teams": [],
        "afc_playoff_matches": {},
        "afc_playoff_standings": [],
        "afc_playoff_qualified": [],
        "afc_playoff_repechaje": None,
        # ---- REPECHAJE INTERNACIONAL ----
        "int_playoff_match1": None,
        "int_playoff_match2": None,
        "int_playoff_qualified": [],
        # ---- MUNDIAL ----
        "wc_host": None,
        "wc_qualified": [],
        "wc_groups": {},
        "wc_matches": {},
        "wc_standings": {},
        "wc_r16": [],
        "wc_r16_results": {},
        "wc_qf": [],
        "wc_qf_results": {},
        "wc_sf": [],
        "wc_sf_results": {},
        "wc_third": None,
        "wc_third_result": None,
        "wc_final": None,
        "wc_final_result": None,
        "wc_champion": None,
        # ---- META ----
        "season": 1,
        "season_history": [],
        "active_page": "🏠 Inicio",
        "top_scorers": {},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ============================================================
# CÁLCULO DE TABLA DE POSICIONES
# ============================================================

def compute_standings(teams, matches):
    stats = {t: {"pts":0,"played":0,"w":0,"d":0,"l":0,"gf":0,"ga":0,"gd":0} for t in teams}

    for (t1, t2), res in matches.items():
        if res is None:
            continue
        hg = res.get("hg", 0)
        ag = res.get("ag", 0)
        if t1 not in stats or t2 not in stats:
            continue
        stats[t1]["played"] += 1
        stats[t2]["played"] += 1
        stats[t1]["gf"] += hg; stats[t1]["ga"] += ag
        stats[t2]["gf"] += ag; stats[t2]["ga"] += hg
        stats[t1]["gd"] = stats[t1]["gf"] - stats[t1]["ga"]
        stats[t2]["gd"] = stats[t2]["gf"] - stats[t2]["ga"]
        if hg > ag:
            stats[t1]["pts"] += 3; stats[t1]["w"] += 1; stats[t2]["l"] += 1
        elif ag > hg:
            stats[t2]["pts"] += 3; stats[t2]["w"] += 1; stats[t1]["l"] += 1
        else:
            stats[t1]["pts"] += 1; stats[t2]["pts"] += 1
            stats[t1]["d"] += 1;   stats[t2]["d"] += 1

    sorted_teams = sorted(
        teams,
        key=lambda t: (stats[t]["pts"], stats[t]["gd"], stats[t]["gf"], t),
        reverse=True
    )
    return [{"pos": i+1, "team": t, **stats[t]} for i, t in enumerate(sorted_teams)]


def generate_group_matches(teams):
    matches = {}
    for i in range(len(teams)):
        for j in range(i+1, len(teams)):
            matches[(teams[i], teams[j])] = None
    return matches


def get_match_result(matches, t1, t2):
    if (t1, t2) in matches:
        return matches[(t1, t2)]
    if (t2, t1) in matches:
        r = matches[(t2, t1)]
        if r is None:
            return None
        return {"hg": r["ag"], "ag": r["hg"],
                "scorers_h": r.get("scorers_a", []),
                "scorers_a": r.get("scorers_h", [])}
    return None


def update_scorer(player, team, goals, prefix=""):
    key = f"{prefix}{player}|{team}"
    sc = st.session_state.top_scorers
    sc[key] = sc.get(key, 0) + goals
    st.session_state.top_scorers = sc


def update_ranking_from_standings(final_standings, bonus_champion=60, bonus_step=5):
    ranking = st.session_state.fifa_ranking
    n = len(final_standings)
    for entry in final_standings:
        pos  = entry.get("pos", n)
        team = entry.get("team", "")
        if not team:
            continue
        bonus = max(0, bonus_champion - (pos - 1) * bonus_step)
        ranking[team] = ranking.get(team, 1000) + bonus
    st.session_state.fifa_ranking = ranking


def reset_tournament_state(prefix_keys):
    for k in prefix_keys:
        if k in ["euro_champion","ca_champion","af_champion","co_champion","as_champion","wc_champion",
                 "euro_final","ca_final","af_final","co_final","as_final","wc_final",
                 "euro_final_result","ca_final_result","af_final_result","co_final_result",
                 "as_final_result","wc_final_result","wc_host",
                 "conmebol_playoff_repechaje","concacaf_playoff_repechaje","afc_playoff_repechaje",
                 "wc_third","wc_third_result"]:
            st.session_state[k] = None
        elif isinstance(st.session_state.get(k), list):
            st.session_state[k] = []
        elif isinstance(st.session_state.get(k), dict):
            st.session_state[k] = {}
        else:
            st.session_state[k] = None
