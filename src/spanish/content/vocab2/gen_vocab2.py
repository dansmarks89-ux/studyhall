"""Build src/spanish/data/vocab2.json: the Everyday vocabulary track (VE01..VE30), extra clinic words
per medical level (VMB1..VMB8) and extra example sentences for the words the course already had.

  python3 src/spanish/content/vocab2/gen_vocab2.py <content dir>

<content dir> holds out/ (writer files) and rev/ (reviewer patches: {"fix":[...], "drop":[...]}).
"""
import json, os, re, sys, unicodedata, glob
HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, "..", "..", "data")
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "src")
def load(name):
    p = os.path.join(SRC, "out", name); X = json.load(open(p))
    r = os.path.join(SRC, "rev", name)
    if os.path.exists(r):
        R = json.load(open(r)); fix = {f["id"]: f for f in R.get("fix", [])}; drop = set(R.get("drop", []))
        ids = {x["id"] for x in X}
        X = [fix.get(x["id"], x) for x in X if x["id"] not in drop] + [f for i, f in fix.items() if i not in ids]  # reviewer may re-add under a new id
    for x in X:  # writers labelled parts of speech two ways
        x["pos"] = POS.get(x.get("pos", ""), x.get("pos", ""))
    return X
POS = {"adj": "adjective", "adv": "adverb", "conj": "conjunction", "prep": "preposition", "pron": "pronoun", "interj": "interjection", "n": "noun", "v": "verb"}
def norm(w):
    w = unicodedata.normalize("NFC", w.lower().strip()); w = re.sub(r"[¿?¡!.,]", "", w)
    return re.sub(r"^(el|la|los|las|un|una)\s+", "", w).strip()
L = json.load(open(os.path.join(DATA, "levels.tagged.json")))
APP = set(json.load(open(os.path.join(SRC, "app_words.json"))))
seen = set(APP)  # duplicates are removed within a track; the Everyday and medical tracks may share a word

def build_set(sid, lv, track, n, title, ents):
    """Compact set; the app builds the questions from these entries at runtime."""
    keep = ("id", "w", "en", "pos", "note", "type", "ex")
    return {"id": sid, "lv": lv, "track": track, "n": n, "title": title, "entries": [{k: e[k] for k in keep if k in e} for e in ents]}

IDS = set()
def dedupe(X):
    keep = []
    for x in X:
        k = norm(x["w"])
        if k in seen: continue
        seen.add(k)
        i, n = x["id"], 2
        while x["id"] in IDS: x["id"] = f"{i}-{n}"; n += 1  # accent pairs (si/sí) can share a slug
        IDS.add(x["id"]); keep.append(x)
    return keep

vsets = []
ev = sorted(glob.glob(os.path.join(SRC, "out", "ev-*.json")), key=lambda p: int(re.findall(r"\d+", os.path.basename(p))[0]))
for p in ev:
    b = int(re.findall(r"\d+", os.path.basename(p))[0]); X = dedupe(load(os.path.basename(p)))
    s = build_set(f"VE{b+1:02d}", f"E{b+1:02d}", "every", b + 1, f"Everyday words {b+1}", X); vsets.append(s)
LVT = {l["id"]: l["title"] for l in L}
seen = set(APP)
for p in sorted(glob.glob(os.path.join(SRC, "out", "med-*.json"))):
    k = int(re.findall(r"\d+", os.path.basename(p))[0]); X = dedupe(load(os.path.basename(p)))
    s = build_set(f"VMB{k}", f"MB{k}", "med", k, f"{LVT['M'+str(k)]}: more clinic words", X); s["after"] = f"VM{k}"; vsets.append(s)
more = {}
for p in sorted(glob.glob(os.path.join(SRC, "out", "extra-*.json"))):
    for x in load(os.path.basename(p)):
        sid, ix = x["id"].rsplit("-", 1)
        more[f"{sid[1:]}:{ix}"] = [[e["es"], e["en"]] for e in x["ex"]]
json.dump({"sets": vsets, "more": more}, open(os.path.join(DATA, "vocab2.json"), "w"), ensure_ascii=False, separators=(",", ":"))
print(len(vsets), "sets", sum(len(s["entries"]) for s in vsets), "words", len(more), "extra-example entries",
      os.path.getsize(os.path.join(DATA, "vocab2.json")) // 1024, "KB")
