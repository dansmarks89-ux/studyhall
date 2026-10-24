"""Build data/conj2.json: tables (same shape as conj.json) for every course verb that conj.json lacks.

Verbs come from vocab2.json entries with pos "verb" plus the "to …" entries of the level vocab and the
drill vocab sets. Headwords are reduced to the infinitive as taught: "(…)" notes are dropped, "a / b"
gives both verbs, a trailing governed preposition is dropped ("encargarse de" -> "encargarse");
anything still longer than one word is a phrase and is skipped.
Base tables come from conj.table (verbecc), corrected by hand where it is wrong (MODEL, PARTICIPLE, FIX,
DEFECTIVE below); reflexive verbs get their pronoun before the verb, and attached (with the
written accent) to affirmative commands.

  python3 src/spanish/content/pipeline/conj2.py
"""
import json, re
from pathlib import Path
from conj import table

DATA = Path(__file__).resolve().parents[2] / "data"
VERB = re.compile(r"[a-záéíóúñü]*(ar|er|ir|ír)(se)?")
GOVERNED = {"a", "con", "de", "en", "por", "que"}
PRON = ["me", "te", "se", "nos", "se"]
PRES, PRET, FUT, COND, PERF, PLUP, SUBJ, CMD_POS, CMD_NEG = 0, 1, 3, 4, 5, 6, 7, 9, 10

# verbecc fails on these (atrever: mispredicted as a "ver" compound; suceder: raises) -> regular model verb.
MODEL = {"atrever": "temer", "suceder": "temer"}
# verbecc uses the adjective (despierto, electo, preso…) in compound tenses; these take the regular participle.
PARTICIPLE = set("""atender bendecir comprender confesar confundir consumir convencer corregir despertar dividir
 elegir excluir expresar extender fijar juntar nacer prender presumir salvar soltar suspender sustituir""".split())
# Whole rows corrected by hand: missing stem change or accents, valer's tú command (vale, not archaic val),
# and the RAE 2010 spelling of the monosyllables crie, crio, hui, rio (no written accent).
FIX = {
    "nevar": {PRES: ["nievo", "nievas", "nieva", "nevamos", "nievan"],
              SUBJ: ["nieve", "nieves", "nieve", "nevemos", "nieven"],
              CMD_POS: ["", "nieva", "nieve", "nevemos", "nieven"],
              CMD_NEG: ["", "nieves", "nieve", "nevemos", "nieven"]},
    "prever": {PRES: ["preveo", "prevés", "prevé", "prevemos", "prevén"],
               PRET: ["preví", "previste", "previó", "previmos", "previeron"],
               CMD_POS: ["", "prevé", "prevea", "preveamos", "prevean"]},
    "convenir": {CMD_POS: ["", "convén", "convenga", "convengamos", "convengan"]},
    "prevenir": {CMD_POS: ["", "prevén", "prevenga", "prevengamos", "prevengan"]},
    "detener": {CMD_POS: ["", "detén", "detenga", "detengamos", "detengan"]},
    "retener": {CMD_POS: ["", "retén", "retenga", "retengamos", "retengan"]},
    "valer": {CMD_POS: ["", "vale", "valga", "valgamos", "valgan"]},
    "criar": {PRET: ["crie", "criaste", "crio", "criamos", "criaron"]},
    "huir": {PRET: ["hui", "huiste", "huyó", "huimos", "huyeron"]},
    "reír": {PRET: ["reí", "reíste", "rio", "reímos", "rieron"]},
}
# soler is defective: no future, conditional or commands.
DEFECTIVE = {"soler": (FUT, COND, CMD_POS, CMD_NEG)}


def infinitives(headword):
    out = []
    for part in re.sub(r"\s*\([^)]*\)", "", headword).split(" / "):
        words = part.split()
        if len(words) == 2 and words[1] in GOVERNED:
            words = words[:1]
        if len(words) == 1 and VERB.fullmatch(words[0]):
            out.append(words[0])
    return out


