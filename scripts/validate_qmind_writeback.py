#!/usr/bin/env python3
"""
IA Hoteles Agent - QMind Write-back Validator
=============================================
Materializa el contrato de write-back del executor
(`.agents/workflows/phased_project_executor.md` v2.20.0):

- :572-574 — al cierre de cada fase, el `10-analisis-post-implementacion.md`
  actualizado se re-ingiere al notebook QMind `iah-cli-lecciones`.
- :588    — QMind indexa snapshots de contenido, no rutas; archivar NO requiere
  acción en QMind; re-ingerir SOLO si cambia el contenido.

Este validador comprueba, contra el notebook real (vía CLI `qmind source list`,
no contra un manifest manual), que todo plan archivado en
`.opencode/plans/Archives/` que tenga `10-analisis-post-implementacion.md`
tiene al menos una fuente ingesta cuyo título lo identifique.

Reemplaza la confianza en que la sesión recuerde el write-back (el punto de
fallo histórico del ciclo de capitalización de lecciones).

Uso:
    python scripts/validate_qmind_writeback.py             # verifica ingesta Y contenido
    python scripts/validate_qmind_writeback.py --nb <ID>   # fuerza notebook
    python scripts/validate_qmind_writeback.py --strict    # falla si qmind no está disponible
    python scripts/validate_qmind_writeback.py --upload TRIBUNAL-OFFLINE-2026-09-09
        # write-back: sube 10-analisis + CONTEXT con declaración durable
    python scripts/validate_qmind_writeback.py --upload C:/ruta/al/plan
        # write-back con ruta absoluta
    python scripts/validate_qmind_writeback.py --upload <PLAN> --file <copia saneada> --title <titulo>
        # actualización explícita: sube ese archivo con ese título, guarda la instantánea
        # versionada y marca como `reemplazada` la fuente vigente anterior del mismo plan.
        # Con --file o --title presentes solo se publica ese documento (los CONTEXT no entran);
        # sin ellos --upload se comporta exactamente como siempre.

El criterio dejó de ser la existencia del título (premisas P3 y P4 del mini-plan
`VERIFICADOR-ESCRITURA-QMIND-2026-09-20`). Hay dos capas:
- **ingesta por título** sobre los `10-analisis` archivados (la de siempre);
- **contenido y vigencia** sobre el registro de instantáneas
  (`.opencode/qmind-writeback/registro.json`), con el mismo dialecto de frescura del hermano
  `verify_qmind_context_freshness.py` (contrato D2): `metadata.fileSha256`/`fileSize` del propio
  `source list` como primera vía, la **descarga + sha256** como verificación de esa promesa,
  `NO-EVALUABLE` cuando no hubo observación (nunca `VENCIDO` ni verde) y `PROMESA-ROTA` si la
  descarga desmiente al índice.

Son **dos preguntas separadas** (AC1/AC2 de `CURA-INSTRUMENTOS-QMIND-S15-2026-10-07`, schema 1.1):
- *¿el plan cambió?* → `sha_cuerpo` grabado al publicar contra el sha del cuerpo actual del repo.
- *¿lo publicado casa con el servidor?* → la capa D2 de arriba, sobre la instantánea.

Publicar una **copia saneada** (`--file`) deja de ser estructuralmente vencible: el cuerpo del repo ya no
se compara contra los bytes ingeridos. Una entrada sin `sha_cuerpo` (registro `1.0`, anterior a la cura) es
`NO-EVALUABLE por migracion`: no se rellena hacia atrás, porque calcular el sha de hoy y escribirlo en la
entrada vieja daría verde por construcción.

Códigos de salida (verificación):
    0 — medido y vigente: cada 10-analisis archivado está ingestado y cada instantánea vigente
        casa por contenido
    1 — rojo medido: falta ingesta, cuerpo vencido, promesa rota o dos fuentes vigentes del
        mismo plan sin marca de reemplazo
    2 — NO-EVALUABLE: la medición no ocurrió (CLI ausente sin --strict, instantánea o cuerpo
        inaccesibles, registro sin entradas). **No es PASS**: el resumen lo nombra como estado
        propio. Con --strict la ausencia del CLI se anuncia como FAIL (1) en vez de WARN (2).
Códigos de salida (--upload): 0 = publicado y registrado; 1 = fallo o mal uso de --file/--title.
"""

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
ANALISIS_FILENAME = "10-analisis-post-implementacion.md"
NOTEBOOK_TITLE = "iah-cli-lecciones"
TRAILING_DATE = re.compile(r"-\d{4}-\d{2}-\d{2}$")
CONTEXT_DIR = ROOT_DIR / ".opencode" / "context"
PLANS_DIR = ROOT_DIR / ".opencode" / "plans"
REGISTRO_PATH = ROOT_DIR / ".opencode" / "qmind-writeback" / "registro.json"
INSTANEAS_DIR = ROOT_DIR / ".opencode" / "qmind-writeback" / "instantaneas"
REGISTRO_ESQUEMA = "1.1"
ESTADO_VIGENTE = "vigente"
ESTADO_REEMPLAZADA = "reemplazada"
ID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
CONTEXT_DECLARATION_MARKERS = [
    re.compile(r"^Lección de forma:", re.MULTILINE),
    re.compile(r"^Lección durable:", re.MULTILINE),
    re.compile(r"^Lecciones capitalizadas", re.MULTILINE),
]


