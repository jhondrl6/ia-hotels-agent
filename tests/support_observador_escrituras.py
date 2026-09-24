"""Observador de **operaciones de escritura**, no de estado final.

Nacio para S13 (deuda del plan `VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20`, tramo §4 del mandato de
remediacion del bloque B de `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22`): comparar el estado antes y
despues de una funcion no demuestra que nadie abrio un archivo en modo escritura, y una prueba que
vuelve a definir su propia funcion de huellas o que provoca el rojo con `os.utime` no prueba el
observador del arnes, sino otra copia del mismo.

Este modulo es **la unica** implementacion de `huellas()` y del observador. Las pruebas que observan
escrituras lo importan por ruta; ninguna define una pareja de huellas propia.

Alcance del observador (declarado, y `ALCANCE` es lo que publican las pruebas):
  * cubre el **proceso de pytest**: parchea los mecanismos de escritura de `pathlib`, `builtins.open`,
    `os` y `shutil`, incluidas las rutas indirectas (renamer/sustituir/copiar/borrar);
  * **NO cubre procesos hijos**: lo que escribe un `subprocess` escapa al parcheo in-process. Una
    prueba que necesite cubrir un hijo debe dirigirlo a un destino desechable y afirmarlo por `huellas()`.
"""
from __future__ import annotations

import builtins
import contextlib
import hashlib
import os
import shutil
from pathlib import Path

__all__ = ["Escrituras", "observador_de_escrituras", "huellas", "ALCANCE", "MODOS_ESCRITURA"]

ALCANCE = ("proceso actual (pytest): pathlib + builtins.open + os + shutil, incluidas rutas "
           "indirectas; NO cubre procesos hijos")

# Modos de `open()` que escriben. `x`/`a`/`w` y sus variantes `+` y `b`.
MODOS_ESCRITURA = frozenset({
    "w", "wb", "bw", "w+", "w+b", "wb+", "r+", "r+b", "rb+", "a", "ab", "ba",
    "a+", "a+b", "ab+", "x", "xb", "bx", "x+", "x+b", "xb+",
})


def huellas(directorio: Path, *, archivos=None) -> dict:
    """sha256 + mtime_ns + tamano de cada archivo bajo `directorio`.

    La pareja (hash, mtime) es lo que delata la re-escritura de bytes identicos; el tamano se anade
    porque un cambio de longitud siempre mueve el hash, asi que no aporta signal nuevo pero si hace
    el dict legible en un log.
    """
    if not directorio.exists():
        return {}
    salida = {}
    for p in sorted(directorio.rglob("*") if archivos is None else archivos):
        if not p.is_file():
            continue
        datos = p.read_bytes()
        st = p.stat()
        salida[p.as_posix()] = (hashlib.sha256(datos).hexdigest(), st.st_mtime_ns, st.st_size)
    return salida


class Escrituras:
    """Registro de las operaciones de escritura observadas, con su operacion y su resultado."""

    def __init__(self):
        self.operaciones: list[tuple[str, str, bool]] = []   # (op, ruta_posix, ok)

    def rutas(self) -> list[str]:
        return [ruta for _, ruta, _ in self.operaciones]

    def dentro_de(self, *directorios: Path) -> list[tuple[str, str, bool]]:
        """Las operaciones cuyo destino cae bajo alguno de `directorios`.

        Compara por componentes de ruta, no por prefijo de string: `/repo/evidence-x` no esta
        «dentro de» `/repo/evidence`.
        """
        blancos = [Path(d).resolve() for d in directorios]
        encontradas = []
        for op, ruta, ok in self.operaciones:
            try:
                resuelta = Path(ruta).resolve()
            except OSError:
                resuelta = Path(ruta)
            for blanco in blancos:
                if resuelta == blanco or blanco in resuelta.parents:
                    encontradas.append((op, ruta, ok))
                    break
        return encontradas

    def resumen(self) -> str:
        if not self.operaciones:
            return "0 operaciones observadas"
        lineas = [f"{len(self.operaciones)} operaciones observadas:"]
        for op, ruta, ok in self.operaciones:
            lineas.append(f"  {op:24} {'OK ' if ok else 'ERR'} {ruta}")
        return "\n".join(lineas)

    def __repr__(self) -> str:  # pragma: no cover - solo legibilidad de fallos
        return f"<Escrituras {len(self.operaciones)} ops>"


def _modo_escribe(modo: str) -> bool:
    base = (modo or "r").replace("t", "").strip()
    return any(c in base for c in "wax+") or "+" in base


def _ruta_de(arg) -> str | None:
    if isinstance(arg, Path):
        return arg.as_posix()
    if isinstance(arg, (str, bytes, os.PathLike)):
        try:
            return os.fspath(arg) if isinstance(arg, os.PathLike) else str(arg)
        except Exception:
            return None
    return None


