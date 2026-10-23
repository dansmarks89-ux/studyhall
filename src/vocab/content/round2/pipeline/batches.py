import json, glob, re, collections, spacy, wn
W = wn.Wordnet('oewn:2024')
inv = json.load(open("/tmp/wp/gloss/inventory.json"))
card = inv["card"]; freq = inv["freq"]
PM = {"noun": "n", "verb": "v", "adjective": "a", "adverb": "r"}
need = [k for k in freq if k not in card]
cards = json.load(open("/tmp/wp/pipe/all_final.json"))
pas = []
for f in sorted(glob.glob("/tmp/wp/pas/*.json")): pas += json.load(open(f))
sents = [e for x in cards for e in (x.get("ex") or [])] + [s.strip() for p in pas for s in re.split(r"(?<=[.!?])\s+", p["text"])]
# one short context sentence per key: find by surface forms
inv_s = collections.defaultdict(list)
for s, ks in inv["surf"].items():
    for k in ks: inv_s[k].append(s)
idx = collections.defaultdict(list)
for s in sents:
    for w in set(re.findall(r"[a-z][a-z'-]*", s.lower())): idx[w].append(s)
out = []; nowk = 0
for k in sorted(need):
    lem, pos = k.split("|")
    gl = [x.definition() for x in W.synsets(lem, pos=PM[pos])][:4]
    if pos == "adjective": gl = gl or [x.definition() for x in W.synsets(lem, pos="s")][:4]
    if not gl: nowk += 1
    ctx = min((s for f in inv_s[k] for s in idx.get(f, [])), key=len, default="")
    out.append({"k": k, "wordnet": gl, "context": ctx[:220]})
print("need", len(out), "without WordNet entry", nowk)
n = 16; import os
for i in range(n):
    json.dump(out[i::n], open(f"/tmp/wp/gloss/in-{i}.json", "w"), ensure_ascii=False, indent=0)
print("batch size", len(out[0::n]))
