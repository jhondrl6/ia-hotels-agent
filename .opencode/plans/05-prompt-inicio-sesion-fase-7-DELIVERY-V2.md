# FASE 7: Delivery Pipeline v2 - Automated Packaging

**ID**: FASE-7-DELIVERY-V2
**Objetivo**: Implementar pipeline de delivery automatizado con packaging
**Dependencias**: FASE 6 completada
**Duración estimada**: 1-2 horas
**Skill**: delivery-pipeline, automation

---

## Problema Actual

```
- Assets en folders dispersos
- No hay packaging automatizado
- Entrega manual requiere copy-paste
```

---

## Solución: Delivery Package

```
output/v4_complete/hotel_visperas/
    ├── 01_DIAGNOSTICO.md
    ├── 02_PROPUESTA.md
    └── hotel_visperas/
        ├── geo_playbook/
        └── ...

↓
    
deliveries/hotel_visperas_20260323.zip
    ├── DIAGNOSTICO.md
    ├── PROPUESTA_COMERCIAL.md
    ├── ASSETS/
    │   ├── geo_playbook.md
    │   └── ...
    ├── MANIFEST.json
    └── README_DELIVERY.md
```

---

## Tareas

### T7A: Crear DeliveryPackager
**Archivo**: `modules/delivery/delivery_packager.py` (NUEVO)

```python
class DeliveryPackager:
    def package(hotel_id: str, output_dir: str) -> str:
        """Crea ZIP con todos los assets"""
    
    def create_manifest(hotel_id: str, assets: list) -> dict:
        """Genera manifest.json"""
    
    def create_readme(delivery_dir: str) -> None:
        """Genera README con instrucciones"""
```

### T7B: Integrar en Orchestration
**Archivo**: `modules/orchestration_v4/` (modificar)

```python
# Después de asset generation
packager = DeliveryPackager()
delivery_path = packager.package(hotel_id, output_dir)
```

### T7C: Template README Delivery
**Archivo**: `templates/delivery_readme_template.md` (NUEVO)

Secciones:
- Overview de deliverables
- Instrucciones por asset
- Timeline sugerido
- Checklist de implementación

---

## Tests Obligatorios

| Test | Criterio |
|------|----------|
| `test_package_creates_zip` | ZIP existe con todos los assets |
| `test_manifest_complete` | Manifest incluye todos los assets |
| `test_readme_generated` | README existe con instrucciones |

---

## Criterios de Completitud

- [ ] DeliveryPackager implementado
- [ ] Packaging genera ZIP válido
- [ ] README con instrucciones generado
- [ ] Integración en orchestration funciona
- [ ] Tests pasan
