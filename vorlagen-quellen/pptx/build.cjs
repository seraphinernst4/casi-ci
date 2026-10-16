// Baut die CASI-PowerPoint-Vorlage (Folienmaster mit Layouts) und eine Beispielpräsentation.
// Aufruf: node build.cjs <ausgabe-ordner>  – danach finish.py (Theme, Boxen, Schriften einbetten, .potx)
// Maße und Regeln: ci/SKILL.md → Abschnitt "Slides".
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");

const OUT = process.argv[2] || ".";
const ASSETS = path.join(__dirname, "..", "assets");
const C_TINTE = path.join(ASSETS, "casi-c-tinte.png"); // das „C“ aus der Wortmarke CASI, 714 × 800 px
const C_WEISS = path.join(ASSETS, "casi-c-weiss.png");
const C_RATIO = 714 / 800;

// CASI-Farben (ci/tokens.json)
const C = { papier: "FFFFFF", block: "EEF2F1", tinte: "0E4D49", leise: "5F7471", akzent: "8B1538" };
const SANS = "PP Mori";
const SANS_SB = "PP Mori Semibold";
const SERIF = "IBM Plex Serif";

// Raster (Zoll): 13,333 × 7,5 – Ränder 0,67 – Inhalt y 1,05 bis 7,0
const W = 13.333, H = 7.5, M = 0.67, CW = W - 2 * M, TOP = 1.05, BOTTOM = 7.0;
const GAP = 0.4;
const COL = (CW - GAP) / 2;
const SIDE = 4.2; // Breite der Box neben Text

// Erkennungstext für finish.py: Platzhalter mit diesem Hinweis werden zur grauen Box,
// die mit dem Text mitwächst (abgerundet, #EEF2F1, Innenabstand 0,3″).
const BOX_PROMPT = "Text in der Box";

const pageNumber = { x: W - M - 1.5, y: 7.07, w: 1.5, h: 0.2, fontFace: SANS, fontSize: 7.5, color: C.leise, align: "right", valign: "top", margin: 0 };

const title = () => ({
  placeholder: {
    options: { name: "title", type: "title", x: M, y: 0.54, w: CW, h: 0.42, fontFace: SANS_SB, fontSize: 17, color: C.tinte, valign: "top", align: "left", margin: 0 },
    text: "Titel hinzufügen",
  },
});

// Fließtext: IBM Plex Serif. Labels/Metadaten: PP Mori (font: SANS).
const text = (name, x, y, w, h, extra = {}) => ({
  placeholder: {
    options: { name, type: "body", x, y, w, h, fontFace: SERIF, fontSize: 12, color: C.tinte, valign: "top", align: "left", margin: 0, lineSpacingMultiple: 1.35, paraSpaceAfter: 6, ...extra },
    text: extra.prompt || "Text hinzufügen",
  },
});
const label = (name, x, y, w, h, extra = {}) => text(name, x, y, w, h, { fontFace: SANS, lineSpacingMultiple: 1.2, paraSpaceAfter: 0, ...extra });
const boxText = (name, x, y, w, h) => text(name, x, y, w, h, { prompt: BOX_PROMPT });

const content = (titleName, objects) => ({ title: titleName, background: { color: C.papier }, slideNumber: pageNumber, objects });

function defineLayouts(pres) {
  // 1 Titel (Deckblatt)
  pres.defineSlideMaster({
    title: "Titel",
    background: { color: C.papier },
    objects: [
      { image: { x: M, y: 0.54, w: 0.55 * C_RATIO, h: 0.55, path: C_TINTE, altText: "CASI" } },
      label("kicker", M, 2.2, CW, 0.3, { fontFace: SANS_SB, fontSize: 10, charSpacing: 1, prompt: "REIHE · NUMMER" }),
      { placeholder: { options: { name: "title", type: "title", x: M, y: 2.62, w: CW, h: 1.8, fontFace: SANS_SB, fontSize: 40, color: C.tinte, valign: "top", align: "left", margin: 0, lineSpacingMultiple: 1.05 }, text: "Titel der Präsentation" } },
      label("subtitle", M, 4.55, CW * 0.75, 0.9, { fontSize: 14, color: C.leise, prompt: "Untertitel" }),
      label("meta", M, 6.7, CW, 0.3, { fontSize: 9, color: C.leise, prompt: "Absender · Datum" }),
    ],
  });

  // 2 Abschnitt
  pres.defineSlideMaster(content("Abschnitt", [
    label("kicker", M, 2.2, CW, 0.3, { fontFace: SANS_SB, fontSize: 10, prompt: "Abschnitt" }),
    { placeholder: { options: { name: "title", type: "title", x: M, y: 2.62, w: CW, h: 1.6, fontFace: SANS_SB, fontSize: 30, color: C.tinte, valign: "top", align: "left", margin: 0, lineSpacingMultiple: 1.05 }, text: "Titel des Abschnitts" } },
  ]));

  // 3 Inhalt
  pres.defineSlideMaster(content("Inhalt", [title(), text("body", M, TOP, CW, BOTTOM - TOP)]));

  // 4 Nur Titel (für Grafiken, Tabellen, freie Komposition)
  pres.defineSlideMaster(content("Nur Titel", [title()]));

  // 5 Zwei Spalten
  pres.defineSlideMaster(content("Zwei Spalten", [title(), text("left", M, TOP, COL, BOTTOM - TOP), text("right", M + COL + GAP, TOP, COL, BOTTOM - TOP)]));

  // 6 Text mit Box – Box wächst mit dem Text
  pres.defineSlideMaster(content("Text mit Box", [
    title(),
    text("body", M, TOP, CW - SIDE - GAP, BOTTOM - TOP),
    boxText("box", W - M - SIDE, TOP, SIDE, 1.2),
  ]));

  // 7 Zwei Boxen – beide wachsen mit dem Text
  pres.defineSlideMaster(content("Zwei Boxen", [title(), boxText("left", M, TOP, COL, 1.2), boxText("right", M + COL + GAP, TOP, COL, 1.2)]));

  // 8 Abbildung
  pres.defineSlideMaster(content("Abbildung", [
    title(),
    { placeholder: { options: { name: "picture", type: "pic", x: M, y: TOP, w: CW, h: 5.35, color: C.tinte }, text: "Abbildung einfügen" } },
    label("caption", M, 6.55, CW, 0.4, { fontSize: 7.5, color: C.leise, prompt: "Bildunterschrift" }),
  ]));

  // 9 Schluss
  const PANEL = 4.6;
  pres.defineSlideMaster({
    title: "Schluss",
    background: { color: C.papier },
    objects: [
      { rect: { x: 0, y: 0, w: PANEL, h: H, fill: { color: C.akzent }, line: { type: "none" } } },
      { image: { x: M, y: 0.54, w: 0.55 * C_RATIO, h: 0.55, path: C_WEISS, altText: "CASI" } },
      { placeholder: { options: { name: "title", type: "title", x: M, y: 2.62, w: PANEL - 2 * M, h: 3.0, fontFace: SANS_SB, fontSize: 24, color: C.papier, valign: "top", align: "left", margin: 0, lineSpacingMultiple: 1.1 }, text: "Schlusssatz" } },
      label("body", PANEL + M, 2.62, W - PANEL - 2 * M, 3.0, { fontSize: 12, lineSpacingMultiple: 1.35, prompt: "Kontakt" }),
    ],
  });

  // 10 Leer
  pres.defineSlideMaster(content("Leer", []));
}

