# -*- coding: utf-8 -*-
"""Dientes de `report` y `decide` (SESION 3.5 / FASE-B.2, 2026-10-04).

Cierran CR-1 y CR-2: los cuatro cocientes del maestro (:88-91) construidos desde registros
persistidos, con denominadores separados y con el extremo a extremo como instrumento testado. Todo
aqui es offline: los insumos son `respuestas.jsonl` + `etiquetas.json` + `muestra.json` +
`protocolo.json` sinteticos, el guard de sockets del conftest esta armado por fixture autouse, y la
via del SDK se ejercita con una puerta falsa (cero credenciales leidas).

Cada diente lleva su mutante o su control negativo con la caida nombrada (L-V2.1): un verde que no
pudo perder no prueba nada (L-R.3). Los mutantes van sobre el modulo cargado o sobre una copia del
insumo en `tmp_path`; el arbol de trabajo no se toca.

La poblacion base esta calculada a mano, y el calculo va escrito junto a la asercion:

| par | split | etiqueta      | importancia | target en candidatos | brazo jev     | brazo deepseek      |
|-----|-------|---------------|-------------|----------------------|---------------|---------------------|
| A   | eval  | pertinente    | alta        | si                   | elige L-A ok  | abstencion          |
| B   | eval  | pertinente    | media       | no                   | elige L-Z mal | fallo (conexion)    |
| C   | dev   | pertinente    | alta        | (no se despacho)     | sin fila      | sin fila            |
| D   | dev   | no_pertinente | null        | (no elegible)        | sin fila      | sin fila            |

Conjunto importante elegible = {A, B, C} (3); pertinentes 3 sobre 4 pares -> suficiencia 3/4 = 0.75.
jev: recuperacion 1/2 (C no medido), precision 1/2, recall 1/1, e2e 1/2.
deepseek: recuperacion 1/2, precision 0/0 NO-EVALUABLE, recall 0/1, e2e 0/2, abstencion 1/1.
"""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
EVID = REPO_ROOT / "evidence" / "EVALUACION-JEV-TYPESAFE-2026-09-21"
RESPUESTAS_C = EVID / "FASE-C" / "respuestas.jsonl"
INFORME_C = EVID / "FASE-C" / "informe_comparativa.json"
PROTOCOLO_C = EVID / "protocolo.json"
COCIENTES = ("recuperacion", "precision_entre_propuestas", "recall_importante_candidatos",
             "extremo_a_extremo")


# ----------------------------------------------------------------------------------------------
# insumos sinteticos
# ----------------------------------------------------------------------------------------------

def _par(pid: str, lesson: str, split: str) -> dict:
    return {"pair_id": pid, "target_plan": pid.split("::")[0], "target_phase": "FASE-B",
            "lesson_id": lesson, "input_fragment": f"fragmento de {pid}",
            "original_sha256": "0" * 64, "sanitized_sha256": "0" * 64, "split": split}


def muestra_base() -> dict:
    pares = [_par("A::L-A", "L-A", "eval"), _par("B::L-B", "L-B", "eval"),
             _par("C::L-C", "L-C", "dev"), _par("D::L-D", "L-D", "dev")]
    return {"schema": "jev-pilot-muestra/v1", "status": "CONGELADA",
            "corpus_source": "synthetic", "temporal_cut": "2026-09-12",
            "review": {"human_reviewed": True, "reviewer": "jhon", "reviewed_at": "2026-10-02"},
            "pairs": pares, "exclusions": [],
            "counts": {"total": len(pares), "dev": 2, "eval": 2, "excluidos": 0}}


def etiquetas_base() -> dict:
    return {"schema": "jev-pilot-etiquetas/v1", "review_status": "revisada",
            "labels": [
                {"pair_id": "A::L-A", "label": "pertinente", "importance": "alta",
                 "reviewer": "jhon", "reviewed_at": "2026-10-02"},
                {"pair_id": "B::L-B", "label": "pertinente", "importance": "media",
                 "reviewer": "jhon", "reviewed_at": "2026-10-02"},
                {"pair_id": "C::L-C", "label": "pertinente", "importance": "alta",
                 "reviewer": "jhon", "reviewed_at": "2026-10-02"},
                {"pair_id": "D::L-D", "label": "no_pertinente", "importance": None,
                 "reviewer": "jhon", "reviewed_at": "2026-10-02"}]}


def protocolo_base(**criterios) -> dict:
    """Copia del protocolo congelado con los umbrales sobrescribibles.

    Los protocolos sinteticos provocan las reglas de `decide`; no re-leen los criterios del
    versionado, que esta CONGELADA y sus umbrales se aplican y no se interpretan.
    """
    adopcion = {"cobertura_min": 0.95, "margen_vs_deepseek": 0.25,
                "tratamiento_abstenciones": "contadas como fallo de recuperacion, no como "
                                            "insuficiente; publicadas en denominador aparte",
                "suficiencia_minima": 0.5, "latencia_max": 30000,
                "revision_humana": "obligatoria; designado: jhon (2026-10-02)"}
    adopcion.update(criterios)
    return {"schema": "jev-pilot-protocolo/v1", "status": "CONGELADA",
            "congelado": {"revisado_por": "jhon", "fecha": "2026-10-04"},
            "reglas_recuperacion": "top-8 por consulta fria, mismo conjunto elegible",
            "rubrica": {"valores": ["pertinente", "no_pertinente", "insuficiente"],
                        "importancia": ["alta", "media", "baja"]},
            "modelos": {"jev_pin": "jev-1.13.0", "comparador": "DeepSeek", "excluido": "Anthropic"},
            "parametros": {"retry_policy": {"max_retries": 0}, "timeout_s": 30},
            "limites_gasto": {"usd": None, "llamadas": 12, "tokens_in": 1834, "tokens_out": 139,
                              "motivo": "fuera de gobernanza por decision del operador"},
            "criterios_adopcion": adopcion}


