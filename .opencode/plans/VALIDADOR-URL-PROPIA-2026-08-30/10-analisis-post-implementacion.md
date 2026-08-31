# Análisis Post-Implementación — VALIDADOR-URL-PROPIA-2026-08-30

> **Estado**: FASE-B completada 2026-08-31 — siguiente: FASE-C
> **Plan**: VALIDADOR-URL-PROPIA-2026-08-30
> **Versión objetivo**: 4.74.0
> **Creado desde la concepción** (executor v2.17.0 §4): cada fase llena sus secciones AL CIERRE.

## Resumen de Ejecución (llenar al cierre de cada fase)
| Fase | Sesión | Estado | Iteraciones | delegate_task | Notas |
|------|--------|--------|-------------|---------------|-------|
| Preparación | 2026-08-30 | ✅ | ~30 | No | Paso 0 ejecutado: memoria + QMind `iah-cli-lecciones` (2 queries) |
| FASE-A | 2026-08-30 | ✅ | ~28 | No (DIRECTO) | TDD rojo→verde: 45/45 contratos (23 def test_); baseline real 14 rojos preexistentes registrada; 28/28 canonicalización; validaciones 7/7; smoke CLI exit 2 |
| FASE-B | 2026-08-31 | ✅ | ~31 | Sí (2 subagentes) | 47 casos nuevos (35 `def test_`) en 3 archivos; integrado 120 passed (guardián AST 4 superficies + F2 + canonicalización 28/28); regresión hook-pdf/scrapers 76✓+4s, auditor/never-block 125✓+2s; smokes CLI: hook-pdf OTA→exit 2, reporte real Salento Real→exit 0, v4complete OTA→exit 2; validaciones 6/7 (Version Sync = drift documental preexistente, no código) |
| FASE-C | 2026-08-31 | ✅ | ~20 | Sí (subagente probes) | 11/11 probes PASS; regresión 101 passed 0 failed; P6 corregido (--output-dir vs --report-json); P5 verificado: no re-persiste (ensure_url aborta antes de save_state) |
| FASE-D | — | ⏳ | — | Mixto | |
| FASE-VERIFY | — | ⏳ | — | No (DIRECTO) | |
| FASE-RELEASE-4.74.0 | — | ⏳ | — | Sí (delegable) | |

## Matriz de Verificación de Hallazgos (llenar en FASE-VERIFY)
| # | Hallazgo / Gap | Expected | Real | Status |
|---|----------------|----------|------|--------|
| GA-1 | Colapso de identidad: URLs OTA producen target_id compartido | v4complete/onboard/execute/deploy rechazan URL OTA con exit 2, mensaje claro, sin red/API | P1-P4: exit 2, mensaje español nombra plataforma, duración < 30s, sin artefactos en output/ | ✅ C |
| GA-2 | Scraper emite datos de tercero con confianza arbitraria | Guard aborta antes del scrapeo; capa datos protegida (assert_own_site) | P7: UrlNoPropiaError en WebScraper 0 HTTP; P8: UrlNoPropiaError en V4ComprehensiveAuditor 0 Places | ✅ C |
| N1 | Contaminación cruzada de onboarding por netloc | Imposible: la URL OTA ya no entra al pipeline | — | ⏳ |
| N2 | ADR de OTA entra al motor financiero | Imposible: rechazo previo al fallback de ADR | — | ⏳ |
| N3 | last_url propaga URLs envenenadas | No se persisten bloqueadas; reinyección rechazada con mención del estado | P5: estado envenenado → rechazo con mención "estado persistente"; ensure_url aborta antes de save_state — NO re-persiste | ✅ C |
| N4 | Coste Places API con queries basura | Rechazo antes de cualquier llamada API (probe P1: duración < 30 s) | P1-P4: exit 2 instantáneo, sin marcadores de scraping/auditoría en stdout, sin artefactos en output/ | ✅ C |
| N6 | Identidad duplicada (onboarding_controller) | Fix ortogonal: no se tocaron los normalizadores; guardián AST cubre las superficies de entrada | 28/28 canonicalización re-verificado tras B; normalizadores intactos | ✅ B |
| N8 | hook-pdf sin superficie para guard | Validación sobre `report_json["url"]` (probe P6) | P6: hook-pdf con fixture OTA → exit 2, rechazo claro, sin PDF | ✅ C |
| AC3/AC8 | No-regresión tradicional | 28/28 canonicalización + E2E Salento Real equivalente al baseline H2 | P10: 28/28 canonicalización PASSED; regresión 101 passed 0 failed | ⏳ E2E en D |

