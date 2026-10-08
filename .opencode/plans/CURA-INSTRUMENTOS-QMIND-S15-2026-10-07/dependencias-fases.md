# Dependencias y conflictos de fases — CURA-INSTRUMENTOS-QMIND-S15 (2026-10-07)

## Grafo

```
Preparacion (FASE-0)  ✅ 2026-10-08 · commit b536748 · empujado 98c190e..b536748 · L3 sin hallazgos
      |
      v
FASE-A1  AC1 sha_cuerpo + AC2 puerta cuerpo-contra-cuerpo
      |                      \
      v                       \  (dependencia dura: el bloque DUPLICADO-VIGENTE
FASE-A2  AC3 slug + AC4 id        no se evalua mientras la puerta corte VENCIDO)
      |                             \
      v                              v
FASE-A3  AC5 ruta archivada + AC6 era G
      |
      v
FASE-B   AC7 diagnostico medido + AC8 cura con diente intacto
      |
      +--> (si AC7 abre la fila) FASE-C  AC9 cura en el generador
      |                                  (4 + 16 + 36 funciones hermanas)
      v
FASE-RELEASE  AC10 write-back propio + docs + archivado R2.10
```

**Reglas del grafo, leídas del código y no supuestas:**

- A1 → A2 → A3 son **secuenciales por conflicto de archivo**, no por conveniencia: las tres editan
  `scripts/validate_qmind_writeback.py`, dos de ellas (`A1`, `A2`) la misma función `registrar_publicacion()`, y las
  tres suman dientes en `tests/test_validate_qmind_writeback_escritura.py`.
- **A3 depende duramente de A1** (no de A2): con el guard viejo, `verificar_contenido()` sale por `continue` antes
  de evaluar los huéspedes, así que AC6 **no es evaluable** sin la puerta nueva. Medido por flujo de control en la
  preparación (maestro §1 fila 5).
- **B es independiente de A** en código (otra superficie: `scripts/build_lesson_index.py` y su test), pero **va
  después**: las dos familias regeneran el par `.opencode/LECCIONES-INDEX.md` + `.opencode/lecciones_index.json`, y
  el índice es derivado de *todo* `.md` que nombre un ID. Ejecutarlas en paralelo produce rojos ajenos en `[6/8]`.
- **C es condicional y no es de relleno:** si B gobierna la divergencia desde el fixture, C se declara «no aplica» y
  el plan cierra sin ella.
- **RELEASE requiere A1, A2, A3 y B** (y C si se abrió). **FASE-VERIFY no aplica** (executor §4.6, criterio 2:
  cero ejecuciones E2E en este plan; ver maestro §3).

## Tabla de conflictos por archivo

| Archivo / superficie | Fases que lo tocan | Conflicto | Resolución |
|---|---|---|---|
| `scripts/validate_qmind_writeback.py` | A1, A2, A3 | ALTO | Orden estricto A1→A2→A3; cada fase revalida el símbolo antes de editar |
| `tests/test_validate_qmind_writeback_escritura.py` | A1, A2, A3 | ALTO | Aditivo; ninguna aserción vieja se re-baja |
| `.opencode/qmind-writeback/registro.json` | A1 (escritor curado), A2 (campos nuevos), A3 (lectura/contabilidad de la era G), RELEASE (su propia publicación) | ALTO | **Solo lo escribe el escritor.** Ninguna fase lo edita a mano; la vía (a) de AC6 requiere autorización literal expresa |
| `.opencode/qmind-writeback/instantaneas/` | A2 (esquema de nombres), RELEASE (publicación) | MEDIO | El `README.md` del directorio es prosa humana: viaja en el commit que cambia la semántica (A1 para la comparación, A2 para el nombre) |
| `.opencode/qmind-writeback/instantaneas/README.md` | A1, A2 | MEDIO | Una de las dos lo re-escribe; la otra declara que quedó pendiente y lo anota |
| `scripts/run_all_validations.py` | A3 (posible), RELEASE | BAJO | **Preferencia: no tocarlo.** Si una fase lo edita, re-ata antes los dos dientes que leen su fuente (contrato §tests) |
| `scripts/build_lesson_index.py` | **solo C** | n/a | B tiene prohibido editarlo |
| `tests/test_build_lesson_index_s15_fecha_versionada.py` | B, C | ALTO | B cura el fixture; C cura el generador y re-corre la familia |
| `tests/test_build_lesson_index.py` (16) y `tests/test_verify_qmind_context_freshness.py` (36) | C (re-ejecución) | BAJO | Se re-corren; no se editan sin razón medida |
| `.opencode/LECCIONES-INDEX.md` + `.opencode/lecciones_index.json` | **todas** (derivado) | MEDIO | Regenerar con su escritor como **último paso** de cada cierre (R2.10). `[6/8]` del hook bloquea el commit vencido |
| `CHANGELOG.md`, `docs/GUIA_TECNICA.md` | todas (fase propia) + RELEASE (encabezado de versión) | MEDIO | Fases intermedias solo bajo `## [Sin publicar]` |
| `docs/contributing/REGISTRY.md` | todas (su propia fila) | BAJO | El escritor es aditivo; RELEASE **verifica y no re-registra** |
| `.opencode/plans/CURA-INSTRUMENTOS-QMIND-S15-2026-10-07/` | todas | MEDIO | Cada fase escribe su estado y conserva el de las cerradas; ninguna re-transcribe cifras ajenas |
| Notebook `iah-cli-lecciones` | A3 (solo lectura: censo/descarga), RELEASE (una subida autorizada) | MEDIO | Operación remota con autorización literal propia; sin `source delete` |
| `.opencode/plans/Archives/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/**` | **ninguna** | — | Prohibido editar (plan cerrado, archivado y publicado) |
| `AGENTS.md`, `.cursorrules`, `VERSION.yaml`, workflow, hooks | **ninguna intermedia**; VERSION en RELEASE con mandato | — | Clasificador: requieren instrucción literal expresa |

