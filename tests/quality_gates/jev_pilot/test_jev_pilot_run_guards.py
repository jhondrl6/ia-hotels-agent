"""AC8 sobre el modo `run`: el guard corta ANTES de construir y el ledger persiste por llamada.

Nada de este archivo sale a la red: el envio se inyecta (`enviar=`), y los dos controles que importan
son de **cero envios** — un guard que nadie dispara no existe, asi que cada camino negado afirma
tambien que la funcion inyectada no llego a llamarse (L-V2.1: la caida por la causa prevista, no la
etiqueta).
"""
from __future__ import annotations

import builtins
import json
from pathlib import Path

import pytest

PIN = "jev-1.13.0"
DEVUELTO = "jev-9.9.9"


def _muestra(status="CONGELADA"):
    return {"schema": "jev-pilot-muestra/v1", "status": status,
            "pairs": [
                {"pair_id": "P1::L-1", "target_plan": "P1", "lesson_id": "L-1",
                 "input_fragment": "texto frio uno", "split": "dev"},
                {"pair_id": "P2::L-2", "target_plan": "P2", "lesson_id": "L-2",
                 "input_fragment": "texto frio dos", "split": "eval"}],
            "counts": {"total": 2, "dev": 1, "eval": 1, "excluidos": 0}}


def _etiquetas():
    return {"schema": "jev-pilot-etiquetas/v1", "labels": [
        {"pair_id": "P1::L-1", "label": "pertinente", "importance": "alta"},
        {"pair_id": "P2::L-2", "label": "pertinente", "importance": "media"}]}


def _protocolo(tokens_in=None, tokens_out=None):
    return {"schema": "jev-pilot-protocolo/v1", "status": "BORRADOR",
            "rubrica": {"valores": ["pertinente", "no_pertinente", "insuficiente"],
                        "importancia": ["alta", "media", "baja"]},
            "modelos": {"jev_pin": PIN, "comparador": "DeepSeek", "excluido": "Anthropic"},
            "parametros": {"retry_policy": {"max_retries": 0}, "timeout_s": 30},
            "limites_gasto": {"usd": None, "llamadas": 12, "tokens_in": tokens_in,
                              "tokens_out": tokens_out, "motivo": "techo pendiente de medir"}}


def _indice():
    return {"lecciones": [
        {"id": "L-1", "enunciado": "texto frio uno", "plan": "P1", "total_citas": 3,
         "planes_que_lo_citan": ["OTRO-PLAN"]},
        {"id": "L-2", "enunciado": "otra leccion sin relation", "plan": "P2"},
        {"id": "L-3", "enunciado": "texto frio tambien parecido", "plan": "P3"}]}


def _preflight(jev="AUTENTICADA", provisional=True, sdk_instalado=True):
    return {"schema": "jev-pilot-preflight/v1", "proveedores": {
        "jev": {"habilitacion_declarada": provisional, "sdk_instalado": sdk_instalado,
                "autenticacion_real": jev, "cuota_o_saldo": "NO-DISPONIBLE-POR-SDK"},
        "deepseek": {"habilitacion_declarada": True, "sdk_instalado": True,
                     "autenticacion_real": "AUTENTICADA", "cuota_o_saldo": None}}}


def _armar(tmp_path, runner, *, muestra=None, protocolo=None, preflight=None, indice=None,
           con_preflight=True):
    raiz = tmp_path / "p"
    raiz.mkdir(parents=True, exist_ok=True)
    (raiz / "muestra.json").write_text(
        json.dumps(muestra or _muestra()), encoding="utf-8")
    (raiz / "etiquetas.json").write_text(json.dumps(_etiquetas()), encoding="utf-8")
    (raiz / "protocolo.json").write_text(json.dumps(protocolo or _protocolo()), encoding="utf-8")
    (raiz / "indice.json").write_text(json.dumps(indice or _indice()), encoding="utf-8")
    if con_preflight:
        (raiz / "preflight.json").write_text(json.dumps(preflight or _preflight()),
                                             encoding="utf-8")
    kwargs = {"muestra": raiz / "muestra.json", "etiquetas": raiz / "etiquetas.json",
              "protocolo": raiz / "protocolo.json", "indice": raiz / "indice.json",
              "preflight": raiz / "preflight.json", "out_dir": tmp_path / "out",
              "proveedor": "jev", "k": 8, "splits": "dev"}
    return kwargs