def fila(brazo: str, pid: str, lesson: str, *, propuesta, candidatos, en_candidatos: bool,
         error_kind=None, attempts=1, intentos=None, usage=None) -> dict:
    return {"pair_id": pid, "split": "eval" if pid[0] in ("A", "B") else "dev",
            "lesson_id_target": lesson, "etiqueta": "pertinente", "importancia": "alta",
            "candidatos_frios": candidatos, "leccion_target_en_candidatos": en_candidatos,
            "brazo": brazo, "modelo_pedido": "jev-1.13.0" if brazo == "jev" else "deepseek-chat",
            "modelo_efectivo": None, "propuesta": propuesta,
            "abstencion": (None if propuesta is None or isinstance(propuesta, list)
                           else propuesta == "ninguna-aplica"),
            "attempts": attempts, "error_kind": error_kind,
            "duracion_ms": [i.get("duracion_ms") for i in (intentos or [])],
            "usage_normalized": usage, "request_id": None, "intentos": intentos or []}


def respuestas_base() -> list:
    cands_a = ["L-A", "L-X", "L-Y"]
    cands_b = ["L-X", "L-Y", "L-Z"]
    return [
        fila("jev", "A::L-A", "L-A", propuesta="L-A", candidatos=cands_a, en_candidatos=True,
             intentos=[{"n": 1, "resultado": "exito", "duracion_ms": 200.0}],
             usage={"input_tokens": 10, "output_tokens": 5, "total": 15, "estado": "observado"}),
        fila("jev", "B::L-B", "L-B", propuesta="L-Z", candidatos=cands_b, en_candidatos=False,
             intentos=[{"n": 1, "resultado": "exito", "duracion_ms": 300.0}],
             usage={"input_tokens": 10, "output_tokens": 5, "total": 15, "estado": "observado"}),
        fila("deepseek", "A::L-A", "L-A", propuesta="ninguna-aplica", candidatos=cands_a,
             en_candidatos=True,
             intentos=[{"n": 1, "resultado": "exito", "duracion_ms": 1000.0}],
             usage={"input_tokens": 8, "output_tokens": 4, "total": 12, "estado": "observado"}),
        fila("deepseek", "B::L-B", "L-B", propuesta=None, candidatos=cands_b, en_candidatos=False,
             error_kind="conexion",
             intentos=[{"n": 1, "resultado": "fallo", "duracion_ms": 12.0,
                        "error_kind": "conexion", "clase": "TypeSafeAPIConnectionError"}]),
    ]


def insumos(tmp_path: Path, respuestas=None, muestra=None, etiquetas=None, protocolo=None) -> dict:
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


def correr_report(runner, tmp_path, **kwargs) -> dict:
    r = insumos(tmp_path, **kwargs)
    return runner.report(respuestas=r["respuestas"], etiquetas=r["etiquetas"],
                         muestra=r["muestra"], protocolo=r["protocolo"], fecha="2026-10-04")


# ----------------------------------------------------------------------------------------------
# CR-1: los cuatro cocientes, con denominadores separados y valores conocidos
# ----------------------------------------------------------------------------------------------

def test_los_cuatro_cocientes_casan_con_el_calculo_a_mano(runner, tmp_path):
    """AC10: cada cociente contra numeros verificables por otra via."""
    informe = correr_report(runner, tmp_path)
    jev = informe["por_brazo"]["jev"]
    assert jev["precision_entre_propuestas"] == {"value": 0.5, "numerator": 1, "denominator": 2,
                                                 "motivo": ""}, jev["precision_entre_propuestas"]
    assert jev["recall_importante_candidatos"] == {"value": 1.0, "numerator": 1, "denominator": 1,
                                                  "motivo": ""}
    assert jev["extremo_a_extremo"] == {"value": 0.5, "numerator": 1, "denominator": 2,
                                        "motivo": ""}
    assert (jev["recuperacion"]["numerator"], jev["recuperacion"]["denominator"]) == (1, 2)
    assert jev["recuperacion"]["sin_medir"] == ["C::L-C"], jev["recuperacion"]["sin_medir"]
    ds = informe["por_brazo"]["deepseek"]
    assert ds["recall_importante_candidatos"] == {"value": 0.0, "numerator": 0, "denominator": 1,
                                                 "motivo": ""}, ds["recall_importante_candidatos"]
    assert ds["extremo_a_extremo"] == {"value": 0.0, "numerator": 0, "denominator": 2,
                                       "motivo": ""}


def test_los_cuatro_denominadores_no_comparten_un_denominador_unico(runner, tmp_path):
    """CR-1 en su forma: `metrics()` comparte `den` entre precision y recall y aqui no puede.

    Si el instrumento usara la envoltura de FASE-A, los dos cocientes de clasificacion saldrian con
    el mismo denominador y el recall de jev diria 1/2 en vez de 1/1.
    """
    jev = correr_report(runner, tmp_path)["por_brazo"]["jev"]
    denominadores = {k: jev[k]["denominator"] for k in COCIENTES}
    assert denominadores == {"recuperacion": 2, "precision_entre_propuestas": 2,
                             "recall_importante_candidatos": 1, "extremo_a_extremo": 2}
    assert jev["precision_entre_propuestas"]["denominator"] != \
        jev["recall_importante_candidatos"]["denominator"], \
        "precision y recall compartieron denominador: la envoltura de FASE-A no expresa AC10"


def test_mutante_acierto_siempre_falso_mueve_los_tres_cocientes_que_usan_la_regla(runner, tmp_path):
    """Mutante: `es_acierto` devuelto falso. Cae por la causa prevista y se restaura."""
    antes = correr_report(runner, tmp_path)["por_brazo"]["jev"]
    numeradores_antes = {k: antes[k]["numerator"] for k in COCIENTES}
    assert numeradores_antes == {"recuperacion": 1, "precision_entre_propuestas": 1,
                                "recall_importante_candidatos": 1, "extremo_a_extremo": 1}
    real = runner.es_acierto
    runner.es_acierto = lambda par: False
    try:
        (tmp_path / "mutante").mkdir(exist_ok=True)
        despues = correr_report(runner, tmp_path / "mutante")["por_brazo"]["jev"]
    finally:
        runner.es_acierto = real
    numeradores_despues = {k: despues[k]["numerator"] for k in COCIENTES}
    assert numeradores_despues["precision_entre_propuestas"] == 0
    assert numeradores_despues["recall_importante_candidatos"] == 0
    assert numeradores_despues["extremo_a_extremo"] == 0
    assert numeradores_despues["recuperacion"] == 1, "la recuperacion se recalculo con la regla nueva"
    assert runner.es_acierto is real, "el mutante no se restauró"
    assert runner.es_acierto({"estado_propuesta": "eleccion", "propuesta": "L-A",
                              "target": "L-A", "target_en_candidatos": True}) is True


