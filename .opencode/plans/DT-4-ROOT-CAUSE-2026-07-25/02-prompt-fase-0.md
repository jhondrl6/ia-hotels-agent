# Prompt de Inicio de Sesión: FASE-0 — Reconciliador Post-Orchestrator

**Fase**: FASE-0 — FIX-PRIORITY-1: Reconciliador post-orchestrator (causa raíz transversal)
**Plan**: DT-4-ROOT-CAUSE-2026-07-25
**Sesión**: Nueva (fresh)
**Iteraciones máx**: 60
**Complejidad**: **ALTA** ⚠️ — cross-module, nuevo archivo, decisión arquitectónica
**Ejecución**: **DIRECTA** — No delegable (decisión arquitectónica + cross-module)
**Depende de**: — (root cause)
**Bloquea a**: FASE-2, FASE-RELEASE

---

## Objetivo

Implementar un **reconciliador post-orchestrator** que unifique las 3 fuentes de verdad dispares sobre "este pain está resuelto?" en un solo archivo `pain_ledger_resolved.json`. Este único fix resuelve BUG-6 + BUG-9 + HALLAZGO-N2 + HALLAZGO-N3 + HALLAZGO-N4.

---

## Contexto de Fases Anteriores

DT-3 (v4.64.0) completó 5 fases + RELEASE con estos resultados:
- BUG-1: Rutas flat → per-hotel corregidas ✅
- BUG-2/3: G9 dual-list + status-based eval corregidos ✅
- BUG-4/P-04: AssetAlignmentMatrix unificado ✅
- 100 tests PASS (86 + 14 nuevos)
- v4complete Zi One ejecutado: exit 0, 149s

El contexto CONTEXT-DT-4.md (validado contra código vivo) identificó que los bugs remanentes son síntomas de una causa raíz transversal: **3 fuentes de verdad no consolidadas** para el estado de resolución de pains.

---

## Tareas

### T1: Crear módulo `post_orchestrator_reconciler.py`

**Archivo**: `modules/orchestration/post_orchestrator_reconciler.py` (NUEVO)

Crear clase `PostOrchestratorReconciler` con método `reconcile()` que:

1. Lee `asset_generation_report.json` (generated_assets.pain_ids_resolved + skipped_assets.pain_ids_affected)
2. Lee `pain_ledger.json` (estado actual de cada pain)
3. Emite `pain_ledger_resolved.json` con status final por pain_id:
   - `ASSET_GENERATED` si aparece en generated_assets.pain_ids_resolved (asset generado cubre este pain)
   - `MAPPED_TO_SERVICE` si aparece en skipped_assets.pain_ids_affected con presence=exists (site ya tiene la feature)
   - `JUSTIFIED_SKIP` si skipped con presence=redundant (feature redundante en el sitio)
   - Conserva status original del pain_ledger si no se encontró en ningún asset (ej: DETECTED, DIAGNOSED)