## Lecciones Aprendidas

### Lecciones capitalizadas de planes anteriores (Paso 0, inyectadas en prompts)
| Lección | Origen | Aplicación en este plan |
|---------|--------|-------------------------|
| TDD contratos ANTES del fix | SR-H2 | FASE-A escribe `test_url_propia_guard.py` rojo antes del guard |
| Fix ortogonal al normalizador | Contexto N9 + SR-D | No tocar `_normalize_url`/`generate_hotel_id`; 28 tests intactos |
| Contratos transversales → AST, no regex | L7 / SR-A | Guardián AST: guard presente en las 4 superficies reales (ensure_url + extract_hotel_data + audit + extract_data) |
| El gap está en el caller: verificar si el helper ya existe | L16 | Guard reusa `_normalize_url()` para el netloc |
| No crear un tercer sistema | DT-3 §7.3 | Semillas OTA (web_scraper.py:523, two_phase_flow.py:716-722) centralizadas en `config/url_blocklist.yaml` |
| Delegación de comando largo + evidencia-first | L30 (RC1-RC2) | FASE-D: v4complete por subagente; evidencia copiada antes del análisis |
| Unit tests no detectan cableado omitido; solo E2E | L29 (RC1-RC2) | FASE-D obligatoria para declarar fixes SUPERADOS |
| L13: onboarding loader solo lee `{--output}/clientes` | COHERENCIA-MODULO-ENTREGA | Reinterpretada en auditoría (F5): el baseline H2 corrió CON defaults → FASE-D corre SIN poblar clientes para preservar la equivalencia AC8 |
| Pytest seguro (fuga ~8GB) | Memoria proyecto | Lotes pequeños, salida a archivo, nunca commercial_documents completa |
| log_phase SIN --release en fases intermedias | L9 | Todos los prompts lo indican |
| Classificar fallos de validación (docs vs código) | L2 vieja | Version Sync → sync_versions.py, no re-correr |
| validate_agents_md.py obligatorio pre-commit final | Memoria CONTRIBUTING | Incluido en FASE-RELEASE paso 11 |

