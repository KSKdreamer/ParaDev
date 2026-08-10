## 1. Context: what HoI4 modding implies

HoI4 is a Paradox grand-strategy game where large parts of gameplay content are authored as structured text/data files rather than compiled game code. The public HoI4 wiki describes itself as a knowledge base for players and modders, and HoI4 modding commonly involves files under folders such as `common`, `events`, `localisation`, `gfx`, and `interface`. ([HOI4 Paradox Wiki][1])

The important point is that HoI4 content is **cross-cutting**. A single gameplay feature is rarely one file. For example, a national focus may need a PDX script definition, localisation keys, icon assets, GFX/interface declarations, rewards using effects, and references to events, ideas, modifiers, or decisions. National focuses also encode graph relationships such as prerequisites and mutual exclusivity. The wiki notes that prerequisites and mutual exclusivity can even reference focuses outside the same tree, which makes the dependency model non-local. ([HOI4 Paradox Wiki][2])

Likewise, decisions are split between decision definitions and decision-category definitions, events use localisation keys for title/description text, ideas apply modifiers such as national spirits/laws/designers, and effects are reused across focuses, events, decisions, and other contexts. ([HOI4 Paradox Wiki][3])

So the underlying problem is not simply “generate HoI4 text files.” It is: **how do we let creators author coherent gameplay features as modular source packages, then compile those packages into the scattered file structure required by the game?**

## 2. Product being considered

You are considering a system with three faces:

1. **Python package**
   A programmable SDK/compiler framework for mod content, suitable for scripting, CI, plugin development, validation, and advanced users.

2. **Desktop app**
   A user-facing editor/project manager for creators who want to browse modules, edit content, preview relationships, validate errors, and build/export a mod without writing much Python.

3. **MCP server**
   A machine-readable interface so AI tools or IDE agents can inspect the mod project, search content, explain dependencies, generate candidate content, run validations, and invoke compilation tasks.

The key is that all three should sit on the same underlying project model and compiler pipeline. The desktop app and MCP should not become separate product logic layers; they should be clients of the same core engine.

## 3. The core problem

The current HoI4 authoring model is file-oriented, but the desired authoring model is **feature-oriented**.

Instead of asking a developer to manually place related content across many output folders, you want each gameplay feature to live as a **module folder**. A module could represent a country, character, national focus, focus tree, decision category, decision, idea, event, modifier, scripted GUI, “superevent,” or any custom extension invented by the community.

Each module folder should contain:

* source assets, such as images, DDS files, GUI fragments, PDX script fragments, localisation, metadata, generated or hand-written snippets;
* module metadata, such as ID, tags, authoring type, supported game/version, dependencies, search labels, validation hints;
* enough semantic structure for the compiler to know what artifacts this module produces and what other modules/artifacts it depends on.

Compilation should transform those source modules into game-ready artifacts such as:

* PDX script files under `common/...`, `events/...`, `history/...`, etc.;
* localisation YAML;
* GFX/interface declarations;
* GUI files;
* DDS or converted image assets;
* descriptor/build metadata;
* possibly diagnostics, indexes, cache files, dependency graphs, and source maps.

## 4. Design goals

The first design goal is **modularity**. A creator should be able to reason about “the German monarchist focus branch” or “this decision category” or “this superevent” as a module, not as twenty disconnected entries in unrelated folders.

The second goal is **extensibility**. The system must not hard-code a closed list of module types. Built-in types like `country`, `focus_tree`, `focus`, `decision_category`, `decision`, `event`, `idea`, and `modifier` should use the same extension protocol that custom types use. A community plugin defining `superevent` should be able to add schemas, validators, compilers, asset processors, references, UI panels, search metadata, and output artifacts without forking the core.

The third goal is **composability**. Compilation cannot be a single “render file” function. Some outputs are built from many modules. A decision category contains many decisions. A focus tree contains a graph of focuses. A localisation file aggregates strings from many modules. A GFX file may aggregate sprite declarations from many icon-bearing modules. This suggests at least three compilation levels: artifact-level compilation, module-level compilation, and aggregate/combination-level compilation.

The fourth goal is **customizability**. A developer should be able to replace or wrap parts of the pipeline: custom validation, custom image conversion, custom naming policy, custom localisation emission, custom PDX formatting, custom artifact merger, custom conflict resolution, custom build profile.

The fifth goal is **minimal mental model**. Users should not need to understand every compiler layer. Ideally, the user-facing model is:

> A project contains modules.
> Modules declare sources and relationships.
> Build profiles compile modules into a game-ready mod.
> Plugins add new module types and compilers.

Advanced users can go deeper, but the default workflow should stay simple.

## 5. Non-goals

The system should not initially try to replace HoI4’s entire scripting language with a new programming language. It can offer typed/structured authoring helpers, but raw PDX script escape hatches are necessary because Paradox script is broad, evolving, and full of edge cases.

It should not try to become a full game-engine simulator. Validation is valuable, but perfectly predicting runtime behavior of every trigger, effect, AI weight, scope, localisation rule, GUI behavior, or DLC/version difference is too ambitious for the core architecture.

It should not make HoI4 the only possible game forever. HoI4 is the example and first backend, but the architecture should separate “generic mod-project compiler” concepts from “HoI4 backend” concepts.

It should not assume every module is independent. HoI4 content is naturally relational: focuses call events, events add ideas, decisions use modifiers, icons require GFX declarations, localisation keys are referenced from scripts, and focus-tree layout depends on graph relationships.

