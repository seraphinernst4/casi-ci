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

Einen eigenen CASI-Skill in Claude braucht es nicht mehr – der Connector liefert immer diesen Stand.

## Einrichten (pro Person, einmalig)

**Claude (Web/Desktop):** auf claude.ai „Customize“ → „Connectors“ → „+ Add“ → „Add custom connector“ → Name „CASI CI“, URL `https://ci.casinitiative.org/mcp/CasimirMonnem`, „No sign in“ → „Add“. Im Chat über „+“ → „Connectors“ einschalten.
Im Chat dann z. B.: „Mach mir Folien im CASI-Design“ – Claude ruft die CI selbst ab.

**Claude Code:** `claude mcp add --transport http casi-ci https://ci.casinitiative.org/mcp/CasimirMonnem`

**Andere Tools (Cursor, ChatGPT, Copilot …):** dieselbe URL als „Remote MCP Server / Streamable HTTP“ eintragen.

## Was der Connector kann

| Tool | Zweck |
|---|---|
| `casi_ci_guidelines` | CI als Text – komplett, pro Medium (`slides`, `document`, `email`, `website`, `chart`, `poster`, `social`) oder pro Abschnitt |
| `casi_design_tokens` | Tokens als JSON oder CSS-Variablen (für Code) |
| `casi_templates` | Offizielle Vorlagen mit Download-Link |
| `casi_mail_link` | Link, der den Mail-Baukasten im Backend fertig ausgefüllt öffnet (Newsletter, Einladung, Ankündigung, Rundmail, persönliche Mail) |
| `casi_signatur_link` | Link zur vorausgefüllten Signatur im Mail-Baukasten |
| `casi_kachel_link` | Link, der den Kachel-Baukasten im Backend fertig ausgefüllt öffnet |

Dazu die Ressourcen `casi://ci/SKILL.md`, `casi://ci/tokens.json` und den Prompt `casi-ci`.

## Zugang

Die Adresse endet auf ein festes Wort (`CI_ACCESS_KEY` in Vercel → Settings → Environment Variables, derzeit `CasimirMonnem`). Ohne das Wort antwortet der Server mit 404 – so ist die CI nicht für jeden auffindbar, der die Domain kennt.
Wort ändern: Wert dort ändern → Redeploy → neue Adresse an alle verteilen.

Domain `ci.casinitiative.org`: CNAME `ci` → `cc65b2ebf437c988.vercel-dns-017.com` bei IONOS.
Das Wort steht auch in `wordpress/casi-werkzeuge.php` (Dashboard-Kasten und Vorlagenliste) – bei einer Änderung dort mitändern.

## Teil im WordPress-Backend

Was Menschen benutzen, liegt im Backend von casinitiative.org (Login), ci.casinitiative.org ist nur die Technik-Adresse für Claude; ihre Seiten leiten ins Backend weiter.

| Datei (Repo `wordpress/`) | Zweck |
|---|---|
| `casi-mailversand.php` | Menü „Mail-Baukasten“: Baukasten, Versand über IONOS (Absender info@ oder eigenes Postfach, BCC, Testmail möglich), Unterseite „Postfächer“ mit Protokoll |
| `casi-mailbaukasten.html` | der Mail-Baukasten selbst (wird von `casi-mailversand.php` ausgeliefert) |
| `casi-werkzeuge.php` | Menü „Kachel-Baukasten“ und Dashboard-Kasten „CASI-Werkzeuge“ (Einrichtung, Baukästen, Vorlagen live vom Connector) |
| `casi-kachelbaukasten.html` | der Kachel-Baukasten selbst |

Live liegen die Dateien in `/wp-content/novamira-sandbox/` und werden automatisch geladen. **Vercel spielt sie nicht aus** – nach jeder Änderung hochladen und die Prüfsumme vergleichen. Schriften und Logos kommen aus `/wp-content/uploads/casi-fonts/`, `/casi-marke/` und `/casi-mail/`.

## Lokal testen

```
npm install
npm test
```
