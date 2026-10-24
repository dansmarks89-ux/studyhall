import json, logging, unicodedata, re
logging.disable(logging.CRITICAL)
from verbecc import CompleteConjugator
C=CompleteConjugator(lang='es')
T=[("Present","indicativo","presente"),("Preterite","indicativo","pretérito-perfecto-simple"),("Imperfect","indicativo","pretérito-imperfecto"),("Future","indicativo","futuro"),("Conditional","condicional","presente"),("Present perfect","indicativo","pretérito-perfecto-compuesto"),("Pluperfect","indicativo","pretérito-pluscuamperfecto"),("Present subjunctive","subjuntivo","presente"),("Imperfect subjunctive","subjuntivo","pretérito-imperfecto-1"),("Command (+)","imperativo","afirmativo"),("Command (−)","imperativo","negativo")]
PR=["yo","tú","usted","nosotros","ustedes"]
def table(lem):
    src=lem; sub=None
    try: d=json.loads(C.conjugate(lem).to_json())
    except Exception:
        if lem.endswith("ar"):
            d=json.loads(json.dumps(json.loads(C.conjugate("hablar").to_json())).replace("habl",lem[:-2])); sub="hablar"
        else: return None
    out=[]
    for name,m,t in T:
        lst=d["moods"][m][t]; row=[]
        for p in PR:
            e=[x for x in lst if x["pr"]==p]
            if not e: row.append(""); continue
            s=e[0]["c"][0]
            if m!="imperativo": s=s.split(" ",1)[1]
            s=re.sub(r"^no ","",s)
            row.append(s)
        out.append(row)
    if lem=="ir": out[9][3]="vamos"
    if lem=="despertar": out[5:7]=[[f.replace("despierto","despertado") for f in r] for r in out[5:7]]  # verbecc uses the adjective as the participle
    return out
