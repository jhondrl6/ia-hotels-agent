# 05-prompt-inicio-sesion-fase-2-PATCH-C

> **Plan maestro**: `PLAN-FASE-2-PATCH-TERMALES-20260508.md`
> **Fase**: 3 de 3 (FINAL) | **Tipo**: Verificación E2E | **Tareas**: 2 | **Comandos largos**: 1 (v4complete)

---

## Contexto

FASE-2-PATCH-A y FASE-2-PATCH-B completadas (6/6 patches implementados). Esta fase ejecuta v4complete para Termales Santa Rosa de Cabal y verifica las 7 métricas de éxito.

**URL**: http://www.termales.com.co/
**Objetivo**: 7/7 métricas pasan → EFECTIVA

---

## Tarea Única: Ejecutar v4complete + Verificar 7 Métricas

### Paso 1 — Ejecutar v4complete

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
venv/Scripts/python.exe main.py v4complete --url http://www.termales.com.co/
```

> ⚠️ **Usar `terminal(timeout=600)` con `notify_on_complete=True`** si el budget de iteraciones lo permite. Si no, usar `delegate_task` con toolsets=["terminal"].

### Paso 2 — Protocolo de Evidencia (OBLIGATORIO, inmediatamente después del output)

```bash
mkdir -p evidence/fase-2-PATCH-C
cp output/v4_complete/01_DIAGNOSTICO_*.md evidence/fase-2-PATCH-C/
cp output/v4_complete/02_PROPUESTA_*.md evidence/fase-2-PATCH-C/
cp output/v4_complete/{hotel_id}/v4_audit/*.json evidence/fase-2-PATCH-C/ 2>/dev/null || true
```

### Paso 3 — Verificar 7 Métricas de Éxito

| # | Métrica | Verificación | Target | Resultado |
|---|---------|-------------|--------|-----------|
| M1 | Sin `{{if}}...{{endif}}` | `grep -c "{{if" evidence/fase-2-PATCH-C/02_PROPUESTA_*.md` | 0 | |
| M2 | Coherence refleja assets reales | Leer `coherence_validation.json` → `promised_assets_exist.score` | < 1.0 si faltan assets | |
| M3 | monthly_report tabla dinámica | Leer `ESTIMATED_informe_mensual_*.md` → tabla con assets y estados | No vacía | |
| M4 | Sin `[PENDING_*]` | `grep -r "\[PENDING_" evidence/fase-2-PATCH-C/` | 0 matches | |
| M5 | WhatsApp detectado | Leer `gate_report_*.json` → `present_in_production` | Contiene `whatsapp_button` | |
| M6 | Schema detectado | Leer `audit_report_*.json` → `hotel_schema_detected` | `true` | |
| M7 | Sin placeholder telefónico | `grep -c "+57 300 000 0000" evidence/fase-2-PATCH-C/02_PROPUESTA_*.md` | 0 | |

### Paso 4 — Veredicto

| Score | Clasificación | Acción |
|-------|--------------|--------|
| 7/7 | **EFECTIVA** | Docs cascade + plan cerrado |
| 4-6 | **PARCIAL** | Reportar métricas fallidas, sugerir siguiente iteración |
| <4 | **NO EFECTIVA** | Reportar hallazgos, re-abrir plan con nueva auditoría |

---

## Post-Ejecución (OBLIGATORIO)

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# 1. Registrar fase
venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-2-PATCH-C \
    --desc "v4complete Termales + verificación 7 métricas post-patch. Score: X/7" \
    --check-manual-docs

# 2. Sincronizar versiones
venv/Scripts/python.exe scripts/sync_versions.py

# 3. Validar CHANGELOG (formato CONTRIBUTING.md)
# Verificar: ### Objetivo / ### Cambios / ### Archivos Nuevos / ### Archivos Modificados / ### Tests

# 4. Validar GUIA_TECNICA (nota técnica por fase)

# 5. Validación final
venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

---

## Actualizar Documentación Acumulativa

Editar `09-documentacion-post-proyecto-2-PATCH.md` con:
- Sección A: Módulos modificados
- Sección B: Funcionalidades corregidas
- Sección D: Resultado de métricas (X/7)
- Sección E: Archivos actualizados

---

## Criterios de Completitud

- [ ] v4complete ejecutado para http://www.termales.com.co/
- [ ] Evidencia copiada a `evidence/fase-2-PATCH-C/`
- [ ] 7/7 métricas verificadas con resultados documentados
- [ ] Veredicto emitido (EFECTIVA / PARCIAL / NO EFECTIVA)
- [ ] `log_phase_completion.py` ejecutado
- [ ] `sync_versions.py` ejecutado
- [ ] CHANGELOG actualizado
- [ ] GUIA_TECNICA actualizada
- [ ] `run_all_validations.py --quick` pasa
- [ ] `09-documentacion-post-proyecto-2-PATCH.md` actualizado
- [ ] `06-checklist-implementacion-2-PATCH.md` actualizado (todos ✅)

---

## Restricciones

- **NO implementar nuevos fixes** — solo verificar
- Si alguna métrica falla, documentar EXACTAMENTE qué falló y por qué
- Presupuesto: 60 iteraciones máximo
- 1 fase por sesión
