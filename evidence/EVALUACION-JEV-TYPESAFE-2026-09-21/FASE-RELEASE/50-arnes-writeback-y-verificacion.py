"""Arnès del write-back del `10-analisis` (punto D3 del mandato CIERRE-DE-ABANICO) - 2026-10-05.

Publica por CLI con titulo nuevo que conserva el stem, y verifica la publicacion **por descarga + sha256**,
no por titulo (la convencion del 2026-09-27, re-afirmada por el sello 15 de esta hoja). Redacta por
construccion: cualquier URL o campo firmado sale del crudo antes de escribirse (AC-6).
"""
from __future__ import annotations

import hashlib
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
HOJA = (RAIZ / ".opencode" / "plans" / "Archives" / "EVALUACION-JEV-TYPESAFE-2026-09-21" /
        "10-analisis-post-implementacion.md")
NB = "01a04d98-b7bd-778c-8441-26fdc7e35f45"
STEM = "10-analisis: EVALUACION-JEV-TYPESAFE-2026-09-21"
TITULO_NUEVO = (STEM + " (cierre FASE-RELEASE, etiqueta AC5 dictada 2026-10-05)")
PREVIAS = ("01a10e39-1625-71b1-8ca6-73cbdb1c6a94", "01a10853-6da2", "01a0e4d9")
URL = re.compile(r"https?://\S+")
CAMPOS_FIRMADOS = re.compile(r'"(originUrl|originalFileUri|downloadUrl|uri|url|signedUrl|path)"\s*:'
                             r'\s*"[^"]*"')


def redactar(texto: str) -> str:
    texto = CAMPOS_FIRMADOS.sub(r'"\1": "[REDACTADA]"', texto or "")
    return URL.sub("[URL-REDACTADA]", texto)


