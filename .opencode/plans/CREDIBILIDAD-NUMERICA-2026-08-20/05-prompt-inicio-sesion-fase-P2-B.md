# FASE-P2-B: Pre-carga GBP de Prospectos (F9) + Higiene Documental Comercial (F10)

**ID**: CREDIBILIDAD-NUMERICA-2026-08-20 / FASE-P2-B
**Objetivo**: Crear el script de pre-carga GBP batch de prospectos con gate de completitud de
datos de contacto (F9), y actualizar la documentación comercial desactualizada (F10).
**Dependencias**: FASE-P0-A ✅ (pricing unificado — las docs de pricing deben citar la fuente única)
**Duración estimada**: 1 sesión (≤60 iteraciones)
**Skill**: `phased_project_executor.md` (ejecución DIRECTA)

## Modo de Ejecución

**DIRECTO con el agente principal.** El script usa módulos del proyecto (scrapers, Places API),
por lo que requiere el venv del proyecto — no delegar a subagentes WSL (regla venv).

## Contexto

CONTEXT fallos **F9** y **F10**:
- **F9** (🟡 ALTA): lista de 30 prospectos tiene 66 menciones "Pendiente verificar" y solo
  1 teléfono real. Contactar requiere verificación manual previa de datos. Causa raíz: compilación
  manual sin gate de completitud de datos de contacto. Bloquea el plan de prospección semana 3-4.
  **Fix P2**: pre-carga GBP de prospectos (scrape batch antes de contactar) + gate de completitud.
- **F10** (🟢 MEDIA): `PROPUESTA_EMPAQUETADO_NO_TECNICO.md` describe un ZIP caótico antiguo que ya
  no existe; ejemplos con ADR $200K. Docs comerciales no versionadas junto al código que describen.
  **Fix P2**: higiene documental comercial — actualizar docs que citan pricing/benchmarks/ZIP.

**Nota de alcance**: esta fase CREA el script de pre-carga y actualiza las docs. La EJECUCIÓN
batch real sobre los 30 prospectos es operativa (post-plan) y queda fuera de alcance — se documenta
como seguimiento.

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-P0-A/B/C | ✅ Completadas |
| FASE-P1-A/B/C/D | ✅ Completadas |
| FASE-P2-A | ✅ Completada |

### Base Técnica Disponible
- `modules/scrapers/` (scrapers GBP/Places existentes)
- `modules/auditors/` (Places API client)
- `evidence/Ingresos/01_Lista_Prospectos_Eje_Cafetero.md` (lista a pre-cargar)
- `docs/PRECIOS_PAQUETES.md`, `evidence/Recomendaciones/PROPUESTA_EMPAQUETADO_NO_TECNICO.md` (docs a higienizar)
- Fuente única de pricing (FASE-P0-A) y benchmark maestro (FASE-P1-A)

## Tareas

### T1: Script de pre-carga GBP batch con gate de completitud (F9)
**Objetivo**: script reutilizable que toma una lista de prospectos (URL o nombre+ciudad), ejecuta
la pre-carga GBP/Places, y produce un reporte con gate de completitud (marca "listo para contactar"
solo si tiene teléfono + dirección + categoría verificadas).
**Archivos afectados**:
- `scripts/preload_prospects_gbp.py` (nuevo, usa módulos del proyecto vía venv)
**Criterios de aceptación**:
- [ ] Script lee lista de prospectos (formato simple: YAML o CSV)
- [ ] Ejecuta pre-carga GBP/Places por prospecto
- [ ] Produce reporte con estado de completitud por prospecto (teléfono/dirección/categoría)
- [ ] Marca explícitamente los campos "Pendiente verificar"
- [ ] Modo `--dry-run` para probar sin ejecutar scrapers

### T2: Higiene documental comercial (F10)
**Objetivo**: actualizar las docs comerciales para que citen la fuente única de pricing (P0-A)
y el benchmark maestro (P1-A), y describan el ZIP actual (53 archivos, bien estructurado).
**Archivos afectados**:
- `docs/PRECIOS_PAQUETES.md`
- `evidence/Recomendaciones/PROPUESTA_EMPAQUETADO_NO_TECNICO.md`
- Cualquier doc que cite ADR $200K o pricing contradictorio (buscar con grep)
**Criterios de aceptación**:
- [ ] Docs de pricing citan `config/pricing.yaml` como fuente única (sin cifras hardcodeadas divergentes)
- [ ] Docs de benchmarks citan el benchmark maestro de FASE-P1-A (sin ADR $200K obsoleto)
- [ ] Docs de empaquetado describen el ZIP actual (README_DELIVERY, MANIFEST, IMPLEMENTATION_ORDER)
- [ ] Sin cifras de pricing/benchmark contradictorias entre docs

### T3: Tests / verificación
**Criterios de aceptación**:
- [ ] Script `preload_prospects_gbp.py --dry-run` ejecuta sin error
- [ ] Si hay tests de scrapers/places, pasan sin fallos NUEVOS (capturar baseline de tests/scrapers ANTES de cambiar — esa suite NO está en la línea base §6)
- [ ] `run_all_validations.py --quick` pasa

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| Script dry-run | `scripts/preload_prospects_gbp.py --dry-run` | Sale sin error |
| Regresión scrapers | `pytest tests/scrapers/ -v` (si aplica) | 0 fallos NUEVOS (baseline propia de la fase; scrapers no está en §6) |

**Comando de validación**:
```powershell
.\venv\Scripts\python.exe scripts/preload_prospects_gbp.py --dry-run
.\venv\Scripts\python.exe scripts/run_all_validations.py --quick
```

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. `dependencias-fases.md` y `06-checklist-implementacion.md`: marcar FASE-P2-B ✅.
2. `README.md` del plan: actualizar tabla de progreso.
3. `09-documentacion-post-proyecto.md`: secciones A/B/D/E.
4. `10-analisis-post-implementacion.md`: fila de ejecución + mínimo 3 lecciones + **seguimiento abierto** (ejecución batch operativa post-plan).
5. **Registrar la fase**:
```powershell
.\venv\Scripts\python.exe scripts/log_phase_completion.py --fase FASE-P2-B --desc "Pre-carga GBP prospectos (F9) + higiene docs comerciales (F10)" --archivos-nuevos "scripts/preload_prospects_gbp.py" --archivos-mod "docs/PRECIOS_PAQUETES.md,evidence/Recomendaciones/PROPUESTA_EMPAQUETADO_NO_TECNICO.md" --tests "<N>" --check-manual-docs
```
6. Editar CHANGELOG.md y GUIA_TECNICA.md (template §6).

## Criterios de Completitud (CHECKLIST)

- [ ] Script `preload_prospects_gbp.py` funcional (dry-run OK)
- [ ] Docs comerciales sin cifras contradictorias de pricing/benchmark
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] Post-ejecución completada

## Restricciones

- Máximo 60 iteraciones.
- NO ejecutar la pre-carga batch real sobre los 30 prospectos (operativo, post-plan).
- NO contactar prospectos.
- NO ejecutar v4complete.
