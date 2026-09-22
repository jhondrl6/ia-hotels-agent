# FASE-B — criterios de completitud, uno por uno, con su medición

Cerrada el **2026-09-21** sobre HEAD `74d8ff5` y **commiteada el 2026-09-22 en `647f436`** (46 archivos,
+4.412/−97), que se apoya sobre el commit ajeno `eecf246`. Los HEADs citados en las filas de abajo son el
árbol sobre el que cada medición se tomó, no el del commit (R2.3). Cada fila cita el artefacto donde un
humano lo vería sin abrir el código (R2.4). Techo alcanzable: `VERIFICADO OFFLINE` con su rojo o su
mutante en disco.

| Criterio del prompt de fase | Estado | Dónde se lee / comando |
|---|---|---|
| «Los cinco tests pasan; **ninguno** cubre dos estados» | ✅ **53 casos en 6 archivos** (los 5 nombrados por el prompt + `test_decision_client_mutation_guards.py`, como hizo FASE-A con el suyo). Un estado por archivo: `…no_configurado.py` nunca provoca `ILEGIBLE` (ni llega a un proveedor que conteste), `…ilegible.py` declara en su docstring que el proveedor **sí** está configurado, `…contract_forma.py` solo observa `RESUELTO`. Dentro del archivo de `NO-CONFIGURADO`, un test exige además que las **tres causas** del mismo estado tengan `motivo_clase` distintas, para que no colapsen entre sí | `run_tests.txt`; `./venv/Scripts/python.exe -m pytest tests/quality_gates/decision_client -v` |
| `contract.txt` demuestra el rojo al alterar la forma y el verde con la forma actual (AC8) | ✅ el **mismo** test, dos corridas: verde `exit 0`; rojo `exit 1` contra una copia de `falso_forma.py` a la que se le quitó `"confidence": 0.91`, con `RespuestaIlegible` de 2 motivos. Que caigan **esos** guards y no otros se comprueba en el proceso padre (la anchura del terminal del hijo trunca los motivos) | `contract.txt`, `mutation/mutante_M-AC7-campos-conocidos.txt` |
| `costura.json` reporta `files_changed_to_add_provider`, con su valor o su explicación (AC9) | ✅ valor **1**, medido por sha256 sobre la frontera copiada (puerta incluida): `agregados = [falsos_proveedores/falso_segundo.py]`, `modificados = []`. No hubo que explicar un número mayor porque no lo hubo. Y el `1` no vale si la puerta devuelve siempre el mismo módulo: los dos proveedores se despachan y **contestan distinto** | `costura.json`, `extensibilidad.txt` |
| Cero llamadas de red en toda la fase: **verificable, no afirmado** | ✅ tres instrumentos independientes (`cero-red.txt`): guard autouse que hace explotar `socket.socket`/`create_connection`/`getaddrinfo`/`gethostbyname` en **todos** los casos, con prueba de que el guard está puesto **y** de que la costura llega a `RESUELTO` con él armado; denegatoria AST de 19 módulos capaces de hacer red sobre la puerta y sus proveedores; y `find_spec` del SDK en el venv del producto (`typesafe/jev/httpx2/tenacity` → AUSENTE). Además: 0 comandos de larga duración ejecutados (R3) y ningún comando de `v4complete`/`v4audit` | `cero-red.txt`, `run_tests.txt`, `faseB_baseline_pre.txt` unidad 9 |
| Ninguna evidencia ni log contiene credencial alguna, **ni parcial ni enmascarada** | ✅ En esta fase no existe credencial alguna (ningún proveedor real), y la puerta solo publica `credencial.presente` (bool). Dos tests lo afirman: que del volcado no salen el valor, **ni su longitud, ni sus 6 primeros/últimos caracteres**, y que `evaluar()` no filtra la clave al resultado. `provider_status` es lo que entra en la evidencia | `cero-red.txt` §Credenciales, `informe.json` → `provider_status.RESUELTO.credencial` |
| `--quick` verde **sin** haber tocado su composición (AC16) | ✅ 11/11 en los dos lados con `exit 0` (`faseB_quick_pre.txt` / `faseB_quick_post.txt`), `grep` de `[N/11]` y de los 7 pasos del hook idénticos, y `git diff` **vacío** sobre `run_all_validations.py`, el hook, `build_lesson_index.py` y `validate_governance_numbers.py` (esta última se consumió como heredera, no se reescribió). **Con un rojo propio intermedio declarado**: tras registrar la fase cayó `[3/11]` por la fecha de `REGISTRY.md` y se resolvió con su writer (`sync_versions.py --rule registry_last_update`), no a mano — segunda reproducción del conflicto de los dos escritores (FASE-A lo documentó; dueño y nota en `baseline-pre-post.md`) | `baseline-pre-post.md` §Rojo propio intermedio, comando de la unidad 10 del par |
| `.agents/` y los planes vivos intactos (AC17) | ✅ `git status --porcelain .agents/` vacío; 98.694 y 6.123 bytes sin cambio. No se tocó ningún `05-prompt-*.md` ajeno, ni `.agents/workflows/**` | `faseB_baseline_post.txt` unidades 8 y 11 |
| Herencia de FASE-A re-utilizada, no reinventada | ✅ `coverage_basis` con el mismo esqueleto (`archivos_escaneados`, `poblacion`, `excluidos_por_directorio`, `limites`, `comando`, `medido_el`) y el tri-estado con `motivo_clase`. **Diferencia declarada**: el `status` del escaneo es binario porque el `AUSENTE` y el `LECTOR-FALLIDO` de esta puerta viven en la resolución del proveedor y ahí el tercero se llama `estado_lector` — no se colapsó con `NO-CONFIGURADO` | `import_scanner.txt` → `coverage_basis`, `informe.json` |
| Post-ejecución completa, incluido el índice regenerado en el mismo commit | ✅ **cerrado el 2026-09-22 con la instrucción literal del operador («Commit»)**: `647f436` llevó **dentro** el par `.md`+`.json` (`git show --numstat 647f436` → `LECCIONES-INDEX.md` 24+/17−, `lecciones_index.json` 100+/14−) y los **7** checks del pre-commit pasaron en esa corrida, así que `[6/7]` encontró la pareja fresca y no cortó. Hasta el 2026-09-22 este criterio estaba en ⚠️ **parcial por autorización, no por olvido**: los seis documentos escritos (`dependencias-fases.md`, `README.md`, `06-`, `09-`, `10-`, `00-` con su balance §6), `log_phase_completion.py --fase FASE-B` ejecutado y el índice regenerado en el árbol (**330 IDs** definidos + 51 sin definición al cerrar B; eran 325 al cerrar FASE-A — sube porque esta fase define L-VCF-6 a L-VCF-10, que es A6 golpeando otra vez: la cifra caduca al escribirla, así que se re-mide y se publica). De ese cierre queda **una** cosa fuera y declarada: `EVALUACION-JEV-TYPESAFE-2026-09-21/dependencias-fases.md`, ajena, sin `git checkout` sobre ella | `git show --numstat 647f436`, `git status --porcelain`, salida de `build_lesson_index.py --check`, `docs/contributing/REGISTRY.md` |