def test_un_denominador_cero_es_no_evaluable_y_no_cien_ni_cero(runner, tmp_path):
    """Denominador cero = NO-EVALUABLE con su motivo: nunca 100 % y nunca 0 %."""
    precision = correr_report(runner, tmp_path)["por_brazo"]["deepseek"]["precision_entre_propuestas"]
    assert precision["denominator"] == 0
    assert precision["value"] is None, "un denominador cero se publico como numero"
    assert precision["motivo"] == "denominador_cero"
    assert precision["numerator"] == 0, "el numerador se relleno por la via facil"


def test_la_abstencion_vive_en_su_propio_denominador(runner, tmp_path):
    """Criterio congelado `tratamiento_abstenciones`: denominador aparte, no dentro de precision."""
    ab = correr_report(runner, tmp_path)["por_brazo"]["deepseek"]["abstenciones"]
    assert ab["abstenciones"] == 1 and ab["con_eleccion"] == 0
    assert ab["sin_eleccion_por_fallo"] == 1
    assert ab["cociente_de_abstencion"] == {"value": 1.0, "numerator": 1, "denominator": 1,
                                           "motivo": ""}, ab["cociente_de_abstencion"]


def test_mutante_abstencion_vuelta_eleccion_cambia_precision_y_el_denominador_aparte(runner,
                                                                                     tmp_path):
    """Mutante: tratar `ninguna-aplica` como eleccion. Sube precision y vacia el denominador propio."""
    real = runner.estado_de_propuesta
    runner.estado_de_propuesta = lambda f: ("eleccion" if f and f.get("propuesta")
                                            == "ninguna-aplica" else real(f))
    try:
        (tmp_path / "mutante").mkdir(exist_ok=True)
        ds = correr_report(runner, tmp_path / "mutante")["por_brazo"]["deepseek"]
    finally:
        runner.estado_de_propuesta = real
    assert ds["precision_entre_propuestas"]["denominator"] == 1, "el mutante no mordio"
    assert ds["abstenciones"]["abstenciones"] == 0
    assert ds["abstenciones"]["cociente_de_abstencion"] == {"value": 0.0, "numerator": 0,
                                                           "denominator": 1, "motivo": ""}, \
        ds["abstenciones"]["cociente_de_abstencion"]
    assert runner.estado_de_propuesta is real


def test_un_fallo_del_camino_cuenta_en_extremo_a_extremo_y_no_como_propuesta(runner, tmp_path):
    """:93 del maestro en dos mitades: el fallo no se excluye del e2e, pero tampoco es una eleccion.

    `sin_fila` (nunca despacho) y `sin_eleccion_por_fallo` (despacho y volvio vacio) son estados
    distintos; colapsarlos es la forma facil de mejorar el score excluyendo material.
    """
    ds = correr_report(runner, tmp_path)["por_brazo"]["deepseek"]
    estados = {d["pair_id"]: d["estado_propuesta"] for d in ds["por_par"]}
    assert estados == {"A::L-A": "abstencion", "B::L-B": "sin_eleccion_por_fallo",
                       "C::L-C": "sin_fila"}, estados
    assert ds["extremo_a_extremo"]["denominator"] == 2, "el fallo se excluyo del e2e"
    assert ds["precision_entre_propuestas"]["denominator"] == 0, "el fallo conto como propuesta"
    assert ds["abstenciones"]["sin_fila"] == 1
    assert ds["contabilidad"]["fallos_operativos"] == [
        {"pair_id": "B::L-B", "error_kind": "conexion", "attempts": 1}]


def test_mutante_borrar_el_error_kind_no_saca_el_par_del_extremo_a_extremo(runner, tmp_path):
    """Mutante: quitar el `error_kind`. El par sigue en el e2e y lo que se pierde es la senal S4.

    Este control existe porque la tentacion es que un fallo sin etiqueta se vuelva invisible: el
    denominador tiene que quedarse igual y el conteo de abstenciones es el que se mueve.
    """
    filas = copy.deepcopy(respuestas_base())
    for f in filas:
        if f["brazo"] == "deepseek" and f["pair_id"] == "B::L-B":
            f["error_kind"] = None
    informe = correr_report(runner, tmp_path, respuestas=filas)
    ds = informe["por_brazo"]["deepseek"]
    assert ds["extremo_a_extremo"]["denominator"] == 2, "el par se esfumo del denominador"
    assert ds["por_par"][1]["estado_propuesta"] == "sin_eleccion"
    assert ds["abstenciones"]["sin_eleccion_por_fallo"] == 0
    assert not [s for s in informe["senales_mecanicas"]
                if s["senal"].startswith("deepseek: envios")], "la senal S4 sobrevivio sin fallo"


def test_una_fila_fuera_del_conjunto_se_publica_no_se_descarta(runner, tmp_path):
    """Nada se descarta en silencio: una fila de un par no elegible se cuenta y se nombra."""
    filas = respuestas_base() + [fila("jev", "D::L-D", "L-D", propuesta="L-D",
                                      candidatos=["L-D"], en_candidatos=True,
                                      intentos=[{"n": 1, "resultado": "exito",
                                                 "duracion_ms": 90.0}])]
    jev = correr_report(runner, tmp_path, respuestas=filas)["por_brazo"]["jev"]
    assert jev["contabilidad"]["fuera_del_conjunto_elegible"] == ["D::L-D"]
    assert jev["precision_entre_propuestas"]["denominator"] == 2, (
        "la fila fuera de conjunto se comio el denominador")


def test_la_recuperacion_la_pone_la_funcion_testada_no_un_contador_nuevo(runner, tmp_path):
    """El informe usa `recuperacion_medida`: la pata ya probada en FASE-B se conserva."""
    llamado = []
    real = runner.recuperacion_medida
    runner.recuperacion_medida = lambda *a, **k: llamado.append(1) or real(*a, **k)
    try:
        informe = correr_report(runner, tmp_path)
    finally:
        runner.recuperacion_medida = real
    assert len(llamado) == 2, llamado
    assert runner.recuperacion_medida is real
    assert set(informe["por_brazo"]["jev"]["recuperacion"]) >= {"presentes", "elegibles",
                                                                "medidos", "sin_medir"}


