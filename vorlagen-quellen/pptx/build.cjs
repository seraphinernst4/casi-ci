// Baut die CASI-PowerPoint-Vorlage (Folienmaster mit Layouts) und eine Beispielpräsentation.
// Aufruf: node build.cjs <ausgabe-ordner>  – danach finish.py (Theme, Schriften einbetten, .potx)
// Maße und Regeln: ci/SKILL.md → Abschnitt "Slides".
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");

const OUT = process.argv[2] || ".";
const ASSETS = path.join(__dirname, "..", "assets");
const LOGO = path.join(ASSETS, "logo-lang.png"); // 1063 × 220 px
const LOGO_RATIO = 1063 / 220;

// CASI-Farben (ci/tokens.json)
const C = {
  papier: "FFFFFF",
  block: "EEF2F1",
  tinte: "0E4D49",
  leise: "5F7471",
  linie: "E1E7E5",
  kante: "C5D4D3",
  akzent: "8B1538",
};
const SANS = "PP Mori";
const SANS_SB = "PP Mori Semibold";

// Raster (Zoll): 13,333 × 7,5 – Ränder 0,67 – Inhalt y 1,05 bis 7,0
const W = 13.333, H = 7.5, M = 0.67, CW = W - 2 * M, TOP = 1.05, BOTTOM = 7.0;
const GAP = 0.4;
const COL = (CW - GAP) / 2;
const PAD = 0.3; // Innenabstand in Boxen
const RADIUS = 0.1; // Eckenradius Boxen (≈ 10 px Website)

const pageNumber = { x: W - M - 1.5, y: 7.07, w: 1.5, h: 0.2, fontFace: SANS, fontSize: 7.5, color: C.leise, align: "right", valign: "top", margin: 0 };

const title = (extra = {}) => ({
  placeholder: {
    options: { name: "title", type: "title", x: M, y: 0.54, w: CW, h: 0.42, fontFace: SANS_SB, fontSize: 17, color: C.tinte, valign: "top", align: "left", margin: 0, ...extra },
    text: "Titel hinzufügen",
  },
});

const body = (name, x, y, w, h, extra = {}) => ({
  placeholder: {
    options: { name, type: "body", x, y, w, h, fontFace: SANS, fontSize: 12, color: C.tinte, valign: "top", align: "left", margin: 0, lineSpacingMultiple: 1.25, paraSpaceAfter: 6, ...extra },
    text: extra.prompt || "Text hinzufügen",
  },
});

const box = (x, y, w, h, color = C.block) => ({
  text: { text: "", options: { shape: "roundRect", x, y, w, h, fill: { color }, line: { type: "none" }, rectRadius: RADIUS } },
});

