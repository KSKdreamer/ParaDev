# PIHC3 Localization Single-source Cleanup

Date: 2026-08-02

## Done

- Rechecked the live, tracked, and ignored PIHC3 authoring tree. It contains
  zero `_component`, `_asset_component`, `legacy`, or `inactive_modules`
  directories and zero component-shaped logical object ids.
- Renamed all seven MIO source bundles to readable Chinese suffixes while
  keeping their stable ids and byte-exact PDX/localization sources.
- Removed 134 redundant `COUNTRY_Cxx` YAML projections from the hidden shared
  localization module. The 67 country `main.loc` files now own all 1,250
  effective country localization cells. Where the later-loaded projection had
  diverged, its effective value was merged into the module before removal.
- Removed 1,476 redundant per-Focus YAML projections. All 738 Focus modules now
  own exactly one `main.loc`; the two previously localization-less apostrophe-id
  focuses received their English/Chinese text and Chinese folder titles.
- Kept 19 genuinely tree-wide Focus keys solely in their owning Focus
  collection instead of duplicating them in a node module.
- Renamed the remaining hidden override boundary to
  `LOCALIZATION_REPLACEMENTS - 全局本地化覆盖`.
- Moved all 2,706 State-name cells into the 902 State modules, renamed every
  State folder to `numeric id - Chinese name`, and made the project-local State
  Entity aggregate the same three game-facing `state_names` files.
- Moved all 2,730 victory-point cells into the 898 State modules whose PDX
  definitions uniquely own those provinces. The same State Entity emits the
  three aggregate `victory_points` files for full and module-partial builds.
- Replaced 330 duplicated English Strategic Region folder identities with
  `numeric id - Chinese name`, moved all 990 real region-name cells into those
  modules, and removed 1,716 orphan `STRATEGICREGION_331`–`902` self-name
  placeholders that had no corresponding region.
- Moved the two shared Doctrine reward YAML files into
  `doctrine/PIHC_DOCTRINE_SUPPORT - 教义共享支持`; the project-local Doctrine
  Entity now declares and emits those resources for full, family-partial, and
  module-partial publication.
- Removed the Russian `EVENT_C01_MAIN_25` YAML mirror after verifying all three
  cells were exactly equal to the Russian section already owned by
  `event/C01_MAIN - 满意度调查/main.loc`.
- The hidden override module now has exactly 141 files, all below
  `localisation/replace`; it contains no ordinary Entity localization.
- Extended the generic ParaDev localization YAML parser and guarded editor to
  accept valid Clausewitz localization keys containing apostrophes, such as
  `FOCUS_C12_HOLDER'S_BOULDER_PARADE`.

## Verification

- Focused source-ownership, extension, and template regressions: 38 passed.
- MIO consolidation and preferred-language folder gates pass.
- Focus family publication: 738 modules, 28 collections, 10,803 artifacts,
  zero diagnostics/errors.
- Apostrophe-id Focus module publication expands safely to its owning tree:
  129 modules, one collection, 9,557 artifacts, zero diagnostics/errors.
- Clean/full and cached/full publication: 14,574 active modules, 106
  collections, 33,438 artifacts, zero diagnostics/errors, not blocked.
- State family publication: 902 modules, 10,200 safely scoped artifacts, zero
  diagnostics/errors. A single-State publication keeps one module plus the
  complete aggregate localization closure: 9,299 artifacts, zero errors.
- Strategic Region family publication: 330 modules, 9,628 safely scoped
  artifacts, zero diagnostics/errors. A single-region publication keeps one
  module plus the complete aggregate localization closure: 9,299 artifacts,
  zero errors.
- No-write SDK scaffold plans produce `999 - Friendship Province` and
  `331 - Friendship Skies` with ids and localization keys derived from the
  folder id; neither template asks users to repeat `state_id` or `region_id`.
- The deliberate 1,611-artifact reduction is exactly the removed 134 country,
  1,476 Focus, and one Event duplicate outputs; logical module and collection
  counts are unchanged.
- Full Doctrine and source-layout regression files: 19 passed. The targeted
  Doctrine slot/partial-build and hidden override-boundary checks also passed.
- Actual targeted publication is green: Doctrine family 52 modules / 9,357
  artifacts, Doctrine support module 1 / 9,306, and Event `C01_MAIN` module
  1 / 9,362; all report zero diagnostics and zero errors.
- The published output contains both Doctrine reward files, contains the
  canonical Russian `C01_MAIN_l_russian.yml`, and no longer contains the
  redundant standalone `EVENT_C01_MAIN_25_l_russian.yml`.

## Remaining Explicit-override Work

- The 141 remaining files deliberately use HoI4's
  `localisation/replace` precedence. They stay behind one hidden advanced
  boundary until a semantic Entity can preserve the same override behavior.
- No file should be distributed merely to reduce this number: ownership moves
  require exact runtime precedence and partial-publication parity.
