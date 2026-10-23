"""Apply reviewer patches to the merged content -> pipe/all_final.json (cards only)."""
import json, glob, re, collections, sys
sys.path.insert(0, "/tmp/wp")
items = json.load(open("/tmp/wp/pipe/all_dx.json")); by = {x["id"]: x for x in items}
n = collections.Counter(); bad = []
for f in sorted(glob.glob("/tmp/wp/review/*.patch.json")):
    for p in json.load(open(f)):
        x = by.get(p.get("id"))
        if not x: bad.append((f, p.get("id"))); continue
        if p.get("drop"): x["_drop"] = True; n["drop"] += 1
        if "set" in p:
            for k, v in p["set"].items(): x[k] = v
            n["set"] += 1
        if "remove_dx" in p:
            rm = set(p["remove_dx"]); x["dx"] = [d for d in x.get("dx", []) if d not in rm]; n["remove"] += len(rm)
items = [x for x in items if not x.get("_drop")]
ids = {x["id"] for x in items}
for x in items:
    x["dx"] = [d for d in x.get("dx", []) if d in ids]
    if not x.get("also"): x.pop("also", None)
    c = x.get("cloze")
    if c: c["s"] = re.sub(r"\b([Aa])n? ___", lambda m: m.group(1) + "(n) ___", c["s"])
print(dict(n), "unknown ids:", bad[:5], len(bad))
short = [(x["id"], len(x["dx"])) for x in items if not x["id"].startswith("p-") and len(x["dx"]) < 5]
print("items", len(items), "dx<5:", len(short), short[:10])
json.dump(items, open("/tmp/wp/pipe/all_final.json", "w"), ensure_ascii=False)
