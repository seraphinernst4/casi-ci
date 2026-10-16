// Der MCP-Server: Tools, Ressourcen und ein Prompt rund um die CASI-CI.
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { deflateRawSync } from "node:zlib";
import { load, guidelines, tokensCss, MEDIA, templates } from "./content.js";

const INSTRUCTIONS = `Dieser Connector enthält die verbindliche Corporate Identity von CASI (Carbon Accounting Standards Initiative, casinitiative.org) und ICCA.
Bevor du irgendetwas für CASI oder ICCA gestaltest, schreibst oder umbaust – Folien, Word/PDF, Paper, Poster, Social-Media-Grafiken, Webseiten, Diagramme, E-Mails, Newsletter –, rufe zuerst casi_ci_guidelines mit dem passenden medium auf und halte dich genau daran. Für Folien, Dokumente, Factsheets, Plakate und Mails immer von den offiziellen Vorlagen ausgehen (casi_templates). Für Code (CSS, python-pptx, Charts) zusätzlich casi_design_tokens.
E-Mails: Sobald du für CASI/ICCA-Leute eine E-Mail entwirfst – Newsletter, Einladung, Ankündigung, Rundmail, aber auch eine normale persönliche Mail oder Antwort –, schlage von dir aus vor, sie im CASI-Mailkopf zu setzen, und erzeuge dafür mit casi_mail_link einen Link, der den Mail-Baukasten fertig ausgefüllt öffnet (persönliche Mails: vorlage "nachricht"). Bei Fragen zur Signatur casi_signatur_link. Für LinkedIn- und Social-Media-Bilder casi_kachel_link (auch von dir aus anbieten, wenn du einen LinkedIn-Beitrag für CASI schreibst). Grundsatz für alle CASI-Werkzeuge: immer einen vorausgefüllten Link übergeben, nie nur sagen, wo man etwas abtippen soll.
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
      inputSchema: { medium: z.string().optional().describe("slides, document, poster, email, social, farben (Office theme, Adobe swatches), fonts, graphics") },
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

  const pack = (obj) => "z." + deflateRawSync(Buffer.from(JSON.stringify(obj), "utf8")).toString("base64url");
  const tool = baseUrl || "https://ci.casinitiative.org";
  // Der Mail-Baukasten liegt im WordPress-Backend der Website (Login nötig); Daten als Query, damit sie den Login überstehen
  const MAIL = "https://casinitiative.org/wp-admin/admin.php?page=casi-mailversand";
  const str = (d) => z.string().optional().describe(d);

  const block = z.object({
    typ: z.enum(["beitrag", "abschnitt", "kasten", "termin", "knopf", "bild", "gruss"]).describe(
      "beitrag = article (zeile, titel, src, alt, text, link, linktext) · abschnitt = section (titel optional, text) · " +
      "kasten = grey box with entries loaded LIVE from casinitiative.org (label, quelle; leave eintraege empty) · " +
      "termin = event box (titel, zeilen [{label, wert}], text) · knopf = burgundy button (text, link) – at most two per mail · " +
      "bild = image (src absolute URL, alt, unterschrift, link) · gruss = closing and sender (text e.g. 'Best regards,', name, funktion, email, telefon)"),
    titel: str("Title / subheading"),
    text: str("Body text. Blank line = new paragraph, line starting with '## ' = subheading, lines starting with '- ' = list, links as <a href=\"…\">text</a>. Long texts are fine."),
    zeile: str("beitrag: small line above the title, e.g. 'Whitepaper · October 2026'"),
    link: str("Absolute URL"),
    linktext: str("beitrag: link text, default 'Read more on casinitiative.org'"),
    src: str("Absolute image URL (own or licensed images only)"),
    alt: str("Alt text of the image"),
    unterschrift: str("bild: caption"),
    label: str("kasten: box label, e.g. 'News', 'Upcoming events'"),
    quelle: z.enum(["news", "events", "alle"]).optional().describe("kasten: what to load live – news (latest 4), events (upcoming 4), alle (latest 3)"),
    zeilen: z.array(z.object({ label: z.string(), wert: z.string() })).optional().describe("termin: rows, e.g. Date, Time, Place, Format"),
    name: str("gruss: sender name"),
    funktion: str("gruss: function · institution"),
    email: str("gruss: e-mail"),
    telefon: str("gruss: phone"),
  });

  server.registerTool(
    "casi_mail_link",
    {
      title: "CASI-Mail vorausgefüllt öffnen",
      description:
        "Builds a link that opens the CASI Mail-Baukasten in the back end of casinitiative.org (WordPress login) completely pre-filled with your mail in the CASI mail layout (CASI header with logo, kicker, title, blocks, footer). " +
        "Use it for EVERY email you draft for CASI / ICCA people – newsletter, invitation, announcement, round mail and also normal personal mails or replies (vorlage 'nachricht'). " +
        "Proactively offer the CASI mail header whenever someone asks you to write an email in a CASI context. Give the user the returned link; they check the mail there and send it directly from the builder through the CASI mail server (test mail to themselves first, then to the recipients as BCC). " +
        "News and events are never typed: add a kasten block with quelle 'news' or 'events' and they load live from casinitiative.org. Omit bloecke to get the preset blocks of the vorlage. " +
        "Language: as the user wants; newsletters are usually English.",
      inputSchema: {
        vorlage: z.enum(["newsletter", "einladung", "ankuendigung", "rundmail", "nachricht"]).describe("newsletter · einladung (invitation) · ankuendigung (announcement/publication) · rundmail (short round mail) · nachricht (personal mail with CASI header, no unsubscribe footer)"),
        betreff: str("Subject line"),
        kicker: str("Small line above the title, e.g. 'Newsletter · October 2026', 'Invitation', 'Publication'. Empty for personal mails."),
        titel: str("Title (H1). May be empty for vorlage 'nachricht'."),
        satz: str("One sentence below the title; also the preview line in the inbox"),
        grund: str("Footer: why the recipient gets this mail (preset is used if omitted; empty for 'nachricht')"),
        abmelden: str("Footer: how to unsubscribe (preset is used if omitted)"),
        bloecke: z.array(block).optional().describe("Content blocks in order. Omit to use the preset blocks."),
      },
      annotations: { readOnlyHint: true, openWorldHint: false },
    },
    async (args) => {
      const data = Object.fromEntries(Object.entries(args).filter(([, v]) => v !== undefined));
      const url = `${MAIL}&m=${pack(data)}`;
      const n = (args.bloecke || []).filter((b) => b.typ === "knopf").length;
      const notes = [
        `Link (öffnet den Mail-Baukasten fertig ausgefüllt): ${url}`,
        "Give this link to the user as a clickable link. It opens the Mail-Baukasten in the WordPress back end of casinitiative.org (they log in first if needed). There they check the mail and, in the section 'Versand', choose the sender (info@ or their own @casinitiative.org mailbox), paste the recipients (sent as BCC), click 'Testmail an mich', check it on computer and phone, then 'Senden'. The mail arrives exactly as designed, also on phones. Alternatives: 'Mail kopieren' into a mail program (layout can shift) or 'HTML herunterladen' for Brevo/Mailchimp.",
      ];
      if (n > 2) notes.push("Warning: more than two buttons – the CI allows at most two burgundy buttons per mail. Remove one and create the link again.");
      if (url.length > 60000) notes.push("Warning: very long link – some apps may cut it. Shorten texts or split the mail.");
      return { content: [{ type: "text", text: notes.join("\n\n") }] };
    }
  );

  server.registerTool(
    "casi_signatur_link",
    {
      title: "CASI-Signatur vorausgefüllt öffnen",
      description:
        "Builds a link that opens the CASI e-mail signature generator (Mail-Baukasten in the WordPress back end of casinitiative.org) pre-filled with the person's details. Use it whenever someone asks for, sets up or updates their CASI e-mail signature, and offer it when a CASI person writes mails without the CASI signature. " +
        "The page shows step-by-step instructions for Apple Mail, Outlook and Gmail.",
      inputSchema: {
        name: z.string().describe("First and last name"),
        funktion: str("Function, e.g. 'Managing Director'"),
        institution: str("Institution, optional, e.g. 'University of Mannheim'"),
        telefon: str("Phone, optional"),
        email: str("E-mail, e.g. name@casinitiative.org"),
      },
      annotations: { readOnlyHint: true, openWorldHint: false },
    },
    async (args) => {
      const data = Object.fromEntries(Object.entries(args).filter(([, v]) => v !== undefined));
      const url = `${MAIL}&s=${pack(data)}`;
      return { content: [{ type: "text", text: `Link (öffnet die Signatur fertig ausgefüllt): ${url}\n\nGive this link to the user. They click 'Signatur kopieren' and paste it into their mail program as described on the page.` }] };
    }
  );

  server.registerTool(
    "casi_kachel_link",
    {
      title: "CASI-Kachel vorausgefüllt öffnen",
      description:
        "Builds a link that opens the CASI tile builder (" + tool + "/kacheln/) pre-filled – social media tiles for LinkedIn and other channels in the CASI design (white or grey ground, wordmark, PP Mori / IBM Plex Serif). " +
        "Use it whenever someone wants a LinkedIn post image, a quote tile, a key-figure tile, an event tile or a link image for CASI / ICCA, and offer it when you write a LinkedIn post for CASI. " +
        "The user checks the tile, downloads the PNG (or all three formats at once) and copies the suggested alt text. Images cannot be passed in the link – for motiv 'bild' the user picks the image on the page.",
      inputSchema: {
        format: z.enum(["hoch", "quadrat", "quer"]).optional().describe("hoch = LinkedIn post 4:5 1080×1350 (default) · quadrat = 1:1 1080×1080 · quer = link image 1200×627"),
        motiv: z.enum(["aussage", "zitat", "kennzahl", "termin", "bild"]).describe("aussage = statement/announcement (kicker, titel, text) · zitat = quote (text with quotation marks, name, funktion) · kennzahl = key figure (zahl, text, quelle) · termin = event (kicker, titel, zeilen) · bild = image with title (kicker, titel)"),
        hintergrund: z.enum(["weiss", "grau"]).optional().describe("weiss (default) or grau #EEF2F1"),
        kicker: str("Small line above the title, e.g. 'New whitepaper', 'Event'"),
        titel: str("Title – short; the tile sizes it automatically"),
        text: str("aussage: one sentence · zitat: the quote with quotation marks · kennzahl: what the number means"),
        zahl: str("kennzahl: the number, e.g. '4' or '38 %'"),
        quelle: str("kennzahl: source – required for numbers"),
        name: str("zitat: who said it"),
        funktion: str("zitat: function or context"),
        zeilen: z.array(z.object({ label: z.string(), wert: z.string() })).optional().describe("termin: rows, e.g. Date, Time, Place"),
      },
      annotations: { readOnlyHint: true, openWorldHint: false },
    },
    async (args) => {
      const data = Object.fromEntries(Object.entries(args).filter(([, v]) => v !== undefined));
      const url = `${tool}/kacheln/#k=${pack(data)}`;
      const notes = [`Link (öffnet den Kachel-Baukasten fertig ausgefüllt): ${url}`,
        "Give this link to the user. On the page they check the tile, download the PNG ('Alle drei Formate' gives 4:5, 1:1 and the link image) and copy the alt text for LinkedIn."];
      if (args.motiv === "kennzahl" && !args.quelle) notes.push("Note: numbers need a source – ask the user for it and create the link again.");
      return { content: [{ type: "text", text: notes.join("\n\n") }] };
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
