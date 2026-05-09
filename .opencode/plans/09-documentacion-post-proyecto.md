# Documentación Post-Proyecto — Auditoría M6 Hotel Schema (Termales Santa Rosa de Cabal)

## Sección A: Módulos Nuevos

| Módulo | Archivos | Descripción | Fase |
|--------|----------|-------------|------|
| tests.site_presence_checker | tests/test_site_presence_checker.py | Tests unitarios para _check_schema_exists | FASE-12A |
| tests.proposal_asset_alignment | tests/test_proposal_asset_alignment.py | Tests unitarios para verificación de coherencia | FASE-12B |

## Sección B: Funcionalidades Nuevas

| Feature | Módulo | Descripción | Fase |
|---------|--------|-------------|------|
| Fix: Solo LodgingBusiness como subtipo Hotel | site_presence_checker.py | Eliminada expansión Hotel→{LocalBusiness, Organization} | FASE-12A |
| Divergence detection audit↔presence | proposal_asset_alignment.py | Check de coherencia marca DIVERGENT cuando audit y presence discrepan | FASE-12B |
| Schema separation en propuesta | proposal_asset_alignment.py | Separación Schema Hotel / Schema Organization para transparencia | FASE-12C (opcional) |

## Sección D: Métricas Acumulativas

| Métrica | Valor | Fase |
|---------|-------|------|
| Tests nuevos | +7 (5 site_presence + 2 proposal_alignment) | 12A/12B |
| Archivos modificados | 2 (site_presence_checker.py, proposal_asset_alignment.py) | 12A/12B |
| Archivos nuevos | 2-3 (tests + evidence) | 12A/12B |

## Sección E: Archivos Afiliados Actualizados

| Archivo | Cambio | Fase |
|---------|--------|------|
| modules/asset_generation/site_presence_checker.py | Eliminada expansión Hotel→{LocalBusiness, Organization} | FASE-12A |
| modules/asset_generation/proposal_asset_alignment.py | Agregado check de divergencia audit↔presence | FASE-12B |
| tests/test_site_presence_checker.py | Nuevo — 5+ casos de test | FASE-12A |
| tests/test_proposal_asset_alignment.py | Nuevo — tests de coherencia | FASE-12B |
| CHANGELOG.md | Entrada con formato de cada fase | FASE-RELEASE |
| GUIA_TECNICA.md | Notas técnicas por fase | FASE-RELEASE |