# PLAN: Módulo Hook PDF Generator — `hook_pdf_generator`

**Proyecto:** iah-cli
**Plan ID:** HOOK-PDF-2026-07-09
**Target version:** v4.49.0 (minor — nuevo comando `hook-pdf`)
**Fecha creación:** 2026-07-09
**Convención:** 1 fase por sesión
**Fuente de autoridad:** `/.opencode/context/Historico/MODULO-HOOK-PDF.md` (arquitectura) + `output/Recomendaciones/PROPUESTA_EMPAQUETADO_NO_TECNICO.md` (visual/estructural)

---

## Resumen ejecutivo

Implementar el módulo `hook_pdf_generator` en `modules/commercial_documents/` que genera un PDF gancho de 2 páginas ("¿Cuánto pierde su hotel?") desde el output de v4_complete. Resuelve el Gap #2 "Empaquetado no técnico" del plan de negocio.

**Artefactos:** 3 archivos nuevos (~350 líneas), 3 modificados (~50 líneas). Total ~400 líneas.
**Stack:** weasyprint + pyyaml (dependencias de sistema: libpango, libcairo, libgdk-pixbuf2.0).

---

## Verificación pre-plan (ejecutada 2026-07-09)

| Check | Estado |
|-------|--------|
| `data_structures.py` existe (17KB) | ✅ |
| `main.py` existe (146KB) | ✅ |
| `__init__.py` existe (2KB) | ✅ |
| `v4_diagnostic_generator.py` existe (147KB) | ✅ |
| `v4_proposal_generator.py` existe (106KB) | ✅ |
| `AGENTS.md` existe (24KB) | ✅ |
| `CHANGELOG.md` existe (222KB) | ✅ |
| `VERSION.yaml` existe (21KB) | ✅ |
| `hook_pdf_generator.py` NO existe | ✅ (confirmado: greenfield) |
| `hook_template.md` NO existe | ✅ |
| `hook_styles.css` NO existe | ✅ |
| `test_hook_pdf_generator.py` NO existe | ✅ |
| `output/v4_complete/` con datos Luxorhotel | ⚠ NO encontrado — FASE-4 necesita re-ejecutar v4complete o localizar output existente |
| weasyprint instalado | ⚠ Pendiente — se instala en FASE-1 |
| pyyaml instalado | ⚠ Pendiente — se instala en FASE-1 |

**Nota sobre output/v4_complete/:** El contexto MODULO-HOOK-PDF.md referencia archivos del piloto Luxorhotel con timestamps `20260707_121029`. Si el directorio fue limpiado, FASE-4 debe re-ejecutar `python main.py v4complete --url http://www.luxorhotel.com.co/` antes de probar el generador.

---

## Dependencias entre fases

```
FASE-1 (Setup + Dataclass + Templates)
    ↓
FASE-2 (Generator + CLI Integration)  ← FASE DE MAYOR COMPLEJIDAD TÉCNICA
    ↓
FASE-3 (Tests + Validaciones)
    ↓
FASE-4 (E2E con Luxorhotel + PDF real)
    ↓
FASE-5 (RELEASE: docs, changelog, version)
```

Todas las dependencias son estrictamente secuenciales. Ninguna fase puede saltarse.

---

## Análisis de complejidad técnica por fase

| Fase | Complejidad | Razón | delegate_task viable |
|------|-------------|-------|----------------------|
| FASE-1 | MEDIA | Instalación + dataclass + templates = trabajo mecánico con spec clara | ✅ SÍ — spec completa en §3.2 del contexto |
| FASE-2 | **ALTA** | Generator con parsing YAML+JSON+regex sobre .md, 8 validaciones, render HTML, integración CLI en main.py de 146KB | ⚠ PARCIAL — ver abajo |
| FASE-3 | MEDIA | 8+ tests unitarios contra dataclass y métodos del generator | ✅ SÍ — TDD con spec clara |
| FASE-4 | MEDIA-BAJA | E2E: localizar/regenerar output, ejecutar, validar PDF visualmente | ❌ NO — requiere visión del PDF y decisión humana |
| FASE-5 | BAJA | RELEASE rutinario: docs cascade, changelog, version bump | ✅ SÍ — mecánico |

### FASE-2 — Análisis de la fase de mayor complejidad técnica

**Por qué es la más compleja:**
1. **Parsing multi-fuente:** debe leer frontmatter YAML de 2 archivos .md (con timestamps variables vía glob), más v4_complete_report.json, más secciones del cuerpo del .md via regex para scores GBP, dirección, tabla de 4 pilares
2. **8 validaciones obligatorias** con lógica condicional (Tier A/B/C, no-sobrescritura, dry-run, placeholders sin llenar)
3. **Integración CLI en main.py (146KB):** agregar choice, dispatch, handler, argparse con 6 argumentos — riesgo de colisión con código existente
4. **Render HTML → PDF via weasyprint:** el template .md debe convertirse a HTML+CSS para weasyprint — hay un paso de transformación markdown→HTML que no está trivialmente resuelto

**Decisión delegate_task para FASE-2:** Se divide en 2 sub-tareas delegables en paralelo:
- Sub-agente A: `hook_pdf_generator.py` (clase + métodos, sin CLI)
- Sub-agente B: Integración en `main.py` (argparse + dispatch + handler)
La dependencia B→A es solo de import (B importa la clase de A), pero el esqueleto de main.py se puede preparar en paralelo.

**Riesgo principal:** El paso markdown→HTML para weasyprint. weasyprint renderiza HTML+CSS, no markdown. El template `hook_template.md` debe ser HTML con placeholders `{{}}`, no markdown puro. Esto se resuelve en FASE-1 decidiendo que el template sea HTML con sintaxis `.md` pero extensión `.html` internamente, o que el generator convierta markdown→HTML antes de weasyprint.

---

## DoD (Definition of Done) del plan

- [x] `hook_pdf_generator.py` en `modules/commercial_documents/` con clase `HookPDFGenerator`
- [x] `HookPDFGenerator` exportado en `modules/commercial_documents/__init__.py`
- [x] `HookPDFData` dataclass en `data_structures.py` con todos los placeholders §3.2 + `evidence_tier`
- [x] `HookPDFData` exportado en `__init__.py`
- [x] Template `templates/hook_template.md` (o `.html`) con todos los placeholders del catálogo
- [x] Estilos `templates/hook_styles.css` con diseño 2 páginas
- [x] Comando `hook-pdf` en `main.py` con args: `--output-dir`, `--template`, `--style`, `--dry-run`, `--force`, `--verbose`
- [ ] 8+ tests unitarios en `tests/commercial_documents/test_hook_pdf_generator.py`
- [ ] PDF generado desde output real de Luxorhotel
- [ ] PDF ocupa exactamente 2 páginas
- [ ] Cero placeholders `{{...}}` sin reemplazar
- [ ] Cifra de fuga ≥24pt en página 1
- [ ] Disclaimer de estimación visible (Tier B/C)
- [ ] Funciona con un segundo hotel de prueba
- [ ] Tiempo de generación <30 segundos
- [ ] CHANGELOG.md actualizado
- [ ] VERSION.yaml bumped a v4.49.0
- [ ] AGENTS.md actualizado (tabla de comandos + módulos)
- [ ] `sync_versions.py` ejecutado
- [ ] `doctor.py --regenerate-domain-primer` ejecutado

---
