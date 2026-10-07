# FASE-F — resultados, cortes y deuda con dueño

Fecha: 2026-10-06. HEAD de partida: `9127735` (punta de `origin/master`, FASE-E sellada).
Mandato ejecutado: `05-prompt-inicio-sesion-fase-F.md`. **Sin commit, sin push, sin tag, sin QMind**: el mandato
de ejecución no los autorizaba y los cinco cortes se sostuvieron sin ellos (contrato §Límites y precedencias).

⟦**Rectificación por la orden posterior «Git Commit + L3 + Push» (2026-10-06):** commit único **`20a07ae`**
(39 archivos, +2.342/−81, 8/8 checks del pre-commit), **L3 sobre `9127735..20a07ae` con 0 hallazgos**, push del
mismo rango con paridad **0/0** verificada por `git ls-remote`. Lo de arriba fue el estado bajo el mandato de
ejecución y se conserva como histórico; lo que sigue vigente sin autorización: **tag, QMind, rotación,
`DOMAIN_PRIMER` y la errata S-F7**.⟧

## Cortes consumados (los cinco, sin commit)

| Corte | Estado | Como se midió |
|---|---|---|
| Implementación terminada | HECHO | 9 rutas cerradas sobre `modules/utils/redaction.py` + verificador ampliado; `git status`: 23 M + 2 nuevos |
| Verificación terminada | HECHO | PRE 372 passed / 10 skipped → POST par 373 / 10 (misma selección de 6 rutas, mismo entorno, ambos EXIT 0); POST extendido 419 / 10; **9/9 mutantes rojos por fuga detectada**, 9/9 restaurados por sha256, 9/9 verdes tras restaurar. **Sello de regresión completa sobre el árbol definitivo: 1 failed / 5.064 passed / 41 skipped / 4 xfailed en 390,64 s (EXIT 1)** — `regresion_completa.txt`. El único rojo es ajeno y orden-dependiente: `jev_pilot/test_jev_pilot_deepseek_brazo.py`, que en su archivo aislado pasa **15/15** (mismo rojo que declararon C y D). Quick final **13/13, EXIT 0** (`quick_final.txt`), con el Secrets Check leyendo **1.057 salidas** bajo `output/` y `logs/` (16 más que las 1.041 del PRE: las corridas de pytest de esta propia sesión escribieron logs; 0 hallazgos en ambas mediciones) |
| Cierre documental | HECHO | prompt F, checklist (fila F + fila AC13 + el checkbox de revocación), `dependencias-fases.md`, 00 (§Aplicación efectiva F + `L-F-RED`), 09 (§Cierre FASE-F), 10 (§FASE-F), CHANGELOG bajo `## [Sin publicar]`, `docs/GUIA_TECNICA.md`; `log_phase_completion.py` sin GAP; derivados regenerados con su escritor |
| Listo para revisión | HECHO | Quick 13/13 (lo imprime la corrida), `validate_document_integration.py` all checks passed, SHA del árbol sin promesa (no hay commit que pinear) |
| Espera de autorización | CONSUMIDA PARCIALMENTE | commit, L3 y push ejecutados por orden literal (`20a07ae`, rango `9127735..20a07ae`, 0 hallazgos, paridad 0/0). Quedan pendientes de instrucción propia: **tag, write-back a QMind, rotación de credenciales y `DOMAIN_PRIMER`** |

## R2 — presupuesto e instrumento

**FUERA DE SERVICIO (R2.1).** El instrumento del plan (`evidence/FASE-D/measure_iterations.py <transcript> <corte-ISO>`)
pide el transcript de la sesión y su acceso no está disponible; es la misma condición que declararon A, G, 0, C,
D y E. No se estimó cumplimiento ni se comparó con la referencia de 60.

**Auto-reporte en unidad propia, separado del instrumento:** ~62 intervenciones de herramienta hasta «listo para
revisión» (el corte que esta sesión tenía autorizado: sin commit), 6 corridas de pytest, 2 quicks, 1 arnés de
9 mutantes, 2 regeneraciones de derivados en cadena, 1 reparación de un daño propio en documento (abajo).
No comparable con tramos medidos por el instrumento.

