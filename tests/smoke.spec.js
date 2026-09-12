"use strict";

var test = require("@playwright/test").test;
var expect = require("@playwright/test").expect;
var legacySaveFixtures = require("./fixtures/legacy-save-fixtures");
var profile = process.env.CB_BUILD_PROFILE || "development";

async function materializeLegacySlot(page, fixture) {
    await page.goto("/");
    await page.locator("#sg-btn-new").click();
    await expect(page.locator("body")).toHaveAttribute("data-place", "CandyBox");

    await page.evaluate(function(saveFixture) {
        var key;
        for (key in saveFixture.bools) {
            Saving.saveBool(key, saveFixture.bools[key]);
        }
        for (key in saveFixture.numbers) {
            Saving.saveNumber(key, saveFixture.numbers[key]);
        }
        for (key in saveFixture.strings) {
            Saving.saveString(key, saveFixture.strings[key]);
        }
        LocalSaving.save(saveFixture.slotId);
    }, fixture);
}

test("shows the start modal for an empty browser profile", async function({ page }) {
    await page.goto("/");

    await expect(page.locator("#start-game-modal-overlay")).toBeVisible();
    await expect(page.locator("#sg-btn-new")).toContainText("ÚJ JÁTÉK KEZDÉSE");
});

test("starts a legacy new game without a page error", async function({ page }) {
    var pageErrors = [];
    page.on("pageerror", function(error) {
        pageErrors.push(error.message);
    });

    await page.goto("/");
    await page.locator("#sg-btn-new").click();

    await expect(page.locator("#start-game-modal-overlay")).toHaveCount(0);
    await expect(page.locator("body")).toHaveAttribute("data-place", "CandyBox");
    expect(pageErrors).toEqual([]);
});

test("does not erase existing slot data when starting a new game", async function({ page }) {
    await page.goto("/");
    await page.evaluate(function() {
        localStorage.setItem("slot3", "baseline-save-marker");
        localStorage.setItem("slot3.gameCandiesCurrent", "4000");
    });
    await page.reload();

    await expect(page.locator("#sg-btn-new")).toBeVisible();
    await page.locator("#sg-btn-new").click();

    var preserved = await page.evaluate(function() {
        return localStorage.getItem("slot3");
    });
    expect(preserved).toBe("baseline-save-marker");
});

test("gates the developer control by build profile", async function({ page }) {
    await page.goto("/");

    if (profile === "development") {
        await expect(page.locator("#dev-mode-btn")).toBeVisible();
    } else {
        await expect(page.locator("#dev-mode-btn")).toBeHidden();
    }
});

test("loads a legacy slot and preserves a Forge purchase through save and reload", async function({ page }) {
    var fixture = legacySaveFixtures.forgeWoodenSwordBefore;
    var pageErrors = [];
    page.on("pageerror", function(error) {
        pageErrors.push(error.message);
    });

    await materializeLegacySlot(page, fixture);
    await page.reload();
    await page.locator("#sg-btn-continue").click();

    await expect(page.locator("body")).toHaveAttribute("data-place", "CandyBox");
    await expect(page.locator("#ui-candies-count")).toContainText("4 000");
    expect(await page.evaluate(function() {
        return {
            runtime: Saving.loadBool("gridItemPossessedMainMap"),
            stored: localStorage.getItem("slot1.gridItemPossessedMainMap")
        };
    })).toEqual({ runtime: true, stored: "true" });

    await page.getByRole("button", { name: "MAP", exact: true }).click();
    await expect(page.locator("body")).toHaveAttribute("data-place", "Village");

    await page.locator(".villageBackToTheMapButton").first().click();
    await expect(page.locator("body")).toHaveAttribute("data-place", "MainMap");

    await page.locator(".mapVillageButton").first().click();
    await expect(page.locator("body")).toHaveAttribute("data-place", "Village");

    await page.locator(".mapVillageForgeButton").first().click();
    await expect(page.locator("body")).toHaveAttribute("data-place", "Forge");
    await page.locator(".mapVillageForgeBuyWoodenSwordButton").first().click();

    var purchaseState = await page.evaluate(function() {
        return {
            bought: Saving.loadBool("forgeBoughtWoodenSword"),
            ownsSword: Saving.loadBool("eqItemWeaponWoodenSword"),
            candies: document.getElementById("ui-candies-count").textContent
        };
    });
    expect(purchaseState.bought).toBe(true);
    expect(purchaseState.ownsSword).toBe(true);

    await page.getByRole("button", { name: "SAVE", exact: true }).click();
    await expect(page.locator("body")).toHaveAttribute("data-place", "Save");
    await page.locator(".saveLocalSaveSaveButton").first().click();

    var storedPurchase = await page.evaluate(function() {
        return {
            candies: localStorage.getItem("slot1.gameCandiesCurrent"),
            bought: localStorage.getItem("slot1.forgeBoughtWoodenSword"),
            ownsSword: localStorage.getItem("slot1.eqItemWeaponWoodenSword")
        };
    });
    expect(storedPurchase.bought).toBe("true");
    expect(storedPurchase.ownsSword).toBe("true");
    await page.reload();
    await page.locator("#sg-btn-continue").click();
    await expect(page.locator("body")).toHaveAttribute("data-place", "CandyBox");

    var reloadedState = await page.evaluate(function() {
        return {
            bought: Saving.loadBool("forgeBoughtWoodenSword"),
            ownsSword: Saving.loadBool("eqItemWeaponWoodenSword"),
            candies: Saving.loadNumber("gameCandiesCurrent"),
            hasCb3Payload: localStorage.getItem("slot1.cb3StateJson") !== null
        };
    });
    expect(reloadedState.bought).toBe(true);
    expect(reloadedState.ownsSword).toBe(true);
    expect(reloadedState.candies.toString()).toBe(storedPurchase.candies);
    expect(reloadedState.hasCb3Payload).toBe(false);
    expect(pageErrors).toEqual([]);
});

test("replaces and disposes game-scoped services on a second game start", async function({ page }) {
    await page.goto("/");
    await page.locator("#sg-btn-new").click();
    await expect(page.locator("body")).toHaveAttribute("data-place", "CandyBox");

    var lifecycle = await page.evaluate(function() {
        var firstServices = Main.getServices();
        var oldBusDeliveries = 0;
        var newBusDeliveries = 0;

        firstServices.events.subscribe(function() {
            oldBusDeliveries++;
        });

        Main.bootGame(MainLoadingType.NONE, null);
        var secondServices = Main.getServices();
        secondServices.events.subscribe(function() {
            newBusDeliveries++;
        });

        firstServices.events.publish({ type: "old-runtime-probe", occurredAt: 1 });
        secondServices.events.publish({ type: "new-runtime-probe", occurredAt: 2 });

        return {
            wasReplaced: firstServices !== secondServices,
            oldWasDisposed: firstServices.isDisposed(),
            oldBusWasDisposed: firstServices.events.isDisposed(),
            oldBusDeliveries: oldBusDeliveries,
            newBusDeliveries: newBusDeliveries
        };
    });

    expect(lifecycle).toEqual({
        wasReplaced: true,
        oldWasDisposed: true,
        oldBusWasDisposed: true,
        oldBusDeliveries: 0,
        newBusDeliveries: 1
    });
});
