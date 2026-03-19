"""
Cargador de datos de onboarding desde archivos YAML/JSON.

Proporciona funciones para cargar datos previamente capturados
y fusionarlos con datos del scraper.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


def load_onboarding_data(path: Path) -> Dict[str, Any]:
    """
    Carga datos desde archivo YAML o JSON.
    
    Args:
        path: Ruta al archivo (.yaml, .yml, o .json)
        
    Returns:
        Diccionario con los datos cargados
        
    Raises:
        FileNotFoundError: Si el archivo no existe
        ValueError: Si el formato no es soportado o el contenido es inválido
    """
    if not path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {path}")
    
    suffix = path.suffix.lower()
    
    try:
        content = path.read_text(encoding="utf-8")
        
        if suffix in (".yaml", ".yml"):
            data = yaml.safe_load(content)
        elif suffix == ".json":
            data = json.loads(content)
        else:
            raise ValueError(f"Formato no soportado: {suffix}. Use .yaml, .yml o .json")
        
        if not isinstance(data, dict):
            raise ValueError(f"El archivo debe contener un objeto/diccionario, no {type(data).__name__}")
        
        return data
        
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML: {e}") from e
    except json.JSONDecodeError as e:
        raise ValueError(f"Error parsing JSON: {e}") from e


def merge_with_hotel_data(onboarding_data: Dict, hotel_data: Dict) -> Dict:
    """
    Fusiona datos de onboarding con datos del scraper.
    
    Los datos de onboarding tienen PRIORIDAD y se marcan como 'confirmados'.
    
    Args:
        onboarding_data: Datos capturados en onboarding
        hotel_data: Datos extraídos por el scraper
        
    Returns:
        Diccionario fusionado con campos de onboarding como prioritarios
    """
    result = hotel_data.copy()
    
    if not onboarding_data:
        return result
    
    datos_operativos = onboarding_data.get("datos_operativos", {})
    metadatos = onboarding_data.get("metadatos", {})
    campos_confirmados = metadatos.get("campos_confirmados", [])
    
    for field, value in datos_operativos.items():
        if value is not None:
            result[field] = value
            result[f"{field}_fuente"] = "onboarding_confirmado"
            result[f"{field}_confianza"] = 1.0
    
    if campos_confirmados:
        result["campos_confirmados"] = campos_confirmados
        result["onboarding_fecha"] = metadatos.get("fecha_captura")
    
    hotel_info = onboarding_data.get("hotel", {})
    if hotel_info.get("nombre"):
        result.setdefault("nombre", hotel_info["nombre"])
    if hotel_info.get("ubicacion"):
        result.setdefault("ubicacion", hotel_info["ubicacion"])
    
    return result


def create_onboarding_template() -> Dict[str, Any]:
    """
    Crea una plantilla vacía para datos de onboarding.
    
    Returns:
        Diccionario con estructura de plantilla
    """
    return {
        "hotel": {
            "nombre": None,
            "ubicacion": None,
        },
        "datos_operativos": {
            "habitaciones": None,
            "reservas_mes": None,
            "valor_reserva_cop": None,
            "canal_directo_pct": None,
        },
        "metadatos": {
            "fuente": "onboarding_interactivo",
            "fecha_captura": None,
            "campos_confirmados": [],
        },
    }


def generate_slug(nombre: str) -> str:
    """
    Genera un slug a partir del nombre del hotel.
    
    Args:
        nombre: Nombre del hotel
        
    Returns:
        Slug para usar en nombres de archivo
    """
    import re
    
    slug = nombre.lower().strip()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    slug = slug.strip("-")
    
    return slug or "hotel"
