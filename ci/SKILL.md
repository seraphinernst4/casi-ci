---
name: "casi-skill"
description: "Corporate identity of CASI (casinitiative.org) and ICCA — slides, papers, Word/PDF, posters, social, web, charts, emails and newsletters. Two typefaces, website UI colours (extra colours for graphics), grey rounded boxes, official templates, author's text unchanged."
---

# CASI Corporate Identity

The look is the website casinitiative.org: white page, PP Mori and IBM Plex Serif, a few calm UI colours, light grey boxes with rounded corners, generous space.

**Always current version:** this file mirrors `ci/SKILL.md` in the GitHub repo `seraphinernst4/casi-ci`. If the CASI CI connector (`https://ci.casinitiative.org/mcp/…`) is available, prefer its `casi_ci_guidelines` and `casi_templates` tools – they always serve the latest rules and templates.

**Where things live:** everything people use is in the WordPress back end of casinitiative.org (login): the dashboard box "CASI-Werkzeuge" with the connector setup, the Mail-Baukasten (`/wp-admin/admin.php?page=casi-mailversand`), the Kachel-Baukasten (`/wp-admin/admin.php?page=casi-kacheln`) and all template downloads. `ci.casinitiative.org` is only the technical address for Claude (connector, downloads, brand assets); its pages forward to the back end.

## Two rules above all

**1. Less is more.** Dress the author's material in CASI type and boxes — add nothing for branding's sake. A plain page in the two typefaces is a correct CASI page. When unsure: leave it out.

**2. The author's text is untouchable.** Same words, spelling, case, punctuation, numbers, order. "CO2" stays "CO2" unless the source uses CO₂. Never add (taglines, kickers, titles, headers/footers, "Source:", numbering, notes), never remove or merge, never change case. Typos are listed in the reply, not fixed. Italics stay italic, bold becomes SemiBold, underlines go.

**German text always with ä, ö, ü, ß** – in documents, style names, labels, descriptions and read-me files. Plain ASCII (ae, oe, ue, ss) only in file names, internal IDs and URLs.

## Colour: the website's UI colours only

