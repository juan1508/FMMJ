"""
state.py - Gestión de estado de la aplicación usando st.session_state
"""
import streamlit as st
import random
from data import (
    UEFA_TEAMS, CONMEBOL_TEAMS, CAF_TEAMS, CONCACAF_TEAMS, AFC_TEAMS,
    INITIAL_FIFA_RANKING, PLAYERS
)


def init_state():
    """Inicializa el estado global si no existe."""
    defaults = {
        # Ranking FIFA persistente
        "fifa_ranking": dict(INITIAL_FIFA_RANKING),

        # Torneos de confederación
        "euro_standings": None,
        "copa_america_standings": None,
        "copa_africa_standings": None,
        "copa_oro_standings": None,
        "copa_asia_standings": None,

        # Eliminatorias
        "euro_playoff_groups": None,
        "euro_playoff_standings": None,
        "conmebol_playoff": None,
        "caf_playoff": None,
        "concacaf_playoff": None,
        "afc_playoff": None,

        # Repechaje internacional
        "int_playoff": None,

        # Clasificados al mundial
        "world_cup_qualified": [],

        # Mundial
        "world_cup_host": None,
        "world_cup_groups": None,
        "world_cup_results": None,
        "world_cup_bracket": None,
        "world_cup_champion": None,

        # Historial de temporadas
        "season": 1,
        "season_history": [],

        # UI
        "active_page": "🏠 Inicio",
        "active_confederation": "UEFA",
        "tournament_phase": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ============================================================
# LÓGICA DE SIMULACIÓN
# ============================================================

def team_strength(team: str) -> float:
    """Retorna la fuerza de un equipo basada en el ranking FIFA."""
    ranking = st.session_state.fifa_ranking
    base = ranking.get(team, 1000)
    return base


def simulate_match(home: str, away: str, neutral: bool = True) -> tuple:
    """
    Simula un partido entre dos equipos.
    Retorna (goles_local, goles_visitante).
    """
    h_strength = team_strength(home)
    a_strength = team_strength(away)
    total = h_strength + a_strength

    h_win_prob = h_strength / total
    if not neutral:
        h_win_prob = min(h_win_prob * 1.1, 0.85)

    r = random.random()
    if r < h_win_prob * 0.5:  # Home win
        hg = random.randint(1, 4)
        ag = random.randint(0, hg - 1)
    elif r > 1 - (1 - h_win_prob) * 0.5:  # Away win
        ag = random.randint(1, 4)
        hg = random.randint(0, ag - 1)
    else:  # Draw
        g = random.randint(0, 3)
        hg = ag = g

    return hg, ag


def simulate_tournament(teams: list, neutral: bool = True) -> list:
    """
    Simula un torneo todos contra todos (una vuelta).
    Retorna standings ordenados.
    """
    # standings: {team: {pts, gf, ga, gd, w, d, l, played}}
    standings = {t: {"pts": 0, "gf": 0, "ga": 0, "gd": 0,
                     "w": 0, "d": 0, "l": 0, "played": 0,
                     "results": []} for t in teams}

    matches = []
    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            home = teams[i]
            away = teams[j]
            hg, ag = simulate_match(home, away, neutral)
            matches.append({"home": home, "away": away, "hg": hg, "ag": ag})

            # Update standings
            standings[home]["gf"] += hg
            standings[home]["ga"] += ag
            standings[away]["gf"] += ag
            standings[away]["ga"] += hg
            standings[home]["played"] += 1
            standings[away]["played"] += 1

            if hg > ag:
                standings[home]["pts"] += 3
                standings[home]["w"] += 1
                standings[away]["l"] += 1
                standings[home]["results"].append("W")
                standings[away]["results"].append("L")
            elif hg < ag:
                standings[away]["pts"] += 3
                standings[away]["w"] += 1
                standings[home]["l"] += 1
                standings[home]["results"].append("L")
                standings[away]["results"].append("W")
            else:
                standings[home]["pts"] += 1
                standings[away]["pts"] += 1
                standings[home]["d"] += 1
                standings[away]["d"] += 1
                standings[home]["results"].append("D")
                standings[away]["results"].append("D")

    # Calculate GD
    for t in standings:
        standings[t]["gd"] = standings[t]["gf"] - standings[t]["ga"]

    # Sort
    sorted_teams = sorted(
        standings.keys(),
        key=lambda t: (standings[t]["pts"], standings[t]["gd"], standings[t]["gf"]),
        reverse=True
    )

    result = []
    for pos, team in enumerate(sorted_teams, 1):
        result.append({
            "pos": pos,
            "team": team,
            **standings[team]
        })

    return result, matches


def simulate_knockout(team1: str, team2: str) -> str:
    """Simula un partido de eliminación directa. Retorna ganador."""
    hg, ag = simulate_match(team1, team2)
    if hg > ag:
        return team1
    elif ag > hg:
        return team2
    else:
        # Penaltis: 60/40 al equipo más fuerte
        if team_strength(team1) >= team_strength(team2):
            return team1 if random.random() < 0.55 else team2
        else:
            return team2 if random.random() < 0.55 else team1


# ============================================================
# EUROCOPA - UEFA (24 equipos)
# ============================================================

def simulate_euro(teams=None):
    """Simula la Eurocopa con 24 equipos en fase de grupos + eliminatorias."""
    if teams is None:
        teams = UEFA_TEAMS[:24]

    # 6 grupos de 4 equipos - top 2 pasan + 4 mejores terceros
    random.shuffle(teams)
    groups = {}
    group_labels = ["A", "B", "C", "D", "E", "F"]
    for i, label in enumerate(group_labels):
        groups[label] = teams[i*4:(i+1)*4]

    all_group_standings = {}
    all_matches = []

    for label, group_teams in groups.items():
        standings, matches = simulate_tournament(group_teams)
        all_group_standings[label] = standings
        all_matches.extend(matches)

    # Clasificados: top 2 de cada grupo + 4 mejores 3ros
    qualified_r16 = []
    third_places = []

    for label, standings in all_group_standings.items():
        qualified_r16.append(standings[0]["team"])
        qualified_r16.append(standings[1]["team"])
        third_places.append(standings[2])

    # 4 mejores terceros
    third_places.sort(key=lambda x: (x["pts"], x["gd"], x["gf"]), reverse=True)
    qualified_r16.extend([t["team"] for t in third_places[:4]])

    # Fase eliminatoria
    bracket_results = {"R16": [], "QF": [], "SF": [], "Final": None, "Champion": None}

    # R16 (16 equipos)
    random.shuffle(qualified_r16)
    qf_teams = []
    for i in range(0, 16, 2):
        winner = simulate_knockout(qualified_r16[i], qualified_r16[i+1])
        bracket_results["R16"].append({
            "t1": qualified_r16[i], "t2": qualified_r16[i+1], "winner": winner
        })
        qf_teams.append(winner)

    # QF
    sf_teams = []
    for i in range(0, 8, 2):
        winner = simulate_knockout(qf_teams[i], qf_teams[i+1])
        bracket_results["QF"].append({
            "t1": qf_teams[i], "t2": qf_teams[i+1], "winner": winner
        })
        sf_teams.append(winner)

    # SF
    final_teams = []
    for i in range(0, 4, 2):
        winner = simulate_knockout(sf_teams[i], sf_teams[i+1])
        bracket_results["SF"].append({
            "t1": sf_teams[i], "t2": sf_teams[i+1], "winner": winner
        })
        final_teams.append(winner)

    # Final
    champion = simulate_knockout(final_teams[0], final_teams[1])
    runner_up = final_teams[1] if champion == final_teams[0] else final_teams[0]
    bracket_results["Final"] = {"t1": final_teams[0], "t2": final_teams[1], "winner": champion}
    bracket_results["Champion"] = champion

    # Ordenar todos los equipos por desempeño (aproximado)
    # Champion=1, Runner-up=2, SF=3-4, QF=5-8, R16=9-16, Groups=17-24
    euro_final_standings = []
    placed = set()

    euro_final_standings.append({"pos": 1, "team": champion})
    placed.add(champion)
    euro_final_standings.append({"pos": 2, "team": runner_up})
    placed.add(runner_up)

    pos = 3
    for m in bracket_results["SF"]:
        loser = m["t1"] if m["winner"] != m["t1"] else m["t2"]
        if loser not in placed:
            euro_final_standings.append({"pos": pos, "team": loser})
            placed.add(loser)
            pos += 1

    for m in bracket_results["QF"]:
        loser = m["t1"] if m["winner"] != m["t1"] else m["t2"]
        if loser not in placed:
            euro_final_standings.append({"pos": pos, "team": loser})
            placed.add(loser)
            pos += 1

    for m in bracket_results["R16"]:
        loser = m["t1"] if m["winner"] != m["t1"] else m["t2"]
        if loser not in placed:
            euro_final_standings.append({"pos": pos, "team": loser})
            placed.add(loser)
            pos += 1

    for t in teams:
        if t not in placed:
            euro_final_standings.append({"pos": pos, "team": t})
            placed.add(t)
            pos += 1

    return {
        "group_standings": all_group_standings,
        "bracket": bracket_results,
        "final_standings": euro_final_standings,
        "champion": champion,
        "runner_up": runner_up,
        "matches": all_matches,
    }


def simulate_euro_playoffs(euro_standings: list, host: str = None):
    """
    Simula las eliminatorias UEFA para el mundial.
    Puestos 6-21 → 4 grupos de 4 → top 2 clasifican.
    """
    # Puestos 6 al 21 (índices 5 a 20)
    playoff_teams = [e["team"] for e in euro_standings[5:21]]

    # Distribuir en grupos: 6→A, 7→B, 8→C, 9→D, 10→A...
    groups = {"A": [], "B": [], "C": [], "D": []}
    group_order = ["A", "B", "C", "D"]
    for i, team in enumerate(playoff_teams):
        groups[group_order[i % 4]].append(team)

    # Simular cada grupo (todos vs todos, 1 vuelta = 3 partidos c/u)
    playoff_standings = {}
    for g_label, g_teams in groups.items():
        standings, _ = simulate_tournament(g_teams)
        playoff_standings[g_label] = standings

    # Top 2 de cada grupo clasifican
    qualified = []
    for g_label, standings in playoff_standings.items():
        for entry in standings[:2]:
            qualified.append(entry["team"])

    return playoff_standings, qualified


# ============================================================
# COPA AMÉRICA - CONMEBOL (10 equipos)
# ============================================================

def simulate_copa_america(teams=None):
    """Simula la Copa América (10 equipos, todos vs todos)."""
    if teams is None:
        teams = CONMEBOL_TEAMS

    # Fase de grupos: 2 grupos de 5
    random.shuffle(teams)
    group_a = teams[:5]
    group_b = teams[5:]

    standings_a, matches_a = simulate_tournament(group_a)
    standings_b, matches_b = simulate_tournament(group_b)

    # SF: 1A vs 2B, 1B vs 2A
    sf1_winner = simulate_knockout(standings_a[0]["team"], standings_b[1]["team"])
    sf2_winner = simulate_knockout(standings_b[0]["team"], standings_a[1]["team"])

    # 3rd place
    sf1_loser = standings_a[0]["team"] if sf1_winner == standings_b[1]["team"] else standings_b[1]["team"]
    sf2_loser = standings_b[0]["team"] if sf2_winner == standings_a[1]["team"] else standings_a[1]["team"]
    third = simulate_knockout(sf1_loser, sf2_loser)

    # Final
    champion = simulate_knockout(sf1_winner, sf2_winner)
    runner_up = sf2_winner if champion == sf1_winner else sf1_winner

    # Build final standings
    final_standings = []
    placed = set()
    final_standings.append({"pos": 1, "team": champion})
    placed.add(champion)
    final_standings.append({"pos": 2, "team": runner_up})
    placed.add(runner_up)
    final_standings.append({"pos": 3, "team": third})
    placed.add(third)
    fourth = sf2_loser if third == sf1_loser else sf1_loser
    final_standings.append({"pos": 4, "team": fourth})
    placed.add(fourth)

    pos = 5
    # Remaining by group performance
    for s in standings_a + standings_b:
        if s["team"] not in placed:
            final_standings.append({"pos": pos, "team": s["team"]})
            placed.add(s["team"])
            pos += 1

    return {
        "group_a": standings_a,
        "group_b": standings_b,
        "final_standings": final_standings,
        "champion": champion,
        "runner_up": runner_up,
        "bracket": {
            "SF": [
                {"t1": standings_a[0]["team"], "t2": standings_b[1]["team"], "winner": sf1_winner},
                {"t1": standings_b[0]["team"], "t2": standings_a[1]["team"], "winner": sf2_winner},
            ],
            "Final": {"t1": sf1_winner, "t2": sf2_winner, "winner": champion},
            "Champion": champion,
        }
    }


def simulate_conmebol_playoffs(copa_standings: list):
    """Puestos 2-7 juegan todos vs todos. Top 3 → Mundial, 4to → Repechaje."""
    playoff_teams = [e["team"] for e in copa_standings[1:7]]
    standings, _ = simulate_tournament(playoff_teams)

    qualified = [s["team"] for s in standings[:3]]
    repechaje = standings[3]["team"] if len(standings) > 3 else None

    return standings, qualified, repechaje


# ============================================================
# COPA ÁFRICA - CAF (10 equipos)
# ============================================================

def simulate_copa_africa(teams=None):
    """Simula la Copa África (10 equipos)."""
    if teams is None:
        teams = CAF_TEAMS

    # 2 grupos de 5
    random.shuffle(teams)
    group_a = teams[:5]
    group_b = teams[5:]

    standings_a, _ = simulate_tournament(group_a)
    standings_b, _ = simulate_tournament(group_b)

    sf1_winner = simulate_knockout(standings_a[0]["team"], standings_b[1]["team"])
    sf2_winner = simulate_knockout(standings_b[0]["team"], standings_a[1]["team"])

    sf1_loser = standings_a[0]["team"] if sf1_winner == standings_b[1]["team"] else standings_b[1]["team"]
    sf2_loser = standings_b[0]["team"] if sf2_winner == standings_a[1]["team"] else standings_a[1]["team"]

    champion = simulate_knockout(sf1_winner, sf2_winner)
    runner_up = sf2_winner if champion == sf1_winner else sf1_winner
    third = simulate_knockout(sf1_loser, sf2_loser)
    fourth = sf2_loser if third == sf1_loser else sf1_loser

    final_standings = []
    placed = set()
    for pos, team in enumerate([champion, runner_up, third, fourth], 1):
        final_standings.append({"pos": pos, "team": team})
        placed.add(team)

    pos = 5
    for s in standings_a + standings_b:
        if s["team"] not in placed:
            final_standings.append({"pos": pos, "team": s["team"]})
            placed.add(s["team"])
            pos += 1

    return {
        "final_standings": final_standings,
        "champion": champion,
        "runner_up": runner_up,
        "bracket": {
            "SF": [
                {"t1": standings_a[0]["team"], "t2": standings_b[1]["team"], "winner": sf1_winner},
                {"t1": standings_b[0]["team"], "t2": standings_a[1]["team"], "winner": sf2_winner},
            ],
            "Final": {"t1": sf1_winner, "t2": sf2_winner, "winner": champion},
            "Champion": champion,
        }
    }


def simulate_caf_playoffs(africa_standings: list):
    """Puestos 3-7 (5 equipos) todos vs todos. Top 3 → Mundial."""
    playoff_teams = [e["team"] for e in africa_standings[2:7]]
    standings, _ = simulate_tournament(playoff_teams)
    qualified = [s["team"] for s in standings[:3]]
    return standings, qualified


# ============================================================
# COPA ORO - CONCACAF (6 equipos)
# ============================================================

def simulate_copa_oro(teams=None):
    """Simula la Copa Oro (6 equipos)."""
    if teams is None:
        teams = CONCACAF_TEAMS

    random.shuffle(teams)
    group_a = teams[:3]
    group_b = teams[3:]

    standings_a, _ = simulate_tournament(group_a)
    standings_b, _ = simulate_tournament(group_b)

    sf1_winner = simulate_knockout(standings_a[0]["team"], standings_b[1]["team"])
    sf2_winner = simulate_knockout(standings_b[0]["team"], standings_a[1]["team"])

    sf1_loser = standings_a[0]["team"] if sf1_winner == standings_b[1]["team"] else standings_b[1]["team"]
    sf2_loser = standings_b[0]["team"] if sf2_winner == standings_a[1]["team"] else standings_a[1]["team"]

    champion = simulate_knockout(sf1_winner, sf2_winner)
    runner_up = sf2_winner if champion == sf1_winner else sf1_winner
    third = simulate_knockout(sf1_loser, sf2_loser)
    fourth = sf2_loser if third == sf1_loser else sf1_loser
    fifth = teams[4] if teams[4] not in [champion, runner_up, third, fourth] else teams[5]
    sixth = [t for t in teams if t not in [champion, runner_up, third, fourth, fifth]][0]

    final_standings = []
    for pos, team in enumerate([champion, runner_up, third, fourth, fifth, sixth], 1):
        final_standings.append({"pos": pos, "team": team})

    return {
        "final_standings": final_standings,
        "champion": champion,
        "runner_up": runner_up,
        "bracket": {
            "SF": [
                {"t1": standings_a[0]["team"], "t2": standings_b[1]["team"], "winner": sf1_winner},
                {"t1": standings_b[0]["team"], "t2": standings_a[1]["team"], "winner": sf2_winner},
            ],
            "Final": {"t1": sf1_winner, "t2": sf2_winner, "winner": champion},
            "Champion": champion,
        }
    }


def simulate_concacaf_playoffs(copa_oro_standings: list):
    """Puestos 2-5 todos vs todos. Top 2 → Mundial, 3ro → Repechaje."""
    playoff_teams = [e["team"] for e in copa_oro_standings[1:5]]
    standings, _ = simulate_tournament(playoff_teams)
    qualified = [s["team"] for s in standings[:2]]
    repechaje = standings[2]["team"] if len(standings) > 2 else None
    return standings, qualified, repechaje


# ============================================================
# COPA ASIA - AFC (6 equipos, incluye Australia)
# ============================================================

def simulate_copa_asia(teams=None):
    """Simula la Copa Asia (6 equipos)."""
    if teams is None:
        teams = AFC_TEAMS

    random.shuffle(teams)
    group_a = teams[:3]
    group_b = teams[3:]

    standings_a, _ = simulate_tournament(group_a)
    standings_b, _ = simulate_tournament(group_b)

    sf1_winner = simulate_knockout(standings_a[0]["team"], standings_b[1]["team"])
    sf2_winner = simulate_knockout(standings_b[0]["team"], standings_a[1]["team"])

    sf1_loser = standings_a[0]["team"] if sf1_winner == standings_b[1]["team"] else standings_b[1]["team"]
    sf2_loser = standings_b[0]["team"] if sf2_winner == standings_a[1]["team"] else standings_a[1]["team"]

    champion = simulate_knockout(sf1_winner, sf2_winner)
    runner_up = sf2_winner if champion == sf1_winner else sf1_winner
    third = simulate_knockout(sf1_loser, sf2_loser)
    fourth = sf2_loser if third == sf1_loser else sf1_loser
    remaining = [t for t in teams if t not in [champion, runner_up, third, fourth]]
    fifth = remaining[0] if remaining else None
    sixth = remaining[1] if len(remaining) > 1 else None

    final_standings = []
    for pos, team in enumerate([champion, runner_up, third, fourth] + remaining, 1):
        final_standings.append({"pos": pos, "team": team})

    return {
        "final_standings": final_standings,
        "champion": champion,
        "runner_up": runner_up,
        "bracket": {
            "SF": [
                {"t1": standings_a[0]["team"], "t2": standings_b[1]["team"], "winner": sf1_winner},
                {"t1": standings_b[0]["team"], "t2": standings_a[1]["team"], "winner": sf2_winner},
            ],
            "Final": {"t1": sf1_winner, "t2": sf2_winner, "winner": champion},
            "Champion": champion,
        }
    }


def simulate_afc_playoffs(copa_asia_standings: list):
    """Puestos 2-5 todos vs todos. Top 3 → Mundial, 4to → Repechaje."""
    playoff_teams = [e["team"] for e in copa_asia_standings[1:5]]
    standings, _ = simulate_tournament(playoff_teams)
    qualified = [s["team"] for s in standings[:3]]
    repechaje = standings[3]["team"] if len(standings) > 3 else None
    return standings, qualified, repechaje


# ============================================================
# REPECHAJE INTERNACIONAL
# ============================================================

def simulate_int_playoff(concacaf_3rd: str, afc_4th: str,
                          conmebol_4th: str) -> dict:
    """
    Simula el repechaje internacional.
    CONCACAF 3ro vs AFC 4to
    CONMEBOL 4to vs Nueva Zelanda
    """
    match1_winner = simulate_knockout(concacaf_3rd, afc_4th)
    match2_winner = simulate_knockout(conmebol_4th, "New Zealand")

    return {
        "match1": {"t1": concacaf_3rd, "t2": afc_4th, "winner": match1_winner},
        "match2": {"t1": conmebol_4th, "t2": "New Zealand", "winner": match2_winner},
        "qualified": [match1_winner, match2_winner],
    }


# ============================================================
# MUNDIAL - 32 EQUIPOS
# ============================================================

def build_world_cup(qualified: list, host: str) -> dict:
    """
    Arma el Mundial con los 32 clasificados.
    8 grupos de 4 equipos.
    """
    teams = list(set(qualified))
    if host not in teams and host:
        # El host toma el lugar del 33ro o se añade
        if len(teams) >= 32:
            teams = teams[:32]
        if host not in teams:
            teams.append(host)
        teams = teams[:32]

    random.shuffle(teams)
    # Sembrar host en Grupo A pos 1
    if host in teams:
        teams.remove(host)
        teams.insert(0, host)

    groups = {}
    group_labels = ["A", "B", "C", "D", "E", "F", "G", "H"]
    for i, label in enumerate(group_labels):
        groups[label] = teams[i*4:(i+1)*4]

    return groups


def simulate_world_cup(groups: dict) -> dict:
    """Simula el Mundial completo."""
    group_results = {}
    for label, teams in groups.items():
        standings, matches = simulate_tournament(teams)
        group_results[label] = {"standings": standings, "matches": matches}

    # R16: 1A vs 2B, 1B vs 2A, etc.
    r16_pairs = [
        ("A", 0, "B", 1), ("C", 0, "D", 1),
        ("E", 0, "F", 1), ("G", 0, "H", 1),
        ("B", 0, "A", 1), ("D", 0, "C", 1),
        ("F", 0, "E", 1), ("H", 0, "G", 1),
    ]

    r16_results = []
    qf_teams = []
    for g1, p1, g2, p2 in r16_pairs:
        t1 = group_results[g1]["standings"][p1]["team"]
        t2 = group_results[g2]["standings"][p2]["team"]
        winner = simulate_knockout(t1, t2)
        r16_results.append({"t1": t1, "t2": t2, "winner": winner})
        qf_teams.append(winner)

    qf_results = []
    sf_teams = []
    for i in range(0, 8, 2):
        winner = simulate_knockout(qf_teams[i], qf_teams[i+1])
        qf_results.append({"t1": qf_teams[i], "t2": qf_teams[i+1], "winner": winner})
        sf_teams.append(winner)

    sf_results = []
    final_teams = []
    third_teams = []
    for i in range(0, 4, 2):
        winner = simulate_knockout(sf_teams[i], sf_teams[i+1])
        loser = sf_teams[i] if winner == sf_teams[i+1] else sf_teams[i+1]
        sf_results.append({"t1": sf_teams[i], "t2": sf_teams[i+1], "winner": winner})
        final_teams.append(winner)
        third_teams.append(loser)

    third_place_winner = simulate_knockout(third_teams[0], third_teams[1])
    champion = simulate_knockout(final_teams[0], final_teams[1])
    runner_up = final_teams[1] if champion == final_teams[0] else final_teams[0]

    return {
        "group_results": group_results,
        "R16": r16_results,
        "QF": qf_results,
        "SF": sf_results,
        "Third": {"t1": third_teams[0], "t2": third_teams[1], "winner": third_place_winner},
        "Final": {"t1": final_teams[0], "t2": final_teams[1], "winner": champion},
        "Champion": champion,
        "RunnerUp": runner_up,
    }


# ============================================================
# ACTUALIZACIÓN DE RANKING FIFA
# ============================================================

def update_ranking_from_tournament(results: dict, tournament_type: str = "confederation"):
    """Actualiza el ranking FIFA según los resultados del torneo."""
    ranking = st.session_state.fifa_ranking

    if tournament_type == "world_cup":
        champion = results.get("Champion")
        runner_up = results.get("RunnerUp")
        if champion:
            ranking[champion] = ranking.get(champion, 1000) + 150
        if runner_up:
            ranking[runner_up] = ranking.get(runner_up, 1000) + 80

        # QF
        for m in results.get("QF", []):
            loser = m["t1"] if m["winner"] != m["t1"] else m["t2"]
            ranking[loser] = ranking.get(loser, 1000) + 30
            ranking[m["winner"]] = ranking.get(m["winner"], 1000) + 50

        # Groups
        for g_data in results.get("group_results", {}).values():
            for pos, entry in enumerate(g_data["standings"]):
                pts = entry.get("pts", 0)
                ranking[entry["team"]] = ranking.get(entry["team"], 1000) + pts * 2

    else:
        # Confederación: puntos básicos según posición
        final_standings = results.get("final_standings", [])
        for entry in final_standings:
            pos = entry.get("pos", 10)
            team = entry["team"]
            bonus = max(0, (10 - pos) * 8)
            ranking[team] = ranking.get(team, 1000) + bonus

    st.session_state.fifa_ranking = ranking
