"""review_inputs — resolvedor único de insumos para los cuatro revisores del Tribunal.

Dos defectos medidos gobiernan este módulo (F-P4.2, `01-plan-maestro.md` §1):

1. Cuando los gates bloquean, `run_v4_complete_mode` **borra** diagnóstico y propuesta
   antes de que los Bots lean. Un revisor que resolvía por glob encontraba `None` y su
   check devolvía la lista vacía: verde silencioso sobre un insumo nunca leído
   (`DiagnosisReviewer._check_pain_traceability`).
2. `artifact_paths.resolve_latest` sube tres ascendientes compartidos entre hoteles, así
   que "el más reciente" puede ser el documento de otra corrida.

La cura es un solo resolvedor con rutas **explícitas del mismo run_id**: antes de
cualquier borrado se conserva una copia interna **no exportable** (fuera del árbol
recursivo que empaqueta `DeliveryPackager`) y el manifiesto que la describe
(`review_input_manifest.json`) fija kind, ruta original, sha256, momento, `read_status`
y `disposition`. `retained_by_gate` es la retención deliberada; lo nunca generado sigue
`ABSENT`; y un documento declarado que ya no se alcanza es `NO_LEIDO`, jamás `OK` vacío.
"""

from __future__ import annotations

import hashlib
import json
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping, Optional

from modules.data_validation.whatsapp_contract import (
    READ_ABSENT,
    READ_ERROR,
    READ_NOT_READ,
    READ_OK,
)

MANIFEST_NAME = "review_input_manifest.json"
SNAPSHOT_DIRNAME = "_review_inputs"
SCHEMA_VERSION = "1.0"

DISPOSITION_RETAINED_BY_GATE = "retained_by_gate"
DISPOSITION_INTERNAL_COPY = "internal_review_copy"

# Los dos documentos cliente que el gate borra. El patron es el mismo que ya usaban
# los revisores, para que el fallback sin manifiesto no cambie de identidad.
KIND_DIAGNOSTICO = "diagnostico"
KIND_PROPUESTA = "propuesta"
KIND_PATTERNS: dict[str, str] = {
    KIND_DIAGNOSTICO: "01_DIAGNOSTICO_Y_OPORTUNIDAD*.md",
    KIND_PROPUESTA: "02_PROPUESTA_COMERCIAL*.md",
}
KIND_ORDER: tuple[str, ...] = (KIND_DIAGNOSTICO, KIND_PROPUESTA)

SOURCE_SNAPSHOT = "snapshot"
SOURCE_ORIGINAL = "original"
SOURCE_ZIP = "zip"
SOURCE_DELIVERY_DIR = "delivery_dir"
SOURCE_LEGACY_GLOB = "legacy-ancestor-walk"


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def manifest_path_for(v4_audit_dir: str | Path) -> Path:
    return Path(v4_audit_dir) / MANIFEST_NAME


def run_root_for(v4_audit_dir: str | Path) -> Path:
    """Directorio raiz de la corrida: la forma real del pipeline es ``run_root/hotel/v4_audit``.

    Con un ``v4_audit_dir`` menos profundo (fixtures unitarios) se usa el padre: la
    raiz solo tiene que ser el ancla desde la que ``snapshot_root`` es relativa, y el
    snapshot vive FUERA del directorio del hotel por construccion.
    """
    path = Path(v4_audit_dir)
    parents = list(path.parents)
    return parents[1] if len(parents) >= 2 else path.parent


def snapshot_root_for(run_root: str | Path, run_id: str) -> Path:
    return Path(run_root) / SNAPSHOT_DIRNAME / run_id


def _now_iso() -> str:
    return datetime.now().isoformat()