def course_verbs():
    vocab2 = json.loads((DATA / "vocab2.json").read_text(encoding="utf-8"))
    levels = json.loads((DATA / "levels.tagged.json").read_text(encoding="utf-8"))
    drills = json.loads((DATA / "drills.tagged.json").read_text(encoding="utf-8"))
    heads = [e["w"] for s in vocab2["sets"] for e in s["entries"] if e.get("pos") == "verb"]
    heads += [w for lv in levels for w, en in lv["vocab"] if en.startswith("to ")]
    heads += [e["w"] for s in drills["vsets"] for e in s["entries"] if e["en"].startswith("to ")]
    return {v for h in heads for v in infinitives(h)}


def stressed_vowel(word):
    """Index of the vowel carrying the stress (diphthongs: the strong vowel, or the second of ui/iu)."""
    acc = [i for i, c in enumerate(word) if c in "áéíóú"]
    if acc:
        return acc[0]
    w = re.sub(r"(?<=[qg])u(?=[ei])", "#", word)   # silent u
    syl = [m.span() for m in re.finditer(r"[iuü]?[aeo][iu]?|[iuü][iu]?", w)]
    a, b = syl[-2] if w[-1] in "aeiouns" and len(syl) > 1 else syl[-1]
    nucleus = w[a:b]
    k = next((i for i, c in enumerate(nucleus) if c in "aeo"), len(nucleus) - 1)
    return a + k


def enclitic(form, pron):
    """form + pron with the written accent the new word needs (levanta+te -> levántate, detén+te -> detente)."""
    i = stressed_vowel(form)
    plain = form[:i] + form[i].translate(str.maketrans("áéíóú", "aeiou")) + form[i + 1:]
    word = plain + pron
    after = re.sub(r"(?<=[qg])u(?=[ei])", "#", word[i + 1:])
    after = re.sub(r"^[iu](?![aeo])", "", after) if form[i] in "aeoáéó" else after   # rest of the nucleus
    later = len(re.findall(r"[iuü]?[aeo][iu]?|[iuü][iu]?", after))
    hiatus = form[i] in "íú" and bool(re.search("[aeiou]", form[i - 1:i] + form[i + 1:i + 2]))
    if later >= 2 or hiatus:
        word = word[:i] + "áéíóú"["aeiou".index(word[i])] + word[i + 1:]
    return word


def reflexive(tb):
    out = [[f"{PRON[p]} {f}" for p, f in enumerate(row)] for row in tb[:CMD_POS]]
    pos = tb[CMD_POS]
    nos = pos[3][:-1]                       # sentemos -> sentemo(nos); ir: vamos -> vámonos
    out.append(["", enclitic(pos[1], "te"), enclitic(pos[2], "se"), enclitic(nos, "nos"), enclitic(pos[4], "se")])
    out.append([""] + [f"{PRON[p]} {f}" for p, f in enumerate(tb[CMD_NEG]) if p])
    return out


def build(verb):
    base = verb[:-2] if verb.endswith("se") and VERB.fullmatch(verb[:-2]) else verb
    if base in MODEL:
        model = MODEL[base]
        tb = [[re.sub(rf"\b{model[:-2]}", base[:-2], f) for f in row] for row in table(model)]
    else:
        tb = table(base)
    if base in PARTICIPLE:
        part = base[:-2] + ("ado" if base[-2] == "a" else "ido")
        for row in (PERF, PLUP):
            tb[row] = [f.split()[0] + " " + part for f in tb[row]]
    for row, forms in FIX.get(base, {}).items():
        tb[row] = forms
    for row in DEFECTIVE.get(base, ()):
        tb[row] = [""] * 5
    return reflexive(tb) if base != verb else tb


if __name__ == "__main__":
    have = json.loads((DATA / "conj.json").read_text(encoding="utf-8"))
    out = {v: build(v) for v in sorted(course_verbs() - have.keys())}
    (DATA / "conj2.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(len(out), "verbs ->", DATA / "conj2.json")