function defineLayouts(pres) {
  // 1 Titel (Deckblatt)
  pres.defineSlideMaster({
    title: "Titel",
    background: { color: C.papier },
    objects: [
      { image: { x: M, y: 0.54, w: 0.42 * LOGO_RATIO, h: 0.42, path: LOGO, altText: "Carbon Accounting Standards Initiative" } },
      body("kicker", M, 2.2, CW, 0.3, { fontFace: SANS_SB, fontSize: 10, charSpacing: 1, prompt: "REIHE · NUMMER" }),
      { placeholder: { options: { name: "title", type: "title", x: M, y: 2.62, w: CW, h: 1.8, fontFace: SANS_SB, fontSize: 40, color: C.tinte, valign: "top", align: "left", margin: 0, lineSpacingMultiple: 1.05 }, text: "Titel der Präsentation" } },
      body("subtitle", M, 4.55, CW * 0.75, 0.9, { fontSize: 14, color: C.leise, prompt: "Untertitel" }),
      body("meta", M, 6.7, CW, 0.3, { fontSize: 9, color: C.leise, prompt: "Absender · Datum" }),
    ],
  });

  // 2 Abschnitt
  pres.defineSlideMaster({
    title: "Abschnitt",
    background: { color: C.papier },
    slideNumber: pageNumber,
    objects: [
      body("kicker", M, 2.2, CW, 0.3, { fontFace: SANS_SB, fontSize: 10, prompt: "Abschnitt" }),
      { placeholder: { options: { name: "title", type: "title", x: M, y: 2.62, w: CW, h: 1.6, fontFace: SANS_SB, fontSize: 30, color: C.tinte, valign: "top", align: "left", margin: 0, lineSpacingMultiple: 1.05 }, text: "Titel des Abschnitts" } },
    ],
  });

  // 3 Inhalt
  pres.defineSlideMaster({
    title: "Inhalt",
    background: { color: C.papier },
    slideNumber: pageNumber,
    objects: [title(), body("body", M, TOP, CW, BOTTOM - TOP)],
  });

  // 4 Nur Titel (für Grafiken, Tabellen, freie Komposition)
  pres.defineSlideMaster({
    title: "Nur Titel",
    background: { color: C.papier },
    slideNumber: pageNumber,
    objects: [title()],
  });

  // 5 Zwei Spalten
  pres.defineSlideMaster({
    title: "Zwei Spalten",
    background: { color: C.papier },
    slideNumber: pageNumber,
    objects: [title(), body("left", M, TOP, COL, BOTTOM - TOP), body("right", M + COL + GAP, TOP, COL, BOTTOM - TOP)],
  });

  // 6 Box
  pres.defineSlideMaster({
    title: "Box",
    background: { color: C.papier },
    slideNumber: pageNumber,
    objects: [title(), box(M, TOP, CW, BOTTOM - TOP), body("body", M + PAD, TOP + PAD, CW - 2 * PAD, BOTTOM - TOP - 2 * PAD)],
  });

  // 7 Zwei Boxen
  pres.defineSlideMaster({
    title: "Zwei Boxen",
    background: { color: C.papier },
    slideNumber: pageNumber,
    objects: [
      title(),
      box(M, TOP, COL, BOTTOM - TOP),
      box(M + COL + GAP, TOP, COL, BOTTOM - TOP),
      body("left", M + PAD, TOP + PAD, COL - 2 * PAD, BOTTOM - TOP - 2 * PAD),
      body("right", M + COL + GAP + PAD, TOP + PAD, COL - 2 * PAD, BOTTOM - TOP - 2 * PAD),
    ],
  });

  // 8 Abbildung
  pres.defineSlideMaster({
    title: "Abbildung",
    background: { color: C.papier },
    slideNumber: pageNumber,
    objects: [
      title(),
      { placeholder: { options: { name: "picture", type: "pic", x: M, y: TOP, w: CW, h: 5.35, color: C.tinte }, text: "Abbildung einfügen" } },
      body("caption", M, 6.55, CW, 0.4, { fontSize: 7.5, color: C.leise, lineSpacingMultiple: 1.2, prompt: "Bildunterschrift" }),
    ],
  });

  // 9 Schluss
  const PANEL = 4.6;
  pres.defineSlideMaster({
    title: "Schluss",
    background: { color: C.papier },
    objects: [
      { rect: { x: 0, y: 0, w: PANEL, h: H, fill: { color: C.akzent }, line: { type: "none" } } },
      { placeholder: { options: { name: "title", type: "title", x: M, y: 2.62, w: PANEL - 2 * M, h: 3.0, fontFace: SANS_SB, fontSize: 24, color: C.papier, valign: "top", align: "left", margin: 0, lineSpacingMultiple: 1.1 }, text: "Schlusssatz" } },
      body("body", PANEL + M, 2.62, W - PANEL - 2 * M, 3.0, { prompt: "Kontakt" }),
      { image: { x: PANEL + M, y: 6.58, w: 0.42 * LOGO_RATIO, h: 0.42, path: LOGO, altText: "Carbon Accounting Standards Initiative" } },
    ],
  });

  // 10 Leer
  pres.defineSlideMaster({ title: "Leer", background: { color: C.papier }, slideNumber: pageNumber, objects: [] });
}

function newPres() {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE";
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
  s.addText([{ text: T.p1h, options: { fontFace: SANS_SB, breakLine: true } }, { text: T.p1 }], { placeholder: "left" });
  s.addText([{ text: T.p2h, options: { fontFace: SANS_SB, breakLine: true } }, { text: T.p2 }], { placeholder: "right" });

  s = pres.addSlide({ masterName: "Box" });
  s.addText(T.fwTitle, { placeholder: "title" });
  s.addText(T.fw, { placeholder: "body" });

  s = pres.addSlide({ masterName: "Zwei Boxen" });
  s.addText(T.s3title, { placeholder: "title" });
  s.addText([{ text: T.p3h, options: { fontFace: SANS_SB, breakLine: true } }, { text: T.p3 }], { placeholder: "left" });
  s.addText([{ text: T.p4h, options: { fontFace: SANS_SB, breakLine: true } }, { text: T.p4 }], { placeholder: "right" });

  s = pres.addSlide({ masterName: "Abbildung" });
  s.addText(T.s2title, { placeholder: "title" });
  const figH = 5.35, figW = figH * (1992 / 1310);
  s.addImage({ path: path.join(__dirname, "beispiel-abbildung.png"), x: M, y: TOP, w: figW, h: figH, altText: T.figCaption });
  s.addText(T.figCaption, { placeholder: "caption" });

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
