# Plan: Corrección de Bugs Críticos — Caso Amazilia Hotel

**Estado**: ✅ 4/6 fases completadas  
**Fases**: 6  
**Hotel de prueba**: https://amaziliahotel.com/  
**Validación**: UNA única prueba v4complete al final (minimizar costos API)  
**Prioridad**: CRÍTICA  

---

## Resumen del Problema

La ejecución v4complete para **Amazilia Hotel** (https://amaziliahotel.com/, Google Maps: "Amazilia Hotel") generó assets CON DATOS FALSOS:
- Coordenadas GPS: NYC (40.7128, -74.0060) → debe ser Pereira, Colombia (~4.81°N, -75.69°W)
- Región: "nacional" → debe ser "Pereira" o "Eje Cafetero"
- WhatsApp: href="detected_via_html" (roto)
- Review widget: 5 estrellas falsas (0 reviews reales)
- org_schema: url="https://example.com" (placeholder)
- llms_txt: genérico sin datos del sitio
- monthly_report: "Hotel" genérico
- Propuesta: "No generado" para assets que SÍ existen

---

## Fases

| # | ID | Nombre | Deps | Estado | Prioridad |
|---|-----|--------|------|--------|-----------|
| 1 | FASE-DATASOURCE | Corrección datos fuente (coords, región, tel, GBP) | Ninguna | ✅ 2026-04-14 | CRÍTICA |
| 2 | FASE-PERSONALIZATION | Personalización generators con audit data | FASE-DATASOURCE | ✅ 2026-04-14 | ALTA |
| 3 | FASE-BUGFIXES | Corrección bugs específicos (whatsapp, review, org_schema) | FASE-DATASOURCE | ✅ 2026-04-14 | ALTA |
| 4 | FASE-CONTENT-FIXES | Corrección contenido (optimization_guide, monthly_report, llms_txt) | FASE-PERSONALIZATION | ✅ 2026-04-14 | MEDIA |
| 5 | FASE-VALIDATION-GATE | Gate validación pre-release | FASE-1..4 | ⏳ Pendiente | ALTA |
| 6 | FASE-RELEASE | v4.30.1 release + ÚNICA prueba v4complete | FASE-5 | ⏳ Pendiente | CRÍTICA |

---

## Archivos del Plan

```
.opencode/plans/context/
├── README.md                                    # Este archivo
├── dependencias-fases.md                        # Diagrama de deps
├── 06-checklist-implementacion.md               # Checklist maestro
├── 09-documentacion-post-proyecto.md            # Docs incrementales
├── AUDIT-AMAZILIA-2026-04-14.md                # Contexto completo
├── 05-prompt-inicio-sesion-fase-DATASOURCE.md       # Fase 1
├── 05-prompt-inicio-sesion-fase-PERSONALIZATION.md  # Fase 2
├── 05-prompt-inicio-sesion-fase-BUGFIXES.md         # Fase 3
├── 05-prompt-inicio-sesion-fase-CONTENT-FIXES.md    # Fase 4
├── 05-prompt-inicio-sesion-fase-VALIDATION-GATE.md  # Fase 5
└── 05-prompt-inicio-sesion-fase-RELEASE.md          # Fase 6
```

---

## Flujo de Ejecución

```
                    ┌──────────────────────────────┐
                    │     FASE-DATASOURCE          │ ← Ejecutar primero
                    │  coords, region, tel, GBP     │
                    └──────────────┬───────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                     │
              ▼                    ▼                     ▼
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│ FASE-PERSONALIZATION│  │   FASE-BUGFIXES     │  │ FASE-CONTENT-FIXES │
│ (depende de         │  │ (depende de         │  │ (depende de         │
│  DATASOURCE)        │  │  DATASOURCE)        │  │  PERSONALIZATION)   │
└─────────┬───────────┘  └─────────┬───────────┘  └─────────┬───────────┘
          │                        │                        │
          └────────────────────────┼────────────────────────┘
                                   │
                                   ▼
                         ┌─────────────────────┐
                         │ FASE-VALIDATION-GATE│
                         │ (espera 1-4)        │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    FASE-RELEASE     │
                         │  ÚNICA prueba       │
                         │  v4complete ✅      │
                         └─────────────────────┘
```

---

## Uso

1. **Sesión de preparación** (esta ✅): Generar todos los prompts
2. **Sesión por fase**: Ejecutar cada prompt en su propia sesión
3. **Post-fase**: log_phase_completion.py + actualizar docs
4. **FASE-RELEASE**: ÚNICA ejecución v4complete para validación

---

## Criterio de Éxito Global

Después de FASE-RELEASE, ejecutar `v4complete --url https://amaziliahotel.com/` **UNA SOLA VEZ** y verificar:

### Datos Reales
- [x] hotel_schema → coordenadas Pereira (~4.81°N, -75.69°W)
- [x] hotel_schema → name: "Amazilia" (no placeholder)
- [x] Región: "Pereira" o "Eje Cafetero" (no "nacional")
- [x] Teléfono: +57 3104019049 (no null)
- [x] WhatsApp: número o marcador claro (no "detected_via_html")
- [x] org_schema → URL real amaziliahotel.com (no example.com)
- [x] review_widget → sin estrellas falsas
- [x] llms_txt → menciona Pereira, spa, Eje Cafetero
- [x] monthly_report → usa "Amazilia" (no "Hotel" genérico)
- [x] optimization_guide → sin contradicciones

### Integridad
- [ ] Cadena financiera intacta
- [ ] 385+ tests pasando
- [ ] Publication gates = 9+

### Monitoreo
- [ ] OpenRouter fallback NO se activó

---

## Reglas de Costo API

> [!CAUTION]
> **NO ejecutar v4complete durante el desarrollo de fases.**
> Usar tests unitarios y verificación directa de código.
> **ÚNICA ejecución al final en FASE-RELEASE.**

---

*Plan creado: 2026-04-14*
