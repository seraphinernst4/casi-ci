"""Baut die CASI-Whitepaper-Vorlage (.dotx) aus dem Neusatz von Whitepaper No. 1.

Übernommen werden: Formatvorlagen, Seitenränder, Kopf-/Fußzeilen, Logo, eingebettete
Schriften (PP Mori, IBM Plex Serif). Der Inhalt wird durch ein leeres Gerüst ersetzt:
Deckblatt mit Eingabefeldern, automatisches Inhaltsverzeichnis, Musterseite mit jeder
Formatvorlage, Literatur und Impressum.

Aufruf: python3 whitepaper.py <ausgabe-ordner>
"""
import os
import re
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "quelle-whitepaper-01.docx")
CT_DOC = "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"
CT_DOT = "application/vnd.openxmlformats-officedocument.wordprocessingml.template.main+xml"



# Reihenfolge der Kindelemente laut OOXML-Schema – Word meldet sonst „unlesbaren Inhalt“.
PPR_ORDNUNG = ["pStyle", "keepNext", "keepLines", "pageBreakBefore", "framePr", "widowControl", "numPr", "suppressLineNumbers",
               "pBdr", "shd", "tabs", "suppressAutoHyphens", "kinsoku", "wordWrap", "overflowPunct", "topLinePunct", "autoSpaceDE",
               "autoSpaceDN", "bidi", "adjustRightInd", "snapToGrid", "spacing", "ind", "contextualSpacing", "mirrorIndents",
               "suppressOverlap", "jc", "textDirection", "textAlignment", "textboxTightWrap", "outlineLvl", "divId", "cnfStyle",
               "rPr", "sectPr", "pPrChange"]
SETTINGS_KOPF = ["writeProtection", "view", "zoom", "removePersonalInformation", "removeDateAndTime", "doNotDisplayPageBoundaries",
                 "displayBackgroundShape", "printPostScriptOverText", "printFractionalCharacterWidth", "printFormsData",
                 "embedTrueTypeFonts", "embedSystemFonts", "saveSubsetFonts"]


def ordne(name, data):
    """Bringt pPr-Kinder und den Kopf von settings.xml in Schema-Reihenfolge."""
    if not (name.startswith("word/") and name.endswith(".xml")):
        return data
    from lxml import etree
    W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    root = etree.fromstring(data)
    def sortiere(el, ordnung, nur_kopf=False):
        kinder = list(el)
        rang = {n: i for i, n in enumerate(ordnung)}
        def r(k):
            loc = etree.QName(k).localname if isinstance(k.tag, str) else ""
            return rang.get(loc, len(ordnung))
        if nur_kopf:
            kopf = sorted([k for k in kinder if r(k) < len(ordnung)], key=r)
            rest = [k for k in kinder if r(k) >= len(ordnung)]
            neu = kopf + rest
        else:
            neu = sorted(kinder, key=r)  # stabil: Unbekanntes behält seine Reihenfolge am Ende
        if neu != kinder:
            for k in kinder:
                el.remove(k)
            for k in neu:
                el.append(k)
    for ppr in root.iter(W + "pPr"):
        sortiere(ppr, PPR_ORDNUNG)
    if name == "word/settings.xml":
        sortiere(root, SETTINGS_KOPF, nur_kopf=True)
        for z in root.iter(W + "zoom"):
            if z.get(W + "percent") is None:
                z.set(W + "percent", "100")
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def run(t, rpr=""):
    sp = ' xml:space="preserve"' if t != t.strip() else ""
    return f'<w:r>{f"<w:rPr>{rpr}</w:rPr>" if rpr else ""}<w:t{sp}>{esc(t)}</w:t></w:r>'


def para(style, content="", ppr=""):
    return f'<w:p><w:pPr><w:pStyle w:val="{style}"/>{ppr}</w:pPr>{content}</w:p>'


_id = [100]


def field(style, alias, prompt, ppr=""):
    """Eingabefeld (Inhaltssteuerelement) mit grauem Hinweistext."""
    _id[0] += 1
    return (
        f'<w:p><w:pPr><w:pStyle w:val="{style}"/>{ppr}</w:pPr>'
        f'<w:sdt><w:sdtPr><w:rPr><w:rStyle w:val="PlaceholderText"/></w:rPr><w:alias w:val="{esc(alias)}"/><w:tag w:val="{esc(alias)}"/>'
        f'<w:id w:val="{_id[0]}"/><w:showingPlcHdr/><w:text w:multiLine="1"/></w:sdtPr>'
        f'<w:sdtContent>{run(prompt, "<w:rStyle w:val=\"PlaceholderText\"/>")}</w:sdtContent></w:sdt></w:p>'
    )


