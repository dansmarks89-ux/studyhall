import json, glob, re, collections, spacy
nlp = spacy.load("en_core_web_sm", disable=["ner", "parser"])
cards = json.load(open("/tmp/wp/pipe/all_final.json"))
pas = []
pas = json.load(open("/tmp/wp/pipe/passages_final.json"))
def texts():
    for x in cards:
        for k in ("def", "also", "note", "story", "why", "scenario", "fix", "origin", "q"):
            if isinstance(x.get(k), str): yield x[k]
        for e in x.get("ex") or []: yield e
        if x.get("cloze"): yield x["cloze"]["s"].replace("___", "")
        for t in x.get("tests") or []: yield t["s"]
        for w in x.get("words") or []: yield w["m"]
    for p in pas:
        yield p["text"]
        for q in p["qs"]: yield q["q"]; yield q["why"]
POS = {"NOUN": "noun", "VERB": "verb", "ADJ": "adjective", "ADV": "adverb"}
import wn
from wordfreq import zipf_frequency
W = wn.Wordnet('oewn:2024'); PM = {"noun": "n", "verb": "v", "adjective": "a", "adverb": "r"}
VALID = {}
from wn.morphy import Morphy
MORPHY = Morphy(W)
def wnpos(w):
    if w not in VALID:
        ps = set()
        for s in W.synsets(w): ps.add({"n":"noun","v":"verb","a":"adjective","s":"adjective","r":"adverb"}[s.pos])
        VALID[w] = ps
    return VALID[w]
RC = {}
def resolve(surface, lem, pos):
    key = (surface, lem, pos)
    if key in RC: return RC[key]
    r = []
    for w in (lem, surface):
        if pos in wnpos(w): r = [w + "|" + pos]; break
    if not r:
        for w in (lem, surface):
            if wnpos(w): r = [w + "|" + p for p in sorted(wnpos(w))]; break
    if not r and zipf_frequency(lem, "en") >= 3: r = [lem + "|" + pos]
    if pos in ("noun", "verb", "adjective", "adverb"):
        for m in MORPHY(surface, PM[pos]).get(PM[pos], ()):
            k2 = m + "|" + pos
            if k2 not in r and pos in wnpos(m): r.append(k2)
    RC[key] = r; return r
T = list(set(texts()))
surf = collections.defaultdict(set); freq = collections.Counter()
for doc in nlp.pipe(T, batch_size=256):
    for t in doc:
        if t.pos_ not in POS or not re.fullmatch(r"[A-Za-z][a-z'-]*[a-z]|[a-z]", t.text): continue
        if t.is_stop: continue
        for k in resolve(t.text.lower(), t.lemma_.lower(), POS[t.pos_]):
            surf[t.text.lower()].add(k); freq[k] += 1
card = {}
for x in cards:
    if x["track"] == "vocab": card[x["term"].lower() + "|" + x["pos"]] = x["id"]
keys = set(freq)
need = sorted(k for k in keys if k not in card)
json.dump({"surf": {s: sorted(v) for s, v in surf.items()}, "freq": freq, "card": card}, open("/tmp/wp/gloss/inventory.json", "w"))
print("surface forms", len(surf), "lemma|pos", len(keys), "covered by cards", len(keys) - len(need), "need senses", len(need))
