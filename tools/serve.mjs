// serve.mjs — zero-dependency static file server for local previews.
// Usage: node tools/serve.mjs [dir] [port]
//   dir  — directory to serve (default: current working directory)
//   port — port to listen on (default: PORT env var or 3000)
//
// SECURITY: binds 127.0.0.1 ONLY (never the network) and refuses any path
// containing a dotfile segment (.env, .git, .claude, ...). This repo is a
// business brain — never serve it to an interface other machines can reach.
// Point this at a built site directory, not at the brain root.
import http from "http";
import fs from "fs";
import path from "path";

const ROOT = path.resolve(process.argv[2] || process.cwd());
const PORT = Number(process.argv[3] || process.env.PORT || 3000);
const HOST = "127.0.0.1";

const MIME_TYPES = {
  ".html": "text/html",
  ".css": "text/css",
  ".js": "application/javascript",
  ".mjs": "application/javascript",
  ".json": "application/json",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".gif": "image/gif",
  ".svg": "image/svg+xml",
  ".ico": "image/x-icon",
  ".woff": "font/woff",
  ".woff2": "font/woff2",
  ".ttf": "font/ttf",
};

const server = http.createServer((req, res) => {
  let urlPath = req.url === "/" ? "/index.html" : req.url;
  // Strip query strings
  urlPath = urlPath.split("?")[0];

  const filePath = path.join(ROOT, path.normalize(urlPath));
  // Refuse path traversal outside the served root.
  if (!filePath.startsWith(ROOT)) {
    res.writeHead(403, { "Content-Type": "text/plain" });
    res.end("403 Forbidden");
    return;
  }

  // Refuse dotfiles and dot-directories anywhere in the path (.env, .git,
  // .claude, .netlify, ...). Secrets and config are never servable.
  const rel = path.relative(ROOT, filePath);
  if (rel.split(path.sep).some((seg) => seg.startsWith("."))) {
    res.writeHead(404, { "Content-Type": "text/plain" });
    res.end("404 Not Found");
    return;
  }

  const ext = path.extname(filePath).toLowerCase();
  const contentType = MIME_TYPES[ext] || "application/octet-stream";

  fs.readFile(filePath, (err, data) => {
    if (err) {
      if (err.code === "ENOENT") {
        res.writeHead(404, { "Content-Type": "text/plain" });
        res.end("404 Not Found");
      } else {
        res.writeHead(500, { "Content-Type": "text/plain" });
        res.end("500 Internal Server Error");
      }
      return;
    }
    res.writeHead(200, { "Content-Type": contentType });
    res.end(data);
  });
});

server.listen(PORT, HOST, () => {
  console.log(`Server running at http://${HOST}:${PORT} (localhost only)`);
  console.log(`Serving: ${ROOT}`);
  console.log("Press Ctrl+C to stop.");
});
