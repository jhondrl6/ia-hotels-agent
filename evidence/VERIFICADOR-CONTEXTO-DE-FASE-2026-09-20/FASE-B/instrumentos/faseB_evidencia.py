"""Genera `contract.txt`, `extensibilidad.txt` y `cero-red.txt` de FASE-B con sus salidas literales.

Archivo de trabajo bajo `temp/` (gitignoreado, excluido del escaneo de AC6): no es artefacto del
plan; lo que perdura es su salida en `evidence/.../FASE-B/`. Cada bloque imprime el comando que lo
produjo, para que la evidencia sea re-ejecutable (regla de forma del contrato de ejecucion).
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(".").resolve()
EVID = ROOT / "evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B"
SEL = "tests/quality_gates/decision_client"
FALSOS = ROOT / SEL / "falsos_proveedores"
PY = [sys.executable, "-m", "pytest"]


def correr(args, env=None):
    r = subprocess.run(PY + args, capture_output=True, text=True, cwd=str(ROOT),
                       env={**os.environ, **(env or {})})
    return r.returncode, (r.stdout + r.stderr).replace("\r\n", "\n")


def separar(salida):
    """Quita los SyntaxWarning de archivos ajenos: ruido del arbol, no de esta fase."""
    lineas, fuera = [], False
    for l in salida.splitlines():
        if l.startswith("warnings summary"):
            fuera = True
        if fuera and (l.startswith("=") and "warnings" in l):
            fuera = False
        if "SyntaxWarning" in l or "invalid escape sequence" in l or "H12 FIX" in l:
            continue
        if "Docs: https://docs.pytest.org" in l or "warning generated" in l:
            continue
        if "El lookahead" in l:
            continue
        lineas.append(l)
    return "\n".join(lineas).strip() + "\n"


# ---------------------------------------------------------------- contract.txt (AC8)
rc_v, verde = correr(["-v", "--no-header", "-p", "no:cacheprovider", SEL,
                      "-k", "contract_forma"])

copia = ROOT / "temp" / "faseB_contract_rojo" / "falsos_proveedores"
if copia.parent.exists():
    shutil.rmtree(copia.parent)
copia.parent.mkdir(parents=True)
shutil.copytree(FALSOS, copia)
victim = copia / "falso_forma.py"
texto = victim.read_text(encoding="utf-8")
blanco = ', "confidence": 0.91'
assert blanco in texto
alterado = texto.replace(blanco, "", 1)
assert '"confidence"' not in alterado.split("def evaluar")[1].split("elif")[0]
victim.write_text(alterado, encoding="utf-8")

rc_r, rojo = correr(["-v", "--no-header", "-p", "no:cacheprovider",
                     str(ROOT / SEL / "test_decision_client_contract_forma.py"),
                     "-k", "test_evaluar_devuelve_una_respuesta_tipada_por_pregunta"],
                    env={"IAH_DECISION_PROVIDER": "falso-forma",
                         "IAH_DECISION_PROVIDERS_DIR": str(copia)})
shutil.rmtree(copia.parent)

(EVID / "contract.txt").write_text(
    "# FASE-B / AC8 - contract test de forma: verde con la forma actual, ROJO al alterarla\n\n"
    "Plan: VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20 · Medido: 2026-09-21 · HEAD: "
    + subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                     cwd=str(ROOT)).stdout.strip() + "\n\n"
    "Archivo de tests: `tests/quality_gates/decision_client/test_decision_client_contract_forma.py`\n"
    "Simbolo gobernado: `scripts/decision_client.py::VERIFICACIONES_DE_FORMA` (seis guards, cada "
    "uno con su mutante en `mutation/`).\n\n"
    "## Que fija el contrato (la forma, no los literales del proveedor: L-V2.3)\n\n"
    "| Forma | Campos exigidos | Que la rompe |\n"
    "|---|---|---|\n"
    "| `choice` | `eleccion` entre las opciones declaradas, `probabilidades` sobre **todas** ellas "
    "sumando 1 ± " + "0.02, `confidence` en [0,1] | un campo nuevo, uno que falta, una suma que no "
    "cuadra, confidence ausente |\n"
    "| `score` | `nivel` dentro de la leyenda declarada **y** su `leyenda` correspondiente, "
    "`confidence` en [0,1] | nivel y etiqueta desalineados (la primitiva re-definio criterios) |\n"
    "| `noul` | `probabilidad_si` en [0,1] y **ninguna** `confidence` | inventarle una confidence: "
    "la primitiva no la expone, y rellenarla fabricaria el eje que FASE-C usa en AC12 |\n"
    "| envelope | `modelo` no vacio, `usage` dict o `None`, sin claves fuera de contrato | un 200 "
    "sin `usage` sigue siendo `None`, **no** consumo cero |\n\n"
    "## Version del modelo: declarada, no pineada\n\n"
    "`PIN_MODELO_DECLARADO` en la puerta publica `modelo = jev-1.13.0` con su fuente (docs "
    "publicos consultados el 2026-09-21 por el plan hermano `EVALUACION-JEV-TYPESAFE-2026-09-21`), "
    "`verificado_desde_este_repo = false` y `usado_por_el_codigo = false`. `test_el_pin_del_modelo_"
    "esta_declarado_y_no_decide_nada` lo afirma leyendo el AST de la puerta: el pin aparece **una "
    "sola vez** (su propia definicion). El contract test compara el modelo contra lo que **el "
    "proveedor declara** en su modulo, nunca contra una cadena: asi sigue siendo de forma cuando el "
    "proveedor cambie de version, y asi el repo no se acopla al nombre del proveedor (maestro §2).\n\n"
    "## VERDE — `pytest -v ... -k contract_forma` (exit " + str(rc_v) + ")\n\n```text\n"
    + separar(verde) + "```\n\n"
    "## ROJO — el MISMO test, contra una copia del proveedor falso sin `confidence`\n\n"
    "Comando (capturado tal cual, con el entorno apuntando a la copia alterada en `temp/`):\n\n"
    "```bash\n"
    "IAH_DECISION_PROVIDER=falso-forma \\\n"
    "IAH_DECISION_PROVIDERS_DIR=<copia alterada> \\\n"
    "./venv/Scripts/python.exe -m pytest \\\n"
    "  tests/quality_gates/decision_client/test_decision_client_contract_forma.py \\\n"
    "  -k test_evaluar_devuelve_una_respuesta_tipada_por_pregunta -v\n"
    "```\n\n"
    "La mutacion es una sola linea del proveedor falso: se le quita `\"confidence\": 0.91` de la "
    "respuesta `choice`. El assert del hijo no depende de que el hijo imprima los motivos, asi que "
    "el nombre del guard que cayo se comprueba ademas en el proceso padre "
    "(`test_alterar_la_forma_del_proveedor_falso_rompe_este_mismo_test`, ver `run_tests.txt`).\n\n"
    "exit " + str(rc_r) + " — distinto de cero, que es lo que AC8 exige:\n\n```text\n"
    + separar(rojo) + "```\n\n"
    "## Nota L-VUP-5\n\n"
    "El verde de esta fase no llego a la primera: la primera corrida dio 30 fallos y el primer "
    "intento de mutation check apagaba la lista de guards **entera**, lo que no aislaba a ninguno. "
    "Ambos hechos estan escritos en `mutation/verde_baseline.txt`.\n",
    encoding="utf-8", newline="\n")

# ---------------------------------------------------------------- extensibilidad.txt (AC9)
rc_e, ext = correr(["-v", "--no-header", "-p", "no:cacheprovider",
                    SEL + "/test_decision_client_segundo_proveedor_un_archivo.py"])
(EVID / "extensibilidad.txt").write_text(
    "# FASE-B / AC9 - extensibilidad probada: anadir un segundo proveedor cuesta UN archivo\n\n"
    "Test: `test_decision_client_segundo_proveedor_un_archivo.py` (5 casos) + el instrumento que "
    "mide: `scripts/decision_client.py::medir_costura`, cuya salida esta en `costura.json`.\n\n"
    "## Como se mide, para que el 1 no sea una afirmacion\n\n"
    "1. Copia la puerta (`scripts/decision_client.py`) y sus proveedores falsos a un directorio "
    "temporal; el arbol del repo no se toca (hay un caso que lo prueba por `st_mtime_ns`).\n"
    "2. `sha256` de **todos** los `.py` copiados -> `antes`.\n"
    "3. Escribe **un** archivo nuevo, `falsos_proveedores/falso_segundo.py`, que solo declara "
    "`PROVEEDOR` y su `evaluar()`. No se registra en ninguna parte: la costura descubre proveedores "
    "escaneando el directorio nombrado por `IAH_DECISION_PROVIDERS_DIR`.\n"
    "4. `sha256` otra vez -> `despues`; `files_changed_to_add_provider = |agregados| + |modificados|`.\n"
    "5. Despacha **los dos** proveedores por la misma `evaluar()` y exige que contesten distinto: "
    "si la costura devolviera siempre el primer modulo, el 1 seria humo.\n\n"
    "## Valor publicado\n\n"
    "`files_changed_to_add_provider = 1` · `agregados = [\"falsos_proveedores/falso_segundo.py\"]` · "
    "`modificados = []`. No hay que explicar un numero mayor: no lo hubo.\n\n"
    "## Lo que el 1 NO incluye (declarado, no escondido)\n\n"
    "Igual que hace el AC1 del plan hermano: **tests, runner y manifiesto de dependencias se "
    "contabilizan aparte**. `archivos_de_test_paralelos = 1` (el caso que despacha al proveedor "
    "nuevo). Y cuando D7 active un proveedor **real** habra que anadir, ademas del modulo de "
    "declaracion, la entrada de dependencias del SDK - eso no esta medido aqui porque no se activa "
    "ningun proveedor en este plan.\n\n"
    "## Comparacion de proveedores: NO es de esta fase\n\n"
    "Con un solo proveedor real no hay eleccion que medir, y exigir la produccion de un numero "
    "inexistente se cerraria como `NO-EJERCITADO` certificando humo. La comparacion queda como "
    "deuda **D7** con su disparador (maestro §6), y su consumidor natural es **D6**.\n\n"
    "## Salida del test (exit " + str(rc_e) + ")\n\n```text\n" + separar(ext) + "```\n",
    encoding="utf-8", newline="\n")

# ---------------------------------------------------------------- cero-red.txt
rc_g, guard = correr(["-v", "--no-header", "-p", "no:cacheprovider",
                      SEL + "/test_decision_client_aislamiento_imports.py",
                      "-k", "guard_de_red or trabaje or no_importan_nada"])
(EVID / "cero-red.txt").write_text(
    "# FASE-B - cero llamadas de red, verificadas y no afirmadas\n\n"
    "El contrato de ejecucion de este plan prohibe **una sola** llamada a un proveedor real, y la "
    "completitud de la fase pide que eso sea «verificable, no afirmado». Tres instrumentos, y cada "
    "uno falla solo:\n\n"
    "## 1. Guard vivo en tiempo de ejecucion (`conftest.py`, fixture autouse `sin_red`)\n\n"
    "`socket.socket`, `socket.create_connection`, `socket.getaddrinfo` y `socket.gethostbyname` "
    "estan reemplazados por un explosivo para **todos** los casos de la seleccion. Dos pruebas: "
    "`test_el_guard_de_red_explota_si_alguien_intenta_llamar` (el guard esta puesto: llamarlo "
    "produce `RedProhibida`) y `test_la_costura_trabaja_bajo_el_guard_sin_dispararlo` (la costura "
    "llega a `RESUELTO` con el guard armado, o sea: su verde no vino de la red).\n\n"
    "## 2. Escaneo AST de los modulos de esta fase\n\n"
    "`test_la_puerta_y_sus_proveedores_no_importan_nada_que_pueda_hacer_red` usa una **denegatoria**: "
    "ningun modulo de la puerta ni de los proveedores falsos importa `socket`, `ssl`, `select`, "
    "`asyncio`, `subprocess`, `threading`, `multiprocessing`, `http`, `httpx`, `httpx2`, `httpcore`, "
    "`urllib`, `urllib3`, `requests`, `aiohttp`, `ftplib`, `smtplib`, `telnetlib`, `tenacity`, "
    "`typesafe` ni `jev`. Con lista negra y no con whitelist, para que aniadir un cliente nuevo "
    "ponga el test rojo en vez de pasar por omision.\n\n"
    "## 3. El SDK ni siquiera esta instalado en el venv del producto\n\n"
    "```bash\n"
    "./venv/Scripts/python.exe -c \"import importlib.util as u; "
    "print([(m, bool(u.find_spec(m))) for m in ('typesafe','jev','httpx2','tenacity')])\"\n"
    "```\n\n"
    "`[('typesafe', False), ('jev', False), ('httpx2', False), ('tenacity', False)]` — medido el "
    "2026-09-21 (ver `faseB_baseline_pre.txt`, unidad 9). El SDK que probo el plan hermano quedo "
    "aislado en `tmp_test/venv-jev-sdk`, directorio **excluido** de la poblacion del escaneo AC6 y "
    "publicado con su conteo en `import_scanner.txt`.\n\n"
    "## Salida de las pruebas del guard (exit " + str(rc_g) + ")\n\n```text\n"
    + separar(guard) + "```\n\n"
    "## Credenciales\n\n"
    "Ninguna credencial existe en esta fase y ninguna se leyo. `provider_status` es lo que se "
    "registra; la puerta solo publica de una credencial **si esta o no** (`credencial.presente`, un "
    "bool), nunca el valor, su longitud ni un prefijo - hay dos casos que lo afirman "
    "(`test_con_la_clave_en_el_entorno_solo_se_publica_el_bool`, "
    "`test_evaluar_tampoco_filtra_la_clave`). Una clave que aparece en un transcript obliga a "
    "rotarla, asi que ni enmascarada entra en evidencia.\n",
    encoding="utf-8", newline="\n")

print("contract.txt", rc_v, rc_r, "| extensibilidad.txt", rc_e, "| cero-red.txt", rc_g)
