"use strict";

var test = require("@playwright/test").test;
var expect = require("@playwright/test").expect;
var profile = process.env.CB_BUILD_PROFILE || "development";

async function setSessionFlag(page, value) {
    await page.addInitScript(function(flagValue) {
        if (flagValue === null) {
            sessionStorage.removeItem("cb3CandyFacadeEnabled");
        } else {
            sessionStorage.setItem("cb3CandyFacadeEnabled", flagValue);
        }
    }, value);
}

async function resolvedFlag(page, path) {
    await page.goto(path || "/");
    return page.evaluate(function() {
        return FeatureFlags.isCandyFacadeEnabled();
    });
}

test("uses the build default when no Candy facade override is present", async function({ page }) {
    expect(await resolvedFlag(page, "/")).toBe(false);
});

test("resolves development Candy facade URL overrides", async function({ page }) {
    expect(await resolvedFlag(page, "/?cb3CandyFacade=1")).toBe(profile === "development");
    expect(await resolvedFlag(page, "/?cb3CandyFacade=0")).toBe(false);
});

test("gives the last Candy facade URL occurrence precedence", async function({ page }) {
    expect(await resolvedFlag(page, "/?cb3CandyFacade=0&cb3CandyFacade=1")).toBe(profile === "development");
    expect(await resolvedFlag(page, "/?cb3CandyFacade=1&cb3CandyFacade=0")).toBe(false);
});

test("falls back when the last duplicate URL value is invalid", async function({ page }) {
    await setSessionFlag(page, "1");
    expect(await resolvedFlag(page, "/?cb3CandyFacade=0&cb3CandyFacade=invalid")).toBe(profile === "development");
});

test("uses session override only in development", async function({ page }) {
    await setSessionFlag(page, "1");
    expect(await resolvedFlag(page, "/")).toBe(profile === "development");
});

test("gives a valid URL override precedence over session storage", async function({ page }) {
    await setSessionFlag(page, "1");
    expect(await resolvedFlag(page, "/?cb3CandyFacade=0")).toBe(false);
});

test("falls back from an invalid URL value to the session override", async function({ page }) {
    await setSessionFlag(page, "1");
    expect(await resolvedFlag(page, "/?cb3CandyFacade=invalid")).toBe(profile === "development");
});

test("falls back from an invalid session value to the build default", async function({ page }) {
    await setSessionFlag(page, "true");
    expect(await resolvedFlag(page, "/")).toBe(false);
});

test("does not persist a URL override to session or local storage", async function({ page }) {
    await setSessionFlag(page, null);
    await page.goto("/?cb3CandyFacade=1");

    var stored = await page.evaluate(function() {
        return {
            session: sessionStorage.getItem("cb3CandyFacadeEnabled"),
            local: localStorage.getItem("cb3CandyFacadeEnabled")
        };
    });

    expect(stored).toEqual({ session: null, local: null });
});
