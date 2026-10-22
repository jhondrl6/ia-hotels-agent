# Análisis Post-Implementación — CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15

> Creado desde la concepción del plan (executor v2.15.0): se actualiza al cierre de cada fase, no al final.

## Resumen de Ejecución (llenar al cierre de cada fase)

| Fase | Estado | Notas |
|------|--------|-------|
| FASE-A — Cierre documental | ✅ 2026-10-21 | Crudos `15-`…`26-` en `77dea21` (12 rutas, hook 8/8); acta con shas de blob en `evidence/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/FASE-A/`; quick 13/13 con venv canónico. Sin push (Operador) |
| FASE-B — Censo era-G + decisión | ✅ 2026-10-22 | Censo en `evidence/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/FASE-B/censo-era-g.md`: 5 fuentes identificadas (id/título/sha/fecha/causa), cruce de poblaciones 5/5 idéntico, 0 huéspedes `CONTEXT:`; decisión del Operador (a) «marcar como reemplazada» en las 5; mecanismo especificado (primitivo `registrar_historica()`); quick 13/13 (venv canónico, `04-quick-cierre.txt`). Cero código |
| FASE-C — Cura era-G | ⬜ Pendiente | |
| FASE-RELEASE-4.81.1 | ⬜ Pendiente | |

## Matriz de Verificación de Hallazgos (llenar por fase)

| AC | Enunciado (resumen) | Fase | Estado | Artefacto donde se lee |
|----|---------------------|------|--------|------------------------|
| AC1 | Rutas del registro `D-QW` versionadas y empujadas; índice `--check` verde en el árbol del commit | FASE-A | ✅ salvo «empujadas» (pendiente de autorización de push) | `git show 85ab952` y `77dea21` + `08c-hook-pre-commit.txt` + `09-poblacion-arbol-commit.txt` + acta §2 |
| AC2 | Crudos de la tanda persistidos bajo evidencia con shas en el acta | FASE-A | ✅ | `FASE-A/acta-cierre-documental.md` §1 (shas de blob y disco, 12/12) |
| AC3 | Censo era-G por fuente con causa de falta de contabilidad y cruce de poblaciones | FASE-B | ✅ 2026-10-22 | `FASE-B/censo-era-g.md` §2 y §3 + crudo `01-writeback-rojo-antes.txt` |
| AC4 | Decisión escrita del Operador por fuente + mecanismo con coste | FASE-B | ✅ 2026-10-22 | Tabla de decisión en el censo §5 (respuesta del Operador registrada en la sesión, 2026-10-22) |
| AC5 | Writer sin `[DUPLICADO-VIGENTE]` y con 0 huéspedes; par rojo/verde | FASE-C | ⬜ | Crudos de FASE-B y FASE-C |
| AC6 | Delta R2.3 por fase de código; `--quick` verde por fase | A/B/C | ✅ FASE-A y FASE-B (13/13 cada una); C pendiente | `03b-quick-venv-canonico.txt` y `FASE-B/04-quick-cierre.txt` (y `03-quick.txt`: 9/13 del `.venv-wsl` 3.11, contaminación de intérprete) |
| AC7 | 4.81.1 sincronizada, CHANGELOG de las tres curas, nota de ronda, DOMAIN_PRIMER verificado | RELEASE | ⬜ | CHANGELOG + cobertura-historia + árbol archivado |

## Lecciones Aprendidas (llenar al cierre de cada fase)

### Lecciones capitalizadas de planes anteriores (espejo de `00-lecciones-capitalizadas.md` §2)

| ID | Qué cambia | Real (al cerrar) |
|----|------------|------------------|
| Lección `L-SECF.2` | Commit por pathspec con add nominal y conteo del índice (T2 de FASE-A) | ✅ 2026-10-21: add nominal por ruta + conteo 12/12 + `git status` antes/después (`77dea21`); el protocolo hizo legible la ventana concurrente `53fe9ed` que cortó el intento 2 |
| Deuda `D-QW-1` | El censo declara si alguna fuente viene de la rama que no registra (T1 de FASE-B) | ✅ 2026-10-22: 0 de las 5 huéspedes es `CONTEXT:` (verificado por títulos del listado); el censo §4 declara el límite estructural — `_fuente_nombral` exige `10-analisis` en el título, así que ninguna fuente `CONTEXT:` puede entrar al rojo ni al contador — y deja la población `CONTEXT:` sin registro (41 fuentes) fuera de alcance bajo `D-QW-1` |
| Deuda `D-QW-2` | El censo declara con qué predicado midió (T1 de FASE-B) | ✅ 2026-10-22: el censo declaró su predicado (`_fuente_nombral` + contabilidad por título del registro) y midió `scan_context_declarations()` = 0 en vivo como copia estrecha del writer, sin usarla como población gobernada |
| Lección `L-QW.2` | La marca se escribe en el registro, no se borra del notebook (T1 de FASE-C) | ✅ en su parte de FASE-B (2026-10-22): la decisión (a) fijó dónde se marca (`.opencode/qmind-writeback/registro.json`, entradas `reemplazada`) y con qué evidencia (título + `fuente_id` + `sha_metadata` del censo y el par rojo/verde de AC5); la marca efectiva la escribe FASE-C |
| Lección `L-CST-6` | El mecanismo no se promete sin medirlo (restricciones de B y C) | ✅ en su parte de FASE-B (2026-10-22): se midió que `registrar_publicacion()` no puede registrar sin instantánea, y se declaró firma propuesta + coste en líneas y dientes (censo §5.1) sin prometer nada que el código no tenga |
| Lección `L-V.2` | El verde de AC5 es la corrida real, no el diff (T2 de FASE-C) | ✅ en su parte de FASE-A: el acta cita crudos re-ejecutados en esta sesión y descubrió el rojo falso del intérprete no canónico |
| Deuda `D-V2.1` | Presupuestos auto-reportados en `tool calls` | ✅: auto-reporte ~70 `tool calls` en §6 del acta (estimado ~30, superado por la re-medición del árbol vencido) |