def picture_field(alias):
    _id[0] += 1
    return (
        '<w:p><w:pPr><w:pStyle w:val="CASIAbbildung"/></w:pPr>'
        f'<w:sdt><w:sdtPr><w:alias w:val="{alias}"/><w:tag w:val="{alias}"/><w:id w:val="{_id[0]}"/><w:showingPlcHdr/><w:picture/></w:sdtPr>'
        '<w:sdtContent><w:r><w:t>Abbildung einfügen</w:t></w:r></w:sdtContent></w:sdt></w:p>'
    )


def fld(instr, cached):
    return (
        '<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
        f'<w:r><w:instrText xml:space="preserve"> {instr} </w:instrText></w:r>'
        '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
        f"{run(cached)}"
        '<w:r><w:fldChar w:fldCharType="end"/></w:r>'
    )


def body(orig_paras):
    logo, rule = orig_paras[0], orig_paras[1]
    about = next(p for p in orig_paras if "advances the practice of corporate carbon accounting" in p)
    license_ = next(p for p in orig_paras if "CC BY-SA 4.0" in p)
    toc_line = '<w:pBdr><w:bottom w:val="single" w:sz="4" w:space="5" w:color="E1E7E5"/></w:pBdr><w:spacing w:after="90"/>'
    author_line = toc_line

    b = []
    # ---------------- Deckblatt
    b += [logo, rule]
    b.append(field("CASIReihe", "Reihe und Nummer", "CASI Whitepaper · No. X"))
    b.append(field("CASITitel", "Titel", "Titel des Whitepapers"))
    b.append(field("CASIVorspann", "Vorspann", "Vorspann: der Absatz des Autors, der sagt, worum es geht."))
    b.append(field("CASIMeta", "Autorinnen und Autoren", "Autorinnen und Autoren, mit · getrennt"))
    b.append(field("CASIMeta", "Herausgeber und Datum", "The Carbon Accounting Standards Initiative (CASI) · Monat Jahr"))
    b.append(para("CASIUeberschrift2", run("Contents")))
    # Inhaltsverzeichnis: alle Absätze in „CASI Überschrift 1“, ohne Seitenzahlen (wie im Neusatz)
    b.append(
        '<w:p><w:pPr><w:pStyle w:val="TOC1"/></w:pPr>'
        '<w:r><w:fldChar w:fldCharType="begin" w:dirty="true"/></w:r>'
        '<w:r><w:instrText xml:space="preserve"> TOC \\n \\t "CASI Überschrift 1,1" </w:instrText></w:r>'
        '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
        + run("Inhaltsverzeichnis – Rechtsklick → „Feld aktualisieren“")
        + "</w:p>"
        '<w:p><w:pPr><w:pStyle w:val="CASIFliesstext"/></w:pPr><w:r><w:fldChar w:fldCharType="end"/></w:r></w:p>'
    )

    # ---------------- Musterseite: jede Formatvorlage einmal
    b.append(para("CASIKicker", run("Section 1"), "<w:pageBreakBefore/>"))
    b.append(para("CASIUeberschrift1", run("1\tÜberschrift 1 – CASI Überschrift 1")))
    b.append(para("CASIFliesstext", run("Fließtext – CASI Fließtext: IBM Plex Serif 10,5 pt. Den Text des Autors unverändert übernehmen; Kursiv bleibt kursiv, Fett wird SemiBold.")))
    b.append(para("CASIUeberschrift2", run("Überschrift 2 – CASI Überschrift 2")))
    b.append(para("CASIFliesstext", run("Weiterer Absatz im Fließtext.")))
    b.append(para("CASIListe", run("—\tListenpunkt – CASI Liste, mit Gedankenstrich und Tabulator.")))
    b.append(para("CASIListe", run("—\tZweiter Listenpunkt.")))
    b.append(picture_field("Abbildung"))
    b.append(para("CASIBildunterschrift", run("Figure 1", '<w:b/><w:color w:val="0E4D49"/>') + run(" Bildunterschrift – CASI Bildunterschrift, im Wortlaut des Autors.")))
    b.append(
        '<w:p><w:pPr><w:pStyle w:val="CASIFliesstext"/><w:keepNext/><w:pBdr><w:top w:val="single" w:sz="4" w:space="6" w:color="E1E7E5"/></w:pBdr>'
        '<w:spacing w:before="220" w:after="142"/><w:ind w:left="884" w:hanging="357"/></w:pPr>'
        + run("Begriff", '<w:rFonts w:ascii="PP Mori" w:hAnsi="PP Mori" w:cs="PP Mori"/><w:b/>')
        + "</w:p>"
    )
    b.append(para("CASIFliesstext", run("Erläuterung zum Begriff – eingerückt, mit feiner Linie darüber (wie die Core Principles in Whitepaper No. 1)."), '<w:ind w:left="884"/>'))

    # ---------------- Literatur
    b.append(para("CASIKicker", run("Bibliography"), "<w:pageBreakBefore/>"))
    b.append(para("CASIUeberschrift1", run("References")))
    b.append(para("CASILiteratur", run("Nachname, V. (Jahr). Titel des Beitrags. ") + run("Zeitschrift oder Reihe", "<w:i/>") + run(" Band, Seiten."), "<w:keepLines/>"))

    # ---------------- Impressum
    b.append(para("CASIKicker", run("Imprint"), "<w:pageBreakBefore/>"))
    b.append(para("CASIUeberschrift1", run("About CASI")))
    b.append(about)
    b.append(para("CASIUeberschrift2", run("Authors")))
    b.append(para("CASIFliesstext", run("Vorname Nachname", "<w:b/>") + run(", Institution") + run(" · ") + run("e-mail@institution", '<w:color w:val="5F7471"/>'), author_line))
    b.append(para("CASIUeberschrift2", run("Publication details")))
    b.append(para("CASIFliesstext", run("CASI Whitepaper No. X: ") + run("Titel", "<w:i/>") + run(", Version 1.0, Monat Jahr")))
    b.append(para("CASIUeberschrift2", run("License")))
    b.append(license_)
    return "".join(b)


