"""Checks the conversation hints: src/<lang>/content/hints/<level id>.json (one per level that has role-plays) and,
for Spanish, src/spanish/content/hints/quick.json. The builds import load() and stop on any ERROR.

    python3 src/hints_check.py spanish|cantonese|korean     # check one language, print every ERROR and WARN

A level file:  {"roleplay": [{"title": <the role-play's title>, "hints": [<one hint per goal, in the goals' order>]}]}
A hint:        {"en": <what to say, in English>, <the model sentence>, "start": <its first words>}
  Spanish      "es": "¿Dónde vive usted?"
  Cantonese    "t": ["你住喺邊度呀？", "nei5 zyu6 hai2 bin1 dou6 aa3?"]      (characters, Jyutping)
  Korean       "t": "어디에 사세요?"                                        (the build adds the romanization)
"start" is the model's first words exactly as they appear in it, without "…"; the app adds "…". A one-word model
(Cantonese: one or two characters) may have "start": "" and then the hint goes from the idea straight to the model.
quick.json (Spanish only): {"every": hint, "clinic": hint} for the quick chat's goal "Ask one question back".
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CJK = re.compile(r"[㐀-䶿一-鿿豈-﫿\U00020000-\U0002ffff]")
HANGUL = re.compile(r"[가-힣]")
SYL = re.compile(r"[a-z]+[1-6]")


def levels(lang):
    """The course's role-plays per level, from the level sources."""
    d = os.path.join(ROOT, "src", lang, "content", "levels")
    out = {}
    for f in sorted(os.listdir(d)):
        if re.fullmatch(r"[A-Z]\d+\.json", f):   # (not the Spanish .tags / .vx side files)
            L = json.load(open(os.path.join(d, f), encoding="utf-8"))
            if L.get("roleplay"): out[L["id"]] = L["roleplay"]
    return out


def model(lang, h):
    """The model sentence's text (characters for Cantonese)."""
    if lang == "spanish": return h.get("es")
    t = h.get("t")
    return t[0] if lang == "cantonese" and isinstance(t, list) and len(t) == 2 else t if lang == "korean" else None


def check_text(lang, h, where, E, W):
    m = model(lang, h)
    if not isinstance(m, str) or not m.strip():
        E(f"{where}: missing the model sentence ({'es' if lang == 'spanish' else 't'})"); return
    if not isinstance(h.get("en"), str) or not h["en"].strip(): E(f"{where}: missing 'en'")
    s = h.get("start")
    one = not re.search(r"\s", m.strip()) and (lang != "cantonese" or len(CJK.findall(m)) <= 2)   # a one-word model has no start
    if not isinstance(s, str) or (not s.strip() and not one): E(f"{where}: missing 'start'"); return
    if not s: pass
    elif s.endswith(("…", "...")): E(f"{where}: 'start' must not end with … (the app adds it)")
    elif not m.startswith(s): E(f"{where}: 'start' is not the beginning of the model sentence: {s!r} / {m!r}")
    elif len(s) >= len(m.rstrip(".?!。？！")): E(f"{where}: 'start' is the whole sentence; give only its first words")
    elif lang != "cantonese" and m[len(s)] not in " ,": E(f"{where}: 'start' must end at a word boundary: {s!r} / {m!r}")
    if lang == "spanish":
        if re.search(r"[A-Za-zÁÉÍÓÚÑáéíóúñ]$", m): E(f"{where}: end the sentence with . ? or !")
        for a, b in (("¿", "?"), ("¡", "!")):
            if m.count(a) != m.count(b): E(f"{where}: unbalanced {a} {b}: {m}")
        vos = [w for w in re.findall(r"\w+", m.lower()) if w in ("vosotros", "vosotras", "os") or (re.search(r"(áis|éis)$", w) and not w.endswith("séis"))]
        if vos: E(f"{where}: looks like vosotros ({', '.join(vos)}): {m}")
        if len(m.split()) > 22: W(f"{where}: long for a model ({len(m.split())} words)")
    elif lang == "cantonese":
        zh, jp = h["t"]
        if re.search(r"[0-9]", zh): E(f"{where}: write numbers in characters: {zh}")
        chars = CJK.findall(zh)
        toks = re.sub(r"[,.?!…]", " ", jp).split()
        syl = [t for t in toks if SYL.fullmatch(t)]
        latin = re.findall(r"[A-Za-z]+", zh)
        if [t for t in toks if not SYL.fullmatch(t) and t not in latin]: E(f"{where}: Jyutping has tokens that aren't syllables with a tone 1-6: {jp}")
        if len(chars) != len(syl): E(f"{where}: {len(chars)} characters but {len(syl)} Jyutping syllables: {zh} | {jp}"); return
        try:
            import ToJyutping
        except ImportError:
            W("ToJyutping isn't installed: the per-character reading check was skipped"); return
        for c, y in zip(chars, syl):
            cands = [j for _, js in ToJyutping.get_jyutping_candidates(c) for j in js]
            if cands and y not in cands: E(f"{where}: {c} = {y} is not a dictionary reading ({', '.join(cands[:6])}): {zh}")
    else:
        if not HANGUL.search(m): E(f"{where}: no Hangul in {m!r}")
        if re.search(r"[A-Za-z]", m): W(f"{where}: Latin letters in Korean text: {m}")


def load(lang, strict=True):
    """{level id: [[hint per goal] per role-play]} (and "quick" for Spanish). Raises SystemExit on an ERROR when strict."""
    errs, warns = [], []
    E, W = errs.append, warns.append
    d = os.path.join(ROOT, "src", lang, "content", "hints")
    out = {}
    for lid, rps in levels(lang).items():
        p = os.path.join(d, lid + ".json")
        if not os.path.exists(p): E(f"{lid}: no hints file"); continue
        H = json.load(open(p, encoding="utf-8")).get("roleplay")
        if not isinstance(H, list) or len(H) != len(rps): E(f"{lid}: needs {len(rps)} role-plays, has {len(H) if isinstance(H, list) else 0}"); continue
        out[lid] = []
        for i, (r, h) in enumerate(zip(rps, H)):
            if h.get("title") != r["title"]: E(f"{lid} roleplay {i}: title {h.get('title')!r} isn't {r['title']!r}")
            hs = h.get("hints")
            if not isinstance(hs, list) or len(hs) != len(r["goals"]): E(f"{lid} roleplay {i}: needs {len(r['goals'])} hints, one per goal"); continue
            for j, x in enumerate(hs): check_text(lang, x, f"{lid} roleplay {i} goal {j} ({r['goals'][j][:40]})", E, W)
            out[lid].append(hs)
    if lang == "spanish":
        p = os.path.join(d, "quick.json")
        q = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
        for k in ("every", "clinic"):
            if k not in q: E(f"quick.json: missing '{k}'")
            else: check_text(lang, q[k], f"quick {k}", E, W)
        out["quick"] = q
    if strict and errs: sys.exit("hints: " + "\n".join(errs))
    return out, errs, warns


if __name__ == "__main__":
    _, errs, warns = load(sys.argv[1], strict=False)
    for m in errs: print("ERROR", m)
    for m in warns: print("WARN ", m)
    print(f"{len(errs)} errors, {len(warns)} warnings")
    sys.exit(1 if errs else 0)
