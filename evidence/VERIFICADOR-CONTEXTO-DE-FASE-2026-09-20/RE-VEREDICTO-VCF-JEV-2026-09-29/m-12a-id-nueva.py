import json
import os
import sys

D, TITULO = sys.argv[1], sys.argv[2]
d = json.load(open(os.path.join(D, "09-source-list-post-t1.json"), encoding="utf-8"))
fuentes = d if isinstance(d, list) else (d.get("sources") or d.get("data") or [])
ids = [f.get("id") for f in fuentes if (f.get("title") or "") == TITULO]
if not ids:
    print("AUSENTE")
elif len(ids) > 1:
    print("MULTIPLES %s" % " ".join(ids))
else:
    print(ids[0])
