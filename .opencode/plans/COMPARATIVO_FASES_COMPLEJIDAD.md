# Comparativo de Fases — Complejidad Técnica
## Auditoría M6: Hotel Schema Divergence (Termales Santa Rosa de Cabal)

> Generado: 2026-05-09  
> Base: .opencode/plans/00-plan-hotelschema-refactor.md  
> Método: Análisis por 7 dimensiones de complejidad (escala 1-5)

---

## Matriz de Complejidad

| Dimensión | FASE-12A | FASE-12A-VERIFY | FASE-12B | FASE-12C | FASE-RELEASE |
|-----------|:--------:|:---------------:|:--------:|:--------:|:------------:|
| **Código a modificar** | 2 | 1 | 4 | 3 | 0 |
| **Riesgo de regresión** | 2 | 2 | 4 | 3 | 1 |
| **Dependencias cruzadas** | 1 | 1 | 4 | 3 | 2 |
| **Complejidad de testing** | 2 | 2 | 5 | 3 | 1 |
| **Impacto en pipeline** | 2 | 3 | 5 | 3 | 1 |
| **Comprensión conceptual** | 2 | 2 | 5 | 3 | 2 |
| **Esfuerzo estimado (iter.)** | 12 | 8 | 25 | 20 | 18 |

> Escala: 1=Mínimo → 5=Máximo

---

## Desglose por Fase

### FASE-12A — Fix causa raíz (Complejidad: ★★☆☆☆)

**Archivo objetivo**: `modules/asset_generation/site_presence_checker.py`

| Aspecto | Detalle |
|---------|---------|
| Líneas a cambiar | 1 línea (L365) |
| Archivos nuevos | 1 (`tests/test_site_presence_checker.py`) |
| Alcance del cambio | Local — solo afecta la lista `target_types` en `_check_schema_exists` |
| Testing necesario | 5 casos unitarios simples (mock de dict, assert `found`/`not found`) |
| Riesgo | Bajo — cambio aislado, sin efectos colaterales en otros módulos |
| ¿Requiere entender cross-system? | No — solo un módulo |

**Justificación de baja complejidad**: Es un cambio cosmético en una lista. El único riesgo es que alguien espere que Organization/LocalBusiness aún cuenten como Hotel, pero eso es precisamente el bug que se corrige.

---

### FASE-12A-VERIFY — Verificación con v4complete (Complejidad: ★☆☆☆☆)

**Archivo objetivo**: Ninguno (solo ejecución y verificación)

| Aspecto | Detalle |
|---------|---------|
| Líneas a cambiar | 0 |
| Acción principal | Ejecutar `v4complete` (~5-10 min) |
| Verificación | Leer `asset_generation_report.json` y confirmar `hotel_schema` ≠ SKIPPED |
| Riesgo | Mínimo — solo observación |
| Dependencia | Requiere FASE-12A completada |

**Justificación**: Es una fase de verificación pura. La complejidad está en el tiempo de espera, no en el análisis.

---

### FASE-12B — Coherence gate audit↔presence (Complejidad: ★★★★★) ⚠️ MÁXIMA

**Archivo objetivo**: `modules/asset_generation/proposal_asset_alignment.py`

| Aspecto | Detalle |
|---------|---------|
| Líneas a cambiar | ~15-20 líneas nuevas en `verify_proposal_asset_alignment()` |
| Archivos nuevos | 1 (`tests/test_proposal_asset_alignment.py`) |
| Alcance del cambio | Core del gate de alineación — cruza datos de 2 sistemas (audit + presence) |
| Testing necesario | Muy alto — requiere mockear `assessment` con `audit_report` y `site_presence_report` simultáneamente |
| Riesgo | Alto — si el check es incorrecto, puede bloquear entregas válidas o dejar pasar divergencias |
| ¿Requiere entender cross-system? | **Sí** — obliga a dominar: audit path (`rich_results_client`), presence path (`SitePresenceChecker`), y el gate (`proposal_asset_alignment`) |

**¿Por qué es la más compleja?**

1. **Cruce de sistemas**: Por primera vez se conectan explícitamente dos pipelines que hasta ahora eran independientes: el audit score (`rich_results_client.py`) y el presence check (`site_presence_checker.py`). Esto requiere entender cómo fluyen los datos entre ambos.

2. **Nuevo estado `divergent`**: Hay que agregar un valor que no existía en `presence_status`. Esto afecta:
   - El dataclass `ServiceAlignment` (type hint)
   - `AlignmentReport.to_dict()` (serialización)
   - Cualquier consumidor de `presence_status` que haga match exacto (switch/if-else)

