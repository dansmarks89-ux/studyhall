"""Build the Study Hall Cantonese and Korean courses.

    python3 src/lang/build.py cantonese     -> cantonese/index.html + cantonese/audio.json
    python3 src/lang/build.py korean        -> korean/index.html + korean/audio.json
    python3 src/lang/build.py all

Inputs: src/<lang>/content/levels/L1..L10.json (checked with tools/check_level.py),
src/<lang>/content/sounds_src.json, the pronunciation guide in tools/build_app.py,
and the shared engine src/lang/app.html.
audio.json lists every clip the page can play; the Supabase "tts" function records the missing ones.
"""
import json, os, re, sys, hashlib, random
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(HERE, "tools"))

CONF = {
    "cantonese": dict(code="yue", name="Cantonese", native="廣東話", htmllang="zh-HK", course="cantonese",
                      voice="zh-HK-HiuMaanNeural", voice2="zh-HK-WanLungNeural", romName="Jyutping",
                      font="Noto+Sans+TC", fontFamily="Noto Sans TC", fontFallback='"PingFang HK","PingFang TC","Microsoft JhengHei",sans-serif',
                      ttsLang="zh-HK", voiceRe=r"^(yue|zh[-_](HK|Hant[-_]HK))", voiceNameRe=r"cantonese|粵|粤"),
    "korean": dict(code="ko", name="Korean", native="한국어", htmllang="ko", course="korean",
                   voice="ko-KR-SunHi:DragonHDLatestNeural", voice2="ko-KR-Hyunsu:DragonHDLatestNeural", romName="romanization",
                   font="Noto+Sans+KR", fontFamily="Noto Sans KR", fontFallback='"Apple SD Gothic Neo","Malgun Gothic",sans-serif',
                   ttsLang="ko-KR", voiceRe=r"^ko", voiceNameRe=r"korean|한국"),
}
RATE = "0%"
clip = lambda voice, text: hashlib.sha256(f"{voice}|{RATE}|{text}".encode()).hexdigest()[:32]


