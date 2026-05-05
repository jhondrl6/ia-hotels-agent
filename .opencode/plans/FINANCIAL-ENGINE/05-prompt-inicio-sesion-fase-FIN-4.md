# 05-prompt-inicio-sesion-fase-FIN-4

**Fase**: FIN-4 — E2E Combinado: Validación Financiera + Comercial  
**Plan**: Financial Evidence Engine  
**Sesión**: Nueva (fresh)  
**Iteraciones máx**: 60  
**Depende de**: FIN-1A ✅, FIN-1B ✅, FIN-2A ✅, FIN-2B ✅, FIN-3 ✅, CHAN-1 ✅, CHAN-2 ✅  
**Bloquea a**: RELEASE  
**⚠️ CONTIENE COMANDO LARGO (v4complete) — ÚNICA ejecución del plan**  
**Hotel**: Hotel Castilla Real — https://www.hotelcastillareal.com/

---

## Objetivo

Validación E2E combinada sobre **Hotel Castilla Real** en UNA sola ejecución de v4complete. Se verifican simultáneamente:

1. **Precisión financiera**: ADR ≠ $300K legacy, rangos para Tier C/B, advertencias, CTA, sin centavos falsos
2. **Priorización por canal**: channel_context en report, multiplicadores, ranking ajustado, sin WhatsApp hardcode

---

## Contexto de Fases Anteriores (TODAS ✅)

Pipeline COMPLETO implementado:
- Metadata epistémica (FIN-1A/B): `FinancialEvidence`, `PrecisionValidator`, `EpistemicStatus`
- Benchmarks regionales (FIN-2A/B): `regional_adr_2026.json`, Caribe validado, fallback chain honesto
- Rendering (FIN-3): Templates con `monthly_loss_display`, `precision_warning`, `show_onboarding_cta`
- Channel resolver (CHAN-1): `ChannelEvidenceResolver` sin hardcodear WhatsApp
- Scorer integration (CHAN-2): `OpportunityScorer` con `channel_context` + multiplicadores trazables

---

## Tareas (4 tareas + 1 comando largo)

### T0 (PRE-FLIGHT — obligatorio antes de v4complete)

Verificar que el hotel existe y el entorno está listo:

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# Verificar hotel accesible
curl -sI https://www.hotelcastillareal.com/ | head -1

# Verificar feature flags activables
./venv/Scripts/python.exe -c "
from modules.financial_engine.feature_flags import FinancialFeatureFlags
flags = FinancialFeatureFlags.from_env()
print(f'regional_adr_enabled default: {flags.regional_adr_enabled}')
print(f'validated_regions: {flags.validated_regions}')
print(f'regional_adr_mode default: {flags.regional_adr_mode.value}')
"

# Verificar que el nuevo JSON de benchmarks existe
test -f data/benchmarks/regional_adr_2026.json && echo 'OK: regional_adr_2026.json existe' || echo 'WARNING: No existe'

# Verificar que channel_evidence_resolver es importable
./venv/Scripts/python.exe -c "from modules.financial_engine.channel_evidence_resolver import ChannelEvidenceResolver; print('OK: ChannelEvidenceResolver importable')"
```

### T1: Ejecutar v4complete (COMANDO LARGO)

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# Activar feature flags regionales
export FINANCIAL_REGIONAL_ADR_ENABLED=true
export FINANCIAL_REGIONAL_ADR_MODE=active

# ⚡ ÚNICA ejecución v4complete del plan
./venv/Scripts/python.exe main.py v4complete --url https://www.hotelcastillareal.com/
```

> **Timeout**: 600s. **Estrategia**: Aplica Regla de Decisión v4complete del workflow v2.10.0 §Decisión. Si iteraciones restantes < 30 → `delegate_task` con `notify_on_complete=True`. Si ≥ 30 → ejecución directa con `terminal(timeout=600, notify_on_complete=True)`.

**Protocolo de Evidencia (OBLIGATORIO — inmediatamente después)**:

```bash
mkdir -p evidence/FIN-4
cp output/v4_complete/01_DIAGNOSTICO_*.md evidence/FIN-4/
cp output/v4_complete/02_PROPUESTA_*.md evidence/FIN-4/
cp output/v4_complete/financial_scenarios.json evidence/FIN-4/ 2>/dev/null
cp output/v4_complete/v4_complete_report.json evidence/FIN-4/ 2>/dev/null
cp output/v4_complete/*/v4_audit/*.json evidence/FIN-4/ 2>/dev/null

echo "Evidencia guardada en evidence/FIN-4/"
ls -la evidence/FIN-4/
```

