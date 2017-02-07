import json
from glob import glob

file = "/raw_data.json"

for event in glob("2016*"):
    data = json.load(open(event + file))

    out = []
    for line in data:
        entry = {}
        for key in line.keys():
            entry[key.lower().replace(" ", "_")] = line[key]
        out.append(entry)
    print(out)
    json.dump(out, open(event + file, "w"))
