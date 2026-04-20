# FASE-6: Fix Voice/AEO Deprecated en Propuesta
**Proyecto**: Amaziliahotel E2E Refactor v2
**Anterior**: Ninguna (FASE-6 es independiente)
**Siguiente**: Cualquiera

---

## Contexto

**G9 (MEDIO)**: Voice/AEO está DEPRECATED en `asset_catalog.py` pero sigue prometiéndose en la propuesta.

**Hallazgo post-forense (crítico)**:
- Voice/AEO (`voice_assistant_guide`) tiene `status=AssetStatus.DEPRECATED` en `asset_catalog.py` con comentario "# FASE-5: ELIMINADO de pipeline - sin brecha real"
- PERO el template V6 (~línea 49) muestra: `**✅ Búsqueda por Voz** (AEO) | Aparece cuando alguien dice "Ok Google..."`
- Y `proposal_asset_alignment.py` (~línea 23) mapea: `"Busqueda por Voz": "voice_assistant_guide"` como servicio prometido

**WhatsApp SÍ está implementado** (`whatsapp_button` en asset_catalog tiene status IMPLEMENTED). El plan anterior (v1) decía eliminar WhatsApp — eso era incorrecto. WhatsApp se mantiene.

---

## Tareas de la Fase

### 1. Confirmar estado en asset_catalog

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# Voice debe estar DEPRECATED
grep -n "voice_assistant_guide\|DEPRECATED" modules/asset_generation/asset_catalog.py | head -10

# WhatsApp debe estar IMPLEMENTED (NO tocar)
grep -n "whatsapp_button\|IMPLEMENTED" modules/asset_generation/asset_catalog.py | head -5
```

### 2. Eliminar Voice del template V6

```bash
# Ver la línea exacta
grep -n "Búsqueda por Voz\|Busqueda por Voz\|Voice\|AEO" \
    modules/commercial_documents/templates/propuesta_v6_template.md
```

**Acción**: Eliminar o comentar la línea que promete "Búsqueda por Voz (AEO)" del template.

### 3. Eliminar Voice de proposal_asset_alignment

```bash
grep -n "Busqueda por Voz\|voice_assistant" \
    modules/asset_generation/proposal_asset_alignment.py
```

**Acción**: Eliminar la entrada `"Busqueda por Voz": "voice_assistant_guide"` del mapeo.

### 4. Verificar fix

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# Voice NO debe aparecer en propuesta generada
grep -i "búsqueda por voz\|voice" outputs/amaziliahotel.com/propuesta.md || echo "OK: Voice no aparece"

# WhatsApp SÍ debe seguir apareciendo (servicio activo)
grep -i "whatsapp" outputs/amaziliahotel.com/propuesta.md && echo "OK: WhatsApp sigue activo"
```

---

## Post-Ejecución

### Checklist de completitud

- [ ] Voice/AEO NO aparece como servicio en propuesta
- [ ] WhatsApp SÍ sigue apareciendo (servicio activo, IMPLEMENTED)
- [ ] Servicios activos sí aparecen (SEO Local, Datos Estructurados, etc.)
- [ ] Tests pasando: `pytest tests/commercial_documents/ tests/asset_generation/ -v -k "proposal or alignment"`
- [ ] Sin regresiones en asset_catalog

### Actualizar estado

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-6 \
    --desc "Fix Voice/AEO deprecated — eliminado de template V6 y proposal_asset_alignment. WhatsApp NO se toca (IMPLEMENTED)" \
    --archivos-mod "modules/commercial_documents/templates/propuesta_v6_template.md,modules/asset_generation/proposal_asset_alignment.py" \
    --tests "3" \
    --check-manual-docs
```

---

## Criterios de Aprobación

| Criterio | Estado |
|----------|--------|
| Voice/AEO NO en propuesta | [ ] |
| WhatsApp SÍ en propuesta (activo) | [ ] |
| Servicios activos SÍ aparecen | [ ] |
| Tests pasando | [ ] |
