# Plan: DT-1-DELIVERY-CONTRACT-2026-07-23

> **ID**: DT-1 — Delivery Contract and Cross-Artifact Consistency
> **Origen**: Contexto validado `DT-1-README-DELIVERY-PRESENT-IN-PRODUCTION.md` v2.0
> **Versión del plan**: v1.0
> **Repositorio**: `/mnt/c/Users/Jhond/Github/iah-cli`
> **Severidad**: ALTA — confiabilidad de entrega al cliente

---

## Resumen

El ZIP de entrega contiene 46 archivos y `boton_whatsapp.html` no está presente (correctamente omitido por `present_in_production`). Sin embargo, el `README_DELIVERY.md` dentro del mismo ZIP lista `boton_whatsapp.html`, da instrucciones para instalarlo, y lo incluye en timeline y checklist. El cliente busca un archivo que no fue entregado.

**Causa raíz**: El README se genera desde una template narrativa estática, no desde la lista final de archivos del ZIP ni desde un contrato canónico de estados de assets.

**Solución**: Establecer un Delivery Contract que unifique estado de assets, archivos físicos, manifest, README, gates y evidencia; generar la estructura del README desde los destinos reales del ZIP; y validar automáticamente que README, MANIFEST y ZIP describan exactamente el mismo paquete.

## Fases

| Fase | Descripción | Tareas | Cmd largo | delegate_task |
|------|------------|--------|-----------|---------------|
| [A](02-prompt-fase-A.md) | Contrato canónico y saneamiento | 4 | 0 | DIRECTA |
| [B](03-prompt-fase-B.md) | Pipeline físico (POSIX, tamaños, DeliveryContext) | 5 | 0 | DIRECTA |
| [C](04-prompt-fase-C.md) | README dinámico | 4 | 0 | DIRECTA |
| [D](05-prompt-fase-D.md) | Tests de contrato + gate | 4 | 0 | DIRECTA |
| [E](06-prompt-fase-E.md) | E2E (Zi One) + RELEASE + Análisis post-implementación | 5 | 1 | MIXTO |

## Archivos del plan

```
DT-1-DELIVERY-CONTRACT-2026-07-23/
├── README.md                         ← Este archivo
├── 01-plan-maestro.md                ← Plan detallado con arquitectura y riesgos
├── 02-prompt-fase-A.md               ← Contrato canónico (DeliveryAssetState)
├── 03-prompt-fase-B.md               ← Pipeline físico (POSIX, tamaños)
├── 04-prompt-fase-C.md               ← README dinámico (template + secciones)
├── 05-prompt-fase-D.md               ← Tests cross-artifact + gate
├── 06-prompt-fase-E.md               ← E2E Zi One + RELEASE + análisis post-implementación
├── 07-checklist-implementacion.md    ← Master checklist con tracking
├── 08-analisis-post-implementacion.md ← Análisis post-implementación (template, completar en FASE-E)
├── 09-documentacion-post-proyecto.md ← Post-project doc plan
└── dependencias-fases.md             ← Dependencias + conflictos + R3
```

## Inicio rápido

**Primera fase (nueva sesión)**:

```text
Ejecuta FASE-A del plan DT-1-DELIVERY-CONTRACT-2026-07-23:
/mnt/c/Users/Jhond/Github/iah-cli//.opencode/plans/Archives/DT-1-DELIVERY-CONTRACT-2026-07-23/02-prompt-fase-A.md
```

## Estado

| Fase | Estado |
|------|--------|
| A | ⬜ PENDIENTE |
| B | 🔒 BLOQUEADA |
| C | 🔒 BLOQUEADA |
| D | 🔒 BLOQUEADA |
| E | 🔒 BLOQUEADA |

---

*Plan generado 2026-07-23. Contexto fuente validado contra commit `df75222f2b1ddce9e0761afbbea388831ea88a02`.*
