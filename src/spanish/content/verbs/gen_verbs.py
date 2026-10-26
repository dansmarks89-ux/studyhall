"""Build data/verbs.json (the verb lessons) from the authored batches and the reviewers' patches.

  python3 src/spanish/content/verbs/gen_verbs.py            -> data/verbs.json (refuses on any checker error)
  python3 src/spanish/content/verbs/gen_verbs.py --preview b07 OUT.json   -> one batch with its patch applied, checked

src/out/bNN.json  authored entries {verb: {en, note, uses, cmd, third?, s: [sentences]}} (shape: check.py, VERBS.md)
The build also drops "wrong" tenses that could be a correct reading (safe_wrong) and adds i, where f starts in es.

src/rev/bNN.json  the independent review of that batch: {verb: {"set": {field: value}, "s": {"<index>": sentence | null},
                  "add": [sentences]}}; indexes refer to the authored file; null drops the sentence.
order.json        the order verb lessons come in on each path (most useful first).
"""
import copy, json, re, sys
from pathlib import Path
from check import CMDS, TENSES3, check, lc, table_form

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[1] / "data"


def patched(batch):
    out = json.loads((HERE / "src" / "out" / f"{batch}.json").read_text(encoding="utf-8"))
    rp = HERE / "src" / "rev" / f"{batch}.json"
    rev = json.loads(rp.read_text(encoding="utf-8")) if rp.exists() else {}
    for v, r in rev.items():
        if v not in out:
            sys.exit(f"{batch}: review names {v}, which the batch doesn't have")
        e = out[v] = copy.deepcopy(out[v])
        for k, val in r.get("set", {}).items():
            if val is None: e.pop(k, None)
            else: e[k] = val
        fix = r.get("s", {})
        if any(not k.isdigit() or int(k) >= len(e["s"]) for k in fix):
            sys.exit(f"{batch} {v}: review index out of range")
        e["s"] = [fix.get(str(i), s) for i, s in enumerate(e["s"])]
        e["s"] = [s for s in e["s"] if s is not None] + r.get("add", [])
    return out


# Patterns the reviews found where a listed "wrong" tense can be acceptable (one batch's reviewer caught each; this
# applies the fix to every batch): (tense of the sentence, words in the sentence, tenses that are NOT safe as wrong options)
RISKY = [
    ("Imperfect subjunctive", r"\bsi\b", {"Present"}),                       # si + present + conditional is common speech
    ("Present subjunctive", r"\bespero que\b", {"Preterite", "Future"}),     # espero que llegó / esperar = expect
    ("Present perfect", r"\b(hasta ahora|últimamente)\b", {"Pluperfect"}),    # hasta ahora me habían gustado (pero…)
    ("Present perfect", r"\btodavía no\b", {"Future", "Present", "Preterite"}),
    ("Present", r"^ahora\b(?! que)", {"Preterite"}),                         # ahora sí me gustaron
    ("Conditional", r"\ben (tu|su) lugar\b", {"Preterite", "Future", "Present", "Imperfect"}),   # = instead of you
    ("Future|ir a", r"\ben (un|una|unos|unas|dos|tres|cuatro|cinco|diez|quince|veinte) (momento|minutos?|horas?|días?|semanas?|meses|años?)\b", {"Preterite"}),
    ("Future|ir a", r"\b(esta tarde|esta noche|este fin de semana|esta semana|este mes|este año|hoy)\b", {"Preterite", "Present perfect"}),
]


def safe_wrong(v, s):
    """The "Which tense?" options for a statement: its wrong tenses, minus risky ones (RISKY) and minus any whose form is
    also the form of a tense not listed as wrong (nosotros cantamos = present and preterite; tome = present subjunctive
    and usted command), so an option shown as wrong can never be a correct reading."""
    es, wr = lc(s["es"]), set(s["wrong"])
    for t, rx, bad in RISKY:
        if s["t"] in t.split("|") and re.search(rx, es): wr -= bad
    ok = [x for x in TENSES3 + CMDS if x not in wr]
    taken = {lc(table_form(v, x, s["p"])) for x in ok if table_form(v, x, s["p"])}
    return [x for x in s["wrong"] if x in wr and lc(table_form(v, x, s["p"])) not in taken]


def checked(d, label):
    bad = 0
    for v, e in d.items():
        err, _ = check(v, e)
        for m in err: print("ERROR", label, m)
        bad += len(err)
    return bad


if __name__ == "__main__":
    if sys.argv[1:2] == ["--preview"]:
        d = patched(sys.argv[2])
        Path(sys.argv[3]).write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        sys.exit(1 if checked(d, sys.argv[2]) else 0)
    verbs, bad = {}, 0
    for p in sorted((HERE / "src" / "out").glob("b*.json")):
        d = patched(p.stem)
        bad += checked(d, p.stem)
        dup = set(d) & set(verbs)
        if dup: sys.exit(f"{p.stem}: verbs in two batches: {sorted(dup)}")
        verbs.update(d)
    if bad: sys.exit(f"{bad} errors: data/verbs.json not written")
    order = json.loads((HERE / "order.json").read_text(encoding="utf-8"))["order"]
    if not set(order["every"]) == set(order["clinic"]) == set(verbs):   # both paths order the same verbs, each with content
        sys.exit(f"order.json and the batches differ: {sorted(set(order['every']) ^ set(order['clinic']) | set(order['every']) ^ set(verbs))}")
    for v, e in verbs.items():
        for s in e["s"]:
            if s["k"] == "stmt": s["wrong"] = safe_wrong(v, s)
    def keep(s):   # i: where f starts in es (the app blanks it out)
        m = re.search(rf"(?<![\wáéíóúüñ]){re.escape(lc(s['f']))}(?![\wáéíóúüñ])", lc(s["es"]))
        return dict({k: s[k] for k in ("t", "p", "k", "es", "en", "f", "clue", "wrong") if k in s}, i=m.start())
    out = {"order": order, "verbs": {v: dict({k: e[k] for k in ("en", "note", "uses", "cmd")}, **({"third": True} if e.get("third") else {}),
                                             s=[keep(s) for s in e["s"]]) for v, e in verbs.items()}}
    (DATA / "verbs.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(len(verbs), "verbs,", sum(len(e["s"]) for e in verbs.values()), "sentences ->", DATA / "verbs.json")
