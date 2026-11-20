"""Generate the one-page partner PDF using only the Python standard library."""

from pathlib import Path

PAGE_W = 612
PAGE_H = 792
MARGIN = 54

LINES = [
    ("ADT WORK - PARTNER ONE-PAGER", 18, True, 0),
    ("Vetted African talent. Fixed-price tasks. Weekly delivery.", 11, False, 10),
    ("Partner kit - ADT Community - adt-community.github.io/partner.html", 9, False, 6),
    ("WHAT YOU GET", 12, True, 26),
    ("Vetted contributors living in Africa. Each task goes to a person", 10, False, 6),
    ("checked against a real brief, not an anonymous crowd.", 10, False, 0),
    ("Fixed price, agreed first: $20 per approved task, no hourly billing.", 10, False, 0),
    ("Weekly delivery. A reviewer checks the result against a written", 10, False, 0),
    ("'done when' list; approved work is paid by Wednesday.", 10, False, 0),
    ("HOW THE PILOT WORKS", 12, True, 26),
    ("1. You send a one-paragraph brief and an acceptance test.", 10, False, 6),
    ("2. We turn it into a task and assign a contributor within 2 days.", 10, False, 0),
    ("3. The work is delivered within 7 days and reviewed by you.", 10, False, 0),
    ("4. Approved work is paid that week; you give a short written review.", 10, False, 0),
    ("PRICING", 12, True, 26),
    ("Standard: $20 contributor reward + $3 platform fee (15%) = $23", 10, False, 6),
    ("per approved task. Nothing is charged for work that fails review.", 10, False, 0),
    ("Pilot: first two approved tasks at $20 each - platform fee waived", 10, False, 0),
    ("($40 total instead of $46). Standard pricing from task three.", 10, False, 0),
    ("WHAT WE NEED FROM YOU", 12, True, 26),
    ("A named reviewer (2 working days to approve), access to any tools", 10, False, 6),
    ("the task needs, and a clear definition of a correct result.", 10, False, 0),
    ("START A PILOT", 12, True, 26),
    ("https://adt-community.github.io/partner.html", 11, False, 6),
    ("Questions: github.com/ADT-community/adt-community.github.io", 9, False, 0),
    ("ADT Community - open source projects solving African problems.", 9, False, 26),
]


def pdf_string(text):
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def build_content():
    y = PAGE_H - MARGIN - 12
    parts = []
    for text, size, bold, gap in LINES:
        y -= gap
        if y < MARGIN:
            raise ValueError("One-pager does not fit on a single page")
        font = "/F2" if bold else "/F1"
        parts.append(f"BT {font} {size} Tf {MARGIN} {y} Td ({pdf_string(text)}) Tj ET\n")
        y -= size + 7
    return "".join(parts).encode("ascii")


def build_pdf():
    content = build_content()
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {PAGE_W} {PAGE_H}] "
         "/Resources << /Font << /F1 5 0 R /F2 6 0 R >> >> /Contents 4 0 R >>").encode("ascii"),
        b"<< /Length " + str(len(content)).encode("ascii") + b" >>\nstream\n" + content + b"endstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>",
    ]
    out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for i, obj in enumerate(objects, 1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n".encode("ascii") + obj + b"\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode("ascii")
    out += b"0000000000 65535 f \n"
    for offset in offsets[1:]:
        out += f"{offset:010d} 00000 n \n".encode("ascii")
    out += ("trailer\n<< /Size " + str(len(objects) + 1) + " /Root 1 0 R >>\nstartxref\n"
            + str(xref) + "\n%%EOF\n").encode("ascii")
    return bytes(out)


def main():
    target = Path(__file__).with_name("one-pager.pdf")
    target.write_bytes(build_pdf())
    print(f"{target} ({target.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
