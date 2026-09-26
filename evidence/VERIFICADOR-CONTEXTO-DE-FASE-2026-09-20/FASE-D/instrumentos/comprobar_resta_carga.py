"""Instrumento de cierre de FASE-D: comprueba la resta del par pre/post de carga (AC20).

Lee `carga.json` y los dos archivos del par (`faseD_carga_pre.txt`, `faseD_carga_post.txt`,
producidos con `stat -c %s`), y publica la resta **comprobada** o el descuadre. No escribe nada
salvo el destino que se le pasa por argumento (S13).

Uso del cierre:

    ./venv/Scripts/python.exe \\
      evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/instrumentos/comprobar_resta_carga.py \\
      --evidencia evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D \\
      > evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/carga-pre-post.md
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]

# La consola de este entorno es cp1252 y el destino es un artefacto en UTF-8 (L-VCF-3, en su
# vertiente de archivo escrito y no de marca leida por grep).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def _suma(par: Path) -> int:
    for linea in par.read_text(encoding="utf-8").splitlines():
        if linea.startswith("SUMA"):
            return int(linea.split()[1])
    raise SystemExit(f"[2] {par} no trae la linea SUMA: el par esta incompleto")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--evidencia", required=True, type=Path)
    args = ap.parse_args()
    ev = args.evidencia if args.evidencia.is_absolute() else ROOT / args.evidencia
    carga = json.loads((ev / "carga.json").read_text(encoding="utf-8"))
    pre_stat = _suma(ev / "faseD_carga_pre.txt")
    post_stat = _suma(ev / "faseD_carga_post.txt")
    coste = sum(f["after"]["coste_de_generacion"] for f in carga["por_fase"])
    pre = carga["total"]["before"]["total"]
    post = carga["total"]["after"]["total"]
    delta = pre - post
    divisor = carga["method"]["divisor_tokens"]

    comprueban = {
        "stat_pre == total_before": pre_stat == pre,
        "stat_post + coste == total_after": post_stat + coste == post,
        "suma por fase == total (before)": sum(
            f["before"]["total"] for f in carga["por_fase"]) == pre,
        "suma por fase == total (after)": sum(
            f["after"]["total"] for f in carga["por_fase"]) == post,
        "identidad del delta por fase": all(f["resta_comprobada"] for f in carga["por_fase"]),
    }
    print("# PAR PRE/POST de carga de lectura (AC20) — FASE-D")
    print()
    print(f"- comando de los dos lados: `{carga['method']['comando_bytes']}` "
          "(las rutas estan en `carga.json` -> `rutas_stat`; sin deduplicar: cada fase abre su "
          "copia del workflow)")
    print(f"- comando que produce el pack: `{carga['method']['comando_generacion']}`")
    print(f"- tokens: estimados por divisor {divisor} declarado, no recuento de tokenizer")
    print()
    print("| lado | stat -c %s | total en carga.json | coste de generar |")
    print("|---|---|---|---|")
    print(f"| before | {pre_stat} | {pre} | 0 |")
    print(f"| after | {post_stat} | {post} | {coste} |")
    print()
    print(f"**Resta entre cargas totales: {pre} - {post} = {delta} bytes "
          f"(~{delta // divisor} tokens estimados).**")
    print()
    print("Comprobaciones:")
    for k, v in comprueban.items():
        print(f"- [{'x' if v else ' '}] {k}: {'OK' if v else 'DESCUADRE'}")
    print()
    print("Lectura obligatoria (contrato §Carga total y frescura del pack): la resta **no** es "
          "«fuentes contra pack». Cada lado publica sus tres sumandos y el unico ahorro "
          "atribuible al pack es lo que no entro porque no se declaro "
          "(`omitido_declarado_bytes`), neteado por el andamiaje del propio pack "
          "(`andamiaje_del_pack_bytes`) y por el coste de generarlo. El workflow canonico sigue "
          "en los dos lados: este plan no lo rebanó (deuda D3), y por eso el delta no puede "
          "presentarse como un tercio de la carga.")
    return 0 if all(comprueban.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
