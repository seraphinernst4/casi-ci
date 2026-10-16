# CASI CI Connector

Stellt die Corporate Identity von CASI als **MCP-Connector** bereit. Jede KI, die MCP spricht (Claude, ChatGPT, Cursor, Copilot …), bekommt damit immer den aktuellen Stand.

## Die einzige Quelle

| Datei | Inhalt |
|---|---|
| `ci/SKILL.md` | Die komplette CI: Regeln, Farben, Typografie, Folien, Dokumente, Mails … (identisch mit dem CASI-Skill) |
| `ci/tokens.json` | Farben, Schriften, Radien, Logo-URLs maschinenlesbar (W3C-Design-Token-Format) |

**Nur diese zwei Dateien ändern.** Alles andere ist Technik.

## CI ändern

1. `ci/SKILL.md` (und ggf. `ci/tokens.json`) auf GitHub bearbeiten – direkt im Browser über das Stift-Symbol.
2. „Commit changes“ auf `main`.
3. Vercel baut automatisch neu (ca. 1 Minute). Danach haben **alle** den neuen Stand – niemand muss etwas aktualisieren.

Vor jedem Deployment prüft `npm run check`, ob jede Farbe in beiden Dateien steht. Passt etwas nicht, bricht Vercel ab und der letzte gute Stand bleibt live. Die Fehlermeldung steht im Vercel-Build-Log.

Wenn du den CASI-Skill in Claude änderst: denselben Text hier in `ci/SKILL.md` einfügen (oder umgekehrt), damit beides gleich bleibt.

## Einrichten (pro Person, einmalig)

**Claude (Web/Desktop):** Einstellungen → Connectors → *Benutzerdefinierten Connector hinzufügen* → Name „CASI CI“, URL `https://<projekt>.vercel.app/mcp/<SCHLÜSSEL>`.
Im Chat dann z. B.: „Mach mir Folien im CASI-Design“ – Claude ruft die CI selbst ab.

**Claude Code:** `claude mcp add --transport http casi-ci https://<projekt>.vercel.app/mcp/<SCHLÜSSEL>`

**Andere Tools (Cursor, ChatGPT, Copilot …):** dieselbe URL als „Remote MCP Server / Streamable HTTP“ eintragen.

## Was der Connector kann

| Tool | Zweck |
|---|---|
| `casi_ci_guidelines` | CI als Text – komplett, pro Medium (`slides`, `document`, `email`, `website`, `chart`, `poster`, `social`) oder pro Abschnitt |
| `casi_design_tokens` | Tokens als JSON oder CSS-Variablen (für Code) |

Dazu die Ressourcen `casi://ci/SKILL.md`, `casi://ci/tokens.json` und den Prompt `casi-ci`.

## Zugang

Die URL enthält einen Schlüssel (`CI_ACCESS_KEY`, Vercel → Settings → Environment Variables). Ohne ihn antwortet der Server mit 404.
Neuer Schlüssel: Wert dort ändern → Redeploy → neue URL an alle verteilen.

## Lokal testen

```
npm install
npm test
```
