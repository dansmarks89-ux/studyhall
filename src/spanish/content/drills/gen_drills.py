import json, re, random, collections
random.seed(7)
LV="../course/levels/"
USE={
"Present":"Now, habits and general truths (*Tomo metoprolol todos los días*). Also used for the near future in speech (*Mañana regreso*).",
"Preterite":"A completed event at a specific point or period in the past: it started and ended (*Ayer me desmayé*). Use it for what happened.",
"Imperfect":"Background, ongoing or repeated past: what was going on, what used to happen, descriptions, age, time (*De niño jugaba fútbol*; *Estaba en casa cuando…*).",
"Future":"Will do (*Mañana le haremos el estudio*); also a guess about now (*¿Dónde estará?*). In conversation *ir a* + infinitive is more common.",
"Conditional":"Would: polite requests (*¿Podría…?*), advice (*Yo en su lugar…*), and the result half of an imaginary *si* sentence.",
"Present perfect":"Past connected to now: experiences (*alguna vez*, *nunca*), *ya* / *todavía no*, *últimamente*, *esta semana*. In Latin America a finished event yesterday uses the preterite instead.",
"Pluperfect":"Had done: one past event that happened before another past event (*Cuando llegó la ambulancia, ya se había despertado*).",
"Present subjunctive":"After wanting, asking, advising, hoping, emotion or doubt about someone else's action (*Quiero que tome…*, *Es importante que…*, *Ojalá…*), and after *cuando / para que / antes de que* for something not yet happened.",
"Imperfect subjunctive":"The same triggers in a past or imaginary frame: *si* + imaginary condition (*Si tuviera fiebre…*), *como si*, and wishes about others told in the past (*Me pidió que estuviera tranquilo*).",
"Command (+)":"Telling someone to do something. With patients use the usted form (same as the present subjunctive: *tome*, *respire*); pronouns attach to the end and the stress gets an accent (*acuéstese*).",
"Command (−)":"Telling someone not to do something: *no* + present subjunctive (*no tome*, *no se mueva*). Pronouns go before the verb.",
}
CLUES=[(r"\b(ayer|anoche|anteayer|la semana pasada|el año pasado|el mes pasado|hace \w+ (días|años|semanas|meses)|en 20\d\d|de repente|esta mañana)\b","a finished moment in the past"),
(r"\b(de niñ[oa]|de joven|antes|siempre|todos los días|cada \w+|mientras|a veces|seguido)\b","habit, background or 'used to'"),
(r"\b(mañana|la próxima|el próximo|en (un|una|dos|tres|unos) \w+)\b","a future time"),
(r"\b(ya|alguna vez|nunca|todavía no|últimamente|esta semana|este año|desde)\b","a time 'up to now' or an experience"),
(r"\bcomo si\b","*como si* always takes the imperfect subjunctive"),
(r"\bsi\b","a *si* (if) clause"),
(r"\b(quiero|quería|necesito|espero|esperaba|ojalá|es importante|es necesario|es normal|es posible|prefiero|le pido|le pedí|me pidió|pidió|le dije|le recomiendo|le recomendé|no creo|temía|tenía miedo de|me preocupaba|para que|antes de que|cuando)\b","a trigger that calls for the subjunctive when it's about another person or something not yet real")]
def clue(es):
    s=es.lower(); out=[]
    for rx,txt in CLUES:
        m=re.search(rx,s)
        if m: out.append(f"*{m.group(0)}* → {txt}")
    return out[:2]
FORMSROW=lambda r:" · ".join(f for f in r["f"] if f!="—")
V=json.load(open("../sp/cards.json")); VB={v["v"]:v for v in V}
TQ=json.load(open("tenseQ.final.json"))
P=["yo","tú","usted / él / ella","nosotros","ustedes / ellos"]
def ex2(tense, avoid):
    c=[(v["v"],r) for v in V for r in v["rows"] if r["t"]==tense and r["es"] and v["v"]!=avoid]
    v,r=random.choice(c); return [r["es"],r["en"]]
