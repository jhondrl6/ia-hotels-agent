# -*- coding: utf-8 -*-
"""Dientes de B2-1d: la cuenta de etapa se publica en el acto en que se suma (2026-10-09).

Deuda cerrada: la cuenta de etapa la persistia solo `run`, y un brazo despachado por un arnes
sumaba la misma aritmetica en su memoria sin escribir `consumo.json`. El hallazgo, medido sobre
los artefactos versionados de FASE-C (crudo `CURA-B2-1-2026-10-09/05-`, ancla en `T7`):

| cuenta                                   | llamadas | tokens_out_max |
|------------------------------------------|----------|----------------|
| `FASE-C/consumo.json` (la publicada)     | 2        | 145            |
| `FASE-C/registro_deepseek.json` al salir | 4        | 158            |

O sea: la cuenta publicada se quedo en la foto del primer brazo. La cura es una sola funcion,
`registrar_envio_en_cuenta`, que suma y publica juntas; `run` la usa y un arnes que cuente tiene
que usar la misma, asi que contar sin quedarse en disco deja de ser un camino. No se toca la
puerta del comparador (`decision_client`) ni `modules/providers/llm_provider.py`.

Todo es offline: el envio se inyecta (`enviar=`), el guard de sockets del `conftest.py` esta armado
por fixture autouse, y el unico insumo real que se lee es el versionado de FASE-C (solo lectura).

Poblaciones a mano, junto a cada asercion. La del par principal (`T2`) reproduce las cifras reales:
brazo jev 2 envios con salida 145, arnes comparador 2 envios con salida 158.
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
CONSUMO_C = EVID / "FASE-C" / "consumo.json"
REGISTRO_DS_C = EVID / "FASE-C" / "registro_deepseek.json"

PIN = "jev-1.13.0"
DEVUELTO = "jev-9.9.9"
CLAVES_CUENTA = {"llamadas_usadas", "intentos", "usage_estados",
                 "tokens_in_max", "tokens_out_max"}


# ------------------------------------------------------------------ insumos sinteticos

def _muestra(n_pares: int = 2) -> dict:
    pares = [{"pair_id": f"P{i}::L-{i}", "target_plan": f"P{i}", "lesson_id": f"L-{i}",
              "input_fragment": f"texto frio {i}", "split": ("dev" if i == 1 else "eval")}
             for i in range(1, n_pares + 1)]
    return {"schema": "jev-pilot-muestra/v1", "status": "CONGELADA", "pairs": pares,
            "counts": {"total": n_pares, "dev": 1, "eval": n_pares - 1, "excluidos": 0}}


def _etiquetas() -> dict:
    return {"schema": "jev-pilot-etiquetas/v1", "labels": [
        {"pair_id": "P1::L-1", "label": "pertinente", "importance": "alta"},
        {"pair_id": "P2::L-2", "label": "pertinente", "importance": "media"}]}


def _protocolo(techo_in=2000, techo_out=200) -> dict:
    return {"schema": "jev-pilot-protocolo/v1", "status": "CONGELADA",
            "rubrica": {"valores": ["pertinente", "no_pertinente", "insuficiente"],
                        "importancia": ["alta", "media", "baja"]},
            "modelos": {"jev_pin": PIN, "comparador": "DeepSeek", "excluido": "Anthropic"},
            "parametros": {"retry_policy": {"max_retries": 0}, "timeout_s": 30},
            "limites_gasto": {"usd": None, "llamadas": 12, "tokens_in": techo_in,
                              "tokens_out": techo_out,
                              "motivo": "corta por techo solo donde el test lo dice"}}


def _indice() -> dict:
    return {"lecciones": [
        {"id": "L-1", "enunciado": "texto frio 1", "plan": "P1", "total_citas": 3,
         "planes_que_lo_citan": ["OTRO-PLAN"]},
        {"id": "L-2", "enunciado": "texto frio 2", "plan": "P2"}]}


def _preflight() -> dict:
    return {"schema": "jev-pilot-preflight/v1", "proveedores": {
        "jev": {"habilitacion_declarada": True, "sdk_instalado": True,
                "autenticacion_real": "AUTENTICADA", "cuota_o_saldo": "NO-DISPONIBLE-POR-SDK"},
        "deepseek": {"habilitacion_declarada": True, "sdk_instalado": "NO-APLICA: sin SDK",
                     "autenticacion_real": "AUTENTICADA", "cuota_o_saldo": None}}}


def _armar(tmp_path, *, n_pares=2, splits="dev,eval", protocolo=None) -> dict:
    raiz = tmp_path / "p"
    raiz.mkdir(parents=True, exist_ok=True)
    (raiz / "muestra.json").write_text(json.dumps(_muestra(n_pares)), encoding="utf-8")
    (raiz / "etiquetas.json").write_text(json.dumps(_etiquetas()), encoding="utf-8")
    (raiz / "protocolo.json").write_text(json.dumps(protocolo or _protocolo()), encoding="utf-8")
    (raiz / "indice.json").write_text(json.dumps(_indice()), encoding="utf-8")
    (raiz / "preflight.json").write_text(json.dumps(_preflight()), encoding="utf-8")
    return {"muestra": raiz / "muestra.json", "etiquetas": raiz / "etiquetas.json",
            "protocolo": raiz / "protocolo.json", "indice": raiz / "indice.json",
            "preflight": raiz / "preflight.json", "out_dir": tmp_path / "out",
            "proveedor": "jev", "k": 2, "splits": splits}


def _payload(inp=1200, out=100) -> dict:
    return {"modelo": DEVUELTO, "usage": {"input_tokens": inp, "output_tokens": out},
            "answers": {"P1::L-1": {"tipo": "choice", "choice": "L-1", "confidence": 0.71}},
            "request_id": "req-1"}


def _transporte(tok_in=1200, tok_out=100, muere_en=None):
    """Transporte inyectado: cuenta sus envios y, si `muere_en` llega, revienta en ese envio."""
    vistos = {"n": 0}

    def enviar(state, questions, modelo):
        vistos["n"] += 1
        if vistos["n"] == muere_en:
            raise KeyboardInterrupt("el proceso muere a mitad de la corrida")
        return _payload(inp=tok_in, out=tok_out)
    enviar.vistos = vistos
    return enviar


def _fila_de_envio(mod, proveedor, tok_in, tok_out) -> dict:
    """Fila de ledger como la llena un arnes: `nuevo_ledger` + `registrar_intento` de la casa."""
    fila = mod.nuevo_ledger(proveedor, DEVUELTO)
    mod.registrar_intento(fila, resultado="exito", modelo_efectivo=DEVUELTO,
                          usage={"input_tokens": tok_in, "output_tokens": tok_out},
                          duracion_ms=12.5)
    return fila


def _leer(out_dir: Path) -> dict:
    return json.loads((out_dir / "consumo.json").read_text(encoding="utf-8"))


def _arnes(mod, out_dir: Path, envios: list) -> dict:
    """Un brazo despachado fuera de `run`: lee la cuenta publicada, la suma y la publica.

    `envios` es la lista de (proveedor, tokens_in, tokens_out). Devuelve la cuenta en memoria, que
    es lo que el arnes versionado estampaba en `cuenta_al_salir`.
    """
    cuenta = mod._estado_cuenta(out_dir)
    for proveedor, tok_in, tok_out in envios:
        fila = _fila_de_envio(mod, proveedor, tok_in, tok_out)
        mod.registrar_envio_en_cuenta(out_dir, cuenta, fila)
    return cuenta


def _conducta_previa_del_arnes(out_dir, cuenta, fila, *, nombre="consumo.json") -> dict:
    """El mutante que reproduce B2-1d: suma la misma aritmetica y NO escribe `consumo.json`.

    Es lo que hacia `FASE-C/12-arnes-correr-deepseek-eval.py`: reimplementaba la suma en su
    memoria y publicaba solo su propio registro. No borra el archivo publicado: no lo toca, que
    es como se queda atras de la cuenta real.
    """
    cuenta["llamadas_usadas"] += 1
    cuenta["intentos"] += fila["attempts"]
    uso = fila["usage_normalized"]
    if uso.get("input_tokens") is not None:
        cuenta["tokens_in_max"] = max(cuenta.get("tokens_in_max") or 0, uso["input_tokens"])
    if uso.get("output_tokens") is not None:
        cuenta["tokens_out_max"] = max(cuenta.get("tokens_out_max") or 0, uso["output_tokens"])
    if uso.get("estado") not in ("observado",):
        cuenta.setdefault("usage_estados", []).append(uso.get("estado"))
    return cuenta


@pytest.fixture
def runner_fresco_b21d():
    """Modulo recargado por test: los mutantes apagan un simbolo, no comparten instancia."""
    nombre = "evaluate_jev_pilot_mutante_cuenta_etapa"
    spec = importlib.util.spec_from_file_location(nombre, RUNNER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ------------------------------------------------------ T1: sumar y publicar, un solo acto

def test_registrar_envio_persiste_la_cuenta_en_el_mismo_acto(tmp_path, runner):
    """La cuenta en memoria y la que esta en disco salen de la misma llamada."""
    out = tmp_path / "out"
    cuenta = runner._estado_cuenta(out)
    assert cuenta["llamadas_usadas"] == 0 and cuenta["tokens_out_max"] is None
    fila = _fila_de_envio(runner, "jev", 1778, 145)
    devuelta = runner.registrar_envio_en_cuenta(out, cuenta, fila)
    publicado = _leer(out)
    # poblacion a mano: 1 envio, 1 intento, in_max 1778, out_max 145, usage observado
    assert publicado == {"llamadas_usadas": 1, "intentos": 1, "usage_estados": [],
                         "tokens_in_max": 1778, "tokens_out_max": 145}, publicado
    assert devuelta is cuenta, "muta la cuenta que recibe: no hay dos copias que puedan divergir"
    assert publicado == cuenta, "publicada e intra-memoria son el mismo dict"


def test_la_cuenta_persistida_mantiene_las_cinco_claves(tmp_path, runner):
    """Forma: lo que escribe la contabilidad tiene que ser lo que `_estado_cuenta` espera."""
    out = tmp_path / "out"
    cuenta = runner._estado_cuenta(out)
    runner.registrar_envio_en_cuenta(out, cuenta, _fila_de_envio(runner, "jev", 100, 50))
    assert set(_leer(out)) == CLAVES_CUENTA, sorted(_leer(out))
    assert set(runner._estado_cuenta(out)) == CLAVES_CUENTA
    assert runner._estado_cuenta(out) == _leer(out)


# ------------------------------------------------------ T2: el par verde del defecto

def test_un_arnes_de_brazo_no_deja_la_cuenta_publicada_atras(tmp_path, runner):
    """B2-1d curada: dos brazos, la cuenta publicada es la real (4 llamadas, salida maxima 158).

    Poblacion a mano, con las cifras medidas de FASE-C: brazo jev por `run` con 2 envios de salida
    145 (entrada 1778), luego un arnes comparador con 2 envios de salida 158 (entrada 1054). Antes
    de la cura el disco se quedaba en la foto del primer brazo (2 / 145); ahora dice 4 / 158.
    """
    kwargs = _armar(tmp_path, n_pares=2, splits="dev,eval")
    out = kwargs["out_dir"]
    enviar = _transporte(tok_in=1778, tok_out=145)
    primero = runner.run(**kwargs, enviar=enviar)
    assert primero["status"] == "OK" and primero["envios"] == 2
    despues = _arnes(runner, out, [("deepseek", 1054, 158), ("deepseek", 1000, 130)])
    publicado = _leer(out)
    assert publicado["llamadas_usadas"] == 4, publicado
    assert publicado["tokens_out_max"] == 158, publicado
    assert publicado["tokens_in_max"] == 1778, "la entrada maxima la sigue mandando el brazo jev"
    assert publicado == despues, "la cuenta_al_salir del arnes es lo que quedo en disco"


# ------------------------------------------------------ T3: el contrafactual del hallazgo

def test_sumar_sin_publicar_reproduce_la_divergencia_de_fase_c(
        tmp_path, runner_fresco_b21d):
    """Contrafactual: si la publicacion se separa de la suma, el disco vuelve a decir 2/145.

    Se apaga la escritura de `registrar_envio_en_cuenta` por la conducta del arnes versionado de
    FASE-C. Con el mutante: disco 2/145 contra memoria 4/158, la divergencia exacta del hallazgo.
    Restaurada la funcion, el mismo arnes deja el disco en 4/158 y publicada == real.
    """
    mod = runner_fresco_b21d
    kwargs = _armar(tmp_path, n_pares=2, splits="dev,eval")
    out = kwargs["out_dir"]
    original = copy.copy(mod.registrar_envio_en_cuenta)
    mod.registrar_envio_en_cuenta = _conducta_previa_del_arnes
    try:
        mod.run(**kwargs, enviar=_transporte(tok_in=1778, tok_out=145))
        # `run` cierra con su publicacion de fin de corrida: la foto del brazo jev
        memoria = _arnes(mod, out, [("deepseek", 1054, 158), ("deepseek", 1000, 130)])
        publicado = _leer(out)
        assert publicado["llamadas_usadas"] == 2, publicado
        assert publicado["tokens_out_max"] == 145, publicado
        assert memoria["llamadas_usadas"] == 4 and memoria["tokens_out_max"] == 158, memoria
        assert publicado != memoria, "el mutante fabrica la divergencia, no es un verde vacio"
    finally:
        mod.registrar_envio_en_cuenta = original
    restaurado = _arnes(mod, out, [("deepseek", 1054, 158), ("deepseek", 1000, 130)])
    publicado = _leer(out)
    # restaurada: el arnes corre sobre la cuenta ya publicada (2) -> 2 + 2 = 4, max(145, 158) = 158
    assert publicado["llamadas_usadas"] == 4 and publicado["tokens_out_max"] == 158, publicado
    assert publicado == restaurado, "la restauracion se verifica por el disco, no por el dict"


# ------------------------------------------------------ T4: no hay aritmetica duplicada

def test_el_run_no_reimplementa_la_aritmetica_de_la_cuenta(tmp_path, runner_fresco_b21d):
    """Un solo escritor: si la contabilidad de la casa no suma, `run` se queda en cero llamadas.

    `run` era el unico que hacia la suma en su propio cuerpo. Si aun la hiciera, el mutante daria 1
    envio con cuenta 1 y el diente perderia: esto prueba donde vive la aritmetica, no que exista.
    """
    mod = runner_fresco_b21d
    kwargs = _armar(tmp_path, n_pares=1, splits="dev")
    out = kwargs["out_dir"]
    llamadas = {"n": 0}

    def espia(out_dir, cuenta, fila, *, nombre="consumo.json"):
        llamadas["n"] += 1
        return cuenta  # no suma, no publica

    original = copy.copy(mod.registrar_envio_en_cuenta)
    mod.registrar_envio_en_cuenta = espia
    try:
        resultado = mod.run(**kwargs, enviar=_transporte())
        assert resultado["envios"] == 1
        assert llamadas["n"] == 1, "cada envio tiene que pasar por la contabilidad de la casa"
        assert resultado["cuenta"]["llamadas_usadas"] == 0, (
            "la cuenta avanzo sin la funcion: hay aritmetica duplicada dentro de `run`")
        assert _leer(out)["llamadas_usadas"] == 0
    finally:
        mod.registrar_envio_en_cuenta = original
    # restaurada la funcion, la segunda corrida vuelve a contar desde el 0 que dejo el mutante
    saneado = mod.run(**kwargs, enviar=_transporte())
    assert _leer(out)["llamadas_usadas"] == 1, "restaurada la funcion, el disco vuelve a contar"
    assert saneado["cuenta"]["llamadas_usadas"] == 1


# ------------------------------------------------------ T5: dureza entre sesiones

def test_una_caida_a_mitad_deja_en_disco_lo_que_ya_se_envio(tmp_path, runner):
    """AC8 entre sesiones: se persiste por envio, no al cerrar, asi un fallo no borra el gasto.

    Poblacion: 2 pares, el transporte falso revienta con `KeyboardInterrupt` en el segundo (es
    `BaseException`, o sea escapa al `except Exception` del runner). Esperable: 1 envio publicado.
    """
    kwargs = _armar(tmp_path, n_pares=2, splits="dev,eval")
    out = kwargs["out_dir"]
    enviar = _transporte(tok_in=1200, tok_out=100, muere_en=2)
    with pytest.raises(KeyboardInterrupt):
        runner.run(**kwargs, enviar=enviar)
    publicado = _leer(out)
    assert publicado["llamadas_usadas"] == 1 and publicado["tokens_out_max"] == 100, publicado
    cuenta = runner._estado_cuenta(out)
    assert cuenta == publicado, "el siguiente proceso lee lo que el caido dejo en disco"


def test_sin_publicacion_por_envio_la_caida_no_deja_cuenta(tmp_path, runner_fresco_b21d):
    """Control rojo de T5: con publicacion solo al cerrar, el mismo fallo no deja nada en disco."""
    mod = runner_fresco_b21d
    kwargs = _armar(tmp_path, n_pares=2, splits="dev,eval")
    out = kwargs["out_dir"]
    original = copy.copy(mod.registrar_envio_en_cuenta)
    enviar = _transporte(tok_in=1200, tok_out=100, muere_en=2)
    mod.registrar_envio_en_cuenta = _conducta_previa_del_arnes
    try:
        with pytest.raises(KeyboardInterrupt):
            mod.run(**kwargs, enviar=enviar)
        assert enviar.vistos["n"] == 2, "el envio 2 es el que muere: el 1 ya se conto"
        assert not (out / "consumo.json").exists(), (
            "si el disco apareciera igual, T5 estaria verde por otra razon")
    finally:
        mod.registrar_envio_en_cuenta = original
    con_cura = _arnes(mod, out, [("jev", 1200, 100)])
    assert _leer(out) == con_cura, "restaurada la funcion, volver a contar vuelve a publicar"


# ------------------------------------------------------ T6: las filas negadas no gastan

def test_las_filas_negadas_por_techo_no_suman_a_la_cuenta(tmp_path, runner):
    """B2-1e y B2-1d no se pisan: 1 envio publicado y 1 fila NO-EJERCITADO que no gasta cuenta."""
    kwargs = _armar(tmp_path, n_pares=2, splits="dev,eval", protocolo=_protocolo(1834, 139))
    out = kwargs["out_dir"]
    resultado = runner.run(**kwargs, enviar=_transporte(tok_in=1778, tok_out=145))
    assert resultado["envios"] == 1 and resultado["status"] == "OK"
    publicado = _leer(out)
    assert publicado["llamadas_usadas"] == 1, publicado
    assert publicado["tokens_out_max"] == 145, "el exceso se publica, no se esconde en la cuenta"
    lineas = (out / "ledger.jsonl").read_text(encoding="utf-8").splitlines()
    filas = [json.loads(texto) for texto in lineas if texto]
    assert len(filas) == 2 and filas[1]["estado"] == "NO-EJERCITADO"
    assert filas[1]["motivos"] == ["techo_rebasado_de_tokens_out:145>139"], filas[1]["motivos"]


# ------------------------------------------------------ T7: el ancla al artefacto versionado

def test_el_artefacto_versionado_de_fase_c_muestra_la_divergencia():
    """Procedencia de la deuda, leida del arbol: 2/145 publicados contra 4/158 reales.

    No se re-escribe FASE-C: la hoja esta cerrada y su evidencia es el crudo que fundo la fila
    B2-1d. Si alguien moviera esos artefactos, este diente avisa antes de que la nota de cura cite
    una cifra que ya no esta en disco.
    """
    assert CONSUMO_C.exists(), f"se movio el ancla: {CONSUMO_C}"
    publicado = json.loads(CONSUMO_C.read_text(encoding="utf-8"))
    registro = json.loads(REGISTRO_DS_C.read_text(encoding="utf-8"))
    assert (publicado["llamadas_usadas"], publicado["tokens_out_max"]) == (2, 145), publicado
    assert set(publicado) == CLAVES_CUENTA, sorted(publicado)
    cuenta_salir = registro["cuenta_al_salir"]
    assert (cuenta_salir["llamadas_usadas"], cuenta_salir["tokens_out_max"]) == (4, 158)
    assert registro["cuenta_al_entrar"] == publicado, "el arnes entro con la foto del brazo jev"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
