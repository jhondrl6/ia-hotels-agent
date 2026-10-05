# -*- coding: utf-8 -*-
"""Arnés de contraste de FASE-RELEASE: re-emision vs lo publicado, y determinismo de la corrida.

No mutacion nada del expediente: escribe las dos corridas de determinismo bajo `temp/` (excluido por
`.gitignore`) y compara por sha256 y por clave estructural. Compara `sha256_de_los_insumos` y los
cocientes, no el archivo entero: el limite declarado en FASE-B2 §12 dice que el bloque `insumos`
publica las rutas tal como se pasaron y `fecha` es la de la invocacion, asi que la identidad byte a
byte solo vale dentro de la misma invocacion.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EXP = ROOT / "evidence" / "EVALUACION-JEV-TYPESAFE-2026-09-21"
SCRATCH = ROOT / "temp" / "fase-release-2026-10-05"
RUNNER = str(ROOT / "scripts" / "evaluate_jev_pilot.py")

REPORT_FLAGS = [
    "--respuestas", str(EXP / "FASE-C" / "respuestas.jsonl"),
    "--etiquetas", str(EXP / "etiquetas.json"),
    "--muestra", str(EXP / "muestra.json"),
    "--protocolo", str(EXP / "protocolo.json"),
]
DECIDE_FLAGS = [
    "--protocolo", str(EXP / "protocolo.json"),
]

COCIENTES = ("recuperacion", "precision_entre_propuestas", "recall_importante_candidatos",
             "extremo_a_extremo")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def carga(path: Path):
    return json.loads(path.read_bytes().decode("utf-8"))


def rutas(obj, pref=""):
    """Todas las hojas del JSON por su ruta, para un diferencial exacto."""
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            out.update(rutas(v, f"{pref}.{k}" if pref else k))
        return out
    if isinstance(obj, list):
        out = {}
        for i, v in enumerate(obj):
            out.update(rutas(v, f"{pref}[{i}]"))
        return out
    return {pref: obj}


def diferencial(a, b, ignora=()):
    ha, hb = rutas(a), rutas(b)
    claves = sorted(set(ha) | set(hb))
    dif = []
    for c in claves:
        if any(c == p or c.startswith(p + ".") or c.startswith(p + "[") for p in ignora):
            continue
        if ha.get(c, "<AUSENTE>") != hb.get(c, "<AUSENTE>"):
            dif.append((c, ha.get(c, "<AUSENTE>"), hb.get(c, "<AUSENTE>")))
    return dif


def tabla_cocientes(d, etiqueta):
    print(f"  [{etiqueta}]")
    for brazo in ("capa_fria", "jev", "deepseek"):
        b = d.get("por_brazo", {}).get(brazo, {})
        celdas = []
        for co in COCIENTES:
            m = b.get(co)
            if isinstance(m, dict) and "value" in m:
                celdas.append(f"{co}={m['value']} ({m['numerator']}/{m['denominator']})")
            else:
                celdas.append(f"{co}=<NO LA PRODUCE>")
        print("    " + brazo + ": " + " | ".join(celdas))


def main():
    print("=" * 78)
    print("== 1. shas de los artefactos de las tres hojas (identidad completa, no normalizada)")
    print("=" * 78)
    for nombre in ("informe_comparativa.json", "decision.json", "decision.md"):
        for hoja in ("FASE-C", "FASE-B2", "FASE-RELEASE"):
            p = EXP / hoja / nombre
            print(f"  {nombre:28s} {hoja:13s} {'AUSENTE' if not p.is_file() else sha(p)[:16] + '...'}")
        print()

    print("=" * 78)
    print("== 2. sha256_de_los_insumos: FASE-B2 vs FASE-RELEASE")
    print("=" * 78)
    i_b2 = carga(EXP / "FASE-B2" / "informe_comparativa.json")
    i_rel = carga(EXP / "FASE-RELEASE" / "informe_comparativa.json")
    s_b2, s_rel = i_b2["sha256_de_los_insumos"], i_rel["sha256_de_los_insumos"]
    for k in sorted(s_b2):
        mismo = s_b2[k] == s_rel.get(k)
        print(f"  {k:11s} {'IGUAL' if mismo else 'DIVERGE'}  {s_b2[k][:16]}... vs {s_rel.get(k, '<AUSENTE>')[:16]}...")
    print(f"  => los cuatro insumos son {'los mismos bytes' if s_b2 == s_rel else 'DISTINTOS'}")
    print(f"  fechas: B2={i_b2['fecha']} RELEASE={i_rel['fecha']}")
    print(f"  bloque `insumos` (rutas tal como se pasaron): "
          f"{'IGUAL' if i_b2['insumos'] == i_rel['insumos'] else 'DISTINTO'}")

    print()
    print("=" * 78)
    print("== 3. cocientes publicados por el instrumento, brazo por brazo")
    print("=" * 78)
    tabla_cocientes(i_b2, "FASE-B2 (2026-10-04)")
    tabla_cocientes(i_rel, "FASE-RELEASE (2026-10-05)")
    dif_inf = diferencial(i_b2, i_rel, ignora=("fecha",))
    print(f"\n  diferencial informe B2 vs RELEASE ignorando `fecha`: {len(dif_inf)} claves")
    for c, a, b in dif_inf:
        print(f"    {c}: {a!r} -> {b!r}")

    print()
    print("=" * 78)
    print("== 4. el registro de C, escrito SIN instrumento: mismo asunto, otra forma")
    print("=" * 78)
    i_c = carga(EXP / "FASE-C" / "informe_comparativa.json")
    print(f"  claves del informe de C: {list(i_c)}")
    print("  recuperacion por brazo publicada por C (lectura de sesion, schema sin `por_brazo/cocientes`):")
    for brazo, v in i_c.get("por_brazo", {}).items():
        rec = v.get("recuperacion")
        print(f"    {brazo}: recuperacion={rec}")
    d_c = carga(EXP / "FASE-C" / "decision.json")
    print(f"\n  decision.json de C  : run_status={d_c['run_status']} decision={d_c['decision']} "
          f"transfer={d_c['transfer_status']}")
    print(f"  cobertura_min de C  : {d_c['criterios_congelados_aplicados_sin_releerlos']['cobertura_min']['medido']}")
    d_rel = carga(EXP / "FASE-RELEASE" / "decision.json")
    print(f"  cobertura_min RELEASE: {d_rel['criterios_congelados']['cobertura_min']['medido_por_brazo']}")
    for campo in ("run_status", "decision", "transfer_status"):
        mismo = d_c.get(campo) == d_rel.get(campo)
        print(f"  {campo}: C={d_c.get(campo)!r} RELEASE={d_rel.get(campo)!r} -> {'COINCIDE' if mismo else 'DIVERGE'}")
    dif_dec = diferencial(carga(EXP / "FASE-B2" / "decision.json"), d_rel, ignora=("fecha",))
    print(f"\n  diferencial decision.json B2 vs RELEASE ignorando `fecha`: {len(dif_dec)} claves")
    for c, a, b in dif_dec:
        print(f"    {c}: {str(a)[:70]!r} -> {str(b)[:70]!r}")

    print()
    print("=" * 78)
    print("== 5. determinismo: dos corridas de `report` con la misma invocacion")
    print("=" * 78)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    shas = []
    for i in (1, 2):
        destino = SCRATCH / f"informe-{i}.json"
        r = subprocess.run([sys.executable, RUNNER, "report", *REPORT_FLAGS,
                            "--out", str(destino), "--fecha", "2026-10-05"],
                           capture_output=True, text=True, cwd=str(ROOT))
        print(f"  corrida {i}: EXIT={r.returncode} sha={sha(destino)[:16] if destino.is_file() else '<sin archivo>'}...")
        shas.append(sha(destino) if destino.is_file() else None)
    print(f"  byte a byte: {'IDENTICOS' if shas[0] == shas[1] else 'DISTINTOS'}")

    print()
    print("== 6. con otra fecha, solo se mueve la linea `fecha` (limite de B2 §12, re-medido aqui)")
    SCRATCH2 = SCRATCH / "fecha"
    SCRATCH2.mkdir(parents=True, exist_ok=True)
    destino = SCRATCH2 / "informe.json"
    r = subprocess.run([sys.executable, RUNNER, "report", *REPORT_FLAGS,
                        "--out", str(destino), "--fecha", "2020-01-01"],
                       capture_output=True, text=True, cwd=str(ROOT))
    print(f"  EXIT={r.returncode}")
    d_otra = carga(destino)
    dif_fecha = diferencial(i_rel, d_otra)
    for c, a, b in dif_fecha:
        print(f"    {c}: {str(a)[:60]!r} -> {str(b)[:60]!r}")
    print(f"  claves movidas: {len(dif_fecha)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
