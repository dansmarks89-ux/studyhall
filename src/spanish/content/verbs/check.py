"""Checks one verb-lesson entry (the shape in VERBS.md) against the course's verb tables.

  python3 src/spanish/content/verbs/check.py FILE.json [FILE2.json …]   -> lists every problem; exit 1 if any error

check(verb, entry) returns (errors, warnings); gen_verbs.py refuses to build with any error.
"""
import json, re, sys, unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[1] / "data"
sys.path.insert(0, str(HERE.parent / "pipeline"))
from accents import enclitic  # the same written-accent rule as the tables' affirmative commands  # noqa: E402

CONJ = json.loads((DATA / "conj.json").read_text(encoding="utf-8"))
CONJ.update(json.loads((DATA / "conj2.json").read_text(encoding="utf-8")))
ROWS = ["Present", "Preterite", "Imperfect", "Future", "Conditional", "Present perfect", "Pluperfect",
        "Present subjunctive", "Imperfect subjunctive", "Command (+)", "Command (−)"]
TENSES3 = ["Present", "Preterite", "Imperfect", "ir a", "Future", "Conditional", "Present perfect", "Pluperfect",
           "Present subjunctive", "Imperfect subjunctive"]          # three sentences each: stmt, q, neg
CMDS = ["Command (+)", "Command (−)"]
OBJ_TENSES = {"Present", "Preterite", "Imperfect", "Future", "Present perfect", "Present subjunctive"} | set(CMDS)
KINDS = {"stmt", "q", "neg", "obj", "cmd"}
REFL = ["me", "te", "se", "nos", "se"]
PRON = {"me", "te", "se", "nos", "lo", "la", "los", "las", "le", "les"}
GUSTAR = {"gustar", "encantar", "doler", "importar", "interesar", "fascinar", "apetecer"}
WORD = re.compile(r"[\wáéíóúüñÁÉÍÓÚÜÑ]+")


def lc(s): return s.lower()
def plain(s): return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
def words(s): return WORD.findall(lc(s))
def base(v): return v[:-2] if v.endswith("se") else v


def table_form(v, t, p):
    """The table form for tense t, person p ('' if none); 'ir a' is built from ir's present."""
    if t == "ir a":
        ir = CONJ["ir"][0][p]
        return f"{ir} a {v}" if v == base(v) else f"{REFL[p]} {ir} a {base(v)}"
    return CONJ[v][ROWS.index(t)][p]


def ira_forms(v, p):
    ir = CONJ["ir"][0][p]
    return {f"{ir} a {v}"} if v == base(v) else {f"{REFL[p]} {ir} a {base(v)}", f"{ir} a {base(v)}{REFL[p]}"}


def occurs(f, es):
    """f appears exactly once in es as whole words (case-insensitive)."""
    return len(re.findall(rf"(?<![\wáéíóúüñ]){re.escape(lc(f))}(?![\wáéíóúüñ])", lc(es))) == 1


def form_ok(v, s):
    """Is s['f'] the right form (or pronoun chunk) for its tense and person? Returns an error string or None."""
    t, p, k, f = s["t"], s["p"], s["k"], lc(s["f"])
    if t == "ir a":
        if k == "obj":
            return "obj sentences don't use ir a"
        return None if f in ira_forms(v, p) else f"f should be one of {sorted(ira_forms(v, p))}"
    tf = lc(table_form(v, t, p))
    if not tf:
        return f"{v} has no {t} form for person {p}"
    if t == "Command (+)":
        if f == tf:
            return None
        rest = plain(f)[len(plain(tf)):] if plain(f).startswith(plain(tf)) else None
        prons = re.fullmatch(r"(me|te|se|nos|le|les)?(lo|la|los|las)?", rest or "#")
        if rest and prons and enclitic(tf, rest) == f:
            return None
        if rest and prons:
            return f"with the pronoun attached it is written {enclitic(tf, rest)!r}"
        return f"f should be {tf!r} (or it with a pronoun attached)"
    want = ("no " + tf) if t == "Command (−)" else tf
    if k != "obj":
        return None if f == want else f"f should be {want!r}"
    got, need = [w for w in f.split() if w not in PRON], [w for w in want.split() if w not in PRON]
    if got != need or not set(f.split()) & PRON - set(want.split()):
        return f"an obj f is the pronoun(s) plus {want!r} as one chunk, e.g. 'lo {need[-1]}'"
    return None


