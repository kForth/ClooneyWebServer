import numpy as np
from scipy.optimize import minimize
from scipy.stats import percentileofscore
from tba_py import TBA

from flask_sqlalchemy import SQLAlchemy

import time

IGNORE_ELIMS = True


class OprCalculator(object):
    def __init__(self, tba: TBA):
        self.tba = tba

    def get_matches_from_tba(self, event):
        match_json = self.tba.get_event_matches(event)
        scores = []
        for match in match_json:
            if IGNORE_ELIMS and match["comp_level"] != "qm":
                continue
            if "frc0" in match["alliances"]["red"]["team_keys"] or "frc0" in match["alliances"]["blue"]["team_keys"]:
                continue
            for alli in ["red", "blue"]:
                try:
                    alliance = [
                        int(match["alliances"][alli]["team_keys"][0][3:]),
                        int(match["alliances"][alli]["team_keys"][1][3:]),
                        int(match["alliances"][alli]["team_keys"][2][3:]),
                        match["score_breakdown"][alli]
                    ]
                except:
                    continue
                scores.append(alliance)
        return scores

    def get_team_list_from_matches(self, event_id, matches=None):
        teams = []
        if matches is not None:
            matches = map(lambda x: x[0:-1], matches)
            for match in matches:
                teams += match
        else:
            team_list = self.tba.get_event_teams(event_id)
            teams = list(map(lambda x: x["team_number"], team_list))
        return list(np.unique(teams))

    @staticmethod
    def get_score_sums(match_matrix: list, teams: list):
        scores = [int(0)] * len(teams)
        for i in range(len(match_matrix)):
            match = match_matrix[i]
            for j in range(3):
                if match[j] not in teams:
                    teams.append(int(match[j]))
                    teams.sort()
                    scores.insert(teams.index(match[j]), 0)
                if type(match[-1]) in [int, float, bool]:
                    scores[teams.index(match[j])] += match[-1]
        return teams, scores

    @staticmethod
    def fix_missing_teams(teams, scores):
        for i in range(scores.count(0)):
            index = scores.index(0)
            scores.pop(index)
            teams.pop(index)
        for i in range(teams.count(0)):
            index = teams.index(0)
            scores.pop(index)
            teams.pop(index)
        return teams, scores

    @staticmethod
    def get_interaction_matrix(match_matrix, teams):
        matrix = [list([int(0)] * len(teams)) for _ in range(len(teams))]
        for i in range(len(match_matrix)):
            match = match_matrix[i]
            for j in range(3):
                for k in range(3):
                    matrix[teams.index(match[j])][teams.index(match[k])] += 1
        return matrix

    @staticmethod
    def solve(interactions, scores):
        return np.linalg.solve(interactions, scores)

    @staticmethod
    def minimize(interactions, scores):
        n = len(scores)
        func = lambda x: np.linalg.norm(np.dot(interactions, x) - scores)
        return minimize(func, np.zeros(n), method='L-BFGS-B', bounds=[(0., None) for _ in range(n)])["x"]

    def get_event_oprs(self, event_id, minimize=False, db=None):
        from server.models import OprEntry
        print("Working on: {}".format(event_id))
        start_time = time.time()
        solve_time_accum = 0
        matches = self.get_matches_from_tba(event_id)
        if len(matches) < 1:
            return []
        teams = self.get_team_list_from_matches(event_id, matches)
        interactions = self.get_interaction_matrix(matches, teams)
        opr_list = {}
        for score_type in list(matches[0][-1].keys()):  # + ['teleGears']:
            if len(matches) == 0 or score_type[:4] == "tba_":
                continue
            temp_matches = []
            for m in matches:
                # if score_type == "teleGears":
                #     val = round(1.0 * float(m[-1]["teleopRotorPoints"]), 2)
                #     val = [0, 2, 6, 12, 13][int(val / 40.0)]
                #     temp_matches += [m[:-1] + [val]]
                if type(m[-1][score_type]) in [int, float]:
                    val = round(1.0 * float(m[-1][score_type]), 2)
                    temp_matches += [m[:-1] + [val]]

            dump, scores = self.get_score_sums(temp_matches, list(teams))

            solve_start_time = time.time()
            if minimize:
                oprs = self.minimize(interactions, scores)
            else:
                oprs = self.solve(interactions, scores)
            solve_time_accum += time.time() - solve_start_time
            opr_dict = dict(zip(teams, oprs))
            for team in teams:
                if db is not None and type(db) is SQLAlchemy:
                    percentile = percentileofscore(oprs, opr_dict[team])
                    entry_id = "_".join([str(team), event_id, score_type])
                    entry = OprEntry.query.filter_by(id=entry_id).first()
                    if entry:
                        entry.value = float(opr_dict[team])
                        entry.percentile = float(percentile)
                    else:
                        db.session.add(OprEntry(entry_id, int(team), event_id, score_type, float(opr_dict[team]), float(percentile)))
                if team not in opr_list.keys():
                    opr_list[team] = {
                        "team_number": int(team),
                        "oprs":        {}
                    }
                opr_list[team]["oprs"][score_type] = round(opr_dict[team], 2)

        if db is not None and type(db) is SQLAlchemy:
            db.session.commit()

        print("Finished Event: {}".format(event_id))
        print("Solving took {}s".format(round(solve_time_accum, 1)))
        print("Overall time was {}s".format(round(time.time() - start_time, 1)))
        return list(opr_list.values())

if __name__ == "__main__":
    from server import sql_db
    tba = TBA('GdZrQUIjmwMZ3XVS622b6aVCh8CLbowJkCs5BmjJl2vxNuWivLz3Sf3PaqULUiZW', use_cache=False, cache_filename='../tba.json')

    # events = tba.get_events("2018")
    target_week = 7 #zero index
    event_keys = ['2018txda']
    # for event in events:
    #     if event["week"] is not None and event["week"] < target_week:
    #         event_keys.append(event["key"])

    opr = OprCalculator(tba)

    for event_key in event_keys:
        opr.get_event_oprs(event_key, db=sql_db)
