# Análisis Post-Implementación — CURA-INSTRUMENTOS-QMIND-S15 (2026-10-07)

> **Estado**: preparación cerrada el 2026-10-08 contra HEAD `98c190e` — diseño aprobado contra código vivo y dos
> filas del mandato refutadas por medición. FASE-A1 ejecutada el 2026-10-08 contra HEAD `d8a7d80` (AC1 y AC2
> landed, **commiteadas y empujadas** tras la instrucción literal «Git Commit + L3 + Push» de la misma sesión: commit `63b944a` con los ocho checks del hook versionado en verde, revisión profunda L3 **sin hallazgos** y rango empujado `d8a7d80..63b944a` (paridad verificada con `git ls-remote`)). **Addenda de la enmienda 2026-10-08:** esa banda es el primer push; la fase quedó publicada en `d8a7d80..67b7e2f` (sello `15f4fdd` y addenda `67b7e2f`, cada tanda con su L3 sin hallazgos). El tip que lee esta línea es el que imprima `git ls-remote origin refs/heads/master`. Las
> fases A2, A3, B, C y RELEASE siguen pendientes.
> **Plan**: `.opencode/plans/CURA-INSTRUMENTOS-QMIND-S15-2026-10-07/`
> **Versión objetivo**: no decidida por el plan. `VERSION.yaml` publica `4.79.0` (release del padre, 2026-10-07);
> el número lo dicta el operador en FASE-RELEASE y se invoca con `--release "$VERSION_AUTORIZADA"`.

**Advertencia de lectura:** este archivo **no** declara cierre del plan. `validate_plan_closure.py` (pre-commit)
corta si aparece una declaración de cierre conviviendo con filas pendientes.

## Resumen de Ejecución

| Fase | Sesión | Estado | Iteraciones | delegate_task | Notas |
|---|---|---|---|---|---|
| Preparación | 2026-10-08 | ✅ Cerrada, commiteada (`b536748`) y empujado `98c190e..b536748`, L3 sin hallazgos | auto-reporte con unidad declarada (R2.1: instrumento FUERA DE SERVICIO) — ver `E/FASE-0/00-registro-de-fase.md` | 0 delegaciones de trabajo; 1 lectura delegada (inventario `read-only` del control S15 y del generador) cuyas cifras se re-midieron en el agente principal antes de publicarse | Cero código, cero escrituras remotas. Dos filas del mandato refutadas: el tip (ya empujado, cuatro commits más) y el corpus del control S15 (20 rutas cambiadas bajo `.opencode/`) |
| FASE-A1 | 2026-10-08 | ✅ Cerrada, **commiteada y empujada**: commit `63b944a` con los ocho checks del hook versionado en verde, revisión profunda L3 **sin hallazgos** y rango empujado `d8a7d80..63b944a` (paridad verificada con `git ls-remote`); HEAD medido `d8a7d80` al abrir, paridad por `git ls-remote`. **Banda completa al cerrar la enmienda: `d8a7d80..67b7e2f`** (sello `15f4fdd` y addenda `67b7e2f`, L3 sin hallazgos en las tres tandas) | auto-reporte con unidad declarada: **≈70 `tool_use`** contados a mano sobre las llamadas de la sesión (instrumento canónico FUERA DE SERVICIO, R2.1) — **excede la referencia de 60 y se declara checkpoint, no fase adicional**; detalle en `E/FASE-A1/00-registro-de-fase.md` | 0 delegaciones: la fase es DIRECTA por contrato (§delegate_task) | AC1 y AC2 landed: `sha_cuerpo` + schema 1.1 en `registrar_publicacion()`, puerta cuerpo-contra-cuerpo en `verificar_contenido()` con el gate de registro y D2 conservados, `[CONTADOR]` publicado. PRE 23 passed / POST 31 passed, resta 8 = dientes de esta fase; tres mutantes con su par intacto/mutado sobre copia aislada y el worktree vivo intacto por sha256. Cuatro consecuencias declaradas en el registro de fase, la primera para A3 — **resuelta por DA-CIM.9 el 2026-10-08, ver §Seguimientos** |
| FASE-A2 | ⬜ Pendiente | ⬜ Pendiente | ⬜ | ⬜ | AC3 + AC4; no arranca sin A1 |
| FASE-A3 | ⬜ Pendiente | ⬜ Pendiente | ⬜ | ⬜ | AC5 + AC6; dependencia dura con A1 por flujo de control |
| FASE-B | ⬜ Pendiente | ⬜ Pendiente | ⬜ | ⬜ | AC7 diagnóstico + AC8 cura |
| FASE-C | ⬜ Condicional | ⬜ Condicional | ⬜ | ⬜ | AC9 solo si B abre la fila |
| FASE-RELEASE | ⬜ Pendiente | ⬜ Pendiente | ⬜ | ⬜ | AC10 write-back propio + archivado |