### Lecciones nuevas de este plan (L-… si las hay; «sin lecciones nuevas» es un resultado válido)

Sin lecciones nuevas con ID acuñado en FASE-A (acuñar IDs es decisión del Operador y toca el contrato del Paso 0). Tres observaciones de sesión quedan registradas para quien las acuñe o las absorba en fases posteriores:

1. Un `--quick` corrido con un intérprete fuera del canónico publica **rojos falsos**: 9/13 con `.venv-wsl` (Python 3.11: `SyntaxError` PEP 701 en `validate_governance_numbers.py`, `requests` ausente, clon cross-device) frente a **13/13** con `venv/Scripts/python.exe`. El verde se certifica con el venv canónico.
2. Dos sesiones concurrentes sobre el mismo árbol pueden volver vencido el par del índice **en pleno hook**: el `[6/8]` no distingue «otra sesión está a punto de commitear el par» de «el par está sucio». El `git status` antes/después es lo que permite atribuirlo.
3. (FASE-B, 2026-10-22) El rojo `[DUPLICADO-VIGENTE]` y el contador de huéspedes sin contabilidad son **la misma población** (medido: `_lineas_huesped` es el reportero de `_huespedes_sin_contabilidad`; cruce de ids 5/5): dos etiquetas de una sola lista de deuda, no dos deudas. Una cura por fuente cierra ambas cuentas a la vez, y ninguna política futura debe tratarlas por separado.

## Seguimientos abiertos

| Tema | Estado | Dueño | Acción futura |
|------|--------|-------|---------------|
| `D-QW-1` / `D-QW-2` — rama por defecto del writer y detector divergente | Diferida en el maestro §5 | Operador | Fase propia (o absorción en FASE-C si el censo la toca) |
| `S-CIM-1` — `[18/18]` sin `--strict` | Diferida | Operador | AC propia |
| `S-CST-1` — gate `hard_contradictions` sin productor | Diferida | Operador | Fase propia |
| `P6.5` — el acta niega al revisor que corrió | Diferida | Operador | Decisión de cláusula registrada en CURA |
| Anotaciones «sin commit» de 4.81.0 que el push venció | Diferida | Operador | Sello datado con `2e048e6`/`1f95e84` o addendum en `evidence/` |
| Push de AC1 (rutas del registro) | Pendiente desde FASE-A (2026-10-21) | Operador | Autorizar push con L3 entre el último commit y el push; la paridad con `origin/master` se mide al empujar |
| Hook `[8/8]` cross-device bajo WSL | Documentado en el acta §2 | Operador | Commitear con `TMPDIR` en el mismo FS que el repo (`/mnt/c/Users/Jhond/AppData/Local/Temp`); quick certificado con `venv/Scripts/python.exe` |
| Cura era-G (5 marcas `reemplazada` vía `registrar_historica()`) | Listo para FASE-C (2026-10-22): mecanismo y coste especificados en el censo §5.1 | Operador | Ejecutar FASE-C en sesión nueva con `05-prompt-inicio-sesion-fase-C.md` |

## Métricas de Ejecución (referencia, no copia)

- Por fase: ver `09-documentacion-post-proyecto.md` §D y los crudos en `evidence/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/FASE-*/`.
- El conteo canónico de tests lo imprime `grep -rE "^\s*def test_" tests --include=*.py | wc -l`; la cifra commiteada, `git grep -c -E "^\s*def test_" HEAD -- tests`.

## Decisiones Arquitectónicas

| ID | Decisión | Rationale | Alternativas rechazadas |
|----|----------|-----------|-------------------------|
| DEC-1 | 4.81.1 cubre las tres curas en una sola unidad de versión | Decisión del Operador (2026-10-15) al elegir el plan consolidado: una entrada de CHANGELOG y una nota de ronda por los 9 tests | Dos releases (prompt documental con 4.81.1 ya + plan aparte para era-G) — coste: dos bumps y la segunda vía esperando igual |
| DEC-4 | Borrar del notebook es decisión escrita del Operador, por fuente | Irreversible sobre contenido publicado; el writer solo marca | Borrar en bloque al medir el censo — rechazada por irreversible y sin autorización por fuente |
| DEC-B.1 | Las 5 fuentes de la deuda era-G se **marcan como reemplazadas en el registro**, no se borran (decisión del Operador registrada en la sesión, 2026-10-22) | La opción (a) preserva la contabilidad (L-QW.2) y es reversible sobre el registro; además 2 de las 5 fuentes no tienen respaldo byte-exacto medido (censo §5.2), así que el borrado perdería contenido publicado | Borrar las 5 del notebook (irreversible, pierde sin respaldo las filas 1 y 5) y dejarlas declaradas huésped/excepción (normaliza la deuda sin resolverla y el mecanismo por archivo aparte exige código nuevo en el predicado) |

## Checklist de Cierre (llenar en FASE-RELEASE)

- [ ] `10-analisis` completo (matriz, lecciones, seguimientos, decisiones) antes del write-back
- [ ] Write-back `--upload` retorna 0 y `--strict` confirma la ingesta
- [ ] Orden R2.5/R2.10: write-back → índice → `git mv` → índice
- [ ] Lecciones con pertinencia INCLUIR persistidas en la memoria del proyecto
- [ ] Registro de release ejecutado; cinco cortes declarados
