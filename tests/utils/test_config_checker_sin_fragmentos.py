"""El chequeo de configuracion no imprime ni un fragmento del valor.

`modules/utils/config_checker.py` reportaba sus claves como `value[:4]...value[-4:]` comentado
«por seguridad». Las formas de `modules/utils/redaction.py:22-27` exigen >=16 chars tras `sk-` y
>=25 tras `AIzaSy`: el recorte es mas corto que el patron que deberia cazarlo, asi que sobrevivia
al sumidero y quedaba en stdout, que la evidencia de consola persiste en un repo publico. La rama
`else` del censo imprimia el valor ENTERO de toda variable cuyo nombre no contenga `API` (el
predicado es por nombre, no por naturaleza del valor).

Este archivo gobierna la FORMA, no la cifra: ninguna salida del censo puede tener
`prefijo...sufijo` ni llevar el valor con el que fue construida.
"""
from __future__ import annotations

import importlib.util
import inspect
import re
import subprocess
from pathlib import Path

from modules.utils.config_checker import ConfigChecker

ROOT = Path(__file__).resolve().parents[2]
RUTA_PRODUCTOR = "modules/utils/config_checker.py"
# Revision previa a la cura: la que todavia construia el fragmento.
REV_DEFECTO = "b46a7b3"

# Forma que la cura tiene que eliminar: cualquier `xxx...yyy` pegado a texto de valor.
FORMA_FRAGMENTO = re.compile(r"[A-Za-z0-9_./:\\-]{2,}\.\.\.[A-Za-z0-9_./:\\-]{2,}")

# Formas que NO casan con las de credencial (la convencion del vecino
# test_config_checker_placeholder.py:30): un fixture con forma real seria un hallazgo del
# verificador de secretos, no una prueba.
SINT_DEEPSEEK = "SYNTHETIC-DEEPSEEK-0123456789-aa11"
SINT_GOOGLE = "SYNTHETIC-GOOGLE-0123456789-bb22"
SINT_RUTA = "C:/drivers/SYNTHETIC-WEBDRIVER-0123456789.bin"

# Los nombres que el checker censa. test_el_censo_no_deja_nombre_sin_fixture gobierna que esta
# lista no se quede atras cuando el producto agrega una variable.
NOMBROS = {
    "DEEPSEEK_API_KEY": SINT_DEEPSEEK,
    "ANTHROPIC_API_KEY": SINT_DEEPSEEK,
    "OPENAI_API_KEY": SINT_DEEPSEEK,
    "GOOGLE_API_KEY": SINT_GOOGLE,
    "GOOGLE_MAPS_API_KEY": SINT_GOOGLE,
    "PAGESPEED_API_KEY": SINT_GOOGLE,
    "GOOGLE_PAGESPEED_API_KEY": SINT_GOOGLE,
    "WEBDRIVER_PATH": SINT_RUTA,
}
VALORES = sorted(set(NOMBROS.values()))


def _cargar(nombre: str, ruta: Path):
    espec = importlib.util.spec_from_file_location(nombre, str(ruta))
    modulo = importlib.util.module_from_spec(espec)
    espec.loader.exec_module(modulo)
    return modulo


def _correr(clase_checker, monkeypatch) -> list[str]:
    """El censo entero sobre valores sinteticos: [OK] y advertencias del mismo paso."""
    for nombre, valor in NOMBROS.items():
        monkeypatch.setenv(nombre, valor)
    checker = clase_checker()
    checker._check_env_variables()
    return [texto for texto, _ in checker.checks] + list(checker.warnings)


