"""Validate a Study Hall Cantonese or Korean level file.

    python3 check_level.py yue path/to/L3.json      # Cantonese
    python3 check_level.py ko  path/to/L3.json      # Korean
    python3 check_level.py ko  path/to/L3.json --pron   # also print every Korean "said like" for review

Exit code 0 = no ERRORs. WARN lines must be read and either fixed or left on purpose.
"""
import json, re, sys, os
from collections import Counter

LANG, PATH = sys.argv[1], sys.argv[2]
SHOWPRON = "--pron" in sys.argv
L = json.load(open(PATH, encoding="utf-8"))
errs, warns = [], []
E = lambda m: errs.append(m)
W = lambda m: warns.append(m)

SKILLS = {
 "yue": ["g:particles","g:aspect","g:measure","g:neg","g:question","g:order","g:numbers","g:time","g:modal","g:compare","g:connect","g:pron","g:place","s:tones","s:listen","s:vocab","s:phrase"],
 "ko":  ["g:particles","g:endings","g:tense","g:neg","g:numbers","g:counters","g:question","g:order","g:connect","g:honor","g:want","g:place","g:compare","s:listen","s:vocab","s:phrase","s:read"],
}[LANG]
COUNTS = {"gap": 16, "pick": 8, "tiles": 12, "listen": 10, "dlg": 5}

# ---------------- target-language text ----------------
CJK = re.compile(r"[㐀-䶿一-鿿豈-﫿\U00020000-\U0002ffff]")
HANGUL = re.compile(r"[가-힣]")
if LANG == "yue":
    import ToJyutping, pycantonese
    def ctx_tj(s):
        return [j for c, j in ToJyutping.get_jyutping_list(s) if CJK.match(c)]
    def ctx_pc(s):
        out = []
        for w, j in pycantonese.characters_to_jyutping(s):
            n = len(CJK.findall(w))
            if not n: continue
            sy = re.findall(r"[a-z]+[1-6]", j or "")
            out += sy if len(sy) == n else [None] * n
        return out

seen_text = []  # every target string, for the pronunciation pass

def T(x, where, gap_ok=False):
    """Check one target-language text. Returns the display string."""
    if LANG == "yue":
        if not (isinstance(x, list) and len(x) == 2 and all(isinstance(s, str) for s in x)):
            E(f"{where}: Cantonese text must be [characters, jyutping], got {x!r}"); return ""
        zh, jp = x
        if "___" in zh or "___" in jp:
            if not gap_ok: E(f"{where}: ___ only allowed in a gap question")
            if zh.count("___") != 1 or jp.count("___") != 1: E(f"{where}: exactly one ___ in both characters and jyutping")
        if re.search(r"[0-9]", zh): E(f"{where}: write numbers in Chinese characters, not digits: {zh}")
        if re.search(r"[A-Z]", jp) and not re.search(r"[A-Za-z]", zh): E(f"{where}: jyutping must be lowercase: {jp}")
        chars = CJK.findall(zh)
        latin_zh = re.findall(r"[A-Za-z]+", zh.replace("___", ""))
        toks = jp.replace("___", " ").replace(",", " ").replace(".", " ").replace("?", " ").replace("!", " ").split()
        syl = [t for t in toks if re.fullmatch(r"[a-z]+[1-6]", t)]
        other = [t for t in toks if not re.fullmatch(r"[a-z]+[1-6]", t)]
        if [o for o in other if o not in latin_zh and o not in ("…", "/", "-")]:
            E(f"{where}: jyutping has non-syllable tokens {other} (every syllable needs a tone number 1-6): {jp}")
        if len(chars) != len(syl):
            E(f"{where}: {len(chars)} characters but {len(syl)} jyutping syllables: {zh} | {jp}"); return zh
        # per-character dictionary check (on the sentence with the gap removed)
        plain = zh.replace("___", "")
        a, b = ctx_tj(plain), ctx_pc(plain)
        for i, (c, s) in enumerate(zip(chars, syl)):
            cands = []
            try:
                cands = [j for _, js in ToJyutping.get_jyutping_candidates(c) for j in js]
            except Exception:
                pass
            if not cands:
                W(f"{where}: no dictionary reading for {c} (you wrote {s}); double-check")
            elif s not in cands:
                E(f"{where}: {c} = {s} is not a dictionary reading (readings: {', '.join(cands[:6])}) in {zh}")
            elif (i < len(a) and s != a[i]) and (i < len(b) and s != b[i]):
                W(f"{where}: {c} = {s}, both dictionaries prefer {a[i]}/{b[i]} here: {zh} | {jp}")
        seen_text.append(zh)
        return zh
    else:
        if not isinstance(x, str) or not x.strip():
            E(f"{where}: Korean text must be a non-empty string, got {x!r}"); return ""
        if "___" in x and not gap_ok: E(f"{where}: ___ only allowed in a gap question")
        if re.search(r"[A-Za-z]", x.replace("Dan", "")): W(f"{where}: Latin letters in Korean text: {x}")
        if not HANGUL.search(x.replace("___", "")): E(f"{where}: no Hangul in {x!r}")
        if "___" not in x: seen_text.append(x.strip())
        return x

