# FASE-PATCH-D: Documentation + Version Sync + Technical Debt

**ID**: FASE-PATCH-D
**Objetivo**: Resolver version drift (4.36.0→4.36.1), crear derive_version_from_changelog.py, corregir AGENTS.md (H-7/H-8), catalogar deuda técnica H-9→H-27, y ejecutar docs cascade para fases PATCH-A/B/C
**Dependencias**: FASE-PATCH-A ✅ + FASE-PATCH-B ✅ + FASE-PATCH-C ✅
**Duración estimada**: ~45-60 min
**Skill**: iah-cli-phased-execution

---

## Contexto

Esta fase resuelve los pendientes de infraestructura y documentación. NO modifica código fuente de producción.

### 🔄 Version Drift

- **CHANGELOG.md** L3: `## [4.36.1] - 2026-04-28`
- **VERSION.yaml** L3: `version: "4.36.0"`
- **Causa**: La sesión 2026-04-28 decidió registrar 4.36.1 en CHANGELOG pero no actualizó VERSION.yaml para "evitar mentira documental". Esto dejó un drift que `version_consistency_checker.py` detecta.
- **`derive_version_from_changelog.py`**: Referenciado en `version_consistency_checker.py` L296 como solución, pero el script NUNCA fue creado.

### Documentación

- **H-7**: AGENTS.md tiene 3 números de tests distintos (2224, 1782, 2363). El real es ~2363 funciones, 185 archivos.
- **H-8**: AGENTS.md documenta 5 gates. `publication_gates.py` define 9 (6 blocking + 3 advisory). Faltan: ethics, content_quality, asset_confidence, proposal_asset_alignment.

### Deuda Técnica

- **H-9→H-27**: 20+ hardcodes en pricing, escenarios, fallbacks. NO se corrigen en este PATCH — se catalogan para proyecto futuro.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-1-AMAZILIA-CORRECCION | ✅ Completada |
| FASE-PATCH-A (bugs + stubs + unicode) | ✅ Completada |
| FASE-PATCH-B (placeholders + evidence) | ✅ Completada |
| FASE-PATCH-C (v4complete verification) | ✅ Completada |

---

## Tareas

### Tarea 1: Crear derive_version_from_changelog.py + Resolver version drift

**Objetivo**: Crear el script faltante y formalizar VERSION.yaml → 4.36.1.

**Paso 1.1: Crear `scripts/derive_version_from_changelog.py`**

El script debe:
1. Leer CHANGELOG.md
2. Extraer la versión más reciente (primera entrada `## [X.Y.Z]`)
3. Escribir el campo `version` en VERSION.yaml
4. Preservar el resto del YAML (codename, comentarios, etc.)

Usar como base `extract_latest_version_from_changelog()` de `version_consistency_checker.py` L34-47.

Template mínimo:
```python
#!/usr/bin/env python3
"""Derive VERSION.yaml from CHANGELOG.md latest entry."""
import re, sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
CHANGELOG = ROOT_DIR / "CHANGELOG.md"
VERSION = ROOT_DIR / "VERSION.yaml"

# Fix Windows encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

def extract_latest_version(path):
    content = path.read_text(encoding="utf-8")
    match = re.search(r'^##\s+\[v?(\d+\.\d+\.\d+)\]', content, re.MULTILINE)
    return match.group(1) if match else None

def update_version_yaml(yaml_path, new_version):
    lines = yaml_path.read_text(encoding="utf-8").splitlines()
    new_lines = []
    for line in lines:
        if line.startswith("version:"):
            new_lines.append(f'version: "{new_version}"')
        else:
            new_lines.append(line)
    yaml_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

def main():
    ver = extract_latest_version(CHANGELOG)
    if not ver:
        print("ERROR: No version found in CHANGELOG.md")
        return 1
    update_version_yaml(VERSION, ver)
    print(f"VERSION.yaml → {ver}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

**Paso 1.2: Ejecutar derive + sync**

```bash
# Derivar versión desde CHANGELOG
./venv/Scripts/python.exe scripts/derive_version_from_changelog.py

# Verificar que VERSION.yaml ahora dice 4.36.1
grep "version:" VERSION.yaml

# Sincronizar a los 6 archivos
./venv/Scripts/python.exe scripts/sync_versions.py