def styles(xml):
    def style_block(sid):
        m = re.search(rf'<w:style [^>]*w:styleId="{sid}"[^>]*>.*?</w:style>', xml, re.S)
        return m

    # CASI Reihe: Deckblatt-Zeile wie Kicker, in Großbuchstaben gesetzt (Text bleibt normal geschrieben → Kopfzeile)
    kicker = style_block("CASIKicker").group(0)
    reihe = kicker.replace('w:styleId="CASIKicker"', 'w:styleId="CASIReihe"').replace('<w:name w:val="CASI Kicker"/>', '<w:name w:val="CASI Reihe"/><w:next w:val="CASITitel"/>')
    reihe = reihe.replace('<w:i w:val="0"/>', '<w:i w:val="0"/><w:caps/>', 1).replace('<w:color w:val="0E4D49"/>', '<w:color w:val="0E4D49"/><w:spacing w:val="14"/>', 1)
    xml = xml.replace(kicker, kicker + reihe)

    # Gliederungsebenen → Navigationsbereich, Inhaltsverzeichnis
    for sid, lvl in (("CASIUeberschrift1", 0), ("CASIUeberschrift2", 1), ("CASIUeberschrift3", 2)):
        blk = style_block(sid).group(0)
        xml = xml.replace(blk, blk.replace("</w:pPr>", f'<w:outlineLvl w:val="{lvl}"/></w:pPr>', 1))

    # Word-eigene Vorlagen im CASI-Look (falls jemand „Überschrift 1“ usw. wählt)
    builtin = {
        "Heading1": ('heading 1', "CASIUeberschrift1", '<w:pPr><w:outlineLvl w:val="0"/></w:pPr>'),
        "Heading2": ('heading 2', "CASIUeberschrift2", '<w:pPr><w:outlineLvl w:val="1"/></w:pPr>'),
        "Heading3": ('heading 3', "CASIUeberschrift3", '<w:pPr><w:outlineLvl w:val="2"/></w:pPr>'),
        "Caption": ('caption', "CASIBildunterschrift", ""),
    }
    for sid, (name, base, ppr) in builtin.items():
        m = style_block(sid)
        new = f'<w:style w:type="paragraph" w:styleId="{sid}"><w:name w:val="{name}"/><w:basedOn w:val="{base}"/><w:next w:val="CASIFliesstext"/><w:uiPriority w:val="9"/><w:qFormat/>{ppr}</w:style>'
        xml = xml.replace(m.group(0), new) if m else xml.replace("</w:styles>", new + "</w:styles>")

    extra = (
        '<w:style w:type="paragraph" w:styleId="TOC1"><w:name w:val="toc 1"/><w:basedOn w:val="CASIFliesstext"/><w:next w:val="CASIFliesstext"/><w:uiPriority w:val="39"/>'
        '<w:pPr><w:pBdr><w:bottom w:val="single" w:sz="4" w:space="5" w:color="E1E7E5"/></w:pBdr><w:spacing w:after="90"/></w:pPr></w:style>'
        '<w:style w:type="character" w:styleId="PlaceholderText"><w:name w:val="Placeholder Text"/><w:uiPriority w:val="99"/><w:semiHidden/><w:rPr><w:color w:val="5F7471"/></w:rPr></w:style>'
        '<w:style w:type="character" w:styleId="Hyperlink"><w:name w:val="Hyperlink"/><w:uiPriority w:val="99"/><w:rPr><w:color w:val="0E4D49"/><w:u w:val="single"/></w:rPr></w:style>'
    )
    for sid in ("TOC1", "PlaceholderText", "Hyperlink"):
        m = style_block(sid)
        if m:
            xml = xml.replace(m.group(0), "")
    xml = xml.replace("</w:styles>", extra + "</w:styles>")
    # Sichtbare Namen mit Umlauten; die Kennungen (styleId) bleiben ohne, damit nichts bricht
    for old, new in (("CASI Ueberschrift 1", "CASI Überschrift 1"), ("CASI Ueberschrift 2", "CASI Überschrift 2"),
                     ("CASI Ueberschrift 3", "CASI Überschrift 3"), ("CASI Fliesstext", "CASI Fließtext"), ("CASI Fussnote", "CASI Fußnote")):
        xml = xml.replace(f'<w:name w:val="{old}"/>', f'<w:name w:val="{new}"/>')
    return xml


