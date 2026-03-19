#!/usr/bin/env python3
"""
Generate SYSTEM_STATUS.md file with version info and active skills.
"""
import os
import re
from datetime import datetime
from pathlib import Path


def parse_version_yaml(version_path: str) -> dict:
    """Parse VERSION.yaml for version information."""
    versions = {}
    with open(version_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    version_match = re.search(r'^version:\s*["\']?([^"\'\n]+)["\']?', content, re.MULTILINE)
    plan_match = re.search(r'^plan_maestro_version:\s*["\']?([^"\'\n]+)["\']?', content, re.MULTILINE)
    harness_match = re.search(r'^agent_harness_version:\s*["\']?([^"\'\n]+)["\']?', content, re.MULTILINE)
    
    if version_match:
        versions['version'] = version_match.group(1).strip()
    if plan_match:
        versions['plan_maestro_version'] = plan_match.group(1).strip()
    if harness_match:
        versions['agent_harness_version'] = harness_match.group(1).strip()
    
    return versions


def scan_skills(workflows_dir: str) -> list:
    """Scan .agents/workflows/ for skill files and extract info."""
    skills = []
    workflows_path = Path(workflows_dir)
    
    if not workflows_path.exists():
        return skills
    
    for md_file in sorted(workflows_path.glob('*.md')):
        if md_file.name == 'README.md':
            continue
        
        skill_info = extract_skill_info(md_file)
        if skill_info:
            skills.append(skill_info)
    
    return skills


def extract_skill_info(file_path: Path) -> dict:
    """Extract skill name and trigger from a workflow file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    name = extract_description_from_frontmatter(content)
    if not name:
        name = file_path.stem.replace('_', ' ').title()
    
    trigger = extract_trigger(content)
    
    return {
        'name': name,
        'trigger': trigger,
        'filename': file_path.name
    }


def extract_description_from_frontmatter(content: str) -> str:
    """Extract description from YAML frontmatter."""
    frontmatter_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)
        desc_match = re.search(r'^description:\s*(.+)$', frontmatter, re.MULTILINE)
        if desc_match:
            return desc_match.group(1).strip()
    return ''


def extract_trigger(content: str) -> str:
    """Extract trigger from file content."""
    trigger_match = re.search(r'\*\*Trigger\*\*:\s*"([^"]+)"', content)
    if trigger_match:
        return trigger_match.group(1)
    
    trigger_match = re.search(r'\*\*Trigger\*\*:\s*(.+?)(?:\n|$)', content)
    if trigger_match:
        return trigger_match.group(1).strip()
    
    return 'N/A'


def generate_status_file(versions: dict, skills: list, output_path: str) -> None:
    """Generate the SYSTEM_STATUS.md file."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    lines = [
        '# System Status Dashboard',
        '',
        f'> Auto-generado: {timestamp}',
        '> NO EDITAR MANUALMENTE - Este archivo se regenera automáticamente',
        '',
        '## Versiones',
        '',
        '| Componente | Versión | Fuente |',
        '|------------|---------|--------|',
        f'| Proyecto | {versions.get("version", "N/A")} | VERSION.yaml |',
        f'| Plan Maestro | {versions.get("plan_maestro_version", "N/A")} | plan_maestro_data.json |',
        f'| Agent Harness | {versions.get("agent_harness_version", "N/A")} | agent_harness/__init__.py |',
        '',
        f'## Skills Activas ({len(skills)})',
        '',
        '| Skill | Trigger | Ubicación |',
        '|-------|---------|-----------|',
    ]
    
    for skill in skills:
        trigger_display = skill['trigger'] if len(skill['trigger']) <= 50 else skill['trigger'][:47] + '...'
        lines.append(f"| {skill['name']} | {trigger_display} | {skill['filename']} |")
    
    lines.extend([
        '',
        '## Última Validación',
        '',
        f'- Fecha: {timestamp}',
        '- Estado: ⏳ Pendiente de ejecución',
        '',
        '## Próximos Pasos',
        '',
        '1. Ejecutar `python scripts/validate_context_integrity.py`',
        '2. Revisar resultados arriba',
        '',
    ])
    
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def main():
    base_dir = Path(__file__).parent.parent
    
    version_path = base_dir / 'VERSION.yaml'
    workflows_dir = base_dir / '.agents' / 'workflows'
    output_path = base_dir / '.agent' / 'SYSTEM_STATUS.md'
    
    versions = parse_version_yaml(str(version_path))
    skills = scan_skills(str(workflows_dir))
    generate_status_file(versions, skills, str(output_path))
    
    print(f'SYSTEM_STATUS.md generated at: {output_path}')


if __name__ == '__main__':
    main()