def test_un_ranking_no_es_una_eleccion_pero_si_entrega_extremo_a_extremo(runner, tmp_path):
    """capa_fria: precision NO-EVALUABLE (no elige) y la convencion de acierto es una sola.

    A y C tienen su target entre los candidatos, B no: recall 2/2 y e2e 2/3 por la misma regla.
    """
    filas = [fila("capa_fria", "A::L-A", "L-A", propuesta=["L-A", "L-X"], candidatos=["L-A", "L-X"],
                  en_candidatos=True),
             fila("capa_fria", "B::L-B", "L-B", propuesta=["L-X", "L-Z"], candidatos=["L-X", "L-Z"],
                  en_candidatos=False),
             fila("capa_fria", "C::L-C", "L-C", propuesta=["L-C"], candidatos=["L-C"],
                  en_candidatos=True)]
    for f in filas:
        f["attempts"] = 0
    fria = correr_report(runner, tmp_path, respuestas=filas)["por_brazo"]["capa_fria"]
    assert fria["precision_entre_propuestas"]["motivo"] == "denominador_cero"
    assert (fria["recall_importante_candidatos"]["numerator"],
            fria["recall_importante_candidatos"]["denominator"]) == (2, 2)
    assert (fria["extremo_a_extremo"]["numerator"],
            fria["extremo_a_extremo"]["denominator"]) == (2, 3)
    assert fria["lectura"]["capa_fria_es_un_ranking"] is True
    assert [s for s in correr_report(runner, tmp_path / "s5", respuestas=filas)
            ["senales_mecanicas"] if s["id"] == "S5"]


# ----------------------------------------------------------------------------------------------
# `report` como emisor: proveniencia, insumos, determinismo y cero red
# ----------------------------------------------------------------------------------------------

def test_el_informe_declara_regenerabilidad_y_sha_de_los_insumos(runner, tmp_path):
    """AC4: el informe es regenerable desde registros y declara su procedencia."""
    informe = correr_report(runner, tmp_path)
    assert informe["schema"] == "jev-pilot-informe-comparativa/v1"
    assert informe["generado_sin_red"] is True
    assert informe["instrumento"] == "scripts/evaluate_jev_pilot.py report"
    assert set(informe["sha256_de_los_insumos"]) == {"respuestas", "etiquetas", "muestra",
                                                     "protocolo"}
    assert all(len(v) == 64 for v in informe["sha256_de_los_insumos"].values())
    assert informe["conjunto_elegible"]["importantes_elegibles"] == ["A::L-A", "B::L-B", "C::L-C"]
    assert informe["conjunto_elegible"]["brazos_en_registros"] == ["jev", "deepseek"]


def test_dos_corridas_de_report_y_decide_dan_bytes_identicos(runner, tmp_path):
    """El atributo verificable del cierre: mismo insumo, mismos bytes; y eso es todo."""
    r = insumos(tmp_path)
    correr = lambda: runner.report(respuestas=r["respuestas"], etiquetas=r["etiquetas"],
                                   muestra=r["muestra"], protocolo=r["protocolo"],
                                   fecha="2026-10-04")
    a, b = correr(), correr()
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    protocolo = json.loads(r["protocolo"].read_text(encoding="utf-8"))
    d1 = runner.decide(informe=a, protocolo=protocolo, fecha="2026-10-04")
    d2 = runner.decide(informe=b, protocolo=protocolo, fecha="2026-10-04")
    assert json.dumps(d1, sort_keys=True) == json.dumps(d2, sort_keys=True)
    assert json.dumps(runner.decision_markdown(d1, b), ensure_ascii=False) \
        == json.dumps(runner.decision_markdown(d2, a), ensure_ascii=False)
    otra = runner.decide(informe=b, protocolo=protocolo, fecha="2026-10-05")
    sin_fecha = lambda d: json.dumps({k: v for k, v in d.items() if k != "fecha"}, sort_keys=True)
    assert sin_fecha(otra) == sin_fecha(d2), "solo la fecha debio moverse"


def test_sin_insumos_report_y_decide_se_niegan_con_exit_2_y_causa(runner, capsys):
    """El EXIT nombrado y la causa escrita: emitir sin registros seria rellenar a mano (AC10)."""
    assert runner.main(["report"]) == 2
    assert runner.main(["decide"]) == 2
    err = capsys.readouterr().err
    assert "report exige" in err and "respuestas" in err
    assert "decide exige" in err and "informe" in err
    assert "no abre red" in err


def test_los_dos_modos_estan_registrados_en_el_parser(runner):
    """CR-2/CR-3 se miden en el parser: `report` era `invalid choice`, `decide` un stub y `run` no
    exponia `--etiquetas` (H5 de FASE-C). El crudo de FASE-C `09-negacion-de-report-y-decide.txt`
    registra los cinco modos de entonces.
    """
    acciones = [a for a in runner.build_parser()._actions if a.dest == "mode"]
    sub = acciones[0]
    modos = set(sub.choices)
    assert {"prepare", "check", "run", "report", "decide", "protocolo-check"} <= modos, modos
    ayudas = {a.dest: (a.help or "") for a in sub._choices_actions}
    assert ayudas["decide"] and "no disponible" not in ayudas["decide"], ayudas
    opciones = {nombre: [opt for accion in sub.choices[nombre]._actions
                         for opt in accion.option_strings] for nombre in ("run", "report", "decide")}
    assert "--etiquetas" in opciones["run"], opciones["run"]
    assert {"--respuestas", "--etiquetas", "--muestra", "--protocolo", "--out"} <= \
        set(opciones["report"]), opciones["report"]
    assert {"--informe", "--protocolo", "--out-dir"} <= set(opciones["decide"]), opciones["decide"]


def test_report_sin_un_insumo_en_disco_se_niega_con_exit_1(runner, tmp_path, capsys):
    """Un insumo declarado pero ausente no es un informe vacio: se niega y nombra la ruta."""
    r = insumos(tmp_path)
    assert runner.main(["report", "--respuestas", str(tmp_path / "no-existe.jsonl"),
                        "--etiquetas", str(r["etiquetas"]), "--muestra", str(r["muestra"]),
                        "--protocolo", str(r["protocolo"])]) == 1
    assert "no encuentra insumos" in capsys.readouterr().err


