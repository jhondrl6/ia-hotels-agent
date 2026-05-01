# FASE-CONFIG-7: Validación E2E — v4complete Amazilia Hotel + Análisis de Hallazgos

**Plan:** FEATURE-CONFIG-EXTRACTION v1.0.0
**Workflow:** `.agents/workflows/phased_project_executor.md` v2.9.0
**Presupuesto:** 60 iteraciones max | **Estimado esta fase:** ~48 iteraciones
**Dependencias:** TODAS las fases anteriores (CONFIG-1 a CONFIG-6) DEBEN estar COMPLETADAS
**Fase siguiente:** FASE-CONFIG-8

---

## Contexto

**Fuente:** `.opencode/context/TECHNICAL_DEBT_2026-04-29.md`
**Hotel:** Amazilia Hotel (hotel_id: `amaziliahotel`)
**URL:** https://amaziliahotel.com (verificar URL real en onboarding previo)

Después de 6 fases de extracción de hardcodes, esta fase ejecuta v4complete para Amazilia y analiza si los hallazgos del TECHNICAL_DEBT quedan resueltos.

---

## Objetivo de la Fase

1. Ejecutar v4complete en Amazilia Hotel con el código YA refactorizado (todos los YAML en uso)
2. Verificar que los 31 hardcodes NO aparecen en el output generado
3. Analizar si las causas raíz (CR-1 a CR-7) están efectivamente corregidas
4. Documentar cualquier hallazgo residual

---

## Tareas Específicas

### Tarea 1: Preparación pre-v4complete
- Verificar que TODOS los YAML existen y son válidos:
  ```bash
  ls -la config/pricing.yaml config/scenarios.yaml config/financial_defaults.yaml
  ls -la config/fallbacks.yaml config/commercial.yaml config/regional_benchmarks.yaml
  ```
- Verificar que sync_versions.py está corregido (FASE-CONFIG-1):
  ```bash
  venv/Scripts/python.exe scripts/sync_versions.py --check
  ```
- Ejecutar tests existentes para verificar que no hay regresiones:
  ```bash
  venv/Scripts/python.exe -m pytest tests/ -x --tb=short -q 2>&1 | tail -5
  ```

### Tarea 2: Ejecutar v4complete para Amazilia Hotel (COMANDO LARGO)
**⚠️ Usar subagente con delegate_task (timeout=900, notify_on_complete=True)**

```bash
# Comando a delegar al subagente:
cd /mnt/c/Users/Jhond/Github/iah-cli
venv/Scripts/python.exe main.py v4complete --url https://amaziliahotel.com
```

**Instrucciones para el subagente:**
- Ejecutar v4complete con timeout 600s
- Esperar a que termine
- Reportar: exit_code, coherence_score, publication_status, archivos generados
- No hacer análisis post-ejecución (eso lo hace el agente parent)

**En el agente parent:**
- Usar delegate_task con toolsets=["terminal"]
- Esperar resultado del subagente

### Tarea 3 (OBLIGATORIO - INMEDIATO POST-OUTPUT): Guardar evidencia proactiva
```bash
mkdir -p evidence/fase-config-7

# Copiar archivos críticos
cp output/v4_complete/01_DIAGNOSTICO_*.md evidence/fase-config-7/
cp output/v4_complete/02_PROPUESTA_*.md evidence/fase-config-7/
cp output/v4_complete/amaziliahotel/v4_audit/*.json evidence/fase-config-7/ 2>/dev/null || true
cp output/v4_complete/*.json evidence/fase-config-7/ 2>/dev/null || true

# Copiar YAML config (evidencia del estado de configuración)
cp config/*.yaml evidence/fase-config-7/configs/
```

### Tarea 4: Análisis de Resolución de Hallazgos

Verificar CADA hallazgo del TECHNICAL_DEBT:

#### 4.1 Verificar eliminación de hardcodes en output
```bash
# Buscar hardcodes conocidos en los documentos generados
# Si aparecen, el fix no fue efectivo
grep -n "benchmark.*58\|score.*50\|coherence.*70" evidence/fase-config-7/01_DIAGNOSTICO_*.md
grep -n "0\.15\|0\.20\|0\.25" evidence/fase-config-7/02_PROPUESTA_*.md
grep -n "800.000\|1.200.000\|2.500.000" evidence/fase-config-7/02_PROPUESTA_*.md
grep -n "5\.0X\|break_even.*6" evidence/fase-config-7/02_PROPUESTA_*.md
```

#### 4.2 Verificar flags "estimated"
- Leer el diagnóstico y propuesta generados
- Buscar indicadores de "estimated" o "⚠️ Valor estimado"
- Confirmar que aparecen DONDE aplica (métricas sin datos reales)
- Confirmar que NO aparecen donde NO aplica (métricas con datos reales)

#### 4.3 Verificar consistencia de valores
- Comparar valores en output vs YAML config:
  - Precio del paquete en propuesta vs `pricing.yaml → packages.monthly_default`
  - ROI cap vs `commercial.yaml → roi.cap`
  - Garantías vs `commercial.yaml → guarantees`
  - Planes vs `commercial.yaml → plans`

#### 4.4 Verificar coherence y publication gates
- Leer `coherence_validation.json` o `v4_complete_report.json`
- Verificar coherence_score >= 0.80
- Verificar publication_status = READY_FOR_PUBLICATION
- Si algún gate falla, documentar por qué

#### 4.5 Análisis de hallazgos residuales
Crear documento `evidence/fase-config-7/ANALISIS_HALLAZGOS.md` con:

