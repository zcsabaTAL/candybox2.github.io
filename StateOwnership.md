# Candy Box 3 state ownership baseline

Date: 2026-09-12

This document records the current authoritative owner of durable gameplay state before any Candy Box 3 domain takes ownership. Counts are a reproducible snapshot of `code/main`, not permanent constants.

## Ownership matrix

| Domain | Current authoritative owner | Persistence shape | New architecture status | Migration complexity |
| --- | --- | --- | --- | --- |
| Candies and other resources | The `Game` resource objects, especially `Candies`, backed by registered `Saving` numbers | Coherent objects with `Current`, `Max`, and `Accumulated` numeric keys | Legacy-authoritative facade. One flagged `eatAll` writer is routed through `CandySystem` | Medium for complete writer routing |
| Inventory ownership | `Game.gridItems` and item instances, backed by one bool per item | Flat keys such as `gridItemPossessed*` and `eqItem*` | Legacy-only | Medium to high |
| Equipped items | `Game.selectedEqItems`, reconstructed from `Saving` strings | Separate strings such as `gameWeaponSelected` | Legacy-only | Medium |
| Navigation and visible place | The current `Game.place` plus the transient `Game.savedPlace` return target | Mostly runtime object state, with unlock facts in flat `Saving` keys | Legacy-only | Medium |
| Quest and encounter progress | Scattered `Saving` facts interpreted by newly constructed `Place` and `Quest` instances | Ad hoc bool and number keys across quest and location files | Legacy-only | High |
| Unlocks and progression | `Saving` registry | Flat booleans such as `statusBarUnlocked*`, `mainMapDone*`, and location-specific flags | Legacy-only | High |
| UI, music, voice, and diagnostics | Presentation state in DOM and bridge instances. Volume and mute are device preferences in `localStorage` | Not authoritative for gameplay | Legacy presentation only | Low while read-only |

## Required invariants

- Every state slice has exactly one writable owner.
- New code may initially wrap the legacy owner, but may not maintain a parallel writable copy.
- UI, audio, content definitions, and diagnostics may observe state but may not mutate migrated domains directly.
- `Place` and `Quest` instances are not durable encounter owners. Navigation recreates them.
- There is no standalone equipment store. Ownership booleans and selected-slot strings are distinct legacy mechanisms.
- Ownership can move only after every writer for that domain is inventoried and routed through its facade.

## Runtime scopes

- Game-scoped: `Game`, `GameServices`, `DomainEventBus`, `UIBridge`, and future objects holding the current game or service references. These are disposed or rebound on every `Main.start()`.
- Page-scoped: `MusicBridge`, `PlaceAmbience`, and `WorldObjectLayer` while they do not retain a replaceable `Game` reference.
- Transient: commands, event payloads, and short-lived interaction handlers.

`Main` owns the sole current `GameServices` reference and exposes it through read-only `Main.getServices()`. There is no writable global `GameServices.current` singleton.

## Current call-site snapshot

| Measure | Current count | Meaning |
| --- | ---: | --- |
| Files directly using typed `Saving` registration, reads, or writes | 67 | Overall coupling surface |
| Direct `Saving.load*` calls | 330 | Flat-state reads |
| Direct `Saving.save*` calls | 248 | Flat-state writes, including internal save implementation |
| Direct `Saving.register*` calls | 163 | Explicit registrations. Item constructors also register dynamic item keys |
| Direct `getCandies().add(...)` calls | 20 | Candy mutation sites outside the resource implementation |
| Direct `getCandies().transferTo(...)` calls | 7 | Six always-legacy transfers plus the retained rollback branch for the flagged Candy Box `eatAll` pilot |
| Files containing either direct candy mutation form | 12 | Minimum candy writer migration surface |
| Files containing navigation construction or `goTo*` calls | 41 | Navigation coupling surface |
| Quest and encounter files directly using `Saving` | 14 | Minimum reverse-engineering surface for quest progress |

The 248 write count intentionally includes `Saving.ts` because it measures textual coupling. When estimating application-level writer migration, report both the total and the count excluding persistence infrastructure.

## Key families

- Resources: `gameCandies*`, `gameLollipops*`, `gameChocolateBars*`, `gamePainsAuChocolat*`, and cauldron resource keys.
- Inventory ownership: `gridItemPossessed*` plus item-specific `eqItem*` booleans.
- Equipment selection: `gameWeaponSelected`, `gameHatSelected`, `gameBodyArmourSelected`, `gameGlovesSelected`, `gameBootsSelected`.
- Navigation and unlocks: `statusBarUnlocked*`, `mainMapDone*`, `gridItemPossessedMainMap`.
- Forge pilot: `forgeBought*`, `forgeFoundLollipop`, corresponding `eqItem*` ownership keys, resource numbers.
- Quest and encounter state: `quest*`, location-specific completion keys, and pattern keys such as `TheCavePattern_*`.

## Reproduce the snapshot

Run these searches from the repository root:

```text
rg -l 'Saving\.(load|save|register)(Bool|Number|String)' code/main --glob '*.ts'
rg -o 'Saving\.load(Bool|Number|String)' code/main --glob '*.ts'
rg -o 'Saving\.save(Bool|Number|String)' code/main --glob '*.ts'
rg -o 'Saving\.register(Bool|Number|String)' code/main --glob '*.ts'
rg -o 'getCandies\(\)\.add\(' code/main --glob '*.ts'
rg -o 'getCandies\(\)\.transferTo\(' code/main --glob '*.ts'
rg -l '(setPlace\(new|goTo[A-Z])' code/main --glob '*.ts'
```

Refresh this document before selecting each new migration domain. For encounter work, add a semantic key map and a lossless round-trip test before implementing a repository adapter.
