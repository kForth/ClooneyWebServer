from tba_py import BlueAllianceAPI
import numpy as np
from scipy.optimize import minimize

from server import Database

tba_url = "http://thebluealliance.com/api/v2"
headers = {'X-TBA-App-Id': "kestin_goforth:clooney_scouting_system:v01"}

IGNORE_ELIMS = True


class OprCalculator(object):
    def __init__(self, tba: BlueAllianceAPI):
        self.tba = tba

    def get_matches_from_tba(self, event):
        match_json = self.tba.get_event_matches(event)
        scores = []
        for match in match_json:
            if IGNORE_ELIMS and match["comp_level"] != "qm":
                continue
            if "frc0" in match["alliances"]["red"]["teams"] or "frc0" in match["alliances"]["blue"]["teams"]:
                continue
            for alli in ["red", "blue"]:
                try:
                    alliance = [
                        int(match["alliances"][alli]["teams"][0][3:]),
                        int(match["alliances"][alli]["teams"][1][3:]),
                        int(match["alliances"][alli]["teams"][2][3:]),
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
    def get_score_sums(match_matrix: list, teams: list, key: str):
        scores = [int(0)] * len(teams)
        for i in range(len(match_matrix)):
            match = match_matrix[i]
            for j in range(3):
                if match[j] not in teams:
                    teams.append(int(match[j]))
                    teams.sort()
                    scores.insert(teams.index(match[j]), 0)
                if type(match[-1][key]) in [int, float, bool]:
                    scores[teams.index(match[j])] += match[-1][key]
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

    def get_event_oprs(self, event_id, minimize=True):
        matches = self.get_matches_from_tba(event_id)
        teams = self.get_team_list_from_matches(event_id, matches)
        opr_list = {}

        interactions = self.get_interaction_matrix(matches, teams)
        for score_type in matches[0][-1].keys():
            if len(matches) == 0:
                continue
            temp_matches = []
            for m in matches:
                if type(m[-1][score_type]) in [int, float]:
                    temp_matches += [m[:-1] + [round(1.0 * float(m[-1][score_type]), 2)]]
            dump, scores = self.get_score_sums(matches, list(teams), score_type)

            if minimize:
                oprs = self.minimize(interactions, scores)
            else:
                oprs = self.solve(interactions, scores)

            for team in teams:
                if team not in opr_list.keys():
                    opr_list[str(team)] = {
                        "team_number": int(team),
                        "oprs": {}
                    }
                opr_list[str(team)]["oprs"][score_type] = round(oprs[teams.index(team)], 2)

        return list(opr_list.values())

if __name__ == "__main__":
    event_key = "2017flwp"
    opr = OprCalculator(BlueAllianceAPI("Clooney", "Clooney", "2"))
    db = Database(dirpath="../db/")
    team_oprs = opr.get_event_oprs(event_key)
    db.set_event_oprs(event_key, team_oprs)
