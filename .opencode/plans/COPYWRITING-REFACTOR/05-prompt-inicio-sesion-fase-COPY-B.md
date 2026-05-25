# 05-prompt-inicio-sesion-fase-COPY-B

**Fase**: COPY-B — Commercial Gates + Content Validation Rules
**Plan**: COPYWRITING-REFACTOR (Copywriting.jsonl → Refactorización Comercial)
**Sesión**: Nueva (fresh)
**Iteraciones máx**: 60
**Depende de**: COPY-A ✅ (templates y generators ya modificados)
**Bloquea a**: COPY-C

## Objetivo

Crear un módulo de gates comerciales (`modules/quality_gates/commercial_gate.py`) que bloquee/advierta sobre problemas de copywriting en los documentos generados, e integrarlo en los generators existentes. También agregar la corrección determinística de "IA Bloqueada" → "IA sin guía".

## Contexto de Fases Anteriores

COPY-A reestructuró los templates y corrigió bugs de lógica financiera:
- `diagnostico_v6_template.md`: Vista Gerencia (secciones 1-6) + Anexo Técnico (7+)
- `propuesta_v6_template.md`: Finanzas honestas, OTA narrative, quick wins del dueño
- `v4_diagnostic_generator.py`: `_build_scenario_table_rows` con clamp, `_build_financial_placeholders` con tier unificado

El archivo base de reglas: `.opencode/context/Copywriting.jsonl` — secciones `commercial_gate_spec` (línea 18) y `copywriting_rules` (línea 15).

## Tareas

### T1: Crear `modules/quality_gates/commercial_gate.py`

**Archivo NUEVO**: `modules/quality_gates/commercial_gate.py`

Crear un módulo con dos clases de gates:

**Gates Bloqueantes** (si fallan, el documento NO debe publicarse como está):

| Gate ID | Nombre | Condición | Severidad |
|---------|--------|-----------|-----------|
| CG-SCENARIO-ORDER | Orden de escenarios inválido | `optimista < realista` o `realista < conservador` | BLOCKING |
| CG-SCENARIO-NEGATIVE | Escenario negativo como recuperación | `optimista < 0` mostrado en tabla de recuperación | BLOCKING |
| CG-IA-BLOCKED-CLAIM | "IA Bloqueada" sin evidencia | Contiene "bloqueada" y `blocked_crawlers` vacío | BLOCKING |
| CG-ROI-NEGATIVE | ROI negativo como argumento de cierre | `net_benefit_6m < 0` y no hay plan de onboarding alternativo | BLOCKING |
| CG-CLAIM-VS-EVIDENCE | Claims no soportados por datos | "No aparece" cuando `place_found == true` o rating > 4.0 | BLOCKING |

**Gates Advisory** (warnings que no bloquean pero deben revisarse):

| Gate ID | Nombre | Condición | Severidad |
|---------|--------|-----------|-----------|
| CG-WHATSAPP-LEAD | WhatsApp no lidera narrativa | WhatsApp no es primera brecha/sección en diagnóstico | WARNING |
| CG-OTA-NARRATIVE | Sin narrativa OTA | 0 menciones de Booking/Expedia/comisiones en propuesta | WARNING |
| CG-TIER-CONSISTENCY | Tier inconsistente | Frontmatter tier ≠ texto tier | WARNING |
| CG-TECH-JARGON | Jerga técnica en vista gerencia | Schema/AEO/IAO/Open Graph/Nap/Rich Snippets en primeras 6 secciones | WARNING |

Estructura del módulo:

```python
"""Commercial Gate Validator — bloquea/adiverte sobre problemas de copywriting."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import re

@dataclass
class CommercialGateResult:
    gate_id: str
    name: str
    passed: bool
    severity: str  # "BLOCKING" or "WARNING"
    message: str
    suggestion: str

@dataclass  
class CommercialGateReport:
    all_passed: bool
    blocking_passed: bool
    results: List[CommercialGateResult]
    summary: str

class CommercialGateValidator:
    """Valida documentos comerciales contra reglas de copywriting."""
    
    BLOCKING_GATES = [
        "CG-SCENARIO-ORDER",
        "CG-SCENARIO-NEGATIVE", 
        "CG-IA-BLOCKED-CLAIM",
        "CG-ROI-NEGATIVE",
        "CG-CLAIM-VS-EVIDENCE",
    ]
    
    def validate_diagnostic(
        self,
        diagnostic_text: str,
        scenarios: Any,
        ai_crawlers_data: Dict[str, Any],
        place_found: bool,
        gbp_rating: float,
    ) -> CommercialGateReport:
        """Valida el documento de diagnóstico contra gates comerciales."""
        ...
    
    def validate_proposal(
        self,
        proposal_text: str,
        net_benefit_6m: float,
        roi: float,
        has_onboarding_plan: bool = False,
    ) -> CommercialGateReport:
        """Valida el documento de propuesta contra gates comerciales."""
        ...
```

**Referencia de implementación**: Usar el patrón de `coherence_validator.py` para estructura (resultado + report).

### T2: Corregir "IA Bloqueada" → "IA sin guía" en fuente de datos

**Archivo**: `modules/commercial_documents/v4_diagnostic_generator.py`
**Método exacto**: `_pain_to_brecha()` (L2625)

