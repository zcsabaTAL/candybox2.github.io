# Candy Box 3 architecture freeze

Further legacy architecture work currently provides less product learning than a playable 2D prototype built with AI agents. Resume CB3 only if the prototype exposes a concrete problem that must be solved in CB2 or CB3, or Zoli explicitly decides to continue legacy migration.

Freeze date: 2026-09-16

Freeze commit: `a6af504` (`Add Desert Fortress and The Hole music with place headers`)

## Authoritative records

This file is the entry point for the frozen CB3 work. It does not duplicate the detailed contracts already recorded in:

- [`PHASE0_BASELINE.md`](PHASE0_BASELINE.md): canonical builds, build profiles, smoke tests, CI gate, fixtures, and baseline limitations.
- [`PHASE2A_CANDY_FACADE.md`](PHASE2A_CANDY_FACADE.md): candy facade ownership, command and event contracts, transaction replay rules, errors, and lifecycle scope.
- [`PHASE2B_CANDY_ROLLOUT.md`](PHASE2B_CANDY_ROLLOUT.md): typed feature-flag resolution, production behavior, the Candy Box `eatAll` pilot, and rollback.
- [`StateOwnership.md`](StateOwnership.md): authoritative owners, persistence shapes, runtime scopes, key families, writer inventory, and reproduction searches.

Completed foundation: Phase 0 established reproducible development and production builds plus CI. Phase 1 added game-scoped services, events, command results, disposal contracts, and dispose-before-replace handling. Phase 2A added the passive legacy-authoritative candy facade. Phase 2B added the disabled-by-default rollout flag and routed only the Candy Box `eatAll` pilot when explicitly enabled in development.

The legacy `Candies` and `CandiesEaten` objects remain authoritative. Production uses the generated feature-flag default, currently `false`, and ignores URL and `sessionStorage` overrides. Successful candy transaction fingerprints are game-scoped and in memory only. `Main.start()` must dispose the old game-scoped services before binding replacements to the new `Game` instance.

## Canonical commands and CI

```text
npm ci
npm run generate
npm run build:dev
npm run build:prod
npm run test:smoke
```

For a profile-specific browser run:

```text
npm run test:smoke:dev
npm run test:smoke:prod
```

`.github/workflows/test.yml` runs the development and production browser suite on pull requests and manual dispatch. `.github/workflows/deploy.yml` runs the same test gate on `master`; the production build and GitHub Pages deployment depend on that gate passing.

Relevant browser coverage is in `tests/smoke.spec.js`, `tests/candy-system.spec.js`, `tests/feature-flags.spec.js`, and `tests/candy-rollout.spec.js`. Declarative legacy saves are in `tests/fixtures/legacy-save-fixtures.js`.

## Known limitations at freeze

- Twenty-seven legacy candy mutation sites remain unchanged except for the single flagged Candy Box `eatAll` pilot.
- Candy transaction replay protection is not durable across reloads or new `Game` instances.
- Production keeps the facade rollout flag disabled. Changing a production default requires a new build.
- Inventory, equipment, navigation, quest, encounter, and unlock state remain legacy-owned.
- Encounter progress is distributed across flat `Saving` keys and has no normalized, losslessly round-trippable model.
- The legacy compiler remains TypeScript 1.4.1. `compile.sh` is not the canonical build path.

## Approved but unimplemented Phase 2C decisions

Phase 2C is frozen and must not be started automatically. If explicitly resumed, its bounded pilot is the Forge wooden sword purchase.

- Route the purchase through a command service while the legacy candy, item ownership, purchase flag, inventory, UI refresh, voice, and saving behavior remain authoritative.
- Do not include `price` in the purchase command. Resolve it from one read-only catalog using `shopId` and `itemId`.
- Make candy spending, item granting, and the durable purchase fact atomic and idempotent. A reload must not duplicate the reward or charge.
- Design persistent transaction handling before using the Phase 2A in-memory transaction mechanism for purchases.
- Keep the existing legacy purchase path as the rollback route until parity and save-reload coverage pass.
- Do not make catalog-driven UI price text or localization templating a prerequisite for the purchase pilot.
- Do not move state ownership, introduce bidirectional synchronization, or generalize the pilot into a broader inventory or encounter migration.

## Restart checklist

1. Confirm that Zoli explicitly thawed CB3 or that the Phaser prototype exposed a concrete CB2 or CB3 problem.
2. Fetch the remote and verify the intended restart base against `a6af504` and all later legacy product commits.
3. Read this file and all four authoritative records above.
4. Run `git status --short` and preserve unrelated or generated local changes.
5. Run `npm ci`, both canonical builds, and `npm run test:smoke` before changing architecture.
6. Refresh the counts and ownership facts in `StateOwnership.md`.
7. Reconfirm the next playable capability and timebox. Prefer the Phaser prototype unless legacy architecture work is necessary to unlock it.
8. If Phase 2C is selected, implement only the Forge wooden sword purchase pilot and its bounded acceptance tests.
9. Keep CB2 saves backward compatible. Do not silently discard unknown or invalid progress.
10. Record the new baseline commit, verification results, ownership decision, rollback, and any changed contracts before continuing.
