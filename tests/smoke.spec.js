"use strict";

var test = require("@playwright/test").test;
var expect = require("@playwright/test").expect;
var profile = process.env.CB_BUILD_PROFILE || "development";

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
