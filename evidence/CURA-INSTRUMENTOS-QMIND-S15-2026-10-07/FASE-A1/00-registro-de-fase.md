# Registro de fase — FASE-A1 (CURA-INSTRUMENTOS-QMIND-S15-2026-10-07)

**Sesión:** 2026-10-08 · **HEAD medido al abrir:** `d8a7d80720837ec33b0109e351a20ae9ea9b8466` (los tres commits
documentales de la preparación ya estaban sobre el tip; el prompt avisaba «el HEAD de esta sesión es otro:
re-medir» y la línea de dependencia citaba `98c190e`, que quedó como antecedente)
**Paridad:** `git rev-parse origin/master` = `git ls-remote origin refs/heads/master` = `d8a7d80` (medido, no de memoria)
**Árbol:** worktree con 13 rutas untracked **ajenas** (`12 briefing/FASE-*.md` del plan padre archivado y
`evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-E2E/captura_stdout.txt`), excluidas de toda acción y de todo
conteo (maestro §5 S-CIM-7, sigue vigente).

## Cortes y estado

Implementación terminada → verificación terminada → cierre documental → **listo para revisión** → espera de
autorización. El `git commit` no estaba ejecutado al cerrar esta nota: los cinco cortes se sostienen sin commit. Después, en la misma sesión, llegó la instrucción literal «Git Commit + L3 + Push» y se ejecutó. **Sello:** commit `63b944a` con los ocho checks del hook versionado en verde, revisión profunda L3 **sin hallazgos** y rango empujado `d8a7d80..63b944a` (paridad verificada con `git ls-remote`); 30 rutas (16 modificadas + 14 nuevas), 1165 inserciones y 97 supresiones. AC1 y AC2 están landed y publicados.

**Presupuesto (unidad declarada, no comparable con el instrumento canónico).** El instrumento
`evidence/FASE-D/measure_iterations.py` sigue **FUERA DE SERVICIO** (R2.1) y no se reintentó. Contado a mano sobre
las llamadas de esta sesión: **≈70 `tool_use`**, por encima de la referencia de 60. El exceso se declara como
checkpoint, no como fase adicional (contrato §R2). En qué se fue lo que el plan no presupuestaba: tres inserciones
de cierre que exigían anclas de prosa envuelta (la línea `**Punto de\nreanudación:**` del README del plan no casaba
con su cita de una línea), el guard extra del escritor ante cuerpo no resoluble, y la corrección del resumen de
`main()` que la propia migración volvió falso.

## Qué se midió

| Punto | Valor | Instrumento y árbol |
|---|---|---|
| Quick de apertura | todos verdes, `EXIT=0` | `venv/Scripts/python.exe scripts/run_all_validations.py --quick`; crudo `quick_apertura.txt`; el número lo imprime la corrida |
| PRE selección literal | `23 passed`, `EXIT=0` | `venv/Scripts/python.exe -m pytest tests/test_validate_qmind_writeback_escritura.py -v`; crudo `tests_baseline_pre.txt`; **intérprete venv 3.13.3** (la preparación corrió con el Python del sistema) |
| POST misma selección | `31 passed`, `EXIT=0` | mismo comando e intérprete; crudo `tests_baseline_post.txt`; **resta 31 − 23 = 8 = tests nuevos de ESTA fase** |
| Funciones `def test_` | 23 → **31** | `grep -cE "^\s*def test_"` sobre el archivo |
| Regresión de vecinos | `90 passed`, `EXIT=0` | `tests/test_verify_qmind_context_freshness.py` + `tests/quality_gates/governance_numbers`; crudo `hermanos_regresion.txt` |
| Par de shas del padre (re-confirmado en disco) | crudo `3d2184fb2822f38d3b8fe97d55d565d10027373256fd63feb40fa226ee73d28e` (124.280 B) · publicado `1f0ee6e52f008e7413846039e244a8a242b472ba93e59bc933af2bb47e7286e0` (125.198 B) | `sha256sum` sobre disco; `git show 83a6dc2:<ruta>` casa con el crudo → el delta **+918 B** es del saneado, no de una edición posterior |
| Mutantes | M1, M2 y M3: los tres con sensibilidad demostrada (copia intacta verde / copia mutada roja) | copia aislada en `temp/mutantes_a1/mount` (el worktree vivo **nunca** se mutó); corrida **re-tomada sobre el estado final del instrumento** (sha256 disco `979ea64b2109…`, idéntico antes y después del montaje); ver `mutantes-resumen.txt` |
| Arnés de scratch | borrado al cerrar, con su crudo y su comando archivados | los dos auxiliares de esta fase (`temp/mutantes_a1/run_mutantes.py` y `temp/contador_muestra.py`) vivieron bajo `temp/` (excluido por declaración de Git) y se eliminaron al terminar; lo que producen **no** queda solo en el scratch: la sensibilidad de los tres guardas y la forma del `[CONTADOR]` están fijadas por dientes versionados de `tests/test_validate_qmind_writeback_escritura.py` (M1 → `cuerpo_editado`/`rojo_manda_sobre_la_abstencion_de_migracion`, M2 → `instanea_editada_sin_re_subir_es_vencido`, M3 → `registro_graba_sha_cuerpo`, contador → `los_tres_estados_del_contador_no_se_colapsan`) |
| Contador del verificador | `[CONTADOR] 2 vigente(s): 1 dictaminada(s) por cuerpo, 1 con fidelidad remota medida, 1 NO-EVALUABLE por migracion, 0 sin observacion local … 1+1+0==2` | muestra offline con doble del CLI en memoria (`contador_muestra.txt`): **cero subidas, cero descargas remotas** |

