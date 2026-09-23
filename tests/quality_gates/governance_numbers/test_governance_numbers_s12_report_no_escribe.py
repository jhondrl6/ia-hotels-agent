"""S12 / L-VCF-12 - volver a medir no puede re-escribir el registro fechado de otra fase.

Medido por la propia fase: `python scripts/validate_governance_numbers.py --report` tenia una ruta por
default apuntando a `evidence/…/FASE-A/informe.json`, y cada corrida re-escribia `generated_at`,
`medido_el` y el conteo de funciones de test, o sea **el verde se publicaba pisando evidencia ajena**.
La cura no es un `git checkout` disciplinado cada vez: es que el default no escriba.

Un solo estado por prueba (R2.9), y las tres miden resultados y codigos de salida en lugar de relatar
lo que el instrumento dice que hizo.
"""

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "validate_governance_numbers.py"
EVIDENCIA_CERRADA = ROOT / "evidence" / "VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20"


def huellas(directorio: Path) -> dict:
    """sha256 y mtime de cada archivo del expediente: lo que tiene que quedar igual."""
    return {p.relative_to(ROOT).as_posix():
            (hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_mtime_ns)
            for p in sorted(directorio.rglob("*")) if p.is_file()}


def correr(*extra):
    return subprocess.run([sys.executable, str(SCRIPT), *extra],
                          capture_output=True, text=True, cwd=str(ROOT),
                          env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})


def test_report_sin_destino_no_toca_el_expediente_cerrado(gobierno):
    """El caso que la deuda describe literalmente: `--report` a secas sobre el arbol vigente."""
    antes = huellas(EVIDENCIA_CERRADA)
    r = correr("--report",
               "--governance-doc", str(gobierno["doc"]),
               "--source", str(gobierno["source"]),
               "--hook", str(gobierno["hook"]))
    assert huellas(EVIDENCIA_CERRADA) == antes, (
        "correr el verificador sin destino modifico archivos de evidence/: un verificador no puede "
        "gobernar el registro fechado de otra fase (S12)")
    assert '"status"' in r.stdout, r.stdout[:400] + r.stderr[:400]


def test_report_sin_destino_declara_que_no_escribe_en_lugar_de_hacerlo_a_escondidas(gobierno):
    r = correr("--report",
               "--governance-doc", str(gobierno["doc"]),
               "--source", str(gobierno["source"]),
               "--hook", str(gobierno["hook"]))
    salida = r.stdout + r.stderr
    assert "no se escribio ningun archivo" in salida, salida[:600]
    # Y no quedo un informe suelto en el directorio de trabajo del fixture.
    assert not list(gobierno["tmp"].rglob("informe*.json"))


def test_report_sin_destino_publica_json_parseable_por_stdout(gobierno):
    """stdout lleva SOLO el JSON: el aviso de no-escritura va a stderr, y un consumidor que parsea
    stdout no tiene que filtrar relatos (orden 2026-09-22 §4.A)."""
    r = correr("--report",
               "--governance-doc", str(gobierno["doc"]),
               "--source", str(gobierno["source"]),
               "--hook", str(gobierno["hook"]))
    datos = json.loads(r.stdout)
    assert datos["tool"] == "scripts/validate_governance_numbers.py"
    assert "no se escribio ningun archivo" in r.stderr


def test_report_con_destino_nombrado_si_escribe_ahi(gobierno, tmp_path):
    """El destino explicito sigue existiendo: la cura quita el default, no la capacidad de persistir."""
    destino = tmp_path / "evidencia-nueva" / "informe.json"
    r = correr("--report", str(destino),
               "--governance-doc", str(gobierno["doc"]),
               "--source", str(gobierno["source"]),
               "--hook", str(gobierno["hook"]))
    assert destino.is_file(), r.stdout[:400] + r.stderr[:400]
    assert '"status"' in destino.read_text(encoding="utf-8")


def test_el_script_ya_no_conoce_ruta_de_evidencia_como_destino_de_escritura(modulo_gn):
    """Estructura, no solo conducta: si vuelve a aparecer una ruta de evidencia hardcodeada como
    default, esto se pone rojo aunque nadie la invoque en la corrida de hoy."""
    texto = Path(modulo_gn.__file__).read_text(encoding="utf-8")
    referencias = [linea.strip() for linea in texto.splitlines()
                   if "evidence" in linea and not linea.strip().startswith("#")]
    assert referencias == [], (
        f"el verificador vuelve a nombrar evidence/ fuera de un comentario: {referencias}")


def test_la_costante_del_default_vacio_no_revive(modulo_gn):
    """`REPORT_DEFAULT` era la ruta que pisaba FASE-A; si reaparece, esto se pone rojo aunque la
    conducta de hoy siga siendo correcta, porque el riesgo vuelve a estar armado."""
    assert not hasattr(modulo_gn, "REPORT_DEFAULT")
