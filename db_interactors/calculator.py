import json
import statistics
from operator import itemgetter


class CalculatorDatabaseInteractor:
    def __init__(self, db):
        self._db = db
        self._calc = Calculator()

    def update_entries_for_event(self, event_key):
        entries = [e.data for e in self._db.entries.get_entries_for_event(event_key)]
        event_settings = self._db.events.get_event_settings(event_key)
        sheet = json.loads(event_settings['selected_sheet'])['data']
        data_keys = ['team', 'match', 'pos'] + [e['key'] for e in sheet if e['type'] not in ['Divider', 'Image']]
        data_by_team = {}

        entries.sort(key=itemgetter('match', 'pos'))
        for entry in entries:
            team = entry['team']
            if all([key in data_keys for key in entry.keys()]) and len(entry) == len(data_keys):
                if team not in data_by_team.keys():
                    data_by_team[team] = dict(zip(data_keys, [[] for _ in data_keys]))
                for key in entry.keys():
                    data_by_team[team][key].append(entry[key])

        analysis_data_by_team = {}
        for team in list(data_by_team.keys())[1:]:
            data = data_by_team[team]
            analysis = {
                'team': {'mode', self._calc.mode(data['team'])},
                'match': {'mode': self._calc.mode(data['match'])},
                'pos': {'mode': self._calc.mode(data['pos'])}
            }
            for field in sheet:
                if field['type'] in ['Divider', 'Image']:
                    continue

                key = field['key']
                raw = data[key]
                if not raw:
                    continue

                analysis[key] = {
                    'count': len(raw),
                    'raw': raw
                }
                if field['type'] == 'Numbers':
                    analysis[key].update({
                        'avg': sum(raw) / len(raw),
                        'median': statistics.median(raw),
                        'median_grouped': statistics.median_grouped(raw),
                        'pstdev': statistics.pstdev(raw),
                        'mode': self._calc.mode(raw)
                    })
                elif field['type'] == 'Boolean':
                    analysis[key].update({
                        'avg': raw.count(True) / len(raw),
                        'mode': self._calc.mode(raw)
                    })
                elif field['type'] == 'HorizontalOptions':
                    analysis[key].update({
                        'mode': self._calc.mode(raw),
                        'option_percent':
                            dict([(key, raw.count(key) / len(raw) * 100) for key in field['options'].split(" ")])
                    })
            analysis_data_by_team[team] = analysis

        # TODO: Do something with the data.
        print(analysis_data_by_team)
        return True


class Calculator(object):
    def __init__(self, **fields):
        self.fields = {
            'abs':   abs,
            'min':   min,
            'max':   max,
            'mode':  self.mode,
            'print': print,
            'len':   len,
            'round': round,
            'zip':   zip,
            'sum':   sum,
            'map':   map,
            'int':   int,
            'float': float
        }
        self.fields.update(**fields)

    def mode(self, data):
        freq = dict(zip(data, [0 for _ in data]))
        for elem in data:
            freq[elem] += 1
        return sorted(list(freq.items()), key=itemgetter(1))[-1][0]

    def add_fields(self, **fields):
        for key, value in fields.items():
            self.fields[key] = value

    def solve(self, equation):
        return eval(equation, {"__builtins__": None}, self.fields)
