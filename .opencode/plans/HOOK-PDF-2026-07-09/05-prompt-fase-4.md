# FASE-4: E2E con Luxorhotel + PDF Real

## Instrucciones de la sesión

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: DIRECTA (requiere visión del PDF y decisión humana)

## Contexto previo
FASE-3 completada: 8+ tests unitarios verdes. `HookPDFGenerator` funcional con fixtures sintéticas.

## Objetivo de esta fase
Generar un PDF real desde el output de v4complete del Luxorhotel (o re-ejecutar v4complete si el output fue limpiado), validar visualmente 2 páginas, cero placeholders, ≥24pt, disclaimer visible.

### Tareas
- [ ] 4.1 Verificar si existe `output/v4_complete/` con datos del Luxorhotel. Si NO existe: ejecutar `python3 main.py v4complete --url http://www.luxorhotel.com.co/` (timeout 900s). Si existe: continuar.
- [ ] 4.2 Ejecutar `python3 main.py hook-pdf --output-dir output/v4_complete/ --verbose` y verificar que genera `deliveries/{slug}_gancho.pdf`
- [ ] 4.3 Validar PDF: abrir y verificar 2 páginas exactas, cifra de fuga ≥24pt en página 1, cero `{{...}}` sin reemplazar, disclaimer de estimación visible (Tier B/C)
- [ ] 4.4 Validar contenido: comparar datos del PDF contra valores del MODULO-HOOK-PDF.md §3.2 (fuga mensual, brechas, scores, precios)
- [ ] 4.5 Test con segundo hotel (opcional si hay output disponible): cualquier URL de hotel diferente para validar reutilización del template

### Restricciones
- NO mezclar code fix + v4complete en la misma fase (pitfall del executor: modelos de ejecución diferentes)
- Si v4complete genera errores, documentarlos y pasar a FASE-5 solo si el generador funciona con fixtures (FASE-3 ya probó esto)
- El timeout de v4complete es 900s — usar delegate_task o terminal con background=true
- La validación visual del PDF requiere inspección humana (no automatizable)

### Criterios de completitud
- [ ] `output/v4_complete/deliveries/luxorhotel_gancho.pdf` existe y tiene >0 bytes
- [ ] PDF ocupa exactamente 2 páginas (verificar con `weasyprint` metadata o conteo de páginas)
- [ ] Cero placeholders `{{...}}` en el PDF (buscar en el texto extraído)
- [ ] Cifra de fuga en página 1 con tamaño ≥24pt
- [ ] Disclaimer de estimación visible (Tier B/C)
- [ ] Datos del PDF coinciden con MODULO-HOOK-PDF.md §3.2 (fuga mensual, scores, brechas)
- [ ] Tiempo de generación del PDF <30 segundos (sin contar v4complete)
- [ ] `--dry-run` funciona: muestra datos sin generar archivo

### Próxima sesión
FASE-5 (RELEASE): docs cascade (AGENTS.md, CHANGELOG.md, GUIA_TECNICA.md), VERSION.yaml bump a v4.49.0, sync_versions.py, doctor.py --regenerate-domain-primer, pre-commit.
