# Agente Ecosystem Convention

**Version**: 1.0.0
**Created**: 2026-04-03
**Status**: Active

---

## Architecture Overview

The agent ecosystem uses TWO directories with SEPARATE concerns. They are NOT merged, NOT duplicated -- they are a data/instruction split.

```
.agent/                          .agents/
├── CONVENTION.md (este archivo)  └── workflows/
├── MEMORIA_USUARIO.md               ├── README.md          <- Skill index
├── SYSTEM_STATUS.md                 ├── audit_guardian.md  <- Agent instructions
├── knowledge/                       ├── delivery_wizard.md
│   └── DOMAIN_PRIMER.md             ├── truth_protocol.md
├── memory/                          ├── v4_*.md            <- v4 workflow skills
│   ├── current_state.json           ├── v4_regression_guardian.py
│   ├── error_catalog.json           └── templates/
│   ├── sessions/                        └── prompt-fase-template.md
│   └── archives/
├── patterns/
├── shadow_logs/                    <- Git ignored (dynamic)
└── workflows -> ../.agents/workflows  <- Symlink for direct access
```

## Directory Contract

### .agent/ (singular) = RUNTIME DATA
| Subdirectory | Purpose | Who Writes | Git Controlled |
|-------------|---------|-----------|----------------|
| knowledge/ | Domain context for hotel diagnosis | Developers, AI | YES |
| memory/ | Session state, error catalog | Agent runtime | PARTIAL |
| memory/current_state.json | Last URL + timestamp | Agent runtime | NO (gitignored) |
| memory/sessions/ | Active session logs | Agent runtime | NO (gitignored) |
| memory/archives/ | Consolidated old sessions | Maintenance scripts | NO (gitignored) |
| shadow_logs/ | Pricing comparison logs (legacy vs new) | Agent runtime | NO (gitignored) |
| patterns/ | Doc sync conventions | Developers | YES |
| workflows/ | Symlink -> .agents/workflows | -- | NO (symlink) |

### .agents/workflows/ (plural) = AGENT INSTRUCTIONS
| File Pattern | Purpose | Who Updates | Git Controlled |
|-------------|---------|------------|----------------|
| README.md | Skill index with triggers | Developers | YES |
| *_guardian.md | Protector workflows | Developers | YES |
| v4_*.md | v4 diagnostic workflows | Developers | YES |
| *.py | Validation scripts | Developers | YES |
| templates/ | Prompt templates | Developers | YES |

## Rules for ANY Agent

### When you need to READ instructions:
- Skills are in .agents/workflows/
- The symlink .agent/workflows is a direct alias -- use it interchangeably
- README.md lists ALL available skills with trigger phrases
- DO NOT create new .md files directly -- use meta_skill_creator.md

### When you need to WRITE state or persist data:
- Active sessions: .agent/memory/sessions/<session_id>.json
- Shadow pricing logs: .agent/shadow_logs/<timestamp>_<hash>.json
- Current task: .agent/memory/current_state.json
- NEVER write state to .agents/workflows/

### When SYSTEM_STATUS.md is stale:
Regenerate by running:
```
python scripts/validate_agent_ecosystem.py
```

## Validation

Run the ecosystem validator to check everything is healthy:
```
python scripts/validate_agent_ecosystem.py
```

Checks performed:
1. Symlink integrity (.agent/workflows -> .agents/workflows)
2. README.md has no dead references
3. All workflow files are tracked in README.md
4. Shadow logs are valid JSON (sample check)
5. Memory structure integrity (current_state.json, error_catalog, etc.)
6. Gitignore covers runtime data directories
7. Knowledge base exists (DOMAIN_PRIMER.md)
8. Agents directory has expected content

Also run the context integrity validator (cross-references with AGENTS.md):
```
python scripts/validate_context_integrity.py
```

## Common Pitfalls

1. **Symlink broken**: If .agent/workflows is missing, recreate:
   ```
   ln -sfn ../.agents/workflows .agent/workflows
   ```
   Run from .agent/ directory.

2. **Dead README refs**: If you delete a skill file, ALWAYS update .agents/workflows/README.md.
   Run validate_agent_ecosystem.py to catch orphans.

3. **Git leaks**: Never commit memory/sessions/, shadow_logs/, or current_state.json.
   They are in .gitignore but an agent might bypass.

4. **Version mismatch**: SYSTEM_STATUS.md version in .agent/ may lag VERSION.yaml in project
   root. Always trust VERSION.yaml as the source of truth.

## Migration Guide (if unifying becomes necessary)

If these directories need to merge in the future:
1. Move all .agent/data files to .agents/workflows/data/
2. Preserve the knowledge/ and memory/ subdirectories
3. Convert shadow_logs/ to append-only JSONL format
4. Update all absolute paths to relative
5. NEVER merge with version-controlled instruction files
