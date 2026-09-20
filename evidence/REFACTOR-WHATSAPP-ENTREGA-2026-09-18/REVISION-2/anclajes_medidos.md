# Anclas medidas — REVISION-2 de REFACTOR-WHATSAPP-ENTREGA-2026-09-18

**Fecha de medición:** 2026-09-19  ·  **HEAD:** `938f59f`  ·  **Versión:** 4.77.3  ·  **Espejo legible de:** `anclajes_medidos.json` (mismo directorio; se genera leyéndolo, no a mano).

> Anexo de precisión. Conserva, fuera de los documentos del plan, la posición exacta de cada ancla medida, para que los *.md del plan puedan citar símbolos (R2.2 del executor) sin perder la referencia verificable. No sustituye la verificación: cada ancla se abrió en disco.

## 1. Conteo reproducido antes de tocar nada

| Concepto | Valor |
|---|---|
| ocurrencias_contadas_por_el_verificador | **167** |
| anclas_unicas_de_esas_ocurrencias | **104** |
| ocurrencias_numericas_en_forma_breve_o_por_continuacion | **81** |
| anclas_unicas_adicionales_aportadas_por_las_formas_breves | **37** |
| total_anclas_registradas | **133** |
| total_ocurrencias_registradas | **248** |
| suma_citas_en_iguales_a_ocurrencias | **True** |

Comando que produce el rojo: `python scripts/validate_plan_citations.py  (rojo Plan Citations del quick)`

Cotejo de cobertura — método: por cada token del verificador se buscó una entrada con (basename de ruta_relativa, linea_o_rango) igual Tokens sin cobertura en este anexo: **0**. 104 tokens únicos se fusionan en 96 entradas porque el plan cita el mismo ancla a veces con basename y a veces con ruta completa (p. ej. judge.py:46 y modules/quality_gates/tribunal/outcome.py:84-92).

### 1.1 Desglose por documento (medido)

| Documento | Citas |
|---|---|
| `00-lecciones-capitalizadas.md` | 7 |
| `01-plan-maestro.md` | 108 |
| `05-prompt-inicio-sesion-fase-0.md` | 10 |
| `05-prompt-inicio-sesion-fase-B.md` | 7 |
| `05-prompt-inicio-sesion-fase-C.md` | 10 |
| `05-prompt-inicio-sesion-fase-G.md` | 9 |
| `05-prompt-inicio-sesion-fase-H.md` | 10 |
| `06-checklist-implementacion.md` | 1 |
| `10-analisis-post-implementacion.md` | 2 |
| `dependencias-fases.md` | 3 |
| **Total** | **167** |

Sin citas: `04-contrato-ejecucion.md`, `05-prompt-inicio-sesion-fase-A.md`, `05-prompt-inicio-sesion-fase-D.md`, `05-prompt-inicio-sesion-fase-E.md`, `05-prompt-inicio-sesion-fase-E2E.md`, `05-prompt-inicio-sesion-fase-F.md`, `05-prompt-inicio-sesion-fase-RELEASE.md`, `05-prompt-inicio-sesion-fase-VERIFY.md`, `09-documentacion-post-proyecto.md`, `README.md`.

**Corrección al enunciado de la tarea 0.1.** El desglose de la tarea 0.1 atribuía 1 cita a 09-documentacion-post-proyecto.md. Medido: ese documento tiene 0 citas y el resto del desglose suma exactamente 167, que es el total declarado. Las dos coincidencias `:NNN` de ese archivo son horarios (`11:06-11:10`, `15:01`), no anclas de línea, y el verificador no las cuenta.

## 2. Mediciones de la revisión 2 verificadas en disco

### `M4-blast-radius` — estado: resuelta-cifra-sustituida

Afirmación verificada: 52 archivos y 816 funciones canónicas (866 casos collectados), 545 en los 31 archivos que citan las claves de estado entre comillas dobles, 4 asserts de igualdad exacta de forma

Afirmación anterior refutada: 26 archivos / 476 funciones (anotada en la primera pasada de la revisión 2 sin criterio reproducible; sustituida el 2026-09-19 por decisión del operador). Previa a esa: 50 archivos / 779 / 328 / 2, tomada de un subagente sin re-medir.

| Medido | Valor |
|---|---|
| `archivos_del_vecindario` | 52 |
| `funciones_canonicas` | 816 |
| `casos_collectados_pytest` | 866 |
| `asserts_igualdad_exacta_de_forma` | 4 |
| `archivos_con_estado_hardcodeado` | 31 |
| `funciones_en_esos_archivos` | 545 |

```text
$W='grep -rlE "whatsapp_button|site_presence_report" tests --include=*.py | sort'   # -> 52 archivos
$W | xargs grep -hE "^\s*def test_" | wc -l   # -> 816 funciones canonicas
pytest $W --collect-only -q | tail -1   # -> 866 tests collected
$H=$W | xargs grep -lE '"(status|site_verified|presence_status)"' | sort   # -> 31 archivos
$H | xargs grep -hE "^\s*def test_" | wc -l   # -> 545 funciones
A122..A125 de este anexo enumeran los 4 asserts de igualdad exacta de forma
```

Detalle: 52 / 816 / 866 / 4 se reproducen exactamente y se conservan. El par 26 / 476 no se reprodujo con ninguno de los trece criterios medidos (banda 22/427 a 32/552), así que el 2026-09-19, por decisión del operador, el plan adopta **31 archivos / 545 funciones** y enuncia su criterio: de los 52 archivos del vecindario, los que citan `"(status|site_verified|presence_status)"` entre comillas dobles. Admitir también la comilla simple desplaza el par a 32 / 552, diferencia que queda declarada para que la medición sea reproducible.

| Variante del criterio probada | archivos / funciones |
|---|---|
| criterio (status\|site_verified\|presence_status) sin comillas | 45 / 739 |
| clave + dos puntos | 22 / 427 |
| clave: valor string | 21 / 413 |
| solo "status": | 21 / 391 |
| solo presence_status | 9 / 160 |
| solo site_verified | 8 / 107 |
| sin restringir a las 52 (todo tests/) | 59 / 965 |
| clave citada indistintamente con comilla simple o doble + dos puntos | 23 / 434 |
| clave citada indistintamente con comilla simple o doble | 32 / 552 |
| asignación status\|site_verified\|presence_status = literal | 18 / 260 |
| solo site_verified o presence_status entre comillas | 12 / 186 |
| unión de «clave + dos puntos» con la palabra "status" entre comillas | 29 / 509 |

Banda observada: 22/427 (mínima) a 32/552 (máxima) sobre los 52 archivos del vecindario. 26 cae dentro de la banda pero 476 no es el conteo de ninguna de sus fronteras; los doce criterios anteriores más el redactado en el plan (13 en total) no devuelven el par.

Paso 4: `$W` filtrado por `xargs grep -lE` con la clave entre comillas dobles literales. Verificado otra vez el 2026-09-19 después de la sustitución: 31 archivos y 545 funciones.

Las cifras que dimensionan la división AC19a/AC19b son las reproducibles (52/816/866/4 y 31/545 con su criterio enunciado); 26/476 era una fila accesoria de esa misma medición y desde el 2026-09-19 no figura como afirmación del plan, solo como antecedente refutado en esta fila.

### `M-snapshot-p4` — estado: verificada

Afirmación verificada: 5 assets con verification_failed en el snapshot de FASE-P4 (10 ocurrencias por duplicarse el bloque results)

| Medido | Valor |
|---|---|
| `ocurrencias` | 10 |
| `assets_distintos` | 5 |
| `assets` | ["faq_page", "hotel_schema", "llms_txt", "org_schema", "whatsapp_button"] |
| `explicacion_duplicacion` | "snapshot/<asset>/status y snapshot/results/<asset>/status" |

### `M-catalogo-vs-comentario` — estado: verificada

Afirmación verificada: El comentario de main.py afirma que whatsapp_button SÍ es promised_by=always, y el catálogo lo tiene ELIMINADO

| Medido | Valor |
|---|---|
| `comentario` | "# (which includes promised_by=always assets like voice_assistant_guide, whatsapp_button, monthly_report)" |
| `catalogo` | "promised_by=[\"no_whatsapp_visible\", \"whatsapp_conflict\"]  # FASE-5: \"always\" ELIMINADO - bug sistemico" |

### `M-consentimiento-y-defaults` — estado: verificada

Afirmación verificada: Premisas del §5 y del AC14

| Medido | Valor |
|---|---|
| `observaciones_don_alfonso` | 1 |
| `claves_de_contacto_en_la_observacion` | 0 |
| `adr_cop_y_occupancy_rate_presentes` | true |
| `ONBOARDING_FRESHNESS_HOURS_en_env` | 0 |
| `ONBOARDING_FRESHNESS_HOURS_en_env_template` | 0 |
| `fixture_canal_directo_pct` | 20.0 |
| `warehouse_canal_directo_pct` | 30.0 |
| `default_cristalizado_en_test_e2e` | "tests/e2e/test_onboarding_to_harness_pipeline.py:41 datos.get(\"canal_directo_pct\", 20.0)" |

## 3. Índice de anclas por archivo

Una fila por ancla. La posición citada es la medida el 2026-09-19 en HEAD `938f59f`; la columna símbolo es lo que queda escrito en el documento del plan.