def norm(value: str) -> str:
    return unicodedata.normalize("NFC", value).strip()


def collect_archived_analisis(plans_dir: Path = None) -> list:
    """Retorna [(plan_dir_name, ruta_al_10_analisis)] de los planes archivados.

    La raiz se pasa como dato (default `PLANS_DIR`) para que la bateria monte su poblacion en un tmp y el
    arbol real quede gobernado por el mismo codigo — la misma decision del hermano de frescura.
    """
    base = plans_dir if plans_dir is not None else PLANS_DIR
    archives = base / "Archives"
    if not archives.is_dir():
        return []
    results = []
    for plan_dir in sorted(archives.iterdir()):
        if not plan_dir.is_dir():
            continue
        analisis = plan_dir / ANALISIS_FILENAME
        if analisis.is_file():
            results.append((plan_dir.name, analisis))
    return results


def resolve_notebook_id(explicit: str) -> str:
    """Resuelve el ID del notebook: argumento explícito o búsqueda por título."""
    if explicit:
        return explicit
    exit_code, output = _run_qmind(["notebook", "list", "--format", "json"])
    if exit_code != 0:
        raise QmindUnavailable(f"qmind notebook list falló: {_first_line(output)}")
    data = json.loads(output)
    notebooks = data.get("notebooks", data if isinstance(data, list) else [])
    matches = [nb for nb in notebooks if norm(nb.get("title", "")) == NOTEBOOK_TITLE]
    if not matches:
        raise QmindUnavailable(
            f"No se encontró el notebook '{NOTEBOOK_TITLE}' en la cuenta (fallback :468)"
        )
    return matches[0]["id"]


class QmindUnavailable(RuntimeError):
    """qmind CLI ausente, sin auth, o notebook no encontrado."""


def _qmind_exe() -> str:
    """Resuelve la ruta del CLI. En Windows npm instala qmind.CMD, que CreateProcess
    no puede ejecutar por nombre corto ('qmind' sin extensión) — hay que pasar la ruta resuelta."""
    exe = shutil.which("qmind")
    if exe is None:
        raise QmindUnavailable("CLI 'qmind' no está instalado ni en PATH")
    return exe


def _run_qmind(args: list) -> tuple:
    try:
        result = subprocess.run(
            [_qmind_exe(), *args], capture_output=True,
            encoding="utf-8", errors="replace", timeout=120
        )
        return result.returncode, result.stdout + result.stderr
    except FileNotFoundError:
        raise QmindUnavailable("CLI 'qmind' no está instalado ni en PATH")
    except subprocess.TimeoutExpired:
        raise QmindUnavailable("qmind no respondió (timeout 120s)")


def fetch_source_titles(notebook_id: str) -> list:
    exit_code, output = _run_qmind(
        ["source", "list", "--nb", notebook_id, "--all", "--format", "json"]
    )
    if exit_code != 0:
        raise QmindUnavailable(f"qmind source list falló: {_first_line(output)}")
    data = json.loads(output)
    items = data if isinstance(data, list) else data.get("sources", data.get("items", []))
    return [norm(s.get("title", "")) for s in items]


