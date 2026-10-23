import json, re, sys
sys.path.insert(0,"/tmp/wp")
from defcheck import hard_words
EX={l.split("\t")[2].strip().lower() for l in open("/tmp/wp/existing_terms.txt")}
def stem_in(term, text):
    t=term.lower(); s=text.lower()
    if t in s: return True
    base = re.sub(r"(e|y|ies|es|s|ed|ing)$","",t)
    return len(base)>=4 and re.search(r"\b"+re.escape(base), s) is not None
PRE={"roots":"r-","idioms":"i-","refs":"f-","knowledge":"k-"}
def check(x):
    p=[]; tr=x.get("track")
    for f in ["id","track","level","term","def"] if not str(x.get("id","")).startswith("p-") else ["id","track","level","term","q","options","answer","why","kind"]:
        if f not in x: p.append("missing "+f)
    if p: return p
    if x["term"].strip().lower() in EX: p.append("already exists in the app")
    i=x["id"]
    if tr in PRE and not i.startswith(PRE[tr]): p.append("id prefix should be "+PRE[tr])
    if tr=="reasoning" and not (i.startswith("c-") or i.startswith("p-")): p.append("reasoning id must start c- or p-")
    if tr in ("idioms","refs","knowledge"):
        ex=x.get("ex",[])
        if len(ex)!=2: p.append("need exactly 2 examples")
        c=x.get("cloze") or {}
        if c.get("s","").count("___")!=1 or not c.get("a"): p.append("cloze needs one ___ and answer")
        if tr!="refs" and stem_in(x["term"],x["def"]): p.append("def contains the term")
        if "syn" not in x or "ant" not in x: p.append("syn and ant lists required (may be empty)")
    if tr=="refs" and not x.get("story"): p.append("refs need story")
    if tr=="knowledge" and (not x.get("why") or not x.get("domain")): p.append("knowledge needs why and domain")
    if tr=="roots" and len(x.get("words",[]))!=4: p.append("roots need exactly 4 words")
    if i.startswith("c-") and len(x.get("tests",[]))!=2: p.append("concepts need exactly 2 tests")
    if i.startswith("p-"):
        o=x["options"]
        if len(o)!=6 or not 0<=x["answer"]<=5: p.append("need 6 options and answer 0-5")
        if len({s.strip().lower() for s in o})!=len(o): p.append("duplicate options")
    return p
if __name__=="__main__":
    X=json.load(open(sys.argv[1])); ids=set(); P=0
    from collections import Counter
    for x in X:
        pr=check(x)
        if x.get("id") in ids: pr.append("duplicate id")
        ids.add(x.get("id"))
        for m in pr: print("PROBLEM",x.get("id"),"-",m); P+=1
        if x.get("def") and x.get("track")!="roots":
            h=hard_words(x["def"],3)
            if h: print("warning",x["id"],"- plain-word flag:",", ".join(h))
    if any(str(x.get("id","")).startswith("p-") for x in X): print("answer positions:",Counter(x["answer"] for x in X if str(x["id"]).startswith("p-")))
    print(f"{len(X)} items, {P} problems")
