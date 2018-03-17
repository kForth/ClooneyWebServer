import json

import requests

if __name__ == "__main__":
    entries = json.load(open('/Users/kestin/Documents/2018onto1_fri-12pmto3pm.json'))
    for entry in entries:
        print(entry)
        payload = {
            'event':      '2018onto1',
            'team':       int(entry['team_number']),
            'match': entry['match'],
            'pos': entry  ['pos'],
            'data':       entry
        }
        resp = requests.post('http://clooney.kest.in/api/sql/add_entry', json=payload)
        print(resp)
