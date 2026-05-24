# 05-prompt-inicio-sesion-fase-N8-D

**Fase:** N8-D — E2E v4complete Hotel Castilla Real + Verificación
**Plan:** NUEVO-8-ASSESSMENT-BUILDER
**Sesión:** Nueva (fresh)
**Iteraciones máx:** 60
**Depende de:** N8-C ✅ (extractores simplificados, campos muertos eliminados)
**Bloquea a:** N8-RELEASE
**Tipo:** SUBAGENTE para v4complete + DIRECTA para verificación/docs
**⚠️ CONTIENE COMANDO LARGO (v4complete, ~5-10 min)**

---

## Objetivo

Ejecutar v4complete para "Hotel Castilla Real" (`https://www.hotelcastillareal.com/`) como verificación E2E de que el AssessmentBuilder + extractores simplificados funcionan correctamente. Comparar contra baseline conocido.

## Contexto de Fases Anteriores

**N8-A:** AssessmentPayload dataclass creado.
**N8-B:** AssessmentBuilder implementado, main.py migrado.
**N8-C:** Extractores simplificados (~129 → ~30 líneas), campos zombie eliminados, consistency_report dead injection removida.

**Cambio neto:** El pipeline de v4complete ahora usa el AssessmentBuilder para construir el assessment dict, y los gates usan acceso directo en vez de extractores multi-path. Esto NO debería cambiar el comportamiento — solo la estructura interna.

## Baseline de Referencia

Hotel: Castilla Real (`https://www.hotelcastillareal.com/`)
Región: `eje_cafetero`
Último v4complete exitoso: v4.49.0 (AGENTSMD-DRIFT FASE-A-01c, 2026-05-23)

| Métrica | Baseline |
|---------|----------|
| Coherence score | **0.83** |
| Publication Gates | **9/11** |
| Pain ledger entries | **11** |
| Assets generated | **12** |
| Human checklist items | **5** |
| tier_c_onboarding | **PASS** |
| Blocking issues | None |

Warnings conocidos (no blocking):
- G8: 2 assets below confidence threshold (whatsapp_conflict_guide, hotel_schema)
- WhatsApp conflict detected (GBP vs HTML inconsistency — probable false positive)

## Tareas

### T1: Ejecutar v4complete vía subagente
- **Usar delegate_task** con timeout=900s (15 min) y notify_on_complete=True
- Comando exacto: `./venv/Scripts/python.exe main.py v4complete --url "https://www.hotelcastillareal.com/"`
- Working directory: `/mnt/c/Users/Jhond/Github/iah-cli`
- Toolsets: `["terminal"]`
- Contexto para el subagente:

```
Ejecuta v4complete para Hotel Castilla Real (https://www.hotelcastillareal.com/).

Working directory: /mnt/c/Users/Jhond/Github/iah-cli
Comando: ./venv/Scripts/python.exe main.py v4complete --url "https://www.hotelcastillareal.com/"
Timeout: 900s

Este es un test E2E post-refactor NUEVO-8. Se implementó AssessmentBuilder + extractores simplificados.
El pipeline debería funcionar igual que antes. NO modificar código — solo ejecutar y reportar resultado.

Resultado esperado:
- v4complete termina sin errores
- Coherence score >= 0.80
- 9+/11 publication gates
- Assets generados: ~12
- Pain ledger entries: ~11
```

### T2: Verificar output del v4complete
Después de que el subagente complete:

**2a. Guardar evidencia (OBLIGATORIO — antes de cualquier análisis):**
```bash
mkdir -p /mnt/c/Users/Jhond/Github/iah-cli/evidence/N8-D
# Copiar archivos críticos
cp output/v4_complete/01_DIAGNOSTICO_*.md evidence/N8-D/ 2>/dev/null || echo "No diagnostic found"
cp output/v4_complete/02_PROPUESTA_*.md evidence/N8-D/ 2>/dev/null || echo "No proposal found"
# Buscar y copiar JSONs de audit
find output/v4_complete -name "*.json" -path "*/v4_audit/*" -exec cp {} evidence/N8-D/ \; 2>/dev/null
# Listar evidencia
ls -la evidence/N8-D/
```

**2b. Verificar métricas contra baseline:**
- Coherence score ≥ 0.80 (baseline: 0.83, margen aceptable: ±0.05)
- Publication gates: 9+/11 (baseline: 9/11)
- Pain ledger entries: ≥ 7 (baseline: 11)
- Assets generados: ~12
- **Sin errores de KeyError en los gates** (esto validaría que el builder entrega todos los campos)

**2c. Buscar regresiones:**
```bash
# Verificar que no hay KeyError relacionados con campos del assessment
grep -r "KeyError" output/v4_complete/ 2>/dev/null || echo "No KeyErrors found"
# Verificar coherencia
grep -r "coherence_score\|overall_score" output/v4_complete/ --include="*.json" 2>/dev/null | head -5
```

### T3: Análisis de ejecución + log_phase
- Comparar métricas con baseline:
  - Si coherence ≥ 0.80 y gates ≥ 9/11 → ✅ ÉXITO
  - Si coherence < 0.80 o gates < 9/11 → ⚠️ REGRESIÓN — documentar qué falló
  - Si hay KeyError → ❌ ERROR — el builder no entregó algún campo
- Generar resumen de comparación baseline vs post-refactor
- Ejecutar log_phase

## Criterios de Completitud
- [ ] T1: v4complete ejecutado sin errores fatales
- [ ] T2: Evidencia guardada en `evidence/N8-D/` + métricas verificadas
- [ ] T3: Análisis de ejecución completado + log_phase

## Restricciones
- Máximo 60 iteraciones
- **NO modificar código** — esto es solo verificación
- **Guardar evidencia ANTES de cualquier análisis** (protocolo obligatorio)
- v4complete via subagente con timeout=900s
- Python path: `./venv/Scripts/python.exe`
- Working directory: `/mnt/c/Users/Jhond/Github/iah-cli`

## Post-Ejecución (OBLIGATORIO)

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli && \
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase N8-D \
    --desc "v4complete E2E Hotel Castilla Real — verificacion NUEVO-8" \
    --archivos-nuevos "evidence/N8-D/" \
    --archivos-mod "" \
    --tests "0" \
    --check-manual-docs
```

## Próxima sesión
N8-RELEASE: CHANGELOG + GUIA_TECNICA + sync + validación final
