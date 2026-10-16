// Vercel Function: MCP über Streamable HTTP (zustandslos).
// Erreichbar unter /mcp/<SCHLÜSSEL> (siehe vercel.json). Der Schlüssel liegt als
// Umgebungsvariable CI_ACCESS_KEY in Vercel – ohne ihn antwortet der Server mit 404.
import { timingSafeEqual } from "node:crypto";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { createServer } from "../lib/server.js";

function givenKey(req) {
  if (req.query?.key) return String(req.query.key);
  const url = new URL(req.url || "/", "http://localhost");
  return url.searchParams.get("key") || url.pathname.match(/\/mcp\/([^/]+)/)?.[1] || "";
}

function keyOk(req) {
  const expected = process.env.CI_ACCESS_KEY;
  if (!expected) return true; // lokal ohne Schlüssel
  const a = Buffer.from(givenKey(req));
  const b = Buffer.from(expected);
  return a.length === b.length && timingSafeEqual(a, b);
}

function send(res, status, obj, headers = {}) {
  res.statusCode = status;
  res.setHeader("Content-Type", "application/json");
  for (const [k, v] of Object.entries(headers)) res.setHeader(k, v);
  res.end(JSON.stringify(obj));
}

async function readBody(req) {
  if (req.body !== undefined) return typeof req.body === "string" ? JSON.parse(req.body) : req.body;
  const chunks = [];
  for await (const ch of req) chunks.push(ch);
  const text = Buffer.concat(chunks).toString("utf8");
  return text ? JSON.parse(text) : undefined;
}

export default async function handler(req, res) {
  res.setHeader("Cache-Control", "no-store");
  if (!keyOk(req)) return send(res, 404, { error: "Not found" });

  if (req.method !== "POST") {
    return send(
      res,
      405,
      { jsonrpc: "2.0", error: { code: -32000, message: "Method not allowed" }, id: null },
      { Allow: "POST" }
    );
  }

  let body;
  try {
    body = await readBody(req);
  } catch {
    return send(res, 400, { jsonrpc: "2.0", error: { code: -32700, message: "Parse error" }, id: null });
  }

  const server = createServer();
  const transport = new StreamableHTTPServerTransport({ sessionIdGenerator: undefined, enableJsonResponse: true });
  res.on("close", () => {
    transport.close();
    server.close();
  });
  try {
    await server.connect(transport);
    await transport.handleRequest(req, res, body);
  } catch (err) {
    console.error(err);
    if (!res.headersSent)
      send(res, 500, { jsonrpc: "2.0", error: { code: -32603, message: "Internal server error" }, id: null });
  }
}
