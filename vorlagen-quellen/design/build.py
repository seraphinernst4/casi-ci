"""Baut CASI.thmx (Office-Design für Word, PowerPoint, Excel) und CASI-Farben.ase (Farbfelder für
Illustrator, InDesign, Photoshop). Quelle der Farben: ci/tokens.json. Theme-XML aus der fertigen Folienvorlage.
Aufruf: python3 build.py <ausgabe-ordner>"""
import io, json, re, struct, sys, zipfile
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
tokens = json.loads((ROOT / "ci/tokens.json").read_text())

# Namen wie in PowerPoint (finish.py → EXTRA) und auf der Website
NAMEN = {"page": "Papier", "box": "Box", "text": "Deep Green", "secondary": "Slate", "rule": "Linie", "accent": "Burgundy",
         "box-edge": "Boxkante", "connector": "Verbinder", "icca": "ICCA", "icca-grafik": "ICCA Grafik",
         "burgundy-hell": "Burgundy hell", "burgundy-mittel": "Burgundy mittel", "burgundy-rose": "Burgundy Rand",
         "kette-direct": "Grafik Tinte", "kette-iron": "Kette iron", "kette-steel": "Kette steel", "kette-body": "Kette body",
         "kette-car": "Kette car", "kette-leben": "Kette Lebensende", "grafik-leise": "Grafik leise"}
NAMEN.update({f"x{i}": f"Daten {chr(64 + i)}" for i in range(1, 11)})

def farben(gruppe):
    return [(NAMEN.get(k, k), v["$value"].lstrip("#").upper()) for k, v in tokens[gruppe].items() if isinstance(v, dict) and "$value" in v]

# ---------- Office-Design (.thmx)
with zipfile.ZipFile(ROOT / "vorlagen/CASI-Folien.potx") as z:
    theme = z.read("ppt/theme/theme1.xml").decode("utf8")
theme = re.sub(r'(<a:theme\b[^>]*?\bname=")[^"]*"', r'\1CASI"', theme)

ui = farben("color")
thumb = Image.new("RGB", (256, 192), "#FFFFFF")
d = ImageDraw.Draw(thumb)
order = ["0E4D49", "5F7471", "93AFAD", "C5D4D3", "EEF2F1", "8B1538"]
for i, h in enumerate(order):
    d.rounded_rectangle([16 + i * 38, 120, 16 + i * 38 + 30, 176], 4, fill="#" + h)
d.text((16, 24), "CASI", fill="#0E4D49")
buf = io.BytesIO(); thumb.save(buf, "JPEG", quality=92)

ct = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
      '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
      '<Default Extension="xml" ContentType="application/xml"/><Default Extension="jpeg" ContentType="image/jpeg"/>'
      '<Override PartName="/theme/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/></Types>')
rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme/theme1.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/thumbnail" Target="docProps/thumbnail.jpeg"/></Relationships>')
with zipfile.ZipFile(OUT / "CASI.thmx", "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("[Content_Types].xml", ct)
    z.writestr("_rels/.rels", rels)
    z.writestr("theme/theme/theme1.xml", theme)
    z.writestr("docProps/thumbnail.jpeg", buf.getvalue())

# ---------- Adobe Swatch Exchange (.ase)
def utf16(s):
    return struct.pack(">H", len(s) + 1) + s.encode("utf-16-be") + b"\x00\x00"
def block(typ, data):
    return struct.pack(">HI", typ, len(data)) + data
def gruppe(name, eintraege):
    out = [block(0xC001, utf16(name))]
    for n, h in eintraege:
        r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
        out.append(block(0x0001, utf16(f"CASI {n} #{h}") + b"RGB " + struct.pack(">fff", r, g, b) + struct.pack(">H", 2)))
    out.append(block(0xC002, b""))
    return out, len(eintraege) + 2
gruppen = [("CASI UI-Farben (Text, Flächen)", ui), ("CASI Zusatzfarben (nur Grafiken)", farben("colorExtra"))]
bl, n = [], 0
for name, e in gruppen:
    b, k = gruppe(name, e); bl += b; n += k
(OUT / "CASI-Farben.ase").write_bytes(b"ASEF" + struct.pack(">HHI", 1, 0, n) + b"".join(bl))
print("geschrieben:", OUT / "CASI.thmx", OUT / "CASI-Farben.ase", len(ui), "UI-Farben,", len(farben("colorExtra")), "Zusatzfarben")
