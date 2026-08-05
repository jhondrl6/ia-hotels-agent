# FASE-E — RC3: Higiene Documental (R3.1-R3.4) + Commit Historico

**ID**: RC1-RC2-ENTREGA-COHERENTE-2026-08-04 / FASE-E
**Objetivo**: Cerrar la deuda documental del plan anterior (prompts con `--release`, conteos a mano, citas driftadas, evidencia no preservada) aplicando R3.1-R3.4 del contexto fuente.
**Dependencias**: FASE-D ✅ (verificar en dependencias-fases.md; si no ✅, ABORTAR)
**Duración estimada**: 1-2 horas
**Skill**: `.agents/workflows/phased_project_executor.md`
**Modo de ejecución**: ✅ **DELEGABLE vía `delegate_task`** — SOLO edición de MD/YAML + git + UN script stdlib-only (`scripts/run_all_validations.py`, sin imports del proyecto, sin decisiones arquitectónicas).

---

## Contexto

RC3 = higiene documental sin enforcement (el conocimiento existe, falla la aplicación):

| Rec | Acción | Archivos |
|-----|--------|----------|
| **R3.1** | Eliminar `--release 4.70.0` de prompts 02-05 del plan anterior + añadir nota "NO usar --release en fases intermedias" + **implementar check automatizado `_check_prompts_no_release` en `scripts/run_all_validations.py`** (enforcement permanente de L3/L9 — ver T1) | `.opencode/plans/COHERENCIA-MODULO-ENTREGA-2026-08-03/0{2,3,4,5}-prompt-*.md`, `scripts/run_all_validations.py` |
| **R3.2** | Corregir conteos del 11-doc DESDE FUENTE VIVA (L8): módulos 205 .py, 391 clases, 27 dirs con `__init__`; aritmética acumulativa FASE-D (19, no 17); lista D3 completa (8 valores) | `.opencode/plans/COHERENCIA-MODULO-ENTREGA-2026-08-03/11-documentacion-post-proyecto.md` |
| **R3.3** | Anotar en 10-analisis/11-doc que los artefactos E2E llevan versión 4.69.0 (pre-bump, correcto por diseño) + preservar la evidencia JSON que sobrevive del run 123637 en `evidence/N3-diff/` con nota "diff de 97 líneas NO reproducible: los .md del run1 fueron sobrescritos" | 10-analisis, 11-doc, `evidence/N3-diff/` |
| **R3.4** | Corregir la cita `_coverage_gate` → L1160 en el contexto fuente | `.opencode/context/CONTEXT-VALIDACION-COHERENCIA-PLAN-ENTREGA-2026-08-04.md` (§4) |
| **+** | Commit de la reorganización Historico pendiente (CONTEXT-DELIVERY movido, REGISTRY.md borrado — §4 del contexto) | git |

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-A / B / C / D | ✅ Completadas (verificar antes de empezar) |

---

## Delegación (delegate_task)

```
delegate_task(
  goal="FASE-E: higiene documental R3.1-R3.4 del plan RC1-RC2-ENTREGA-COHERENTE-2026-08-04",
  context="SOLO edición de archivos MD/YAML. Detalle de tareas en
           .opencode/plans/RC1-RC2-ENTREGA-COHERENTE-2026-08-04/05-prompt-inicio-sesion-fase-E.md.
           Conteos R3.2 verificarlos con comandos reales (pytest --collect-only, find/grep),
           nunca de memoria (L8). Al terminar: git add -A && git status --short (NO commit
           si hay código de otras fases sin commitear — coordinar con el parent).",
  timeout=600, notify_on_complete=True
)
```

El agente principal verifica el diff resultante, ejecuta validaciones y hace el docs cascade.

---

## Tareas

### T1: R3.1 — Prompts 02-05 sin `--release` + enforcement automatizado
- En cada `0{2,3,4,5}-prompt-*.md` del plan anterior: eliminar la ocurrencia de
  `--release 4.70.0` del comando `log_phase_completion.py` y añadir la nota:
  "⚠️ NO usar `--release` en fases intermedias (L3/L9) — solo en FASE-RELEASE".
