"""Sumidero unico de redaccion de credenciales (FASE-F, AC13).

Toda salida que pueda transportar texto ajeno --consola, log, exception, reporte o
snapshot-- pasa por aqui ANTES de existir fuera del proceso: redactar despues de
escribir no cumple AC13. Es el unico punto donde viven las formas de credencial;
los sanitizadores preexistentes delegan en el en lugar de duplicarlas.

No imprime ni conserva valores: solo sustituye. El patron del verificador
`scripts/run_all_validations.py` es intencionalmente independiente (instrumento
distinto del producto que fiscaliza); la bateria de F comprueba que los dos cazan
el mismo marcador sintetico.
"""

from __future__ import annotations

import re

MASK = "***"

# Formas de credencial, con independencia de quien la cargo: el valor real nunca
# se publica aunque la instancia no conozca esa key.
SECRET_SHAPES: tuple[re.Pattern[str], ...] = (
    re.compile(r"AIzaSy[A-Za-z0-9_\-]{25,}"),
    re.compile(r"sk-(?:or-|ant-|proj-)?[A-Za-z0-9_\-]{16,}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{25,}"),
    re.compile(r"pplx-[A-Za-z0-9_\-]{16,}"),
)

# `key=<valor>` en cualquier separador (?key=, &key=, "key=", inicio de cadena),
# sin cazar la terminacion de otra palabra (monkey=).
KEY_PARAM_RE = re.compile(r"(?<![A-Za-z0-9_])(key)\s*=\s*['\"]?([^'\"&\s,;]+)", re.I)

# Cabeceras y tokens que requests/urllib reproducen en el texto de la excepcion.
HEADER_SECRET_RE = re.compile(
    r"(?<![A-Za-z0-9_-])((?:x-goog-api-key|api-key|authorization)\s*[:=]\s*)['\"]?([^'\"&\s,;]+)",
    re.I,
)
BEARER_RE = re.compile(r"(Bearer\s+)([A-Za-z0-9._\-]{8,})", re.I)


def redact_secrets(text: str) -> str:
    """Redacta formas de credencial, parametros `key=` y cabeceras de un texto."""
    if not text:
        return text
    for shape in SECRET_SHAPES:
        text = shape.sub(MASK, text)
    # Bearer antes que la cabecera: si no, la cabecera se come la palabra "Bearer"
    # y el token sobrevive suelto en el texto ya "redactado".
    text = BEARER_RE.sub(lambda m: f"{m.group(1)}{MASK}", text)
    text = HEADER_SECRET_RE.sub(lambda m: f"{m.group(1)}{MASK}", text)
    text = KEY_PARAM_RE.sub(lambda m: f"{m.group(1)}={MASK}", text)
    return text


def redact_values(text: str, values: tuple[object, ...] | list[object]) -> str:
    """Redacta por igualdad literal los valores conocidos antes de las formas.

    `values` se usa por su representacion; ningun valor se copia a la salida.
    """
    if not text:
        return text
    for value in values:
        if value:
            literal = value if isinstance(value, str) else str(value)
            if len(literal) >= 8:
                text = text.replace(literal, MASK)
    return text


def _es_solo_marca(valor: str) -> bool:
    return bool(valor) and set(valor) <= set(MASK)


def contains_secret_shape(text: str) -> bool:
    """True si el texto conserva alguna forma de credencial.

    Un valor que ya es la marca de redaccion NO es un leak: `key=***` es exactamente
    lo que producen las sustituciones, y si el guard lo contara como crudo, quien
    redacta y despues verifica no podria verificar nada. La marca se admite como
    valor completo, no se borra del texto: borrarla dejaba la palabra siguiente del
    mensaje como si fuera el valor de la key.
    """
    if not text:
        return False
    if any(shape.search(text) for shape in SECRET_SHAPES):
        return True
    for regex in (KEY_PARAM_RE, HEADER_SECRET_RE, BEARER_RE):
        for coincidencia in regex.finditer(text):
            if not _es_solo_marca(coincidencia.group(2)):
                return True
    return False


class RedactionLeakError(RuntimeError):
    """Un informe o artefacto conserva material que debio redactarse."""


def assert_redacted(text: str, *, channel: str) -> None:
    """Guard fail-closed para informes: falla fuerte antes de persistir.

    No incluye el texto en el mensaje: un informe de redaccion que filtra es peor
    que el leak que denuncia.
    """
    if contains_secret_shape(text):
        raise RedactionLeakError(f"salida sin redactar en el canal {channel!r}")


def redact_and_clip(text: str, limit: int) -> str:
    """Redacta y despues recorta: el orden inverso deja el prefijo al descubierto."""
    redacted = redact_secrets(text)
    if len(redacted) <= limit:
        return redacted
    return redacted[: max(limit - 3, 0)] + "..."


def redact_payload(payload: object) -> object:
    """Redacta cada cadena de una estructura serializable, conservando la forma.

    Se usa en artefactos que mezclan datos canonicos con texto de error ajeno: la
    estructura del reporte sigue legible por sus consumidores; solo cambian los
    valores de tipo cadena.
    """
    if isinstance(payload, str):
        return redact_secrets(payload)
    if isinstance(payload, dict):
        return {key: redact_payload(value) for key, value in payload.items()}
    if isinstance(payload, list):
        return [redact_payload(item) for item in payload]
    if isinstance(payload, tuple):
        return tuple(redact_payload(item) for item in payload)
    return payload
