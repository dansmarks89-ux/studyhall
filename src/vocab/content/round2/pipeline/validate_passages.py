import json, re, sys, glob, collections
X=json.load(open(sys.argv[1])); P=0
lv=X[0]["level"] if X else None
W={w["id"]:w for w in json.load(open(f"/tmp/wp/levelwords/L{lv}.json"))}
use=collections.Counter()
def forms_of(w):
    t=w["term"].lower(); fs={t}
    for f in w.get("forms") or []: fs.add(re.sub(r"\s*\(.*","",f).strip().lower())
    base=re.sub(r"e$","",t)
    return fs, base
for x in X:
    pr=[]
    for f in ["id","track","level","title","text","words","qs"]:
        if f not in x: pr.append("missing "+f)
    if pr: print("PROBLEM",x.get("id"),pr); P+=1; continue
    n=len(x["text"].split()); lo,hi=(40,70) if lv<0 else (80,130) if lv<=2 else (110,170)
    if not lo<=n<=hi: pr.append(f"length {n} words, need {lo}-{hi}")
    if len(x["words"])!=6 or len(set(x["words"]))!=6: pr.append("need 6 different target words")
    low=x["text"].lower()
    for wid in x["words"]:
        use[wid]+=1
        if wid not in W: pr.append(f"{wid} is not a word at this level"); continue
        fs,base=forms_of(W[wid])
        if not any(re.search(r"\b"+re.escape(f)+r"\b",low) for f in fs) and not re.search(r"\b"+re.escape(base[:max(4,len(base)-1)]),low):
            pr.append(f"{W[wid]['term']} not found in text")
    qs=x["qs"]
    if len(qs)!=3 or [q.get("kind") for q in qs].count("word")!=2: pr.append("need 2 word + 1 idea question")
    for q in qs:
        if len(q.get("options",[]))!=6 or not 0<=q.get("answer",-1)<=5: pr.append("question needs 6 options + answer")
        elif len({o.strip().lower() for o in q["options"]})!=6: pr.append("duplicate options")
        if q.get("kind")=="word" and q.get("word") not in x["words"]: pr.append("word question must name one of the passage's target words")
        if not q.get("why"): pr.append("missing why")
    for m in pr: print("PROBLEM",x["id"],"-",m); P+=1
over=[w for w,c in use.items() if c>2]
if over: print("PROBLEM words used in more than 2 passages:",over); P+=1
print(f"{len(X)} passages, {len(use)} distinct words, {P} problems")
print("answer positions:",collections.Counter(q["answer"] for x in X for q in x.get("qs",[]) if "answer" in q))
