import json, glob, re, collections
items = json.load(open("pipeline/all_dx.json")); by = {x["id"]: x for x in items}
n = collections.Counter(); bad = []
for f in sorted(glob.glob("review/*.patch.json")):
    for p in json.load(open(f)):
        x = by.get(p.get("id"))
        if not x: bad.append((f, p.get("id"), "unknown id")); continue
        if p.get("drop"): x["_drop"] = True; n["drop"] += 1
        if "set" in p:
            for k, v in p["set"].items(): x[k] = v
            n["set"] += 1
        if "remove_dx" in p:
            x["dx"] = [d for d in x.get("dx", []) if d not in set(p["remove_dx"])]; n["remove"] += len(p["remove_dx"])
# owner-strict origin standard
t = by.get("i-three-sheets-to-the-wind")
if t: t["origin"] = "Sailors' slang; the exact origin is uncertain."
items = [x for x in items if not x.get("_drop")]
ids = {x["id"] for x in items}
for x in items:
    x["dx"] = [d for d in x.get("dx", []) if d in ids]
    c = x.get("cloze")
    if c:
        s = c["s"]
        s = re.sub(r"\b([Aa])n? ___", lambda m: m.group(1) + "(n) ___", s)
        c["s"] = s
print(n, "bad:", bad)
print("items", len(items), "dx<5:", [(x["id"], len(x["dx"])) for x in items if not x["id"].startswith("p-") and len(x["dx"]) < 5])
json.dump(items, open("pipeline/all_final.json", "w"), ensure_ascii=False)
