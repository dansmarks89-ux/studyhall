import json, collections, sys, wn
W = wn.Wordnet('oewn:2024')
items = json.load(open("/tmp/wp/pipe/all_dx.json")); by = {x["id"]: x for x in items}
PM = {"noun": "n", "verb": "v", "adjective": "a", "adverb": "r"}
def view(x):
    v = {k: x[k] for k in x if k != "dx"}
    if x.get("dx"): v["wrong_options"] = [{"id": d, "term": by[d]["term"], "def": by[d]["def"]} for d in x["dx"]]
    if x["track"] == "vocab":
        p = PM[x["pos"]]
        v["wordnet_glosses"] = [s.definition() for s in W.synsets(x["term"]) if s.pos.replace("s", "a") == p][:6]
    return v
groups = collections.defaultdict(list)
for x in items:
    t = x["track"]
    if t == "vocab": k = ("vocab-old-" + str(min(5, max(0, x["level"]) // 2)) if x.get("_old") else f"vocab-L{x['level']}")
    elif x.get("_old"): continue
    elif t == "reasoning": k = f"reasoning-L{x['level']}"
    else: k = f"{t}-L{x['level']}"
    groups[k].append(view(x))
out = []
for k, v in sorted(groups.items()):
    n = max(1, round(len(v) / 130))
    for i in range(n):
        part = v[i::n]; name = f"{k}-{i}" if n > 1 else k
        json.dump(part, open(f"/tmp/wp/review/{name}.json", "w"), ensure_ascii=False, indent=1); out.append((name, len(part)))
print(len(out), out)