TAG = re.compile(r"\{\{(.+?)\}\}")
def prose(text, where):
    """Prose fields may mention target-language text only inside {{...}} tags."""
    if not isinstance(text, str): return
    for m in TAG.finditer(text):
        inner = m.group(1)
        if LANG == "yue":
            if inner.count("|") != 1: E(f"{where}: inline tag must be {{{{中文|jyut ping}}}}, got {{{{{inner}}}}}"); continue
            T(inner.split("|"), where + " inline")
        else:
            T(inner, where + " inline")
    rest = TAG.sub("", text)
    bare = (CJK if LANG == "yue" else HANGUL).findall(rest)
    if bare: E(f"{where}: target-language text outside {{{{...}}}} tags: {''.join(bare)[:20]}")

def fill(q, opt):
    """The full sentence for a gap item with the answer filled in."""
    if LANG == "yue":
        return [q[0].replace("___", opt[0]), q[1].replace("___", opt[1])]
    return q.replace("___", opt)

def need(o, k, typ, where):
    if k not in o: E(f"{where}: missing '{k}'"); return False
    if typ and not isinstance(o[k], typ): E(f"{where}: '{k}' should be {typ.__name__}"); return False
    return True

def skills(it, where):
    sk = it.get("sk")
    if not isinstance(sk, list) or not (1 <= len(sk) <= 3): E(f"{where}: 'sk' must be a list of 1-3 skill ids"); return
    for s in sk:
        if s not in SKILLS: E(f"{where}: unknown skill {s} (allowed: {', '.join(SKILLS)})")

def options(it, where, n, kind):
    if not need(it, "opts", list, where): return
    o = it["opts"]
    if len(o) != n: E(f"{where}: needs exactly {n} options, has {len(o)}")
    if not (isinstance(it.get("a"), int) and 0 <= it["a"] < len(o)): E(f"{where}: 'a' must be an index into opts")
    if kind == "en":
        if not all(isinstance(x, str) and x.strip() for x in o): E(f"{where}: options must be English strings")
        if len({x.strip().lower() for x in o}) != len(o): E(f"{where}: duplicate options")
    else:
        disp = [T(x, f"{where} opt{i}") for i, x in enumerate(o)]
        if len(set(disp)) != len(disp): E(f"{where}: duplicate options")

# ---------------- level ----------------
for k in ["id", "n", "title", "goal", "notes", "vocab", "items", "roleplay"]:
    need(L, k, None, "level")
lid = L.get("id", "?")
if not re.fullmatch(r"L([1-9]|10)", str(lid)): E(f"level id must be L1..L10, got {lid}")

for i, nb in enumerate(L.get("notes", [])):
    w = f"notes[{i}]"
    need(nb, "h", str, w); need(nb, "p", str, w); prose(nb.get("p"), w)
    for j, ex in enumerate(nb.get("ex", [])):
        if not (isinstance(ex, list) and len(ex) == 2 and isinstance(ex[1], str)): E(f"{w}.ex[{j}] must be [text, English]"); continue
        T(ex[0], f"{w}.ex[{j}]")
if not (3 <= len(L.get("notes", [])) <= 6): E(f"notes: 3-6 blocks, has {len(L.get('notes', []))}")

V = L.get("vocab", [])
if not (35 <= len(V) <= 60): E(f"vocab: 35-60 entries, has {len(V)}")
ven = Counter()
vdisp = Counter()
for i, v in enumerate(V):
    w = f"vocab[{i}]"
    if not isinstance(v, dict): E(f"{w}: must be an object"); continue
    need(v, "en", str, w); need(v, "topic", str, w)
    if v.get("old") is None: prose(v.get("note"), w)
    for j in v.get("avoid", []):
        if not (isinstance(j, int) and 0 <= j < len(V) and j != i): E(f"{w}: 'avoid' must list other vocab indices")
    d = T(v.get("t"), w)
    vdisp[d] += 1; ven[v.get("en", "").strip().lower()] += 1
for d, n in vdisp.items():
    if n > 1: E(f"vocab: '{d}' appears {n} times")
for e, n in ven.items():
    if n > 1: E(f"vocab: English '{e}' appears {n} times; make each English gloss distinct so multiple choice has one right answer")