```python
# modules/orchestration/post_orchestrator_reconciler.py
"""Post-orchestrator reconciliation: unifies 3 sources of truth about pain resolution."""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class PainResolutionStatus:
    """Status values emitted by the reconciler."""
    ASSET_GENERATED = "ASSET_GENERATED"
    MAPPED_TO_SERVICE = "MAPPED_TO_SERVICE"
    JUSTIFIED_SKIP = "JUSTIFIED_SKIP"


class PostOrchestratorReconciler:
    """Reconciles pain_ledger with asset_generation_report after orchestration.

    Three sources of truth exist for "is this pain resolved?":
    1. pain_ledger.json — DETECTED/DIAGNOSED/MAPPED_TO_SERVICE/ASSET_GENERATED/...
    2. generated_assets[].pain_ids_resolved — assets generated that resolve pains
    3. skipped_assets[].pain_ids_affected — assets skipped because site already has them

    This reconciler reads all three, resolves conflicts, and emits a single
    pain_ledger_resolved.json as the canonical post-orchestration state.
    """

    def reconcile(
        self,
        asset_generation_report_path: Path,
        pain_ledger_path: Path,
        output_path: Path,
    ) -> Dict:
        """Reconcile and emit pain_ledger_resolved.json.

        Returns the reconciled pain ledger as a dict.
        """
        # Load inputs
        asset_report = self._load_json(asset_generation_report_path)
        pain_ledger = self._load_json(pain_ledger_path)

        # Build resolution maps
        generated_pain_ids = self._extract_generated_pain_ids(asset_report)
        skipped_pain_map = self._extract_skipped_pain_map(asset_report)

        # Reconcile each pain
        resolved_entries = []
        for entry in pain_ledger.get("entries", pain_ledger if isinstance(pain_ledger, list) else []):
            pain_id = entry.get("pain_id", entry.get("id", ""))
            new_status = self._resolve_status(
                pain_id=pain_id,
                current_status=entry.get("status", "DETECTED"),
                in_generated=pain_id in generated_pain_ids,
                skipped_info=skipped_pain_map.get(pain_id),
            )
            resolved_entry = {**entry, "status": new_status}
            resolved_entries.append(resolved_entry)

        # Build output
        result = {
            "version": "1.0",
            "source": "post_orchestrator_reconciler",
            "entries": resolved_entries,
            "summary": {
                "total": len(resolved_entries),
                "asset_generated": sum(1 for e in resolved_entries if e["status"] == PainResolutionStatus.ASSET_GENERATED),
                "mapped_to_service": sum(1 for e in resolved_entries if e["status"] == PainResolutionStatus.MAPPED_TO_SERVICE),
                "justified_skip": sum(1 for e in resolved_entries if e["status"] == PainResolutionStatus.JUSTIFIED_SKIP),
            },
        }

        # Emit
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info(f"Reconciled pain ledger → {output_path} ({len(resolved_entries)} entries)")

        return result

    def _resolve_status(
        self,
        pain_id: str,
        current_status: str,
        in_generated: bool,
        skipped_info: Optional[Dict],
    ) -> str:
        """Determine final status for a single pain."""
        if in_generated:
            return PainResolutionStatus.ASSET_GENERATED
        if skipped_info:
            presence = skipped_info.get("presence_status", "")
            if presence == "exists":
                return PainResolutionStatus.MAPPED_TO_SERVICE
            if presence == "redundant":
                return PainResolutionStatus.JUSTIFIED_SKIP
            # exists_with_issues or unknown — keep current
        return current_status

    def _extract_generated_pain_ids(self, asset_report: Dict) -> set:
        """Extract pain IDs resolved by generated assets."""
        pain_ids = set()
        for asset in asset_report.get("generated_assets", []):
            for pid in asset.get("pain_ids_resolved", []):
                pain_ids.add(pid)
        return pain_ids

    def _extract_skipped_pain_map(self, asset_report: Dict) -> Dict[str, Dict]:
        """Build map of pain_id → skip_info for skipped assets."""
        skipped_map = {}
        for asset in asset_report.get("skipped_assets", []):
            presence = asset.get("presence_status", "")
            for pid in asset.get("pain_ids_affected", []):
                skipped_map[pid] = {
                    "presence_status": presence,
                    "asset_name": asset.get("asset_name", ""),
                    "site_verified": asset.get("site_verified", False),
                }
        return skipped_map

    def _load_json(self, path: Path) -> Dict:
        """Load a JSON file, returning empty dict/list on failure."""
        if not path.exists():
            logger.warning(f"File not found: {path}")
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
```

**Verificación**:
```bash
grep -n "class PostOrchestratorReconciler" modules/orchestration/post_orchestrator_reconciler.py
# Debe retornar: N:class PostOrchestratorReconciler:
```

---

### T2: Modificar `v4_asset_orchestrator.py` para llamar al reconciliador

**Archivo**: `modules/asset_generation/v4_asset_orchestrator.py`

Después de la generación de assets (generated_assets + skipped_assets ya escritos a disco), llamar al reconciliador antes de retornar:

1. Importar `PostOrchestratorReconciler` al inicio del archivo
2. En el método `run()` (o equivalente), después de escribir `asset_generation_report.json`, agregar:

```python
# Post-orchestration reconciliation
from modules.orchestration.post_orchestrator_reconciler import PostOrchestratorReconciler

reconciler = PostOrchestratorReconciler()
pain_ledger_path = output_dir / hotel_slug / "v4_audit" / "pain_ledger.json"
pain_ledger_resolved_path = output_dir / hotel_slug / "v4_audit" / "pain_ledger_resolved.json"
asset_gen_report_path = output_dir / hotel_slug / "v4_audit" / "asset_generation_report.json"

if pain_ledger_path.exists() and asset_gen_report_path.exists():
    reconciler.reconcile(
        asset_generation_report_path=asset_gen_report_path,
        pain_ledger_path=pain_ledger_path,
        output_path=pain_ledger_resolved_path,
    )
```

**Verificación**:
```bash
grep -n "PostOrchestratorReconciler" modules/asset_generation/v4_asset_orchestrator.py
# Debe retornar al menos 2 líneas (import + uso)
```

---

### T3: Modificar `publication_gates.py` — dos cambios

**Archivo**: `modules/quality_gates/publication_gates.py`

