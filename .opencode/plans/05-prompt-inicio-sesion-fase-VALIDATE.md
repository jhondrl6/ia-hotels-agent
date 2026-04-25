# FASE-VALIDATE: Prueba v4complete Unica — Amazilia Hotel

**ID**: FASE-VALIDATE
**Objetivo**: Ejecutar UNA sola prueba v4complete para "Amazilia Hotel" (nombre exacto en Google Maps) con URL https://amaziliahotel.com/ para validar que todas las correcciones de FASE-A a FASE-D funcionan en un flujo real.
**Dependencias**: FASE-A, FASE-B, FASE-C, FASE-D completadas y verificadas
**Duracion estimada**: 1 - 1.5 horas (depende de latencia APIs)
**Skill**: iah-cli-v4complete-flow-validation, dogfood

---

## Contexto

Esta es la UNICA ejecucion v4complete del proyecto. Su proposito es validar end-to-end que los fixes aplicados en fases anteriores producen una propuesta comercial sin los bugs identificados. Se ejecuta una sola vez para optimizar costos API.

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-A | Completada |
| FASE-B | Completada |
| FASE-C | Completada |
| FASE-D | Completada |

### Base Tecnica Disponible
- Comando: `python main.py v4complete --url https://amaziliahotel.com/`
- Hotel: Amazilia Hotel (como aparece en panel Google Maps, NO "amaziliahotel")
- URL: https://amaziliahotel.com/

---

## Tareas

### Tarea 1: Ejecutar v4complete
**Objetivo**: Generar diagnostico y propuesta completos para Amazilia Hotel.

**Comando exacto**:
```bash
venv/Scripts/python.exe main.py v4complete --url https://amaziliahotel.com/
```

**Criterios de aceptacion**:
- [ ] El comando ejecuta sin errores criticos (errores de API momentaneos son aceptables si se reintentan)
- [ ] Se generan archivos en `output/v4_complete/` incluyendo:
  - `01_DIAGNOSTICO_COMPLETO_*.md`
  - `02_PROPUESTA_COMERCIAL_*.md`
  - `financial_scenarios.json`
- [ ] Tiempo total de ejecucion registrado

### Tarea 2: Verificar ausencia de bugs corregidos
**Objetivo**: Confirmar que los fixes de fases anteriores impactaron el output real.

**Archivos a revisar**: `output/v4_complete/02_PROPUESTA_COMERCIAL_*.md`, `output/v4_complete/financial_scenarios.json`

**Checklist de verificacion**:
- [ ] **BUG-1 (seccion vacia)**: "Esto es lo que hacemos por usted" contiene tabla con servicios (no vacia)
- [ ] **BUG-2 (escenarios invertidos)**: financial_scenarios.json tiene conservative <= realistic <= optimistic
- [ ] **BUG-3 (ROI irreal)**: ROI en propuesta <= 5.0X (no 20X)
- [ ] **BUG-4 (tabla errores)**: Ningun entregable dice "No generado" o "Requiere datos" al cliente
- [ ] **BUG-5 (template V6)**: La propuesta usa secciones del template V6 (si fue creado en FASE-C)
- [ ] **BUG-8 (ortografia)**: No hay errores ortograficos conocidos (hotels, brillen, prover, Absorption, protecion)
- [ ] **D-1 (AEO)**: Si ao_score era bajo, aparece entregable de "Optimizacion para IA Generativa"
- [ ] **D-3 (ADR disclaimer)**: Si ADR es estimado, aparece disclaimer visible
- [ ] **D-4 (timeline)**: Plan de 7 dias es realista (no promete todo en 7 dias)
- [ ] **D-7 (entregables)**: 0 items dicen "No generado" al cliente

### Tarea 3: Documentar resultado
**Objetivo**: Crear evidencia de la validacion para decision go/no-go.

**Archivos afectados**:
- `.opencode/plans/evidence/fase-VALIDATE/` (crear directorio)

**Criterios de aceptacion**:
- [ ] Copiar `02_PROPUESTA_COMERCIAL_*.md` a `evidence/fase-VALIDATE/`
- [ ] Copiar `financial_scenarios.json` a `evidence/fase-VALIDATE/`
- [ ] Crear `evidence/fase-VALIDATE/validacion_checklist.md` con resultado de cada verificacion (PASS/FAIL)
- [ ] Si algun item FALLA, documentar el fallo y evaluar si requiere hotfix o fase adicional

---

## Tests Obligatorios

Esta fase NO tiene tests automatizados nuevos. La validacion es manual contra el checklist de Tarea 2.

**Comando de validacion previo** (antes de ejecutar v4complete):
```bash
venv/Scripts/python.exe scripts/run_all_validations.py --quick
venv/Scripts/python.exe -m pytest tests/commercial_documents/ tests/financial_engine/ tests/delivery/ -v --tb=short
```

**Resultado esperado**: 0 regresiones, 4/4 validaciones PASS.

---

## Post-Ejecucion (OBLIGATORIO)

1. **`.opencode/plans/06-checklist-implementacion.md`** -> Marcar FASE-VALIDATE completada
2. **`09-documentacion-post-proyecto.md`** -> Seccion D: Resultado de validacion v4complete; Seccion E: Archivos de evidencia
3. **REGISTRY.md**:
```bash
venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-VALIDATE --desc "Prueba v4complete unica Amazilia Hotel - validacion end-to-end post-intervencion" --archivos-nuevos "evidence/fase-VALIDATE/validacion_checklist.md" --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] v4complete ejecuto exitosamente para https://amaziliahotel.com/
- [ ] Todos los items de verificacion de Tarea 2 evaluados (PASS/FALLA documentado)
- [ ] Evidencia preservada en `evidence/fase-VALIDATE/`
- [ ] Validaciones previas pasan: 0 regresiones, 4/4 checks
- [ ] `06-checklist-implementacion.md` actualizado
- [ ] REGISTRY.md actualizado
- [ ] Post-ejecucion completada

---

## Restricciones

- **UNICA ejecucion v4complete permitida** en todo el proyecto (optimizacion costos API)
- Si v4complete falla por error de red/API, reintentar MAX 2 veces. Si falla por bug de codigo, documentar y abortar (requiere hotfix, NO nueva ejecucion v4complete)
- NO modificar codigo durante esta fase (solo observar y documentar)
- Windows/WSL: usar `venv/Scripts/python.exe`