items=[]
SETS={"T1":["Present"],"T2":["Preterite"],"T3":["Imperfect"],"T4":["Preterite","Imperfect"],"T5":["Future","Conditional"],"T6":["Present perfect","Pluperfect"],"T7":["Present subjunctive"],"T8":["Imperfect subjunctive"],"T9":["Command (+)","Command (−)"],"T10":list(USE)[:9]}
for q in TQ:
    v=VB[q["v"]]; row=[r for r in v["rows"] if r["t"]==q["tense"]][0]
    why=f"**{q['tense']}.** {USE[q['tense']]}"
    if q["k"] in("pick","ident"):
        cl=clue(q["es"])
        if cl: why+=" Clue: "+"; ".join(cl)+"."
        a,b=q["cz"]
    why+=f" *{q['v']}* in this tense: {FORMSROW(row)}."
    more=[ex2(q["tense"],q["v"])]
    if q["k"]=="pick":
        it={"t":"mc","id":q["id"],"q":q["es"][:a]+"___"+q["es"][b:],"qen":f"{q['en']}  ({q['v']})","opts":q["opts"],"a":0,"why":why,"more":more,"tense":q["tense"],"k":"pick"}
    elif q["k"]=="ident":
        it={"t":"mc","id":q["id"],"q":q["es"][:a]+"*"+q["es"][a:b]+"*"+q["es"][b:],"qen":q["en"]+" — which tense is the verb in italics?","opts":q["opts"],"a":0,"optsEn":True,"why":why,"more":more,"tense":q["tense"],"k":"ident","say":q["es"]}
    elif q["k"]=="conj":
        it={"t":"fill","id":q["id"],"q":"___","prompt":f"{q['v']} · {q['tense']} · {P[q['pi']]}","en":v["g"],"hint":"","a":q["a"],"show":q["a"][0],"say":q["a"][0],"why":why,"more":[[row["es"],row["en"]]] if row["es"] else more,"tense":q["tense"],"k":"conj"}
    else:
        it={"t":"mc","id":q["id"],"q":f"Tell a patient (usted): {q['prompt']}","qen":f"({q['v']})","opts":q["opts"],"a":0,"why":why,"more":[[row["es"],row["en"]]] if row["es"] else [],"tense":q["tense"],"k":"cmd","say":q["opts"][0]}
    items.append(it)
tsets=[]
TT={"T1":"Present","T2":"Preterite","T3":"Imperfect","T4":"Preterite vs. imperfect","T5":"Future and conditional","T6":"Present perfect and pluperfect","T7":"Present subjunctive","T8":"Imperfect subjunctive and si clauses","T9":"Commands","T10":"All tenses mixed"}
for sid,tenses in SETS.items():
    pool=[i["id"] for i in items if i["tense"] in tenses]
    tsets.append({"id":sid,"title":TT[sid],"tenses":tenses,"pool":pool})