def qmind(args: list[str]) -> tuple[int, str]:
    exe = shutil.which("qmind")
    if not exe:
        for extension in (".CMD", ".cmd", ".bat", ".exe"):
            candidato = Path.home() / "AppData" / "Roaming" / "npm" / f"qmind{extension}"
            if candidato.is_file():
                exe = str(candido)
                break
    if not exe:
        raise SystemExit("el CLI qmind no resuelve")
    proc = subprocess.run([exe, *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=300)
    return proc.returncode, redactar((proc.stdout or "") + (proc.stderr or ""))


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def frescura(etiqueta: str) -> tuple[int, list[str]]:
    proc = subprocess.run([sys.executable, str(RAIZ / "scripts" / "verify_qmind_context_freshness.py"),
                           "--strict"], cwd=str(RAIZ), capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=600)
    lineas = [l for l in (proc.stdout or "").splitlines()
              if l.startswith("  [") or l.startswith("[") or l.startswith("notebook ")]
    print(f"-- {etiqueta}: FRESHNESS_EXIT={proc.returncode}")
    for l in lineas:
        print("   " + redactar(l)[:180])
    return proc.returncode, lineas


def main() -> int:
    disco = HOJA.read_bytes()
    print("== 0. el disco que se va a publicar")
    print(f"   {len(disco)} B | sha256 {sha(disco)}")
    print(f"   CR={disco.count(bytes([13]))} LF={disco.count(bytes([10]))}  "
          f"(CR 0 o sea crudo == normalizado, sin artefacto CRLF que declarar)")
    print(f"   titulo nuevo: {TITULO_NUEVO!r}")

    rc_antes, _ = frescura("1. PRE, el verificador curado sobre el arbol vencido")

    print("== 2. poblacion ANTES de publicar")
    rc, salida = qmind(["source", "list", "--nb", NB, "--all", "--format", "json"])
    fuentes_antes = json.loads(salida[salida.find("{"):]).get("sources") or []
    print(f"   rc={rc} | fuentes = {len(fuentes_antes)}")
    por_id = {f.get("id"): f for f in fuentes_antes}
    for sid in PREVIAS:
        encontrado = [k for k in por_id if (k or "").startswith(sid)]
        for k in encontrado:
            m = (por_id[k].get("metadata") or {})
            print(f"   previa {k[:22]}… status={por_id[k].get('status')} "
                  f"sha={str(m.get('fileSha256'))[:12]}… size={m.get('fileSize')} "
                  f"titulo={(por_id[k].get('title') or '')[:60]!r}")

    print("== 3. publicacion por CLI (upload, titulo nuevo, sin borrar ninguna)")
    rc_up, salida_up = qmind(["source", "upload", "--nb", NB, "--file", str(HOJA),
                              "--title", TITULO_NUEVO, "--non-interactive"])
    print(f"   UPLOAD_EXIT={rc_up}")
    nuevo_id = ""
    inicio = salida_up.find("{")
    if inicio >= 0:
        try:
            datos = json.loads(salida_up[inicio:])
            fuente = datos.get("source") or datos
            nuevo_id = fuente.get("id") or ""
            m = fuente.get("metadata") or {}
            print(f"   fuente nueva id={nuevo_id} status={fuente.get('status')} "
                  f"sourceType={fuente.get('sourceType')}")
            print(f"   metadata.fileSha256={m.get('fileSha256')}")
            print(f"   metadata.fileSize={m.get('fileSize')}")
            print(f"   casa_con_disco: sha={m.get('fileSha256') == sha(disco)} "
                  f"size={m.get('fileSize') == len(disco)}")
        except json.JSONDecodeError:
            print("   [AVISO] la salida del upload no es JSON; se imprime redactada:")
            for l in salida_up.splitlines()[:8]:
                print("   " + l[:180])
    else:
        for l in salida_up.splitlines()[:8]:
            print("   " + l[:180])
    if not nuevo_id:
        print("   ABORTO: sin id de la fuente nueva no hay verificacion posible")
        return 1

    print("== 4. verificacion FUERTE de la publicacion: descargar y comparar por sha")
    scratch = Path(tempfile.mkdtemp(prefix="wb-"))
    intentos = []
    bajado = None
    try:
        for i in range(1, 4):
            destino = scratch / f"post-{i}.bin"
            rc_d, sal_d = qmind(["source", "download", "--nb", NB, nuevo_id, "-o", str(destino)])
            if rc_d == 0 and destino.is_file():
                intentos.append(0)
                bajado = destino.read_bytes()
                break
            intentos.append(1)
            print(f"   intento {i}: exit={rc_d} | {sal_d.strip().splitlines()[:1]}")
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    print(f"   RACHA de descargas POST = {'-'.join(str(x) for x in intentos)}")
    if bajado is None:
        print("   [NO-EVALUABLE] la fuente nueva no bajo: NO se declara publicada")
        return 1
    print(f"   bajado: {len(bajado)} B | sha256 {sha(bajado)}")
    print(f"   IGUAL AL DISCO = {bajado == disco} (por crudo) | "
          f"sha igual = {sha(bajado) == sha(disco)}")

    print("== 5. poblACION DESPUES: las previas intactas y una fuente mas")
    rc, salida = qmind(["source", "list", "--nb", NB, "--all", "--format", "json"])
    fuentes_despues = json.loads(salida[salida.find("{"):]).get("sources") or []
    print(f"   rc={rc} | fuentes = {len(fuentes_antes)} -> {len(fuentes_despues)}")
    por_id_d = {f.get("id"): f for f in fuentes_despues}
    for sid in PREVIAS:
        for k in [x for x in por_id_d if (x or "").startswith(sid)]:
            print(f"   previa {k[:22]}… status={por_id_d[k].get('status')} "
                  f"presente={k in por_id and por_id[k].get('title') == por_id_d[k].get('title')}")
    nuevas = [f for f in fuentes_despues if f.get("id") == nuevo_id]
    print(f"   la fuente nueva esta listada = {bool(nuevas)}")
    if nuevas:
        m = (nuevas[0].get("metadata") or {})
        print(f"   su metadata en el listado: sha={m.get('fileSha256')} size={m.get('fileSize')}")
    stem = [f for f in fuentes_despues if STEM in (f.get("title") or "")]
    print(f"   fuentes que conservan el stem del {STEM[:24]}…: {len(stem)} "
          f"(todas vivas: {all(f.get('status') == 'ready' for f in stem)})")

    rc_despues, _ = frescura("6. POST, el verificador curado sobre el arbol publicado")
    print("== 7. el hermano que decide por titulo, re-emitido (no se le toca)")
    proc = subprocess.run([sys.executable, str(RAIZ / "scripts" / "validate_qmind_writeback.py"),
                           "--strict"], cwd=str(RAIZ), capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=600)
    for l in (proc.stdout or "").splitlines():
        if "[" in l and (")" in l or "]" in l):
            print("   " + redactar(l)[:170])
    print(f"   WRITEBACK_STRICT_EXIT={proc.returncode}")
    print("== 8. resumen de los dos veredictos de frescura")
    print(f"   PRE={rc_antes}  POST={rc_despues}   (PRE 1 es el vencido VERDADERO: el disco iba delante)")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    raise SystemExit(main())
