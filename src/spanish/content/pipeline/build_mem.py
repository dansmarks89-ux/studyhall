import json, sys, re, collections
sys.path.insert(0, ".")
from conj import table, T
TN = [t[0] for t in T]
L = "../course/levels/"
ORDER = [f"C{i}" for i in range(1,9)] + [f"M{i}" for i in range(1,9)]
TSK = {"Present":"t:pres","Preterite":"t:pret","Imperfect":"t:imp","Future":"t:fut","Conditional":"t:cond","Present perfect":"t:pperf",
       "Pluperfect":"t:plup","Present subjunctive":"t:psub","Imperfect subjunctive":"t:isub","Command (+)":"t:cmd","Command (−)":"t:cmd"}
# ---- levels with tags ----
levels=[]; lemmas=set()
for lid in ORDER:
    lv=json.load(open(L+lid+".json")); tg=json.load(open(L+lid+".tags.json"))
    assert set(tg)=={i["id"] for i in lv["items"]}, lid
    for it in lv["items"]:
        t=tg[it["id"]]
        it["sk"]=t["sk"]; it["w"]=[f"{lid}:{i}" for i in t.get("vw",[])]
        if "lem" in t: it["lem"],it["tn"],it["pn"]=t["lem"],t["tn"],t["pn"]; lemmas.add(t["lem"])
        if "oe" in t: it["oe"]={int(k):v for k,v in t["oe"].items()}
        if it["t"]=="dlg":
            for k,tt in t.get("turns",{}).items():
                turn=it["turns"][int(k)]; assert turn.get("you"), (it["id"],k)
                turn["sk"]=tt.get("sk",t["sk"]); turn["oe"]={int(a):b for a,b in tt.get("oe",{}).items()}
                if "lem" in tt: turn["lem"],turn["tn"],turn["pn"]=tt["lem"],tt["tn"],tt["pn"]; lemmas.add(tt["lem"])
            for turn in it["turns"]:
                if turn.get("you"): assert "oe" in turn, (it["id"], "turn missing tags")
    levels.append(lv)
# ---- drills ----
D=json.load(open("../drills/drills.json"))
TQ={q["id"]:q for q in json.load(open("../drills/tenseQ.final.json"))}
CARDS=json.load(open("../sp/cards.json")); CV={v["v"]:v for v in CARDS}
base=lambda v: v[:-2] if v.endswith("se") else v
for v in CARDS: lemmas.add(base(v["v"]))
def strip_cmd(c): c=re.sub(r"\s*\(.*\)","",c); return c
for it in D["items"]:
    i=it["id"]
    if i.startswith(("pk:","id:","cj:","cm:")):
        q=TQ[i]; tn=q["tense"]; it["tn"]=tn; it["sk"]=[TSK[tn]]
        if i.startswith(("pk:","cj:")): it["lem"]=base(q["v"]); it["pn"]=q["pi"]
        if i.startswith("pk:"):
            it["oe"]={k:"tense:"+t for k,t in enumerate(q["optT"]) if k>0}
            if tn in("Preterite","Imperfect") and any(t in("Preterite","Imperfect") for t in q["optT"][1:]): it["sk"].append("t:pvi")
            it["sk"].append("g:irreg") if False else None
        elif i.startswith("id:"):
            it["oe"]={k:"tense:"+o for k,o in enumerate(it["opts"]) if k>0}
        elif i.startswith("cm:"):
            rows={r["t"]:r for r in CV[q["v"]]["rows"]}
            tu=strip_cmd(rows[tn]["f"][1]).lower(); oe={}
            for k,o in enumerate(it["opts"]):
                if k==0: continue
                ol=o.lower()
                if ol==tu: oe[k]="register"
                elif ol.endswith(("ar","er","ir","arse","erse","irse")) and " " not in ol.replace("no ",""): oe[k]="infl"
                else: oe[k]="tense:Present"
            it["oe"]=oe; it["sk"]=["t:cmd","g:register"]; it["pn"]=2; it["lem"]=base(q["v"])
    elif i.startswith("v:"):
        _,lid,ix,kind=i.split(":"); it["w"]=[f"{lid}:{ix}"]
        it["sk"]=["s:listen","s:vocab"] if kind=="ls" else ["s:vocab"]
        if it["t"] in("mc","listen"): it["oe"]={k:"word" for k in range(1,len(it["opts"]))}
    elif i.startswith("p:"):
        it["sk"]=["s:phrase"]; it["oe"]={k:"word" for k in range(1,len(it["opts"]))}
miss=[it["id"] for it in D["items"] if "sk" not in it]
assert not miss, miss[:5]
# ---- verb cards: blank person index ----
PR=["yo","tú","usted","nosotros","ustedes"]
def stripf(c):
    c=c.split(" / ")[0]; c=re.sub(r"\s*\(.*\)","",c); c=re.sub(r"^no ","",c); c=re.sub(r"^(me|te|se|nos|le|les) ","",c); return c
for v in CARDS:
    for r in v["rows"]:
        if r.get("cz"):
            a,b=r["cz"]; blank=r["es"][a:b].lower()
            pis=[pi for pi,c in enumerate(r["f"]) if c!="—" and stripf(c).lower()==blank]
            r["pi"]=pis[0] if pis else None
# ---- conjugation tables ----
CONJ={}
for l in sorted(lemmas):
    tb=table(l)
    if tb: CONJ[l]=tb
print("levels",len(levels),"lemmas",len(lemmas),"tables",len(CONJ))
json.dump(levels,open("levels.tagged.json","w"),ensure_ascii=False,separators=(",",":"))
json.dump(D,open("drills.tagged.json","w"),ensure_ascii=False,separators=(",",":"))
json.dump(CARDS,open("cards.tagged.json","w"),ensure_ascii=False,separators=(",",":"))
json.dump(CONJ,open("conj.json","w"),ensure_ascii=False,separators=(",",":"))
import os
for f in ["levels.tagged.json","drills.tagged.json","cards.tagged.json","conj.json"]: print(f, os.path.getsize(f))
c=collections.Counter(tuple(sorted(it["oe"].values())) for it in D["items"] if it["id"].startswith("cm:"))
print(c.most_common(4))
print(sum(1 for v in CARDS for r in v["rows"] if r.get("cz") and r.get("pi") is None),"cloze rows without person")
