# 06-prompt-fase-E — E2E (Zi One) + RELEASE

**Fase**: FASE-E — Validación E2E con Zi One + RELEASE + Análisis post-implementación
**Plan**: DT-1-DELIVERY-CONTRACT-2026-07-23
**Sesión**: Nueva (fresh)
**Iteraciones máx**: 80
**Depende de**: FASE-A ✅, FASE-B ✅, FASE-C ✅, FASE-D ✅
**Bloquea a**: Ninguna (fase final)
**⚠️ CONTIENE COMANDO LARGO** (v4complete, ~8-10 min)
**Tipo**: DIRECTA (E2E + docs cascade)

---

## Objetivo

Ejecutar `v4complete` para Zi One Luxury y verificar que el ZIP generado cumple el contrato de delivery completo. Luego ejecutar el ciclo RELEASE: CHANGELOG, VERSION, sync, validaciones y commit.

## Contexto de fases anteriores

- FASE-A: Contrato canónico de estados definido.
- FASE-B: Pipeline físico corregido (POSIX, tamaños reales, validación post-zip).
- FASE-C: README dinámico con secciones por estado.
- FASE-D: Tests cross-artifact y gate de no-regresión.

Todas las fases previas están implementadas y testeadas. Esta fase valida el comportamiento E2E con un hotel real.

## Tareas

### T0: Verificar datos operativos del cliente (PRE-V4COMPLETE)

Antes de ejecutar v4complete, verificar que los datos operativos del cliente están disponibles y son consistentes:

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# Leer datos operativos del cliente
cat output/clientes/zi-one-luxury_onboarding.yaml
```

Verificar:
- [ ] El archivo `output/clientes/zi-one-luxury_onboarding.yaml` existe y tiene datos Tier A
- [ ] `habitaciones: 34`, `reservas_mes: 800`, `valor_reserva_cop: 290000`, `canal_directo_pct: 40.0`
- [ ] La fuente es `data/hotel_observations/observations.json` (Tier A verified, confidence 0.95)
- [ ] Los datos operativos son consistentes con lo que v4complete usará del scraping en vivo

Si el archivo no existe o tiene datos inconsistentes, documentar la discrepancia pero NO bloquear — v4complete usa scraping en vivo como fuente primaria; el YAML es referencia de ground truth.

### T1: Ejecutar v4complete para Zi One Luxury ⚠️ COMANDO LARGO

**Paso previo (OBLIGATORIO)**: Limpiar el directorio de output de Zi One para evitar evidencia stale o mezclada de ejecuciones anteriores:

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
rm -rf output/ZiOne/v4_complete/
```

> **Razón**: El contexto DT-1 §11 advierte que ejecutar v4complete sobre outputs existentes produce evidencia mezclada/stale. La limpieza garantiza que el ZIP, README, manifest y reportes sean exclusivamente de esta ejecución.

Ejecutar v4complete para Zi One y capturar toda la evidencia:

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe main.py v4complete --url https://zione.co/
```

**Tiempo estimado**: 5-10 minutos.

**Output esperado**: ZIP en `output/ZiOne/v4_complete/deliveries/zione_YYYYMMDD.zip`.

Después de que termine, copiar la evidencia al directorio de evidencia de la fase:

```bash
mkdir -p evidence/fase-E
cp output/ZiOne/v4_complete/deliveries/zione_*.zip evidence/fase-E/
cp output/ZiOne/v4_complete/zione/v4_audit/asset_generation_report.json evidence/fase-E/
cp output/ZiOne/v4_complete/zione/v4_audit/gate_report_*.json evidence/fase-E/
```

### T2: Verificación post-v4complete del delivery

Extraer y verificar el ZIP generado:

```python
import zipfile, json, re
from pathlib import Path

zip_path = sorted(Path("output/ZiOne/v4_complete/deliveries").glob("zione_*.zip"))[-1]
print(f"Verificando: {zip_path}")