### Lecciones nuevas de este plan (numeración L-VUP-n)
| ID | Qué pasó | Por qué | Qué lo previene | Pertinencia | Fase |
|----|----------|---------|-----------------|-------------|------|
| L-VUP-1 | La baseline "13 rojos" del audit midió 14 en FASE-A T1: `test_function_default_flags` es orden-dependiente (falla en combinación, pasa aislado) | El estado de algunos tests de pricing depende del orden/estado de la sesión pytest, no solo del código | Registrar la baseline con la COMBINACIÓN EXACTA de archivos que se usará para comparar en cada fase; los "fallos nuevos" se juzgan con corridas idénticas | Alta (todas las fases comparan contra baseline) | A |
| L-VUP-2 | El archivo de eventos `--force` es append-only y NO está en .gitignore: los tests lo contaminarían | `MemoryManager.save_state` tiene semántica REPLACE (memory.py:303-318) y main.py:1411 la llama después de ensure_url; JSON Lines es el formato append-only natural | Archivo DEDICADO JSON Lines + fixture snapshot/restore en tests (restaura el contenido previo o elimina el archivo si no existía) | Alta (FASE-B/C también escriben/leen eventos) | A |
| L-VUP-3 | Matching de dominios por substring produce falsos positivos (`bookingbogota.com`) y el patrón `X.*` mal anclado produce falsos negativos/positivos | Los dominios son secuencias de etiquetas; la identidad de plataforma vive en fronteras de punto | Matching por SUFIJO DE ETIQUETAS (split por `.`): patrón plano = etiquetas finales iguales; `X.*` = base alineada en frontera con ≥1 etiqueta después (el TLD); contrato C7 congela los anti-falsos-positivos | Alta (mantenimiento de la blocklist) | A |
| L-VUP-4 | Reusar `_normalize_url()` desde un módulo exige import lazy dentro de la función | `main.py` importa los módulos; un import top-level en `own_site_guard` ciclaría cuando FASE-B cablee el guard en el scraper (main→scrapers→guard→main) — la misma dependencia inversa de N6 | `from main import _normalize_url` DENTRO de `_netloc_de()`; FASE-B debe mantener imports lazy del guard en web_scraper/v4_comprehensive | Alta (FASE-B: cableado en capa de datos) | A |
| L-VUP-5 | Los 16 contratos T1 del track `main.py` salieron VERDES a la primera (cero rojos): una fase "de extensión" que no produce rojo es un falso verde potencial | FASE-A ya ordenaba `ensure_url()` (L1428) antes de `save_state()` (L1433), así que la garantía de orden de AC6 no necesitaba fix — el contrato documenta, no repara | Cuando una superficie no dé rojo, ejecutar un **mutation check** (quitar el guard y comprobar que el contrato se pone rojo): `temp/mutation_check_t1.py` puso rojos M1/M2/M3-execute/onboard/deploy. Sin eso, "ya pasaba" no distingue contrato con dientes de test decorativo | Alta (criterio de cierre de cualquier fase de extensión) | B |
| L-VUP-6 | La delegación funcionó en ejecución y falló en cobertura de diseño: 0 colisiones de archivo, 0 decisiones inventadas por los subagentes, pero el conflicto `--force` vs capa de datos NO estaba en el plan y apareció solo al redactar el brief | Los briefs llevaban la API exacta, los mensajes/exit code congelados y una lista de archivos PROHIBIDOS; el plan, en cambio, asumía que "assert_own_site en scraper/auditor" era mecánico y no había previsto que esos llamadores no reciben `args.force` | Delegar solo lo que ya está decidido y cerrar las decisiones nuevas EN EL PARENT antes de lanzar los subagentes (aquí: D-VUP-B1 implementada y verde antes del brief del Track 2). Coste medido: Track 1 gastó 38 tool calls / ~581 s en un resultado que era "solo tests" → en fases de baja complejidad, evaluar si la delegación paga su propio contexto | Alta (FASE-C/D también son delegadas) | B |
| L-VUP-7 | `UrlNoPropiaError` lanzado por scraper/auditor sería **tragado** por los `except Exception` de sus callers en `main.py` (L568/592/865/1371/1760/1981) y convertiría el rechazo en warning | Los modos de main.py ya envuelven los accesos de red con except amplios (patrón never-block); la defensa en capa de datos solo es efectiva para llamadores FUERA de main (sondas, handlers del harness, uso de librería) | No afirmar en docs que la capa de datos protege dentro del CLI (ahí manda `ensure_url`); si algún día se necesita, añadir `except UrlNoPropiaError: raise` en esos bloques — registrado en Seguimientos. Lección emparentada: NameError silencioso en gate tier_c | Alta (interpretación de AC en FASE-VERIFY) | B |
| L-VUP-8 | `FORZADAS_PROCESO` es estado mutable de módulo y pytest puede alterar resultados según el orden de recolección | Un bypass registrado por un test contaminaría el rechazo que otro test espera | Fixture `registro_forzadas_aislado` (autouse) con snapshot/clear/restore del set + verificación empírica en **orden inverso** de archivos (`temp/fase_b_track1_conjunto_inverso.txt`): 0 fallos en ambas direcciones | Alta (cualquier test sobre estado global de módulo) | B |
| L-VUP-9 | Los prompts de probes deben usar los argumentos CLI reales, no suposiciones | P6 usó `--report-json` (inexistente); hook-pdf usa `--output-dir` para buscar el reporte. El subagente ejecutó fielmente un comando inválido y reportó FAIL sin poder evaluar AC7 | Verificar `--help` del comando ANTES de redactar el probe; o incluir un paso de validación de argumentos en el prompt delegado | Alta (todos los prompts de probes futuros) | C |
| L-VUP-10 | "No re-persistir" ≠ "limpiar el estado previo": el rechazo aborta antes de save_state, así que la URL sembrada permanece en disco | P5: el subagente marcó FAIL porque la URL bloqueada seguía en current_state.json tras el rechazo; pero el criterio AC6 es "no RE-persistir" (no escribir de nuevo), no "limpiar lo que ya estaba" | Distinguir entre "el proceso escribió X" vs "X ya estaba ahí y el proceso no lo tocó"; verificar con spy/diff del archivo ANTES y DESPUÉS, no solo con el estado final | Alta (cualquier probe que evalúe efectos secundarios sobre estado persistente) | C |
| L-VUP-11 | El formato de archivos de eventos persistidos debe documentarse en el plan/prompt | P9: el script de verificación asumió lista (`data[-3:]`) pero el archivo es un dict simple; KeyError silencioso que el subagente reportó como anomalía | Incluir el esquema exacto del archivo en el prompt del probe (o referenciar el contrato TDD que lo define) | Media (probes que inspeccionan artefactos) | C |

