# Nota de cierre FASE-E2E — corrida única de `v4complete` (Hotel Don Alfonso)

**Plan**: CURA-COSTURA-TRIBUNAL-2026-10-11 · **Fecha**: 2026-10-12 · **Árbol de apertura**: tip `bce67bc`, `SUCIOS=0`, paridad `0 0`
**Pre-vuelo**: `pre-vuelo.md` (aquí) con su `preflight.json` (sha256 `de570a27…`): **`spawn_autorizado: true`, 13/13 requisitos favorables**
**Corrida**: **UNA sola**, ejecutada por subagente (`Agent`, background) con el comando literal del prompt; EXIT **0**

```
PYTHONUTF8=1 ./venv/Scripts/python.exe main.py v4complete --url https://www.donalfonsohotel.com/ --force-new
```

Duración medida de pared: **~94 s** (spawn 16:55:43 según el subagente; recibo más reciente `2026-10-12T16:57:17`;
artefactos fechados `20261012_165654`/`20261012_165706`). El techo de 900 s del plan no se rozó. No hubo segundo intento
ni re-spawn: el primero terminó con EXIT 0 y output válido.

## 1. Evidencia proactiva (guardada ANTES de verificar — L-VUP-12)

| Artefacto | Ruta en `evidence/…/FASE-E2E/` | Clave |
|---|---|---|
| stdout crudo de la corrida | `stdout-corrida.txt` (368 líneas, 18.221 bytes, sha256 `0e26d540c098a610…`) | la corrida lo escribió por redirect |
| stdout pasado por el sumidero de F | `stdout-corrida-redactado.txt` (17.854 bytes, sha256 `6aff921880d77777…`) | `cambio_por_redaccion: false` — el texto no tiene forma de credencial; la diferencia de bytes es EOL (CRLF→LF), no contenido |
| crudo del preflight y del cierre de evidencia | `preflight-sonda-crudo.txt`, `evidencia-cierre-crudo.txt` | |
| inventario post-corrida con hashes | `inventario_post_corrida.json` (67 archivos, `faltantes_declarados: []`, sha256 `e7e657b9d65d6945…`) | predicado `run_once.preservar_resultado` re-utilizado |
| 26 artefactos de la corrida (01, 02, `v4_audit/` completo, `v4_complete_report.json`) | `corrida/…` con su sha256 por archivo en `evidencia-cierre-crudo.txt` | cada copia pasó `assert_redacted` |
| recibos de extracción del `cache_dir` de producción | `recibos/d66e95d7d92f46a8-llamada-01.json`, `…-cache-02.json` | L-T4A.3: se copian, la cache no se borra |
| YAML derivado + procedencia | `hotel_don_alfonso_onboarding.yaml` (`2990d768…`), `onboarding_provenance.json` (`9e5c5f29…`) | su única procedencia versionable (viven bajo `output/`, gitignored) |

## 2. AC14 leída en los artefactos (no inferida)