with zipfile.ZipFile(zip_path, 'r') as z:
    names = z.namelist()
    manifest = json.loads(z.read("MANIFEST.json"))
    readme = z.read("README_DELIVERY.md").decode("utf-8")
    
    checks = []
    
    # 1. WhatsApp no está en ZIP como archivo
    checks.append(("whatsapp_button not in ZIP", 
                   not any("boton_whatsapp" in n.lower() for n in names)))
    
    # 2. WhatsApp no está en README como instrucción de instalación
    checks.append(("README no instrucciones whatsapp_button",
                   "Add WhatsApp button to footer" not in readme))
    
    # 3. WhatsApp aparece en sección de presencia
    checks.append(("README menciona WhatsApp en contexto de presencia",
                   any(phrase in readme.lower() for phrase in 
                       ["already present", "present but requires", "presente en", "ya implementado"])))
    
    # 4. Rutas POSIX en manifest
    checks.append(("manifest rutas POSIX",
                   not any("\\" in f["name"] for f in manifest["files"])))
    
    # 5. Tamaños reales en manifest
    readme_manifest = next((f for f in manifest["files"] if f["name"] == "README_DELIVERY.md"), None)
    manifest_manifest = next((f for f in manifest["files"] if f["name"] == "MANIFEST.json"), None)
    checks.append(("README size > 0", readme_manifest and readme_manifest["size_bytes"] > 0))
    checks.append(("MANIFEST size > 0", manifest_manifest and manifest_manifest["size_bytes"] > 0))
    
    # 6. total_files coincide
    checks.append(("total_files matches", manifest["total_files"] == len(names)))
    
    # 9. No hardcoded asset names
    checks.append(("no hardcoded boton_whatsapp.html", "boton_whatsapp.html" not in readme))
    checks.append(("no hardcoded hotel-schema.json", "hotel-schema.json" not in readme))
    checks.append(("no hardcoded geo_playbook.md", "geo_playbook.md" not in readme))
    
    # 9.1 Advisory Guides section present for whatsapp_conflict_guide
    if any("whatsapp_conflict_guide" in n.lower() or "guia_conflicto" in n.lower() for n in names):
        checks.append(("Advisory Guides section present",
                       "Advisory Guides" in readme or "advisory" in readme.lower()))
    
    # 10. Package filename correcto
    checks.append(("ZIP filename in README", zip_path.name in readme))
    
    # 9. _validate_zip() pasa
    from modules.delivery.delivery_packager import DeliveryPackager
    packager = DeliveryPackager()
    errors = packager._validate_zip(zip_path, manifest)
    checks.append(("_validate_zip passes", len(errors) == 0))
    
    # Reportar
    for name, passed in checks:
        print(f"{'✅' if passed else '❌'} {name}")
        if not passed and name == "_validate_zip passes":
            for e in errors:
                print(f"   - {e}")
    
    all_pass = all(p for _, p in checks)
    print(f"\n{'✅ ALL CHECKS PASSED' if all_pass else '❌ SOME CHECKS FAILED'}")
```

**Si algún check falla**: documentar el fallo, NO continuar a RELEASE hasta resolver.

### T3: RELEASE (docs cascade + version bump + sync + commit)

**Solo si T2 pasó todos los checks.**

Agrupar las tareas de RELEASE en 4 bloques:

**Bloque 1 — Diagnóstico + sync de versiones**:

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
# Verificar estado de versión actual
./venv/Scripts/python.exe scripts/version_consistency_checker.py

# Leer versión actual de VERSION.yaml
./venv/Scripts/python.exe -c "import yaml; v=yaml.safe_load(open('VERSION.yaml')); print(f'Current: {v[\"version\"]}')"
```

**Verificar versión previa**: Si VERSION.yaml dice `4.63.0`, hacer bump a `4.63.1`. Si dice `4.62.0` (el RELEASE de ASSET-ALIGNMENT no se ejecutó), hacer bump a `4.63.0` (no 4.63.1) y actualizar el codename y CHANGELOG consecuentemente. Ajustar el número de versión en todos los bloques siguientes según corresponda.

Editar `VERSION.yaml` para bump PATCH:

```yaml
version: "4.63.1"
release_date: "2026-07-23"
codename: "Delivery-Contract"
```

Ejecutar sync:

```bash
./venv/Scripts/python.exe scripts/sync_versions.py
```

**Bloque 2 — CHANGELOG + GUIA_TECNICA**:

Actualizar `CHANGELOG.md` con entrada `[4.63.1]`:

```markdown
## [4.63.1] - 2026-07-23

### Delivery Contract — README, Manifest y ZIP cross-artifact consistency

**Objetivo**: Resolver la desincronización entre README_DELIVERY.md, MANIFEST.json,
ZIP y estados de assets. El README ahora se genera desde los destinos reales del ZIP
y respeta el estado canónico de cada asset.

### Cambios Implementados
- FASE-A: `DeliveryAssetState` enum, `DeliveryAssetEntry` (con `is_advisory`), `DeliveryContext` (con `from_asset_generation_report()`) en `delivery_context.py`
- FASE-B: Rutas POSIX en manifest/ZIP, tamaños reales, filename único, `_validate_zip()`, carga automática de `DeliveryContext` en `package()`
- FASE-C: README dinámico con secciones por estado (Present/Issues/Estimated/Advisory Guides/Evidence)
- FASE-D: Tests cross-artifact (19+ tests) + gate de no-regresión `DeliveryValidationError`
- FASE-E: E2E validation con Zi One Luxury + RELEASE

### Archivos Modificados
- `modules/delivery/delivery_context.py` — +DeliveryAssetState, +DeliveryAssetEntry (is_advisory), +DeliveryContext (from_asset_generation_report)
- `modules/delivery/delivery_packager.py` — Rutas POSIX, tamaños reales, README dinámico, validación, carga DeliveryContext
- `modules/assessment_builder.py` — Propagación de pain_ids_affected en skipped_assets
- `templates/delivery_readme_template.md` — Template modular sin hardcodeos + sección Advisory Guides
- `tests/delivery/test_delivery_contract.py` — 19+ tests de contrato cross-artifact

### Tests
- 10 tests existentes del packager: PASS
- 19+ tests nuevos de contrato: PASS
```

Actualizar `docs/GUIA_TECNICA.md` con nota técnica:

```markdown
## Notas de Cambios v4.63.1 — Delivery Contract

**Resumen**: El sistema de delivery ahora garantiza consistencia cross-artifact
(README ↔ MANIFEST ↔ ZIP) mediante un contrato canónico de estados de assets.

**Módulos afectados**: `modules/delivery/`, `modules/assessment_builder.py`

**Arquitectura**: `DeliveryAssetState` → `DeliveryAssetEntry` (con `is_advisory`) → `DeliveryContext` (con `from_asset_generation_report()`) →
template modular → validación post-zip obligatoria.

**Backwards compatibility**: El packager mantiene comportamiento legacy si no recibe
`DeliveryContext`. La template legacy se reemplazó completamente; los placeholders
nuevos quedan vacíos en modo legacy.
```

**Bloque 3 — Skills/workflows + SYSTEM_STATUS**:

```bash
# Verificar skills/workflows
ls .agents/workflows/*.md | wc -l

# Regenerar SYSTEM_STATUS
./venv/Scripts/python.exe scripts/doctor.py --status
```

**Bloque 4 — DOMAIN_PRIMER + symlink + validación final + commit**:

```bash
# Regenerar Domain Primer
./venv/Scripts/python.exe scripts/doctor.py --regenerate-domain-primer

# Validación final
./venv/Scripts/python.exe scripts/run_all_validations.py --quick

# Commit
git add -A
git commit -m "release: v4.63.1 — Delivery Contract cross-artifact consistency"
```

### T4: Análisis post-implementación y lecciones aprendidas

**Objetivo**: Completar el archivo `08-analisis-post-implementacion.md` con los resultados reales de TODAS las fases (A→E).

**Procedimiento**:

1. Leer la template:
```bash
cat /.opencode/plans/Archives/DT-1-DELIVERY-CONTRACT-2026-07-23/08-analisis-post-implementacion.md
```

