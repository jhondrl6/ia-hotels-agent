"""FASE-P3-B / AC-F5 — banderas reales de analitica en el bloque FASE-K.

Q5=(a) en `evidence/FASE-P1/decision-enforcement.md` (DA-P1.8): el pipeline calculaba
`ga4_client.is_available()` y lo descartaba fijando `ga4_enabled=False` al construir
`HotelFinancialData`, asi que la regla FASE-1 de `_determine_evidence_tier` ("sin
GA4+GSC, nunca A") nunca veia su input verdadero y el Tier A era inalcanzable por
construccion, no por falta de dato.

Dos capas de verificacion, porque la una sin la otra no certifica:
  * conductual — `ScenarioCalculator` si da `A` con analitica y `B+` sin ella (la regla
    que el plan declara intacta sigue siendo la regla);
  * de cableado — AST sobre `main.py`: el constructor recibe los nombres hoisteados, no
    constantes; el calculo vive por encima del consumidor, al mismo nivel de guarda y
    fuera de cualquier `except` ancho (L-T2C.2: dentro del `try` de FASE-K un NameError
    degradaria el tier en silencio).

Un test que solo lea el fuente puede volverse vacuo; por eso cada asercion de este
archivo tiene su mutacion registrada en `evidence/FASE-P3-B/` (NR7).
"""

import ast
from pathlib import Path

import pytest

from modules.financial_engine.scenario_calculator import HotelFinancialData, ScenarioCalculator

MAIN_PY = Path(__file__).resolve().parents[3] / "main.py"
FUNC = "run_v4_complete_mode"


# --------------------------------------------------------------------------- #
# Layer AST — lectura del fuente de produccion
# --------------------------------------------------------------------------- #

@pytest.fixture(scope="module")
def fase_k():
    """(funcion, mapa de padres, llamada HotelFinancialData) de main.py."""
    tree = ast.parse(MAIN_PY.read_text(encoding="utf-8"))
    func = next(
        (n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == FUNC),
        None,
    )
    assert func is not None, f"main.py ya no define {FUNC}()"
    parents = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[child] = node
    calls = [
        n for n in ast.walk(func)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
        and n.func.id == "HotelFinancialData"
    ]
    assert len(calls) == 1, (
        f"se esperaba una unica construccion de HotelFinancialData en el flujo "
        f"v4complete (FASE-K); hay {len(calls)} — el cableado de AC-F5 se duplico"
    )
    return func, parents, calls[0]


def _keyword(call, name):
    for kw in call.keywords:
        if kw.arg == name:
            return kw.value
    raise AssertionError(
        f"HotelFinancialData del bloque FASE-K perdio el argumento `{name}`: "
        f"el tier volveria a decidirse con el default False del DTO"
    )


def _assignments(func, target):
    found = []
    for node in ast.walk(func):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == target:
                    found.append(node)
    return found


def _guard_ancestry(node, parents):
    """Guardas que condicionan que `node` se ejecute: cuerpos de `if` y `except`."""
    guards = []
    cur = node
    parent = parents.get(cur)
    while parent is not None:
        if isinstance(parent, ast.If) and any(cur is b for b in parent.body):
            guards.append(("if", parent.lineno))
        if isinstance(parent, ast.Try) and any(cur is h for h in parent.handlers):
            guards.append(("handler", parent.lineno))
        cur = parent
        parent = parents.get(cur)
    return frozenset(guards)


def _broad_try_ancestry(node, parents):
    """Lineas de `try` cuyo cuerpo envuelve a `node` y cuyo handler traga todo."""
    hits = []
    cur = node
    parent = parents.get(cur)
    while parent is not None:
        if isinstance(parent, ast.Try) and any(cur is s for s in parent.body):
            for handler in parent.handlers:
                catches_all = handler.type is None or (
                    isinstance(handler.type, ast.Name)
                    and handler.type.id in ("Exception", "BaseException")
                )
                if catches_all:
                    hits.append(parent.lineno)
                    break
        cur = parent
        parent = parents.get(cur)
    return hits


