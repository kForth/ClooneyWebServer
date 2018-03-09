from tba_py import TBA

from server.db import Database


class ErrorChecker(object):
    def __init__(self, db: Database, tba: TBA):
        self.db = db
        self.tba = tba

    def check_event(self, event_id):
        raw_data = self.db.get_raw_data(event_id)
        matches = [x["match_number"] for x in self.tba.get_event_matches(event_id) if x["comp_level"] == "qm"]
        data_matches = list(map(lambda x: x["match"] if "match" in x.keys() else None, raw_data))
        match_counts = {}
        for i in range(1, len(matches) + 1):
            match_counts[str(i)] = data_matches.count(str(i))
        print(match_counts)

if __name__ == "__main__":
    tba = TBA('GdZrQUIjmwMZ3XVS622b6aVCh8CLbowJkCs5BmjJl2vxNuWivLz3Sf3PaqULUiZW', use_cache=True, cache_filename='../tba.json')
    db = Database(path_prefix="../")
    check = ErrorChecker(db, tba)
    check.check_event("2017onto2")
