"""Arnhes de mutaciones FASE-F (AC13) — versionado con la evidencia de la fase.

Cada mutante desactiva UN guard real del arbol vivo, corre UN nodo de test y exige
rojo por fuga detectada. Se restaura por bytes y se verifica sha256 contra el
estado previo. Salida: crudo para evidence/FASE-F/mutantes_crudo.txt.

Leccion de D bajo Windows: leer y escribir en BINARIO. Con write_text los .py del
arbol pasaban a CRLF y el sha de restauracion dejaba de casar.
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PY = str(ROOT / "venv" / "Scripts" / "python.exe")

MUTANTES = [
    {
        "id": "M1",
        "archivo": "modules/auditors/llm_mention_checker.py",
        "busca": "        return redact_secrets(str(error))",
        "reemplaza": "        return str(error)",
        "guard": "LLMMentionChecker._sanitize_error",
        "nodo": "tests/auditors/test_p5_ac_s1_secret_sanitization.py::TestSanitizeError::test_redacts_key_param",
        "causa": "el mensaje crudo del proveedor sale a consola",
    },
    {
        "id": "M2",
        "archivo": "modules/auditors/llm_mention_checker.py",
        "busca": "        return redact_secrets(text)",
        "reemplaza": "        return text",
        "guard": "LLMMentionChecker._sanitize_text",
        "nodo": "tests/utils/test_fase_f_sumidero_redaccion.py::TestCalificacionSanitizadoresExistentes::test_sanitize_text_redacta_una_forma_ajena_sin_keys_cargadas",
        "causa": "una credencial de otro proveedor sobrevive al log",
    },
    {
        "id": "M3",
        "archivo": "modules/utils/http_client.py",
        "busca": "        safe_error = redact_secrets(error)",
        "reemplaza": "        safe_error = error",
        "guard": "HttpClient._log_ssl_bypass",
        "nodo": "tests/utils/test_fase_f_sumidero_redaccion.py::TestConsolaSinMarcadores::test_log_ssl_bypass_imprime_redactado",
        "causa": "la consola imprime el texto sin redactar",
    },
    {
        "id": "M4",
        "archivo": "modules/utils/ssl_logger.py",
        "busca": "        text = redact_secrets(text)",
        "reemplaza": "        text = text",
        "guard": "SSLLogger._sanitize_for_log",
        "nodo": "tests/utils/test_fase_f_sumidero_redaccion.py::TestEscrituraBajoLogs::test_ssl_logger_escribe_el_archivo_sin_el_marcador",
        "causa": "el marcador queda persistido en logs/ssl_fallback.log",
    },
    {
        "id": "M5",
        "archivo": "main.py",
        "busca": "    payload = redact_payload(report.to_dict())",
        "reemplaza": "    payload = report.to_dict()",
        "guard": "_persist_coherence_pre_gate (artefacto de D bajo output/)",
        "nodo": "tests/utils/test_fase_f_sumidero_redaccion.py::TestEscrituraBajoOutput::test_pre_gate_persiste_el_mensaje_redactado",
        "causa": "el artefacto escribe el mensaje crudo bajo output/",
    },
    {
        "id": "M6",
        "archivo": "scripts/run_all_validations.py",
        "busca": "        for path in self._untracked_output_files():",
        "reemplaza": "        for path in []:",
        "guard": "ValidationRunner._check_no_secrets sobre output/ y logs/",
        "nodo": "tests/utils/test_fase_f_sumidero_redaccion.py::TestVerificadorCubreSalidas::test_un_marcador_en_la_salida_sin_versionar_es_blocking[logs]",
        "causa": "la ruta gitignored vuelve a quedar sin lector",
    },
    {
        "id": "M7",
        "archivo": "modules/utils/redaction.py",
        "busca": "    text = BEARER_RE.sub(lambda m: f\"{m.group(1)}{MASK}\", text)",
        "reemplaza": "    text = text",
        "guard": "orden Bearer-cabecera en redact_secrets",
        "nodo": "tests/utils/test_fase_f_sumidero_redaccion.py::TestSumideroUnico::test_bearer_separado_de_la_forma_sk_tambien_se_redacta",
        "causa": "el token sobrevive suelto tras redactar la cabecera",
    },
    {
        "id": "M8",
        "archivo": "modules/data_validation/external_apis/pagespeed_client.py",
        "busca": "            raise Exception(f\"Request failed: {redact_secrets(str(e))}\")",
        "reemplaza": "            raise Exception(f\"Request failed: {str(e)}\")",
        "guard": "PageSpeedClient._make_request",
        "nodo": "tests/utils/test_fase_f_sumidero_redaccion.py::TestWritersDeProveedor::test_pagespeed_request_exception_sale_redactado",
        "causa": "la excepcion lleva la URL con la key de los params",
    },
    {
        "id": "M9",
        "archivo": "scripts/run_all_validations.py",
        "busca": "            (r'sk-(?:or|ant)-[A-Za-z0-9\\-]{16,}', \"OpenRouter/Anthropic key (sk-or-/sk-ant-)\"),",
        "reemplaza": "            (r'sk-UNCA-MATCH-[A-Za-z0-9]{20,}', \"mutante sin forma real\"),",
        "guard": "patron nuevo de _secret_patterns",
        "nodo": "tests/utils/test_fase_f_sumidero_redaccion.py::TestVerificadorCubreSalidas::test_patron_nuevo_caza_las_formas_que_el_viejo_perdia[caza-sk-or]",
        "causa": "sk-or-v1 vuelve a quedar fuera del verificador",
    },
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resumeen(fallo: str) -> str:
    lineas = [l for l in fallo.splitlines() if l.startswith("FAILED ")]
    return ";".join(lineas) or "(sin linea FAILED)"


resultados = []
for mut in MUTANTES:
    ruta = ROOT / mut["archivo"]
    antes = sha(ruta)
    original = ruta.read_bytes()
    texto = original.decode("utf-8")
    si = texto.count(mut["busca"])
    if si != 1:
        resultados.append({**mut, "estado": "NO-APLICA", "anclas": si})
        continue
    ruta.write_bytes(texto.replace(mut["busca"], mut["reemplaza"], 1).encode("utf-8"))
    try:
        proc = subprocess.run(
            [PY, "-m", "pytest", mut["nodo"], "-q", "-p", "no:warnings", "--no-header", "-x"],
            cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        exit_rojo = proc.returncode
        corto = proc.stdout + proc.stderr
        resultados.append({
            "id": mut["id"],
            "archivo": mut["archivo"],
            "guard": mut["guard"],
            "nodo": mut["nodo"],
            "causa_esperada": mut["causa"],
            "anclas": si,
            "exit_con_mutante": exit_rojo,
            "rojo_por_fuga": exit_rojo != 0,
            "resumen": resumeen(corto)[-400:],
        })
    finally:
        ruta.write_bytes(original)
    despues = sha(ruta)
    resultados[-1]["restaurado"] = despues == antes
    resultados[-1]["sha256"] = antes[:16]

verdes = []
for mut in MUTANTES:
    proc = subprocess.run(
        [PY, "-m", "pytest", mut["nodo"], "-q", "-p", "no:warnings", "--no-header"],
        cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    verdes.append((mut["id"], proc.returncode, (proc.stdout + proc.stderr).strip().splitlines()[-1:]))

caidos = sum(1 for r in resultados if r.get("rojo_por_fuga"))
restaurados = sum(1 for r in resultados if r.get("restaurado"))
print(json.dumps({"mutantes": resultados, "verdes_post_restauracion": verdes}, ensure_ascii=False, indent=1))
print("TOTAL", len(resultados), "CAIDOS", caidos, "RESTAURADOS", restaurados)