## Seguimientos abiertos
| Tema | Estado | Acción futura |
|------|--------|---------------|
| Línea base sucia: **14 tests rojos preexistentes verificados 2026-08-30 (FASE-A T1)** — calculator_v2 ×3, pricing_resolution_wrapper ×9 (+1 vs los ×8 documentados), site_verification_propagation ×1, config_pricing ×1; canonicalización 28/28 verde (`temp/fase_a_baseline.txt`) | REGISTRADO | NO atribuir al plan; las fases comparan contra estos 14 |
| Residuo `test_config_pricing::test_tiers_boutique_min_price` + N10 (pricing.yaml inconsistente) | Fuera de alcance | Decisión separada: ¿test, yaml o ambos contra escalera canónica? |
| RC3: confidence/CMS mide estructura, no identidad de fuente (terceros no blocklisted) | Watchlist | Vigilar con la blocklist versionada; posible plan futuro |
| N5: bug numérico latente en `generar_reporte_ejecutivo()` | Fuera de alcance | Fix de la familia credibilidad numérica |
| N7: higiene main.py (`_audit_handler` ×5, 3 esquemas de identidad) | Fuera de alcance | Candidato a plan de refactor |
| GOOGLE_PAGESPEED_API_KEY inválida | Decisión del usuario (OPS) | Rotación fuera del plan |
| Blocklist maintenance | Al cierre | Fecha de próxima revisión de `config/url_blocklist.yaml` |
| `except Exception` en callers de main.py (L568/592/865/1371/1760/1981) tragaría el `UrlNoPropiaError` de scraper/auditor (L-VUP-7) | REGISTRADO FASE-B | Fuera de alcance: dentro del CLI el enforcement es `ensure_url`. Si un futuro llamador interno necesitara el rechazo duro, añadir `except UrlNoPropiaError: raise` en esos bloques |
| `main.py:247` hardcodea `sys.exit(2)` en vez de `EXIT_CODE_URL_NO_PROPIA` (el valor 2 está congelado por el guardián AST de FASE-A) | Debt menor | Unificar cuando se toque `ensure_url`; hoy hook-pdf sí usa la constante y el guardián AST acepta ambas formas |
| AC7 se evalúa DESPUÉS de leer los 3 archivos fuente (el guard va tras `report_json["url"]`, que exige la carga) | Aceptado | Si alguna vez el reporte fuera potencialmente hostil por tamaño, mover la validación a una lectura previa del JSON |
| `hook-pdf` sin `--url` reinyecta `last_url` en `args.url` (rama L222-229) aunque el comando no la usa: en el smoke A se vio `[HARNESS] 🔄 Usando URL persistente` antes del rechazo AC7 | Quirk preexistente | **FASE-C P6**: sembrar/verificar que el `last_url` del estado NO coincida con la url del fixture de reporte, para que el exit 2 se atribuya a AC7 y no al choke point |
| Gate `version-sync` bloqueó el commit de FASE-B y `sync_versions.py` NO lo despeja: solo reescribe las fechas `last_update`, deja `agents_version: v4.71.0` en AGENTS.md mientras VERSION.yaml marca 4.73.0 (medición 2026-08-31, `temp/fase_b_sync_versions.txt`) | **FASE-RELEASE, bloqueante del commit** | En el paso de bump a 4.74.0 editar además el encabezado `agents_version` de AGENTS.md (y revisar `.cursorrules`/GUIA_TECNICA). NO usar `--no-verify` |
| Conteo global de tests: grep `def test_` en `tests/` = **3677** tras FASE-B vs base documentada 3,631 + 58 del plan = 3,689 | Descuadre documental (no de código) | Conciliar en FASE-RELEASE con el método canónico (`def test_`, no `collect-only`) y actualizar README + AGENTS juntos con la cifra real |