| ID | Ruta relativa | Línea o rango | Símbolo que lo contiene | Forma | Oc. | Estado |
|---|---|---|---|---|---|---|
| A121 | `.gitignore` | `20,54,77` | `.gitignore — patrones *.log (20), output/*/ (54), .env (77); logs/* en 18` | breve | 1 | verificada-con-nota |
| A131 | `.opencode/plans/Archives/SR-PIPELINE-FIXES-2026-08-27/10-analisis-post-implementacion.md` | `125` | `MD: ### Lecciones nuevas de este plan (L-PF1+ …)` | calificada | 1 | verificada |
| A133 | `.opencode/plans/Archives/TRIBUNAL-ENFORCEMENT-OBS-2026-09-11/10-analisis-post-implementacion.md` | `68` | `MD: ### FASE-P1 (2026-09-14) — decisiones DA-P1.1 … DA-P1.10` | calificada | 1 | verificada |
| A130 | `.opencode/plans/Archives/TRIBUNAL-OFFLINE-2026-09-09/10-analisis-post-implementacion.md` | `133-134` | `MD: #### FASE-E2E (2026-09-11)` | calificada | 1 | verificada |
| A132 | `.opencode/plans/Archives/VALIDADOR-URL-PROPIA-2026-08-30/10-analisis-post-implementacion.md` | `65` | `MD: ### Lecciones nuevas de este plan (numeración L-VUP-n)` | calificada | 1 | verificada |
| A040 | `agent_harness/memory.py` | `334-357` | `MemoryManager.find_latest_analysis` | calificada | 1 | verificada |
| A041 | `agent_harness/memory.py` | `357` | `MemoryManager.find_latest_analysis` | calificada,breve | 3 | verificada |
| A042 | `agent_harness/memory.py` | `405-417` | `MemoryManager.cleanup_old_sessions` | calificada | 1 | verificada |
| A129 | `evidence/FASE-I/comparacion-vs-baseline.md` | `81` | `MD: ## 2. NRs verificados` | calificada | 2 | verificada |
| A001 | `main.py` | `43-176` | `build_parser` | calificada | 1 | verificada |
| A002 | `main.py` | `166-176` | `build_parser` | cantidad-no-ancla | 1 | no-cuadraba-corregida |
| A003 | `main.py` | `84-88` | `build_parser` | calificada,breve | 3 | verificada |
| A004 | `main.py` | `220-231` | `ensure_url` | calificada,breve | 2 | verificada |
| A005 | `main.py` | `1433` | `main` | breve | 1 | verificada |
| A006 | `main.py` | `1666` | `run_v4_complete_mode` | calificada | 3 | verificada |
| A007 | `main.py` | `1686` | `run_v4_complete_mode` | breve | 3 | verificada |
| A008 | `main.py` | `1703-1706` | `run_v4_complete_mode` | breve | 3 | verificada |
| A009 | `main.py` | `1736` | `run_v4_complete_mode` | calificada,breve | 2 | verificada |
| A010 | `main.py` | `1744-1749` | `run_v4_complete_mode (OperationPermission V4ComprehensiveAuditor.audit)` | breve | 1 | verificada-con-nota |
| A011 | `main.py` | `1750-1756` | `run_v4_complete_mode` | calificada,breve | 3 | verificada |
| A012 | `main.py` | `1864` | `run_v4_complete_mode` | calificada | 2 | verificada |
| A013 | `main.py` | `1872` | `run_v4_complete_mode` | calificada,breve | 4 | verificada |
| A014 | `main.py` | `1890` | `run_v4_complete_mode` | breve | 2 | verificada |
| A015 | `main.py` | `1909` | `run_v4_complete_mode` | calificada | 3 | verificada |
| A016 | `main.py` | `2263` | `run_v4_complete_mode > get_scenario_value` | calificada,continuacion | 1 | verificada |
| A017 | `main.py` | `2445-2446` | `run_v4_complete_mode > get_scenario_value` | calificada | 1 | verificada |
| A018 | `main.py` | `2657` | `run_v4_complete_mode > V4DiagnosticGenerator.generate` | calificada | 1 | verificada |
| A019 | `main.py` | `2865` | `run_v4_complete_mode > V4ProposalGenerator.generate` | breve | 1 | verificada |
| A020 | `main.py` | `2807` | `run_v4_complete_mode (comentario FIX-D7, junto al guard `if generate_proposal`)` | calificada,breve | 4 | verificada |
| A021 | `main.py` | `3009-3012` | `run_v4_complete_mode` | calificada | 1 | verificada |
| A022 | `main.py` | `3019-3021` | `run_v4_complete_mode` | calificada | 1 | verificada |
| A023 | `main.py` | `3027-3029` | `run_v4_complete_mode` | breve | 1 | verificada |
| A024 | `main.py` | `3421-3429` | `run_v4_complete_mode (rama de supresión del Tribunal)` | calificada,breve | 3 | verificada |
| A025 | `main.py` | `3437-3443` | `run_v4_complete_mode (rama publish)` | calificada,breve | 3 | verificada |
| A026 | `main.py` | `3829-3863` | `_compute_package_evidence` | breve | 1 | verificada |
| A027 | `main.py` | `3866-3906` | `_observation_to_onboarding_format` | calificada | 1 | verificada |
| A028 | `main.py` | `3877-3882` | `_observation_to_onboarding_format._FIELD_MAP` | calificada,breve | 4 | verificada |
| A029 | `main.py` | `3909-3980` | `_load_latest_onboarding_data` | calificada,breve | 3 | verificada |
| A030 | `main.py` | `3921` | `_load_latest_onboarding_data (docstring, Args → hotel_name)` | breve | 3 | verificada |
| A031 | `main.py` | `3933-3965` | `_load_latest_onboarding_data (rama YAML de clientes_dir)` | breve | 1 | verificada |
| A032 | `main.py` | `3934` | `_load_latest_onboarding_data (rama YAML)` | breve | 1 | verificada |
| A033 | `main.py` | `3941` | `_load_latest_onboarding_data (rama YAML)` | breve | 1 | verificada |
| A034 | `main.py` | `3948` | `_load_latest_onboarding_data (rama YAML)` | calificada,breve | 4 | verificada |
| A035 | `main.py` | `3954-3963` | `_load_latest_onboarding_data (control de frescura)` | calificada | 1 | verificada |
| A036 | `main.py` | `3957-3958` | `_load_latest_onboarding_data (control de frescura)` | calificada,breve | 3 | verificada |
| A037 | `main.py` | `3967-3978` | `_load_latest_onboarding_data (fallback warehouse)` | breve | 2 | verificada |
| A038 | `main.py` | `4009-4045` | `_build_gate_report_payload` | calificada,breve | 1 | verificada |
| A039 | `main.py` | `4042` | `_build_gate_report_payload` | breve | 1 | verificada |
| A052 | `modules/asset_generation/asset_catalog.py` | `58-68` | `ASSET_CATALOG["whatsapp_button"]` | calificada | 3 | verificada |
| A053 | `modules/asset_generation/asset_catalog.py` | `63` | `ASSET_CATALOG["whatsapp_button"].required_confidence` | calificada | 1 | verificada |
| A054 | `modules/asset_generation/asset_catalog.py` | `67` | `ASSET_CATALOG["whatsapp_button"].promised_by` | calificada | 3 | verificada |
| A055 | `modules/asset_generation/conditional_generator.py` | `241-264` | `ConditionalGenerator.PAIN_TO_ASSET` | calificada | 3 | verificada |
| A056 | `modules/asset_generation/conditional_generator.py` | `427` | `ConditionalGenerator._generate_content` | calificada | 1 | verificada |
| A060 | `modules/asset_generation/pain_ledger.py` | `137-168` | `PainLedger.apply_site_verification` | calificada | 1 | verificada |
| A050 | `modules/asset_generation/preflight_checks.py` | `44-51` | `NEW_HOTEL_THRESHOLDS (constante de módulo)` | calificada | 1 | verificada-con-nota |
| A051 | `modules/asset_generation/preflight_checks.py` | `48` | `NEW_HOTEL_THRESHOLDS["whatsapp_button"]` | calificada | 4 | verificada |
| A061 | `modules/asset_generation/proposal_asset_alignment.py` | `461-497` | `_presence_exists` | calificada | 1 | verificada |
| A049 | `modules/asset_generation/site_presence_adapter.py` | `107-127` | `_presence_result_to_canonical` | calificada,breve | 3 | verificada |
| A043 | `modules/asset_generation/site_presence_checker.py` | `343` | `SitePresenceChecker._check_asset_presence` | breve | 2 | verificada |
| A044 | `modules/asset_generation/site_presence_checker.py` | `371-374` | `SitePresenceChecker._check_asset_presence` | calificada,breve | 4 | verificada |
| A045 | `modules/asset_generation/site_presence_checker.py` | `447-502` | `SitePresenceChecker._check_html_element` | calificada,breve | 2 | verificada |
| A046 | `modules/asset_generation/site_presence_checker.py` | `477` | `SitePresenceChecker._check_html_element` | calificada | 5 | verificada |
| A047 | `modules/asset_generation/site_presence_checker.py` | `480-483` | `SitePresenceChecker._check_html_element` | breve | 2 | verificada |
| A048 | `modules/asset_generation/site_presence_checker.py` | `501-502` | `SitePresenceChecker._check_html_element` | breve | 2 | verificada |
| A057 | `modules/asset_generation/v4_asset_orchestrator.py` | `286` | `V4AssetOrchestrator.generate_assets` | calificada,breve | 3 | verificada |
| A058 | `modules/asset_generation/v4_asset_orchestrator.py` | `701-758` | `V4AssetOrchestrator._solutions_to_asset_specs` | calificada | 1 | verificada |
| A059 | `modules/asset_generation/v4_asset_orchestrator.py` | `871-877` | `V4AssetOrchestrator._extract_validated_fields` | calificada | 1 | verificada |
| A067 | `modules/auditors/llm_mention_checker.py` | `118-120` | `LLMMentionChecker.__init__` | breve | 1 | verificada |
| A068 | `modules/auditors/llm_mention_checker.py` | `135-144` | `LLMMentionChecker._sanitize_text` | calificada | 1 | verificada |
| A069 | `modules/auditors/llm_mention_checker.py` | `146-156` | `LLMMentionChecker._sanitize_error` | breve | 1 | verificada-con-nota |
| A065 | `modules/auditors/v4_comprehensive.py` | `278` | `V4AuditResult.to_dict` | calificada,continuacion | 1 | verificada |
| A066 | `modules/auditors/v4_comprehensive.py` | `1563-1599` | `V4ComprehensiveAuditor._detect_whatsapp_from_html` | calificada | 5 | verificada |
| A083 | `modules/commercial_documents/coherence_config.py` | `60-65` | `CoherenceConfig.DEFAULT_RULES["whatsapp_verified"]` | calificada | 1 | verificada |
| A078 | `modules/commercial_documents/coherence_validator.py` | `409-414` | `CoherenceValidator._check_whatsapp_verified` | calificada | 1 | verificada |
| A079 | `modules/commercial_documents/coherence_validator.py` | `411-414` | `CoherenceValidator._check_whatsapp_verified` | calificada | 1 | verificada |
| A080 | `modules/commercial_documents/coherence_validator.py` | `437,446` | `CoherenceValidator._check_whatsapp_verified (dos retornos por campo ausente)` | breve | 1 | verificada |
| A081 | `modules/commercial_documents/coherence_validator.py` | `457-459` | `CoherenceValidator._check_whatsapp_verified (boost DT-4)` | continuacion | 1 | verificada |
| A082 | `modules/commercial_documents/coherence_validator.py` | `586-620` | `CoherenceValidator._extract_verified_in_production_types` | continuacion | 1 | verificada |
| A070 | `modules/commercial_documents/pain_solution_mapper.py` | `60-78` | `PainSolutionMapper.PAIN_SOLUTION_MAP` | calificada | 1 | verificada |
| A071 | `modules/commercial_documents/pain_solution_mapper.py` | `63` | `PainSolutionMapper.PAIN_SOLUTION_MAP["no_whatsapp_visible"]` | calificada | 1 | verificada |
| A072 | `modules/commercial_documents/pain_solution_mapper.py` | `72` | `PainSolutionMapper.PAIN_SOLUTION_MAP["whatsapp_conflict"]` | breve | 1 | verificada |
| A073 | `modules/commercial_documents/pain_solution_mapper.py` | `333-339` | `PainSolutionMapper.detect_pains` | calificada | 1 | verificada |
| A074 | `modules/commercial_documents/pain_solution_mapper.py` | `338` | `PainSolutionMapper.detect_pains (parámetro whatsapp_html_detected)` | calificada | 1 | verificada |
| A075 | `modules/commercial_documents/pain_solution_mapper.py` | `355` | `PainSolutionMapper.detect_pains (rama no_whatsapp_visible)` | calificada | 1 | verificada |
| A076 | `modules/commercial_documents/pain_solution_mapper.py` | `890-934` | `PainSolutionMapper.get_assets_for_pain` | breve | 1 | verificada |
| A077 | `modules/commercial_documents/pain_solution_mapper.py` | `925-927` | `PainSolutionMapper.get_assets_for_pain (especial whatsapp_conflict)` | calificada | 2 | verificada |
| A084 | `modules/commercial_documents/v4_diagnostic_generator.py` | `177` | `ELEMENTO_KB_TO_PAIN_ID["nap_consistente"]` | calificada,breve | 3 | verificada-con-nota |
| A085 | `modules/commercial_documents/v4_diagnostic_generator.py` | `3300-3305` | `V4DiagnosticGenerator._identify_brechas` | calificada | 2 | verificada |
| A086 | `modules/commercial_documents/v4_proposal_generator.py` | `1388-1405` | `V4ProposalGenerator._generate_dynamic_services_table` | calificada | 1 | verificada |
| A087 | `modules/commercial_documents/v4_proposal_generator.py` | `1437` | `V4ProposalGenerator._generate_dynamic_services_table` | calificada,breve | 3 | verificada |
| A088 | `modules/commercial_documents/v4_proposal_generator.py` | `1559-1582` | `V4ProposalGenerator._generate_dynamic_services_table` | continuacion | 3 | verificada |
| A117 | `modules/data_validation/external_apis/pagespeed_client.py` | `34-39` | `PageSpeedClient._make_request` | calificada | 2 | verificada |
| A118 | `modules/data_validation/external_apis/pagespeed_client.py` | `53,62` | `PageSpeedClient._make_request` | continuacion | 2 | verificada |
| A064 | `modules/delivery/delivery_context.py` | `48-78` | `DeliveryAssetEntry.from_skipped_asset` | calificada | 1 | verificada |
| A112 | `modules/delivery/delivery_packager.py` | `343-357` | `DeliveryPackager.suppress` | calificada | 1 | verificada |
| A113 | `modules/financial_engine/scenario_calculator.py` | `508-509` | `ScenarioCalculator._determine_evidence_tier` | calificada | 1 | verificada |
| A114 | `modules/financial_engine/scenario_calculator.py` | `520` | `ScenarioCalculator._determine_evidence_tier` | breve | 1 | verificada |
| A062 | `modules/quality_gates/alignment_result.py` | `62-77` | `_presence_resolved` | calificada | 1 | verificada |
| A063 | `modules/quality_gates/delivery_quality_report.py` | `266-276` | `DeliveryQualityReportGenerator.generate` | calificada | 1 | verificada |
| A092 | `modules/quality_gates/domain_gates.py` | `312-314` | `CommercialGate.__init__` | calificada | 1 | verificada |
| A089 | `modules/quality_gates/publication_gates.py` | `709-721` | `PublicationGatesOrchestrator._critical_recall_gate (rama PASSED)` | calificada,breve | 5 | verificada |
| A090 | `modules/quality_gates/publication_gates.py` | `2124-2127` | `PublicationGatesOrchestrator._extract_critical_recall (return 1.0)` | breve | 5 | verificada |
| A091 | `modules/quality_gates/publication_gates.py` | `1030` | `PublicationGatesOrchestrator._proposal_asset_alignment_gate` | calificada,continuacion | 1 | verificada |
| A110 | `modules/quality_gates/tribunal/acta_writer.py` | `135` | `ActaWriter._write_md` | calificada | 1 | verificada |
| A111 | `modules/quality_gates/tribunal/acta_writer.py` | `157` | `ActaWriter._render_reviewer_reports` | breve | 1 | verificada |
| A109 | `modules/quality_gates/tribunal/artifact_paths.py` | `44-49` | `resolve_latest (bucle de ascendientes)` | calificada | 1 | verificada |
| A106 | `modules/quality_gates/tribunal/asset_reviewer.py` | `123-130` | `AssetReviewer._resolve_artifact` | calificada | 1 | verificada |
| A107 | `modules/quality_gates/tribunal/asset_reviewer.py` | `191-214` | `AssetReviewer._resolve_delivery_zip` | breve | 1 | verificada |
| A102 | `modules/quality_gates/tribunal/diagnosis_reviewer.py` | `81-88` | `DiagnosisReviewer._resolve_artifact` | calificada | 1 | verificada |
| A103 | `modules/quality_gates/tribunal/diagnosis_reviewer.py` | `120-128` | `DiagnosisReviewer._load_diagnostic_md` | breve | 1 | verificada |
| A104 | `modules/quality_gates/tribunal/diagnosis_reviewer.py` | `136-137` | `DiagnosisReviewer._check_pain_traceability` | calificada,breve | 2 | verificada |
| A105 | `modules/quality_gates/tribunal/diagnosis_reviewer.py` | `199` | `DiagnosisReviewer._check_vacuous_recall` | calificada | 4 | verificada-con-nota |
| A108 | `modules/quality_gates/tribunal/honesty_reviewer.py` | `201-205` | `HonestyReviewer._resolve_manifest_path` | calificada | 2 | verificada |
| A093 | `modules/quality_gates/tribunal/judge.py` | `43` | `T1_CERTIFIABLE_CLAUSES (constante de módulo)` | calificada,breve | 2 | verificada |
| A094 | `modules/quality_gates/tribunal/judge.py` | `46` | `BLOCKING_VERDICTS (constante de módulo)` | calificada | 5 | verificada |
| A095 | `modules/quality_gates/tribunal/judge.py` | `141-165` | `TribunalJudge._resolve_manifest` | calificada | 2 | verificada |
| A096 | `modules/quality_gates/tribunal/judge.py` | `226-230` | `TribunalJudge._evaluate_clauses (entrada P6.5)` | breve | 2 | verificada |
| A097 | `modules/quality_gates/tribunal/judge.py` | `269-279` | `TribunalJudge._evaluate_p6_2` | calificada,breve | 2 | verificada |
| A098 | `modules/quality_gates/tribunal/judge.py` | `450-462` | `TribunalJudge._apply_first_floor_rule` | calificada | 1 | verificada |
| A099 | `modules/quality_gates/tribunal/judge.py` | `494` | `TribunalJudge._compute_verdict` | calificada | 3 | verificada |
| A100 | `modules/quality_gates/tribunal/outcome.py` | `84-92` | `ReviewerReport.to_dict` | calificada,breve | 4 | verificada |
| A101 | `modules/quality_gates/tribunal/outcome.py` | `101` | `ReviewerReport.verified_block` | calificada | 2 | verificada-con-nota |
| A115 | `modules/scrapers/google_places_client.py` | `356` | `GooglePlacesClient.search_by_name` | calificada | 2 | verificada |
| A116 | `modules/utils/http_client.py` | `259-267` | `HttpClient._sanitize_error` | calificada | 2 | verificada-con-nota |
| A119 | `scripts/run_all_validations.py` | `240-264` | `ValidationRunner._git_tracked_files` | calificada | 1 | verificada |
| A120 | `scripts/run_all_validations.py` | `266-356` | `ValidationRunner._check_no_secrets` | calificada | 1 | verificada |
| A122 | `tests/asset_generation/test_site_presence_adapter.py` | `68` | `TestNormalizeSitePresence.test_normalize_from_none` | calificada | 3 | verificada |
| A128 | `tests/delivery/test_p2_cuarentena_zip.py` | `188` | `_informe_bloqueante (helper de fixture)` | breve | 1 | verificada |
| A126 | `tests/quality_gates/test_publication_gates.py` | `622` | `TestCriticalRecallGate.test_empty_critical_issues_with_audit_passes` | breve | 2 | verificada |
| A127 | `tests/quality_gates/tribunal/test_diagnosis_reviewer.py` | `115,130-131` | `audit_with_founded_recall (fixture)` | breve | 2 | verificada |
| A125 | `tests/quality_gates/tribunal/test_s_e2_generate_proposal_false.py` | `42` | `TestPresenceLookupCanonicalDict.test_none_normalize_produces_empty_results` | calificada | 1 | verificada |
| A124 | `tests/test_assessment_builder.py` | `267` | `TestAssessmentPayloadSerialization.test_payload_serialization` | calificada | 1 | verificada |
| A123 | `tests/test_site_presence_persistence.py` | `104` | `test_ruta_fallo_checker_snapshot_vacio_canonico` | calificada | 3 | verificada |