3. **Mocking complejo**: Los tests deben simular simultáneamente:
   - Un `assessment` con `audit_report.schema.hotel_schema_detected = false`
   - Un `site_presence_report` con `hotel_schema.status = "exists"`
   - Verificar que el resultado es `divergent` y no `present_in_production`

4. **Riesgo asimétrico**: Un falso positivo (marcar divergent cuando no lo es) bloquea entregas válidas. Un falso negativo (no detectar divergencia) deja pasar el bug original. El margen de error es estrecho.

5. **Impacto en pipeline**: Este check se ejecuta en el gate `proposal_asset_alignment` (Gate 9), que es el último checkpoint antes de la publicación. Un error aquí afecta directamente la aprobación de la propuesta comercial.

**Plan de mitigación de riesgo**:
- Escribir tests ANTES de aplicar el change
- Validar con el output real de `v4complete` (FASE-12A-VERIFY) como fixture
- Hacer dry-run con `--dry-run` si el flag existe

---

### FASE-12C — Separación de servicios (Complejidad: ★★★☆☆)

**Archivo objetivo**: `proposal_asset_alignment.py` + `pain_solution_mapper.py`

| Aspecto | Detalle |
|---------|---------|
| Líneas a cambiar | ~10-15 (añadir entrada a dict + ajustar mapper) |
| Archivos nuevos | Tests (~3-5 casos) |
| Alcance del cambio | Mapeo comercial — cambia la presentación al cliente, no la lógica de detección |
| Riesgo | Medio — puede romper templates de propuesta |
| ¿Requiere entender cross-system? | Parcialmente — hay que conocer `pain_solution_mapper` |

**Complejidad intermedia**: Toca la interfaz comercial, no el motor de detección. El riesgo es que la propuesta muestre datos incorrectos al cliente, pero no afecta la generación de assets.

---

### FASE-RELEASE — Documentación y cierre (Complejidad: ★★☆☆☆)

| Aspecto | Detalle |
|---------|---------|
| Código a modificar | 0 (solo documentación) |
| Acciones | log_phase_completion, sync_versions, CHANGELOG, GUIA_TECNICA, v4complete final, run_all_validations |
| Riesgo | Bajo — tareas mecánicas |
| Dependencia | Todas las fases previas completadas |
| Dificultad | Baja ejecución, pero requiere rigor en el formato |

**Complejidad baja en lo técnico, alta en lo procedural**: Hay que seguir exactamente el protocolo de documentación del workflow `phased_project_executor.md` §4.5.

---

## Ranking por Complejidad Técnica

| Rank | Fase | Score | Razón principal |
|------|------|:-----:|-----------------|
| **1** | **FASE-12B** | **24/25** | Cross-system + nuevo estado + testing complejo + impacto gate |
| 2 | FASE-12C | 16/25 | Múltiples archivos comerciales + tests |
| 3 | FASE-RELEASE | 14/25 | Procedural, mucho protocolo |
| 4 | FASE-12A | 12/25 | Cambio puntual + tests simples |
| 5 | FASE-12A-VERIFY | 7/25 | Observación pura |

---

## Recomendación de Ejecución

```
Sesión 1 → FASE-12A       (código + tests)
Sesión 2 → FASE-12A-VERIFY (v4complete + evidencia)
Sesión 3 → FASE-12B       (coherence check + tests + v4complete)
Sesión 4 → FASE-12C       (separación servicios, si aplica)
Sesión 5 → FASE-RELEASE   (documentación + validación final)
```

**¿Por qué FASE-12B debería ir en Sesión 3 y no en Sesión 2?**
Porque depende funcionalmente de FASE-12A: si el fix de la línea 365 no funciona, el check de divergencia de FASE-12B nunca se disparará. Mejor verificar primero que el fix base resuelve el problema, y luego agregar la capa de coherencia.

---

## Métricas Comparativas Resumidas

| Métrica | 12A | Verify | 12B | 12C | Release |
|---------|:---:|:------:|:---:|:---:|:-------:|
| Archivos a modificar | 1 | 0 | 1 | 2-3 | 0 |
| Archivos nuevos (tests) | 1 | 0 | 1 | 0 | 0 |
| v4complete requeridos | 0 | 1 | 1 | 0-1 | 1 |
| Iteraciones estimadas | 12 | 8 | 25 | 20 | 18 |
| **Total** | **55-70 iters** | | | | |

> Dentro del límite de 60 iteraciones/sesión. FASE-12B con su v4complete encaja justo en el límite superior (25 + overhead ~30 = 55).