function newPres() {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE";
  // Theme: Überschriften PP Mori Semibold, Standard PP Mori (Labels, Tabellen, Diagramme).
  pres.theme = { headFontFace: SANS_SB, bodyFontFace: SANS };
  pres.author = "Carbon Accounting Standards Initiative";
  pres.company = "Carbon Accounting Standards Initiative";
  pres.title = "CASI";
  defineLayouts(pres);
  return pres;
}

async function buildTemplate() {
  const pres = newPres();
  pres.addSlide({ masterName: "Titel" });
  await pres.writeFile({ fileName: path.join(OUT, "CASI-Folien.pptx") });
}

const lbl = (t) => ({ text: t, options: { fontFace: SANS_SB, breakLine: true } });

async function buildExample() {
  const T = JSON.parse(fs.readFileSync(path.join(__dirname, "beispiel-text.json"), "utf8"));
  const pres = newPres();
  pres.title = "CASI Folien – Beispiel";

  let s = pres.addSlide({ masterName: "Titel" });
  s.addText(T.kicker, { placeholder: "kicker" });
  s.addText(T.title, { placeholder: "title" });
  s.addText(T.authors, { placeholder: "subtitle" });
  s.addText(T.meta, { placeholder: "meta" });

  s = pres.addSlide({ masterName: "Abschnitt" });
  s.addText(T.s1kicker, { placeholder: "kicker" });
  s.addText(T.s1title, { placeholder: "title" });

  s = pres.addSlide({ masterName: "Inhalt" });
  s.addText(T.execTitle, { placeholder: "title" });
  s.addText([{ text: T.exec1, options: { breakLine: true } }, { text: T.exec2 }], { placeholder: "body" });

  s = pres.addSlide({ masterName: "Zwei Spalten" });
  s.addText(T.s3title, { placeholder: "title" });
  s.addText([lbl(T.p1h), { text: T.p1 }], { placeholder: "left" });
  s.addText([lbl(T.p2h), { text: T.p2 }], { placeholder: "right" });

  s = pres.addSlide({ masterName: "Text mit Box" });
  s.addText(T.fwTitle, { placeholder: "title" });
  s.addText(T.fw, { placeholder: "body" });
  s.addText(T.fwBox, { placeholder: "box" });

  s = pres.addSlide({ masterName: "Zwei Boxen" });
  s.addText(T.s3title, { placeholder: "title" });
  s.addText([lbl(T.p3h), { text: T.p3 }], { placeholder: "left" });
  s.addText([lbl(T.p4h), { text: T.p4 }], { placeholder: "right" });

  s = pres.addSlide({ masterName: "Abbildung" });
  s.addText(T.s2title, { placeholder: "title" });
  const figH = 5.35, figW = figH * (1992 / 1310);
  s.addImage({ path: path.join(__dirname, "beispiel-abbildung.png"), x: M, y: TOP, w: figW, h: figH, altText: T.figCaption });
  s.addText(T.figCaption, { placeholder: "caption" });

  // Website-Grafiken: leere „Nur Titel“-Folien, finish.py setzt die Formen aus website-grafiken.pptx ein
  for (const g of T.grafiken) {
    s = pres.addSlide({ masterName: "Nur Titel" });
    s.addText(g.titel, { placeholder: "title" });
  }

  s = pres.addSlide({ masterName: "Schluss" });
  s.addText(T.closing, { placeholder: "title" });
  s.addText(T.contact, { placeholder: "body" });

  await pres.writeFile({ fileName: path.join(OUT, "CASI-Folien-Beispiel.pptx") });
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  await buildTemplate();
  await buildExample();
  console.log("geschrieben:", OUT);
})();
