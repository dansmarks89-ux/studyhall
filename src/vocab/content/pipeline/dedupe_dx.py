import json, re, random, collections
from nltk.corpus import wordnet as wn
items = json.load(open("pipeline/all_raw.json"))
by = {x["id"]: x for x in items}
drop = set()
# vocab keeps the word; the reference story moves onto the vocab card
for w in ["stentorian","jeremiad","nemesis","scapegoat","mercurial","panacea","laconic","quixotic","shibboleth"]:
    v, f = by["v-"+w], by["f-"+w]
    v["story"] = f["story"]; v["source"] = f["source"]; drop.add(f["id"])
for w in ["irony","monopoly","precedent","catalyst"]: drop.add("k-"+w)
drop.add("i-chutzpah")
by["c-equivocation"]["term"] = "equivocation (fallacy)"
for s in ["by-the-skin-of-your-teeth","a-fly-in-the-ointment","salad-days","the-milk-of-human-kindness","go-the-extra-mile"]: drop.add("i-"+s)
drop |= {"k-karma","f-placebo-effect","k-regression-to-the-mean"}
items = [x for x in items if x["id"] not in drop]
by = {x["id"]: x for x in items}
print("kept", len(items), collections.Counter(x["track"] for x in items))

WORD = re.compile(r"[a-z']+")
STOP = set("a an the of to and or in on for with by is are be as at that this it its from who which what someone something one's your their his her".split())
def toks(s): return {t for t in WORD.findall(s.lower()) if t not in STOP and len(t)>2}
def wn_syn(a, b):
    A = {s for s in wn.synsets(a.replace(" ","_"))}; B = {s for s in wn.synsets(b.replace(" ","_"))}
    return bool(A & B)
def related(x, y):
    tx, ty = x["term"].lower(), y["term"].lower()
    if tx == ty: return True
    sx = {s.lower() for s in x.get("syn",[])+x.get("ant",[])}; sy = {s.lower() for s in y.get("syn",[])+y.get("ant",[])}
    if ty in sx or tx in sy: return True
    if len(set(s.lower() for s in x.get("syn",[])) & set(s.lower() for s in y.get("syn",[])))>0: return True
    if x["track"] in ("vocab","knowledge") and " " not in tx and " " not in ty and wn_syn(tx, ty): return True
    if ty in x.get("def","").lower() or tx in y.get("def","").lower(): return True
    a, b = toks(x.get("def","")), toks(y.get("def",""))
    if a and b and len(a & b)/min(len(a),len(b)) >= 0.5: return True
    if tx[:5] == ty[:5] and len(tx)>5: return True  # look-alikes would be too easy / confusing as a pool
    return False
random.seed(7)
pools = collections.defaultdict(list)
for x in items:
    if x["id"].startswith("p-"): continue
    key = x["track"] + ("|c" if x["id"].startswith("c-") else "")
    pools[key].append(x)
for x in items:
    if x["id"].startswith("p-"): continue
    key = x["track"] + ("|c" if x["id"].startswith("c-") else "")
    cand = [y for y in pools[key] if y["id"] != x["id"]]
    def score(y):
        s = abs(y["level"] - x["level"]) * 2
        if x["track"]=="vocab" and y.get("pos") != x.get("pos"): s += 100
        if x["track"]=="knowledge" and y.get("domain") != x.get("domain"): s += 3
        if x["track"]=="roots" and y.get("type") != x.get("type"): s += 4
        if x["track"]=="reasoning" and y.get("kind") != x.get("kind"): s += 1
        return s + random.random()*2.5
    cand.sort(key=score)
    dx = []
    for y in cand:
        if related(x, y): continue
        dx.append(y["id"])
        if len(dx) == 9: break
    x["dx"] = dx
json.dump(items, open("pipeline/all_dx.json","w"), ensure_ascii=False)
print(collections.Counter(len(x.get("dx",[])) for x in items))
