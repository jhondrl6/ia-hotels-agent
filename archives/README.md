# Archivos de Respaldo e Históricos

**Última actualización:** 26 Noviembre 2025

---

## 📁 Estructura

```
archives/
├── backups/                              ← Respaldos pre-refactorización
│   ├── pre_injerto_narrativo_20251126/
│   ├── pre_refactor_20251125_193441/
│   └── (otros respaldos históricos)
├── docs_superseded/                      ← Documentación obsoleta
│   ├── docs_superseded_backup_20251126.zip  ← Comprimido (16 archivos)
│   └── INDICE_BACKUP.md                  ← Índice de contenido
├── deprecated_plans/                     ← Planes estratégicos obsoletos
│   ├── plan_maestro_v1_OBSOLETO.md
│   └── plan_maestro_v2_1_OBSOLETO.md
├── deprecated_structure_20251122_184345/ ← Estructura código antigua
│   ├── outputs/
│   └── templates/
└── outputs/                              ← Históricos de auditorías antiguas
    └── hotel_vísperas_20251101_200958/
```

---

## 🔄 Cuándo Usar Esta Carpeta

### Restaurar Respaldos Pre-Refactorización

```bash
# Listar respaldos disponibles
ls -la archives/backups/

# Si necesitas revertir cambios, descomprime el ZIP apropiado
# Ejemplo: restaurar estructura pre-refactor
cp -r archives/backups/pre_refactor_20251125_193441/ ./restore_point
```

### Consultar Documentación Histórica

```bash
# Si necesitas información de versiones anteriores
cd archives/docs_superseded/
unzip docs_superseded_backup_20251126.zip
# Buscar el archivo que necesitas en el contenido extraído
```

---

## 📊 Tamaño y Limpieza

| Carpeta | Tamaño | Frecuencia de Limpieza |
|---------|--------|----------------------|
| backups/ | ~50MB | Mantener últimos 3 respaldos |
| docs_superseded/ | ~120KB (ZIP) | Archivado, no requiere mantenimiento |
| deprecated_plans/ | ~100KB | Mantener por referencia |
| deprecated_structure_*/ | ~2MB | Eliminar después de 90 días |
| outputs/ | Variable | Limpiar outputs > 6 meses |

---

## 🛡️ Política de Respaldos

- **Automáticos antes de cambios mayores**: Sí, en `backups/`
- **Retención**: 3 últimos respaldos máximo
- **Compresión**: ZIP para reducir espacio
- **Documentación**: Cada respaldo tiene timestamp en nombre

---

## ❌ NO VERSIONABLE EN GIT

Estos archivos están en `.gitignore` y no se sincronizan:

```
archives/docs_superseded_backup_*.zip  ← Se versionan comprimidos
archives/deprecated_structure_*/       ← Código antiguo, no versionado
archives/outputs/                      ← Outputs históricos, no versionados
```

Solo `archives/backups/` se versionan si contienen configuración crítica.

---

**Archivos de respaldo y referencia histórica**  
**Versión:** 2.3.2

---

## deprecated_modules_20260304/

Módulos archivados el 2026-03-04 durante consolidación v4.4.1.

### Contenido

| Módulo | Razón de Archivado |
|--------|-------------------|
| `decision_engine.py` | Legacy v2.4.2, reemplazado por `financial_engine/` |
| `orchestrator/` | Legacy v3.x, reemplazado por `orchestration_v4/` |
| `generators/report_builder.py` | Huérfano, nunca usado |
| `generators/certificate_gen.py` | v2.2, versión más reciente en `delivery/generators/` |
| `utils/cac_tracker.py` | Huérfano, nunca usado |

### Tests Archivados

| Test | Razón |
|------|-------|
| `test_v23_integration.py` | Tests para flujo legacy v2.3 |
| `test_visperas_v242.py` | Tests para v2.4.2 |
| `test_v242_quick.py` | Tests para v2.4.2 |
| `test_pipeline_no_llm.py` | Tests para pipeline legacy |

---

**Archivos de respaldo y referencia histórica**  
**Versión:** 2.4.0