class ReviewInputRead:
    """Lectura de un insumo con su estado explicito (AC9).

    `content` es None salvo en READ_OK. Un estado de error nunca se renderiza como
    vacio favorable: quien consume el resultado debe mirar `read_status`.
    """

    __slots__ = (
        "kind",
        "read_status",
        "content",
        "source",
        "path",
        "sha256",
        "size_bytes",
        "disposition",
        "cause",
        "run_id",
    )

    def __init__(
        self,
        kind: str,
        read_status: str,
        *,
        content: Optional[str] = None,
        source: Optional[str] = None,
        path: Optional[str] = None,
        sha256: Optional[str] = None,
        size_bytes: Optional[int] = None,
        disposition: Optional[str] = None,
        cause: Optional[str] = None,
        run_id: str = "",
    ) -> None:
        self.kind = kind
        self.read_status = read_status
        self.content = content
        self.source = source
        self.path = path
        self.sha256 = sha256
        self.size_bytes = size_bytes
        self.disposition = disposition
        self.cause = cause
        self.run_id = run_id

    @property
    def ok(self) -> bool:
        return self.read_status == READ_OK

    def to_dict(self) -> dict:
        """Serializacion para los reportes: nunca incluye el contenido."""
        return {
            "kind": self.kind,
            "read_status": self.read_status,
            "source": self.source,
            "path": self.path,
            "sha256": self.sha256,
            "size_bytes": self.size_bytes,
            "disposition": self.disposition,
            "cause": self.cause,
            "run_id": self.run_id,
        }


