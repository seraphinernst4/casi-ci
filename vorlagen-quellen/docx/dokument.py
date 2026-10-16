"""Baut die CASI-Word-Vorlagen „Dokument“ (Bericht, Protokoll, Memo) und „Brief“ (DIN 5008, Form B).

Grundlage wie beim Whitepaper: der Neusatz von Whitepaper No. 1 (Formatvorlagen, Schriften,
Logo, Kopf- und Fußzeilen). Absenderangaben wie im Impressum der Website.

Aufruf: python3 dokument.py <ausgabe-ordner>
"""
import os
import re
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from whitepaper import SRC, CT_DOC, CT_DOT, ordne, run, para, field, fld, styles, header  # noqa: E402

HDR_CT = "application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"
FTR_CT = "application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"
REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"

# Absender – Wortlaut wie im Impressum (casinitiative.org/impressum)
ABSENDER_ZEILE = "CASI · Universität Mannheim · Schloss Ostflügel · 68161 Mannheim"
FUSS = [
    "Carbon Accounting Standards Initiative (CASI)",
    "Mannheim Institute for Sustainable Energy Studies (MISES) · Universität Mannheim",
    "Schloss Ostflügel, Raum O 351–359 · 68161 Mannheim · Deutschland · casinitiative.org",
]


def table_style():
    """CASI Tabelle: keine Gitterlinien, eine Linie unter der Kopfzeile, PP Mori."""
    return (
        '<w:style w:type="table" w:customStyle="1" w:styleId="CASITabelle"><w:name w:val="CASI Tabelle"/><w:uiPriority w:val="59"/>'
        '<w:pPr><w:spacing w:before="40" w:after="40" w:line="276" w:lineRule="auto"/></w:pPr>'
        '<w:rPr><w:rFonts w:ascii="PP Mori" w:hAnsi="PP Mori" w:cs="PP Mori"/><w:color w:val="0E4D49"/><w:sz w:val="18"/></w:rPr>'
        '<w:tblPr><w:tblInd w:w="164" w:type="dxa"/><w:tblBorders><w:top w:val="nil"/><w:left w:val="nil"/><w:bottom w:val="nil"/><w:right w:val="nil"/>'
        '<w:insideH w:val="nil"/><w:insideV w:val="nil"/></w:tblBorders><w:tblCellMar><w:left w:w="0" w:type="dxa"/><w:right w:w="142" w:type="dxa"/></w:tblCellMar></w:tblPr>'
        '<w:tblStylePr w:type="firstRow"><w:rPr><w:b/></w:rPr><w:tcPr><w:tcBorders><w:bottom w:val="single" w:sz="6" w:space="0" w:color="0E4D49"/></w:tcBorders></w:tcPr></w:tblStylePr>'
        "</w:style>"
        '<w:style w:type="paragraph" w:customStyle="1" w:styleId="CASITabellentext"><w:name w:val="CASI Tabellentext"/><w:qFormat/>'
        '<w:pPr><w:spacing w:before="57" w:after="57" w:line="264" w:lineRule="auto"/></w:pPr>'
        '<w:rPr><w:rFonts w:ascii="PP Mori" w:hAnsi="PP Mori" w:cs="PP Mori" w:eastAsia="PP Mori"/><w:color w:val="0E4D49"/><w:sz w:val="18"/></w:rPr></w:style>'
    )


def sample_table():
    rows = [("Spalte", "Spalte", "Wert"), ("Eintrag", "Eintrag", "0"), ("Eintrag", "Eintrag", "0")]
    widths = (3600, 3600, 2200)
    out = ['<w:tbl><w:tblPr><w:tblStyle w:val="CASITabelle"/><w:tblW w:w="9400" w:type="dxa"/><w:tblLook w:val="04A0" w:firstRow="1" w:lastRow="0" w:firstColumn="0" w:lastColumn="0" w:noHBand="1" w:noVBand="1"/></w:tblPr><w:tblGrid>']
    out += [f'<w:gridCol w:w="{w}"/>' for w in widths]
    out.append("</w:tblGrid>")
    for r in rows:
        out.append("<w:tr>")
        for i, (c, w) in enumerate(zip(r, widths)):
            jc = '<w:jc w:val="right"/>' if i == 2 else ""
            out.append(f'<w:tc><w:tcPr><w:tcW w:w="{w}" w:type="dxa"/></w:tcPr><w:p><w:pPr><w:pStyle w:val="CASITabellentext"/>{jc}</w:pPr>{run(c)}</w:p></w:tc>')
        out.append("</w:tr>")
    out.append("</w:tbl>")
    return "".join(out)


