"""Writes src/vocab/data/pron.json: {word: "respelling|IPA"} for every plain word (letters, one inner apostrophe) in
the CMU Pronouncing Dictionary that also appears in the wordfreq English word list (this drops most names). Look up
uses it for words that have no card. Run from this folder:  python3 pron_all.py   (pip cmudict wordfreq)"""
import json, re
from wordfreq import zipf_frequency
from pronlib import D, pron

out = {}
for w in sorted(D):
    if re.fullmatch(r"[a-z]+(?:'[a-z]+)?", w) and zipf_frequency(w, "en") > 0:
        p = pron(w)
        if p: out[w] = p["say"] + "|" + p["ipa"]
json.dump(out, open("../../data/pron.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print(len(out), "words")
