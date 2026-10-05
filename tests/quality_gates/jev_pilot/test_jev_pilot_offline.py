"""Tests offline del instrumento del piloto Jev (FASE-A).

Cada guard lleva su par causal verde/rojo: no basta una suite verde, hay que
ver que el control dispara cuando se viola lo que protege (L-D5, AC10/AC11).
Sin red, sin clientes, sin credenciales: la muestra se construye en tmp_path.
"""
from __future__ import annotations

import builtins
import importlib.util
import json
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
_SCRIPT = _REPO_ROOT / "scripts" / "evaluate_jev_pilot.py"

_spec = importlib.util.spec_from_file_location("evaluate_jev_pilot", _SCRIPT)
ejv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ejv)


def _candidates():
    # Dos planes que, por el hash determinista del split, caen en sets distintos;
    # tambein un duplicado y un excluido para probar dedup y exclusiones.
    return [
        {"target_plan": "PlanA", "target_phase": "FASE-B", "lesson_id": "L-1",
         "original_text": "texto original A1", "sanitized_text": "saneado A1"},
        {"target_plan": "PlanA", "target_phase": "FASE-B", "lesson_id": "L-1",
         "original_text": "texto original A1", "sanitized_text": "saneado A1"},
        {"target_plan": "PlanB", "target_phase": "FASE-C", "lesson_id": "L-2",
         "original_text": "orig B2", "sanitized_text": "saneado B2"},
        {"target_plan": "PlanC", "target_phase": "FASE-B", "lesson_id": "L-3",
         "original_text": "orig C3", "sanitized_text": "descartado",
         "excluded": True, "exclude_reason": "fuera de ventana temporal"},
    ]


def _prepare_write(tmp_path: Path):
    muestra, etiquetas = ejv.prepare(_candidates(), "2026-09-12", "own:lecciones_index")
    mpath = tmp_path / "muestra.json"
    epath = tmp_path / "etiquetas.json"
    mpath.write_text(json.dumps(muestra, ensure_ascii=False), encoding="utf-8")
    epath.write_text(json.dumps(etiquetas, ensure_ascii=False), encoding="utf-8")
    return muestra, etiquetas, mpath, epath


def _fails(check_result: dict, guard: str) -> bool:
    return any(f["guard"] == guard and not f["ok"] for f in check_result["findings"])


def test_prepare_dedups_and_marks_draft(tmp_path):
    muestra, etiquetas, _, _ = _prepare_write(tmp_path)
    ids = [(p["target_plan"], p["lesson_id"]) for p in muestra["pairs"]]
    assert ids.count(("PlanA", "L-1")) == 1          # dedup
    assert muestra["counts"]["excluidos"] == 1        # exclusion registrada
    assert muestra["status"] == "BORRADOR"
    assert all(l["label"] is None and l["reviewer"] is None for l in etiquetas["labels"])


def test_sample_detects_content_change(tmp_path):
    """AC3 verde/rojo: cambiar un fragmento invalida su SHA."""
    _, _, mpath, epath = _prepare_write(tmp_path)
    assert ejv.check(mpath, epath)["check_status"] == "OK"      # verde
    data = json.loads(mpath.read_text(encoding="utf-8"))
    data["pairs"][0]["input_fragment"] += " adulterado"          # mutation
    mpath.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    assert _fails(ejv.check(mpath, epath), "content_sha")        # rojo


def test_split_rejects_same_plan_in_both_sets(tmp_path):
    """AC3 verde/rojo: un plan no puede aparecer en dev y eval."""
    _, _, mpath, epath = _prepare_write(tmp_path)
    assert not _fails(ejv.check(mpath, epath), "split_disjoint")  # verde
    data = json.loads(mpath.read_text(encoding="utf-8"))
    dup = dict(data["pairs"][0])
    dup["pair_id"] = "PlanA::L-1#dup"
    dup["lesson_id"] = "L-9"
    dup["split"] = "eval" if dup["split"] == "dev" else "dev"     # mismo plan, otro set
    data["pairs"].append(dup)
    mpath.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    assert _fails(ejv.check(mpath, epath), "split_disjoint")      # rojo


def test_labels_do_not_enter_payload(tmp_path):
    """AC3 verde/rojo: etiquetas e importancia quedan fuera de los inputs."""
    muestra, _, mpath, epath = _prepare_write(tmp_path)
    assert not _fails(ejv.check(mpath, epath), "labels_not_in_payload")   # verde
    data = json.loads(mpath.read_text(encoding="utf-8"))
    data["pairs"][0]["importance"] = "alta"                                # fuga a input
    mpath.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    assert _fails(ejv.check(mpath, epath), "labels_not_in_payload")        # rojo
    for pair in ejv.payload_for_models(data):
        assert not (ejv.LABEL_KEYS & set(pair.keys()))


def test_unreviewed_sample_is_not_frozen(tmp_path):
    """AC3 verde/rojo: revision humana pendiente no pasa por aprobada."""
    _, _, mpath, epath = _prepare_write(tmp_path)
    assert ejv.check(mpath, epath)["check_status"] == "OK"                 # BORRADOR: verde
    data = json.loads(mpath.read_text(encoding="utf-8"))
    data["status"] = "CONGELADA"                                           # congelar sin revisar
    mpath.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    assert _fails(ejv.check(mpath, epath), "unreviewed_not_frozen")        # rojo


