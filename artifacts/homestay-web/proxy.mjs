import http from "http";

const PORT = parseInt(process.env.PORT);
const FLASK_PORT = 5000;

if (!PORT) {
  console.error("PORT env variable is required");
  process.exit(1);
}

const server = http.createServer((req, res) => {
  const options = {
    hostname: "localhost",
    port: FLASK_PORT,
    path: req.url,
    method: req.method,
    headers: {
      ...req.headers,
      host: `localhost:${FLASK_PORT}`,
    },
  };

  const proxyReq = http.request(options, (proxyRes) => {
    res.writeHead(proxyRes.statusCode, proxyRes.headers);
    proxyRes.pipe(res, { end: true });
  });

  proxyReq.on("error", () => {
    res.writeHead(502, { "Content-Type": "text/html" });
    res.end(`
      <html><body style="font-family:sans-serif;text-align:center;padding:2rem">
        <h2>Flask app is starting…</h2>
        <p>The Artist Rally Homestay server is coming up on port ${FLASK_PORT}. Please wait a moment and refresh.</p>
        <script>setTimeout(()=>location.reload(),3000)</script>
      </body></html>
    `);
  });

  req.pipe(proxyReq, { end: true });
});

server.listen(PORT, "0.0.0.0", () => {
  console.log(`Proxy running on port ${PORT} → Flask on port ${FLASK_PORT}`);
});
