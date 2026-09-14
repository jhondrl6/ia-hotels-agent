# FASE-P3-B: Fixes de cableado y test

**ID**: TRIBUNAL-ENFORCEMENT-OBS-2026-09-11 / FASE-P3-B
**Objetivo**: Cerrar los dos fixes fijos que quedaban de la P3 original — whitelist barreda (AC-F3, test-only) y versión del acta desde `VERSION.yaml` — y, **solo si Q5=(a)**, el AC-F5: propagar las banderas reales de analítica al `HotelFinancialData` del bloque FASE-K.
**Dependencias**: FASE-P1 ✅ (Q5 decidida) + FASE-P3-A ✅ (secuencia obligada: comparten conteo NR1; y si P2 se ejecutó, también va antes).
**Presupuesto**: 15 iteraciones si Q5≠(a); 25 si Q5=(a) (R2.1, corte = commit; D-V2.1 aplica: auto-reporte con unidad declarada si el instrumento no alcanza el transcript).
**Complejidad técnica**: BAJA (Q5≠a) / MEDIA (Q5=a — toca `main.py`)
**Modo de ejecución**: DIRECTO
**Skill**: `phased_project_executor.md` v2.24.0

---

## Contexto

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-P1 | ⟨P1 fija: Q5 (a) propagar / (b) B_PLUS declarado / (c) P4 diferida⟩ |
| FASE-P2 | ⟨P1 fija: ejecutada o no aplica⟩ |
| FASE-P3-A | ⟨P3-A cierra: ✅ + fecha⟩ |
| FASE-P3-B | ← ESTA FASE |

### Base técnica disponible
- `test_barreda_un_solo_emisor_de_la_clave` — en rojo desde v4.76.0 con la limitación declarada (D-V.1); la cura es **test-only**: autorizar a Bot 3 como emisor legítimo de `asset_path`, **sin tocar el emisor**
- `modules/quality_gates/tribunal/acta_writer.py` — versión hardcodeada → leer `VERSION.yaml` (fuente única, convención del repo)
- `main.py` bloque FASE-K — `HotelFinancialData(..., ga4_enabled=False, gsc_enabled=False)` fijos; la disponibilidad real se calcula más abajo (`ga4_client.is_available()` → `analytics_data["use_ga4"]`) — **solo si Q5=(a)**
- `modules/financial_engine/scenario_calculator.py` — `_determine_evidence_tier`

### Lecciones capitalizadas aplicables a esta fase
(filtras de `00-lecciones-capitalizadas.md` §2)

| ID | Lección (una línea) | Qué cambia en ESTA fase |
|----|---------------------|-------------------------|
| L-T2C.2 | Un NameError latente sobrevive meses si su consumidor está bajo un `except Exception` ancho | Si Q5=a: el hoist en `main.py` exige test propio del tier con y sin analítica, y queda prohibido envolverlo en un `except` ancho |
| L-T4A.5 / L-VUP-5 | Un test que no puede fallar no certifica el AC | NR7 sobre AC-F3 (el whitelist no puede dejar la barra muerta) y AC-F5 si aplica |
| L-VUP-1 | La baseline de tests es orden-dependiente (`test_function_default_flags`) | El par pre/post NR1 se toma con la combinación exacta de archivos declarada y los flaky listados en la evidencia |
| L-V.4 | Un AC que falla se documenta con causa y dueño, no se arregla en otra fase | Barreda: se cierra LA whitelist prometida en D-V.1 — nada de retocar `asset_reviewer.py` de paso |

---

## Tareas (R3: 2 tareas fijas + 1 condicional, 0 comandos largos)

### Tarea 1: AC-F3 — whitelist barreda (test-only)
- Editar `test_barreda_un_solo_emisor_de_la_clave` para autorizar a Bot 3 como emisor legítimo. **Edición de test: no tocar el emisor.**
- NR7: confirmar que la regla sigue viva — si se elimina la autorización del resto legítimo, la barra debe volver a rojo; si la edición deja el test vacuo (pase garantizado), no cuenta.

### Tarea 2: versión del acta desde `VERSION.yaml`
- `acta_writer.py` lee la fuente única; test de regesión que la clave `version` del acta coincide con `VERSION.yaml` (nunca hardcodear la aserción del valor).

### Tarea 3 (condicional — solo si Q5=(a)): AC-F5 — banderas de analítica
- Propagar `ga4_available`/`gsc_available` reales al `HotelFinancialData` del bloque FASE-K (hoist sobre el bloque).
- Tests obligatorios: tier con analítica disponible y sin ella; **ningún `except` ancho alrededor del hoist** (L-T2C.2); delta NR1 con par pre/post.
- Si Q5≠(a): la tarea no se ejecuta y su no-ejecución se registra con la decisión de Q5 como causa (checklist §P3-B).

**Criterios de aceptación**:
- [ ] `test_barreda_un_solo_emisor_de_la_clave` verde con la regla viva (AC-F3 + NR7)
- [ ] Acta con `version` == `VERSION.yaml` (test lo verifica leyendo el YAML, no con literal)
- [ ] Si Q5=a: AC-F5 con sus dos tests de tier y hoist sin `except` ancho; si Q5≠a: constancia registrada
- [ ] Delta NR1 con resta R2.7 verificada
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] Cero cambios en `judge.py`/`asset_reviewer.py` (P3-A) y `delivery_packager.py` (P2)

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| Barreda whitelist | test existente (edición test-only) | Verde con regla viva; rojo si se retira la autorización legítima |
| Versión del acta | `tests/quality_gates/tribunal/` (archivo propio) | Coincidencia con `VERSION.yaml` leída del disco |
| Tier con/sin analítica (solo Q5=a) | idem | `A` con banderas reales; `B_PLUS` sin analítica |

**Comando de validación**:
```bash
python -m pytest tests/quality_gates/tribunal/ -v
python scripts/run_all_validations.py --quick
```

---

## Post-Ejecución (OBLIGATORIO)

1. `dependencias-fases.md`: P3-B ✅ + fecha
2. `README.md`: tabla de progreso
3. `09-documentacion-post-proyecto.md`: acumular secciones de esta fase
4. `10-analisis-post-implementacion.md`: fila + lecciones + métricas
5. `00-lecciones-capitalizadas.md` §2: realidad contra promesa
6. `evidence/FASE-P3-B/`: pares NR7, par NR1, constancia Q5
7. `log_phase_completion.py --fase FASE-P3-B --desc "..." --check-manual-docs` (SIN `--release`)

**NO esperar a la siguiente sesión.**

---

## Criterios de Completitud (CHECKLIST)

- [ ] ACs de la fase con artefacto + clave (R2.4)
- [ ] NR7 donde aplica; Q5≠(a) registrado como condicional no disparado
- [ ] Iteraciones medidas y escritas (L-R.1 — un `—` no cierra)
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] Post-ejecución completada (7 puntos)

**NO marcar la fase como completada si algún criterio falla.**

---

## Restricciones

- NO re-decidir Q5 (L-VUP-6).
- **Edición test-only en AC-F3**: el emisor (`asset_reviewer.py`) no se toca — es la promesa exacta de D-V.1.
- NO tocar `main.py` salvo Tarea 3 con Q5=(a).
- NO ejecutar `v4complete`.
- AGENTS.md registra `test_barreda_un_solo_emisor_de_la_clave` como fallo conocido (D-V.1): al cerrar esta fase, la actualización del estado de tests del documento corresponde a FASE-RELEASE junto con el bump.