## Estado de los artefactos

- `scripts/validate_qmind_writeback.py`: `REGISTRO_ESQUEMA` 1.1, `raiz_de_planes()`, `registrar_publicacion()` con
  el parámetro `cuerpo` obligatorio, `verificar_contenido()` con guarda de migración → guarda de cuerpo → gate de
  registro → capa D2, `[CONTADOR]`, y dos ramas del resumen de `main()` según haya o no población gobernada.
- `tests/test_validate_qmind_writeback_escritura.py`: +8 dientes; las tres llamadas a `registrar_publicacion()`
  adaptadas al parámetro nuevo; **ninguna aserción vieja re-bajada**.
- `.opencode/qmind-writeback/instantaneas/README.md`: re-escrito por su dueño humano (prosa no regenerable por
  escritor). El esquema de nombres queda declarado pendiente para A2.
- `.opencode/qmind-writeback/registro.json`: **intacto**. Sus dos entradas del padre siguen en schema 1.0, sin
  `sha_cuerpo` y sin back-fill; ningún diente lo editó (uno lo prueba por bytes antes/después).
- Ninguna subida, descarga o borrado en el notebook; `AGENTS.md`, `.cursorrules`, `VERSION.yaml`, el workflow, los
  hooks y la numeración de checks del runner no se tocaron; ningún documento del plan padre archivado fue editado.

## Consecuencias declaradas (para que las fases siguientes no las redescubran)

1. **AC6 sigue sin ser evaluable sobre las entradas `1.0`.** La guarda de migración termina en `continue`, así que
   el bloque `[DUPLICADO-VIGENTE]` no se recorre para ellas: el rojo de la era G solo aparecerá cuando haya una
   entrada 1.1 en el registro (AC10) o cuando A3 gobierne la huésped explícitamente. Dueño: FASE-A3.
2. **El texto del gate de registro cambió** («la instantanea publicada en disco … no casa con el sha256 … que
   declara el registro») para que el diente viejo siga afirmando lo que afirma; la aserción no se tocó y el mutante
   M2 demuestra que el diente ahora lo sostiene ese gate. Lección nueva `L-CIM.1`.
3. **El resumen de `[17/18]` mentía sobre su cobertura con población mixta**; ahora distingue «no goberna ninguna
   publicación» (población vacía) de «NO-EVALUABLE en alguna publicación (ver el [CONTADOR])». Lección nueva
   `L-CIM.2`.
4. Modo completo **no** se corrió como certificación propia (L-V2.2); lo hace FASE-RELEASE con su crudo.
5. Verificación en el árbol del commit (L-VCF-15): los 31 dientes se re-corrieron sobre HEAD (crudo `post_commit_en_head.txt`) y la identidad del instrumento publicado se comprobó por sha256 del **blob** contra el archivo que se mutó (`979ea64b…`): si casan, la evidencia de los tres mutantes corresponde a los bytes que están en el tip.

## Erratas que cobra el sello (medidas, no heredadas)

- **La fila de REGISTRY quedó corta.** `log_phase_completion.py` la escribió con `--archivos-mod 13 --archivos-nuevos 13`, medidos antes de los últimos retoques documentales; al commit entraron **30 rutas** (16 modificadas + 14 nuevas). El escritor es aditivo y **no** se re-ejecuta sobre una fase cerrada, así que el delta se declara aquí y no se re-registra.
- **DOMAIN_PRIMER no viajó.** `doctor.py --regenerate-domain-primer` corrió y el derivado quedó byte-idéntico a HEAD; por eso `.agent/knowledge/DOMAIN_PRIMER.md` no aparece entre las rutas del commit. Precedente del mismo resultado en el CHANGELOG de la tanda JEV.
- **Seis crudos de consola son CRLF en disco y LF en el blob.** `quick_apertura.txt`, `quick_cierre.txt`, `tests_baseline_pre.txt`, `tests_baseline_post.txt`, `contador_muestra.txt` y `hermanos_regresion.txt` nacieron de un `>` sobre stdout de Python (cp1252/CRLF bajo Git Bash) y `core.autocrlf=input` los normalizó al indexar: una verificación por sha256 de esos archivos debe hacerse sobre `git show`, no sobre disco.
- **El `README.md` de `instantaneas/` viajó en el mismo commit que la cura**, que era la cláusula de L-G3 que al cerrar el documento estaba pendiente.

## Derivados regenerados en este cierre, con su escritor

`doctor.py --regenerate-domain-primer` (210 archivos Python, 25 módulos), `build_lesson_index.py` (358 IDs
definidos + 91 sin definición; `[fechas] nombre=347 commit=11 sin_fuente=0`), `log_phase_completion.py` (único
escritor de la fila de REGISTRY, con `--nota` declarando la unidad de sus columnas),
`validate_document_integration.py` (all checks passed) y `run_all_validations.py --quick` (crudo
`quick_cierre.txt`).

**No se corrieron, con motivo:** `validate_opencode_refs.py --fix` — no entraron rutas nuevas bajo `.opencode/`, y
el fixer también edita documentos de **otros** planes (leer el GUIA_TECNICA del padre: reparó 18 referencias en
cuatro archivos, dos fuera del plan), lo que chocaría con la prohibición de editar el plan padre archivado; y
`validate_wiring.py --write-report` — no entraron archivos `.py` nuevos al árbol versionado (se editaron dos
existentes) y el quick lo confirmó verde con su denominador impreso. `validate_plan_citations.py
--update-baseline` **no** se invocó: la corrida imprime «0 nuevas y 0 crecimientos», así que no hubo citas que
registrar.
