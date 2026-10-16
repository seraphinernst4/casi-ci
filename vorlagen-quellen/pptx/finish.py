"""Nachbearbeitung der von build.js geschriebenen .pptx:
1. CASI-Farbschema ins Theme schreiben (über apply_theme.js aus dem pptx-Skill oder eigenem Ersatz)
2. PP Mori und PP Mori Semibold einbetten (.fntdata, damit es ohne installierte Schrift stimmt)
3. Für die Vorlage zusätzlich eine .potx erzeugen

Aufruf: python3 finish.py <ordner> <ordner-mit-PPMori-TTFs>
Die TTFs liegen NICHT im Repo (Lizenz) – sie kommen aus CASI-Schriften.zip.
"""
import os
import re
import shutil
import sys
import zipfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "fonts"))
from eot import make_eot  # noqa: E402

sys.path.insert(0, os.path.dirname(__file__))
import json  # noqa: E402
from grafiken import inject  # noqa: E402

THEME = {
    "dk1": "0E4D49",  # Tinte – Text
    "lt1": "FFFFFF",  # Papier
    "dk2": "5F7471",  # Leise – Nebentext
    "lt2": "EEF2F1",  # Block – Boxen
    "accent1": "0E4D49",  # Diagramm-Reihe 1: Deep Green
    "accent2": "5F7471",  # Reihe 2: Slate
    "accent3": "93AFAD",  # Reihe 3: Deep-Green-Ton (Verbinder)
    "accent4": "C5D4D3",  # Reihe 4: Kante
    "accent5": "E1E7E5",  # Linie
    "accent6": "8B1538",  # Burgundy – höchstens zweimal pro Seite
    "hlink": "0E4D49",  # Links in Textfarbe
    "folHlink": "0E4D49",
}

# Familie in PowerPoint → Schnitte (regular/italic) → TTF-Datei
FONTS = [
    ("PP Mori", {"regular": "PPMori-Regular.ttf"}),
    ("PP Mori Semibold", {"regular": "PPMori-Semibold.ttf"}),
    ("IBM Plex Serif", {"regular": "IBMPlexSerif-Regular.ttf", "italic": "IBMPlexSerif-Italic.ttf"}),
]
BOX_PROMPT = "Text in der Box"
EMU = 914400
BOX_PAD = int(0.3 * EMU)
REL_FONT = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/font"
CT_PRES = "application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"
CT_POTX = "application/vnd.openxmlformats-officedocument.presentationml.template.main+xml"


EXTRA = [  # Zusatzfarben (ci/tokens.json → colorExtra) – erscheinen in PowerPoint unter „Benutzerdefinierte Farben“
    ("ICCA", "13917C"), ("ICCA Grafik", "1A9C7E"), ("Burgundy hell", "F6EBEF"), ("Burgundy mittel", "CB96A6"),
    ("Kette iron", "A75F26"), ("Kette steel", "1A6685"), ("Kette body", "17876F"), ("Kette car", "2A7A4B"),
    ("Kette Lebensende", "85499E"), ("Grafik Tinte", "29363D"), ("Grafik leise", "54626A"), ("Burgundy Rand", "E3C2CD"),
    ("Daten A", "B060E0"), ("Daten B", "3060C0"), ("Daten C", "2080B0"), ("Daten D", "50B0D0"), ("Daten E", "20C090"),
    ("Daten F", "30A060"), ("Daten G", "E08820"), ("Daten H", "D06020"), ("Daten I", "E04040"), ("Daten J", "C04080"),
]


def theme_xml(xml):
    scheme = '<a:clrScheme name="CASI">' + "".join(
        f'<a:{k}><a:srgbClr val="{v}"/></a:{k}>' for k, v in THEME.items()
    ) + "</a:clrScheme>"
    xml = re.sub(r"<a:clrScheme\b[\s\S]*?</a:clrScheme>", scheme, xml, count=1)
    xml = re.sub(r'(<a:(?:theme|fontScheme)\b[^>]*?\bname=")[^"]*"', r'\1CASI"', xml)
    cust = "<a:custClrLst>" + "".join(f'<a:custClr name="{n}"><a:srgbClr val="{h}"/></a:custClr>' for n, h in EXTRA) + "</a:custClrLst>"
    xml = re.sub(r"<a:custClrLst>[\s\S]*?</a:custClrLst>", "", xml)
    if "<a:extraClrSchemeLst/>" in xml:
        xml = xml.replace("<a:extraClrSchemeLst/>", "<a:extraClrSchemeLst/>" + cust, 1)
    elif "</a:extraClrSchemeLst>" in xml:
        xml = xml.replace("</a:extraClrSchemeLst>", "</a:extraClrSchemeLst>" + cust, 1)
    else:
        xml = xml.replace("</a:theme>", cust + "</a:theme>", 1)
    return xml