def test_decide_rechaza_un_informe_que_no_produjo_report(runner, tmp_path, capsys):
    """El insumo de `decide` es un informe del instrumento, no cualquier json con el schema viejo.

    Control negativo ejercitado sobre el artefacto versionado: el informe de FASE-C lo escribio un
    arnes de la sesion, no el runner, y por eso no trae `criterios`.
    """
    assert INFORME_C.exists(), "el antecedente versionado desaparecio del arbol"
    informe_c = json.loads(INFORME_C.read_text(encoding="utf-8"))
    assert "criterios" not in informe_c
    assert informe_c["schema"] == "jev-pilot-informe-comparativa/v1"
    r = insumos(tmp_path)
    ruta = tmp_path / "informe_de_arnes.json"
    ruta.write_text(json.dumps(informe_c), encoding="utf-8")
    assert runner.main(["decide", "--informe", str(ruta), "--protocolo",
                        str(r["protocolo"])]) == 1
    err = capsys.readouterr().err
    assert "producido por `report`" in err and "criterios" in err


def test_report_y_decide_no_importan_el_sdk_ni_abren_red(runner, tmp_path, monkeypatch):
    """AC6/AC11 sobre el camino nuevo, con el guard del conftest armado y el import vigilado."""
    import builtins
    real_import = builtins.__import__
    intentos = []

    def guarded(name, *args, **kwargs):
        root = name.split(".")[0]
        if name in runner.FORBIDDEN_MODULES or root in runner.FORBIDDEN_MODULES:
            intentos.append(name)
            raise AssertionError(f"intento de importar cliente/red: {name}")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded)
    r = insumos(tmp_path)
    assert runner.main(["report", "--respuestas", str(r["respuestas"]), "--etiquetas",
                        str(r["etiquetas"]), "--muestra", str(r["muestra"]), "--protocolo",
                        str(r["protocolo"]), "--out", str(tmp_path / "informe.json")]) == 0
    assert runner.main(["decide", "--informe", str(tmp_path / "informe.json"), "--protocolo",
                        str(r["protocolo"]), "--out-dir", str(tmp_path / "d")]) == 3
    assert intentos == [], intentos
    assert (tmp_path / "informe.json").exists()
    assert (tmp_path / "d" / "decision.json").exists()
    assert (tmp_path / "d" / "decision.md").exists()


# ----------------------------------------------------------------------------------------------
# CR-2: `decide` aplica la regla congelada y las reglas de run_status del maestro (:101)
# ----------------------------------------------------------------------------------------------

def test_decide_sobre_los_registros_reales_reproduce_el_estado_de_la_corrida_de_C(runner):
    """El emisor nuevo no contradice el registro: run_status, decision y las cuatro etiquetas.

    Los insumos son los de una corrida cerrada: se leen, no se editan. Si el instrumento dijera
    otra cosa de lo que la sesion 3 estampo, el rojo es del emisor o del registro.
    """
    assert RESPUESTAS_C.exists() and PROTOCOLO_C.exists()
    informe = runner.report(respuestas=RESPUESTAS_C, etiquetas=EVID / "etiquetas.json",
                            muestra=EVID / "muestra.json", protocolo=PROTOCOLO_C,
                            fecha="2026-10-04")
    decision = runner.decide(informe=informe,
                             protocolo=json.loads(PROTOCOLO_C.read_text(encoding="utf-8")),
                             fecha="2026-10-04")
    assert decision["run_status"] == "INCOMPLETO", decision["run_status"]
    assert decision["decision"] is None
    assert decision["schema"] == "jev-pilot-decision/v1"
    literales = decision["literales_y_su_estado"]
    assert literales["ACTIVAR"]["estado"].startswith("EXCLUIDA")
    assert "0.95" in literales["ACTIVAR"]["base"]
    assert literales["RECHAZAR"]["estado"] == "NO EMITIDA"
    assert literales["COSTE-NO-PAGADO"]["estado"] == "BLOQUEADO"
    assert literales["MUESTRA-INSUFICIENTE"]["estado"] == \
        "EXCLUIDA por la regla congelada; ponible por el operador"
    assert literales["MUESTRA-INSUFICIENTE"]["base"].count("1 par") == 1
    margen = decision["criterios_congelados"]["margen_vs_deepseek"]
    assert margen["estado"] == "NO-EVALUABLE"
    assert margen["diferencia_calculada"] == 0.0
    assert margen["denominador_efectivo_de_la_comparacion"] == 1
    assert decision["transfer_status"] == "PENDIENTE"
    assert decision["d6_eligibility"]["valor"].startswith("NO ELEGIBLE")


def test_report_casa_con_los_dos_cocientes_que_la_corrida_midio(runner):
    """Prueba de que el instrumento y la corrida hablan el mismo idioma (mandato §5)."""
    informe = runner.report(respuestas=RESPUESTAS_C, etiquetas=EVID / "etiquetas.json",
                            muestra=EVID / "muestra.json", protocolo=PROTOCOLO_C,
                            fecha="2026-10-04")
    for brazo in ("capa_fria", "jev", "deepseek"):
        rec = informe["por_brazo"][brazo]["recuperacion"]
        assert (rec["numerator"], rec["denominator"], rec["value"]) == (1, 2, 0.5), (brazo, rec)
    lat = informe["por_brazo"]["jev"]["latencia"]
    assert lat["max_latencia_ms"] == 395.794
    assert lat["latencias_ms_de_respuesta"] == [395.794]
    assert lat["duracion_ms_de_fallos"] == [48.478], (
        "la duracion del intento que fallo por conexion se conto como latencia de respuesta")
    assert informe["criterios"]["latencia_max"]["estado"] == "CUMPLE"
    assert informe["criterios"]["suficiencia_minima"]["medido"]["value"] == 0.5
    assert informe["protocolo"]["status"] == "CONGELADA"