## Lo que la fase midió sobre su propio instrumento (no sobre el producto)

1. **Un detector ampliado choca con el fixture del corpus viejo, no con el producto** (`L-F-RED`). El patrón
   nuevo `sk-or-/sk-ant-` puso rojo `tests/auditors/test_p5_ac_s1_secret_sanitization.py` en el quick: su
   `SYNTHETIC_OPENROUTER_KEY` empieza con el prefijo y sigue con cuerpo legible, y los patrones viejos lo
   esquivaban por azar (la clase `[A-Za-z0-9]` no tragaba guiones). Se resolvió por construcción del fixture
   (concatenación, como `test_p5_ac_s2_remediacion.py`), **no** estrechando el patrón.
2. **El propio informe de redacción puede volver a filtrar.** Al redactar el CHANGELOG cité el literal del
   fixture que acababa de causar el rojo: el archivo versionado quedó con una cadena que el verificador nuevo
   rechaza. Lo detectó la corrida, no la intención. Corregido a descripción sin literal. Regla práctica: un
   documento que documenta un leak no puede citar el leak.
3. **Daño propio al editar por anclaje de encabezado.** Insertar la sección de F en `09-documentacion-…md`
   usando el encabezado de E como `old_string` sin re-emitirlo borró ese encabezado (el cuerpo de E quedó
   colgando de la sección de F). Reparado con un script binario que restituyó el título y devolvió el orden
   B → E → F; verificado: `git diff --numstat` del archivo = **+38/−0**, o sea solo la sección nueva, con las
   lineas de E intactas. Lección: editar por anclaje exige re-escribir el anclaje; y la verificación del daño
   se hace con el numstat, no leyendo el archivo.
4. **La pata nueva del verificador hay que medirla antes de activarla.** 1.041 archivos bajo `output/` y
   `logs/`, 0 hallazgos con los patrones reales. Sin esa medición el quick habría podido ponerse rojo por una
   exposición histórica ajena a F, y la tentación de «excluir la ruta» habría quedado dentro de la fase.
5. **La rama que nadie ejercita puede estar rota desde que se escribió.** `f"{_MAX_SCAN_BYTES}"` citaba un
   global inexistente desde AC-S2: inexecutable porque ningún archivo versionado llega al umbral (el mayor,
   780.700 bytes). Dos dientes nuevos la ejecutan en `tmp_repo`.

6. **El verde de un árbol no avala lo que se está preparando para publicar.** Al commitear (orden posterior), la
   pata `staged` de `_check_no_secrets` **cortó el commit**: leyó las líneas `+` del diff y encontró literales con
   forma de credencial que el escaneo de archivos versionados nunca había visto, porque **esa pata no aplica la
   exclusión de cuarentena** (`archives`, `evidence`, `.opencode`), tal como lo declara su propio docstring desde
   P5. Los tres literales eran de esta propia fase: el id parametrizado del mutante M9 en `mutantes_crudo.txt` y en
   `run_mutations.py`, y la cita del fixture viejo en `00-…` y `10-…`. Es la verificación que faltaba: 13/13 con
   1.041 salidas leídas y 0 hallazgos **no** probaba que el contenido staged fuera limpio. Saneado sin tocar la
   regla — ids de parametrización descriptivos (`caza-sk-or`, `forma-openrouter`, …), arnés regenerado y prosa que
   describe el prefijo sin reproducir el valor — y el hook volvió a pasar 8/8.

## Deuda declarada con dueño