def fix_shapes(xml):
    """Platzhalter ohne Innenabstand; Box-Platzhalter werden zur mitwachsenden grauen Box."""
    def one(m):
        sp = m.group(0)
        if "<p:ph" not in sp:
            return sp
        if BOX_PROMPT in sp:
            sp = re.sub(
                r'<a:prstGeom prst="rect"><a:avLst>\s*</a:avLst></a:prstGeom><a:noFill/><a:ln>\s*</a:ln>',
                '<a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val 4000"/></a:avLst></a:prstGeom>'
                '<a:solidFill><a:srgbClr val="EEF2F1"/></a:solidFill><a:ln><a:noFill/></a:ln>',
                sp,
            )
            ins = f'lIns="{BOX_PAD}" tIns="{BOX_PAD}" rIns="{BOX_PAD}" bIns="{BOX_PAD}"'
            sp = re.sub(r"<a:bodyPr([^>]*?)(/?)>", lambda b: f"<a:bodyPr{b.group(1)} {ins}><a:spAutoFit/></a:bodyPr>" if b.group(2) else f"<a:bodyPr{b.group(1)} {ins}><a:spAutoFit/>", sp, count=1)
            sp = sp.replace("<a:spAutoFit/></a:bodyPr></a:bodyPr>", "<a:spAutoFit/></a:bodyPr>")
        elif "lIns=" not in sp:
            sp = re.sub(r"<a:bodyPr\b", '<a:bodyPr lIns="0" tIns="0" rIns="0" bIns="0"', sp, count=1)
        return sp
    return exact_radius(re.sub(r"<p:sp>[\s\S]*?</p:sp>", one, xml))


def exact_radius(xml):
    """Eckenradius aller Boxen exakt 0,1″: adj = Radius / min(Breite, Höhe) × 100000.
    So decken sich Layout-Box und Folien-Box an den oberen Ecken genau."""
    def radius(m):
        w, h = int(m.group(1)), int(m.group(2))
        adj = round(0.1 * EMU / min(w, h) * 100000)
        return f'<a:ext cx="{w}" cy="{h}"/></a:xfrm><a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val {adj}"/></a:avLst>'
    return re.sub(r'<a:ext cx="(\d+)" cy="(\d+)"/></a:xfrm><a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val \d+"/></a:avLst>', radius, xml)


def box_idx(layout_xml):
    return set(re.findall(r'idx="(\d+)"[^>]*?/></p:nvPr></p:nvSpPr><p:spPr><a:xfrm>[^<]*<a:off[^>]*/><a:ext[^>]*/></a:xfrm><a:prstGeom prst="roundRect"', layout_xml.replace("\n", "").replace("\t", "")))


def text_height(paras, width_emu, fonts_dir):
    """Höhe einer mitwachsenden Box schätzen (PowerPoint passt sie erst beim Bearbeiten an)."""
    from PIL import ImageFont
    from fontTools.ttLib import TTFont

    size = 12
    ttf = os.path.join(fonts_dir, "IBMPlexSerif-Regular.ttf")
    tt = TTFont(ttf)
    upm = tt["head"].unitsPerEm
    os2 = tt["OS/2"]
    # Gemessen in PowerPoint (Mac): IBM Plex Serif 12 pt bei 135 % → Zeilenabstand ≈ 1,625 × Schriftgröße
    line = 1.625 * size
    font = ImageFont.truetype(ttf, size * 10)
    inner = (width_emu - 2 * BOX_PAD) / EMU * 72 * 10 * 0.97  # Sicherheitsabstand: PowerPoint bricht früher um
    lines = 0
    for para in paras:
        cur = ""
        n = 1
        for word in para.split():
            test = (cur + " " + word).strip()
            if font.getlength(test) > inner and cur:
                n += 1
                cur = word
            else:
                cur = test
        lines += n
    pts = lines * line + 6 * (len(paras) - 1)
    return int(((pts + line) / 72 + 2 * BOX_PAD / EMU) * EMU)  # eine Zeile Reserve


