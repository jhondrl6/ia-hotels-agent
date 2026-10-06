"""Arnès AC-4 (racha de descargas) + verificacion de la promesa del servidor, sobre el arbol curado.

Que la racha del 2026-10-05 quedo **sin crudo** es el defecto que esta corrida cierra: el registro de
FASE-RELEASE sect.15 (linea 738) declara tres intentos directos que dieron `1-1-0` y los consigna como
"medida sin evidencia adjunta". Aca la medida vuelve a hacerse y SU SALIDA QUEDA EN DISCO.

Redactado por diseno: de `qmind source list --format json` solo se imprimen `id`, `title`, `status`,
`metadata.fileSha256` y `metadata.fileSize`. Nunca se imprime el JSON crudo ni `originUrl`, que porta
credenciales de acceso (AC-6: ni valor, ni longitud, ni prefijo).
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
NB = "01a04d98-b7bd-778c-8441-26fdc7e35f45"
FUENTE = "01a0efcc-3297-7782-9467-757fe81018fc"
GOBERNADO = RAIZ / ".opencode" / "context" / "CONTEXT-JEV-TYPESAFE-CASOS-DE-USO-2026-09-21.md"
DECLARADO = (RAIZ / ".opencode" / "plans" / "Archives" / "EVALUACION-JEV-TYPESAFE-2026-09-21" /
             "10-analisis-post-implementacion.md")
INTENTOS = 3


def qmind(args: list[str]) -> tuple[int, str]:
    exe = shutil.which("qmind")
    if not exe:
        for extension in (".CMD", ".cmd", ".bat", ".exe"):
            candidato = Path.home() / "AppData" / "Roaming" / "npm" / f"qmind{extension}"
            if candidato.is_file():
                exe = str(candido)
                break
    if not exe:
        raise SystemExit("el CLI qmind no resuelve: la medida no se pudo tomar")
    proc = subprocess.run([exe, *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=180)
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def sha(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def main() -> int:
    print("== 1. el disco gobernado (no se toco en esta sesion)")
    for ruta in (GOBERNADO, DECLARADO):
        bytes_disco = ruta.stat().st_size
        print(f"   {ruta.name}: {bytes_disco} B | sha256 {sha(ruta)[:16]}…")

    print("== 2. lo que el SERVIDOR declara, sin descargar (source list, campos redactados)")
    rc, salida = qmind(["source", "list", "--nb", NB, "--all", "--format", "json"])
    print(f"   rc={rc}")
    if rc != 0:
        print(f"   [SIN-MEDIDA] el listado no respondio: {salida.strip().splitlines()[:1]}")
        return 1
    inicio = salida.find("{")
    datos = json.loads(salida[inicio:])
    fuentes = datos.get("sources") or []
    print(f"   fuentes publicadas: {len(fuentes)}")
    prometidas = []
    objetivo = None
    sha_ctx = sha(GOBERNADO)
    for f in fuentes:
        meta = f.get("metadata") or {}
        if f.get("id") == FUENTE:
            objetivo = f
        if (meta.get("fileSha256") or "") == sha_ctx:
            prometidas.append(f)
        if (meta.get("fileSha256") or "") and f.get("id") in (FUENTE,):
            print(f"   {f['id']} | status={f.get('status')} | "
                  f"fileSha256={meta.get('fileSha256', '')[:16]}… | fileSize={meta.get('fileSize')}")
    print(f"   fuentes cuyo metadata casa con el CONTEXT en disco: {len(prometidas)} "
          f"({', '.join((p.get('id') or '')[:13] + '…' for p in prometidas) or 'ninguna'})")

    print(f"== 3. racha de {INTENTOS} descargas directas de {FUENTE[:13]}… (la medida del 1-1-0)")
    scratch = Path(tempfile.mkdtemp(prefix="racha-"))
    secuencia = []
    try:
        for i in range(1, INTENTOS + 1):
            destino = scratch / f"intento-{i}.bin"
            rc_d, err = qmind(["source", "download", "--nb", NB, FUENTE, "-o", str(destino)])
            if rc_d == 0 and destino.is_file():
                secuencia.append(0)
                print(f"   intento {i}: exit=0 | {destino.stat().st_size} B | sha "
                      f"{sha(destino)[:16]}… | casa_con_disco={sha(destino) == sha_ctx}")
            else:
                secuencia.append(1)
                primera = (err or "").strip().splitlines()[:1]
                print(f"   intento {i}: exit={rc_d} | dejo archivo={destino.is_file()} | "
                      f"{primera[0][:80] if primera else '(sin mensaje)'}")
            destino.unlink(missing_ok=True)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    print(f"   RACHA (codigo de cada intento) = {'-'.join(str(s) for s in secuencia)}")
    print(f"   exitosas = {secuencia.count(0)} | fallidas = {secuencia.count(1)}")

    print("== 4. el verificador curado, sobre el mismo arbol (--strict)")
    proc = subprocess.run([sys.executable, str(RAIZ / "scripts" / "verify_qmind_context_freshness.py"),
                           "--strict"], cwd=str(RAIZ), capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=600)
    lineas = proc.stdout.splitlines()
    for l in lineas:
        if l.startswith("  [") or l.startswith("[") or l.startswith("notebook "):
            print("   " + l[:170])
    for etiqueta in ("[FRESCO]", "[VENCIDO]", "[SIN-DESCARGA]", "[NO-EVALUABLE]", "[PROMESA-ROTA]",
                     "[AVISO]"):
        print(f"   conteo {etiqueta} = {sum(1 for l in lineas if etiqueta in l)}")
    print(f"   FRESHNESS_EXIT={proc.returncode}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    raise SystemExit(main())
