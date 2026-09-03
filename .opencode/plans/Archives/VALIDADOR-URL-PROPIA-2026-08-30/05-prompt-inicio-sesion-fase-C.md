# FASE-C — Verificación empírica con URLs de Finca Hotel Don Julio + regresión

**ID**: VALIDADOR-URL-PROPIA / FASE-C
**Objetivo**: Demostrar empíricamente que el guard funciona sobre el caso real (Finca Hotel Don Julio: URLs de Booking e Instagram) y que el comportamiento tradicional con sitio propio permanece inalterado. Produce la evidencia P1-P11 que certificará FASE-VERIFY.
**Dependencias**: FASE-A ✅, FASE-B ✅
**Duración estimada**: 1-2 horas (~36-45 iteraciones)
**Skill**: `phased_project_executor.md` v2.17.0

## Modo de ejecución (regla del executor)

**DELEGADO a subagente** (probes CLI cortos y deterministas + pytest por lotes; sin decisiones de diseño; sin comandos de larga duración: el guard aborta antes de red). El parent verifica el reporte del subagente contra `evidence/FASE-VUP-C/` antes de aceptar la fase.

**Instrucción al subagente**: "Ejecutar y reportar, no interpretar ni arreglar" (L30). Si un probe falla, capturar la salida completa y reportar — NO corregir código (corresponde a sesión de recuperación).

## Contexto

El 2026-08-29 las sondas originales (Apéndice A del contexto) demostraron el fallo: Booking → auditoría de la página de Booking; Instagram → `confidence: alta` + `cms: shopify` falsos. Esta fase demuestra la situación inversa: el pipeline ahora RECHAZA esas entradas de forma fuerte, temprana y sin costo API (N4: antes se gastaba Places API con queries "Instagram"/"Booking").

URLs reales del caso (Finca Hotel Don Julio, sin web propia):
- `https://www.booking.com/hotel/co/finca-don-julio.es.html`
- `https://www.instagram.com/fincahoteldonjulio`

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-A | ✅ Completada |
| FASE-B | ✅ Completada |
| FASE-C | ⏳ En progreso (esta sesión) |

### Lecciones capitalizadas aplicables
| Lección | Aplicación concreta |
|---------|---------------------|
| Verificación con acentos/JSON: Python UTF-8, no pipes de consola (L15/L6) | Parsear mensajes y JSON con Python; pytest con `> temp/x.txt 2>&1` |
| Rechazo ≠ causa: trazar el mecanismo completo | En cada probe verificar EXIT CODE + MENSAJE + AUSENCIA de actividad (tiempo < umbral, sin artefactos de scraping en output/) |
| Pytest seguro (memoria) | Lotes pequeños secuenciales; NUNCA suite commercial_documents completa |

## Tareas

### T1: Sondas P1-P11 (evidencia de efectividad)
**Objetivo**: Capturar comportamiento real del guard en `evidence/FASE-VUP-C/`.

