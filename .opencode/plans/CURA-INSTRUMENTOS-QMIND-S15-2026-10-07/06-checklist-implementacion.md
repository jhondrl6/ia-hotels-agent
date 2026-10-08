# Checklist de implementación — CURA-INSTRUMENTOS-QMIND-S15 (2026-10-07)

Estado al 2026-10-08, medido contra HEAD `98c190e`. Una fase por sesión (R1); ninguna casilla de fase pendiente se
marca como hecha por adelantado. Las cifras que imprime una corrida **no** se copian aquí: viven en
`09-documentacion-post-proyecto.md` §D, en su test o en su crudo.

## Etapa 1 — Preparación (ESTA sesión)

- [x] Paso 0 ejecutado por **tres capas** y por **dos ejes** (síntoma y superficie de cierre) → `00-lecciones-capitalizadas.md` §1, con 10 consultas re-ejecutables
- [x] ≥3 candidatos descartados con motivo (§3, siete filas) y reserva de serie propia `L-CIM` declarada (§3bis)
- [x] Cobertura declarada con su verificador y su límite (§4), estado real de QMind medido (3 consultas, una con 0 chunks registrada como sin-hallazgos)
- [x] Estado del mandato **revalidado** contra el tip actual: dos filas refutadas y re-ancoradas, cuatro confirmadas con medición nueva, una rectificada por lectura (`01-plan-maestro.md` §1)
- [x] Anclajes de código re-validados **por símbolo** antes de citarlos (R2.2): ningún `archivo:linea` en el plan
- [x] FASE-A dividida por R3 (seis ACs en una fase eran más de cuatro tareas) en A1/A2/A3 por parejas de acoplamiento real
- [x] Criterios de activación de FASE-VERIFY medidos → **no aplica** (maestro §3)
- [x] Un prompt por fase con sus cuatro tareas, sus lecciones copiadas de §2 del `00` y su lista de lectura en la forma canónica
- [x] `dependencias-fases.md` con grafo, tabla de conflictos y la dependencia dura A1→A3 leída del flujo de control
- [x] `04-contrato-ejecucion.md` con límites, presupuesto (R2.1, instrumento FUERA DE SERVICIO), reglas de mutantes y cierre incremental en 8 pasos
- [x] `09` y `10` creados **desde la concepción** del plan, con estructura vacía y **sin** declaración de cierre (la fila de `validate_plan_closure.py` no se dispara)
- [x] Baselines de apertura archivados: `E/FASE-0/quick_apertura.txt` (13/13, EXIT 0) y `E/FASE-0/pre_seleccion_apertura.txt` (1 failed / 26 passed, EXIT 1, intérprete declarado)
- [x] Auto-reporte de presupuesto con unidad declarada y corte usado (`E/FASE-0/00-registro-de-fase.md`)
- [x] Trabajo ajeno untracked **excluido y declarado**, no tocado (maestro §5 S-CIM-7)
- [x] Commit, L3 y push — autorizados por el operador en la misma sesión: ⟦**Sello 2026-10-08, misma sesión:** llegó la instrucción literal «Git Commit + L3 + Push». Commit `b536748` con los ocho checks del hook versionado pasados, revisión profunda L3 **sin hallazgos** y rango empujado `98c190e..b536748` (paridad verificada con `git ls-remote`). No se re-escribe la frase original: registra el estado del árbol al cerrar el documento.⟧

## Etapa 2 — Implementación

### FASE-A1 — AC1 y AC2 (⬜ Pendiente)

- [ ] PRE re-medido con HEAD, status, quick y la selección literal
- [ ] `registrar_publicacion()` escribe `sha_cuerpo`; `schema_version` 1.1; `cargar_registro` tolera entradas 1.0
- [ ] Migración sin back-fill: entrada sin campo → NO-EVALUABLE con motivo, nunca VENCIDO ni verde
- [ ] `verificar_contenido()` decide vigencia cuerpo contra cuerpo, conserva el gate `e["sha256"] != sha_inst` y el contrato D2
- [ ] Diente contrario: copia saneada con crudo intacto → antes `[VENCIDO]`, ahora vigente
- [ ] Diente de vigencia real: cuerpo editado después de publicar → VENCIDO
- [ ] Cuatro estados no colapsados (R2.9) y contador publicado por el verificador
- [ ] 23 dientes viejos verdes **sin re-bajar ninguna aserción**
- [ ] Mutantes archivados con restauración por sha256, ejecutados sobre el instrumento versionado
- [ ] `README.md` de `instantaneas/` actualizado por su dueño humano en el mismo commit
- [ ] Cierre incremental del contrato (8 pasos) con registro propio y quick verde

### FASE-A2 — AC3 y AC4 (⬜ Pendiente)

