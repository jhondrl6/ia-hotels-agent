# FASE-5: RELEASE (Docs + Version + Changelog)

## Instrucciones de la sesión

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: SUBAGENTE (delegate_task) — mecánico

## Contexto previo
FASE-4 completada: PDF real generado desde Luxorhotel, 2 páginas validadas, cero placeholders, datos correctos. El módulo está funcional end-to-end.

## Objetivo de esta fase
Cierre formal del plan: actualizar documentación, bump de versión, changelog, domain primer regeneration, pre-commit.

### Tareas
- [ ] 5.1 CHANGELOG.md: agregar entrada `[Unreleased]` → `v4.49.0` con: "Added: hook-pdf command — genera PDF gancho de 2 páginas desde output de v4complete (Gap #2 Empaquetado no técnico)"
- [ ] 5.2 VERSION.yaml: bump de v4.48.x a v4.49.0 (minor — nuevo comando)
- [ ] 5.3 AGENTS.md: actualizar tabla de módulos (commercial_documents: añadir "PDF gancho"), tabla de comandos CLI (añadir fila `hook-pdf`), y si hay sección de workflows, notar que hook-pdf es post-procesamiento de v4complete
- [ ] 5.4 Ejecutar `python3 scripts/sync_versions.py --check` (verificar consistencia), luego sin args para aplicar. NOTA: sync_versions.py NO acepta --bump ni --release-name. Solo --check, --list, --validate, --rule.
- [ ] 5.5 Ejecutar `python3 scripts/doctor.py --regenerate-domain-primer` (detecta automáticamente hook_pdf_generator.py)
- [ ] 5.6 Ejecutar pre-commit: `python3 -m pre_commit run --all-files` o el equivalente del repo
- [ ] 5.7 log_phase: registrar FASE-5 como completada con `scripts/log_phase_completion.py --fase HOOK-PDF-FASE-5 --desc release_docs_version_bump`

### Restricciones
- RELEASE valida documentación, NO corrige código (pitfall: "RELEASE phases validate documentation quality, NOT code correctness")
- Si pre-commit falla en archivos NO tocados por este plan, es pre-existing — documentar y continuar
- Si sync_versions.py muestra WARN de README.md, es esperado y harmless
- sync_versions.py usa datetime.now() para {date} — last_update será hoy, no la release_date del VERSION.yaml
- El git tag debe ir ANTES del commit de REGISTRY (si se hace tag)
- NO ejecutar `--force-with-lease` ni `branch -d` desde el agente (WSL safety guard bloquea)

### Criterios de completitud
- [ ] CHANGELOG.md tiene entrada v4.49.0 con el feature hook-pdf
- [ ] VERSION.yaml muestra `4.49.0`
- [ ] AGENTS.md tabla de módulos incluye "PDF gancho" en commercial_documents
- [ ] AGENTS.md tabla de comandos incluye fila `hook-pdf`
- [ ] `sync_versions.py --check` pasa sin errores (WARNs de README esperados)
- [ ] DOMAIN_PRIMER.md regenerado (incluye hook_pdf_generator.py automáticamente)
- [ ] pre-commit pasa (o falla solo en archivos pre-existing)
- [ ] log_phase_completion.py ejecutado

### Próxima sesión
Plan completo. No hay más fases. Verificar con `python3 main.py hook-pdf --output-dir output/v4_complete/` que todo funciona end-to-end después del release.

### Prompt para delegate_task

```
Goal: Eres un subagente trabajando en el repositorio iah-cli en /mnt/c/Users/Jhond/Github/iah-cli. Ejecuta la fase RELEASE (FASE-5) del plan HOOK-PDF-2026-07-09.

Contexto: FASE-1 a FASE-4 están completas. El módulo hook_pdf_generator está implementado en modules/commercial_documents/hook_pdf_generator.py, el comando hook-pdf está en main.py, los tests pasan, y el PDF real fue generado exitosamente desde el output de Luxorhotel.

Tareas:
1. CHANGELOG.md: agregar entrada v4.49.0 — "Added: hook-pdf command — PDF gancho de 2 páginas desde v4complete (Gap #2)"
2. VERSION.yaml: bump a 4.49.0 (minor)
3. AGENTS.md: actualizar tabla de módulos (commercial_documents: añadir "PDF gancho" y comando "hook-pdf") y tabla de comandos CLI (añadir fila hook-pdf)
4. Ejecutar: python3 scripts/sync_versions.py --check (verificar). Luego python3 scripts/sync_versions.py (aplicar).
5. Ejecutar: python3 scripts/doctor.py --regenerate-domain-primer
6. Ejecutar pre-commit: python3 -m pre_commit run --all-files
7. Ejecutar: python3 scripts/log_phase_completion.py --fase HOOK-PDF-FASE-5 --desc release_docs_version_bump

Notas: sync_versions.py NO acepta --bump ni --release-name. Solo --check, --list, --validate, --rule. Si pre-commit falla en archivos no tocados por este plan, es pre-existing — documentar. Responder en español.
```
