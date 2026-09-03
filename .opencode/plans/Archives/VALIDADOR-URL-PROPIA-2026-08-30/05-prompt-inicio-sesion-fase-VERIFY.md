# FASE-VERIFY — Certificación formal de AC1-AC8 contra evidencia real

**ID**: VALIDADOR-URL-PROPIA / FASE-VERIFY
**Objetivo**: Certificar formalmente que los criterios de aceptación del plan se cumplen contra la evidencia real generada en FASE-C (probes Don Julio) y FASE-D (E2E Salento Real), con diff antes/después. Completar la matriz de verificación del `10-analisis-post-implementacion.md` y declarar cada fix como SUPERADO o no.
**Dependencias**: FASE-A ✅, FASE-B ✅, FASE-C ✅, FASE-D ✅
**Duración estimada**: 1-2 horas (~41-50 iteraciones)
**Skill**: `phased_project_executor.md` v2.17.0 §4.6

## Modo de ejecución (regla del executor)

**DIRECTO — NO delegable.** Requiere juicio y contexto completo del plan (§4.6). Esta fase certifica la INTEGRACIÓN coherente de todos los cambios, no los checks locales de cada fase.

## Contexto

FASE-VERIFY activada por cumplir los 3 criterios (§4.6): ≥3 fases impl (A-D), ejecución E2E (FASE-D), ACs cross-fase (AC1-AC8). Fuentes de evidencia:
- `evidence/FASE-VUP-C/` — probes P1-P11 + `resumen_probes.json`
- `evidence/FASE-VUP-D/` — output E2E Salento Real + `comparacion.md`
- Baseline: `output/salentoreal_final_v4c_h2/` + `evidence/FASE-SR-H2/smoke_result_h2.json`
- `tests/test_url_propia_guard.py`, `tests/test_guardian_ast_url_guard.py`, `tests/test_target_id_canonicalization.py`

### Metodología mínima (7 pasos, §4.6)
1. Leer output post-fix y baseline.
2. Verificar cada AC contra output real (no solo unit tests).
3. Comparar antes/después.
4. Greps residuales de strings que debieron desaparecer.
5. Completar matriz de verificación del 10-analisis.
6. Registrar lecciones de la verificación (mínimo 3).
7. `log_phase_completion.py` SIN `--release` + `run_all_validations.py --quick`.

## Tareas

### T1: Matriz de certificación AC1-AC8
Verificar cada AC con su método (lectura directa, parseo JSON con Python UTF-8, grep):

| AC | Método de verificación | Evidencia a inspeccionar |
|----|------------------------|--------------------------|
| AC1 | `resumen_probes.json` P1: exit_code 2, mensaje_clave en español, duración < 30 s, sin artefactos nuevos en output/ | `evidence/FASE-VUP-C/p1_booking.txt` |
| AC2 | P2 igual que P1 (categoría red social) | `p2_instagram.txt` |
| AC3 | P10: 28/28 canonicalización + corrida FASE-D con sitio propio sin interferencia del guard | `p10_canonicalization.txt` + `evidence/FASE-VUP-D/` |
| AC4 | P9: evento en el archivo dedicado `.agent/memory/url_guard_force_events.json` (parseado con Python) + documentación del flag (help extendido de `--force`, main.py:172) | `p9_force.txt` + estado |
| AC5 | P3/P4 + guardián AST PASSED (4 superficies: ensure_url + extract_hotel_data + audit + extract_data) | `p3..p4*.txt`, `p11_guard_tests.txt` |
| AC6 | P5 (procedimiento sembrado): rechazo desde estado persistente con mención explícita; URL bloqueada no re-persistida | `p5_last_url.txt` |
| AC7 | P6: hook-pdf rechaza url bloqueada sin `--url` | `p6_hookpdf.txt` |
| AC8 | `comparacion.md`: coherence ≥ 0.8, gates sin regresión blocking, plan de assets equivalente al baseline H2 | `evidence/FASE-VUP-D/comparacion.md` |

### T2: Greps residuales (0 matches esperados)
| Patrón | Scope | Esperado |
|--------|-------|----------|
| Lista OTA duplicada sin referenciar `url_blocklist` | `main.py`, `modules/` (código activo) | centralizado o con referencia |
| `def ensure_url` | `main.py` | exactamente 1 definición |
| `assert_own_site` en `main.py` | `main.py` | exactamente 1 llamada (dentro de `ensure_url`; auditoría F2: nada en los modos) |
| Cobertura estructural | orden en `main()`: `ensure_url` (L~1406) precede a routing y a `save_state` (L~1411) | verificado por lectura directa |

### T3: Declaración de fixes superados + lecciones
- Para GA-1 y GA-2 (y N1-N4, N6, N8 del contexto): declarar SUPERADO / PARCIAL / NO SUPERADO con la evidencia citada. Recordar L29: fix de integración SOLO se certifica con evidencia E2E del artefacto afectado (FASE-D), nunca con solo unit tests.
- Residuos que permanecen vivos (contexto §7): RC3 (confidence/CMS para terceros no blocklisted → watchlist), N5 (bug numérico latente), N7 (higiene main.py), pricing residual — van a Seguimientos abiertos, NO bloquean.
- Mínimo 3 lecciones nuevas (qué pasó / por qué / qué lo previene + INCLUIR/EXCLUIR).

## Post-Ejecución (OBLIGATORIO)

1. `dependencias-fases.md` → FASE-VERIFY ✅.
2. `06-checklist-implementacion.md` → fila VERIFY ✅.
3. `10-analisis-post-implementacion.md` → Matriz de Verificación completa (columnas Real/Status), lecciones de la verificación, Seguimientos.
4. Write-back de lecciones (Paso 0/§4): persistir lecciones INCLUIR en la memoria del proyecto (una entrada durable por lección) y re-ingerir el 10-analisis al notebook QMind `iah-cli-lecciones` si está disponible.
5. Registro (SIN `--release`):
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-VERIFY --desc "Certificacion AC1-AC8 contra evidencia real: probes Don Julio + E2E Salento Real" \
    --check-manual-docs
```
6. `python scripts/run_all_validations.py --quick` + commit.

## Criterios de Completitud (CHECKLIST)

- [ ] Matriz AC1-AC8 con Real/Status para las 8 filas
- [ ] Greps residuales con 0 matches (o justificados)
- [ ] Declaración de fixes superados para GA-1/GA-2 con evidencia citada
- [ ] ≥3 lecciones + write-back a memoria
- [ ] `run_all_validations.py --quick` pasado/clasificado

## Restricciones

- **NO modifica código fuente ni templates.** Si un AC falla: documentar en Seguimientos y planificar sesión de recuperación separada.
- **NO ejecuta v4complete** — la corrida E2E ya ocurrió en FASE-D.
- **Máximo 60 iteraciones** (R2).
- NO usar `--release` en `log_phase_completion.py`.