def build(lang):
    C = CONF[lang]
    yue = C["code"] == "yue"
    base = os.path.join(REPO, "src", lang, "content")
    if not yue:
        from ko_pron import pron as ko_pron, rom as ko_rom, strip as ko_strip
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

    # pronunciation guide (from the original flashcard pages), with the study steps rewritten for the course
    import build_app as B
    guide = B.yue_guide() if yue else B.ko_guide()
    steps = HOWTO[lang]
    guide = re.sub(r"<section><h2>How to study</h2>.*?</section>", steps, guide, flags=re.S)
    for m in re.finditer(r'data-say="([^"]+)"', guide):
        want(m.group(1))

    data = {"levels": levels, "drills": drills, "guide": guide,
            "audio": {f"{v}|{t}": n for (v, t), n in audio.items()}}
    cfg = {"course": C["course"], "lang": C["code"], "name": C["name"], "native": C["native"], "htmlLang": C["htmllang"],
           "voice": C["voice"], "voice2": C["voice2"], "romName": C["romName"], "ttsLang": C["ttsLang"],
           "voiceRe": C["voiceRe"], "voiceNameRe": C["voiceNameRe"],
           "audioBase": "https://wbrssohmepioxapwbcne.supabase.co/storage/v1/object/public/audio/" + C["course"] + "/"}
    src = open(os.path.join(HERE, "app.html"), encoding="utf-8").read()
    rep = {"__CONFIG__": json.dumps(cfg, ensure_ascii=False), "__DATA__": json.dumps(data, ensure_ascii=False, separators=(",", ":")),
           "__NAME__": C["name"], "__NATIVE__": C["native"], "__HTMLLANG__": C["htmllang"], "__FONT__": C["font"],
           "__FONTFAMILY__": C["fontFamily"], "__FONTFALLBACK__": C["fontFallback"], "__THEME__": THEMES[lang]}
    for k in sorted(rep, key=len, reverse=True):
        assert k in src, k
        src = src.replace(k, rep[k])
    left = re.findall(r"__[A-Z]+__", src)
    assert not left, left
    outdir = os.path.join(REPO, C["course"])
    os.makedirs(outdir, exist_ok=True)
    head, body = src.split('<div class="wrap">', 1)
    page = HOSTED_HEAD.replace("__COURSE__", C["course"]).replace("</head>\n<body>\n", head + "</head>\n<body>\n") + '<div class="wrap">' + body + "\n</body>\n</html>\n"
    open(os.path.join(outdir, "index.html"), "w", encoding="utf-8").write(page)
    manifest = [{"n": n, "t": t, "v": v, "r": RATE} for (v, t), n in sorted(audio.items(), key=lambda kv: kv[1])]
    json.dump(manifest, open(os.path.join(outdir, "audio.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    # claude.ai preview build (no Study Hall sign-in)
    os.makedirs(os.path.join(REPO, "build"), exist_ok=True)
    open(os.path.join(REPO, "build", f"{C['course']}-course.html"), "w", encoding="utf-8").write(src)
    nitems = sum(len(l["items"]) for l in levels); nv = sum(len(l["vocab"]) for l in levels)
    print(f"{lang}: {nitems} items, {nv} vocab, {len(drills[-1]['_items'])} drill items, {len(audio)} audio clips, page {os.path.getsize(os.path.join(outdir, 'index.html'))//1024} KB")


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
    from ko_pron import pron as ko_pron, rom as ko_rom, strip as ko_strip
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


HOWTO = {
    "cantonese": """<section><h2>How to study</h2><ol>
<li>Play every example on this page and copy it out loud. Come back to it whenever a sound confuses you.</li>
<li>Start <b>Sounds → The six tones</b>. Each card plays a syllable and you name the tone. This is the core skill of Cantonese listening.</li>
<li>Open <b>Level 1</b>: read the short lesson, practise, then take the 30-question test. 90% unlocks the next level. If a level already feels easy, go straight to its test.</li>
<li><b>Today</b> mixes your reviews, your weak spots and new material. Doing it daily is the fastest way forward.</li>
<li><b>Cards</b> drills the words and phrases of every unlocked level: see &amp; hear, listen only, or say it.</li>
<li>Always answer out loud before you check, then play the audio and copy it.</li>
</ol></section>""",
    "korean": """<section><h2>How to study</h2><ol>
<li>Play every example on this page and copy it out loud.</li>
<li>Work through <b>Sounds → Basic letters</b> and <b>Reading words</b> first. Most people can read Hangul after a few short sessions.</li>
<li>Open <b>Level 1</b>: read the short lesson, practise, then take the 30-question test. 90% unlocks the next level. If a level already feels easy, go straight to its test.</li>
<li><b>Today</b> mixes your reviews, your weak spots and new material. Doing it daily is the fastest way forward.</li>
<li><b>Cards</b> drills the words and phrases of every unlocked level. Romanization is training wheels: once you can read Hangul, turn it off in Settings.</li>
<li>Always answer out loud before you check, then play the audio and copy it.</li>
</ol></section>""",
}

THEMES = {
    "cantonese": """:root{--paper:#F8F6F5;--panel:#FFFFFF;--ink:#1F1A19;--muted:#6B605E;--line:#E6DFDD;--accent:#B0231A;--accent-ink:#FFFFFF;--accent-soft:#F8E7E4;--ground:rgba(176,35,26,.07)}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--paper:#141112;--panel:#1C1819;--ink:#ECE9E8;--muted:#A39C9A;--line:#352C2B;--accent:#FF8A7A;--accent-ink:#141112;--accent-soft:#3A2422;--ground:rgba(255,138,122,.07);color-scheme:dark}}
:root[data-theme="dark"]{--paper:#141112;--panel:#1C1819;--ink:#ECE9E8;--muted:#A39C9A;--line:#352C2B;--accent:#FF8A7A;--accent-ink:#141112;--accent-soft:#3A2422;--ground:rgba(255,138,122,.07);color-scheme:dark}""",
    "korean": """:root{--paper:#F6F7F5;--panel:#FFFFFF;--ink:#18201C;--muted:#5F6964;--line:#DEE4E0;--accent:#2647A8;--accent-ink:#FFFFFF;--accent-soft:#E6EBF8;--ground:rgba(30,120,80,.08)}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--paper:#101413;--panel:#171C1B;--ink:#E9EDEB;--muted:#9AA5A0;--line:#2A3230;--accent:#8FA8FF;--accent-ink:#101413;--accent-soft:#1E2742;--ground:rgba(120,200,160,.06);color-scheme:dark}}
:root[data-theme="dark"]{--paper:#101413;--panel:#171C1B;--ink:#E9EDEB;--muted:#9AA5A0;--line:#2A3230;--accent:#8FA8FF;--accent-ink:#101413;--accent-soft:#1E2742;--ground:rgba(120,200,160,.06);color-scheme:dark}""",
}

HOSTED_HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<link rel="manifest" href="../manifest.webmanifest">
<link rel="icon" href="../icons/icon-192.png">
<link rel="apple-touch-icon" href="../icons/apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Study Hall">
<script src="../shared/supabase.js"></script>
<script src="../shared/sh.js"></script>
<script>SH.install("__COURSE__"); window.SH_HOSTED = true;</script>
</head>
<body>
"""

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    for lang in (["cantonese", "korean"] if which == "all" else [which]):
        build(lang)
