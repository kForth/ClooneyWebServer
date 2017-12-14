import json
import requests

if __name__ == "__main__":
    event_key = "2017onham"
    data = json.load(open('../old_data/onham.json'))
    for line in data:
        filename = line['filename']
        line['match'] = int(line['match'])
        line['pos'] = int(line['pos'])
        line['team'] = int(line['team_number'])
        del line['filename']
        del line['team_number']
        del line['robot_drawing']
        del line['notes']
        payload = {
            'event': event_key,
            'data': line,
            'filename': filename
        }
        resp = requests.post('http://0.0.0.0:5002/add/entry', json=payload)
        if resp.status_code != 200:
            print(resp)
