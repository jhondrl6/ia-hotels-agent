# Módulos Archivados - v4.6.0

**Fecha:** 23 Marzo 2026
**Versión:** IA Hoteles Agent v4.6.0
**Razón:** Limpieza post-FASE 10 - Módulos huérfanos/sin uso

---

## Módulos Archivados

### modules_generators/ (3 archivos)

| Archivo | Estado | Razón |
|---------|--------|-------|
| `proposal_gen.py` | HUÉRFANO | Reemplazado por `commercial_documents/v4_proposal_generator.py` |
| `seo_report_builder.py` | HUÉRFANO | Sin uso en flujos activos |
| `toolkit_consultor_gen.py` | HUÉRFANO | Sin uso en flujos activos |

### modules_validation/ (3 archivos)

| Archivo | Estado | Razón |
|---------|--------|-------|
| `content_validator.py` | HUÉRFANO | Funcionalidad similar a `asset_generation/asset_content_validator.py` |
| `plan_validator.py` | HUÉRFANO | Sin uso en flujos activos |
| `security_validator.py` | HUÉRFANO | Sin uso en flujos activos |

### modules_knowledge/ (1 archivo)

| Archivo | Estado | Razón |
|---------|--------|-------|
| `graph_manager.py` | HUÉRFANO | Solo usado por watchdog, que tampoco se utiliza |

### modules_watchdog/ (2 archivos)

| Archivo | Estado | Razón |
|---------|--------|-------|
| `scanner.py` | HUÉRFANO | No se importa en main.py ni flujos activos |
| `truth_validator.py` | HUÉRFANO | No se importa en ningún lugar |

---

## Comando Deprecated

| Comando | Archivo Referencia | Estado |
|---------|-------------------|--------|
| `audit` | `main.py` | DEPRECATED - Usar `v4complete` en su lugar |

---

## Restauración

Si en el futuro se necesitan estos módulos:

```bash
# Restaurar un módulo específico
mv docs/archive/legacy_code/modules_generators/proposal_gen.py modules/generators/

# Restaurar un directorio completo
mv docs/archive/legacy_code/modules_validation modules/
```

---

## Decisión de Archivo vs Eliminación

Estos módulos fueron **archivados** (no eliminados) porque:
1. Podrían contener lógica útil para referencia
2. Permiten rollback rápido si se necesitan
3. Documentan la evolución del proyecto

**Eliminar definitivamente** después de 6 meses sin necesidad de rollback.
