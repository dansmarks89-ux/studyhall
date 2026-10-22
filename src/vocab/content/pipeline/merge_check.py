import json, glob, re, collections
from nltk.corpus import wordnet as wn
C = "content/"
items = []
def load(pat):
    out=[]
    for f in sorted(glob.glob(C+pat)): out += json.load(open(f))
    return out
idB = load("_idB_*.json"); json.dump(idB, open(C+"idioms-B.json","w"), ensure_ascii=False, indent=1)
files = {"vocab": "vocab-L*.json", "roots":"roots.json", "idioms":"idioms-[AB].json", "refs":"refs-[AB].json",
         "knowledge":"knowledge-[AB].json", "reasoning":"reasoning-*.json"}
for tr, pat in files.items():
    for x in load(pat):
        x["_file"] = tr; items.append(x)
print("total", len(items), collections.Counter(x["track"] for x in items))
probs = []
def P(x, m): probs.append((x.get("id"), m))
ids = collections.Counter(x["id"] for x in items)
for k,v in ids.items():
    if v>1: probs.append((k, "duplicate id"))
terms = collections.defaultdict(list)
for x in items: terms[x["term"].lower().strip()].append(x["id"])
for t,v in terms.items():
    if len(v)>1: probs.append((",".join(v), "duplicate term "+t))
bands = {}
for lv in range(11):
    for line in open(f"pipeline/bands/level{lv}.txt"):
        w,pos,z = line.rstrip("\n").split("\t"); bands[w]=(lv,pos.split(","))
POSMAP={"noun":"n","verb":"v","adjective":"a","adverb":"r"}
def stem_in(term, text):
    t=term.lower(); s=text.lower()
    if t in s: return True
    base = re.sub(r"(e|y|ies|es|s|ed|ing)$","",t)
    return len(base)>=4 and re.search(r"\b"+re.escape(base), s) is not None
for x in items:
    tr = x["track"]
    for f in ["id","track","level","term","def"]:
        if f not in x: P(x,"missing "+f)
    if tr=="vocab":
        w=x["term"]
        if w not in bands: P(x,"not in band files")
        elif bands[w][0]!=x["level"]: P(x,f"band {bands[w][0]} != level {x['level']}")
        if POSMAP.get(x.get("pos")) not in bands.get(w,(0,[]))[1]: P(x,f"pos {x.get('pos')} not in WordNet {bands.get(w)}")
    needs_cloze = tr in ("vocab","idioms","refs","knowledge")
    if needs_cloze:
        ex=x.get("ex",[])
        if len(ex)!=2: P(x,"ex count")
        c=x.get("cloze") or {}
        if c.get("s","").count("___")!=1: P(x,"cloze blanks")
        if not c.get("a"): P(x,"cloze answer missing")
        if stem_in(x["term"], x["def"]) and tr!="refs": P(x,"def contains term")
        for e in ex:
            if not stem_in(x["term"].split()[0], e) and tr=="vocab": P(x,"example lacks term: "+e[:50])
    if tr=="roots" and len(x.get("words",[]))!=4: P(x,"roots words")
    if x["id"].startswith("c-") and len(x.get("tests",[]))!=2: P(x,"tests")
    if x["id"].startswith("p-"):
        if len(x.get("options",[]))!=6 or not (0<=x.get("answer",-1)<=5): P(x,"options/answer")
        if len(set(o.strip().lower() for o in x["options"]))!=6: P(x,"dup options")
print(len(probs), "problems")
for p in probs: print(p)
for x in items: x.pop("_file",None)
json.dump(items, open("pipeline/all_raw.json","w"), ensure_ascii=False)
