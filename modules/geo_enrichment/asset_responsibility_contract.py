"""Asset Responsibility Contract - Relación explícita entre assets CORE y GEO.

Este módulo documenta y garantiza la relación correcta entre assets CORE y assets GEO
para evitar confusión en implementación.

Regla de Oro:
    NUNCA REEMPLAZAR, SIEMPRE ENRIQUECER
    - Los assets CORE son obligatorios.
    - Los assets GEO son enrichment ADICIONAL.

Ejemplo de estructura de archivos:
    03_PARA_TU_WEBMASTER/
        hotel_schema.json              <- CORE (del pipeline original)
        hotel_schema_rich.json         <- GEO (del enrichment)
        faq_schema.json                <- CORE (del pipeline original)
        faq_schema_rich.json           <- GEO (del enrichment)
        boton_whatsapp.html            <- CORE (del pipeline original)
        boton_whatsapp_rich.html       <- GEO (del enrichment)

Referencia: FASE-5 prompt, README.md
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class AssetType(Enum):
    """Tipo de asset según su origen y propósito."""
    CORE = "core"           # Generado por pipeline original
    GEO = "geo"             # Generado por GEO enrichment
    ADVISORY = "advisory"   # Recomendación, no archivo


@dataclass
class AssetResponsibility:
    """Responsabilidad de un asset individual.
    
    Attributes:
        filename: Nombre del archivo (e.g., 'hotel_schema.json').
        type: Tipo de asset (CORE, GEO, o ADVISORY).
        priority: Prioridad de implementación (1 = primero).
        mandatory: Si el asset es obligatorio.
        replaces: Nombre del asset que reemplaza (si aplica).
        enriched_by: Nombre del asset que lo enriquece (si aplica).
        description: Descripción legible del asset.
        implementation_note: Nota sobre cómo implementar.
    """
    filename: str
    type: AssetType
    priority: int
    mandatory: bool
    replaces: Optional[str] = None
    enriched_by: Optional[str] = None
    description: str = ""
    implementation_note: str = ""

    def __post_init__(self):
        """Validaciones post-construcción."""
        if self.type == AssetType.GEO and not self.enriched_by and not self.replaces:
            logger.warning(
                f"[AssetResponsibility] GEO asset '{self.filename}' sin "
                f"'enriched_by' o 'replaces' - verificar si es realmente un enrichment"
            )


@dataclass
class AssetResponsibilityContract:
    """Contract que define la relación entre assets CORE y GEO.
    
    Este contract es la fuente de verdad para que el webmaster sepa
    qué archivos implementar y en qué orden.
    
    Usage:
        contract = AssetResponsibilityContract()
        
        # Obtener orden de implementación
        order = contract.get_implementation_order(
            core_assets=['hotel_schema.json', 'faq_schema.json'],
            geo_assets=['hotel_schema_rich.json', 'faq_schema_rich.json']
        )
        
        # Obtener regla de reemplazo para un asset
        rule = contract.get_replacement_rule('hotel_schema_rich.json')
        
        # Generar template de entrega
        template = contract.generate_delivery_template(hotel_name="Hotel Ejemplo")
    """

    # Mapeo de assets CORE a sus correspondiente GEO enrichment
    CORE_TO_GEO_MAP: Dict[str, str] = field(default_factory=lambda: {
        'hotel_schema.json': 'hotel_schema_rich.json',
        'faq_schema.json': 'faq_schema_rich.json',
        'boton_whatsapp.html': 'boton_whatsapp_rich.html',
    })

    # Mapeo inverso
    GEO_TO_CORE_MAP: Dict[str, str] = field(default_factory=lambda: {
        'hotel_schema_rich.json': 'hotel_schema.json',
        'faq_schema_rich.json': 'faq_schema.json',
        'boton_whatsapp_rich.html': 'boton_whatsapp.html',
    })

    # Orden de prioridad por tipo de asset
    PRIORITY_ORDER: List[AssetType] = field(default_factory=lambda: [
        AssetType.CORE,
        AssetType.GEO,
    ])

    def get_core_responsibilities(self) -> List[AssetResponsibility]:
        """Retorna lista de assets CORE con sus responsabilidades."""
        return [
            AssetResponsibility(
                filename='hotel_schema.json',
                type=AssetType.CORE,
                priority=1,
                mandatory=True,
                description='Schema.org básico del hotel (nombre, ubicación, contacto)',
                implementation_note='Insertar en <head> de todas las páginas o en JSON-LD block'
            ),
            AssetResponsibility(
                filename='faq_schema.json',
                type=AssetType.CORE,
                priority=1,
                mandatory=True,
                description='FAQ Schema para preguntas frecuentes del hotel',
                implementation_note='Insertar en <head> si hay página de FAQs o en bloque JSON-LD'
            ),
            AssetResponsibility(
                filename='boton_whatsapp.html',
                type=AssetType.CORE,
                priority=1,
                mandatory=True,
                description='Botón de WhatsApp básico con link directo',
                implementation_note='Insertar como widget flotante o en header/footer'
            ),
        ]

    def get_geo_responsibilities(self) -> List[AssetResponsibility]:
        """Retorna lista de assets GEO (enrichments) con sus responsabilidades."""
        return [
            AssetResponsibility(
                filename='hotel_schema_rich.json',
                type=AssetType.GEO,
                priority=2,
                mandatory=False,  # Solo obligatorio si score < 68
                enriched_by='GEO Enrichment Layer',
                description='Schema.org enriquecido con datos de GBP, horarios extendidos, amenities',
                implementation_note='REEMPLAZA temporalmente a hotel_schema.json SOLO si se validó que enriquece, NO reemplaza'
            ),
            AssetResponsibility(
                filename='faq_schema_rich.json',
                type=AssetType.GEO,
                priority=2,
                mandatory=False,
                enriched_by='GEO Enrichment Layer',
                description='FAQ Schema con más preguntas y respuestas detalladas',
                implementation_note='SUMA a faq_schema.json - implementar ambos si es posible'
            ),
            AssetResponsibility(
                filename='boton_whatsapp_rich.html',
                type=AssetType.GEO,
                priority=2,
                mandatory=False,
                enriched_by='GEO Enrichment Layer',
                description='Botón WhatsApp con mensaje pre-cargado y analytics',
                implementation_note='SUMA a boton_whatsapp.html - puede implementar ambos o elegir el rico'
            ),
        ]

    def get_implementation_order(
        self,
        core_assets: Optional[List[str]] = None,
        geo_assets: Optional[List[str]] = None
    ) -> List[AssetResponsibility]:
        """Retorna lista ordenada de assets a implementar.
        
        Args:
            core_assets: Lista de filenames CORE presentes (None = todos).
            geo_assets: Lista de filenames GEO presentes (None = todos).
            
        Returns:
            Lista ordenada de AssetResponsibility (CORE primero, luego GEO).
        """
        result: List[AssetResponsibility] = []
        seen_filenames = set()

        # Primero: CORE assets
        for resp in self.get_core_responsibilities():
            if core_assets is None or resp.filename in core_assets:
                if resp.filename not in seen_filenames:
                    result.append(resp)
                    seen_filenames.add(resp.filename)

        # Segundo: GEO assets
        for resp in self.get_geo_responsibilities():
            if geo_assets is None or resp.filename in geo_assets:
                if resp.filename not in seen_filenames:
                    result.append(resp)
                    seen_filenames.add(resp.filename)

        return result

    def get_replacement_rule(self, asset_type: str) -> Dict[str, Any]:
        """Retorna la regla de reemplazo/enriquecimiento para un asset.
        
        Args:
            asset_type: Nombre del archivo a consultar.
            
        Returns:
            Dict con:
                - rule: 'enrich' | 'replace' | 'standalone' | 'unknown'
                - paired_asset: Asset complementario (si existe)
                - description: Descripción de la regla
        """
        # Es un GEO asset
        if asset_type in self.GEO_TO_CORE_MAP:
            core_asset = self.GEO_TO_CORE_MAP[asset_type]
            return {
                'rule': 'enrich',
                'paired_asset': core_asset,
                'description': (
                    f"'{asset_type}' es un ENRICHMENT de '{core_asset}'. "
                    f"NO REEMPLAZA, SUMA. Implementar ambos si es posible."
                ),
                'implementation': (
                    f"1) Implementar '{core_asset}' primero (CORE es obligatorio). "
                    f"2) Luego añadir '{asset_type}' como mejora adicional."
                )
            }

        # Es un CORE asset
        if asset_type in self.CORE_TO_GEO_MAP:
            geo_asset = self.CORE_TO_GEO_MAP[asset_type]
            return {
                'rule': 'enrich_target',
                'paired_asset': geo_asset,
                'description': (
                    f"'{asset_type}' es CORE y puede ser enriquecido por '{geo_asset}'. "
                    f"Primero implementar '{asset_type}', luego evaluar '{geo_asset}'."
                ),
                'implementation': (
                    f"1) Implementar '{asset_type}' (CORE - obligatorio). "
                    f"2) Si score < 68, añadir '{geo_asset}' como enrichment."
                )
            }

        # No tiene par
        if asset_type.endswith('_rich.json') or '_rich.' in asset_type:
            return {
                'rule': 'unknown_enrich',
                'paired_asset': None,
                'description': (
                    f"'{asset_type}' parece ser un enrichment pero no tiene "
                    f"par CORE registrado. Verificar manualmente."
                ),
                'implementation': 'Verificar manualmente si debe reemplazar o sumar.'
            }

        return {
            'rule': 'standalone',
            'paired_asset': None,
            'description': f"'{asset_type}' no tiene relación con otro asset.",
            'implementation': f"Implementar '{asset_type}' de forma independiente."
        }

    def get_asset_chain(self, core_asset: str) -> Dict[str, Any]:
        """Retorna la cadena completa de enrichment para un asset.
        
        Args:
            core_asset: Nombre del asset CORE.
            
        Returns:
            Dict con la cadena de responsabilidad.
        """
        if core_asset not in self.CORE_TO_GEO_MAP:
            return {
                'core': core_asset,
                'geo': None,
                'chain': [core_asset],
                'description': f'{core_asset} no tiene enrichment GEO.'
            }

        geo_asset = self.CORE_TO_GEO_MAP[core_asset]
        return {
            'core': core_asset,
            'geo': geo_asset,
            'chain': [core_asset, geo_asset],
            'description': (
                f'{core_asset} (CORE) -> {geo_asset} (GEO enrichment). '
                'Implementar en orden: 1) CORE primero, 2) GEO después como suma.'
            )
        }

    def generate_delivery_template(
        self,
        hotel_name: str,
        core_assets: Optional[List[str]] = None,
        geo_assets: Optional[List[str]] = None,
        geo_score: Optional[int] = None
    ) -> str:
        """Genera un template de entrega con instrucciones claras.
        
        Args:
            hotel_name: Nombre del hotel para el template.
            core_assets: Lista de filenames CORE generados.
            geo_assets: Lista de filenames GEO generados.
            geo_score: Score GEO para determinar si GEO assets son obligatorios.
            
        Returns:
            String con el template de entrega formateado en Markdown.
        """
        core_assets = core_assets or []
        geo_assets = geo_assets or []
        geo_score = geo_score or 100

        # Determinar si GEO assets son obligatorios
        geo_mandatory = geo_score < 68

        lines = [
            f"# 📦 Delivery Package - {hotel_name}",
            "",
            f"**Fecha:** {self._get_date()}",
            f"**Score GEO:** {geo_score} ({'OBLIGATORIO' if geo_mandatory else 'OPCIONAL'})",
            "",
            "---",
            "",
            "## ⚠️ REGLA DE ORO: NUNCA REEMPLAZAR, SIEMPRE ENRIQUECER",
            "",
            "Los archivos CORE son **OBLIGATORIOS**.",
            "Los archivos GEO son **ENRICHMENT ADICIONAL**.",
            "",
            "---",
            "",
            "## 📋 ORDEN DE IMPLEMENTACIÓN",
            "",
        ]

        order = self.get_implementation_order(core_assets, geo_assets)

        for i, resp in enumerate(order, 1):
            mandatory_mark = "✅" if resp.mandatory else "⬜"
            type_mark = "[CORE]" if resp.type == AssetType.CORE else "[GEO]"

            lines.append(f"### {i}. {resp.filename} {mandatory_mark} {type_mark}")
            lines.append(f"   - **Descripción:** {resp.description}")
            lines.append(f"   - **Prioridad:** {resp.priority} ({'primero' if resp.priority == 1 else 'después'})")
            lines.append(f"   - **Obligatorio:** {'Sí' if resp.mandatory else 'No'}")
            if resp.implementation_note:
                lines.append(f"   - **Cómo implementar:** {resp.implementation_note}")
            lines.append("")

        # Agregar guía de relaciones
        lines.extend([
            "---",
            "",
            "## 🔗 GUÍA DE RELACIONES ENTRE ARCHIVOS",
            "",
        ])

        for core_asset in self.CORE_TO_GEO_MAP.keys():
            if core_asset in core_assets:
                geo_asset = self.CORE_TO_GEO_MAP[core_asset]
                geo_present = geo_asset in geo_assets

                lines.append(f"### {core_asset} ↔ {geo_asset}")
                lines.append(f"- **{core_asset}** (CORE): Implementar PRIMERO")
                if geo_present:
                    lines.append(f"- **{geo_asset}** (GEO): Implementar DESPUÉS como suma")
                    lines.append(f"  - La regla es **ENRIQUECER, NO REEMPLAZAR**")
                    if geo_mandatory:
                        lines.append(f"  - ⚠️ **OBLIGATORIO** (score GEO {geo_score} < 68)")
                    else:
                        lines.append(f"  - ⬜ OPCIONAL (score GEO {geo_score} >= 68)")
                else:
                    lines.append(f"- **{geo_asset}**: No generado (opcional)")
                lines.append("")

        # Agregar checkboxes
        lines.extend([
            "---",
            "",
            "## ✅ CHECKLIST DE IMPLEMENTACIÓN",
            "",
        ])

        for resp in order:
            checked = "x" if resp.mandatory else " "
            lines.append(f"- [{checked}] {resp.filename}")

        lines.extend([
            "",
            "---",
            "",
            "*Generado por IA Hoteles Agent v4.0 - FASE-5 Asset Responsibility Contract*",
        ])

        return "\n".join(lines)

    def _get_date(self) -> str:
        """Retorna la fecha actual formateada."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M")

    def export_contract_json(
        self,
        core_assets: Optional[List[str]] = None,
        geo_assets: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Exporta el contract como diccionario JSON.
        
        Args:
            core_assets: Lista de filenames CORE generados.
            geo_assets: Lista de filenames GEO generados.
            
        Returns:
            Dict con el contract completo serializable.
        """
        order = self.get_implementation_order(core_assets, geo_assets)

        return {
            'contract_version': '1.0.0',
            'rule': 'NEVER_REPLACE_ALWAYS_ENRICH',
            'core_assets': [r.filename for r in order if r.type == AssetType.CORE],
            'geo_assets': [r.filename for r in order if r.type == AssetType.GEO],
            'implementation_order': [
                {
                    'filename': r.filename,
                    'type': r.type.value,
                    'priority': r.priority,
                    'mandatory': r.mandatory,
                    'description': r.description,
                    'implementation_note': r.implementation_note,
                }
                for r in order
            ],
            'replacement_rules': {
                filename: self.get_replacement_rule(filename)
                for filename in (core_assets or []) + (geo_assets or [])
            }
        }


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def get_implementation_order(
    core_assets: Optional[List[str]] = None,
    geo_assets: Optional[List[str]] = None
) -> List[AssetResponsibility]:
    """Función convenience para obtener orden de implementación.
    
    Args:
        core_assets: Lista de filenames CORE generados.
        geo_assets: Lista de filenames GEO generados.
        
    Returns:
        Lista ordenada de AssetResponsibility.
    """
    contract = AssetResponsibilityContract()
    return contract.get_implementation_order(core_assets, geo_assets)


def get_replacement_rule(asset_type: str) -> Dict[str, Any]:
    """Función convenience para obtener regla de reemplazo.
    
    Args:
        asset_type: Nombre del archivo a consultar.
        
    Returns:
        Dict con la regla de reemplazo.
    """
    contract = AssetResponsibilityContract()
    return contract.get_replacement_rule(asset_type)


def generate_delivery_template(
    hotel_name: str,
    core_assets: Optional[List[str]] = None,
    geo_assets: Optional[List[str]] = None,
    geo_score: Optional[int] = None
) -> str:
    """Función convenience para generar template de entrega.
    
    Args:
        hotel_name: Nombre del hotel.
        core_assets: Lista de filenames CORE generados.
        geo_assets: Lista de filenames GEO generados.
        geo_score: Score GEO para determinar obligatoriedad.
        
    Returns:
        Template de entrega en Markdown.
    """
    contract = AssetResponsibilityContract()
    return contract.generate_delivery_template(hotel_name, core_assets, geo_assets, geo_score)
