# A4 — decisión de la deuda de gate del servicio condicional (2026-09-20)

**Resumen.** A4 se decide **re-anclando el fixture del test al dolor que sí promete un
servicio contado** y **assertionando el punto ciego en un test propio**, sin tocar el
comportamiento del gate. La gobernanza real del universo contado queda como deuda AC5 con
dueño **C/D** (maestro §4, AC5; matriz de fases: fila C y fila D listan AC5).

Corrección de registro: en el checkpoint y en §06/§10 esta deuda figuraba con dueño
"D-E". **E no es dueña de AC5**; el dueño vinculante es C/D. Ahí se corrigió.

## Hecho medido

`_proposal_asset_alignment_gate` (`modules/quality_gates/publication_gates.py`, rama
FASE-SR-B D-PF1) deriva `committed = matrix.committed_services(...)`. La matriz se construye
sobre el **universo contado** (`counts_in_alignment=True`). Tras AC2, el dolor
`no_whatsapp_visible` promete `guia_configuracion_whatsapp`, que es condicional y **no** se
cuenta. Con un ledger cuyo único dolor mapeado es ese, `committed` queda vacío y el gate
toma el "PASS trivial (never-block)":

| Campo | Valor medido |
|---|---|
| `passed` / `status` | `True` / `PASSED` |
| `value` | `1.0` |
| `alignment.actionable_total` | `0` |
| `alignment.coverage_ratio` | `1.0` |
| `message` | `0 servicios comprometidos — nada prometido` |

El mensaje es falso en el dominio del negocio: hay una brecha mapeada y un entregable
prometido, y el gate no verifica que la guía se genere ni se entregue. **Hoy una corrida que
promete la guía y no la produce puede publicarse.** Eso es lo que había que decidir.

## Opciones evaluadas

| Opción | Qué hace | Coste medido | Veredicto |
|---|---|---|---|
| **O1** | Dejar el test rojo como denuncia | 1 rojo permanente en la suite de gates; el rojo no distingue "deuda" de "regresión" y el plan prohíbe registrar un fallo legítimo como aprobación, pero tampoco dejarlo indefinido | Descartada: el rojo ya cumplió su función (detectó y documentó el punto ciego); mantenerlo sin dueño de decisión no añade señal |
| **O2** | Contar el servicio condicional (`counts_in_alignment=True`) | **15 rojos** medidos en POST de FASE-B: el gate exigía entregar la guía en hoteles sin la brecha y degradaba la cobertura del resto | Descartada en B, registrada en S-B4 |
| **O3** | Ampliar el universo de la matriz | **13 rojos**, incluido el anti-A5 `test_particion_identica`; el builder devolvía filas que nadie pidió | Descartada en B |
| **O4** | Cambiar el gate para que verifique la entrega de los condicionales sin mover el denominador | Superficie AC5 = C/D, y B tiene prohibido alterar el bloqueo del gate; requiere decisión de producto sobre qué bloquea un entregable de preparación | **No ejecutada en B**: es el contenido de la deuda, con la reproducción de arriba como punto de partida |
| **O5** | **Re-anclar el fixture del test y caracterizar el punto ciego** | 0 rojos; `assert len(blocking) == 3` se conserva y se refuerza; el hoy queda assertionado | **EJECUTADA** |

## Por qué O5 no debilita el test

`test_get_blocking_issues` prueba que `get_blocking_gates` devuelve **solo** los gates
fallidos, con tres bloqueantes. El tercero (`proposal_asset_alignment`) se obtenía porque
`no_whatsapp_visible` prometía `whatsapp_button` — servicio contado antes de B. El anclaje se
mueve al dolor de WhatsApp que **sigue** prometiendo un servicio contado
(`whatsapp_conflict` → `boton_whatsapp`: mismo dominio, misma barra, y el gate bloquea de
verdad: `actionable_total=1`, `coverage_ratio=0.0`, `status=BLOCKED`), y se añade
`assert "proposal_asset_alignment" in blocking_names`, que antes no estaba: el test ahora
exige explícitamente que el gate de alignment esté entre los bloqueantes. Es decir, **la
aserción es más fuerte que la original**, no más débil.

El caso que se perdió (ledger solo-condicional) no queda huérfano: se añade
`test_deuda_ac5_ledger_solo_condicional_pasa_trivial`, que aserta el pase trivial,
`actionable_total == 0` y `coverage_ratio == 1.0`, y que declara por contrato que **debe
ponerse rojo cuando AC5 gobierne la deuda** (ahí se actualizará a `passed is False` /
`BLOCKED`).

## Contrafactuales medidos (PRE/POST con la misma selección)

Selección = `seleccion_pertinente.txt` (25 archivos) + `tests/quality_gates/test_publication_gates.py`.
PRE medido sobre `473ed0f` en un `git worktree --detach` propio (árbol de trabajo intacto,
worktree y registro eliminados después):

| Unidad | PRE (`473ed0f`, sin A4) | POST (con A4) |
|---|---|---|
| Selección extendida (26 archivos) | **1 failed / 619 passed / 1 skipped** en 46,5 s | **0 failed / 621 passed / 1 skipped** en 45,5 s |
| Colección de la selección | 620 casos | 621 casos (+1: el test de caracterización) |
| Funciones canónicas (`grep -rE "^\s*def test_" tests --include=*.py`) | 4.299 | **4.300 (+1)** |
| Regresión completa | 4 failed / 4.261 passed / 41 skipped / 4 xfailed en 244 s (`tests_postfull_regresion.txt`) | **3 failed / 4.263 passed / 41 skipped / 4 xfailed en 196,5 s** (`tests_a4_postfull.txt`) |

Los 3 rojos del POST son **los mismos 3 que ya estaban en la evidencia de FASE-0**
(`test_function_default_flags`, `test_diagnostic_geo_metrics` y
`test_validate_lesson_capitalization[…2026-09-11…]`, este último porque el plan
TRIBUNAL-ENFORCEMENT-OBS salió de la población del verificador al archivarse). Con A4, **ningún
rojo es atribuible a FASE-B**: 4 → 3 y el que desaparece es `test_get_blocking_issues`.

El PRE de la selección extendida es, además, el **contrafactual de que el test re-anclado no
es decorativo**: con el dolor antiguo (`no_whatsapp_visible`) el `assert len(blocking) == 3`
falla; con `whatsapp_conflict` pasa y el gate bloquea por la vía real.

## Qué NO se tocó

Umbrales, `config/pricing.yaml`, `BLOCKING_VERDICTS`, `GATE_BLOCKING_ENABLED`,
`TribunalJudge._compute_verdict`, los contratos `write/publish/suppress` de
`DeliveryPackager`, y **cualquier línea de comportamiento del gate**. El cambio de A4 es un
archivo: `tests/quality_gates/test_publication_gates.py`.

## Lo que recibe C/D (S-B1 redefinido)

No es "arregla un test": es la decisión de producto **si un servicio condicional comprometido
por el ledger debe bloquear la publicación cuando su entregable no se genera**, y con qué
denominador. La reproducción mínima está en la tabla de arriba; el test de caracterización
fija el comportamiento vigente.
