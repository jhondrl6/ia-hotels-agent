# 02-prompt-fase-A — Contrato canónico y saneamiento de evidencia

**Fase**: FASE-A — DeliveryAssetState + DeliveryContext
**Plan**: DT-1-DELIVERY-CONTRACT-2026-07-23
**Sesión**: Nueva (fresh)
**Iteraciones máx**: 60
**Depende de**: Ninguna (fase inicial)
**Bloquea a**: FASE-B
**Tipo**: DIRECTA (investigación + implementación de dataclasses)

---

## Objetivo

Definir el contrato canónico de estados de assets para delivery (`DeliveryAssetState`, `DeliveryAssetEntry`, `DeliveryContext`) y propagar `skipped_assets` coherentemente desde `AssessmentBuilder` para que el packager pueda consumirlos.

## Contexto del problema

Actualmente hay 6+ fuentes que interpretan de manera diferente si un asset está presente, generado, o cubierto:

1. `SitePresenceChecker` → `asset_result.skipped_assets`
2. `AssessmentBuilder.skipped_assets` → parcialmente propagado
3. `publication_gates._proposal_asset_alignment_gate` → fake report desde skipped_assets
4. `asset_generation_report.json` → `skipped_assets` con `presence_status`
5. `gate_report.json` → `present_in_production`
6. `coherence_validation*.json` → `promised_assets_exist`
7. `metadata.json` individual → `can_use`

Estados usados pero no unificados: `exists`, `present_in_production`, `skipped_existing`, `exists_with_issues`, `redundant`, `verification_failed`, `indeterminate`.

## Tareas

### T1: Definir enum `DeliveryAssetState`

**Archivo**: `modules/delivery/delivery_context.py` (modificar)

Agregar al inicio del archivo (después de imports):

```python
from enum import Enum

class DeliveryAssetState(Enum):
    """Estado canónico de un asset para el delivery package."""
    DELIVERED = "delivered"                    # Archivo generado y presente en el ZIP
    PRESENT_IN_PRODUCTION = "present"          # Existe en sitio, verificado, sin issues
    PRESENT_WITH_ISSUES = "present_issues"     # Existe en sitio pero con conflicto (ej: WhatsApp)
    ESTIMATED = "estimated"                    # Generado con datos estimados (ESTIMATED_ prefix)
    FAILED = "failed"                          # Falló la generación
    INDETERMINATE = "indeterminate"            # No se pudo verificar presencia
    NOT_DELIVERED = "not_delivered"            # No generado y no presente en producción
```

**Verificación**: El archivo debe tener el enum definido y exportable.

### T2: Resolver semántica `covered` / `requires_action` / `requires_review`

**Archivo**: `modules/delivery/delivery_context.py` (modificar)

Agregar la dataclass `DeliveryAssetEntry` que capture estado + atributos independientes:

