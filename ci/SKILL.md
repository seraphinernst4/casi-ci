---
name: "casi-skill"
description: "Corporate identity of CASI (casinitiative.org) and ICCA — slides, papers, Word/PDF, posters, social, web, charts, emails and newsletters. Two typefaces, website UI colours only, grey rounded boxes, author's text unchanged."
---

# CASI Corporate Identity

The look is the website casinitiative.org: white page, PP Mori and IBM Plex Serif, a few calm UI colours, light grey boxes with rounded corners, generous space.

## Two rules above all

**1. Less is more.** Dress the author's material in CASI type and boxes — add nothing for branding's sake. A plain page in the two typefaces is a correct CASI page. When unsure: leave it out.

**2. The author's text is untouchable.** Same words, spelling, case, punctuation, numbers, order. "CO2" stays "CO2" unless the source uses CO₂. Never add (taglines, kickers, titles, headers/footers, "Source:", numbering, notes), never remove or merge, never change case. Typos are listed in the reply, not fixed. Italics stay italic, bold becomes SemiBold, underlines go.

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
| Value chain | direct `#29363D`, iron `#8C5A3C`, steel `#5B7C99`, car `#3F6B3F`, body `#0E8388`, end of life `#6B4C6E` | value-chain graphics |
| Data / transaction markers A–J | `#B060E0` `#3060C0` `#2080B0` `#50B0D0` `#20C090` `#30A060` `#E08820` `#D06020` `#E04040` `#C04080` | categorical data, transaction markers |

Charts: start with Deep Green, then Slate, then tints of Deep Green (`#93AFAD`, `#C5D4D3`). If the author's data has more categories than that, use the data colours A–J in order. Labels on coloured fills: white or Deep Green, whichever has the stronger contrast. In the PowerPoint template all extra colours are under "Custom colours".

Contrast on white: Deep Green 9.65:1, Burgundy 9.28:1, Slate 4.97:1 — fine for text. Slate on the grey box only 4.41:1: there use Deep Green, or Slate from 14 pt semibold.

## Typography

| Typeface | Job |
|---|---|
| **IBM Plex Serif** | text read as sentences: paragraphs, footnotes, abstracts, quotations, references, web body text, running text on slides |
| **PP Mori** | everything that names, orders, counts or points: titles, headings, labels, metadata, captions, tables, figures, charts, navigation, buttons, slide titles and labels |

One typeface per element, never mixed in one paragraph or label. Weights: Regular 400, Italic, SemiBold 600 only. Set the typeface on every run — no inheritance.

- Fonts: `/wp-content/uploads/casi-fonts/` (PP Mori `.woff2`, `.fntdata` for PowerPoint; IBM Plex Serif `.woff2` — a subset without ₂ and →; for documents use the full IBM Plex Serif, OFL). PP Mori is commercial — check the licence before passing files on.
- PPTX: PP Mori on every run, embed the `.fntdata`. DOCX: styles set explicitly; recommend "embed fonts". PDF/HTML/PNG: embed or `@font-face`; never a system default.
- Fallbacks only if fonts are unavailable: PP Mori → Helvetica Neue; IBM Plex Serif → Georgia. Say so.
- CSS: `"PP Mori", "Helvetica Neue", Helvetica, Arial, sans-serif` · `"IBM Plex Serif", Georgia, serif`.

| Scale | Title | H1 | H2 | Body | Small (captions, meta, footnotes) |
|---|---|---|---|---|---|
| Website / email (px) | 44 (email 30) | 30 | 20 | 17 / 1.6 serif | 15 · 14 · 13 |
| Documents A4 (pt) | 24–28 | 14 | 11 | 10 / 1.45 serif | 8.5 · 8 |
| Slides 16:9 (pt) | 17 (cover 40, section 30) | — | — | 12 / 1.35 serif | 7.5 |

Headings SemiBold, body Regular — both Deep Green; small text Slate. Max five sizes per page. Ragged right, never justified. No letter-spacing except on text the author wrote in capitals (+0.08–0.18 em).

## Boxes and lines

- Box: `#EEF2F1`, corners 8 px (10 px large panels); or white with 1 px `#C5D4D3` where it sits on grey. No shadows, gradients, 3D, heavy borders. Boxes only where the author had a box, panel or shaded table.
- Lines only with meaning: sum lines, T-account rules, one rule under a table header. 1 px Deep Green (web), 0.5–0.75 pt (print). No bars, accent rules or rules under headings.
- Diagrams the author drew: grey/white boxes, PP Mori Deep Green, connectors `#93AFAD` meeting the box edges, no arrowheads unless direction is unclear (then an open chevron).

## Website graphics, texts and resources

Host: `https://casinitiative.org` — all paths below are relative to it.

