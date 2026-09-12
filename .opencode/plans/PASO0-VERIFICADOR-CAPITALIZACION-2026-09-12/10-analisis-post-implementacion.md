# 10 — Análisis Post-Implementación: PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12

> **Creado desde la concepción** (executor §4, v2.11.0 en adelante): este archivo existía antes de la
> primera fase para que las lecciones no se escriban de memoria cuando ya se perdieron.
> **Advertencia de formato**: el check de cierre de planes (`[5/6]` del hook hoy, `[5/7]` tras la
> renumeración de FASE-V2, script `validate_plan_closure.py`) prohíbe que una **cabecera** de cierre
> afirme el cierre por completo mientras quede alguna fila `⬜ Pendiente` en el Resumen de Ejecución (§1).
> Al cerrar: actualizar §1 primero, y solo después titular la sección de cierre.

## 1. Resumen de Ejecución

| Fase | Fecha | Estado | Tests nuevos | Regresiones | Nota |
|------|-------|--------|--------------|-------------|------|
| Paso 0 | 2026-09-12 | ✅ | n/a | n/a | 10 consultas, 18 lecciones capitalizadas, 6 descartes, 5 hallazgos sin efecto |
| FASE-V1 | 2026-09-12 | ✅ | 0 | 0 | Q1–Q5 decididas con medición; contrato C0–C8 |
| FASE-V2 | ⬜ | ⬜ Pendiente | ⬜ | ⬜ | script + tests + NR7 + cableado |
| FASE-V3 | ⬜ | ⬜ Pendiente | 0 | ⬜ | cierre documental y archivado |

## 2. Lecciones Aprendidas nuevas

Formato obligatorio: qué pasó / por qué / qué lo previene / pertinencia (INCLUIR o EXCLUIR).

| ID | Enunciado | Qué pasó | Por qué | Qué lo previene | Pertinencia |
|----|-----------|----------|---------|-----------------|-------------|
| ⬜ (rellena al cierre de V2 y V3) | | | | | |

## 3. Matriz de verificación de ACs

| AC | Criterio (resumen) | Artefacto y clave | Estado | Cómo se leyó |
|----|--------------------|-------------------|--------|--------------|
| AC-A1…AC-A5 | decisiones Q1–Q5 | `evidence/FASE-V1/decision-verificador.md` | ✅ | lectura de las secciones `## Q1`…`## Q5` |
| AC-B1…AC-B5 | script, tests, NR7, cableado, cobertura | `evidence/FASE-V2/` | ⬜ | — |
| AC-C1, AC-C2 | docs sin fósiles y deuda cerrada | `git diff` de V3 + checklist del predecesor | ⬜ | — |

## 4. Métricas de Ejecución

- Población a la que aplica el verificador: `—`
- Cobertura publicada por el script en su salida: `—`
- Funciones de test canónicas pre / post: `—` / `—` (par en `evidence/FASE-V2/baseline-pre-post.md`)

## 5. Seguimientos abiertos detectados

Ver `06-checklist-implementacion.md` §Deuda: D-V2.1 (instrumento de R2.1 fuera de esta máquina),
promoción a R2.11, verificador de conteos declarados en §4, prompts de fase vs §2 del `00-`, y migración
del `[7/7]` si se activa la Opción 2 del pre-commit.

## 6. Decisiones Arquitectónicas

| ID | Decisión | Alternativas rechazadas y por qué |
|----|----------|-----------------------------------|
| ⬜ (rellena al cierre de V3) | | |