## 4. Hecho que prueba cada ancla

### `.gitignore`

- **A121** — cita literal `:54 / :20 / :77`, posición `20,54,77`, contenedor `.gitignore — patrones *.log (20), output/*/ (54), .env (77); logs/* en 18`: Las rutas de mayor riesgo están declaradas ignoradas, así que nunca entran al escaneo de secretos. *[verificada-con-nota]*
  - Nota: `logs/*` es la línea 18, no la 20; la 20 es `*.log`. El maestro agrupa ambas bajo `:20`. Se citan por patrón.
  - Citada en: 01-plan-maestro.md:25

### `.opencode/plans/Archives/SR-PIPELINE-FIXES-2026-08-27/10-analisis-post-implementacion.md`

- **A131** — cita literal `Archives/SR-PIPELINE-FIXES-2026-08-27/10-analisis-post-implementacion.md:125`, posición `125`, contenedor `MD: ### Lecciones nuevas de este plan (L-PF1+ …)`: Definición original de L-PF11 (dos corridas del mismo hotel comparten identidad de memoria).
  - Citada en: 00-lecciones-capitalizadas.md:29

### `.opencode/plans/Archives/TRIBUNAL-ENFORCEMENT-OBS-2026-09-11/10-analisis-post-implementacion.md`

- **A133** — cita literal `Archives/TRIBUNAL-ENFORCEMENT-OBS-2026-09-11/10-analisis-post-implementacion.md:68`, posición `68`, contenedor `MD: ### FASE-P1 (2026-09-14) — decisiones DA-P1.1 … DA-P1.10`: Definición original de DA-P1.9 (T3a la da el hotel, por contacto del operador).
  - Citada en: 00-lecciones-capitalizadas.md:29

