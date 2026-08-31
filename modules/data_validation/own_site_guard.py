"""Guard de URL propia — plan VALIDADOR-URL-PROPIA-2026-08-30 (FASE-A).

Enforcea el invariante RC1: la URL de entrada debe ser el sitio web PROPIO del
hotel. Las URLs de OTAs, redes sociales o buscadores se rechazan ANTES de
cualquier llamada de red/API (choke point: main.ensure_url, exit code 2).

Fix ORTOGONAL al normalizador (N9): reusa main._normalize_url() para extraer
el netloc; no modifica la semántica de canonicalización (28 tests de
test_target_id_canonicalization.py intactos).

API:
    classify_url(url) -> UrlClassification
    assert_own_site(url, force=False, origen=ORIGEN_CLI, comando="", events_path=None)
    UrlNoPropiaError  (mensaje en español, nombre la plataforma, exit 2 en CLI)

Orígenes: ORIGEN_CLI (--url), ORIGEN_ESTADO_PERSISTENTE (reinyección last_url) y
ORIGEN_CAPA_DATOS (defensa en scrapers/auditors, FASE-B).

Blocklist versionada: config/url_blocklist.yaml (matching por SUFIJO DE
ETIQUETAS de dominio, nunca substring — contrato C7).

Eventos --force: .agent/memory/url_guard_force_events.json — archivo DEDICADO
append-only en formato JSON Lines: un objeto {"timestamp", "url", "comando"}
por línea. No se usa MemoryManager.save_state porque tiene semántica REPLACE
(memory.py:303-318) y main.py:1411 la llama con {"last_url": ...} después de
ensure_url, lo que borraría el evento.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
FORCE_EVENTS_PATH = REPO_ROOT / ".agent" / "memory" / "url_guard_force_events.json"

ORIGEN_CLI = "--url"
ORIGEN_ESTADO_PERSISTENTE = "estado_persistente"
ORIGEN_CAPA_DATOS = "capa_datos"

EXIT_CODE_URL_NO_PROPIA = 2

# D-VUP-B1: netlocs que el operador autorizó con --force en ESTE proceso. Lo
# consulta solo ORIGEN_CAPA_DATOS (scraper/auditor), que no recibe args.force:
# sin este registro el guard de capa de datos anularía el bypass del choke point.
FORZADAS_PROCESO: set = set()

NOMBRE_CATEGORIA = {
    "ota": "un agregador de reservas (OTA)",
    "red_social": "una red social",
    "buscador": "un buscador",
}


class UrlNoPropiaError(Exception):
    """La URL de entrada no pertenece al sitio web propio del hotel."""

    def __init__(self, mensaje: str, clasificacion: Optional["UrlClassification"] = None):
        super().__init__(mensaje)
        self.clasificacion = clasificacion

    @property
    def categoria(self) -> Optional[str]:
        return self.clasificacion.categoria if self.clasificacion else None


@dataclass(frozen=True)
class UrlClassification:
    url_original: str
    netloc: str
    bloqueada: bool
    categoria: Optional[str] = None
    plataforma: Optional[str] = None


def _netloc_de(url: str) -> str:
    # L16: reusar el helper existente; no reimplementar parsing.
    # Import lazy: main importa este módulo en ensure_url (evitar ciclo).
    from main import _normalize_url
    return _normalize_url(url)


def _load_blocklist() -> dict:
    from modules.common.yaml_loader import load_yaml_config
    config = load_yaml_config("url_blocklist", config_dir=REPO_ROOT / "config")
    return config.get("categorias", {}) or {}


def _plataforma_de(patron: str) -> str:
    return patron[:-2] if patron.endswith(".*") else patron


def _match_etiquetas(netloc: str, patron: str) -> bool:
    """Matching por sufijo de etiquetas de dominio (contrato C7).

    - "plataforma.tld":   netloc exacto o subdominio (etiquetas finales iguales).
    - "plataforma.tld.*": dominio regional — base alineada en frontera de
      etiquetas con ≥1 etiqueta después (el TLD regional).
    """
    patron = patron.strip().lower()
    n_etiq = netloc.split(".")
    if patron.endswith(".*"):
        b_etiq = patron[:-2].split(".")
        nb, nbb = len(n_etiq), len(b_etiq)
        for i in range(0, nb - nbb):
            if n_etiq[i:i + nbb] == b_etiq:
                return True
        return False
    p_etiq = patron.split(".")
    if len(n_etiq) < len(p_etiq):
        return False
    return n_etiq[-len(p_etiq):] == p_etiq


def classify_url(url: str) -> UrlClassification:
    """Clasifica una URL contra la blocklist versionada.

    Returns:
        UrlClassification con bloqueada=True y categoria/plataforma cuando el
        netloc coincide con algún patrón; bloqueada=False en caso contrario.
    """
    netloc = _netloc_de(url)
    categorias = _load_blocklist()
    for categoria in ("ota", "red_social", "buscador"):
        for patron in categorias.get(categoria, []) or []:
            patron = str(patron)
            if _match_etiquetas(netloc, patron):
                return UrlClassification(
                    url_original=url,
                    netloc=netloc,
                    bloqueada=True,
                    categoria=categoria,
                    plataforma=_plataforma_de(patron),
                )
    return UrlClassification(url_original=url, netloc=netloc, bloqueada=False)


def _mensaje_rechazo(clasif: UrlClassification, origen: str) -> str:
    nombre = NOMBRE_CATEGORIA.get(clasif.categoria, "una plataforma externa")
    lineas = [
        f"URL rechazada: {clasif.url_original} pertenece a {nombre} "
        f"({clasif.plataforma}), no al sitio web propio del hotel."
    ]
    if origen == ORIGEN_ESTADO_PERSISTENTE:
        lineas.append(
            "Esta URL proviene del estado persistente (last_url), no de --url."
        )
    lineas.append(
        "Proporciona la URL del sitio web propio del hotel "
        "(ej: https://www.tuhotel.com). Para auditar esta URL de todos modos "
        "usa --force (bypass explícito del operador; el evento queda registrado)."
    )
    return " ".join(lineas)


def _registrar_evento_force(clasif: UrlClassification, comando: str, events_path=None) -> Path:
    path = Path(events_path) if events_path else FORCE_EVENTS_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    evento = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "url": clasif.url_original,
        "comando": comando or "",
    }
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(evento, ensure_ascii=False) + "\n")
    return path


def assert_own_site(
    url: str,
    force: bool = False,
    origen: str = ORIGEN_CLI,
    comando: str = "",
    events_path=None,
) -> UrlClassification:
    """Valida que la URL sea del sitio propio del hotel.

    Raises:
        UrlNoPropiaError: si la URL está blocklisted y force=False. El mensaje
            en español nombra la plataforma y pide la URL del sitio propio; con
            origen="estado_persistente" menciona explícitamente ese origen (AC6).

    Con force=True no lanza (bypass explícito del operador) y persiste el
    evento en el archivo dedicado append-only. Nótese que en ese caso main.py
    SÍ persiste la URL como last_url; una reinyección posterior será rechazada
    con mención del estado persistente (ciclo auto-consistente).

    Con origen="capa_datos" (scraper/auditor) se honra el --force ya concedido
    en el proceso para ese netloc (D-VUP-B1): esos llamadores no reciben
    args.force y otherwise anularían la autorización del operador. Los orígenes
    --url y estado_persistente conservan la semántica de FASE-A.
    """
    clasif = classify_url(url)
    if not clasif.bloqueada:
        return clasif
    if force:
        FORZADAS_PROCESO.add(clasif.netloc)
        path = _registrar_evento_force(clasif, comando, events_path)
        print(
            f"[GUARD] --force activo: se permite la URL no propia {url}. "
            f"Evento registrado en {path}"
        )
        return clasif
    if origen == ORIGEN_CAPA_DATOS and clasif.netloc in FORZADAS_PROCESO:
        return clasif
    raise UrlNoPropiaError(_mensaje_rechazo(clasif, origen), clasificacion=clasif)