```python
from dataclasses import dataclass, field
from typing import Optional, List

@dataclass
class DeliveryAssetEntry:
    """Entrada canónica de un asset para el delivery README y manifest."""
    asset_type: str                          # ej: "whatsapp_button"
    service_name: str                        # ej: "Botón de WhatsApp"
    state: DeliveryAssetState                # Estado canónico
    delivery_path: Optional[str] = None      # Ruta dentro del ZIP (POSIX), None si no entregado
    site_verified: bool = False              # ¿Se verificó presencia en sitio?
    confidence: float = 0.0                  # Confidence score del asset
    covered: bool = False                    # ¿Está cubierto (entregado O presente verificado)?
    requires_action: bool = False            # ¿Requiere acción del cliente?
    requires_review: bool = False            # ¿Requiere revisión humana antes de instalar?
    is_advisory: bool = False                # True para guías (ej: whatsapp_conflict_guide), no instalable
    message: str = ""                        # Mensaje descriptivo para el README
    source_refs: List[str] = field(default_factory=list)  # Referencias a fuentes de evidencia
    
    @classmethod
    def from_skipped_asset(cls, skipped: dict, service_name: str = "") -> "DeliveryAssetEntry":
        """Construye desde un skipped_asset del asset_generation_report."""
        presence = skipped.get("presence_status", "")
        asset_type = skipped.get("asset_type", "")
        site_verified = skipped.get("site_verified", False)
        
        # Determinar estado según presence_status
        if presence == "exists":
            # Verificar si hay issues (whatsapp_conflict => PRESENT_WITH_ISSUES)
            has_issues = skipped.get("pain_ids_affected") and any(
                "conflict" in pid.lower() for pid in skipped.get("pain_ids_affected", [])
            )
            if has_issues:
                state = DeliveryAssetState.PRESENT_WITH_ISSUES
                msg = f"Existe en producción pero requiere revisión: {skipped.get('reason', '')}"
            else:
                state = DeliveryAssetState.PRESENT_IN_PRODUCTION
                msg = f"Existe en producción — verificado el {skipped.get('reason', '')}"
        elif presence == "exists_with_issues":
            state = DeliveryAssetState.PRESENT_WITH_ISSUES
            msg = f"Existe en producción con incidencias: {skipped.get('reason', '')}"
        elif presence in ("redundant",):
            state = DeliveryAssetState.PRESENT_IN_PRODUCTION
            msg = "Redundante — ya fue entregado previamente"
        else:
            state = DeliveryAssetState.INDETERMINATE
            msg = f"No se pudo verificar presencia ({presence})"
        
        return cls(
            asset_type=asset_type,
            service_name=service_name,
            state=state,
            site_verified=site_verified,
            confidence=0.0,
            covered=(state in (DeliveryAssetState.PRESENT_IN_PRODUCTION,)),
            requires_action=(state == DeliveryAssetState.PRESENT_WITH_ISSUES),
            requires_review=(state in (DeliveryAssetState.PRESENT_WITH_ISSUES, DeliveryAssetState.INDETERMINATE)),
            message=msg,
            source_refs=["asset_generation_report.json"]
        )
    
    @classmethod
    def from_generated_asset(cls, asset: dict, service_name: str = "", dest_path: str = "") -> "DeliveryAssetEntry":
        """Construye desde un generated_asset del asset_generation_report."""
        asset_type = asset.get("asset_type", "")
        confidence = asset.get("confidence_score", 0.0)
        can_use = asset.get("can_use", True)
        preflight = asset.get("preflight_status", "")
        
        # Detectar assets advisory (guías, no instalables)
        advisory_types = {"whatsapp_conflict_guide", "og_tags_guide", "analytics_setup_guide"}
        is_advisory = asset_type in advisory_types or "guide" in asset_type.lower() or "guia" in asset_type.lower()
        
        if preflight == "BLOCKED":
            state = DeliveryAssetState.FAILED
        elif not can_use:
            state = DeliveryAssetState.ESTIMATED
        elif preflight == "WARNING":
            # Generated with warning — still delivered but estimated
            if "ESTIMATED" in asset.get("filename", ""):
                state = DeliveryAssetState.ESTIMATED
            else:
                state = DeliveryAssetState.DELIVERED
        else:
            state = DeliveryAssetState.DELIVERED
        
        return cls(
            asset_type=asset_type,
            service_name=service_name,
            state=state,
            delivery_path=dest_path,
            site_verified=False,
            confidence=confidence,
            covered=(state == DeliveryAssetState.DELIVERED),
            requires_action=(state in (DeliveryAssetState.DELIVERED, DeliveryAssetState.ESTIMATED) and not is_advisory),
            requires_review=(state == DeliveryAssetState.ESTIMATED or is_advisory),
            is_advisory=is_advisory,
            message=f"Asset {'entregado' if state == DeliveryAssetState.DELIVERED else 'estimado'} (confidence: {confidence:.2f})",
            source_refs=["asset_generation_report.json"]
        )
```

**Verificación**: Importar `DeliveryAssetEntry` y probar `from_skipped_asset()` con datos reales de Zi One.

### T3: Crear `DeliveryContext` como estructura de contrato

**Archivo**: `modules/delivery/delivery_context.py` (modificar)

Extender la clase existente o agregar una nueva dataclass `DeliveryContext` que agrupe los estados:

```python
@dataclass
class DeliveryContext:
    """Contexto completo para generación del README y empaquetado.
    
    Fuente única de verdad para el DeliveryPackager. Contiene todos los estados
    de assets normalizados, la lista final de archivos, y metadatos del paquete.
    """
    hotel_id: str
    zip_filename: str                       # Nombre final real del ZIP (ej: "zione_20260723.zip")
    assets: List[DeliveryAssetEntry] = field(default_factory=list)
    files: List[Dict[str, Any]] = field(default_factory=list)  # files_to_package
    diagnostics_path: Optional[str] = None
    proposal_path: Optional[str] = None
    
    @property
    def delivered_assets(self) -> List[DeliveryAssetEntry]:
        return [a for a in self.assets if a.state == DeliveryAssetState.DELIVERED]
    
    @property
    def present_assets(self) -> List[DeliveryAssetEntry]:
        return [a for a in self.assets if a.state == DeliveryAssetState.PRESENT_IN_PRODUCTION]
    
    @property
    def present_with_issues_assets(self) -> List[DeliveryAssetEntry]:
        return [a for a in self.assets if a.state == DeliveryAssetState.PRESENT_WITH_ISSUES]
    
    @property
    def estimated_assets(self) -> List[DeliveryAssetEntry]:
        return [a for a in self.assets if a.state == DeliveryAssetState.ESTIMATED]
    
    @property
    def advisory_assets(self) -> List[DeliveryAssetEntry]:
        """Assets que son guías advisory (no instalables, solo de revisión)."""
        return [a for a in self.assets if a.is_advisory]
    
    @property
    def covered_count(self) -> int:
        return sum(1 for a in self.assets if a.covered)
    
    @property
    def total_services(self) -> int:
        return len(self.assets)
    
    @classmethod
    def from_asset_generation_report(
        cls,
        report_path: Path,
        hotel_id: str,
        zip_filename: str,
        files: List[Dict[str, Any]],
        service_name_map: Optional[Dict[str, str]] = None,
    ) -> "DeliveryContext":
        """Construye un DeliveryContext desde asset_generation_report.json.
        
        Este classmethod es el puente entre el pipeline y el packager:
        lee el reporte, clasifica cada asset en su estado canónico, y
        construye la lista de DeliveryAssetEntry que el README y el
        manifest consumirán.
        
        Args:
            report_path: Ruta a asset_generation_report.json
            hotel_id: ID del hotel
            zip_filename: Nombre final del ZIP (ej: "zione_20260723.zip")
            files: Lista final de archivos a empaquetar (files_to_package)
            service_name_map: Mapeo opcional asset_type → service_name humano
        
        Returns:
            DeliveryContext poblado, o con assets=[] si el reporte no existe.
        """
        report_path = Path(report_path)
        if not report_path.exists():
            # Reporte ausente → contexto vacío (README legacy)
            return cls(hotel_id=hotel_id, zip_filename=zip_filename, files=files)
        
        import json
        with open(report_path, "r", encoding="utf-8") as f:
            report = json.load(f)
        
        # Mapeo default asset_type → service_name
        default_names = {
            "whatsapp_button": "Botón de WhatsApp",
            "org_schema": "Schema Organization",
            "hotel_schema": "Schema Hotel",
            "local_business_schema": "Schema LocalBusiness",
            "faq_page": "FAQ Page Schema",
            "optimization_guide": "Guía de Optimización SEO",
            "open_graph": "Open Graph Tags",
            "geo_enriched": "Geo Enrichment",
            "analytics_setup": "Analytics Setup Guide",
            "whatsapp_conflict_guide": "Guía de Conflicto WhatsApp",
        }
        names = {**default_names, **(service_name_map or {})}
        
        assets = []
        
        # Procesar generated_assets
        for gen in report.get("generated_assets", []):
            asset_type = gen.get("asset_type", "")
            # Buscar el delivery_path real en la lista de files
            dest_path = ""
            for f in files:
                dest = f.get("dest", "")
                if asset_type in dest.lower() or asset_type.replace("_", "") in dest.lower():
                    dest_path = dest
                    break
            entry = DeliveryAssetEntry.from_generated_asset(
                gen, names.get(asset_type, asset_type), dest_path
            )
            assets.append(entry)
        
        # Procesar skipped_assets
        for skipped in report.get("skipped_assets", []):
            asset_type = skipped.get("asset_type", "")
            entry = DeliveryAssetEntry.from_skipped_asset(
                skipped, names.get(asset_type, asset_type)
            )
            assets.append(entry)
        
        # Procesar failed_assets
        for failed in report.get("failed_assets", []):
            asset_type = failed.get("asset_type", "")
            entry = DeliveryAssetEntry(
                asset_type=asset_type,
                service_name=names.get(asset_type, asset_type),
                state=DeliveryAssetState.FAILED,
                confidence=failed.get("confidence_score", 0.0),
                covered=False,
                requires_action=False,
                requires_review=True,
                message=f"Generación fallida: {failed.get('reason', 'desconocido')}",
                source_refs=["asset_generation_report.json"],
            )
            assets.append(entry)
        
        return cls(
            hotel_id=hotel_id,
            zip_filename=zip_filename,
            assets=assets,
            files=files,
        )
```