| # | Comando | Resultado esperado | Evidencia |
|---|---------|--------------------|-----------|
| P1 | `./venv/Scripts/python.exe main.py v4complete --url "https://www.booking.com/hotel/co/finca-don-julio.es.html"` | exit 2; mensaje en español que nombre la plataforma y pida la URL del sitio propio; duración < 30 s; sin artefactos nuevos en `output/`; sin marcadores de scraping/auditoría en stdout (auditoría F7: estos 4 puntos SON el criterio observable de "sin llamadas API") | `p1_booking.txt` |
| P2 | `./venv/Scripts/python.exe main.py v4complete --url "https://www.instagram.com/fincahoteldonjulio"` | igual que P1 (red social) | `p2_instagram.txt` |
| P3 | `./venv/Scripts/python.exe main.py onboard --url <booking>` y `execute --url <booking>` | mismo rechazo | `p3_onboard_execute.txt` |
| P4 | `./venv/Scripts/python.exe main.py deploy --url <instagram>` | mismo rechazo | `p4_deploy.txt` |
| P5 | **Procedimiento sembrado (auditoría F3)**: (1) `./venv/Scripts/python.exe -c "from agent_harness.memory import MemoryManager; MemoryManager().save_state({'last_url': 'https://www.booking.com/hotel/co/finca-don-julio.es.html'})"`; (2) `./venv/Scripts/python.exe main.py v4complete` SIN `--url`; (3) verificar con Python el archivo de estado; (4) restaurar `last_url` a `https://www.hotelsalentoreal.com/` | rechazo con mención explícita de estado persistente; la URL bloqueada NO fue re-persistida. ⚠️ SIN el paso 1 el test es inválido: tras P1 el estado sigue con hotelsalentoreal.com (el rechazo ocurre antes de save_state) y el comando arrancaría un v4complete completo — violación de restricciones | `p5_last_url.txt` |
| P6 | `hook-pdf` contra fixture `v4_complete_report.json` con `url` de booking (crear fixture mínimo en `temp/`) | rechazo claro, sin PDF | `p6_hookpdf.txt` |
| P7 | Script Python: `WebScraper().extract_hotel_data(<booking>)` | `UrlNoPropiaError`, 0 peticiones HTTP | `p7_scraper.txt` |
| P8 | Script Python: auditor con URL OTA | excepción del guard, 0 llamadas Places | `p8_auditor.txt` |
| P9 | `v4complete --url <booking> --force` capturado con **timeout ~45 s** (el proceso se mata tras confirmar; el exit code del proceso matado NO es criterio) | NO lanza el guard; warning persistido en el archivo dedicado `.agent/memory/url_guard_force_events.json` (inspección con Python); stdout muestra que el pipeline pasó el guard (auditoría F8) | `p9_force.txt` |
| P10 | `pytest tests/test_target_id_canonicalization.py -v` | 28/28 PASSED | `p10_canonicalization.txt` |
| P11 | `pytest tests/test_url_propia_guard.py tests/test_guardian_ast_url_guard.py -v` | 100% PASSED | `p11_guard_tests.txt` |

**Criterios de aceptación**:
- [ ] Los 11 probes capturados en `evidence/FASE-VUP-C/`.
- [ ] P1-P4 con exit code ≠ 0 y mensaje en español verificable en el archivo.
- [ ] P5 demuestra AC6; P6 demuestra AC7; P9 demuestra AC4.
- [ ] Script resumen `evidence/FASE-VUP-C/resumen_probes.json` (parseable, UTF-8) con {probe, exit_code, mensaje_clave, duracion_s, status}.

### T2: Regresión dirigida (no-afectación del flujo tradicional)
**Objetivo**: Confirmar que nada del comportamiento con sitio propio cambió.

**Acciones** (lotes pequeños, salida a archivo):
- `pytest tests/test_url_propia_guard.py tests/test_guardian_ast_url_guard.py tests/test_target_id_canonicalization.py -v > temp/fase_c_regression.txt 2>&1`
- Suites que ejerciten `ensure_url`/onboarding/hook-pdf tocadas en FASE-B (según `git diff --name-only` de A+B).
- Comparar fallos contra la baseline registrada en FASE-A (10-analisis): los mismos preexistentes, cero nuevos.

**Criterios de aceptación**:
- [ ] 28/28 canonicalización + contratos del guard PASSED.
- [ ] Sin fallos nuevos vs baseline.
- [ ] Copia de salidas en `evidence/FASE-VUP-C/`.

## Post-Ejecución (OBLIGATORIO)

1. `dependencias-fases.md` → FASE-C ✅ con fecha.
2. `README.md` del plan + `06-checklist-implementacion.md`.
3. `09-documentacion-post-proyecto.md` → sección D (métricas de probes).
4. `10-analisis-post-implementacion.md` → fila Resumen de Ejecución (delegate_task: sí), mínimo 3 lecciones, Seguimientos (cualquier probe anómalo).
5. Registro (SIN `--release`):
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-C --desc "Verificacion empirica guard: 11 probes con URLs reales Don Julio (Booking/Instagram) + regresion 28 canonicalizacion" \
    --tests "N" --check-manual-docs
```
6. Commit (evidencia incluida).

## Criterios de Completitud (CHECKLIST)

- [ ] 11/11 probes en `evidence/FASE-VUP-C/` + `resumen_probes.json`
- [ ] Rechazos sin costo API ni artefactos de scraping (P1-P4)
- [ ] Regresión dirigida sin fallos nuevos
- [ ] Post-ejecución completa

## Restricciones

- **Máximo 60 iteraciones** (R2).
- **NO modificar código** — si un probe falla, documentar y marcar ⏳ INCOMPLETA (la corrección va en sesión de recuperación).
- P9 (`--force`): abortar tras verificar el warning; NO dejar correr el pipeline completo sobre Booking.
- NO ejecutar `v4complete` con sitio propio (eso es FASE-D).
- NO usar `--release` en `log_phase_completion.py`.
