# Dependencias de Fases — CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15

## Diagrama de dependencias

```
Preparacion (sesion del 2026-10-15: Paso 0 + maestro + prompts)
        │
        ▼
    FASE-A  ── cierre documental de la tanda de instrumentos
        │         (sin codigo; commit de las rutas D-QW + crudos + acta)
        ▼
    FASE-B  ── censo era-G + decision por fuente (Operador en el bucle)
        │         (sin codigo, sin borrar, sin subir: medicion y decision)
        ▼
    FASE-C  ── cura era-G: el mecanismo que FASE-B decidio
        │         (scripts/validate_qmind_writeback.py y/o registro escrito por el writer;
        │          unica fase que puede tocar codigo)
        ▼
    FASE-RELEASE-4.81.1 ── bump + docs + write-back + archivado (orden R2.5/R2.10)
```

## Estado de fases

| Fase | Estado |
|------|--------|
| Preparación (Paso 0 + maestro + prompts) | ✅ 2026-10-15 |
| FASE-A | ✅ 2026-10-21 — crudos `15-`…`26-` en `77dea21` (12 rutas, hook 8/8 con `TMPDIR` en el FS del repo); las 4 rutas del registro ya estaban en `85ab952`; acta y post-ejecución en el commit `docs(plan)` de la sesión. Sin push (Operador). Población medida: 1 gobernado (la cifra «2» del prompt está vencida por `26bd0f5`) |
| FASE-B | ✅ 2026-10-22 — censo + decisiones en `evidence/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/FASE-B/censo-era-g.md`; rojo-antes `EXIT 1` (intento 1 de 1, crudo `01-`); cruce de poblaciones 5/5 idéntico (el rojo y el contador son la misma población); 0 huéspedes `CONTEXT:` verificado por títulos. Decisión del Operador para las 5 fuentes: **(a) marcar como reemplazada en el registro**. **FASE-C editará exactamente**: `scripts/validate_qmind_writeback.py` (primitivo nuevo `registrar_historica()` + wiring CLI, firma y coste en el censo §5.1), `tests/test_validate_qmind_writeback_escritura.py` (3 dientes: contabilidad, no-vigencia, idempotencia) y `.opencode/qmind-writeback/registro.json` **solo por el writer** (5 entradas `reemplazada`) |
| FASE-C | ✅ 2026-10-22 — cura ejecutada por el mecanismo de FASE-B: primitivo `registrar_historica()` + puerta CLI `--mark-historic` en `scripts/validate_qmind_writeback.py`, 4 dientes (3 mínimos del censo §5.1 + 1 de la puerta CLI) en `tests/test_validate_qmind_writeback_escritura.py` con diente rojo-antes, mutante del guard de idempotencia y delta 63→67; las 5 entradas `reemplazada` quedaron escritas **por el writer** (registro 9→14 entradas, 8 vigentes intactas). AC5: corrida real sin `[DUPLICADO-VIGENTE]` y `0 fuente(s) huesped(s)` sobre 8/8 (racha dirigida de 3 intentos por descargas flaqueantes; el residuo `NO-EVALUABLE` es la abstención estructural de la entrada `1.0` sin `sha_cuerpo`, declarada). Absorción T4: `S-SEC-1` definida en §5 del maestro + par del índice regenerado. Quick 13/13. Sin commit (Operador) |
| FASE-RELEASE-4.81.1 | ⬜ Pendiente |

## Conflictos de archivos por fase