## Matriz de Verificación de Hallazgos

Se llena al cierre de la última fase de implementación (FASE-VERIFY no aplica en este plan: maestro §3).

| # | Hallazgo | Expected | Real | Status |
|---|---|---|---|---|
| H-1 | `verificar_contenido()` comparaba sha(instantánea) contra sha(cuerpo crudo), así que ninguna subida saneada puede dar verde | Medido 2026-10-07 por el padre y re-confirmado el 2026-10-08: crudo `3d2184fb2822…` (124.280 B) vs publicado `1f0ee6e52f00…` (125.198 B), crudo sin editar desde `83a6dc2` | Re-medido al cerrar A1 sobre `d8a7d80`: crudo `3d2184fb2822f38d3b8fe97d55d565d10027373256fd63feb40fa226ee73d28e` (124.280 B) y publicado `1f0ee6e52f008e7413846039e244a8a242b472ba93e59bc933af2bb47e7286e0` (125.198 B); el `git show 83a6dc2` de la ruta archivada casa con el disco | ✅ confirmado **y curado** por AC2 en FASE-A1 (diente contrario con el blob `d8a7d80` corriendo el guard viejo) |
| H-2 | El slug `[:120]` pisa la instantánea de la publicación reemplazada | Medido 2026-10-08: **un** archivo en `instantaneas/` para **dos** entradas con shas distintos; el archivo casa con `1f0ee6e52f00…` | ⬜ | ⬜ confirmado; los bytes de la entrada `reemplazada` están perdidos (deuda S-CIM-3) |
| H-3 | `fuente_id` se publica vacío en las dos ramas de `do_upload()` | Confirmado por lectura del emisor; y por lectura de la memoria de referencia: la respuesta del CLI es tabla, no JSON | ⬜ | ⬜ su cierre es AC4 |
| H-4 | `--upload Archives/<PLAN>` ya resuelve hoy; lo que falta es el diente y el rojo nombrado | Rectificación del mandato, medida por lectura de `main()` y `cuerpo_del_plan()` | ⬜ | ⬜ AC5 re-escrita como gobernar, no construir |
| H-5 | El rojo `DUPLICADO-VIGENTE` de la era G está **detrás** del rojo de vigencia | Confirmado por flujo de control: el bloque huésped es inalcanzable mientras el gate de cuerpo corte `continue` | ⬜ | ⬜ AC6 depende duramente de AC2 |
| H-6 | El control S15 pierde por clasificación dependiente del corpus/entorno | Reproducido 2026-10-08 contra `98c190e`: 1 failed / 26 passed, mensaje `- mtime + nombre` | ⬜ | ⬜ su diagnóstico es AC7 |

## Lecciones Aprendidas

Formato: qué pasó / por qué / qué lo previene + pertinencia (INCLUIR = viaja a la memoria del proyecto y al
notebook mediante su write-back autorizado; EXCLUIR = queda solo aquí).

### Lecciones capitalizadas de planes anteriores (espejo de `00-lecciones-capitalizadas.md` §2)

| Lección | Aplicación en este plan |
|---|---|
| L-QW.1, L-QW.2, L-QW.3, L-QW.4 | Diseñan AC1-AC6 y la forma de AC10 (entrega offline vs aceptación remota). Definidas por el hermano `VERIFICADOR-ESCRITURA-QMIND-2026-09-20` |
| L-PF6, L-PF10 | Los tres estados que la migración y el parseo no pueden colapsar |
| L-T4A.5, L-VUP-5, L-V2.1 | La forma de los dientes: mutante sobre el símbolo real, aserción que pierde nombrada |
| L-V2.2 | El modo completo se corre y su crudo se archiva; el check curado no se auditó a sí mismo |
| L-V2.3 | Dos dientes leen la **fuente** de `run_all_validations.py`: re-atar antes de re-numerar |
| L-VCF-15 | El control se ejecuta sobre el generador commiteado en la revisión fija, no sobre HEAD |
| L-ENT.12 | El contador que el verificador exige de sí mismo, publicado |
| L-ENT.14 | Censos e inventarios sin `head` ni tubería que recorte |
| L-G3 | Schema 1.1, tests y prosa (`README.md` de `instantaneas/`) en el mismo commit |

