"""Baut die CASI-Word-Vorlage „Factsheet“ (A4, eine bis zwei Seiten) und ein ausgefülltes Beispiel.

Aufbau: Logo und Linie · Reihe · Titel · Vorspann · Kennzahlen (drei getrennte graue Boxen) ·
zweispaltiger Text (Zwischenüberschriften, Fließtext, Liste) und Kontakt am Ende. Grundlage wie bei Dokument und Brief:
der Neusatz von Whitepaper No. 1 (Formatvorlagen, Schriften, Logo, Kopf- und Fußzeilen).

Aufruf: python3 factsheet.py <ausgabe-ordner>
"""
import os
import re
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from whitepaper import SRC, CT_DOC, CT_DOT, ordne, run, para, field, styles, header  # noqa: E402
from dokument import table_style  # noqa: E402

BREITE = 9412  # Satzspiegel in Twips (A4, 22 mm links und rechts)


def kennzahl_styles():
    return (
        '<w:style w:type="paragraph" w:customStyle="1" w:styleId="CASIKennzahl"><w:name w:val="CASI Kennzahl"/><w:next w:val="CASIKennzahltext"/><w:qFormat/>'
        '<w:pPr><w:spacing w:before="0" w:after="40" w:line="240" w:lineRule="auto"/><w:ind w:left="0"/></w:pPr>'
        '<w:rPr><w:rFonts w:ascii="PP Mori Semibold" w:hAnsi="PP Mori Semibold" w:cs="PP Mori Semibold" w:eastAsia="PP Mori Semibold"/><w:color w:val="0E4D49"/><w:sz w:val="48"/></w:rPr></w:style>'
        # Text in der grauen Box: Deep Green (Slate erreicht auf Grau nur 4,41:1)
        '<w:style w:type="paragraph" w:customStyle="1" w:styleId="CASIKennzahltext"><w:name w:val="CASI Kennzahltext"/><w:basedOn w:val="CASIMeta"/><w:qFormat/>'
        '<w:pPr><w:spacing w:before="0" w:after="0" w:line="288" w:lineRule="auto"/><w:ind w:left="0"/></w:pPr><w:rPr><w:color w:val="0E4D49"/></w:rPr></w:style>'
    )


# Drei getrennte graue Boxen (abgerundet, gleich hoch) nebeneinander.
# Jede Box ist eine abgerundete Form mit Textfeld; feste Höhe für Zahl + drei Zeilen Erklärung.
TW = 635  # EMU je Twip
LUECKE = 284  # 5 mm zwischen den Boxen
BOX_B = (BREITE - 2 * LUECKE) // 3
BOX_H = 2400  # 42 mm: Zahl + bis zu vier Zeilen Erklärung
RADIUS = 142  # 2,5 mm
INNEN = (227, 255, 227, 227)  # links, oben, rechts, unten (4 / 4,5 / 4 / 4 mm)


def box(n, inhalt):
    cx, cy = BOX_B * TW, BOX_H * TW
    adj = round(RADIUS / min(BOX_B, BOX_H) * 100000)
    l, t, r, b = (v * TW for v in INNEN)
    return (
        '<w:p><w:pPr><w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="auto"/><w:ind w:left="0"/></w:pPr><w:r><w:drawing>'
        f'<wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{cx}" cy="{cy}"/><wp:effectExtent l="0" t="0" r="0" b="0"/>'
        f'<wp:docPr id="{100 + n}" name="Kennzahl {n}"/><wp:cNvGraphicFramePr/>'
        '<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:graphicData uri="http://schemas.microsoft.com/office/word/2010/wordprocessingShape">'
        '<wps:wsp><wps:cNvSpPr/><wps:spPr>'
        f'<a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
        f'<a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val {adj}"/></a:avLst></a:prstGeom>'
        '<a:solidFill><a:srgbClr val="EEF2F1"/></a:solidFill><a:ln><a:noFill/></a:ln></wps:spPr>'
        f'<wps:txbx><w:txbxContent>{inhalt}</w:txbxContent></wps:txbx>'
        f'<wps:bodyPr rot="0" vert="horz" wrap="square" lIns="{l}" tIns="{t}" rIns="{r}" bIns="{b}" anchor="t" anchorCtr="0"><a:noAutofit/></wps:bodyPr>'
        "</wps:wsp></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>"
    )