### `.opencode/plans/Archives/TRIBUNAL-OFFLINE-2026-09-09/10-analisis-post-implementacion.md`

- **A130** — cita literal `Archives/TRIBUNAL-OFFLINE-2026-09-09/10-analisis-post-implementacion.md:133-134`, posición `133-134`, contenedor `MD: #### FASE-E2E (2026-09-11)`: Definición original de L-E2E.1 (el punto de cableado importa tanto como el cableado).
  - Citada en: 00-lecciones-capitalizadas.md:29

### `.opencode/plans/Archives/VALIDADOR-URL-PROPIA-2026-08-30/10-analisis-post-implementacion.md`

- **A132** — cita literal `Archives/VALIDADOR-URL-PROPIA-2026-08-30/10-analisis-post-implementacion.md:65`, posición `65`, contenedor `MD: ### Lecciones nuevas de este plan (numeración L-VUP-n)`: Definición original de L-VUP-13 ("Using defaults" es condición de equivalencia).
  - Citada en: 00-lecciones-capitalizadas.md:29

### `agent_harness/memory.py`

- **A040** — cita literal `agent_harness/memory.py:334-357`, posición `334-357`, contenedor `MemoryManager.find_latest_analysis`: Definición de find_latest_analysis(target_id).
  - Citada en: 05-prompt-inicio-sesion-fase-H.md:53
- **A041** — cita literal `agent_harness/memory.py:357`, posición `357`, contenedor `MemoryManager.find_latest_analysis`: output_dir = Path("output"): el escaneo de análisis previos usa un directorio fijo, relativo al cwd, no el --output de la corrida.
  - Citada en: 01-plan-maestro.md:31, 01-plan-maestro.md:116, 05-prompt-inicio-sesion-fase-H.md:53
- **A042** — cita literal `agent_harness/memory.py:405-417`, posición `405-417`, contenedor `MemoryManager.cleanup_old_sessions`: cleanup_old_sessions(self, days: int = 20) borra sesiones de más de N días.
  - Citada en: 01-plan-maestro.md:31

### `evidence/FASE-I/comparacion-vs-baseline.md`

- **A129** — cita literal `evidence/FASE-I/comparacion-vs-baseline.md:81`, posición `81`, contenedor `MD: ## 2. NRs verificados`: Fila `details` con el delta {critical_issues_count: 0, recall_basis: "audit_present_no_critical_issues"} frente a {}: el hueco de serialización ya estaba medido en 2026-09-11.
  - Citada en: 00-lecciones-capitalizadas.md:27, 10-analisis-post-implementacion.md:79

### `main.py`

- **A001** — cita literal `main.py:43-176`, posición `43-176`, contenedor `build_parser`: build_parser declara el comando `command` posicional y todas las opciones con parser.add_argument sobre un único parser: no hay subparsers, así que las opciones aplican a cualquier comando.
  - Citada en: 01-plan-maestro.md:30
- **A002** — cita literal `~27 opciones`, posición `166-176`, contenedor `build_parser`: Cantidad de opciones globales del parser. Medido con AST sobre build_parser: 31 llamadas a add_argument y 30 flags largos distintos. *[no-cuadraba-corregida]*
  - Nota: El maestro decía "~27 opciones". Medido el 2026-09-19: 31 llamadas a `add_argument`, 30 flags largos únicos. Se corrige la cifra en el documento.
  - Citada en: 01-plan-maestro.md:30
- **A003** — cita literal `main.py:84-88`, posición `84-88`, contenedor `build_parser`: `--permission-mode` se declara con choices auto|smart_approve|approve|chat y default="auto": si el argv no lo fija, la corrida autoriza las llamadas externas.
  - Citada en: 01-plan-maestro.md:142, 05-prompt-inicio-sesion-fase-H.md:54, 01-plan-maestro.md:31
- **A004** — cita literal `main.py:220-231`, posición `220-231`, contenedor `ensure_url`: ensure_url reinyecta el `last_url` persistido cuando `--url` falta: `--url` es opcional y una corrida puede apuntar a un hotel distinto del pretendido.
  - Citada en: 01-plan-maestro.md:31, 01-plan-maestro.md:116
- **A005** — cita literal `:1433`, posición `1433`, contenedor `main`: MemoryManager().save_state({"last_url": args.url}) muta estado compartido en cada invocación.
  - Citada en: 01-plan-maestro.md:31
- **A006** — cita literal `main.py:1666`, posición `1666`, contenedor `run_v4_complete_mode`: memory.cleanup_old_sessions(days=20) se invoca dentro del propio v4complete: la corrida borra sesiones de .agent/memory antes de trabajar.
  - Citada en: 01-plan-maestro.md:31, 01-plan-maestro.md:116, 05-prompt-inicio-sesion-fase-H.md:55
- **A007** — cita literal `:1686`, posición `1686`, contenedor `run_v4_complete_mode`: canonical_url = _normalize_url(args.url): tercera identidad de la corrida, la que indexa la memoria.
  - Citada en: 01-plan-maestro.md:32, 01-plan-maestro.md:142, 05-prompt-inicio-sesion-fase-H.md:46
- **A008** — cita literal `:1703-1706`, posición `1703-1706`, contenedor `run_v4_complete_mode`: hotel_name = args.nombre or _extract_hotel_name_from_url(args.url): el nombre del paquete sale de --nombre, no de la URL.
  - Citada en: 01-plan-maestro.md:32, 01-plan-maestro.md:142, 05-prompt-inicio-sesion-fase-H.md:46
- **A009** — cita literal `main.py:1736 / :1736`, posición `1736`, contenedor `run_v4_complete_mode`: discovered_analysis = memory.find_latest_analysis(canonical_url): la corrida puede reutilizar un análisis previo en vez de auditar.
  - Citada en: 05-prompt-inicio-sesion-fase-H.md:53, 01-plan-maestro.md:31
- **A010** — cita literal `:1744`, posición `1744-1749`, contenedor `run_v4_complete_mode (OperationPermission V4ComprehensiveAuditor.audit)`: estimated_cost=0.03 e is_external=True en la operación de auditoría: la llamada externa tiene coste y se gatea por permission-mode. *[verificada-con-nota]*
  - Nota: El literal `estimated_cost=0.03` está en la línea 1746; la 1744 es el comentario que abre el bloque. Se cita por símbolo.
  - Citada en: 01-plan-maestro.md:142
- **A011** — cita literal `main.py:1750-1756`, posición `1750-1756`, contenedor `run_v4_complete_mode`: Si check_permission(audit_op, perm_mode) falla, el pipeline continúa sin auditoría (audit_result=None) y con defaults: mismo exit code, otro flujo.
  - Citada en: 01-plan-maestro.md:116, 05-prompt-inicio-sesion-fase-H.md:54, 01-plan-maestro.md:31
- **A012** — cita literal `main.py:1864`, posición `1864`, contenedor `run_v4_complete_mode`: canal_directo = datos_operativos.get('canal_directo_pct', 20.0): el default de canal directo del pipeline es 20.0.
  - Citada en: 01-plan-maestro.md:29, 01-plan-maestro.md:130
- **A013** — cita literal `main.py:1872`, posición `1872`, contenedor `run_v4_complete_mode`: print("   ℹ️  Using defaults (no fresh onboarding data found)"): sucursal de defaults del loader, visible solo en el log.
  - Citada en: 01-plan-maestro.md:113, 05-prompt-inicio-sesion-fase-H.md:37, 01-plan-maestro.md:29, 01-plan-maestro.md:130
- **A014** — cita literal `:1890`, posición `1890`, contenedor `run_v4_complete_mode`: direct_channel_pct = 0.20 # Default 20%: segundo punto de default del mismo canal.
  - Citada en: 01-plan-maestro.md:29, 01-plan-maestro.md:130
- **A015** — cita literal `main.py:1909`, posición `1909`, contenedor `run_v4_complete_mode`: "hotel_id": args.url: el hotel_id del reporte sale de la URL, no del nombre comercial.
  - Citada en: 01-plan-maestro.md:32, 01-plan-maestro.md:142, 05-prompt-inicio-sesion-fase-H.md:46
- **A016** — cita literal `main.py:2263,2273`, posición `2263`, contenedor `run_v4_complete_mode > get_scenario_value`: match_percentage=0.5 y 0.6 en los escenarios: dos barras de coincidencia distintas sobre el mismo hecho. Continuaciones citadas en el mismo rango: 2273.
  - Citada en: 01-plan-maestro.md:104
- **A017** — cita literal `main.py:2445-2446`, posición `2445-2446`, contenedor `run_v4_complete_mode > get_scenario_value`: detected_pains = pain_mapper.detect_pains(...) en main sí propaga la señal HTML: una de las tres rutas que divergen.
  - Citada en: 01-plan-maestro.md:18
- **A018** — cita literal `main.py:2657`, posición `2657`, contenedor `run_v4_complete_mode > V4DiagnosticGenerator.generate`: El diagnóstico se escribe con output_dir=str(output_dir) (padre), no en el directorio del hotel: por eso el glob de ascendientes lo alcanza.
  - Citada en: 01-plan-maestro.md:24
- **A019** — cita literal `:2865`, posición `2865`, contenedor `run_v4_complete_mode > V4ProposalGenerator.generate`: La propuesta se escribe con el mismo output_dir padre que el diagnóstico.
  - Citada en: 01-plan-maestro.md:24
- **A020** — cita literal `main.py:2807`, posición `2807`, contenedor `run_v4_complete_mode (comentario FIX-D7, junto al guard `if generate_proposal`)`: El comentario dice "(which includes promised_by=always assets like voice_assistant_guide, whatsapp_button, monthly_report)": afirma que whatsapp_button SÍ es promised_by=always.
  - Nota: Confirmado contra AssetCatalog["whatsapp_button"].promised_by, que solo lista no_whatsapp_visible y whatsapp_conflict con el comentario `FASE-5: "always" ELIMINADO`. La contradicción es en el sentido que declara el maestro: el comentario de main.py es el que se quedó atrás.
  - Citada en: 01-plan-maestro.md:19, 05-prompt-inicio-sesion-fase-B.md:21, 05-prompt-inicio-sesion-fase-B.md:30, 01-plan-maestro.md:19