## Lo que la fase **no** cerró (para que FASE-C no lo lea como cerrado)

- **Push**: sigue **sin autorizar** — el commit de la fase (`647f436`) y su barrido de citas (`612efd0`)
  están en el árbol local, así que la paridad contra `origin/master` era `0/2` al commitear la fase y
  quedó en **`0/3`** el mismo día (medida con `git rev-list --left-right --count origin/master...HEAD`;
  cada commit documental suma uno, por eso se re-mide). Por delante de esta fase está el commit ajeno
  `eecf246`, también sin empujar.
- **Rutas ajenas**: al cerrar la sesión de fase había **tres** sucias (`EVALUACION-JEV-TYPESAFE-2026-09-21/dependencias-fases.md`,
  `.opencode/context/Refuerzo.md` y `ROADMAP.md`, esta última aparecida durante la sesión, mtime 22:17:38).
  Las dos últimas se las llevó la otra sesión en `eecf246`; lo único que quedó **fuera** del commit de
  FASE-B es `EVALUACION-JEV-TYPESAFE-2026-09-21/dependencias-fases.md`, sin `git checkout` sobre ella
  (es trabajo en curso de otra sesión, no basura que limpiar). Detalle en `baseline-pre-post.md`
  §Rutas ajenas.
- **La población que el propio commit movió, y el archivo que nadie había excluido**: al commitear, los
  `.py` rastreados por git pasaron de **678** (PRE/POST medidos el 2026-09-21) a **691** —los
  **13** `.py` de esta fase—, así que la fila «la fase no commitea `.py`» de la tabla pre/post quedó
  refutada por el propio commit y está rectificada con su nota. Y al reconciliar las dos poblaciones de
  AC6 quedó el residuo: el escáner ve **692** y git **691**; el `+1` es
  `.venv-wsl/bin/activate_this.py`, un archivo de entorno que entra en el denominador porque
  `.venv-wsl` **no está** en `ARCHIVOS_EXCLUIDOS_DE_LA_POBLACION`. No se arregló en este barrido
  (tocar la puerta obliga a re-ejecuciones de sus 53 casos y sus mutantes): quedó como **S11** en
  `10-analisis-post-implementacion.md`, con el 0 de AC6 intacto porque ese archivo no importa el SDK.
- **D7** (activar el proveedor) y con ella la comparación entre proveedores: sigue debida, con su
  disparador cumplido en la parte que gobernaba a AC9 («que AC9 haya cerrado en verde la costura»).
- **S10** (nueva, abierta por esta fase): dónde vivirá el `import` del SDK cuando D7 se active. No se
  decidió aquí porque hacerlo era reinterpretar una restricción del plan en silencio (L-VCF-9).
- **Presupuesto con instrumento** (R2.1): sigue fuera de servicio — `find . -name "*.jsonl"` = 0 en el
  workspace, medido hoy. No se publicó una cifra de `tool_use` aproximada: la métrica se retiró y se
  declaró la unidad contable en disco, que es lo que R2.1 manda cuando el instrumento no corre.
- Los estados `NO-CONFIGURADO`/`ILEGIBLE` sobre el **árbol real** no se ejercitaron con un proveedor
  de verdad: se ejercitaron con los dos proveedores falsos y con rutas en `tmp_path`. Un verde de
  fixture no prueba el camino de producción, y aquí el camino de producción está prohibido por el
  contrato (cero red), así que esa límite es el diseño de la fase, no un olvido.