**Verificación**: Crear un `DeliveryContext` de prueba con assets de Zi One y verificar propiedades. Verificar también `from_asset_generation_report()` con el reporte real de Zi One (`output/ZiOne/v4_complete/zione/v4_audit/asset_generation_report.json`): debe producir 10 DELIVERED + 1 PRESENT (whatsapp_button).

### T4: Propagar `skipped_assets` con `presence_status` en `AssessmentBuilder`

**Archivo**: `modules/assessment_builder.py` (modificar)

El método `with_assets()` ya propaga `skipped_assets` (líneas 227-236). Verificar que el campo `presence_status` se conserva correctamente. Si es necesario, agregar el campo explícitamente:

```python
# En with_assets(), después de L236:
if asset_result and hasattr(asset_result, 'skipped_assets') and asset_result.skipped_assets:
    self._payload.skipped_assets = [
        {
            "asset_type": a.asset_type,
            "presence_status": getattr(a, 'presence_status', 'exists'),
            "reason": getattr(a, 'reason', ''),
            "site_verified": getattr(a, 'site_verified', False),
            "pain_ids_affected": getattr(a, 'pain_ids_affected', []),
        }
        for a in asset_result.skipped_assets
    ]
```

Agregar también un método `with_delivery_context()` o asegurar que `build()` incluya toda la metadata necesaria para construir un `DeliveryContext` desde el assessment.

**Verificación**: Ejecutar `python -c "from modules.assessment_builder import AssessmentBuilder; print('OK')"`

## Criterios de Completitud

- [ ] `DeliveryAssetState` enum definido con 7 valores en `delivery_context.py`
- [ ] `DeliveryAssetEntry` dataclass con `from_skipped_asset()` y `from_generated_asset()`
- [ ] `from_skipped_asset()` asigna PRESENT_WITH_ISSUES si hay pain_ids con "conflict"
- [ ] `DeliveryContext` dataclass con propiedades `delivered_assets`, `present_assets`, etc.
- [ ] `DeliveryContext.from_asset_generation_report()` classmethod implementado y funcional
- [ ] `from_asset_generation_report()` retorna contexto vacío (assets=[]) si el reporte no existe
- [ ] `covered`, `requires_action`, `requires_review` son campos independientes (no inferidos de un solo booleano)
- [ ] `is_advisory` flag en `DeliveryAssetEntry`; `from_generated_asset()` detecta guías automáticamente
- [ ] `DeliveryContext.advisory_assets` propiedad implementada
- [ ] `AssessmentBuilder.with_assets()` propaga `pain_ids_affected` en `skipped_assets`
- [ ] Tests existentes del packager siguen pasando
- [ ] Import limpio: `from modules.delivery.delivery_context import DeliveryAssetState, DeliveryAssetEntry, DeliveryContext`

## Restricciones

- NO modificar `SitePresenceChecker`
- NO modificar `CoherenceValidator`
- NO modificar `main.py`
- NO modificar `delivery_packager.py` (eso es FASE-B y FASE-C)
- Mantener compatibilidad con `DeliveryContext` existente (la clase actual en `delivery_context.py`)
- Los cambios en `assessment_builder.py` deben ser mínimos y no romper los 11 gates

## Archivos involucrados

| Archivo | Tipo de cambio |
|---------|---------------|
| `modules/delivery/delivery_context.py` | AGREGAR: enum + dataclasses (al final del archivo, manteniendo la clase existente `DeliveryContext`) |
| `modules/assessment_builder.py` | MODIFICAR: `with_assets()` (L227-236) |

## Post-Ejecución (OBLIGATORIO)

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-A --desc "DT1_DeliveryAssetState_DeliveryContext_skipped_assets_propagation"
```
