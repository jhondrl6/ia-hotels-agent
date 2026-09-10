# FASE-T2-B: Revisor de Completitud de Assets (Bot 3)

**ID**: TRIBUNAL-OFFLINE-2026-09-09 / FASE-T2-B
**Objetivo**: Implementar `tribunal/asset_reviewer.py` — revisor determinista que verifica cobertura de assets por servicio, detecta assets genéricos, ESTIMATED no etiquetados, y `IMPLEMENTATION_ORDER.md` vacío. Produce `revision_assets.json`.
**Dependencias**: FASE-T1 ✅ (contrato de acta estable)
**Complejidad técnica**: **MEDIA** — módulo determinista, lectura de artefactos + filesystem, sin LLM
**Modo de ejecución**: **DIRECTO** (agente principal). NO delegable: la fase crea un módulo **y corre tests que importan el proyecto**; el venv es Windows accedido desde WSL ⟹ ejecutor v2.20.0, branch «imports del proyecto + venv Windows → DIRECTA… NO delegar a subagentes».
**Skill**: `phased_project_executor.md` v2.20.0

---

## Contexto

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-T1 | ✅ Completada (contrato de acta definido) |
| FASE-T2-A | ✅ o ⬜ (independiente de esta fase) |
| FASE-T2-B | ← ESTA FASE |

### Base Técnica Disponible

- **Contrato de acta** (T1): `modules/quality_gates/tribunal/judge.py`
- **Artefactos que Bot 3 lee**:
  - `asset_generation_report.json` (qué assets se generaron, con qué confidence) — en `v4_audit/`
  - `delivery_quality_report.json` (QA post-generación) — en `v4_audit/`
  - `MANIFEST.json` (lista de archivos del paquete) — **en `deliveries_dir`**
  - Archivos reales en `ASSETS/` — **en `deliveries_dir`**
  - `proposal_asset_matrix.json` (servicio→asset mapping, con `asset_path`) — en `v4_audit/`
  - `IMPLEMENTATION_ORDER.md` (debe tener contenido real) — **en `deliveries_dir`**
- **Regla de resolución de `deliveries_dir` (contrato T1)**: glob `v4_complete/deliveries/<hotel_id>_*` → el más reciente. Firma: `review(v4_audit_dir, deliveries_dir)`.
- **Residuo P12** (regla corregida por auditoría 2026-09-09): `promised_assets_exist` en `coherence_validator.py` NO está hardcodeado — calcula faltantes y su `message` declara la fuente (`via generated_assets` / `via catalogo_estatico`). Bot 3 marca `P12_UNVERIFIABLE` cuando la fuente declarada es catálogo estático (o formato legacy `via PROPOSAL_SERVICE_TO_ASSET`): P6.3 no verificable desde el artefacto. **NO marcar por score==1.0** (un run post-gen verificado también da 1.0). La verificación real de P6.3 la hace Bot 3 contra archivos en disco.

### Lecciones aplicables

| Lección | Aplicación |
|---------|-----------|
| R2.4: AC legible en artefacto | Test de serialización del JSON real |
| P12 (fuente catálogo estático) | Bot 3 señala P6.3 no verificable cuando el `message` declara `via catalogo_estatico`; no por score |
| A6 cerrado (v4.75.0) | `asset_path` ya se pobla; Bot 3 lo usa para verificar existencia real |
| Tribunal NO reimplementa gates | Lee `delivery_quality_report.json`, no re-ejecuta el QA |

---

## Tareas

### Tarea 1: Implementar `asset_reviewer.py`

**Objetivo**: Clase `AssetReviewer` con método `review() → AssetFindings`.

**Archivo a crear**:
- `modules/quality_gates/tribunal/asset_reviewer.py`

**Responsabilidades del Bot 3** (§5 del CONTEXT):
1. Cada servicio de propuesta tiene al menos un asset generado o presente en producción
2. Assets no son genéricos (mencionan hotel, brecha específica, punto de implementación)
3. Assets con `can_use: false` o `preflight_status: BLOCKED` no se presentan como entregables listos
4. Assets ESTIMATED están explícitamente etiquetados en README
5. No hay assets huérfanos (generados sin servicio que los respalde)
6. **P12**: `promised_assets_exist` con fuente declarada catálogo estático en el `message` → P6.3 no verificable (NO por score)
7. `IMPLEMENTATION_ORDER.md` vacío → asset incompleto. **Definición de "vacío" (auditoría 2026-09-09)**: 0 bytes O plantilla con secciones sin contenido por-hotel (el stub real del baseline pesa 468 B y sus secciones ORDEN/GUÍA/CHECKLIST están vacías — cuenta como vacío)

**Clasificación por servicio**:
- `CON-ASSET`: servicio tiene asset generado y presente
- `SIN-ASSET`: servicio prometido sin asset
- `ASSET-GENERICO`: asset existe pero no menciona hotel/brecha específica
- `ASSET-ESTIMATED-NO-ETIQUETADO`: confidence < 0.9 sin disclaimer visible

