# 2026-06-21 10:30 - PIHC3 Cache And Smoke Fixture

## Slice

- Removed generated Python bytecode from `projects/PIHC3/system/__pycache__/`.
- Rechecked current focus-preview migration coverage: 738 source focuses and 0 missing `focus_asset_component/.../preview.png` files.
- Updated `boot-progress-smoke.tsx` and `diagram-tab-smoke.tsx` to pass the current `AppShell` scoped browser loading props, keeping browser-only smoke fixtures aligned with the production shell contract.

## Verification

```bash
rtk uv run python - <<'PY'
from pathlib import Path
import yaml
root = Path('projects/PIHC3')
focus_tree_root = root/'src/modules/focus_tree'
asset_root = root/'src/modules/focus_asset_component'
missing = []
total = 0
for meta in focus_tree_root.glob('*/meta.yaml'):
    data = yaml.safe_load(meta.read_text(encoding='utf-8')) or {}
    settings = data.get('settings') if isinstance(data.get('settings'), dict) else data
    for row in settings.get('source_focuses') or []:
        if not isinstance(row, dict):
            continue
        fid = row.get('focus_id') or row.get('id') or row.get('object_id')
        if not isinstance(fid, str) or not fid:
            continue
        total += 1
        normalized = ''.join(ch if ch.isalnum() or ch == '_' else '_' for ch in fid)
        preview = asset_root/f'FOCUS_ASSET_COMPONENT_{normalized}'/'preview.png'
        if not preview.is_file():
            missing.append((meta.parent.name, fid, row.get('icon_path')))
print({'total': total, 'missing': len(missing)})
PY
rtk bash -lc 'find projects/PIHC3 -name "__pycache__" -o -name "*.pyc" -o -name ".DS_Store"'
rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'generated_cache_files or generated_runtime_directories or project_tree_has_no_generated_cache_files'
rtk curl -fsS http://127.0.0.1:5180/e2e/boot-progress-smoke.tsx -o /tmp/paradev-boot-progress-smoke.js
rtk curl -fsS http://127.0.0.1:5180/e2e/diagram-tab-smoke.tsx -o /tmp/paradev-diagram-tab-smoke.js
rtk npm --prefix apps/desktop run test:unit -- src/components/AppShell.test.tsx src/App.test.ts src/components/ProjectPanel.test.tsx src/styles/diagram.test.ts
rtk npm --prefix apps/desktop run build
rtk git diff --check -- apps/desktop/e2e/boot-progress-smoke.tsx apps/desktop/e2e/diagram-tab-smoke.tsx projects/PIHC3 tests/test_pihc3_migration_contracts.py
```

All commands passed. The Vite production build still reports the existing large-chunk warning.
