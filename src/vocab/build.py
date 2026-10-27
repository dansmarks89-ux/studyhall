"""Build Word Power: src/vocab/app.html + src/vocab/data/{items,passages,gloss}.json
   -> vocab/index.html, vocab/data.<hash>.json (cards and passages), vocab/gloss.<hash>.json

  python3 src/vocab/build.py [site root]     (default: the repo root, two levels above this file)

The data files are named by a hash of their content, so browsers can keep them for good.
The previous build's files (the ones the old index.html names) are kept for one more deploy, for devices that
still have the old page; older hashed files in vocab/ are deleted.
"""
import hashlib, json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, "vocab")

def load(name): return json.load(open(os.path.join(HERE, "data", name), encoding="utf-8"))

def write(stem, obj):
    b = json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    name = f"{stem}.{hashlib.sha256(b).hexdigest()[:10]}.json"
    open(os.path.join(OUT, name), "wb").write(b)
    print("wrote", name, len(b), "bytes")
    return name

src = open(os.path.join(HERE, "app.html"), encoding="utf-8").read()
assert src.count("__DATA__") == 1 and src.count("__GLOSS__") == 1
items = [{k: v for k, v in x.items() if k != "_old"} for x in load("items.json")]
passages = load("passages.json")
gloss = load("gloss.json")
ids = {x["id"] for x in items}
for g in passages: assert set(g["words"]) <= ids, g["id"] + ": a target word has no card"

os.makedirs(OUT, exist_ok=True)
HASHED = re.compile(r"(?:data|gloss)\.[0-9a-f]{10}\.json")
INDEX = os.path.join(OUT, "index.html")
keep = set(HASHED.findall(open(INDEX, encoding="utf-8").read())) if os.path.exists(INDEX) else set()
names = [write("data", {"items": items, "passages": passages}), write("gloss", gloss)]
for f in os.listdir(OUT):
    if HASHED.fullmatch(f) and f not in keep and f not in names: os.remove(os.path.join(OUT, f))
open(INDEX, "w", encoding="utf-8").write(src.replace("__DATA__", names[0]).replace("__GLOSS__", names[1]))
print("wrote", INDEX, len(items), "items,", len(passages), "passages")
sys.exit(subprocess.run([sys.executable, os.path.join(os.path.dirname(HERE), "lint.py")]).returncode)