| Archivo | FASE-A | FASE-B | FASE-C | RELEASE |
|---------|--------|--------|--------|---------|
| `.opencode/context/CONTEXT-DEUDAS-WRITER-QMIND-2026-10-15.md` | **COMMITEA** (ya escrito) | — | — | — |
| `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-RELEASE/15-…` (crudos) | **CREA** | — | — | — |
| `.opencode/LECCIONES-INDEX.md` + `.opencode/lecciones_index.json` | **COMMITEA** (par ya regenerado) | — | — | **REGENERA** (write-back → `git mv` → regenera) |
| `.opencode/qmind-writeback/registro.json` | — | — | **EDITA solo por el writer** — mecanismo (a) decidido en FASE-B (2026-10-22): 5 entradas `reemplazada` vía `registrar_historica()` | **EDITA** (entrada del write-back del plan, por el writer) |
| `scripts/validate_qmind_writeback.py` | — | — | **EDITA** — especificado en FASE-B (2026-10-22): primitivo `registrar_historica()` + wiring CLI (firma propuesta y coste medido en el censo §5.1) | — |
| `tests/test_validate_qmind_writeback_escritura.py` | — | — | **EDITA** — 3 dientes del mecanismo (contabilidad, no-vigencia, idempotencia; censo §5.1) | — |
| Notebook `iah-cli-lecciones` | **NO SE TOCA** | **NO SE TOCA** (solo se lista) | **BORRA solo con autorización por fuente** (si la decisión es b) | **SUBE** el 10-analisis del plan (write-back) |
| `VERSION.yaml`, `CHANGELOG.md`, `docs/GUIA_TECNICA.md`, `docs/cobertura-historia.md`, `AGENTS.md` §Cobertura | — | — | — | **EDITA** |
| `.opencode/plans/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/` (docs del plan) | todas | todas | todas | todas (y `git mv` a `Archives/`) |
| `docs/contributing/REGISTRY.md`, `.agent/SYSTEM_STATUS.md`, `.agent/knowledge/DOMAIN_PRIMER.md` | — | — | escribe el registro de fase / regenera (FASE-C) | escribe el registro de release / verifica |

## Conflictos con trabajo ajeno

- Al concebir este plan el árbol trae **4 rutas sin commitear** que son de este plan (el contexto `D-QW`, el crudo `14-` y el par del índice): FASE-A las commitea con pathspec y autorización. No hay trabajo de terceros pendiente. **Vencido el 2026-10-15**: esas cuatro rutas y la carpeta del plan quedaron versionadas en `85ab952` con pathspec y hook 8/8; la fase sigue debiendo sus crudos y el acta.
- `temp/` (gitignored) contiene los crudos de la sesión previa: FASE-A los persiste bajo evidencia **antes** de que nadie los borre; ninguna fase los borra sin orden del Operador.
- El `10-analisis` de CURA y los dos CONTEXT publicados están **congelados** (DEC-2/DEC-3): editar cualquiera de los tres los deja VENCIDO en el notebook.

## Cautelas de secuencia

- **El rojo-antes es antes**: la corrida del writer de FASE-B se guarda como crudo y es lo que hace legítimo el ✅ de AC5 (R2.8: sin el rojo no hay verde).
- **Borrar es irreversible**: la decisión (b) de FASE-B autoriza por fuente; si FASE-C encuentra una fuente sin decisión, para y pregunta en texto plano.
- **El orden del cierre no se permuta**: write-back → índice → `git mv` → índice (R2.10); archivar antes desactiva los verificadores.
- **La L3 va entre el último commit y el push** en cada corte que se empuje; un commit nuevo re-abre el gate, y la cobertura se declara con su rango medido.

## Determinación post-FASE-B (2026-10-22): hallazgo del gate de secretos — absorber en FASE-C

> Fuente única de esta determinación; el resto de documentos la referencian. No re-transcribir cifras.

**Qué pasó**: durante el cierre documental de FASE-B (commits `658601f`/`9bedf66`, otra sesión), el Secrets Check imprimió `SIN_HALLAZGOS` con su pata staged **sin leer una sola línea**. Hallazgo nuevo, declarado y no curado.

**Mecanismo medido** (repro propio en `evidence/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/FASE-B/08-repro-guard-cp1252.txt`; relectura del staged real en `07-barrido-staged-utf8.txt`): `subprocess.run(..., capture_output=True, text=True)` sin `encoding=` hereda cp1252 (venv canónico); el diff staged trae bytes de las ranuras ilegales de cp1252 (p. ej. `0x8f`); el hilo lector revienta con `UnicodeDecodeError`, `run()` devuelve `stdout=None` sin excepción, y el guard `if not staged_diff: return []` de `_check_staged_content` cierra en verde. El `except Exception: return []` del mismo símbolo hace del gate un **fail-open**: cualquier fallo del insumo se publica como `SIN_HALLAZGOS`. La evidencia estaba limpia (relectura en bytes con los 9 patrones reales: 3.033 líneas añadidas, 0 hallazgos); lo que faltaba era el insumo del gate. Señal que lo delató: el denominador quieto del tracked contra el barrido por forma que crecía.