@contextlib.contextmanager
def observador_de_escrituras():
    """Recolecta las operaciones de escritura del bloque, sin bloquear ninguna.

    Envolvente, no sustitutiva: cada mecanismo original se sigue ejecutando igual.
    """
    registro = Escrituras()

    def _registrar(op: str, destino):
        ruta = _ruta_de(destino)
        if ruta is not None:
            registro.operaciones.append((op, ruta, True))

    def _registrar_fallo(op: str, destino):
        ruta = _ruta_de(destino)
        if ruta is not None:
            for i, (o, r, ok) in enumerate(reversed(registro.operaciones)):
                if o == op and r == ruta and ok:
                    idx = len(registro.operaciones) - 1 - i
                    registro.operaciones[idx] = (o, r, False)
                    break

    parches = []

    def patch(target, nombre, factory):
        original = getattr(target, nombre)
        setattr(target, nombre, factory(original))
        parches.append((target, nombre, original))

    # --- pathlib: los metodos que usa el codigo bajo prueba -----------------
    def _write_text(orig):
        def envuelto(self, *a, **k):
            destino = self
            try:
                r = orig(self, *a, **k)
            except Exception:
                _registrar_fallo("Path.write_text", destino)
                raise
            _registrar("Path.write_text", destino)
            return r
        return envuelto

    def _write_bytes(orig):
        def envuelto(self, *a, **k):
            destino = self
            try:
                r = orig(self, *a, **k)
            except Exception:
                _registrar_fallo("Path.write_bytes", destino)
                raise
            _registrar("Path.write_bytes", destino)
            return r
        return envuelto

    def _path_open(orig):
        def envuelto(self, mode="r", *a, **k):
            if _modo_escribe(mode):
                _registrar(f"Path.open({mode})", self)
            return orig(self, mode, *a, **k)
        return envuelto

    def _mkdir(orig):
        def envuelto(self, *a, **k):
            _registrar("Path.mkdir", self)
            return orig(self, *a, **k)
        return envuelto

    def _touch(orig):
        def envuelto(self, *a, **k):
            _registrar("Path.touch", self)
            return orig(self, *a, **k)
        return envuelto

    def _path_rename(orig):
        def envuelto(self, target, *a, **k):
            _registrar("Path.rename", self)
            _registrar("Path.rename->dest", target)
            return orig(self, target, *a, **k)
        return envuelto

    def _path_replace(orig):
        def envuelto(self, target, *a, **k):
            _registrar("Path.replace", self)
            _registrar("Path.replace->dest", target)
            return orig(self, target, *a, **k)
        return envuelto

    patch(Path, "write_text", _write_text)
    patch(Path, "write_bytes", _write_bytes)
    patch(Path, "open", _path_open)
    patch(Path, "mkdir", _mkdir)
    patch(Path, "touch", _touch)
    patch(Path, "rename", _path_rename)
    patch(Path, "replace", _path_replace)

    # --- builtins.open ------------------------------------------------------
    _open_orig = builtins.open

    def open_envuelto(file, mode="r", *a, **k):
        if _modo_escribe(mode):
            _registrar(f"open({mode})", file)
        return _open_orig(file, mode, *a, **k)

    patch(builtins, "open", lambda _o: open_envuelto)

    # --- os: rutas indirectas ----------------------------------------------
    def _os_replace(orig):
        def envuelto(src, dst, *a, **k):
            _registrar("os.replace->src", src)
            _registrar("os.replace->dst", dst)
            return orig(src, dst, *a, **k)
        return envuelto

    def _os_rename(orig):
        def envuelto(src, dst, *a, **k):
            _registrar("os.rename->src", src)
            _registrar("os.rename->dst", dst)
            return orig(src, dst, *a, **k)
        return envuelto

    def _os_remove(orig):
        def envuelto(path, *a, **k):
            _registrar("os.remove", path)
            return orig(path, *a, **k)
        return envuelto

    def _os_makedirs(orig):
        def envuelto(name, *a, **k):
            _registrar("os.makedirs", name)
            return orig(name, *a, **k)
        return envuelto

    def _os_mkdir(orig):
        def envuelto(name, *a, **k):
            _registrar("os.mkdir", name)
            return orig(name, *a, **k)
        return envuelto

    def _os_open(orig):
        def envuelto(path, flags, *a, **k):
            escribe = bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_APPEND | os.O_TRUNC))
            if escribe:
                _registrar("os.open", path)
            return orig(path, flags, *a, **k)
        return envuelto

    def _os_truncate(orig):
        def envuelto(path, length, *a, **k):
            _registrar("os.truncate", path)
            return orig(path, length, *a, **k)
        return envuelto

    for nombre, factory in (("replace", _os_replace), ("rename", _os_rename),
                            ("remove", _os_remove), ("makedirs", _os_makedirs),
                            ("mkdir", _os_mkdir), ("open", _os_open),
                            ("truncate", _os_truncate)):
        if hasattr(os, nombre):
            patch(os, nombre, factory)

    if hasattr(os, "ftruncate"):
        def _os_ftruncate(orig):
            def envuelto(fd, length, *a, **k):
                registro.operaciones.append(("os.ftruncate", f"fd:{fd}", True))
                return orig(fd, length, *a, **k)
            return envuelto
        patch(os, "ftruncate", _os_ftruncate)

    # --- shutil: creacion y sustitucion por via indirecta -------------------
    def _sh(name):
        def factory(orig):
            def envuelto(src, dst, *a, **k):
                _registrar(f"shutil.{name}->dst", dst)
                return orig(src, dst, *a, **k)
            return envuelto
        return factory

    for nombre in ("copyfile", "copy", "copy2", "copytree", "move"):
        if hasattr(shutil, nombre):
            patch(shutil, nombre, _sh(nombre))

    if hasattr(shutil, "rmtree"):
        def _rmtree(orig):
            def envuelto(path, *a, **k):
                _registrar("shutil.rmtree", path)
                return orig(path, *a, **k)
            return envuelto
        patch(shutil, "rmtree", _rmtree)

    try:
        yield registro
    finally:
        for target, nombre, original in reversed(parches):
            setattr(target, nombre, original)
