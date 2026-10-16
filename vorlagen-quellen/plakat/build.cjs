// Baut die CASI-Plakatvorlagen A3 und A1 (Hochformat) und je ein Beispiel.
// Aufruf: node build.cjs <ausgabe-ordner>  – danach finish.py (Theme, Radien, Schriften einbetten, .potx)
// A1 ist A3 × 2 in allen Maßen; Regeln: ci/SKILL.md → "Posters".
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");

const OUT = process.argv[2] || ".";
const ASSETS = path.join(__dirname, "..", "assets");
const LOGO = path.join(ASSETS, "casi-logo-tinte.png"); // Wortmarke CASI in Deep Green, 3000 × 996 px
const LOGO_RATIO = 3000 / 996;
const C = { papier: "FFFFFF", block: "EEF2F1", tinte: "0E4D49", leise: "5F7471" };
const SANS = "PP Mori", SANS_SB = "PP Mori Semibold", SERIF = "IBM Plex Serif";

const FORMATE = {
  A3: { s: 1, w: 297, h: 420, spalten: 2 },
  A1: { s: 2, w: 594, h: 841, spalten: 3 },
};
const mm = (v) => v / 25.4;

function build(name, f, beispiel) {
  const s = f.s;
  const W = mm(f.w), H = mm(f.h);
  const M = mm(18) * s, CW = W - 2 * M;
  const pres = new pptxgen();
  pres.defineLayout({ name: "CASI-" + name, width: W, height: H });
  pres.layout = "CASI-" + name;
  pres.theme = { headFontFace: SANS_SB, bodyFontFace: SANS };
  pres.author = pres.company = "Carbon Accounting Standards Initiative";
  pres.title = "CASI Plakat " + name;

  const pt = (v) => v * s; // Schriftgrößen: A3-Werte, A1 doppelt
  const logo = { image: { x: M, y: M, w: 0.42 * s * LOGO_RATIO, h: 0.42 * s, path: LOGO, altText: "CASI" } };
  const FUSS_Y = H - M - 0.22 * s;
  const fuss = { text: { text: "Carbon Accounting Standards Initiative · casinitiative.org", options: { x: M, y: FUSS_Y, w: CW, h: 0.22 * s, fontFace: SANS, fontSize: pt(10), color: C.leise, margin: 0, valign: "bottom" } } };
  const ph = (name, x, y, w, h, opt, prompt) => ({ placeholder: { options: { name, type: "body", x, y, w, h, color: C.tinte, valign: "top", align: "left", margin: 0, ...opt }, text: prompt } });
  const titel = (y, h, size, prompt) => ({ placeholder: { options: { name: "title", type: "title", x: M, y, w: CW, h, fontFace: SANS_SB, fontSize: pt(size), color: C.tinte, valign: "top", align: "left", margin: 0, lineSpacingMultiple: 1.02 }, text: prompt } });

  // ---- Layout 1: Plakat (Veranstaltung, Ankündigung)
  const BOX_H = 1.55 * s, BOX_Y = FUSS_Y - 0.45 * s - BOX_H, PAD = 0.3 * s;
  const BILD_Y = 9.0 * s, BILD_H = BOX_Y - 0.45 * s - BILD_Y;
  const SP3 = (CW - 2 * PAD - 2 * 0.3 * s) / 3;
  const infoFeld = (i) => [
    ph(`label${i + 1}`, M + PAD + i * (SP3 + 0.3 * s), BOX_Y + PAD, SP3, 0.3 * s, { fontFace: SANS, fontSize: pt(11) }, ["Datum", "Ort", "Anmeldung"][i]), // in der grauen Box Deep Green (Slate dort zu kontrastarm),
    ph(`info${i + 1}`, M + PAD + i * (SP3 + 0.3 * s), BOX_Y + PAD + 0.36 * s, SP3, BOX_H - 2 * PAD - 0.36 * s, { fontFace: SANS_SB, fontSize: pt(15), lineSpacingMultiple: 1.15 }, "Angabe"),
  ];
  pres.defineSlideMaster({
    title: "Plakat",
    background: { color: C.papier },
    objects: [
      logo,
      ph("kicker", M, 3.0 * s, CW, 0.35 * s, { fontFace: SANS_SB, fontSize: pt(14), charSpacing: 1 }, "REIHE · ANLASS"),
      titel(3.45 * s, 3.6 * s, 60, "Titel des Plakats"),
      ph("lead", M, 7.2 * s, CW * 0.82, 1.6 * s, { fontFace: SERIF, fontSize: pt(20), lineSpacingMultiple: 1.35 }, "Ein oder zwei Sätze, worum es geht."),
      { placeholder: { options: { name: "picture", type: "pic", x: M, y: BILD_Y, w: CW, h: BILD_H }, text: "Abbildung oder Grafik einfügen" } },
      { rect: { x: M, y: BOX_Y, w: CW, h: BOX_H, fill: { color: C.block }, line: { type: "none" } } }, // finish.py → abgerundet
      ...infoFeld(0), ...infoFeld(1), ...infoFeld(2),
      fuss,
    ],
  });

  // ---- Layout 2: Wissenschaftliches Poster (Konferenz)
  const SP = f.spalten, GAP = 0.45 * s;
  const COL = (CW - (SP - 1) * GAP) / SP;
  const TEXT_Y = 4.9 * s, TEXT_H = FUSS_Y - 0.45 * s - TEXT_Y;
  const spalten = Array.from({ length: SP }, (_, i) =>
    ph(`spalte${i + 1}`, M + i * (COL + GAP), TEXT_Y, COL, TEXT_H, { fontFace: SERIF, fontSize: pt(12), lineSpacingMultiple: 1.4, paraSpaceAfter: pt(8) }, "Text der Spalte")
  );
  pres.defineSlideMaster({
    title: "Poster (Konferenz)",
    background: { color: C.papier },
    objects: [
      logo,
      ph("kicker", M, 1.6 * s, CW, 0.3 * s, { fontFace: SANS_SB, fontSize: pt(12), charSpacing: 1 }, "KONFERENZ · ORT · JAHR"),
      titel(2.0 * s, 1.75 * s, 40, "Titel des Posters"),
      ph("autoren", M, 3.85 * s, CW, 0.65 * s, { fontFace: SANS, fontSize: pt(14), color: C.leise, lineSpacingMultiple: 1.25 }, "Autorinnen und Autoren · Institution"),
      ...spalten,
      fuss,
    ],
  });

  // ---- Layout 3: Leer (nur Logo und Fuß)
  pres.defineSlideMaster({ title: "Leer", background: { color: C.papier }, objects: [logo, fuss] });

  if (!beispiel) {
    pres.addSlide({ masterName: "Plakat" });
    pres.addSlide({ masterName: "Poster (Konferenz)" });
    return pres.writeFile({ fileName: path.join(OUT, `CASI-Plakat-${name}.pptx`) });
  }

  // ---- Beispiel: Texte unverändert aus CASI Whitepaper No. 1
  const T = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "pptx", "beispiel-text.json"), "utf8"));
  const ABB = path.join(__dirname, "..", "pptx", "beispiel-abbildung.png"), ABB_R = 1992 / 1310;
  let sl = pres.addSlide({ masterName: "Plakat" });
  sl.addText(T.kicker, { placeholder: "kicker" });
  sl.addText(T.title, { placeholder: "title" });
  sl.addText(T.closing, { placeholder: "lead" });
  const bh = Math.min(BILD_H, CW / ABB_R);
  sl.addImage({ path: ABB, x: M, y: BILD_Y, w: bh * ABB_R, h: bh, altText: T.figCaption });
  [["Authors", T.authors], ["Published", "October 2025, revised December 2025"], ["Download", "casinitiative.org"]].forEach(([l, v], i) => {
    sl.addText(l, { placeholder: `label${i + 1}` });
    sl.addText(v, { placeholder: `info${i + 1}` });
  });

  sl = pres.addSlide({ masterName: "Poster (Konferenz)" });
  sl.addText(T.kicker, { placeholder: "kicker" });
  sl.addText(T.title, { placeholder: "title" });
  sl.addText(T.authors + " · " + T.meta, { placeholder: "autoren" });
  // Zwischenüberschrift: PP Mori SemiBold als eigener Absatz (wie Labels auf Folien)
  const kopf = (t) => ({ text: t, options: { fontFace: SANS_SB, fontSize: pt(14), breakLine: true } });
  const abs = (t) => ({ text: t, options: { breakLine: true } });
  const spalte = (...teile) => teile.flat();
  const inhalt = SP === 2
    ? [spalte(kopf(T.execTitle), abs(T.exec1)), spalte(kopf(T.p1h), abs(T.p1), kopf(T.p2h), abs(T.p2))]
    : [spalte(kopf(T.execTitle), abs(T.exec1)), spalte(kopf(T.p1h), abs(T.p1), kopf(T.p2h), abs(T.p2)), spalte(kopf(T.p3h), abs(T.p3))];
  inhalt.forEach((p, i) => {
    delete p[p.length - 1].options.breakLine;
    sl.addText(p, { placeholder: `spalte${i + 1}` });
  });
  // Abbildung unter der ersten Spalte (Website-Grafik aus dem Whitepaper) mit Bildunterschrift
  const fw = COL, fh = fw / ABB_R, fy = FUSS_Y - 0.45 * s - fh - 0.5 * s;
  sl.addImage({ path: ABB, x: M, y: fy, w: fw, h: fh, altText: T.figCaption });
  sl.addText(T.figCaption, { x: M, y: fy + fh + 0.1 * s, w: fw, h: 0.4 * s, fontFace: SANS, fontSize: pt(9), color: C.leise, margin: 0, valign: "top" });
  return pres.writeFile({ fileName: path.join(OUT, `CASI-Plakat-${name}-Beispiel.pptx`) });
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  for (const [name, f] of Object.entries(FORMATE)) {
    await build(name, f, false);
    await build(name, f, true);
  }
  console.log("geschrieben:", OUT);
})();