# Verificar consistencia
./venv/Scripts/python.exe scripts/version_consistency_checker.py
```

**Criterios de aceptación**:
- [ ] `scripts/derive_version_from_changelog.py` creado y funcional
- [ ] VERSION.yaml muestra `version: "4.36.1"`
- [ ] `sync_versions.py` ejecutado sin errores
- [ ] `version_consistency_checker.py` reporta ✅ SINCRONIZADO (ya con unicode fix)

### Tarea 2: Corregir AGENTS.md (H-7 + H-8)

**Objetivo**: Unificar test count y documentar gates reales.

**H-7 fix**:
1. Ejecutar conteo real de tests:
   ```bash
   ./venv/Scripts/python.exe -m pytest --collect-only -q 2>/dev/null | tail -1
   ```
2. Buscar TODAS las ocurrencias de números de tests en AGENTS.md:
   ```bash
   grep -n "funciones\|tests\|funciones" AGENTS.md
   ```
3. Reemplazar cada número inconsistente por el valor real (~2363 funciones, 185 archivos)
4. Verificar que AGENTS.md ahora tiene UN solo número consistente

**H-8 fix**:
1. Verificar gates reales en código:
   ```bash
   grep -n "class.*Gate\|def.*gate" modules/postprocessors/publication_gates.py | head -20
   ```
2. En AGENTS.md, buscar la sección que menciona "5 gates" o similar
3. Actualizar a "9 gates (6 blocking + 3 advisory)" con lista completa

**Criterios de aceptación**:
- [ ] AGENTS.md tiene UN solo número de tests (consistente)
- [ ] AGENTS.md documenta 9 gates con nombres correctos
- [ ] No hay otras referencias a "2224" o "1782" en AGENTS.md

### Tarea 3: Catalogar deuda técnica H-9→H-27

**Objetivo**: Crear documento de deuda técnica que sirva como input para un futuro proyecto de extracción de config.

**Crear `docs/technical_debt/hardcodes_audit_2026-04-29.md`** con:

```markdown
# Hardcodes Audit — AmaziliaHotel Forensic (2026-04-29)

**Fuente**: ContextMv2.md §Hardcodes
**Severidad**: HIGH (impactan pricing, ROI, y credibilidad comercial)
**Estado**: NO CORREGIDOS — catalogados como deuda técnica para proyecto futuro

## Catálogo

| ID | Elemento | Archivo:Línea | Valor Hardcodeado | Recomendación |
|----|----------|---------------|-------------------|---------------|
| H-9 | MONTHLY_PACKAGE_PRICE | proposal L52 | 1,200,000 | Extraer a pricing_config.yaml |
| H-10 | SETUP_FEE | proposal L53 | 2,500,000 | Extraer a pricing_config.yaml |
| ... | ... | ... | ... | ... |

## Recomendación de Abordaje

1. Crear `config/pricing.yaml` con TIER_CONFIG completo
2. Migrar fallbacks (50, 70, 85) a `config/fallbacks.yaml`
3. Extraer scenario assumptions a `config/scenarios.yaml`
4. Cada extracción requiere: migración + tests + backwards compatibility
```

**Usar la tabla completa de ContextMv2.md (H-9 a H-27) para poblar el catálogo.**

**Criterios de aceptación**:
- [ ] Archivo creado en `docs/technical_debt/hardcodes_audit_2026-04-29.md`
- [ ] Contiene los 19 items (H-9 a H-27) con archivo, línea, valor, y recomendación
- [ ] Incluye recomendación de abordaje

### Tarea 4: Docs cascade para PATCH-A, B, C

**Objetivo**: Ejecutar log_phase_completion.py para las 3 fases de implementación.

```bash
# FASE-PATCH-A
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-PATCH-A \
    --desc "Fix BUG-1 (ROI X), BUG-2 (pain_ratio), H-3/H-4/H-5 (stubs), unicode crash" \
    --archivos-mod "modules/commercial_documents/v4_proposal_generator.py,modules/commercial_documents/v4_diagnostic_generator.py,scripts/version_consistency_checker.py" \
    --check-manual-docs

# FASE-PATCH-B
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-PATCH-B \
    --desc "Fix H-1 (web_score placeholder), H-2 (phone placeholder), H-6 (Evidence Tier)" \
    --archivos-mod "modules/commercial_documents/v4_proposal_generator.py,modules/orchestration_v4/two_phase_flow.py,modules/financial_engine/scenario_calculator.py" \
    --check-manual-docs

# FASE-PATCH-C
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-PATCH-C \
    --desc "v4complete verification - todos los fixes reflejados en output" \
    --check-manual-docs

# Validación final
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

**Criterios de aceptación**:
- [ ] REGISTRY.md tiene entradas para FASE-PATCH-A, B, C
- [ ] No hay [GAP] en DOCUMENTATION AUDIT
- [ ] run_all_validations.py --quick: 4/4

---

## Post-Ejecución (OBLIGATORIO)

1. Actualizar `dependencias-fases-v2.md`: marcar FASE-PATCH-D como ✅
2. Actualizar `06-checklist-implementacion-v2.md`: marcar items de PATCH-D
3. Actualizar `README-v2.md`: tabla de progreso
4. Verificar que todo está listo para FASE-RELEASE-4.37.0

---

## Criterios de Completitud (CHECKLIST)

- [x] `derive_version_from_changelog.py` creado y funcional
- [x] VERSION.yaml = 4.36.1, sincronizado con CHANGELOG
- [x] sync_versions.py ejecutado
- [x] version_consistency_checker.py reporta SINCRONIZADO
- [x] AGENTS.md test count unificado (1 solo número)
- [x] AGENTS.md gates: 9 documentados
- [x] `docs/technical_debt/hardcodes_audit_2026-04-29.md` creado con H-9→H-27
- [x] REGISTRY.md actualizado con PATCH-A, B, C
- [x] run_all_validations.py --quick: 4/4

---

## Restricciones

- **NO modificar código fuente** de producción (solo scripts y docs)
- **NO ejecutar v4complete**
- **NO modificar ROADMAP.md**
- **Máximo 60 iteraciones**
