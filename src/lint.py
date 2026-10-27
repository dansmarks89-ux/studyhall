"""Checks the built pages' scripts for names that are used but never declared (a leftover after a refactor, a typo).
In strict mode such a name throws as soon as its line runs, which stops the exercise on screen.

  python3 src/lint.py        -> exits 1 and lists each problem; every build runs it after writing its page

Rules and the shared scripts' globals are in src/eslint.config.mjs. Needs Node and, once per clone, `npm ci` in the
repo folder (installs the pinned ESLint from package.json)."""
import os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = ["index.html", "spanish/index.html", "cantonese/index.html", "korean/index.html", "vocab/index.html"]
SCRIPTS = ["shared/sh.js", "shared/ui.js", "shared/voice.js"]

eslint = os.path.join(ROOT, "node_modules", ".bin", "eslint")
if not os.path.exists(eslint):
    sys.exit("lint: ESLint isn't installed. Run `npm ci` in " + ROOT + " once, then build again.")

with tempfile.TemporaryDirectory() as tmp:
    files = [os.path.join(ROOT, s) for s in SCRIPTS]
    for page in PAGES:
        html = open(os.path.join(ROOT, page), encoding="utf-8").read()
        for i, js in enumerate(re.findall(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", html, re.S)):
            f = os.path.join(tmp, page.replace("/", "_") + f".{i}.js")
            open(f, "w", encoding="utf-8").write(js)
            files.append(f)
    r = subprocess.run([eslint, "--config", os.path.join(ROOT, "src", "eslint.config.mjs"), "--no-warn-ignored", *files],
                       capture_output=True, text=True, cwd=tmp)
    if r.returncode:
        sys.exit("lint: undeclared names (page_name.N.js is the Nth inline script of that page)\n" + (r.stdout or r.stderr))
print("lint: ok,", len(files), "scripts")
