// Liest die CASI-CI aus ci/SKILL.md und ci/tokens.json.
// Diese beiden Dateien sind die einzige Quelle – alles andere wird daraus abgeleitet.
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import path from "node:path";

const ROOT = process.cwd();
const SKILL_PATH = path.join(ROOT, "ci", "SKILL.md");
const TOKENS_PATH = path.join(ROOT, "ci", "tokens.json");

// Feste, gut lesbare IDs für die Abschnitte des SKILL.md (nach Überschrift).
// Unbekannte neue Abschnitte bekommen automatisch eine ID aus ihrem ersten Wort.
const SECTION_IDS = [
  [/^two rules/i, "rules"],
  [/^colou?r/i, "colour"],
  [/^typo/i, "typography"],
  [/^boxes/i, "boxes"],
  [/^website/i, "website"],
  [/^e-?mail/i, "email"],
  [/^slides/i, "slides"],
  [/^documents/i, "documents"],
  [/^other/i, "other"],
  [/^check/i, "check"],
];

// Welche Abschnitte ein Agent für welches Medium bekommt.
const CORE = ["intro", "rules", "colour", "typography", "boxes", "check"];
export const MEDIA = {
  all: null,
  slides: [...CORE, "slides", "website"],
  document: [...CORE, "documents"],
  email: [...CORE, "email", "website"],
  website: [...CORE, "website", "other"],
  chart: [...CORE, "other"],
  poster: [...CORE, "documents", "other"],
  social: [...CORE, "other"],
};

function slug(heading) {
  for (const [re, id] of SECTION_IDS) if (re.test(heading)) return id;
  return heading.toLowerCase().split(/\s+/)[0].replace(/[^a-z0-9-]/g, "") || "section";
}

function stripFrontmatter(md) {
  const m = md.match(/^---\n([\s\S]*?)\n---\n?/);
  if (!m) return { meta: {}, body: md };
  const meta = {};
  for (const line of m[1].split("\n")) {
    const kv = line.match(/^(\w+):\s*"?(.*?)"?\s*$/);
    if (kv) meta[kv[1]] = kv[2];
  }
  return { meta, body: md.slice(m[0].length) };
}

let cache = null;

export function load() {
  if (cache) return cache;
  const raw = readFileSync(SKILL_PATH, "utf8");
  const tokensRaw = readFileSync(TOKENS_PATH, "utf8");
  const { meta, body } = stripFrontmatter(raw);

  const sections = [];
  let current = { id: "intro", title: "Einleitung", lines: [] };
  for (const line of body.split("\n")) {
    const h = line.match(/^##\s+(.+?)\s*$/);
    if (h) {
      sections.push(current);
      current = { id: slug(h[1]), title: h[1], lines: [line] };
    } else current.lines.push(line);
  }
  sections.push(current);
  for (const s of sections) s.text = s.lines.join("\n").trim();

  const hash = createHash("sha256").update(raw).update(tokensRaw).digest("hex").slice(0, 10);
  const commit = (process.env.VERCEL_GIT_COMMIT_SHA || "").slice(0, 7);
  const version = commit ? `${hash} (Commit ${commit})` : hash;

  cache = {
    meta,
    raw,
    body: body.trim(),
    sections: sections.filter((s) => s.text),
    tokens: JSON.parse(tokensRaw),
    tokensRaw,
    version,
  };
  return cache;
}

export function guidelines({ medium = "all", section } = {}) {
  const c = load();
  let parts;
  if (section) {
    parts = c.sections.filter((s) => s.id === section);
    if (!parts.length) {
      return `Unbekannter Abschnitt "${section}". Verfügbar: ${c.sections.map((s) => s.id).join(", ")}`;
    }
  } else {
    const ids = MEDIA[medium] ?? null;
    parts = ids ? c.sections.filter((s) => ids.includes(s.id)) : c.sections;
  }
  return `${parts.map((s) => s.text).join("\n\n")}\n\n---\nCASI-CI, Stand ${c.version}. Abschnitte: ${c.sections
    .map((s) => s.id)
    .join(", ")}.`;
}

// Tokens als CSS-Custom-Properties.
export function tokensCss() {
  const { tokens, version } = load();
  const out = [`/* CASI Design Tokens – Stand ${version} – generiert aus ci/tokens.json */`, ":root {"];
  for (const [name, t] of Object.entries(tokens.color ?? {})) {
    const v = t.$extensions?.["org.casinitiative.cssVar"] || `--casi-${name}`;
    out.push(`  ${v}: ${t.$value}; /* ${t.$description ?? ""} */`);
  }
  for (const [name, t] of Object.entries(tokens.font ?? {})) {
    const val = Array.isArray(t.$value) ? t.$value.map((f) => (/\s/.test(f) ? `"${f}"` : f)).join(", ") : t.$value;
    out.push(`  --casi-font-${name}: ${val};`);
  }
  out.push("}");
  return out.join("\n");
}

// Vorlagen-Liste aus vorlagen/vorlagen.json
export function templates() {
  return JSON.parse(readFileSync(path.join(ROOT, "vorlagen", "vorlagen.json"), "utf8")).vorlagen;
}