def _payload(modelo=DEVUELTO, inp=1200, out=180):
    return {"modelo": modelo, "usage": {"input_tokens": inp, "output_tokens": out},
            "answers": {"P1::L-1": {"tipo": "choice", "choice": "L-1", "confidence": 0.71}},
            "request_id": "req-1"}


def _enviador():
    vistos = {"llamadas": []}

    def enviar(state, questions, modelo):
        vistos["llamadas"].append({"state": state, "questions": questions, "modelo": modelo})
        return _payload()
    return enviar, vistos


# ------------------------------------------------------------------ AC8: cero envios en cada corte

def test_sin_preflight_el_runner_no_envia_nada(tmp_path, runner):
    """AC12 como precondicion de AC8: sin preflight no se construye cliente ni se dispara uno."""
    kwargs = _armar(tmp_path, runner, con_preflight=False)
    enviar, vistos = _enviador()
    resultado = runner.run(**kwargs, enviar=enviar,
                           autorizacion_de_null={"declarada": True, "motivo": "medicion"})
    assert resultado["status"] == "NEGADO" and resultado["envios"] == 0
    assert resultado["motivos"] == [f"preflight-ausente:{kwargs['preflight'].as_posix()}"]
    assert enviar is not None and vistos["llamadas"] == [], (
        "el guard nego por escrito pero la funcion de envio se llamo igual")
    assert not (tmp_path / "out" / "ledger.jsonl").exists()


@pytest.mark.parametrize("jev, provisional, sdk_instalado, motivo_esperado", [
    ("NO-INTENTADA", True, True, "autenticacion_real"),
    (False, True, True, "autenticacion_real"),
    ("AUTENTICADA", False, True, "habilitacion_declarada"),
    ("AUTENTICADA", True, False, "sdk_instalado"),
])
def test_cada_estado_de_ac12_que_falta_corta_el_envio(tmp_path, runner, jev, provisional,
                                                     sdk_instalado, motivo_esperado):
    """Los cuatro estados de AC12 se comprueban uno por uno, y cada ausencia deja cero envios."""
    kwargs = _armar(tmp_path, runner,
                    preflight=_preflight(jev=jev, provisional=provisional,
                                         sdk_instalado=sdk_instalado))
    enviar, vistos = _enviador()
    resultado = runner.run(**kwargs, enviar=enviar,
                           autorizacion_de_null={"declarada": True, "motivo": "medicion"})
    assert resultado["status"] == "NEGADO" and vistos["llamadas"] == []
    assert any(motivo_esperado in m for m in resultado["motivos"]), resultado["motivos"]


def test_preflight_de_otro_proveedor_no_autoriza_este(tmp_path, runner):
    """AC12 es por proveedor: un preflight que solo trae `deepseek` no habilita el brazo `jev`."""
    datos = _preflight()
    datos["proveedores"] = {"deepseek": datos["proveedores"]["deepseek"]}
    kwargs = _armar(tmp_path, runner, preflight=datos)
    enviar, vistos = _enviador()
    resultado = runner.run(**kwargs, enviar=enviar,
                           autorizacion_de_null={"declarada": True, "motivo": "medicion"})
    assert any("jev" in m for m in resultado["motivos"]) and vistos["llamadas"] == []


# ------------------------------------------- REL-1 (dictado D4, 2026-10-05): la declaracion NO-APLICA

NO_APLICA_HONESTO = ("NO-APLICA: el comparador es un API HTTP, no un SDK; el contrato del brazo es "
                     "`evaluar(state, preguntas)` de scripts/proveedores/deepseek.py")

# Formas que NO excuses nada: el literal pelado, el literal con separador y nada despues, otra palabra
# que empieza igual y las minusculas. Los tres estados que el dictado manda seguir cortando (ausente,
# None, cualquier otro valor) van a parte.
NO_APLICA_INVALIDOS = [
    ("NO-APLICA", "el literal sin motivo"),
    ("NO-APLICA:", "el separador sin motivo"),
    ("NO-APLICA   ", "solo espacios despues"),
    ("NO-APLICABLE: el brazo no usa SDK", "otra palabra que empieza igual"),
    ("no-aplica: el brazo no usa SDK", "minusculas: el literal es NO-APLICA"),
    ("NO", "otro literal"),
    (1, "un entero que se parece a True"),
    (0, "cero"),
    ("True", "el booleano escrito como texto"),
]


