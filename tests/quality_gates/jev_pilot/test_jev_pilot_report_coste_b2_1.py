# -*- coding: utf-8 -*-
"""Dientes de la contabilidad de coste de `report` (CURA B2-1 / B2-1c, 2026-10-09).

Cierran las dos filas que FASE-RELEASE dejó con dueño en `scripts/evaluate_jev_pilot.py` (`report`)
bajo el criterio AC4: el informe no comparaba `usage_normalized` contra `limites_gasto` ni publicaba
`cost_calculated`/`cost_billed`, y el exceso de 145 tokens de salida contra el techo congelado de 139
no lo publicaba ningún instrumento.

Todo es offline: los insumos son `respuestas.jsonl` + `etiquetas.json` + `muestra.json` +
`protocolo.json` sintéticos, el guard de sockets del `conftest.py` está armado por fixture autouse,
y el único insumo real que se lee es el versionado de FASE-C (solo lectura, cero red, cero clientes).

Población sintética, calculada a mano y escrita junto a cada aserción:

| brazo       | fila | input | output | contra techo in 1834 | contra techo out 139 |
|-------------|------|-------|--------|----------------------|-----------------------|
| jev         | J1   | 1778  | 145    | DENTRO, margen 56     | EXCESO, +6            |
| jev         | J2   | 10    | 5      | —                    | —                     |
| deepseek    | D1   | 1054  | 130    | DENTRO, margen 780    | DENTRO, margen 9      |
| deepseek    | D2 | —  | —      | sin medida (`sin_usage`) | sin medida        |
| capa_fria   | C1   | None  | None   | NO-EVALUABLE          | NO-EVALUABLE          |

Sumas de jev: input 1778+10 = **1788**, output 145+5 = **150**. Con tarifa declarada
(in 0.30 / out 2.50 USD por 1M) el coste calculado es 1788/1e6*0.30 + 150/1e6*2.50 =
0.0005364 + 0.000375 = **0.0009114**.
"""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
RUNNER = REPO_ROOT / "scripts" / "evaluate_jev_pilot.py"
EVID = REPO_ROOT / "evidence" / "EVALUACION-JEV-TYPESAFE-2026-09-21"
RESPUESTAS_C = EVID / "FASE-C" / "respuestas.jsonl"
PROTOCOLO_C = EVID / "protocolo.json"
MUESTRA_C = EVID / "muestra.json"
ETIQUETAS_C = EVID / "etiquetas.json"


# ----------------------------------------------------------------------------------------------
# insumos sinteticos
# ----------------------------------------------------------------------------------------------

def _par(pid: str, lesson: str, split: str) -> dict:
    return {"pair_id": pid, "target_plan": pid.split("::")[0], "target_phase": "CURA-B2-1",
            "lesson_id": lesson, "input_fragment": f"fragmento de {pid}",
            "original_sha256": "0" * 64, "sanitized_sha256": "0" * 64, "split": split}


def muestra_base() -> dict:
    pares = [_par("A::L-A", "L-A", "eval"), _par("B::L-B", "L-B", "eval")]
    return {"schema": "jev-pilot-muestra/v1", "status": "CONGELADA",
            "corpus_source": "synthetic", "temporal_cut": "2026-09-12",
            "review": {"human_reviewed": True, "reviewer": "jhon", "reviewed_at": "2026-10-02"},
            "pairs": pares, "exclusions": [],
            "counts": {"total": 2, "dev": 0, "eval": 2, "excluidos": 0}}


def etiquetas_base() -> dict:
    return {"schema": "jev-pilot-etiquetas/v1", "review_status": "revisada",
            "labels": [
                {"pair_id": "A::L-A", "label": "pertinente", "importance": "alta",
                 "reviewer": "jhon", "reviewed_at": "2026-10-02"},
                {"pair_id": "B::L-B", "label": "pertinente", "importance": "media",
                 "reviewer": "jhon", "reviewed_at": "2026-10-02"}]}


