"use strict";

var childProcess = require("child_process");
var fs = require("fs");
var path = require("path");

var repositoryRoot = path.resolve(__dirname, "..");
var generatorRoot = path.join(repositoryRoot, "pythonScripts");

fs.mkdirSync(path.join(repositoryRoot, "code", "gen"), { recursive: true });

run("python3", ["genAscii.py"]);
run("python3", ["genText.py"]);

process.stdout.write("Generated legacy ASCII and text TypeScript sources.\n");

function run(command, args) {
    var result = childProcess.spawnSync(command, args, {
        cwd: generatorRoot,
        stdio: "inherit"
    });

    if (result.error) {
        process.stderr.write(result.error.message + "\n");
        process.exit(1);
    }
    if (result.status !== 0) {
        process.exit(result.status || 1);
    }
}
