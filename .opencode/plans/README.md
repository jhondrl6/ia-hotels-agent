# Plan de Intervencion Forense - AmaziliaHotel

**Version**: 4.36.0
**Fecha**: 2026-04-26
**Fuente**: Veredicto.md (Hallazgos 2b, 3, 5 + gate_report presence)

## Resumen

Intervencion de 4 hallazgos confirmados del audit forense de AmaziliaHotel:

1. **hotel_schema dual** (ALTO): Asset oficial vacio vs schema rico en geo_enriched. Bridge existe pero no siempre aplica. → **FASE-A**

2. **Comision OTA mal etiquetada** (MEDIO): $2,610,000 (monthly_loss) presentado como "Comision OTA" cuando la real es $5,400,000. → **FASE-B**

3. **open_graph asset roto** (MEDIO): Template no existe, pain_id `no_og_tags` no se dispara. El sistema NUNCA genera OG tags para hoteles que las necesitan. → **FASE-C**

4. **gate_report falsos missing** (MEDIO): Reporta whatsapp_button como "missing" cuando YA existe en sitio. Alignment artificialmente bajo. → **FASE-D**

## Hallazgos descartados

- **whatsapp_button**: Hotel ya lo tiene en sitio. Pipeline lo detecta y SKIPEA correctamente.
- **research.json confidence**: MEDIO, deferir. Problema de calibracion interna.
- **llms.txt duplicado**: BAJO, deferir. Ineficiencia sin impacto al cliente.

## Estructura del Plan

```
.opencode/plans/
├── README.md                                    (este archivo)
├── dependencias-fases.md                        (diagrama + conflictos)
├── 05-prompt-inicio-sesion-fase-A.md            (hotel_schema dual)
├── 05-prompt-inicio-sesion-fase-B.md            (Comision OTA label)
├── 05-prompt-inicio-sesion-fase-C.md            (open_graph asset)
├── 05-prompt-inicio-sesion-fase-D.md            (gate_report presence)
├── 05-prompt-inicio-sesion-fase-RELEASE.md      (cierre + docs)
├── 06-checklist-implementacion.md               (seguimiento)
└── 09-documentacion-post-proyecto.md            (cascada documental)
```

## Fases

| Fase | Descripcion | Archivos Principales | Estado |
|------|-------------|---------------------|--------|
| FASE-A | Unificar hotel_schema | conditional_generator.py, v4_asset_orchestrator.py | Pendiente |
| FASE-B | Corregir label financiero | v4_diagnostic_generator.py, template | Pendiente |
| FASE-C | Reparar open_graph | template (NUEVO), pain_solution_mapper.py | Pendiente |
| FASE-D | gate_report presence | gate_report generator, SitePresenceChecker | Pendiente |
| FASE-RELEASE-4.36.0 | Cierre + documentacion | VERSION.yaml, CHANGELOG, GUIA_TECNICA | Pendiente |

## Dependencias

```
FASE-A ──┐
FASE-B ──┤
FASE-C ──┼──→ FASE-RELEASE-4.36.0
FASE-D ──┘
```

Conflicto bajo: FASE-A y FASE-C tocan conditional_generator.py (ramas distintas).
Recomendacion: orden secuencial A → B → C → D → RELEASE.

## Reglas de Ejecucion

1. **1 fase por sesion** (regla mandatoria del phased_project_executor)
2. **Maximo 60 iteraciones** del agente por fase
3. **FASE-RELEASE** requiere las 4 fases de implementacion completadas
4. **Post-ejecucion obligatoria** al cierre de cada fase

## Progreso

```
[ ] FASE-A: hotel_schema dual
[ ] FASE-B: Comision OTA label
[ ] FASE-C: open_graph asset
[ ] FASE-D: gate_report presence
[ ] FASE-RELEASE-4.36.0: Cierre + docs
```
