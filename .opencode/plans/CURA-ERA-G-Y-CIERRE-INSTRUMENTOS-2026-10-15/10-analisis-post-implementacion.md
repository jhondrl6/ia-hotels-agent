# Análisis Post-Implementación — CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15

> Creado desde la concepción del plan (executor v2.15.0): se actualiza al cierre de cada fase, no al final.

## Resumen de Ejecución (llenar al cierre de cada fase)

| Fase | Estado | Notas |
|------|--------|-------|
| FASE-A — Cierre documental | ⬜ Pendiente | |
| FASE-B — Censo era-G + decisión | ⬜ Pendiente | |
| FASE-C — Cura era-G | ⬜ Pendiente | |
| FASE-RELEASE-4.81.1 | ⬜ Pendiente | |

## Matriz de Verificación de Hallazgos (llenar por fase)

| AC | Enunciado (resumen) | Fase | Estado | Artefacto donde se lee |
|----|---------------------|------|--------|------------------------|
| AC1 | Rutas del registro `D-QW` versionadas y empujadas; índice `--check` verde en el árbol del commit | FASE-A | ⬜ | `git show` del commit + crudos |
| AC2 | Crudos de la tanda persistidos bajo evidencia con shas en el acta | FASE-A | ⬜ | `FASE-A/acta-cierre-documental.md` |
| AC3 | Censo era-G por fuente con causa de falta de contabilidad y cruce de poblaciones | FASE-B | ⬜ | `FASE-B/censo-era-g.md` |
| AC4 | Decisión escrita del Operador por fuente + mecanismo con coste | FASE-B | ⬜ | Tabla de decisión en el informe |
| AC5 | Writer sin `[DUPLICADO-VIGENTE]` y con 0 huéspedes; par rojo/verde | FASE-C | ⬜ | Crudos de FASE-B y FASE-C |
| AC6 | Delta R2.3 por fase de código; `--quick` verde por fase | A/B/C | ⬜ | Pares en `FASE-*/` |
| AC7 | 4.81.1 sincronizada, CHANGELOG de las tres curas, nota de ronda, DOMAIN_PRIMER verificado | RELEASE | ⬜ | CHANGELOG + cobertura-historia + árbol archivado |

## Lecciones Aprendidas (llenar al cierre de cada fase)

### Lecciones capitalizadas de planes anteriores (espejo de `00-lecciones-capitalizadas.md` §2)

| ID | Qué cambia | Real (al cerrar) |
|----|------------|------------------|
| Lección `L-SECF.2` | Commit por pathspec con add nominal y conteo del índice (T2 de FASE-A) | (se anota al cerrar) |
| Deuda `D-QW-1` | El censo declara si alguna fuente viene de la rama que no registra (T1 de FASE-B) | (se anota al cerrar) |
| Deuda `D-QW-2` | El censo declara con qué predicado midió (T1 de FASE-B) | (se anota al cerrar) |
| Lección `L-QW.2` | La marca se escribe en el registro, no se borra del notebook (T1 de FASE-C) | (se anota al cerrar) |
| Lección `L-CST-6` | El mecanismo no se promete sin medirlo (restricciones de B y C) | (se anota al cerrar) |
| Lección `L-V.2` | El verde de AC5 es la corrida real, no el diff (T2 de FASE-C) | (se anota al cerrar) |
| Deuda `D-V2.1` | Presupuestos auto-reportados en `tool calls` | (se anota al cerrar) |

### Lecciones nuevas de este plan (L-… si las hay; «sin lecciones nuevas» es un resultado válido)

(se llena al cerrar las fases)

## Seguimientos abiertos

| Tema | Estado | Dueño | Acción futura |
|------|--------|-------|---------------|
| `D-QW-1` / `D-QW-2` — rama por defecto del writer y detector divergente | Diferida en el maestro §5 | Operador | Fase propia (o absorción en FASE-C si el censo la toca) |
| `S-CIM-1` — `[18/18]` sin `--strict` | Diferida | Operador | AC propia |
| `S-CST-1` — gate `hard_contradictions` sin productor | Diferida | Operador | Fase propia |
| `P6.5` — el acta niega al revisor que corrió | Diferida | Operador | Decisión de cláusula registrada en CURA |
| Anotaciones «sin commit» de 4.81.0 que el push venció | Diferida | Operador | Sello datado con `2e048e6`/`1f95e84` o addendum en `evidence/` |

## Métricas de Ejecución (referencia, no copia)

- Por fase: ver `09-documentacion-post-proyecto.md` §D y los crudos en `evidence/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/FASE-*/`.
- El conteo canónico de tests lo imprime `grep -rE "^\s*def test_" tests --include=*.py | wc -l`; la cifra commiteada, `git grep -c -E "^\s*def test_" HEAD -- tests`.

## Decisiones Arquitectónicas

| ID | Decisión | Rationale | Alternativas rechazadas |
|----|----------|-----------|-------------------------|
| DEC-1 | 4.81.1 cubre las tres curas en una sola unidad de versión | Decisión del Operador (2026-10-15) al elegir el plan consolidado: una entrada de CHANGELOG y una nota de ronda por los 9 tests | Dos releases (prompt documental con 4.81.1 ya + plan aparte para era-G) — coste: dos bumps y la segunda vía esperando igual |
| DEC-4 | Borrar del notebook es decisión escrita del Operador, por fuente | Irreversible sobre contenido publicado; el writer solo marca | Borrar en bloque al medir el censo — rechazada por irreversible y sin autorización por fuente |

## Checklist de Cierre (llenar en FASE-RELEASE)

- [ ] `10-analisis` completo (matriz, lecciones, seguimientos, decisiones) antes del write-back
- [ ] Write-back `--upload` retorna 0 y `--strict` confirma la ingesta
- [ ] Orden R2.5/R2.10: write-back → índice → `git mv` → índice
- [ ] Lecciones con pertinencia INCLUIR persistidas en la memoria del proyecto
- [ ] Registro de release ejecutado; cinco cortes declarados