- **A021** — cita literal `main.py:3009-3012`, posición `3009-3012`, contenedor `run_v4_complete_mode`: _gate_blocking_enabled = getenv("GATE_BLOCKING_ENABLED", "true") y su rama: el borrado de documentos exige NOT_READY o claim escalado, no ocurre en cualquier bloqueo.
  - Citada en: 01-plan-maestro.md:24
- **A022** — cita literal `main.py:3019-3021`, posición `3019-3021`, contenedor `run_v4_complete_mode`: _diag_var = "diagnostic_path" + `if _diag_var in locals() and locals()[_diag_var]`: resolución de rutas por lookup de locals().
  - Citada en: dependencias-fases.md:47
- **A023** — cita literal `:3027-3029`, posición `3027-3029`, contenedor `run_v4_complete_mode`: Mismo patrón para _prop_var = "proposal_path": segunda instancia del lookup frágil.
  - Citada en: dependencias-fases.md:47
- **A024** — cita literal `main.py:3421-3429`, posición `3421-3429`, contenedor `run_v4_complete_mode (rama de supresión del Tribunal)`: package_evidence = _compute_package_evidence(quarantine_tmp_path) y su re-escritura del acta ocurren SOLO en la rama que suprime, antes de packager.suppress().
  - Citada en: 01-plan-maestro.md:63, 01-plan-maestro.md:111, 05-prompt-inicio-sesion-fase-0.md:27
- **A025** — cita literal `main.py:3437-3443`, posición `3437-3443`, contenedor `run_v4_complete_mode (rama publish)`: delivery_zip_path = packager.publish(quarantine_tmp_path): la rama publish no calcula ni registra package_evidence.
  - Citada en: 01-plan-maestro.md:111, 01-plan-maestro.md:119, 05-prompt-inicio-sesion-fase-0.md:27
- **A026** — cita literal `~3829-3863`, posición `3829-3863`, contenedor `_compute_package_evidence`: Productor de la evidencia del paquete: sha256 y member_count del ZIP en cuarentena.
  - Citada en: 05-prompt-inicio-sesion-fase-0.md:27
- **A027** — cita literal `main.py:3866-3906`, posición `3866-3906`, contenedor `_observation_to_onboarding_format`: Transformador observación → YAML de onboarding.
  - Citada en: 05-prompt-inicio-sesion-fase-H.md:38
- **A028** — cita literal `main.py:3877-3882`, posición `3877-3882`, contenedor `_observation_to_onboarding_format._FIELD_MAP`: _FIELD_MAP tiene exactamente 4 claves: habitaciones→rooms, reservas_mes→monthly_reservations, valor_reserva_cop→avg_reservation_cop, canal_directo_pct→direct_channel_percentage.
  - Nota: Verificado además que la observación de Don Alfonso en data/hotel_observations/observations.json sí contiene adr_cop (330000) y occupancy_rate (0.4242): el transformador los descarta, no es un problema de la fuente.
  - Citada en: 01-plan-maestro.md:29, 01-plan-maestro.md:113, 01-plan-maestro.md:130, 05-prompt-inicio-sesion-fase-H.md:38
- **A029** — cita literal `main.py:3909-3980`, posición `3909-3980`, contenedor `_load_latest_onboarding_data`: Firma del loader: (hotel_url, hotel_name, output_dir=None). Contiene las tres ramas de salida.
  - Citada en: 01-plan-maestro.md:113, 05-prompt-inicio-sesion-fase-H.md:36, 01-plan-maestro.md:30
- **A030** — cita literal `:3921`, posición `3921`, contenedor `_load_latest_onboarding_data (docstring, Args → hotel_name)`: La docstring declara `hotel_name: Nombre del hotel (solo para logging, no se usa para matching)`.
  - Nota: 3920 es la línea de `hotel_url`. El ancla correcta es 3921, como queda registrado aquí y como símbolo en el documento.
  - Citada en: 01-plan-maestro.md:30, 01-plan-maestro.md:113, 05-prompt-inicio-sesion-fase-H.md:36
- **A031** — cita literal `:3933-3965`, posición `3933-3965`, contenedor `_load_latest_onboarding_data (rama YAML de clientes_dir)`: clientes_dir = output_dir or Path("output/clientes"); la rama YAML va del guard `if clientes_dir.exists():` (3933) al `return data` (3965).
  - Citada en: 05-prompt-inicio-sesion-fase-H.md:37
- **A032** — cita literal `:3934`, posición `3934`, contenedor `_load_latest_onboarding_data (rama YAML)`: clientes_dir.glob("*_onboarding.yaml"): glob no recursivo.
  - Citada en: 01-plan-maestro.md:30
- **A033** — cita literal `:3941`, posición `3941`, contenedor `_load_latest_onboarding_data (rama YAML)`: `if not data or 'metadatos' not in data: continue`: exige la clave metadatos para considerar el YAML.
  - Citada en: 01-plan-maestro.md:30
- **A034** — cita literal `main.py:3948`, posición `3948`, contenedor `_load_latest_onboarding_data (rama YAML)`: `if _normalize_url(yaml_url) != normalized_url: continue`: la clave de coincidencia es la URL normalizada; el nombre no participa.
  - Citada en: 01-plan-maestro.md:132, 01-plan-maestro.md:30, 01-plan-maestro.md:113, 05-prompt-inicio-sesion-fase-H.md:36
- **A035** — cita literal `main.py:3954-3963`, posición `3954-3963`, contenedor `_load_latest_onboarding_data (control de frescura)`: freshness_hours = os.getenv("ONBOARDING_FRESHNESS_HOURS") y su bloque de descarte por antigüedad.
  - Nota: Medido además: ONBOARDING_FRESHNESS_HOURS no aparece en .env ni en .env.template (0 coincidencias en cada archivo), así que el bloque hoy no corre.
  - Citada en: 01-plan-maestro.md:134
- **A036** — cita literal `main.py:3957-3958`, posición `3957-3958`, contenedor `_load_latest_onboarding_data (control de frescura)`: fecha_str = data.get('metadatos', {}).get('fecha_captura') seguido de `if fecha_str:`: sin fecha capturada el control se omite en silencio.
  - Citada en: 05-prompt-inicio-sesion-fase-H.md:39, 01-plan-maestro.md:113, 01-plan-maestro.md:134
- **A037** — cita literal `:3967-3976 / :3967-3978`, posición `3967-3978`, contenedor `_load_latest_onboarding_data (fallback warehouse)`: Comentario "# Fallback: buscar en observations.json", re-conversión con _observation_to_onboarding_format y `except Exception: pass  # Fallback silencioso`.
  - Nota: Las dos formas del rango conviven en el plan (3976 en el maestro, 3978 en el prompt H). El bloque termina en 3978 (`pass`); ambas caen dentro. Se unifica al símbolo.
  - Citada en: 01-plan-maestro.md:30, 05-prompt-inicio-sesion-fase-H.md:37
- **A038** — cita literal `main.py:4009-4045`, posición `4009-4045`, contenedor `_build_gate_report_payload`: Writer del gate_report: serializa el payload de cada gate.
  - Citada en: 05-prompt-inicio-sesion-fase-0.md:26
- **A039** — cita literal `~4042`, posición `4042`, contenedor `_build_gate_report_payload`: "details": r.details: el writer del reporte no filtra el diccionario; el hueco de serialización está en el productor del gate, no aquí.
  - Citada en: 05-prompt-inicio-sesion-fase-0.md:26

### `modules/asset_generation/asset_catalog.py`

- **A052** — cita literal `asset_catalog.py:58-68`, posición `58-68`, contenedor `ASSET_CATALOG["whatsapp_button"]`: Entrada completa del asset: required_field="whatsapp", required_confidence=0.7, block_on_failure=False.
  - Citada en: 01-plan-maestro.md:19, 05-prompt-inicio-sesion-fase-B.md:21, 05-prompt-inicio-sesion-fase-G.md:24
- **A053** — cita literal `asset_catalog.py:63`, posición `63`, contenedor `ASSET_CATALOG["whatsapp_button"].required_confidence`: required_confidence=0.7 con block_on_failure=False: tercera barra sobre el mismo hecho, no bloqueante.
  - Citada en: 01-plan-maestro.md:104
- **A054** — cita literal `asset_catalog.py:67`, posición `67`, contenedor `ASSET_CATALOG["whatsapp_button"].promised_by`: promised_by=["no_whatsapp_visible", "whatsapp_conflict"]  # FASE-5: "always" ELIMINADO - bug sistemico.
  - Citada en: 01-plan-maestro.md:19, 01-plan-maestro.md:19, 05-prompt-inicio-sesion-fase-B.md:21

### `modules/asset_generation/conditional_generator.py`

- **A055** — cita literal `conditional_generator.py:241-264`, posición `241-264`, contenedor `ConditionalGenerator.PAIN_TO_ASSET`: Segundo mapa pain→asset. Medido sobre el rango: no contiene la clave no_whatsapp_visible.
  - Citada en: 01-plan-maestro.md:19, 05-prompt-inicio-sesion-fase-B.md:21, 05-prompt-inicio-sesion-fase-G.md:24
- **A056** — cita literal `conditional_generator.py:427`, posición `427`, contenedor `ConditionalGenerator._generate_content`: validated_data.get("whatsapp") or validated_data.get("whatsapp_number", {}): la clave whatsapp tiene precedencia, y phone_web viaja por esa clave.
  - Citada en: 01-plan-maestro.md:46

### `modules/asset_generation/pain_ledger.py`

- **A060** — cita literal `pain_ledger.py:137-168`, posición `137-168`, contenedor `PainLedger.apply_site_verification`: Consumer 1 del reporte canónico: results = site_presence_report.get("results", {}) y promoción a VERIFIED_IN_SITE.
  - Citada en: 01-plan-maestro.md:67

### `modules/asset_generation/preflight_checks.py`

- **A050** — cita literal `preflight_checks.py:44-51`, posición `44-51`, contenedor `NEW_HOTEL_THRESHOLDS (constante de módulo)`: Diccionario de umbrales para hoteles nuevos. *[verificada-con-nota]*
  - Nota: El diccionario vive a nivel de módulo (clave NEW_HOTEL_THRESHOLDS en 46); no está dentro de la dataclass PreflightReport. Se cita por clave.
  - Citada en: 01-plan-maestro.md:19