- Verificación puntual: grep `--release` en esos 4 archivos → 0 hits.
- **Implementar el check automatizado (enforcement R3.1 — el contexto pide
  "añadir grep de prompts a run_all_validations.py")**: nuevo método
  `_check_prompts_no_release()` en `scripts/run_all_validations.py`, siguiendo el
  patrón de los `_check_*` existentes (L3/L9):
  - Escanear `.opencode/plans/` los archivos `0[2-5]-prompt*.md` (fases
    intermedias), EXCLUYENDO `Archives/` (histórico, no se audita) y
    excluyendo `*RELEASE*` (esa fase SÍ usa `--release`).
  - Buscar la regex `--release\s+\d` (con número de versión) → violación.
  - Registrar `ValidationResult` ("Prompts No Release", PASS/FAIL con detalle
    de archivos); registrarlo en `run_all()` tras `_check_document_integration`
    para que corra TAMBIÉN en `--quick` (las fases intermedias validan con
    `--quick`, y este check es exactamente la red anti-regresión de L3/L9).
  - Verificación: `python scripts/run_all_validations.py --quick` → TOTAL PASS
    (conteo dinámico del script: 5 checks existentes + 1 nuevo = 6 en quick mode).

### T2: R3.2 — Conteos del 11-doc desde fuente viva
- Ejecutar y capturar: `python -m pytest --collect-only -q` (conteo), conteo de .py en
  modules/, dirs con `__init__.py`.
- Corregir en 11-doc: métricas de módulos/clases, acumulado FASE-D (=19), lista D3 con
  los 8 valores (incluir el 2º 1,198,906 de `low_seo_score`).

### T3: R3.3 — Anotación pre-bump + preservación de evidencia N3
- Añadir nota en 10-analisis y 11-doc: "los artefactos E2E llevan la versión del código
  que corrió (4.69.0 + fixes); el bump a 4.70.0 es posterior y no se re-ejecutó v4complete".
- Copiar los JSON supervivientes del run 123637 a `evidence/N3-diff/` + README explicando
  que el diff de 97 líneas ya no es reproducible (N20).

### T4: R3.4 + commit Historico
- En el contexto fuente §4: corregir la cita `_coverage_gate` a la línea real actual
  (verificarla en vivo en `modules/quality_gates/publication_gates.py` — era L1160 al
  08-04; SIEMPRE re-verificar antes de escribir, las líneas driftan — Pitfall 15).
- `git status` + commit de la reorganización Historico pendiente.

---

## Tests Obligatorios

| Check | Comando | Criterio |
|-------|---------|----------|
| Sin `--release` en prompts intermedios | grep sobre los 4 archivos | 0 hits |
| Check automatizado R3.1 | `python scripts/run_all_validations.py --quick` | TOTAL PASS — incluye check **"Prompts No Release"** (6/6 en quick: 5 existentes + 1 nuevo; conteo dinámico del script) |
| Validaciones | `python scripts/run_all_validations.py --quick` | 6/6 (5 existentes + Prompts No Release) |
| Integración documental | `python scripts/validate_document_integration.py` | PASS |

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. Actualizar `dependencias-fases.md` (FASE-E ✅) y `README.md` del plan.
2. `09-documentacion-post-proyecto.md`: Sección E (archivos documentales corregidos).
3. `10-analisis-post-implementacion.md`: fila FASE-E en Resumen de Ejecución, Lecciones Aprendidas (R3.1-R3.4, Lxx+1), Seguimientos abiertos.
4. Registrar la fase:
```bash
python scripts/log_phase_completion.py --fase FASE-E --desc "RC3: higiene documental R3.1-R3.4 + preservacion evidencia N3 + commit Historico" --archivos-mod ".opencode/plans/COHERENCIA-MODULO-ENTREGA-2026-08-03/11-documentacion-post-proyecto.md" --tests "0" --check-manual-docs
```
**SIN `--release`** (L3/L9 — y esta fase es precisamente la que corrige esa violación).

---

## Criterios de Completitud (CHECKLIST)

- [ ] Prompts 02-05 sin `--release` (grep 0 hits) con nota preventiva
- [ ] `_check_prompts_no_release` implementado en `run_all_validations.py` y verificado con `--quick` (TOTAL PASS)
- [ ] Conteos del 11-doc verificados contra comandos en vivo
- [ ] Nota pre-bump 4.69.0 añadida; evidencia N3 preservada en `evidence/N3-diff/`
- [ ] Cita `_coverage_gate` corregida contra línea viva
- [ ] Commit de la reorganización Historico realizado
- [ ] `run_all_validations.py --quick` TOTAL PASS (incluye "Prompts No Release")
- [ ] `log_phase_completion.py` ejecutado SIN --release

## Restricciones

- Máximo 60 iteraciones (R2).
- SOLO archivos documentales (MD/YAML) + `scripts/run_all_validations.py` (única excepción de código, stdlib-only) y git — NO modificar otro código fuente.
- NO ejecutar `v4complete` ni pytest de módulos (fase documental).
- NO usar Select-String para verificar texto con acentos (L15): Python UTF-8 o ripgrep.