def sha256_de(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def _validar_id(valor: str, etiqueta: str) -> str:
    """Los ids que entran al CLI están validados por patrón, no interpolados crudos."""
    if not ID_RE.match(valor or ""):
        raise QmindUnavailable(f"{etiqueta} no es un UUID válido: {valor!r}")
    return valor


def fetch_sources(notebook_id: str) -> list:
    """Fuente -> {id, title, sha_metadata, tam_metadata}. Clave del listado: `sources`.

    Es la primera vía del contrato D2: `metadata.fileSha256`/`fileSize` son lo que el servidor
    declara sobre sus propios bytes, y nunca deciden solos — la descarga los verifica.
    """
    exit_code, output = _run_qmind(
        ["source", "list", "--nb", _validar_id(notebook_id, "nb"), "--all", "--format", "json"]
    )
    if exit_code != 0:
        raise QmindUnavailable(f"qmind source list falló: {_first_line(output)}")
    inicio = output.find("{")
    if inicio < 0:
        raise QmindUnavailable(f"el listado no trae JSON: {_first_line(output)}")
    data = json.loads(output[inicio:])
    items = data if isinstance(data, list) else data.get("sources", data.get("items", []))
    return [{"id": s.get("id", ""), "title": norm(s.get("title", "")),
             "sha_metadata": (s.get("metadata") or {}).get("fileSha256", ""),
             "tam_metadata": (s.get("metadata") or {}).get("fileSize", "")}
            for s in items if s.get("id")]


def descargar_fuente(notebook_id: str, source_id: str, destino: Path) -> bool:
    """Descarga una fuente. False si la bajada no dejó archivo legible."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    exit_code, output = _run_qmind(
        ["source", "download", "--nb", _validar_id(notebook_id, "nb"),
         _validar_id(source_id, "source id"), "-o", str(destino)]
    )
    if exit_code != 0:
        print(f"  [AVISO] descarga {source_id} salió {exit_code}: {_first_line(output)}")
        return False
    return destino.is_file()


def cuerpo_del_plan(plan: str, plans_dir: Path = None) -> Path:
    """El 10-analisis del plan, resuelto en raíz de planes o bajo `Archives/`.

    Un `git mv` del archivado mueve el cuerpo sin mover el registro: devuelve None y la capa de
    contenido lo publica como NO-EVALUABLE, nunca como VENCIDO.
    """
    base = plans_dir if plans_dir is not None else PLANS_DIR
    for relativo in (plan, f"Archives/{plan}"):
        candidato = base / relativo / ANALISIS_FILENAME
        if candidato.is_file():
            return candidato
    return None


def cargar_registro(ruta: Path) -> dict:
    """El registro versionado de publicaciones. Ausente = registro vacío, no error."""
    if not ruta.is_file():
        return {"schema_version": REGISTRO_ESQUEMA, "entradas": []}
    try:
        datos = json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise QmindUnavailable(f"registro de write-back ilegible en {ruta}: {exc}")
    if not isinstance(datos.get("entradas"), list):
        raise QmindUnavailable(f"registro sin clave `entradas` (schema esperado {REGISTRO_ESQUEMA})")
    return datos


def guardar_registro(ruta: Path, datos: dict) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def entradas_del_plan(datos: dict, plan: str) -> list:
    return [e for e in datos["entradas"] if e.get("plan") == plan]


def titulo_por_defecto(plan: str) -> str:
    """El título histórico del write-back. Se conserva: cambiarlo rompería a los planes ya ingestaos."""
    return f"10-analisis: {plan} (lecciones aprendidas y decisiones)"


def directorio_de_instantaneas(ruta_registro: Path) -> Path:
    """Las instantáneas viven junto a su registro: el mismo directorio, para poder montar pruebas."""
    return ruta_registro.parent / "instantaneas"


def resolver_instanea(entrada: dict, ruta_registro: Path) -> Path:
    """La ruta guardada es relativa al registro: el montaje en tmp resuelve igual que el repo."""
    return directorio_de_instantaneas(ruta_registro) / entrada.get("instanea", "")


def raiz_de_planes(plan_dir: Path) -> Path:
    """La raiz bajo la que `cuerpo_del_plan()` re-resuelve el cuerpo de un plan pasado por `--upload`.

    `--upload` recibe `<PLAN>` o `Archives/<PLAN>` ya compuesto contra `--plans-dir`, y el sha que entra al
    registro es el del **cuerpo**: se re-resuelve con el mismo lector que usa la capa de verificación en vez
    de dar por hecho que `plan_dir/10-analisis` es el cuerpo.
    """
    return plan_dir.parent.parent if plan_dir.parent.name == "Archives" else plan_dir.parent


def registrar_publicacion(datos: dict, ruta_registro: Path, plan: str, titulo: str,
                          archivo: Path, fuente_id: str, fecha: str, cuerpo: Path) -> dict:
    """Copia la instantánea al repo, la registra como vigente y marca la anterior del mismo plan.

    `sha256` es el de la instantánea (lo que el servidor recibió) y `sha_cuerpo` el del cuerpo del plan en el
    momento de publicar (lo que el repo prometió): dos identidades, dos preguntas (AC1). Con `--file` las dos
    difieren por diseño —la copia va saneada— y la puerta de vigencia lee la segunda.

    Borrar la fuente antigua en el notebook es irreversible sobre contenido publicado y sigue
    siendo decisión escrita del operador (maestro §4): aquí se **marca**, no se borra.
    """
    slug = re.sub(r"[^A-Za-z0-9._-]+", "_", f"{plan}--{titulo}")[:120] + ".md"
    destino = directorio_de_instantaneas(ruta_registro) / slug
    destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(archivo, destino)
    sha = sha256_de(destino)
    for entrada in entradas_del_plan(datos, plan):
        if entrada.get("estado") == ESTADO_VIGENTE:
            entrada["estado"] = ESTADO_REEMPLAZADA
            entrada["reemplazada_por"] = titulo
    entrada = {"plan": plan, "titulo": titulo, "estado": ESTADO_VIGENTE,
               "fuente_id": fuente_id, "sha256": sha, "sha_cuerpo": sha256_de(cuerpo),
               "instanea": slug, "publicado": fecha}
    datos["entradas"].append(entrada)
    datos["schema_version"] = REGISTRO_ESQUEMA
    guardar_registro(ruta_registro, datos)
    return entrada


def is_ingested(plan_dir_name: str, titles: list) -> bool:
    """Un plan está ingestado si hay fuente '10-analisis' que lo nombre.

    Los títulos en el notebook siguen los patrones:
      '10-analisis: <PLAN> (lecciones aprendidas...)'
      '<PLAN> 10-analisis-post-implementacion (...)'
    El stem (nombre del directorio sin fecha final) cubre variantes de título
    como 'VALIDADOR-URL-PROPIA 10-analisis-post-implementacion'.
    """
    stem = TRAILING_DATE.sub("", plan_dir_name)
    for title in titles:
        if "10-analisis" not in title:
            continue
        if plan_dir_name in title or stem in title:
            return True
    return False


def _first_line(text: str) -> str:
    return (text.strip().splitlines() or ["(sin salida)"])[0][:200]


def upload_source(notebook_id: str, file_path: Path, title: str) -> tuple:
    """Ejecuta `qmind source upload`. Retorna (exit_code, output)."""
    exit_code, output = _run_qmind([
        "source", "upload",
        "--nb", notebook_id,
        "--file", str(file_path),
        "--title", title,
    ])
    return exit_code, output


def scan_context_declarations() -> list:
    """Retorna [(ruta, título)] de CONTEXT files en .opencode/context/ que
    autodeclaren una lección durable (executor :577-583)."""
    if not CONTEXT_DIR.is_dir():
        return []
    results = []
    for ctx_file in sorted(CONTEXT_DIR.glob("CONTEXT-*.md")):
        content = ctx_file.read_text(encoding="utf-8", errors="replace")
        if any(marker.search(content) for marker in CONTEXT_DECLARATION_MARKERS):
            title = f"CONTEXT: {ctx_file.stem}"
            results.append((ctx_file, title))
    return results


def _fuente_nombral(fuente: dict, plan: str) -> bool:
    """Si el título de la fuente nombra a este plan (mismo criterio de `is_ingested`, ahora por fuente)."""
    stem = TRAILING_DATE.sub("", plan)
    return "10-analisis" in fuente["title"] and (plan in fuente["title"] or stem in fuente["title"])


_CACHE_BAJADAS: dict = {}


def _hash_bajado(nb: str, source_id: str, scratch: Path, stem: str):
    """sha256 de lo que el notebook publica para `source_id`, descargando una vez por corrida."""
    clave = (nb, source_id)
    if clave in _CACHE_BAJADAS:
        return _CACHE_BAJADAS[clave]
    destino = scratch / f"{stem}--{source_id}.bin"
    if not descargar_fuente(nb, source_id, destino):
        _CACHE_BAJADAS[clave] = None
        return None
    valor = sha256_de(destino)
    _CACHE_BAJADAS[clave] = valor
    destino.unlink(missing_ok=True)
    return valor


def verificar_contenido(nb: str, fuentes: list, datos: dict, scratch: Path,
                        plans_dir: Path = None, registro_path: Path = None) -> tuple:
    """Contenido y vigencia de cada instantánea registrada. Devuelve (código, líneas).

    Códigos: 0 todo vigente, 1 rojo medido, 2 NO-EVALUABLE. El rojo manda sobre la abstención, y
    la abstención manda sobre el verde: lo que no se observó nunca se pinta de VENCIDO (D2).

    Dos preguntas separadas sobre la misma entrada (AC2): la **vigencia del plan** se dictamina cuerpo contra
    cuerpo (`sha_cuerpo` publicado vs sha del cuerpo actual), y la **fidelidad de lo publicado** sigue con la
    metadata del servidor y su descarga. La instantánea editada sin re-subuir la corta el gate de registro, que
    no se toca.
    """
    base = plans_dir if plans_dir is not None else PLANS_DIR
    ruta_registro = registro_path if registro_path is not None else REGISTRO_PATH
    lineas = []
    vigentes = [e for e in datos["entradas"] if e.get("estado") == ESTADO_VIGENTE]
    if not vigentes:
        return 2, [f"[NO-EVALUABLE] contenido: 0 instantaneas vigentes en "
                   f"{ruta_registro}; la capa de contenido no goberna nada hasta "
                   f"la primera publicacion por --upload"]

    rojo = 0
    abstencion = 0
    contador = {"cuerpo": 0, "remoto": 0, "migracion": 0, "local": 0}
    for e in vigentes:
        etiqueta = f"{e['plan']} :: {e['titulo']}"
        instanea = resolver_instanea(e, ruta_registro)
        cuerpo = cuerpo_del_plan(e["plan"], base)
        if not instanea.is_file():
            abstencion = 2
            contador["local"] += 1
            lineas.append(f"  [NO-EVALUABLE] {etiqueta}: la instantanea registrada no esta en {instanea}")
            continue
        if cuerpo is None:
            abstencion = 2
            contador["local"] += 1
            lineas.append(f"  [NO-EVALUABLE] {etiqueta}: el cuerpo del plan no resuelve bajo {base} "
                          f"(movido o archivado): re-fijar su ruta en el registro; no es VENCIDO")
            continue

        sha_inst = sha256_de(instanea)
        sha_cuerpo_ahora = sha256_de(cuerpo)
        if not e.get("sha_cuerpo"):
            abstencion = 2
            contador["migracion"] += 1
            lineas.append(f"  [NO-EVALUABLE] {etiqueta}: la entrada no grabo sha_cuerpo (registro schema "
                          f"{datos.get('schema_version') or 'sin_version'}), es anterior a la cura y no se "
                          f"rellena hacia atras; no es VENCIDO ni verde")
            continue
        contador["cuerpo"] += 1
        if e["sha_cuerpo"] != sha_cuerpo_ahora:
            rojo = 1
            lineas.append(f"  [VENCIDO] {etiqueta}: la instantanea publicada sobre otra version del cuerpo: "
                          f"el registro grabo sha_cuerpo={e['sha_cuerpo'][:12]}... y el cuerpo del repo "
                          f"({cuerpo}) hoy es {sha_cuerpo_ahora[:12]}...: re-publicar con titulo nuevo")
            continue
        if e.get("sha256") and e["sha256"] != sha_inst:
            rojo = 1
            lineas.append(f"  [VENCIDO] {etiqueta}: la instantanea publicada en disco ({sha_inst[:12]}...) no "
                          f"casa con el sha256={e['sha256'][:12]}... que declara el registro")
            continue

        prometidas = [f for f in fuentes if f["sha_metadata"] and f["sha_metadata"] == sha_inst]
        if prometidas:
            casadas, rotas, sin_bajar = [], [], []
            for fuente in prometidas:
                bajo = _hash_bajado(nb, fuente["id"], scratch, e["plan"])
                if bajo is None:
                    sin_bajar.append(fuente)
                elif bajo == sha_inst:
                    casadas.append(fuente)
                else:
                    rotas.append((fuente, bajo))
            if casadas:
                contador["remoto"] += 1
                lineas.append(f"  [FRESCO] {etiqueta}: {len(casadas)} fuente(s) que casan por metadata del "
                              f"servidor, promesa verificada por descarga+sha256")
            elif rotas:
                rojo = 1
                contador["remoto"] += 1
                for fuente, bajo in rotas:
                    lineas.append(f"  [PROMESA-ROTA] {etiqueta}: {fuente['id'][:13]}... declara "
                                  f"fileSha256={fuente['sha_metadata'][:12]}... y su descarga dio "
                                  f"{bajo[:12]}...: el indice y los bytes del servidor no casan")
                continue
            else:
                abstencion = 2
                lineas.append(f"  [NO-EVALUABLE] {etiqueta}: {len(sin_bajar)} fuente(s) cuyo metadata casa "
                              f"no bajaron; sin observacion no hay VENCIDO")
                continue
        else:
            candidatas = [f for f in fuentes if f["title"] == e["titulo"]]
            if not candidatas:
                rojo = 1
                contador["remoto"] += 1
                lineas.append(f"  [VENCIDO] {etiqueta}: ninguna fuente del notebook lleva el titulo "
                              f"registrado y el servidor no promete este sha")
            else:
                bajo = _hash_bajado(nb, candidatas[0]["id"], scratch, e["plan"])
                if bajo is None:
                    abstencion = 2
                    lineas.append(f"  [NO-EVALUABLE] {etiqueta}: la fuente {candidatas[0]['id'][:13]}... "
                                  f"no bajó; la comparacion de contenido no ocurrio")
                    continue
                if bajo != sha_inst:
                    rojo = 1
                    contador["remoto"] += 1
                    lineas.append(f"  [VENCIDO] {etiqueta}: titulo coincidente con contenido distinto "
                                  f"(publicado {sha_inst[:12]}... ingerido {bajo[:12]}...)")
                    continue
                contador["remoto"] += 1
                lineas.append(f"  [FRESCO] {etiqueta}: descarga+sha256 casa "
                              f"({sha_inst[:12]}...) con {candidatas[0]['id'][:13]}...")

        # Vigencia (AC4): toda fuente que nombra al plan debe estar contable en el registro.
        registrados = {t["titulo"] for t in entradas_del_plan(datos, e["plan"])}
        huesped = [f for f in fuentes if _fuente_nombral(f, e["plan"]) and f["title"] not in registrados]
        if huesped:
            rojo = 1
            for f in huesped:
                lineas.append(f"  [DUPLICADO-VIGENTE] {etiqueta}: la fuente {f['id'][:13]}... "
                              f"({f['title'][:60]}...) nombra al plan y no esta marcada como "
                              f"reemplazada: dos fuentes vigentes del mismo plan")
    lineas.append(f"  [CONTADOR] {len(vigentes)} vigente(s): {contador['cuerpo']} dictaminada(s) por cuerpo, "
                  f"{contador['remoto']} con fidelidad remota medida, {contador['migracion']} NO-EVALUABLE "
                  f"por migracion, {contador['local']} sin observacion local; cuerpo y remota son preguntas "
                  f"distintas y pueden solaparse: {contador['cuerpo']}+{contador['migracion']}"
                  f"+{contador['local']}=={len(vigentes)}")
    return (rojo or abstencion), lineas


def dentro_del_repo(ruta: Path, base: Path = None) -> bool:
    """El archivo que se publica tiene que ser una copia versionada bajo el repo (P6)."""
    raiz = base if base is not None else ROOT_DIR
    try:
        ruta.resolve().relative_to(raiz.resolve())
    except (ValueError, OSError):
        return False
    return True


def do_upload(plan_dir: Path, notebook_id: str, titulo: str = None, archivo: Path = None,
              registro_path: Path = None, fecha: str = None,
              repo_root: Path = None) -> int:
    """Write-back de un plan: sube el 10-analisis (+CONTEXT) o el documento explícito.

    Sin `titulo`/`archivo` el comportamiento es el histórico. Con ellos se publica ESA copia con
    ESE título: es la vía de actualización que el writer no tenía (P4), y deja en el repo la
    instantánea versionada que la capa de contenido va a verificar. El registro graba además el sha del
    cuerpo del plan (`sha_cuerpo`), que es lo que la puerta de vigencia compara (AC1).
    """
    registro_path = registro_path if registro_path is not None else REGISTRO_PATH
    base_repo = repo_root if repo_root is not None else ROOT_DIR
    if not plan_dir.is_dir():
        print(f"[FAIL] Upload: el directorio no existe: {plan_dir}")
        return 1

    analisis = plan_dir / ANALISIS_FILENAME
    explicita = bool(titulo or archivo)
    origen = archivo if archivo is not None else analisis
    if not origen.is_file():
        print(f"[FAIL] Upload: {origen} no existe")
        return 1
    if archivo is not None and not dentro_del_repo(archivo, base_repo):
        print(f"[FAIL] Upload: --file tiene que estar bajo el repo ({base_repo}); "
              f"{archivo} no lo está: se publica una copia versionada, no un archivo suelto")
        return 1

    plan_name = plan_dir.name
    cuerpo = cuerpo_del_plan(plan_name, raiz_de_planes(plan_dir))
    if cuerpo is None:
        print(f"[FAIL] Upload: el cuerpo de {plan_name} no resuelve bajo {raiz_de_planes(plan_dir)} "
              f"({ANALISIS_FILENAME}): sin cuerpo no hay sha_cuerpo que grabar y el registro no se inventa "
              f"uno")
        return 1

    try:
        titles = fetch_source_titles(notebook_id)
    except QmindUnavailable as exc:
        print(f"[FAIL] Upload: {exc}")
        return 1

    uploaded = 0
    skipped = 0
    failed = 0
    try:
        datos = cargar_registro(registro_path)
    except QmindUnavailable as exc:
        print(f"[FAIL] Upload: {exc}")
        return 1

    if explicita:
        analisis_title = norm(titulo) if titulo else titulo_por_defecto(plan_name)
        if analisis_title in [norm(t) for t in titles]:
            misma = [e for e in entradas_del_plan(datos, plan_name)
                     if e.get("titulo") == analisis_title
                     and e.get("sha256") == sha256_de(origen)]
            if misma:
                print(f"[SKIP] {analisis_title} — el contenido ya publicado casa por sha256: nada que re-subir")
                skipped += 1
            else:
                print(f"[FAIL] Upload: el título {analisis_title!r} ya está vigente en el notebook y su "
                      f"contenido no es el de {origen}. El backend no sobrescribe: re-usar ese título "
                      f"publicaría una segunda fuente sin marca de reemplazo. Publique con un título nuevo "
                      f"(la anterior queda marcada como reemplazada) o corrija el contenido.")
                return 1
        else:
            print(f"[UP] {analisis_title} <- {origen.name}")
            code, out = upload_source(notebook_id, origen, analisis_title)
            if code != 0:
                print(f"[FAIL] Upload falló: {_first_line(out)}")
                return 1
            entrada = registrar_publicacion(datos, registro_path, plan_name, analisis_title,
                                            origen, "", fecha or _hoy(), cuerpo)
            print(f"[OK] Registrada instantanea {entrada['instanea']} sha256={entrada['sha256']}")
            uploaded += 1
        print(f"\n[RESUMEN] upload={uploaded} skip={skipped} fail={failed}")
        return 0

    analisis_title = titulo_por_defecto(plan_name)
    if is_ingested(plan_name, titles):
        print(f"[SKIP] {analisis_title} — ya está ingestado (evitando duplicado, executor :584)")
        skipped += 1
    else:
        print(f"[UP] {analisis_title}")
        code, out = upload_source(notebook_id, analisis, analisis_title)
        if code != 0:
            print(f"[FAIL] Upload falló: {_first_line(out)}")
            failed += 1
        else:
            print(f"[OK] Subido: {analisis.stem}")
            entrada = registrar_publicacion(datos, registro_path, plan_name, analisis_title,
                                            analisis, "", fecha or _hoy(), cuerpo)
            print(f"[OK] Registrada instantanea {entrada['instanea']} sha256={entrada['sha256']}")
            uploaded += 1

    context_files = scan_context_declarations()
    for ctx_path, ctx_title in context_files:
        if norm(ctx_title) in titles:
            print(f"[SKIP] {ctx_title} — ya está ingestado")
            skipped += 1
            continue
        print(f"[UP] {ctx_title}")
        code, out = upload_source(notebook_id, ctx_path, ctx_title)
        if code != 0:
            print(f"[FAIL] Upload falló: {_first_line(out)}")
            failed += 1
        else:
            print(f"[OK] Subido: {ctx_path.name}")
            uploaded += 1

    print(f"\n[RESUMEN] upload={uploaded} skip={skipped} fail={failed}")
    return 1 if failed else 0


def _hoy() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Valida el write-back QMind de los 10-analisis: ingesta por titulo Y contenido vigente"
    )
    parser.add_argument("--nb", default="", help="ID del notebook (default: buscar 'iah-cli-lecciones')")
    parser.add_argument(
        "--strict", action="store_true",
        help="Sin qmind disponible corta FAIL (1) en vez de WARN + NO-EVALUABLE (2); en ambos casos "
             "deja de ser PASS"
    )
    parser.add_argument(
        "--upload", metavar="PLAN_DIR",
        help="Write-back: sube el 10-analisis y CONTEXT con declaración durable del plan indicado"
    )
    parser.add_argument(
        "--title", metavar="TITULO",
        help="Con --upload: titulo explicito de la publicacion (actualizacion). No colisiona en "
             "silencio con una fuente vigente del mismo plan."
    )
    parser.add_argument(
        "--file", metavar="RUTA", type=Path,
        help="Con --upload: archivo explicito que sube, obligado a estar bajo el repo (copia saneada "
             "y versionada)"
    )
    parser.add_argument(
        "--registro", metavar="RUTA", type=Path, default=REGISTRO_PATH,
        help="Ruta del registro versionado de publicaciones (default: .opencode/qmind-writeback/registro.json)"
    )
    parser.add_argument(
        "--plans-dir", metavar="RUTA", type=Path, default=PLANS_DIR,
        help="Raiz de planes con la que se resuelve el cuerpo de cada instantanea (default: .opencode/plans)"
    )
    args = parser.parse_args(argv)

    if (args.title or args.file) and not args.upload:
        print("[FAIL] QMind Write-back: --title y --file solo tienen sentido con --upload <PLAN>")
        return 1

    if args.upload:
        try:
            notebook_id = resolve_notebook_id(args.nb)
        except QmindUnavailable as exc:
            print(f"[FAIL] Upload: {exc}")
            return 1
        plan_dir = Path(args.upload)
        if not plan_dir.is_absolute():
            plan_dir = (args.plans_dir / plan_dir).resolve()
        return do_upload(plan_dir, notebook_id, titulo=args.title, archivo=args.file,
                         registro_path=args.registro)

    try:
        datos = cargar_registro(args.registro)
    except QmindUnavailable as exc:
        print(f"[FAIL] QMind Write-back: {exc}")
        return 1

    try:
        notebook_id = resolve_notebook_id(args.nb)
        fuentes = fetch_sources(notebook_id)
    except QmindUnavailable as exc:
        if args.strict:
            print(f"[FAIL] QMind Write-back: instrumento ausente — {exc}")
            return 1
        print(f"[WARN] QMind Write-back: verificación no ejecutada — {exc}")
        print(f"[WARN] Fallback executor :468 activo; registrar la limitación en dependencias-fases.md")
        print("[NO-EVALUABLE] qmind write-back: la medicion NO ocurrio; NO es PASS")
        return 2

    titles = [f["title"] for f in fuentes]
    archived = collect_archived_analisis(args.plans_dir)
    missing = [name for name, _ in archived if not is_ingested(name, titles)]
    if missing:
        print(f"[FAIL] QMind Write-back: {len(missing)} de {len(archived)} 10-analisis archivados sin ingesta")
        for name in missing:
            print(f"- {name}: sin fuente '10-analisis' en el notebook '{NOTEBOOK_TITLE}'")
        print("Fix: python scripts/validate_qmind_writeback.py --upload <PLAN> --file <copia saneada> --title <titulo nuevo>")
        print("Contexto: .opencode/context/QMIND-RECOVERY-MANIFEST.md / executor :572-574")
    else:
        print(f"[OK] QMind Write-back: {len(archived)}/{len(archived)} 10-analisis archivados ingested en '{NOTEBOOK_TITLE}'")

    scratch = Path(tempfile.mkdtemp(prefix="verif-writeback-"))
    try:
        codigo_contenido, lineas = verificar_contenido(
            notebook_id, fuentes, datos, scratch,
            plans_dir=args.plans_dir, registro_path=args.registro)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
        _CACHE_BAJADAS.clear()
    for linea in lineas:
        print(linea)

    codigo_titulo = 1 if missing else 0
    estado = "VENCIDO" if codigo_contenido == 1 else ("NO-EVALUABLE" if codigo_contenido == 2 else "OK")
    if codigo_titulo == 1 or codigo_contenido == 1:
        resumen = f"[FAIL] qmind write-back: titulo {'OK' if not missing else str(len(missing))+' falta(n)'} | contenido: {estado}"
        print(resumen)
        return 1
    if codigo_contenido == 2:
        if any("[CONTADOR]" in l for l in lineas):
            # Hubo poblacion y al menos una entrada se abstvo (migracion o cuerpo inaccesible): decir
            # «no goberna ninguna publicacion» seria falso, goberno a las que tenian sha_cuerpo.
            print("[NO-EVALUABLE] qmind write-back: titulo verificado | contenido: NO-EVALUABLE en alguna "
                  "publicacion (ver el [CONTADOR]); la abstencion no es PASS y no se pinta de VENCIDO")
        else:
            print("[NO-EVALUABLE] qmind write-back: titulo verificado | contenido: NO-EVALUABLE, la "
                  "comparacion no goberna ninguna publicacion todavia")
        return 2
    print(f"[PASS] qmind write-back: titulo y contenido vigentes ({len(archived)} archivado(s), "
          f"{len([l for l in lineas if '[FRESCO]' in l])} instantanea(s) fresca(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
