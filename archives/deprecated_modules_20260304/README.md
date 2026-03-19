# Módulos Archivados - Consolidación v4.4.1

**Fecha de archivado:** 2026-03-04  
**Versión del sistema:** 4.4.1  
**Razón:** Limpieza de módulos legacy y consolidación de arquitectura

---

## 📁 Estructura del Archivo

```
deprecated_modules_20260304/
├── README.md                    ← Este archivo
├── decision_engine.py           ← Motor de reglas v2.4.2 (legacy)
├── generators/
│   ├── report_builder.py       ← Huérfano (sin uso)
│   └── certificate_gen.py      ← v2.2 obsoleto
├── orchestrator/
│   ├── __init__.py
│   ├── pipeline.py             ← Pipeline v3.x (legacy)
│   ├── stage_handlers.py       ← Handlers v3.x (legacy)
│   └── mixins.py
├── tests/
│   ├── test_v23_integration.py ← Tests flujo v2.3
│   ├── test_visperas_v242.py   ← Tests v2.4.2
│   ├── test_v242_quick.py      ← Tests v2.4.2
│   └── test_pipeline_no_llm.py ← Tests pipeline
└── utils/
    └── cac_tracker.py          ← Huérfano (sin uso)
```

---

## 📦 Módulos Archivados

### `decision_engine.py`

- **Versión:** v2.4.2
- **Estado:** Legacy, reemplazado por `modules/financial_engine/`
- **Último uso:** Comandos `audit`, `stage` (ahora deprecados)
- **Reemplazo:** `modules/financial_engine/scenario_calculator.py`

### `orchestrator/`

- **Versión:** v3.x
- **Estado:** Legacy, reemplazado por `modules/orchestration_v4/`
- **Componentes:**
  - `pipeline.py` - Pipeline de análisis v3.x
  - `stage_handlers.py` - Lógica de etapas
  - `mixins.py` - Utilidades compartidas
- **Reemplazo:** `modules/orchestration_v4/two_phase_flow.py`

### `generators/report_builder.py`

- **Estado:** Huérfano, nunca utilizado en producción
- **Reemplazo:** `modules/generators/report_builder_fixed.py`

### `generators/certificate_gen.py`

- **Versión:** v2.2
- **Estado:** Obsoleto, versión más reciente existe en `delivery/generators/`
- **Reemplazo:** `modules/delivery/generators/certificate_gen.py` (v2.5.3)

### `utils/cac_tracker.py`

- **Estado:** Huérfano, implementación incompleta
- **Función prevista:** Tracking de Costo de Adquisición de Cliente (CAC)
- **Estado actual:** Sin uso, sin integración

---

## 🔄 Comandos Afectados

| Comando | Estado | Alternativa |
|---------|--------|-------------|
| `audit` | ⚠️ Deprecado | `v4complete` |
| `stage` | ⚠️ Deprecado | `v4complete` |
| `spark` | ⚠️ Deprecado | `v4complete` |
| `v4audit` | ✅ Activo | - |
| `v4complete` | ✅ Activo (recomendado) | - |

---

## 📊 Tests Archivados

| Test | Cobertura | Razón de Archivado |
|------|-----------|-------------------|
| `test_v23_integration.py` | Integración v2.3 | Flujo legacy |
| `test_visperas_v242.py` | Caso Visperas v2.4.2 | Versión obsoleta |
| `test_v242_quick.py` | Quick tests v2.4.2 | Versión obsoleta |
| `test_pipeline_no_llm.py` | Pipeline sin LLM | Pipeline archivado |

---

## 🛡️ Política de Retención

- **Retención mínima:** 180 días (hasta 2026-09-01)
- **Posible eliminación:** Después de 2026-09-01 si no hay referencias activas
- **Restauración:** Copiar archivo(s) necesario(s) a ubicación original

---

## ⚠️ NO USAR EN PRODUCCIÓN

Estos módulos están archivados por:
1. **Obsolescencia:** Reemplazados por implementaciones v4.x
2. **Incompatibilidad:** No compatibles con arquitectura actual
3. **Seguridad:** Sin mantenimiento de parches de seguridad

---

**Archivo creado:** 2026-03-04  
**Sistema:** IA Hoteles Agent v4.4.1