def test_un_fallo_operativo_de_autenticacion_es_FALLIDO_y_nunca_RECHAZAR(runner, tmp_path):
    """AC5: `run_status=FALLIDO`, `decision=null`, y el literal de rechazo no se emite."""
    filas = copy.deepcopy(respuestas_base())
    for f in filas:
        if f["brazo"] == "jev":
            f["error_kind"], f["propuesta"] = "auth", None
    informe = correr_report(runner, tmp_path, respuestas=filas)
    decision = runner.decide(informe=informe, protocolo=protocolo_base(), fecha="2026-10-04")
    assert decision["run_status"] == "FALLIDO"
    assert decision["decision"] is None
    assert decision["literales_y_su_estado"]["RECHAZAR"]["estado"] == "NO EMITIDA"
    assert any("el fallo se corrige" in m for m in decision["motivo_decision_null"]), \
        decision["motivo_decision_null"]


def test_la_contabilidad_rota_tambien_es_FALLIDO_aunque_el_transporta_responda(runner, tmp_path):
    """AC8 como asercion: `attempts` mayor que 1 con max_retries=0 son envios fuera del ledger."""
    filas = copy.deepcopy(respuestas_base())
    for f in filas:
        if f["brazo"] == "jev" and f["pair_id"] == "A::L-A":
            f["attempts"] = 3
            f["intentos"] = [{"n": n, "resultado": "exito", "duracion_ms": 100.0}
                             for n in (1, 2, 3)]
    informe = correr_report(runner, tmp_path, respuestas=filas)
    assert informe["por_brazo"]["jev"]["contabilidad"]["fallos_de_contabilidad"] == [
        "intentos-fuera-de-ledger:A::L-A:jev=3"]
    decision = runner.decide(informe=informe, protocolo=protocolo_base(), fecha="2026-10-04")
    assert decision["run_status"] == "FALLIDO"
    assert decision["decision"] is None


def test_una_indisponibilidad_no_elimina_el_brazo(runner, tmp_path):
    """AC12: conexion caida => INCOMPLETO, y el brazo sigue publicado con sus otras filas."""
    informe = correr_report(runner, tmp_path)
    decision = runner.decide(informe=informe, protocolo=protocolo_base(), fecha="2026-10-04")
    assert decision["run_status"] == "INCOMPLETO"
    brazos = {i["brazo"] for i in decision["estado_del_run"]["indisponibilidades"]}
    assert brazos == {"deepseek"}
    assert "deepseek" in informe["por_brazo"], "el brazo con indisponibilidad desaparecio"


@pytest.mark.parametrize("criterios,esperado,porque", [
    ({"cobertura_min": 0.5, "margen_vs_deepseek": 0.25}, "ACTIVAR",
     "cobertura 0.5 >= 0.5, margen 0.5 >= 0.25, latencia sin fallos"),
    ({"cobertura_min": 0.5, "margen_vs_deepseek": 0.75}, "RECHAZAR",
     "comparacion valida y el margen medido (0.5) no llega al congelado (0.75)"),
])
def test_activar_y_rechazar_se_provocan_con_respuestas_sin_fallos(runner, tmp_path, criterios,
                                                                  esperado, porque):
    """Cada regla de etiqueta, provocada con protocolos sinteticos y no con los datos reales."""
    filas = [copy.deepcopy(f) for f in respuestas_base()
             if not (f["brazo"] == "deepseek" and f["error_kind"])]
    for f in filas:
        if f["brazo"] == "deepseek" and f["pair_id"] == "A::L-A":
            f["propuesta"], f["abstencion"] = "L-X", False
    protocolo = protocolo_base(**criterios)
    informe = correr_report(runner, tmp_path, respuestas=filas, protocolo=protocolo)
    decision = runner.decide(informe=informe, protocolo=protocolo, fecha="2026-10-04")
    assert decision["run_status"] == "COMPLETO", decision["estado_del_run"]
    assert decision["decision"] == esperado, (porque, decision["motivo_decision_null"],
                                              decision["criterios_congelados"])
    assert decision["literales_y_su_estado"][esperado]["estado"] == "EMITIDA"


def test_mutante_umbral_de_margen_voltea_la_etiqueta_emitida(runner, tmp_path):
    """El mismo insumo, dos umbrales: la etiqueta sale del criterio congelado, no de una opinion."""
    filas = [copy.deepcopy(f) for f in respuestas_base()
             if not (f["brazo"] == "deepseek" and f["error_kind"])]
    for f in filas:
        if f["brazo"] == "deepseek" and f["pair_id"] == "A::L-A":
            f["propuesta"], f["abstencion"] = "L-X", False
    salidas = {}
    for margen in (0.25, 0.75):
        protocolo = protocolo_base(cobertura_min=0.5, margen_vs_deepseek=margen)
        informe = correr_report(runner, tmp_path / f"m{margen}", respuestas=filas,
                                protocolo=protocolo)
        salidas[margen] = runner.decide(informe=informe, protocolo=protocolo,
                                       fecha="2026-10-04")["decision"]
    assert salidas == {0.25: "ACTIVAR", 0.75: "RECHAZAR"}, salidas


def test_suficiencia_bajo_el_umbral_emite_MUESTRA_INSUFICIENTE(runner, tmp_path):
    """MUESTRA-INSUFICIENTE por su regla congelada, no por una lectura nueva del criterio."""
    etiquetas = copy.deepcopy(etiquetas_base())
    for l in etiquetas["labels"]:
        if l["pair_id"] in ("A::L-A", "B::L-B"):
            l["label"], l["importance"] = "no_pertinente", None
    filas = [fila("jev", "C::L-C", "L-C", propuesta="L-C", candidatos=["L-C"], en_candidatos=True),
             fila("deepseek", "C::L-C", "L-C", propuesta="L-C", candidatos=["L-C"],
                  en_candidatos=True)]
    informe = correr_report(runner, tmp_path, respuestas=filas, etiquetas=etiquetas)
    decision = runner.decide(informe=informe, protocolo=protocolo_base(), fecha="2026-10-04")
    assert decision["criterios_congelados"]["suficiencia_minima"]["medido"]["value"] == 0.25
    assert decision["criterios_congelados"]["suficiencia_minima"]["lectura_congelada"] == \
        "1 de 4 pares pertinentes"
    assert decision["decision"] == "MUESTRA-INSUFICIENTE"