```markdown
# Análisis de Resolución de Hallazgos — Amazilia Hotel v4complete

**Fecha:** [fecha de ejecución]
**Coherence:** [score]
**Publication:** [status]

## CR-1/CR-2/CR-3: sync_versions bug
- [ ] sync_versions.py propaga correctamente → [PASA/FALLA]
- [ ] --check reporta correctamente → [PASA/FALLA]

## CR-3: Fallbacks silenciosos
- [ ] Flags "estimated" visibles en output → [PASA/FALLA]
- [ ] H-11 benchmark_score no hardcodeado → [PASA/FALLA]
- [ ] H-12 score_tecnico no hardcodeado → [PASA/FALLA]
- [ ] H-13 coherence_score no hardcodeado → [PASA/FALLA]
- [ ] H-27 voice_readiness no hardcodeado → [PASA/FALLA]

## CR-4: Parámetros financieros
- [ ] H-14 recovery_factors → YAML → [PASA/FALLA]
- [ ] H-17 scenario_weights → YAML → [PASA/FALLA]
- [ ] H-18a/b floor_price unificado → [PASA/FALLA]
- [ ] H-19 TIER_CONFIG → YAML → [PASA/FALLA]
- [ ] H-20 degradation_rate → YAML → [PASA/FALLA]
- [ ] H-21 OTA shifts → YAML → [PASA/FALLA]
- [ ] H-22 ia_boost → YAML → [PASA/FALLA]
- [ ] N-01 pain_ratio → YAML → [PASA/FALLA]
- [ ] N-11/N-11b financial defaults → YAML → [PASA/FALLA]
- [ ] N-12 GATE ratios → YAML → [PASA/FALLA]

## CR-5: Garantías duplicadas
- [ ] _build_guarantees_section() eliminado → [PASA/FALLA]
- [ ] Garantías solo en template + YAML → [PASA/FALLA]

## CR-6: Config/code reconnect
- [ ] settings.yaml sin duplicados → [PASA/FALLA]
- [ ] Generadores no importan settings.yaml → [PASA/FALLA]

## CR-7: Narrativas de impacto
- [ ] N-05 pain narratives → YAML → [PASA/FALLA]
- [ ] N-02, N-03, N-06-N-10 umbrales → YAML → [PASA/FALLA]

## Hardcodes comerciales
- [ ] H-15 ROI cap → YAML → [PASA/FALLA]
- [ ] H-16 break_even → YAML → [PASA/FALLA]
- [ ] H-23 descuentos → YAML → [PASA/FALLA]
- [ ] H-24 cuotas → YAML → [PASA/FALLA]
- [ ] H-26 plan stubs → YAML → [PASA/FALLA]
- [ ] N-04/N-04b payment discounts → YAML → [PASA/FALLA]

## GAPs NO cubiertos
- [ ] Profound/Semrush API stubs → [SIGUEN SIENDO STUBS]
- [ ] Coordenadas 0.0 en auditors → [NO CORREGIDO]
- [ ] Integración LLM en scraper_fallback → [NO CORREGIDO]

## Veredicto Final
[¿Se superan los hallazgos del TECHNICAL_DEBT_2026-04-29?]
[¿Quedan hardcodes residuales? ¿Cuáles?]
[¿La calidad del output mejoró, se mantuvo o empeoró?]
```

---

## Archivos Involucrados

| Archivo | Tipo | Propósito |
|---------|------|-----------|
| `output/v4_complete/01_DIAGNOSTICO_*.md` | OUTPUT | Verificar eliminación de hardcodes |
| `output/v4_complete/02_PROPUESTA_*.md` | OUTPUT | Verificar valores YAML en propuesta |
| `output/v4_complete/amaziliahotel/v4_audit/*.json` | OUTPUT | Verificar coherence + gates |
| `output/v4_complete/v4_complete_report.json` | OUTPUT | Verificar publication status |
| `evidence/fase-config-7/ANALISIS_HALLAZGOS.md` | NUEVO | Documento de análisis |

---

## Criterios de Completitud

- [ ] v4complete ejecutado exitosamente para Amazilia Hotel
- [ ] Evidencia guardada en `evidence/fase-config-7/`
- [ ] Coherence >= 0.80
- [ ] Publication gates: READY_FOR_PUBLICATION
- [ ] 31 hardcodes NO aparecen como literales en output generado
- [ ] Flags "estimated" visibles donde aplica
- [ ] Valores en output coinciden con YAML config (no con hardcodes antiguos)
- [ ] `ANALISIS_HALLAZGOS.md` creado con veredicto por cada CR y hardcode
- [ ] Hallazgos residuales documentados (GAPs no cubiertos)

---

## Restricciones

- **NO modificar código** en esta fase (todo el código ya está refactorizado)
- **NO modificar YAML config** a menos que se detecte un error
- **Si v4complete falla**, documentar el error y continuar con el análisis
- **Máximo 60 iteraciones** (R2)
- **Subagente obligatorio** para v4complete (timeout=900)
- **Evidencia proactiva OBLIGATORIA** antes de cualquier verificación

---

## Post-Ejecución

```bash
venv/Scripts/python.exe scripts/log_phase_completion.py     --fase FASE-CONFIG-7     --desc "Validación E2E: v4complete Amazilia Hotel + análisis de resolución de 31 hardcodes y 7 causas raíz. Verificación de flags estimated, consistency YAML vs output."     --archivos-nuevos "evidence/fase-config-7/ANALISIS_HALLAZGOS.md"     --tests "0"     --coherence [COMPLETAR_CON_VALOR_REAL]     --check-manual-docs
```

**Siguiente fase:**
```
Carga y ejecuta .opencode/plans/05-prompt-inicio-sesion-fase-CONFIG-8.md siguiendo .agents/workflows/phased_project_executor.md
```