def _preflight_de(proveedor, valor, *, omitir=False):
    """El registro de UN proveedor con `sdk_instalado` puesto (o quitado); el otro queda intacto."""
    datos = _preflight()
    registro = datos["proveedores"][proveedor]
    if omitir:
        registro.pop("sdk_instalado")
    else:
        registro["sdk_instalado"] = valor
    return datos


def _preflight_de_deepseek(sdk_instalado=None, **otros):
    datos = _preflight()
    datos["proveedores"]["deepseek"]["sdk_instalado"] = sdk_instalado
    datos["proveedores"]["deepseek"].update(otros)
    return datos


def _escribir_preflight(tmp_path, datos):
    ruta = tmp_path / "preflight.json"
    ruta.write_text(json.dumps(datos), encoding="utf-8")
    return ruta


def test_no_aplica_con_motivo_escusa_el_estado_y_la_excusa_queda_publicada(tmp_path, runner):
    """VERDE de D4: el brazo que escribe su motivo pasa, y la excusa no es silenciosa."""
    ruta = _escribir_preflight(tmp_path, _preflight_de("deepseek", NO_APLICA_HONESTO))
    res = runner.revisar_preflight(ruta, "deepseek")
    assert res["ok"] is True and res["motivos"] == [], res["motivos"]
    assert res["no_aplica_declarados"]["sdk_instalado"].startswith(
        "el comparador es un API HTTP"), res["no_aplica_declarados"]


def test_el_guard_no_corta_el_run_cuando_el_brazo_declara_no_aplica_con_motivo(tmp_path, runner):
    """El brazo se corta o no se corta **en el `run`**: aca no se corta y hay un envio."""
    kwargs = _armar(tmp_path, runner, preflight=_preflight_de("jev", NO_APLICA_HONESTO))
    enviar, vistos = _enviador()
    resultado = runner.run(**kwargs, enviar=enviar,
                           autorizacion_de_null={"declarada": True, "motivo": "medicion"})
    assert resultado["status"] == "OK" and resultado["envios"] == 1
    assert len(vistos["llamadas"]) == 1


def test_no_aplica_sin_motivo_corta_el_run_y_no_envia_nada(tmp_path, runner):
    """ROJO de D4 con la causa nombrada: `NO-APLICA` pelado es la ausencia con mejor cara."""
    kwargs = _armar(tmp_path, runner, preflight=_preflight_de("jev", "NO-APLICA"))
    enviar, vistos = _enviador()
    resultado = runner.run(**kwargs, enviar=enviar,
                           autorizacion_de_null={"declarada": True, "motivo": "medicion"})
    assert resultado["status"] == "NEGADO" and vistos["llamadas"] == []
    assert any("sdk_instalado='NO-APLICA'" in m for m in resultado["motivos"]), resultado["motivos"]


@pytest.mark.parametrize("valor, porque", NO_APLICA_INVALIDOS)
def test_cada_forma_que_no_es_declaracion_valida_sigue_cortando(tmp_path, runner, valor, porque):
    """D4 por el lado contrario: solo se excusa el literal del brazo, con su motivo escrito."""
    ruta = _escribir_preflight(tmp_path, _preflight_de("deepseek", valor))
    res = runner.revisar_preflight(ruta, "deepseek")
    assert res["ok"] is False, f"se colo una excusa invalida ({porque}): {res}"
    assert any("sdk_instalado" in m for m in res["motivos"]), (porque, res["motivos"])
    assert res.get("no_aplica_declarados", {}) == {}, (porque, res["no_aplica_declarados"])


def test_estado_ausente_del_registro_sigue_cortando(tmp_path, runner):
    """D4 nombra el valor ausente: quitar la clave no es declararla inaplicable."""
    ruta = _escribir_preflight(tmp_path, _preflight_de("deepseek", None, omitir=True))
    res = runner.revisar_preflight(ruta, "deepseek")
    assert res["ok"] is False
    assert "preflight-sdk_instalado=None" in res["motivos"], res["motivos"]
    assert res["no_aplica_declarados"] == {}


def test_la_excusa_no_cubre_un_estado_que_si_corta(tmp_path, runner):
    """La excusa es por estado: un `NO-APLICA` valido no salva la habilitacion que falta."""
    ruta = _escribir_preflight(tmp_path, _preflight_de_deepseek(NO_APLICA_HONESTO,
                                                                habilitacion_declarada=False))
    res = runner.revisar_preflight(ruta, "deepseek")
    assert res["ok"] is False
    assert res["motivos"] == ["preflight-habilitacion_declarada=False"], res["motivos"]
    assert "sdk_instalado" in res["no_aplica_declarados"], res["no_aplica_declarados"]


