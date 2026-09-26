#!/usr/bin/env python3
"""Generador de briefing packs por fase (FASE-D de VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20).

POR QUE EXISTE (medido, no supuesto)
    El maestro §1, medicion A7: una sesion de fase declara **ocho** lecturas y las hace
    en ocho aperturas separadas (263.973 bytes ~ 65.993 tokens estimados en el plan
    medido). Este script compone por cada fase UN archivo con lo que su propio prompt
    declara leer, y mide el delta de carga total que eso produce.

QUE HACE
    Lee los `05-prompt-inicio-sesion-fase-*.md` del plan, extrae de cada uno la lista
    de lectura que **ese prompt declara** en su bloque «Prompt de ejecucion» (la cadena
    que empieza por `Lee `), resuelve cada seccion nombrada (`§N`, `§Nombre`, `§1-§4`)
    y emite `<plan>/briefing/FASE-X.md` con la seccion copiada literal y su procedencia
    al pie. Declara `no_incluye[]` y `lectura_aparte_obligatoria[]` — el workflow
    canonic entra ahi mientras la deuda D3 no lo rebane.

PROHIBIDO EDITAR A MANO
    Es un artefacto generado: se regenera con `--plan`. `--check` lo vence comparando
    el **sha256 de cada fuente de `sources[]` contra el arbol vigente**. `head` es
    procedencia, no llave de caducidad: si goberlara, el commit que guarda el pack lo
    dejaria vencido dentro de ese commit (invalidacion circular, contrato
    §Carga total y frescura del pack).

TRES ESTADOS, NINGUNO COLAPSADO (AC22, L-PF6, L-PF10)
    COMPLETO · SECCION-NO-RESUELTA (nombra la seccion pedida y las rutas intentadas) ·
    FUENTE-AUSENTE (el pack **no se emite**: un pack mas corto en silencio esta prohibido).

Cero dependencias de proveedor y cero red: es determinista.

Uso:
    python scripts/build_phase_briefing.py --plan VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20
    python scripts/build_phase_briefing.py --plan <nombre|ruta> [--plan <ruta> ...]
    python scripts/build_phase_briefing.py --plan <ruta> --check
    python scripts/build_phase_briefing.py --plan <ruta> --informe [-]
    python scripts/build_phase_briefing.py --plan <ruta> --carga [-]
    python scripts/build_phase_briefing.py --plan <ruta> --listar-declarado
    python scripts/build_phase_briefing.py --fuentes-modulos <simbolo> --plan <ruta>

Archivos bajo `Archives/` tambien se resuelven: el RELEASE regenera y verifica el pack
**despues** del `git mv` (AC19).

Salida: 0 = packs emitidos y frescos; 1 = pack no emitido, vencido o --check rojo;
        2 = error de uso (plan no resuelto).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PLANS = ROOT / ".opencode" / "plans"
WORKFLOW_CANONICO = ".agents/workflows/phased_project_executor.md"
PROMPT_RE = re.compile(r"^05-prompt-inicio-sesion-fase-(.+)\.md$")
BRIEFING_DIRNAME = "briefing"
DIVISOR_TOKENS = 4
UNIDAD_BYTES = "stat -c %s <ruta>"

ESTADO_COMPLETO = "COMPLETO"
ESTADO_RECORTE = "SECCION-NO-RESUELTA"
ESTADO_AUSENTE = "FUENTE-AUSENTE"
CAUSAS_CHECK = ("FUENTE-AUSENTE", "SHA-DISTINTO", "FUENTE-ILEGIBLE", "PACK-AUSENTE")

META_INICIO = "<!-- BEGIN BRIEFING-META"
META_FIN = "END BRIEFING-META -->"
META_RE = re.compile(r"<!-- BEGIN BRIEFING-META\n(.*?)\nEND BRIEFING-META -->", re.S)

MARCA_RECORTE = "[SECCION-NO-RESUELTA]"

# ---------------------------------------------------------------------------
# Guard AC23: el simbolo real que niega el truncamiento silencioso.
# Apagarlo NO cambia ninguna otra ruta del programa: deja de escribir el bloque
# que declara el recorte, y el pack se achica sin decirlo — que es exactamente
# lo que los tests de AC22 afirman.
# ---------------------------------------------------------------------------
GUARD_NO_TRUNCAMIENTO_ACTIVO = True


class RecorteNoDeclarado(RuntimeError):
    """El pack perderia una seccion pedida sin declararla: no se emite."""


# ---------------------------------------------------------------------------
# medidas
# ---------------------------------------------------------------------------

def sha_de(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def bytes_de(texto: str) -> int:
    return len(texto.encode("utf-8"))


def tokens_estimados(n_bytes: int) -> int:
    """Estimacion por divisor declarado (A7 del maestro), no recuento de tokenizer."""
    return n_bytes // DIVISOR_TOKENS


def _sin_acentos(texto: str) -> str:
    crudo = unicodedata.normalize("NFD", texto)
    return "".join(c for c in crudo if unicodedata.category(c) != "Mn").lower()


def _fuente_vista(ruta: Path, raiz: Path) -> str:
    try:
        return ruta.resolve().relative_to(raiz.resolve()).as_posix()
    except ValueError:
        return ruta.as_posix()


def log(mensaje: str) -> None:
    """Progreso a stderr: stdout queda solo para el JSON pedido (S12)."""
    print(mensaje, file=sys.stderr)


def ahora_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def head_actual(raiz: Path) -> tuple[str, str]:
    """Procedencia, con estado propio cuando no hay arbol git (clon `git archive`)."""
    try:
        r = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=str(raiz),
                           capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return "SIN-ARBOL-GIT", "git no es ejecutable en este entorno"
    if r.returncode != 0:
        return "SIN-ARBOL-GIT", (r.stderr or r.stdout).strip() or "git rev-parse fallo"
    return r.stdout.strip(), "git rev-parse --short HEAD"


# ---------------------------------------------------------------------------
# resolucion del plan (Archives/ incluido: es la llamada del RELEASE)
# ---------------------------------------------------------------------------

def _prompts_de(plan_dir: Path) -> list[tuple[str, Path]]:
    out = []
    for p in sorted(plan_dir.glob("05-prompt-inicio-sesion-fase-*.md")):
        m = PROMPT_RE.match(p.name)
        if m:
            out.append((m.group(1), p))
    return out


def rutas_intentadas(nombre_o_ruta: str, plans_dir: Path) -> list[str]:
    crudo = Path(nombre_o_ruta)
    base = [plans_dir / crudo.name, plans_dir / "Archives" / crudo.name, crudo]
    vistos, out = set(), []
    for c in base:
        clave = str(c).lower()
        if clave in vistos:
            continue
        vistos.add(clave)
        out.append(c.resolve().as_posix())
    return out


def resolver_plan(nombre_o_ruta: str, plans_dir: Path) -> Path | None:
    """El plan bajo `plans_dir/`, bajo `plans_dir/Archives/`, o la ruta dada tal cual."""
    for c in [plans_dir / Path(nombre_o_ruta).name,
              plans_dir / "Archives" / Path(nombre_o_ruta).name,
              Path(nombre_o_ruta)]:
        if c.is_dir() and _prompts_de(c):
            return c
    return None


# ---------------------------------------------------------------------------
# la lista de lectura DECLARADA por el prompt
# ---------------------------------------------------------------------------

def _bloque_texto_prompt(texto: str) -> str:
    """Contenido de los bloques fenced del documento (el de ejecucion esta entre ellos).

    Todos, no solo el ultimo: limitar la busqueda al ultimo bloque verdea vacio cuando
    el `Lee` vive en otro lado.
    """
    return "\n".join(re.findall(r"^```[a-zA-Z]*\n(.*?)^```", texto, re.S | re.M))


def _oracion_lee(bloque: str) -> str:
    """Desde `Lee ` al inicio de linea hasta el primer punto de fin de oracion.

    «Punto de fin» = esta a profundidad de parentesis cero **y** va seguido de espacio o
    de fin del bloque: los puntos de `01-plan-maestro.md` y de `263.973` no cierran nada,
    y cortar por ellos dejaria el pack con dos de las ocho lecturas declaradas.
    """
    m = re.search(r"^Lee ", bloque, re.M)
    if not m:
        return ""
    texto = bloque[m.start():]
    prof = 0
    for i, ch in enumerate(texto):
        if ch == "(":
            prof += 1
        elif ch == ")":
            prof = max(0, prof - 1)
        elif ch == "." and prof == 0 and (i + 1 >= len(texto) or texto[i + 1] in " \n"):
            return " ".join(texto[:i + 1].split())
    return " ".join(texto.split())


def _dividir_superficies(texto: str) -> list[str]:
    """Trocea por comas y por ` y ` a profundidad de parentesis cero."""
    partes: list[str] = []
    buf: list[str] = []
    prof = 0
    i = 0
    while i < len(texto):
        ch = texto[i]
        if ch == "(":
            prof += 1
        elif ch == ")":
            prof -= 1
        if prof == 0 and ch == ",":
            partes.append("".join(buf))
            buf = []
            i += 1
            continue
        if prof == 0 and texto.startswith(" y ", i):
            partes.append("".join(buf))
            buf = []
            i += 3
            continue
        buf.append(ch)
        i += 1
    partes.append("".join(buf))
    return [p.strip(" ,.") for p in partes if p.strip(" ,.")]


def _secciones_y_cuerpo(trozo: str) -> tuple[list[str], str]:
    """Refs `§` declaradas (aunque esten dentro de un parentetico) + el cuerpo del item.

    `§1-§4` se colapsa a rango. El cuerpo se reconstruye borrando los spans `§`, para
    que un titulo de seccion con espacios («§Carga total y frescura del pack») no deje
    restos dentro del nombre del archivo.
    """
    texto = re.sub(r"§\s*([0-9]+)\s*-\s*§", r"§\1-", trozo)
    posiciones = [m.start() for m in re.finditer("§", texto)]
    spans = [(ini, posiciones[k + 1] if k + 1 < len(posiciones) else len(texto))
             for k, ini in enumerate(posiciones)]
    refs: list[str] = []
    for ini, fin in spans:
        crudo = re.sub(r"\([^()]*\)", "", texto[ini + 1:fin])
        crudo = crudo.split("(")[0].strip(" .,)»\u201d\u201c`\"'")
        crudo = re.sub(r"\s+y$", "", crudo)
        if crudo:
            refs.append(crudo)
    cuerpo = texto
    for ini, fin in reversed(spans):
        cuerpo = cuerpo[:ini] + cuerpo[fin:]
    cuerpo = re.sub(r"\([^()]*\)", "", cuerpo)
    cuerpo = re.sub(r"\([^()]*$", "", cuerpo)
    cuerpo = re.sub(r"\s+y$", "", cuerpo)
    return refs, cuerpo.strip(" ,.")


def parsear_lista_lectura(texto_prompt: str) -> list[dict]:
    """Items declarados: documento + secciones + calificador parentetico + literal.

    Un item que no nombra archivo ni workflow es prosa («los cuatro prompts de fase»):
    se conserva para que el pack lo **declare**, no para adivinarlo.
    """
    oracion = _oracion_lee(_bloque_texto_prompt(texto_prompt))
    if not oracion:
        return []
    oracion = re.sub(r"^Lee\s+", "", oracion).strip()
    items: list[dict] = []
    for trozo in _dividir_superficies(oracion):
        trozo = trozo.replace("**", "").strip()
        if not trozo:
            continue
        refs, cuerpo = _secciones_y_cuerpo(trozo)
        secciones: list[str] = []
        for ref in refs:
            if re.fullmatch(r"[0-9]+\s*-\s*[0-9]+", ref):
                a, b = (int(x) for x in re.split(r"\s*-\s*", ref))
                secciones += [str(n) for n in range(a, b + 1)]
            else:
                secciones.append(ref)
        calif = " ".join(re.findall(r"\(([^()]*)\)", trozo))
        if not cuerpo:
            if items and secciones:
                items[-1]["secciones"] = list(dict.fromkeys(items[-1]["secciones"] + secciones))
                continue
            cuerpo = trozo
        ruta_md = re.search(r"[\w./-]+\.md", cuerpo)
        if re.search(r"workflow\s+(can[oó]nic|canonical)", cuerpo, re.I):
            doc, clase = WORKFLOW_CANONICO, "workflow"
        elif ruta_md:
            doc, clase = ruta_md.group(0).lstrip("./"), "archivo"
        elif "/" in cuerpo and cuerpo.endswith((".py", ".json", ".yaml")):
            doc, clase = cuerpo.lstrip("./"), "archivo"
        else:
            doc, clase = cuerpo, "prosa"
        items.append({"documento": doc, "clase": clase,
                      "secciones": list(dict.fromkeys(secciones)),
                      "calificador": calif, "declarado": trozo})
    return items


# ---------------------------------------------------------------------------
# secciones de un documento
# ---------------------------------------------------------------------------

TITULO_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")


def _titulos(lineas: list[str]) -> list[dict]:
    out = []
    for i, linea in enumerate(lineas):
        m = TITULO_RE.match(linea.rstrip("\r"))
        if m:
            out.append({"indice": i, "nivel": len(m.group(1)), "texto": m.group(2)})
    return out


def _numero_titulo(texto: str) -> str:
    m = re.match(r"^([0-9]+)\b", texto.strip())
    return m.group(1) if m else texto.strip()


def _hits_de(lineas_doc: list[str], ref: str) -> list[dict]:
    titulos = _titulos(lineas_doc)
    if ref.isdigit():
        return [t for t in titulos if t["nivel"] >= 2 and _numero_titulo(t["texto"]) == ref]
    aguja = _sin_acentos(ref)
    return [t for t in titulos if t["nivel"] >= 2 and aguja in _sin_acentos(t["texto"])]


def _extensa(lineas: list[str], titulo: dict) -> str:
    """Del titulo hasta el siguiente titulo de nivel igual o menor."""
    titulos = _titulos(lineas)
    fin = len(lineas)
    for t in titulos:
        if t["indice"] > titulo["indice"] and t["nivel"] <= titulo["nivel"]:
            fin = t["indice"]
            break
    return "\n".join(lineas[titulo["indice"]:fin]).rstrip("\n")


def resolver_secciones(texto: str, refs: list[str]) -> tuple[dict[str, str], list[str], list[str]]:
    """(resueltas por ref, no resueltas, titulos de nivel 1-2 del documento)."""
    lineas = texto.split("\n")
    resueltas: dict[str, str] = {}
    no_resueltas: list[str] = []
    candidatos = [t["texto"] for t in _titulos(lineas) if t["nivel"] <= 2]
    for ref in refs:
        hits = _hits_de(lineas, ref)
        if len(hits) == 1:
            resueltas[ref] = _extensa(lineas, hits[0])
        else:
            no_resueltas.append(ref)
    return resueltas, no_resueltas, candidatos


def resolver_ruta_documento(doc: str, plan_dir: Path, raiz: Path) -> tuple[Path | None, list[str]]:
    """Ruta del documento declarado + las rutas intentadas (por si hay que declararla)."""
    candidatos = [plan_dir / doc, plan_dir / Path(doc).name, raiz / doc]
    for c in candidatos:
        if c.is_file():
            return c, [x.as_posix() for x in candidatos]
    return None, [c.as_posix() for c in candidatos]


# ---------------------------------------------------------------------------
# el pack de una fase
# ---------------------------------------------------------------------------

def construir_fase(plan_dir: Path, fase: str, prompt: Path, head: str,
                   generado_en: str, raiz: Path) -> dict:
    texto_prompt = prompt.read_text(encoding="utf-8", errors="replace")
    declarados = parsear_lista_lectura(texto_prompt)
    # Vacio != ausente (L-PF10): un prompt que no declara ninguna lectura en el formato
    # `Lee ...` produce un pack SIN-DECLARACION, no un COMPLETO — medido: 0 de los 27
    # planes archivados usan esa convencion, y llamarlo COMPLETO seria el verde vacuo.
    declaracion = "DECLARADA" if declarados else "SIN-DECLARACION"
    fuentes: list[dict] = []
    no_incluye: list[str] = []
    lectura_aparte: list[str] = [WORKFLOW_CANONICO]
    estado = ESTADO_COMPLETO
    if declaracion == "SIN-DECLARACION":
        no_incluye.append(
            "todo — el prompt no declara lectura en el formato parseado ("
            "una linea `Lee ...` dentro de un bloque fenced de «Prompt de ejecucion»)")

    for item in declarados:
        doc, clase = item["documento"], item["clase"]
        if clase == "workflow":
            ruta_wf = raiz / WORKFLOW_CANONICO
            n = len(ruta_wf.read_bytes()) if ruta_wf.is_file() else 0
            fuentes.append({
                "declarado": item["declarado"], "documento": doc, "clase": "workflow",
                "ruta": _fuente_vista(ruta_wf, raiz), "existe": ruta_wf.is_file(),
                "gobernada": False, "en_pack": False, "sha256": None,
                "bytes_documento": n, "bytes_copiados": 0, "calificador": item["calificador"],
                "secciones_pedidas": list(item["secciones"]), "secciones_resueltas": [],
                "secciones_no_resueltas": list(item["secciones"]), "candidatos": [],
                "rutas_intentadas": [ruta_wf.as_posix()],
                "motivo": "no se copia: lectura aparte obligatoria mientras D3 no lo rebane",
            })
            continue
        if clase == "prosa":
            estado = ESTADO_RECORTE
            fuentes.append({
                "declarado": item["declarado"], "documento": doc, "clase": "prosa",
                "ruta": None, "existe": False, "gobernada": False, "en_pack": False,
                "sha256": None, "bytes_documento": 0, "bytes_copiados": 0,
                "calificador": item["calificador"],
                "secciones_pedidas": list(item["secciones"]), "secciones_resueltas": [],
                "secciones_no_resueltas": list(item["secciones"]) or ["(el item no nombra un archivo)"],
                "candidatos": [], "rutas_intentadas": [],
                "motivo": "el prompt nombra un conjunto en prosa, no una ruta: no se adivina",
            })
            no_incluye.append(f"{doc} — declarado en prosa, sin ruta: queda por leer aparte")
            continue

        ruta, intentadas = resolver_ruta_documento(doc, plan_dir, raiz)
        if ruta is None:
            estado = ESTADO_AUSENTE
            fuentes.append({
                "declarado": item["declarado"], "documento": doc, "clase": "archivo",
                "ruta": None, "existe": False, "gobernada": False, "en_pack": False,
                "sha256": None, "bytes_documento": 0, "bytes_copiados": 0,
                "calificador": item["calificador"],
                "secciones_pedidas": list(item["secciones"]), "secciones_resueltas": [],
                "secciones_no_resueltas": list(item["secciones"]) or ["(documento)"],
                "candidatos": [], "rutas_intentadas": intentadas,
                "motivo": "fuente ausente: el pack no se emite",
            })
            continue

        es_prompt_propio = ruta.resolve() == prompt.resolve()
        visible = _fuente_vista(ruta, raiz)
        if not visible.startswith(".opencode/"):
            # Copiar un documento de FUERA de `.opencode/` **hacia dentro** cambiaria la
            # poblacion que escanea `validate_opencode_refs.py` ([8/11] del quick): cada
            # referencia que ese texto contiene pasaria a contar como referencia nueva del
            # plan, y un derivado no puede reabrir gates ajenos. Se declara lectura aparte,
            # con su ruta y sus bytes, y sigue entrando a la carga de los dos lados.
            n_doc = len(ruta.read_bytes())
            if visible not in lectura_aparte:
                lectura_aparte.append(visible)
            no_incluye.append(
                f"{visible} — declarada por el prompt pero vive fuera de `.opencode/`: se lee "
                "aparte para no ampliar la poblacion que escanea validate_opencode_refs.py")
            fuentes.append({
                "declarado": item["declarado"], "documento": doc, "clase": "aparte",
                "ruta": visible, "existe": True, "gobernada": False, "en_pack": False,
                "sha256": None, "bytes_documento": n_doc, "bytes_copiados": 0,
                "calificador": item["calificador"], "secciones_pedidas": list(item["secciones"]),
                "secciones_resueltas": [], "secciones_no_resueltas": [], "candidatos": [],
                "rutas_intentadas": [visible], "copia_documento_completo": False,
                "motivo": "fuera de .opencode/: lectura aparte, no se copia",
            })
            continue
        texto = ruta.read_text(encoding="utf-8", errors="replace")
        copia_completa = False
        if item["secciones"] and not es_prompt_propio:
            resueltas, no_res, candidatos = resolver_secciones(texto, item["secciones"])
        elif es_prompt_propio:
            resueltas, no_res, candidatos = {}, [], []
            copia_completa = True
            if item["secciones"]:
                no_incluye.append(
                    f"{doc} — el prompt pide secciones de su propio archivo; se copia entero "
                    "para no recortar las instrucciones de la fase")
        else:
            resueltas, no_res, candidatos = {}, [], []
            copia_completa = True
        copiados = sum(bytes_de(v) for v in resueltas.values())
        if copia_completa:
            copiados = bytes_de(texto)
        n_documento = len(ruta.read_bytes())
        if no_res:
            estado = ESTADO_RECORTE
        fuera = max(0, n_documento - copiados)
        if fuera:
            no_incluye.append(
                f"{doc} — {fuera} bytes fuera de lo declarado "
                f"({', '.join(item['secciones']) or 'documento completo'})")
        fuentes.append({
            "declarado": item["declarado"], "documento": doc, "clase": "archivo",
            "ruta": _fuente_vista(ruta, raiz), "existe": True,
            "gobernada": not es_prompt_propio,
            "en_pack": bool(resueltas) or copia_completa,
            "copia_documento_completo": copia_completa,
            "sha256": sha_de(ruta), "bytes_documento": n_documento,
            "bytes_copiados": copiados, "calificador": item["calificador"],
            "secciones_pedidas": list(item["secciones"]),
            "secciones_resueltas": list(resueltas), "secciones_no_resueltas": no_res,
            "candidatos": candidatos, "rutas_intentadas": intentadas,
            "motivo": None if not no_res else "seccion declarada y no resuelta",
            "es_prompt_propio": es_prompt_propio,
        })

    return {
        "fase": fase, "plan": plan_dir.name, "prompt": _fuente_vista(prompt, raiz),
        "head": head, "generated_at": generado_en, "estado": estado,
        "declaracion": declaracion,
        "lectura_aparte_obligatoria": lectura_aparte, "no_incluye": no_incluye,
        "fuentes": fuentes, "divisor_tokens": DIVISOR_TOKENS,
    }


def _declarar_recorte(fuente: dict) -> str:
    """El bloque que declara el recorte. Con el guard AC23 apagado devuelve cadena vacia."""
    if not GUARD_NO_TRUNCAMIENTO_ACTIVO:
        return ""
    rutas = ", ".join(fuente["rutas_intentadas"]) or "(sin ruta)"
    candidatos = ", ".join(fuente.get("candidatos", [])) or "—"
    return "\n".join([
        f"### {MARCA_RECORTE} `{fuente['documento']}` — secciones pedidas y no resueltas",
        "",
        f"- **seccion pedida**: {', '.join(fuente['secciones_no_resueltas'])}",
        f"- **declarado literal en el prompt**: `{fuente['declarado']}`",
        f"- **rutas intentadas**: {rutas}",
        f"- **titulos disponibles en el documento**: {candidatos}",
        f"- **motivo**: {fuente['motivo']}",
        "- **consecuencia**: este pack **no** esta completo. No se emite un pack mas corto en "
        "silencio (AC22): quien ejecute esta fase lee ademas lo nombrado arriba.",
    ])


def render_pack(paquete: dict, raiz: Path) -> str:
    lineas = [
        f"# Briefing pack — FASE-{paquete['fase']}",
        "",
        "> **Artefacto generado. NO editar a mano.** Regenerar con:",
        f"> `python scripts/build_phase_briefing.py --plan {paquete['plan']}`",
        "> La frescura la gobierna el sha256 de `sources[]` contra el arbol vigente:",
        f"> `python scripts/build_phase_briefing.py --plan {paquete['plan']} --check`.",
        "",
        f"- **plan**: `{paquete['plan']}`",
        f"- **fuente de lo declarado**: `{paquete['prompt']}` (bloque «Prompt de ejecucion»)",
        f"- **estado del pack**: `{paquete['estado']}`",
        f"- **declaracion de lectura en el prompt**: `{paquete.get('declaracion', 'DECLARADA')}`",
        f"- **procedencia**: HEAD `{paquete['head']}` · generado `{paquete['generated_at']}`",
        f"- **tokens**: estimados por divisor {DIVISOR_TOKENS}, no recuento de tokenizer",
        "",
        "## Lectura aparte obligatoria (el pack **no** la sustituye)",
        "",
    ]
    for ruta in paquete["lectura_aparte_obligatoria"]:
        p = raiz / ruta
        n = len(p.read_bytes()) if p.is_file() else 0
        if ruta == WORKFLOW_CANONICO:
            motivo = ("se lee aparte mientras la deuda **D3** no rebane el workflow por fase; "
                      "copiarlo aqui seria rebanar `.agents/` por la puerta de atras (AC17)")
        else:
            motivo = ("el prompt la declara pero vive fuera de `.opencode/`: copiarla dentro "
                      "ampliaria la poblacion que escanea `validate_opencode_refs.py` ([8/11])")
        lineas.append(f"- `{ruta}` — {n} bytes (~{tokens_estimados(n)} tokens). {motivo}.")
    lineas += ["", "## Que **no** incluye este pack", ""]
    lineas += ([f"- {x}" for x in paquete["no_incluye"]]
               or ["- Nada omitido: el prompt no declaro secciones parciales."])
    lineas += ["", "---", "", "# Contenido declarado, copiado de su fuente", ""]

    declaro_recorte = False
    for fuente in paquete["fuentes"]:
        if fuente["secciones_no_resueltas"]:
            bloque = _declarar_recorte(fuente)
            if bloque:
                declaro_recorte = True
                lineas += [bloque, ""]
        if not fuente["en_pack"] or fuente["ruta"] is None or fuente["clase"] == "workflow":
            continue
        texto = (raiz / fuente["ruta"]).read_text(encoding="utf-8", errors="replace")
        if fuente.get("copia_documento_completo"):
            refs = ["(documento completo)"]
        else:
            refs = fuente["secciones_resueltas"]
        for ref in refs:
            if ref == "(documento completo)":
                seccion, rotulo = texto, f"`{fuente['documento']}` (documento completo)"
            else:
                lineas_doc = texto.split("\n")
                hits = _hits_de(lineas_doc, ref)
                if not hits:
                    continue
                seccion = _extensa(lineas_doc, hits[0])
                rotulo = f"`{fuente['documento']}` §{ref}"
            lineas += [
                f"## Fuente: {rotulo}", "", seccion, "",
                f"> **Procedencia**: `{fuente['ruta']}` · sha256 `{fuente['sha256']}` · "
                f"{bytes_de(seccion)} bytes copiados de {fuente['bytes_documento']} del documento · "
                f"HEAD `{paquete['head']}` · generado `{paquete['generated_at']}`",
                "",
            ]

    if paquete["estado"] == ESTADO_RECORTE and not declaro_recorte and GUARD_NO_TRUNCAMIENTO_ACTIVO:
        raise RecorteNoDeclarado(
            "el pack se marcaria SECCION-NO-RESUELTA sin ningun bloque que nombre el recorte")

    meta = {
        "generado_por": "scripts/build_phase_briefing.py",
        "plan": paquete["plan"], "fase": paquete["fase"], "estado": paquete["estado"],
        "declaracion": paquete.get("declaracion", "DECLARADA"),
        "provenance": {"head": paquete["head"], "generated_at": paquete["generated_at"]},
        "no_incluye": paquete["no_incluye"],
        "lectura_aparte_obligatoria": paquete["lectura_aparte_obligatoria"],
        "sources": [{"ruta": f["ruta"], "sha256": f["sha256"], "documento": f["documento"],
                     "secciones": f["secciones_resueltas"], "en_pack": f["en_pack"]}
                    for f in paquete["fuentes"] if f["gobernada"]],
        "divisor_tokens": DIVISOR_TOKENS,
    }
    lineas += ["---", "", META_INICIO, json.dumps(meta, ensure_ascii=False, indent=2), META_FIN, ""]
    return "\n".join(lineas)


# ---------------------------------------------------------------------------
# generar / verificar
# ---------------------------------------------------------------------------

def linea_de_estado(pack: dict, emitido: Path | None) -> str:
    """Lo que la sesion lee en stdout al producir el pack: se publica como coste (AC20)."""
    return (f"[pack] FASE-{pack['fase']}: {pack['estado']} -> "
            f"{emitido.name if emitido else 'no emitido'}\n")


def invocacion_literal(plan_dir: Path, raiz: Path) -> str:
    return (f"./venv/Scripts/python.exe scripts/build_phase_briefing.py --plan "
            f"{_fuente_vista(plan_dir, raiz)}")


def generar(plan_dir: Path, briefing_dir: Path, raiz: Path) -> tuple[list[dict], int]:
    head, _ = head_actual(raiz)
    stamp = ahora_utc()
    paquetes: list[dict] = []
    salio = 0
    for fase, prompt in _prompts_de(plan_dir):
        pack = construir_fase(plan_dir, fase, prompt, head, stamp, raiz)
        if pack["estado"] == ESTADO_AUSENTE:
            emitido = None
            salio = max(salio, 1)
        else:
            briefing_dir.mkdir(parents=True, exist_ok=True)
            destino = briefing_dir / f"FASE-{fase}.md"
            destino.write_bytes(render_pack(pack, raiz).encode("utf-8"))
            emitido = destino
        paquetes.append(pack)
        log(linea_de_estado(pack, emitido).rstrip("\n"))
        for f in pack["fuentes"]:
            if f["secciones_no_resueltas"] or not f["existe"]:
                log(f"    - {f['documento']}: {f['motivo']} | pedidas "
                      f"{f['secciones_no_resueltas']} | rutas {f['rutas_intentadas']}")
    pedidas = sum(len(f["secciones_pedidas"]) for p in paquetes for f in p["fuentes"])
    resueltas = sum(len(f["secciones_resueltas"]) for p in paquetes for f in p["fuentes"])
    no_resueltas = sum(len(f["secciones_no_resueltas"]) for p in paquetes for f in p["fuentes"])
    por_estado = {e: sum(1 for p in paquetes if p["estado"] == e)
                  for e in (ESTADO_COMPLETO, ESTADO_RECORTE, ESTADO_AUSENTE)}
    log(f"[denominador] {len(paquetes)} packs · "
          + " · ".join(f"{e} {n}" for e, n in por_estado.items())
          + f" · fuentes {sum(len(p['fuentes']) for p in paquetes)}"
          + f" · secciones pedidas {pedidas}, resueltas {resueltas}, declaradas no resueltas "
            f"{no_resueltas}")
    return paquetes, salio


def leer_meta(ruta_pack: Path) -> dict | None:
    try:
        texto = ruta_pack.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    m = META_RE.search(texto)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return None


def verificar(plan_dir: Path, briefing_dir: Path, raiz: Path) -> tuple[list[dict], int]:
    """Frescura por sha de las fuentes gobernadas. HEAD solo informa procedencia (AC21)."""
    head, _ = head_actual(raiz)
    resultados: list[dict] = []
    salio = 0
    for fase, _prompt in _prompts_de(plan_dir):
        ruta_pack = briefing_dir / f"FASE-{fase}.md"
        if not ruta_pack.is_file():
            salio = 1
            resultados.append({"fase": fase, "causa": "PACK-AUSENTE",
                               "detalle": ruta_pack.as_posix()})
            log(f"[VENCIDO] FASE-{fase}: PACK-AUSENTE -> {ruta_pack.as_posix()}")
            continue
        meta = leer_meta(ruta_pack)
        if meta is None:
            salio = 1
            resultados.append({"fase": fase, "causa": "FUENTE-ILEGIBLE",
                               "detalle": f"el pack {ruta_pack.name} no trae bloque BRIEFING-META"})
            log(f"[VENCIDO] FASE-{fase}: FUENTE-ILEGIBLE (sin bloque BRIEFING-META)")
            continue
        incidencias: list[dict] = []
        for src in meta["sources"]:
            if not src.get("sha256"):
                incidencias.append({"fuente": src["ruta"], "causa": "FUENTE-ILEGIBLE",
                                    "motivo": "el bloque de procedencia no publica sha256"})
                continue
            ruta = raiz / src["ruta"]
            if not ruta.is_file():
                incidencias.append({"fuente": src["ruta"], "causa": "FUENTE-AUSENTE",
                                    "sha_esperado": src["sha256"]})
                continue
            try:
                actual = sha_de(ruta)
            except OSError as e:
                incidencias.append({"fuente": src["ruta"], "causa": "FUENTE-ILEGIBLE",
                                    "motivo": str(e)})
                continue
            if actual != src["sha256"]:
                incidencias.append({"fuente": src["ruta"], "causa": "SHA-DISTINTO",
                                    "sha_publicado": src["sha256"], "sha_arbol": actual})
        procedencia_distinta = meta["provenance"]["head"] != head
        if incidencias:
            salio = 1
            log(f"[VENCIDO] FASE-{fase}: {len(incidencias)} fuente(s) movidas")
            for i in incidencias:
                log(f"    - {i['causa']}: {i['fuente']}")
        elif not meta["sources"]:
            # Cero fuentes no es un verde: es un check sin nada que verificar (L-PF10).
            log(f"[SIN-FUENTES] FASE-{fase}: 0 fuentes gobernadas — nada que vencer "
                "(el prompt no declaro lectura)")
        else:
            extra = " (procedencia distinta, no vence)" if procedencia_distinta else ""
            log(f"[OK] FASE-{fase}: {len(meta['sources'])} fuentes frescas{extra}")
        resultados.append({"fase": fase, "causa": None if not incidencias else "VENCIDO",
                           "incidencias": incidencias,
                           "estado": meta["estado"],
                           "declaracion": meta.get("declaracion", "DECLARADA"),
                           "fuentes": len(meta["sources"]),
                           "sin_fuentes": not meta["sources"],
                           "procedencia_distinta": procedencia_distinta,
                           "head_pack": meta["provenance"]["head"], "head_arbol": head})
    return resultados, salio


# ---------------------------------------------------------------------------
# carga total (AC20) e informe (AC19/AC21/AC22)
# ---------------------------------------------------------------------------

def medir_carga(paquetes: list[dict], plan_dir: Path, briefing_dir: Path,
                raiz: Path) -> dict:
    wf = raiz / WORKFLOW_CANONICO
    n_wf = len(wf.read_bytes()) if wf.is_file() else 0
    invoc = invocacion_literal(plan_dir, raiz)
    por_fase = []
    for pack in paquetes:
        declaradas = [f for f in pack["fuentes"] if f["clase"] != "workflow"]
        ausentes = [f for f in declaradas if not f["existe"]]
        ruta_pack = briefing_dir / f"FASE-{pack['fase']}.md"
        emitido = ruta_pack if (pack["estado"] != ESTADO_AUSENTE and ruta_pack.is_file()) else None
        antes = {
            "workflow_obligatorio": n_wf + sum(f["bytes_documento"] for f in declaradas if f["existe"]),
            "coste_de_generacion": 0, "pack_consumido": 0,
        }
        despues = {
            "workflow_obligatorio": n_wf + sum(
                f["bytes_documento"] for f in declaradas if not f["en_pack"]),
            "coste_de_generacion": bytes_de(invoc) + bytes_de(linea_de_estado(pack, emitido)),
            "pack_consumido": len(emitido.read_bytes()) if emitido else 0,
        }
        t_antes, t_despues = sum(antes.values()), sum(despues.values())
        antes["total"], antes["tokens_estimados"] = t_antes, tokens_estimados(t_antes)
        despues["total"], despues["tokens_estimados"] = t_despues, tokens_estimados(t_despues)
        presentes = [f for f in declaradas if f["existe"]]
        copiado = sum(f["bytes_copiados"] for f in presentes if f["en_pack"])
        omitido = sum(max(0, f["bytes_documento"] - f["bytes_copiados"])
                      for f in presentes if f["secciones_pedidas"])
        coste = despues["coste_de_generacion"]
        andamiaje = despues["pack_consumido"] - copiado
        por_fase.append({
            "fase": f"FASE-{pack['fase']}", "estado": pack["estado"],
            "before": antes, "after": despues,
            "total_before": t_antes, "total_after": t_despues,
            "delta_bytes": t_antes - t_despues,
            "delta_tokens_estimados": tokens_estimados(t_antes) - tokens_estimados(t_despues),
            "workflow_canonico_bytes": n_wf,
            "copiado_a_pack_bytes": copiado,
            "andamiaje_del_pack_bytes": andamiaje,
            "omitido_declarado_bytes": omitido,
            "resta_comprobada": (t_antes - t_despues) == (omitido - andamiaje - coste),
            "fuentes_ausentes": [f["documento"] for f in ausentes],
        })
    claves = ("workflow_obligatorio", "coste_de_generacion", "pack_consumido")
    total = {lado: {k: sum(f[lado][k] for f in por_fase) for k in claves}
             for lado in ("before", "after")}
    for lado in total:
        total[lado]["total"] = sum(total[lado].values())
        total[lado]["tokens_estimados"] = tokens_estimados(total[lado]["total"])
    total["delta_bytes"] = total["before"]["total"] - total["after"]["total"]
    total["delta_tokens_estimados"] = (total["before"]["tokens_estimados"]
                                       - total["after"]["tokens_estimados"])
    return {"por_fase": por_fase, "total": total}


def rutas_de_stat(paquetes: list[dict], briefing_dir: Path, raiz: Path) -> dict:
    """Las rutas que `stat -c %s` imprime en cada lado del par pre/post.

    Con **multiplicidad por fase**: un documento que declaran cinco fases aparece cinco veces,
    porque cada sesion lo abre por su cuenta. Deduplicar aqui daria una lista que no reproduce
    la suma medida, que es justo lo que el par pre/post existe para comprobar.
    """
    antes: list[str] = []
    despues: list[str] = []
    for pack in paquetes:
        antes.append(WORKFLOW_CANONICO)
        despues.append(WORKFLOW_CANONICO)
        for f in pack["fuentes"]:
            if f["clase"] != "workflow" and f["existe"] and f["ruta"]:
                antes.append(f["ruta"])
        for f in pack["fuentes"]:
            if f["clase"] != "workflow" and f["existe"] and f["ruta"] and not f["en_pack"]:
                despues.append(f["ruta"])
        ruta_pack = briefing_dir / f"FASE-{pack['fase']}.md"
        if pack["estado"] != ESTADO_AUSENTE and ruta_pack.is_file():
            despues.append(_fuente_vista(ruta_pack, raiz))
    return {"before": antes, "after": despues,
            "cuenta": {"before": len(antes), "after": len(despues)},
            "nota": ("las fuentes que no existen no tienen ruta que `stat` pueda abrir: entran "
                     "al total con 0 bytes y se declaran en `fuentes_ausentes` de cada fase")}


def render_carga(paquetes: list[dict], plan_dir: Path, briefing_dir: Path,
                 raiz: Path) -> dict:
    medida = medir_carga(paquetes, plan_dir, briefing_dir, raiz)
    t = medida["total"]
    return {
        "tool": "build_phase_briefing.py", "ac": "AC20",
        "plan": _fuente_vista(plan_dir, raiz),
        "head": head_actual(raiz)[0], "generated_at": ahora_utc(),
        "method": {
            "comando_bytes": UNIDAD_BYTES,
            "comando_generacion": invocacion_literal(plan_dir, raiz),
            "divisor_tokens": DIVISOR_TOKENS,
            "suma_de_lado": ("stat -c %s sobre cada ruta de `rutas_stat.before` / "
                             "`rutas_stat.after` y sumar: las rutas salen repetidas por fase "
                             "porque cada sesion abre su copia; deduplicarlas daria una lista "
                             "que no reproduce la suma medida"),
            "reproduccion": ("./venv/Scripts/python.exe "
                             + invocacion_literal(plan_dir, raiz)
                             + " --carga evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/carga.json"),
            "sumandos": {
                "workflow_obligatorio": ("lo que la fase lee aparte del pack. En `before` es TODA la "
                                         "lectura declarada (todavia no existe pack, todo se lee "
                                         "aparte); en `after` queda reducido al workflow canonico mas "
                                         "las fuentes declaradas que no se pudieron copiar. Se publica "
                                         "separado `workflow_canonico_bytes` para no confundir la "
                                         "clave con el solo workflow"),
                "coste_de_generacion": ("la corrida del generador que la sesion ejecuta: bytes de la "
                                        "invocacion literal + bytes de la linea que imprime"),
                "pack_consumido": "bytes del pack que la fase efectivamente lee",
            },
            "resta": ("delta = total_before - total_after, y por construccion debe cuadrar con "
                      "omitido_declarado_bytes - andamiaje_del_pack_bytes - coste_de_generacion. "
                      "Se publica el resultado de esa comprobacion en `resta_comprobada`"),
            "regla": ("la resta va entre CARGAS TOTALES, no entre «fuentes» y «pack». Concatenar no "
                      "es ahorrar: el unico ahorro atribuible al pack es `omitido_declarado_bytes`, "
                      "lo que no entro porque no se declaro. Un delta cero o negativo es resultado "
                      "valido y se explica (L-D3)."),
        },
        "rutas_stat": rutas_de_stat(paquetes, briefing_dir, raiz),
        "por_fase": medida["por_fase"],
        "total": {
            "before": t["before"], "after": t["after"],
            "delta_bytes": t["delta_bytes"],
            "delta_tokens_estimados": t["delta_tokens_estimados"],
        },
    }


def construir_informe(paquetes: list[dict], verificacion: list[dict], plan_dir: Path,
                      briefing_dir: Path, raiz: Path) -> dict:
    head, fuente_head = head_actual(raiz)
    packs = []
    for pack in paquetes:
        packs.append({
            "fase": f"FASE-{pack['fase']}",
            "ruta_pack": _fuente_vista(briefing_dir / f"FASE-{pack['fase']}.md", raiz),
            "estado": pack["estado"],
            "declaracion": pack.get("declaracion", "DECLARADA"),
            "no_incluye": pack["no_incluye"],
            "lectura_aparte_obligatoria": pack["lectura_aparte_obligatoria"],
            "provenance": {"head": pack["head"], "generated_at": pack["generated_at"],
                           "head_fuente": fuente_head},
            "sources": [{"ruta": f["ruta"], "sha256": f["sha256"], "gobernada": f["gobernada"],
                         "documento": f["documento"], "en_pack": f["en_pack"],
                         "secciones_pedidas": f["secciones_pedidas"],
                         "secciones_resueltas": f["secciones_resueltas"],
                         "secciones_no_resueltas": f["secciones_no_resueltas"]}
                        for f in pack["fuentes"]],
            "fuentes_completas": pack["fuentes"],
        })
    por_estado = {e: sum(1 for p in paquetes if p["estado"] == e)
                  for e in (ESTADO_COMPLETO, ESTADO_RECORTE, ESTADO_AUSENTE)}
    total_fuentes = sum(len(p["fuentes"]) for p in paquetes)
    total_pedidas = sum(len(f["secciones_pedidas"]) for p in paquetes for f in p["fuentes"])
    total_resueltas = sum(len(f["secciones_resueltas"]) for p in paquetes for f in p["fuentes"])
    total_no_resueltas = sum(len([r for r in f["secciones_no_resueltas"]
                                  if r in f["secciones_pedidas"]])
                             for p in paquetes for f in p["fuentes"])
    total_recortes = sum(1 for p in paquetes for f in p["fuentes"] if f["secciones_no_resueltas"])
    return {
        "tool": "build_phase_briefing.py", "acs": ["AC19", "AC21", "AC22"],
        "plan": _fuente_vista(plan_dir, raiz), "head": head,
        "head_fuente": fuente_head, "generated_at": ahora_utc(),
        "status": "EMITIDO" if por_estado[ESTADO_AUSENTE] == 0 else "NO-EMITIDO",
        "packs": packs,
        "verificacion_check": verificacion,
        "coverage_basis": {
            "poblacion": ("los 05-prompt-inicio-sesion-fase-*.md del plan nombrado por --plan; "
                          "ningun otro archivo de plan se recorre"),
            "archivos_rastreados": len(paquetes),
            "archivos_prompts": {plan_dir.name: len(_prompts_de(plan_dir))},
            "fuentes_declaradas": total_fuentes,
            "secciones_pedidas": total_pedidas,
            "secciones_resueltas": total_resueltas,
            "secciones_no_resueltas": total_no_resueltas,
            "recortes_declarados_en_el_pack": total_recortes,
            "packs_por_estado": por_estado,
            "packs_sin_declaracion_de_lectura": sum(
                1 for p in paquetes if p.get("declaracion") == "SIN-DECLARACION"),
            "no_emitidos_por_fuente_ausente": por_estado[ESTADO_AUSENTE],
            "familias_no_cubiertas": [
                "el workflow canonico: se declara como lectura aparte, nunca se copia (AC17/D3)",
                "el codigo de scripts/: no es lectura declarada por los prompts",
                "la evidencia de otras fases (evidence/): no entra en el pack",
                "los archivos que un prompt nombra en prosa sin ruta: se declaran, no se adivinan",
                "las plantillas de documentacion dentro del workflow: ~un quinto de su volumen, "
                "propiedad de D3",
            ],
            "unidad_bytes": UNIDAD_BYTES,
            "divisor_tokens": DIVISOR_TOKENS,
            "comando": invocacion_literal(plan_dir, raiz),
            "medido_el": ahora_utc(),
        },
    }


def listar_declarado(plan_dir: Path, raiz: Path) -> int:
    head, _ = head_actual(raiz)
    for fase, prompt in _prompts_de(plan_dir):
        items = parsear_lista_lectura(prompt.read_text(encoding="utf-8", errors="replace"))
        log(f"FASE-{fase} ({prompt.name}): {len(items)} items declarados, head {head}")
        for it in items:
            log(f"  - [{it['clase']}] {it['documento']} | secciones {it['secciones']} "
                  f"| calificador {it['calificador'][:60]}")
    return 0


def fuentes_modulos(simbolo: str) -> list[str]:
    """Que modulos declaran una funcion propia en su lectura (denominador de AC19)."""
    out = []
    for p in sorted((ROOT / "scripts").glob("*.py")):
        try:
            items = parsear_lista_lectura(p.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
        if any(simbolo in it["documento"] for it in items):
            out.append(p.name)
    return out


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _salida(texto: str, destino: str | None) -> None:
    """Sin destino o `-`: imprime y NO escribe (S12/L-VCF-12). Con ruta: escribe ahi."""
    if destino is None or destino == "-":
        sys.stdout.write(texto)
        print("[aviso] no se escribio ningun archivo: pase una ruta para publicar el artefacto",
              file=sys.stderr)
        return
    p = Path(destino)
    if not p.is_absolute():
        p = ROOT / p
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(texto.encode("utf-8"))
    log(f"[escrito] {p.as_posix()}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Genera (o verifica) el briefing pack por fase de un plan")
    ap.add_argument("--plan", action="append", default=[],
                    help="nombre del plan o ruta, bajo plans/ o plans/Archives/ (repetible)")
    ap.add_argument("--plans-dir", type=Path, default=DEFAULT_PLANS)
    ap.add_argument("--briefing-dir", type=Path, default=None,
                    help="destino de los packs (por defecto <plan>/briefing)")
    ap.add_argument("--check", action="store_true", help="no escribe; vence por sha de fuentes")
    ap.add_argument("--informe", metavar="RUTA", default=None,
                    help="ruta donde escribir informe.json (o `-` para imprimir)")
    ap.add_argument("--carga", metavar="RUTA", default=None,
                    help="ruta donde escribir carga.json (o `-` para imprimir)")
    ap.add_argument("--listar-declarado", action="store_true",
                    help="imprime la lista de lectura que cada prompt declara")
    ap.add_argument("--fuentes-modulos", metavar="SIMBOLO", default=None,
                    help="que scripts nombran una funcion propia en su lectura declarada")
    args = ap.parse_args(argv)

    raiz = ROOT
    if args.fuentes_modulos:
        nombres = fuentes_modulos(args.fuentes_modulos)
        print(json.dumps({"simbolo": args.fuentes_modulos, "modulos": nombres,
                          "poblacion": len(list((raiz / "scripts").glob("*.py")))},
                         ensure_ascii=False, indent=2))
        return 0
    if not args.plan:
        print("[2] hace falta --plan <nombre|ruta>", file=sys.stderr)
        return 2

    resueltos: list[Path] = []
    for nombre in args.plan:
        p = resolver_plan(nombre, args.plans_dir)
        if p is None:
            print(f"[2] plan no resuelto: {nombre} — rutas intentadas: "
                  f"{', '.join(rutas_intentadas(nombre, args.plans_dir))}", file=sys.stderr)
            return 2
        resueltos.append(p)

    if args.listar_declarado:
        for plan_dir in resueltos:
            listar_declarado(plan_dir, raiz)
        return 0

    salio = 0
    for plan_dir in resueltos:
        briefing = args.briefing_dir or (plan_dir / BRIEFING_DIRNAME)
        if args.check:
            _, s = verificar(plan_dir, briefing, raiz)
            salio = max(salio, s)
            continue
        paquetes, s = generar(plan_dir, briefing, raiz)
        salio = max(salio, s)
        verificacion, s2 = verificar(plan_dir, briefing, raiz)
        salio = max(salio, s2)
        if args.informe is not None or args.carga is not None:
            informe = construir_informe(paquetes, verificacion, plan_dir, briefing, raiz)
        if args.informe is not None:
            _salida(json.dumps(informe, ensure_ascii=False, indent=2) + "\n", args.informe)
        if args.carga is not None:
            _salida(json.dumps(render_carga(paquetes, plan_dir, briefing, raiz),
                               ensure_ascii=False, indent=2) + "\n", args.carga)
    return salio


if __name__ == "__main__":
    sys.exit(main())
