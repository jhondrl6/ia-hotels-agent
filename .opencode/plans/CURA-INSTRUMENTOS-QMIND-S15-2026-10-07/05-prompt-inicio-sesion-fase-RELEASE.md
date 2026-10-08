# FASE-RELEASE — Cierre documental, write-back propio y archivado (AC10)

**ID:** CURA-INSTRUMENTOS-QMIND-S15 / FASE-RELEASE
**Objetivo:** publicar la cura como documentación oficial del repo, **usar el writer curado para publicar el
`10-analisis` de este propio plan** (AC10) y archivar el plan en el orden R2.10.
**Dependencias:** A1, A2, A3 y B cerradas (y C si FASE-B la abrió). RELEASE **no modifica código** — si encuentra
un defecto de producto, lo registra con dueño y lo devuelve a otra sesión.
**Complejidad:** MEDIA (sincronización y orden), ALTA en consecuencia (es donde AC10 se juega y donde el plan se
vuelve consultable por el siguiente).
**Skill:** `.agents/workflows/phased_project_executor.md` §4.5, §4.5.6, §4.5.7, R2.5, R2.10; `docs/CONTRIBUTING.md`
Paso 1-6.
**Modo:** DIRECTO para las decisiones; delegable la recolección documental con allowlist expresa.
**R3:** 4 tareas, 0 comandos largos. **Comandos remotos:** `qmind source upload` (la publicación de AC10) **solo**
con autorización literal propia de esta sesión; `qmind source list`/`download` para verificarla.

## Contexto

Este plan cura al instrumento que consume en su propio cierre. **AC10 no es simbólica:** el `10-analisis` de este
plan va a llevar identidades sustituidas en su receta de saneado (o el operador autoriza que no lleve ninguna), así
que es el caso que hoy `[17/18]` no puede dictaminar. Si AC1 o AC2 no landed, AC10 **no puede** dar verde: esa es
su prueba de que el plan cerró su propia meta.

Estado de git medido en la preparación y que esta fase **re-mide**: `origin/master == HEAD` el 2026-10-08 con
`98c190e`, sin tag, y las cuatro fases previas pueden haber sumado commits y un push propio. El número de release
**no está decidido por el plan**: `VERSION.yaml` publica `4.79.0` (padre, 2026-10-07); el operador lo dicta aquí.

### Estado de fases anteriores (se re-medira al abrir)

| Fase | Estado al 2026-10-08 |
|---|---|
| FASE-A1 (AC1, AC2) | ⬜ Pendiente |
| FASE-A2 (AC3, AC4) | ⬜ Pendiente |
| FASE-A3 (AC5, AC6) | ⬜ Pendiente |
| FASE-B (AC7, AC8) | ⬜ Pendiente |
| FASE-C (AC9) | ⬜ Condicional — puede cerrar como «no aplica», y eso es un resultado |

### Lecciones capitalizadas aplicables a esta fase

| ID | Lección | Qué cambia en ESTA fase |
|---|---|---|
| L-QW.4 | Un límite conocido y escrito no se cierra solo: necesita dueño y disparador | AC10 separa **entrega offline** (copia saneada versionada, título propuesto, sha del cuerpo, prueba de sha inverso) de **aceptación remota** (la subida). Sin autorización literal, cierra `PENDIENTE-AUTORIZACION`, nunca «publicado» |
| L-V2.2 | Un verificador no apoya su conclusión en el artefacto de otro gate | El `[17/18]` curado no certifica su propio cierre: se corre el modo completo y su crudo se archiva con el estado de cada check |
| L-ENT.14 | Una prueba de NO-existencia recortada por un `head` no prueba nada | La verificación de la publicación es por **descarga + sha256** con la racha de intentos contada; el censo del plan se publica completo |
| L-VUP-9 | Los comandos delegados deben usar flags comprobados | Antes de subir, `--help` del writer **y del CLI** contra el árbol vigente; ninguna bandera se inventa. El antecedente del padre: `--upload` pelado responde SKIP por título |
| L-G3 | Cambiar un contrato reescribe sus tests y su prosa en el mismo commit | CHANGELOG, GUIA_TECNICA y el `README.md` de `instantaneas/` publican la semántica nueva del registro `1.1`, del slug y de `fuente_id`, sin re-transcribir mediciones de otras fases |
| L-VCF-15 | Un verde del árbol de trabajo no sustituye la prueba en el árbol del commit | Después de cada commit derivado, la verificación se repite sobre el árbol del commit; cada verde lleva la etiqueta de dónde corrió |

