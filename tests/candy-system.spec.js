"use strict";

var test = require("@playwright/test").test;
var expect = require("@playwright/test").expect;

async function startGame(page) {
    await page.goto("/");
    await page.locator("#sg-btn-new").click();
    await expect(page.locator("body")).toHaveAttribute("data-place", "CandyBox");
}

test("candy facade mutates the authoritative legacy resources and emits events", async function({ page }) {
    await startGame(page);

    var result = await page.evaluate(function() {
        var services = Main.getServices();
        var delivered = [];
        services.events.subscribe(function(event) { delivered.push(event); });

        var grant = services.candies.grant(400, "test-reward", "grant-1");
        var spend = services.candies.spend(150, "test-cost", "spend-1");
        var beforeEat = services.candies.getBalance();
        var eat = services.candies.eatAll("eat-1");

        return {
            grant: grant,
            spend: spend,
            eat: eat,
            beforeEat: beforeEat,
            balance: services.candies.getBalance(),
            legacyBalance: services["game"].getCandies().getCurrent(),
            eaten: services["game"].getCandiesEaten().getCurrent(),
            delivered: delivered
        };
    });

    expect(result.grant.ok).toBe(true);
    expect(result.spend.ok).toBe(true);
    expect(result.eat.ok).toBe(true);
    expect(result.eat.events[0].payload.amount).toBe(result.beforeEat);
    expect(result.balance).toBe(0);
    expect(result.legacyBalance).toBe(0);
    expect(result.eaten).toBe(result.beforeEat);
    expect(result.delivered.map(function(event) { return event.type; })).toEqual([
        "candy.granted", "candy.spent", "candy.eaten"
    ]);
});

test("candy facade validates its complete error contract", async function({ page }) {
    await startGame(page);

    var result = await page.evaluate(function() {
        var candy = Main.getServices().candies;
        return {
            zero: candy.grant(0, "reason", "zero"),
            fraction: candy.spend(1.5, "reason", "fraction"),
            reason: candy.grant(1, "   ", "reason"),
            transaction: candy.grant(1, "reason", "   "),
            insufficient: candy.spend(1, "reason", "insufficient"),
            emptyEat: candy.eatAll("empty-eat")
        };
    });

    expect(result.zero.errorCode).toBe("INVALID_AMOUNT");
    expect(result.fraction.errorCode).toBe("INVALID_AMOUNT");
    expect(result.reason.errorCode).toBe("INVALID_REASON");
    expect(result.transaction.errorCode).toBe("INVALID_TRANSACTION_ID");
    expect(result.insufficient.errorCode).toBe("NOT_ENOUGH_CANDIES");
    expect(result.emptyEat.errorCode).toBe("NO_CANDIES_TO_EAT");
});

test("candy facade replays matching commands and rejects conflicting payloads", async function({ page }) {
    await startGame(page);

    var result = await page.evaluate(function() {
        var services = Main.getServices();
        var deliveries = 0;
        services.events.subscribe(function() { deliveries++; });

        var first = services.candies.grant(10, "reward", "same-id");
        var replay = services.candies.grant(10, "reward", "same-id");
        var conflict = services.candies.grant(11, "reward", "same-id");

        return {
            first: first,
            replay: replay,
            conflict: conflict,
            balance: services.candies.getBalance(),
            deliveries: deliveries
        };
    });

    expect(result.first.ok).toBe(true);
    expect(result.replay).toEqual({ ok: true, replayed: true });
    expect(result.conflict.errorCode).toBe("TRANSACTION_ID_CONFLICT");
    expect(result.balance).toBe(10);
    expect(result.deliveries).toBe(1);
});

test("failed commands do not reserve their transaction IDs", async function({ page }) {
    await startGame(page);

    var result = await page.evaluate(function() {
        var candy = Main.getServices().candies;
        var failedSpend = candy.spend(5, "cost", "retry-id");
        candy.grant(5, "setup", "setup-id");
        var retriedSpend = candy.spend(5, "cost", "retry-id");
        var failedEat = candy.eatAll("eat-retry-id");
        candy.grant(3, "setup", "setup-id-2");
        var retriedEat = candy.eatAll("eat-retry-id");

        return {
            failedSpend: failedSpend,
            retriedSpend: retriedSpend,
            failedEat: failedEat,
            retriedEat: retriedEat
        };
    });

    expect(result.failedSpend.errorCode).toBe("NOT_ENOUGH_CANDIES");
    expect(result.retriedSpend.ok).toBe(true);
    expect(result.failedEat.errorCode).toBe("NO_CANDIES_TO_EAT");
    expect(result.retriedEat.ok).toBe(true);
});

test("disposed candy services cannot mutate old or replacement games", async function({ page }) {
    await startGame(page);

    var result = await page.evaluate(function() {
        var firstServices = Main.getServices();
        firstServices.candies.grant(7, "setup", "old-setup");
        var oldCandySystem = firstServices.candies;

        Main.bootGame(MainLoadingType.NONE, null);
        var secondServices = Main.getServices();
        var disposedResult = oldCandySystem.grant(100, "stale", "stale-id");

        return {
            oldDisposed: oldCandySystem.isDisposed(),
            disposedResult: disposedResult,
            secondBalance: secondServices.candies.getBalance()
        };
    });

    expect(result.oldDisposed).toBe(true);
    expect(result.disposedResult.errorCode).toBe("RUNTIME_DISPOSED");
    expect(result.secondBalance).toBe(0);
});