def dokument_body(orig):
    logo, rule = orig[0], orig[1]
    b = [logo, rule]
    b.append(field("CASIReihe", "Art des Dokuments", "Bericht · Protokoll · Memo"))
    b.append(field("CASITitel", "Titel", "Titel des Dokuments"))
    b.append(field("CASIMeta", "Absender und Datum", "Name · Funktion · Datum"))
    b.append(para("CASIUeberschrift1", run("1\tÜberschrift 1 – CASI Überschrift 1")))
    b.append(field("CASIFliesstext", "Text", "Text – CASI Fließtext. Den Text des Autors unverändert übernehmen."))
    b.append(para("CASIUeberschrift2", run("Überschrift 2 – CASI Überschrift 2")))
    b.append(para("CASIListe", run("—\tListenpunkt – CASI Liste.")))
    b.append(para("CASIListe", run("—\tZweiter Listenpunkt.")))
    b.append(para("CASIFliesstext", run("Tabelle – Formatvorlage „CASI Tabelle“: keine Gitterlinien, eine Linie unter der Kopfzeile, Zahlen rechtsbündig; Zellen in „CASI Tabellentext“.")))
    b.append(sample_table())
    b.append(para("CASIBildunterschrift", run("Table 1", '<w:b/><w:color w:val="0E4D49"/>') + run(" Beschriftung im Wortlaut des Autors.")))
    return "".join(b)


def frame(x, y, w, h=None):
    hh = f' w:h="{h}" w:hRule="exact"' if h else ""
    return f'<w:framePr w:w="{w}"{hh} w:hSpace="0" w:wrap="around" w:vAnchor="page" w:hAnchor="page" w:x="{x}" w:y="{y}"/>'


def brief_body():
    # DIN 5008 Form B: Anschriftfeld 45 mm von oben, 85 × 45 mm; Informationsblock rechts ab 125 mm
    adr = frame(1417, 2552, 4535, 2551)
    info = frame(7087, 2835, 4252)
    meta_r = '<w:rFonts w:ascii="PP Mori" w:hAnsi="PP Mori" w:cs="PP Mori"/><w:color w:val="5F7471"/><w:sz w:val="14"/>'
    b = []
    b.append(f'<w:p><w:pPr><w:pStyle w:val="CASIMeta"/>{adr}<w:spacing w:after="170"/><w:ind w:left="0"/></w:pPr>{run(ABSENDER_ZEILE, meta_r)}</w:p>')
    for i, (alias, prompt) in enumerate((("Empfänger", "Empfängerin oder Empfänger"), ("Organisation", "Organisation"), ("Straße", "Straße Nr."), ("Ort", "PLZ Ort"))):
        b.append(field("CASIMeta", alias, prompt, f'{adr}<w:spacing w:after="0" w:line="276" w:lineRule="auto"/><w:ind w:left="0"/>'))
    for label, prompt in (("Datum", "TT. Monat JJJJ"), ("Ansprechperson", "Name"), ("E-Mail", "name@casinitiative.org")):
        b.append(f'<w:p><w:pPr><w:pStyle w:val="CASIMeta"/>{info}<w:spacing w:after="0"/><w:ind w:left="0"/></w:pPr>{run(label)}</w:p>')
        b.append(field("CASIMeta", label, prompt, f'{info}<w:spacing w:after="113"/><w:ind w:left="0"/>'))
    # Betreff auf Höhe ~103 mm (oberer Rand 27 mm)
    b.append(field("CASIUeberschrift2", "Betreff", "Betreff", '<w:spacing w:before="4250" w:after="400"/>'))
    b.append(field("CASIFliesstext", "Anrede", "Anrede,"))
    b.append(field("CASIFliesstext", "Brieftext", "Brieftext – CASI Fließtext."))
    b.append(field("CASIFliesstext", "Grußformel", "Grußformel", '<w:spacing w:after="840"/>'))
    b.append(field("CASIMeta", "Name", "Vorname Nachname", '<w:spacing w:after="0"/>'))
    b.append(field("CASIMeta", "Funktion", "Funktion"))
    return "".join(b)


def logo_header(logo_para):
    return (
        "<?xml version='1.0' encoding='UTF-8' standalone='yes'?>"
        '<w:hdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
        f'xmlns:r="{REL}" '
        'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing">'
        + logo_para.replace('<w:spacing w:after="220"/>', '<w:spacing w:after="0"/>')
        + "</w:hdr>"
    )


def footer_xml(lines):
    ps = "".join(f'<w:p><w:pPr><w:pStyle w:val="CASIMeta"/><w:spacing w:after="0"/></w:pPr>{run(t)}</w:p>' for t in lines)
    return (
        "<?xml version='1.0' encoding='UTF-8' standalone='yes'?>"
        '<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">' + ps + "</w:ftr>"
    )


