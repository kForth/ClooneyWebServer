if __name__ == "__main__":
    import sqlite3
    import json

    event_id = '2018oncmp2'
    db = sqlite3.connect('../db/db.sqlite')

    entries = db.execute('SELECT data FROM scouting_entries WHERE event=\'{}\''.format(event_id)).fetchall()
    entries = [json.loads(e[0]) for e in entries]
    if entries:
        json.dump(entries, open('../{}.json'.format(event_id), 'w+'))