## Estado de seguimiento

| # | Fase | Estado | HEAD medido al cerrar | Nota |
|---|---|---|---|---|
| 0 | Preparación | ✅ CERRADA 2026-10-08, commiteada y empujada | `98c190e` al medir; tip empujado `b536748` | Dos filas del mandato refutadas y re-ancoradas (maestro §1); AC5 bajó de construcción a diente |
| 1 | FASE-A1 | ✅ CERRADA, COMMITEADA y EMPUJADA 2026-10-08 — commit `63b944a` con los ocho checks del hook versionado en verde, revisión profunda L3 **sin hallazgos** y rango empujado `d8a7d80..63b944a` (paridad verificada con `git ls-remote`) | `d8a7d80` al abrir; tip publicado `63b944a` | AC1 y AC2 landed: `sha_cuerpo` + schema 1.1, puerta cuerpo-contra-cuerpo con el gate de registro y D2 conservados, `[CONTADOR]` publicado; PRE 23 → POST 31 (resta 8), tres mutantes sobre copia aislada. Consecuencia durísima para A3: la guarda de migración termina en `continue`, así que las entradas `1.0` **tampoco** llegan al bloque `[DUPLICADO-VIGENTE]` y el rojo de la era G sigue sin evaluarse hasta que haya una entrada 1.1 en el registro |
| 2 | FASE-A2 | ⬜ Pendiente | — | No arranca si A1 no cerró |
| 3 | FASE-A3 | ⬜ Pendiente | — | Dependencia dura con A1 por flujo de control; su rojo de AC6 es un hallazgo verdadero |
| 4 | FASE-B | ⬜ Pendiente | — | Diagnóstico con medición antes de tocar nada |
| 5 | FASE-C | ⬜ Condicional — la abre B | — | Si B no la abre, se declara «no aplica» |
| 6 | FASE-RELEASE | ⬜ Pendiente | — | Requiere versión dictada y autorización literal de la subida |

## Fila abierta por B (plantilla para cuando la llene)

`FASE-C` se abre **solo** si AC7 concluye que la gobernanza no cabe en el fixture. B publica entonces en su
evidencia: la hipótesis confirmada, las dos descartadas con su medición, y la frase literal «la cura está en
`_plan_date`/`build()` porque <razón medida>». Sin esa frase escrita, C no tiene mandato.

## Límites de esta página

El grafo codifica dependencias **leídas del código** (flujo de control del verificador, conflicto de archivo, orden
R2.10). No codifica preferencias de dificultad ni estimaciones de duración, y **no** sustituye la re-medición de
HEAD en cada fase: las dos filas refutadas del maestro §1 demuestran que un estado heredado caduca entre sesiones.