def fix_slide(xml, boxes, fonts_dir):
    def one(m):
        sp = m.group(0)
        idx = re.search(r'idx="(\d+)"', sp)
        if not idx or idx.group(1) not in boxes:
            return sp
        sp = re.sub(
            r'<a:prstGeom prst="rect"><a:avLst>\s*</a:avLst></a:prstGeom><a:noFill/><a:ln>\s*</a:ln>',
            '<a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val 4000"/></a:avLst></a:prstGeom>'
            '<a:solidFill><a:srgbClr val="EEF2F1"/></a:solidFill><a:ln><a:noFill/></a:ln>',
            sp,
        )
        sp = re.sub(r'lIns="0" tIns="0" rIns="0" bIns="0"', f'lIns="{BOX_PAD}" tIns="{BOX_PAD}" rIns="{BOX_PAD}" bIns="{BOX_PAD}"', sp, count=1)
        sp = re.sub(r"(<a:bodyPr[^>]*>)(</a:bodyPr>)", r"\1<a:noAutofit/>\2", sp, count=1)  # feste, berechnete Höhe: gleiches Bild in PowerPoint, Keynote, PDF
        paras = ["".join(re.findall(r"<a:t>([^<]*)</a:t>", p)) for p in re.findall(r"<a:p>[\s\S]*?</a:p>", sp)]
        paras = [p for p in paras if p.strip()]
        w = int(re.search(r'<a:ext cx="(\d+)"', sp).group(1))
        h = text_height(paras, w, fonts_dir)
        sp = re.sub(r'(<a:ext cx="\d+" cy=")\d+(")', lambda e: f"{e.group(1)}{h}{e.group(2)}", sp, count=1)
        return sp
    xml = re.sub(r"<p:sp>[\s\S]*?</p:sp>", one, xml)
    # Boxen nebeneinander (gleiche y-Position) bekommen die gleiche Höhe – die größte
    rows = {}
    for m in re.finditer(r'<a:off x="\d+" y="(\d+)"/><a:ext cx="\d+" cy="(\d+)"/></a:xfrm><a:prstGeom prst="roundRect"', xml):
        rows.setdefault(m.group(1), []).append(int(m.group(2)))
    for y, hs in rows.items():
        if len(hs) > 1:
            xml = re.sub(rf'(<a:off x="\d+" y="{y}"/><a:ext cx="\d+" cy=")\d+("/></a:xfrm><a:prstGeom prst="roundRect")', lambda e: f"{e.group(1)}{max(hs)}{e.group(2)}", xml)
    return exact_radius(xml)