# ---------- vocab ----------
vitems=[];vsets=[]
def clean_say(w): return re.sub(r"\s*\(.*?\)","",w).replace("…","").strip()
for t in "CM":
  for k in range(1,9):
    L=json.load(open(f"{LV}{t}{k}.json")); X=json.load(open(f"{LV}{t}{k}.vx.json")); lid=f"{t}{k}"
    ent=[{**x,"w":v[0],"gl":v[1],"exen":x["en"]} for v,x in zip(L["vocab"],X)]
    syn=lambda a,b: a["w"]==b["w"] or a["gl"].lower()==b["gl"].lower() or bool(set(map(str.lower,a.get("type",[])))&set(map(str.lower,b.get("type",[])))) or clean_say(b["w"]).lower() in map(str.lower,a.get("type",[])) or clean_say(a["w"]).lower() in map(str.lower,b.get("type",[]))
    pool=[]
    for i,e in enumerate(ent):
        others=[o for o in ent if not syn(e,o)]
        random.shuffle(others)
        d=others[:3]
        why=f"*{e['w']}* = {e['gl']}." + (f" {e['note']}" if e.get("note") else "")
        more=[[e["ex"],e["exen"]]]
        base=f"v:{lid}:{i}"
        vitems.append({"t":"mc","id":base+":se","q":f"What does *{e['w']}* mean?","opts":[e["gl"]]+[o["gl"] for o in d],"a":0,"optsEn":True,"why":why,"more":more,"say":clean_say(e["w"]),"k":"v2e"})
        vitems.append({"t":"mc","id":base+":es","q":f"Which is Spanish for “{e['gl']}”?","opts":[e["w"]]+[o["w"] for o in d],"a":0,"why":why,"more":more,"say":clean_say(e["w"]),"k":"e2v"})
        vitems.append({"t":"listen","id":base+":ls","say":clean_say(e["w"]),"opts":[e["gl"]]+[o["gl"] for o in d],"a":0,"why":why,"more":more,"k":"listen"})
        ids=[base+":se",base+":es",base+":ls"]
        if e.get("type"):
            vitems.append({"t":"fill","id":base+":ty","q":"___","prompt":f"Type the Spanish for: {e['gl']}","en":"","hint":"","a":e["type"],"show":e["type"][0],"say":e["type"][0],"why":why,"more":more,"k":"type"}); ids.append(base+":ty")
        hd=[o for o in others if o["hit"].lower()!=e["hit"].lower() and o["hit"].lower() not in map(str.lower,e.get("type",[]))][:3]
        if len(hd)==3:
            ex=e["ex"]; j=ex.index(e["hit"])
            vitems.append({"t":"mc","id":base+":ex","q":ex[:j]+"___"+ex[j+len(e["hit"]):],"qen":e["exen"],"opts":[e["hit"]]+[o["hit"] for o in hd],"a":0,"why":why,"more":[],"say":ex,"k":"ex"}); ids.append(base+":ex")
        pool+=ids
    for j,(es,en) in enumerate(L["phrases"]):
        others=[p for p in L["phrases"] if p[0]!=es]; random.shuffle(others)
        base=f"p:{lid}:{j}"
        vitems.append({"t":"mc","id":base+":se","q":f"What does *{es}* mean?","opts":[en]+[o[1] for o in others[:3]],"a":0,"optsEn":True,"why":"","more":[],"say":es,"k":"v2e"})
        vitems.append({"t":"mc","id":base+":es","q":f"How do you say “{en}”?","opts":[es]+[o[0] for o in others[:3]],"a":0,"why":"","more":[],"say":es,"k":"e2v"})
        pool+=[base+":se",base+":es"]
    vsets.append({"id":"V"+lid,"lv":lid,"track":"conv" if t=="C" else "med","n":k,"title":L["title"],"entries":[{"w":e["w"],"en":e["gl"],"ex":e["ex"],"exen":e["exen"],"note":e.get("note","")} for e in ent],"phrases":L["phrases"],"pool":pool})
# sanity: options distinct, correct at 0
bad=[i["id"] for i in items+vitems if i["t"] in("mc","listen") and len(set(o.lower() for o in i["opts"]))!=len(i["opts"])]
print("dup-option items:",len(bad),bad[:8])
items=[i for i in items if i["id"] not in bad]; vitems=[i for i in vitems if i["id"] not in bad]
ok=set(i["id"] for i in items+vitems)
for s in tsets+vsets: s["pool"]=[p for p in s["pool"] if p in ok]
json.dump({"use":USE,"tsets":tsets,"vsets":vsets,"items":items+vitems},open("drills.json","w"),ensure_ascii=False,separators=(",",":"))
print(len(items),len(vitems),[ (s["id"],len(s["pool"])) for s in tsets])
print(min(len(s["pool"]) for s in vsets))
import os;print(os.path.getsize("drills.json"))
