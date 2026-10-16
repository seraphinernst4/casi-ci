// Der MCP-Server: Tools, Ressourcen und ein Prompt rund um die CASI-CI.
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { load, guidelines, tokensCss, MEDIA, templates } from "./content.js";

const INSTRUCTIONS = `Dieser Connector enthält die verbindliche Corporate Identity von CASI (Carbon Accounting Standards Initiative, casinitiative.org) und ICCA.
Bevor du irgendetwas für CASI oder ICCA gestaltest, schreibst oder umbaust – Folien, Word/PDF, Paper, Poster, Social-Media-Grafiken, Webseiten, Diagramme, E-Mails, Newsletter –, rufe zuerst casi_ci_guidelines mit dem passenden medium auf und halte dich genau daran. Für Folien, Dokumente und Mails immer von den offiziellen Vorlagen ausgehen (casi_templates). Für Code (CSS, python-pptx, Charts) zusätzlich casi_design_tokens.
The guidelines are always the current version; do not rely on older copies.`;

export function createServer({ baseUrl = "", key = "" } = {}) {
  const c = load();
  const server = new McpServer(
    { name: "casi-ci", version: c.version },
    { instructions: INSTRUCTIONS }
  );

  const sectionIds = c.sections.map((s) => s.id);

  server.registerTool(
    "casi_ci_guidelines",
    {
      title: "CASI Corporate Identity",
      description:
        "Returns the binding, always-current CASI / ICCA corporate identity (colours, typefaces, boxes, layout rules, text rules). " +
        "Call this FIRST whenever you create, format or redesign anything for CASI or ICCA: slides, documents, papers, PDFs, posters, social posts, web pages, charts, emails or newsletters. " +
        "Choose `medium` to get the core rules plus the part for that medium, or `section` for one section only.",
      inputSchema: {
        medium: z
          .enum(Object.keys(MEDIA))
          .optional()
          .describe("Output type. 'all' (default) returns the full CI."),
        section: z
          .enum(sectionIds)
          .optional()
          .describe("Return only this section instead of a medium bundle."),
      },
      annotations: { readOnlyHint: true, openWorldHint: false },
    },
    async ({ medium, section }) => ({
      content: [{ type: "text", text: guidelines({ medium, section }) }],
    })
  );

  server.registerTool(
    "casi_design_tokens",
    {
      title: "CASI Design Tokens",
      description:
        "Returns CASI design tokens (colours with roles, font stacks, weights, corner radii, logo and font URLs) for use in code: CSS, python-pptx, docx, charts. " +
        "Format 'json' = W3C design-token JSON, 'css' = :root custom properties. Always read casi_ci_guidelines too – tokens alone do not contain the rules.",
      inputSchema: {
        format: z.enum(["json", "css"]).optional().describe("Default 'json'."),
      },
      annotations: { readOnlyHint: true, openWorldHint: false },
    },
    async ({ format = "json" }) => ({
      content: [{ type: "text", text: format === "css" ? tokensCss() : c.tokensRaw }],
    })
  );

  server.registerTool(
    "casi_templates",
    {
      title: "CASI Vorlagen",
      description:
        "Lists the official CASI templates (PowerPoint, Word, email, …) and the CASI font package with download links. " +
        "Always start CASI slides, documents and emails from these templates instead of building the layout yourself. Optional `medium` filters the list.",
      inputSchema: { medium: z.string().optional().describe("e.g. slides, document, email, fonts") },
      annotations: { readOnlyHint: true, openWorldHint: false },
    },
    async ({ medium }) => {
      const list = templates().filter((t) => !medium || t.medium === medium);
      const lines = list.map(
        (t) =>
          t.link
            ? `- **${t.titel}**\n  ${t.wofuer}\n  Link: ${t.link}`
            : `- **${t.titel}** (${t.datei})\n  ${t.wofuer}\n  Download: ${baseUrl}/vorlagen/${encodeURIComponent(key)}/${encodeURIComponent(t.datei)}`
      );
      return { content: [{ type: "text", text: lines.length ? lines.join("\n") : "Keine Vorlage für dieses Medium." }] };
    }
  );

  server.registerResource(
    "casi-ci-skill",
    "casi://ci/SKILL.md",
    { title: "CASI CI (komplett)", description: "Die vollständige CASI Corporate Identity", mimeType: "text/markdown" },
    async (uri) => ({ contents: [{ uri: uri.href, mimeType: "text/markdown", text: c.body }] })
  );

  server.registerResource(
    "casi-ci-tokens",
    "casi://ci/tokens.json",
    { title: "CASI Design Tokens", description: "Farben, Schriften, Radien als JSON", mimeType: "application/json" },
    async (uri) => ({ contents: [{ uri: uri.href, mimeType: "application/json", text: c.tokensRaw }] })
  );

  server.registerPrompt(
    "casi-ci",
    {
      title: "CASI-CI anwenden",
      description: "Fügt die aktuelle CASI-CI für ein Medium in den Chat ein",
      argsSchema: { medium: z.enum(Object.keys(MEDIA)).optional() },
    },
    ({ medium }) => ({
      messages: [
        {
          role: "user",
          content: {
            type: "text",
            text: `Gestalte alles in diesem Chat nach der folgenden CASI Corporate Identity:\n\n${guidelines({ medium })}`,
          },
        },
      ],
    })
  );

  return server;
}
