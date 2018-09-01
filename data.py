from server.models import AnalysisEntry

if __name__ == "__main__":
    entries = AnalysisEntry.query.filter_by(event='2017oncmp')
    good = []
    for entry in entries:
        data = entry.get_data()
        if data["auto_gears_scored"]["value"] > 0:
            good.append(data)

    from pprint import pprint
    pprint(list(map(lambda x: str(x['team_number']['value']) + " : " + str(x['auto_gears_scored']['value']) + " : " + str(x['tele_gears_scored']['value']) + " : " + str(x['tele_climbed']['count_common']), good)))
