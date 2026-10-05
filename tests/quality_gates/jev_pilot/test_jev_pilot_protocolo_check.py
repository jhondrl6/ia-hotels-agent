"""Dientes de `validar_protocolo` (paso 6 de FASE-B, 2026-10-03).

El lector goberna tres cosas que antes estaban en prosa: la forma del schema, los ocho umbrales
(incluida la coherencia entre `timeout_s` y `latencia_max`, que ningun valor suelto puede decir) y
la politica de nulos: los unicos admitidos son `tokens_in`, `tokens_out` y el `usd` declarado fuera
de gobernanza, y los tres con su motivo escrito.

Cada control afirma el GUARD que lo produjo, no solo el veredicto (L-V2.1). Y la mitad favorable se
mide contra el `protocolo.json` versionado, no contra un dict inventado aqui: un validador que solo
ve fixtures propias da verde sin haber leido el artefacto que dice gobernar.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
PROTOCOLO_REAL = (REPO_ROOT / "evidence" / "EVALUACION-JEV-TYPESAFE-2026-09-21"
                  / "protocolo.json")


@pytest.fixture(scope="module")
def real() -> dict:
    return json.loads(PROTOCOLO_REAL.read_text(encoding="utf-8"))


def guarda(runner, protocolo, nombre: str) -> list:
    return [h["motivo"] for h in runner.validar_protocolo(protocolo)["hallazgos"]
            if h["guard"] == nombre]


def test_el_protocolo_versionado_pasa_y_deja_un_solo_nulo_declarado(runner, real):
    """Estado del protocolo desde su congelado: CONGELADA con dueño y fecha, y un solo null.

    Re-anclado en FASE-B.2 (2026-10-04) cerrando CR-4. Linea anterior, conservada como antecedente:
    hasta el 2026-10-03 este control afirmaba `protocolo_status == "BORRADOR"` y su mensaje decia
    "si alguien lo congelo aqui, esto es el aviso". FASE-C lo congelo (jhon, 2026-10-04,
    `protocolo.json:congelado`), el aviso sonó y ese rojo es el que la sesion 3 no pudo tocar porque
    su §5 le prohibia `tests/`: quedo registrado como CR-4 con rojo previo **1 failed / 23 passed**
    (crudo `FASE-C/22-bateria-protocolo-final.txt`). La cura re-ancla el estado, no baja la asercion:
    el diente contrario se queda, y sigue avisando si el versionado regresara a BORRADOR, porque eso
    si seria un hallazgo y no un pendiente.

    Antes de la corrida k=8 el control afirmaba TRES null; la tanda los redujo a uno.
    """
    resultado = runner.validar_protocolo(real)
    assert resultado["check_status"] == "OK", resultado["hallazgos"]
    assert resultado["protocolo_status"] == "CONGELADA", (
        "el protocolo se devolvio a BORRADOR despues de su congelado del 2026-10-04: hallazgo")
    assert real["congelado"] == {"revisado_por": "jhon", "fecha": "2026-10-04"}, real["congelado"]
    # El diente contrario: el mismo lector tiene que seguir viendo un BORRADOR si alguien lo vuelve.
    vuelto = copy.deepcopy(real)
    vuelto["status"] = "BORRADOR"
    assert runner.validar_protocolo(vuelto)["protocolo_status"] == "BORRADOR", (
        "el ancla nueva se apoyo en un campo que el lector ya no devuelve")
    assert runner.validar_protocolo(vuelto)["check_status"] == "OK", "BORRADOR dejo de ser forma valida"
    assert resultado["k"] == 8
    assert resultado["umbrales_gobernados"] == 8
    assert resultado["nulos"] == ["limites_gasto.usd"], resultado["nulos"]
    gastos = real["limites_gasto"]
    assert isinstance(gastos["tokens_in"], int) and gastos["tokens_in"] > 0
    assert isinstance(gastos["tokens_out"], int) and gastos["tokens_out"] > 0
    assert str(gastos["tokens_in"]) in gastos["motivo"] and "correr_k8.py" in gastos["motivo"], (
        "la cifra del techo viaja sin el comando que la midio")


def test_los_dos_techos_de_tokens_sin_motivo_escrito_cae(runner, real):
    """El guard de nulidad se prueba devolviendo el artefacto a su estado anterior, no fiandolo.

    El protocolo versionado ya no trae los techos en null, asi que una asercion que dependa de eso
    se volveria verde por vacio. Aqui se vuelven a poner null sobre una copia y se exige que el
    lector los reclame dos veces, una por clave.
    """
    roto = copy.deepcopy(real)
    roto["limites_gasto"]["tokens_in"] = None
    roto["limites_gasto"]["tokens_out"] = None
    roto["limites_gasto"]["motivo"] = "   "
    assert len(guarda(runner, roto, "nulo-sin-motivo")) == 2, roto
    # y con el motivo escrito, los mismos dos null vuelven a ser admisibles
    roto["limites_gasto"]["motivo"] = real["limites_gasto"]["motivo"]
    assert guarda(runner, roto, "nulo-sin-motivo") == []


@pytest.mark.parametrize("ruta", ["parametros.retry_policy.max_retries", "parametros.timeout_s",
                                 "limites_gasto.llamadas", "criterios_adopcion.cobertura_min",
                                 "criterios_adopcion.suficiencia_minima",
                                 "criterios_adopcion.margen_vs_deepseek",
                                 "criterios_adopcion.latencia_max"])
def test_cada_umbral_que_falta_se_nombra_por_su_ruta(runner, real, ruta):
    roto = copy.deepcopy(real)
    padre, _, clave = ruta.rpartition(".")
    actual = roto
    for parte in ruta.split(".")[:-1]:
        actual = actual[parte]
    del actual[ruta.split(".")[-1]]
    hallazgos = runner.validar_protocolo(roto)["hallazgos"]
    assert any(h["guard"] == "umbral-ausente" and ruta in h["motivo"] for h in hallazgos), hallazgos


def test_un_umbral_vuelto_null_es_hallazgo_no_un_favorable(runner, real):
    """Un techo en null que ya NO es de los admitidos bloquea: `null` no es «sin opinion» gobernable."""
    roto = copy.deepcopy(real)
    roto["criterios_adopcion"]["cobertura_min"] = None
    assert guarda(runner, roto, "umbral-null"), roto
    assert runner.validar_protocolo(roto)["check_status"] == "FALLO"


def test_los_seis_umbrales_numericos_no_pueden_estar_fuera_de_rango(runner, real):
    for clave, valor in (("cobertura_min", 1.4), ("suficiencia_minima", 0.0),
                         ("margen_vs_deepseek", -0.1)):
        roto = copy.deepcopy(real)
        roto["criterios_adopcion"][clave] = valor
        assert guarda(runner, roto, "umbral-rango"), f"{clave}={valor} paso sin aviso"


def test_latencia_max_tiene_que_casar_con_el_timeout(runner, real):
    """Coherencia entre umbrales: 30 s y 30.000 ms son la misma decision; 30 s y 15.000 ms se contradicen."""
    roto = copy.deepcopy(real)
    roto["criterios_adopcion"]["latencia_max"] = 15000
    motivos = guarda(runner, roto, "umbral-coherencia")
    assert motivos and "15000" in motivos[0] and "30" in motivos[0], motivos


def test_max_retries_distinto_de_cero_lo_corta_tambien_el_validador(runner, real):
    """AC8 en dos capas: el runner lo niega al reservar y el lector del protocolo lo niega al leer."""
    roto = copy.deepcopy(real)
    roto["parametros"]["retry_policy"]["max_retries"] = 2
    assert guarda(runner, roto, "umbral-reintentos")


def test_un_cuarto_null_no_se_admite(runner, real):
    """La politica de nulos es una lista cerrada: una clave nueva en null no entra por ser nueva."""
    roto = copy.deepcopy(real)
    roto["limites_gasto"]["requests_por_minuto"] = None
    motivos = guarda(runner, roto, "nulo-no-admitido")
    assert motivos and "requests_por_minuto" in motivos[0], motivos



def test_el_usd_null_necesita_la_declaracion_de_fuera_de_gobernanza(runner, real):
    """`usd` no es un pendiente disfrazado: su null vale porque el operador lo declaro fuera de gobernanza."""
    roto = copy.deepcopy(real)
    roto["limites_gasto"]["motivo"] = "techo de tokens pendiente de medir la recuperacion"
    assert guarda(runner, roto, "usd-sin-declaracion")


def test_la_k_se_lee_de_la_regla_de_recuperacion_y_su_ausencia_es_hallazgo(runner, real):
    roto = copy.deepcopy(real)
    assert runner.validar_protocolo(roto)["k"] == 8
    roto["reglas_recuperacion"] = "top-k por consulta fria, valor a decidir"
    assert guarda(runner, roto, "umbral-k")
    assert runner.validar_protocolo(roto)["k"] is None


@pytest.mark.parametrize("cambio,guard", [
    ({"schema": "jev-pilot-protocolo/v2"}, "schema"),
    ({"status": "APROBADA"}, "status"),
    ({"rubrica": {"valores": [], "importancia": ["alta"]}}, "rubrica"),
    ({"modelos": {"jev_pin": "", "comparador": "DeepSeek", "excluido": "Anthropic"}},
     "modelo-pedido"),
    ({"modelos": {"jev_pin": "jev-1.13.0", "comparador": "", "excluido": "Anthropic"}},
     "comparador"),
    ({"modelos": {"jev_pin": "jev-1.13.0", "comparador": "DeepSeek", "excluido": "OpenAI"}},
     "excluido"),
])
def test_cada_rotura_de_forma_produce_su_guard_nombrado(runner, real, cambio, guard):
    roto = copy.deepcopy(real)
    for clave, valor in cambio.items():
        if isinstance(valor, dict):
            roto[clave] = {**roto.get(clave, {}), **valor}
        else:
            roto[clave] = valor
    assert guarda(runner, roto, guard), (cambio, runner.validar_protocolo(roto)["hallazgos"])


def test_revision_humana_sin_disenado_no_pasa_por_cumplida(runner, real):
    """AC12/AC4: `obligatoria` a secas no designa a nadie; el protocolo versionado si lo hace."""
    roto = copy.deepcopy(real)
    roto["criterios_adopcion"]["revision_humana"] = "obligatoria"
    assert not guarda(runner, roto, "revision-humana"), (
        "la forma actual del protocolo exige designado y fecha, pero el lector no la corta")
    roto["criterios_adopcion"]["revision_humana"] = "obligatoria; pendiente de designar"
    assert guarda(runner, roto, "revision-humana")
    assert "jhon" in real["criterios_adopcion"]["revision_humana"]


def test_la_negacion_del_lector_tambien_tiene_codigo_de_salida(runner, real, tmp_path, capsys):
    """El CLI no puede imprimir OK y salir distinto de cero (o viceversa): el EXIT codifica el guard."""
    ruta = tmp_path / "protocolo.json"
    ruta.write_text(json.dumps(real), encoding="utf-8")
    assert runner.main(["protocolo-check", "--protocolo", str(ruta)]) == 0
    roto = copy.deepcopy(real)
    roto["parametros"]["retry_policy"]["max_retries"] = 3
    ruta.write_text(json.dumps(roto), encoding="utf-8")
    assert runner.main(["protocolo-check", "--protocolo", str(ruta)]) == 1


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
