# CASI CI Connector

Stellt die Corporate Identity von CASI als **MCP-Connector** bereit. Jede KI, die MCP spricht (Claude, ChatGPT, Cursor, Copilot …), bekommt damit immer den aktuellen Stand.

## Die einzige Quelle

| Datei | Inhalt |
|---|---|
| `ci/SKILL.md` | Die komplette CI: Regeln, Farben, Typografie, Folien, Dokumente, Mails … (identisch mit dem CASI-Skill) |
| `ci/tokens.json` | Farben, Schriften, Radien, Logo-URLs maschinenlesbar (W3C-Design-Token-Format) |

**Nur diese zwei Dateien ändern.** Alles andere ist Technik.

## Vorlagen

Liegen in `vorlagen/` und stehen in `vorlagen/vorlagen.json`. Der Connector listet sie mit `casi_templates` und gibt Download-Links (`/vorlagen/<WORT>/<Datei>`) aus.
Die Quellen (Bau-Skripte) liegen in `vorlagen-quellen/`. PowerPoint neu bauen:

```
node vorlagen-quellen/pptx/build.cjs vorlagen
python3 vorlagen-quellen/pptx/finish.py vorlagen <Ordner mit den CASI-Schriften (TTF)>
```

Die Schriftdateien selbst liegen nicht im Repo (PP Mori ist lizenzpflichtig) – sie kommen aus `CASI-Schriften.zip`.

## CI ändern

1. `ci/SKILL.md` (und ggf. `ci/tokens.json`) auf GitHub bearbeiten – direkt im Browser über das Stift-Symbol.
2. „Commit changes“ auf `main`.
3. Vercel baut automatisch neu (ca. 1 Minute). Danach haben **alle** den neuen Stand – niemand muss etwas aktualisieren.

Vor jedem Deployment prüft `npm run check`, ob jede Farbe in beiden Dateien steht. Passt etwas nicht, bricht Vercel ab und der letzte gute Stand bleibt live. Die Fehlermeldung steht im Vercel-Build-Log.

Wenn du den CASI-Skill in Claude änderst: denselben Text hier in `ci/SKILL.md` einfügen (oder umgekehrt), damit beides gleich bleibt.

## Einrichten (pro Person, einmalig)

**Claude (Web/Desktop):** Einstellungen → Connectors → *Benutzerdefinierten Connector hinzufügen* → Name „CASI CI“, URL `https://ci.casinitiative.org/mcp/CasimirMonnem`.
Im Chat dann z. B.: „Mach mir Folien im CASI-Design“ – Claude ruft die CI selbst ab.

**Claude Code:** `claude mcp add --transport http casi-ci https://ci.casinitiative.org/mcp/CasimirMonnem`

**Andere Tools (Cursor, ChatGPT, Copilot …):** dieselbe URL als „Remote MCP Server / Streamable HTTP“ eintragen.

## Was der Connector kann

| Tool | Zweck |
|---|---|
| `casi_ci_guidelines` | CI als Text – komplett, pro Medium (`slides`, `document`, `email`, `website`, `chart`, `poster`, `social`) oder pro Abschnitt |
| `casi_design_tokens` | Tokens als JSON oder CSS-Variablen (für Code) |
| `casi_templates` | Offizielle Vorlagen mit Download-Link |

Dazu die Ressourcen `casi://ci/SKILL.md`, `casi://ci/tokens.json` und den Prompt `casi-ci`.

## Zugang

Die Adresse endet auf ein festes Wort (`CI_ACCESS_KEY` in Vercel → Settings → Environment Variables, derzeit `CasimirMonnem`). Ohne das Wort antwortet der Server mit 404 – so ist die CI nicht für jeden auffindbar, der die Domain kennt.
Wort ändern: Wert dort ändern → Redeploy → neue Adresse an alle verteilen.

Domain `ci.casinitiative.org`: CNAME `ci` → `cc65b2ebf437c988.vercel-dns-017.com` bei IONOS.

## Lokal testen

```
npm install
npm test
```