### Lecciones nuevas de este plan (serie `L-CIM`, reservada; se llena al cerrar cada fase)

Ninguna al cerrar la preparación. **Sin cuota:** «sin lecciones nuevas» es un resultado válido para una fase
documental. Lo que esta sesión sí produjo fueron **mediciones que refutan premisas heredadas** (maestro §1), que
quedan registradas como tales y no infladas a lecciones.

| ID | Enunciado (una línea) | Qué lo produjo en A1 | Pertinencia |
|---|---|---|---|
| L-CIM.1 | Cuando un verificador tiene dos guardas locales que emiten la misma etiqueta, la guarda que se conserva tiene que seguir nombrando lo que afirma el diente viejo: si no, el diente muerde por la rama equivocada y el mutante de la otra guarda pasa desapercibido. | Al retirar la comparación instantánea-vs-cuerpo, el diente `test_instanea_editada_sin_re_subir_es_vencido` quedó sostenido por el gate de registro, y su aserción pedía la frase «la instantanea publicada». Se re-escribió el **texto** del gate (nunca la aserción) y el diente nuevo de vigencia niega en contra («que declara el registro» no debe aparecer) para que cada rojo se atribuya a su guarda | INCLUIR |
| L-CIM.2 | La abstención se publica por entrada, no por corrida: un resumen que dice «no goberna ninguna publicación» con población mixta miente sobre la cobertura que el propio verificador acaba de medir. | La migración `1.0` introdujo una población donde unas entradas se dictaminan y otras se abstienen; el resumen de `[17/18]` conservaba la frase del caso vacío. Se bifurcó el texto y el `[CONTADOR]` publica los cuatro conteos con su suma | INCLUIR |

## Seguimientos abiertos

| Tema | Estado | Acción futura |
|---|---|---|
| `[18/18]` invocado sin `--strict` (deuda S-2 del hermano) | FUERA DE ALCANCE, nombrada | maestro §5 S-CIM-1: dueño operador, disparador una AC propia |
| Rojo `[DUPLICADO-VIGENTE]` de la era G tras AC2 | DECLARADO con dos salidas | maestro §5 S-CIM-2; la vía (a) requiere autorización literal |
| Las entradas `1.0` salen NO-EVALUABLE **con `continue`**, así que tampoco llegan al bloque `[DUPLICADO-VIGENTE]`: el rojo de la era G sigue sin evaluarse mientras el registro solo tenga entradas viejas | **DECIDIDA 2026-10-08 por el operador (Caso A, vía a1): gobernar el bloque huesped tambien en el camino de migracion (DA-CIM.9).** Queda MEDIDA en A1 por flujo de control y deja de ser una consecuencia que A3 deba redescubrir: es subtarea 3b de su prompt, con especificación, tres dientes y mutante | dueño FASE-A3 (AC6, subtarea 3b); su disparador era la gobernanza explícita de la huésped y ya está dictado — una entrada `1.1` en el registro (AC10) sigue siendo el otro camino, no la decisión tomada |
| Byte-exacto perdido de la entrada `reemplazada` | NO RECUPERABLE | maestro §5 S-CIM-3; se publica en CHANGELOG con la fila del registro |
| Limpieza retroactiva de `TRIBUNAL-OFFLINE-2026-09-09` | FUERA DE ALCANCE | maestro §5 S-CIM-4 |
| Packs de briefing de este plan | NO GENERADOS, declarado | maestro §5 S-CIM-5 |
| Trabajo ajeno untracked (12 `briefing/FASE-*.md` del padre y un crudo de FASE-E2E) | EXCLUIDO y preservado | maestro §5 S-CIM-7; commit propio y separado si el operador lo pide |
| Modo completo con los tres rojos heredados del padre | MEDICION DEL PADRE, referenciada | maestro §5 S-CIM-8; se re-mide en el RELEASE de este plan |
| `historial` del corpus: la fila S15 dice que «un `[FAIL]` en un clon con CRLF no es S15» | VIVA como segundo disparador de FASE-B | AC7 la mide; si cae ahí, la receta de clonado viaja con su propia batería |

