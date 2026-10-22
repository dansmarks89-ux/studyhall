"""Build Word Power: src/vocab/app.html + src/vocab/data/items.json -> vocab/index.html

  python3 src/vocab/build.py
"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
src = open(os.path.join(HERE, "app.html"), encoding="utf-8").read()
items = json.load(open(os.path.join(HERE, "data", "items.json"), encoding="utf-8"))
assert src.count("__DATA__") == 1
data = json.dumps(items, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
out = os.path.join(REPO, "vocab", "index.html"); os.makedirs(os.path.dirname(out), exist_ok=True)
open(out, "w", encoding="utf-8").write(src.replace("__DATA__", data))
print("wrote", out, os.path.getsize(out), "bytes,", len(items), "items")
