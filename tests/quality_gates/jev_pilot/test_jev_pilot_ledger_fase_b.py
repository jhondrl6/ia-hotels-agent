"""Tests offline de la pata (b) del runner (FASE-B, 2026-10-03).

`attempts`, `error_kind` y `usage_normalized` nacen aqui, en el ledger del piloto: la costura
declara que no le pertenecen. Nada de red ni de clientes: las funciones reciben objetos y
clasifican por nombre de clase, asi que se prueban con sustitutos que llevan el nombre real del
SDK. Cada control afirma su causa, no solo su etiqueta (L-V2.1, L-D5).
"""
from __future__ import annotations

import builtins
import importlib.util
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
_SCRIPT = _REPO_ROOT / "scripts" / "evaluate_jev_pilot.py"

_spec = importlib.util.spec_from_file_location("evaluate_jev_pilot", _SCRIPT)
ejv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ejv)


class Uso:
    """Sustituto con la forma medida de `typesafe_sdk.Usage`: ambos campos son `int | None`."""

    def __init__(self, input_tokens=None, output_tokens=None):
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens


def _tipo(nombre, bases=(Exception,), status=None):
    clase = type(nombre, bases, {})
    if status is not None:
        def __init__(self, *a, **k):
            Exception.__init__(self, nombre)
            self.status = status
        clase.__init__ = __init__
    return clase


def _limites_completos(**cambios):
    limites = {"llamadas": 12, "tokens_in": 40000, "tokens_out": 8000,
               "max_reintentos": 0, "timeout_s": 30}
    limites.update(cambios)
    return limites


# ------------------------------------------------------- el guard offline y su hueco medido

def test_el_guard_bloquea_el_nombre_real_del_sdk():
    """AC11: la lista prohibida debe nombrar el modulo que EXISTE, no solo el que suena.

    Medido el 2026-10-03: el paquete se importa como `typesafe_sdk` (distribucion `typesafe-sdk`);
    `import typesafe` da ModuleNotFoundError. Con la lista vieja, el nombre real pasaba libre.
    """
    assert "typesafe_sdk" in ejv.FORBIDDEN_MODULES
    assert "typesafe-sdk" in ejv.FORBIDDEN_MODULES

    real_import = builtins.__import__

    def guarded(name, *args, **kwargs):
        root = name.split(".")[0]
        if name in ejv.FORBIDDEN_MODULES or root in ejv.FORBIDDEN_MODULES:
            raise AssertionError(f"intento de importar cliente/red: {name}")
        return real_import(name, *args, **kwargs)

    builtins.__import__ = guarded
    try:
        with pytest.raises(AssertionError, match="typesafe_sdk"):
            exec("import typesafe_sdk")
    finally:
        builtins.__import__ = real_import


# ---------------------------------------------------------------- error_kind (AC9, clase y status)

def test_error_kind_distingue_clases_y_conserva_status():
    """AC9: 401/429/timeout/5xx no se colapsan; se afirma por clase Y por `status`."""
    auth = _tipo("TypeSafeAuthenticationError", status=401)
    cuota = _tipo("TypeSafeRateLimitError", status=429)
    timeout = _tipo("TypeSafeAPITimeoutError")
    servidor = _tipo("TypeSafeInternalServerError", status=500)
    ilegible = _tipo("TypeSafeAPIResponseValidationError", status=200)

    assert ejv.error_kind_de(auth()) == {"error_kind": "auth",
                                         "clase": "TypeSafeAuthenticationError", "status": 401}
    assert ejv.error_kind_de(cuota())["error_kind"] == "cuota"
    assert ejv.error_kind_de(timeout())["error_kind"] == "timeout"
    assert ejv.error_kind_de(servidor()) == {"error_kind": "servidor",
                                             "clase": "TypeSafeInternalServerError", "status": 500}
    assert ejv.error_kind_de(ilegible())["error_kind"] == "respuesta_ilegible"
    kinds = {ejv.error_kind_de(c())["error_kind"]
             for c in (auth, cuota, timeout, servidor, ilegible)}
    assert len(kinds) == 5, f"las cinco clases colapsaron en: {sorted(kinds)}"


def test_error_kind_clasifica_subclases_por_su_antecesor():
    """AC9: el SDK publica jerarquia; una subclase nueva del proveedor no puede volverse
    `desconocido` solo por no estar nombrada en la tabla.

    Medido con mutante el 2026-10-03: la version anterior de este control usaba una hija ya
    nombrada (`TypeSafeRateLimitError`), asi que apagar la caminata del MRO la dejaba verde. Aqui la
    hija lleva un nombre que la tabla NO conoce: si alguien corta el MRO, esto cae por `desconocido`.
    """
    antecesor = _tipo("TypeSafeRateLimitError", status=429)
    hija = _tipo("TypeSafeNuevaErrorDelProveedor", bases=(antecesor,), status=429)
    clasificado = ejv.error_kind_de(hija())
    assert clasificado["error_kind"] == "cuota", clasificado
    assert clasificado["clase"] == "TypeSafeNuevaErrorDelProveedor", (
        "la clase publica del ledger debe ser la real, no la del antecesor que la clasifico")
    assert clasificado["status"] == 429


def test_error_kind_desconocido_no_es_ausente():
    """DA-C3/AC2: un fallo inesperado y la ausencia de intento son estados distintos."""
    desconocido = ejv.error_kind_de(ValueError("el proveedor devolvio otra cosa"))
    assert desconocido["error_kind"] == "desconocido"
    assert desconocido["clase"] == "ValueError"
    assert nuevo()["error_kind"] is None, "un ledger sin intentos no puede decir `desconocido`"