- [ ] No arranca si A1 no cerró
- [ ] Slug con sha (o correlativo) sin colisión entre publicaciones ni con `README.md`, y legible
- [ ] Dos publicaciones del mismo plan dejan dos byte-exactos distintos, cada entrada casa con el suyo
- [ ] `fuente_id` parseado de la tabla `Key: value` en **las dos ramas** de `do_upload()`
- [ ] Parseo fallido → estado «id no capturado» + censo; **contador de subidas de la corrida = 1**
- [ ] Ninguna subida real ejecutada; ninguna salida con enlace firmado persistida
- [ ] Cinco mutantes con su par rojo/verde y restauración por sha
- [ ] Cierre incremental con registro propio y quick verde

### FASE-A3 — AC5 y AC6 (⬜ Pendiente)

- [ ] Dependencia dura con A1 verificada antes de empezar
- [ ] `--upload Archives/<PLAN>` publica con clave `plan_dir.name`; `--upload <PLAN>` con el plan archivado corta `[FAIL]` nombrando la ruta buscada
- [ ] `cuerpo_del_plan()` resuelve las dos raíces y su ausencia es NO-EVALUABLE, nunca VENCIDO
- [ ] Todo diente de rutas montado en `tmp_path` con `--plans-dir` y `--registro`, sin tocar el registro real
- [ ] Censo del notebook publicado completo (sin `head`), con racha de intentos si la red falló
- [ ] AC6 cerrada por una de sus dos vías **escrita en evidencia**: rojo declarado con dueño y sha, o `vigente-historica` con autorización literal
- [ ] Nada borrado en el notebook; modo completo corrido con crudo archivado, sin auditarse con el check recién curado
- [ ] Cierre incremental con registro propio y quick verde

### FASE-B — AC7 y AC8 (⬜ Pendiente)

- [ ] Diagnóstico publicado **por cada `i` divergente**: tupla `fuente_fecha` de A y B, documento dueño, tier ganador
- [ ] Tres hipótesis candidatas medidas (reloj del corpus / entorno del clon / cambio de población) con su confirmada y sus dos descartadas
- [ ] Banda reproducida contra el HEAD de la sesión, no contra la medición del mandato
- [ ] Cura sin tocar `scripts/build_lesson_index.py`; si la exige, se abre FASE-C y B no edita el generador
- [ ] `REV_CONTROL_DEFECTUOSO` sigue anclado a la revisión fija; ninguna aserción convertida en pertenencia; ningún baseline re-fijado
- [ ] Mutante que apaga la gobernanza nueva devuelve el rojo; restauración por sha256
- [ ] Cortes de entorno declarados NO-EVALUABLE con la ruta buscada, no como divergencia hallada
- [ ] Hermandades re-corridas (16 y 36 funciones) con par pre/post y resta comprobada
- [ ] Cierre incremental con registro propio y quick verde

### FASE-C — AC9 (⬜ Condicional: solo si B la abre con su fila escrita)

- [ ] Fila de B que la abre, citada en la evidencia
- [ ] Cura en `_plan_date`/`build()` con decisión escrita y alternativas rechazadas con su medición
- [ ] Los tres tiers de `[fechas]` con su diente; `SIN-FUENTE` no colapsa con `commit`
- [ ] 4 + 16 + 36 funciones verdes; verificación repetida sobre el árbol del commit
- [ ] Par del índice regenerado en el mismo commit que la cura
- [ ] Si B **no** la abrió: esta lista se cierra con la declaración «no aplica» y nada se ejecuta

## Etapa 3 — Cierre

### FASE-RELEASE (⬜ Pendiente)

- [ ] Versión dictada por el operador y sincronizada; VERSION SYNC GATE sin `(!)`; `--release` con el valor real, nunca placeholder
- [ ] CHANGELOG con encabezado de versión **solo** para los bloques de este plan; GUIA_TECNICA con la nota técnica
- [ ] Registro verificado por grep y **no re-registrado**
- [ ] AC10: paquete offline completo; subida **solo** con autorización literal propia; verificación por descarga + sha256 con racha contada
- [ ] Orden R2.10 respetado: write-back con el plan en raíz → índice → `git mv` → índice otra vez → refs → citas → quick
- [ ] `doctor.py --context` (verificar) y no regenerar a mano; `validate_document_integration.py`; `validate_governance_numbers.py`
- [ ] Modo completo con crudo archivado y los tres rojos heredados del padre re-medidos y atribuidos con dueño
- [ ] Sello de la fase estampa **lo que imprimió su propia corrida** (tip, L3 si se corrió, rango empujado)
- [ ] Plan archivado bajo `Archives/` dentro del mismo cierre (R2.5)

## Controles transversales del plan

- [ ] Ningún documento del plan padre archivado fue editado en ninguna fase
- [ ] Ninguna identidad de cliente se propagó a documentación, commits ni al notebook
- [ ] Ninguna fase tocó `AGENTS.md`, `.cursorrules` o `VERSION.yaml` (salvo RELEASE con mandato)
- [ ] Ningún `.py` nuevo se escribió bajo `evidence/`
- [ ] Todo commit (si llega la autorización) lleva sus derivados regenerados en el mismo commit
