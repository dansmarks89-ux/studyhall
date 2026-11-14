import json, re
from pronlib import pron
items = json.load(open("pipeline/all_final.json")); n = 0
for x in items:
    t = x["term"]
    if re.fullmatch(r"[A-Za-z]+", t):
        p = pron(t)
        if p: x["pr"] = p; n += 1
json.dump(items, open("pipeline/all_final.json", "w"), ensure_ascii=False)
print("pronunciations:", n, "of", sum(1 for x in items if re.fullmatch(r"[A-Za-z]+", x["term"])))
for w in ["obsequious","candid","ubiquitous","pusillanimous","advocate","entrepreneur","extraordinary"]: print(w, pron(w))