class TestCableadoBanderasEnFASEK:
    """El constructor de FASE-K ya no miente sobre la conectividad."""

    def test_ga4_enabled_no_es_constante(self, fase_k):
        _, _, call = fase_k
        value = _keyword(call, "ga4_enabled")
        assert isinstance(value, ast.Name), (
            "ga4_enabled vuelve a ser un literal: el Tier A queda inalcanzable por "
            "construccion (DA-P1.8)"
        )
        assert value.id == "ga4_available", value.id

    def test_gsc_enabled_no_es_constante(self, fase_k):
        _, _, call = fase_k
        value = _keyword(call, "gsc_enabled")
        assert isinstance(value, ast.Name), (
            "gsc_enabled vuelve a ser un literal: con la regla FASE-1 exige ambas "
            "banderas, asi que una falsa cancela la otra"
        )
        assert value.id == "gsc_available", value.id

    @pytest.mark.parametrize("target", ["ga4_available", "gsc_available"])
    def test_disponibilidad_calculada_antes_del_consumidor(self, fase_k, target):
        func, _, call = fase_k
        assigns = _assignments(func, target)
        assert len(assigns) == 1, (
            f"{target} se calcula {len(assigns)} veces: dos fuentes del mismo hecho "
            f"es la causa estructural que este plan nombra como L-SR3"
        )
        assert assigns[0].lineno < call.lineno, (
            f"{target} (linea {assigns[0].lineno}) se calcula despues de "
            f"HotelFinancialData (linea {call.lineno}): FASE-K consumiría el valor viejo"
        )

    @pytest.mark.parametrize("target", ["ga4_available", "gsc_available"])
    def test_hoist_alcanzable_donde_lo_es_fase_k(self, fase_k, target):
        """El hoist no puede estar bajo una guarda que FASE-K no este tambien."""
        func, parents, call = fase_k
        assign = _assignments(func, target)[0]
        hoist_guards = _guard_ancestry(assign, parents)
        consumer_guards = _guard_ancestry(call, parents)
        assert hoist_guards.issubset(consumer_guards), (
            f"{target} esta condicionado por {sorted(hoist_guards - consumer_guards)} "
            f"y el bloque FASE-K no: en ese regimen el constructor veria un NameError "
            f"en lugar de la bandera real"
        )

    @pytest.mark.parametrize("target", ["ga4_available", "gsc_available"])
    def test_hoist_fuera_de_todo_except_ancho(self, fase_k, target):
        """L-T2C.2: envuelto en `except Exception`, un fallo degradaria el tier en silencio."""
        func, parents, _ = fase_k
        assign = _assignments(func, target)[0]
        hits = _broad_try_ancestry(assign, parents)
        assert not hits, (
            f"{target} se calcula dentro de un try con handler ancho (linea {hits}); "
            f"un NameError enmascarado baja el tier sin que nadie lo vea"
        )


class TestManifiestoNoContradiceElTier:
    """`gsc_configured` del MANIFEST lee el mismo valor que alimenta el tier."""

    def test_gsc_configured_usa_el_valor_hoisteado(self, fase_k):
        func, _, _ = fase_k
        dicts = []
        for node in ast.walk(func):
            if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Attribute) and t.attr == "_quality_metadata"
                for t in node.targets
            ):
                dicts.append(node)
        assert len(dicts) == 1, "se perdio o se duplico el dict de quality_metadata"
        meta = dicts[0].value
        assert isinstance(meta, ast.Dict)
        values = {
            k.value: v for k, v in zip(meta.keys, meta.values) if isinstance(k, ast.Constant)
        }
        for key, expected in (("ga4_configured", "ga4_available"),
                              ("gsc_configured", "gsc_available")):
            node = values.get(key)
            assert isinstance(node, ast.Name) and node.id == expected, (
                f"{key} ya no lee el valor unico de la corrida ({expected}): el ZIP "
                f"podria declarar una conectividad distinta de la que subio el tier"
            )


# --------------------------------------------------------------------------- #
# Capa conductual — la regla FASE-1, sobre el codigo de produccion
# --------------------------------------------------------------------------- #

def _hotel_data(ga4: bool, gsc: bool) -> HotelFinancialData:
    """Mismo shape que construye FASE-K con onboarding completo (adr/canal verificados)."""
    return HotelFinancialData(
        rooms=24,
        adr_cop=320000.0,
        occupancy_rate=0.62,
        direct_channel_percentage=0.18,
        ota_commission_rate=0.15,
        adr_source="onboarding",
        occupancy_source="onboarding",
        channel_source="onboarding",
        ga4_enabled=ga4,
        gsc_enabled=gsc,
    )


class TestReglaFASE1SigueViva:
    """Lo que cambio es el input de la regla, no la regla."""

    def test_tier_a_con_analitica_disponible(self):
        breakdown = ScenarioCalculator().calculate_breakdown(_hotel_data(True, True))
        assert breakdown.evidence_tier == "A"

    def test_tier_b_mas_sin_analitica(self):
        breakdown = ScenarioCalculator().calculate_breakdown(_hotel_data(False, False))
        assert breakdown.evidence_tier == "B+"

    @pytest.mark.parametrize("ga4,gsc", [(True, False), (False, True)],
                             ids=["solo-ga4", "solo-gsc"])
    def test_tier_b_mas_con_una_sola_fuente(self, ga4, gsc):
        """La regla exige ambas: propagar solo una bandera no subiria el tier."""
        breakdown = ScenarioCalculator().calculate_breakdown(_hotel_data(ga4, gsc))
        assert breakdown.evidence_tier == "B+"

    def test_tier_a_exige_dato_verificado_ademas_de_la_conectividad(self):
        """Conectividad sin onboarding verificado NO es A — la regla no se afloja."""
        data = _hotel_data(True, True)
        data.adr_source = "scraping"
        data.channel_source = "scraping"
        breakdown = ScenarioCalculator().calculate_breakdown(data)
        assert breakdown.evidence_tier != "A"
