# 05-prompt-inicio-sesion-fase-CHAN-2

**Fase**: CHAN-2 — OpportunityScorer Integration with Channel Weights  
**Plan**: Financial Evidence Engine  
**Sesión**: Nueva (fresh)  
**Iteraciones máx**: 60  
**Depende de**: CHAN-1 ✅  
**Bloquea a**: CHAN-3  

---

## Objetivo

Integrar los multiplicadores de canal del `ChannelEvidenceResolver` en el `OpportunityScorer` existente, sin crear un ranking paralelo. El scorer acepta `channel_context` opcional y devuelve metadata trazable del ajuste.

---

## Contexto de Fase Anterior

- CHAN-1: `ChannelEvidenceResolver` existe con `ChannelEvidence` que contiene `channel_weights` y `dominant_channel`

---

## Tareas

### T1: Extender `OpportunityScore` con metadata de canal

**Archivo**: `modules/financial_engine/opportunity_scorer.py`

Agregar campos opcionales a `OpportunityScore`:

```python
@dataclass
class OpportunityScore:
    # ... campos existentes ...
    # NUEVOS:
    base_total_score: float = 0.0
    channel_multiplier: float = 1.0
    channel_reason: str = ""
    
    @property
    def adjusted_total_score(self) -> float:
        """Score ajustado por canal. Si channel_multiplier=1.0, = total_score."""
        return self.base_total_score * self.channel_multiplier
```

### T2: Agregar `channel_context` a `score_brechas()`

```python
def score_brechas(
    self,
    brechas: List[Dict[str, Any]],
    assessment: Optional[Dict] = None,
    competitor_data: Optional[Dict] = None,
    total_monthly_loss: Optional[float] = None,
    channel_context: Optional[Dict] = None,  # NUEVO
) -> List[OpportunityScore]:
```

Si `channel_context` es `None` → comportamiento actual sin cambios (backwards compatible).

Si `channel_context` tiene datos:

```python
channel_weights = channel_context.get("channel_weights", {})
dominant_channel = channel_context.get("dominant_channel", "unknown")

# Mapear tipo de brecha → categoría de canal para multiplicador
BRECHA_CHANNEL_MAP = {
    "whatsapp_conflict": "whatsapp",
    "no_whatsapp_visible": "whatsapp",
    "gbp_incomplete": "gbp_local",
    "low_gbp_score": "gbp_local",
    "no_hotel_schema": "iao_schema",
    "faq_schema_missing": "iao_schema",
    "poor_performance": "performance_mobile",
    "no_meta_descriptions": "seo_content",
    "poor_heading_structure": "seo_content",
    "no_og_tags": "iao_schema",
    "low_citability": "iao_schema",
    # ... resto de brechas
}

for score in scores:
    channel_category = BRECHA_CHANNEL_MAP.get(score.brecha_id, "direct_conversion")
    multiplier = channel_weights.get(channel_category, 1.0)
    
    score.base_total_score = score.total_score
    score.channel_multiplier = multiplier
    score.channel_reason = f"Canal inferido: {dominant_channel}, multiplicador {channel_category}: {multiplier}"
```

El `total_score` se preserva como `base_total_score`; el consumidor decide si usar `adjusted_total_score`.

### T3: Integrar en `v4_diagnostic_generator`

**Archivo**: `modules/commercial_documents/v4_diagnostic_generator.py`

En `_compute_opportunity_scores()` (L2562):

```python
from modules.financial_engine.channel_evidence_resolver import ChannelEvidenceResolver

def _compute_opportunity_scores(self, audit_result, financial_scenarios):
    # ... lógica existente ...
    
    # NUEVO: resolver evidencia de canal
    resolver = ChannelEvidenceResolver()
    channel_evidence = resolver.resolve(
        onboarding_data=self._get_onboarding_data(),
        web_evidence=self._get_web_evidence(audit_result),
        gbp_data=self._get_gbp_data(audit_result),
        diagnostic_pains=audit_result.get("pains", []),
    )
    
    channel_context = {
        "dominant_channel": channel_evidence.dominant_channel.value,
        "confidence": channel_evidence.confidence.value,
        "channel_weights": channel_evidence.channel_weights,
    }
    
    scores = self.scorer.score_brechas(
        brechas, assessment, competitor_data,
        channel_context=channel_context,
    )
    return scores, channel_context
```

Propagar `channel_context` a las variables de template para mostrar justificación.

### T4: Tests

**Archivo**: `tests/financial_engine/test_opportunity_scorer_channels.py` (NUEVO)

Mínimo 8 tests:
1. `test_scorer_without_channel_context_unchanged` → Sin channel_context, mismo output
2. `test_whatsapp_breaches_weighted_when_whatsapp_dominant` → Brechas WhatsApp suben
3. `test_gbp_breaches_weighted_when_gbp_dominant` → Brechas GBP suben
4. `test_base_total_score_preserved` → base_total_score = total_score original
5. `test_channel_multiplier_stored` → channel_multiplier en OpportunityScore
6. `test_neutral_weights_no_change` → Pesos 1.0 → sin ajuste
7. `test_channel_reason_populated` → channel_reason string no vacío
8. `test_backwards_compatible_existing_tests` → Tests existentes de scorer sin romper

---

## Criterios de Completitud

- [ ] `OpportunityScore` tiene `base_total_score`, `channel_multiplier`, `channel_reason`
- [ ] `score_brechas()` acepta `channel_context` opcional
- [ ] Sin `channel_context` → comportamiento idéntico al actual
- [ ] `BRECHA_CHANNEL_MAP` cubre todas las brechas del scorer
- [ ] `v4_diagnostic_generator` pasa `channel_context` al scorer
- [ ] `tests/financial_engine/test_opportunity_scorer_channels.py` ≥8 tests pasando
- [ ] Tests existentes de `opportunity_scorer` sin regresiones

---

## Restricciones

- **Modo de Ejecución**: DIRECTO con agente principal. Fase de código puro (4 tareas, 0 comandos largos) — aplica Regla código+tests del workflow v2.10.0 §Decisión. NO usar subagente. Budget: ~35 iteraciones para T1-T4 + ~25 para docs/verificación.
- Máximo 60 iteraciones
- **NO crear ranking paralelo** de brechas
- **NO modificar `ChannelEvidenceResolver`** (solo usarlo)
- **NO ejecutar `v4complete`** (ya ejecutado en FIN-4)
- Backwards compatible: sin channel_context = sin cambios

---

## Post-Ejecución

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase CHAN-2 \
    --desc "OpportunityScorer integration with channel evidence weights" \
    --archivos-nuevos "tests/financial_engine/test_opportunity_scorer_channels.py" \
    --archivos-mod "modules/financial_engine/opportunity_scorer.py,modules/commercial_documents/v4_diagnostic_generator.py" \
    --tests "8" \
    --check-manual-docs
```
