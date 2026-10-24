"""Vocabulario de umbrales de fotos GBP: un nombre por semántica, un solo sitio de definición.

La definición vive en `config/regional_benchmarks.yaml` (bloque `umbrales_fotos`). Este módulo
es el lector: expone cada umbral con su nombre y verifica la escalera
`MIN ≤ OPORTUNIDAD ≤ RÚBRICA ≤ BRECHA ≤ TARGET` al importar.

No trae dict de respaldo con los mismos números: un segundo valor vivo es el defecto que esta
cura ataca (`D25`/`D25-bis`). Si el bloque falta o está incompleto, el lector falla fuerte.
"""

from pathlib import Path
from typing import Dict

from modules.common.yaml_loader import YAMLLoadError, load_yaml_config

CONFIG_DIR = Path(__file__).resolve().parents[2] / "config"
NOMBRE_CONFIG = "regional_benchmarks"
CLAVE_BLOQUE = "umbrales_fotos"

ORDEN_ESCALERA = (
    "MIN_FOTOS_BRECHA",
    "FOTOS_OPORTUNIDAD",
    "FOTOS_RUBRICA_EXCELENTE",
    "FOTOS_BRECHA_DIAGNOSTICO",
    "FOTOS_TARGET_DIAGNOSTICO",
)


class UmbralesFotosError(RuntimeError):
    """El bloque `umbrales_fotos` no está publicado, está incompleto o pierde la escalera."""


def _leer_umbrales() -> Dict[str, int]:
    try:
        config = load_yaml_config(NOMBRE_CONFIG, config_dir=CONFIG_DIR)
    except YAMLLoadError as exc:
        raise UmbralesFotosError(
            f"No se pudo leer {CONFIG_DIR / (NOMBRE_CONFIG + '.yaml')}: {exc}"
        ) from exc

    bloque = config.get(CLAVE_BLOQUE)
    if not isinstance(bloque, dict):
        raise UmbralesFotosError(
            f"Falta el bloque '{CLAVE_BLOQUE}' en {NOMBRE_CONFIG}.yaml"
        )

    faltantes = [nombre for nombre in ORDEN_ESCALERA if nombre not in bloque]
    if faltantes:
        raise UmbralesFotosError(
            f"Faltan umbrales en '{CLAVE_BLOQUE}': {faltantes}. "
            f"Publicados: {sorted(bloque)}"
        )

    try:
        valores = {nombre: int(bloque[nombre]) for nombre in ORDEN_ESCALERA}
    except (TypeError, ValueError) as exc:
        raise UmbralesFotosError(
            f"Los umbrales de '{CLAVE_BLOQUE}' deben ser enteros: {exc}"
        ) from exc

    crecientes = [valores[nombre] for nombre in ORDEN_ESCALERA]
    rotos = [
        f"{ORDEN_ESCALERA[i]}={crecientes[i]} > {ORDEN_ESCALERA[i + 1]}={crecientes[i + 1]}"
        for i in range(len(crecientes) - 1)
        if crecientes[i] > crecientes[i + 1]
    ]
    if rotos:
        raise UmbralesFotosError(
            "La escalera de umbrales está invertida "
            f"({'MIN ≤ OPORTUNIDAD ≤ RÚBRICA ≤ BRECHA ≤ TARGET'}): {'; '.join(rotos)}"
        )

    return valores


_VALORES = _leer_umbrales()

MIN_FOTOS_BRECHA = _VALORES["MIN_FOTOS_BRECHA"]
FOTOS_OPORTUNIDAD = _VALORES["FOTOS_OPORTUNIDAD"]
FOTOS_RUBRICA_EXCELENTE = _VALORES["FOTOS_RUBRICA_EXCELENTE"]
FOTOS_BRECHA_DIAGNOSTICO = _VALORES["FOTOS_BRECHA_DIAGNOSTICO"]
FOTOS_TARGET_DIAGNOSTICO = _VALORES["FOTOS_TARGET_DIAGNOSTICO"]