def build(out_dir):
    zin = zipfile.ZipFile(SRC)
    base = {n: zin.read(n) for n in zin.namelist()}
    order = zin.namelist()
    doc0 = base["word/document.xml"].decode()
    start = doc0.index("<w:body>") + len("<w:body>")
    sect0 = re.search(r"<w:sectPr.*?</w:sectPr>", doc0, re.S).group(0)
    orig = re.findall(r"<w:p[ >].*?</w:p>", doc0[start:], re.S)

    st = styles(base["word/styles.xml"].decode()).replace("</w:styles>", table_style() + "</w:styles>")
    rels0 = base["word/_rels/document.xml.rels"].decode()
    for n in ("image2.png", "image3.png", "image4.png", "image5.png"):
        rels0 = re.sub(rf'<Relationship [^>]*Target="media/{n}"/>', "", rels0)

    def write(name, files, extra_order=()):
        for fname, ctype in ((f"{name}.dotx", CT_DOT), (f"{name}-Vorschau.docx", CT_DOC)):
            out = os.path.join(out_dir, fname)
            with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
                for n in list(order) + list(extra_order):
                    if n not in files:
                        continue
                    d = files[n]
                    if n == "[Content_Types].xml":
                        d = d.decode().replace(CT_DOC, ctype).encode()
                    z.writestr(n, ordne(n, d))
            print("geschrieben:", out)

    os.makedirs(out_dir, exist_ok=True)

    # ---------------- Dokument
    f = dict(base)
    for n in ("image2.png", "image3.png", "image4.png", "image5.png"):
        f.pop(f"word/media/{n}", None)
    f["word/styles.xml"] = st.encode()
    f["word/_rels/document.xml.rels"] = rels0.encode()
    f["word/header1.xml"] = header(base["word/header1.xml"].decode()).encode()
    f["word/document.xml"] = (doc0[:start] + dokument_body(orig) + sect0 + "</w:body></w:document>").encode()
    f["docProps/core.xml"] = re.sub(r"<dc:title>.*?</dc:title>", "<dc:title>CASI Dokument</dc:title>", base["docProps/core.xml"].decode()).encode()
    write("CASI-Dokument", f)

    # ---------------- Brief
    f = dict(base)
    for n in ("image2.png", "image3.png", "image4.png", "image5.png"):
        f.pop(f"word/media/{n}", None)
    f["word/styles.xml"] = st.encode()
    rels = rels0
    # erste Seite: Logo-Kopf und Absender-Fuß; Folgeseiten: Fuß mit Seitenzahl (footer1)
    f["word/header3.xml"] = logo_header(orig[0]).encode()
    f["word/_rels/header3.xml.rels"] = (
        "<?xml version='1.0' encoding='UTF-8' standalone='yes'?>"
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        f'<Relationship Id="rId9" Type="{REL}/image" Target="media/image1.png"/></Relationships>'
    ).encode()
    f["word/footer3.xml"] = footer_xml(FUSS).encode()
    f["word/header4.xml"] = (
        "<?xml version='1.0' encoding='UTF-8' standalone='yes'?>"
        '<w:hdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:p><w:pPr><w:pStyle w:val="Header"/></w:pPr></w:p></w:hdr>'
    ).encode()
    rels = rels.replace(
        "</Relationships>",
        f'<Relationship Id="rIdBriefKopf1" Type="{REL}/header" Target="header3.xml"/>'
        f'<Relationship Id="rIdBriefFuss1" Type="{REL}/footer" Target="footer3.xml"/>'
        f'<Relationship Id="rIdBriefKopf2" Type="{REL}/header" Target="header4.xml"/></Relationships>',
    )
    f["word/_rels/document.xml.rels"] = rels.encode()
    ct = base["[Content_Types].xml"].decode()
    ct = ct.replace(
        "</Types>",
        f'<Override PartName="/word/header3.xml" ContentType="{HDR_CT}"/>'
        f'<Override PartName="/word/header4.xml" ContentType="{HDR_CT}"/>'
        f'<Override PartName="/word/footer3.xml" ContentType="{FTR_CT}"/></Types>',
    )
    f["[Content_Types].xml"] = ct.encode()
    sect = (
        '<w:sectPr><w:headerReference w:type="default" r:id="rIdBriefKopf2"/><w:footerReference w:type="default" r:id="rId29"/>'
        '<w:headerReference w:type="first" r:id="rIdBriefKopf1"/><w:footerReference w:type="first" r:id="rIdBriefFuss1"/>'
        '<w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1531" w:right="1134" w:bottom="1417" w:left="1253" w:header="850" w:footer="567" w:gutter="0"/>'
        '<w:cols w:space="720"/><w:titlePg/><w:docGrid w:linePitch="360"/></w:sectPr>'
    )
    f["word/document.xml"] = (doc0[:start] + brief_body() + sect + "</w:body></w:document>").encode()
    f["docProps/core.xml"] = re.sub(r"<dc:title>.*?</dc:title>", "<dc:title>CASI Brief</dc:title>", base["docProps/core.xml"].decode()).encode()
    write("CASI-Brief", f, extra_order=("word/header3.xml", "word/_rels/header3.xml.rels", "word/header4.xml", "word/footer3.xml"))


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else ".")