ids = Counter()
cnt = Counter()
for i, it in enumerate(L.get("items", [])):
    t = it.get("t"); iid = it.get("id", f"#{i}"); w = iid
    ids[iid] += 1; cnt[t] += 1
    if not re.fullmatch(rf"{lid}-(gap|pick|tiles|listen|dlg)-\d\d", str(iid)): E(f"{w}: id must look like {lid}-gap-01")
    elif iid.split("-")[1] != t: E(f"{w}: id type doesn't match t={t}")
    if t == "gap":
        q = T(it.get("q"), w + " q", gap_ok=True)
        if "___" not in (q or ""): E(f"{w}: q needs ___")
        need(it, "en", str, w); need(it, "why", str, w); prose(it.get("why"), w); options(it, w, 4, "t"); skills(it, w)
        if isinstance(it.get("opts"), list) and isinstance(it.get("a"), int) and it["a"] < len(it["opts"]):
            T(fill(it["q"], it["opts"][it["a"]]), w + " (filled)")
    elif t == "pick":
        need(it, "q", str, w); need(it, "why", str, w); prose(it.get("q"), w); prose(it.get("why"), w); options(it, w, 4, "t"); skills(it, w)
    elif t == "tiles":
        need(it, "en", str, w); skills(it, w)
        full = T(it.get("full"), w + " full")
        a = it.get("a", [])
        if not (isinstance(a, list) and 3 <= len(a) <= 10): E(f"{w}: 'a' must be a list of 3-10 word tiles")
        disp = [T(x, f"{w} a[{j}]") for j, x in enumerate(a)]
        if len(set(disp)) != len(disp): W(f"{w}: repeated tile {disp}")
        if LANG == "yue":
            if "".join(CJK.findall("".join(disp))) != "".join(CJK.findall(full or "")): E(f"{w}: tiles {disp} don't spell 'full' {full}")
        elif re.sub(r"[?!,.\s]", "", "".join(disp)) != re.sub(r"[?!,.\s]", "", full or ""): E(f"{w}: tiles {disp} don't spell 'full' {full}")
        for k2, alt in enumerate(it.get("alt", [])):
            ad = [T(x, f"{w} alt{k2}[{j}]") for j, x in enumerate(alt)]
            if sorted(ad) != sorted(disp): E(f"{w}: alt{k2} must use exactly the same tiles as 'a'")
        ex = it.get("extra", [])
        if not (isinstance(ex, list) and 2 <= len(ex) <= 3): E(f"{w}: 'extra' needs 2-3 distractor tiles")
        for j, x in enumerate(ex):
            dx = T(x, f"{w} extra[{j}]")
            if dx in disp: E(f"{w}: extra tile {dx} is also in the answer")
    elif t == "listen":
        T(it.get("say"), w + " say"); options(it, w, 6, "en"); skills(it, w); prose(it.get("why"), w)
    elif t == "dlg":
        need(it, "title", str, w)
        turns = it.get("turns", [])
        you = [x for x in turns if x.get("you")]
        if not (4 <= len(turns) <= 8): E(f"{w}: 4-8 turns")
        if not (2 <= len(you) <= 3): E(f"{w}: 2-3 'you' turns")
        if turns and turns[0].get("you"): E(f"{w}: first turn should be the other person")
        for j, tu in enumerate(turns):
            ww = f"{w} turn{j}"
            if tu.get("you"):
                need(tu, "why", str, ww); prose(tu.get("why"), ww); options(tu, ww, 3, "t"); skills(tu, ww)
            else:
                need(tu, "who", str, ww); need(tu, "en", str, ww); T(tu.get("s"), ww)
    else:
        E(f"{w}: unknown type {t}")
for iid, n in ids.items():
    if n > 1: E(f"duplicate id {iid}")
for t, n in COUNTS.items():
    if cnt[t] != n: E(f"items: need exactly {n} '{t}', have {cnt[t]}")

RP = L.get("roleplay", [])
if len(RP) != 2: E(f"roleplay: need 2, have {len(RP)}")
for i, r in enumerate(RP):
    w = f"roleplay[{i}]"
    for k in ["title", "setup", "persona", "opening_en"]: need(r, k, str, w)
    T(r.get("opening"), w + " opening")
    if not (3 <= len(r.get("goals", [])) <= 5): E(f"{w}: 3-5 goals")

if LANG == "ko" and SHOWPRON:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from ko_pron import pron, rom, strip
    ov = L.get("pron", {})
    print("---- said like (override with the level's \"pron\" map) ----")
    for s in sorted(set(seen_text)):
        p = ov.get(s) or pron(s)
        mark = "OVR" if s in ov else ("   " if strip(p) == strip(s) else " ~ ")
        print(f"{mark} {s}  ->  {p}  |  {rom(p)}")
if LANG == "ko":
    for k in L.get("pron", {}):
        if k not in seen_text: W(f"pron override for '{k}' doesn't match any text in the level")

for m in errs: print("ERROR", m)
for m in warns: print("WARN ", m)
print(f"{lid}: {len(errs)} errors, {len(warns)} warnings; items {dict(cnt)}; vocab {len(V)}")
sys.exit(1 if errs else 0)