class TestEmisorSinFragmentos:
    def test_clave_larga_no_deja_ni_un_fragmento_de_su_valor(self, monkeypatch):
        salida = _correr(ConfigChecker, monkeypatch)
        assert any("DEEPSEEK_API_KEY" in s for s in salida), "el censo no reporto la clave: fixture roto"
        for texto in salida:
            for valor in VALORES:
                assert valor not in texto, f"valor entero filtrado: {texto!r}"
                assert valor[:4] not in texto, f"prefijo filtrado: {texto!r}"
                assert valor[-4:] not in texto, f"sufijo filtrado: {texto!r}"

    def test_la_forma_prefijo_punto_punto_sufijo_no_aparece_en_ninguna_salida(self, monkeypatch):
        salida = _correr(ConfigChecker, monkeypatch)
        culpables = [s for s in salida if FORMA_FRAGMENTO.search(s)]
        assert culpables == [], f"reaparecio la forma `prefijo...sufijo`: {culpables}"

    def test_se_publican_nombre_estado_y_longitud(self, monkeypatch):
        salida = _correr(ConfigChecker, monkeypatch)
        assert salida.count(f"[OK] DEEPSEEK_API_KEY: configurada ({len(SINT_DEEPSEEK)} chars)") == 1, salida
        assert salida.count(f"[OK] WEBDRIVER_PATH: definido ({len(SINT_RUTA)} chars)") == 1, salida

    def test_variable_sin_api_en_el_nombre_tampoco_imprime_su_valor(self, monkeypatch):
        salida = [s for s in _correr(ConfigChecker, monkeypatch) if "WEBDRIVER_PATH" in s]
        assert salida, "el censo no reporto la variable: fixture roto"
        for texto in salida:
            assert SINT_RUTA not in texto, f"valor entero filtrado: {texto!r}"
            assert SINT_RUTA[:4] not in texto and SINT_RUTA[-4:] not in texto

    def test_el_censo_no_deja_nombre_sin_fixture(self):
        fuente = inspect.getsource(ConfigChecker._check_env_variables)
        inicio = fuente.index("env_vars = {")
        cierre = fuente.index("}", inicio)
        bloque = fuente[inicio:cierre + 1]
        censados = set(re.findall(r"'([A-Z][A-Z0-9_]{3,})'", bloque))
        assert censados, "no se lee el censo desde la fuente: el control perdio su insumo"
        sin_fixture = censados - set(NOMBROS)
        assert not sin_fixture, f"variables censadas sin valor sintetico: {sorted(sin_fixture)}"


class TestControlesContraElDefecto:
    def test_la_revision_anclada_si_imprimia_el_fragmento(self, tmp_path, monkeypatch):
        """`git show b46a7b3:...` ejercitado: con los MISMOS valores sinteticos la version vieja
        emite `prefijo...sufijo` y la cura no. Eso prueba que el diente caza este defecto."""
        proc = subprocess.run(["git", "show", f"{REV_DEFECTO}:{RUTA_PRODUCTOR}"],
                              capture_output=True, text=True, encoding="utf-8", cwd=str(ROOT))
        assert proc.returncode == 0, f"{REV_DEFECTO} no resuelve: re-anclar el control ({proc.stderr[:120]})"
        fuente_vieja = proc.stdout
        assert "value[:4]" in fuente_vieja, (
            f"la revision {REV_DEFECTO} ya no construye el fragmento: dejo de ser anterior a la cura, "
            "re-anclar el control a una revision previa")

        # El modulo viejo carga .env en tiempo de import: se anula para que nunca le llegue un
        # valor real. Con los ocho nombres ya puestos, el censo solo ve sinteticos.
        monkeypatch.setattr("dotenv.load_dotenv", lambda *a, **k: False)
        ruta_vieja = tmp_path / "config_checker_viejo.py"
        ruta_vieja.write_text(fuente_vieja, encoding="utf-8", newline="\n")
        viejo = _cargar("config_checker_viejo", ruta_vieja)

        fragmentos = [s for s in _correr(viejo.ConfigChecker, monkeypatch) if FORMA_FRAGMENTO.search(s)]
        assert fragmentos, "la version anclada no emitio la forma: el control perdio su rojo"
        esperado = f"[OK] DEEPSEEK_API_KEY: {SINT_DEEPSEEK[:4]}...{SINT_DEEPSEEK[-4:]}"
        assert esperado in fragmentos, f"el rojo no es el del defecto gobernado: {fragmentos[:3]}"
        for texto in fragmentos:
            for valor in VALORES:
                assert valor not in texto, "el control negativo imprimio el valor entero"

    def test_el_mutante_restaurado_no_puede_pasar_en_verde(self, tmp_path, monkeypatch):
        """Oportunidad de perder: el archivo curado con la linea del fragmento vuelta a su forma
        vieja tiene que fallar el diente de la forma."""
        fuente = (ROOT / RUTA_PRODUCTOR).read_text(encoding="utf-8")
        mutado = fuente.replace(
            '(f"[OK] {var}: configurada ({len(value.strip())} chars)", "ok")',
            '(f"[OK] {var}: " + value[:4] + "..." + value[-4:], "ok")',
            1,
        )
        assert mutado != fuente, "el ancla del mutante no casa: re-anclar contra la linea curada"
        monkeypatch.setattr("dotenv.load_dotenv", lambda *a, **k: False)
        ruta = tmp_path / "config_checker_mutado.py"
        ruta.write_text(mutado, encoding="utf-8", newline="\n")
        mutante = _cargar("config_checker_mutante", ruta)

        assert [s for s in _correr(mutante.ConfigChecker, monkeypatch) if FORMA_FRAGMENTO.search(s)], \
            "el mutante paso inadvertido"