def process(src, fonts_dir, potx=False, grafiken=None):
    tmp = src + ".tmp"
    zin = zipfile.ZipFile(src)
    zout = zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED)
    files = {n: zin.read(n) for n in zin.namelist()}

    # 0 Website-Grafiken einsetzen (nur Beispielpräsentation)
    if grafiken:
        here = os.path.dirname(__file__)
        T = json.load(open(os.path.join(here, "beispiel-text.json"), encoding="utf-8"))
        web = zipfile.ZipFile(os.path.join(here, "website-grafiken.pptx"))
        titles = {g["titel"]: g["quelle"] for g in T["grafiken"]}
        for n in sorted(k for k in files if re.match(r"ppt/slides/slide\d+\.xml$", k)):
            xml = files[n].decode()
            for title, no in titles.items():
                if f"<a:t>{title}</a:t>" in xml and "Nur Titel" in files[n.replace("slides/", "slides/_rels/") + ".rels"].decode() + "Nur Titel":
                    k = inject(files, n, web, no, str(no))
                    print(f"  Grafik {no} ({title}) → {n}: {k} Formen")
        if 'Extension="svg"' not in files["[Content_Types].xml"].decode():
            files["[Content_Types].xml"] = files["[Content_Types].xml"].decode().replace("<Default ", '<Default Extension="svg" ContentType="image/svg+xml"/><Default ', 1).encode()
        if 'Extension="png"' not in files["[Content_Types].xml"].decode():
            files["[Content_Types].xml"] = files["[Content_Types].xml"].decode().replace("<Default ", '<Default Extension="png" ContentType="image/png"/><Default ', 1).encode()

    # 1 Theme
    files["ppt/theme/theme1.xml"] = theme_xml(files["ppt/theme/theme1.xml"].decode()).encode()

    # Layouts: Innenabstände, Boxen
    for n in list(files):
        if n.startswith("ppt/slideLayouts/slideLayout") and n.endswith(".xml"):
            files[n] = fix_shapes(files[n].decode()).encode()

    # Folien: Platzhalter, die im Layout Boxen sind, ebenfalls als Box (pptxgenjs schreibt eigene Geometrie)
    for n in list(files):
        if re.match(r"ppt/slides/slide\d+\.xml$", n):
            rel = files[n.replace("slides/", "slides/_rels/") + ".rels"].decode()
            lay = re.search(r'Target="\.\./slideLayouts/(slideLayout\d+\.xml)"', rel).group(1)
            boxes = box_idx(files["ppt/slideLayouts/" + lay].decode())
            if boxes:
                files[n] = fix_slide(files[n].decode(), boxes, fonts_dir).encode()

    # 2 Schriften
    rels = files["ppt/_rels/presentation.xml.rels"].decode()
    pres = files["ppt/presentation.xml"].decode()
    ct = files["[Content_Types].xml"].decode()
    entries = []
    i = 0
    for family, styles in FONTS:
        parts = ""
        for style in ("regular", "bold", "italic", "boldItalic"):
            if style not in styles:
                continue
            i += 1
            data, fam = make_eot(os.path.join(fonts_dir, styles[style]))
            assert fam == family, (fam, family)
            files[f"ppt/fonts/font{i}.fntdata"] = data
            rid = f"rIdCasiFont{i}"
            rels = rels.replace("</Relationships>", f'<Relationship Id="{rid}" Type="{REL_FONT}" Target="fonts/font{i}.fntdata"/></Relationships>')
            parts += f'<p:{style} r:id="{rid}"/>'
        entries.append(f'<p:embeddedFont><p:font typeface="{family}" pitchFamily="2" charset="0"/>{parts}</p:embeddedFont>')
    if 'Extension="fntdata"' not in ct:
        ct = ct.replace("<Default ", '<Default Extension="fntdata" ContentType="application/x-fontdata"/><Default ', 1)
    lst = "<p:embeddedFontLst>" + "".join(entries) + "</p:embeddedFontLst>"
    # Reihenfolge laut Schema: … sldSz, notesSz, smartTags?, embeddedFontLst, custShowLst …
    pres = re.sub(r"(<p:notesSz\b[^>]*/>)", r"\1" + lst, pres, count=1)
    if "embedTrueTypeFonts" not in pres:
        pres = re.sub(r"<p:presentation\b", '<p:presentation embedTrueTypeFonts="1"', pres, count=1)
    files["ppt/_rels/presentation.xml.rels"] = rels.encode()
    files["ppt/presentation.xml"] = pres.encode()
    files["[Content_Types].xml"] = ct.encode()

    for n in zin.namelist():
        zout.writestr(n, files.pop(n))
    for n, d in files.items():  # neue Teile (Schriften)
        zout.writestr(n, d)
    zout.close()
    zin.close()
    shutil.move(tmp, src)

    if potx:
        out = src[:-5] + ".potx"
        zin = zipfile.ZipFile(src)
        zout = zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED)
        for n in zin.namelist():
            d = zin.read(n)
            if n == "[Content_Types].xml":
                d = d.decode().replace(CT_PRES, CT_POTX).encode()
            zout.writestr(n, d)
        zout.close()
        print("geschrieben:", out)
    print("fertig:", src)


if __name__ == "__main__":
    folder, fonts_dir = sys.argv[1], sys.argv[2]
    process(os.path.join(folder, "CASI-Folien.pptx"), fonts_dir, potx=True)
    process(os.path.join(folder, "CASI-Folien-Beispiel.pptx"), fonts_dir, grafiken=True)
