"""TrueType -> Embedded OpenType (.fntdata), wie PowerPoint eingebettete Schriften speichert.

Aufruf:  python3 eot.py Schrift.ttf ziel.fntdata
Unkomprimiert, ohne XOR-Verschlüsselung (EOT Version 0x00020001).
"""
import struct
import sys

from fontTools.ttLib import TTFont


def name(font, nid):
    return font["name"].getDebugName(nid) or ""


def make_eot(ttf_path):
    data = open(ttf_path, "rb").read()
    f = TTFont(ttf_path)
    os2, head = f["OS/2"], f["head"]

    def utf16(s):
        b = s.encode("utf-16-le")
        return struct.pack("<H", len(b)) + b

    panose = os2.panose
    panose_bytes = bytes(
        [
            panose.bFamilyType, panose.bSerifStyle, panose.bWeight, panose.bProportion,
            panose.bContrast, panose.bStrokeVariation, panose.bArmStyle, panose.bLetterForm,
            panose.bMidline, panose.bXHeight,
        ]
    )
    italic = 1 if (os2.fsSelection & 1) else 0

    body = b"".join(
        [
            struct.pack("<I", 0x00020001),  # Version
            struct.pack("<I", 0),  # Flags
            panose_bytes,
            struct.pack("<B", 1),  # Charset DEFAULT_CHARSET
            struct.pack("<B", italic),
            struct.pack("<I", os2.usWeightClass),
            struct.pack("<H", os2.fsType),
            struct.pack("<H", 0x504C),  # MagicNumber
            struct.pack("<IIII", os2.ulUnicodeRange1, os2.ulUnicodeRange2, os2.ulUnicodeRange3, os2.ulUnicodeRange4),
            struct.pack("<II", getattr(os2, "ulCodePageRange1", 0), getattr(os2, "ulCodePageRange2", 0)),
            struct.pack("<I", head.checkSumAdjustment),
            struct.pack("<IIII", 0, 0, 0, 0),
            struct.pack("<H", 0) + utf16(name(f, 1)),
            struct.pack("<H", 0) + utf16(name(f, 2)),
            struct.pack("<H", 0) + utf16(name(f, 5)),
            struct.pack("<H", 0) + utf16(name(f, 4)),
            struct.pack("<H", 0) + utf16(""),  # RootString
        ]
    )
    eot_size = 8 + len(body) + len(data)
    return struct.pack("<II", eot_size, len(data)) + body + data, name(f, 1)


if __name__ == "__main__":
    out, family = make_eot(sys.argv[1])
    open(sys.argv[2], "wb").write(out)
    print(f"{sys.argv[2]}: {family} ({len(out)} Bytes)")