def test_el_preflight_versionado_de_fase_c_ya_no_corta_el_comparador(tmp_path, runner):
    """H14 medido sobre el artefacto que lo produjo, no sobre un fixture que lo imita.

    El crudo `FASE-RELEASE/19-ac12-revisar-preflight-y-ac6-guard-real.txt` estampó
    `deepseek -> ok: false` con el motivo `preflight-sdk_instalado='NO-APLICA: ...'`. Ese valor es
    declaracion valida, asi que el brazo pasa; `jev` pasa como siempre y `anthropic` sigue cortado por
    sus tres estados ausentes, que son la exclusion declarada del plan, no una inaplicacion.
    """
    raiz = Path(__file__).resolve().parents[3]
    ruta = (raiz / "evidence" / "EVALUACION-JEV-TYPESAFE-2026-09-21"
            / "FASE-C" / "preflight.json")
    assert ruta.exists(), f"el artefacto ancla se movio: {ruta}"

    jev = runner.revisar_preflight(ruta, "jev")
    assert jev["ok"] is True and jev["no_aplica_declarados"] == {}, jev["motivos"]

    dee = runner.revisar_preflight(ruta, "deepseek")
    assert dee["ok"] is True, dee["motivos"]
    assert set(dee["no_aplica_declarados"]) == {"sdk_instalado"}, dee["no_aplica_declarados"]

    anth = runner.revisar_preflight(ruta, "anthropic")
    assert anth["ok"] is False
    assert anth["motivos"] == ["preflight-habilitacion_declarada=False",
                               "preflight-sdk_instalado=None",
                               "preflight-autenticacion_real=None"], anth["motivos"]
    assert anth["no_aplica_declarados"] == {}


def test_presupuesto_agotado_no_envia_y_el_ledger_no_aparece(tmp_path, runner):
    """AC8: la cuenta persistida manda. Llamadas agotadas = cero envios, sin tocar el transporte."""
    kwargs = _armar(tmp_path, runner)
    out = kwargs["out_dir"]
    out.mkdir(parents=True, exist_ok=True)
    (out / "consumo.json").write_text(json.dumps({"llamadas_usadas": 12, "intentos": 12}),
                                      encoding="utf-8")
    enviar, vistos = _enviador()
    resultado = runner.run(**kwargs, enviar=enviar,
                           autorizacion_de_null={"declarada": True, "motivo": "medicion"})
    assert resultado["motivos"] == ["llamadas_agotadas"] and resultado["envios"] == 0
    assert vistos["llamadas"] == []


def test_techo_de_tokens_null_sin_autorizacion_bloquea_y_conella_se_envia(tmp_path, runner):
    """AC8/protocolo: los dos null del protocolo bloquean; la autorizacion del operador los levanta."""
    kwargs = _armar(tmp_path, runner)
    enviar, vistos = _enviador()
    bloqueado = runner.run(**kwargs, enviar=enviar)
    assert bloqueado["status"] == "NEGADO"
    assert bloqueado["motivos"] == ["techo_de_tokens_in_sin_declarar",
                                   "techo_de_tokens_out_sin_declarar"]
    assert vistos["llamadas"] == []

    autorizada = runner.run(**kwargs, enviar=enviar,
                            autorizacion_de_null={"declarada": True,
                                                  "motivo": "corrida k=8, operador 2026-10-03"})
    assert autorizada["status"] == "OK" and autorizada["envios"] == 1
    assert len(vistos["llamadas"]) == 1


def test_muestra_sin_congelar_no_se_envia(tmp_path, runner):
    """La muestra es CONGELADA o no hay corrida: un BORRADOR daria una medicion sin insumo fijo."""
    kwargs = _armar(tmp_path, runner, muestra=_muestra("BORRADOR"))
    enviar, vistos = _enviador()
    resultado = runner.run(**kwargs, enviar=enviar,
                           autorizacion_de_null={"declarada": True, "motivo": "x"})
    assert resultado["motivos"] == ["muestra-no-congelada"] and vistos["llamadas"] == []


