"""`D25-bis` — un solo valor vivo para `recovery_factors` (FASE-F).

El maestro es `config/scenarios.yaml` (`realistic: 0.35`). Antes de esta fase el factor
realista vivía en tres sitios que nadie sincronizaba: el dict de respaldo de
`V4ProposalGenerator._load_scenario_config` (0.20), el default del `.get('realistic', 0.20)` del
cálculo de ROI y el default del `.get('realistic', 0.35)` de `V4DiagnosticGenerator`. Hoy el
respaldo vive en un solo sitio (`modules/common/scenario_config.py`) y este test lo contra
contra el maestro: si divergen, se pone en rojo.
"""

import ast
from pathlib import Path

import pytest

from modules.common.scenario_config import RESPALDO_ESCENARIOS, respaldo_escenarios
from modules.common.yaml_loader import YAMLLoadError, load_yaml_config

RAIZ = Path(__file__).resolve().parents[2]
MAESTRO = RAIZ / "config" / "scenarios.yaml"

LECTORES = (
    "modules/commercial_documents/v4_proposal_generator.py",
    "modules/commercial_documents/v4_diagnostic_generator.py",
)


def _divergencias() -> list:
    """Claves del respaldo que no casan con el maestro, con el valor de cada lado."""
    maestro = load_yaml_config("scenarios", config_dir=RAIZ / "config")
    divergen = []
    for clave, valor in RESPALDO_ESCENARIOS.items():
        publicado = maestro.get(clave)
        if isinstance(valor, dict):
            for sub, sub_valor in valor.items():
                if (publicado or {}).get(sub) != sub_valor:
                    divergen.append(
                        f"{clave}.{sub}: respaldo={sub_valor} maestro={(publicado or {}).get(sub)}"
                    )
        elif publicado != valor:
            divergen.append(f"{clave}: respaldo={valor} maestro={publicado}")
    return divergen


def test_maestro_publica_el_factor_que_se_presto_a_duplicarse():
    """Ancla del dato: `scenarios.yaml` dice 0.35 (el respaldo alguna vez dijo 0.20)."""
    maestro = load_yaml_config("scenarios", config_dir=RAIZ / "config")
    assert maestro["recovery_factors"] == {"conservative": 0.15, "realistic": 0.35, "optimistic": 0.25}
    assert maestro["recovery_factors"]["realistic"] == 0.35


def test_el_respaldo_no_diverge_del_maestro():
    """AC6: un solo valor vivo. El respaldo puede existir, no puede contradecir."""
    assert _divergencias() == []


def test_mutante_de_divergencia_pone_en_rojo_el_cotejo(monkeypatch):
    """El diente del diente: restaurar el 0.20 viejo en el respaldo hace caer el cotejo."""
    monkeypatch.setitem(RESPALDO_ESCENARIOS["recovery_factors"], "realistic", 0.20)
    divergen = _divergencias()
    assert divergen and divergen[0].startswith("recovery_factors.realistic"), divergen
    assert "respaldo=0.2" in divergen[0] and "maestro=0.35" in divergen[0]


def test_el_camino_de_respaldo_devuelve_el_factor_del_maestro():
    """Sin YAML legible, la propuesta calcula con 0.35, no con el factor fosilizado."""
    from modules.commercial_documents.v4_proposal_generator import V4ProposalGenerator

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(
            "modules.commercial_documents.v4_proposal_generator.load_yaml_config",
            lambda *a, **k: (_ for _ in ()).throw(YAMLLoadError("not found")),
        )
        config = V4ProposalGenerator()._load_scenario_config()
    assert config["recovery_factors"]["realistic"] == 0.35
    assert config["scenario_weights"] == RESPALDO_ESCENARIOS["scenario_weights"]


def test_el_respaldo_devuelve_copia_y_no_la_instancia_maestra():
    """Quien consuma el respaldo no puede mutar la única fuente Python de estos valores."""
    copia = respaldo_escenarios()
    copia["recovery_factors"]["realistic"] = 0.99
    assert RESPALDO_ESCENARIOS["recovery_factors"]["realistic"] == 0.35


@pytest.mark.parametrize("rel_ruta", LECTORES)
def test_los_lectores_no_ponen_default_al_factor(rel_ruta: str):
    """Ningún lector recupera el `.get('realistic', X)`: el valor lo dicta una sola fuente."""
    arbol = ast.parse((RAIZ / rel_ruta).read_text(encoding="utf-8"))
    defaults = []
    for nodo in ast.walk(arbol):
        if (
            isinstance(nodo, ast.Call)
            and isinstance(nodo.func, ast.Attribute)
            and nodo.func.attr == "get"
            and any(isinstance(a, ast.Constant) and a.value == "realistic" for a in nodo.args)
            and len(nodo.args) > 1
        ):
            defaults.append(ast.unparse(nodo))
    assert not defaults, f"{rel_ruta} vuelve a tener un default del factor: {defaults}"


@pytest.mark.parametrize("rel_ruta", LECTORES)
def test_ambos_generadores_declaran_el_mismo_sitio_de_respaldo(rel_ruta: str):
    """Los dos caminos comerciales leen el respaldo del módulo único, no el suyo propio."""
    arbol = ast.parse((RAIZ / rel_ruta).read_text(encoding="utf-8"))
    importados = {
        alias.name
        for nodo in ast.walk(arbol)
        if isinstance(nodo, ast.ImportFrom) and (nodo.module or "").endswith("scenario_config")
        for alias in nodo.names
    }
    assert importados & {"respaldo_escenarios", "RESPALDO_ESCENARIOS"}, (
        f"{rel_ruta} calcula dinero sin declarar la fuente del respaldo"
    )


def test_el_archivo_de_respaldo_es_legible_por_su_ruta_absoluta():
    """La ancla del maestro existe: si alguien mueve scenarios.yaml, este test lo nombra."""
    assert MAESTRO.exists(), f"falta el maestro {MAESTRO}"
