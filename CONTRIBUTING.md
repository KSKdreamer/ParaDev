# Contributing to ParaDev

Read [docs/README.md](docs/README.md) first for the docs map and authority boundaries.

## Setup

```bash
rtk bash scripts/sync-env.bash
rtk bash scripts/flake.bash --ci
rtk bash scripts/test.bash
```

## Pull Requests

Use the pull request template in `.github/pull_request_template.md`.

Before opening a pull request:

- Run `rtk bash scripts/sync-env.bash --check`
- Run `rtk bash scripts/flake.bash --ci`
- Run `rtk bash scripts/test.bash`
- Do not commit secrets, local `.venv` paths, or machine-specific overrides.

## Linear

- For continuous Linear issues, keep one rolling status comment per issue and edit that comment as work progresses.
- Add a new Linear comment only for a distinct decision, handoff, blocker, or user-requested update that should remain separate.