| Elemento de AC14 | Dónde se lee | Valor medido |
|---|---|---|
| Onboarding Tier A inyectado | `stdout-corrida.txt:157` | **`✅ Onboarding data loaded: 4 campos confirmados`** — sin `Using defaults` en el log (grep 0) |
| coherence ≥ 0.8 | `corrida/…/v4_audit/coherence_validation.json` y `…_post_gen.json` (sha idéntico `c7f29c9a…`) | `is_coherent: true`, **`overall_score: 0.96`**; en el gate: `Coherence score 0.96 meets threshold 0.8` |
| gate report | `corrida/…/v4_audit/gate_report_20261012_165706.json` | `readiness.status: READY_FOR_PUBLICATION`, `ready: true`, `blocking_issues: []`, 13 `gate_results` todas `passed: true`; 2 warnings (`asset_confidence`, `pricing_compliance` con `operational_floor`) |
| acta del tribunal emitida con los 4 revisores y su report | `corrida/…/v4_audit/acta_revision.json` + `.md`; `revision_diagnostico/assets/alineacion/honestidad.json` | los cuatro Bots con `report_path`; cláusulas `P6.1 PASS, P6.2 NOT_EVALUABLE, P6.3 PASS, P6.4 PASS, P6.5 NOT_EVALUABLE, P6.6 PASS`; `evidence_tier "B+"` con `first_floor_rule.applied: true` |
| recibo con proveedor servido, modelo **pedido** y **firmado**, versión de prompt y usage | `recibos/d66e95d7…-llamada-01.json` | `proveedor_configurado: deepseek`, `proveedor_servido: deepseek`, **`modelo_pedido: deepseek-chat` vs `modelo_firmado: deepseek-flash`** (la etiqueta de serving predicha), `finish_reason: stop`, `latencia_ms: 10790.6`, `usage: 5250 prompt / 3190 completion / 8440 total`, `version_prompt: v2` |
| **estado de la extracción leído del recibo** | idem + `…-cache-02.json` | **`OK_CON_PROMESAS`** con `num_promesas: 42`; `digest_texto` del recibo **casa con el sha256 de la propuesta copiada** (`7328cb42e672516976…`) → el texto extraído es esta propuesta. La segunda extracción sale por **cache** con `proveedor_servido: null` (AC4: un hit no construye proveedor). **No hay hallazgo de extracción no-OK en esta corrida** |
| estado del ZIP | `acta_revision.json → package_evidence` + `stdout-corrida.txt:306,323` | cuarentena `donalfonsohotel_20261012.zip.tmp` (sha256 `dc00cdb94130552b…`, **56 miembros**) → **`suppressed: true`**, `⛔ ZIP SUPPRIMIDO: Tribunal verdict is BLOQUEADO`, y `find output/v4_complete -name "*.zip" -o -name "*.zip.tmp"` devuelve **0** archivos. `blocks_delivery_zip(acta)` medido con la función de `judge.py:52` sobre el acta copiada = **True** |

## 3. Diente de AC19, leído en el acta y no inferido del veredicto

- `verdict: BLOQUEADO` con `corrective_actions` de **dos** entradas **nombradas**: `finding_type: OVER_PRESENTATION`,
  `severity: CRITICAL`, `artifact: 02_PROPUESTA_COMERCIAL.md`, `owner: comercial` — **no** aparece
  `VEREDICTO_BLOQUEANTE_SIN_HALLAZGO`. Las dos líneas coincidentes: `## 🛡️ GARANTÍAS: Protección total para usted`
  y `### 5. Transparencia total`.
- El acta proyecta el estado de extracción por revisor (`extraccion: {estado: OK_CON_PROMESAS, motivo: null}` en
  Bot 2 y Bot 4; ausente en Bot 1 y Bot 3, que no consumen el extractor).
- **Límite declarado**: la extracción de esta corrida salió **OK**, así que la fila nueva de AC19 (CRITICAL bajo
  `INPUT_NOT_EVALUABLE`/`FALLIDO`) **no se ejercitó en flujo real**. Lo que se ejercitó fue la fila clásica
  (`OK_WITH_FINDINGS` + `critical_count: 2` + `recommendation: BLOQUEAR`). La prueba de la fila nueva sigue siendo la de
  FASE-C2 (par rojo/verde y differential en `evidence/…/FASE-C2/`); FASE-VERIFY no puede darla por certificada en E2E.
- **Fresco de AC10 en la propuesta de esta corrida**: 2 CRITICAL emitidos, ambos absolutos de prosa de garantía. El
  precedente de FASE-B predecía **tres** (los dos absolutos **más** la celda «(Verificado)» de la tabla). Medido en
  `revision_honestidad.json`: el tercer finding de Bot 4 es `CG_WARNING_UNDISCLOSED` (**WARNING**, `CG-WHATSAPP-LEAD`),
  no el `LENGUAJE_DE_VERIFICACIÓN` esperado. **Falta certificar en FASE-VERIFY** por qué la celda «Verificado» no salió
  como CRITICAL en esta propuesta (candidatos: el texto ya no está, cambió de fila, o lo filtra `LINEA_DE_TABLA`/
  `MONTO_DECLARADO` — el grupo de lenguaje no se filtra por AC10, así que la explicación no es esa).