It should not force all creators into Python. Python should be the power-user and plugin interface, but ordinary users should be able to work through declarative files and the desktop app.

## 6. Key architectural tension

The central tension is between **local authoring** and **global output**.

A module should be self-contained from the author’s perspective:

```text
modules/
  focus/industrial_revival/
    module.yml
    focus.pdx
    loc/en.yml
    icon.png
```

But the game expects global, convention-heavy output:

```text
common/national_focus/my_country.txt
localisation/english/my_mod_l_english.yml
gfx/interface/goals/my_icon.dds
interface/my_mod_goals.gfx
```

That means the compiler must understand both:

* the **local semantic unit**: “this module is a focus with an icon, reward, localisation, prerequisites, tags”;
* the **global target layout**: “this focus belongs in a specific focus tree file, with aggregated localisation and GFX declarations.”

This is why the compiler probably cannot be only artifact-level or only module-level. It needs a layered model.

## 7. Examples of the compilation problem

A **single focus** module may produce or contribute to:

* one `focus = { ... }` block;
* localisation entries for name, description, completion tooltip;
* one icon asset converted to DDS;
* one GFX sprite declaration;
* dependency edges to prerequisite focuses;
* references to rewards such as ideas, events, decisions, or modifiers.

A **focus tree** module may not itself be “one file only.” It may aggregate many focus modules, validate graph layout, resolve `relative_position_id`, check duplicate IDs, check missing prerequisites, and emit a full `focus_tree = { ... }` artifact.

A **decision category** module may aggregate decisions from multiple folders. The category is a parent artifact, but the decisions may be authored independently.

An **event** module may have PDX script, localisation, event picture assets, options, triggers, and references from focuses or decisions. HoI4 event titles/descriptions are localisation-key based, so event compilation must coordinate script and localisation outputs. ([HOI4 Paradox Wiki][4])

An **idea** module may define a national spirit, law, designer, officer-corps spirit, or hidden idea, and may be referenced by focuses/events/decisions that add, remove, or modify it. Ideas are a static mechanism for applying modifiers to countries. ([HOI4 Paradox Wiki][5])

A **scripted GUI** or custom **superevent** module may be a plugin-defined composition of GUI, GFX, scripted triggers/effects, localisation, images, and events. The architecture must support this without requiring the core to know what a superevent is. HoI4 scripted GUIs are used to attach scripted behavior to custom UI elements, so they are inherently multi-artifact features. ([HOI4 Paradox Wiki][6])

## 8. What “protocol and interface between modules” needs to solve

The module protocol needs to answer these questions consistently:

1. **Identity**
   What is this module’s stable ID? What game object IDs does it claim? What namespace does it belong to?

2. **Type**
   Is this a built-in `focus`, `event`, `decision`, etc., or a plugin-provided type such as `superevent`?

3. **Sources**
   What files belong to this module? Which are declarative data, raw PDX script, localisation, images, GUI fragments, generated files, or opaque assets?

4. **Exports**
   What semantic objects does this module provide to other modules? Example: `idea:GER_industrial_revival`, `event:ger.12`, `focus:GER_rebuild_industry`.

5. **Imports/references**
   What does this module depend on or refer to? Example: a focus references an event ID, an idea ID, an icon, a prerequisite focus, or a localisation key.

6. **Artifacts**
   What output artifacts does this module produce directly, and which aggregate artifacts does it contribute to?

7. **Compilation hooks**
   Which compiler handles this module? Can it be replaced, extended, ordered, or composed with other compilers?

8. **Validation**
   What can be validated locally? What requires global project knowledge? What is an error, warning, hint, or style issue?

9. **Search/index metadata**
   How should the desktop app and MCP expose this module to users and agents? Tags, relationships, generated IDs, owning feature, source locations, build outputs, diagnostics.

10. **Source maps**
    When a generated HoI4 file has an error, how does the tool map it back to the original module folder/source file?

## 9. The success criterion

A successful architecture would let a user create a module like “Add a political reform decision category with ten decisions, two events, one idea, custom icons, and localisation” without manually tracking every output file.

A successful plugin system would let another developer define “superevent” as a new module type that compiles into events, GUI, GFX, scripted effects, sounds, localisation, and images, while still participating in the same dependency graph, validation engine, build cache, desktop UI, search index, and MCP tools.

A successful mental model would let a beginner say:

> “I added a module. I built the mod. The tool told me what is missing.”

And let an advanced developer say:

> “I replaced the focus-tree aggregator, added a custom validator, exposed new MCP tools, and registered a new artifact emitter.”

[1]: https://hoi4.paradoxwikis.com/Hearts_of_Iron_4_Wiki?utm_source=chatgpt.com "Hearts of Iron 4 Wiki - Paradox Wikis"
[2]: https://hoi4.paradoxwikis.com/National_focus_modding?utm_source=chatgpt.com "National focus modding - Hearts of Iron 4 Wiki"
[3]: https://hoi4.paradoxwikis.com/Decision_modding?utm_source=chatgpt.com "Decision modding - Hearts of Iron 4 Wiki"
[4]: https://hoi4.paradoxwikis.com/Event_modding?utm_source=chatgpt.com "Event modding - Hearts of Iron 4 Wiki"
[5]: https://hoi4.paradoxwikis.com/Idea_modding?utm_source=chatgpt.com "Idea modding - Hearts of Iron 4 Wiki"
[6]: https://hoi4.paradoxwikis.com/Scripted_GUI_modding?utm_source=chatgpt.com "Scripted GUI modding - Hearts of Iron 4 Wiki"
