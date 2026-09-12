# Phase 2B: Candy facade rollout pilot

## Scope and ownership

The legacy `Candies` and `CandiesEaten` resource objects remain the only authoritative state. Phase 2B adds typed feature-flag resolution and routes only the Candy Box `eatAll` interaction through `CandySystem` when enabled. Every other candy mutation, including Forge purchases, remains on its legacy path.

## Feature flag contract

`BuildConfig.cb3CandyFacadeEnabled` is the production-safe build default and is initially `false` in both build profiles.

Development builds resolve `cb3CandyFacadeEnabled` in this order:

1. The last `cb3CandyFacade=1|0` URL parameter.
2. `sessionStorage["cb3CandyFacadeEnabled"]` with an exact value of `1` or `0`.
3. The generated build default.

An invalid URL value falls through to the session value. An invalid session value falls through to the build default. Production builds do not read URL or session overrides and use only the build default.

Developer flags are never written to `localStorage` or player save slots. An URL override does not update `sessionStorage`.

## Pilot integration

`CandyBox.clickedEatCandiesButton()` retains both branches in the same call site:

- Flag disabled or feature component unavailable: use the existing `candies.transferTo(candiesEaten)` operation.
- Flag enabled: call `Main.getServices().candies.eatAll(transactionId)`.

Facade failures do not fall through to a second legacy mutation. Successful commands continue to update the same authoritative legacy resources and emit one `candy.eaten` event.

Transaction IDs use a page-scoped static `CandyBox` counter. Navigation creates new `CandyBox` instances, so an instance counter would collide with the game-scoped `CandySystem` transaction registry. The static counter remains unique across those reconstructed places. It does not require a game-start reset because a new game also creates an empty transaction registry.

## Rollback

Keep `BuildConfig.cb3CandyFacadeEnabled` set to `false` in production. In development, remove overrides or set `cb3CandyFacade=0`. The legacy mutation branch remains present and no save migration or parallel candy representation exists.
