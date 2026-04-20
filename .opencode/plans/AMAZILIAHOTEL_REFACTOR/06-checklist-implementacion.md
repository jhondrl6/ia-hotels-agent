# Checklist de Implementacion: Amaziliahotel Refactorizacion

**Proyecto**: Refactorizacion Amaziliahotel v4complete  
**Score inicial**: 16/100 → **Score objetivo**: 80/100  
**Total fases**: 8 (FASE-1, 2A, 2B, 2C, 3, 4, 5, 6)

---

## PROGRESO GENERAL

| # | Fase | Estado | Fecha Inicio | Fecha Fin | Notas |
|---|------|--------|--------------|----------|-------|
|| 1 | FASE-1: BookingScraper Real | ✅ COMPLETADA | 2026-04-19 | 2026-04-19 | Scraping real + fallback GBP verificado |
||| 2 | FASE-2A: hotel_schema real | ✅ COMPLETADA | 2026-04-19 | 2026-04-19 | Schema regenerado con datos reales GBP |
|| 3 | FASE-2B: monthly_report real | ✅ COMPLETADA | 2026-04-19 | 2026-04-19 | Regenerado con datos reales GBP (reviews=202, rating=4.5) |
|| 4 | FASE-2C: optimization_guide | ✅ COMPLETADA | 2026-04-19 | 2026-04-19 | Contradiccion title tag corregida |
| 5 | FASE-3: Bugs generadores | ✅ COMPLETADA | 2026-04-19 | 2026-04-19 | 4 bugs: H3(faq ext), H4(duplicados), H10(coherence), H12(paths) |
| 6 | FASE-4: Open Graph | ✅ COMPLETADA | 2026-04-19 | 2026-04-19 | Asset B4 Open Graph generado con datos GBP |
| 7 | FASE-5: Decisiones + Gates | ⏳ PENDIENTE | - | - | D1:WhatsApp ELIMINAR, D2:Voice ELIMINAR |
| 8 | FASE-6: Docs comerciales | ⏳ PENDIENTE | - | - | ROI 3X Tier C, servicios alineados |

---

## CRONOGRAMA SUGERIDO

```
Semana 1:
  - Lunes: FASE-1 (BookingScraper) - 2-3 horas
  - Martes: FASE-2A + 2B + 2C (regeneraciones) - 1.5 horas (paralelizables)
  - Miercoles: FASE-3 (bugs) - 1-2 horas
  - Jueves: FASE-4 (Open Graph) - 1 hora
  - Viernes: FASE-5 (decisiones + bug promised_by) - 1.5 horas
  - Viernes tarde: FASE-6 (docs comerciales) - 1.5 horas

Total estimado: ~9.5 horas distribuidas en 5-6 dias
```

---

## VERIFICACIONES INTER-FASES

| Verificacion | Cuando | Criterio |
|-------------|--------|----------|
| research.json no vacio | Post FASE-1 | `data_found` tiene datos |
| confidence > 0.5 | Post FASE-1 | Verificado en JSON |
| delivery_ready > 50% | Post FASE-1 | Gate actualizado |
| Score forense > 40 | Post FASE-2A/B/C | Recalcular |
| B4 cubierto | Post FASE-4 | open_graph_meta/ existe |
| WhatsApp eliminado | Post FASE-5 | Carpeta eliminada o deprecated |
| Voice eliminado pipeline | Post FASE-5 | `promised_by=[]` para voice |
| `promised_by` sin "always" | Post FASE-5 | WhatsApp y Voice sin tags automaticos |
| delivery_ready >= 80% | Post FASE-5 | Gates 8 y 9 pasan |
| ROI realista | Post FASE-6 | 3X Tier C, 20X solo con GA4 |
| Servicios alineados | Post FASE-6 | 5 servicios: GEO, IAO, SEO, Datos, Informe |
| WhatsApp claim eliminado | Post FASE-6 | Propuesta NO dice "No hay boton" |

---

## VALIDACION E2E FINAL (Post FASE-6, unica ejecucion v4complete)

**RESTRICCION DE COSTO**: Esta es la UNICA ejecucion de v4complete en todo el proyecto.
NO ejecutar v4complete en ninguna fase previa (FASE-1 a FASE-6).
Las fases previas se validan con tests unitarios + py_compile + grep unicamente.