def test_coste_no_pagado_solo_cuando_no_hay_envios_y_el_usd_esta_en_gobernanza(runner, tmp_path):
    """La rama economica del maestro (:101): describe la decision de NO ejecutar, no un rechazo."""
    con_usd = protocolo_base()
    con_usd["limites_gasto"]["usd"] = 5
    informe = correr_report(runner, tmp_path, respuestas=[], protocolo=con_usd)
    decision = runner.decide(informe=informe, protocolo=con_usd, fecha="2026-10-04")
    assert decision["run_status"] == "NO-EJERCITADO"
    assert decision["decision"] == "COSTE-NO-PAGADO"
    assert decision["literales_y_su_estado"]["COSTE-NO-PAGADO"]["estado"] == "EMITIDA"


def test_coste_no_pagado_queda_bloqueado_con_usd_fuera_de_gobernanza(runner, tmp_path):
    """La otra mitad de la misma regla: sin gobernanza de coste no hay literal de coste.

    Es el estado que publico FASE-C y el emisor nuevo lo reproduce con su motivo.
    """
    informe = correr_report(runner, tmp_path, respuestas=[])
    decision = runner.decide(informe=informe, protocolo=protocolo_base(), fecha="2026-10-04")
    assert decision["run_status"] == "NO-EJERCITADO"
    assert decision["decision"] is None
    assert decision["literales_y_su_estado"]["COSTE-NO-PAGADO"]["estado"] == "BLOQUEADO"
    assert any("fuera de gobernanza" in m for m in decision["motivo_decision_null"])


def test_decide_no_elige_cuando_un_criterio_queda_no_evaluable(runner, tmp_path):
    """Sin magnitud no hay veredicto: `decide` emite el estado y las bases, y se queda en null."""
    filas = [f for f in respuestas_base() if f["brazo"] == "jev"]
    informe = correr_report(runner, tmp_path, respuestas=filas)
    decision = runner.decide(informe=informe, protocolo=protocolo_base(), fecha="2026-10-04")
    assert decision["criterios_congelados"]["margen_vs_deepseek"]["estado"] == "NO-EVALUABLE"
    assert decision["decision"] is None
    assert any("requieren magnitud medida" in m for m in decision["motivo_decision_null"])
    assert decision["requiere_revision_del_operador"] is True


def test_el_decision_md_sale_del_mismo_calculo_y_no_pierde_un_cero(runner, tmp_path):
    """AC5 pide los dos artefactos: la tabla del .md tiene que imprimir un 0.0 legitimo.

    Control contra una cadena de `or`: un cero es falso en Python y con `or` desaparecia de la
    celda, que es la forma mas cara de perder el dato. Aqui los dos brazos erran en A y fallan el
    envio de B: extremo a extremo 0/2 en ambos, diferencia 0.0, margen NO-EVALUABLE por el fallo.
    """
    filas = []
    for brazo in ("jev", "deepseek"):
        filas.append(fila(brazo, "A::L-A", "L-A", propuesta="L-Z", candidatos=["L-A", "L-Z"],
                          en_candidatos=True,
                          intentos=[{"n": 1, "resultado": "exito", "duracion_ms": 200.0}]))
        filas.append(fila(brazo, "B::L-B", "L-B", propuesta=None, candidatos=["L-X"],
                          en_candidatos=False, error_kind="conexion",
                          intentos=[{"n": 1, "resultado": "fallo", "duracion_ms": 9.0}]))
    informe = correr_report(runner, tmp_path, respuestas=filas)
    margen = informe["criterios"]["margen_vs_deepseek"]
    assert margen["diferencia_calculada"] == 0.0 and margen["estado"] == "NO-EVALUABLE"
    decision = runner.decide(informe=informe, protocolo=protocolo_base(), fecha="2026-10-04")
    md = runner.decision_markdown(decision, informe)
    assert "| margen_vs_deepseek | 0.25 | 0.0 | NO-EVALUABLE |" in md, md
    assert "`decision`: **null**" in md
    assert "pendiente de revision del operador" in md
    assert "run_status`: **INCOMPLETO**" in md


def test_un_brazo_excluido_que_aparece_en_registros_se_nombra(runner, tmp_path):
    """AC12: Anthropic esta excluido; una fila suya es un hecho que el informe declara."""
    filas = respuestas_base() + [fila("anthropic", "A::L-A", "L-A", propuesta="L-A",
                                      candidatos=["L-A"], en_candidatos=True)]
    assert "anthropic" in correr_report(runner, tmp_path, respuestas=filas)["excluido_en_registros"]


# ----------------------------------------------------------------------------------------------
# CR-3: el CLI del `run` y la credencial del SDK por el camino del contrato
# ----------------------------------------------------------------------------------------------

class PuertaFalsa:
    """La costura falsa: registra como se le pide el cliente, sin SDK y sin red."""

    def __init__(self):
        self.llamadas = []
        self.opciones_cliente = None

    def cargar_sdk(self):
        self.llamadas.append("cargar_sdk")
        return {"modulo": object(), "resolucion": {"sistema": "falso"}}

    def cliente_jev(self, modulo, *, modelo, timeout=None, **kwargs):
        self.opciones_cliente = {"modelo": modelo, "timeout": timeout, "extra": kwargs}
        self.llamadas.append("cliente_jev")
        return object()

    def system_one_jev(self, cliente, *, state, questions, modelo):
        self.llamadas.append("system_one_jev")
        ids = list(questions)[0]
        return {"answers": {ids: {"eleccion": state["candidatos"][0]["id"]}},
                "modelo": modelo, "usage": {"input_tokens": 10, "output_tokens": 5},
                "request_id": "req-falso"}


