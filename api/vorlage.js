// Liefert eine Vorlage aus vorlagen/ aus – nur mit dem Wort aus der Connector-Adresse.
// Adresse: /vorlagen/<WORT>/<Datei>
import { readFileSync, existsSync } from "node:fs";
import path from "node:path";

const TYPES = {
  ".potx": "application/vnd.openxmlformats-officedocument.presentationml.template",
  ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
  ".dotx": "application/vnd.openxmlformats-officedocument.wordprocessingml.template",
  ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  ".thmx": "application/vnd.ms-officetheme",
  ".pdf": "application/pdf",
  ".html": "text/html; charset=utf-8",
  ".png": "image/png",
  ".zip": "application/zip",
};

export default function handler(req, res) {
  const url = new URL(req.url || "/", "http://localhost");
  const m = url.pathname.match(/\/vorlagen\/([^/]+)\/([^/]+)$/);
  const key = req.query?.key ?? m?.[1] ?? "";
  const file = decodeURIComponent(req.query?.file ?? m?.[2] ?? "");
  const expected = process.env.CI_ACCESS_KEY;
  const list = JSON.parse(readFileSync(path.join(process.cwd(), "vorlagen", "vorlagen.json"), "utf8")).vorlagen;
  const known = list.some((v) => v.datei === file);
  const p = path.join(process.cwd(), "vorlagen", path.basename(file));
  if ((expected && key !== expected) || !known || !existsSync(p)) {
    res.statusCode = 404;
    return res.end("Not found");
  }
  res.setHeader("Content-Type", TYPES[path.extname(p).toLowerCase()] || "application/octet-stream");
  res.setHeader("Content-Disposition", `attachment; filename="${path.basename(p)}"`);
  res.setHeader("Cache-Control", "no-store");
  res.end(readFileSync(p));
}