## Tareas

### Tarea 1 — Diagnóstico y versionado con el mandato del operador

Re-medir HEAD, paridad y status; leer `VERSION.yaml` y el encabezado de `CHANGELOG.md`; **pedir al operador el
número de release y la autorización literal de la subida** antes de escribir cualquier bloque con encabezado de
versión. Actualizar `VERSION.yaml` con el valor dictado y correr el sincronizador con su check:

```bash
./venv/Scripts/python.exe scripts/sync_versions.py
./venv/Scripts/python.exe scripts/version_consistency_checker.py
```

**Gate:** `log_phase_completion.py` de esta fase se invoca con `--release "$VERSION_AUTORIZADA"` (valor dictado,
nunca un placeholder) y el VERSION SYNC GATE tiene que pasar sin `(!)`.

### Tarea 2 — Documentación oficial

`CHANGELOG.md`: dar encabezado de versión a **los bloques de este plan** (A1, A2, A3, B, C si aplicó, RELEASE) con
Objetivo / Cambios Implementados / Archivos Nuevos / Archivos Modificados / Tests / **Límites publicados**; los
bloques de **otros** planes quedan donde están. `docs/GUIA_TECNICA.md`: la nota técnica del instrumento curado.
`docs/CONTRIBUTING.md` no se toca sin necesidad real. Verificar el registro **sin re-registrar** (el escritor es
aditivo):

```bash
for F in FASE-A1 FASE-A2 FASE-A3 FASE-B; do grep -c "^## $F - " docs/contributing/REGISTRY.md; done
```

### Tarea 3 — AC10: publicar este plan con el writer curado, en el orden R2.10

Primero el paquete offline: copia saneada **versionada** del `10-analisis`, prueba de sha inverso, título propuesto
que conserve el stem del plan, sha del cuerpo. Con autorización literal, y **con el plan aún en raíz**:

```bash
./venv/Scripts/python.exe scripts/validate_qmind_writeback.py --upload CURA-INSTRUMENTOS-QMIND-S15-2026-10-07 --file <copia saneada versionada> --title <titulo nuevo>
./venv/Scripts/python.exe scripts/build_lesson_index.py
git mv .opencode/plans/CURA-INSTRUMENTOS-QMIND-S15-2026-10-07 .opencode/plans/Archives/
./venv/Scripts/python.exe scripts/build_lesson_index.py
./venv/Scripts/python.exe scripts/validate_opencode_refs.py --fix
./venv/Scripts/python.exe scripts/validate_plan_citations.py --update-baseline
```

Después, **verificación por descarga + sha256** (no por título, no por `SKIP`) con la racha contada, y el censo
completo del plan. Sin observación, el estado es NO-EVALUABLE con su motivo; nunca se pinta de VENCIDO ni de
publicado. El resultado y sus shas viven en `E/FASE-RELEASE/` y en `registro.json` — **una vez publicado el cuerpo,
no se re-edita**: re-escribir shas vencería su propio cuerpo (consecuencia que el padre ya pagó).

### Tarea 4 — Validaciones finales, DOMAIN_PRIMER y sello

`doctor.py --context` (verificar, no regenerar, en RELEASE), `validate_document_integration.py`,
`validate_governance_numbers.py`, quick y **modo completo** con el crudo archivado y el estado de cada check,
incluidos los tres que el cierre del padre dejó rojos (`Tests`, `[17/18]`, `[18/18]`) con su dueño actual: `[18/18]`
sigue fuera de alcance (deuda S-CIM-1 del maestro) y AC6 puede dejar un rojo **verdadero** declarado con dueño (S-CIM-2).
Ninguno de los dos se tapa. Sello de la fase con el tip que estampa, la L3 si se corrío y el rango empujado.