| Role | Hex |
|---|---|
| Page | `#FFFFFF` |
| Box, band | `#EEF2F1` |
| All text — headings and reading text (the website's `body`), hairlines, outline button | Deep Green `#0E4D49` |
| Secondary text (meta, captions, footnotes, page numbers, footer) | Slate `#5F7471` |
| Light rule | `#E1E7E5` |
| Box edge (white box on grey), divider inside a grey box | `#C5D4D3` |
| Filled button, current menu item, call to action | Burgundy `#8B1538` — at most twice per page |

These are the website's CSS tokens (`--papier`, `--block`, `--tinte`, `--leise`, `--linie`, `--akzent`, plus `#C5D4D3`). That is the whole palette for text, surfaces and UI. Links have no colour of their own — on the website they take the text colour; in emails and documents they are underlined in the colour of the text around them. Nothing else gets colour: no coloured numbers, bullets, bars or accents.

**Extra colours – graphics only.** The website's graphics have their own colours. They may be used in graphics, charts, diagrams, maps and illustrations (fills, lines, data marks), never for text, headings, buttons, boxes, backgrounds or decoration. Prefer taking the graphic itself from the website (see below) over rebuilding it.

| Group | Hex | Use |
|---|---|---|
| ICCA green | `#13917C` (UI, `--icca`), `#1A9C7E` (hero graphic) | ICCA marks and system diagrams |
| Burgundy tints | `#F6EBEF` light, `#CB96A6` mid | hero flow graphic |
| Value chain (fields with white text) | iron `#A75F26`, steel `#1A6685`, body `#17876F`, car `#2A7A4B`, end of life `#85499E`; own contribution white with hairline, text `#29363D` | value-chain graphics |
| Graphic neutrals | ink `#29363D`, secondary text in graphics `#54626A`, burgundy outline `#E3C2CD` | inside graphics only |
| Data / transaction markers A–J | `#B060E0` `#3060C0` `#2080B0` `#50B0D0` `#20C090` `#30A060` `#E08820` `#D06020` `#E04040` `#C04080` | categorical data, transaction markers |

Charts: start with Deep Green, then Slate, then tints of Deep Green (`#93AFAD`, `#C5D4D3`). If the author's data has more categories than that, use the data colours A–J in order. Labels on coloured fills: white or Deep Green, whichever has the stronger contrast. In the PowerPoint template all extra colours are under "Custom colours".

Contrast on white: Deep Green 9.65:1, Burgundy 9.28:1, Slate 4.97:1 — fine for text. Slate on the grey box only 4.41:1: there use Deep Green, or Slate from 14 pt semibold.

## Typography

| Typeface | Job |
|---|---|
| **IBM Plex Serif** | text read as sentences: paragraphs, footnotes, abstracts, quotations, references, web body text, running text on slides |
| **PP Mori** | everything that names, orders, counts or points: titles, headings, labels, metadata, captions, tables, figures, charts, navigation, buttons, slide titles and labels |

One typeface per element, never mixed in one paragraph or label. Weights: Regular 400, Italic, SemiBold 600 only. Set the typeface on every run — no inheritance.

- Fonts: `/wp-content/uploads/casi-fonts/` (PP Mori `.woff2`, `.fntdata` for PowerPoint; IBM Plex Serif `.woff2` – a subset without ₂ and →; for documents use the full IBM Plex Serif, OFL). PP Mori is commercial – CASI staff only, check the licence before passing files on.
- **Missing fonts:** the CASI templates embed both typefaces, so they display without installation. To install them, use the font package `CASI-Schriften.zip` (connector tool `casi_templates`, medium `fonts`): TTF from `Installieren/` for Office, OTF for InDesign/Illustrator, WOFF2 for web. When a user's file shows a substitute font, offer this download instead of switching to a fallback.
- PPTX: PP Mori on every run, embed the `.fntdata`. DOCX: styles set explicitly; recommend "embed fonts". PDF/HTML/PNG: embed or `@font-face`; never a system default.
- Fallbacks only if fonts are unavailable: PP Mori → Helvetica Neue; IBM Plex Serif → Georgia. Say so.
- CSS: `"PP Mori", "Helvetica Neue", Helvetica, Arial, sans-serif` · `"IBM Plex Serif", Georgia, serif`.

| Scale | Title | H1 | H2 | Body | Small (captions, meta, footnotes) |
|---|---|---|---|---|---|
| Website / email (px) | 44 (email 30) | 30 | 20 | 17 / 1.6 serif | 15 · 14 · 13 |
| Documents A4 (pt) | 27 | 18.5 | 12.5 | 10.5 / 1.6 serif | 9.5 kicker · 8.5 |
| Slides 16:9 (pt) | 17 (cover 40, section 30) | — | — | 12 / 1.35 serif | 7.5 |
| Posters A3 (pt; A1 = × 2) | 60 (conference poster 40) | — | 14 | 20 lead · 12 / 1.4 serif | 14 kicker · 10 |
| Social tiles (px at 1080) | 92 → 40, sized to fit | — | — | 34 / 1.4 serif (quote 64 → 30) | 28 kicker · 24 |

Headings SemiBold, body Regular — both Deep Green; small text Slate. Max five sizes per page. Ragged right, never justified. No letter-spacing except on text the author wrote in capitals (+0.08–0.18 em).

## Boxes and lines

- Box: `#EEF2F1`, corners 8 px (10 px large panels); or white with 1 px `#C5D4D3` where it sits on grey. No shadows, gradients, 3D, heavy borders. Boxes only where the author had a box, panel or shaded table.
- Text inside a grey box or on grey ground is always Deep Green – labels and small text too (Slate reaches only 4.41:1 on grey).
- Several items side by side (key figures, principles, steps) get one box each: separate boxes, same height, same gap – never one long box divided into columns.
- Lines only with meaning: sum lines, T-account rules, one rule under a table header. 1 px Deep Green (web), 0.5–0.75 pt (print). No bars, accent rules or rules under headings.
- Diagrams the author drew: grey/white boxes, PP Mori Deep Green, connectors `#93AFAD` meeting the box edges, no arrowheads unless direction is unclear (then an open chevron).

## Graphics: external stay, internal follow the website

**External graphics stay exactly as they are.** A figure from a third party – a source is named that is not CASI (e.g. "Source: WRI (1998)"), a partner's or a publication's chart, a photo, a screenshot – is not redrawn, recoloured, re-lettered or cropped. Only its caption is set in CASI style, in the author's wording.

**Internal graphics are redrawn in the style of the website graphics.** Everything CASI made itself – diagrams, schemes, charts, statements, process pictures, icons, also older CASI figures in a different look – follows the website's figures (`.abb`):
1. If the website already has this graphic: take it from there (Backend → Texte → Grafiken (PowerPoint)), never a copy of an older version.
2. Otherwise rebuild it with these rules:
   - **Type:** PP Mori only (labels are used, not read), one step smaller than the running text; box titles SemiBold; Deep Green, secondary text `#54626A`.
   - **Boxes:** `#EEF2F1` without outline, or white with a 1 px `#C5D4D3` edge (as in the website graphics); corners 10 px (small boxes 8 px); no shadows, gradients or 3D.
   - **Lines:** 1 px hairline Deep Green; connectors orthogonal, meeting box edges; small arrowheads only where direction matters.
   - **Symbols:** the website's line symbols (`https://ci.casinitiative.org/marke/symbole/`: direct emissions, direct removals, upstream emissions, CO2 ledger, CO2 balance sheet, net CO2 contribution, net CO2 flow, product carbon footprints – in Deep Green, white and Burgundy). A new symbol is drawn by the same rules: 24 × 24 grid, stroke 1.5 px, round caps and joins, no fill, simple geometric forms, one colour; it sits to the left of its label.
   - **Inputs and outputs:** inputs in Deep Green on grey; reports/outputs in Burgundy on `#F6EBEF` with `#CB96A6` hairline (as in the ICCA overview).
   - **Marks A–J:** small pills (radius 2 px, about 2:1), letter white SemiBold on the data colour = booked on accounts; outlined version (same size, coloured outline and letter) = read from accounts for reporting.
   - **Colours:** UI colours plus the extra colours above – nothing else.
3. Unclear whether a graphic is external or internal? Ask, do not guess.

## Website graphics, texts and resources

Host: `https://casinitiative.org` — all paths below are relative to it.

- **ICCA graphics as PowerPoint, always current:** Backend → Texte → Grafiken (PowerPoint) (`/wp-admin/admin.php?page=casi-grafiken`). Tick slides, download — editable native shapes, PP Mori embedded. For outsiders: "Link für Dritte" there. Use these instead of redrawing; if a deck has an outdated version, say so and offer the current one.
- **Texts:** every visible website text lives in Backend → **Texte** (`/wp-admin/admin.php?page=casi-texte`). New website-related material uses the terms exactly as there.
- **Logo:** the wordmark "CASI" `/wp-content/uploads/2026/07/LOGO.svg` (email: `/wp-content/uploads/casi-mail/casi-logo-mail-deepgreen.png`). In all CASI templates and emails the logo is Deep Green `#0E4D49` (documents, letters, slides, posters, tiles, mails, signature); only the website header keeps its black logo file; white only on Burgundy or dark ground. The short logo is the "C" of that wordmark alone: `https://ci.casinitiative.org/marke/casi-c-tinte.svg` (white: `casi-c-weiss.svg`, PNG next to it). Older C marks (a ring of fine dots) are no longer valid – never use them. Only where the source has a logo; clear space = height of the "C".
- Styles and scripts: `/wp-content/uploads/casi-css/`, `/wp-content/uploads/casi-js/`.

**Changing the website: every text into the register — always, unasked.** Every new or changed visible text (graphics, tiles, labels, buttons, alt texts, aria-labels, mails) goes into the register in the same step; a change is not finished before. Register: `casi_texte_code()` in `/wp-content/novamira-sandbox/casi-texte.php`, one line per text `'id' => array(gruppe, teil, label, standard, art)` (`art`: `zeile`, `satz`, `text`, `plain`, `attr`; labels German, in reading order). Output via `casi_t()` (HTML), `casi_tx()` (plain), `casi_ta()` (attribute). Same text in two places: own key via the `$folgt` list. Then check: visible in Backend → Texte, page unchanged, Elementor cache cleared.

## Email and newsletter

**Tools:** the Mail-Baukasten lives in the WordPress back end of the website: `https://casinitiative.org/wp-admin/admin.php?page=casi-mailversand` (menu "Mail-Baukasten", login with the right `edit_posts`). It builds signatures and complete mails (presets: newsletter, invitation, announcement, short round mail, personal mail with CASI header) from blocks and sends them directly. Old links to `ci.casinitiative.org/mail/` forward there. HTML templates via `casi_templates` (medium `email`): `CASI-Newsletter-Vorlage.html`, `CASI-Einladung-Vorlage.html`, `CASI-Ankuendigung-Vorlage.html`, `CASI-Rundmail-Vorlage.html`, `CASI-Signatur-Vorlage.html`. News and events come live from `https://casinitiative.org/wp-json/casi/v1/news?anzahl=12` (fields zeile, titel, text, link, rubrik, datum) – never typed by hand.

**Sending:** in the section "Versand" of the Mail-Baukasten, through the CASI mail server (IONOS), exactly as designed – the standard way, because pasting into a mail program loses styles and the phone layout. Sender info@casinitiative.org (website mailbox, WP Mail SMTP) or a personal @casinitiative.org mailbox an administrator sets up under "Mail-Baukasten → Postfächer" (IONOS password, stored encrypted, checked on saving); recipients as BCC (max. 300 per send, in packets of 40); "Testmail senden" is optional and always goes to info@casinitiative.org; a log of every send is under "Postfächer". "Mail kopieren" and "HTML herunterladen" remain as fallbacks. Source in the repo: `wordpress/casi-mailversand.php` and `wordpress/casi-mailbaukasten.html`; live in `/wp-content/novamira-sandbox/` – deploy both after every change (Vercel does not deploy them).

**Phones:** long words and links must wrap (`overflow-wrap:anywhere; word-break:break-word` on text cells); nothing may make the mail wider than 320 px.

**For AI agents:** whenever you draft an email for CASI / ICCA people – also a normal personal mail or reply – offer on your own to set it in the CASI mail header and create a pre-filled link with the connector tool `casi_mail_link` (personal mails: `vorlage: "nachricht"`, with a `gruss` block for closing and sender). For signatures use `casi_signatur_link`. Rule for all CASI web tools: hand over a pre-filled link, never only tell people where to type things in.

**Semibold in mails:** always by the font's own name, not only by weight – `font-family:'PP Mori Semibold','PP Mori','Helvetica Neue',Helvetica,Arial,sans-serif; font-weight:600`, with `@font-face` for both names. Apple Mail otherwise turns 600 into a fake bold or drops it word by word when a mail is pasted.

**Mail blocks** (all inside the 600 px frame, 40 px between blocks):
- Kicker above the title (e.g. "Newsletter · October 2026", "Invitation", "Publication"): PP Mori 13 px Slate, 56 px below the logo; title follows 12 px below.
- Article: line (rubric) 13 px Slate · title PP Mori SemiBold 20 px, linked if there is a target · optional image 520 px wide, 10 px corners · long text · text link "Read more on casinitiative.org" PP Mori 15 px underlined.
- Long text: IBM Plex Serif 17 px / 1.6, paragraphs 16 px apart; subheadings PP Mori SemiBold 17 px (28 px above); lists as table rows with "–" and hanging text; links underlined in Deep Green. Long mails are fine – structure them with subheadings, never with colour, bold blocks or boxes.
- Box with entries: as the confirmation mail (grey box, label 14 px, entries separated by 1 px #C5D4D3).
- Event box: grey box, event name SemiBold 17 px, rows label 13 px / value 15 px, separated by 1 px #C5D4D3.
- Button: Burgundy #8B1538, 8 px corners, PP Mori SemiBold 15 px white, padding 13 × 22 px – at most two per mail.
- Image: only the author's own or licensed images, 520 px, 10 px corners, caption 13 px Slate.
- Closing and sender (personal mails): greeting IBM Plex Serif 17 px, name PP Mori SemiBold 15 px, function and contact 13 px Slate – no second logo. Personal mails have no unsubscribe line.

**Signature:** name PP Mori SemiBold 14 px Deep Green; function (· institution) 13 px Slate; logo PNG 84 × 28 px in Deep Green linked to the start page; then 12 px Slate: "Carbon Accounting Standards Initiative · casinitiative.org", phone · e-mail. Nothing else – no quotes, banners, social icons, extra colours or images.

Model: the newsletter confirmation mail (`/wp-content/novamira-sandbox/casi-newsletter-mail.php`; preview `/wp-admin/admin-post.php?action=casi_nl_vorschau`, test mail to yourself `…?action=casi_nl_test`). Every CASI mail copies it — layout, sizes and colours — and changes only the heading, the sentence and the entries.

**Mail colours — the UI colours only:** all text inside the page and the box Deep Green `#0E4D49` (Slate reaches only 4.41:1 on the grey box, so label and meta lines in the box are Deep Green too); footer on white Slate `#5F7471`; links underlined in the colour of their text; box `#EEF2F1`, dividers `#C5D4D3`; page white.

**Layout (top to bottom)**
1. Logo PNG 84 × 28 px in Deep Green, linked to the start page.
2. Heading PP Mori SemiBold 30 px / 1.15 Deep Green (26 px on phones), 56 px space above.
3. Sentence IBM Plex Serif 17 px / 1.6 Deep Green, 40 px space below.
4. Content box: `#EEF2F1`, 10 px corners, padding 24 px. Label PP Mori 14 px Deep Green. Entries 16 px top and bottom, separated by 1 px `#C5D4D3`, each: meta line (rubric · date) PP Mori 13 px Deep Green → title PP Mori SemiBold 17 px / 1.35 Deep Green as a link → text IBM Plex Serif 15 px / 1.55 Deep Green.
5. Footer PP Mori 13 px / 1.55 Slate `#5F7471`, 44 px space above: sender · casinitiative.org — why this mail + how to unsubscribe — Impressum; links Slate, underlined.

**Linking website content — the point of the mail**
- Entries are pulled live from the website (as `casi_nl_news()` takes the three newest News exactly as on the start page) — never copied by hand, so mail and site never disagree.
- Every entry links to the website: the title is the link (Deep Green, no underline, underlined on hover), pointing to where the entry lives on the website — News to `/news/` as in the confirmation mail; an entry with its own target (a publication, an event) to that target. Links inside entry texts stay — Deep Green, underlined.
- URLs absolute, built with `home_url()` / `content_url()` so they follow the domain.
- The plain-text version lists the same entries followed by the URL.

**Technical rules**
- 600 px table layout, `role="presentation"`, all styles inline; padding 44 px 40 px (32 px 22 px on phones).
- Fonts via `@font-face` from `/wp-content/uploads/casi-fonts/` (Apple Mail shows them; Gmail/Outlook fall back to Helvetica/Georgia — that is accepted).
- `color-scheme: light`; hidden preheader = the sentence; always a plain-text alternative.
- Headers: `Reply-To: info@casinitiative.org`, `List-Unsubscribe`.
- All mail texts in the Texte register (Auf allen Seiten → Formulare → …), keys like `mail.nl.*`; subject, heading and sentence included.
- A test mail ("Testmail senden" in the Mail-Baukasten, goes to info@casinitiative.org) is recommended before big sends, but not required.

## Slides

**Template:** `CASI-Folien.potx` (connector tool `casi_templates`). Start every deck from it and pick the layout per slide: Titel, Abschnitt, Inhalt, Nur Titel, Zwei Spalten, Text mit Box, Zwei Boxen, Abbildung, Schluss, Leer. PP Mori and IBM Plex Serif are embedded.

16:9, 13.333 × 7.5 in, white. Margins 0.67 in; content y 1.05–7.0. Title (only if the author has one) PP Mori 17 pt SemiBold Deep Green at (0.67, 0.54), w 11.99. Running text IBM Plex Serif 12 pt / 1.35 Deep Green, paragraphs 6 pt apart; labels inside running text (a term above its explanation) PP Mori SemiBold as their own paragraph. Page number PP Mori 7.5 pt Slate right-aligned at y 7.07. No logo on content slides – the "C" appears only on cover and closing.

Boxes on slides: layouts "Text mit Box" (running text left, box 4.2 in wide right) and "Zwei Boxen". `#EEF2F1`, corner radius 0.1 in on all four corners, padding 0.3 in, top-aligned at y 1.05, as tall as their text (they grow while typing) – never as large empty panels. Boxes side by side get the same height (the taller one). Only where the author had a box, panel or highlighted passage. When generating a file, set the box height to fit the text (IBM Plex Serif 12 pt at 135 % ≈ 0.27 in per line, plus 0.6 in padding and one spare line) and the radius per box with adj = 0.1 in / min(w, h) × 100000.

Cover: "C" at (0.67, 0.54), height 0.55 in; kicker PP Mori SemiBold 10 pt (author's capitals, +0.08 em) at y 2.2; title 40 pt at (0.67, 2.62); subtitle PP Mori 14 pt Slate at y 4.55; sender · date PP Mori 9 pt Slate at y 6.7. Section divider: kicker as on the cover, title 30 pt at (0.67, 2.62). Closing: Burgundy panel left (w 4.6 in, full height), white "C" and closing sentence (PP Mori SemiBold 24 pt white) in it; contact PP Mori 12 pt on the right — texts from the user.

python-pptx: set `run.font.name` on every run; rounded corners via `roundRect` adj = radius / min(w, h) × 100000; no shadows (`a:effectLst` empty).

## Documents

**Templates** (connector tool `casi_templates`, medium `document`): `CASI-Whitepaper.dotx` – the set of CASI Whitepaper No. 1, for whitepapers and papers; `CASI-Dokument.dotx` – reports, minutes, memos; `CASI-Brief.dotx` – letters; `CASI-Factsheet.dotx` – one-page factsheets. Start every document from one of them and use their styles only:

| Style | Use | Set |
|---|---|---|
| CASI Reihe | series · number on the cover (shown in capitals, typed normally) | PP Mori SemiBold 9.5 pt |
| CASI Titel | title | PP Mori SemiBold 27 pt |
| CASI Vorspann | abstract on the cover | IBM Plex Serif 10.5 pt Slate |
| CASI Meta | authors, publisher · date | PP Mori 8.5 pt Slate |
| CASI Kicker | small line above a chapter heading (Foreword, Section 1, Bibliography, Imprint) | PP Mori SemiBold 9.5 pt |
| CASI Überschrift 1 / 2 / 3 | headings (number and tab before the text if the author numbered) | PP Mori SemiBold 18.5 / 12.5 / 10.5 pt |
| CASI Fließtext | running text | IBM Plex Serif 10.5 pt / 1.6 |
| CASI Liste | list item: "—", tab, text | IBM Plex Serif 10.5 pt, hanging indent |
| CASI Abbildung / CASI Bildunterschrift | figure / caption ("Figure N" SemiBold Deep Green, then the author's caption) | PP Mori 8.5 pt Slate |
| CASI Literatur | references | IBM Plex Serif 9.5 pt |
| CASI Fußnote | footnotes | IBM Plex Serif 8.5 pt |
| CASI Tabelle / CASI Tabellentext | tables: no grid, one Deep Green rule under the header row, header SemiBold, numbers right-aligned | PP Mori 9 pt |

A4, margins 25 mm top/bottom, 22 mm left/right. Cover: long logo, hairline, series, title, abstract, authors, publisher · date, contents (automatic, no page numbers). Running header from the cover (series · title) above a hairline `#E1E7E5`; footer "Carbon Accounting Standards Initiative · casinitiative.org" and page number. Every chapter starts on a new page with its kicker. Headings: the author's levels, no numbering unless the author numbered. Tables: author's structure; a shaded table becomes one grey box; inside only the header rule and sum lines; numbers right-aligned. External figures unchanged, internal figures in the website graphic style (see Graphics); captions in the author's wording and position. Print: export as PDF from Word (fonts are embedded).

**Letters** (`CASI-Brief.dotx`): written in English. DIN 5008 form B for window envelopes. Margins 36 mm top, 22 mm left and right, as in the other documents. First page: long logo top left at exactly the same place as in Dokument, Whitepaper and Factsheet (25 mm from the top, 22 mm text edge); sender line PP Mori 7 pt Slate above the address field (45 mm from top, 80 × 45 mm), "CASI · University of Mannheim · Schloss Ostflügel · 68161 Mannheim"; address PP Mori 8.5 pt (recipient, organisation, street, postcode city, country if abroad); information block from 125 mm (Date, Contact, Email: label Slate, value below; date as "16 October 2026"); subject CASI Überschrift 2 at about 103 mm; salutation ("Dear …,"), text and closing ("Kind regards,") in CASI Fließtext; name and function CASI Meta. Footer of the first page: the sender as in the website imprint, in English (Carbon Accounting Standards Initiative (CASI) · Mannheim Institute for Sustainable Energy Studies (MISES) · University of Mannheim · Schloss Ostflügel, Room O 351–359 · 68161 Mannheim · Germany · casinitiative.org); following pages: page number only.

**Factsheets** (`CASI-Factsheet.dotx`): A4, one page. Long logo and hairline as in the document template; CASI Reihe ("Factsheet · topic"), CASI Titel (6 pt less space after), CASI Vorspann; up to three key figures, each in its own grey box (three separate rounded boxes, corners 2.5 mm, 5 mm apart, all 42 mm high; number "CASI Kennzahl" PP Mori SemiBold 24 pt, meaning "CASI Kennzahltext" Deep Green below, at most four lines; numbers only with a source); then running text in two columns (CASI Überschrift 2, CASI Fließtext, CASI Liste) ending with the contact (CASI Kicker "Contact", CASI Meta). If it does not fit on one page, shorten with the author – never shrink type.

## Other media

**Posters** (`CASI-Plakat-A3.potx`, `CASI-Plakat-A1.potx`, connector tool `casi_templates`, medium `poster`): portrait, white, margins 18 mm (A3) / 36 mm (A1); A1 is A3 × 2 in every measure, so an A1 file prints correctly scaled on A3. Wordmark top left (height 0.42 in on A3); footer "Carbon Accounting Standards Initiative · casinitiative.org" PP Mori Slate bottom left. Layouts:
- *Plakat* (event, announcement, publication): kicker PP Mori SemiBold 14 pt (author's capitals, +0.08 em), title PP Mori SemiBold 60 pt, lead IBM Plex Serif 20 pt, picture or internal graphic, grey info box at the bottom (corners 0.14 in on A3) with three fields: label PP Mori 11 pt Deep Green (Slate is too weak on grey), value PP Mori SemiBold 15 pt. Wordmark in Deep Green top left.
- *Poster (Konferenz)*: kicker 12 pt, title 40 pt, authors · institution PP Mori 14 pt Slate, running text IBM Plex Serif 12 pt / 1.4 in two columns (A3) or three (A1), subheadings PP Mori SemiBold 14 pt as their own paragraph, figures with caption PP Mori 9 pt Slate.
- *Leer*: only wordmark and footer.
Print: export as PDF from PowerPoint (fonts are embedded); no bleed needed – the white page is the ground.

**Social media tiles:** the Kachel-Baukasten in the WordPress back end `https://casinitiative.org/wp-admin/admin.php?page=casi-kacheln` (connector tool `casi_kachel_link` opens it pre-filled). Formats: LinkedIn post 4:5 (1080 × 1350), square 1:1 (1080 × 1080), link image 1200 × 627. Motifs: statement/announcement, quote, key figure (with source), event (grey box with rows), image with title (own or licensed images only). Ground white or `#EEF2F1`; wordmark in Deep Green top left (40 px at 1080), "casinitiative.org" PP Mori 24 px bottom left; margins 80 px; text block sits at the bottom above the footer; title PP Mori SemiBold sized to fit (92 → 40 px), kicker PP Mori 28 px; small text Slate on white, Deep Green on grey ground and in grey boxes; sentence and quote IBM Plex Serif. No colour fields, no Burgundy areas, no stock decoration, no hashtags on the image. Always give an alt text (the builder suggests one).

**Colours and fonts in other programs:** `CASI.thmx` – Office theme (Word, PowerPoint, Excel: Design → Themes → Browse) with the UI colours as theme colours, the extra colours as custom colours, headings PP Mori Semibold and body PP Mori; `CASI-Farben.ase` – swatches for Illustrator, InDesign and Photoshop (groups "UI colours" and "extra colours – graphics only"). Fonts: `CASI-Schriften.zip`.

Web: as the website (reading text 17 px serif, links in the text colour). Charts: white or grey ground, no border/3D/shadow, PP Mori, direct labels, gridlines only if values must be read, colours per the palette above.

## Check before delivering

1. Text identical to the source; nothing added or removed.
2. Right typeface per element, set on every run; Regular/Italic/SemiBold only.
3. Text, surfaces and UI only in the UI colours, in emails too; extra colours only in graphics and charts.
4. Boxes grey or white-edged, 8/10 px corners, only where the author had them; lines only with meaning.
5. External graphics untouched; internal graphics in the website graphic style with the website symbols.
6. Emails: content linked to the website with absolute URLs, plain-text version.
7. Website changes: every visible text editable in Backend → Texte.