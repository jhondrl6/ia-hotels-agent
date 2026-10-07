"""Contrato de WhatsApp (FASE-C, REFACTOR-WHATSAPP-ENTREGA-2026-09-18).

Una sola hoja de vocabulario para los DOS lectores de WhatsApp que existen en el
repo y un solo criterio de forma para el numero que viaja a un `wa.me`.

Designacion explicita de los lectores (prerrequisito de AC19a):

  * LECTOR DE PRESENCIA — `SitePresenceChecker._check_html_element`
    (modules/asset_generation/site_presence_checker.py). Gobierna la presencia
    canonica (`whatsapp_button` en el `site_presence_report`) y por tanto el
    skip de assets ya presentes. No produce numero para el boton.
  * LECTOR DE DOLOR — `V4ComprehensiveAuditor._detect_whatsapp_from_html`
    (modules/auditors/v4_comprehensive.py). Produce `whatsapp_html_detected`,
    que gobierna el pain (`no_whatsapp_visible`) y la coherencia.

Los dos siguen alimentando decisiones distintas y asi se declara; lo que se
unifica aqui es el vocabulario de patrones y la clasificacion de la evidencia,
para que la misma huella no pueda llamarse "numero" en una ruta y "canal" en la
otra. Ninguno de los dos afirma ausencia: la ausencia confirmada no es una
salida de este contrato.

Forma del numero (AC6): se valida AL LIMITE DE GENERACION. No se reutiliza
`modules/data_validation/cross_validator.normalize_phone_number`, porque ese
normalizador muta el digito (retira 57, 60 y el cero inicial) en servicio de la
COMPARACION entre fuentes; el destino de un boton no admite recomposicion —
`sin inferir pais ni completar partes`, que es el mandato de C. Aqui solo se
despojan separadores, se exigen digitos ASCII y se casa la longitud.
"""

from __future__ import annotations

import re
from typing import Any, Dict, Optional

from .confidence_taxonomy import ConfidenceLevel

ASCII_DIGITS = "0123456789"
SEPARADORES_PERMITIDOS = " +-()./\t"

# Banda de longitud internacional. Maximo 15 digitos: ITU-T E.164. Minimo 8:
# separa un numero nacional real de un recorte o un resto; el repo no tenia
# suelo propio y este es el criterio que C fija, documentado con su fuente.
LONGITUD_MIN = 8
LONGITUD_MAX = 15

# Centinelas que viajaron como telefono en el pasado medido.
CENTINELAS = frozenset({
    "detected_via_html",
    "detectado_via_html",
    "no_detectado",
    "sin_dato",
    "n/a",
    "na",
    "none",
    "null",
})

# ── Vocabulario compartido de los dos lectores ───────────────────────────────
WA_HREF_TOKENS = ("wa.me", "api.whatsapp.com", "web.whatsapp.com", "whatsapp://",
                  "whatsapp.com/send")
PLUGIN_FINGERPRINT_TOKENS = ("joinchat", "creame-whatsapp-me", "ht-ctc",
                             "click-to-chat", "wa-chat", "whatsapp")
WHATSAPP_HTML_PATTERNS = (
    r"wa\.me/",
    r"api\.whatsapp\.com",
    r"web\.whatsapp\.com",
    r"whatsapp://",
    r"whatsapp\.com/send",
    r'class="[^"]*whatsapp[^"]*"',
    r'id="[^"]*whatsapp[^"]*"',
    r"joinchat",
    r"creame-whatsapp-me",
    r"ht-ctc",
    r"click-to-chat",
    r"wa-chat",
    r"data-settings.*telephone",
)

WA_ME_HREF_RE = re.compile(r"wa\.me/(\d{4,20})", re.IGNORECASE)

