import json, re, random
random.seed(42)
V=json.load(open("../sp/cards.json"))
P=["yo","tú","usted / él / ella","nosotros","ustedes / ellos"]
T=["Present","Preterite","Imperfect","Future","Conditional","Present perfect","Pluperfect","Present subjunctive","Imperfect subjunctive","Command (+)","Command (−)"]
DIS={"Present":["Preterite","Imperfect","Present subjunctive","Conditional"],
"Preterite":["Imperfect","Present","Pluperfect","Present subjunctive"],
"Imperfect":["Preterite","Present","Imperfect subjunctive","Future"],
"Future":["Conditional","Preterite","Imperfect","Present subjunctive"],
"Conditional":["Future","Imperfect subjunctive","Present","Preterite"],
"Present perfect":["Pluperfect","Present","Imperfect","Future"],
"Pluperfect":["Present perfect","Imperfect","Present","Conditional"],
"Present subjunctive":["Present","Imperfect subjunctive","Future","Preterite"],
"Imperfect subjunctive":["Conditional","Imperfect","Present subjunctive","Preterite"]}
def strip(cell):
    c=cell.split(" / ")[0]; c=re.sub(r"\s*\(.*\)","",c); c=re.sub(r"^no ","",c); c=re.sub(r"^(me|te|se|nos|le|les) ","",c); return c
SET={"T1":["Present"],"T2":["Preterite"],"T3":["Imperfect"],"T4":["Preterite","Imperfect"],"T5":["Future","Conditional"],
"T6":["Present perfect","Pluperfect"],"T7":["Present subjunctive"],"T8":["Imperfect subjunctive"],"T9":["Command (+)","Command (−)"],"T10":T[:9]}
Q=[]
for v in V:
    rows={r["t"]:r for r in v["rows"]}
    for r in v["rows"]:
        t=r["t"]
        # conjugate (typed)
        for pi,cell in enumerate(r["f"]):
            if cell=="—" or "/" in cell: continue
            ans=[cell] if "(" not in cell else [re.sub(r"\s*\(.*\)","",cell), re.search(r"\((.*)\)",cell).group(1)]
            Q.append({"id":f"cj:{v['v']}:{t}:{pi}","k":"conj","tense":t,"v":v["v"],"g":v["g"],"pi":pi,"a":ans})
        if t not in DIS or not r.get("cz"): continue
        a,b=r["cz"]; blank=r["es"][a:b]
        pis=[pi for pi,c in enumerate(r["f"]) if c!="—" and strip(c).lower()==blank.lower()]
        if not pis: continue
        pi=pis[0]
        opts=[blank]; used=[t]
        for dt in DIS[t]:
            c=rows[dt]["f"][pi]
            if c=="—": continue
            f=strip(c)
            if blank[0].isupper(): f=f[0].upper()+f[1:]
            if f.lower() in [o.lower() for o in opts]: continue
            opts.append(f); used.append(dt)
            if len(opts)==4: break
        if len(opts)==4:
            Q.append({"id":f"pk:{v['v']}:{t}","k":"pick","tense":t,"v":v["v"],"g":v["g"],"pi":pi,"es":r["es"],"en":r["en"],"cz":r["cz"],"opts":opts,"optT":used})
        # identify: options are tense names; skip if the blank equals the same person's form in a distractor tense
        names=[t]
        for dt in DIS[t]:
            c=rows[dt]["f"][pi]
            if c!="—" and strip(c).lower()==blank.lower(): continue
            names.append(dt)
            if len(names)==4: break
        if len(names)==4 and not any(strip(rows[x]["f"][pi]).lower()==blank.lower() for x in T[:9] if x!=t and rows[x]["f"][pi]!="—"):
            Q.append({"id":f"id:{v['v']}:{t}","k":"ident","tense":t,"v":v["v"],"g":v["g"],"pi":pi,"es":r["es"],"en":r["en"],"cz":r["cz"],"opts":names})
    # commands: choose the right usted command
    for t in ["Command (+)","Command (−)"]:
        r=rows[t]; u=r["f"][2]
        if u=="—": continue
        neg=t.endswith("−)")
        cand=[u, r["f"][1], ("no " if neg else "")+strip(rows["Present"]["f"][2]) if not neg else "no "+strip(rows["Present"]["f"][2]), ("no " if neg else "")+re.sub(r"se$","",v["v"]) ]
        if v["v"].endswith("se") and not neg: cand[3]=v["v"]
        # present with reflexive pronoun for reflexive verbs
        if v["v"].endswith("se"):
            cand[2]=("no " if neg else "")+"se "+strip(rows["Present"]["f"][2])
            cand[3]=("no " if neg else "")+v["v"]
        cand=[c for i,c in enumerate(cand) if c and c not in cand[:i]]
        if len(cand)==4 and r["f"][1]!="—":
            Q.append({"id":f"cm:{v['v']}:{t}","k":"cmd","tense":t,"v":v["v"],"g":v["g"],"neg":neg,"opts":cand,"es":r["es"],"en":r["en"]})
from collections import Counter
print(Counter(q["k"] for q in Q), len(Q))
json.dump(Q,open("tenseQ.json","w"),ensure_ascii=False,indent=0)
# review file for pick/ident
with open("tense_review.txt","w") as f:
    for q in Q:
        if q["k"]=="pick":
            a,b=q["cz"]; f.write(f'{q["id"]} | {q["es"][:a]}___{q["es"][b:]} | EN: {q["en"]} | correct: {q["opts"][0]} ({q["tense"]}) | distractors: '+"; ".join(f"{o} ({t})" for o,t in zip(q["opts"][1:],q["optT"][1:]))+"\n")
        if q["k"]=="cmd":
            f.write(f'{q["id"]} | tell a patient (usted): {"don't " if q["neg"] else ""}{q["g"]} | correct: {q["opts"][0]} | distractors: {"; ".join(q["opts"][1:])}\n')
