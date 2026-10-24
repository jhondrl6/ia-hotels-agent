"""FASE-H2 (`D18`, AC8): `config/settings.yaml` sin el bloque `thresholds` sin lector.

Las cuatro claves (`gbp_min_score`, `schema_required`, `min_reviews`, `min_photos`) estaban
declaradas LEGACY y **ningun** lector de produccion las consumia: el unico consumo del
archivo es `get_default_client()`, que toma `scrapers.requests`. Lo que quedaba era una
copia de umbrales que competia con sus sucesores reales (`gbp_score_bajo` del `BenchmarkLoader`
y `umbrales_fotos` de FASE-F), que es la clase de defecto que `L-SR3` nombra.

El diente no se conforma con que la clave no este en el YAML: exige que nadie la lea y que
el retiro este declarado con motivo y sucesor en el propio archivo.
"""

import yaml
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SETTINGS = RAIZ / "config" / "settings.yaml"
CLAVES_RETIRADAS = ("gbp_min_score", "schema_required", "min_reviews", "min_photos")


def _config() -> dict:
    return yaml.safe_load(SETTINGS.read_text(encoding="utf-8"))


def test_el_bloque_thresholds_ya_no_es_configuracion():
    """Las cuatro claves no existen en el YAML: no es que esten a cero."""
    import re

    config = _config()
    assert "thresholds" not in config, "el bloque `thresholds` volvio a config/settings.yaml"
    plano = SETTINGS.read_text(encoding="utf-8")
    assert re.search(r"^thresholds:", plano, flags=re.MULTILINE) is None
    # `package_thresholds` (bloque aparte, dueño Operador) si conserva sus claves regionales;
    # lo que se retiro es el bloque superior, asi que el guard se ancla a la cabecera.
    for clave in ("gbp_min_score", "schema_required", "min_photos"):
        assert f"{clave}:" not in plano, f"{clave} volvio a publicarse como configuracion"


def test_ningun_lector_de_produccion_pide_las_cuatro_claves():
    """0 referencias en modules/, scripts/ y main.py: ahi es donde viviria un lector.

    Se excluye tests/ a proposito: la prosa de un test puede nombrar la clave retirada
    para documentar la cura (hacerlo no es leerla). Un lector de verdad aparece en codigo.
    """
    produccion = [RAIZ / "main.py"] + list((RAIZ / "modules").rglob("*.py")) + list(
        (RAIZ / "scripts").rglob("*.py")
    )
    for clave in CLAVES_RETIRADAS:
        lectoras = [
            a.relative_to(RAIZ).as_posix()
            for a in produccion
            if a.is_file()
            and "__pycache__" not in a.parts
            and clave in a.read_text(encoding="utf-8")
        ]
        assert lectoras == [], f"{clave} tiene lectores de produccion: {lectoras}"


def test_el_unico_consumo_del_archivo_es_scrapers_requests():
    """El claim de `D18` es verificable: un solo archivo abre settings.yaml y lee una ruta."""
    aperturas = [
        a.relative_to(RAIZ).as_posix()
        for a in [RAIZ / "main.py"] + list((RAIZ / "modules").rglob("*.py")) + list((RAIZ / "scripts").rglob("*.py"))
        if a.is_file()
        and "__pycache__" not in a.parts
        and "config/settings.yaml" in a.read_text(encoding="utf-8")
    ]
    assert aperturas == ["modules/utils/http_client.py"], f"settings.yaml tiene mas abridores: {aperturas}"
    fuente = (RAIZ / "modules" / "utils" / "http_client.py").read_text(encoding="utf-8")
    assert "settings.get('scrapers', {}).get('requests', {})" in fuente
    for clave in CLAVES_RETIRADAS:
        assert clave not in fuente



def test_el_retiro_esta_declarado_con_su_sucesor():
    """El comentario de D18 nombra el motivo y los dos sucesores por su simbolo."""
    texto = SETTINGS.read_text(encoding="utf-8")
    assert "D18" in texto
    for sucesor in ("gbp_score_bajo", "umbrales_fotos", "sin sucesor"):
        assert sucesor in texto, f"el retiro no declara el sucesor {sucesor}"


def test_scrapers_requests_sigue_intacto_y_sigue_siendo_lo_unico_que_se_lee():
    """`scrapers.requests` es el consumo real del archivo y no se movio."""
    config = _config()
    requests = config["scrapers"]["requests"]
    for clave in ("timeout", "verify_ssl", "ssl_fallback"):
        assert clave in requests, f"scrapers.requests perdio {clave}"
    assert config["scrapers"]["requests"]["ssl_fallback"]["enabled"] is True
    fuente = (RAIZ / "modules" / "utils" / "http_client.py").read_text(encoding="utf-8")
    assert "settings.get('scrapers', {}).get('requests', {})" in fuente


def test_el_header_legacy_sigue_diciendo_quien_es_el_activo():
    """La cabecera del archivo sigue nombrando los configs activos; el retiro no la borro."""
    primeras_lineas = "\n".join(SETTINGS.read_text(encoding="utf-8").splitlines()[:15])
    assert "LEGACY" in primeras_lineas
    for activo in ("config/pricing.yaml", "config/scenarios.yaml", "config/regional_benchmarks.yaml"):
        assert activo in primeras_lineas