| ID | Qué | Dueño | Condición para cerrarla |
|---|---|---|---|
| S-F1 | `scripts/preload_prospects_gbp.py` persiste `PlaceData.error_message` en markdown y JSON; llega redactado desde el cliente pero el script no se tocó (fuera de allowlist) | H / VERIFY | un diente sobre el script o decisión escrita de que la redacción en la fuente basta |
| S-F2 | `_query_perplexity` no tiene `try/except` propio; depende del de `_query_provider`, y su rama de consola no tiene diente propio | VERIFY | prueba de consola sobre esa ruta o exclusión declarada |
| S-F3 | la pata nueva lee el instante de la validación; un archivo que aparezca después queda fuera hasta la siguiente corrida. Los 8 checks del pre-commit leen HEAD y `output/`/`logs/` nunca entran al index, así que el hook no puede cubrirlo | RELEASE o deuda permanente | watch/hook con alcance a rutas gitignored, o aceptar el límite escrito |
| S-F4 | allowlist de cuarentena (`archives`, `evidence`, `.opencode`) de P5 sin ampliar ni reducir. **Medido al commitear:** la asimetría es real y tiene consecuencia — el escaneo de archivos versionados excluye esas rutas, la pata `staged` **no** (decisión declarada en el docstring de P5), así que un literal con forma de credencial dentro de la propia evidencia pasa el quick pero corta el commit | operador | decisión expresa: unificar criterios o documentar la asimetría como política (con su fila en `10-analisis`) |
| S-F5 | AC13 quedó verificado **offline**: la integración con captura/snapshot del runner (stdout/stderr reales) es prueba de H | H | la batería de H sobre el runner |
| S-F6 | `credential_status.json` acredita la rotación de 2026-09-18 como afirmación del operador; OpenRouter/Perplexity/PageSpeed/DeepSeek quedan `PENDIENTE-SIN-EVIDENCIA-OPERATIVA` | operador | evidencia operativa sin secreto, o mantener la fila pendiente |
| S-F7 | `log_phase_completion.py` publicó `--archivos-mod 32` y el conteo final medido es **39** (23 modificados + 2 nuevos de producto/tests + 14 de evidencia). El escritor no tiene bandera de corrección y re-correrlo duplica la fila | RELEASE | rectificación en el sello documental del release, no en REGISTRY (precedente: la errata de C, misma causa) |
| S-F8 | `assert_redacted` (el guard fail-closed del sumidero) **no tiene llamador en el producto de F**: F definió el contrato pero no construyó el runner que lo consume. Está cubierto por dos dientes propios y es la boca que H debe cerrar al capturar stdout/stderr y el snapshot | H | llamada real del guard en el writer de capturas de H, con su diente |
| S-F9 | Dos limpiezas del sumidero se hicieron **después** de arrancar la primera regresión completa (retirar la forma especulativa `xgoogap-`, el kwarg `channel` sin lector en `redact_and_clip`, un guard que contaba `key=***` como leak con sus dos dientes, y dos frases de docstring): el sello publicado es la **segunda** corrida completa (`regresion_completa.txt`) y la primera queda archivada como `regresion_1_vencida_por_edicion_propia.txt` con su número real — **1 failed / 5.062 passed / 41 skipped / 4 xfailed en 402,11 s, EXIT=1** — declarada vencida por edición propia, no reutilizada como verde | F (cerrado aqui) | ninguna: es la declaración del corte |
| — | `DOMAIN_PRIMER` **no se regeneró**: el mandato de F no autorizó escribir `.agent/knowledge/DOMAIN_PRIMER.md` (está versionado; cada regeneración ensucia el árbol). Se arrastra el checkpoint desde C, como hicieron D y E | RELEASE, con instrucción expresa | `doctor.py --regenerate-domain-primer` solo con mandato de escritura |

## Notas para quien commitee F

- Los packs no se vencen con lo de esta fase: `build_phase_briefing.py --plan REFACTOR-WHATSAPP-ENTREGA-2026-09-18`
  respondió `[SIN-FUENTES] FASE-F: el prompt no declaro lectura`, así que no hay bytes de workflow proyectados que
  reescribir; medido, no asumido (es la trampa de `L-VCF-20`).
- El sha de los commits de F y su rango van al **sello documental de RELEASE**, cobrando la decisión de C/D/E de no
  abrir sellos intermedios por acciones git: un sello que documenta una acción git es a su vez una acción git.
- La nota del §8 del informe y la pila de rangos de C siguen esperando el añadido (`..ea37732`) que no reescribe
  la sede: se cobra en el mismo commit documental del release.
- Si el quick se re-corre después del commit, `[13/13]` compara contra el árbol del commit: commitear los 36
  archivos juntos evita el verde vacío de un árbol a medio publicar.