2. Completar cada sección con datos reales de la ejecución:

   **§1 — Resumen de Ejecución por Fase**: Estado final de cada fase, delegate_task real, iteraciones consumidas, complejidad real.

   **§2 — Cifras Esperadas vs Reales**: Completar la columna "Post-fix (real)" con valores verificados del ZIP generado. Marcar cada métrica ✅/❌/⚠️.

   **§3 — Matriz de Verificación de Hallazgos (14/14)**: Para cada hallazgo F-01 a F-14, verificar si el criterio de éxito se cumplió. Estado: ✅ SUPERADO / ⚠️ PARCIAL / ❌ NO RESUELTO / ⏭️ FUERA DE ALCANCE.

   **§4 — Fuentes de Datos**: Confirmar que `output/clientes/zi-one-luxury_onboarding.yaml` fue verificado en T0. Documentar cualquier discrepancia entre datos operativos YAML y scraping en vivo.

   **§5 — Fase de Mayor Complejidad**: Identificar cuál de las 5 fases fue la más compleja y por qué. Incluir lección específica.

   **§6 — Evaluación de delegate_task**: Comparar modo planeado vs real. ¿La matriz fue precisa? ¿Hubo desviaciones?

   **§7 — Tabla de Riesgos**: Completar columna "Resultado" para cada riesgo. ¿Se materializó? ¿La mitigación funcionó?

   **§9 — Lecciones Aprendidas**: Recopilar de TODAS las fases. Categorizar en:
   - Planificación: ¿qué se planificó bien/mal?
   - Ejecución: ¿qué funcionó/sorprendió?
   - Verificación: ¿el E2E detectó lo esperado?
   - Delivery Contract: ¿el patrón de contrato canónico funcionó?

   **§10 — Deuda Técnica**: Revisar si la deuda registrada (TD-1 a TD-4) sigue vigente o fue resuelta. Agregar nueva deuda descubierta.

   **§11 — Evidencia**: Confirmar que todos los archivos listados están en `evidence/fase-E/`.

3. Actualizar `09-documentacion-post-proyecto.md` Sección E (Lecciones aprendidas) con un resumen de las lecciones de §9.

**Output esperado**: `08-analisis-post-implementacion.md` completamente rellenado con datos reales, sin placeholders `(completar)` restantes.

## Criterios de Completitud

- [ ] T0: Datos operativos de `output/clientes/zi-one-luxury_onboarding.yaml` verificados.
- [ ] v4complete Zi One se ejecutó exitosamente.
- [ ] Directorio `output/ZiOne/v4_complete/` fue limpiado antes de la ejecución.
- [ ] ZIP generado contiene README_DELIVERY.md sin `boton_whatsapp.html` como entregable.
- [ ] WhatsApp aparece en sección de presencia/revisión (no instalación).
- [ ] Manifest usa rutas POSIX, tamaños reales, total_files correcto.
- [ ] `_validate_zip()` pasa sin errores.
- [ ] CHANGELOG.md tiene entrada de versión completa.
- [ ] VERSION.yaml actualizado (verificando versión previa antes del bump).
- [ ] `sync_versions.py` ejecutado sin errores.
- [ ] GUIA_TECNICA.md tiene nota técnica para v4.63.1.
- [ ] DOMAIN_PRIMER.md regenerado.
- [ ] `run_all_validations.py --quick` pasa.
- [ ] Commit realizado con mensaje descriptivo.
- [ ] Evidencia copiada a `evidence/fase-E/`.
- [ ] `08-analisis-post-implementacion.md` completado con datos reales (sin placeholders).
- [ ] Matriz de verificación 14/14 hallazgos completada con estados reales.
- [ ] Lecciones aprendidas de TODAS las fases documentadas en §9.
- [ ] Sección E de `09-documentacion-post-proyecto.md` actualizada con resumen de lecciones.

## Restricciones

- NO modificar código en esta fase (solo verificar y documentar).
- NO ejecutar v4complete para otros hoteles.
- NO modificar `main.py` ni lógica de negocio.
- Si T2 falla, NO continuar a RELEASE. Reportar el fallo y detener.

## Archivos involucrados

| Archivo | Tipo de cambio |
|---------|---------------|
| `VERSION.yaml` | MODIFICAR (bump a 4.63.1) |
| `CHANGELOG.md` | MODIFICAR (agregar entrada) |
| `docs/GUIA_TECNICA.md` | MODIFICAR (nota técnica) |
| `evidence/fase-E/` | CREAR (evidencia de validación) |
| Archivos auto-sync | MODIFICADOS por sync_versions.py |

## Post-Ejecución (OBLIGATORIO)

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-E --desc "DT1_E2E_ZiOne_v4complete_RELEASE_v4.63.1" --check-manual-docs
```