### T2: Verificar criterios FINANCIEROS

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

echo "=== CRITERIOS FINANCIEROS ==="

# C1: ADR ≠ $300.000 (legacy hardcode)
./venv/Scripts/python.exe -c "
import json, glob
files = glob.glob('output/v4_complete/financial_scenarios.json')
if files:
    with open(files[0]) as f:
        data = json.load(f)
    adr = data.get('adr_cop', 0)
    conservative = data.get('conservative', {})
    adr2 = conservative.get('adr_cop', 0) if conservative else 0
    final_adr = adr or adr2
    if final_adr == 300000:
        print('❌ FAIL: ADR = 300000 (LEGACY)')
    else:
        print(f'✅ C1 PASS: ADR = {final_adr} (≠ 300000 legacy)')
else:
    print('⚠️  C1 SKIP: financial_scenarios.json no encontrado')
"

# C2: precision_tier + can_show_exact_money en output
./venv/Scripts/python.exe -c "
import json, glob
files = glob.glob('output/v4_complete/v4_complete_report.json') + glob.glob('output/v4_complete/financial_scenarios.json')
for f in files:
    with open(f) as fh:
        data = json.load(fh)
    tier = data.get('precision_tier') or data.get('financial_precision_tier')
    exact = data.get('can_show_exact_money')
    if tier:
        print(f'✅ C2 PASS: precision_tier={tier}, can_show_exact_money={exact}')
        break
else:
    print('❌ FAIL: precision_tier no encontrado en ningún JSON')
"

# C3: Diagnóstico NO muestra $2.610.000 exacto sin advertencia
grep -l "2.610.000\|2,610,000" output/v4_complete/01_DIAGNOSTICO_*.md 2>/dev/null && \
    echo '⚠️  C3 WARNING: Cifra $2.610.000 aparece en diagnóstico' || \
    echo '✅ C3 PASS: $2.610.000 legacy NO aparece'

# C4: Advertencia de estimación preliminar visible (si Tier C/B)
grep -qi "IMPORTANTE\|preliminar\|benchmark regional\|default del sistema\|Para convertir esta estimación" \
    output/v4_complete/01_DIAGNOSTICO_*.md 2>/dev/null && \
    echo '✅ C4 PASS: Advertencia/precisión presente' || \
    echo '⚠️  C4 INFO: Sin advertencia (posible Tier A)'

# C5: CTA de onboarding presente (si Tier C/B)
grep -qi "complete los datos\|confirme su\|Para convertir esta estimación\|onboarding" \
    output/v4_complete/01_DIAGNOSTICO_*.md 2>/dev/null && \
    echo '✅ C5 PASS: CTA de onboarding presente' || \
    echo '⚠️  C5 INFO: Sin CTA (posible Tier A)'

# C6: Sin centavos falsos en desglose
grep -P '\$\d{1,3}(,\d{3})*\.\d+' output/v4_complete/01_DIAGNOSTICO_*.md 2>/dev/null && \
    echo '⚠️  C6 WARNING: Posibles centavos en output' || \
    echo '✅ C6 PASS: Sin centavos falsos'

# C7: ADR source label
grep -qi "benchmark regional\|dato confirmado\|web scraping\|onboarding" \
    output/v4_complete/01_DIAGNOSTICO_*.md 2>/dev/null && \
    echo '✅ C7 PASS: Fuente de datos mencionada' || \
    echo '⚠️  C7 WARNING: No se menciona fuente de ADR'
```

### T3: Verificar criterios de CANAL

```bash
echo ""
echo "=== CRITERIOS DE CANAL ==="

# C8: channel_context en v4_complete_report.json
./venv/Scripts/python.exe -c "
import json, glob
files = glob.glob('output/v4_complete/v4_complete_report.json')
if files:
    with open(files[0]) as f:
        data = json.load(f)
    cc = data.get('channel_context') or data.get('channel_evidence')
    if cc:
        print(f'✅ C8 PASS: channel_context presente')
        print(f'   dominant_channel: {cc.get(\"dominant_channel\", \"?\")}')
        print(f'   confidence: {cc.get(\"confidence\", \"?\")}')
    else:
        print('⚠️  C8 WARNING: channel_context no encontrado en report')
else:
    print('⚠️  C8 SKIP: v4_complete_report.json no encontrado')
"

