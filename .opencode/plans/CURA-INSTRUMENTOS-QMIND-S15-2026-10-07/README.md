# PLAN CURA-INSTRUMENTOS-QMIND-S15 (2026-10-07) — índice

Cura de los dos instrumentos que gobiernan las lecciones del repo: el **verificador de write-back de QMind**
(`scripts/validate_qmind_writeback.py`, check `[17/18]` del modo completo) y el **control S15 del índice de
lecciones** (`tests/test_build_lesson_index_s15_fecha_versionada.py`, que vigila `[6/8]` del pre-commit, o sea cada
commit).

**Origen:** mandato del operador del 2026-10-07 (texto de sesión nueva) y el cierre del plan padre
`REFACTOR-WHATSAPP-ENTREGA-2026-09-18` (4.79.0), cuya sesión dejó los dos huecos medidos y sin cura: sin writer para
saneear, y sin control S15 estable.

**Estado:** preparación cerrada el 2026-10-08 contra HEAD `98c190e`. **Sin código implementado.** ⟦Estado de FASE-A1, 2026-10-08, misma fecha y sesión distinta: AC1 y AC2 landed en el árbol de trabajo contra HEAD `d8a7d80`, **sin commitear** porque el commit no se autorizó en el chat. La frase anterior describe el árbol al cerrar la preparación y se conserva como registro.⟧ ⟦**Sello 2026-10-08, misma sesión:** llegó la instrucción literal «Git Commit + L3 + Push». commit `63b944a` con los ocho checks del hook versionado en verde, revisión profunda L3 **sin hallazgos** y rango empujado `d8a7d80..63b944a` (paridad verificada con `git ls-remote`). El sha del commit que estampa esta nota no se estampa en sí mismo.⟧ ⟦Sello del
cierre: el operador autorizó commit, L3 y push en la misma sesión. El commit documental de la preparación es
`b536748`, los ocho checks del hook versionado pasaron, la revisión profunda L3 no produjo hallazgos y el rango
empujado es `98c190e..b536748`. El sha del commit que estampa esta nota no se estampa aquí.⟧ **Punto de reanudación: FASE-A2** (AC3 y AC4), que por contrato no arranca si A1 no cerró; A1 cerró commiteada y empujada (`63b944a`), así que la línea base de A2 es ese tip.

## Por qué importa cada fila

| Hueco | Lo que impide hoy | AC que lo cierra |
|---|---|---|
| La puerta de vigencia compara la instantánea contra el **cuerpo crudo** | Ningún plan cuyo `10-analisis` lleve identidades sustituidas puede dar verde en `[17/18]`: o se publica la identidad del cliente o el check corta. Es el caso que el plan padre y su FASE-G **obligan** a saneear | AC1, AC2 |
| El slug de la instantánea trunca a 120 caracteres | Dos publicaciones con prefijo común pisaron el mismo archivo: el registro del padre tiene dos shas y el repo **un** byte-exacto | AC3 |
| `fuente_id` se publica vacío | Nada en el repo dice **qué fuente del notebook** es la que se publicó; la verificación depende del título | AC4 |
| `--upload` con el plan archivado | La ruta equivocada corta un `[FAIL]` que no nombra lo que buscó; y el modo verificación debe resolver en las dos raíces | AC5 |
| La fuente de la era G no está contable | Al curar AC2 aparece un rojo **verdadero** `[DUPLICADO-VIGENTE]` que hoy está tapado por el rojo de vigencia | AC6 |
| El control S15 pierde según el entorno | Un rojo que se re-produce en cada sesión y empuja a debilitar un control anti-regresión | AC7, AC8 (+ AC9 condicional) |

## Documentos

| Archivo | Para qué |
|---|---|
| `00-lecciones-capitalizadas.md` | Paso 0: 10 consultas re-ejecutables por dos ejes, 15 filas capitalizadas con su efecto sobre un AC concreto, 7 descartes, cobertura declarada con su límite |
| `01-plan-maestro.md` | §1 revalidación medida del mandato (dos filas refutadas, cuatro confirmadas, una rectificada por lectura), §2 decisiones congeladas, §3 fases con R3, §4 AC1-AC10 con su artefacto legible, §5 deudas con dueño, §6 qué hizo y qué no hizo la preparación |
| `04-contrato-ejecucion.md` | Límites y precedencias, inicio de cada fase, presupuesto (R2.1 con el instrumento **fuera de servicio**), reglas de tests/mutantes/tres estados, cierre incremental en 8 pasos, orden R2.10 del write-back y del archivado |
| `dependencias-fases.md` | Grafo, tabla de conflictos por archivo y la dependencia **dura** A1→A3 leída del flujo de control |
| `05-prompt-inicio-sesion-fase-A1.md` | AC1 + AC2 — las dos identidades y la puerta de vigencia |
| `05-prompt-inicio-sesion-fase-A2.md` | AC3 + AC4 — slug sin colisión y `fuente_id` desde la tabla |
| `05-prompt-inicio-sesion-fase-A3.md` | AC5 + AC6 — rutas archivadas y la era G declarada con dueño |
| `05-prompt-inicio-sesion-fase-B.md` | AC7 + AC8 — diagnóstico medido del control S15 y cura con diente intacto |
| `05-prompt-inicio-sesion-fase-C.md` | AC9 — condicional: solo si B concluye que la cura está en el generador |
| `05-prompt-inicio-sesion-fase-RELEASE.md` | AC10 — write-back de **este** plan con el writer curado, docs oficiales y archivado |
| `06-checklist-implementacion.md` | Casillas por fase; ninguna pendiente se marca por adelantado |
| `09-documentacion-post-proyecto.md` | **Fuente canónica** de las métricas por fase |
| `10-analisis-post-implementacion.md` | Resumen, matriz de hallazgos, lecciones (serie `L-CIM` reservada), seguimientos y decisiones DA-CIM.1…DA-CIM.8. **No declara cierre** |
| `evidence/CURA-INSTRUMENTOS-QMIND-S15-2026-10-07/FASE-0/` | Crudos de apertura (quick y selección PRE) y registro de la fase de preparación |

## Progreso

| Fase | ACs | Estado |
|---|---|---|
| Preparación | — | ✅ 2026-10-08 |
| FASE-A1 | AC1, AC2 | ⬜ Pendiente |
| FASE-A2 | AC3, AC4 | ⬜ Pendiente |
| FASE-A3 | AC5, AC6 | ⬜ Pendiente |
| FASE-B | AC7, AC8 | ⬜ Pendiente |
| FASE-C | AC9 | ⬜ Condicional (la abre B) |
| FASE-RELEASE | AC10 | ⬜ Pendiente |
| FASE-VERIFY | — | **No aplica** (executor §4.6, criterio 2: cero ejecuciones E2E) |

## Cómo continuar

Una fase por sesión (R1). La siguiente sesión abre con el contenido de
`05-prompt-inicio-sesion-fase-A1.md` (bloque «Prompt de ejecución») y **re-mide** HEAD, paridad, status y el quick
antes de escribir la primera línea: dos filas del mandato caducaron entre su redacción y esta preparación, y la
tercera puede caducar entre sesiones.

Reglas que gobiernan sin excepción (maestro §2 y contrato): ninguna fase re-baja una aserción existente para
conseguir verde; todo mutante se ejecuta sobre el instrumento versionado y se restaura verificando sha256; el
registro de QMind **solo** lo escribe el escritor; nada se borra en el notebook; commit, L3 y push requieren
instrucción literal del operador en el chat de la sesión correspondiente.
