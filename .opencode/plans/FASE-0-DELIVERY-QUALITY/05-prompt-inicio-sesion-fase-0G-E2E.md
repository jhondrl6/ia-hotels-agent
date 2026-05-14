# FASE-0G: E2E Controlado

> **Fase:** 0G  
> **Tipo:** Verificación + comando largo  
> **Comando largo:** Sí (`v4complete`)  
> **Dependencias:** 0A-0F  
> **Máximo iteraciones:** 60  
> **Restricción:** ÚNICA ejecución de `v4complete`. Presupuesto de iteraciones: investigación+verificación+docs debe dejar margen para v4complete.

---

## Contexto

Lee primero:
1. `FASE-0-CONTEXTO-IMPLEMENTACION-ROADMAP.md` §10
2. Este prompt

---

## Pre-flight

Antes de ejecutar `v4complete`, verificar:
```bash
# APIs y entorno
PYTHONIOENCODING=utf-8 ./venv/Scripts/python.exe -X utf8 scripts/run_all_validations.py --quick

# Hotel objetivo (por defecto: hotelcastillareal; o nuevo si se define)
```

Si validaciones fallan, NO ejecutar v4complete. Corregir primero.

---

## Tareas

### Tarea 1: Ejecutar v4complete

Comando:
```bash
PYTHONIOENCODING=utf-8 ./venv/Scripts/python.exe -X utf8 main.py v4complete --url https://hotelcastillareal.com
```

O si se define otro hotel, usar esa URL.

Usar `terminal(timeout=600, notify_on_complete=True)`.

**Inmediatamente después de que termine:** copiar evidencia:
```bash
mkdir -p evidence/FASE-0G-E2E
cp output/v4_complete/hotelcastillareal/v4_audit/*.json evidence/FASE-0G-E2E/
cp output/v4_complete/hotelcastillareal/v4_audit/*.md evidence/FASE-0G-E2E/ 2>/dev/null || true
cp output/v4_complete/v4_complete_report.json evidence/FASE-0G-E2E/
```

### Tarea 2: Verificar artifacts FASE 0

Confirmar existencia en disco:
```bash
find output/v4_complete/hotelcastillareal/v4_audit -type f | sort
find output/v4_complete/deliveries -type f -iname '*.zip'
```

Requeridos:
- [ ] `asset_generation_report.json`
- [ ] `coherence_validation.json`
- [ ] `delivery_quality_report.json` → **nuevo**
- [ ] `pain_ledger.json` → **nuevo**
- [ ] `human_checklist.md` → **nuevo**
- [ ] `proposal_asset_matrix.json` → **nuevo**
- [ ] ZIP en `deliveries/`

### Tarea 3: Validar G0/G6/G7/G8

Construir tabla:

| Gate | Pregunta | Evidencia | Resultado |
|------|----------|-----------|-----------|
| G0 | ¿Diagnóstico, oportunidad, propuesta, assets autoconsistentes? | `delivery_quality_report.json` status | |
| G6 | ¿Misma historia? | `coherence_score_final >= 0.8` | |
| G7 | ¿Todas las brechas trazables? | `pain_ledger.json` 100% != UNTRACKED | |
| G8 | ¿Assets específicos, no genéricos? | `asset_specificity_gate` | |

Si algún gate FAIL, documentar y decidir si se requiere fase de corrección antes de RELEASE.

**Si G8 FAIL:** proceder a FASE-0H (`05-prompt-inicio-sesion-fase-0H-G8.md`). No intentar fix ad-hoc en esta sesión.

---

## Criterios de Completitud

- [ ] `v4complete` ejecutó sin errores críticos
- [ ] Evidencia copiada a `evidence/FASE-0G-E2E/`
- [ ] Todos los artifacts nuevos existen en disco
- [ ] ZIP existe si `delivery_quality_report.json` es PASS
- [ ] Tabla G0/G6/G7/G8 completada con PASS/FAIL justificado

---

## Post-Ejecución

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-0G-E2E \
    --desc "E2E controlado con artifacts FASE 0" \
    --tests "0" \
    --check-manual-docs
```

Actualizar `06-checklist-implementacion.md`: marcar 0G-1..0G-3 como ✅.
