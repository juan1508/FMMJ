"""
state.py - Lógica de estado y helpers del simulador MMJ World Cup
"""
import streamlit as st
from data import INITIAL_FIFA_RANKING, FLAG_MAP


def flag(team):
    return FLAG_MAP.get(team, "🏳️")


def init_state():
    defaults = {
        "fifa_ranking": dict(INITIAL_FIFA_RANKING),
        # ---- EUROCOPA ----
        "euro_teams": [],          # 24 equipos seleccionados
        "euro_groups": {},         # {A:[t1,t2,t3,t4], B:...}  6 grupos
        "euro_matches": {},        # {(t1,t2): {hg,ag,scorers_h,scorers_a}}
        "euro_standings": {},      # calculado
        "euro_r16": [],            # 16 partidos R16
        "euro_r16_results": {},
        "euro_qf": [],
        "euro_qf_results": {},
        "euro_sf": [],
        "euro_sf_results": {},
        "euro_final": None,
        "euro_final_result": None,
        "euro_champion": None,
        "euro_final_standings": [], # clasificación final ordenada
        # ---- COPA AMERICA ----
        "ca_teams": [],            # 16 equipos (10 CONMEBOL + 6 invitados)
        "ca_groups": {},           # 4 grupos de 4
        "ca_matches": {},
        "ca_standings": {},
        "ca_r16": [],              # 8 partidos según bracket definido
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
        "af_teams": [],            # 10 equipos, 2 grupos de 5
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
        "co_teams": [],            # 6 equipos
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
        "int_playoff_match1": None,  # {t1, t2, result}
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
        # Goleadores globales
        "top_scorers": {},  # {player_team_key: goals}
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ============================================================
# CÁLCULO DE TABLA DE POSICIONES
# ============================================================

def compute_standings(teams, matches):
    """
    matches: dict con key (t1,t2) o (t2,t1), valor {hg, ag}
    Retorna lista ordenada de dicts con stats.
    """
    stats = {t: {"pts":0,"played":0,"w":0,"d":0,"l":0,"gf":0,"ga":0,"gd":0,"results":[]} for t in teams}

    for (t1, t2), res in matches.items():
        if res is None:
            continue
        hg = res.get("hg", 0)
        ag = res.get("ag", 0)
        if t1 not in stats or t2 not in stats:
            continue
        stats[t1]["played"] += 1
        stats[t2]["played"] += 1
        stats[t1]["gf"] += hg
        stats[t1]["ga"] += ag
        stats[t2]["gf"] += ag
        stats[t2]["ga"] += hg
        stats[t1]["gd"] = stats[t1]["gf"] - stats[t1]["ga"]
        stats[t2]["gd"] = stats[t2]["gf"] - stats[t2]["ga"]
        if hg > ag:
            stats[t1]["pts"] += 3
            stats[t1]["w"] += 1
            stats[t2]["l"] += 1
            stats[t1]["results"].append("W")
            stats[t2]["results"].append("L")
        elif ag > hg:
            stats[t2]["pts"] += 3
            stats[t2]["w"] += 1
            stats[t1]["l"] += 1
            stats[t2]["results"].append("W")
            stats[t1]["results"].append("L")
        else:
            stats[t1]["pts"] += 1
            stats[t2]["pts"] += 1
            stats[t1]["d"] += 1
            stats[t2]["d"] += 1
            stats[t1]["results"].append("D")
            stats[t2]["results"].append("D")

    sorted_teams = sorted(
        teams,
        key=lambda t: (stats[t]["pts"], stats[t]["gd"], stats[t]["gf"], t),
        reverse=True
    )
    result = []
    for pos, team in enumerate(sorted_teams, 1):
        result.append({"pos": pos, "team": team, **stats[team]})
    return result


def generate_group_matches(teams):
    """Genera todos los pares de partidos para un grupo (todos vs todos 1 vuelta)."""
    matches = {}
    for i in range(len(teams)):
        for j in range(i+1, len(teams)):
            matches[(teams[i], teams[j])] = None
    return matches


def get_match_result(matches, t1, t2):
    """Busca resultado del partido entre t1 y t2 en cualquier orden."""
    if (t1, t2) in matches:
        return matches[(t1, t2)]
    if (t2, t1) in matches:
        r = matches[(t2, t1)]
        if r is None:
            return None
        # flip
        return {"hg": r["ag"], "ag": r["hg"],
                "scorers_h": r.get("scorers_a", []),
                "scorers_a": r.get("scorers_h", [])}
    return None


def update_scorer(player, team, goals, prefix=""):
    """Añade goles al registro global de goleadores."""
    key = f"{prefix}{player}|{team}"
    sc = st.session_state.top_scorers
    sc[key] = sc.get(key, 0) + goals
    st.session_state.top_scorers = sc


def update_ranking_from_standings(final_standings, bonus_champion=60, bonus_step=5):
    """Actualiza ranking FIFA según posición final en torneo."""
    ranking = st.session_state.fifa_ranking
    n = len(final_standings)
    for entry in final_standings:
        pos = entry.get("pos", n)
        team = entry.get("team", "")
        if not team:
            continue
        bonus = max(0, bonus_champion - (pos - 1) * bonus_step)
        ranking[team] = ranking.get(team, 1000) + bonus
    st.session_state.fifa_ranking = ranking


def reset_tournament_state(prefix_keys):
    """Resetea las claves de estado de un torneo."""
    for k in prefix_keys:
        default_val = [] if k.endswith(("teams","standings","qualified","r16","qf","sf","playoff_qualified")) else {}
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
