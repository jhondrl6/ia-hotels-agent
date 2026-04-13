# Documentación Post-Proyecto — ELIMINAR-SCORE-GLOBAL-TABLA-DIAGNOSTICO

**Proyecto:** Eliminar fila "Visibilidad Digital (Global)" de tabla de diagnóstico
**Fecha:** 2026-04-12
**Fases completadas:** FASE-1

---

## Sección A: Resumen Ejecutivo

**Objetivo alcanzado:** Eliminar la fila redundante "Visibilidad Digital (Global)" de la tabla de diagnóstico del cliente, manteniendo el cálculo interno de `score_global` para la propuesta comercial.

**Impacto:**
- Mejora la claridad del diagnóstico para el cliente (4 pilares vs. 5 filas)
- Elimina dato sin benchmark regional (fila Global mostraba `- | -`)
- Refuerza la arquitectura de 4 pilares diferenciados

---

## Sección B: Módulos Nuevos

**No aplica** — No se crearon módulos nuevos en este proyecto.

---

## Sección C: Módulos Modificados

| Módulo | Cambio realizado |
|--------|-----------------|
| `templates/diagnostico_v6_template.md` | Eliminada línea 56 (fila "Visibilidad Digital (Global)") |
| `v4_diagnostic_generator.py` | Eliminada línea 626 (`score_global_status` — dead code). Corregido docstring en `calcular_cumplimiento()` |

---

## Sección D: Métricas Acumulativas

| Métrica | Antes | Después |
|---------|-------|---------|
| Filas en tabla de diagnóstico | 5 | 4 |
| Variables dead code eliminadas | 0 | 1 (`score_global_status`) |
| Tests con regresión | — | 0 |
| Archivos modificados | — | 2 |

---

## Sección E: Archivos Afiliados Actualizados

**Completado 2026-04-12**

- [x] REGISTRY.md — entrada FASE-1 registrada via log_phase_completion.py (duplicado eliminado)
- [x] CHANGELOG.md — sección "Post-FASE-1: Eliminar Score Global de Tabla Diagnóstico" agregada bajo [4.28.0]
- [x] GUIA_TECNICA.md — NO APLICA (archivo no existe en repo; lección aprendida L3)

---

## Sección F: Decisiones de Diseño Documentadas

**Decisión 1:** `score_global` se mantiene como cálculo interno
- **Razón:** Usado por `v4_proposal_generator.py` como `score_tecnico` para determinar el paquete recomendado (básico/avanzado/premium)
- **Alternativa descartada:** Eliminar completamente `score_global` — No viable porque rompería la recomendación de paquete

**Decisión 2:** `score_global_status` eliminado
- **Razón:** Nunca fue referenciado en ningún template ni en código posterior — pure dead code
- **Verificación:** Grep confirma 0 referencias externas a la variable

---

## Sección G: Lecciones Aprendidas

**L1: Dead code con dependencia indirecta es riesgoso**
- `score_global_status` parecía dead code simple pero `score_global` SÍ se usa en `v4_proposal_generator.py`. Verificar siempre grep antes de eliminar variables que comparten prefijo.

**L2: Cambios "simples" requieren trazabilidad completa**
- Eliminar 1 línea de template + 1 variable suena trivial, pero el plan post-proyecto exigió 6 herramientas/archivos diferentes. No saltar el proceso por aparentar simplicidad.

**L3: GUIA_TECNICA.md no existe como archivo**
- El plan asume su existencia pero no está en el repo. Referencia obsoleta que debe actualizarse en CONTRIBUTING.md o crearse si realmente se necesita.

---

## Sección H: Artefactos de Verificación

**Logs de tests:**
```
tests/commercial_documents/test_iao_score.py — PASA (0 regresión)
tests/commercial_documents/ -k "diagnostic" — PASA
```

**Grep de verificación:**
```
grep "Visibilidad Digital" templates/diagnostico_v6_template.md → 0 resultados
grep "score_global_status" v4_diagnostic_generator.py → 0 resultados
```
