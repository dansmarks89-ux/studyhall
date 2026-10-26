"""Build the Clinic Spanish course from src/spanish/app.html + src/spanish/data/*.json.

  python3 src/spanish/build.py hosted   -> spanish/index.html (the Study Hall page)
  python3 src/spanish/build.py claude   -> build/clinic-spanish-course.html (claude.ai artifact version)

Both first run content/vocab2/gen_vocab2.py (Everyday words + more clinic words -> data/vocab2.json) and
content/verbs/gen_verbs.py (the verb lessons -> data/verbs.json). The hosted page loads those as
spanish/vocab2.<hash>.json and spanish/verbs.<hash>.json (named by content, so browsers keep them for good);
the previous build's files are kept for pages still open, older ones are deleted. The claude version inlines them,
and inlines shared/ui.css and shared/ui.js too (the hosted page links them).

The two learning paths (Everyday, Clinic) are built here from the existing content, so the same lesson always
has the same words: every unit is a course level (C1..C8, M1..M8) or a word set (Everyday E01..E30, more clinic
words MB1..MB8), split into lessons of up to 5 (short, about 10 minutes) or 7 (long, about 15 minutes) new words (per word two
recognition questions and one recall, plus grammar, sentences and reviews), with a level's grammar notes spread
over its lessons in order. Word keys match the app's: "C1:4" = level C1 vocab[4], "C1:p2" = its phrases[2],
"E01:sv01-de" = an Everyday entry. TENSES says where the grammar that teaches each verb tense sits, found from the
levels' grammar headings: a tense opens in lessons once the lesson with that note is done (or the unit is passed).

Run from anywhere; paths are relative to this file.
"""
import hashlib, json, math, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
subprocess.run([sys.executable, os.path.join(HERE, "content", "vocab2", "gen_vocab2.py")], check=True)
subprocess.run([sys.executable, os.path.join(HERE, "content", "verbs", "gen_verbs.py")], check=True)
def load(name): return json.load(open(os.path.join(HERE, "data", name), encoding="utf-8"))
def dumps(o): return json.dumps(o, ensure_ascii=False, separators=(",", ":"))

LEVELS, VOCAB2 = load("levels.tagged.json"), load("vocab2.json")
LV = {l["id"]: l for l in LEVELS}
SETS = {s["lv"]: s for s in VOCAB2["sets"]}
CONJ = load("conj.json")
CONJ2 = load("conj2.json")
assert not set(CONJ) & set(CONJ2)
CONJ.update(CONJ2)  # conj2 = every other verb the course teaches; reflexive verbs keyed as taught ("sentarse")

