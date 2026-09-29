import json, pathlib, sys
d = pathlib.Path(sys.argv[1])
pre = json.loads((d / "01-c1-report-pre.json").read_text(encoding="utf-8"))
post = json.loads((d / "03-c1-report-post.json").read_text(encoding="utf-8"))
out = []
for nombre, inf in (("PRE", pre), ("POST", post)):
    cb = inf["coverage_basis"]
    out.append(f"{nombre}: status={inf['status']} families={len(cb['families_not_covered'])} "
               f"poblacion={json.dumps(cb['poblacion'], sort_keys=True, ensure_ascii=False)} "
               f"quick_total={cb['fuentes']['quick']['total']} hook_total={cb['fuentes']['hook']['total']} "
               f"instancias={cb['poblacion']['instancias_totales']}")
    out.append(f"  familias={[f['familia'] for f in cb['families_not_covered']]}")
print("\n".join(out))
misma = (pre["coverage_basis"]["poblacion"] == post["coverage_basis"]["poblacion"]
         and [f["familia"] for f in pre["coverage_basis"]["families_not_covered"]]
         == [f["familia"] for f in post["coverage_basis"]["families_not_covered"]])
print("POBLACION_Y_FAMILIAS_IDENTICAS:", misma)
est_pre = [f["estado"] for f in pre["coverage_basis"]["families_not_covered"]]
est_post = [f["estado"] for f in post["coverage_basis"]["families_not_covered"]]
for i, (a, b) in enumerate(zip(est_pre, est_post), 1):
    print(f"estado[{i}] PRE ={a}")
    print(f"estado[{i}] POST={b}")
print("estados que cambiaron:", sum(1 for a, b in zip(est_pre, est_post) if a != b))
