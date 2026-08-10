# PIHC3 Army Headquarters Compatibility Progress

Date: 2026-07-19 01:27

## Done

- Refreshed the local HOI4 source baseline to Operation Postern 1.19.2 and reviewed
  Paradox's 1.19 Army HQ release notes plus the current official-wiki search surface.
- Found that PIHC3 replaces both `history/general` and `common/units`, hiding the new
  vanilla default HQ template and its required base subunits.
- Added a PIHC-country generic Army HQ template and PIHC-equipment-compatible
  `hq_support_company`/`hq_infantry` definitions.
- Extended the startup checker and added focused regression tests for source and
  compiled output.
- Emitted the current PIHC3 mod to the configured HOI4 mod directory.

## Verification

- Full build plan and emitted build: 18,040 modules, 78 collections, 37,591 artifacts,
  0 diagnostics, 0 errors.
- `rtk uv run pytest tests/test_pihc3_army_hq_contract.py -q`: 3 passed.
- `check_startup_error_contracts.py` passed against both source and the compiled PIHC3
  output.
- Build manifests assign `common/units/hq_support.txt` and
  `history/general/taog_hq_template.txt` to the new native modules.

## Risks Or Blockers

- The ordinary compile wrapper still encounters an unrelated persisted HeavenBase
  database-dialect config error. This build used an isolated temporary HeavenBase
  config without altering the user's stored configuration.
- The current slice restores the deployable default HQ. Specialized HQ companies and
  alternate motorized/armored HQ templates still need explicit PIHC technology and
  equipment design before they should be enabled.

## Next

- Play-test a 1936 PIHC country with *Thunder at Our Gates*: assign a general, deploy
  the default HQ, and confirm requisition, proximity, and undeploy behavior in-game.