# ---------- paths ----------
SIZE = {"short": 5, "long": 7}
def chunks(words, size):
    k = math.ceil(len(words) / size)
    return [words[len(words) * i // k: len(words) * (i + 1) // k] for i in range(k)]
def level_words(l):
    """The level's vocabulary in order, with its phrases spread evenly through it."""
    v = [((i + .5) / len(l["vocab"]), f"{l['id']}:{i}") for i in range(len(l["vocab"]))]
    p = [((i + .5) / len(l["phrases"]), f"{l['id']}:p{i}") for i in range(len(l["phrases"]))]
    return [k for _, k in sorted(v + p, key=lambda x: x[0])]
def unit(uid):
    if uid in LV:
        l = LV[uid]; words, notes = level_words(l), len(l["grammar"])
        u = {"kind": "level", "title": l["title"]}
    else:
        s = SETS[uid]; words, notes = [f"{uid}:{e['id']}" for e in s["entries"]], 0
        u = {"kind": "words", "set": s["id"], "title": s["title"]}
    u["lessons"] = {}
    for ln, size in SIZE.items():
        parts = chunks(words, size)
        at = {}  # grammar note j goes to lesson floor(j * lessons / notes)
        for j in range(notes): at.setdefault(j * len(parts) // notes, []).append(j)
        u["lessons"][ln] = [dict({"id": f"{uid}-{ln[0]}{i + 1}", "w": w}, **({"g": at[i]} if i in at else {})) for i, w in enumerate(parts)]
    return u

every = []
for n in range(1, 9):
    every.append(f"C{n}")
    every += [f"E{k:02d}" for k in range(4 * n - 3, min(4 * n, 30) + 1)]
clinic = "C1 M1 MB1 C2 C3 M2 MB2 C4 M3 MB3 C5 M4 MB4 C6 M5 MB5 C7 M6 MB6 M7 MB7 C8 M8 MB8".split()
assert every[-3:] == ["C8", "E29", "E30"] and len(every) == 38
for i, u in enumerate(clinic):  # each M level comes after its bestAfter level, and its MB set right after it
    if u[0] == "M" and u[1] != "B": assert clinic.index(LV[u]["bestAfter"]) < i and clinic[i + 1] == "MB" + u[1:], u
UNITS = {u: unit(u) for u in dict.fromkeys(every + clinic)}

# ---------- where each verb tense is taught (first grammar heading that matches, in level order) ----------
TAUGHT = [  # tense, heading pattern, track
    ("Present", r"^stem-changing verbs", "conv"), ("Preterite", r"^regular preterite endings", "conv"),
    ("Imperfect", r"^the imperfect: forms", "conv"), ("ir a", r"^ir a \+ infinitive", "conv"),
    ("Future", r"^simple future", "conv"), ("Present perfect", r"^present perfect", "conv"),
    ("Present subjunctive", r"^forming the present subjunctive", "conv"),
    ("Command (+)", r"^commands: tú and usted", "conv"), ("Command (−)", r"^commands: tú and usted", "conv"),
    ("Command (+)", r"^usted commands", "med"), ("Command (−)", r"^negative commands", "med"),  # the clinic path teaches commands in M5
    ("Conditional", r"^the conditional", "conv"), ("Imperfect subjunctive", r"^the imperfect subjunctive", "conv")]
TENSES = {}
for tense, rx, track in TAUGHT:
    hit = next(([l["id"], j] for l in LEVELS if l["track"] == track for j, g in enumerate(l["grammar"]) if re.search(rx, g["h"], re.I)), None)
    assert hit, (tense, rx)
    TENSES.setdefault(tense, []).append(hit)
assert TENSES["Present"] == [["C1", 4]] and TENSES["Command (+)"] == [["C7", 4], ["M5", 0]], TENSES
PATH = {"units": UNITS, "paths": {"every": every, "clinic": clinic}, "tenses": TENSES, "size": SIZE}

# ---------- page ----------
src = open(os.path.join(HERE, "app.html"), encoding="utf-8").read()
for ph, data in [("__LEVELS__", LEVELS), ("__DRILLS__", load("drills.tagged.json")), ("__CONJ__", CONJ),
                 ("__VERBS__", load("cards.tagged.json")), ("__PATH__", PATH)]:
    assert src.count(ph) == 1, ph
    src = src.replace(ph, dumps(data))
LAZY = {"__VOCAB2__": ("vocab2", dumps(VOCAB2)), "__VERBLESSONS__": ("verbs", dumps(load("verbs.json")))}   # loaded after the page
for ph in LAZY: assert src.count(ph) == 1, ph
SHARED = '<link rel="stylesheet" href="../shared/ui.css">\n<script src="../shared/ui.js"></script>'
assert src.count(SHARED) == 1 and src.count("<!--HOSTED-->") == 1

target = sys.argv[1] if len(sys.argv) > 1 else ""
if target == "claude":
    out = os.path.join(REPO, "build", "clinic-spanish-course.html"); os.makedirs(os.path.dirname(out), exist_ok=True)
    shared = lambda f: open(os.path.join(REPO, "shared", f), encoding="utf-8").read()
    src = src.replace(SHARED, f"<style>\n{shared('ui.css')}</style>\n<script>\n{shared('ui.js')}</script>").replace("<!--HOSTED-->", "")
    for ph, (_, body) in LAZY.items(): src = src.replace(ph, body)
    open(out, "w", encoding="utf-8").write(src)
elif target == "hosted":
    OUT = os.path.join(REPO, "spanish"); os.makedirs(OUT, exist_ok=True)
    HASHED = re.compile(r"(?:vocab2|verbs)\.[0-9a-f]{10}\.json")
    INDEX = os.path.join(OUT, "index.html")
    keep = set(HASHED.findall(open(INDEX, encoding="utf-8").read())) if os.path.exists(INDEX) else set()
    for ph, (stem, body) in LAZY.items():
        b = body.encode("utf-8"); name = f"{stem}.{hashlib.sha256(b).hexdigest()[:10]}.json"
        open(os.path.join(OUT, name), "wb").write(b); keep.add(name)
        print("wrote", name, len(b), "bytes")
        src = src.replace(ph, json.dumps(name))
    for f in os.listdir(OUT):
        if HASHED.fullmatch(f) and f not in keep: os.remove(os.path.join(OUT, f))
    def sub(old, new):
        global src
        assert src.count(old) == 1, old
        src = src.replace(old, new)
    # messages that mention claude.ai
    sub('return "Claude isn\'t available on this page (permission was declined or Claude is turned off for your account). The rest of the course works without it.";',
        'return (e&&e.message)||"You don\'t have AI access for this course. The rest of the course works without it.";')
    sub('if(code==="rate_limited") return "Too many requests right now, or your Claude usage limit was reached. Try again in a little while.";',
        'if(code==="rate_limited") return (e&&e.message)||"Too many requests right now. Try again in a little while.";')
    sub('if(code==="session_expired") return "Your session expired. Sign in to Claude again, then reload this page.";',
        'if(code==="session_expired") return "You were signed out. Reload this page to sign in again.";')
    sub('return "The connection to Claude failed. Try again.";',
        'return ((e&&e.message)||"Something went wrong.")+" Try again.";')
    sub(" It uses your Claude usage, and the first time it asks your permission.</p>", " Each person gets a set number of AI replies per day.</p>")
    sub("Claude reads your record and tells you what to work on next. Uses your Claude usage.</p>", "Claude reads your record and tells you what to work on next.</p>")
    sub("<!--HOSTED-->", '<link rel="manifest" href="../manifest.webmanifest">\n<link rel="icon" href="../icons/icon-192.png">\n'
        '<link rel="apple-touch-icon" href="../icons/apple-touch-icon.png">\n<meta name="apple-mobile-web-app-capable" content="yes">\n'
        '<meta name="mobile-web-app-capable" content="yes">\n<meta name="apple-mobile-web-app-title" content="Study Hall">\n'
        '<script src="../shared/supabase.js"></script>\n<script src="../shared/sh.js"></script>\n'
        '<script>SH.install("spanish");</script>\n<script src="../shared/voice.js"></script>')
    out = INDEX
    open(out, "w", encoding="utf-8").write(src)
else:
    sys.exit("target: claude | hosted")
print("wrote", out, os.path.getsize(out))
