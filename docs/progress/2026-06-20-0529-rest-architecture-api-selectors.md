# REST Architecture API Selectors

- Exposed the architecture API table selector through `GET /architecture?api_table=true` while preserving the default architecture graph response.
- Added focused REST route, OpenAPI seed, and generated REST API table coverage for `symbol` and `index_name`/`key` selector projections.
- Regenerated `docs/user-manual/rest-api-reference.md` and updated `docs/architecture/interfaces.md` so SDK, CLI, and REST selector entry points are documented together.
- Verification scope stayed targeted to avoid competing with PIHC3 migration work.
