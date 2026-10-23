import json, re, sys
sys.path.insert(0, "/tmp/wp")
from defcheck import hard_words
B = json.load(open("/tmp/wp/bands/all.json"))
POSMAP={"noun":"n","verb":"v","adjective":"a","adverb":"r"}
def stem_in(term, text):
    t=term.lower(); s=text.lower()
    if t in s: return True
    base = re.sub(r"(e|y|ies|es|s|ed|ing)$","",t)
    return len(base)>=4 and re.search(r"\b"+re.escape(base), s) is not None
def check(x):
    p=[]; w=[]
    for f in ["id","track","level","term","def","ex","cloze","syn","ant","pos"]:
        if f not in x: p.append("missing "+f)
    if p: return p,w
    t=x["term"]
    if x["id"]!="v-"+re.sub(r"[^a-z0-9-]","",t.lower().replace(" ","-")): p.append("id should be v-"+t.lower())
    b=B.get(t)
    if not b: p.append("term not in band list")
    elif b[0]!=x["level"]: p.append(f"term is level {b[0]}, not {x['level']}")
    elif POSMAP.get(x["pos"]) not in b[1]: p.append(f"pos {x['pos']} not a dictionary part of speech for this word ({b[1]})")
    if stem_in(t, x["def"]): p.append("def contains the term")
    if len(x["ex"])!=2: p.append("need exactly 2 examples")
    for e in x["ex"]:
        if not stem_in(t.split()[0], e): p.append("example lacks the term: "+e[:40])
    c=x["cloze"]
    if not isinstance(c,dict) or c.get("s","").count("___")!=1 or not c.get("a"): p.append("cloze needs one ___ and an answer")
    if x.get("also"):
        d=x["also"].split("(")[0]
        if stem_in(t,d): p.append("also: definition part contains the term")
    lv=x["level"]; n=len(x["def"].split())
    if lv<0 and not 4<=n<=12: p.append(f"starter def must be 4-12 words (has {n})")
    if lv>=0 and not 6<=n<=22: p.append(f"def must be 6-22 words (has {n})")
    h=hard_words(x["def"], lv)
    if h: w.append("plain-word flag in def: "+", ".join(h))
    if x.get("also"):
        h=hard_words(x["also"].split("(")[0], lv)
        if h: w.append("plain-word flag in also: "+", ".join(h))
    return p,w
if __name__=="__main__":
    items=json.load(open(sys.argv[1])); ids=set(); P=W=0
    for x in items:
        p,w=check(x)
        if x.get("id") in ids: p.append("duplicate id")
        ids.add(x.get("id"))
        for m in p: print("PROBLEM", x.get("id"), "-", m); P+=1
        for m in w: print("warning", x.get("id"), "-", m); W+=1
    print(f"{len(items)} items, {P} problems, {W} plain-word warnings")
