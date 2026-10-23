import json, glob
P = []
for f in sorted(glob.glob("/tmp/wp/pas/L*.json")): P += json.load(open(f))
by = {p["id"]: p for p in P}; n = 0; drop = set()
for f in sorted(glob.glob("/tmp/wp/review/pas-*.patch.json")):
    for p in json.load(open(f)):
        if p.get("drop"): drop.add(p["id"])
        for k, v in (p.get("set") or {}).items(): by[p["id"]][k] = v
        n += 1
P = [p for p in P if p["id"] not in drop]
json.dump(P, open("/tmp/wp/pipe/passages_final.json", "w"), ensure_ascii=False)
print("passages", len(P), "patches", n, "dropped", len(drop))