def test_proveedor_no_autorizado_se_niega_sin_importar_el_sdk(tmp_path, runner):
    """AC11/AC8: `run` con un proveedor que no esta en la lista se niega antes de tocar cualquier import."""
    kwargs = _armar(tmp_path, runner)
    kwargs["proveedor"] = "anthropic"
    real = builtins.__import__

    def guardado(name, *a, **kw):
        root = name.split(".")[0]
        if name in runner.FORBIDDEN_MODULES or root in runner.FORBIDDEN_MODULES:
            raise AssertionError(f"el runner intento importar cliente/red: {name}")
        return real(name, *a, **kw)

    builtins.__import__ = guardado
    try:
        resultado = runner.run(**kwargs, enviar=lambda *a: _payload(),
                               autorizacion_de_null={"declarada": True, "motivo": "x"})
    finally:
        builtins.__import__ = real
    assert resultado["envios"] == 0 and "anthropic" in resultado["motivos"][0]


def test_deepseek_no_es_un_camino_del_runner(tmp_path, runner):
    """El comparador se despacha por la costura; el runner lo niega en vez de duplicar la puerta."""
    kwargs = _armar(tmp_path, runner)
    kwargs["proveedor"] = "deepseek"
    enviar, vistos = _enviador()
    resultado = runner.run(**kwargs, enviar=enviar,
                           autorizacion_de_null={"declarada": True, "motivo": "x"})
    assert resultado["status"] == "NEGADO" and vistos["llamadas"] == []
    assert any("costura" in m for m in resultado["motivos"])


# ------------------------------------------------------------------ el ledger, por llamada y por intento

def test_el_run_persiste_una_linea_por_llamada_con_los_tres_campos(tmp_path, runner):
    """AC8/AC4: el ledger guarda `attempts`, `error_kind`/`usage_normalized` y el modelo DEVUELTO."""
    kwargs = _armar(tmp_path, runner)
    enviar, vistos = _enviador()
    resultado = runner.run(**kwargs, enviar=enviar,
                           autorizacion_de_null={"declarada": True, "motivo": "medicion"})
    lineas = [json.loads(l) for l in
              (tmp_path / "out" / "ledger.jsonl").read_text(encoding="utf-8").splitlines() if l]
    assert len(lineas) == 1, "un par elegible en `dev` debe dejar exactamente una linea"
    fila = lineas[0]
    assert fila["attempts"] >= 1
    assert fila["error_kind"] is None, "una llamada exitosa no puede quedar clasificada como fallo"
    assert fila["usage_normalized"]["estado"] == "observado"
    assert fila["usage_normalized"]["input_tokens"] == 1200
    assert fila["modelo_efectivo"] == "jev-9.9.9" != fila["modelo_solicitado"]
    assert fila["pair_id"] == "P1::L-1" and fila["split"] == "dev"
    assert resultado["cuenta"]["llamadas_usadas"] == 1
    assert resultado["modelos_efectivos"] == ["jev-9.9.9"]


def test_un_fallo_del_transporta_deja_el_ledger_con_su_error_kind_y_sin_coste_cero(tmp_path, runner):
    """DA-C3/AC10: un fallo se registra como fallo; el uso sigue sin observar y la reserva no se libera."""
    kwargs = _armar(tmp_path, runner)

    def explotar(state, questions, modelo):
        raise RuntimeError("el transporte se cae")

    resultado = runner.run(**kwargs, enviar=explotar,
                           autorizacion_de_null={"declarada": True, "motivo": "medicion"})
    fila = json.loads((tmp_path / "out" / "ledger.jsonl").read_text(encoding="utf-8").strip())
    assert fila["attempts"] == 1 and fila["estado"] == "FALLO"
    assert fila["error_kind"] == "desconocido" and fila["usage_normalized"]["total"] is None
    assert fila["usage_normalized"]["libera_reserva_como_cero"] is False
    assert resultado["envios"] == 1, "un envio que fallo es un envio gastado, no un cero contable"


def test_la_segunda_corrida_en_la_misma_cuenta_para_por_presupuesto(tmp_path, runner):
    """El techo de llamadas se lee del disco entre corridas: la segunda no puede pasarse del rango."""
    kwargs = _armar(tmp_path, runner)
    protocolo = _protocolo()
    protocolo["limites_gasto"]["llamadas"] = 1
    (kwargs["protocolo"]).write_text(json.dumps(protocolo), encoding="utf-8")
    enviar, vistos = _enviador()
    primera = runner.run(**kwargs, enviar=enviar,
                         autorizacion_de_null={"declarada": True, "motivo": "medicion"})
    segunda = runner.run(**kwargs, enviar=enviar,
                         autorizacion_de_null={"declarada": True, "motivo": "medicion"})
    assert primera["envios"] == 1 and segunda["envios"] == 0
    assert segunda["motivos"] == ["llamadas_agotadas"]
    assert len(vistos["llamadas"]) == 1, "la cuenta persistida no detuvo el segundo envio"