## Métricas de Ejecución

Referencia, no transcripción: los valores viven en `09-documentacion-post-proyecto.md` §D y en los crudos de
`E/FASE-0/` (apertura) y de cada fase. El número de checks del quick y del modo completo lo imprime la corrida
(`validate_governance_numbers.py` lo contrasta); ningún documento de este plan lo fija.

## Decisiones Arquitectónicas

| ID | Decisión | Rationale | Alternativas rechazadas | Fase |
|---|---|---|---|---|
| DA-CIM.1 | Curar por separación de las dos preguntas (`sha_cuerpo` + puerta cuerpo-cuerpo), no por `--sanear` en el writer | **Dictada por el operador, no se reabre.** El writer no conoce la política de identidades de cada cliente y un saneado automático en el emisor crearía una segunda verdad sobre qué era publicable | `--sanear` en el writer; comparar sha(instantánea) contra sha(copia saneada) — eso no responde «¿el plan cambió?» | Preparación |
| DA-CIM.2 | `schema_version` 1.0 → 1.1 con campo nuevo y **sin back-fill** | Rellenar hacia atrás con el sha de hoy fabrica verde por construcción y borra la historia de un cuerpo editado antes de la primera corrida del migrador | Migración calculando `sha(cuerpo hoy)`; exigir re-publicación de todas las entradas | Preparación |
| DA-CIM.3 | Ante parseo fallido del id: **no re-subir**, verificar por censo | La idempotencia es por título y un título nuevo nunca existió: re-subir crea el duplicado que L-QW.2 mide | re-intento ciego del `upload`; dejar `fuente_id` vacío sin estado | Preparación |
| DA-CIM.4 | AC6 cierra declarando con dueño, no tocando el notebook | `source delete` es irreversible sobre contenido publicado y exige decisión escrita aparte; el registro a mano por una fuente ajena también pide autorización literal | borrar la era G; marcarla `reemplazada` sin su sha | Preparación |
| DA-CIM.5 | FASE-A dividida en A1/A2/A3 por parejas de acoplamiento real | R3: seis ACs con mutante propio son más de cuatro tareas; el corte por acoplamiento (qué función toca cada una) mantiene cada fase verificable en una sesión | dejar FASE-A con seis ACs; dividir por tamaño arbitrario | Preparación |
| DA-CIM.6 | La cura del generador pertenece a FASE-C con su propio AC | Es código de producto con 16 + 36 funciones hermanas y alimenta `[6/8]` de cada commit | meter el cambio del generador dentro de FASE-B | Preparación |
| DA-CIM.7 | AC10: el plan se publica a sí mismo con el writer curado, y su certificación está separada en entrega offline / aceptación remota | Es la única prueba de que la cura cierra su meta en el caso real (cuerpo con identidades sustituidas), sin convertir el mandato en una subida no autorizada | certificar solo con fixtures; simular el éxito remoto | Preparación |
| DA-CIM.8 | FASE-VERIFY no se activa | Criterio 2 de §4.6: cero ejecuciones E2E en el plan; fallando uno de los tres, la etapa no aplica | añadir una sesión de certificación cruzada sin output E2E | Preparación |

## Checklist de Cierre (llenar en FASE-RELEASE)

- [ ] AC1-AC8 certificadas con su par verde/rojo archivado; AC9 si la fase se ejecutó
- [ ] AC10 con publicación verificada por descarga + sha256, o `PENDIENTE-AUTORIZACION` declarado sin simular éxito
- [ ] CHANGELOG con la versión dictada, GUIA_TECNICA, REGISTRY verificado sin re-registrar
- [ ] Orden R2.10 completo y plan archivado bajo `Archives/` (R2.5)
- [ ] Modo completo con crudo archivado y cada rojo con dueño
- [ ] `00-lecciones-capitalizadas.md` con la aplicación efectiva real de sus filas
