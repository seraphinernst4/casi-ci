"""Nachbearbeitung der Plakate mit den Funktionen der Folienvorlage (../pptx/finish.py):
Theme und Zusatzfarben, Eckenradius je Format (A3 0,14″, A1 0,28″), Schriften einbetten, .potx.
Aufruf: python3 finish.py <ordner> <TTF-Ordner>"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pptx"))
import finish as F

import re, zipfile, shutil

def runde_boxen(src):
    """Graue Rechtecke in den Layouts werden zu abgerundeten Boxen (exakter Radius folgt in F.process)."""
    tmp = src + ".tmp"
    with zipfile.ZipFile(src) as zi, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zo:
        for n in zi.namelist():
            d = zi.read(n)
            if n.startswith("ppt/slideLayouts/slideLayout") and n.endswith(".xml"):
                d = d.decode().replace('<a:srgbClr val="EEF2F1"/></a:solidFill><a:ln></a:ln>', '<a:srgbClr val="EEF2F1"/></a:solidFill><a:ln><a:noFill/></a:ln>').encode()
                d = re.sub(r'<a:prstGeom prst="rect"><a:avLst\s*/?>(?:</a:avLst>)?</a:prstGeom>(<a:solidFill><a:srgbClr val="EEF2F1")',
                           r'<a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val 4000"/></a:avLst></a:prstGeom>\1', d.decode()).encode()
            zo.writestr(n, d)
    shutil.move(tmp, src)

folder, fonts = sys.argv[1], sys.argv[2]
for name, radius in (("A3", 0.14), ("A1", 0.28)):
    F.RADIUS = radius
    for f in (f"CASI-Plakat-{name}.pptx", f"CASI-Plakat-{name}-Beispiel.pptx"):
        runde_boxen(os.path.join(folder, f))
    F.process(os.path.join(folder, f"CASI-Plakat-{name}.pptx"), fonts, potx=True)
    F.process(os.path.join(folder, f"CASI-Plakat-{name}-Beispiel.pptx"), fonts)
