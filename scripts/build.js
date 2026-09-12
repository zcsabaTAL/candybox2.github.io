"use strict";

var childProcess = require("child_process");
var fs = require("fs");
var path = require("path");

var repositoryRoot = path.resolve(__dirname, "..");
var environment = process.argv[2] || "development";

if (environment !== "development" && environment !== "production") {
    fail("Unknown build environment: " + environment);
}

run(process.execPath, [path.join(__dirname, "generate-content.js")]);
run(process.execPath, [path.join(__dirname, "generate-build-config.js"), environment]);

var sourceFiles = [];
appendTypeScriptFiles(sourceFiles, path.join(repositoryRoot, "libs"), false);
appendTypeScriptFiles(sourceFiles, path.join(repositoryRoot, "code", "main"), false);
appendTypeScriptFiles(sourceFiles, path.join(repositoryRoot, "code", "gen"), false);
appendArenaTypeScriptFiles(sourceFiles, path.join(repositoryRoot, "code", "arena"));

var temporaryBundle = path.join(repositoryRoot, "candybox2_uncompressed.js.temp");
var compiler = path.join(repositoryRoot, "node_modules", ".bin", "tsc");
var compilerArguments = sourceFiles.concat(["--out", temporaryBundle]);

run(compiler, compilerArguments);

var license = fs.readFileSync(path.join(repositoryRoot, "candybox2_sourceCodeLicense.txt"));
var compiled = fs.readFileSync(temporaryBundle);
var bundle = Buffer.concat([license, compiled]);

fs.writeFileSync(path.join(repositoryRoot, "candybox2.js"), bundle);
fs.writeFileSync(path.join(repositoryRoot, "candybox2_uncompressed.js"), bundle);
fs.unlinkSync(temporaryBundle);

process.stdout.write("Candy Box 2 " + environment + " build completed.\n");

function appendTypeScriptFiles(target, directory, recursive) {
    if (!fs.existsSync(directory)) {
        fail("Missing source directory: " + directory);
    }

    fs.readdirSync(directory).sort().forEach(function(fileName) {
        var filePath = path.join(directory, fileName);
        var stat = fs.statSync(filePath);

        if (stat.isDirectory() && recursive) {
            appendTypeScriptFiles(target, filePath, true);
        } else if (stat.isFile() && path.extname(fileName) === ".ts") {
            target.push(filePath);
        }
    });
}

function appendArenaTypeScriptFiles(target, arenaDirectory) {
    if (!fs.existsSync(arenaDirectory)) {
        fail("Missing source directory: " + arenaDirectory);
    }

    fs.readdirSync(arenaDirectory).sort().forEach(function(fileName) {
        var filePath = path.join(arenaDirectory, fileName);
        if (fs.statSync(filePath).isDirectory()) {
            appendTypeScriptFiles(target, filePath, false);
        }
    });
}

function run(command, args) {
    var result = childProcess.spawnSync(command, args, {
        cwd: repositoryRoot,
        stdio: "inherit"
    });

    if (result.error) {
        fail(result.error.message);
    }
    if (result.status !== 0) {
        process.exit(result.status || 1);
    }
}

function fail(message) {
    process.stderr.write(message + "\n");
    process.exit(1);
}