# presence_evidence_kind (AC19a). `texto_visible` es el cuarto valor: la sonda
# de texto ya existia y produce found=True hoy; reducirla a `plugin_fingerprint`
# la mal-atribuiria y reducirla a `ninguna` contradeciria su propio found.
EVIDENCE_WA_ME_HREF = "wa.me_href"
EVIDENCE_PLUGIN_FINGERPRINT = "plugin_fingerprint"
EVIDENCE_TEXT = "texto_visible"
EVIDENCE_NONE = "ninguna"

# read_status (AC19a). El fallo de transporte es estado DESCONOCIDO, no ausencia.
READ_OK = "OK"
READ_ERROR = "READ_ERROR"
READ_NO_APLICABLE = "NO-APLICABLE"
# FASE-D (AC9): ABSENT es el cuarto estado y completa la tri-ada que exige el
# plan (READ_OK incluido vacío, ABSENT, READ_ERROR). Sin el no se podia
# distinguir "el artefacto no esta" de "nadie lo quiso leer". Se anade aqui, no
# en un enum propio del lector: FASE-C designo este archivo como vocabulario
# unico de read_status, y una segunda lista del mismo hecho es el defecto que
# esa designacion vino a evitar.
READ_ABSENT = "ABSENT"
# FASE-E (AC11): NO_LEIDO es el quinto estado y cubre el hueco que deja ABSENT.
# ABSENT dice "nunca existio"; NO_LEIDO dice "el run lo declaro, pero este resolvedor
# ya no lo alcanza" (documento retirado del arbol cliente sin copia interna). Sin este
# estado, la retencion por gate se confunde con la ausencia original y el revisor
# puede render como OK una lista vacia que en realidad nunca tuvo insumo que leer.
# Vive aqui, junto a los otros cuatro, por la misma designacion de FASE-C.
READ_NOT_READ = "NO_LEIDO"


def detect_whatsapp_in_html(html: Any) -> bool:
    """Lector de dolor: coincide con el vocabulario compartido (sin pattern propio)."""
    if not html:
        return False
    text = str(html).lower()
    return any(re.search(pattern, text) for pattern in WHATSAPP_HTML_PATTERNS)


def extract_wa_me_number(html_fragment: str) -> Optional[str]:
    """Numero del `href` wa.me, tal cual se lo encontro. No se normaliza ni se completa."""
    if not html_fragment:
        return None
    match = WA_ME_HREF_RE.search(html_fragment)
    return match.group(1) if match else None


def clasificar_evidencia(matched_texts: Any, whatsapp_href_number: Optional[str] = None) -> str:
    """Clasifica la evidencia de presencia a partir de lo que la sonda registro.

    Una huella de plugin declara presencia, jamas numero: `plugin_fingerprint`
    nunca habilita un destino. Un `href` que solo menciona la palabra (p. ej.
    `/contacto-whatsapp`) es texto, no canal: `texto_visible`.
    """
    textos = [str(t) for t in (matched_texts or [])]
    if whatsapp_href_number:
        return EVIDENCE_WA_ME_HREF
    for texto in textos:
        bajo = texto.lower()
        if bajo.startswith("whatsapp_link:") and any(tok in bajo for tok in WA_HREF_TOKENS):
            return EVIDENCE_WA_ME_HREF
    for texto in textos:
        if str(texto).lower().startswith("css_class:"):
            return EVIDENCE_PLUGIN_FINGERPRINT
    if textos:
        return EVIDENCE_TEXT
    return EVIDENCE_NONE


def normalizar_numero_whatsapp(valor: Any) -> Optional[str]:
    """Normalizacion EXPLICITITA y sin invencion: separadores fuera, digitos ASCII dentro.

    Devuelve la cadena de digitos solo si la entrada es utilizable; `None` en
    cualquier otro caso (la causa se obtiene con `rechazo_numero_whatsapp`).
    """
    digits, causa = rechazo_numero_whatsapp(valor)
    return None if causa else digits