## Métricas de Ejecución (llenar al cierre)
| Métrica | Valor |
|---------|-------|
| Tests nuevos totales | +58 def test_ (92 casos) tras FASE-B: +23/45 en A, +35/47 en B |
| Tests finales (def test_) | — (FASE-RELEASE: conteo con grep/collect-only; grep global de esta sesión marcó 3677 vs 3631 documentado → auditar con el método canónico) |
| Regresiones nuevas | 0 (FASE-A vs baseline de 14; FASE-B vs sus suites dirigidas: integrado 120 passed, hook-pdf/scrapers 76✓+4s, auditor/never-block 125✓+2s; FASE-C regresión dirigida 101 passed 0 failed). **Nota de alcance**: en B NO se re-ejecutó la combinación completa de la baseline de 14 rojos (ordering-dependiente, L-VUP-1) → se re-verifica en FASE-C/VERIFY con la misma combinación de archivos |
| Coherence E2E Salento Real | — (baseline H2: 0.88) |
| Probes Don Julio superados | 11/11 PASS (FASE-C) |
| ACs certificados | —/8 |
| Duración total del plan | — |

## Decisiones Arquitectónicas
| ID | Decisión | Rationale | Alternativas rechazadas | Fase |
|----|----------|-----------|-------------------------|------|
| D-VUP-A1 | Choke point único en `ensure_url()` (auditoría 2026-08-30: `main()` lo llama para TODOS los comandos en L1406; los "modos sin ensure_url" no existen) + defensa en capa de datos y hook-pdf | Enforcement en el límite de entrada (RC4); un solo lugar para mensajes/exit code; guards por modo serían redundancia fosilizada (anti-lección L-PF2/L-NC10) | Guards por comando (duplicación verificada innecesaria); marcaje suave en scraper (Opción B — propaga basura marcada) | A |
| D-VUP-A2 | Guard ORTOGONAL: no cambia `_normalize_url` ni `generate_hotel_id` | 28 tests congelan semántica netloc-only (N9); netloc es correcto para sitios propios | Cambiar normalización para preservar path (rompería identidad SR-D) | A |
| D-VUP-A3 | Blocklist versionada `config/url_blocklist.yaml` (categorías ota/red_social/buscador) | Mantenible sin tocar código; centraliza semillas existentes (no tercer sistema) | Lista hardcoded en main.py; detección heurística de OTA | A |
| D-VUP-A4 | Modo "sin web" (Opción C) fuera de alcance | Es producto nuevo; merece contexto de decisión comercial propio | Construir runner GBP-only ahora | Preparación |
| D-VUP-A5 | Eventos `--force` en archivo DEDICADO append-only `.agent/memory/url_guard_force_events.json` (JSON Lines: {timestamp, url, comando} por línea) | `MemoryManager.save_state` es REPLACE (memory.py:303-318) y main.py:1411 la llama DESPUÉS de ensure_url → borraría el evento; JSON Lines permite append sin read-modify-write | save_state / estado general; JSON array (exige reescritura completa) | A |
| D-VUP-A6 | Import lazy de `_normalize_url` dentro de `_netloc_de()` (no top-level) | Dependencia inversa con main (N6): un import top-level ciclaría al cablear FASE-B el guard en scrapers/auditors que main importa | Import top-level (frágil ante el cableado de FASE-B); copiar el normalizador (tercer sistema) | A |
| D-VUP-B1 | `assert_own_site` registra en `FORZADAS_PROCESO` (set de netlocs) el `--force` concedido en el proceso y **solo** `ORIGEN_CAPA_DATOS` lo consulta para no lanzar | Scrapers/auditors no reciben `args.force`; sin el registro, `v4complete --url <ota> --force` (sonda P9) quedaría abortado por su propio scraper y el bypass del operador sería inútil. Limitarlo a capa de datos preserva intacta la semántica FASE-A (`TestCicloForceReinyeccion` sigue esperando rechazo tras force) | Registro global para todos los orígenes (rompería el contrato C4/ciclo congelado en A); propagar `force` a las firmas de scraper/auditor (7 call sites en main, invasivo); variable de entorno (estado oculto no testeable) | B |
| D-VUP-B2 | hook-pdf: guard sobre `report_json["url"]` dentro de `extract_data(force=False)`, `generate()` reenvía `force`, y `run_hook_pdf_mode` captura `UrlNoPropiaError` ANTES de su `except Exception` con `sys.exit(EXIT_CODE_URL_NO_PROPIA)` | El reporte es input no confiable (N8: hook-pdf no recibe `--url`); sin el catch específico el rechazo caería en el handler genérico y saldría con exit 1, divergiendo del contrato de FASE-A | Validar en `run_hook_pdf_mode` leyendo el JSON (duplica la lógica de carga del generador); dejar exit 1 (rompe la unificación); exigir `--url` en hook-pdf (superficie nueva innecesaria) | B |
| D-VUP-B3 | `origen="report_json"` como cadena libre (sin nueva constante en `own_site_guard`) y guidance específico de hook-pdf impreso desde el CLI | `_mensaje_rechazo` solo special-casea `estado_persistente`: una origen nuevo reutiliza el mensaje congelado de FASE-A sin tocarlo; la explicación "el url viene del reporte" es propia de la superficie, no del guard | Añadir `ORIGEN_REPORT` al módulo (ensancha la API congelada en A); condicionar el mensaje a `comando` (acopla el guard a nombres de CLI) | B |

## Checklist de Cierre (llenar en FASE-RELEASE)
- [ ] Todas las fases ✅ en `06-checklist-implementacion.md`
- [ ] Matriz de verificación completa (FASE-VERIFY)
- [ ] Métricas finales llenas
- [ ] Lecciones INCLUIR persistidas en memoria del proyecto + 10-analisis re-ingerido a QMind
- [ ] CHANGELOG + GUIA_TECNICA + VERSION sync 4.74.0
- [ ] Contexto disparador archivado en `.opencode/context/Historico/`
