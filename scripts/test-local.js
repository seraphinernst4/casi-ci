// Startet den Server lokal und ruft alle Tools einmal über einen echten MCP-Client auf.
import http from "node:http";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";
import handler from "../api/mcp.js";

const base = process.env.MCP_URL;
let srv;
let url = base;
if (!base) {
  srv = http.createServer((req, res) => handler(req, res));
  await new Promise((r) => srv.listen(0, r));
  url = `http://localhost:${srv.address().port}/mcp/${process.env.CI_ACCESS_KEY ?? "test"}`;
}
const client = new Client({ name: "casi-test", version: "1.0.0" });
await client.connect(new StreamableHTTPClientTransport(new URL(url)));
console.log("Server:", client.getServerVersion());
console.log("Instructions:", client.getInstructions()?.slice(0, 80) + "…");
const { tools } = await client.listTools();
console.log("Tools:", tools.map((t) => t.name).join(", "));
const g = await client.callTool({ name: "casi_ci_guidelines", arguments: { medium: "slides" } });
console.log("guidelines(slides):", g.content[0].text.length, "Zeichen; Ende:", g.content[0].text.slice(-140).replace(/\n/g, " "));
const s = await client.callTool({ name: "casi_ci_guidelines", arguments: { section: "colour" } });
console.log("section colour startet mit:", s.content[0].text.split("\n")[0]);
const css = await client.callTool({ name: "casi_design_tokens", arguments: { format: "css" } });
console.log(css.content[0].text.split("\n").slice(0, 4).join("\n"));
const { resources } = await client.listResources();
console.log("Ressourcen:", resources.map((r) => r.uri).join(", "));
const { prompts } = await client.listPrompts();
console.log("Prompts:", prompts.map((p) => p.name).join(", "));
await client.close();
srv?.close();
