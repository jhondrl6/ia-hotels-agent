# FASE-J: E2E Validation + Release

**ID**: FASE-J
**Objetivo**: Ejecutar `v4complete` para `amaziliahotel.com` como validación end-to-end, verificar que todas las correcciones F/G/H/I funcionan integradas, y emitir release v4.26.0
**Dependencias**: FASE-F, FASE-G, FASE-H, FASE-I TODAS completadas
**Duración estimada**: 2-3 horas
**Skill**: `iah-cli-phased-execution`

---

## Contexto

### Propósito

Esta es la fase de verificación integral. Todas las correcciones de las fases F-I deben manifestarse correctamente cuando se ejecuta el flujo completo `v4complete` contra un hotel real. Usamos `amaziliahotel.com` como caso de prueba porque ya tiene datos históricos de ejecución previa (6 brechas detectadas, coherence 0.84).

### Criterio de Éxito: Superación de Brechas

La ejecución debe demostrar:

1. **Phantom Costs Eliminados** (FASE-F): Si el hotel tiene N < 4 problemas reales, las brechas N+1..4 muestran "$0"
2. **Impactos Reales** (FASE-G): Los costos en la propuesta reflejan los pesos reales (0.30, 0.25, etc.), no una distribución fija
3. **No Overwrite Silencioso** (FASE-G): Los nombres de brechas son consistentes entre diagnóstico y propuesta
4. **Caché Funcionando** (FASE-H): No hay degradación de performance
5. **Sin Duplicados** (FASE-I): data_structures importa limpiamente

### Veredicto Posibles

| Resultado | Significado | Acción |
|-----------|-------------|--------|
| **EXITOSO** | Todas las correcciones se manifiestan correctamente | Proceder con release |
| **PERSISTENCIA PARCIAL** | Algunas correcciones funcionaron, otras no | Documentar qué falla, crear fix phase |
| **FALLIDO** | Las correcciones no se manifiestan en E2E | Rollback + análisis de causa raíz |

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-F | ✅ Completada — Phantom costs eliminados |
| FASE-G | ✅ Completada — Dual source resuelto + impactos reales |
| FASE-H | ✅ Completada — Caché + cleanup |
| FASE-I | ✅ Completada — Deduplication |

---

## Tareas

### Tarea 1: Pre-flight Checks

**Objetivo**: Verificar que el entorno está listo para ejecución E2E

**Comandos**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# Verificar integridad de imports
./venv/Scripts/python.exe -c "
from modules.commercial_documents.v4_proposal_generator import V4ProposalGenerator
from modules.commercial_documents.v4_diagnostic_generator import V4DiagnosticGenerator
from modules.commercial_documents.data_structures import DiagnosticSummary, Scenario
print('All imports OK')
"

# Quick validations
./venv/Scripts/python.exe scripts/run_all_validations.py --quick

# Verificar que tests de las fases anteriores pasan
./venv/Scripts/python.exe -m pytest tests/test_proposal_alignment.py tests/commercial_documents/test_diagnostic_brechas.py -v
```

**Criterios de aceptación**:
- [ ] Todos los imports exitosos
- [ ] run_all_validations --quick pasa
- [ ] Tests de FASE-F/G/H/I pasan

### Tarea 2: Ejecutar v4complete para amaziliahotel.com

**Objetivo**: Ejecución E2E completa y capturar resultados

**Comando**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe main.py v4complete --url https://amaziliahotel.com
```

**Nota**: Esta ejecución consume APIs externas (PageSpeed, Places, etc.) y tiene costo real. Asegurarse de que las API keys estén configuradas.

**Datos a capturar post-ejecución**:
- [ ] Exit code del comando
- [ ] Coherence score
- [ ] Número de brechas detectadas
- [ ] Costos por brecha en la propuesta (verificar pesos reales vs fijos)
- [ ] Número de assets generados
- [ ] Publication ready status
- [ ] Tiempo total de ejecución (comparar con baseline previo para verificar caché)

### Tarea 3: Verificar Resultados Contra Criterios de Aceptación

**Objetivo**: Analizar los documentos generados y verificar que las correcciones se manifiestan