## Post-ejecución (OBLIGATORIO)

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-RELEASE \
    --fecha 2026-10-08 --desc "CURA-INSTRUMENTOS-QMIND-S15: release y write-back propio con el writer curado" \
    --release "$VERSION_AUTORIZADA" --auto-sync \
    --archivos-mod "$ARCHIVOS_MOD_MEDIDOS" --tests "$TESTS_MEDIDOS" --check-manual-docs
```

`--archivos-mod` se mide **después** de los fixers derivados y contando lo que `git` cuenta (los renombrados son
rutas). Después: 09/10/00/06/dependencias/README con el estado real, CHANGELOG y GUIA_TECNICA ya convertidos a la
versión dictada, derivados regenerados, quick verde, y la declaracion de los cinco cortes con el auto-reporte de
presupuesto.

## Criterios de Completitud (CHECKLIST)

- [ ] Versión dictada por el operador y sincronizada; VERSION SYNC GATE sin `(!)`; ningún encabezado de versión inventado
- [ ] AC10 legible en su artefacto: `registro.json` con `sha_cuerpo`, `fuente_id` y slug único, y verificación por descarga + sha con su racha; o `PENDIENTE-AUTORIZACION` declarado sin simular éxito
- [ ] `[17/18]` con su dictamen impreso sobre **este** plan (vigente por cuerpo, NO-EVALUABLE con motivo, o rojo verdadero con dueño) — nunca verde por ausencia
- [ ] Orden R2.10 respetado y probado: write-back con el plan en raíz, índice antes y después del `git mv`, refs y citas re-ancladas en el mismo commit
- [ ] Modo completo corrido con crudo archivado; los tres rojos heredados del padre re-mididos y atribuidos con dueño
- [ ] Registro verificado sin re-registrar; nada del plan padre archivado fue editado
- [ ] El plan quedó **archivado** bajo `Archives/` dentro del mismo cierre (R2.5) y sus documentos congelados
- [ ] Post-ejecución completo; quick verde; CHANGELOG/GUIA_TECNICA coherentes con su fuente (09 §D)

## Restricciones

- **No modifica código fuente ni templates.** Si AC10 exige tocar el writer, eso es un defecto de las fases A y se
  devuelve con dueño.
- La subida y el push son acciones remotas con autorización literal **propia** cada una; el hecho de que el paso
  esté en el orden no las habilita. `qmind source delete` no se invoca.
- No tocar `AGENTS.md` ni `.cursorrules` sin instrucción literal expresa (el clasificador bloquea su commit).
- No re-transcribir mediciones de otras fases: cada cifra vive en 09 §D, en su test o en su crudo.

## Prompt de ejecución

```
Actua como ejecutor de fases del repo C:\Users\Jhond\Github\iah-cli (rama master), en espanol y sin acentos en
el mensaje de commit.

Lee 01-plan-maestro.md §1 y §4, 04-contrato-ejecucion.md, 00-lecciones-capitalizadas.md §2 y §4, dependencias-fases.md, 05-prompt-inicio-sesion-fase-RELEASE.md y el workflow canónico.

Ejecuta SOLO FASE-RELEASE del plan .opencode/plans/CURA-INSTRUMENTOS-QMIND-S15-2026-10-07, y solo con todas las
fases previas cerradas.

OBJETIVO: publicar la documentacion oficial, usar el writer curado para publicar el analisis de este propio plan y
archivar el plan en el orden del executor.

TAREAS: 1) version dictada por el operador y sincronizacion. 2) CHANGELOG, GUIA_TECNICA y registro verificado sin
re-registrar. 3) AC10 con paquete offline, autorizacion literal, verificacion por descarga y sha y orden R2.10.
4) DOMAIN_PRIMER verificado, quick y modo completo con crudo, sello de la fase.

CRITERIOS: el registro muestra sha_cuerpo, fuente_id y slug unico; el dictamen de la capa de contenido nombra
cuerpo o abstencion con motivo; ningun rojo se tapa.

RESTRICCIONES: sin editar codigo, sin source delete, sin subir ni empujar sin autorizacion literal propia, sin
tocar AGENTS ni .cursorrules, sin re-transcribir mediciones ajenas.

```
