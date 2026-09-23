#!/usr/bin/env python3
"""Veredicto de contrato sobre los cinco contraejemplos, para dos revisiones del mismo modulo.

Instrumento de la remediacion del bloque A de
`.opencode/context/ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md`.

    ./venv/Scripts/python.exe <este archivo> --modulo RUTA --etiqueta PRE
    ./venv/Scripts/python.exe <este archivo> --modulo RUTA --etiqueta POST

Cada criterio se escribe como **lo que el contrato exige**, no como «el bug sigue ahi»: asi el mismo
script sirve para la revision anterior (por `git show HEAD:scripts/decision_client.py`, sin stash
sobre el trabajo sin commitear) y para el arbol de trabajo, y el verde de hoy es comparable con el
rojo de ayer porque afirma la misma proposicion.

Sin red, sin proveedor real, sin escribir en el arbol del repo: los proveedores falsos que se
necesitan para provocar estados viven en un tempdir propio y se borran al salir.
"""

from __future__ import annotations

import argparse
import importlib.util
import shutil
import sys
import tempfile
from pathlib import Path


def cargar(ruta_modulo: Path):
    spec = importlib.util.spec_from_file_location("dc_bajo_veredicto", ruta_modulo)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _dir_con(*archivos: tuple) -> str:
    d = Path(tempfile.mkdtemp(prefix="iah-veredicto-"))
    for nombre, texto in archivos:
        (d / nombre).write_text(texto, encoding="utf-8")
    return str(d)


ROTO = "raise RuntimeError('el modulo del proveedor no carga')\n"
PROVEEDOR_MINIMO = (
    "PROVEEDOR = {'nombre': 'minimo', 'credencial_env': None}\n\n"
    "def evaluar(state, preguntas):\n"
    "    return {'modelo': 'm', 'respuestas': [], 'usage': None, 'request_id': None}\n")


def criterios(dc):
    """(id, descripcion del contrato, fn) donde fn() devuelve (cumple: bool, evidencia: str)."""

    def cx1():
        d = _dir_con(("roto.py", ROTO))
        try:
            try:
                dc.resolver_proveedor({dc.ENV_PROVIDER: "roto", dc.ENV_PROVIDERS_DIR: d})
                return False, "resolver_proveedor devolvio un proveedor para un modulo que no cargo"
            except dc.LectorFallido as exc:
                return True, f"LectorFallido: {exc}"
            except Exception as exc:            # noqa: BLE001 - aqui se observa el estado, no se traga
                return False, f"{type(exc).__name__}: {exc}"
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def cx1b():
        d = _dir_con(("roto.py", ROTO))
        try:
            est = dc.estado_proveedor({dc.ENV_PROVIDER: "roto", dc.ENV_PROVIDERS_DIR: d})
            cumple = est.get("provider_status") != "NO-CONFIGURADO" and \
                est.get("estado_lector") == "LECTOR-FALLIDO"
            return cumple, (f"provider_status={est.get('provider_status')!r} "
                            f"estado_lector={est.get('estado_lector')!r}")
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def cx2():
        payload = {"modelo": "m", "respuestas": [{"pregunta_id": "n1", "tipo": "noul",
                                                 "probabilidad_si": 0.4,
                                                 "campo_inventado": 7}]}
        motivos = dc.check_campos_conocidos(payload, [dc.Pregunta("n1", "noul", "?")])
        cumple = any("campo_inventado" in m for m in motivos)
        return cumple, f"motivos={motivos or '[] (el campo desconocido escapo)'}"

    def cx3_tipo():
        payload = {"modelo": "m", "respuestas": [{"pregunta_id": "n1", "tipo": [],
                                                 "probabilidad_si": 0.4}]}
        try:
            motivos = dc.check_campos_conocidos(payload, [dc.Pregunta("n1", "noul", "?")])
            return bool(motivos), f"motivos={motivos}"
        except Exception as exc:                # noqa: BLE001
            return False, f"{type(exc).__name__}: {exc} (el instrumento cayo, no informo)"

    def cx3_id():
        lote = [dc.Pregunta("p1", "noul", "?")]
        payload = {"modelo": "m", "respuestas": [{"pregunta_id": [], "tipo": "noul",
                                                 "probabilidad_si": 0.4}]}
        try:
            dc.validar_payload(payload, lote, "x")
            return False, "acepto un payload sin motiver"
        except dc.RespuestaIlegible as exc:
            return True, f"ILEGIBLE {exc.motivos}"
        except Exception as exc:                # noqa: BLE001
            return False, f"{type(exc).__name__}: {exc} (el instrumento cayo, no informo)"

    def cx4():
        lote = [dc.Pregunta("mismo", "noul", "? A"), dc.Pregunta("mismo", "noul", "? B")]
        d = _dir_con(("minimo.py", PROVEEDOR_MINIMO))
        try:
            entorno = {dc.ENV_PROVIDER: "minimo", dc.ENV_PROVIDERS_DIR: d}
            try:
                r = dc.evaluar("estado", lote, entorno, _payload={
                    "modelo": "m", "respuestas": [
                        {"pregunta_id": "mismo", "tipo": "noul", "probabilidad_si": 0.4}],
                    "usage": None, "request_id": None})
                return False, (f"provider_status={r.provider_status!r} con "
                               f"{len(r.respuestas)} respuesta para {len(lote)} preguntas")
            except dc.RespuestaIlegible as exc:
                return False, f"ILEGIBLE (no rechaza el lote, rechaza la respuesta): {exc.motivos}"
            except ValueError as exc:
                return True, f"ValueError del lote: {exc}"
            except Exception as exc:            # noqa: BLE001
                return False, f"{type(exc).__name__}: {exc}"
        finally:
            shutil.rmtree(d, ignore_errors=True)

    return [
        ("CX1", "un modulo de proveedor que no carga NO se resuelve como ausencia", cx1),
        ("CX1b", "la sonda de estado lo nombra LECTOR-FALLIDO, no NO-CONFIGURADO", cx1b),
        ("CX2", "un campo fuera de contrato en `noul` se reporta como ruptura", cx2),
        ("CX3a", "`tipo` que no es texto produce motivos, no un TypeError", cx3_tipo),
        ("CX3b", "`pregunta_id` que no es texto produce ILEGIBLE, no un TypeError", cx3_id),
        ("CX4", "un lote con ids repetidos se rechaza antes de cerrar en RESUELTO", cx4),
    ]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--modulo", required=True)
    ap.add_argument("--etiqueta", default="MODULO")
    args = ap.parse_args(argv)

    dc = cargar(Path(args.modulo).resolve())
    criterios_dc = criterios(dc)

    print(f"== veredicto de contrato / {args.etiqueta} / modulo: {args.modulo}")
    print(f"   generado por: {Path(__file__).name}")
    print()
    n_ok = 0
    for cid, contrato, fn in criterios_dc:
        try:
            cumple, evidencia = fn()
        except Exception as exc:                # noqa: BLE001
            cumple, evidencia = False, f"{type(exc).__name__}: {exc}"
        n_ok += bool(cumple)
        print(f"[{'CUMPLE' if cumple else 'NO CUMPLE'}] {cid}: {contrato}")
        print(f"         {evidencia}")
    print()
    print(f"total: {n_ok}/{len(criterios_dc)} criterios del contrato cumplidos "
          f"en {args.etiqueta}")
    return 0 if n_ok == len(criterios_dc) else 1


if __name__ == "__main__":
    sys.exit(main())
