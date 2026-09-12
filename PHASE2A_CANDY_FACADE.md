# Phase 2A: passive candy facade

## Scope and ownership

The legacy `Candies` and `CandiesEaten` resource objects remain the only authoritative state. `LegacyCandyRepository` delegates to their existing `add()` and `transferTo()` primitives. Phase 2A does not route any of the 27 legacy candy mutation call sites through `CandySystem`, add a feature flag, or create a second saved candy representation.

`GameServices` owns the game-scoped facade and disposes components in this order: `CandySystem`, `LegacyCandyRepository`, `DomainEventBus`, then its `Game` reference.

## Public contract

`CandyRepository` exposes `getBalance()`, `grant(amount)`, `spend(amount)`, and `eatAll()`. The amount-less `eatAll()` deliberately preserves the legacy intent and delegates to `candies.transferTo(candiesEaten)`.

`CandySystem` exposes:

```text
getBalance()
grant(amount, reason, transactionId)
spend(amount, reason, transactionId)
eatAll(transactionId)
```

Successful commands publish exactly one event after the authoritative mutation. Events are `candy.granted`, `candy.spent`, and `candy.eaten`. The event payload contains the transaction ID, resolved amount, previous balance, and new balance. Grant and spend events also contain the reason.

An empty-balance `eatAll()` returns `NO_CANDIES_TO_EAT`. It does not mutate state, publish an event, or reserve the transaction ID.

## Idempotency

Successful commands are recorded in a game-scoped in-memory transaction registry using the transaction ID and a fingerprint of operation, amount, and reason.

- Same transaction ID and same payload: successful replay with `replayed: true`, without mutation or event publication.
- Same transaction ID and different payload: `TRANSACTION_ID_CONFLICT`.
- Failed command: the transaction ID is not recorded and can be retried after state changes.
- Reload or a new `Game` instance clears the registry. Durable purchase flows must not migrate to this facade until persistent transaction handling is designed.

## Error codes

- `INVALID_AMOUNT`
- `INVALID_REASON`
- `INVALID_TRANSACTION_ID`
- `NOT_ENOUGH_CANDIES`
- `NO_CANDIES_TO_EAT`
- `TRANSACTION_ID_CONFLICT`
- `RUNTIME_DISPOSED`

`DUPLICATE_TRANSACTION` is not part of the contract.

## Rollout boundary

Feature flag plumbing belongs to Phase 2B. Phase 2A is passive and has no URL, `sessionStorage`, `localStorage`, or save-slot flag. Production and development gameplay therefore continue to use the same legacy call sites after this phase.
