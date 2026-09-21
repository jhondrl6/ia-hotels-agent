"""AC4 — mutation check **por asercion** sobre el simbolo real del guard (R2.8, L-T4A.5, L-V2.1).

Verde a la primera sin rojo es un falso verde potencial (L-VUP-5): este archivo apaga, uno a uno,
los simbolos reales del guard y exige que **la asercion que dice atacar** sea la que desaparece o
cambia su motivo. El anclaje es `assertion_key` (sujeto + afirmacion + documento), **no**
`assertion_id`: los ids son posicionales y se re-numeran cuando un hallazgo cae, anclar en ellos
daria un rojo que nombra a un tercero (la leccion del corpus L-V2.1 en su variante propia, medida
en esta fase y registrada en `10-analisis-post-implementacion.md`).

Las dos salidas quedan en disco: `verde_baseline.txt` y `mutante_<MUTANTE>.txt` bajo
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/mutation/`.
"""

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "validate_governance_numbers.py"
WF = "phased_project_executor.md"
TPL = "lecciones-capitalizadas-template.md"
N_WF, N_TPL = WF[:-3], TPL[:-3]          # `name` del documento es su stem
DOCS = [{"path": ROOT / ".agents" / "workflows" / WF, "name": N_WF},
        {"path": ROOT / ".agents" / "workflows" / "templates" / TPL, "name": N_TPL}]
SOURCE = ROOT / "scripts" / "run_all_validations.py"
HOOK = ROOT / "scripts" / "git_hooks" / "pre-commit"
EVIDENCE = ROOT / "evidence" / "VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20" / "FASE-A" / "mutation"

# Claves de las cuatro aserciones del maestro §1 (estables ante re-numeracion).
K_A1 = "validate_plan_citations.py|check 8|" + N_WF
K_A2 = "validate_lesson_capitalization.py|[9/9]|" + N_WF
K_A3 = "validate_qmind_writeback.py|[12/12]|" + N_WF
K_A4 = "validate_lesson_capitalization.py|[10/10]|" + N_TPL
BASELINE_KEYS = [K_A1, K_A2, K_A3, K_A4]


