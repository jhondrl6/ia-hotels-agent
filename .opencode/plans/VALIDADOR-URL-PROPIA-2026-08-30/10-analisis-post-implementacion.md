# Análisis Post-Implementación — VALIDADOR-URL-PROPIA-2026-08-30

> **Estado**: Preparación completada — pendiente FASE-A
> **Plan**: VALIDADOR-URL-PROPIA-2026-08-30
> **Versión objetivo**: 4.74.0
> **Creado desde la concepción** (executor v2.17.0 §4): cada fase llena sus secciones AL CIERRE.

## Resumen de Ejecución (llenar al cierre de cada fase)
| Fase | Sesión | Estado | Iteraciones | delegate_task | Notas |
|------|--------|--------|-------------|---------------|-------|
| Preparación | 2026-08-30 | ✅ | ~30 | No | Paso 0 ejecutado: memoria + QMind `iah-cli-lecciones` (2 queries) |
| FASE-A | — | ⏳ | — | No (DIRECTO) | |
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
| L-VUP-1 | (llenar) | | | | A |
| L-VUP-2 | (llenar) | | | | A |
| L-VUP-3 | (llenar) | | | | A |
| ... | mínimo 3 por fase completada | | | | B-D, VERIFY |

## Seguimientos abiertos
| Tema | Estado | Acción futura |
|------|--------|---------------|
| Línea base sucia: hasta 12 tests rojos preexistentes (2026-08-29) | Re-verificar en FASE-A T1 | Registrar conteo real; NO atribuir al plan |
| Residuo `test_config_pricing::test_tiers_boutique_min_price` + N10 (pricing.yaml inconsistente) | Fuera de alcance | Decisión separada: ¿test, yaml o ambos contra escalera canónica? |
| RC3: confidence/CMS mide estructura, no identidad de fuente (terceros no blocklisted) | Watchlist | Vigilar con la blocklist versionada; posible plan futuro |
| N5: bug numérico latente en `generar_reporte_ejecutivo()` | Fuera de alcance | Fix de la familia credibilidad numérica |
| N7: higiene main.py (`_audit_handler` ×5, 3 esquemas de identidad) | Fuera de alcance | Candidato a plan de refactor |
| GOOGLE_PAGESPEED_API_KEY inválida | Decisión del usuario (OPS) | Rotación fuera del plan |
| Blocklist maintenance | Al cierre | Fecha de próxima revisión de `config/url_blocklist.yaml` |

## Métricas de Ejecución (llenar al cierre)
| Métrica | Valor |
|---------|-------|
| Tests nuevos totales | — |
| Tests finales (def test_) | — |
| Regresiones nuevas | 0 (objetivo) |
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

## Checklist de Cierre (llenar en FASE-RELEASE)
- [ ] Todas las fases ✅ en `06-checklist-implementacion.md`
- [ ] Matriz de verificación completa (FASE-VERIFY)
- [ ] Métricas finales llenas
- [ ] Lecciones INCLUIR persistidas en memoria del proyecto + 10-analisis re-ingerido a QMind
- [ ] CHANGELOG + GUIA_TECNICA + VERSION sync 4.74.0
- [ ] Contexto disparador archivado en `.opencode/context/Historico/`