def header(xml):
    """Kopfzeile: Reihe · Titel – automatisch aus dem Deckblatt (Feld STYLEREF)."""
    new = (
        fld('STYLEREF "CASI Reihe" \\* MERGEFORMAT', "CASI Whitepaper · No. X")
        + run(" · ")
        + fld('STYLEREF "CASI Titel" \\* MERGEFORMAT', "Titel des Whitepapers")
    )
    return re.sub(r"(<w:pPr>.*?</w:pPr>).*?(</w:p>)", lambda m: m.group(1) + new + m.group(2), xml, count=1, flags=re.S)


def build(out_dir):
    zin = zipfile.ZipFile(SRC)
    files = {n: zin.read(n) for n in zin.namelist()}

    doc = files["word/document.xml"].decode()
    start = doc.index("<w:body>") + len("<w:body>")
    sect = re.search(r"<w:sectPr.*?</w:sectPr>", doc, re.S).group(0)
    orig = re.findall(r"<w:p[ >].*?</w:p>", doc[start:], re.S)
    doc = doc[:start] + body(orig) + sect + "</w:body></w:document>"
    files["word/document.xml"] = doc.encode()

    files["word/styles.xml"] = styles(files["word/styles.xml"].decode()).encode()
    files["word/header1.xml"] = header(files["word/header1.xml"].decode()).encode()

    # nicht mehr gebrauchte Abbildungen des Whitepapers entfernen (Logo bleibt)
    rels = files["word/_rels/document.xml.rels"].decode()
    for n in ("image2.png", "image3.png", "image4.png", "image5.png"):
        files.pop(f"word/media/{n}", None)
        rels = re.sub(rf'<Relationship [^>]*Target="media/{n}"/>', "", rels)
    files["word/_rels/document.xml.rels"] = rels.encode()

    core = files["docProps/core.xml"].decode()
    core = re.sub(r"<dc:title>.*?</dc:title>", "<dc:title>CASI Whitepaper</dc:title>", core)
    files["docProps/core.xml"] = core.encode()

    os.makedirs(out_dir, exist_ok=True)
    for name, ctype in (("CASI-Whitepaper.dotx", CT_DOT), ("CASI-Whitepaper-Vorschau.docx", CT_DOC)):
        out = os.path.join(out_dir, name)
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            for n in zin.namelist():
                if n not in files:
                    continue
                d = files[n]
                if n == "[Content_Types].xml":
                    d = d.decode().replace(CT_DOC, ctype).encode()
                z.writestr(n, ordne(n, d))
        print("geschrieben:", out)


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else ".")
