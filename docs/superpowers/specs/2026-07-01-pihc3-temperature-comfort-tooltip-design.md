# PIHC3 Temperature Comfort Tooltip Design

Status: approved

Date: 2026-07-01

## Goal

Improve the PIHC3 state temperature system so the selected-state GUI tooltip explains current state temperatures, state comfort, national comfort, and the active temperature modifier effects while national modifiers are based on population-weighted comfort rather than averaged class ids.

## Requirements

- Keep the existing monthly outdoor and indoor temperature formulas, including terrain influence, controller temperature influence, global threat, and controller tension.
- Keep the existing selected-state temperature GUI and preserve current hit-area edits that make the needle/base hoverable.
- Replace national averaged class logic with population-weighted comfort score logic.
- Cache tooltip and modifier inputs in state/country variables during the monthly update; tooltip localization must not redo score math.
- Map indoor class to comfort score as follows: class 1 = 1.0, class 2 = 3.0, class 3 = 7.0, class 4 = 9.0, class 5 = 10.0, class 6 = 9.0, class 7 = 1.0.
- Compute each state's population share against its controller's controlled-state population.
- Compute national comfort as `sum(state_population_k * state_comfort_score) / sum(state_population_k)`, falling back to `10.0` when controlled population is zero.
- Retier national modifier effects by national comfort thresholds `2.5`, `4.0`, `6.0`, and `7.5`.
- Add `production_speed_buildings_factor` to the national dynamic modifier and `state_production_speed_buildings_factor` to the state dynamic modifier.
- Add the national modifier effects to the hover tooltip after the national comfort score.
- Color state names, numeric values, and default dynamic values yellow. Color below-zero class names blue-ish and non-negative class names orange-ish.

## Architecture

The runtime remains in `scripted_effect/PIHC_STATE_TEMPERATURE`. `PIHC_update_state_indoor_temperature_frame` continues to assign class/frame ids, but it also caches state comfort score and comfort percent. `PIHC_update_average_temperature_buff` is renamed semantically through variables, while the effect id can stay stable for integration compatibility; it now sums state comfort scores by population and writes country-level comfort and modifier effect variables.

The tooltip text lives in the temperature modifier localization module and uses a new PIHC3 scripted-localisation component for class names and active national effect rows. This keeps the `.gui` file focused on hover hit areas and avoids duplicating gameplay formulas inside localization.

## Tooltip Content

The needle/base hover tooltip should display:

```text
<state name> 地块当前：
室外温度为：XX.X °C
室内温度为：XX.X °C
室内温度等级：<colored level name>
舒适度分数：XX.X / 10.0 (XX.X %)
-----
全国温度舒适度：XX.X / 10.0
<national modifier effects>
```

English localization should carry the same data with equivalent labels.

## Modifier Tiers

National modifier effects use these comfort tiers:

| National comfort | monthly_population | winter_attrition_factor | acclimatization_cold_climate_gain_factor | production_speed_buildings_factor |
| --- | ---: | ---: | ---: | ---: |
| `<= 2.5` | `-0.40` | `0.20` | `0.30` | `-0.20` |
| `<= 4.0` | `-0.30` | `0.15` | `0.20` | `-0.15` |
| `<= 6.0` | `-0.20` | `0.10` | `0.10` | `-0.10` |
| `<= 7.5` | `-0.05` | `0.05` | `0.05` | `-0.05` |
| `> 7.5` | `0.15` | `-0.10` | `0.00` | `0.00` |

State modifier effects continue to follow the existing state temperature class tiers for supply and manpower. Add a state building-speed penalty to those tiers:

| Class band | state_production_speed_buildings_factor |
| --- | ---: |
| `<= 1` | `-0.30` |
| `<= 2` | `-0.20` |
| `<= 3` | `-0.15` |
| `<= 4` | `-0.05` |
| `<= 5` | `0.00` |
| `<= 6` | `-0.05` |
| `> 6` | `-0.10` |

## Testing

Add focused assertions to `tests/test_pihc3_migration_contracts.py` for the score mapping, cached variables, national thresholds, added dynamic modifier fields, scripted-localisation module, and detailed GUI tooltip localization. Run the targeted state-temperature tests and the generated terrain-var check after implementation.