def _insumos_de_corrida(tmp_path: Path) -> dict:
    muestra = muestra_base()
    muestra["pairs"] = [_par("A::L-A", "L-A", "eval")]
    muestra["counts"] = {"total": 1, "dev": 0, "eval": 1, "excluidos": 0}
    etiquetas = {"schema": "jev-pilot-etiquetas/v1", "review_status": "revisada",
                 "labels": [{"pair_id": "A::L-A", "label": "pertinente", "importance": "alta",
                             "reviewer": "jhon", "reviewed_at": "2026-10-02"}]}
    indice = {"lecciones": [{"id": "L-A", "enunciado": "fragmento de A::L-A"},
                            {"id": "L-X", "enunciado": "nada que ver"}]}
    preflight = {"schema": "jev-pilot-preflight/v1",
                 "proveedores": {"jev": {"habilitacion_declarada": True, "sdk_instalado": True,
                                          "autenticacion_real": "AUTENTICADA",
                                          "cuota_o_saldo": "NO-DISPONIBLE-POR-SDK",
                                          "modelo_efectivo_preflight": "jev-1.13.0"}}}
    rutas = {}
    for nombre, datos in (("muestra", muestra), ("etiquetas", etiquetas),
                          ("protocolo", protocolo_base()), ("indice", indice),
                          ("preflight", preflight)):
        ruta = tmp_path / f"{nombre}_corrida.json"
        ruta.write_text(json.dumps(datos, ensure_ascii=False), encoding="utf-8")
        rutas[nombre] = ruta
    return rutas


def _main_run(runner, r, out, extra=()):
    return runner.main(["run", "--proveedor", "jev", "--muestra", str(r["muestra"]),
                        "--protocolo", str(r["protocolo"]), "--indice", str(r["indice"]),
                        "--preflight", str(r["preflight"]), "--out-dir", str(out),
                        "--splits", "eval", *extra])


def test_el_cli_del_run_propaga_etiquetas_y_publica_la_recuperacion(runner, tmp_path, monkeypatch):
    """CR-3, mitad --etiquetas: por CLI la recuperacion se publicaba en null (H5 de FASE-C)."""
    monkeypatch.setattr(runner, "_puerta", lambda: PuertaFalsa())
    monkeypatch.setattr(runner, "credencial_del_sdk",
                        lambda *a, **k: {"nombre": "x", "fuente": "falso", "accion": "ninguna"})
    r = _insumos_de_corrida(tmp_path)
    assert _main_run(runner, r, tmp_path / "run1") == 0
    resumen = json.loads((tmp_path / "run1" / "run_resumen.json").read_text(encoding="utf-8"))
    assert resumen["recuperacion"] is None, "sin --etiquetas el runner invento una recuperacion"
    assert _main_run(runner, r, tmp_path / "run2",
                     ("--etiquetas", str(r["etiquetas"]))) == 0
    resumen2 = json.loads((tmp_path / "run2" / "run_resumen.json").read_text(encoding="utf-8"))
    assert (resumen2["recuperacion"]["numerator"], resumen2["recuperacion"]["denominator"]) == (1, 1)


def test_la_credencial_se_resuelve_por_entorno_y_no_sale_en_ningun_artefacto(runner, tmp_path,
                                                                             monkeypatch):
    """CR-3, mitad contrato: el SDK lee su entorno; el runner rellena por nombre y no imprime nada.

    La clave del `.env` sintetico es un centinela: si apareciera en el estado devuelto o en el
    resumen del runner, la fuga es medida y no afirmada.
    """
    centinela = "CLAVE-SINTETICA-NO-IMPRIMIBLE-1234567890"
    (tmp_path / ".env").write_text(f"TYPESAFE_API_KEY={centinela}\nOTRA=1\n", encoding="utf-8")
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
    estado = runner.credencial_del_sdk(tmp_path)
    assert estado == {"nombre": "TYPESAFE_API_KEY", "fuente": "dotenv",
                      "accion": "rellenada-desde-env"}
    assert os.environ["TYPESAFE_API_KEY"] == centinela
    assert centinela not in json.dumps(estado), "la credencial viajo en el estado publicado"

    assert runner.credencial_del_sdk(tmp_path)["fuente"] == "entorno", "piso lo que ya estaba"
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
    (tmp_path / "sin-env").mkdir()
    assert runner.credencial_del_sdk(tmp_path / "sin-env")["accion"] == "env-no-encuentra-env"
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
    (tmp_path / ".env").write_text("OTRA=1\n", encoding="utf-8")
    assert runner.credencial_del_sdk(tmp_path)["accion"] == "clave-no-esta-en-env"


def test_el_run_con_enviar_inyectado_nunca_toca_la_credencial(runner, tmp_path, monkeypatch):
    """La via offline del `run` no lee `.env`: la credencial vive detras de la inyeccion."""
    tocada = []
    monkeypatch.setattr(runner, "credencial_del_sdk",
                        lambda *a, **k: tocada.append(1) or {"nombre": "x"})
    r = _insumos_de_corrida(tmp_path)

    def enviar(state, questions, modelo):
        ids = list(questions)[0]
        return {"answers": {ids: {"eleccion": "L-A"}}, "modelo": modelo,
                "usage": {"input_tokens": 1, "output_tokens": 1}, "request_id": "r"}

    resultado = runner.run(muestra=r["muestra"], protocolo=r["protocolo"], indice=r["indice"],
                          preflight=r["preflight"], out_dir=tmp_path / "run3", proveedor="jev",
                          k=8, splits="eval", enviar=enviar)
    assert resultado["status"] == "OK"
    assert tocada == [], "la via inyectada abrio el camino de la credencial"
    assert resultado["credencial"] is None
    assert resultado["resolucion_sdk"] is None


def test_la_puerta_recibe_api_key_ausente_por_contrato(runner, tmp_path, monkeypatch):
    """Mutante de contrato: si el runner empezara a pasar la clave, la puerta deja de ser unica."""
    puerta = PuertaFalsa()
    monkeypatch.setattr(runner, "_puerta", lambda: puerta)
    estado = {"nombre": "TYPESAFE_API_KEY", "fuente": "falso", "accion": "ninguna"}
    llamadas = []
    monkeypatch.setattr(runner, "credencial_del_sdk",
                        lambda *a, **k: llamadas.append(a) or dict(estado))
    r = _insumos_de_corrida(tmp_path)
    assert _main_run(runner, r, tmp_path / "run4") == 0
    assert "api_key" not in puerta.opciones_cliente["extra"], (
        "el runner empezo a pasar la credencial: el contrato dice que la resuelve el SDK")
    assert puerta.llamadas == ["cargar_sdk", "cliente_jev", "system_one_jev"]
    assert len(llamadas) == 1, "la credencial se resolvio mas de una vez por corrida"
    resumen = json.loads((tmp_path / "run4" / "run_resumen.json").read_text(encoding="utf-8"))
    assert resumen["credencial"] == estado
    assert json.dumps(resumen).count("CLAVE") == 0


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
