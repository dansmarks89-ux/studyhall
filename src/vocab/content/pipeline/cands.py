import json, re, random
from wordfreq import top_n_list, zipf_frequency
from nltk.corpus import wordnet as wn
words = top_n_list('en', 200000)
out = []
for rank, w in enumerate(words):
    if not re.fullmatch(r"[a-z]{3,}", w): continue
    syns = wn.synsets(w)
    if not syns: continue
    # must be a lemma (base form) in WordNet, lowercase (not just a proper noun)
    poss = sorted({s.pos().replace('s','a') for s in syns if any(l.name()==w for l in s.lemmas())})
    if not poss: continue
    out.append({"w": w, "z": zipf_frequency(w, 'en'), "pos": poss, "n": len(out)})
json.dump(out, open("lemmas.json","w"))
print(len(out))
import collections
c = collections.Counter(round(x["z"]*2)/2 for x in out)
for k in sorted(c, reverse=True): print(k, c[k], [x["w"] for x in out if round(x["z"]*2)/2==k][:: max(1,c[k]//12)][:12])
