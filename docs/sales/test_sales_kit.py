import re
import unittest
from pathlib import Path

SALES = Path(__file__).resolve().parent
ROOT = SALES.parent.parent


def read(name):
    return (SALES / name).read_text(encoding="utf-8")


def read_root(name):
    return (ROOT / name).read_text(encoding="utf-8")


class SalesKitTests(unittest.TestCase):
    def test_one_pager_is_one_page_pdf(self):
        data = (SALES / "one-pager.pdf").read_bytes()
        self.assertTrue(data.startswith(b"%PDF-"))
        self.assertEqual(len(re.findall(rb"/Type\s*/Page\b", data)), 1)
        self.assertIn(b"/Count 1", data)
        self.assertTrue(data.rstrip().endswith(b"%%EOF"))

    def test_one_pager_content(self):
        text = (SALES / "one-pager.pdf").read_bytes().decode("latin-1")
        for phrase in ("Vetted African talent", "Fixed-price tasks", "Weekly delivery",
                       "$20", "15%", "$3", "$23", "Pilot", "$40", "partner.html"):
            self.assertIn(phrase, text, phrase)

    def test_one_pager_renders(self):
        try:
            import pymupdf
        except ImportError:
            self.skipTest("pymupdf is not installed; raw PDF structure was checked instead")
        doc = pymupdf.open(SALES / "one-pager.pdf")
        self.assertEqual(doc.page_count, 1)
        self.assertIn("15%", doc[0].get_text())

    def test_pricing_matches_pitch(self):
        text = read("pricing.md")
        for phrase in ("15%", "$3", "$23", "$20", "$40", "first two approved tasks"):
            self.assertIn(phrase, text, phrase)

    def test_thirty_companies(self):
        rows = [line for line in read("target-companies.md").splitlines()
                if re.match(r"^\|\s*\d+\s*\|", line)]
        self.assertEqual(len(rows), 30)
        names = set()
        for row in rows:
            cells = [cell.strip() for cell in row.strip().strip("|").split("|")]
            self.assertEqual(len(cells), 7, row)
            number, name, kind, where, url, task, source = cells
            self.assertTrue(number.isdigit())
            self.assertTrue(name and name not in names, name)
            names.add(name)
            self.assertIn(kind, ("Startup", "Agency", "NGO"), kind)
            self.assertTrue(where)
            self.assertTrue(url.startswith(("https://", "http://")), url)
            self.assertGreater(len(task), 15, task)
            self.assertTrue(source)
        all_text = read("target-companies.md")
        for kind in ("Startup", "Agency", "NGO"):
            self.assertIn(kind, all_text)

    def test_work_page_has_partner_section(self):
        page = read_root("work.html")
        self.assertIn('id="partners"', page)
        self.assertIn('href="work.html#partners"', page)
        for phrase in ("Vetted African talent", "Fixed-price tasks", "Weekly delivery",
                       "15%", "$23", "Pilot offer", "$40", "docs/sales/one-pager.pdf",
                       'href="docs/sales/pricing.md"', 'href="partner.html"'):
            self.assertIn(phrase, page, phrase)

    def test_partner_page_matches_pricing(self):
        page = read_root("partner.html")
        for phrase in ("15%", "$23", "$20", "$40", "docs/sales/one-pager.pdf",
                       "docs/sales/pricing.md"):
            self.assertIn(phrase, page, phrase)

    def test_local_links_exist(self):
        for page in ("work.html", "partner.html"):
            text = read_root(page)
            for href in re.findall(r'href="([^"#][^"]*)"', text):
                if href.startswith(("http://", "https://", "mailto:")) or "${" in href:
                    continue
                target = href.split("#")[0].split("?")[0]
                self.assertTrue((ROOT / target).exists(), f"{page}: {href}")


if __name__ == "__main__":
    unittest.main()
