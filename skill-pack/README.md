# Personal AI Workspace Skill Pack build tools

Local deterministic tools for validating, building, scanning, and packaging the public Phase 1 skills. These scripts never call personal cloud services and never mutate a live Workspace.

## Development

```bash
python -m pip install -e '.[dev]'
python -m pytest
```

## Stable commands

```bash
python skill-pack/scripts/build_skill_pack.py --source skills/personal-ai-workspace-installer-upgrader --version 0.1.0-beta.1
python skill-pack/scripts/validate_skill_pack.py skill-pack/build/personal-ai-workspace-installer-upgrader
python skill-pack/scripts/scan_private_identifiers.py .
python skill-pack/scripts/package_skill_pack.py skill-pack/build/personal-ai-workspace-installer-upgrader
```

The repository-root scan covers every regular UTF-8 public source and configuration
file, including extensionless files and unfamiliar text suffixes. It excludes only
private Git internals, generated environments/caches, and the implementation-governance
records under `.superpowers/` and `docs/superpowers/`, which intentionally quote
restricted identifiers while defining the public/private boundary. Unknown files that
are neither UTF-8 text nor a declared binary asset format fail the scan.