def protocolo_base(**gastos) -> dict:
    base = {"schema": "jev-pilot-protocolo/v1", "status": "CONGELADA",
            "congelado": {"revisado_por": "jhon", "fecha": "2026-10-04"},
            "reglas_recuperacion": "top-8 por consulta fria, mismo conjunto elegible",
            "rubrica": {"valores": ["pertinente", "no_pertinente", "insuficiente"],
                        "importancia": ["alta", "media", "baja"]},
            "modelos": {"jev_pin": "jev-1.13.0", "comparador": "DeepSeek", "excluido": "Anthropic"},
            "parametros": {"retry_policy": {"max_retries": 0}, "timeout_s": 30},
            "limites_gasto": {"usd": None, "llamadas": 12, "tokens_in": 1834, "tokens_out": 139,
                              "motivo": "fuera de gobernanza por decision del operador"},
            "criterios_adopcion": {"cobertura_min": 0.95, "margen_vs_deepseek": 0.25,
                                   "tratamiento_abstenciones": "contadas como fallo de recuperacion",
                                   "suficiencia_minima": 0.5, "latencia_max": 30000,
                                   "revision_humana": "obligatoria; designado: jhon (2026-10-02)"}}
    base["limites_gasto"].update(gastos)
    return base


def fila(brazo: str, pid: str, lesson: str, *, propuesta="L-A", usage=None,
         intentos=None, cargo_facturado=None, error_kind=None, attempts=1) -> dict:
    return {"pair_id": pid, "split": "eval", "lesson_id_target": lesson,
            "etiqueta": "pertinente", "importancia": "alta",
            "candidatos_frios": [lesson, "L-X"], "leccion_target_en_candidatos": True,
            "brazo": brazo, "modelo_pedido": "jev-1.13.0" if brazo == "jev" else "deepseek-chat",
            "modelo_efectivo": None, "propuesta": propuesta,
            "abstencion": (None if propuesta is None or isinstance(propuesta, list)
                           else propuesta == "ninguna-aplica"),
            "attempts": attempts, "error_kind": error_kind,
            "duracion_ms": [i.get("duracion_ms") for i in (intentos or [])],
            "usage_normalized": usage, "cargo_facturado": cargo_facturado,
            "request_id": None, "intentos": intentos or []}


def uso(entrada, salida, estado="observado") -> dict:
    total = None if (entrada is None or salida is None) else entrada + salida
    return {"input_tokens": entrada, "output_tokens": salida, "total": total, "estado": estado,
            "libera_reserva_como_cero": False}


def respuestas_base() -> list:
    return [
        fila("jev", "A::L-A", "L-A", intentos=[{"n": 1, "resultado": "exito", "duracion_ms": 200.0}],
             usage=uso(1778, 145)),
        fila("jev", "B::L-B", "L-B", intentos=[{"n": 1, "resultado": "exito", "duracion_ms": 300.0}],
             usage=uso(10, 5)),
        fila("deepseek", "A::L-A", "L-A", propuesta="ninguna-aplica",
             intentos=[{"n": 1, "resultado": "exito", "duracion_ms": 1000.0}], usage=uso(1054, 130)),
        fila("deepseek", "B::L-B", "L-B", propuesta=None, error_kind="conexion",
             intentos=[{"n": 1, "resultado": "fallo", "duracion_ms": 12.0}],
             usage=uso(None, None, "sin_usage")),
        fila("capa_fria", "A::L-A", "L-A", intentos=[], usage=uso(None, None, "no_intentada")),
    ]


def insumos(tmp_path: Path, *, respuestas=None, protocolo=None, muestra=None, etiquetas=None):
    tmp_path.mkdir(parents=True, exist_ok=True)
    ruta_r = tmp_path / "respuestas.jsonl"
    filas = respuestas if respuestas is not None else respuestas_base()
    ruta_r.write_text("".join(json.dumps(f, ensure_ascii=False) + "\n" for f in filas),
                      encoding="utf-8")
    rutas = {"respuestas": ruta_r}
    for nombre, datos in (("muestra", muestra or muestra_base()),
                          ("etiquetas", etiquetas or etiquetas_base()),
                          ("protocolo", protocolo or protocolo_base())):
        ruta = tmp_path / f"{nombre}.json"
        ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")
        rutas[nombre] = ruta
    return rutas


def correr(runner, tmp_path, **kwargs) -> dict:
    r = insumos(tmp_path, **kwargs)
    return runner.report(respuestas=r["respuestas"], etiquetas=r["etiquetas"],
                         muestra=r["muestra"], protocolo=r["protocolo"], fecha="2026-10-09")


def coste_de(informe: dict, brazo: str) -> dict:
    return informe["por_brazo"][brazo]["contabilidad"]["coste"]


