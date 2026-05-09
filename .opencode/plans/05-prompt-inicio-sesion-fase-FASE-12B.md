# FASE-12B: Coherence gate — Detección de divergencia audit↔presence

## Instrucciones de la sesión

> **REGLA**: Una fase = una sesión.

### Contexto previo
- FASE-12A completada: el fix de `site_presence_checker.py` resuelve el falso positivo.
- Sin embargo, si alguien reintroduce la expansión o hay otro falso positive futuro, el gate no lo detectaría.
- Se necesita un coherence check entre audit path y presence path.

### Objetivo de esta fase
1. Agregar verificación de divergencia en `proposal_asset_alignment.py`.
2. Cuando audit diga `hotel_schema_detected=false` pero presence diga `EXISTS` → marcar como `divergent`.
3. Crear tests para el nuevo comportamiento.
4. Ejecutar v4complete y verificar que `coherence_report` detecta la divergencia.

### Tareas

- [x] **1. Investigar código** — Leer `proposal_asset_alignment.py` (L146-362) y entender flujo de `verify_proposal_asset_alignment()`.
- [x] **2. Implementar SOL-2** — Agregar check de divergencia antes de marcar `present_in_production` (ver implementación abajo).
- [x] **3. Agregar `divergent` como estado válido** — `presence_status` ya es `Optional[str]`, no requiere cambios en dataclass. `to_dict()` ya serializa `presence_status` para items con `presence_verified=True`.
- [x] **4. Crear tests** — `tests/asset_generation/test_proposal_alignment.py` con 4 casos: divergencia, no-divergencia, backward-compat, to_dict. 22/22 pasan.
- [x] **5. Ejecutar v4complete** — Sobre termales.com.co. Coherence 0.89. Sin divergencia para este sitio (audit y presence coinciden).
- [x] **6. Verificar coherence_report** — hotel_schema en "aligned" (confidence 0.85). Código FASE-12B operativo pero no activado (sin discrepancia).

### Restricciones
- No modificar el fix de FASE-12A.
- Máximo 60 iteraciones.

### Entregable
- [x] `proposal_asset_alignment.py` con check de divergencia.
- [x] Tests pasando (22/22, +4 nuevos).
- [x] v4complete ejecutado (coherence 0.89). Sin divergencia en termales.com.co (esperado).

### Próxima sesión
FASE-RELEASE o FASE-12C (opcional): Separación de servicios en propuesta.

### Nota de completitud
✅ **FASE-12B COMPLETADA** — 2026-05-09. Código implementado, probado y verificado en E2E.