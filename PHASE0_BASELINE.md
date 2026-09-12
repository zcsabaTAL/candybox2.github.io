# Candy Box 3 migration, Phase 0 baseline

Date: 2026-09-12

Working branch: `codex/cb3-phase-0`

GitHub baseline revision: `43cf4fe7a10e498decceddbc0f0a6dad8421abe2`

## Scope

This phase establishes a reproducible safety baseline. It does not migrate gameplay state, change save keys, or redirect any legacy gameplay path.

## Verified repository facts

- The browser bundle is compiled with TypeScript 1.4.1.
- `compile.sh` depends on global `tsc`, `yuicompressor`, and `7za`, regenerates content, updates AppCache metadata, minifies output, and creates release archives.
- The practical development build compiles the TypeScript sources and prepends `candybox2_sourceCodeLicense.txt` to both JavaScript bundles.
- `candybox2.js`, `candybox2_uncompressed.js`, `code/gen`, and `node_modules` are ignored build artifacts.
- There is currently no backend or server-authoritative game state. Saves remain in browser storage.
- No gameplay ownership changes are part of this baseline.

## Canonical commands

```text
npm run generate
npm run build:dev
npm run build:prod
```

Both build commands regenerate the legacy ASCII and text TypeScript sources, then compile the same legacy game. Their only intentional difference at this stage is the generated `BuildConfig.environment` value. Every CB3 feature flag remains disabled in both profiles.

## Safety invariants

- Legacy `Game`, `Saving`, navigation, candy, inventory, quest, and encounter behavior remain authoritative.
- Existing save slots are not rewritten or migrated.
- Generated bundles must not be staged blindly.
- A failed build must return a non-zero exit code and must not leave a temporary bundle behind after a successful build.
- Missing or unknown future feature flags must resolve to disabled behavior.

## Baseline verification still required on the development machine

- Start the existing local server on port 8080.
- Run both canonical builds.
- Confirm that a new game starts.
- Confirm that an existing slot loads without modification.
- Confirm CandyBox, MainMap, Village, and Forge navigation.
- Confirm the existing wooden sword purchase, save, reload, inventory, music, and dialogue behavior.
- Record representative save fixtures before any save-schema work.

## Automated smoke suite

The first browser automation slice uses pinned Playwright 1.63.0 and Chromium only. Run both build profiles with:

```text
npm run test:smoke
```

The suite verifies the empty-profile start modal, legacy new-game startup, preservation of pre-existing slot storage, and development versus production visibility of the DEV MODE control.

Verified on 2026-09-12:

- Node 26.5.0;
- TypeScript 1.4.1 development build passed;
- TypeScript 1.4.1 production build passed;
- Playwright 1.63.0 with Chromium;
- four development-profile smoke tests passed;
- four production-profile smoke tests passed.

## Preserved Drive changes

The Google Drive working copy contained source changes newer than the GitHub baseline. They were copied into the writable worktree before Phase 0 implementation and remain identifiable as pre-existing work in:

- `MusicBridge.ts`;
- `Quest.ts`;
- `QuestLog.ts`;
- `QuestLogMessage.ts`;
- `SorceressHut.ts`;
- `UIBridge.ts`;
- `VoiceBridge.ts`;
- portions of `index.html` unrelated to build-profile gating.

These preserved changes must not be attributed to the Phase 0 architecture work or discarded during review.

## Next bounded step

After both builds and the manual smoke baseline pass, add a Chromium-only Playwright spike for three or four stable paths. Do not change gameplay ownership in that spike.