def rechazo_numero_whatsapp(valor: Any) -> tuple[Optional[str], Optional[str]]:
    """(digitos, causa). `causa` es None cuando la entrada es utilizable.

    Causas: VACIO / CENTINELA / TIPO_NO_TEXTO / SIN_DIGITOS / DIGITOS_NO_ASCII /
    CARACTERES_NO_PERMITIDOS / LONGITUD_INVALIDA.
    """
    if valor is None:
        return None, "VACIO"
    if not isinstance(valor, str):
        if isinstance(valor, (int, float, bool)):
            return None, "TIPO_NO_TEXTO"
        return None, "TIPO_NO_TEXTO"

    crudo = valor.strip()
    if not crudo:
        return None, "VACIO"
    if crudo.casefold() in CENTINELAS:
        return None, "CENTINELA"

    sin_separadores = "".join(
        c for c in crudo if c not in SEPARADORES_PERMITIDOS and c != "\u00a0"
    )
    if not sin_separadores:
        return None, "SIN_DIGITOS"
    if any(c.isdigit() and c not in ASCII_DIGITS for c in sin_separadores):
        return None, "DIGITOS_NO_ASCII"
    if any(c not in ASCII_DIGITS for c in sin_separadores):
        return None, "CARACTERES_NO_PERMITIDOS"
    if not (LONGITUD_MIN <= len(sin_separadores) <= LONGITUD_MAX):
        return None, "LONGITUD_INVALIDA"
    return sin_separadores, None


# ── Destino de un enlace de reserva (AC6) ─────────────────────────────────────
# Nombre de la clave bajo la cual el pipeline entrega la observacion del canal
# a quien construye texto de reserva. Una sola clave, tres campos ya existentes
# en el vocabulario del contrato y del audit.
CLAVE_CANAL_WHATSAPP = "canal_whatsapp"


def destino_whatsapp_verificado(canal: Any, numero_en_uso: Any = None) -> Optional[str]:
    """Destino para un `wa.me`, SOLO si el canal observado lo trae como href.

    Regla: hay destino cuando (a) la presencia del canal se classifico
    `wa.me_href`, (b) el estado validado del canal es VERIFIED y (c) el numero
    del href es utilizable por `normalizar_numero_whatsapp`. Cualquier otro
    caso no habilita destino: `plugin_fingerprint` sin href, `estimated`,
    `conflict`, `unknown` o ausencia. La huella de un plugin declara presencia,
    jamas numero (AC19a), y el telefono de otro canal (GBP o web) nunca es el
    canal de WhatsApp.

    `numero_en_uso` es el numero que el texto pretendia usar (p. ej. el
    telefono del hotel). Si se informa y, normalizado, no casa con el del
    canal, tampoco hay destino: dos numeros distintos detras de un mismo
    enlace de reserva es la contradiccion que AC6 quiere evitar. Ausente o
    vacio, no hay nada que contrastar y manda el numero del canal.
    """
    if not isinstance(canal, dict):
        return None
    if canal.get("presence_evidence_kind") != EVIDENCE_WA_ME_HREF:
        return None
    if canal.get("whatsapp_status") != ConfidenceLevel.VERIFIED.value:
        return None
    destino = normalizar_numero_whatsapp(canal.get("whatsapp_href_number"))
    if not destino:
        return None
    if numero_en_uso not in (None, ""):
        if normalizar_numero_whatsapp(numero_en_uso) != destino:
            return None
    return destino


class NumeroWhatsAppNoUtilizable(ValueError):
    """El boton no puede construirse con este numero: no se produce href (AC6)."""

    def __init__(self, causa: str, valor: Any, origen: Optional[str] = None):
        self.causa = causa
        self.origen = origen
        self.valor_tipo = type(valor).__name__
        self.valor_longitud = len(str(valor)) if valor is not None else 0
        super().__init__(
            f"numero_de_whatsapp_no_utilizable: causa={causa} origen={origen or 'desconocido'}"
        )

    def a_dict(self) -> Dict[str, Any]:
        return {
            "causa": self.causa,
            "origen": self.origen,
            "valor_tipo": self.valor_tipo,
            "valor_longitud": self.valor_longitud,
        }