def kennzahlen(werte):
    """Drei Kennzahlen in drei getrennten, gleich hohen grauen Boxen (Tabelle nur zum Ausrichten)."""
    breiten = (BOX_B, LUECKE, BOX_B, LUECKE, BOX_B)
    out = [
        '<w:tbl><w:tblPr><w:tblW w:w="%d" w:type="dxa"/><w:tblInd w:w="0" w:type="dxa"/>' % sum(breiten),
        '<w:tblBorders><w:top w:val="nil"/><w:left w:val="nil"/><w:bottom w:val="nil"/><w:right w:val="nil"/><w:insideH w:val="nil"/><w:insideV w:val="nil"/></w:tblBorders>',
        '<w:tblLayout w:type="fixed"/><w:tblCellMar><w:top w:w="0" w:type="dxa"/><w:left w:w="0" w:type="dxa"/><w:bottom w:w="0" w:type="dxa"/><w:right w:w="0" w:type="dxa"/></w:tblCellMar>',
        '<w:tblLook w:val="0000" w:firstRow="0" w:lastRow="0" w:firstColumn="0" w:lastColumn="0" w:noHBand="1" w:noVBand="1"/></w:tblPr>',
        "<w:tblGrid>" + "".join(f'<w:gridCol w:w="{w}"/>' for w in breiten) + "</w:tblGrid><w:tr>",
    ]
    leer = '<w:p><w:pPr><w:spacing w:before="0" w:after="0"/></w:pPr></w:p>'
    for i, w in enumerate(breiten):
        inhalt = box(i // 2 + 1, "".join(werte[i // 2])) if i % 2 == 0 else leer
        out.append(f'<w:tc><w:tcPr><w:tcW w:w="{w}" w:type="dxa"/></w:tcPr>{inhalt}</w:tc>')
    out.append("</w:tr></w:tbl>")
    return "".join(out)


def abschnitt(sect0, spalten=1, fortlaufend=True, erste=False):
    pg = re.search(r"<w:pgSz[^>]*/><w:pgMar[^>]*/>", sect0).group(0)
    cols = f'<w:cols w:num="{spalten}" w:space="567"/>' if spalten > 1 else '<w:cols w:space="720"/>'
    if erste:  # erste Seite mit Logo-Kopf und Titelseiten-Einstellungen wie im Original
        return sect0.replace('<w:cols w:space="720"/>', cols)
    typ = '<w:type w:val="continuous"/>' if fortlaufend else ""
    return f'<w:sectPr>{typ}{pg}{cols}<w:docGrid w:linePitch="360"/></w:sectPr>'


def koerper(orig, sect0, beispiel=None):
    logo, rule = orig[0], orig[1]
    B = beispiel
    f = (lambda style, alias, prompt, ppr="": para(style, run(B[alias]), ppr)) if B else field
    b = [logo, rule]
    b.append(f("CASIReihe", "Reihe", "Factsheet · Thema"))
    b.append(f("CASITitel", "Titel", "Titel des Factsheets", '<w:spacing w:after="340"/>'))
    b.append(f("CASIVorspann", "Vorspann", "Zwei oder drei Sätze: worum es geht und warum es wichtig ist."))
    zellen = []
    for i in range(3):
        if B:
            z, t = B["kennzahlen"][i]
            zellen.append((para("CASIKennzahl", run(z)), para("CASIKennzahltext", run(t))))
        else:
            zellen.append((field("CASIKennzahl", f"Kennzahl {i + 1}", "00"), field("CASIKennzahltext", f"Erklärung {i + 1}", "Was die Zahl bedeutet")))
    b.append(kennzahlen(zellen))
    # Ende Abschnitt 1 (einspaltig, erste Seite)
    b.append(f'<w:p><w:pPr><w:spacing w:after="0"/>{abschnitt(sect0, erste=True)}</w:pPr></w:p>')
    # Abschnitt 2: zweispaltig
    if B:
        for kopf, text, liste in B["abschnitte"]:
            b.append(para("CASIUeberschrift2", run(kopf), '<w:spacing w:before="400"/>' if kopf == B["abschnitte"][0][0] else ""))
            if text:
                b.append(para("CASIFliesstext", run(text)))
            for li in liste:
                b.append(para("CASIListe", run("—\t" + li)))
    else:
        b.append(f("CASIUeberschrift2", "Zwischenüberschrift 1", "Zwischenüberschrift", '<w:spacing w:before="400"/>'))
        b.append(f("CASIFliesstext", "Text 1", "Text – CASI Fließtext. Der Text läuft in zwei Spalten."))
        b.append(f("CASIUeberschrift2", "Zwischenüberschrift 2", "Zwischenüberschrift"))
        b.append(f("CASIFliesstext", "Text 2", "Text"))
        b.append(para("CASIListe", run("—\tListenpunkt – CASI Liste.")))
        b.append(para("CASIListe", run("—\tZweiter Listenpunkt.")))
    # Kontakt am Ende der zweiten Spalte (gleicher Abschnitt)
    b.append(para("CASIKicker", run("Kontakt" if not B else B["kontaktlabel"]), '<w:keepNext/><w:spacing w:before="400"/>'))
    for i, (alias, prompt) in enumerate((("Kontakt Name", "Vorname Nachname · Funktion"), ("Kontakt E-Mail", "name@casinitiative.org"), ("Web", "casinitiative.org"))):
        if B:
            b.append(para("CASIMeta", run(B["kontakt"][i]), '<w:keepNext/><w:spacing w:after="0"/>' if i < 2 else '<w:spacing w:after="0"/>'))
        else:
            b.append(field("CASIMeta", alias, prompt, '<w:keepNext/><w:spacing w:after="0"/>' if i < 2 else '<w:spacing w:after="0"/>'))
    return "".join(b), abschnitt(sect0, spalten=2)


BEISPIEL = {  # Texte aus CASI Whitepaper No. 1, unverändert
    "Reihe": "Factsheet · ICCA",
    "Titel": "Foundations of Integrated Corporate Carbon Accounting",
    "Vorspann": "In this first whitepaper we introduce the framework of Integrated Corporate Carbon Accounting (ICCA). Such accounting systems ensure that product-level carbon footprints (PCFs) seamlessly integrate with company-level carbon emissions.",
    "kennzahlen": [("4", "Core principles: completeness, timely recognition, accuracy, unbiasedness"), ("1", "Carbon ledger for direct and indirect emissions and removals"), ("2", "Carbon metrics: Product Carbon Footprints and Corporate Carbon Footprint")],
    "abschnitte": None,
    "kontaktlabel": "Contact",
    "kontakt": ["Carbon Accounting Standards Initiative", "MISES · Universität Mannheim", "casinitiative.org"],
}


def beispiel_texte():
    import json
    T = json.load(open(os.path.join(os.path.dirname(__file__), "..", "pptx", "beispiel-text.json"), encoding="utf-8"))
    return [
        (T["p3h"], T["p3"], []),
        (T["s3title"].split("  ", 1)[-1], "", [T["p1h"], T["p2h"], T["p3h"], T["p4h"]]),
    ]


def build(out_dir):
    zin = zipfile.ZipFile(SRC)
    base = {n: zin.read(n) for n in zin.namelist()}
    order = zin.namelist()
    doc0 = base["word/document.xml"].decode()
    start = doc0.index("<w:body>") + len("<w:body>")
    sect0 = re.search(r"<w:sectPr.*?</w:sectPr>", doc0, re.S).group(0)
    orig = re.findall(r"<w:p[ >].*?</w:p>", doc0[start:], re.S)

    st = styles(base["word/styles.xml"].decode()).replace("</w:styles>", table_style() + kennzahl_styles() + "</w:styles>")
    rels0 = base["word/_rels/document.xml.rels"].decode()
    for n in ("image2.png", "image3.png", "image4.png", "image5.png"):
        rels0 = re.sub(rf'<Relationship [^>]*Target="media/{n}"/>', "", rels0)

    f = dict(base)
    for n in ("image2.png", "image3.png", "image4.png", "image5.png"):
        f.pop(f"word/media/{n}", None)
    f["word/styles.xml"] = st.encode()
    f["word/_rels/document.xml.rels"] = rels0.encode()
    f["word/header1.xml"] = header(base["word/header1.xml"].decode()).encode()
    f["docProps/core.xml"] = re.sub(r"<dc:title>.*?</dc:title>", "<dc:title>CASI Factsheet</dc:title>", base["docProps/core.xml"].decode()).encode()

    BEISPIEL["abschnitte"] = beispiel_texte()
    os.makedirs(out_dir, exist_ok=True)
    for fname, ctype, bsp in (("CASI-Factsheet.dotx", CT_DOT, None), ("CASI-Factsheet-Vorschau.docx", CT_DOC, None), ("CASI-Factsheet-Beispiel.docx", CT_DOC, BEISPIEL)):
        body, last = koerper(orig, sect0, bsp)
        f["word/document.xml"] = (doc0[:start] + body + last + "</w:body></w:document>").encode()
        out = os.path.join(out_dir, fname)
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            for n in order:
                if n in f:
                    d = f[n]
                    if n == "[Content_Types].xml":
                        d = d.decode().replace(CT_DOC, ctype).encode()
                    z.writestr(n, ordne(n, d))
        print("geschrieben:", out)


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else ".")
