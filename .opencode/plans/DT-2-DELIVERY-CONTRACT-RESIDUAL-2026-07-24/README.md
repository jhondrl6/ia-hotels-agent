# DT-2 — Delivery Contract Residual Fixes (Post-DT-1)

> **Plan ID**: DT-2-DELIVERY-CONTRACT-RESIDUAL-2026-07-24
> **Versión base**: v4.63.1 → **Versión objetivo**: v4.63.2
> **Hotel de referencia**: Zi One Luxury (https://zione.co/)
> **Datos reales**: `output/clientes/zi-one-luxury_onboarding.yaml`
> **Contexto fuente**: `.opencode/context/CONTEXT-DT-2-DELIVERY-CONTRACT-RESIDUAL.md`
> **Fecha**: 2026-07-24

---

## Resumen

DT-1 (7.5/10) dejó 7 findings residuales agrupados en 3 raíces:
- RAÍZ-1: Orden de construcción (P-01)
- RAÍZ-2: Filtros sin exclusión mutua (P-02, P-06, P-07)
- RAÍZ-3: Gates declarados pero no implementados (P-03, P-05)

El plan corrige los 7 findings en 7 fases (1 fase por sesión).

---

## Fases

| Fase | Archivo | Findings | Ejecución | Estado |
|------|---------|----------|-----------|--------|
| A | 02-prompt-fase-A.md | P-01, P-07 | SUBAGENTE | ⬜ |
| B | 03-prompt-fase-B.md | P-02 | DIRECTA | ✅ |
| C | 04-prompt-fase-C.md | P-03, P-05 | DIRECTA | ⬜ |
| D | 05-prompt-fase-D.md | P-04, P-06 | DIRECTA | ⬜ |
| E | 06-prompt-fase-E.md | 7 tests | DIRECTA | ⬜ |
| F | 07-prompt-fase-F.md | v4complete + análisis | MIXTO | ⬜ |
| RELEASE | 08-prompt-fase-release.md | v4.63.2 | SUBAGENTE | ⬜ |

**Fase de mayor complejidad**: FASE-C (P-05 G9 dead gate — decisión arquitectónica)

---

## Dependencias

```
A → B → C → D → E → F → RELEASE
```

A y B comparten `delivery_packager.py` L603 (B va después de A).
C, D son independientes entre sí pero van después de B por orden.
E depende de A-D (testea los fixes).
F depende de E (verifica con v4complete).
RELEASE depende de F.

---

## Cómo iniciar

```bash
# En una nueva sesión:
Carga el plan DT-2 en /mnt/c/Users/Jhond/Github/iah-cli/.opencode/plans/DT-2-DELIVERY-CONTRACT-RESIDUAL-2026-07-24/
Lee 01-plan-maestro.md y 02-prompt-fase-A.md
Ejecuta FASE-A: P-01 (conteo README post-manifest) + P-07 (string vs enum)
```

---

## Archivos del Plan

| # | Archivo | Descripción |
|---|---------|-------------|
| 01 | 01-plan-maestro.md | Resumen, dependencias, complejidad, DoD |
| 02 | 02-prompt-fase-A.md | P-01 + P-07 (SUBAGENTE) |
| 03 | 03-prompt-fase-B.md | P-02 (SUBAGENTE) |
| 04 | 04-prompt-fase-C.md | P-03 + P-05 (DIRECTA — mayor complejidad) |
| 05 | 05-prompt-fase-D.md | P-04 + P-06 (DIRECTA) |
| 06 | 06-prompt-fase-E.md | 7 tests nuevos (DIRECTA) |
| 07 | 07-prompt-fase-F.md | v4complete Zi One + análisis (MIXTO) |
| 08 | 08-prompt-fase-release.md | RELEASE v4.63.2 (SUBAGENTE) |
| 09 | 09-checklist-implementacion.md | Checklist maestro |
| 10 | 10-analisis-post-implementacion.md | Template de retrospectiva |
