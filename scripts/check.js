// Prüft vor jedem Deployment, ob SKILL.md und tokens.json zusammenpassen.
// Schlägt die Prüfung fehl, bricht Vercel das Deployment ab – live bleibt der letzte gute Stand.
import { readFileSync } from "node:fs";

const fail = (msg) => { console.error("✗ " + msg); process.exitCode = 1; };
const skill = readFileSync("ci/SKILL.md", "utf8");
let tokens;
try { tokens = JSON.parse(readFileSync("ci/tokens.json", "utf8")); }
catch (e) { fail("ci/tokens.json ist kein gültiges JSON: " + e.message); process.exit(1); }

if (!/^---\n(?:[\s\S]*?\n)?name:/.test(skill)) fail("ci/SKILL.md: Kopfbereich (--- name: … ---) fehlt");
for (const h of ["Colour", "Typography", "Check before delivering"]) {
  if (!new RegExp("^##\\s+" + h, "mi").test(skill)) fail(`ci/SKILL.md: Abschnitt "## ${h}…" fehlt`);
}
for (const [name, t] of Object.entries(tokens.color ?? {})) {
  if (!skill.toUpperCase().includes(String(t.$value).toUpperCase()))
    fail(`Farbe "${name}" (${t.$value}) steht in tokens.json, aber nicht in SKILL.md – eine der beiden Dateien anpassen`);
}
const skillHex = new Set((skill.match(/#[0-9A-F]{6}\b/gi) ?? []).map((h) => h.toUpperCase()));
const tokenHex = new Set(Object.values(tokens.color ?? {}).map((t) => String(t.$value).toUpperCase()));
for (const h of skillHex) if (!tokenHex.has(h)) fail(`Farbe ${h} steht in SKILL.md, fehlt aber in tokens.json`);

import { existsSync } from "node:fs";
const vl = JSON.parse(readFileSync("vorlagen/vorlagen.json", "utf8")).vorlagen;
for (const v of vl) if (!existsSync("vorlagen/" + v.datei)) fail(`vorlagen.json nennt ${v.datei}, die Datei fehlt in vorlagen/`);

if (!process.exitCode) console.log(`✓ CASI-CI geprüft: ${skillHex.size} Farben, SKILL.md und tokens.json stimmen überein`);
