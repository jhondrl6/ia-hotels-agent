### 06 sync de la fecha del README (destino autorizado por el operador) -- 2026-09-25T21:50:55Z
Autorizacion literal: pregunta «como sigo» -> «Correr el sync sobre README.md» (2026-09-25).

Traceback (most recent call last):
  File "<string>", line 9, in <module>
    Path(str(OUT)+'/antes.json').write_text(json.dumps(antes,indent=1),encoding='utf-8')
             ^^^
NameError: name 'OUT' is not defined

$ python scripts/sync_versions.py --rule readme_version_header
============================================================
VERSION SYNC
============================================================

Source: C:\Users\Jhond\Github\iah-cli\VERSION.yaml
  version: 4.78.0
  codename: Gobernanza, costura, pertinencia y carga medida
  date: 2026-09-25

OK: README.md (readme_version_header) - updated

============================================================
Result: All files in sync
EXIT=0

$ python -c 'comparar huellas'
Traceback (most recent call last):
  File "<string>", line 5, in <module>
    antes=json.loads(Path(str(OUT)+'/antes.json').read_text(encoding='utf-8'))
                              ^^^
NameError: name 'OUT' is not defined

$ git diff --numstat README.md
2	2	README.md

bytes README: CRLF=0  lineas=306

linea 5:
**v4.78.0** -- Gobernanza, costura, pertinencia y carga medida | Actualizado 25 Septiembre 2026

$ python scripts/sync_versions.py --check
============================================================
VERSION SYNC (CHECK)
============================================================

Source: C:\Users\Jhond\Github\iah-cli\VERSION.yaml
  version: 4.78.0
  codename: Gobernanza, costura, pertinencia y carga medida
  date: 2026-09-25

OK: README.md (readme_version_header) - in sync
OK: AGENTS.md (agents_version_comment) - in sync
OK: AGENTS.md (agents_header_banner) - in sync
OK: .cursorrules (cursorrules_header) - in sync
OK: docs/CONTRIBUTING.md (contributing_version_header) - in sync
OK: docs/GUIA_TECNICA.md (guia_tecnica_header) - in sync

============================================================
Result: All files in sync
EXIT=0