**Salida**: `revision_assets.json`
```json
{
    "reviewer": "asset_reviewer",
    "clauses": ["P6.3", "P6.4"],
    "coverage_by_service": [
        {
            "service": "...",
            "status": "CON-ASSET" | "SIN-ASSET" | "ASSET-GENERICO" | "ASSET-ESTIMATED-NO-ETIQUETADO",
            "asset_path": "..." | null,
            "asset_exists_on_disk": true | false,
            "finding": "..." | null
        }
    ],
    "findings": [
        {
            "severity": "CRITICAL" | "WARNING" | "INFO",
            "finding_type": "EMPTY_DELIVERY_TEMPLATE" | "P12_UNVERIFIABLE" | "ORPHAN_ASSET" | "GENERIC_ASSET" | "UNLABELED_ESTIMATED",
            "description": "..."
        }
    ],
    "summary": {"services_covered": N, "services_total": N, "coverage_ratio": 0.X},
    "verdict_recommendation": "APROBADO" | "DEVOLVER-PRUEBAS" | "BLOQUEAR"
}
```

**Criterios de aceptación**:
- [ ] Clase `AssetReviewer` con método `review(v4_audit_dir, deliveries_dir) → dict`
- [ ] Clasifica cada servicio en una de las 4 categorías
- [ ] Detecta `IMPLEMENTATION_ORDER.md` vacío (0 B o plantilla sin contenido por-hotel) → `EMPTY_DELIVERY_TEMPLATE`
- [ ] Detecta P12 por fuente declarada en el `message` (catálogo estático) → `P12_UNVERIFIABLE`; con `via generated_assets` + archivo en disco → sin finding
- [ ] Verifica existencia real de archivos en disco (no solo en MANIFEST)

### Tarea 2: Tests

**Archivo a crear**:
- `tests/quality_gates/tribunal/test_asset_reviewer.py`

**Tests obligatorios**:
| Test | Criterio |
|------|----------|
| `test_coverage_by_service_populated` | Salida tiene `coverage_by_service` con entradas por servicio |
| `test_empty_implementation_order_detected` | Fixture con `IMPLEMENTATION_ORDER.md` vacío (0 B o plantilla con secciones vacías) → `EMPTY_DELIVERY_TEMPLATE` |
| `test_p12_catalog_source_detected` | Fixture con `promised_assets_exist` message `via catalogo_estatico` → `P12_UNVERIFIABLE` |
| `test_p12_generated_assets_not_flagged` | Fixture con message `via generated_assets` + asset en disco → sin finding P12 |
| `test_orphan_asset_detected` | Asset en disco sin servicio en matriz → `ORPHAN_ASSET` |
| `test_generic_asset_flagged` | Asset sin mención de hotel → `ASSET-GENERICO` |
| `test_serialization_to_disk` | Escribe JSON, lo re-lee, verifica claves (R2.4) |
| `test_asset_exists_on_disk_verified` | `asset_path` poblado + archivo existe → `asset_exists_on_disk: true` |

**Comando de validación**:
```bash
./venv/Scripts/python.exe -m pytest tests/quality_gates/tribunal/test_asset_reviewer.py -v
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

### Tarea 3: Docs + Post-ejecución

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-T2-B \
    --desc "Bot 3: revisor de completitud de assets (cobertura por servicio, P12 detectado, IMPLEMENTATION_ORDER vacío)" \
    --archivos-nuevos "modules/quality_gates/tribunal/asset_reviewer.py,tests/quality_gates/tribunal/test_asset_reviewer.py" \
    --tests "8" \
    --check-manual-docs
```

---

## Post-Ejecución (OBLIGATORIO)

1. **`dependencias-fases.md`**: marcar FASE-T2-B ✅
2. **`README.md` del plan**: actualizar progreso
3. **`09-documentacion-post-proyecto.md`**: Secciones A, B, D
4. **`10-analisis-post-implementacion.md`**: fila T2-B + lecciones (mínimo 3)
5. **`evidence/FASE-T2-B/`**: baseline pre/post
6. **`06-checklist-implementacion.md`**: marcar items T2-B

---

## Criterios de Completitud (CHECKLIST)

- [ ] **AC7**: `revision_assets.json` con `coverage_by_service[]` (test de serialización verde)
- [ ] **AC8**: `IMPLEMENTATION_ORDER.md` vacío señalado — vacío = 0 B o plantilla sin contenido por-hotel (test verde)
- [ ] **P12**: fuente catálogo estático declarada en el `message` detectada como finding (no por score)
- [ ] **NR1**: `passed_post = passed_pre + tests nuevos`
- [ ] **NR3**: `run_all_validations.py --quick` TOTAL PASS
- [ ] **NR4**: No reimplementa gates
- [ ] **Post-ejecución completada**

---

## Restricciones

- **Presupuesto**: 35 iteraciones, corte en commit de código (R2.1)
- **NO ejecutar v4complete**
- **NO modificar ROADMAP.md ni `main.py` ni `judge.py`**
- **NO usar números de línea** (R2.2)
- **DIRECTO (no delegable)**: los tests importan el proyecto y el venv es Windows/WSL. Si excepcionalmente se demuestra que los tests son stdlib-only, la delegación requeriría que el parent ejecute los tests.
