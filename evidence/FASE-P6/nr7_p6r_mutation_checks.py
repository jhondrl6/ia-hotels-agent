"""NR7 P6-R — pares verde/rojo por REVERSIÓN DEL FIX (no de expectativas).

Método declarado por el plan (AC-G5 / L-T4A.5): "cada camino causal se cierra
revirtiendo el fix, no simulando el veredicto". Este script:
  1. corre el test objetivo en VERDE con el fix intacto;
  2. aplica la reversión exacta del fix al archivo de producción (una sola
     coincidencia obligatoria, si no aborta);
  3. corre el mismo test y exige ROJO;
  4. restaura el archivo desde el backup de memoria y verifica el hash.

Precedente de formato: nr7_mutation_checks.py de FASE-P3-A (restaura el árbol y
comprueba el rojo). AC-G4 no tiene par por reversión propia: su "fix" no es un
diff de producción sino la matriz reproducible de >=3 perfiles; queda anotado.

Uso:  python evidence/FASE-P6/nr7_p6r_mutation_checks.py
Salida: tabla por consola (se transcribe a nr7_p6r_mutation_checks.md).
"""
import hashlib
import os
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def _write_verified(path: Path, data: bytes, expect_sha: str, retries: int = 5) -> bool:
    """Escribe en binario con flush+fsync y re-verifica el hash releyendo.

    En Windows una lectura inmediata puede servir la versión vieja del caché de
    archivos; este reintento cierra esa carrera (costó un falso negativo en la
    primera corrida de este script).
    """
    for _ in range(retries):
        with open(path, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        time.sleep(0.05)
        if hashlib.sha256(path.read_bytes()).hexdigest() == expect_sha:
            return True
    return False

PAIRS = [
    {
        "id": "NR7-P6R-G1",
        "fix": "derivacion dest-real en DeliveryPackager.write (R6)",
        "file": "modules/delivery/delivery_packager.py",
        "old": (
            "        _asset_names = set(core_assets or []) | set(geo_assets or [])\n"
            "        asset_zip_paths: Dict[str, str] = {}\n"
            "        for _f in files_to_package:\n"
            "            _name = Path(_f[\"dest\"]).name\n"
            "            if _name in _asset_names:\n"
            "                asset_zip_paths.setdefault(_name, _f[\"dest\"])\n"
        ),
        "new": "        asset_zip_paths: Dict[str, str] = {}\n",
        "test": "tests/test_p6r_full_flow_matrix.py::test_acg1_orden_publicado_usa_ruta_real_del_zip",
    },
    {
        "id": "NR7-P6R-G2a",
        "fix": "guard clientes_dir.exists() eliminado (AC-G2/F-P4.7)",
        "file": "main.py",
        "old": (
            "    normalized_url = _normalize_url(hotel_url)\n"
            "\n"
            "    # Buscar primero en YAMLs de clientes (si el directorio existe)\n"
        ),
        "new": (
            "    if not clientes_dir.exists():\n"
            "        return None\n"
            "    normalized_url = _normalize_url(hotel_url)\n"
            "\n"
            "    # Buscar primero en YAMLs de clientes (si el directorio existe)\n"
        ),
        "test": "tests/test_ac_g2_onboarding_fallback.py::test_load_onboarding_fallback_to_observations_when_clientes_dir_missing",
    },
    {
        "id": "NR7-P6R-G2b",
        "fix": "converter sin defaults inventados (R4 / AC-G2 clausula 2)",
        "file": "main.py",
        "old": "        valor = obs.get(obs_key)\n        if valor is not None:\n",
        "new": "        valor = obs.get(obs_key)\n        valor = valor if valor is not None else 10\n        if True:\n",
        "test": "tests/test_onboarding_injection.py::TestObservationToOnboardingFormat::test_missing_fields_propagate_nothing",
    },
    {
        "id": "NR7-P6R-G3",
        "fix": "_compute_package_evidence computa sha256/member_count reales (AC-G3)",
        "file": "main.py",
        "old": (
            "        return {\n"
            "            \"sha256\": sha256_hex,\n"
            "            \"member_count\": member_count,\n"
            "        }\n"
        ),
        "new": "        return {\"sha256\": None, \"member_count\": 0}\n",
        "test": "tests/test_p6r_full_flow_matrix.py::test_perfil2_donalfonso_anonimizado_gates_ok_revisor_objeta_bloquea",
    },
    {
        "id": "NR7-P6R-G5",
        "fix": "llave compuesta blocks_publish = bool(blocks) and enabled (contrato Q7/L-P6.1)",
        "file": "modules/quality_gates/tribunal/outcome.py",
        "old": "blocks_publish=bool(blocks) and enabled,",
        "new": "blocks_publish=bool(blocks),",
        "test": "tests/test_p6r_full_flow_matrix.py::test_perfil5_kill_switch_llaves_separadas",
    },
]


def _run(test_id: str) -> tuple[int, str]:
    r = subprocess.run(
        [sys.executable, "-B", "-m", "pytest", test_id, "-q", "--no-header", "-p", "no:cacheprovider"],
        cwd=REPO, capture_output=True, text=True,
    )
    lines = [l for l in r.stdout.splitlines() if "passed" in l or "failed" in l or "error" in l.lower()]
    return r.returncode, (lines[-1] if lines else r.stdout[-200:])


def main() -> int:
    results = []
    for pair in PAIRS:
        path = REPO / pair["file"]
        original = path.read_bytes()
        sha_before = hashlib.sha256(original).hexdigest()
        row = {"id": pair["id"], "fix": pair["fix"], "file": pair["file"],
               "test": pair["test"], "sha": sha_before[:12]}

        rc_green, out_green = _run(pair["test"])
        row["green"] = (rc_green == 0, out_green)

        text = original.decode("utf-8")
        crlf = "\r\n" in text
        old = pair["old"].replace("\n", "\r\n") if crlf else pair["old"]
        new = pair["new"].replace("\n", "\r\n") if crlf else pair["new"]
        n = text.count(old)
        if n != 1:
            row["mutation"] = f"ABORT: patron encontrado {n} veces (exigido 1)"
            row["red"] = (None, "no aplicado")
            results.append(row)
            continue

        try:
            mutated = text.replace(old, new, 1).encode("utf-8")
            if not _write_verified(path, mutated, hashlib.sha256(mutated).hexdigest()):
                raise RuntimeError(f"MUTACION no aterrizo en {pair['file']}")
            rc_red, out_red = _run(pair["test"])
            row["red"] = (rc_red != 0, out_red)
        finally:
            ok = _write_verified(path, original, sha_before)
            row["restored"] = ok
            if not ok:
                raise RuntimeError(f"RESTAURACION FALLIDA en {pair['file']}")

        results.append(row)

    print("\n== NR7 P6-R: pares por reversión del fix ==")
    all_ok = True
    for r in results:
        g = r["green"][0]
        red_ok = r.get("red", (None,))[0] is True
        restored = r.get("restored", "n/a (aborted)")
        pair_ok = g and red_ok and restored is True
        all_ok = all_ok and pair_ok
        print(f"[{'PASS' if pair_ok else 'FAIL'}] {r['id']}  verde={r['green']}  "
              f"rojo={r.get('red')}  restaurado={restored}  sha={r['sha']}  ({r['test']})")
    print(f"TOTAL: {'todos los pares verde/rojo con restauracion verificada' if all_ok else 'HAY FALLOS — revisar'}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
