"""Build the Clinic Spanish course from src/spanish/app.html + src/spanish/data/*.json.

  python3 src/spanish/build.py hosted   -> spanish/index.html (the Study Hall page)
  python3 src/spanish/build.py claude   -> build/clinic-spanish-course.html (claude.ai artifact version)

Both first run content/vocab2/gen_vocab2.py (Everyday words + more clinic words -> data/vocab2.json).
The hosted page loads that as spanish/vocab2.<hash>.json (named by content, so browsers keep it for good);
the previous build's file is kept for pages still open, older ones are deleted. The claude version inlines it.

Run from anywhere; paths are relative to this file.
"""
import hashlib, json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
subprocess.run([sys.executable, os.path.join(HERE, "content", "vocab2", "gen_vocab2.py")], check=True)
src = open(os.path.join(HERE, "app.html"), encoding="utf-8").read()
def j(name): return json.dumps(json.load(open(os.path.join(HERE, "data", name), encoding="utf-8")), ensure_ascii=False, separators=(",", ":"))
for ph, f in [("__LEVELS__", "levels.tagged.json"), ("__DRILLS__", "drills.tagged.json"), ("__CONJ__", "conj.json"), ("__VERBS__", "cards.tagged.json")]:
    assert src.count(ph) == 1, ph
    src = src.replace(ph, j(f))

assert src.count("__VOCAB2__") == 1
vocab2 = j("vocab2.json")

target = sys.argv[1]
if target == "claude":
    out = os.path.join(REPO, "build", "clinic-spanish-course.html"); os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(src.replace("__VOCAB2__", vocab2))
elif target == "hosted":
    OUT = os.path.join(REPO, "spanish"); os.makedirs(OUT, exist_ok=True)
    HASHED = re.compile(r"vocab2\.[0-9a-f]{10}\.json")
    INDEX = os.path.join(OUT, "index.html")
    keep = set(HASHED.findall(open(INDEX, encoding="utf-8").read())) if os.path.exists(INDEX) else set()
    b = vocab2.encode("utf-8"); name = f"vocab2.{hashlib.sha256(b).hexdigest()[:10]}.json"
    open(os.path.join(OUT, name), "wb").write(b)
    for f in os.listdir(OUT):
        if HASHED.fullmatch(f) and f not in keep and f != name: os.remove(os.path.join(OUT, f))
    print("wrote", name, len(b), "bytes")
    src = src.replace("__VOCAB2__", json.dumps(name))
    def sub(old, new, count=1):
        global src
        n = src.count(old)
        assert n == count, (old, n)
        src = src.replace(old, new)
    # messages that mention claude.ai
    sub('return "Claude isn\'t available on this page (permission was declined or Claude is turned off for your account). The rest of the course works without it.";',
        'return (e&&e.message)||"You don\'t have AI access for this course. The rest of the course works without it.";')
    sub('if(code==="rate_limited") return "Too many requests right now, or your Claude usage limit was reached. Try again in a little while.";',
        'if(code==="rate_limited") return (e&&e.message)||"Too many requests right now. Try again in a little while.";')
    sub('if(code==="session_expired") return "Your session expired. Sign in to Claude again, then reload this page.";',
        'if(code==="session_expired") return "You were signed out. Reload this page to sign in again.";')
    sub('$("talkstatus").textContent="Claude isn\'t available here. Open this page inside claude.ai to use conversations.";',
        '$("talkstatus").textContent="AI isn\'t available right now. Reload the page and try again.";')
    sub('return "The connection to Claude failed. Press Send to try again.";',
        'return ((e&&e.message)||"Something went wrong.")+" Press Send to try again.";')
    sub(" It uses your Claude usage, and the first time it asks your permission.</p>",
        " Each person gets a set number of AI replies per day.</p>")
    sub("Claude reads your record and tells you what to work on next. Uses your Claude usage.</p>",
        "Claude reads your record and tells you what to work on next.</p>")
    sub('<h1>Clinic Spanish Course</h1>',
        '<h1><a href="../" class="shhome" aria-label="Study Hall home">Study Hall</a> <span aria-hidden="true">/</span> Clinic Spanish</h1>')
    sub('<span class="sub" id="sync">Progress saved in this browser</span>',
        '<span class="sub" id="sync">Progress saved in this browser</span><span class="sub" id="shwho"></span>')
    head, body = src.split('<div class="wrap">', 1)
    extra_css = ("<style>body{margin:0}.wrap{padding-top:max(20px,env(safe-area-inset-top));padding-bottom:max(48px,env(safe-area-inset-bottom))}"
                 ".shhome{color:var(--muted);text-decoration:none;font-weight:400}.shhome:hover{text-decoration:underline}"
                 "#shwho{display:flex;gap:10px;align-items:baseline}#shwho button{font:inherit;color:var(--focus);background:none;border:0;padding:0;cursor:pointer;text-decoration:underline}</style>")
    page = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            '<meta name="theme-color" content="#FDFBFA" media="(prefers-color-scheme: light)">\n'
            '<meta name="theme-color" content="#11151B" media="(prefers-color-scheme: dark)">\n'
            '<link rel="manifest" href="../manifest.webmanifest">\n'
            '<link rel="icon" href="../icons/icon-192.png">\n'
            '<link rel="apple-touch-icon" href="../icons/apple-touch-icon.png">\n'
            '<meta name="apple-mobile-web-app-capable" content="yes">\n'
            '<meta name="mobile-web-app-capable" content="yes">\n'
            '<meta name="apple-mobile-web-app-title" content="Study Hall">\n'
            + head + extra_css + '\n'
            '<script src="../shared/supabase.js"></script>\n<script src="../shared/sh.js"></script>\n'
            '<script>SH.install("spanish");</script>\n<script src="../shared/voice.js"></script>\n'
            '</head>\n<body>\n<div class="wrap">' + body + '\n</body>\n</html>\n')
    out = INDEX
    open(out, "w", encoding="utf-8").write(page)
else:
    sys.exit("target: claude | hosted")
print("wrote", out, os.path.getsize(out))