**Problema**: El dict estático `_get_pain_narratives()` (L2692) define:
```python
'ai_crawler_blocked': {
    'nombre': 'IA Bloqueada (Invisible para ChatGPT)',
    ...
}
```
Este string se usa SIEMPRE, incluso cuando `blocked_crawlers == []` (el hotel NO tiene crawlers bloqueados). El diagnóstico miente diciendo "IA Bloqueada" cuando la IA sí puede acceder.

**Flujo real de datos**: `_identify_brechas()` → `_pain_to_brecha(pain)` → `_get_pain_narratives(pain)` → dict estático → `nombre` se asigna sin validar `blocked_crawlers`.

**Fix (determinístico, sin regex)**: En `_pain_to_brecha()` (L2625), después de obtener el dict de `_get_pain_narratives()`, agregar lógica condicional:

```python
def _pain_to_brecha(self, pain, region: str = "eje_cafetero") -> Optional[Dict[str, Any]]:
    narratives = self._get_pain_narratives(pain)
    if not narratives:
        return None
    
    nombre = narratives['nombre']
    
    # GAP-COPY-FIX: "IA Bloqueada" solo si realmente hay crawlers bloqueados
    if pain.id == 'ai_crawler_blocked':
        # Verificar blocked_crawlers desde el audit result
        ai_crawlers = getattr(audit_result, 'ai_crawlers', None)
        blocked = getattr(ai_crawlers, 'blocked_crawlers', []) or [] if ai_crawlers else []
        if not blocked:
            nombre = 'IA sin guía (Sin mapa para asistentes de IA)'
    
    return {
        'pain_id': pain.id,
        'nombre': nombre,
        'impacto': narratives.get('impacto', 0.10),
        'detalle': narratives.get('detalle', ''),
    }
```

**Nota**: Se requiere acceso a `audit_result` dentro de `_pain_to_brecha()`. Si el método no recibe `audit_result` actualmente, agregarlo como parámetro. Alternativa: hacer el check en `_identify_brechas()` (L2563) ANTES de llamar a `_pain_to_brecha()`, pasando la info de `blocked_crawlers` como argumento adicional.

**Ventaja sobre regex**: 
- Determinístico (sin falsos positivos por matches parciales en otros textos)
- Afecta solo `ai_crawler_blocked`, no cualquier texto que contenga "bloqueada"
- La fuente de verdad es el dato, no el texto renderizado

### T3: Integrar commercial gates en los generators

**Archivos**: 
- `modules/commercial_documents/v4_diagnostic_generator.py`
- `modules/commercial_documents/v4_proposal_generator.py`

En cada generator, después de generar el documento:

1. Importar `CommercialGateValidator`
2. Instanciar con los datos disponibles del audit
3. Ejecutar `validate_diagnostic()` o `validate_proposal()` según corresponda
4. Si hay gates BLOCKING que fallan:
   - Agregar sección "⚠️ Alertas Comerciales" al final del documento
   - NO bloquear la generación (el pipeline sigue)
   - Loggear warnings
5. Agregar el resultado al `gate_report` o `coherence_validation` existente

```python
# En v4_diagnostic_generator, después de generate()
from modules.quality_gates.commercial_gate import CommercialGateValidator

validator = CommercialGateValidator()
commercial_report = validator.validate_diagnostic(
    diagnostic_text=final_document,
    scenarios=scenarios,
    ai_crawlers_data=audit_result.ai_crawlers,
    place_found=audit_result.gbp_place_found,
    gbp_rating=audit_result.gbp_rating,
)

if not commercial_report.blocking_passed:
    # Agregar alertas al documento
    alert_section = "\n---\n## ⚠️ Alertas Comerciales\n\n"
    for result in commercial_report.results:
        if not result.passed and result.severity == "BLOCKING":
            alert_section += f"- **{result.name}**: {result.message}\n  → {result.suggestion}\n"
    final_document += alert_section
```

## Criterios de Completitud

- [x] `modules/quality_gates/commercial_gate.py` existe con ≥5 gates (3+ BLOCKING, 2+ WARNING)
- [x] Tests: al menos 3 tests unitarios para gates (escenario negativo, IA bloqueada, ROI negativo)
- [x] Corrección "IA Bloqueada" → "IA sin guía" implementada en `_pain_to_brecha()` (L2625) — fuente de datos
- [x] `CommercialGateValidator` integrado en ambos generators
- [x] Si un documento tiene gates BLOCKING fallidos, se agrega sección de alertas
- [x] `log_phase_completion.py` ejecutado al finalizar

## Restricciones

- **NO ejecutar v4complete** en esta fase
- **NO modificar** los templates (ya modificados en COPY-A)
- **NO modificar** `_build_scenario_table_rows` ni `_build_financial_placeholders` (ya corregidos en COPY-A)
- Máximo 60 iteraciones

## Post-Ejecución (OBLIGATORIO)

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-COPY-B --desc "Commercial gates: scenario_order, roi_positive, ia_blocked_claim, whatsapp_lead, ota_narrative" --check-manual-docs
```

Luego actualizar `09-documentacion-post-proyecto.md` marcando FASE-COPY-B como [x].