def _modulo():
    """Nombre de modulo unico por carga: un nombre fijo reutilizaba el `sys.modules` ya cargado
    y el mutante anterior seguia apagado (rojo que no era por el guard mutado)."""
    global _CARGAS
    _CARGAS += 1
    spec = importlib.util.spec_from_file_location(f"vgn_mut_{_CARGAS}", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_CARGAS = 0


def _medir(mut=None) -> dict:
    """Corre el escaneo real contra el arbol vigente con (opcionalmente) un guard apagado."""
    mod = _modulo()
    if mut:
        mut(mod)
    informe = mod.analizar(DOCS, SOURCE, HOOK)
    return {
        "keys": [f["assertion_key"] for f in informe["findings"]],
        "ids": {f["assertion_key"]: f["assertion_id"] for f in informe["findings"]},
        "reasons": {f["assertion_key"]: f["reasons"] for f in informe["findings"]},
        "occurrences": {f["assertion_key"]: len(f["occurrences"])
                        for f in informe["findings"]},
        "no_resueltas": informe["coverage_basis"]["poblacion"]["clase_no_resuelta"],
        "historicas": informe["coverage_basis"]["poblacion"]["clase_historica_congelada"],
    }


MUTANTES = [
    {
        "id": "M-A1",
        "simbolo": "check_n_discrepa()",
        "objetivo": K_A1,
        "apagar": lambda mod: setattr(mod, "check_n_discrepa", lambda claimed, record: False),
        "esperado": {"perdidos": [K_A1], "presentes": [K_A2, K_A3, K_A4]},
    },
    {
        "id": "M-A4",
        "simbolo": "total_discrepa()",
        "objetivo": K_A4 + " (su unico motivo es el denominador: [10/10] vs [10/11])",
        "apagar": lambda mod: setattr(mod, "total_discrepa", lambda claimed, t: False),
        "esperado": {"perdidos": [K_A4], "presentes": [K_A1, K_A2, K_A3],
                     "reasons_de": {K_A2: ["ordinal"], K_A3: ["ordinal"]}},
    },
    {
        "id": "M-A2",
        "simbolo": "ordinal_discrepa()",
        "objetivo": K_A2 + " — el guard mutado aportaba su motivo «ordinal»",
        "apagar": lambda mod: setattr(mod, "ordinal_discrepa", lambda claimed, record: False),
        "esperado": {"perdidos": [], "presentes": BASELINE_KEYS,
                     "reasons_de": {K_A2: ["denominador"], K_A3: ["denominador"]}},
    },
    {
        "id": "M-A3",
        "simbolo": 'KIND_MARKERS["full"]',
        "objetivo": K_A3 + " — sin marcador de modo completo su [12/12] no resuelve fuente",
        "apagar": lambda mod: setattr(mod, "KIND_MARKERS",
                                      {k: v for k, v in mod.KIND_MARKERS.items() if k != "full"}),
        "esperado": {"perdidos": [K_A3], "presentes": [K_A1, K_A2, K_A4],
                     "no_resueltas_suben": True},
    },
    {
        "id": "M-POBLACION",
        "simbolo": "es_mencion_historica()",
        "objetivo": "la regla de poblacion A8 (sin ella «y ninguna otra» se rompe)",
        "apagar": lambda mod: setattr(mod, "es_mencion_historica",
                                      lambda *a, **k: (False, ("sin-guard", "sin-guard"))),
        "esperado": {"perdidos": [], "presentes": BASELINE_KEYS, "hallazgos_extra": True,
                     "historicas_a_cero": True},
    },
    {
        "id": "M-SUJETO",
        "simbolo": "sujeto_de_la_instancia()",
        "objetivo": "la atribucion asercion -> check (sin sujeto no hay contraste posible)",
        "apagar": lambda mod: setattr(mod, "sujeto_de_la_instancia",
                                      lambda ventana, ancla, pool: None),
        "esperado": {"perdidos": BASELINE_KEYS, "presentes": []},
    },
]


@pytest.fixture(scope="module")
def verde() -> dict:
    medida = _medir()
    assert medida["keys"] == BASELINE_KEYS, (
        f"el baseline debe ser exactamente las cuatro aserciones del maestro §1: {medida['keys']}"
    )
    assert medida["historicas"] == 8, "la poblacion congelada tambien forma parte del verde"
    return medida


@pytest.mark.parametrize("mutante", MUTANTES, ids=[m["id"] for m in MUTANTES])
def test_el_rojo_es_causado_por_el_guard_mutado(mutante: dict, verde: dict):
    rojo = _medir(mutante["apagar"])
    esperado = mutante["esperado"]

    perdidos = [k for k in verde["keys"] if k not in rojo["keys"]]
    assert sorted(perdidos) == sorted(esperado["perdidos"]), (
        f"{mutante['id']}: se esperaba perder {esperado['perdidos']}, se perdio {perdidos} "
        "— el rojo debe nombrar la asercion mutada (L-V2.1)"
    )
    for presente in esperado["presentes"]:
        assert presente in rojo["keys"], f"{mutante['id']} no debia tocar {presente}"
    for clave, reasons in esperado.get("reasons_de", {}).items():
        assert rojo["reasons"][clave] == reasons, (
            f"{mutante['id']}: los motivos de {verde['ids'][clave]} debian pasar a {reasons}, "
            f"quedaron {rojo['reasons'][clave]}"
        )
    if esperado.get("no_resueltas_suben"):
        assert rojo["no_resueltas"] > verde["no_resueltas"]
    if esperado.get("hallazgos_extra"):
        assert len(rojo["keys"]) > len(verde["keys"]), (
            "apagar la regla de poblacion debe producir hallazgos adicionales: AC1 dice «y "
            "ninguna otra» justo gracias a ella"
        )
    if esperado.get("historicas_a_cero"):
        assert rojo["historicas"] == 0


def test_las_dos_salidas_quedan_en_disco(verde: dict):
    """AC4 sin el lado rojo en disco queda ⚠️ (R2.4): aqui se escriben el verde y cada mutante."""
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    verde_txt = [
        "# AC4 VERDE (baseline, guards activos)",
        f"arbol: {ROOT.name} · script: {SCRIPT.relative_to(ROOT).as_posix()}",
        f"assertion_ids: {verde['ids']}",
        f"reasons: {json.dumps(verde['reasons'], ensure_ascii=False, indent=1)}",
        f"occurrences por asercion: {json.dumps(verde['occurrences'], ensure_ascii=False)}",
        f"instancias no resueltas: {verde['no_resueltas']}",
        f"instancias historicas congeladas: {verde['historicas']}",
        "",
        "comando de reproduccion:",
        "  python -m pytest tests/quality_gates/governance_numbers/"
        "test_governance_numbers_mutation_por_asercion.py -q",
    ]
    (EVIDENCE / "verde_baseline.txt").write_text("\n".join(verde_txt) + "\n", encoding="utf-8")
    for mut in MUTANTES:
        rojo = _medir(mut["apagar"])
        lineas = [
            f"# AC4 ROJO — mutante {mut['id']} · objetivo: {mut['objetivo']}",
            f"simbolo real apagado: {mut['simbolo']}",
            f"aserciones en verde: {verde['keys']}",
            f"aserciones en rojo: {rojo['keys']}",
            f"perdidos: {[k for k in verde['keys'] if k not in rojo['keys']]}",
            f"gained: {[k for k in rojo['keys'] if k not in verde['keys']]}",
            f"reasons en rojo: {json.dumps(rojo['reasons'], ensure_ascii=False)}",
            f"ids en rojo (posicionales, se re-numerican): {json.dumps(rojo['ids'])}",
            f"no resueltas: {rojo['no_resueltas']} | historicas: {rojo['historicas']}",
            f"esperado por el test: {json.dumps(mut['esperado'], ensure_ascii=False, default=str)}",
            "",
            "comando de reproduccion (mismo que genero este archivo):",
            "  python -m pytest tests/quality_gates/governance_numbers/"
            "test_governance_numbers_mutation_por_asercion.py -q",
        ]
        (EVIDENCE / f"mutante_{mut['id']}.txt").write_text("\n".join(lineas) + "\n",
                                                           encoding="utf-8")
    assert (EVIDENCE / "verde_baseline.txt").exists()
    for mut in MUTANTES:
        assert (EVIDENCE / f"mutante_{mut['id']}.txt").exists()
