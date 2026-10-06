"""FASE-E — mutaciones de los guards reales (AC10/AC11/AC12).

Cada mutante aplica una edicion de ANCLA UNICA sobre el simbolo de produccion, corre el
test que debe caer y RESTAURA el blob exacto que leyo al empezar (nunca `git show HEAD`:
el producto de esta fase esta sin commitear, y restaurar desde HEAD lo revertiria).
El rojo tiene que provenir del guard, no de syntax o import: se coteja la causa impresa.

Uso: ./venv/Scripts/python.exe evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-E/run_mutations.py
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
TESTS = "tests/quality_gates/tribunal/test_fase_e_snapshot_resolvedor.py"
PY = "./venv/Scripts/python.exe"

MUTANTES = [
    {
        "id": "M1",
        "ac": "AC11",
        "archivo": "main.py",
        "que_se_rompe": "main.py deja de congelar los insumos antes del borrado",
        "old": "        capture_review_inputs(\n            run_root=output_dir,",
        "new": "        _capture_review_inputs_suprimido(\n            run_root=output_dir,",
        "nth": 1,
        "test": "test_main_congela_los_insumos_antes_de_borrar_los_documentos",
        "causa_esperada": "main.py ya no congela los insumos",
    },
    {
        "id": "M2",
        "ac": "AC11",
        "archivo": "main.py",
        "que_se_rompe": "Bot 1 vuelve a recibir rutas propias en vez del resolvedor del run",
        "old": "DiagnosisReviewer(v4_audit_dir, review_inputs=_ri)",
        "new": "DiagnosisReviewer(v4_audit_dir)",
        "nth": 1,
        "test": "test_main_pasa_el_resolvedor_al_juez_y_a_los_cuatro_bots",
        "causa_esperada": "perdio el resolvedor",
    },
    {
        "id": "M3",
        "ac": "AC11",
        "archivo": "modules/quality_gates/tribunal/diagnosis_reviewer.py",
        "que_se_rompe": "el insumo no leido vuelve a ser lista vacia (el verde silencioso de F-P4.2)",
        "old": "            findings.extend(self._check_diagnostic_input())",
        "new": "            pass",
        "nth": 1,
        "test": "test_bot1_insumo_no_leido_no_es_lista_vacia",
        "causa_esperada": "assert 0 == 1",
    },
    {
        "id": "M4",
        "ac": "AC11",
        "archivo": "modules/quality_gates/tribunal/review_inputs.py",
        "que_se_rompe": "la copia interna perdida se disfraza de error de lectura en vez de NO_LEIDO",
        "old": "                base.read_status = READ_NOT_READ",
        "new": "                base.read_status = READ_ERROR",
        "nth": 1,
        "test": "test_borrado_sin_copia_interna_es_NO_LEIDO_y_no_OK_vacio",
        "causa_esperada": "NO_LEIDO",
    },
    {
        "id": "M5",
        "ac": "AC10",
        "archivo": "modules/geo_enrichment/asset_responsibility_contract.py",
        "que_se_rompe": "la seccion de assets fuera de catalogo vuelve a publicar el basename",
        "old": "            zip_path = asset_zip_paths.get(asset, asset)",
        "new": "            zip_path = asset",
        "nth": 1,
        "test": "test_el_asset_nuevo_de_b_viaja_con_su_ruta_real_y_su_orden",
        "causa_esperada": "el orden publica el basename",
    },
    {
        "id": "M6",
        "ac": "AC11/AC12",
        "archivo": "modules/delivery/delivery_packager.py",
        "que_se_rompe": "el snapshot interno vuelve a viajar al ZIP del cliente",
        "old": "                    if any(part in self._INTERNAL_DIR_NAMES for part in rel_path.parts):",
        "new": "                    if False and any(part in self._INTERNAL_DIR_NAMES for part in rel_path.parts):",
        "nth": 1,
        "test": "test_el_snapshot_y_su_manifiesto_no_saluden_al_cliente",
        "causa_esperada": "_review_inputs",
    },
    {
        "id": "M7",
        "ac": "AC11/AC12",
        "archivo": "modules/delivery/delivery_packager.py",
        "que_se_rompe": "el manifiesto de insumos se filtra por nombre al paquete",
        "old": '_INTERNAL_DOC_PREFIXES = ("acta_revision", "review_input_manifest")',
        "new": '_INTERNAL_DOC_PREFIXES = ("acta_revision",)',
        "nth": 1,
        "test": "test_el_snapshot_y_su_manifiesto_no_saluden_al_cliente",
        "causa_esperada": "review_input_manifest",
    },
    {
        "id": "M8",
        "ac": "AC11",
        "archivo": "modules/quality_gates/tribunal/artifact_paths.py",
        "que_se_rompe": "resolve_latest ignora la ruta explicita del run y vuelve al mtime entre hoteles",
        "old": "    if explicit is not None:",
        "new": "    if False and explicit is not None:",
        "nth": 1,
        "test": "test_ruta_explitica_gana_a_un_archivo_mas_reciente_de_otro_hotel",
        "causa_esperada": "is None",
    },
]


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def aplicar(texto: str, old: str, new: str, nth: int) -> str:
    ocurrencias = texto.count(old)
    if ocurrencias < nth:
        raise SystemExit(f"ANCLA INSUFICIENTE: {ocurrencias} ocurrencias, se exigian {nth}")
    idx, busqueda, vistos = -1, 0, 0
    while vistos < nth:
        idx = texto.find(old, busqueda)
        if idx == -1:
            raise SystemExit(f"ocurrencia {nth} no encontrada")
        vistos += 1
        busqueda = idx + len(old)
    return texto[:idx] + new + texto[idx + len(old):]


def correr(test: str) -> tuple[int, str]:
    proc = subprocess.run(
        [PY, "-m", "pytest", f"{TESTS}::{test}", "-q", "--tb=short", "-p", "no:randomly"],
        cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    salida = proc.stdout + proc.stderr
    lineas = [
        l for l in salida.splitlines()
        if l.startswith("E   ") or "FAILED" in l or "passed" in l or "failed" in l or "Error" in l
    ]
    return proc.returncode, "\n".join(lineas[-8:])


def main() -> int:
    resultados, crudos = [], []
    exit_code, detalle, cae, causa_ok = None, "", False, False

    for m in MUTANTES:
        path = ROOT / m["archivo"]
        original = path.read_bytes()
        antes = sha(original)
        try:
            path.write_text(aplicar(original.decode("utf-8"), m["old"], m["new"], m["nth"]),
                            encoding="utf-8", newline="")
            assert sha(path.read_bytes()) != antes, f"{m['id']}: la mutacion no toco el archivo"
            exit_code, detalle = correr(m["test"])
            cae = exit_code != 0
            causa_ok = m["causa_esperada"] in detalle
        finally:
            path.write_bytes(original)
            resta = sha(path.read_bytes())

        if "SyntaxError" in detalle or "ImportError" in detalle or "ModuleNotFound" in detalle:
            causa_ok = False  # rojo de instrumento, no del guard
        crudos.append(f"=== {m['id']} · {m['archivo']} · {m['test']}\nEXIT={exit_code}\n{detalle}\n")
        resultados.append({
            "id": m["id"], "ac": m["ac"], "archivo": m["archivo"],
            "guard_mutado": m["que_se_rompe"], "test": m["test"],
            "occurrencia_mutada": m["nth"], "exit_code": exit_code,
            "cayo_por_el_guard": cae and causa_ok,
            "causa_esperada": m["causa_esperada"], "crudo": detalle,
            "sha_antes": antes, "sha_restaurado": resta, "arbol_intacto": resta == antes,
        })

    (OUT / "mutation_report.json").write_text(json.dumps({
        "instrumento": "evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-E/run_mutations.py",
        "seleccion_de_prueba": TESTS,
        "mutantes": resultados,
        "TOTAL": len(resultados),
        "cayen_por_su_guard": sum(1 for r in resultados if r["cayo_por_el_guard"]),
        "arbol_intacto": all(r["arbol_intacto"] for r in resultados),
    }, indent=2, ensure_ascii=False), encoding="utf-8", newline="\n")
    (OUT / "mutaciones_crudo.txt").write_text("\n".join(crudos), encoding="utf-8", newline="\n")

    for r in resultados:
        print(f"{r['id']} {r['ac']:11s} EXIT={r['exit_code']} guard={r['cayo_por_el_guard']} restaurado={r['arbol_intacto']}")
    caidos = sum(1 for r in resultados if r["cayo_por_el_guard"])
    intactos = sum(1 for r in resultados if r["arbol_intacto"])
    print(f"TOTAL {caidos}/{len(resultados)} caen por su guard; restauracion {intactos}/{len(resultados)}")
    return 0 if (caidos == len(resultados) and intactos == len(resultados)) else 1


if __name__ == "__main__":
    sys.exit(main())
