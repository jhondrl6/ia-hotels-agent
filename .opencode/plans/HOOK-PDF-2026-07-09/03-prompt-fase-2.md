# FASE-2: Generator + CLI Integration (FASE DE MAYOR COMPLEJIDAD TÉCNICA)

## Instrucciones de la sesión

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: SUBAGENTE PARCIAL (delegate_task en 2 sub-tareas paralelas)

## Contexto previo
FASE-1 completada: weasyprint+pyyaml instalados, `HookPDFData` dataclass creado en `data_structures.py` y exportado. Template `hook_template.md` y `hook_styles.css` creados con todos los placeholders.

## Objetivo de esta fase
Implementar la clase `HookPDFGenerator` con sus 4 métodos (extract_data, validate_data, render_html, generate) + integrar el comando `hook-pdf` en `main.py`.

### Tareas
- [ ] 2.1 Crear `modules/commercial_documents/hook_pdf_generator.py` con clase `HookPDFGenerator`:
  - `__init__(output_dir, template_path=None, style_path=None)`
  - `extract_data() -> HookPDFData` — parsea frontmatter YAML de 01_DIAGNOSTICO + 02_PROPUESTA via glob pattern, lee v4_complete_report.json, extrae scores/dirección/GBP del cuerpo .md via regex
  - `validate_data(data) -> list[str]` — ejecuta 8 validaciones (placeholders sin llenar, campos obligatorios, timestamps, formato COP, slug, no-sobrescritura, dry-run, tier)
  - `render_html(data) -> str` — reemplaza placeholders en el template
  - `generate(force=False, dry_run=False) -> Path` — orquesta extract→validate→render→PDF via weasyprint
- [ ] 2.2 Exportar `HookPDFGenerator` en `modules/commercial_documents/__init__.py`
- [ ] 2.3 Modificar `main.py`: agregar `hook-pdf` a choices de argparse, dispatch en `main()`, handler `run_hook_pdf_mode(args)` con args `--output-dir`, `--template`, `--style`, `--dry-run`, `--force`, `--verbose`
- [ ] 2.4 Smoke test: `python3 -c "from modules.commercial_documents.hook_pdf_generator import HookPDFGenerator; print('OK')"` + `python3 main.py hook-pdf --help`

### Restricciones
- NO mezclar code fix + v4complete en la misma fase
- El parser YAML debe leer el frontmatter (bloque entre `---` al inicio del .md)
- Glob pattern para localizar `01_DIAGNOSTICO_Y_OPORTUNIDAD_*.md` y `02_PROPUESTA_COMERCIAL_*.md` sin timestamp manual
- Formato COP: separador de miles (.) sin decimales — usar f-string o locale
- Slug: `hotel_name.lower()` sin acentos ni especiales
- Abortar si no encuentra los 3 archivos fuente (2 .md + 1 .json)
- `--dry-run` muestra datos sin generar PDF
- NO hardcodear `$120.000` en Python — va en el template como `{{PRECIO_EXPRESS}}`
- weasyprint.render_html recibe HTML string, no markdown — el template ya es HTML (FASE-1)

### Criterios de completitud
- [ ] `HookPDFGenerator` instanciable con `output_dir` como Path
- [ ] `extract_data()` retorna `HookPDFData` con todos los campos llenos desde fixtures de prueba
- [ ] `validate_data()` retorna lista de errores/warnings
- [ ] `render_html()` retorna string sin `{{...}}` sin reemplazar
- [ ] `generate()` produce un archivo .pdf (o muestra datos en dry-run)
- [ ] `python3 main.py hook-pdf --help` muestra los 6 argumentos
- [ ] `from modules.commercial_documents import HookPDFGenerator` funciona
- [ ] Cero syntax errors en `python3 -c "import modules.commercial_documents.hook_pdf_generator"`

### Próxima sesión
FASE-3: Tests unitarios (8+ tests) cubriendo extract_data, validate_data, render_html, generate, formato COP, slug, glob pattern resolution, tier detection.

### Prompt para delegate_task (sub-agente A: generator)

```
Goal: Eres un subagente trabajando en el repositorio iah-cli en /mnt/c/Users/Jhond/Github/iah-cli. Implementa la clase HookPDFGenerator en modules/commercial_documents/hook_pdf_generator.py.

Contexto: FASE-1 del plan HOOK-PDF-2026-07-09 está completa. El dataclass HookPDFData ya existe en data_structures.py con todos los campos del catálogo. El template hook_template.md y los estilos hook_styles.css ya existen en templates/. La especificación completa está en .opencode/context/MODULO-HOOK-PDF.md §3.6 (firma del script) y §3.1-3.4 (fuentes de datos, placeholders, validaciones).

Implementa la clase HookPDFGenerator con:
1. __init__(self, output_dir: Path, template_path: Path = None, style_path: Path = None) — defaults apuntan a templates/hook_template.md y templates/hook_styles.css
2. extract_data(self) -> HookPDFData — lee 01_DIAGNOSTICO_*.md y 02_PROPUESTA_*.md via glob, parsea frontmatter YAML, lee v4_complete_report.json, extrae scores/direccion/GBP del cuerpo .md via regex. Retorna HookPDFData.
3. validate_data(self, data: HookPDFData) -> list[str] — 8 validaciones de MODULO-HOOK-PDF.md §3.4
4. render_html(self, data: HookPDFData) -> str — reemplaza {{PLACEHOLDER}} en el template
5. generate(self, force: bool = False, dry_run: bool = False) -> Path — orquesta extract→validate→render→weasyprint. Output: deliveries/{slug}_gancho.pdf

Formato COP: separador miles (.) sin decimales. Slug: hotel_name.lower() sin acentos ni especiales. Abortar si faltan los 3 archivos fuente. Responder en español.
```

### Prompt para delegate_task (sub-agente B: CLI integration)

```
Goal: Eres un subagente trabajando en el repositorio iah-cli en /mnt/c/Users/Jhond/Github/iah-cli. Integra el comando hook-pdf en main.py.

Contexto: FASE-1 del plan HOOK-PDF-2026-07-09 está completa. La clase HookPDFGenerator se está creando en paralelo en modules/commercial_documents/hook_pdf_generator.py. Su firma: HookPDFGenerator(output_dir: Path, template_path: Path = None, style_path: Path = None) con método generate(force=False, dry_run=False) -> Path.

Lee main.py y sigue el patrón existente de comandos (líneas 17-60 muestran el patrón build_parser + dispatch + handler). Agrega:
1. "hook-pdf" a los choices del argumento command en build_parser()
2. Dispatch en main(): if args.command == "hook-pdf": run_hook_pdf_mode(args); sys.exit(0)
3. Handler run_hook_pdf_mode(args) que:
   - Parsea --output-dir (obligatorio), --template (default templates/hook_template.md), --style (default templates/hook_styles.css), --dry-run, --force, --verbose
   - Importa HookPDFGenerator de modules.commercial_documents.hook_pdf_generator
   - Instancia y llama generate(force=args.force, dry_run=args.dry_run)
   - Print del path del PDF generado

Restricciones: NO crear hook_pdf_generator.py (se crea en paralelo). Solo modificar main.py. Responder en español.
```
