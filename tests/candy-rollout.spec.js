"use strict";

var test = require("@playwright/test").test;
var expect = require("@playwright/test").expect;
var profile = process.env.CB_BUILD_PROFILE || "development";

async function startGame(page, path) {
    await page.goto(path);
    await page.locator("#sg-btn-new").click();
    await expect(page.locator("body")).toHaveAttribute("data-place", "CandyBox");
}

async function grantLegacyCandies(page, amount) {
    await page.evaluate(function(value) {
        Main.getServices()["game"].getCandies().add(value);
    }, amount);
}

test("keeps the legacy eat-all path when the Candy facade flag is disabled", async function({ page }) {
    await startGame(page, "/?cb3CandyFacade=0");
    await grantLegacyCandies(page, 17);

    await page.evaluate(function() {
        var events = [];
        Main.getServices().events.subscribe(function(event) {
            if(event.type == "candy.eaten") events.push(event);
        });
        window.candyRolloutEvents = events;
    });

    await page.locator(".candyBoxEatCandiesButton").first().click();

    var state = await page.evaluate(function() {
        var game = Main.getServices()["game"];
        return {
            candies: game.getCandies().getCurrent(),
            candiesEaten: game.getCandiesEaten().getCurrent()
        };
    });

    expect(state).toEqual({ candies: 0, candiesEaten: 17 });
    expect(await page.evaluate(function() { return window.candyRolloutEvents.length; })).toBe(0);
});

test("routes eat-all through the facade only when development override enables it", async function({ page }) {
    await startGame(page, "/?cb3CandyFacade=1");
    await grantLegacyCandies(page, 23);

    var result = await page.evaluate(function() {
        var events = [];
        Main.getServices().events.subscribe(function(event) {
            if(event.type == "candy.eaten") events.push(event);
        });
        window.candyRolloutEvents = events;
        return FeatureFlags.isCandyFacadeEnabled();
    });

    await page.locator(".candyBoxEatCandiesButton").first().click();

    var state = await page.evaluate(function() {
        var game = Main.getServices()["game"];
        return {
            candies: game.getCandies().getCurrent(),
            candiesEaten: game.getCandiesEaten().getCurrent(),
            events: window.candyRolloutEvents
        };
    });

    expect(result).toBe(profile === "development");
    expect(state.candies).toBe(0);
    expect(state.candiesEaten).toBe(23);
    expect(state.events).toHaveLength(profile === "development" ? 1 : 0);
    if(profile === "development") {
        expect(state.events[0].payload.amount).toBe(23);
        expect(state.events[0].payload.previousBalance).toBe(23);
        expect(state.events[0].payload.newBalance).toBe(0);
        expect(state.events[0].payload.transactionId).toMatch(/^candy-box:eat-all:\d+$/);
    }
});

test("uses unique eat-all transactions after Candy Box is reconstructed", async function({ page }) {
    test.skip(profile !== "development", "The facade override is development-only.");
    await startGame(page, "/?cb3CandyFacade=1");
    await grantLegacyCandies(page, 5);

    await page.evaluate(function() {
        var events = [];
        Main.getServices().events.subscribe(function(event) {
            if(event.type == "candy.eaten") events.push(event);
        });
        window.candyRolloutEvents = events;
    });
    await page.locator(".candyBoxEatCandiesButton").first().click();

    await grantLegacyCandies(page, 7);
    await page.evaluate(function() {
        Main.getServices()["game"].goToCandyBox();
    });
    await expect(page.locator("body")).toHaveAttribute("data-place", "CandyBox");
    await page.locator(".candyBoxEatCandiesButton").first().click();

    var state = await page.evaluate(function() {
        var game = Main.getServices()["game"];
        return {
            candies: game.getCandies().getCurrent(),
            candiesEaten: game.getCandiesEaten().getCurrent(),
            events: window.candyRolloutEvents
        };
    });

    expect(state.candies).toBe(0);
    expect(state.candiesEaten).toBe(12);
    expect(state.events).toHaveLength(2);
    expect(state.events[0].payload.transactionId).not.toBe(state.events[1].payload.transactionId);
});
