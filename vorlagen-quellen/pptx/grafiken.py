"""Setzt Grafiken aus der Website-PowerPoint (Backend → Texte → Grafiken) als echte Formen
in Folien der Beispielpräsentation ein. Kicker, Titel, Fußzeile und Seitenzahl der Quelle
werden weggelassen – Titel und Seitenzahl kommen vom CASI-Layout.
"""
import re

REL_IMG = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"
EMU = 914400


def _shapes(spTree):
    """Direkte Kinder von spTree (sp, pic, grpSp, cxnSp) als Textstücke."""
    out, i = [], 0
    body = spTree
    pat = re.compile(r"<p:(sp|pic|grpSp|cxnSp)>")
    while True:
        m = pat.search(body, i)
        if not m:
            break
        tag = m.group(1)
        depth, j = 0, m.start()
        tok = re.compile(rf"<p:{tag}>|</p:{tag}>")
        for t in tok.finditer(body, m.start()):
            depth += 1 if not t.group(0).startswith("</") else -1
            if depth == 0:
                j = t.end()
                break
        out.append(body[m.start():j])
        i = j
    return out


def _is_frame(sh):
    """Kicker/Titel oben, Fußzeile/Seitenzahl unten."""
    off = re.search(r'<a:off x="(\d+)" y="(\d+)"/>', sh)
    has_text = bool(re.search(r"<a:t>[^<]+</a:t>", sh))
    if not off or not has_text:
        return False
    y = int(off.group(2)) / EMU
    return y < 1.0 or y > 7.0


def inject(files, slide_name, src_zip, src_no, tag):
    src = src_zip.read(f"ppt/slides/slide{src_no}.xml").decode()
    src_rels = src_zip.read(f"ppt/slides/_rels/slide{src_no}.xml.rels").decode()
    tree = src[src.index("<p:spTree>"):src.index("</p:spTree>")]
    shapes = [s for s in _shapes(tree) if not _is_frame(s)]
    xml = "".join(shapes)

    # Schrift: Website schreibt „PP Mori SemiBold“ + fett; CASI-Familie heißt „PP Mori Semibold“
    xml = re.sub(r'(<a:rPr[^>]*?) b="1"([^>]*>(?:(?!</a:rPr>).)*?typeface="PP Mori SemiBold")', r"\1\2", xml, flags=re.S)
    xml = xml.replace('typeface="PP Mori SemiBold"', 'typeface="PP Mori Semibold"')

    # IDs eindeutig machen
    counter = [1000]
    def new_id(m):
        counter[0] += 1
        return f'<p:cNvPr id="{counter[0]}"'
    xml = re.sub(r'<p:cNvPr id="\d+"', new_id, xml)

    # Bilder/SVG mitnehmen
    rels_name = slide_name.replace("slides/", "slides/_rels/") + ".rels"
    rels = files[rels_name].decode()
    targets = dict(re.findall(r'Id="([^"]+)"[^>]*Target="\.\./media/([^"]+)"', src_rels))
    mapping = {}
    for rid in sorted(set(re.findall(r'r:(?:embed|link)="([^"]+)"', xml))):
        media = targets[rid]
        new_media = f"web-{tag}-{media}"
        files[f"ppt/media/{new_media}"] = src_zip.read(f"ppt/media/{media}")
        new_rid = f"rIdWeb{tag}{len(mapping) + 1}"
        mapping[rid] = new_rid
        rels = rels.replace("</Relationships>", f'<Relationship Id="{new_rid}" Type="{REL_IMG}" Target="../media/{new_media}"/></Relationships>')
    xml = re.sub(r'r:(embed|link)="([^"]+)"', lambda m: f'r:{m.group(1)}="{mapping[m.group(2)]}"', xml)
    files[rels_name] = rels.encode()

    slide = files[slide_name].decode()
    slide = slide.replace("</p:spTree>", xml + "</p:spTree>", 1)
    for ns in re.findall(r'xmlns:(\w+)="[^"]+"', src[:src.index(">", src.index("<p:sld")) + 1]):
        decl = re.search(rf'xmlns:{ns}="[^"]+"', src).group(0)
        if f"xmlns:{ns}=" not in slide[:slide.index(">", slide.index("<p:sld")) + 1]:
            slide = slide.replace("<p:sld ", f"<p:sld {decl} ", 1)
    files[slide_name] = slide.encode()
    return len(shapes)
