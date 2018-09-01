import json
import random

import requests

from tba_py import TBA

if __name__ == "__main__":
    tba = TBA('GdZrQUIjmwMZ3XVS622b6aVCh8CLbowJkCs5BmjJl2vxNuWivLz3Sf3PaqULUiZW')
    event_key = '2018onto1'
    sheet = json.load(open('/Users/kestin/Projects/ClooneySheetGen/resources/powerup_test_3.json'))
    matches = tba.get_event_matches(event_key)
    if not matches:
        matches = []
        teams = tba.get_event_teams(event_key)
        for match_num in range(100):
            match = {
                'match_number': match_num + 1,
                'alliances': {
                    'red': {
                        'team_keys': []
                    },
                    'blue': {
                        'team_keys': []
                    }
                }
            }
            for alliance in ['red', 'blue']:
                for i in range(3):
                    match['alliances'][alliance]['team_keys'] += ['frc' + str(random.choice(teams)['team_number'])]
            matches += [match]

    for match in matches:
        for alliance in sorted(match['alliances'].keys()):
            for team in match['alliances'][alliance]['team_keys']:
                team = team[3:]
                payload = {
                    'event': event_key,
                    'team': int(team),
                    'match': match['match_number'],
                    'pos': match['alliances'][alliance]['team_keys'].index('frc' + team) + (3 if alliance == 'blue' else 0)
                }
                data = payload.copy()
                for field in sheet:
                    if field['type'] == 'HorizontalOptions':
                        if type(field['options']) is str:
                            value = random.choice(field['options']['options'].split(" "))
                        else:
                            value = random.choice(field['options']['options'])
                    elif field['type'] == 'Numbers':
                        max_val = (field['ones'] if 'ones' in field.keys() else 9) + 10 * (field['tens'] if 'tens' in field.keys() else 1)
                        value = random.randint(0, max_val)
                    elif field['type'] == 'Boolean':
                        value = (random.randint(0, 1) == 1)
                    else:
                        continue
                    data[field['id']] = value
                payload['data'] = data
                resp = requests.post('http://0.0.0.0:5000/api/sql/add_entry', json=payload)
                if resp.status_code != 200:
                    print(resp)
    print("Done")