def capture_review_inputs(
    *,
    run_root: str | Path,
    run_id: str,
    v4_audit_dir: str | Path,
    documents: Mapping[str, Optional[str | Path]],
    retained_by_gate: bool = False,
) -> dict:
    """Conserve una copia interna no exportable ANTES de cualquier borrado.

    Escribe `run_root/_review_inputs/<run_id>/<kind>/<archivo>` (hermano del directorio
    del hotel, fuera del `rglob` que empaqueta `DeliveryPackager`) y el manifiesto en
    `v4_audit_dir`. Retorna el manifiesto serializado.

    `retained_by_gate=True` estampa `disposition=retained_by_gate`: el pipeline va a
    borrar el original deliberadamente, y esa retención no es un hallazgo nuevo.
    """
    run_root = Path(run_root)
    v4_audit_dir = Path(v4_audit_dir)
    snapshot_root = snapshot_root_for(run_root, run_id)
    captured_at = _now_iso()

    entries: list[dict] = []
    for kind in KIND_ORDER:
        original = documents.get(kind)
        entry: dict[str, Any] = {
            "kind": kind,
            "run_id": run_id,
            "original_path": str(original) if original else None,
            "internal_path": None,
            "sha256": None,
            "size_bytes": None,
            "captured_at": captured_at,
            "read_status": READ_ABSENT,
            "disposition": DISPOSITION_RETAINED_BY_GATE if retained_by_gate else None,
            "cause": None,
        }

        if original is None or not Path(original).is_file():
            # Nunca generado: no hubo nada que retener, asi que la disposition de
            # retencion NO se estampa. Si se estampara, el lector tendria que elegir
            # entre NO_LEIDO (retirado por el gate) y ABSENT (jamas existio), y esa
            # confusion es el defecto que AC11 vino a separar.
            entry["read_status"] = READ_ABSENT
            entry["disposition"] = None
            entry["cause"] = "documento no generado por esta corrida"
            entries.append(entry)
            continue

        try:
            raw = Path(original).read_bytes()
        except OSError as exc:
            entry["read_status"] = READ_ERROR
            entry["cause"] = f"el original no se pudo leer: {exc}"
            entries.append(entry)
            continue

        internal = snapshot_root / kind / Path(original).name
        try:
            internal.parent.mkdir(parents=True, exist_ok=True)
            internal.write_bytes(raw)
        except OSError as exc:
            entry["read_status"] = READ_ERROR
            entry["cause"] = f"la copia interna no se pudo escribir: {exc}"
            entries.append(entry)
            continue

        entry.update(
            internal_path=internal.relative_to(run_root).as_posix(),
            sha256=sha256_bytes(raw),
            size_bytes=len(raw),
            read_status=READ_OK,
            disposition=(
                DISPOSITION_RETAINED_BY_GATE
                if retained_by_gate
                else DISPOSITION_INTERNAL_COPY
            ),
            cause=None,
        )
        entries.append(entry)

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "generated_at": captured_at,
        "snapshot_root": snapshot_root.relative_to(run_root).as_posix(),
        "documents": entries,
    }
    v4_audit_dir.mkdir(parents=True, exist_ok=True)
    with open(manifest_path_for(v4_audit_dir), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    return manifest


class ReviewInputs:
    """El unico resolvedor que los cuatro revisores y el Juez consultan.

    Con manifiesto: la ruta es explicita y anclada al `run_id`, sin competir por mtime
    con otros hoteles. Sin manifiesto (callers de tests unitarios y corridas viejas) se
    conserva el glob ascendente historico, pero el estado queda declarado en `source`
    como `legacy-ancestor-walk`: la ambiguedad se ve, no se herma en silencio.
    """

    def __init__(
        self,
        *,
        v4_audit_dir: str | Path,
        run_id: str = "",
        manifest: Optional[dict] = None,
        package_zip_path: Optional[str | Path] = None,
        deliveries_dir: Optional[str | Path] = None,
    ) -> None:
        self.v4_audit_dir = Path(v4_audit_dir)
        self.run_id = run_id or (manifest or {}).get("run_id", "")
        self.manifest = manifest
        self.package_zip_path = Path(package_zip_path) if package_zip_path else None
        self.deliveries_dir = Path(deliveries_dir) if deliveries_dir else None
        self.run_root = self._resolve_run_root()
        self._reads: dict[str, ReviewInputRead] = {}

    @classmethod
    def for_run(
        cls,
        v4_audit_dir: str | Path,
        *,
        run_id: str = "",
        manifest: Optional[dict] = None,
        package_zip_path: Optional[str | Path] = None,
        deliveries_dir: Optional[str | Path] = None,
    ) -> "ReviewInputs":
        """Instancia el resolvedor cargando el manifiesto del run si existe.

        ``manifest`` explicito manda sobre el disco: es la via con la que un test (o un
        operador) reproduce el estado "declarado pero la copia ya no esta", sin escribir
        dos veces el artefacto.
        """
        if manifest is None:
            path = manifest_path_for(v4_audit_dir)
            if path.is_file():
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        manifest = json.load(f)
                except (json.JSONDecodeError, OSError):
                    manifest = None
        return cls(
            v4_audit_dir=v4_audit_dir,
            run_id=run_id,
            manifest=manifest,
            package_zip_path=package_zip_path,
            deliveries_dir=deliveries_dir,
        )

    def _resolve_run_root(self) -> Path:
        return run_root_for(self.v4_audit_dir)

    # ── manifiesto ────────────────────────────────────────────────────

    def entry_for(self, kind: str) -> Optional[dict]:
        if not self.manifest:
            return None
        for entry in self.manifest.get("documents", []):
            if entry.get("kind") == kind:
                return entry
        return None

    def pinned_path(self, kind: str) -> Optional[Path]:
        """Ruta explicita del run que `artifact_paths.resolve_latest` debe respetar.

        Retorna None solo si el run no declaro ese kind; si lo declaro y la copia ya no
        esta, retorna la ruta ausente para que el llamador NO caiga al ascendiente.
        """
        entry = self.entry_for(kind)
        if entry is None:
            return None
        internal = entry.get("internal_path")
        if internal:
            return self.run_root / internal
        original = entry.get("original_path")
        return Path(original) if original else None

    # ── lecturas ──────────────────────────────────────────────────────

    def read_document(self, kind: str) -> ReviewInputRead:
        """Lee el insumo del run: copia interna primero, original despues, glob al final."""
        pattern = KIND_PATTERNS.get(kind)
        if pattern is None:
            raise ValueError(f"kind de revision desconocido: {kind}")

        entry = self.entry_for(kind)
        if entry is None:
            read = self._read_by_legacy_glob(kind, pattern)
        else:
            read = self._read_from_entry(kind, entry)

        self._reads[kind] = read
        return read

    def _read_from_entry(self, kind: str, entry: dict) -> ReviewInputRead:
        disposition = entry.get("disposition")
        base = ReviewInputRead(
            kind=kind,
            read_status=READ_ABSENT,
            disposition=disposition,
            run_id=self.run_id,
        )

        internal = entry.get("internal_path")
        if internal:
            path = self.run_root / internal
            raw, error = _read_bytes(path)
            if error == "archivo ausente":
                # La ruta explicita se PERDIO: el run declaro la copia y ya no esta.
                # Es NO_LEIDO (nadie lo leyó), no READ_ERROR (que reservamos para bytes
                # ilegibles o sha que no casa): confundirlos ocultaria la perdida de la
                # ruta del run, que es justo el rojo que exige AC11.
                base.read_status = READ_NOT_READ
                base.path = path.as_posix()
                base.cause = (
                    "la copia interna declarada por el manifiesto no esta en su ruta: "
                    "el insumo nunca fue leido"
                )
                return base
            if error is not None:
                base.read_status = READ_ERROR
                base.path = path.as_posix()
                base.cause = f"la copia interna no se pudo leer: {error}"
                return base
            declared = entry.get("sha256")
            digest = sha256_bytes(raw)
            if declared and declared != digest:
                base.read_status = READ_ERROR
                base.path = path.as_posix()
                base.sha256 = digest
                base.cause = "el sha256 de la copia interna no casa con el manifiesto"
                return base
            text = _decode(raw)
            if text is None:
                base.read_status = READ_ERROR
                base.path = path.as_posix()
                base.cause = "la copia interna no es UTF-8"
                return base
            base.read_status = READ_OK
            base.content = text
            base.source = SOURCE_SNAPSHOT
            base.path = path.as_posix()
            base.sha256 = digest
            base.size_bytes = len(raw)
            return base

        original = entry.get("original_path")
        if original:
            path = Path(original)
            raw, error = _read_bytes(path)
            if error is None:
                text = _decode(raw)
                if text is not None:
                    base.read_status = READ_OK
                    base.content = text
                    base.source = SOURCE_ORIGINAL
                    base.path = path.as_posix()
                    base.sha256 = sha256_bytes(raw)
                    base.size_bytes = len(raw)
                    return base
                base.read_status = READ_ERROR
                base.path = path.as_posix()
                base.cause = "el original no es UTF-8"
                return base
            # El original ya no esta: lo que decide es si la retencion fue deliberada.
            if disposition == DISPOSITION_RETAINED_BY_GATE:
                base.read_status = READ_NOT_READ
                base.path = path.as_posix()
                base.cause = (
                    "el gate retiro el documento del arbol cliente y no hay copia "
                    "interna: el insumo nunca fue leido"
                )
                return base
            base.read_status = READ_ABSENT
            base.path = path.as_posix()
            base.cause = entry.get("cause") or "el original declarado ya no existe"
            return base

        base.read_status = entry.get("read_status") or READ_ABSENT
        base.cause = entry.get("cause") or "documento nunca generado"
        return base

    def _read_by_legacy_glob(self, kind: str, pattern: str) -> ReviewInputRead:
        """Fallback sin manifiesto: resuelve por patron y DECLARA la ambiguedad."""
        from modules.quality_gates.tribunal.artifact_paths import read_text, resolve_latest

        path = resolve_latest(pattern, self.v4_audit_dir, self.deliveries_dir)
        if path is None:
            return ReviewInputRead(
                kind=kind,
                read_status=READ_ABSENT,
                cause="sin manifiesto de insumos y patron no resuelto",
                run_id=self.run_id,
            )
        content = read_text(path)
        if content is None:
            return ReviewInputRead(
                kind=kind,
                read_status=READ_ERROR,
                source=SOURCE_LEGACY_GLOB,
                path=path.as_posix(),
                cause="el archivo resuelto no se pudo leer",
                run_id=self.run_id,
            )
        return ReviewInputRead(
            kind=kind,
            read_status=READ_OK,
            content=content,
            source=SOURCE_LEGACY_GLOB,
            path=path.as_posix(),
            size_bytes=len(content.encode("utf-8")),
            cause="resuelto por patron ascendente: sin ancla de run_id",
            run_id=self.run_id,
        )

    def read_manifest_json(self) -> ReviewInputRead:
        """MANIFEST.json del paquete: desde el ZIP del run, no desde un directorio fantasma.

        L-E2E.1: en regimen ZIP-only nunca existio `deliveries/<hotel>/MANIFEST.json`, y
        los dos lectores que lo buscaban obtenian None sin decir por que.
        """
        kind = "manifest"
        if self.package_zip_path is not None and self.package_zip_path.is_file():
            try:
                with zipfile.ZipFile(self.package_zip_path) as zf:
                    raw = zf.read("MANIFEST.json")
            except KeyError:
                return self._record(ReviewInputRead(
                    kind=kind,
                    read_status=READ_ABSENT,
                    source=SOURCE_ZIP,
                    path=self.package_zip_path.as_posix(),
                    cause="MANIFEST.json no es miembro del paquete",
                    run_id=self.run_id,
                ))
            except (zipfile.BadZipFile, OSError) as exc:
                return self._record(ReviewInputRead(
                    kind=kind,
                    read_status=READ_ERROR,
                    source=SOURCE_ZIP,
                    path=self.package_zip_path.as_posix(),
                    cause=f"el paquete no se pudo abrir: {exc}",
                    run_id=self.run_id,
                ))
            text = _decode(raw)
            if text is None:
                return self._record(ReviewInputRead(
                    kind=kind,
                    read_status=READ_ERROR,
                    source=SOURCE_ZIP,
                    path=self.package_zip_path.as_posix(),
                    cause="MANIFEST.json no es UTF-8",
                    run_id=self.run_id,
                ))
            try:
                data = json.loads(text)
            except json.JSONDecodeError as exc:
                return self._record(ReviewInputRead(
                    kind=kind,
                    read_status=READ_ERROR,
                    source=SOURCE_ZIP,
                    path=self.package_zip_path.as_posix(),
                    cause=f"MANIFEST.json no es JSON valido: {exc}",
                    run_id=self.run_id,
                ))
            return self._record(ReviewInputRead(
                kind=kind,
                read_status=READ_OK,
                content=data,
                source=SOURCE_ZIP,
                path=self.package_zip_path.as_posix(),
                sha256=sha256_bytes(raw),
                size_bytes=len(raw),
                run_id=self.run_id,
            ))

        if self.deliveries_dir is None or not self.deliveries_dir.is_dir():
            return self._record(ReviewInputRead(
                kind=kind,
                read_status=READ_ABSENT,
                cause="sin paquete del run ni deliveries_dir que consultar",
                run_id=self.run_id,
            ))

        from modules.quality_gates.tribunal.artifact_paths import load_json, pick_most_recent

        path = pick_most_recent(self.deliveries_dir.glob("*/MANIFEST.json"))
        if path is None:
            return self._record(ReviewInputRead(
                kind=kind,
                read_status=READ_ABSENT,
                source=SOURCE_DELIVERY_DIR,
                cause="MANIFEST.json en regimen ZIP-only: no hay directorio descomprimido",
                run_id=self.run_id,
            ))
        data = load_json(path)
        if data is None:
            return self._record(ReviewInputRead(
                kind=kind,
                read_status=READ_ERROR,
                source=SOURCE_DELIVERY_DIR,
                path=path.as_posix(),
                cause="el MANIFEST.json del directorio no se pudo parsear",
                run_id=self.run_id,
            ))
        return self._record(ReviewInputRead(
            kind=kind,
            read_status=READ_OK,
            content=data,
            source=SOURCE_DELIVERY_DIR,
            path=path.as_posix(),
            run_id=self.run_id,
        ))

    def _record(self, read: ReviewInputRead) -> ReviewInputRead:
        self._reads[read.kind] = read
        return read

    # ── evidencia para el acta ────────────────────────────────────────

    def reads(self) -> list[ReviewInputRead]:
        return list(self._reads.values())

    def reads_report(self) -> dict:
        """Bloque `review_inputs` de los reportes: que se pidio, que se leyo y por que no."""
        return {
            "run_id": self.run_id,
            "resolver": "review_inputs",
            "manifest_present": self.manifest is not None,
            "package_zip_path": (
                self.package_zip_path.as_posix() if self.package_zip_path else None
            ),
            "documents": [read.to_dict() for read in self.reads()],
        }


def _read_bytes(path: Path) -> tuple[Optional[bytes], Optional[str]]:
    try:
        return path.read_bytes(), None
    except FileNotFoundError:
        return None, "archivo ausente"
    except OSError as exc:
        return None, str(exc)


def _decode(raw: bytes) -> Optional[str]:
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return None