- **A051** — cita literal `preflight_checks.py:48`, posición `48`, contenedor `NEW_HOTEL_THRESHOLDS["whatsapp_button"]`: "whatsapp_button": 0.3,  # Reduced from 0.7: la barra más baja que planifica el botón en hotel nuevo.
  - Citada en: 01-plan-maestro.md:104, 05-prompt-inicio-sesion-fase-G.md:24, 06-checklist-implementacion.md:55, 05-prompt-inicio-sesion-fase-B.md:21

### `modules/asset_generation/proposal_asset_alignment.py`

- **A061** — cita literal `proposal_asset_alignment.py:461-497`, posición `461-497`, contenedor `_presence_exists`: Consumer 2: resuelve presencia canónica con is_present_in_production.
  - Citada en: 01-plan-maestro.md:67

### `modules/asset_generation/site_presence_adapter.py`

- **A049** — cita literal `modules/asset_generation/site_presence_adapter.py:107-127`, posición `107-127`, contenedor `_presence_result_to_canonical`: Única puerta de forma del reporte canónico: devuelve exactamente status, site_verified y confidence; no propaga details.
  - Citada en: 05-prompt-inicio-sesion-fase-C.md:9, 01-plan-maestro.md:27, 01-plan-maestro.md:67

### `modules/asset_generation/site_presence_checker.py`

- **A043** — cita literal `:343`, posición `343`, contenedor `SitePresenceChecker._check_asset_presence`: _check_html_element(site_url, ...): la sonda HTML recibe la URL raíz; no hay crawl ni /contacto/.
  - Citada en: 01-plan-maestro.md:27, 05-prompt-inicio-sesion-fase-C.md:9
- **A044** — cita literal `site_presence_checker.py:371-374`, posición `371-374`, contenedor `SitePresenceChecker._check_asset_presence`: `if not schema_report.get("schemas_encontrados"): if "error" in schema_report: status = PresenceStatus.VERIFICATION_FAILED`: el verification_failed lo estampa el error del schema report, no el fetch HTML.
  - Citada en: 01-plan-maestro.md:47, 10-analisis-post-implementacion.md:69, 05-prompt-inicio-sesion-fase-C.md:9, 01-plan-maestro.md:27
- **A045** — cita literal `modules/asset_generation/site_presence_checker.py:447-502`, posición `447-502`, contenedor `SitePresenceChecker._check_html_element`: Lector HTML canónico completo: sondas de texto, href y clases CSS.
  - Citada en: 01-plan-maestro.md:27, 05-prompt-inicio-sesion-fase-C.md:9
- **A046** — cita literal `site_presence_checker.py:477`, posición `477`, contenedor `SitePresenceChecker._check_html_element`: Primer lector: `any(pattern in href.lower() for pattern in ['wa.me','api.whatsapp.com','whatsapp'])` sobre <a href>.
  - Citada en: 01-plan-maestro.md:27, 01-plan-maestro.md:67, 01-plan-maestro.md:160, 05-prompt-inicio-sesion-fase-C.md:9, 05-prompt-inicio-sesion-fase-C.md:23
- **A047** — cita literal `:480-483`, posición `480-483`, contenedor `SitePresenceChecker._check_html_element`: re.search(r'wa\.me/(\d+)') → whatsapp_href_number: el lector sí extrae el número, que el adaptador luego descarta.
  - Citada en: 01-plan-maestro.md:27, 05-prompt-inicio-sesion-fase-C.md:9
- **A048** — cita literal `:501-502`, posición `501-502`, contenedor `SitePresenceChecker._check_html_element`: `except Exception: return {"found": False}`: cualquier fallo de transporte colapsa a no-encontrado.
  - Citada en: 01-plan-maestro.md:27, 05-prompt-inicio-sesion-fase-C.md:9

### `modules/asset_generation/v4_asset_orchestrator.py`

- **A057** — cita literal `modules/asset_generation/v4_asset_orchestrator.py:286`, posición `286`, contenedor `V4AssetOrchestrator.generate_assets`: pains = self.pain_mapper.detect_pains(audit_result, validation_summary, analytics_data) sin whatsapp_html_detected: la divergencia viva entre rutas.
  - Citada en: 05-prompt-inicio-sesion-fase-G.md:24, 01-plan-maestro.md:18, 05-prompt-inicio-sesion-fase-G.md:69
- **A058** — cita literal `v4_asset_orchestrator.py:701-758`, posición `701-758`, contenedor `V4AssetOrchestrator._solutions_to_asset_specs`: Convertidor solutions→AssetSpec: cuarto punto donde se decide el plan de assets.
  - Citada en: 01-plan-maestro.md:19
- **A059** — cita literal `v4_asset_orchestrator.py:871-877`, posición `871-877`, contenedor `V4AssetOrchestrator._extract_validated_fields`: validated_data["whatsapp"] = validated_data.get("phone_web", "") (FIX-A2): el teléfono web se asigna a la clave whatsapp.
  - Citada en: 01-plan-maestro.md:46

### `modules/auditors/llm_mention_checker.py`

- **A067** — cita literal `:118-120`, posición `118-120`, contenedor `LLMMentionChecker.__init__`: Se guardan exactamente 3 valores de key (gemini, openrouter, perplexity): el universo que el redactor puede reconocer.
  - Citada en: 01-plan-maestro.md:25
- **A068** — cita literal `llm_mention_checker.py:135-144`, posición `135-144`, contenedor `LLMMentionChecker._sanitize_text`: Bucle `for key_value in (self._gemini_key, self._openrouter_key, self._perplexity_key): text.replace(key_value, "***")`: redacción solo por igualdad literal de 3 keys.
  - Citada en: 01-plan-maestro.md:25
- **A069** — cita literal `:146-156`, posición `146-156`, contenedor `LLMMentionChecker._sanitize_error`: re.sub(r'([?&]key=)[^&\s"\']+', r'\1***', msg): solo el patrón key= de query. *[verificada-con-nota]*
  - Nota: 146 es el decorador @staticmethod; la definición es 147. Se cita por símbolo.
  - Citada en: 01-plan-maestro.md:25

### `modules/auditors/v4_comprehensive.py`

- **A065** — cita literal `v4_comprehensive.py:278`, posición `278`, contenedor `V4AuditResult.to_dict`: "error_message": self.schema.error_message (278) y self.gbp.error_message (296): el texto crudo de la excepción se persiste en el audit_report. Continuaciones citadas en el mismo rango: 296.
  - Citada en: 01-plan-maestro.md:25
- **A066** — cita literal `modules/auditors/v4_comprehensive.py:1563-1599`, posición `1563-1599`, contenedor `V4ComprehensiveAuditor._detect_whatsapp_from_html`: Segundo lector de WhatsApp, con su propia lista de patrones por regex sobre html.lower(): produce whatsapp_html_detected, goberna el pain.
  - Citada en: 01-plan-maestro.md:27, 01-plan-maestro.md:67, 01-plan-maestro.md:160, 05-prompt-inicio-sesion-fase-C.md:9, 05-prompt-inicio-sesion-fase-C.md:23

### `modules/commercial_documents/coherence_config.py`

- **A083** — cita literal `coherence_config.py:60-65`, posición `60-65`, contenedor `CoherenceConfig.DEFAULT_RULES["whatsapp_verified"]`: confidence_threshold=0.9 con blocking=True para whatsapp_verified.
  - Citada en: 01-plan-maestro.md:104

### `modules/commercial_documents/coherence_validator.py`

- **A078** — cita literal `coherence_validator.py:409-414`, posición `409-414`, contenedor `CoherenceValidator._check_whatsapp_verified`: Lectura del presence report dentro del check (site_whatsapp_exists / whatsapp_presence = site_presence_report.get("whatsapp_button", {})).
  - Citada en: 01-plan-maestro.md:20
- **A079** — cita literal `coherence_validator.py:411-414`, posición `411-414`, contenedor `CoherenceValidator._check_whatsapp_verified`: Consumer 8 del reporte canónico: lee la clave whatsapp_button y su estado.
  - Citada en: 01-plan-maestro.md:67
- **A080** — cita literal `:437, :446`, posición `437,446`, contenedor `CoherenceValidator._check_whatsapp_verified (dos retornos por campo ausente)`: Las dos ramas `if not whatsapp_field [and whatsapp_html_detected]: return CoherenceCheck(...)` retornan antes del boost: el boost solo actúa cuando existe campo.
  - Citada en: 01-plan-maestro.md:20
- **A081** — cita literal `coherence_validator.py:409-414,457-459`, posición `457-459`, contenedor `CoherenceValidator._check_whatsapp_verified (boost DT-4)`: `if site_whatsapp_exists: confidence_score = max(confidence_score, 0.95)`.
  - Citada en: 01-plan-maestro.md:20
- **A082** — cita literal `coherence_validator.py:411-414,586-620`, posición `586-620`, contenedor `CoherenceValidator._extract_verified_in_production_types`: Consumer 8 (segundo punto): itera top-level keys y results del reporte canónico.
  - Nota: La continuacion 586-620 NO pertenece a _check_whatsapp_verified: cae en _extract_verified_in_production_types. El rango compuesto del maestro mezclaba dos métodos; se separan.
  - Citada en: 01-plan-maestro.md:67

### `modules/commercial_documents/pain_solution_mapper.py`

- **A070** — cita literal `pain_solution_mapper.py:60-78`, posición `60-78`, contenedor `PainSolutionMapper.PAIN_SOLUTION_MAP`: Primer mapa pain→soluciones, con confidence_required por pain.
  - Citada en: 01-plan-maestro.md:19
- **A071** — cita literal `pain_solution_mapper.py:63`, posición `63`, contenedor `PainSolutionMapper.PAIN_SOLUTION_MAP["no_whatsapp_visible"]`: "confidence_required": 0.9 para no_whatsapp_visible.
  - Citada en: 01-plan-maestro.md:104
- **A072** — cita literal `:72`, posición `72`, contenedor `PainSolutionMapper.PAIN_SOLUTION_MAP["whatsapp_conflict"]`: "confidence_required": 0.5 y assets [whatsapp_button, whatsapp_conflict_guide] para whatsapp_conflict.
  - Citada en: 01-plan-maestro.md:104
- **A073** — cita literal `pain_solution_mapper.py:333-339`, posición `333-339`, contenedor `PainSolutionMapper.detect_pains`: Firma real de detect_pains, con whatsapp_html_detected: bool = False al final.
  - Citada en: 01-plan-maestro.md:18
