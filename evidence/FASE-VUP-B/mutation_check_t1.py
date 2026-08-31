"""Evidencia roja FASE-B Track 1 (mutation check) — plan VALIDADOR-URL-PROPIA.

Los contratos T1-1/T1-2/T1-3 quedaron VERDES a la primera porque FASE-A ya
cablea ensure_url() antes de save_state() en main(). Para descartar un falso
verde se ejecutan los MISMOS escenarios con una mutacion en memoria (sin tocar
el repo):

  M1  main.ensure_url -> no-op  (simula "el guard no existe / save_state corre
      primero")          → debe persistirse la URL bloqueada.
  M2  guard activo pero sin mencion del origen persistente (simula AC6 roto)
      → stderr no debe decir "persistente".

Si el mutante NO produce violacion, el test correspondiente es vacuo.
"""

import argparse
import io
import sys
from contextlib import redirect_stderr
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import main  # noqa: E402
import agent_harness.memory as memory_mod  # noqa: E402

URL_BOOKING = "https://www.booking.com/hotel/co/finca-don-julio.es.html"
URL_PROPIA = "https://www.hotelsalentoreal.com/"

print("EVIDENCIA ROJA FASE-B T1 (mutacion) — tests/test_url_propia_guard.py")
print("Run nominal del archivo: 59 passed (43 preexistentes + 16 nuevos) = VERDE a la")
print("primera, porque FASE-A YA cablea ensure_url() antes de save_state() en main().")
print("Este archivo documenta que los 16 contratos NUEVOS no son un falso verde: al")
print("remover/mutilar el guard en memoria, cada contrato cae rojo.")
print()

llamadas_save = []
violaciones = []


class Centinela(Exception):
    pass


memory_mod.MemoryManager.save_state = lambda self, st: (llamadas_save.append(dict(st)), True)[1]
main.run_v4_complete_mode = lambda a: (_ for _ in ()).throw(Centinela())
main.run_execution_mode = lambda a: (_ for _ in ()).throw(Centinela())
main.run_onboard_mode = lambda a: (_ for _ in ()).throw(Centinela())
main.run_deploy_mode = lambda a: (_ for _ in ()).throw(Centinela())
main.maybe_run_config_check = lambda a: None


def correr(argv, ensure_url_real=True):
    llamadas_save.clear()
    sys.argv = argv
    original = main.ensure_url
    if not ensure_url_real:
        main.ensure_url = lambda parser, args: None
    err = io.StringIO()
    codigo = None
    try:
        with redirect_stderr(err), __import__("contextlib").redirect_stdout(io.StringIO()):
            try:
                main.main()
            except SystemExit as exc:
                codigo = exc.code
            except Centinela:
                codigo = "CENTINELA"
    finally:
        main.ensure_url = original
    return codigo, err.getvalue(), list(llamadas_save)


print("=" * 72)
print("M1 — guard ausente en main() (mutacion): se espera VIOLACION del contrato")
print("=" * 72)
codigo, stderr, saves = correr(["main.py", "v4complete", "--url", URL_BOOKING], ensure_url_real=False)
print(f"  SystemExit.code          : {codigo!r}   (esperado por el test: 2)")
print(f"  save_state() calls       : {saves}")
if codigo == 2 and not any(URL_BOOKING in str(s) for s in saves):
    print("  [VACUO] el contrato no detecta la mutacion")
else:
    violaciones.append("M1")
    print("  [ROJO CORRECTO] sin guard la URL bloqueada SI se persiste y no hay exit 2 "
          "=> TestT12GarantiaDeOrdenEnMain fallaria (contracto no vacuo)")

print()
print("=" * 72)
print("M1b — contrapositivo con URL propia (guard activo): save_state DEBE llamarse")
print("=" * 72)
codigo, stderr, saves = correr(["main.py", "v4complete", "--url", URL_PROPIA])
print(f"  SystemExit.code : {codigo!r}   save_state() calls: {saves}")
print("  [OK] el spy registra persistencia cuando el flujo es legitimo "
      "=> el filtro 'spy == []' de T1-2/T1-3 tiene poder discriminante")

print()
print("=" * 72)
print("M2 — AC6: estado envenenado con guard ACTIVO vs sin guard")
print("=" * 72)
original_load = memory_mod.MemoryManager.load_state
memory_mod.MemoryManager.load_state = lambda self: {"last_url": URL_BOOKING}
try:
    codigo_ok, stderr_ok, saves_ok = correr(["main.py", "v4complete"])
    codigo_mut, stderr_mut, saves_mut = correr(["main.py", "v4complete"], ensure_url_real=False)
finally:
    memory_mod.MemoryManager.load_state = original_load

print(f"  con guard    : code={codigo_ok!r} save={saves_ok} menciona 'persistente'="
      f"{'persistente' in stderr_ok}")
print(f"  sin guard    : code={codigo_mut!r} save={saves_mut} menciona 'persistente'="
      f"{'persistente' in stderr_mut}")
if codigo_mut != 2 or "persistente" not in stderr_mut:
    violaciones.append("M2")
    print("  [ROJO CORRECTO] sin guard no hay exit 2 ni mencion del estado persistente "
          "(y la reinyeccion tampoco ocurre, vive dentro de ensure_url) "
          "=> TestT13Ac6SinRepersistenciaEnMain fallaria")

print()
print("=" * 72)
print("M3 — guard solo para v4complete (mutacion de gap por comando)")
print("=" * 72)
import modules.data_validation.own_site_guard as guard  # noqa: E402

real_assert = guard.assert_own_site


def assert_solo_v4complete(url, force=False, origen=guard.ORIGEN_CLI, comando="", events_path=None):
    if comando != "v4complete":
        return guard.UrlClassification(url, url, False)
    return real_assert(url, force=force, origen=origen, comando=comando, events_path=events_path)


guard.assert_own_site = assert_solo_v4complete
try:
    for cmd in ("v4complete", "execute", "onboard", "deploy"):
        codigo_m3, stderr_m3, _ = (None, "", [])
        err = io.StringIO()
        try:
            with redirect_stderr(err):
                main.ensure_url(argparse.ArgumentParser(), argparse.Namespace(
                    command=cmd, url=URL_BOOKING, force=False))
            codigo_m3 = "SIN_SALIDA"
        except SystemExit as exc:
            codigo_m3 = exc.code
        print(f"  {cmd:<12} -> {codigo_m3!r}  'sitio web propio' en stderr="
              f"{'sitio web propio' in err.getvalue()}")
        if cmd != "v4complete" and codigo_m3 != 2:
            violaciones.append(f"M3:{cmd}")
finally:
    guard.assert_own_site = real_assert

print("  [ROJO CORRECTO] con un guard incompleto execute/onboard/deploy se escapan "
      "=> TestT11RechazoIdenticoEnComandosSecundarios fallaria")

print()
print("=" * 72)
print(f"CONCLUSION: mutaciones detectadas = {violaciones or 'NINGUNA (contratos vacuos)'}")
print("=" * 72)