**Cambio 3a**: Agregar `ASSET_GENERATED` a `_JUSTIFIED_STATUSES` (L1186):

```python
# Antes:
_JUSTIFIED_STATUSES: Set[str] = {"JUSTIFIED_SKIP", "BLOCKED", "MAPPED_TO_SERVICE"}

# Después:
_JUSTIFIED_STATUSES: Set[str] = {
    "JUSTIFIED_SKIP", "BLOCKED", "MAPPED_TO_SERVICE", "ASSET_GENERATED"
}
```

**Cambio 3b**: Modificar `_coverage_gate` (L1230) para leer `pain_ledger_resolved` con fallback a `pain_ledger`:

Buscar dónde se carga `pain_ledger` para el coverage gate y agregar lógica:

```python
# Intentar leer pain_ledger_resolved primero (post-orchestrator reconciliation)
pain_ledger_resolved = assessment.get("pain_ledger_resolved")
if pain_ledger_resolved:
    pain_entries = pain_ledger_resolved.get("entries", pain_ledger_resolved)
else:
    # Fallback: usar pain_ledger tradicional
    pain_entries = assessment.get("pain_ledger", [])
```

**Verificación**:
```bash
grep -n "ASSET_GENERATED" modules/quality_gates/publication_gates.py | grep -v "import\|from\|#"
# Debe mostrar la línea de _JUSTIFIED_STATUSES con ASSET_GENERATED incluido

grep -n "pain_ledger_resolved" modules/quality_gates/publication_gates.py
# Debe retornar al menos 1 línea
```

---

### T4: Modificar `coherence_validator.py` para consultar SitePresence

**Archivo**: `modules/quality_gates/coherence_validator.py`

Modificar `_check_whatsapp_verified()` para consultar `site_presence_report.whatsapp.presence_status == "exists"` y aumentar confidence a 0.9+ cuando aplique:

```python
def _check_whatsapp_verified(self, assessment: Dict, site_presence_report: Optional[Dict] = None) -> Dict:
    """Check if WhatsApp presence is verified on the site."""
    confidence = assessment.get("whatsapp_confidence", 0.0)

    # Boost confidence if SitePresenceChecker confirmed WhatsApp exists
    if site_presence_report:
        whatsapp_presence = site_presence_report.get("whatsapp", {})
        if whatsapp_presence.get("presence_status") == "exists":
            confidence = max(confidence, 0.95)

    threshold = 0.9
    passed = confidence >= threshold

    return {
        "score": confidence,
        "passed": passed,
        "message": (
            f"WhatsApp presence verified (confidence: {confidence:.2f})"
            if passed
            else f"WhatsApp confidence insufficient ({confidence:.2f}) - requires >= {threshold}"
        ),
    }
```

**Verificación**:
```bash
grep -n "site_presence_report\|presence_status.*exists" modules/quality_gates/coherence_validator.py
# Debe retornar líneas con la nueva lógica
```

---

## Criterios de Completitud

- [ ] `modules/orchestration/post_orchestrator_reconciler.py` creado con clase `PostOrchestratorReconciler`
- [ ] `_JUSTIFIED_STATUSES` incluye `ASSET_GENERATED` (publication_gates.py:1186)
- [ ] `_coverage_gate` lee `pain_ledger_resolved` con fallback a `pain_ledger` (publication_gates.py)
- [ ] `v4_asset_orchestrator.py` llama al reconciliador post-generación
- [ ] `coherence_validator._check_whatsapp_verified()` consulta `site_presence_report` para boost de confidence
- [ ] 100 tests existentes siguen PASS: `./venv/Scripts/python.exe -m pytest -q`
- [ ] Python syntax check: `./venv/Scripts/python.exe -m py_compile modules/orchestration/post_orchestrator_reconciler.py`
- [ ] git commit con mensaje descriptivo

---

## Restricciones

- **NO delegar**: Esta fase es DIRECTA — requiere el agente principal para la decisión arquitectónica del contrato de reconciliación
- **NO modificar `scenario_calculator.py`** — fuera de scope
- **NO modificar `PAIN_SOLUTION_MAP`** — fuera de scope
- **NO ejecutar v4complete** en esta fase — solo código + tests
- Máximo 60 iteraciones
- WSL safety guard: usar `write_file` para crear archivos, no heredocs en terminal

---

## Post-Ejecución (OBLIGATORIO)

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-0 --desc "Reconciliador_post_orchestrator_causa_raiz_transversal" --check-manual-docs
```

---

## Siguiente Sesión

**FASE-1** — BUG-8: Reinterpretación comercial del escenario optimista (independiente de FASE-0 pero recomendado ejecutar después).
