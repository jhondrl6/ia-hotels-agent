"""FASE-H — arnes de mutaciones del runner y de la derivacion (AC15/AC17).

Cada mutante apaga UN guard real del simbolo que esta fase escribio, sobre el archivo vivo, y
corre la seleccion de pruebas que ese guard gobierna. Criterios del contrato:

* el rojo lo produce la asercion del guard, no un `SyntaxError` ni un `ImportError`;
* la restauracion se verifica por sha256 del archivo, no por confianza;
* ningun mutante toca la asercion del test ni el control productivo de FASE-E2E.

Lectura/escritura en BINARIO: `Path.write_text` en Windows pasa los archivos a CRLF y el sha256
de restauracion deja de casar (medido en FASE-D). Aqui se leen y se escriben bytes.

Uso:
  ./venv/Scripts/python.exe evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-H/run_mutations.py
Salida:
  evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-H/mutation_report.json
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
DIR_FASE = RAIZ / "evidence" / "REFACTOR-WHATSAPP-ENTREGA-2026-09-18" / "FASE-H"
PYTHON = str(RAIZ / "venv" / "Scripts" / "python.exe")
RUNNER = "evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-H/run_once.py"
DERIVAR = "evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-H/derivar_onboarding.py"
BATERIA_RUNNER = "tests/test_fase_h_intento_unico.py"
BATERIA_ONBOARDING = "tests/test_fase_h_onboarding_procedencia.py"

MUTANTES = [
    {
        "id": "M1",
        "archivo": RUNNER,
        "guardia": "reserva por creacion exclusiva (O_EXCL) antes del spawn",
        "ac": "AC17",
        "buscar": "bandera = os.O_CREAT | os.O_EXCL | os.O_WRONLY",
        "reemplazo": "bandera = os.O_CREAT | os.O_WRONLY | os.O_TRUNC",
        "pruebas": [
            f"{BATERIA_RUNNER}::test_el_intento_queda_consumido_aunque_el_hijo_falla",
            f"{BATERIA_RUNNER}::test_la_reserva_existente_no_se_sobrescribe_ni_se_borra",
            f"{BATERIA_RUNNER}::test_timeout_no_concede_segunda_ejecucion_y_no_fabrica_exit_code",
            f"{BATERIA_RUNNER}::test_dos_lanzadores_concurrentes_uno_solo_crea_proceso",
        ],
        # El dict que imprime la asercion cambia de clave segun que lanzador gane la carrera, asi
        # que el ancla del motivo es el valor compartido ('gano'), no una clave de suerte.
        "motivo_esperado": "sin O_EXCL la reserva exclusiva no existe",
    },
    {
        "id": "M2",
        "archivo": RUNNER,
        "guardia": "guard de fuga del control (_serializar_control)",
        "ac": "AC13",
        "buscar": "if cargar_sumidero().contains_secret_shape(texto):",
        "reemplazo": "if False and cargar_sumidero().contains_secret_shape(texto):",
        "pruebas": [
            f"{BATERIA_RUNNER}::test_un_control_con_forma_de_credencial_no_llega_a_disco",
            f"{BATERIA_RUNNER}::test_la_captura_de_stdout_redacta_antes_de_escribir",
        ],
        "motivo_esperado": 'CapturaSinRedactar',
    },
    {
        "id": "M3",
        "archivo": RUNNER,
        "guardia": "assert_redacted como llamador del contrato de F (cierra S-F8)",
        "ac": "AC13",
        "buscar": "        sink.assert_redacted(redactado, channel=canal)",
        "reemplazo": "        pass  # MUTANTE: guard de fuga desconectado",
        "pruebas": [
            f"{BATERIA_RUNNER}::test_assert_redacted_tiene_lamador_en_el_producto",
            f"{BATERIA_RUNNER}::test_el_guard_de_fuga_operante_cuando_redaccion_se_apaga",
        ],
        "motivo_esperado": 'assert_redacted',
    },
    {
        "id": "M4",
        "archivo": RUNNER,
        "guardia": "cotejo de hashes congelados contra el preflight",
        "ac": "AC17",
        "buscar": "    if divergentes:\n        raise DivergenciaDeHash(",
        "reemplazo": "    if False and divergentes:\n        raise DivergenciaDeHash(",
        "pruebas": [f"{BATERIA_RUNNER}::test_divergencia_de_hash_contra_el_preflight_detiene_el_spawn"],
        "motivo_esperado": 'spawn con arbol divergente',
    },
    {
        "id": "M5",
        "archivo": RUNNER,
        "guardia": "el argv lanzado debe ser el que autorizo el preflight",
        "ac": "AC17",
        "buscar": "    if list(preflight.get(\"argv_congelado\") or []) != list(argv):",
        "reemplazo": "    if False and list(preflight.get(\"argv_congelado\") or []) != list(argv):",
        "pruebas": [f"{BATERIA_RUNNER}::test_un_argv_que_el_preflight_no_autorizo_se_rechaza"],
        "motivo_esperado": 'spawn con argv no autorizado',
    },
    {
        "id": "M6",
        "archivo": RUNNER,
        "guardia": "attempts no se baja jamas",
        "ac": "AC17",
        "buscar": 'if clave == "attempts" and int(valor) < int(control.get("attempts", 0)):',
        "reemplazo": "if False:",
        "pruebas": [f"{BATERIA_RUNNER}::test_attempts_no_se_baja_jamas"],
        "motivo_esperado": 'TransicionInvalida',
    },
    {
        "id": "M7",
        "archivo": RUNNER,
        "guardia": "los estados terminales no se reabren (TRANSICIONES)",
        "ac": "AC17",
        "buscar": "    if estado not in TRANSICIONES.get(actual, ()):",
        "reemplazo": "    if False and estado not in TRANSICIONES.get(actual, ()):",
        "pruebas": [
            f"{BATERIA_RUNNER}::test_control_dudoso_es_terminal_y_no_se_resea",
            f"{BATERIA_RUNNER}::test_el_intento_queda_consumido_aunque_el_hijo_falla",
        ],
        "motivo_esperado": 'TransicionInvalida',
    },
    {
        "id": "M8",
        "archivo": RUNNER,
        "guardia": "rama efectiva del loader: solo YAML_DE_DIR_CLIENTES es aceptable",
        "ac": "AC14",
        "buscar": (
            "    return (\n"
            "        proveniencia.get(\"rama_efectiva\") == RAMA_ACEPTABLE\n"
            "        and (integracion.get(\"loader\") or {}).get(\"rama_efectiva\") == RAMA_ACEPTABLE\n"
            "    )"
        ),
        "reemplazo": "    return True  # MUTANTE: fallback silencioso aceptado",
        "pruebas": [
            f"{BATERIA_ONBOARDING}::test_las_ram_silenciosas_del_loader_no_son_favorables",
            f"{BATERIA_ONBOARDING}::test_el_preflight_recalculado_no_inventa_el_consentimiento",
        ],
        "motivo_esperado": 'assert True is False',
    },
    {
        "id": "M9",
        "archivo": RUNNER,
        "guardia": "el requisito del consentimiento se decide por el documento, no por la fase",
        "ac": "AC14/AC17",
        "buscar": '"cumple": bool(consentimiento["autoriza_entrega"]),',
        "reemplazo": '"cumple": True,  # MUTANTE: consentimiento autosatisfecho',
        "pruebas": [
            f"{BATERIA_ONBOARDING}::test_el_preflight_recalculado_no_inventa_el_consentimiento",
            f"{BATERIA_ONBOARDING}::test_el_preflight_publicado_declara_el_consentimiento_pendiente_y_attempts_cero",
        ],
        "motivo_esperado": 'autosatisfacerlo',
    },
    {
        "id": "M10",
        "archivo": RUNNER,
        "guardia": "redactar antes de persistir (orden del sumidero de F)",
        "ac": "AC13",
        "buscar": "    redactado = sink.redact_secrets(crudo)",
        "reemplazo": "    redactado = crudo  # MUTANTE: crudo al disco",
        "pruebas": [
            f"{BATERIA_RUNNER}::test_la_captura_de_stdout_redacta_antes_de_escribir",
            f"{BATERIA_RUNNER}::test_el_guard_de_fuga_operante_cuando_redaccion_se_apaga",
        ],
        "motivo_esperado": 'salida sin redactar',
    },
    {
        "id": "M11",
        "archivo": DERIVAR,
        "guardia": "la URL del derivado es la de la corrida (unica edicion del contenido)",
        "ac": "AC14",
        "buscar": 'derivado["hotel"]["url"] = URL_SOLICITADA  # unica edicion del contenido',
        "reemplazo": "pass  # MUTANTE: se conserva la URL historica",
        "pruebas": [
            f"{BATERIA_ONBOARDING}::test_la_procedencia_declarar_no_disponible_los_campos_no_transportados",
            f"{BATERIA_ONBOARDING}::test_el_derivado_productivo_toma_la_rama_yaml_y_su_hash_casa",
        ],
        "motivo_esperado": 'tomar la rama YAML',
    },
    {
        "id": "M12",
        "archivo": DERIVAR,
        "guardia": "sin fecha_captura no se deriva (fail-closed propio de H)",
        "ac": "AC14",
        "buscar": "    if not metadatos.get(\"fecha_captura\"):",
        "reemplazo": "    if False:",
        "pruebas": [f"{BATERIA_ONBOARDING}::test_sin_fecha_de_captura_la_derivacion_rechaza_en_lugar_de_seguir"],
        "motivo_esperado": 'ValueError',
    },
    {
        "id": "M13",
        "archivo": DERIVAR,
        "guardia": "selector unico: cero o multiples detienen",
        "ac": "AC14",
        "buscar": "    if len(coincidencias) != 1:",
        "reemplazo": "    if False:",
        "pruebas": [
            f"{BATERIA_ONBOARDING}::test_cero_coincidencias_detienen_el_preflight",
            f"{BATERIA_ONBOARDING}::test_multiples_coincidencias_detienen_el_preflight",
        ],
        "motivo_esperado": 'DID NOT RAISE',
    },
]

ROJO = re.compile(r"^FAILED (\S+?)(?: - (.*))?\s*$", re.MULTILINE)


RAZON = re.compile(r"^(.+?\.py):(\d+): (\S.*)$", re.MULTILINE)


def sha_bytes(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def correr(pruebas: list[str]) -> dict:
    proceso = subprocess.run(
        [
            PYTHON, "-m", "pytest", *pruebas,
            "-q", "--no-header", "-p", "no:cacheprovider", "-rf", "--tb=line",
        ],
        cwd=str(RAIZ),
        capture_output=True,
    )
    texto = proceso.stdout.decode("utf-8", errors="replace").replace("\r\n", "\n")
    rojos = [{"test": nodo, "causa": (causa or "").strip()} for nodo, causa in ROJO.findall(texto)]
    razones = [f"{Path(ruta).name}:{linea}: {razon}" for ruta, linea, razon in RAZON.findall(texto)]
    resumen = next(
        (linea for linea in reversed(texto.splitlines()) if re.search(r"\d+ (passed|failed)", linea)),
        "",
    )
    for entrada, razon in zip(rojos, razones):
        entrada.setdefault("razon", razon)
    return {
        "exit_code": proceso.returncode,
        "rojos": rojos,
        "razones": razones,
        "resumen": resumen,
        "crudo_ultimas_lineas": [linea for linea in texto.splitlines() if linea.strip()][-8:],
        "error_de_instrumento": bool(
            re.search(r"ImportError|ModuleNotFoundError|SyntaxError|collection error", texto)
        ),
    }


def principal() -> int:
    informe = {
        "artefacto": "mutation_report",
        "plan": "REFACTOR-WHATSAPP-ENTREGA-2026-09-18",
        "fase": "FASE-H",
        "fecha": "2026-10-06",
        "instrumento": "run_mutations.py (edicion en el arbol vivo, restauracion por sha256)",
        "regla": (
            "un rojo deliberado con guard desconectado no es un defecto: se restaura y se verifica "
            "por hash. Si el rojo viniera de import/sintaxis, el mutante no conta."
        ),
        "mutantes": [],
    }
    verde_base = correr([BATERIA_RUNNER, BATERIA_ONBOARDING])
    informe["linea_base_verde"] = verde_base

    for mutante in MUTANTES:
        ruta = RAIZ / mutante["archivo"]
        original = ruta.read_bytes()
        sha_original = hashlib.sha256(original).hexdigest()
        texto = original.decode("utf-8")
        ocurrencias = texto.count(mutante["buscar"])
        registro = {
            "id": mutante["id"],
            "archivo": mutante["archivo"],
            "guard": mutante["guardia"],
            "ac": mutante["ac"],
            "anclaje_unico": ocurrencias == 1,
        }
        if ocurrencias != 1:
            registro["estado"] = "ANCLAJE_NO_UNICO"
            registro["ocurrencias"] = ocurrencias
            informe["mutantes"].append(registro)
            continue
        ruta.write_bytes(texto.replace(mutante["buscar"], mutante["reemplazo"]).encode("utf-8"))
        aplicado = correr(mutante["pruebas"])
        ruta.write_bytes(original)
        restaurado = sha_bytes(ruta) == sha_original
        verificado_verde = correr(mutante["pruebas"]) if restaurado else {}
        causas = [r.get("razon") or r["causa"] for r in aplicado["rojos"]] or aplicado["razones"]
        registro.update(
            {
                "estado": "ROJO_POR_EL_GUARD" if aplicado["exit_code"] != 0 else "VERDE_CON_MUTANTE",
                "exit_con_mutante": aplicado["exit_code"],
                "rojos": [r["test"] for r in aplicado["rojos"]],
                "causas_impresas": causas,
                "resumen_con_mutante": aplicado["resumen"],
                "rojo_por_instrumento_roto": aplicado["error_de_instrumento"],
                "sha256_antes": sha_original,
                "restaurado_por_sha256": restaurado,
                "exit_tras_restaurar": verificado_verde.get("exit_code"),
                "verdes_tras_restaurar": not verificado_verde.get("rojos"),
                "motivo_esperado": mutante["motivo_esperado"],
                "motivo_presente_en_el_rojo": any(
                    mutante["motivo_esperado"] in causa for causa in causas
                )
                or mutante["motivo_esperado"] in aplicado["resumen"],
            }
        )
        informe["mutantes"].append(registro)
        print(
            f"{mutante['id']}: exit={aplicado['exit_code']} restaurado={restaurado} "
            f"rojos={len(aplicado['rojos'])} motivo={registro['motivo_presente_en_el_rojo']} "
            f"| {', '.join(Path(t).name for t in registro['rojos'])} :: {' / '.join(causas)[:110]}"
        )

    caidos = sum(1 for m in informe["mutantes"] if m["estado"] == "ROJO_POR_EL_GUARD")
    restaurados = sum(1 for m in informe["mutantes"] if m.get("restaurado_por_sha256"))
    informe["resumen"] = {
        "mutantes": len(informe["mutantes"]),
        "rojos_por_el_guard": caidos,
        "restaurados_por_sha256": restaurados,
        "rojos_por_import_o_sintaxis": sum(1 for m in informe["mutantes"] if m.get("rojo_por_instrumento_roto")),
        "anclajes_no_unicos": sum(1 for m in informe["mutantes"] if m["estado"] == "ANCLAJE_NO_UNICO"),
    }
    (DIR_FASE / "mutation_report.json").write_text(
        json.dumps(informe, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(informe["resumen"], indent=2, ensure_ascii=False))
    return 0 if caidos == len(MUTANTES) and restaurados == len(MUTANTES) else 1


if __name__ == "__main__":
    sys.exit(principal())
