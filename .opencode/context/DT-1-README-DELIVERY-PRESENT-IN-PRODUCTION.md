# Contexto: README_DELIVERY — present_in_production en estructura

> **ID**: DT-1-README-DELIVERY-PRESENT-IN-PRODUCTION
> **Fecha**: 2026-07-23
> **Origen**: ASSET-ALIGNMENT-ZIONE-2026-07-23, FASE-5, hallazgo 9.9 (residual)
> **Severidad**: 🟡 MEDIO
> **Estado**: Pendiente de intervención (documentado para nueva sesión)
> **Hotel de prueba**: Zi One Luxury (https://zione.co/), output en `output/v4_complete/zione/`

---

## 1. El Problema

El `README_DELIVERY.md` que se incluye en el ZIP de entrega al cliente contiene referencias hardcodeadas a archivos que pueden no estar presentes en el ZIP porque el asset ya existe en producción (`present_in_production`).

### Evidencia concreta (Zi One Luxury, 2026-07-23)

El ZIP `zione_20260723.zip` contiene 46 archivos. `boton_whatsapp.html` NO está en el ZIP porque `whatsapp_button` está marcado como `present_in_production` (el sitio ya tiene botón de WhatsApp).

Pero el `README_DELIVERY.md` incluido en el ZIP dice:

**Línea 26** (sección Package Structure):
```
│   ├── boton_whatsapp.html     # WhatsApp button code
```

**Línea 54** (sección Implementation Instructions):
```
#### WhatsApp Button (`boton_whatsapp.html`)
1. Copy the HTML code
2. Add to your CMS footer or via custom HTML widget
3. Test on mobile devices
```

**Línea 70** (Suggested Timeline):
```
- [ ] Add WhatsApp button to footer
```

**Línea 95** (Implementation Checklist):
```
- [ ] WhatsApp button visible on all pages
```

El cliente abre el ZIP, lee el README, busca `boton_whatsapp.html` y no lo encuentra. Confusión.

### Mismo problema con otros assets present_in_production

En Zi One Luxury, `org_schema` también es `present_in_production`. Si en el futuro la propuesta incluye servicios adicionales con assets ya en producción, el mismo problema se replica.

---

## 2. Causa Raíz

La template `templates/delivery_readme_template.md` es **estática**. Tiene hardcodeados:
- La estructura del paquete (líneas 23-27)
- Las instrucciones por asset (líneas 44-57)
- El timeline (líneas 68-70)
- El checklist (líneas 92-95)

El método `create_readme()` en `modules/delivery/delivery_packager.py:274` solo reemplaza 4 placeholders:
- `{{HOTEL_ID}}`
- `{{DATE}}`
- `{{TOTAL_FILES}}`
- `{{TOTAL_SIZE}}`

No tiene lógica para secciones condicionales basadas en `present_in_production`.

---

## 3. Datos Disponibles para la Solución

### 3.1 Fuente de verdad: asset_generation_report.json

```json
// output/v4_complete/{hotel_id}/v4_audit/asset_generation_report.json
{
  "skipped_assets": [
    {
      "asset_type": "whatsapp_button",
      "reason": "Asset ya implementado en sitio de producción",
      "presence_status": "exists",
      "site_verified": true,
      "pain_ids_affected": ["no_whatsapp_visible"]
    }
  ]
}
```

### 3.2 Fuente de verdad: gate_report.json (Gate 9)

```json
// output/v4_complete/{hotel_id}/v4_audit/gate_report_*.json
{
  "gate_name": "proposal_asset_alignment",
  "details": {
    "present_in_production": [
      {
        "service": "Botón de WhatsApp",
        "asset": "whatsapp_button",
        "presence_verified": true,
        "presence_status": "exists"
      },
      {
        "service": "Schema Organization",
        "asset": "org_schema",
        "presence_verified": true,
        "presence_status": "exists"
      }
    ]
  }
}
```

### 3.3 Mapeo service → asset: PROPOSAL_SERVICE_TO_ASSET

```python
# modules/asset_generation/proposal_asset_alignment.py
PROPOSAL_SERVICE_TO_ASSET = {
    "SEO Local": "optimization_guide",
    "Botón de WhatsApp": "whatsapp_button",
    "Schema Hotel": "hotel_schema",
    "Schema Organization": "org_schema",
    "Informe Mensual": "monthly_report",
    "Página de FAQ": "faq_page",
    "Meta Tags Sociales (Open Graph)": "open_graph",
    "Optimización para IA Generativa": "llms_txt",
}
```

### 3.4 Archivos involucrados

| Archivo | Rol | Qué cambiar |
|---------|-----|-------------|
| `templates/delivery_readme_template.md` | Template estática del README | Agregar placeholders condicionales `{{#if PRESENT_IN_PRODUCTION}}...{{/if}}` |
| `modules/delivery/delivery_packager.py:274` | `create_readme()` | Leer `asset_generation_report.json`, detectar `skipped_assets` con `presence_status=exists`, pasar `present_in_production` como variable de template |
| `modules/delivery/delivery_packager.py:140-150` | `package()` caller | Pasar datos de `asset_generation_report.json` a `create_readme()` |

### 3.5 Pipeline de llamadas

```
main.py v4complete
  → v4_asset_orchestrator.generate_all()
    → delivery_packager.package(hotel_id="zione", ...)
      → create_readme(delivery_dir, hotel_id, manifest)  # L145 — NO recibe asset_report
```

`create_readme()` se llama en L145 con solo `(delivery_dir, hotel_id, manifest)`. No recibe el `asset_generation_report.json` ni el `gate_report.json`. Para acceder a `present_in_production`, hay que:

1. O bien leer `asset_generation_report.json` desde disco dentro de `create_readme()`
2. O bien pasar los datos desde el caller `package()`

---

## 4. Solución Propuesta

### 4.1 Enfoque

Hacer la template `delivery_readme_template.md` **condicional** para assets `present_in_production`. En vez de listarlos como archivos entregables, mostrar:

```
✅ Ya implementado en su sitio — no requiere acción
```

### 4.2 Cambios necesarios (ordenados por archivo)

#### A) `templates/delivery_readme_template.md`

Agregar sección condicional. Reemplazar las secciones hardcodeadas de WhatsApp con placeholders:

```markdown
## Package Structure

```
{{HOTEL_ID}}_{{DATE}}.zip
├── DIAGNOSTICO.md              # Diagnostic analysis
├── PROPUESTA_COMERCIAL.md      # Commercial proposal
├── ASSETS/
│   ├── hotel-schema.json       # JSON-LD Schema markup
│   ├── geo_playbook.md         # GEO/Local SEO playbook
│   ├── faq_page.md            # FAQ page content
{{ASSET_STRUCTURE_ENTRIES}}
│   └── ...                     # Additional assets
├── MANIFEST.json               # Package manifest
└── README_DELIVERY.md         # This file
```

{{PRESENT_IN_PRODUCTION_SECTION}}
```

Donde:
- `{{ASSET_STRUCTURE_ENTRIES}}` = líneas de estructura dinámicas (para assets en ZIP) o empty
- `{{PRESENT_IN_PRODUCTION_SECTION}}` = sección completa con assets ya en producción, o empty si no hay

#### B) `modules/delivery/delivery_packager.py`

Modificar `create_readme()` para:
1. Leer `asset_generation_report.json` del directorio del hotel
2. Extraer `skipped_assets` con `presence_status == "exists"`
3. Generar contenido condicional: assets en ZIP → entries normales, assets `present_in_production` → nota "✅ Ya implementado"
4. Reemplazar placeholders en la template

```python
def create_readme(self, delivery_dir, hotel_id, manifest=None, hotel_dir=None):
    # ... existing template loading ...
    
    # NEW: Detect present_in_production assets
    present_in_production = []
    if hotel_dir:
        asset_report_path = hotel_dir / "v4_audit" / "asset_generation_report.json"
        if asset_report_path.exists():
            with open(asset_report_path) as f:
                asset_report = json.load(f)
            present_in_production = [
                a for a in asset_report.get("skipped_assets", [])
                if a.get("presence_status") == "exists"
            ]
    
    # Generate conditional sections
    if present_in_production:
        pip_section = self._generate_present_in_production_section(present_in_production)
    else:
        pip_section = ""
    
    content = content.replace("{{PRESENT_IN_PRODUCTION_SECTION}}", pip_section)
    # ... etc ...
```

#### C) Modificar caller en `package()` (L145)

Pasar `hotel_dir` (el `source_dir` resuelto) a `create_readme()`:

```python
# L145: cambiar
self.create_readme(self.deliveries_dir, hotel_id, manifest)
# por:
self.create_readme(self.deliveries_dir, hotel_id, manifest, hotel_dir=source_dir)
```

### 4.3 Comportamiento esperado post-fix

Para Zi One Luxury (whatsapp_button = present_in_production):

**Estructura del ZIP (README_DELIVERY.md)**:
```
zione_20260723.zip
├── DIAGNOSTICO.md
├── PROPUESTA_COMERCIAL.md
├── ASSETS/
│   ├── optimization_guide/    # Guía de optimización SEO Local
│   ├── open_graph/            # Meta tags Open Graph (complemento)
│   ├── ...                    # Otros assets generados
├── MANIFEST.json
└── README_DELIVERY.md
```

**Sección "Ya implementado en su sitio"**:
```
## ✅ Ya Implementado en su Sitio

Los siguientes elementos ya están presentes en https://zione.co/ y NO requieren acción:

| Servicio | Asset | Estado |
|----------|-------|--------|
| Botón de WhatsApp | whatsapp_button | ✅ Verificado en producción |
| Schema Organization | org_schema | ✅ Verificado en producción |

Estos elementos fueron detectados durante la auditoría y se consideran cubiertos.
No es necesario instalarlos — su sitio ya los tiene configurados correctamente.
```

**Timeline y Checklist**: sin referencias a "Add WhatsApp button".

---

## 5. Verificación Post-Fix

1. Ejecutar v4complete para Zi One Luxury:
   ```bash
   cd /mnt/c/Users/Jhond/Github/iah-cli
   ./venv/Scripts/python.exe main.py v4complete --url https://zione.co/
   ```

2. Extraer y verificar README_DELIVERY.md del ZIP:
   ```bash
   unzip -p output/v4_complete/deliveries/zione_*.zip README_DELIVERY.md | grep -i whatsapp
   ```
   Debe mostrar SOLO la sección "Ya implementado", NO instrucciones de instalación.

3. Verificar que la estructura no lista `boton_whatsapp.html`:
   ```bash
   unzip -p output/v4_complete/deliveries/zione_*.zip README_DELIVERY.md | grep "boton_whatsapp"
   ```
   Si hay match, debe ser dentro de "✅ Ya Implementado", no en la estructura de archivos.

---

## 6. Riesgos y Consideraciones

| Riesgo | Probabilidad | Mitigación |
|--------|-------------|------------|
| Template mal formada rompe el README para hoteles sin present_in_production | Baja | Sección `{{PRESENT_IN_PRODUCTION_SECTION}}` vacía si no hay → sin cambios visuales |
| Cambio en schema de asset_generation_report.json | Baja | Usar `.get()` con defaults, no asumir keys |
| Hotel sin asset_generation_report.json (corner case) | Baja | `if asset_report_path.exists()` guard |
| Múltiples assets present_in_production (ej: org_schema + whatsapp_button) | Baja | Iterar sobre la lista, generar una entrada por asset |

---

## 7. Relación con el Plan ASSET-ALIGNMENT-ZIONE

- **Origen**: Hallazgo 9.9 del contexto original `ZIONE-PROPOSAL-ASSET-ALIGNMENT-BLOCK-2026-07-23.md`
- **Fix intentado en**: FASE-4 (correcciones de presentación)
- **Fix parcial**: La FASE-4 corrigió MANIFEST sync y otras 5 issues, pero el README_DELIVERY no quedó completamente dinámico para `present_in_production`
- **Registrado como**: DT-1 en `08-analisis-post-implementacion.md`

---

## 8. Datos del ZIP de Prueba

Para referencia, el ZIP actual (`output/v4_complete/deliveries/zione_20260723.zip`, 46 archivos) contiene:

- `README_DELIVERY.md` — con las referencias hardcodeadas a `boton_whatsapp.html`
- `MANIFEST.json` — 46 entradas, sin `boton_whatsapp.html`
- Assets generados: optimization_guide, open_graph, faq_page, hotel_schema, etc.
- NO contiene: `boton_whatsapp.html` (present_in_production)

Evidencia completa en: `evidence/fase-5/`

---

*Contexto generado para intervención en nueva sesión. No modificar código en la sesión actual (FASE-5 ya cerrada).*
