# Patrón: Sincronización Documental Multi-Archivo Post-Release

**Categoría**: Mantenimiento de Documentación  
**Complejidad**: Media  
**Última actualización**: 2025-12-29 (v2.6.2)

---

## Contexto

Cada vez que se lanza una nueva versión del proyecto, múltiples archivos de documentación deben actualizarse de forma coordinada para mantener la coherencia entre:
- Documentación técnica (`GUIA_TECNICA.md`)
- Documentación de usuario (`README.md`)
- Índices y catálogos (`INDICE_DOCUMENTACION.md`)
- Documentación comercial (`PRECIOS_PAQUETES.md`)
- Roadmap estratégico (`ROADMAP.md`)
- Contexto del agente (`.cursorrules`)

## Problema

Sin un patrón documentado, es fácil olvidar actualizar algún archivo, causando:
- Versiones inconsistentes entre documentos
- Referencias a features antiguas en documentación nueva
- Usuarios confundidos sobre qué versión están usando
- Pérdida de trazabilidad de cambios

## Solución

### 1. Checklist de Archivos Afectados

Tras un release, actualizar **en este orden**:

```markdown
[ ] CHANGELOG.md (registro técnico completo - PRIMERO)
[ ] README.md (versión + banner con highlight del fix)
[ ] ROADMAP.md (marcar hito como completado)
[ ] GUIA_TECNICA.md (versión + nuevos componentes/umbrales)
[ ] INDICE_DOCUMENTACION.md (versión + sección de cambios recientes)
[ ] PRECIOS_PAQUETES.md (si afecta decisiones comerciales)
[ ] .cursorrules (registro de sesión + quick view)
```

### 2. Plantilla de Actualización por Archivo

#### README.md
```markdown
**Versión:** {version} | **Última actualización:** {fecha}

> **✅ MOTOR v{version} ({fecha})**: {resumen_cambios_1_linea}. [Ver CHANGELOG.md](CHANGELOG.md)
```

#### ROADMAP.md
```markdown
| v{version} | {feature_name} | 🟢 HECHO |
```

#### GUIA_TECNICA.md
```markdown
**Última actualización:** {fecha}  
**Versión:** {version}

# Estructura del Proyecto (actualizar si hay nuevos archivos)
├── tests/
│  ├── test_{nueva_feature}.py ← {descripción}

# Umbrales de Decisión (actualizar si hay nuevos benchmarks)
| `{nuevo_parametro}` | {valor} | **v{version}**: {descripción} |
```

#### INDICE_DOCUMENTACION.md
```markdown
**Versión:** {version}  
**Última actualización:** {fecha}

## 📋 Notas de Cambios Recientes (v{version})

### {Título del Cambio}

✅ **Cambios de Arquitectura:**
{lista de cambios}

✅ **Impacto Medible:**
{resultados cuantificables}

📖 **Ver documentación actualizada:**
{links a archivos modificados}
```

#### PRECIOS_PAQUETES.md
```markdown
**Última actualización:** {fecha}  
**Versión:** {version}

> **✅ MOTOR v{version}**: {cambio_que_afecta_decisiones}
```

#### .cursorrules
```markdown
<!-- cursorrules_version: {version} | last_update: {fecha} -->

## 🚦 Estado Actual (Quick View)
| **Versión** | v{version} ({DESCRIPTOR}) | {fecha} |

### [{fecha}] {Título de Sesión}
*   **Acción Técnica**: {qué se hizo}
*   **Documentación Sincronizada**: Actualizados N archivos clave (links)
*   **Verificación Real**: {evidencia cuantificable}
```

### 3. Script de Verificación (Opcional)

Para proyectos grandes, considera un script que verifique consistencia:

```python
# scripts/verify_doc_sync.py
import re

def check_version_consistency():
    """Ensure all docs reference the same version."""
    files = {
        'README.md': r'Versión:\*\* (\d+\.\d+\.\d+)',
        'GUIA_TECNICA.md': r'Versión:\*\* (\d+\.\d+\.\d+)',
        'INDICE_DOCUMENTACION.md': r'Versión:\*\* (\d+\.\d+\.\d+)',
        '.cursorrules': r'cursorrules_version: (\d+\.\d+\.\d+)'
    }
    
    versions = {}
    for file, pattern in files.items():
        with open(file) as f:
            match = re.search(pattern, f.read())
            if match:
                versions[file] = match.group(1)
    
    unique_versions = set(versions.values())
    if len(unique_versions) > 1:
        print(f"⚠️  Inconsistencia detectada: {versions}")
        return False
    
    print(f"✅ Todas las versiones sincronizadas: {unique_versions.pop()}")
    return True
```

---

## Caso de Uso: v2.6.2

Durante el release de la v2.6.2 (GBP Activity Score Precision Fix):

1. **CHANGELOG.md**: Documentado fix técnico con impacto cuantificado
2. **README.md**: Actualizado banner a v2.6.2 destacando "GBP Activity Score Precision Fix"
3. **ROADMAP.md**: Marcado hito v2.6.2 como 🟢 HECHO
4. **GUIA_TECNICA.md**: Agregado `fotos_meta: 15` a tabla de umbrales + referencia a nueva suite de tests
5. **INDICE_DOCUMENTACION.md**: Nueva sección "v2.6.2" con cambios de arquitectura
6. **PRECIOS_PAQUETES.md**: Actualizado header del motor con "Refined v2.6.2"
7. **.cursorrules**: Sesión consolidada registrada con evidencia de delivery

**Tiempo total**: ~15 minutos  
**Archivos sincronizados**: 6/6

---

## Checklist de Validación

Antes de cerrar la actualización documental:

- [ ] Todas las referencias a versión son consistentes
- [ ] Fechas de "última actualización" son correctas
- [ ] Links a archivos nuevos están incluidos
- [ ] CHANGELOG.md tiene la entrada más detallada
- [ ] README.md destaca el cambio principal en 1 línea
- [ ] .cursorrules tiene la sesión registrada con artefactos

---

## Referencias

- [actualizar_contexto.md](../workflows/actualizar_contexto.md) — Workflow de actualización de contexto
- [PROTOCOLO_CONTEXTO_AGENTE.md](../../docs/PROTOCOLO_CONTEXTO_AGENTE.md) — Protocolo completo
