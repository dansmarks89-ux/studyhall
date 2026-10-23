import json, sys, re
inp = json.load(open(sys.argv[1])); out = json.load(open(sys.argv[2])); P = 0
for it in inp:
    k = it["k"]; w = k.split("|")[0]
    if k not in out: print("PROBLEM missing", k); P += 1; continue
    s = out[k]
    if not isinstance(s, list) or len(s) > 3: print("PROBLEM need a list of 0-3 senses:", k); P += 1; continue
    stem = w[:max(4, len(w) - 2)] if len(w) > 4 else w
    for x in s:
        n = len(x.split())
        if not 3 <= n <= 14: print("PROBLEM", k, f"sense has {n} words:", x); P += 1
        if re.search(r"\b" + re.escape(stem), x.lower()): print("PROBLEM", k, "sense contains the word:", x); P += 1
extra = set(out) - {i["k"] for i in inp}
if extra: print("PROBLEM keys not in input:", list(extra)[:5]); P += 1
print(f"{len(out)} entries, {sum(1 for v in out.values() if not v)} empty, {P} problems")
