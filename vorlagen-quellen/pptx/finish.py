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

FONTS = [("PP Mori", "PPMori-Regular.ttf"), ("PP Mori Semibold", "PPMori-Semibold.ttf")]
REL_FONT = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/font"
CT_PRES = "application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"
CT_POTX = "application/vnd.openxmlformats-officedocument.presentationml.template.main+xml"


def theme_xml(xml):
    scheme = '<a:clrScheme name="CASI">' + "".join(
        f'<a:{k}><a:srgbClr val="{v}"/></a:{k}>' for k, v in THEME.items()
    ) + "</a:clrScheme>"
    xml = re.sub(r"<a:clrScheme\b[\s\S]*?</a:clrScheme>", scheme, xml, count=1)
    xml = re.sub(r'(<a:(?:theme|fontScheme)\b[^>]*?\bname=")[^"]*"', r'\1CASI"', xml)
    return xml


def process(src, fonts_dir, potx=False):
    tmp = src + ".tmp"
    zin = zipfile.ZipFile(src)
    zout = zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED)
    files = {n: zin.read(n) for n in zin.namelist()}

    # 1 Theme
    files["ppt/theme/theme1.xml"] = theme_xml(files["ppt/theme/theme1.xml"].decode()).encode()

    # 2 Schriften
    rels = files["ppt/_rels/presentation.xml.rels"].decode()
    pres = files["ppt/presentation.xml"].decode()
    ct = files["[Content_Types].xml"].decode()
    entries = []
    for i, (family, ttf) in enumerate(FONTS, 1):
        data, fam = make_eot(os.path.join(fonts_dir, ttf))
        assert fam == family, (fam, family)
        files[f"ppt/fonts/font{i}.fntdata"] = data
        rid = f"rIdCasiFont{i}"
        rels = rels.replace("</Relationships>", f'<Relationship Id="{rid}" Type="{REL_FONT}" Target="fonts/font{i}.fntdata"/></Relationships>')
        entries.append(f'<p:embeddedFont><p:font typeface="{family}" pitchFamily="2" charset="0"/><p:regular r:id="{rid}"/></p:embeddedFont>')
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
    process(os.path.join(folder, "CASI-Folien-Beispiel.pptx"), fonts_dir)