def check(v, e):
    err, warn = [], []
    E = lambda m: err.append(f"{v}: {m}")
    W = lambda m: warn.append(f"{v}: {m}")
    if v not in CONJ:
        return [f"{v}: no verb table"], []
    for key in ("en", "note", "uses", "cmd", "s"):
        if key not in e:
            E(f"missing {key}")
    if err:
        return err, warn
    if not (0 < len(e["en"]) <= 60): E("en: 1-60 characters")
    if not (20 <= len(e["note"]) <= 260): E("note: 20-260 characters")
    if e["cmd"] not in ("both", "pos", "neg", "none"): E("cmd must be both, pos, neg or none")
    if set(e) - {"en", "note", "uses", "cmd", "third", "s"}: E(f"unknown fields {sorted(set(e) - {'en', 'note', 'uses', 'cmd', 'third', 's'})}")
    third = v in GUSTAR or e.get("third") is True     # said of things: only the usted/él/ella and ustedes/ellos forms are practiced
    if not (2 <= len(e["uses"]) <= 3): E("uses: 2 or 3")
    for u in e["uses"]:
        if set(u) != {"es", "en", "x", "xen"} or not all(isinstance(u[x], str) and u[x].strip() for x in u):
            E(f"use {u}: needs es, en, x, xen")
    seen, by = set(), {}
    for i, s in enumerate(e["s"]):
        tag = f"s[{i}] {s.get('es', '')!r}"
        need = {"t", "p", "k", "es", "en", "f"}
        if not need <= set(s):
            E(f"{tag}: needs {sorted(need - set(s))}"); continue
        extra = set(s) - need - {"clue", "wrong"}
        if extra: E(f"{tag}: unknown fields {sorted(extra)}")
        t, p, k, es = s["t"], s["p"], s["k"], s["es"]
        if t not in TENSES3 + CMDS: E(f"{tag}: unknown tense {t!r}"); continue
        if k not in KINDS: E(f"{tag}: unknown kind {k!r}"); continue
        if not isinstance(p, int) or not 0 <= p <= 4 or (t in CMDS and p == 0): E(f"{tag}: bad person {p}"); continue
        if (t in CMDS and k not in ("cmd", "obj")) or (k == "cmd" and t not in CMDS): E(f"{tag}: commands use k cmd (or obj)")
        if k == "obj" and t not in OBJ_TENSES: E(f"{tag}: obj sentences use {sorted(OBJ_TENSES)}")
        if lc(es) in seen: E(f"{tag}: duplicate sentence")
        seen.add(lc(es))
        m = form_ok(v, s)
        if m: E(f"{tag}: {m}")
        if not occurs(s["f"], es): E(f"{tag}: f {s['f']!r} must appear once in es, as whole words")
        if not re.match(r"^[¿¡]?[A-ZÁÉÍÓÚÑ]", es) or not re.search(r"[.?!]$", es): E(f"{tag}: start with a capital (or ¿ ¡) and end with . ? or !")
        if es.count("¿") != es.count("?") or es.count("¡") != es.count("!"): E(f"{tag}: unpaired ¿? or ¡!")
        if k == "q" and "?" not in es: E(f"{tag}: a question needs ¿…?")
        if k == "neg" and not set(words(es)) & {"no", "nunca", "nadie", "nada", "tampoco", "ni", "ningún", "ninguna", "ninguno"}: E(f"{tag}: a negative needs no / nunca / …")
        if set(words(es)) & {"vosotros", "vosotras", "os", "vos"}: E(f"{tag}: no vosotros / vos")
        n = len(es.split())
        if n > 14: E(f"{tag}: {n} words (14 at most)")
        elif n > 12: W(f"{tag}: {n} words (12 or fewer reads better)")
        if not s["en"].strip() or not re.search(r"[.?!]$", s["en"]): E(f"{tag}: en must be a full sentence")
        if k == "stmt":
            if not s.get("clue") or not occurs(s["clue"], es): E(f"{tag}: a stmt needs a clue that appears once in es")
            elif lc(s["clue"]) in lc(s["f"]): E(f"{tag}: the clue can't be part of f")
            wr = s.get("wrong", [])
            bad = [x for x in wr if x not in TENSES3 or x == t]
            if bad: E(f"{tag}: wrong has bad tenses {bad}")
            if len(wr) < 3: E(f"{tag}: wrong needs at least 3 tenses")
            if t != "ir a" and any(x != "ir a" and lc(table_form(v, x, p)) == lc(s["f"]) for x in wr): E(f"{tag}: a wrong tense has the same form as f")
        elif "wrong" in s or "clue" in s:
            E(f"{tag}: clue and wrong are for stmt sentences only")
        by.setdefault(t, []).append(s)
    for t in TENSES3:
        ks = [s["k"] for s in by.get(t, [])]
        for k in ("stmt", "q", "neg"):
            if ks.count(k) != 1: E(f"{t}: needs exactly one {k} sentence (has {ks.count(k)})")
        ps = [s["p"] for s in by.get(t, []) if s["k"] != "obj"]
        if not third and len(set(ps)) < min(3, len(ps)): W(f"{t}: use three different persons")
    cmds = [s for t in CMDS for s in by.get(t, [])]
    if e["cmd"] == "none" and cmds: E("cmd is none but there are command sentences")
    if e["cmd"] == "neg" and by.get("Command (+)"): E("cmd is neg but there are affirmative commands")
    if e["cmd"] == "pos" and (by.get("Command (−)") or len(by.get("Command (+)", [])) < 2): E("cmd pos: at least 2 affirmative commands and no negative ones")
    if e["cmd"] == "both" and (len(by.get("Command (+)", [])) < 2 or not by.get("Command (−)")): E("cmd both: at least 2 affirmative and 1 negative command")
    if e["cmd"] == "neg" and len(by.get("Command (−)", [])) < 2: E("cmd neg: at least 2 negative commands")
    if len([s for s in e["s"] if s["k"] == "obj"]) > 2: E("at most 2 obj sentences")
    if third and any(s["p"] not in (2, 4) for s in e["s"] if s["t"] not in CMDS): E("third: every sentence uses person 2 or 4")
    if not third:
        for p in range(5):
            if sum(s["p"] == p for s in e["s"]) < 2: W(f"person {p} appears fewer than 2 times")
    return err, warn


if __name__ == "__main__":
    bad = 0
    for path in sys.argv[1:]:
        d = json.loads(Path(path).read_text(encoding="utf-8"))
        for v, e in d.items():
            err, warn = check(v, e)
            bad += len(err)
            for m in err: print("ERROR", m)
            for m in warn: print("warn ", m)
        print(path, len(d), "verbs checked")
    sys.exit(1 if bad else 0)