**Archivos a inspeccionar**:
```
output/amaziliahotelcom_*/
├── diagnostico_v6_*.md    → Verificar brechas_section con impactos reales
├── propuesta_v6_*.md      → Verificar que NO tiene phantom costs
├── v4_complete_report.json → Coherence, publication status
└── assets/                 → Número de assets generados
```

**Checklist de verificación**:

3a. **Phantom Costs (FASE-F)**:
- [ ] Abrir propuesta generada
- [ ] Contar brechas con costo > $0
- [ ] Verificar que no hay brechas "Tercer problema" / "Cuarto problema" con costos
- [ ] Si hay < 4 brechas reales, las extras muestran "$0" o no aparecen

3b. **Impactos Reales (FASE-G)**:
- [ ] Abrir diagnóstico generado
- [ ] Verificar que cada brecha tiene un impacto específico (no uniforme)
- [ ] Los costos en la propuesta son proporcionales a los impactos del diagnóstico
- [ ] No hay inconsistencia entre nombres en diagnóstico vs propuesta

3c. **No Overwrite (FASE-G)**:
- [ ] Los nombres de brechas en el diagnóstico son los mismos que `_identify_brechas()` genera
- [ ] No hay nombres de OpportunityScorer reemplazando los de _identify_brechas

3d. **Performance (FASE-H)**:
- [ ] Tiempo de ejecución razonable (no significativamente más lento que baseline)
- [ ] Sin errores o warnings sobre caché

3e. **Sin Duplicados (FASE-I)**:
- [ ] Import de data_structures limpio (ya verificado en Tarea 1)

### Tarea 4: Emitir Veredicto

**Objetivo**: Determinar si la implementación fue exitosa o si hay persistencia

**Veredicto template**:
```
VEREDICTO: [EXITOSO / PERSISTENCIA PARCIAL / FALLIDO]

Correcciones Verificadas:
- [✅/❌] Phantom Costs eliminados: [detalle]
- [✅/❌] Impactos reales conectados: [detalle]
- [✅/❌] Dual source resuelto: [detalle]
- [✅/❌] Caché funcionando: [detalle]
- [✅/❌] Sin duplicados: [detalle]

Métricas:
- Brechas detectadas: [N] (antes: [N_previo])
- Coherence: [X.XX] (antes: 0.84)
- Assets generados: [N]
- Publication Ready: [true/false]

Persistencias (si aplica):
- [Lista de problemas que persisten después de las correcciones]
```

### Tarea 5: Release v4.26.0 (solo si veredicto EXITOSO)

**Objetivo**: Emitir release con todas las correcciones

**Pasos**:

1. Actualizar `VERSION.yaml`:
```yaml
version: "4.26.0"
codename: "Brecha Architectural Fix"
release_date: "2026-04-10"
```

2. Actualizar `CHANGELOG.md`:
```markdown
## [4.26.0] - Brecha Architectural Fix (2026-04-10)

### Objetivo
Eliminar gap arquitectónico donde la propuesta V6 no consumía brechas reales del diagnóstico.

### Cambios Implementados
- `modules/commercial_documents/v4_proposal_generator.py` - Eliminada distribución fija 40/30/20/10, phantom costs corregidos
- `modules/commercial_documents/v4_diagnostic_generator.py` - Resuelto dual source conflict, caché para _identify_brechas (9x→1x), cleanup pain_to_type
- `modules/commercial_documents/data_structures.py` - Eliminados duplicados de Scenario, calculate_quick_wins, extract_top_problems. Agregado brechas_reales a DiagnosticSummary

### Tests
- 14 tests nuevos (5 phantom + 5 dual source + 4 cache/dedup)
- 0 regresiones
- Validado E2E con amaziliahotel.com
```

3. Ejecutar release:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-RELEASE-4.26.0 \
    --desc "Brecha Architectural Fix - phantom costs, dual source, cache, dedup" \
    --archivos-mod "modules/commercial_documents/v4_proposal_generator.py,modules/commercial_documents/v4_diagnostic_generator.py,modules/commercial_documents/data_structures.py" \
    --tests "14" \
    --coherence "[SCORE]" \
    --check-manual-docs