# ------------------------------------------------------------------- la capa fria y sus limites

def test_la_capa_fria_solo_lleva_id_y_enunciado(tmp_path, runner):
    """AC3: `planes_que_lo_citan` y las fechas de aceptacion no entran al input que ven los modelos."""
    fria = runner.recuperacion_fria("texto frio uno", _indice()["lecciones"], k=8)
    assert fria["candidatos"], "una capa fria sin candidatos no ejercita nada"
    for c in fria["candidatos"]:
        assert set(c) == {"id", "enunciado"}, f"el candidato filtro metadatos: {sorted(c)}"
    assert fria["k"] == 8 and fria["poblacion"] == 3
    assert fria["candidatos"][0]["id"] == "L-1", "la leccion propia del enunciado debe ir primera"


def test_el_recorte_de_k_es_determinista_y_publica_su_desempate(tmp_path, runner):
    """Regla congelada: similitud descendente y, a igualdad, id ascendente. Sin azar ni estado."""
    lecciones = [{"id": "B", "enunciado": "texto X"}, {"id": "A", "enunciado": "texto X"},
                 {"id": "C", "enunciado": "texto X"}]
    first = runner.recuperacion_fria("texto X", lecciones, k=2)
    second = runner.recuperacion_fria("texto X", lecciones, k=2)
    assert [c["id"] for c in first["candidatos"]] == ["A", "B"]
    assert first == second, "la regla fria no es determinista: la corrida no es reproducible"


def test_recuperacion_medida_publica_denominador_y_cero_es_no_evaluable(tmp_path, runner):
    """Metrica 1 con valores conocidos (AC10) y denominador cero como NO-EVALUABLE, no como 100 %."""
    muestra, etiquetas = _muestra(), _etiquetas()
    filas = [{"pair_id": "P1::L-1", "leccion_target_en_candidatos": True},
             {"pair_id": "P2::L-2", "leccion_target_en_candidatos": False}]
    medida = runner.recuperacion_medida(muestra, etiquetas, filas)
    assert medida == {"value": 0.5, "numerator": 1, "denominator": 2, "motivo": "",
                      "presentes": ["P1::L-1"], "elegibles": ["P1::L-1", "P2::L-2"],
                      "medidos": ["P1::L-1", "P2::L-2"], "sin_medir": []}

    sin_elegibles = runner.recuperacion_medida(
        muestra, {"labels": [{"pair_id": "P1::L-1", "label": "no_pertinente",
                              "importance": None}]}, filas)
    assert sin_elegibles["value"] is None and sin_elegibles["motivo"] == "denominador_cero"
    assert sin_elegibles["denominator"] == 0


def test_un_elegible_sin_fila_en_el_ledger_no_es_fallo_de_recuperacion(tmp_path, runner):
    """El rojo falso que esta prueba cierra: un elegible que esta corrida no despacho NO se cuenta como omision.

    Pasa tal cual en la corrida k=8 del 2026-10-03: los dos pares pertinentes-importantes del
    protocolo versionado viven en `eval`, y la corrida despacho `dev`. Sin este desglose el cociente
    salia 0.0 y acusaba a la capa fria de no recuperar nada, cuando lo que faltaba era la medida.
    """
    muestra, etiquetas = _muestra(), _etiquetas()
    sin_filas = runner.recuperacion_medida(muestra, etiquetas, [])
    assert sin_filas["value"] is None
    assert sin_filas["denominator"] == 0 and sin_filas["numerator"] == 0
    assert sorted(sin_filas["sin_medir"]) == ["P1::L-1", "P2::L-2"]
    assert "denominador_cero" in sin_filas["motivo"]

    mitad = runner.recuperacion_medida(
        muestra, etiquetas,
        [{"pair_id": "P1::L-1", "leccion_target_en_candidatos": False}])
    assert mitad["numerator"] == 0 and mitad["denominator"] == 1 and mitad["value"] == 0.0
    assert mitad["sin_medir"] == ["P2::L-2"]
    assert "no medidos, no fallados" in mitad["motivo"], mitad["motivo"]