- El acta marca **`P6.5 NOT_EVALUABLE`** («Reservada para Bot 4 (honestidad NL) — D-T1.3 opción a») **mientras Bot 4
  corrió, emitió 3 findings con `finding_type`/`clause: P6.5` y su recomendación fue `BLOQUEAR`**. Es la misma forma del
  defecto que AC12 curó para P6.2, pero en la fila de P6.5 y con `source_artifact: null`. No lo cura ninguna AC de este
  plan; se escala con dueño (Operador / FASE-VERIFY) en `10-analisis` §Seguimientos.

## 4. Hallazgos de la fase (registrados, no «arreglados» con una segunda corrida)

1. **`--force-new` es inerte en `v4complete`** (medido en pre-vuelo: su único consumidor es `main.py:773`,
   `run_execution_mode`). La frase del prompt «`--force-new` para garantizar inyección fresca de onboarding» no describe
   el mecanismo. Confirmado en el log real: `[HARNESS] Contexto inyectado: 1 ejecución(es) previa(s) encontrada(s)` y
   la sonda de preflight encontró análisis previo para `donalfonsohotel.com`
   (`output/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/v4_complete`). La corrida **no estuvo aislada de la memoria**; la
   inyección de onboarding la garantizó el YAML en `output/clientes`, no la bandera.
2. **Dos sesiones de memoria se borraron** durante el run: `memory.cleanup_old_sessions(days=20)` (`main.py:1666`)
   alcanzó exactamente los dos archivos que el preflight predijo
   (`.agent/memory/sessions/2026-09-19_3b0f3a94.json`, `…_dfa27c04.json`). Declarado antes de gastar el intento; no es
   reversible y no se intentó revertir nada.
3. **Degradaciones de APIs externas** (no bloqueantes, por diseño ADVISORY): `PageSpeed API timed out`
   (`stdout-corrida.txt:4`, `Status: ERROR` en la sección 3/5), `[STUB] Sin API key SerpAPI`, y el checker de menciones
   de LLM falló con `'NoneType' object has no attribute 'lower'` (`[ADVISORY]`). El run terminó igualmente con su
   contrato de cuatro estados y su recibo.
4. **El crudo llegó a disco sin redactar** porque el spawn fue un redirect de shell, no el `lanzar_unico` de H (que
   redacta antes de disco). Verificado con el sumidero de F: `contains_secret_shape` y `assert_redacted` pasan sobre el
   crudo y la copia redactada es textualmente idéntica. Queda declarada la diferencia de EOL (18.221 → 17.854 bytes).
5. **Inestabilidad de DNS medida en el preflight**: el HEAD de `urllib` (stdlib) falló 3/3 en el mismo proceso en el que
   `requests` —el cliente del pipeline— obtuvo 200 con 142.017 bytes. El requisito `el_dominio_responde` se decide por
   el mecanismo de la corrida y se publicó el contraste con sus fallos (`preflight.json`).