**Alcance de la deuda**: 4 sitios de `run_all_validations.py` con el mismo raigambre (`text=True` sin `encoding=`), con **consumidor y modo de fallo distintos** — discriminados aquí porque el fix se busca por consumidor, no por síntoma:

- `_check_staged_content` (Secrets Check, **pata staged**): **activo — ya mordió**; decodificación + fail-open (`except Exception: return []` y el guard `if not staged_diff`). Es el caso del repro.
- `_git_staged_paths` → lo consume `_check_client_material` (**pata Client Material**, que también suma `_git_tracked_files()`): **latente** — con staged vacío su `[]` es correcto hoy; muerde si un **nombre de ruta** staged trae bytes fuera de cp1252, y la pérdida es **silenciosa: rutas staged sin escanear por marcadores de cliente**. (El barrido de fragmentos **no** consume este símbolo: `_barrido_fragmentos` se alimenta de `_git_tracked_files()` + `_untracked_output_files()` — nombrarlo bien importa: buscar el fix en la pata equivocada deja la pérdida del Client Material sin curar.)
- `_git_tracked_files` (Secrets tracked, fragmentos y Client Material): **latente**, con fallback declarado a `_walk` (puede divergir del índice de git sin decirlo).
- `_run_command` (verificadores delegados): modo de fallo **distinto** — `except Exception: return 1, str(e)`: sale rojo con mensaje raro, no verde silencioso.

**Determinación del Operador (2026-10-22)**: (a) registrar la deuda con ID propio, **absorbida por la sesión de FASE-C** — documental, cero código para el gate; (b) el fix con tests queda como **vía de cierre en fase propia**, no en FASE-C ni en este plan (FASE-C tiene su contrato era-G y AC7 ya declara los conteos de la ronda que tests nuevos moverían); (c) lo declarado en el mensaje de commit queda como **evidencia del hallazgo**, no como registro.

**Mecánica de la absorción (lo que FASE-C ejecuta, Tarea 4 de su prompt)**:

1. ID propuesto `S-SEC-1` (familia `S` = «Hallazgos y seguimientos de plan»); la acuñación definitiva es del Operador — si prefiere otro, se ajusta al registrar.
2. Fila con el ID en primera celda (convención de definición de `build_lesson_index.py`) en §5 «Deudas diferidas con dueño» de `01-plan-maestro.md`: síntoma, mecanismo, alcance (los 4 sitios), dueño Operador y camino de cierre = fase propia con fix **fail-closed** (bytes + decodificación tolerante + abstención o rojo ante insumo ilegible) + dientes + par de crudos legible/ilegible.
3. Regenerar el par `.opencode/LECCIONES-INDEX.md` + `.opencode/lecciones_index.json` (`python scripts/build_lesson_index.py`) y commitearlo junto a la fila — el `[6/8]` del hook lo exige.
4. `run_all_validations.py --quick` verde y mención de la absorción en el `--archivos-mod` del `log_phase_completion` de FASE-C.
5. **Prohibido en la absorción**: tocar los CONTEXT congelados (DEC-2/DEC-3), el `10-analisis` de CURA, o cualquier documento registrado y publicado en el notebook; y **ningún código del gate** en FASE-C (su cura es fase propia).

**Estado transitorio declarado**: hasta que el paso 2 escriba la definición, `S-SEC-1` figura en `citados_sin_definicion` del índice regenerado — es el estado verdadero (cita sin definición), no un defecto; se cierra con la definición. **Cerrado el 2026-10-22 (FASE-C, T4)**: la definición humana (síntoma, mecanismo, alcance de los cuatro sitios, dueño y camino de cierre) quedó en §5 del maestro con `S-SEC-1` al frente de la fila, y el par `.opencode/LECCIONES-INDEX.md` + `.opencode/lecciones_index.json` se regeneró con `build_lesson_index.py` — verificado que `citados_sin_definicion` deja de listar el ID (114→113). **Divergencia de forma declarada (código manda)**: el corpus de definiciones del generador son los `09-/10-análisis` y `.opencode/context/`, **no** el maestro — la fila §5 por sí sola nunca habría sacado al ID de `citados_sin_definicion`, así que la definición mecánica (`**S-SEC-1** — enunciado`) vive en `10-analisis-post-implementacion.md` de este plan, junto a su fila de seguimiento. Cero código para el gate, tal como determinó el Operador.
