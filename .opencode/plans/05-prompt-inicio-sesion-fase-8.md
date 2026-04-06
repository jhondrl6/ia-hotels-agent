# FASE-8: Prueba E2E v4complete en hotelvisperas.com

**ID**: FASE-8
**Objetivo**: Ejecutar v4complete con GEO Flow completo sobre hotelvisperas.com y certificar que todo funciona correctamente
**Dependencias**: FASE-7 (Documentación actualizada)
**Duracion estimada**: 2 horas
**Skill**: systematic-debugging

---

## Contexto

La FASE-7 completó la documentación. Esta es la prueba final E2E para certificar la integración.

### Sitio de Prueba

- **URL**: https://www.hotelvisperas.com/es
- **Hotel**: Hotel Vísperas
- **Ubicación**: Santa Rosa de Cabal, Risaralda
- **Caso esperado**: FOUNDATION o CRITICAL (sitio básico sin optimización GEO)

### Escenario de Prueba

```
Hotelvisperas.com ha sido diagnosticado anteriormente:
- Pérdida mensual: $6.9M COP
- Score Credibilidad Web: 71/100
- GEO baseline: No optimizado

Ahora con GEO Flow integrado:
- GEO Diagnostic debería dar score < 68 (FOUNDATION/CRITICAL)
- Caso operativo: C o D → FULL enrichment
- Sync Contract debería clasificar como "Brecha técnica confirma pérdida"
```

---

## Tareas

### Tarea 1: Ejecutar v4complete con GEO Flow

**Objetivo**: Correr el pipeline completo con GEO

**Comando**:
```bash
python main.py v4complete --url https://www.hotelvisperas.com/es
```

**Criterios de aceptacion**:
- [ ] Pipeline ejecuta sin errores fatales
- [ ] GEO Flow se ejecuta (logs muestran geo_enriched)
- [ ] Output en `/output`

### Tarea 2: Verificar Caso Operativo C/D (FULL enrichment)

**Objetivo**: Confirmar que se activó FULL enrichment

**Archivos esperados** (Caso C/D - FOUNDATION/CRITICAL):
```
output/
    geo_enriched/
        geo_dashboard.md
        geo_badge.md
        geo_report.json
        llms.txt
        hotel_schema_rich.json
        faq_schema.json
        geo_fix_kit.md
        sync_result.json
        asset_responsibility_guide.md
```

**Criterios de aceptacion**:
- [ ] geo_enriched/ existe
- [ ] 7+ archivos generados
- [ ] Contenido válido (no empty, no placeholder)

### Tarea 3: Verificar Sync Contract

**Objetivo**: Confirmar que la sincronización narrativa funciona

**Criterios de aceptacion**:
- [ ] sync_result.json existe
- [ ] Tag: "Brecha técnica confirma pérdida" o similar
- [ ] combination_tag coherente con diagnóstico comercial

### Tarea 4: Verificar Caso Operativo A (MINIMAL) - Test complementario

**Objetivo**: Probar que el sistema también funciona si GEO está bien

**Nota**: Para probar este caso, crear mock con GEO score 90.

**Criterios de aceptacion**:
- [ ] geo_flow puede ejecutarse con mock GEO=90
- [ ] Caso MINIMAL genera solo geo_badge.md
- [ ] No hay errores

### Tarea 5: Verificar que pipeline original funciona

**Objetivo**: Confirmar que los assets CORE no se rompieron

**Criterios de aceptacion**:
- [ ] propuesta.md generada correctamente
- [ ] diagnosis documentos presentes
- [ ] 03_PARA_TU_WEBMASTER/ con assets CORE
- [ ] Coherence score >= 0.8

### Tarea 6: Generar E2E Certification Report

**Objetivo**: Documentar resultados de la prueba

**Criterios de aceptacion**:
- [ ] Documento E2E_CERTIFICATION.md creado
- [ ] Score GEO documentado
- [ ] Archivos generados listados
- [ ] Pipeline original funcionando
- [ ] Sync Contract funcionando
- [ ] Coherence >= 0.8

---

## Tests Obligatorios

| Test | Criterio de Exito |
|------|-------------------|
| v4complete ejecutable | Sin errores fatales |
| FULL enrichment | 7+ archivos en geo_enriched/ |
| Sync Contract | Tag coherente con diagnóstico |
| Pipeline CORE intacto | Assets originales presentes |
| Coherence | >= 0.8 |

**Comando de validacion**:
```bash
python -m pytest tests/ -v --tb=short
python scripts/run_all_validations.py --quick
```

---

## Post-Ejecucion (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. **`.opencode/plans/README.md`**
   - Marcar FASE-8 como ✅ Completada
   - Documentar score GEO obtenido

2. **E2E_CERTIFICATION.md** en `.opencode/plans/`
   - Resultados completos
   - Score GEO
   - Lista de archivos
   - Issues (si hay)

3. **Ejecutar FASE-RELEASE-4.11.0**
```bash
python scripts/log_phase_completion.py \
    --fase FASE-RELEASE-4.11.0 \
    --desc "GEO Enrichment Integration - E2E Certified" \
    --check-manual-docs
```

---

## Criterios de Completitud

- [ ] v4complete ejecuta sin errores
- [ ] FULL enrichment activo (Caso C/D)
- [ ] geo_enriched/ con 7+ archivos
- [ ] Sync Contract con tag coherente
- [ ] Pipeline CORE intacto
- [ ] Coherence >= 0.8
- [ ] E2E_CERTIFICATION.md generado
- [ ] FASE-RELEASE-4.11.0 registrado