6. El redirecccionamiento `www.donalfonsohotel.com` → `donalfonsohotel.com` es la misma identidad para
   `_normalize_url` (docstring: «Reduce https://www.zione.co/ → zione.co»), así que no activó el checkpoint de
   «dominio distinto».

## 5. Validaciones, cortes y errata del registro de fase

`log_phase_completion.py` se corrió con la lista de `--archivos-nuevos` que dictaba el prompt, ampliada con los
artefactos que la fase efectivamente escribió, y **quedó corta en dos rutas**: `stdout-corrida.txt` y
`stdout-corrida-redactado.txt` no están nombradas en la fila del `REGISTRY.md` (la corrida es aditiva y volver a
ejecutar el escritor apilaría un duplicado, así que se corrige **aquí**, no re-escribiendo la fila). Las 26 copias de
`corrida/` y las 2 de `recibos/` viajan declaradas como ruta de directorio, con su conteo en `evidencia-cierre-crudo.txt`.
Cortes al cerrar: `git status --porcelain=v1 | wc -l` = **21 rutas** (8 modificadas + 13 nuevas, dos de ellas
directorios), `git grep -c -E "^\s*def test_" HEAD -- tests` = **5321** (delta 0), DOMAIN_PRIMER regenerado salió
**byte-idéntico** (no aparece en status), y los dos arneses de scratch (`temp/preflight_e2e.py`,
`temp/evidencia_e2e.py`) se eliminaron. **Sin `git commit`**: los cinco cortes terminan en espera de autorización.


### 5.1 Validaciones y presupuesto

- `run_all_validations.py --quick`: **primera corrida 12/13 con EXIT 1** (crudo en `quick-cierre.txt`). El rojo no era
  del run ni del árbol heredado: lo metió **esta sesión** al escribir en `09` §D una cita numérica de línea
  (`Plan Citations: NUEVO con citas numéricas (1)`), contra R2.2 del maestro («citas: símbolos, nunca `archivo` +
  número»). Curada a símbolo y **re-corrida al cierre**; la cifra vigente es la que imprime el final del mismo crudo,
  y el `[GUARDA]` de la corrida confirma que las 13 etiquetas casan con el `TOTAL` dinámico.
- Delta R2.3: **0 funciones `def test_`** — la fase no añadió código ni tests. Línea base leída en HEAD:
  `git grep -c -E "^\s*def test_" HEAD -- tests` = **5321** (no se mueve).
- Cortes: implementación terminada (pre-vuelo + corrida + evidencia) → verificación terminada (§2 y §3) → cierre
  documental (T3) → listo para revisión → **espera de autorización**. **Sin `git commit` ejecutado.** El único archivo
  nuevo fuera de `evidence/` es el scratch del arnés (`temp/preflight_e2e.py`, `temp/evidencia_e2e.py`), gitignorado y
  excluido por rol del gate de cableado; se elimina al cerrar.
- Presupuesto R2.1 recalibrado **antes** de correr a ~45 tool calls: **excedido**. El auto-reporte de esta sesión es
  **~50 tool calls** (unidad `tool calls`, contadas por el agente, sin instrumento del repo que las mida — el mismo hueco
  que declararon FASE-A/B/C). Lo consumió T0(c) con la opción A: tres re-corridas del arnés (una por truncamiento del
  heredoc, una por un `KeyError` propio, una por el criterio del dominio) y la re-medición del dominio con dos clientes.

### 5.2 Addendum del Operador (2026-10-12, posterior al corte)

La línea de arriba —«**Sin `git commit` ejecutado**»— describe el corte declarado al cerrar y sigue siendo verdad para
ese momento. Después llegó la autorización con la letra **«Git Commit + L3 + Push»**, y la tanda se publicó en
**`fbdee8e`** (padre `bce67bc`, **49 archivos**, `SUCIOS=0` al terminar, `git grep -c -E "^\s*def test_" HEAD -- tests`
reproducido en el árbol del commit = **5321**). El mismo commit lleva el contexto
`CONTEXT-CONTRATO-PLANTILLA-TIER-2026-10-12.md` y el par del índice.

Dos cosas que este addendum declara y que el `git status` del momento no podía:

- **Bytes en disco vs blob**: los sha256 citados en esta nota y en `evidencia-cierre-crudo.txt` son de los **bytes en
  disco** al medir. Con `core.autocrlf` el blob queda normalizado a LF (34 archivos de la tanda avisaron al etapar), así
  que un cotejo `git show <sha>:ruta | sha256sum` **no casa** y no es evidencia de alteración: el cotejo de evidencia
  aquí es disco a disco.
- **El crudo del quick quedó desplazado**: `quick-cierre.txt` conserva la **re-corrida** (13/13) porque la primera
  (12/13) se escribió en la misma ruta y fue sobrescrita; su valor queda afirmado en §5.1 y en esta nota, no en el
  crudo. La corrida con el contexto nuevo ya publicado es `quick-post-contexto.txt` (**13/13, EXIT 0**).

