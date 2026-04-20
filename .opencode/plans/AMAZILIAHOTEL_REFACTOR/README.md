# Plan: Refactorizacion Amaziliahotel v4complete

## Resumen

| Campo | Valor |
|-------|-------|
| **Score inicial** | 16/100 |
| **Score objetivo** | 80/100 |
| **Fases** | 6 fases (8 sesiones: 2A/2B/2C paralelizables) |
| **Duracion estimada** | 9.5 horas (5-8 dias) |
| **Causa raiz** | BookingScraper STUB (83% de bugs) |
| **Hallazgos cubiertos** | 15/15 (100%) |
| **Hallazgos criticos** | 3/3 resueltos |
| **Hallazgos altos** | 5/5 resueltos (A4 ROI corregido, A5 servicios alineados) |
| **Hallazgos medios** | 4/4 resueltos (H7 ELIMINAR, H8 ELIMINAR pipeline, M4 cerrado) |

## Decisiones de Producto (Pre-FASE-5)

| ID | Asset | Decision | Justificacion |
|----|-------|----------|---------------|
| H7 | WhatsApp | **ELIMINAR** | Hotel YA tiene WhatsApp. Claim "No hay boton" es FALSO. Bug `promised_by=["always"]` |
| H8 | Voice Assistant | **ELIMINAR pipeline** | Sin brecha real. Tag `"always_aeo"` genera siempre sin verificacion |
| - | Informe Mensual | **MANTENER, reclasificar** | Servicio incluido legitimo, no fix de brecha |

## Estructura del Plan

```
AMAZILIAHOTEL_REFACTOR/
├── README.md                      # Este archivo
├── dependencias-fases.md          # Diagrama y matriz de dependencias
├── 05-prompt-inicio-sesion-fase-1.md   # FASE-1: BookingScraper
├── 05-prompt-inicio-sesion-fase-2a.md  # FASE-2A: hotel_schema
├── 05-prompt-inicio-sesion-fase-2b.md  # FASE-2B: monthly_report
├── 05-prompt-inicio-sesion-fase-2c.md  # FASE-2C: optimization_guide
├── 05-prompt-inicio-sesion-fase-3.md   # FASE-3: Bugs generadores
├── 05-prompt-inicio-sesion-fase-4.md   # FASE-4: Open Graph
├── 05-prompt-inicio-sesion-fase-5.md   # FASE-5: Decisiones producto + Gates
├── 05-prompt-inicio-sesion-fase-6.md   # FASE-6: Correccion documentos comerciales
├── 06-checklist-implementacion.md      # Checklist maestro
└── 09-documentacion-post-proyecto.md   # Documentacion incremental
```

## Fases (Workflow: phased_project_executor.md)

| # | ID | Descripcion | Dependencias | Bloqueante |
|---|----|-------------|--------------|------------|
| 1 | FASE-1 | BookingScraper Real | Ninguna | SI |
| 2 | FASE-2A | Regenerar hotel_schema | FASE-1 | NO |
| 3 | FASE-2B | Regenerar monthly_report | FASE-1 | NO |
| 4 | FASE-2C | Regenerar optimization_guide | FASE-1 | NO |
| 5 | FASE-3 | Correccion bugs (H3,H4,H10,H12) | FASE-1 | NO |
| 6 | FASE-4 | Generar Open Graph (B4) | FASE-1 | NO |
| 7 | FASE-5 | Decisiones producto + Gates | FASE-1, FASE-3 | NO |
| 8 | FASE-6 | Correccion documentos comerciales | FASE-1, FASE-5 | NO |

**Nota**: FASE-2A/2B/2C son paralelizables (dependen solo de FASE-1, sin overlap de archivos).

## Restriccion de Costo API

**v4complete se ejecuta UNA SOLA VEZ al final del proyecto.**

Ninguna fase previa (FASE-1 a FASE-6) ejecuta v4complete. La validacion en fases intermedias se realiza con:
- Tests unitarios: `./venv/Scripts/python.exe -m pytest`
- Syntax checks: `./venv/Scripts/python.exe -m py_compile`
- Grep verifications: verificacion directa de patrones en codigo

La validacion E2E final se ejecuta DESPUES de FASE-6:
```bash
./venv/Scripts/python.exe main.py v4complete --url https://amaziliahotel.com/ --debug
```
Ver detalle completo en `06-checklist-implementacion.md` seccion "VALIDACION E2E FINAL".

## Para Iniciar Sesion de Fase

1. Leer `05-prompt-inicio-sesion-fase-N.md`
2. Seguir tareas y criterios de aceptacion
3. Al completar, ejecutar `log_phase_completion.py`
4. Actualizar `06-checklist-implementacion.md`

**Fases disponibles**:
- FASE-1: BookingScraper Real (bloqueante)
- FASE-2A: Regenerar hotel_schema
- FASE-2B: Regenerar monthly_report
- FASE-2C: Regenerar optimization_guide
- FASE-3: Correccion bugs generadores
- FASE-4: Generar Open Graph
- FASE-5: Decisiones producto + Gates (WhatsApp ELIMINAR, Voice ELIMINAR pipeline)
- FASE-6: Correccion documentos comerciales (ROI 3X Tier C, servicios alineados)

## Fuente de Datos para Refactorizacion

- **Auditoria forense**: `.opencode/plans/context/AMAZILIAHOTEL_FORENSIC_AUDIT_RESULTS.md`
- **GBP verificado**: Amazilia Hotel Campestre, rating 4.5, reviews 202
- **Phone**: +57 310 4019049
- **Address**: Via Pereira a #Entrada 8 Cafelia, CERRITOS, Pereira, Risaralda
- **WhatsApp**: Hotel YA tiene boton de WhatsApp (573104019049 = GBP phone)
- **Documentos comerciales**: `output/v4_complete/01_DIAGNOSTICO_*.md`, `output/v4_complete/02_PROPUESTA_*.md`

## Correcciones Aplicadas al Plan (2026-04-19)

| Cambio | Razon |
|--------|-------|
| H7 WhatsApp: MANTENER → **ELIMINAR** | Hotel ya tiene WhatsApp. Claim falso en propuesta |
| H8 Voice: MANTENER → **ELIMINAR pipeline** | Sin brecha real. Generacion automatica injustificada |
| A4 ROI: "ajustar" → **3X Tier C / 20X con GA4** | ROI 20X insostenible sin GA4 |
| A5: 2 servicios inventados → **ambos eliminados** | WhatsApp claim falso + Voice sin brecha |
| Informe Mensual: sin decision → **MANTENER reclasificado** | Servicio legitimo, no fix de brecha |
| Nombres archivo: corregidos | Evitar friccion en ejecucion |

---

*Workflow: `.agents/workflows/phased_project_executor.md` v2.4.0*
