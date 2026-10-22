import json
from nltk.corpus import wordnet as wn
items = json.load(open("pipeline/all_dx.json")); by = {x["id"]: x for x in items}
PM={"noun":"n","verb":"v","adjective":"a","adverb":"r"}
def view(x):
    v = {k: x[k] for k in x if k != "dx"}
    if x.get("dx"):
        v["wrong_options"] = [{"id": d, "term": by[d]["term"], "def": by[d]["def"]} for d in x["dx"]]
    if x["track"] == "vocab":
        p = PM[x["pos"]]
        v["wordnet_glosses"] = [s.definition() for s in wn.synsets(x["term"]) if s.pos().replace("s","a")==p and any(l.name()==x["term"] for l in s.lemmas())][:6]
    return v
chunks = {}
for x in items:
    t = x["track"]
    if t == "vocab": k = f"vocab-L{x['level']}"
    elif t == "reasoning": k = "reasoning-concepts" if x["id"].startswith("c-") else ("reasoning-problems-L1" if x["level"]==1 else "reasoning-problems-L2" if x["level"]==2 else "reasoning-problems-L3")
    elif t in ("idioms","refs","knowledge"): k = f"{t}-{'1to3' if x['level']<=3 else '4to5'}"
    else: k = t
    chunks.setdefault(k, []).append(view(x))
for k, v in chunks.items():
    json.dump(v, open(f"review/{k}.json","w"), ensure_ascii=False, indent=1); print(k, len(v))
