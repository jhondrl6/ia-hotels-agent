# DELIVERY-ZIP-SINGLE-WRITE-2026-08-01

> Plan de refactorizacion por fases para corregir el fallo critico de delivery packaging.
> El pipeline v4complete genera contenido correcto pero NUNCA materializa el ZIP de entrega.

---

## Resumen

| Aspecto | Valor |
|---------|-------|
| **Problema** | ZIP de entrega nunca se materializa (Bug 1: README post-medicion) |
| **Solucion** | Opcion C: Single-Write Architecture con fixed-point iteration |
| **Version objetivo** | v4.69.0 |
| **Fases** | 5 (A, B, C, D, RELEASE) |
| **Hotel de verificacion** | Zi One Luxury (https://zione.co/) |
| **Complejidad maxima** | FASE-B (Core Rewrite) ★ |
| **Contexto** | `.opencode/context/CONTEXT-DELIVERY-ZIP-PACKAGING-BROKEN-2026-08-01.md` |

---

## Progreso

| Fase | Nombre | Estado | Delegable |
|------|--------|--------|-----------|
| FASE-A | Test Infrastructure + Bug 3 | ✅ Completada (parcial, integrada en B) | SI |
| FASE-B | Core Rewrite: Single-Write ★ | ✅ Completada 2026-08-01 | NO |
| FASE-C | Error Handling + Cleanup | ✅ Completada 2026-08-01 | SI |
| FASE-D | E2E v4complete Zi One Luxury | ✅ Completada 2026-08-01 | Parcial |
| FASE-RELEASE-4.69.0 | Release + Docs | ✅ Completada 2026-08-02 | SI |

---

## Archivos del Plan

| Archivo | Descripcion |
|---------|-------------|
| `01-plan-maestro.md` | Plan maestro con resumen, fases, criterios |
| `02-prompt-fase-A.md` | Prompt de sesion: Test Infrastructure |
| `03-prompt-fase-B.md` | Prompt de sesion: Core Rewrite (★ complejidad maxima) |
| `04-prompt-fase-C.md` | Prompt de sesion: Error Handling |
| `05-prompt-fase-D.md` | Prompt de sesion: E2E v4complete |
| `06-prompt-fase-RELEASE.md` | Prompt de sesion: Release |
| `07-checklist-implementacion.md` | Checklist maestro con trackers |
| `08-analisis-post-implementacion.md` | Analisis post-implementacion (diligericiar por fase) |
| `09-documentacion-post-proyecto.md` | Documentacion acumulativa para RELEASE |
| `dependencias-fases.md` | Diagrama de dependencias + conflictos |

---

## Ejecucion

Cada fase se ejecuta en una **sesion nueva** del agente:

1. Abrir nueva sesion
2. Leer el prompt de la fase (`02-prompt-fase-A.md`, etc.)
3. Ejecutar tareas segun el prompt
4. Verificar criterios de completitud
5. Ejecutar post-ejecucion (log_phase_completion.py)
6. Cerrar sesion

**FASE-RELEASE** es la ultima sesion. Solo se ejecuta cuando A+B+C+D estan ✅.

---

## Onboarding Zi One Luxury

```yaml
hotel:
  nombre: Zi One Luxury
  ubicacion: Pereira, Eje Cafetero
datos_operativos:
  habitaciones: 34
  reservas_mes: 800
  valor_reserva_cop: 290000
  canal_directo_pct: 40.0
```

Fuente: `output/clientes/zi-one-luxury_onboarding.yaml`
