"""Build the Study Hall Cantonese and Korean courses.

    python3 src/lang/build.py cantonese     -> cantonese/index.html + cantonese/audio.json
    python3 src/lang/build.py korean        -> korean/index.html + korean/audio.json
    python3 src/lang/build.py all

Inputs: src/<lang>/content/levels/L1..L10.json (checked with tools/check_level.py),
src/<lang>/content/sounds_src.json, the pronunciation guide in tools/build_app.py,
and the shared engine src/lang/app.html.
Everyday words: src/<lang>/content/vocab2/out/ev-<b>.json (set b+1) and extra-<k>.json (more examples for
existing vocab), each patched by vocab2/rev/<same name> ({"fix": [entries], "drop": [ids]}) when present.
They go to <lang>/vocab2.<hash>.json (the previous build's file is kept for pages still open); the claude.ai
preview build inlines them.
audio.json lists every clip the page can play; the Supabase "tts" function records the missing ones.
"""
import json, os, re, sys, hashlib, random, functools
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(HERE, "tools"))

CONF = {
    "cantonese": dict(code="yue", name="Cantonese", native="廣東話", htmllang="zh-HK", course="cantonese",
                      voice="zh-HK-HiuMaanNeural", voice2="zh-HK-WanLungNeural", romName="Jyutping",
                      font="Noto+Sans+TC", fontVar="--font-tc",
                      ttsLang="zh-HK", voiceRe=r"^(yue|zh[-_](HK|Hant[-_]HK))", voiceNameRe=r"cantonese|粵|粤",
                      sounds=dict(id="TONES", title="Tones", sub="The six tones by ear", sets=["S1", "S2", "S3"]),
                      chars=True,  # the optional Characters track in Practice
                      formSkill=dict(title="Grammar", sub="The levels' grammar, with {forms}"),  # {forms} = the markers unlocked so far
                      # Grammar forms practised in lessons (the aspect markers), each unlocked by the level note that teaches it.
                      forms=[dict(k="緊", label="Happening now", hint="gan2", at=("L5", "Happening right now")),
                             dict(k="咗", label="Done", hint="zo2", at=("L6", "Done, and")),
                             dict(k="未", label="Not yet", hint="mei6", at=("L6", "Done, and")),
                             dict(k="過", label="Ever done", hint="gwo3", at=("L6", "Ever done"))],
                      talkOpen=["你好！", "nei5 hou2!"]),
    "korean": dict(code="ko", name="Korean", native="한국어", htmllang="ko", course="korean",
                   voice="ko-KR-SunHi:DragonHDLatestNeural", voice2="ko-KR-Hyunsu:DragonHDLatestNeural", romName="romanization",
                   font="Noto+Sans+KR", fontVar="--font-kr",
                   ttsLang="ko-KR", voiceRe=r"^ko", voiceNameRe=r"korean|한국",
                   sounds=dict(id="HANGUL", title="Hangul", sub="Read the Korean alphabet", sets=["H1", "H2", "H3", "H4"],
                               ask="Can you read Hangul, the Korean alphabet?", check=["H1", "H3"]),  # asked on a first visit; yes = a 6-item check from these sets
                   chars=False,
                   formSkill=dict(title="Verbs", sub="Verb endings ({forms}) on the verbs you know, and the levels' grammar"),
                   # Verb endings practised in lessons (forms in content/conj/conj.json), each unlocked by the level note that teaches it.
                   forms=[dict(k="present", label="Present", hint="-아요 / -어요", at=("L3", "Eating, drinking")),
                          dict(k="neg", label="Not", hint="안 + verb", at=("L3", "Have, don't have")),
                          dict(k="please", label="Please do", hint="-(으)세요", at=("L4", "Where is it?")),
                          dict(k="want", label="Want to", hint="-고 싶어요", at=("L4", "Wanting")),
                          dict(k="past", label="Past", hint="-았어요 / -었어요", at=("L6", "Past tense")),
                          dict(k="future", label="Future", hint="-(으)ㄹ 거예요", at=("L6", "Future"))],
                   talkOpen="안녕하세요!"),
}
RATE = "0%"
clip = lambda voice, text: hashlib.sha256(f"{voice}|{RATE}|{text}".encode()).hexdigest()[:32]