```bash
# ============================================================
# UNICA EJECUCION v4complete -- optimizar costo API
# ============================================================

# 0. Pre-condiciones: todas las fases completadas
./venv/Scripts/python.exe -m py_compile modules/scrapers/booking_scraper.py
./venv/Scripts/python.exe -m py_compile modules/asset_generation/asset_catalog.py
./venv/Scripts/python.exe -m py_compile modules/asset_generation/conditional_generator.py

# 1. EJECUCION v4complete -- Amazilia Hotel
mkdir -p evidence/amazilia-e2e-final
./venv/Scripts/python.exe main.py v4complete \
    --url https://amaziliahotel.com/ \
    --debug 2>&1 | tee evidence/amazilia-e2e-final/ejecucion_final.log

# 2. Capturar score forense post-refactor
# Verificar en el output:
#   - Score forense >= 80/100
#   - 0 problemas criticos
#   - delivery_ready >= 80%
#   - WhatsApp NO aparece como servicio (hotel ya lo tiene)
#   - Voice NO aparece como servicio
#   - ROI realista (no 20X directo)

# 3. Verificacion manual de documentos generados
grep -n -i "boton de whatsapp" output/v4_complete/02_PROPUESTA_*.md  # Debe ser 0 matches
grep -n -i "busqueda por voz" output/v4_complete/02_PROPUESTA_*.md   # Debe ser 0 matches en tabla servicios
grep -n "ROI" output/v4_complete/02_PROPUESTA_*.md                    # Debe mostrar 3X no "ROI: 20.0"

# 4. Verificar assets generados
ls output/v4_complete/amaziliahotel/open_graph_meta/    # Debe existir (B4 cubierto)
ls output/v4_complete/amaziliahotel/whatsapp_button/    # NO debe existir (eliminado)
ls output/v4_complete/amaziliahotel/voice_assistant_guide/ # NO debe existir (eliminado)

# 5. Validaciones globales
./venv/Scripts/python.exe scripts/run_all_validations.py --quick

# 6. Doctor status
./venv/Scripts/python.exe scripts/doctor.py --status

# 7. Consistency check
./venv/Scripts/python.exe scripts/version_consistency_checker.py
```

### Checklist Final
- [ ] **v4complete ejecutado**: Unica ejecucion, log en evidence/amazilia-e2e-final/
- [ ] Score forense >= 80/100
- [ ] Tri-Play valido para servicios con brecha real (GEO, IAO, SEO, Datos Estructurados)
- [ ] 0 problemas criticos
- [ ] delivery_ready >= 80%
- [ ] Todos los gates pasan
- [ ] `run_all_validations.py --quick` pasa 4/4
- [ ] CHANGELOG.md actualizado
- [ ] GUIA_TECNICA.md actualizada
- [ ] REGISTRY.md completo
- [ ] ROI 3X para Tier C en propuesta (20X solo como potencial con GA4)
- [ ] WhatsApp NO aparece como servicio vendible (hotel ya lo tiene)
- [ ] Voice NO aparece como servicio en propuesta
- [ ] Informe Mensual reclasificado como "Servicio Incluido"
- [ ] `promised_by` sin tags "always" ni "always_aeo"
- [ ] Carpeta whatsapp_button/ NO existe en output
- [ ] Carpeta voice_assistant_guide/ NO existe en output
- [ ] Carpeta open_graph_meta/ SI existe en output (B4 cubierto)

---

## REGISTRO DE SESIONES

|| Sesion | Fecha | Fase | Agent | Resultado |
||--------|-------|------|-------|-----------|
|| 1 | 2026-04-19 | Preparacion | Hermes | Plan creado |
|| 1b | 2026-04-19 | Correccion plan | Hermes | H7→ELIMINAR, H8→ELIMINAR, ROI por Tier |
|| 2 | 2026-04-19 | FASE-1 | Hermes | BookingScraper real + fallback GBP verificado |
||| 3 | 2026-04-19 | FASE-2A | Hermes | hotel_schema regenerado con datos reales GBP |
||| 3a | 2026-04-19 | FASE-2B | Hermes | ✅ COMPLETADA - monthly_report con datos reales GBP (reviews=202, rating=4.5) |
|| 3b | 2026-04-19 | FASE-2C | Hermes | ✅ COMPLETADA - Contradiccion title tag corregida |
| 4 | 2026-04-19 | FASE-3 | Hermes | ✅ COMPLETADA - 4 bugs: H3(faq ext), H4(duplicados), H10(coherence unificado), H12(paths) |
| 5 | 2026-04-19 | FASE-4 | Hermes | ✅ COMPLETADA - open_graph_generator.py + ESTIMATED_open_graph.html |
| 6 | - | FASE-5 | - | ⏳ PENDIENTE |
| 7 | - | FASE-6 | - | ⏳ PENDIENTE |

---

*Actualizado: 2026-04-19 (correcciones H7 ELIMINAR, H8 ELIMINAR pipeline, ROI por Tier)*
