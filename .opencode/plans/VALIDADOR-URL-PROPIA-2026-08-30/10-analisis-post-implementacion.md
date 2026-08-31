# Análisis Post-Implementación — VALIDADOR-URL-PROPIA-2026-08-30

> **Estado**: FASE-A completada 2026-08-30 — siguiente: FASE-B
> **Plan**: VALIDADOR-URL-PROPIA-2026-08-30
> **Versión objetivo**: 4.74.0
> **Creado desde la concepción** (executor v2.17.0 §4): cada fase llena sus secciones AL CIERRE.

## Resumen de Ejecución (llenar al cierre de cada fase)
| Fase | Sesión | Estado | Iteraciones | delegate_task | Notas |
|------|--------|--------|-------------|---------------|-------|
| Preparación | 2026-08-30 | ✅ | ~30 | No | Paso 0 ejecutado: memoria + QMind `iah-cli-lecciones` (2 queries) |
| FASE-A | 2026-08-30 | ✅ | ~28 | No (DIRECTO) | TDD rojo→verde: 45/45 contratos (23 def test_); baseline real 14 rojos preexistentes registrada; 28/28 canonicalización; validaciones 7/7; smoke CLI exit 2 |
| FASE-B | — | ⏳ | — | Sí (2 subagentes) | |
| FASE-C | — | ⏳ | — | Sí | |
| FASE-D | — | ⏳ | — | Mixto | |
| FASE-VERIFY | — | ⏳ | — | No (DIRECTO) | |
| FASE-RELEASE-4.74.0 | — | ⏳ | — | Sí (delegable) | |

## Matriz de Verificación de Hallazgos (llenar en FASE-VERIFY)
| # | Hallazgo / Gap | Expected | Real | Status |
|---|----------------|----------|------|--------|
| GA-1 | Colapso de identidad: URLs OTA producen target_id compartido | v4complete/onboard/execute/deploy rechazan URL OTA con exit 2, mensaje claro, sin red/API | — | ⏳ |
| GA-2 | Scraper emite datos de tercero con confianza arbitraria | Guard aborta antes del scrapeo; capa datos protegida (assert_own_site) | — | ⏳ |
| N1 | Contaminación cruzada de onboarding por netloc | Imposible: la URL OTA ya no entra al pipeline | — | ⏳ |
| N2 | ADR de OTA entra al motor financiero | Imposible: rechazo previo al fallback de ADR | — | ⏳ |
| N3 | last_url propaga URLs envenenadas | No se persisten bloqueadas; reinyección rechazada con mención del estado | — | ⏳ |
| N4 | Coste Places API con queries basura | Rechazo antes de cualquier llamada API (probe P1: duración < 30 s) | — | ⏳ |
| N6 | Identidad duplicada (onboarding_controller) | Fix ortogonal: no se tocaron los normalizadores; guardián AST cubre las superficies de entrada | — | ⏳ |
| N8 | hook-pdf sin superficie para guard | Validación sobre `report_json["url"]` (probe P6) | — | ⏳ |
| AC3/AC8 | No-regresión tradicional | 28/28 canonicalización + E2E Salento Real equivalente al baseline H2 | — | ⏳ |

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

## Métricas de Ejecución (llenar al cierre)
| Métrica | Valor |
|---------|-------|
| Tests nuevos totales | +23 def test_ (45 casos parametrize) tras FASE-A |
| Tests finales (def test_) | — (FASE-RELEASE: conteo con grep/collect-only) |
| Regresiones nuevas | 0 (verificado FASE-A vs baseline de 14) |
| Coherence E2E Salento Real | — (baseline H2: 0.88) |
| Probes Don Julio superados | —/11 |
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

## Checklist de Cierre (llenar en FASE-RELEASE)
- [ ] Todas las fases ✅ en `06-checklist-implementacion.md`
- [ ] Matriz de verificación completa (FASE-VERIFY)
- [ ] Métricas finales llenas
- [ ] Lecciones INCLUIR persistidas en memoria del proyecto + 10-analisis re-ingerido a QMind
- [ ] CHANGELOG + GUIA_TECNICA + VERSION sync 4.74.0
- [ ] Contexto disparador archivado en `.opencode/context/Historico/`