def nuevo():
    return ejv.nuevo_ledger("jev", "jev-1.13.0")


# ------------------------------------------------------------------- usage_normalized (AC8/AC10)

def test_usage_desconocido_no_es_cero():
    """AC10: `Usage()` del SDK resuelve (None, None) medido; desconocido no es 0 ni 100 %."""
    vacio = ejv.normalizar_usage(Uso())
    assert vacio["estado"] == "desconocido"
    assert vacio["total"] is None and vacio["input_tokens"] is None
    assert vacio["libera_reserva_como_cero"] is False

    sin = ejv.normalizar_usage(None)
    assert sin["estado"] == "sin_usage" and sin["total"] is None

    observado = ejv.normalizar_usage(Uso(1200, 300))
    assert observado == {"input_tokens": 1200, "output_tokens": 300, "total": 1500,
                         "estado": "observado", "libera_reserva_como_cero": False}

    parcial = ejv.normalizar_usage(Uso(input_tokens=1200))
    assert parcial["estado"] == "parcial" and parcial["total"] is None


def test_usage_no_entero_no_se_cuela_como_token():
    """AC10: un `True` o un string en el campo de tokens es uso desconocido, no 1 ni basura."""
    assert ejv.normalizar_usage(Uso(True, "12"))["estado"] == "desconocido"


# ---------------------------------------------------------------- presupuesto antes de cada intento

def test_presupuesto_completo_reserva_y_agotado_no():
    """AC8: la reserva se comprueba ANTES de cada intento; el agotamiento implica cero envios."""
    ok = ejv.reservar_presupuesto({"llamadas_usadas": 3}, _limites_completos())
    assert ok["reservado"] is True and ok["llamadas_restantes"] == 9

    agotada = ejv.reservar_presupuesto({"llamadas_usadas": 12}, _limites_completos())
    assert agotada["reservado"] is False and agotada["motivos"] == ["llamadas_agotadas"]

    ausente = ejv.reservar_presupuesto({}, _limites_completos())
    assert ausente["reservado"] is False and "cuenta_de_llamadas_ausente" in ausente["motivos"]


def test_los_defaults_del_sdk_se_niegan_porque_gastan_sin_ledger():
    """AC8: max_reintentos != 0 (el default medido es 2 -> 3 intentos por 429) no se autoriza."""
    con_reintentos = ejv.reservar_presupuesto({"llamadas_usadas": 0},
                                              _limites_completos(max_reintentos=2))
    assert con_reintentos["reservado"] is False
    assert "reintentos_sin_ledger" in con_reintentos["motivos"]


def test_techo_de_tokens_null_bloquea_salvo_autorizacion_declarada():
    """AC8/protocolo: los dos null bloquean, y la corrida que los mide se autoriza por escrito."""
    sin_declarar = ejv.reservar_presupuesto({"llamadas_usadas": 0},
                                            _limites_completos(tokens_in=None, tokens_out=None))
    assert sin_declarar["reservado"] is False
    assert sin_declarar["motivos"] == ["techo_de_tokens_in_sin_declarar",
                                       "techo_de_tokens_out_sin_declarar"]

    declarada = ejv.reservar_presupuesto(
        {"llamadas_usadas": 0},
        _limites_completos(tokens_in=None, tokens_out=None,
                           autorizacion_de_null={"declarada": True,
                                                 "motivo": "corrida de medicion k=8, "
                                                            "operador 2026-10-03"}))
    assert declarada["reservado"] is True, declarada["motivos"]


# ------------------------------------------------------------------------- el ledger de intentos

def test_el_ledger_cuenta_intentos_y_no_colapsa_exito_con_fallo():
    """AC8/AC2: `attempts` es el conteo real, y un fallo no borra lo observado antes."""
    ledger = nuevo()
    assert ledger["attempts"] == 0 and ledger["estado"] == "NO-EJERCITADO"

    cuota = _tipo("TypeSafeRateLimitError", status=429)
    ejv.registrar_intento(ledger, resultado="fallo", excepcion=cuota(), duracion_ms=18)
    assert ledger["attempts"] == 1 and ledger["error_kind"] == "cuota"
    assert ledger["estado"] == "FALLO"

    ejv.registrar_intento(ledger, resultado="exito", usage=Uso(1200, 300),
                          modelo_efectivo="jev-1.13.0", duracion_ms=640)
    assert ledger["attempts"] == 2
    assert [f["n"] for f in ledger["intentos"]] == [1, 2]
    assert ledger["intentos"][0]["status"] == 429
    assert ledger["usage_normalized"]["estado"] == "observado"
    assert ledger["modelo_efectivo"] == "jev-1.13.0"
    assert ledger["estado"] == "EJERCITADO"


def test_los_tres_campos_de_la_pata_b_viven_en_el_runner_y_no_en_la_costura():
    """La particion D-B: la costura conserva pedido/modelo/tiempo; estos tres nacen aqui.

    Si alguien los mueve a `decision_client.py`, este control cae por la causa nombrada: el
    runner deja de publicarlos.
    """
    for nombre in ("nuevo_ledger", "registrar_intento", "reservar_presupuesto",
                   "error_kind_de", "normalizar_usage"):
        assert hasattr(ejv, nombre), f"el runner perdio {nombre}"
    assert "attempts" in nuevo()
    assert "error_kind" in nuevo()
    assert "usage_normalized" in nuevo()


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
