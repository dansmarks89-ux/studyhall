"""Combine existing + new content, apply upgrade patches, compute wrong options (dx)."""
import json, glob, re, random, collections, sys
import wn
W = wn.Wordnet('oewn:2024')
WP = "/tmp/wp/"
old = json.load(open("/tmp/studyhall/src/vocab/data/items.json"))
for x in old: x["_old"] = True
items = list(old)
for f in sorted(glob.glob(WP+"new/*.json")) + sorted(glob.glob(WP+"newt/*.json")):
    items += json.load(open(f))
by = {}
dup = []
for x in items:
    if x["id"] in by: dup.append(x["id"]); continue
    by[x["id"]] = x
# duplicate terms within a track (new vs new / new vs old): keep the first (old first)
seen = {}; drop = set()
for x in by.values():
    k = (x["track"] if x["track"] != "reasoning" else x["id"][:2], x["term"].lower().strip())
    if k in seen: drop.add(x["id"]); dup.append(x["id"])
    else: seen[k] = x["id"]
for d in drop: by.pop(d, None)
items = list(by.values())
# upgrade patches for existing vocab
n = collections.Counter()
for f in sorted(glob.glob(WP+"rev/out-*.patch.json")):
    for p in json.load(open(f)):
        x = by.get(p["id"])
        if x and "set" in p:
            for k, v in p["set"].items(): x[k] = v
            n[f[-15:]] += 1
print("dropped duplicates:", dup); print("upgrade patches:", dict(n))
WORD = re.compile(r"[a-z']+")
STOP = set("a an the of to and or in on for with by is are be as at that this it its from who which what someone something one's your their his her not very".split())
def toks(s): return {t for t in WORD.findall(s.lower()) if t not in STOP and len(t) > 2}
SYN = {}
def syns(w):
    if w not in SYN: SYN[w] = {s.id for s in W.synsets(w.replace(" ", "_"))} | {s.id for s in W.synsets(w)}
    return SYN[w]
def related(x, y):
    tx, ty = x["term"].lower(), y["term"].lower()
    if tx == ty: return True
    lx = {s.lower() for s in x.get("syn", []) + x.get("ant", [])}; ly = {s.lower() for s in y.get("syn", []) + y.get("ant", [])}
    if ty in lx or tx in ly: return True
    if set(s.lower() for s in x.get("syn", [])) & set(s.lower() for s in y.get("syn", [])): return True
    if set(s.lower() for s in x.get("ant", [])) & set(s.lower() for s in y.get("syn", [])): return True
    if x["track"] in ("vocab", "knowledge") and " " not in tx and " " not in ty and syns(tx) & syns(ty): return True
    if ty in x.get("def", "").lower() or tx in y.get("def", "").lower(): return True
    a, b = toks(x.get("def", "")), toks(y.get("def", ""))
    if a and b and len(a & b) / min(len(a), len(b)) >= 0.5: return True
    if tx[:5] == ty[:5] and len(tx) > 5: return True
    if tx[:4] == ty[:4] and x["track"] == "vocab": return True
    return False
random.seed(7)
pools = collections.defaultdict(list)
key = lambda x: x["track"] + ("|c" if x["id"].startswith("c-") else "") + ("|" + x.get("pos", "") if x["track"] == "vocab" else "")
for x in items:
    if not x["id"].startswith("p-"): pools[key(x)].append(x)
PREV = {x["id"]: x.get("dx") for x in json.load(open(WP+"pipe/all_dx_v1.json"))}
for x in items:
    if x["id"].startswith("p-"): x["dx"] = []; continue
    if PREV.get(x["id"]) and not x.get("_old"):
        x["dx"] = [d for d in PREV[x["id"]] if d in by]
        if len(x["dx"]) >= 6: continue
    if x.get("_old") and x.get("dx"):   # reviewed already; keep, drop ids that no longer exist
        x["dx"] = [d for d in x["dx"] if d in by]
        if len(x["dx"]) >= 6: continue
    cand = [y for y in pools[key(x)] if y["id"] != x["id"] and abs(y["level"] - x["level"]) <= 3]
    if len(cand) < 20: cand = [y for y in pools[key(x)] if y["id"] != x["id"]]
    def score(y):
        s = abs(y["level"] - x["level"]) * 2
        if x["track"] == "knowledge" and y.get("domain") != x.get("domain"): s += 3
        if x["track"] == "roots" and y.get("type") != x.get("type"): s += 4
        if x["track"] == "reasoning" and y.get("kind") != x.get("kind"): s += 1
        return s + random.random() * 2.5
    cand.sort(key=score)
    dx = list(x.get("dx") or [])
    for y in cand:
        if y["id"] in dx or related(x, y): continue
        dx.append(y["id"])
        if len(dx) == 9: break
    x["dx"] = dx
json.dump(items, open(WP+"pipe/all_dx.json", "w"), ensure_ascii=False)
c = collections.Counter((x["track"], x["level"]) for x in items)
print(len(items), sorted(c.items())); print("dx<6:", sum(1 for x in items if not x["id"].startswith("p-") and len(x["dx"]) < 6))