def build(lang):
    C = CONF[lang]
    yue = C["code"] == "yue"
    base = os.path.join(REPO, "src", lang, "content")
    if not yue:
        from ko_pron import rom as ko_rom, strip as ko_strip
        ko_pron = cached_ko_pron()
    audio = {}  # (voice, text) -> name

    def say_text(s):
        """Text sent to the voice: no gap marks or ellipses."""
        s = s.replace("___", "…").replace("…", " ").replace(" / ", "，" if yue else ", ")
        return re.sub(r"\s+", " ", s).strip()

    def want(text, voice=None):
        t = say_text(text)
        if t:
            v = voice or C["voice"]
            audio[(v, t)] = clip(v, t)
        return t

    def T(x, pronmap, voice=None, play=True):
        """Normalize a target text to {s, r, p?} and register its audio."""
        if yue:
            s, r = x[0], x[1]
            o = {"s": s, "r": r}
        else:
            s = x
            if "___" in s:
                o = {"s": s, "r": ""}
            else:
                p = pronmap.get(s) or ko_pron(s)
                o = {"s": s, "r": ko_rom(p)}
                if ko_strip(p) != ko_strip(s):
                    o["p"] = p
        if play and "___" not in o["s"]:
            want(o["s"], voice)
        return o

    def fill(q, opt):
        if yue:
            return [q[0].replace("___", opt[0]), q[1].replace("___", opt[1])]
        return q.replace("___", opt)

    TAG = re.compile(r"\{\{(.+?)\}\}")

    def prose(text, pronmap):
        """Replace {{…}} tags with placeholders the page renders; register their audio."""
        if not text:
            return text
        def rep(m):
            inner = m.group(1)
            o = T(inner.split("|") if yue else inner, pronmap)
            return "{{" + json.dumps(o, ensure_ascii=False) + "}}"
        return TAG.sub(rep, text)

    levels = []
    for n in range(1, 11):
        L = json.load(open(os.path.join(base, "levels", f"L{n}.json"), encoding="utf-8"))
        pm = L.get("pron", {}) if not yue else {}
        lid = L["id"]
        out = {"id": lid, "n": n, "title": L["title"], "goal": L["goal"], "notes": [], "vocab": [], "items": [], "roleplay": []}
        for nb in L["notes"]:
            out["notes"].append({"h": nb["h"], "p": prose(nb["p"], pm), "ex": [[T(e[0], pm), e[1]] for e in nb.get("ex", [])]})
        for i, v in enumerate(L["vocab"]):
            vpm = dict(pm)
            if not yue and v.get("pron") and v["t"] not in vpm:
                vpm[v["t"]] = v["pron"]
            note = v.get("note", "")
            vo = {"id": f"{lid}-v-{i:02d}", "t": T(v["t"], vpm), "en": v["en"], "topic": v.get("topic", ""),
                  "note": prose(note, pm) if v.get("old") is None else note, "avoid": v.get("avoid", [])}
            if v.get("old"):
                vo["old"] = v["old"]
            out["vocab"].append(vo)
        for it in L["items"]:
            t = it["t"]
            o = {"id": it["id"], "t": t, "sk": it.get("sk", [])}
            if t == "gap":
                o.update(q=T(it["q"], pm), en=it["en"], opts=[T(x, pm, play=False) for x in it["opts"]], a=it["a"], why=prose(it["why"], pm))
                o["full"] = T(fill(it["q"], it["opts"][it["a"]]), pm)
            elif t == "pick":
                o.update(q=prose(it["q"], pm), opts=[T(x, pm) for x in it["opts"]], a=it["a"], why=prose(it["why"], pm))
            elif t == "tiles":
                o.update(en=it["en"], full=T(it["full"], pm), a=[T(x, pm, play=False) for x in it["a"]],
                         alt=[[T(x, pm, play=False)["s"] for x in alt] for alt in it.get("alt", [])],
                         extra=[T(x, pm, play=False) for x in it["extra"]])
            elif t == "listen":
                o.update(say=T(it["say"], pm), opts=it["opts"], a=it["a"], why=prose(it.get("why", ""), pm))
            elif t == "dlg":
                turns = []
                for tu in it["turns"]:
                    if tu.get("you"):
                        turns.append({"you": True, "opts": [T(x, pm) for x in tu["opts"]], "a": tu["a"], "why": prose(tu["why"], pm), "sk": tu["sk"]})
                    else:
                        turns.append({"who": tu["who"], "s": T(tu["s"], pm, voice=C["voice2"]), "en": tu["en"]})
                o.update(title=it["title"], turns=turns)
                o["sk"] = sorted({s for tu in it["turns"] if tu.get("you") for s in tu["sk"]})
            out["items"].append(o)
        for r in L["roleplay"]:
            out["roleplay"].append({"title": r["title"], "setup": r["setup"], "persona": r["persona"],
                                    "opening": T(r["opening"], pm, voice=C["voice2"]), "opening_en": r["opening_en"], "goals": r["goals"]})
        levels.append(out)

    drills = build_drills(lang, levels, T, want)

    # pronunciation guide (from the original flashcard pages); the path replaces its old "How to study" steps
    import build_app as B
    guide = B.yue_guide() if yue else B.ko_guide()
    guide = re.sub(r"\s*<section><h2>How to study</h2>.*?</section>", "", guide, flags=re.S)
    for m in re.finditer(r'data-say="([^"]+)"', guide):
        want(m.group(1))
    talk_open = T(C["talkOpen"], {}, voice=C["voice2"])

    data = {"levels": levels, "drills": drills, "guide": guide,
            "audio": {f"{v}|{t}": n for (v, t), n in audio.items()}}
    # Everyday words: their clips go into audio.json for the admin sync, not into the page (the page computes the names).
    v2 = build_vocab2(lang, levels, want)
    attach_needs(lang, levels, v2)
    data["path"] = build_path(C, levels, drills, v2)
    cfg = {"course": C["course"], "lang": C["code"], "name": C["name"], "native": C["native"], "htmlLang": C["htmllang"],
           "voice": C["voice"], "voice2": C["voice2"], "romName": C["romName"], "ttsLang": C["ttsLang"],
           "voiceRe": C["voiceRe"], "voiceNameRe": C["voiceNameRe"], "talkOpen": talk_open, "chars": C["chars"], "formSkill": C["formSkill"],
           "soundAsk": C["sounds"].get("ask", ""), "soundCheck": C["sounds"].get("check", []),
           "forms": [{k: f[k] for k in ("k", "label", "hint")} for f in C["forms"]],
           "audioBase": "https://wbrssohmepioxapwbcne.supabase.co/storage/v1/object/public/audio/" + C["course"] + "/"}
    src = open(os.path.join(HERE, "app.html"), encoding="utf-8").read()
    rep = {"__CONFIG__": json.dumps(cfg, ensure_ascii=False), "__DATA__": json.dumps(data, ensure_ascii=False, separators=(",", ":")),
           "__NAME__": C["name"], "__FONT__": C["font"], "__FONTVAR__": C["fontVar"], "__COURSE__": C["course"]}
    for k in sorted(rep, key=len, reverse=True):
        assert k in src, k
        src = src.replace(k, rep[k])
    assert src.count("__VOCAB__") == 1 and src.count("__HOSTED__") == 1
    left = re.findall(r"__[A-Z]+__", src.replace("__VOCAB__", "").replace("__HOSTED__", ""))
    assert not left, left
    outdir = os.path.join(REPO, C["course"])
    os.makedirs(outdir, exist_ok=True)
    index = os.path.join(outdir, "index.html")
    v2json = json.dumps(v2, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    v2name = f"vocab2.{hashlib.sha256(v2json).hexdigest()[:10]}.json"
    keep = set(V2FILE.findall(open(index, encoding="utf-8").read())) if os.path.exists(index) else set()
    open(os.path.join(outdir, v2name), "wb").write(v2json)
    for f in os.listdir(outdir):
        if V2FILE.fullmatch(f) and f != v2name and f not in keep:
            os.remove(os.path.join(outdir, f))
    open(index, "w", encoding="utf-8").write(src.replace("__VOCAB__", json.dumps({"url": v2name})).replace("__HOSTED__", HOSTED.replace("__COURSE__", C["course"])))
    manifest = [{"n": n, "t": t, "v": v, "r": RATE} for (v, t), n in sorted(audio.items(), key=lambda kv: kv[1])]
    json.dump(manifest, open(os.path.join(outdir, "audio.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    # claude.ai preview build (no Study Hall sign-in): design system and everyday words inlined
    shared = lambda f: open(os.path.join(REPO, "shared", f), encoding="utf-8").read()
    preview = (src.replace("__VOCAB__", '{"data":' + v2json.decode("utf-8") + "}").replace("__HOSTED__", "")
               .replace('<link rel="stylesheet" href="../shared/ui.css">', "<style>\n" + shared("ui.css") + "</style>")
               .replace('<script src="../shared/ui.js"></script>', "<script>\n" + shared("ui.js") + "</script>"))
    assert "../shared/" not in preview
    os.makedirs(os.path.join(REPO, "build"), exist_ok=True)
    open(os.path.join(REPO, "build", f"{C['course']}-course.html"), "w", encoding="utf-8").write(preview)
    nitems = sum(len(l["items"]) for l in levels); nv = sum(len(l["vocab"]) for l in levels)
    nl = sum(len(u["ls"]) for u in data["path"]["units"]), sum(len(u.get("ll", [])) for u in data["path"]["units"])
    print(f"{lang}: {nitems} items, {nv} vocab, {len(drills[-1]['_items'])} drill items, {len(data['path']['units'])} units, {nl[0]} short / {nl[1]} long lessons, "
          f"{len(audio)} audio clips, page {os.path.getsize(index)//1024} KB, {v2name} {len(v2json)//1024} KB")


# ------------------------------------------------------------------ the learning path
# Lesson sizes (about 10 and 15 minutes at ~20 s a question and ~25 s a card): new words in a short and in a long
# lesson (separate lessons of each unit), and for the sound unit (one length, about 10 minutes) questions or Hangul
# letters per lesson.
WORDS = {"short": 5, "long": 7}
DRILL_Q, LETTERS = 25, 8
TAGTEXT = re.compile(r"\{\{(\{.+?\})\}\}")  # the {{json}} tags prose() leaves in notes
EDGE = "？?！!。.，,、；;：:～~…\"'“”‘’()（）「」 "


def split(xs, size, up=False):
    """xs in order, cut into round(len/size) runs (ceil when up) whose lengths differ by at most one, longer runs spread evenly."""
    k = max(1, -int(-len(xs) // size) if up else round(len(xs) / size))
    q, r = divmod(len(xs), k)
    out, i = [], 0
    for j in range(k):
        n = q + ((j + 1) * r // k - j * r // k)
        out.append(xs[i:i + n])
        i += n
    return out


def clean(s):
    """A headword as a lesson title shows it: the first of "a / b", no blanks or edge punctuation."""
    s = s.split(" / ")[0].replace("___", " ").replace("…", " ")
    return re.sub(r"\s+", " ", s).strip(EDGE)


def gloss(en):
    """The first sense of an English gloss, without notes in brackets (which can nest)."""
    g = en
    while re.search(r"\([^()]*\)", g):
        g = re.sub(r"\s*\([^()]*\)", "", g)
    return re.split(r"[;,]", g)[0].strip() or re.search(r"\(([^()]*)\)", en).group(1)


def build_path(C, levels, drills, v2):
    """The course as one path of units, each cut into short lessons (ls, ids <unit>-<n>) and, separately, long lessons
    (ll, ids <unit>-L<n>; not in the sound unit); the learner's lesson length picks the list (same words, same order).
    Units: the sound unit (drill sets), then each level followed by two Everyday sets.
    Lesson fields: w = new words (vocab ids), n = indexes of the level notes shown as Grammar cards, d = drill items
    asked, m = drill items introduced first (Hangul letters), set = drill set, t = title (target words, or the drill set's
    title for the sound unit), o = place in the path (words or drill items before the lesson's first one).
    The page picks each lesson's grammar items, sentences and reviews when it starts.
    forms = [[form, o of the short lesson whose Grammar card teaches it], ...]."""
    LV = {l["id"]: l for l in levels}
    ES = {s["id"]: s for s in v2["sets"]}
    DS = {d["id"]: d for d in drills if "id" in d}
    DI = {i["id"]: i for i in drills[-1]["_items"]}
    snd = C["sounds"]
    order = [snd["id"]] + [u for n in range(1, 11) for u in (f"L{n}", f"E{2 * n - 1}", f"E{2 * n}")]
    rnd = random.Random(11)
    title = lambda ws: ", ".join(list(dict.fromkeys(c for c in (clean(w["t"]["s"]) for w in ws) if c))[:3])
    def drill_lessons():
        ls = []
        for sid in snd["sets"]:
            items = DS[sid]["items"]
            letters = [i for i in items if DI[i]["t"] == "letter"]
            if letters:  # Hangul letters: met two at a time, each pair asked right away; then the listening trios
                parts, rest = split(letters, LETTERS, True), [i for i in items if DI[i]["t"] != "letter"]
                for k, part in enumerate(parts):
                    ls.append({"d": part + rest[k::len(parts)][:len(part)], "m": part, "set": sid})
            else:  # a sample of the set's cards, met as a list first
                pick = items if len(items) <= 3 * DRILL_Q else rnd.sample(items, 3 * DRILL_Q)
                for part in split(pick, DRILL_Q):
                    ls.append({"d": part, "m": [], "set": sid})
        per, seen = {}, {}
        for L in ls:
            per[L["set"]] = per.get(L["set"], 0) + 1
        for L in ls:
            seen[L["set"]] = seen.get(L["set"], 0) + 1
            L["t"] = DS[L["set"]]["title"] + (f", part {seen[L['set']]}" if per[L["set"]] > 1 else "")
        return ls

    def level_lessons(l, n):
        topics = list(dict.fromkeys(v["topic"] for v in l["vocab"]))
        vocab = sorted(l["vocab"], key=lambda v: topics.index(v["topic"]))  # stable: the level's order within each topic
        parts = split(vocab, n)
        # Grammar cards: each note goes to the first lesson with a word it mentions (spread out, in note order).
        notes, at, cap = [[] for _ in parts], 0, -(-len(l["notes"]) // len(parts))
        for i, nb in enumerate(l["notes"]):
            said = {json.loads(t)["s"] for t in TAGTEXT.findall(nb["p"])} | {e[0]["s"] for e in nb["ex"]}
            hit = next((k for k, part in enumerate(parts) if any(v["t"]["s"] in said for v in part)), None)
            at = max(at, hit if hit is not None else i * len(parts) // len(l["notes"]))
            while at < len(parts) - 1 and len(notes[at]) >= cap:
                at += 1
            notes[at].append(i)
        return [{"w": [v["id"] for v in part], "n": notes[k], "t": title(part)} for k, part in enumerate(parts)]

    units = []
    for uid in order:
        if uid == snd["id"]:
            units.append({"id": uid, "k": "drill", "title": snd["title"], "sub": snd["sub"], "sets": snd["sets"], "ls": drill_lessons()})
        elif uid in LV:
            l = LV[uid]
            units.append({"id": uid, "k": "level", "title": l["title"], "sub": l["goal"],
                          "ls": level_lessons(l, WORDS["short"]), "ll": level_lessons(l, WORDS["long"])})
        elif uid in ES:
            e = ES[uid]
            lessons = lambda n: [{"w": [w["id"] for w in part], "t": title(part)} for part in split(e["words"], n)]
            units.append({"id": uid, "k": "words", "title": e["title"], "sub": ", ".join(gloss(w["en"]) for w in e["words"][:4]),
                          "ls": lessons(WORDS["short"]), "ll": lessons(WORDS["long"])})
    o = 0
    for u in units:
        for key, tag in (("ls", ""), ("ll", "L")):
            at = o
            for k, L in enumerate(u.get(key, [])):
                L["id"], L["o"] = f"{u['id']}-{tag}{k + 1}", at
                at += len(L.get("w") or L["d"])
        o += sum(len(L.get("w") or L["d"]) for L in u["ls"])
    forms = []
    for f in C["forms"]:
        lid, head = f["at"]
        u = next(u for u in units if u["id"] == lid)
        i = next(i for i, nb in enumerate(LV[lid]["notes"]) if nb["h"].startswith(head))
        forms.append([f["k"], next(L["o"] for L in u["ls"] if i in L["n"])])
    return {"units": units, "forms": forms}


# ------------------------------------------------------------------ Korean pronunciation cache
@functools.cache
def cached_ko_pron():
    """ko_pron.pron with an on-disk cache in build/ (it takes ~30 ms a sentence); reset when ko_pron.py changes.
    Delete build/ko_pron_cache.json after upgrading g2pk2 or kiwipiepy."""
    from ko_pron import pron
    path = os.path.join(REPO, "build", "ko_pron_cache.json")
    ver = hashlib.sha256(open(os.path.join(HERE, "tools", "ko_pron.py"), "rb").read()).hexdigest()[:12]
    try:
        cache = json.load(open(path, encoding="utf-8"))
        if cache.get("_v") != ver:
            cache = {}
    except (OSError, ValueError):
        cache = {}
    cache["_v"] = ver
    def f(s):
        if s not in cache:
            cache[s] = pron(s)
            if len(cache) % 500 == 0:
                save()
        return cache[s]
    def save():
        os.makedirs(os.path.dirname(path), exist_ok=True)
        json.dump(cache, open(path, "w", encoding="utf-8"), ensure_ascii=False)
    import atexit
    atexit.register(save)
    return f


# ------------------------------------------------------------------ Everyday words (vocab2)
V2FILE = re.compile(r"vocab2\.[0-9a-f]{10}\.json")
CJK = re.compile(r"[㐀-䶿一-鿿\U00020000-\U0003FFFF]")
NONWORD = re.compile(r"[^0-9A-Za-z㐀-䶿一-鿿\U00020000-\U0003FFFF]")  # Cantonese tiles drop these (punctuation, spaces)
KO_PUNCT = re.compile(r"[?!,.…~\"'“”‘’()]")
# Cantonese aspect markers and the English that shows which one a sentence needs (so only one option fits).
_EVER = re.compile(r"\b(ever|before|been|never|once|twice|times)\b", re.I)
_YET = re.compile(r"\b(yet|still not|haven't|hasn't)\b", re.I)
ASPECT_CUE = {
    "緊": lambda s, i, en: bool(re.search(r"\b(am|is|are|was|were)\s+(\w+\s+)?\w+ing\b|'(m|re|s)\s+\w+ing\b", en, re.I)),
    "咗": lambda s, i, en: not (_EVER.search(en) or _YET.search(en) or re.search(r"\w+ing\b", en)),
    "過": lambda s, i, en: bool(_EVER.search(en) or "冇" in s[:i]) and not re.search(r"\bthan\b", en),  # not the comparative 過
    "未": lambda s, i, en: bool(_YET.search(en)),
}
# Words where the character is not the aspect marker.
ASPECT_NOT = ["要緊", "緊張", "緊急", "抓緊", "收緊", "拉緊", "綁緊", "緊緊", "不過", "經過", "超過", "難過", "錯過", "通過", "度過",
              "過去", "過嚟", "過來", "過馬路", "過年", "過節", "未來", "未必", "未曾", "從未", "未婚"]


def build_vocab2(lang, levels, want):
    """Compact entries for the page: sets of everyday words and extra examples for existing vocab.
    Each example gets "g" = [start, end, r_from, r_to(, Korean: romanization of the blank)] when the word can be
    blanked in it exactly once (start/end in code points of s; r_from..r_to-1 = the blanked tokens of the space-separated
    romanization, -1 when they can't be told apart); each word gets "tl" = the
    example used for sentence tiles (Cantonese: [index, tile lengths in characters of the example without punctuation])."""
    yue = lang == "cantonese"
    d = os.path.join(REPO, "src", lang, "content", "vocab2")
    if not yue:
        from ko_pron import rom as ko_rom, strip as ko_strip
        ko_pron = cached_ko_pron()
        from kiwipiepy import Kiwi
        kiwi = Kiwi()
        conj = json.load(open(os.path.join(REPO, "src", lang, "content", "conj", "conj.json"), encoding="utf-8"))
        FORMS = [f["k"] for f in CONF[lang]["forms"]]
    else:
        import pycantonese
        conj = {}
    stats = {"dup_course": 0, "dup_everyday": 0, "no_gap": 0, "no_tiles": 0, "patched": 0, "dropped": 0}

    def load(name):
        arr = json.load(open(os.path.join(d, "out", name), encoding="utf-8"))
        rp = os.path.join(d, "rev", name)
        if os.path.exists(rp):
            rev = json.load(open(rp, encoding="utf-8"))
            fix = {e["id"]: e for e in rev.get("fix", [])}
            drop = set(rev.get("drop", []))
            stats["patched"] += sum(1 for e in arr if e["id"] in fix)
            stats["dropped"] += sum(1 for e in arr if e["id"] in drop)
            have = {e["id"] for e in arr}
            arr = [fix.get(e["id"], e) for e in arr if e["id"] not in drop] + [e for i, e in fix.items() if i not in have]  # re-added under a new id
        return arr

    def files(prefix):
        fs = [(int(m.group(1)), f) for f in os.listdir(os.path.join(d, "out")) if (m := re.fullmatch(prefix + r"-(\d+)\.json", f))] if os.path.isdir(os.path.join(d, "out")) else []
        return sorted(fs)

    def ko_text(s):
        p = ko_pron(s)
        o = {"s": s, "r": ko_rom(p)}
        if ko_strip(p) != ko_strip(s):
            o["p"] = p
        return o

    def ko_span(hw, s):
        """(start, end) of the word in a Korean example: the headword itself, or for a -다 verb/adjective the
        conjugated word from its stem to the end of that word (found with the Kiwi tagger)."""
        if not hw.endswith("다") or s.count(hw) == 1:
            return (s.find(hw), s.find(hw) + len(hw)) if s.count(hw) == 1 else None
        stem, toks = hw[:-1], kiwi.tokenize(s)
        hits = []
        for i in range(len(toks)):
            acc = ""
            for j in range(i, len(toks)):
                acc += toks[j].form
                if acc == stem and toks[j].tag[0] in "VX":
                    hits.append((toks[i].start, toks[j].start + toks[j].len))
                    break
                if not stem.startswith(acc):
                    break
        if len(hits) != 1:
            return None
        a, b = hits[0]
        while b < len(s) and re.match(r"[가-힣]", s[b]):
            b += 1
        return a, b

    def gap(hw, x):
        """The "g" field for example x, or None if the word can't be blanked exactly once."""
        s = x["s"]
        if yue:
            if s.count(hw) != 1:
                return None
            a = s.find(hw)
            ra = len(CJK.findall(s[:a]))
            return [a, a + len(hw), ra, ra + len(CJK.findall(hw))]
        sp = ko_span(hw, s)
        if not sp:
            return None
        a, b = sp
        ra = len(s[:a].split()) - (1 if a and not s[a - 1].isspace() else 0)
        rb = len(s[:b].split())
        if ra >= rb or len(x["r"].split()) != len(s.split()):
            ra = rb = -1
        return [a, b, ra, rb, ko_rom(ko_pron(s[a:b]))]

    def tiles(hw, ex):
        if not yue:
            for k, x in enumerate(ex):
                if 3 <= len([w for w in (KO_PUNCT.sub("", t) for t in x["s"].split()) if w]) <= 7:
                    return [k]
            return None
        for k, x in enumerate(ex):
            s = NONWORD.sub("", x["s"])
            i = s.find(hw)
            if i < 0:
                continue
            words = (pycantonese.segment(s[:i]) if i else []) + [hw] + (pycantonese.segment(s[i + len(hw):]) if s[i + len(hw):] else [])
            if 3 <= len(words) <= 8:
                return [k, [len(w) for w in words]]
        return None

    def aspect(s, en):
        """Cantonese: [code point, romanization token] of the aspect marker in s that can be blanked, or None.
        Only sentences with exactly one marker character, not inside another word, whose English shows which marker fits."""
        hits = [i for i, c in enumerate(s) if c in ASPECT_CUE]
        if len(hits) != 1:
            return None
        i = hits[0]
        if any(s.startswith(w, j) for w in ASPECT_NOT for j in range(max(0, i - len(w) + 1), i + 1)):
            return None
        return [i, len(CJK.findall(s[:i]))] if ASPECT_CUE[s[i]](s, i, en) else None

    def example(x):
        if yue:
            assert len(CJK.findall(x["s"])) == len(x["r"].split()), x
            o = {"s": x["s"], "r": x["r"], "en": x["en"]}
            a = aspect(x["s"], x["en"])
            if a:
                o["a"] = a
        else:
            o = dict(ko_text(x["s"]), en=x["en"])
        want(x["s"])
        return o

    def examples(hw, raw):
        out = []
        for x in raw:
            o = example(x)
            g = gap(hw, o)
            if g:
                o["g"] = g
            else:
                stats["no_gap"] += 1
            out.append(o)
        return out

    seen = {v["t"]["s"] for l in levels for v in l["vocab"]}
    course = set(seen)
    sets = []
    for b, name in files("ev"):
        words = []
        for e in load(name):
            s = e["t"]["s"]
            if s in seen:
                stats["dup_course" if s in course else "dup_everyday"] += 1
                continue
            seen.add(s)
            t = {"s": s, "r": e["t"]["r"]} if yue else ko_text(s)
            want(s)
            w = {"id": e["id"], "t": t, "pos": e["pos"], "en": e["en"], "note": e.get("note", ""), "ex": examples(s, e["ex"])}
            if s in conj:  # Korean verb and adjective forms for the lesson's Verbs step
                c = conj[s]
                w["cj"] = {f: ko_text(c[f]) for f in FORMS if c.get(f)}
                for f in w["cj"].values():
                    want(f["s"])
                if c["note"]:
                    w["cn"] = c["note"]
            tl = tiles(s, w["ex"])
            if tl:
                w["tl"] = tl
            else:
                stats["no_tiles"] += 1
            words.append(w)
        sets.append({"id": f"E{b + 1}", "n": b + 1, "title": f"Everyday words {b + 1}", "words": words})

    voc = {v["id"]: v for l in levels for v in l["vocab"]}
    extra, flagged = {}, []
    for k, name in files("extra"):
        for e in load(name):
            v = voc.get(e["id"])
            if not v or v["t"]["s"] != e["t"]["s"]:
                print(f"  {name}: {e['id']} does not match an existing word; skipped")
                continue
            if e.get("flag"):
                flagged.append(f"{e['id']} ({e['flag']})")
            extra[e["id"]] = examples(v["t"]["s"], e["ex"])
    nw = sum(len(s["words"]) for s in sets)
    print(f"{lang} everyday: {len(sets)} sets, {nw} words; dropped as duplicates: {stats['dup_course']} already in the course, "
          f"{stats['dup_everyday']} repeated; review patches: {stats['patched']} fixed, {stats['dropped']} dropped; "
          f"{stats['no_gap']} examples without a gap question, {stats['no_tiles']} words without tiles; extra examples for {len(extra)} words")
    if flagged:
        print(f"  flagged by the writers ({len(flagged)}): " + "; ".join(flagged))
    return {"sets": sets, "extra": extra}


# ------------------------------------------------------------------ which words a sentence uses
# Lessons ask sentences (tiles, cloze, shadowing, Say it) whose words the learner has met. Each sentence gets
# "k" = indexes of the course words in it (course vocab in level order, then the Everyday words in set order; the page
# builds the same list) and "u" = how many of its words are in neither (left out when 0). Function words and names
# count as known, so they are in neither.
FUNC_YUE = set("我 你 佢 我哋 你哋 佢哋 係 唔 有 冇 嘅 咗 緊 過 啦 呀 喇 嗎 呢 㗎 喎 啊 吖 囉 咩 嘞 噃 吓 啩 嘛 個 啲 都 就 同 喺 好 "
               "一 二 兩 三 四 五 六 七 八 九 十 百 千 萬 零 呢 嗰 先 再 又".split())
FUNC_KO = set("나 저 너 우리 저희 이 그 저 것 거 수 때 좀 더 안 못 잘 아주 정말 진짜 네 예 아니요 아뇨 "
              "있다 없다 하다 되다 이다 아니다 보다 주다 같다 이렇다 그렇다 저렇다 씨 님".split())
KO_SKIP = ("J", "E", "XS", "XP", "S", "VCP", "VCN", "NNP", "NR", "W", "U", "Z")  # particles, endings, affixes, symbols, names, numbers


def attach_needs(lang, levels, v2):
    words = [v for l in levels for v in l["vocab"]] + [w for s in v2["sets"] for w in s["words"]]
    yue = lang == "cantonese"
    hw = {}
    for i, w in enumerate(words):
        for alt in w["t"]["s"].split(" / "):
            c = NONWORD.sub("", alt.replace("___", "")) if yue else KO_PUNCT.sub("", alt.replace("___", "")).strip()
            if c:
                hw.setdefault(c, i)
    if yue:
        import pycantonese
        longest = max(len(h) for h in hw)

        def need(s):
            ids, u = set(), 0
            for seg in pycantonese.segment(NONWORD.sub("", s)):
                if seg in FUNC_YUE or not CJK.search(seg):
                    continue
                if seg in hw:
                    ids.add(hw[seg]); continue
                i, gap = 0, False  # cover the segment with the longest headwords; a run of uncovered characters is one unknown word
                while i < len(seg):
                    n = next((n for n in range(min(longest, len(seg) - i), 0, -1) if seg[i:i + n] in hw or seg[i:i + n] in FUNC_YUE), 0)
                    if n:
                        if seg[i:i + n] in hw and seg[i:i + n] not in FUNC_YUE:
                            ids.add(hw[seg[i:i + n]])
                        i += n; gap = False
                    else:
                        u += not gap; gap = True; i += 1
            return ids, u
    else:
        from kiwipiepy import Kiwi
        kiwi = Kiwi()
        phrases = sorted((h for h in hw if " " in h or (len(h) >= 3 and not h.endswith("다"))), key=len, reverse=True)

        def need(s):
            ids, u, cover = set(), 0, [False] * len(s)
            for h in phrases:  # set phrases and multi-word entries, matched as written
                for m in re.finditer(re.escape(h), s):
                    if not any(cover[m.start():m.end()]):
                        ids.add(hw[h]); cover[m.start():m.end()] = [True] * len(h)
            toks = kiwi.tokenize(s)
            for j, t in enumerate(toks):
                if cover[t.start] or t.tag.startswith(KO_SKIP):
                    if t.tag.startswith("XSV") or t.tag.startswith("XSA"):  # noun + 하다: the -하다 verb when it is an entry
                        if j and toks[j - 1].form + "하다" in hw and not cover[toks[j - 1].start]:
                            ids.discard(hw.get(toks[j - 1].form, -1)); ids.add(hw[toks[j - 1].form + "하다"])
                    continue
                lemma = t.form + "다" if t.tag[0] == "V" else t.form
                if lemma in FUNC_KO or t.form in FUNC_KO:
                    continue
                if lemma in hw:
                    ids.add(hw[lemma])
                elif not (j + 1 < len(toks) and toks[j + 1].tag[:3] in ("XSV", "XSA") and t.form + "하다" in hw):
                    u += 1
            return ids, u

    def mark(o, s):
        ids, u = need(s)
        o["k"] = sorted(ids)
        if u:
            o["u"] = u
    for w in words:
        for x in w.get("ex", []):
            mark(x, x["s"])
    for ex in v2["extra"].values():
        for x in ex:
            mark(x, x["s"])
    for l in levels:
        for it in l["items"]:
            text = {"tiles": lambda: it["full"]["s"], "gap": lambda: it["full"]["s"], "listen": lambda: it["say"]["s"],
                    "pick": lambda: it["opts"][it["a"]]["s"],
                    "dlg": lambda: " ".join(tu["s"]["s"] if "s" in tu else tu["opts"][tu["a"]]["s"] for tu in it["turns"])}[it["t"]]()
            mark(it, text)


# ------------------------------------------------------------------ sound drills
def build_drills(lang, levels, T, want):
    rnd = random.Random(7)
    if lang == "cantonese":
        import ToJyutping
        src = json.load(open(os.path.join(REPO, "src", lang, "content", "sounds_src.json"), encoding="utf-8"))
        CJK = re.compile(r"[㐀-䶿一-鿿]")
        # Single characters with exactly one dictionary reading, from the course text and the original tone sets.
        chars = {}
        for l in levels:
            for v in l["vocab"]:
                s, r = v["t"]["s"], v["t"]["r"]
                cs = CJK.findall(s); sy = re.findall(r"[a-z]+[1-6]", r)
                if len(cs) == len(sy):
                    for c, y in zip(cs, sy):
                        chars.setdefault(c, set()).add(y)
        for jp, ch, mean, grp in src["tones"]:
            chars.setdefault(ch, set()).add(jp)
        single = {}
        for c, used in chars.items():
            try:
                cands = [j for _, js in ToJyutping.get_jyutping_candidates(c) for j in js]
            except Exception:
                continue
            if len(set(cands)) == 1 and cands[0] in used:
                single[c] = cands[0]
        meaning = {ch: mean for jp, ch, mean, grp in src["tones"]}
        tone_items = []
        for c, jp in sorted(single.items(), key=lambda kv: kv[1]):
            tone = int(jp[-1])
            want(c)
            tone_items.append({"id": f"T-{c}", "t": "tone", "s": c, "r": jp, "tone": tone, "en": meaning.get(c, "")})
        sets = []
        six = [i for i in tone_items if i["s"] in meaning]
        rest = [i for i in tone_items if i["s"] not in meaning]
        sets.append({"id": "S1", "title": "The six tones", "sub": "Hear one syllable, name its tone", "items": [i["id"] for i in six + rest[:20]]})
        hard = [i for i in tone_items if i["tone"] in (2, 3, 5, 6)]
        sets.append({"id": "S2", "title": "The hard pairs", "sub": "Tones 3 vs 6 and 2 vs 5", "items": [i["id"] for i in hard]})
        # tone patterns of real two-syllable words
        pat_items = []
        for l in levels:
            for v in l["vocab"]:
                sy = re.findall(r"[a-z]+[1-6]", v["t"]["r"])
                if len(sy) == 2 and len(CJK.findall(v["t"]["s"])) == 2:
                    pat = " ".join(x[-1] for x in sy)
                    pat_items.append({"id": f"P-{v['id']}", "t": "tpat", "s": v["t"]["s"], "r": v["t"]["r"], "pat": pat, "en": v["en"], "lv": l["n"]})
        sets.append({"id": "S3", "title": "Tones in real words", "sub": "Hear a two-syllable word, pick its tone pattern", "items": [i["id"] for i in pat_items]})
        items = tone_items + pat_items
        return sets + [{"_items": items}]
    # Korean: letters, tight/puffed sets, reading words, spelling vs sound
    from ko_pron import rom as ko_rom, strip as ko_strip
    ko_pron = cached_ko_pron()
    src = json.load(open(os.path.join(REPO, "src", lang, "content", "sounds_src.json"), encoding="utf-8"))
    items = []
    basic, extra = [], []
    for letter, rom, ex, how, kind in src["letters"]:
        want(ex)
        it = {"id": f"H-{letter}", "t": "letter", "s": letter, "rom": rom, "ex": ex, "how": how, "kind": kind}
        items.append(it)
        (extra if kind in ("tight consonant", "puffed consonant") or (kind == "vowel" and letter in "ㅐㅒㅔㅖㅘㅙㅚㅝㅞㅟㅢ") else basic).append(it["id"])
    trios = [["가", "카", "까"], ["다", "타", "따"], ["바", "파", "빠"], ["자", "차", "짜"], ["사", "싸"], ["고", "코", "꼬"], ["도", "토", "또"], ["부", "푸", "뿌"], ["지", "치", "찌"], ["시", "씨"]]
    for tr in trios:
        for s in tr:
            want(s)
            items.append({"id": f"K-{s}", "t": "trio", "s": s, "set": tr})
    extra += [f"K-{s}" for tr in trios for s in tr]
    words = {}
    for w, en in src["reading"]:
        words[w] = en
    for l in levels[:5]:
        for v in l["vocab"]:
            s = v["t"]["s"]
            if re.fullmatch(r"[가-힣]{1,4}", s):
                words.setdefault(s, v["en"])
    read = []
    for w, en in words.items():
        p = ko_pron(w)
        want(w)
        it = {"id": f"R-{w}", "t": "read", "s": w, "en": en, "r": ko_rom(p)}
        if ko_strip(p) != ko_strip(w):
            it["p"] = p
        items.append(it); read.append(it["id"])
    # spelling vs sound: words whose pronunciation differs; wrong options apply only some of the changes
    sound = []
    seen = set()
    for l in levels:
        for v in l["vocab"]:
            t = v["t"]
            if "p" not in t or len(t["s"]) > 12 or t["s"] in seen:
                continue
            s, p = re.sub(r"[?!,.]", "", t["s"]), t["p"]
            if len(s) != len(p):
                continue
            diff = [i for i, (a, b) in enumerate(zip(s, p)) if a != b]
            if not (1 <= len(diff) <= 4):
                continue
            variants = set()
            for mask in range(1, 2 ** len(diff) - 1):
                chars = list(s)
                for k, i in enumerate(diff):
                    if mask >> k & 1:
                        chars[i] = p[i]
                variants.add("".join(chars))
            variants.discard(p)
            wrong = [s] + sorted(variants)[:2]
            if len(wrong) < 2:
                continue
            seen.add(t["s"])
            items.append({"id": f"P-{v['id']}", "t": "sound", "s": t["s"], "p": p, "wrong": wrong[:3], "en": v["en"]})
            sound.append(f"P-{v['id']}")
    sets = [
        {"id": "H1", "title": "Basic letters", "sub": "14 consonants and the simple vowels", "items": basic},
        {"id": "H2", "title": "Puffed, tight and combined", "sub": "ㅋ/ㄲ-type consonants and the w- and y- vowels", "items": extra},
        {"id": "H3", "title": "Reading words", "sub": "Sound out whole words", "items": read},
        {"id": "H4", "title": "Spelling vs sound", "sub": "How words change when spoken", "items": sound},
    ]
    return sets + [{"_items": items}]


# Hosted page only: home-screen app links, Study Hall sign-in, saved progress, AI and voices.
HOSTED = """<link rel="manifest" href="../manifest.webmanifest">
<link rel="icon" href="../icons/icon-192.png">
<link rel="apple-touch-icon" href="../icons/apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Study Hall">
<script src="../shared/supabase.js"></script>
<script src="../shared/sh.js"></script>
<script src="../shared/voice.js"></script>
<script>SH.install("__COURSE__"); window.SH_HOSTED = true;</script>"""

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    for lang in (["cantonese", "korean"] if which == "all" else [which]):
        build(lang)
