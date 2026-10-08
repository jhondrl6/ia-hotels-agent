"""Contrafactual del check [17/18]: que regla goberna realmente el par (instantanea, cuerpo).

Monta la poblacion en un tmp (no toca el arbol del repo) y corre verificar_contenido() del
instrumento versionado sobre dos casos:
  A) la subida es byte-identica al cuerpo del plan  -> se espera vigente (codigo 0)
  B) la subida es una copia saneada (identidad sustituida) -> se espera VENCIDO (codigo 1)
Si B cae rojo, el check es insatisfacible para cualquier plan cuyo 10-analisis lleve identidad de
cliente, que es exactamente el caso que el propio plan obliga a sanear.
"""
import hashlib
import io
import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path.cwd() / "scripts"))
import validate_qmind_writeback as V  # noqa: E402

CUERPO = Path(".opencode/plans/Archives/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/10-analisis-post-implementacion.md").read_bytes()
SANEADA = Path("evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-RELEASE/qmind-upload-10-analisis-cierre-4.79.0-saneado.md").read_bytes()
PLAN = "CONTRAFACTUAL-PLAN"


def caso(nombre, subido):
    tmp = Path(tempfile.mkdtemp(prefix="cf1718-"))
    try:
        plans = tmp / "plans"
        destino = plans / "Archives" / PLAN
        destino.mkdir(parents=True)
        (destino / "10-analisis-post-implementacion.md").write_bytes(CUERPO)
        snap = tmp / "instantaneas"
        snap.mkdir()
        inst = snap / (PLAN + "--10-analisis.md")
        inst.write_bytes(subido)
        registro = tmp / "registro.json"
        json.dump({"schema_version": "1.0", "entradas": [{
            "plan": PLAN, "titulo": "10-analisis: " + PLAN + " (contrafactual)", "estado": "vigente",
            "fuente_id": "src-1", "sha256": hashlib.sha256(subido).hexdigest(),
            "instanea": inst.name, "publicado": "2026-10-07"}]}, io.open(registro, "w", encoding="utf-8"))
        fuentes = []  # sin poblacion de notebook: se observa solo la primera puerta (instanea vs cuerpo)
        codigo, lineas = V.verificar_contenido("nb", fuentes, json.load(io.open(registro, encoding="utf-8")),
                                               tmp / "scratch", plans_dir=plans, registro_path=registro)
        print("=== %s ===" % nombre)
        print("  sha(instantanea) = %s  sha(cuerpo) = %s" % (hashlib.sha256(subido).hexdigest()[:12],
                                                             hashlib.sha256(CUERPO).hexdigest()[:12]))
        print("  codigo=%d  %s" % (codigo, (lineas[0][:170] if lineas else "(sin lineas)")))
        return codigo
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    a = caso("A  subida byte-identica al cuerpo", CUERPO)
    b = caso("B  subida saneada (identidad sustituida)", SANEADA)
    print("\nLECTURA: A=%d B=%d  ->  %s" % (
        a, b,
        "el check solo se satisface publicando el cuerpo SIN sanear: con copia saneada es VENCIDO estructural"
        if (a == 0 and b == 1) else "no reproduce el hueco esperado; revisar"))


if __name__ == "__main__":
    main()