- **A074** — cita literal `pain_solution_mapper.py:338`, posición `338`, contenedor `PainSolutionMapper.detect_pains (parámetro whatsapp_html_detected)`: El parámetro sí existe en la firma: la omisión del orquestador es un olvido de cableado, no una inexistencia.
  - Citada en: 05-prompt-inicio-sesion-fase-G.md:24
- **A075** — cita literal `pain_solution_mapper.py:355`, posición `355`, contenedor `PainSolutionMapper.detect_pains (rama no_whatsapp_visible)`: `if (not whatsapp_field or whatsapp_field.confidence in (UNKNOWN, CONFLICT)) and not whatsapp_html_detected:`: con centinela ESTIMATED no dispara; la divergencia exige campo UNKNOWN/CONFLICT + HTML.
  - Citada en: 01-plan-maestro.md:18
- **A076** — cita literal `:890-934`, posición `890-934`, contenedor `PainSolutionMapper.get_assets_for_pain`: Método completo que decide can_generate por pain.
  - Citada en: 01-plan-maestro.md:19
- **A077** — cita literal `pain_solution_mapper.py:925-927`, posición `925-927`, contenedor `PainSolutionMapper.get_assets_for_pain (especial whatsapp_conflict)`: `if pain_id == "whatsapp_conflict": can_generate = True`: fuerza el botón ante conflicto, saltando la comparación de confianza.
  - Citada en: 01-plan-maestro.md:20, 01-plan-maestro.md:105

### `modules/commercial_documents/v4_diagnostic_generator.py`

- **A084** — cita literal `modules/commercial_documents/v4_diagnostic_generator.py:177`, posición `177`, contenedor `ELEMENTO_KB_TO_PAIN_ID["nap_consistente"]`: "nap_consistente": ("whatsapp_conflict", "whatsapp_button", None): un gap de NAP produce pain y asset de WhatsApp. *[verificada-con-nota]*
  - Nota: El contenedor es el diccionario de módulo ELEMENTO_KB_TO_PAIN_ID (clave en 166), no un método. Se cita por clave.
  - Citada en: 05-prompt-inicio-sesion-fase-B.md:21, 01-plan-maestro.md:19, 05-prompt-inicio-sesion-fase-G.md:24
- **A085** — cita literal `v4_diagnostic_generator.py:3300-3305`, posición `3300-3305`, contenedor `V4DiagnosticGenerator._identify_brechas`: detect_pains(..., whatsapp_html_detected=whatsapp_html_detected) en el generador de diagnóstico: segunda ruta que sí propaga la señal.
  - Citada en: 01-plan-maestro.md:18, 05-prompt-inicio-sesion-fase-G.md:24

### `modules/commercial_documents/v4_proposal_generator.py`

- **A086** — cita literal `v4_proposal_generator.py:1388-1405`, posición `1388-1405`, contenedor `V4ProposalGenerator._generate_dynamic_services_table`: Consumer 7: construcción de presence_lookup desde site_presence_report.
  - Citada en: 01-plan-maestro.md:67
- **A087** — cita literal `modules/commercial_documents/v4_proposal_generator.py:1437`, posición `1437`, contenedor `V4ProposalGenerator._generate_dynamic_services_table`: `if asset_type == "whatsapp_button" and whatsapp_conflict:` → override del estado mostrado en la matriz de servicios.
  - Citada en: 05-prompt-inicio-sesion-fase-B.md:21, 01-plan-maestro.md:19, 05-prompt-inicio-sesion-fase-G.md:24
- **A088** — cita literal `v4_proposal_generator.py:1437,1559-1582`, posición `1559-1582`, contenedor `V4ProposalGenerator._generate_dynamic_services_table`: whatsapp_service_name derivado de PROPOSAL_SERVICE_TO_ASSET y el filtro whatsapp_sin_brecha que excluye el servicio de la lista.
  - Citada en: 01-plan-maestro.md:19, 05-prompt-inicio-sesion-fase-B.md:21, 05-prompt-inicio-sesion-fase-G.md:24

### `modules/data_validation/external_apis/pagespeed_client.py`

- **A117** — cita literal `pagespeed_client.py:34-39`, posición `34-39`, contenedor `PageSpeedClient._make_request`: params = {"url": url, "key": self.api_key, ...}: la key viaja en query.
  - Citada en: 01-plan-maestro.md:25, 01-plan-maestro.md:112
- **A118** — cita literal `pagespeed_client.py:34-39,53,62`, posición `53,62`, contenedor `PageSpeedClient._make_request`: raise Exception(f"...{response.status_code}: {response.text}") (53) y f"Request failed: {str(e)}" (62): interpolan cuerpo y excepción crudos.
  - Citada en: 01-plan-maestro.md:25, 01-plan-maestro.md:112

### `modules/delivery/delivery_context.py`

- **A064** — cita literal `delivery_context.py:48-78`, posición `48-78`, contenedor `DeliveryAssetEntry.from_skipped_asset`: Consumer 6: lee presence_status y site_verified del skipped_asset y deriva el estado de entrega.
  - Citada en: 01-plan-maestro.md:67

### `modules/delivery/delivery_packager.py`

- **A112** — cita literal `delivery_packager.py:343-357`, posición `343-357`, contenedor `DeliveryPackager.suppress`: tmp.unlink(): la supresión borra el .zip.tmp, de modo que el contenido del ZIP no es legible después de la decisión.
  - Citada en: 01-plan-maestro.md:109

### `modules/financial_engine/scenario_calculator.py`

- **A113** — cita literal `scenario_calculator.py:508-509`, posición `508-509`, contenedor `ScenarioCalculator._determine_evidence_tier`: ga4_enabled and gsc_enabled and has_verified_data → EvidenceTier.A: tier A exige los dos conectores.
  - Citada en: 01-plan-maestro.md:124
- **A114** — cita literal `:520`, posición `520`, contenedor `ScenarioCalculator._determine_evidence_tier`: return EvidenceTier.B al final del cascada: B es el default, no una excepción.
  - Citada en: 01-plan-maestro.md:124

### `modules/quality_gates/alignment_result.py`

- **A062** — cita literal `alignment_result.py:62-77`, posición `62-77`, contenedor `_presence_resolved`: Consumer 3: presence.get("status") bajo el criterio canónico.
  - Citada en: 01-plan-maestro.md:67

### `modules/quality_gates/delivery_quality_report.py`

- **A063** — cita literal `delivery_quality_report.py:266-276`, posición `266-276`, contenedor `DeliveryQualityReportGenerator.generate`: Consumer 5: el QA de entrega lee site_presence_report dentro de la partición canónica.
  - Citada en: 01-plan-maestro.md:67

### `modules/quality_gates/domain_gates.py`

- **A092** — cita literal `domain_gates.py:312-314`, posición `312-314`, contenedor `CommercialGate.__init__`: whatsapp_confidence_threshold con default 0.9: sexta barra, en el módulo legado no productivo.
  - Citada en: 01-plan-maestro.md:104

### `modules/quality_gates/publication_gates.py`

- **A089** — cita literal `publication_gates.py:709-721`, posición `709-721`, contenedor `PublicationGatesOrchestrator._critical_recall_gate (rama PASSED)`: details: Dict[str, Any] = {} y la anotación con critical_issues_count/recall_basis SOLO cuando critical_issues está vacío y hay audit_schema.
  - Citada en: 01-plan-maestro.md:28, 01-plan-maestro.md:63, 01-plan-maestro.md:119, dependencias-fases.md:64, 05-prompt-inicio-sesion-fase-0.md:11
- **A090** — cita literal `:2124-2127`, posición `2124-2127`, contenedor `PublicationGatesOrchestrator._extract_critical_recall (return 1.0)`: critical_issues NO vacío y _evident_critical_missed == 0 → return 1.0: el recall fundado que viaja sin details.
  - Citada en: 01-plan-maestro.md:28, 01-plan-maestro.md:63, 01-plan-maestro.md:119, dependencias-fases.md:64, 05-prompt-inicio-sesion-fase-0.md:11
- **A091** — cita literal `publication_gates.py:1030,1064-1077`, posición `1030`, contenedor `PublicationGatesOrchestrator._proposal_asset_alignment_gate`: Consumer 4: assessment.get("site_presence_report") y su paso al matrix y a AlignmentResult. Continuaciones citadas en el mismo rango: 1064-1077.
  - Citada en: 01-plan-maestro.md:67

### `modules/quality_gates/tribunal/acta_writer.py`

- **A110** — cita literal `acta_writer.py:135`, posición `135`, contenedor `ActaWriter._write_md`: lines.extend(self._render_reviewer_reports(acta.get("reviewer_reports"))): to_dict alimenta también el acta en MD.
  - Citada en: 05-prompt-inicio-sesion-fase-0.md:27
- **A111** — cita literal `:157`, posición `157`, contenedor `ActaWriter._render_reviewer_reports`: Renderizador de la sección Reportes de Revisores (una fila por Bot, AC-E0).
  - Citada en: 05-prompt-inicio-sesion-fase-0.md:27

### `modules/quality_gates/tribunal/artifact_paths.py`

- **A109** — cita literal `artifact_paths.py:44-49`, posición `44-49`, contenedor `resolve_latest (bucle de ascendientes)`: for _ in range(ancestor_levels + 1) con ANCESTOR_LEVELS = 3: recorre 4 directorios hacia arriba, sí alcanza el output_dir padre.
  - Citada en: 01-plan-maestro.md:24

### `modules/quality_gates/tribunal/asset_reviewer.py`

- **A106** — cita literal `asset_reviewer.py:123-130`, posición `123-130`, contenedor `AssetReviewer._resolve_artifact`: Mismo patrón que Bot 1: glob propio sobre v4_audit_dir.
  - Citada en: 01-plan-maestro.md:24
- **A107** — cita literal `:191-214`, posición `191-214`, contenedor `AssetReviewer._resolve_delivery_zip`: Único revisor que abre el ZIP en cuarentena (.zip.tmp).
  - Citada en: 01-plan-maestro.md:110

### `modules/quality_gates/tribunal/diagnosis_reviewer.py`

- **A102** — cita literal `diagnosis_reviewer.py:81-88`, posición `81-88`, contenedor `DiagnosisReviewer._resolve_artifact`: Glob limitado a self.v4_audit_dir: no alcanza los documentos escritos en el output_dir padre.
  - Citada en: 01-plan-maestro.md:24
- **A103** — cita literal `:120-128`, posición `120-128`, contenedor `DiagnosisReviewer._load_diagnostic_md`: Usa _resolve_artifact y devuelve None si no resuelve.
  - Citada en: 01-plan-maestro.md:24