```

4. Version sync:
```bash
./venv/Scripts/python.exe scripts/sync_versions.py
./venv/Scripts/python.exe scripts/version_consistency_checker.py
```

5. Commit:
```bash
git add -A
git commit -m "v4.26.0: Brecha Architectural Fix — phantom costs, dual source, cache, dedup (FASE-F/G/H/I/J)"
```

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| Pre-flight imports | Terminal | Todos los imports OK |
| Tests FASE-F | `tests/test_proposal_alignment.py` | 5/5 pasan |
| Tests FASE-G/H | `tests/commercial_documents/test_diagnostic_brechas.py` | 9/9 pasan |
| Tests FASE-I | `tests/commercial_documents/test_data_structures.py` | 4/4 pasan |
| v4complete E2E | Terminal | Exit code 0 |
| Document inspection | Manual | Phantom costs = 0, impactos reales |

**Comando de validación completo**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/ -v --tb=short
./venv/Scripts/python.exe scripts/run_all_validations.py
```

---

## Post-Ejecución (OBLIGATORIO)

Al finalizar esta fase, actualizar INMEDIATAMENTE:

1. **`dependencias-fases.md`**: Marcar FASE-J como ✅ Completada
2. **`06-checklist-implementacion.md`**: Marcar TODOS los items como ✅
3. **`09-documentacion-post-proyecto.md`**: Completar TODAS las secciones
4. **Documentación oficial**: CHANGELOG.md, GUIA_TECNICA.md, VERSION.yaml, REGISTRY.md
5. **Git commit** con tag v4.26.0

---

## Criterios de Completitud (CHECKLIST)

- [ ] **v4complete ejecutado**: Exit code 0 para amaziliahotel.com
- [ ] **Phantom costs = 0**: No hay brechas ficticias con costo > $0
- [ ] **Impactos reales**: Costos proporcionales a pesos (0.30, 0.25, etc.)
- [ ] **Coherence >= 0.80**: Umbral de publicación cumplido
- [ ] **Veredicto emitido**: EXITOSO, PERSISTENCIA PARCIAL, o FALLIDO documentado
- [ ] **Release emitido** (si exitoso): VERSION.yaml 4.26.0, CHANGELOG, sync
- [ ] **Suite completa pasa**: 0 regresiones
- [ ] **Validaciones pasan**: run_all_validations.py (no solo --quick)
- [ ] **Documentación completa**: CHANGELOG, GUIA_TECNICA, REGISTRY, docs afiliados
- [ ] **Git commit + tag**: Todo commiteado y tagueado

---

## Restricciones

- NO modificar código en esta fase — solo validar y documentar
- Si se encuentran bugs, documentarlos pero NO fixearlos en esta sesión (crear nueva fase)
- El v4complete consume APIs reales — verificar API keys antes de ejecutar
- Si amaziliahotel.com no responde, usar un hotel alternativo del output existente

---

## Prompt de Ejecución

```
Actúa como QA lead especializado en validación E2E.

OBJETIVO: Validar que todas las correcciones FASE-F/G/H/I funcionan integradas via v4complete.

CONTEXTO:
- FASE-F: Phantom costs eliminados en proposal generator
- FASE-G: Dual source resuelto + impactos reales conectados
- FASE-H: _identify_brechas cacheado (9x→1x)
- FASE-I: data_structures.py sin duplicados
- Baseline previo: amaziliahotel.com → 6 brechas, coherence 0.84

TAREAS:
1. Pre-flight checks (imports, tests, validations)
2. Ejecutar: python main.py v4complete --url https://amaziliahotel.com
3. Inspeccionar documentos generados vs criterios de aceptación
4. Emitir veredicto: EXITOSO / PERSISTENCIA PARCIAL / FALLIDO
5. Si EXITOSO: release v4.26.0 + documentación completa

CRITERIOS:
- 0 phantom costs en propuesta
- Costos = impacto_real × monthly_loss_max
- Coherence >= 0.80
- 0 regresiones en suite completa

VALIDACIONES:
- pytest tests/ -v --tb=short
- python scripts/run_all_validations.py
- Inspección manual de documentos generados
```
