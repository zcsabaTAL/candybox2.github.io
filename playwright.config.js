"use strict";

var defineConfig = require("@playwright/test").defineConfig;
var profile = process.env.CB_BUILD_PROFILE || "development";

if (profile !== "development" && profile !== "production") {
    throw new Error("Unknown CB_BUILD_PROFILE: " + profile);
}

module.exports = defineConfig({
    testDir: "./tests",
    fullyParallel: false,
    workers: 1,
    retries: 0,
    timeout: 30000,
    reporter: "line",
    use: {
        baseURL: "http://127.0.0.1:8082",
        browserName: "chromium",
        headless: true,
        trace: "retain-on-failure"
    },
    webServer: {
        command: "npm run build:" + (profile === "development" ? "dev" : "prod") + " && node scripts/test-server.js 8082",
        url: "http://127.0.0.1:8082",
        reuseExistingServer: false,
        timeout: 120000
    },
    metadata: {
        buildProfile: profile
    }
});
