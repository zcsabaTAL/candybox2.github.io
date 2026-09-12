"use strict";

var fs = require("fs");
var http = require("http");
var path = require("path");

var repositoryRoot = path.resolve(__dirname, "..");
var port = parseInt(process.argv[2] || "8082", 10);
var mimeTypes = {
    ".css": "text/css; charset=utf-8",
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".mp3": "audio/mpeg",
    ".png": "image/png",
    ".wav": "audio/wav"
};

http.createServer(function(request, response) {
    var requestUrl = new URL(request.url, "http://127.0.0.1:" + port);
    var requestPath = decodeURIComponent(requestUrl.pathname);
    var relativePath = requestPath === "/" ? "index.html" : requestPath.replace(/^\/+/, "");
    var filePath = path.resolve(repositoryRoot, relativePath);

    if (filePath !== repositoryRoot && filePath.indexOf(repositoryRoot + path.sep) !== 0) {
        response.writeHead(403);
        response.end("Forbidden");
        return;
    }

    fs.stat(filePath, function(statError, stat) {
        if (statError || !stat.isFile()) {
            response.writeHead(404);
            response.end("Not found");
            return;
        }

        response.writeHead(200, {
            "Content-Type": mimeTypes[path.extname(filePath).toLowerCase()] || "application/octet-stream",
            "Cache-Control": "no-store"
        });
        fs.createReadStream(filePath).pipe(response);
    });
}).listen(port, "127.0.0.1", function() {
    process.stdout.write("Candy Box smoke server listening on http://127.0.0.1:" + port + "\n");
});