- **ICCA graphics as PowerPoint, always current:** Backend → Texte → Grafiken (PowerPoint) (`/wp-admin/admin.php?page=casi-grafiken`). Tick slides, download — editable native shapes, PP Mori embedded. For outsiders: "Link für Dritte" there. Use these instead of redrawing; if a deck has an outdated version, say so and offer the current one.
- **Texts:** every visible website text lives in Backend → **Texte** (`/wp-admin/admin.php?page=casi-texte`). New website-related material uses the terms exactly as there.
- **Logo:** the wordmark "CASI" `/wp-content/uploads/2026/07/LOGO.svg` (email: `/wp-content/uploads/casi-mail/casi-logo-mail.png`). The short logo is the "C" of that wordmark alone: `https://ci.casinitiative.org/marke/casi-c-tinte.svg` (white: `casi-c-weiss.svg`, PNG next to it). Older C marks (a ring of fine dots) are no longer valid – never use them. Only where the source has a logo; clear space = height of the "C".
- Styles and scripts: `/wp-content/uploads/casi-css/`, `/wp-content/uploads/casi-js/`.

**Changing the website: every text into the register — always, unasked.** Every new or changed visible text (graphics, tiles, labels, buttons, alt texts, aria-labels, mails) goes into the register in the same step; a change is not finished before. Register: `casi_texte_code()` in `/wp-content/novamira-sandbox/casi-texte.php`, one line per text `'id' => array(gruppe, teil, label, standard, art)` (`art`: `zeile`, `satz`, `text`, `plain`, `attr`; labels German, in reading order). Output via `casi_t()` (HTML), `casi_tx()` (plain), `casi_ta()` (attribute). Same text in two places: own key via the `$folgt` list. Then check: visible in Backend → Texte, page unchanged, Elementor cache cleared.

## Email and newsletter

Model: the newsletter confirmation mail (`/wp-content/novamira-sandbox/casi-newsletter-mail.php`; preview `/wp-admin/admin-post.php?action=casi_nl_vorschau`, test mail to yourself `…?action=casi_nl_test`). Every CASI mail copies it — layout, sizes and colours — and changes only the heading, the sentence and the entries.

**Mail colours — the UI colours only:** all text inside the page and the box Deep Green `#0E4D49` (Slate reaches only 4.41:1 on the grey box, so label and meta lines in the box are Deep Green too); footer on white Slate `#5F7471`; links underlined in the colour of their text; box `#EEF2F1`, dividers `#C5D4D3`; page white.

**Layout (top to bottom)**
1. Logo PNG 84 × 28 px, linked to the start page.
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
- Send a test mail to yourself before anything goes out.

## Slides

**Template:** `CASI-Folien.potx` (connector tool `casi_templates`). Start every deck from it and pick the layout per slide: Titel, Abschnitt, Inhalt, Nur Titel, Zwei Spalten, Text mit Box, Zwei Boxen, Abbildung, Schluss, Leer. PP Mori and IBM Plex Serif are embedded.

16:9, 13.333 × 7.5 in, white. Margins 0.67 in; content y 1.05–7.0. Title (only if the author has one) PP Mori 17 pt SemiBold Deep Green at (0.67, 0.54), w 11.99. Running text IBM Plex Serif 12 pt / 1.35 Deep Green, paragraphs 6 pt apart; labels inside running text (a term above its explanation) PP Mori SemiBold as their own paragraph. Page number PP Mori 7.5 pt Slate right-aligned at y 7.07. No logo on content slides – the "C" appears only on cover and closing.

Boxes on slides grow with their text (`spAutoFit`), top-aligned at y 1.05, padding 0.3 in, `#EEF2F1`, never as large empty panels; only where the author had a box, panel or highlighted passage.

Cover: "C" at (0.67, 0.54), height 0.55 in; kicker PP Mori SemiBold 10 pt (author's capitals, +0.08 em) at y 2.2; title 40 pt at (0.67, 2.62); subtitle PP Mori 14 pt Slate at y 4.55; sender · date PP Mori 9 pt Slate at y 6.7. Section divider: kicker as on the cover, title 30 pt at (0.67, 2.62). Closing: Burgundy panel left (w 4.6 in, full height), white "C" and closing sentence (PP Mori SemiBold 24 pt white) in it; contact PP Mori 12 pt on the right — texts from the user.

python-pptx: set `run.font.name` on every run; rounded corners via `roundRect` adj = radius / min(w, h) × 100000; no shadows (`a:effectLst` empty).

## Documents

A4, margins 25 mm top/bottom, 22 mm left/right. Title page: the author's lines in their order, flush left, logo only if the author has one. Headings: the author's levels on the scale, no numbering unless the author numbered, new page only where the source has one. Footnotes IBM Plex Serif 8 pt Slate, separated by space. Tables: author's structure; a shaded table becomes one grey box; inside only the header rule and sum lines; numbers right-aligned. Third-party images unchanged; captions in the author's wording and position.

## Other media

Web: as the website (reading text 17 px serif, links in the text colour). Posters: document scale × ~2.8 for A1. Social: the user's text on white. Charts: white or grey ground, no border/3D/shadow, PP Mori, direct labels, gridlines only if values must be read, colours per the palette above.

## Check before delivering

1. Text identical to the source; nothing added or removed.
2. Right typeface per element, set on every run; Regular/Italic/SemiBold only.
3. Only the UI colours above, in emails too; graphic colours stay in their graphics.
4. Boxes grey or white-edged, 8/10 px corners, only where the author had them; lines only with meaning.
5. Emails: content linked to the website with absolute URLs, plain-text version, test mail sent.
6. Website changes: every visible text editable in Backend → Texte.