def test_una_leccion_importante_ausente_de_candidatos_baja_la_recuperacion(tmp_path, runner):
    """El diente del lado contrario: si la fria no la trajo, el numerador no se infla solo.

    Con los dos pares importantes elegibles y ninguno presente entre candidatos, el cociente es 0/2
    y vale 0.0: la ausencia no se vuelve denominador cero ni `NO-EVALUABLE`.
    """
    muestra = _muestra()
    muestra["pairs"][0]["lesson_id"] = "L-QUE-NADIE-TRAE"
    filas = [{"pair_id": "P1::L-1", "leccion_target_en_candidatos": False},
             {"pair_id": "P2::L-2", "leccion_target_en_candidatos": False}]
    medida = runner.recuperacion_medida(muestra, _etiquetas(), filas)
    assert medida["numerator"] == 0 and medida["denominator"] == 2 and medida["value"] == 0.0
    assert medida["motivo"] == "" and medida["presentes"] == []


# ------------------------------------------------ B2-1e: el techo ya rebasado corta el siguiente envio

def _limites(techo_in=1834, techo_out=139, declarada=True):
    return {"llamadas": 12, "tokens_in": techo_in, "tokens_out": techo_out, "usd": None,
            "max_reintentos": 0, "timeout_s": 30,
            "autorizacion_de_null": {"declarada": declarada, "motivo": "medicion"}}


def _cuenta(uso_in=1778, uso_out=145, llamadas=1):
    return {"llamadas_usadas": llamadas, "intentos": llamadas, "usage_estados": [],
            "tokens_in_max": uso_in, "tokens_out_max": uso_out}


@pytest.fixture
def runner_fresco_b21e():
    """Modulo recargado por test: el mutante apaga un simbolo y no puede compartir instancia con
    los que leen el arbol versionado (leccion del conftest de la seleccion hermana)."""
    import importlib.util

    ruta = Path(__file__).resolve().parents[3] / "scripts" / "evaluate_jev_pilot.py"
    spec = importlib.util.spec_from_file_location("evaluate_jev_pilot_mutante_guards", ruta)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_un_techo_rebasado_en_la_cuenta_corta_el_siguiente_envio(runner):
    """B2-1e: 145 contra el techo congelado de 139 agota la reserva ANTES del proximo intento.

    Maestro §115: si la contabilidad ya no acota, la corrida se detiene. El exceso del envio N no se
    podia predecir antes de N, pero dejar pasar el N+1 es gastar contra un presupuesto rebasado.
    """
    reserva = runner.reservar_presupuesto(_cuenta(), _limites())
    assert reserva["reservado"] is False
    assert reserva["motivos"] == ["techo_rebasado_de_tokens_out:145>139"], reserva["motivos"]
    assert reserva["exceso_observado"] == [{"campo": "tokens_out", "techo": 139, "observado": 145}]
    assert reserva["llamadas_restantes"] == 11, "las llamadas no se agotaron: lo que se agoto fue el techo"


def test_el_valor_igual_al_techo_no_es_exceso(runner):
    """Frontera `>` y no `>=`: 139 contra 139 reserva. Un `>=` cortaria una corrida legal."""
    assert runner.reservar_presupuesto(_cuenta(uso_out=139), _limites())["reservado"] is True


def test_techo_null_no_inventa_un_corte(runner):
    """Sin techo no hay rebasamiento que declarar: la cuenta con 145 sigue reservando."""
    reserva = runner.reservar_presupuesto(_cuenta(), _limites(techo_in=None, techo_out=None))
    assert reserva["reservado"] is True
    assert reserva["motivos"] == [] and reserva["exceso_observado"] == []


def test_un_booleen_en_la_cuenta_no_es_un_token_de_uno(runner):
    """El mismo error de tipo que el guard de preflight ya curó: `True` no es 1 token."""
    cuenta = _cuenta(uso_in=None, uso_out=None)
    cuenta["tokens_out_max"] = True
    reserva = runner.reservar_presupuesto(cuenta, _limites(techo_out=1))
    assert reserva["reservado"] is True, "un flag no es una medida de tokens"


def test_los_dos_campos_rebasados_se_publican_los_dos(runner):
    """No se corta por el primero y se olvida el segundo: la reserva nombra los dos techos rotos."""
    reserva = runner.reservar_presupuesto(_cuenta(uso_in=2000, uso_out=145),
                                          _limites(techo_in=1834, techo_out=139))
    assert reserva["motivos"] == ["techo_rebasado_de_tokens_in:2000>1834",
                                  "techo_rebasado_de_tokens_out:145>139"], reserva["motivos"]
    assert [e["campo"] for e in reserva["exceso_observado"]] == ["tokens_in", "tokens_out"]


