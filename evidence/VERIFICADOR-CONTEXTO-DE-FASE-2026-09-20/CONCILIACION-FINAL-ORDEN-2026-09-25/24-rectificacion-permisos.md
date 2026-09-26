# Rectificación de permisos de RELEASE — 2026-09-25

Mandato: «Corrige la ambiguedad». Solo se corrigen instrucciones; no se ejecuta RELEASE ni se concede autorización de escritura central.

## Ambigüedad retirada

El prompt canónico y su copia pegable incluían sync en «OFFLINE (tu mandato)» mientras reservaban permisos para sus destinos. El contrato repetía «Es el cierre propio de la fase». Offline solo significa sin red: no es autorización para escribir.

Las versiones anteriores de los tres documentos se conservan completas en `21-contrato-antes.txt`, `22-prompt-canonico-antes.txt` y `23-prompt-pegable-antes.txt`. `20-permisos-pre.json` registra contenido y mtime del árbol antes de editar, para distinguir este cambio del trabajo preexistente.

## Regla vigente

- C0 precede cualquier escritura de RELEASE: contrastar mandato literal con destinos reales de cada writer. Si falta un destino necesario, detenerse, pedir permiso y declarar preflight incompleto; no cierre offline completo.
- `sync_versions.py --check` no escribe. Sin esa bandera puede modificar los destinos de `scripts/sync_config.yaml`: `README.md` de raíz, `AGENTS.md`, `.cursorrules`, `docs/CONTRIBUTING.md` y `docs/GUIA_TECNICA.md`. El permiso se limita a versión/fecha/codename y debe nombrar los archivos.
- `VERSION.yaml` es entrada, no salida del sync; cambiarla requiere versión y fecha aprobadas. No se propone ni ejecuta un incremento aquí.
- `log_phase_completion.py` escribe REGISTRY; con `--archivos-mod` también escribe `docs/contributing/.last_doc_phase.json`. Se deben autorizar ambas salidas si se usa esa invocación; no duplicar registros.
- La alineación de política de DOMAIN_PRIMER requiere decisión literal separada. Un permiso de sync no la incluye ni autoriza regenerar el primer.
- Se retiran `--fix` y `--update-baseline` de la secuencia automática. Los checks no escriben; una corrección de corpus pide sus archivos, y nunca se actualiza un baseline para absorber errores.
- Consulta, subida, archivado, commit y push mantienen permisos separados. El contrato y el prompt comparten la cola: últimas escrituras autorizadas → packs → índice → checks.

La petición actual no resuelve C0 de una futura RELEASE: solo exige que esté escrito sin ambigüedad.

## Verificación de esta corrección

Se regeneraron únicamente los packs de CONTEXTO y el par del índice mediante sus escritores; ambos checks, integración documental, referencias, citas, capitalización y quick terminaron con exit 0. Las salidas completas y exits reales están en `26-validacion-permisos.txt`; el informe `25-packs-permisos.json` declara los cinco packs COMPLETO. Se comprobó además la presencia de C0 y de los cuatro prompts explícitos en el pack RELEASE.

`27-frontera-permisos.json` compara contenido y mtime contra `20-permisos-pre.json`: ninguna ruta preexistente modificada fuera de la lista autorizada, ninguna desaparecida y ninguna alta fuera del expediente; HEAD sin cambiar y staging vacío. El delta de los tres documentos se conserva en `28-diff-permisos.txt`. Las garantías se limitan al inventario y al estado PRE/POST, no prueban ausencia de escrituras transitorias ni se deducen de un `git status` limpio.

No se ejecutaron RELEASE, sync en escritura, registro de fases, tests, red, cambios centrales, archivado, commit ni push. C0 de una futura RELEASE sigue sin autorización; esta corrección queda listo para revisión.

## Continuación («ejecución según las modificaciones establecidas»)

**Propagación de C0 a sus consumidores.** El barrido de la frase «tres momentos» dio once puntos. Se
corrigieron los que **contaban permisos**: encabezado y §Tarea 4 de este prompt, las dos apariciones en el
bloque de arranque del `README.md`, la fila `CONTEXTO/RELEASE` de `dependencias-fases.md` y el checklist de
`10-analisis-post-implementacion.md`. Se **dejaron intactas** `09:109` y `dependencias:279`: enumeran
*cierre original / corrección técnica / aceptación* de FASE-B, no permisos — mismo literal, otro asunto.
Renombrar el título del bloque se evaluó y descartó: los `§` que resuelve el generador son los del contrato
(`§Dos momentos del cierre`, `§Carga total y frescura del pack`, `§Orden del cierre`), así que renombrar solo
desincronizaba prosa; se anotó la cuenta vigente (C0 · offline · remoto · traslado) en su lugar.

**Orden y contrato.** `04-contrato-ejecucion.md` añade a su tabla de prohibiciones la fila de escritura de
configuración central y retira `--fix`/`--update-baseline` de `§Orden del cierre`; el prompt hace lo propio
en su bash. Medido en `34-writers-en-bash.json`: **10 líneas de comando** por documento, **0**
invocaciones de writer, y un **control negativo** (inyectar la invocación en un archivo temporal) prueba
que el predicado puede perder.

**Tres comprobaciones propias, retractadas y rehechas.** `31` publicó `evidencia_cerrada_intacta` construido
con `... or True` (verde vacío); `32` buscó `--update-baseline` en todo el texto y contó como invocación la
prosa que lo prohíbe (rojo falso); `33` repitió el error de corte al incluir el bloque ```text del prompt
pegable. `34` es la medida correcta y las supersede. Los tres quedan como antecedente con su motivo.

**Evidencia cerrada verificada por sha256**, no por ausencia en `git status` (`32-frontera-corregida.json`):
FASE-A 15, FASE-B 25, FASE-C 23, FASE-D 29, BLOQUE-B-REMEDIACION 1858, BLOQUE-C-ENMIENDAS 25,
BLOQUE-C-REMEDIACION 30 archivos — **0 modificados** y hash idéntico al inventario previo en los siete.

**Cola y frontera.** Tras las ediciones se re-corró escrituras → packs → índice → ambos `--check` →
integración documental → refs → citas → capitalización → `--quick`: nueve ejecuciones, **todas exit 0**,
cinco packs `COMPLETO` (`30-validacion-coherencia.txt`). Catorce archivos cambiados en estas dos pasadas,
**ninguno fuera del permiso**, ninguno desaparecido, ninguna alta ajena al expediente; HEAD `5817edd` y
staging vacío (`31-frontera-coherencia.json`).

**Estado:** la corrección de permisos está propagada y verificada. **C0 sigue sin autorizar** esta vez como
antes: no se ejecutaron sync en escritura, registro, `--fix`, `--update-baseline`, tests, red, archivado,
commit ni push. Listo para revisión.
