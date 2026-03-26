# Prompt: FASE-H-05 - E2E Certification

## Proyecto: iah-cli | hotelvisperas.com
## Fecha: 2026-03-26

---

## Pre-requisito

**FASE-H-02 y FASE-H-04 DEBEN estar completadas.**

---

## Contexto

Esta es la fase final de certificación end-to-end. Después de aplicar los fixes en H-02 y H-04, debemos verificar que el flujo completo V4COMPLETE funciona sin desconexiones.

**Objetivo**: Verificar que NO hay desconexiones entre:
1. Diagnóstico (problemas detectados)
2. Propuesta comercial (assets prometidos)
3. Assets generados (entregables reales)

---

## Tareas de FASE-H-05

### 1. Ejecutar V4COMPLETE E2E

```bash
python main.py v4complete --url https://www.hotelvisperas.com/es --nombre "Hotel Vísperas" --debug 2>&1
```

### 2. Verificar Coherence Score

El coherence score debe ser ≥ 0.8.

```
Coherence Score: 0.XX
Status: READY_FOR_PUBLICATION ✅
```

### 3. Verificar Desconexiones Resueltas

| Desconexión | Verificación | Esperado |
|-------------|--------------|----------|
| WhatsApp | `whatsapp_button` generado | ✅ Archivo existe en delivery_assets |
| Optimization Guide | `optimization_guide` pasa validación | ✅ Status = generated, no BLOCKED |
| ROI | ROI en propuesta comercial | ~3.9X (no 292X) |

### 4. Validar Cross-Reference

| Documento | Debe contener | Verificación |
|-----------|---------------|--------------|
| DIAGNOSTICO.md | 5 problemas | Verificar lista |
| PROPUESTA_COMERCIAL.md | 4 assets prometidos | Verificar lista |
| delivery_assets/ | 4+ archivos | Listar archivos |
| MANIFEST.json | Coherencia | 0 desconnetions |

### 5. Checklist de Certificación

- [ ] Coherence Score ≥ 0.8
- [ ] whatsapp_button 生成 (generado)
- [ ] optimization_guide 生成 (generado, no BLOCKED)
- [ ] ROI corregido (~3.9X)
- [ ] 0 desconnetions en coherence_validator
- [ ] Status: READY_FOR_PUBLICATION

---

## Post-Ejecución

### 1. Actualizar REGISTRY.md

```bash
python scripts/log_phase_completion.py \
    --fase FASE-H-05 \
    --desc "E2E Certification para hotelvisperas.com - 0 desconexiones" \
    --coherence 0.87 \
    --check-manual-docs
```

### 2. Documentación Incremental

Agregar a `09-documentacion-post-proyecto.md`:
- Sección FASE-H-05 completa
- Métricas finales
- Estado del proyecto: COMPLETADO ✅

### 3. Checklist Final

- [ ] REGISTRY.md actualizado
- [ ] CHANGELOG.md actualizado (si aplica)
- [ ] Git commit con cambios

---

## Criterios de Completitud

- [ ] v4complete ejecuta sin errores
- [ ] Coherence Score ≥ 0.8
- [ ] whatsapp_button generado
- [ ] optimization_guide generado
- [ ] ROI corregido
- [ ] 0 desconnetions
- [ ] Status: READY_FOR_PUBLICATION
- [ ] REGISTRY.md actualizado
- [ ] Proyecto COMPLETADO ✅

---

## Notas

- Si alguna verificación falla, volver a la fase correspondiente (H-02 o H-04)
- No proceder hasta que todas las verificaciones pasen
- Esta es la fase final - si pasa, el proyecto está certificado

---

*Prompt creado: 2026-03-26*
*Proyecto: iah-cli | hotelvisperas.com*
*Depende de: FASE-H-02, FASE-H-04*