def test_el_segundo_par_se_niega_cuando_el_primero_paso_el_techo(tmp_path, runner):
    """El guard existe si alguien lo dispara: con `enviar` inyectado, el par 2 queda NO-EJERCITADO.

    Poblacion a mano: dos pares (`dev,eval`), techo de salida 139, el transporte falso devuelve 145
    en cada envio. Esperable: 1 envio, 1 fila negada con su motivo, cuenta en 1 llamada.
    """
    kwargs = _armar(tmp_path, runner, protocolo=_protocolo(tokens_in=1834, tokens_out=139))
    kwargs["splits"] = "dev,eval"
    vistos = {"llamadas": 0}

    def enviar(state, questions, modelo):
        vistos["llamadas"] += 1
        return _payload(out=145)

    resultado = runner.run(**kwargs, enviar=enviar)
    assert resultado["status"] == "OK" and resultado["envios"] == 1
    assert vistos["llamadas"] == 1, "el segundo par no pudo llamar al transporte"
    assert resultado["cuenta"]["llamadas_usadas"] == 1
    assert resultado["cuenta"]["tokens_out_max"] == 145
    filas = [json.loads(l) for l in (tmp_path / "out" / "ledger.jsonl")
             .read_text(encoding="utf-8").splitlines() if l]
    assert len(filas) == 2
    assert filas[0]["estado"] == "EJERCITADO" and filas[0]["usage_normalized"]["output_tokens"] == 145
    assert filas[1]["estado"] == "NO-EJERCITADO"
    assert filas[1]["motivos"] == ["techo_rebasado_de_tokens_out:145>139"], filas[1]["motivos"]


def test_una_cuenta_persistida_con_techo_rebasado_negada_toda_la_corrida(tmp_path, runner):
    """El corte also vive entre sesiones: `consumo.json` con 145 contra techo 139 niega el `run` entero."""
    kwargs = _armar(tmp_path, runner, protocolo=_protocolo(tokens_in=1834, tokens_out=139))
    out = kwargs["out_dir"]
    out.mkdir(parents=True, exist_ok=True)
    (out / "consumo.json").write_text(json.dumps(_cuenta(uso_in=1778, uso_out=145, llamadas=2)),
                                      encoding="utf-8")
    enviados = {"n": 0}

    def enviar(state, questions, modelo):
        enviados["n"] += 1
        return _payload(out=100)

    resultado = runner.run(**kwargs, enviar=enviar)
    assert resultado["status"] == "NEGADO" and resultado["envios"] == 0
    assert resultado["motivos"] == ["techo_rebasado_de_tokens_out:145>139"]
    assert enviados["n"] == 0, "NEGADO tiene que ser cero transporte, no una etiqueta"
    assert not (out / "ledger.jsonl").exists(), "negado antes de cualquier fila"


def test_si_el_protocolo_no_lleva_los_techos_el_corte_muere(runner_fresco_b21e, tmp_path):
    """Contrafactual de cableado (M3): si `limites_desde_protocolo` no baja los techos, el guard es letra muerta.

    Se apaga el transportador y el segundo par se envia: asi el diente de arriba prueba el corte y
    este prueba que el corte depende del traslado, no de una casualidad del fixture.
    """
    import copy

    def limites_ciegos(protocolo, *, autorizacion_de_null=None):
        return {"llamadas": 12, "tokens_in": None, "tokens_out": None, "usd": None,
                "max_reintentos": 0, "timeout_s": 30,
                "autorizacion_de_null": {"declarada": True, "motivo": "medicion"}}

    original = copy.copy(runner_fresco_b21e.limites_desde_protocolo)
    runner_fresco_b21e.limites_desde_protocolo = limites_ciegos
    try:
        kwargs = _armar(tmp_path, runner_fresco_b21e,
                        protocolo=_protocolo(tokens_in=1834, tokens_out=139))
        kwargs["splits"] = "dev,eval"
        vistos = {"llamadas": 0}

        def enviar(state, questions, modelo):
            vistos["llamadas"] += 1
            return _payload(out=145)

        resultado = runner_fresco_b21e.run(**kwargs, enviar=enviar)
        assert vistos["llamadas"] == 2, "sin techos trasladados el guard no corta nada"
        assert resultado["envios"] == 2
    finally:
        runner_fresco_b21e.limites_desde_protocolo = original
    restaurado = runner_fresco_b21e.reservar_presupuesto(_cuenta(), _limites())
    assert restaurado["reservado"] is False, "la restauracion se verifica, no se asume"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