@pytest.fixture
def runner_fresco():
    """Modulo recargado por test: los mutantes apagan un simbolo y no pueden compartir instancia
    con los que leen el arbol versionado (leccion del conftest de la seleccion hermana)."""
    spec = importlib.util.spec_from_file_location("evaluate_jev_pilot_mutante", RUNNER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ----------------------------------------------------------------------------------------------
# B2-1c: la comparacion contra los techos congelados
# ----------------------------------------------------------------------------------------------

def test_el_exceso_de_jev_sobre_el_techo_se_publica_con_su_magnitud(runner, tmp_path):
    """B2-1c: 145 medido contra 139 congelado es EXCESO de 6, y la fila va nombrada."""
    coste = coste_de(correr(runner, tmp_path), "jev")
    out = coste["contra_techos"]["output"]
    assert out["techo_congelado"] == 139 and out["clave_del_techo"] == "tokens_out"
    assert out["veredicto"] == "EXCESO"
    assert out["medido_maximo_por_llamada"] == 145, "el maximo por llamada, no la suma"
    assert out["exceso_sobre_el_techo"] == 6, "145 - 139"
    assert out["filas_fuera_del_techo"] == ["A::L-A"]


def test_la_unidad_de_comparacion_es_la_que_congelo_el_protocolo(runner, tmp_path):
    """La columna declara por que se compara el maximo y no la suma: el techo se escribio por llamada."""
    coste = coste_de(correr(runner, tmp_path), "jev")
    assert coste["unidad_de_comparacion"].startswith("maximo observado por llamada")
    assert "limites_gasto.motivo" in coste["unidad_de_comparacion"]


def test_un_valor_igual_al_techo_no_es_exceso(runner, tmp_path):
    """Frontera: 139 contra 139 es DENTRO. El mutante `>=` en lugar de `>` pierde este verde."""
    filas = [fila("jev", "A::L-A", "L-A", usage=uso(100, 139))]
    out = coste_de(correr(runner, tmp_path, respuestas=filas), "jev")["contra_techos"]["output"]
    assert out["veredicto"] == "DENTRO"
    assert out["exceso_sobre_el_techo"] is None
    assert out["margen_restante_bajo_el_techo"] == 0, "dentro con margen cero, no con exceso cero"


def test_el_margen_restante_no_es_un_exceso_negativo(runner, tmp_path):
    """DENTRO publica margen (139-130=9) y exceso None; un -9 en `exceso_sobre_el_techo` mentiría."""
    out = coste_de(correr(runner, tmp_path), "deepseek")["contra_techos"]["output"]
    assert out["veredicto"] == "DENTRO"
    assert out["exceso_sobre_el_techo"] is None
    assert out["margen_restante_bajo_el_techo"] == 9, "139 - 130"
    assert coste_de(correr(runner, tmp_path), "deepseek")["contra_techos"]["input"][
        "margen_restante_bajo_el_techo"] == 780, "1834 - 1054"


def test_un_brazo_dentro_no_arrastra_al_que_excede(runner, tmp_path):
    """La comparacion es por brazo: deepseek DENTRO y jev EXCESO en el mismo informe."""
    informe = correr(runner, tmp_path)
    assert coste_de(informe, "jev")["veredicto_exceso"] == "EXCESO"
    assert coste_de(informe, "deepseek")["veredicto_exceso"] == "DENTRO"
    assert coste_de(informe, "jev")["contra_techos"]["input"]["veredicto"] == "DENTRO", \
        "jev pasa los 6 de salida y sigue dentro de los 1834 de entrada"


def test_techo_null_es_NO_EVALUABLE_y_nunca_DENTRO(runner, tmp_path):
    """El falso verde que la casa prohíbe: techo ausente no es aprobación. Mutante: invertir el None."""
    informe = correr(runner, tmp_path, protocolo=protocolo_base(tokens_out=None))
    out = coste_de(informe, "jev")["contra_techos"]["output"]
    assert out["veredicto"] == "NO-EVALUABLE"
    assert out["techo_congelado"] is None
    assert "es null" in out["motivo"]
    assert coste_de(informe, "jev")["veredicto_exceso"] == "NO-EVALUABLE"


def test_la_capa_fria_sin_envios_es_NO_EVALUABLE_no_cero(runner, tmp_path):
    """C1 no hizo envio y no deja medida: la columna se abstiene, no aprueba el techo."""
    out = coste_de(correr(runner, tmp_path), "capa_fria")["contra_techos"]["output"]
    assert out["veredicto"] == "NO-EVALUABLE"
    assert out["medido_maximo_por_llamada"] is None
    assert "ningun envio dejo medida" in out["motivo"]


def test_las_filas_sin_medida_se_cuentan_por_estado_no_como_cero(runner, tmp_path):
    """AC10: D2 hizo un envio sin usage. Entra al conteo de ausencia y no suma como 0 tokens."""
    coste = coste_de(correr(runner, tmp_path), "deepseek")
    assert coste["filas"] == 2
    assert coste["tokens"]["output"]["n_observaciones"] == 1
    assert coste["tokens"]["output"]["n_filas_con_envio"] == 1
    assert coste["tokens"]["output"]["filas_sin_medida_por_estado"] == {"sin_usage": 1}
    assert coste["tokens"]["output"]["suma"] == 130, "la suma es de lo observado, no de las filas"


def test_el_veredicto_global_manda_sobre_la_abstencion_parcial(runner, tmp_path):
    """Con un campo EXCESO y otro NO-EVALUABLE el brazo no se declara NO-EVALUABLE: el rojo manda."""
    informe = correr(runner, tmp_path, protocolo=protocolo_base(tokens_in=None))
    assert coste_de(informe, "jev")["contra_techos"]["input"]["veredicto"] == "NO-EVALUABLE"
    assert coste_de(informe, "jev")["veredicto_exceso"] == "EXCESO"


# ----------------------------------------------------------------------------------------------
# B2-1: las tres columnas separadas (tokens / coste calculado / cargo facturado)
# ----------------------------------------------------------------------------------------------

def test_cost_calculated_sin_tarifa_es_NO_EVALUABLE_y_nombrar_su_causa(runner, tmp_path):
    """AC4 con la columna presente y nula por causa: no hay tarifa en el protocolo ni en el registro."""
    coste = coste_de(correr(runner, tmp_path), "jev")["cost_calculated"]
    assert coste["estado"] == "NO-EVALUABLE"
    assert coste["usd"] is None
    assert coste["tarifa_por_mtok"] == {"input": None, "output": None}
    assert "precios_por_mtok" in coste["motivo"] and "provider_registry" in coste["motivo"]


def test_cost_calculated_con_tarifa_casa_con_el_calculo_a_mano(runner, tmp_path):
    """1788/1e6*0.30 + 150/1e6*2.50 = 0.0005364 + 0.000375 = 0.0009114."""
    protocolo = protocolo_base(precios_por_mtok={"input": 0.30, "output": 2.50})
    coste = coste_de(correr(runner, tmp_path, protocolo=protocolo), "jev")["cost_calculated"]
    assert coste["estado"] == "CALCULADO"
    assert coste["usd"] == pytest.approx(0.0009114, abs=1e-9)
    assert coste["base"] == {"suma_input": 1788, "suma_output": 150}


def test_tarifa_declarada_sin_medida_no_da_un_cero_como_coste(runner, tmp_path):
    """El mutante `or 0` sobre sumas vacias: con tarifa y sin observacion la columna se abstiene."""
    protocolo = protocolo_base(precios_por_mtok={"input": 0.30, "output": 2.50})
    filas = [fila("capa_fria", "A::L-A", "L-A", usage=uso(None, None, "no_intentada"))]
    coste = coste_de(correr(runner, tmp_path, respuestas=filas,
                            protocolo=protocolo), "capa_fria")["cost_calculated"]
    assert coste["estado"] == "NO-EVALUABLE"
    assert coste["usd"] is None
    assert "suma vacia" in coste["motivo"]


def test_cost_billed_sin_observacion_es_NO_OBSERVADO_nunca_cero(runner, tmp_path):
    """El cargo lo dice el proveedor: sin registro persistido la columna se declara no observada."""
    coste = coste_de(correr(runner, tmp_path), "jev")["cost_billed"]
    assert coste["estado"] == "NO-OBSERVADO"
    assert coste["usd"] is None
    assert coste["n_filas_con_cargo"] == 0
    assert "en vez de 0" in coste["motivo"]


def test_cost_billed_suma_las_filas_que_traen_cargo(runner, tmp_path):
    """0.001 + 0.002 = 0.003, y cuenta solo las filas que lo trajeron."""
    filas = [fila("jev", "A::L-A", "L-A", usage=uso(10, 5), cargo_facturado=0.001),
             fila("jev", "B::L-B", "L-B", usage=uso(10, 5), cargo_facturado=0.002),
             fila("jev", "A::L-A", "L-A", usage=uso(10, 5))]
    coste = coste_de(correr(runner, tmp_path, respuestas=filas), "jev")["cost_billed"]
    assert coste["estado"] == "OBSERVADO"
    assert coste["usd"] == pytest.approx(0.003, abs=1e-9)
    assert coste["n_filas_con_cargo"] == 2


def test_las_tres_columnas_viven_juntas_y_separadas_en_el_informe(runner, tmp_path):
    """AC4: tokens observados, coste calculado y cargo facturado salen en el mismo bloque, sin fusionarse."""
    coste = coste_de(correr(runner, tmp_path), "jev")
    assert {"tokens", "cost_calculated", "cost_billed", "contra_techos", "veredicto_exceso"} <= set(coste)
    assert coste["tokens"]["input"]["suma"] == 1788
    assert coste["tokens"]["input"]["maximo_por_llamada"] == 1778, "suma y maximo no son lo mismo"
    assert coste["cost_calculated"]["usd"] is None


# ----------------------------------------------------------------------------------------------
# la senal mecanica y su control negativo
# ----------------------------------------------------------------------------------------------

def test_s6_sale_solo_con_exceso_y_nombra_techo_medido_y_fila(runner, tmp_path):
    """El informe dice el exceso sin interpretar el protocolo: techo, medido y fila en la base."""
    informe = correr(runner, tmp_path)
    s6 = [s for s in informe["senales_mecanicas"] if s["id"] == "S6"]
    assert len(s6) == 1, "solo jev excede, asi que una senal y no dos"
    base = s6[0]["base"]["excedido_por"][0]
    assert base == {"campo": "output", "techo": 139, "medido": 145, "exceso": 6,
                    "filas": ["A::L-A"]}


def test_s6_no_aparece_cuando_todo_esta_dentro(runner, tmp_path):
    """Control negativo de la senal: sin exceso no hay S6 que leer."""
    filas = [fila("jev", "A::L-A", "L-A", usage=uso(100, 100))]
    informe = correr(runner, tmp_path, respuestas=filas)
    assert not [s for s in informe["senales_mecanicas"] if s["id"] == "S6"]


def test_el_exceso_no_le_da_veredicto_al_modelo(runner, tmp_path):
    """AC5: la contabilidad se publica; `decide` sigue negandose a elegir. Sin este diente el exceso
    podria convertirse en un FALLIDO o en un RECHAZAR por via de la senal."""
    runner_ = runner
    informe = correr(runner_, tmp_path)
    protocolo = json.loads((tmp_path / "protocolo.json").read_text(encoding="utf-8"))
    decision = runner_.decide(informe=informe, protocolo=protocolo, fecha="2026-10-09")
    assert decision["decision"] is None
    assert decision["run_status"] in ("COMPLETO", "INCOMPLETO")
    assert coste_de(informe, "jev")["veredicto_exceso"] == "EXCESO"


def test_dos_corridas_con_el_bloque_de_coste_siguen_dando_bytes_identicos(runner, tmp_path):
    """AC4 pide regenerable: las claves nuevas no introducen orden inestable.

    Las dos corridas van sobre los MISMOS archivos: los insumos llevan su ruta al informe, asi que
    copiarlos a otro directorio compararia rutas y no determinismo.
    """
    r = insumos(tmp_path)
    correr_de = lambda: runner.report(respuestas=r["respuestas"], etiquetas=r["etiquetas"],
                                      muestra=r["muestra"], protocolo=r["protocolo"],
                                      fecha="2026-10-09")
    sin_fecha = lambda d: json.dumps({k: v for k, v in d.items() if k != "fecha"}, sort_keys=False)
    a, b = correr_de(), correr_de()
    assert sin_fecha(a) == sin_fecha(b)
    assert coste_de(a, "jev")["contra_techos"] == coste_de(b, "jev")["contra_techos"]


# ----------------------------------------------------------------------------------------------
# ancla al arbol versionado: el crudo de FASE-C, solo lectura
# ----------------------------------------------------------------------------------------------

def test_sobre_los_registros_versionados_de_C_los_dos_brazos_excedieron_el_techo(runner):
    """B2-1c medido sobre el artefacto real. La deuda publicaba 145 (+6) y el brazo comparador
    tambien paso el techo: 158 (+19). Ningun instrumento lo decia."""
    informe = runner.report(respuestas=RESPUESTAS_C, etiquetas=ETIQUETAS_C, muestra=MUESTRA_C,
                            protocolo=PROTOCOLO_C, fecha="2026-10-09")
    jev = coste_de(informe, "jev")["contra_techos"]["output"]
    assert (jev["medido_maximo_por_llamada"], jev["exceso_sobre_el_techo"]) == (145, 6)
    ds = coste_de(informe, "deepseek")["contra_techos"]["output"]
    assert (ds["medido_maximo_por_llamada"], ds["exceso_sobre_el_techo"]) == (158, 19)
    assert coste_de(informe, "capa_fria")["veredicto_exceso"] == "NO-EVALUABLE"


def test_sobre_C_la_contabilidad_de_coste_queda_publicada_sin_cero_favorable(runner):
    """El informe real de C: tarifa ausente, cargo no observado, y la capa fria contada por estado."""
    informe = runner.report(respuestas=RESPUESTAS_C, etiquetas=ETIQUETAS_C, muestra=MUESTRA_C,
                            protocolo=PROTOCOLO_C, fecha="2026-10-09")
    jev = coste_de(informe, "jev")
    assert jev["cost_calculated"] == {"usd": None, "estado": "NO-EVALUABLE",
                                      "tarifa_por_mtok": {"input": None, "output": None},
                                      "motivo": jev["cost_calculated"]["motivo"]}
    assert jev["cost_calculated"]["estado"] == "NO-EVALUABLE"
    assert jev["cost_billed"]["estado"] == "NO-OBSERVADO"
    assert jev["tokens"]["input"]["n_observaciones"] == 1, "un envio de jev dejo medida"


def test_sobre_C_decide_sigue_emitiendo_decision_null(runner):
    """La re-emision de C no se movio: la cura anade contabilidad y no re-abre la decision."""
    informe = runner.report(respuestas=RESPUESTAS_C, etiquetas=ETIQUETAS_C, muestra=MUESTRA_C,
                            protocolo=PROTOCOLO_C, fecha="2026-10-09")
    protocolo = json.loads(PROTOCOLO_C.read_text(encoding="utf-8"))
    decision = runner.decide(informe=informe, protocolo=protocolo, fecha="2026-10-09")
    assert decision["decision"] is None
    assert decision["run_status"] == "INCOMPLETO"


# ----------------------------------------------------------------------------------------------
# contrafactual de instrumento: el verde tiene que poder perder
# ----------------------------------------------------------------------------------------------

def test_apagar_la_comparacion_contra_el_techo_pierde_el_diente(runner_fresco, tmp_path):
    """Mutante M1: `_entero_o_none` devuelve None para los techos y la comparacion se abstiene.

    Sin el rojo ejecutado, la bateria del exceso seria un verde por vacio (L-R.3).
    """
    original = runner_fresco._entero_o_none
    runner_fresco._entero_o_none = lambda valor: None
    try:
        informe = correr(runner_fresco, tmp_path)
        assert coste_de(informe, "jev")["contra_techos"]["output"]["veredicto"] == "NO-EVALUABLE"
        assert not [s for s in informe["senales_mecanicas"] if s["id"] == "S6"]
    finally:
        runner_fresco._entero_o_none = original
    restaurado = coste_de(correr(runner_fresco, tmp_path / "post"), "jev")["contra_techos"]["output"]
    assert restaurado["veredicto"] == "EXCESO", "la restauracion va verificada, no asumida"


def test_contar_las_filas_sin_medida_como_cero_pierde_el_diente(runner_fresco, tmp_path):
    """Mutante M2: `ESTADOS_USAGE_OBSERVADOS` tragandose `sin_usage` borra la ausencia del informe.

    El diente que cae es `test_las_filas_sin_medida_se_cuentan_por_estado_no_como_cero`: con el
    mutante la fila sin medida desaparece de `filas_sin_medida_por_estado` y pasa a contar como
    fila con envio, que es exactamente el cero favorable que AC10 prohíbe.
    """
    originales = copy.copy(runner_fresco.ESTADOS_USAGE_OBSERVADOS)
    runner_fresco.ESTADOS_USAGE_OBSERVADOS = ("observado", "parcial", "sin_usage", "no_intentada")
    try:
        tokens = coste_de(correr(runner_fresco, tmp_path), "deepseek")["tokens"]["output"]
        assert tokens["n_filas_con_envio"] == 2, "el mutante cuenta la fila sin medida como medida"
        assert tokens["filas_sin_medida_por_estado"] == {}, "y la ausencia deja de publicarse"
    finally:
        runner_fresco.ESTADOS_USAGE_OBSERVADOS = originales
    restaurado = coste_de(correr(runner_fresco, tmp_path / "post"), "deepseek")["tokens"]["output"]
    assert restaurado["filas_sin_medida_por_estado"] == {"sin_usage": 1}
    assert restaurado["n_filas_con_envio"] == 1, "la restauracion va verificada, no asumida"