def test_metrics_known_counts_and_empty_denominator():
    """AC10: resultados comprobables por otra via; denominador cero NO es 100 %."""
    assert ejv.score(3, 4) == {"value": 0.75, "numerator": 3, "denominator": 4, "motivo": ""}
    empty = ejv.score(0, 0)
    assert empty["value"] is None and empty["motivo"] == "denominador_cero"
    m = ejv.metrics({"num": 8, "den": 10},
                    {"prec_num": 6, "rec_num": 8, "den": 10},
                    {"num": 5, "den": 10})
    assert m["recuperacion"]["value"] == 0.8
    assert m["precision_entre_propuestas"]["value"] == 0.6
    assert m["extremo_a_extremo"]["value"] == 0.5


def _protocolo_minimo() -> dict:
    """Protocolo sintetico para el guard de imports: la k y los umbrales, nada del versionado."""
    return {"schema": "jev-pilot-protocolo/v1", "status": "CONGELADA",
            "reglas_recuperacion": "top-8 por consulta fria",
            "criterios_adopcion": {"cobertura_min": 0.95, "margen_vs_deepseek": 0.25,
                                   "suficiencia_minima": 0.5, "latencia_max": 30000,
                                   "revision_humana": "obligatoria; designado: jhon (2026-10-02)"},
            "limites_gasto": {"usd": None, "llamadas": 12, "tokens_in": 1834, "tokens_out": 139},
            "parametros": {"retry_policy": {"max_retries": 0}, "timeout_s": 30},
            "modelos": {"jev_pin": "jev-1.13.0", "comparador": "DeepSeek", "excluido": "Anthropic"}}


def test_prepare_and_check_do_not_construct_clients(tmp_path, monkeypatch):
    """AC11: los modos locales nunca instancian clientes ni tocan la red.

    FASE-B.2 (2026-10-04) re-ancla la mitad de `decide` de esta asercion. El contrato que gobernaba
    era "los modos que hacen inferencias se niegan en seco"; desde CR-2 `decide` es offline y emite,
    asi que lo que sigue negado --con el mismo EXIT 2-- es emitir SIN INSUMOS. El cambio se escribe
    aqui y no en silencio: `main(["decide"])` sin insumos sigue valiendo 2, y con insumos vale 3
    (emitido sin decision) mientras el guard de imports prohibidos siga armado.
    """
    real_import = builtins.__import__

    def guarded(name, *args, **kwargs):
        root = name.split(".")[0]
        if name in ejv.FORBIDDEN_MODULES or root in ejv.FORBIDDEN_MODULES:
            raise AssertionError(f"intento de importar cliente/red: {name}")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded)
    muestra, _, mpath, epath = _prepare_write(tmp_path)
    assert ejv.check(mpath, epath)["check_status"] == "OK"
    # run sigue negado: es el unico modo que podria gastar una llamada (AC8/AC12).
    assert ejv.main(["run"]) == 2
    # report/decide se niegan SIN insumos, no por ser modos nuevos.
    assert ejv.main(["report"]) == 2
    assert ejv.main(["decide"]) == 2

    # Con insumos offline, emiten sin importar nada prohibido (guard armado en todo el bloque).
    par = muestra["pairs"][0]
    ruta_respuestas = tmp_path / "respuestas.jsonl"
    fila = {"pair_id": par["pair_id"], "split": par["split"], "lesson_id_target": par["lesson_id"],
            "brazo": "jev", "propuesta": par["lesson_id"], "abstencion": False,
            "candidatos_frios": [par["lesson_id"]], "leccion_target_en_candidatos": True,
            "attempts": 1, "error_kind": None, "intentos": [], "usage_normalized": None,
            "duracion_ms": [], "request_id": None}
    ruta_respuestas.write_text(json.dumps(fila, ensure_ascii=False) + "\n", encoding="utf-8")
    ruta_protocolo = tmp_path / "protocolo.json"
    protocolo = _protocolo_minimo()
    ruta_protocolo.write_text(json.dumps(protocolo, ensure_ascii=False), encoding="utf-8")

    informe = ejv.report(respuestas=ruta_respuestas, etiquetas=epath, muestra=mpath,
                         protocolo=ruta_protocolo, fecha="2026-10-04")
    assert informe["generado_sin_red"] is True
    e2e = informe["por_brazo"]["jev"]["extremo_a_extremo"]
    assert e2e["value"] is None and e2e["motivo"] == "denominador_cero", e2e
    # La muestra de `_prepare_write` esta SIN revisar (label None), o sea no hay conjunto elegible:
    # el emisor publica NO-EVALUABLE con su motivo en vez de inventar un numero (AC10).
    assert informe["conjunto_elegible"]["importantes_elegibles"] == []
    assert ejv.main(["report", "--respuestas", str(ruta_respuestas), "--etiquetas", str(epath),
                     "--muestra", str(mpath), "--protocolo", str(ruta_protocolo),
                     "--out", str(tmp_path / "informe.json")]) == 0
    decision = ejv.decide(informe=informe, protocolo=protocolo, fecha="2026-10-04")
    # La regla congelada se aplico sin red y sin importar el SDK: con 0 de 4 pares pertinentes la
    # suficiencia no se cumple, y esa es la salida que gobierna (no RECHAZAR, que exige comparacion
    # valida). El emisor propone; la adopcion la firma el operador.
    assert decision["schema"] == "jev-pilot-decision/v1"
    assert decision["run_status"] == "INCOMPLETO"
    assert decision["decision"] == "MUESTRA-INSUFICIENTE"
    assert decision["requiere_revision_del_operador"] is True


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