- **A104** — cita literal `diagnosis_reviewer.py:136-137`, posición `136-137`, contenedor `DiagnosisReviewer._check_pain_traceability`: `if pain_ledger is None or diagnostic_md is None: return findings` con findings vacío: verde silencioso ante documento no resuelto.
  - Citada en: 01-plan-maestro.md:110, 01-plan-maestro.md:24
- **A105** — cita literal `modules/quality_gates/tribunal/diagnosis_reviewer.py:199`, posición `199`, contenedor `DiagnosisReviewer._check_vacuous_recall`: `if recall_value == 1.0 and not has_critical_count:` (198) y el append del hallazgo SEVERITY_CRITICAL / FINDING_VACUOUS_RECALL / clause P6.1 (199). *[verificada-con-nota]* Continuaciones citadas en el mismo rango: 198 (el if; el append citado cae en 199).
  - Nota: El prompt de FASE-0 transcribía el `if` como contenido de la línea 199; el `if` está en 198 y el append en 199. Al citar `_check_vacuous_recall` la precisión se conserva y el desfase desaparece.
  - Citada en: 05-prompt-inicio-sesion-fase-0.md:11, 01-plan-maestro.md:28, 05-prompt-inicio-sesion-fase-0.md:34, dependencias-fases.md:64

### `modules/quality_gates/tribunal/honesty_reviewer.py`

- **A108** — cita literal `honesty_reviewer.py:201-205`, posición `201-205`, contenedor `HonestyReviewer._resolve_manifest_path`: pick_most_recent(self.deliveries_dir.glob("*/MANIFEST.json")): nunca encuentra manifiesto en modo ZIP-only.
  - Citada en: 01-plan-maestro.md:24, 01-plan-maestro.md:110

### `modules/quality_gates/tribunal/judge.py`

- **A093** — cita literal `judge.py:43`, posición `43`, contenedor `T1_CERTIFIABLE_CLAUSES (constante de módulo)`: T1_CERTIFIABLE_CLAUSES = ("P6.1", "P6.3", "P6.4", "P6.6"): son 4 cláusulas, no 6.
  - Citada en: 05-prompt-inicio-sesion-fase-0.md:36, 01-plan-maestro.md:111
- **A094** — cita literal `judge.py:46`, posición `46`, contenedor `BLOCKING_VERDICTS (constante de módulo)`: BLOCKING_VERDICTS = frozenset({VERDICT_BLOCKED, VERDICT_RETURN}): APROBADO-CONDICIONAL-PENDING-ONBOARDING no está, así que es publicable.
  - Citada en: 00-lecciones-capitalizadas.md:13, 01-plan-maestro.md:28, 01-plan-maestro.md:63, 01-plan-maestro.md:124, 05-prompt-inicio-sesion-fase-0.md:28
- **A095** — cita literal `judge.py:141-165`, posición `141-165`, contenedor `TribunalJudge._resolve_manifest`: Resuelve MANIFEST.json por glob en deliveries_dir: en modo ZIP-only ese archivo no existe.
  - Citada en: 01-plan-maestro.md:24, 01-plan-maestro.md:110
- **A096** — cita literal `:226-230`, posición `226-230`, contenedor `TribunalJudge._evaluate_clauses (entrada P6.5)`: P6.5 fijada a STATUS_NOT_EVALUABLE por diseño (D-T1.3 opción a).
  - Citada en: 01-plan-maestro.md:111, 05-prompt-inicio-sesion-fase-0.md:36
- **A097** — cita literal `judge.py:269-279`, posición `269-279`, contenedor `TribunalJudge._evaluate_p6_2`: P6.2 retorna NOT_EVALUABLE: "no implementado en T1".
  - Citada en: 01-plan-maestro.md:111, 05-prompt-inicio-sesion-fase-0.md:36
- **A098** — cita literal `judge.py:450-462`, posición `450-462`, contenedor `TribunalJudge._apply_first_floor_rule`: Regla de primer piso: evidence_tier in FIRST_FLOOR_TIERS (B/C) → máximo APROBADO-CONDICIONAL.
  - Citada en: 01-plan-maestro.md:117
- **A099** — cita literal `judge.py:494`, posición `494`, contenedor `TribunalJudge._compute_verdict`: `if any(r.verified_critical or r.verified_block for r in reviewer_reports): return VERDICT_BLOCKED`: por aquí el hallazgo CRITICAL de Bot 1 suprimió el ZIP.
  - Citada en: 01-plan-maestro.md:28, 01-plan-maestro.md:119, 05-prompt-inicio-sesion-fase-0.md:11

### `modules/quality_gates/tribunal/outcome.py`

- **A100** — cita literal `modules/quality_gates/tribunal/outcome.py:84-92`, posición `84-92`, contenedor `ReviewerReport.to_dict`: to_dict serializa reviewer/status/findings_count/critical_count/recommendation/report_path y OMITE findings (el campo existe en la dataclass).
  - Citada en: 05-prompt-inicio-sesion-fase-0.md:27, 01-plan-maestro.md:63, 01-plan-maestro.md:111, 01-plan-maestro.md:119
- **A101** — cita literal `outcome.py:101`, posición `101`, contenedor `ReviewerReport.verified_block`: status.is_ok and recommendation == RECOMMENDATION_BLOCK: basta la recomendación para bloquear, aunque el conteo crítico sea 0 (intermedio falso del contrafactual). *[verificada-con-nota]*
  - Nota: La propiedad se define en 100 y su cuerpo retorna en 101. Se cita por símbolo.
  - Citada en: 00-lecciones-capitalizadas.md:13, 05-prompt-inicio-sesion-fase-0.md:28

### `modules/scrapers/google_places_client.py`

- **A115** — cita literal `google_places_client.py:356`, posición `356`, contenedor `GooglePlacesClient.search_by_name`: error_message=f"Request error: {str(e)}": texto crudo de excepción, sin redacción, que se persiste vía V4AuditResult.to_dict.
  - Citada en: 01-plan-maestro.md:25, 01-plan-maestro.md:112

### `modules/utils/http_client.py`

- **A116** — cita literal `http_client.py:259-267`, posición `259-267`, contenedor `HttpClient._sanitize_error`: Trunca el mensaje a 100 caracteres pero no redacta: devuelve str(error) con la URL. *[verificada-con-nota]*
  - Nota: El maestro encadena `http_client.py:259-267 → logs/ssl_fallback.log`. El sumidero que escribe ese log es modules/utils/ssl_logger.py (LOG_FILE = "ssl_fallback.log"), no este método. Se corrige la atribución en el documento.
  - Citada en: 01-plan-maestro.md:25, 01-plan-maestro.md:112

### `scripts/run_all_validations.py`

- **A119** — cita literal `run_all_validations.py:240-264`, posición `240-264`, contenedor `ValidationRunner._git_tracked_files`: Población que recorre el quick: git ls-files + staged.
  - Citada en: 01-plan-maestro.md:112
- **A120** — cita literal `run_all_validations.py:266-356`, posición `266-356`, contenedor `ValidationRunner._check_no_secrets`: El verificador de secretos solo itera archivos versionados: output/ y logs/ quedan fuera por construcción.
  - Citada en: 01-plan-maestro.md:25

### `tests/asset_generation/test_site_presence_adapter.py`

- **A122** — cita literal `tests/asset_generation/test_site_presence_adapter.py:68`, posición `68`, contenedor `TestNormalizeSitePresence.test_normalize_from_none`: assert result == {"results": {}}: igualdad exacta de forma (assert 1 de 4).
  - Citada en: 01-plan-maestro.md:67, 05-prompt-inicio-sesion-fase-C.md:3, 05-prompt-inicio-sesion-fase-C.md:47

### `tests/delivery/test_p2_cuarentena_zip.py`

- **A128** — cita literal `~188`, posición `188`, contenedor `_informe_bloqueante (helper de fixture)`: Construye un hallazgo con "finding_type": "VACUOUS_RECALL" para probar la cuarentena.
  - Citada en: 05-prompt-inicio-sesion-fase-0.md:41

### `tests/quality_gates/test_publication_gates.py`

- **A126** — cita literal `~622`, posición `622`, contenedor `TestCriticalRecallGate.test_empty_critical_issues_with_audit_passes`: assert result.details.get("critical_issues_count") == 0 en el camino de cero issues: contrato que el cambio de FASE-0 debe dejar verde.
  - Citada en: 05-prompt-inicio-sesion-fase-0.md:41, 05-prompt-inicio-sesion-fase-0.md:69

### `tests/quality_gates/tribunal/test_diagnosis_reviewer.py`

- **A127** — cita literal `~115 / ~130 / :130-131`, posición `115,130-131`, contenedor `audit_with_founded_recall (fixture)`: Fixture con critical_recall=1.0 y details {critical_issues_count: 3, recall_basis: "audit_present_no_critical_issues"}: demuestra que el revisor acepta un conteo >0 y, a la vez, empareja un conteo con una base contradictoria.
  - Nota: El prompt de FASE-0 apunta correctamente a tests/quality_gates/tribunal/test_diagnosis_reviewer.py (no al de publication_gates). La observación de la combinación internamente contradictoria es exacta.
  - Citada en: 05-prompt-inicio-sesion-fase-0.md:41, 05-prompt-inicio-sesion-fase-0.md:43

### `tests/quality_gates/tribunal/test_s_e2_generate_proposal_false.py`

- **A125** — cita literal `tests/quality_gates/tribunal/test_s_e2_generate_proposal_false.py:42`, posición `42`, contenedor `TestPresenceLookupCanonicalDict.test_none_normalize_produces_empty_results`: assert snapshot == {"results": {}}: assert 4 de 4.
  - Citada en: 01-plan-maestro.md:67

### `tests/test_assessment_builder.py`

- **A124** — cita literal `tests/test_assessment_builder.py:267`, posición `267`, contenedor `TestAssessmentPayloadSerialization.test_payload_serialization`: assert d["site_presence_report"] == {"presence_status": "unknown"}: assert 3 de 4.
  - Citada en: 01-plan-maestro.md:67

### `tests/test_site_presence_persistence.py`

- **A123** — cita literal `tests/test_site_presence_persistence.py:104`, posición `104`, contenedor `test_ruta_fallo_checker_snapshot_vacio_canonico`: assert payload["snapshot"] == {"results": {}}: assert 2 de 4. El archivo está en la raíz de tests/, no bajo tests/asset_generation/.
  - Citada en: 01-plan-maestro.md:67, 05-prompt-inicio-sesion-fase-C.md:3, 05-prompt-inicio-sesion-fase-C.md:47

