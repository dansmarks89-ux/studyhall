import json, re, cmudict
D = cmudict.dict()
V = {"AA","AE","AH","AO","AW","AY","EH","ER","EY","IH","IY","OW","OY","UH","UW"}
ONS = {tuple(o.split()) for o in """P R|P L|B R|B L|T R|D R|K R|K L|G R|G L|F R|F L|TH R|SH R|S P|S T|S K|S M|S N|S L|S W|S P R|S T R|S K R|S P L|S K W|T W|D W|K W|G W|TH W|P Y|B Y|K Y|G Y|F Y|V Y|M Y|HH Y|S K Y|S P Y""".split("|")}
def legal(c):
    return len(c) <= 1 and (not c or c[0] != "NG") or tuple(c) in ONS
def sylls(ph):
    base = [re.sub(r"\d", "", p) for p in ph]
    nuc = [i for i, p in enumerate(base) if p in V]
    if not nuc: return None
    out = []; start = 0
    for k, i in enumerate(nuc):
        if k + 1 < len(nuc):
            j = nuc[k + 1]; cons = list(range(i + 1, j)); split = j
            for s in range(i + 1, j + 1):
                if legal(base[s:j]): split = s; break
            out.append(ph[start:split]); start = split
        else:
            out.append(ph[start:])
    return out
IPA = {"AA":"ɑ","AE":"æ","AO":"ɔ","AW":"aʊ","AY":"aɪ","EH":"ɛ","EY":"eɪ","IH":"ɪ","IY":"i","OW":"oʊ","OY":"ɔɪ","UH":"ʊ","UW":"u",
       "B":"b","CH":"tʃ","D":"d","DH":"ð","F":"f","G":"ɡ","HH":"h","JH":"dʒ","K":"k","L":"l","M":"m","N":"n","NG":"ŋ","P":"p","R":"r","S":"s","SH":"ʃ","T":"t","TH":"θ","V":"v","W":"w","Y":"j","Z":"z","ZH":"ʒ"}
RS = {"AA":"ah","AE":"a","AO":"aw","AW":"ow","AY":"eye","EH":"eh","EY":"ay","IH":"ih","IY":"ee","OW":"oh","OY":"oy","UH":"uu","UW":"oo",
      "B":"b","CH":"ch","D":"d","DH":"th","F":"f","G":"g","HH":"h","JH":"j","K":"k","L":"l","M":"m","N":"n","NG":"ng","P":"p","R":"r","S":"s","SH":"sh","T":"t","TH":"th","V":"v","W":"w","Y":"y","Z":"z","ZH":"zh"}
def ipa_p(p):
    b = re.sub(r"\d", "", p); s = p[-1] if p[-1].isdigit() else ""
    if b == "AH": return "ʌ" if s == "1" or s == "2" else "ə"
    if b == "ER": return "ɝ" if s in "12" and s else "ɚ"
    return IPA[b]
def rs_p(p):
    b = re.sub(r"\d", "", p)
    if b == "AH": return "uh"
    if b == "ER": return "ur"
    return RS[b]
def pron(word):
    w = word.lower()
    if w not in D: return None
    ph = D[w][0]; ss = sylls(ph)
    if not ss: return None
    ipa = ""; rs = []
    for s in ss:
        st = next((p[-1] for p in s if p[-1].isdigit()), "0")
        ipa += ("ˈ" if st == "1" and len(ss) > 1 else "ˌ" if st == "2" else "") + "".join(ipa_p(p) for p in s)
        r = "".join(rs_p(p) for p in s)
        rs.append(r.upper() if st == "1" and len(ss) > 1 else r)
    return {"ipa": "/" + ipa + "/", "say": "-".join(rs)}
items = json.load(open("pipeline/all_final.json")); n = 0
for x in items:
    t = x["term"]
    if re.fullmatch(r"[A-Za-z]+", t):
        p = pron(t)
        if p: x["pr"] = p; n += 1
json.dump(items, open("pipeline/all_final.json", "w"), ensure_ascii=False)
print("pronunciations:", n, "of", sum(1 for x in items if re.fullmatch(r"[A-Za-z]+", x["term"])))
for w in ["obsequious","candid","ubiquitous","pusillanimous","advocate","entrepreneur","extraordinary"]: print(w, pron(w))