# C9: NO se asume WhatsApp sin evidencia
./venv/Scripts/python.exe -c "
import json, glob
files = glob.glob('output/v4_complete/v4_complete_report.json')
if files:
    with open(files[0]) as f:
        data = json.load(f)
    cc = data.get('channel_context') or data.get('channel_evidence') or {}
    dom = cc.get('dominant_channel', '')
    conf = cc.get('confidence', '')
    if dom == 'whatsapp' and conf == 'low':
        print('❌ FAIL C9: WhatsApp dominante con confianza LOW (hardcode?)')
    elif dom == 'whatsapp':
        print(f'✅ C9 PASS: WhatsApp dominante con confianza {conf} (requiere evidencia)')
    else:
        print(f'✅ C9 PASS: Canal dominante = {dom} (no WhatsApp forzado)')
"

# C10: channel_multiplier en opportunity scores
./venv/Scripts/python.exe -c "
import json, glob
files = glob.glob('output/v4_complete/v4_complete_report.json')
if files:
    with open(files[0]) as f:
        data = json.load(f)
    scores = data.get('opportunity_scores', [])
    if not scores:
        print('⚠️  C10 SKIP: opportunity_scores vacío')
    else:
        has_mult = any(s.get('channel_multiplier', 1.0) != 1.0 for s in scores)
        print(f'✅ C10 PASS: Scores={len(scores)}, channel_multiplier activo={has_mult}')
        for s in scores[:3]:
            print(f'   {s.get(\"brecha_id\",\"?\"):30s} base={s.get(\"base_total_score\",0):.0f} mult={s.get(\"channel_multiplier\",1.0):.2f}')
"

# C11: channel_reason trazable
grep -qi "canal inferido\|multiplicador\|channel_reason\|dominant_channel" \
    output/v4_complete/01_DIAGNOSTICO_*.md 2>/dev/null && \
    echo '✅ C11 PASS: channel_reason trazable en diagnóstico' || \
    echo '⚠️  C11 INFO: channel_reason no visible en diagnóstico (puede estar en JSON)'
```

### T4: Reporte final

Generar `evidence/FIN-4/validation_report.md` con resumen de criterios:

```markdown
# FIN-4 Combined E2E Validation Report

**Hotel**: Hotel Castilla Real (hotelcastillareal.com)
**Fecha**: $(date +%Y-%m-%d)
**v4complete exit code**: $?

## Criterios Financieros

| # | Criterio | Resultado |
|---|----------|-----------|
| C1 | ADR ≠ $300K legacy | ... |
| C2 | precision_tier + can_show_exact_money | ... |
| C3 | Sin $2.610.000 exacto | ... |
| C4 | Advertencia preliminar | ... |
| C5 | CTA onboarding | ... |
| C6 | Sin centavos falsos | ... |
| C7 | Fuente de datos mencionada | ... |

## Criterios de Canal

| # | Criterio | Resultado |
|---|----------|-----------|
| C8 | channel_context presente | ... |
| C9 | WhatsApp no asumido sin evidencia | ... |
| C10 | channel_multiplier en scores | ... |
| C11 | channel_reason trazable | ... |

## Veredicto

- [ ] READY — todos los criterios pasan
- [ ] ISSUES — crear FASE-FIX para: ...
```

---

## Criterios de Completitud

- [ ] Pre-flight checks pasan (hotel accesible, flags, JSON, imports)
- [ ] v4complete ejecutado exitosamente sobre Hotel Castilla Real
- [ ] Evidencia copiada a `evidence/FIN-4/`
- [ ] C1-C7 verificados (financieros) — al menos C1, C2, C3 deben pasar
- [ ] C8-C11 verificados (canal) — al menos C8, C9 deben pasar
- [ ] `evidence/FIN-4/validation_report.md` generado con veredicto
- [ ] Si hay fallos → documentados con ISSUES claros

---

## Restricciones

- Máximo 60 iteraciones (planificar presupuesto ANTES de v4complete)
- **UNA sola ejecución de v4complete** — sin reintentos
- **NO modificar código** — solo validación
- Si iteraciones restantes < 30 → usar `delegate_task` para v4complete (workflow v2.10.0 §Regla de Decisión v4complete)
- Si v4complete falla → reportar en validation_report.md, NO re-ejecutar

---

## Post-Ejecución

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FIN-4 \
    --desc "E2E combinado financiero + comercial — Hotel Castilla Real" \
    --archivos-nuevos "evidence/FIN-4/" \
    --tests "0" \
    --check-manual-docs
```
