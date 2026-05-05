# 05-prompt-inicio-sesion-fase-CHAN-1

**Fase**: CHAN-1 — Channel Evidence Resolver  
**Plan**: Financial Evidence Engine  
**Sesión**: Nueva (fresh)  
**Iteraciones máx**: 60  
**Depende de**: FIN-3 ✅  
**Bloquea a**: CHAN-2  

---

## Objetivo

Crear `modules/financial_engine/channel_evidence_resolver.py`: un módulo que infiere el canal dominante de un hotel boutique basado en evidencia (onboarding, web scraping, GBP, diagnóstico), sin asumir WhatsApp como default. Usa pesos neutrales cuando no hay evidencia suficiente.

---

## Contexto de Fases Anteriores

El pipeline financiero completo (FIN-1A a FIN-3) está implementado. Ahora extendemos con priorización por canal. La validación E2E combinada se hará en FIN-4. Este módulo es nuevo y no modifica nada existente.

---

## Tareas

### T1: Diseñar e implementar `ChannelEvidenceResolver`

**Archivo**: `modules/financial_engine/channel_evidence_resolver.py` (NUEVO)

Estructura:

```python
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum

class InferredChannel(Enum):
    WHATSAPP = "whatsapp"
    GBP_LOCAL = "gbp"
    BOOKING_ENGINE = "booking_engine"
    OTA_DEPENDENT = "ota_dependent"
    SEO_CONTENT = "seo_content"
    UNKNOWN = "unknown"

class EvidenceConfidence(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class ChannelEvidence:
    dominant_channel: InferredChannel
    confidence: EvidenceConfidence
    evidence: List[str]          # Evidencia encontrada (legible)
    assumptions: List[str]       # Supuestos explícitos
    channel_weights: Dict[str, float]  # Pesos para OpportunityScorer

# Pesos boutique neutrales (sin evidencia suficiente)
NEUTRAL_WEIGHTS = {
    "gbp_local": 1.15,
    "direct_conversion": 1.10,
    "performance_mobile": 1.05,
    "whatsapp": 1.00,
    "seo_content": 0.95,
    "iao_schema": 0.95,
}

class ChannelEvidenceResolver:
    """Infiera canal dominante basado en evidencia, no en supuestos."""

    def resolve(
        self,
        onboarding_data: Optional[Dict] = None,
        web_evidence: Optional[Dict] = None,
        gbp_data: Optional[Dict] = None,
        diagnostic_pains: Optional[List[str]] = None,
    ) -> ChannelEvidence:
        """Resuelve canal dominante con nivel de confianza."""
        ...
```

### T2: Implementar lógica de inferencia

Reglas (en orden de prioridad):

**1. Onboarding confirma canal (HIGH confidence)**:
```python
if onboarding_data:
    whatsapp_share = onboarding_data.get("whatsapp_share", 0)
    direct_pct = onboarding_data.get("direct_channel_pct", 0)
    if whatsapp_share >= 0.40:
        return self._whatsapp_dominant(onboarding_data, EvidenceConfidence.HIGH)
    if direct_pct >= 0.50 and whatsapp_share < 0.10:
        return self._booking_engine_dominant(onboarding_data, EvidenceConfidence.HIGH)
```

**2. Web scraping + GBP proporcionan señales (MEDIUM confidence)**:
```python
# WhatsApp como CTA único + sin motor de reservas → WhatsApp probable
if web_evidence.get("whatsapp_visible") and not web_evidence.get("booking_engine_detected"):
    whatsapp_clues = self._count_whatsapp_signals(web_evidence, gbp_data)
    if whatsapp_clues >= 3:
        return self._whatsapp_dominant(web_evidence, EvidenceConfidence.MEDIUM)

# GBP con alto volumen de reviews → GBP/local dominante
if gbp_data.get("review_count", 0) >= 50 and gbp_data.get("score", 0) >= 4.0:
    return self._gbp_dominant(gbp_data, EvidenceConfidence.MEDIUM)
```

**3. Sin evidencia suficiente (LOW confidence)**:
```python
return ChannelEvidence(
    dominant_channel=InferredChannel.UNKNOWN,
    confidence=EvidenceConfidence.LOW,
    evidence=["No hay evidencia suficiente para inferir canal dominante."],
    assumptions=["Se usan pesos boutique neutrales para Eje Cafetero."],
    channel_weights=NEUTRAL_WEIGHTS,
)
```

**4. Prohibido**:
- ❌ `if region == "eje_cafetero": whatsapp_weight = 1.4`
- ❌ `# boutique hotels use whatsapp as main channel`

### T3: Tests unitarios

**Archivo**: `tests/financial_engine/test_channel_evidence_resolver.py` (NUEVO)

Mínimo 8 tests:
1. `test_whatsapp_dominant_from_onboarding_high_share` → WhatsApp HIGH con 40%+ share
2. `test_gbp_dominant_high_reviews` → GBP MEDIUM con 50+ reviews
3. `test_unknown_channel_no_evidence` → UNKNOWN LOW sin datos
4. `test_neutral_weights_when_unknown` → Pesos neutrales aplicados
5. `test_no_whatsapp_hardcode_by_region` → Región NO influye en peso WhatsApp
6. `test_booking_engine_dominant_from_onboarding` → Booking engine HIGH con directo 50%+
7. `test_whatsapp_cta_only_web_medium` → WhatsApp MEDIUM cuando es único CTA visible
8. `test_channel_weights_present_in_output` → Pesos incluidos en ChannelEvidence

---

## Criterios de Completitud

- [x] `modules/financial_engine/channel_evidence_resolver.py` existe
- [x] `ChannelEvidenceResolver.resolve()` implementado con 3 niveles de confianza
- [x] WhatsApp NUNCA se infiere por región o tipo de hotel
- [x] Pesos neutrales aplicados cuando confidence=LOW
- [x] `tests/financial_engine/test_channel_evidence_resolver.py` ≥8 tests pasando
- [x] Sin regla hardcodeada por región (verificado con grep `eje_cafetero` — solo comentario en test)

## Estado: ✅ COMPLETADA — 2026-05-04

---

## Restricciones

- **Modo de Ejecución**: DIRECTO con agente principal. Fase de código puro (3 tareas, 0 comandos largos) — aplica Regla código+tests del workflow v2.10.0 §Decisión. NO usar subagente. Budget: ~35 iteraciones para T1-T3 + ~25 para docs/verificación.
- Máximo 60 iteraciones
- **NO modificar `OpportunityScorer`** (CHAN-2)
- **NO modificar `v4_diagnostic_generator`** (CHAN-2)
- **NO hardcodear WhatsApp** como dominante
- **NO asumir región** como proxy de canal

---

## Post-Ejecución

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase CHAN-1 \
    --desc "Channel Evidence Resolver — inferencia de canal dominante basada en evidencia" \
    --archivos-nuevos "modules/financial_engine/channel_evidence_resolver.py,tests/financial_engine/test_channel_evidence_resolver.py" \
    --tests "8" \
    --check-manual-docs
```
