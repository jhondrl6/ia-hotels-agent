# Documentación Post-Proyecto — TRIBUNAL-ENFORCEMENT-OBS-2026-09-11

> **Versión objetivo**: 4.77.0
> **Propósito**: Acumular datos por fase para que FASE-RELEASE genere CHANGELOG y GUIA_TECNICA oficiales.
> **Creado**: 2026-09-14 en la sesión de ajuste (el executor lo exigía desde la concepción; se instala vacío y se acumula al cierre de cada fase — no se rellena de memoria al final).

---

## Sección A: Módulos Nuevos / Modificados

| Módulo | Archivos | Descripción | Fase |
|--------|----------|-------------|------|
| **_(ninguno — P1 es fase de decisión: sin assets, sin código de producción)_** | — | Verificable en `git status` del commit de cierre: solo `.opencode/plans/…` y `evidence/FASE-P1/` | P1 |

**Guía por fase**: P1 no produce filas (decisión). P2: `judge.py`/`main.py`/`delivery_packager.py` según O elegida. P3-A: `asset_reviewer.py`/`judge.py`. P3-B: `acta_writer.py`/`main.py` (solo Q5=a)/test barreda. P4: ninguna (observación). RELEASE: docs.

## Sección B: Funcionalidades Nuevas

| Feature | Módulo | Descripción | Fase |
|---------|--------|-------------|------|
| **Contrato del veredicto enriquecido** (documento, no código) | `evidence/FASE-P1/` | Matriz recomendación→veredicto de 8 pasos, consecuencia del bloqueo (escalar: ZIP suprimido + `corrective_actions` + humano decide), **cuatro** estados por revisor y kill switch heredado. **Vinculante** para P2/P3-A/P3-B | P1 |
| **Prompt de FASE-P2** | `.opencode/plans/<PLAN>/` | `05-prompt-inicio-sesion-fase-P2.md`, con O1-cuarentena y la cláusula "no re-decidir" | P1 |
| Enforcement del tribunal (los dientes) | `tribunal/`, `main.py`, `delivery/` | **No existe todavía**: P1 lo especificó, P2 lo implementa | P2 (pendiente) |

## Sección D: Métricas Acumulativas

| Métrica | Pre-plan (v4.76.0) | Al cerrar P1 | Al cerrar P2 | Al cerrar P3-A | Al cerrar P3-B | Al cerrar P4 | Final (v4.77.0) |
|---------|--------------------|--------------|--------------|----------------|----------------|--------------|------------------|
| Funciones test (canónico `grep -rE "^\s*def test_" tests --include=*.py`) | 4.063 | **4.063** (sin cambio) | — | — | — | — | — |
| Archivos `test_*.py` | 293 | **293** (sin cambio) | — | — | — | — | — |
| Fallos conocidos (suite en HEAD) | 3 (2 ajenos + barreda/D-V.1) | **3** (sin cambio) | — | — | ⟨P3-B cierra barreda → 2⟩ | — | — |
| `--quick` checks | 9/9 | **9/9** (2026-09-14 14:00, medido en el cierre; re-verificado por los 7 hooks de `fd8e4f4`) | — | — | — | — | — |
| Iteraciones de fase (unidad declarada, D-V2.1) | — | ≈30 `ids` / ≈58 `tool_use` | — | — | — | — | — |

> La fila de barreda asume que P3-B se ejecuta con Q5≠(a) o (a); si P4 se difiere, la columna P4 se marca "Diferida" con referencia a la decisión.

## Sección E: Archivos Afiliados Actualizados

| Archivo | Actualizado en | Nota |
|---------|----------------|------|
| `REGISTRY.md` vía `log_phase_completion.py --fase FASE-P1` (**sin** `--release`) | P1 | Registro de fase de decisión |
| `01-plan-maestro.md` | P1 | §1 orden y presupuesto · §2.1 confirmado y agravado · §3 O1-cuarentena · §6 **ACs finales** (17 filas + columna NR7) |
| `06-checklist-implementacion.md` | P1 | Estado Global, checklist de P1 cerrado, y P3-A/P3-B/P2 reescritos con lo decidido |
| `dependencias-fases.md` | P1 | Diagrama y tabla reordenados (P3→P2) · **FASE-VERIFY cerrada en no activa** · prompt de P2 marcado como creado |
| `README.md` · `00-lecciones-capitalizadas.md` · `10-analisis-post-implementacion.md` · este `09` | P1 | Progreso 1/6 · §3.b resuelto · DA-P1.1…DA-P1.10 + 5 lecciones · aporte de fase |
| **`AGENTS.md` / `CHANGELOG.md` / `GUIA_TECNICA.md` / `VERSION.yaml`** | **P1: NO** | P1 no toca documentos versionados. Lo que **RELEASE debe publicar** al cerrar 4.77.0: (1) la decisión de enforcement y su consecuencia; (2) el orden P3→P2 y por qué; (3) que **no hubo sesión FASE-VERIFY** y AC-V1 la sustituyó; (4) **AC-F5 cambia el `evidence_tier` de corridas reales** — comportamiento visible, se declara (DA-P1.8); (5) el acta deja de omitir la sección de revisores y pasa a listar **cuatro** estados |

## Aporte de FASE-P1 para GUIA_TECNICA

- **Técnico**: `_read_evidence_tier` depende de un `MANIFEST.json` que en el flujo real aún no existe, así que el acta operaba con `"C"` por fallback silencioso; `_is_template_stub` contaba frontmatter como contenido; `acta_writer` suprimía la sección de revisores cuando estaba vacía. Los tres son de la misma familia —**ausencia publicada como hallazgo**— que NR8/`DA-C3` prohíben.
- **De proceso**: el Paso 0 de P1 cumplió en producir evidencia propia — los tres hechos del párrafo anterior no estaban en el plan y cambiaron dos ACs (nace AC-F6; AC-F2 se re-enuncia). Contraste honesto: **la misma tarea re-afirmó lo que ya decía §2.1**; confirmar no es descubrir.
- **Comercial**: G0 queda **encarrilado, no cerrado**. P1 quita la objeción de diseño; el dato sigue dependiendo de T3a/T3b (un hotel que dé sus números y su analítica), y este plan ya no finge tenerlo.

---

## Volcado para FASE-RELEASE

RELEASE (Tarea 3) verifica que cada fase cerrada ✅ tenga su aporte aquí; una fase sin fila en A/B/D/E se marca en el `10-analisis` como omisión detectada en el cierre, no se inventa.
