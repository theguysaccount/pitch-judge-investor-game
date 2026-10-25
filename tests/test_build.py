import json
import os
import re
import tempfile
import unittest
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

from judge import data, site

BASE = "https://example.test/game"


class P(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.meta, self.title, self.ld = [], {}, "", []
        self._t = self._ld = False
        self._buf = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        if tag in ("link", "script") and (a.get("href") or a.get("src")):
            self.links.append(a.get("href") or a.get("src"))
        if tag == "meta" and (a.get("name") or a.get("property")):
            self.meta[a.get("name") or a.get("property")] = a.get("content", "")
        if tag == "link" and a.get("rel") == "canonical":
            self.meta["canonical"] = a["href"]
        if tag == "title" and not self.title:
            self._t = True
        if tag == "script" and a.get("type") == "application/ld+json":
            self._ld, self._buf = True, []

    def handle_endtag(self, tag):
        if tag == "title":
            self._t = False
        if tag == "script" and self._ld:
            self.ld.append("".join(self._buf))
            self._ld = False

    def handle_data(self, d):
        if self._t:
            self.title += d
        if self._ld:
            self._buf.append(d)


class BuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = tempfile.mkdtemp()
        os.environ["PJ_BASE_URL"] = BASE
        site.build(out=cls.out, quiet=True)
        cls.pages = {}
        for root, _, files in os.walk(cls.out):
            for f in files:
                if f.endswith(".html") and "_og" not in root:
                    p = os.path.join(root, f)
                    with open(p, encoding="utf-8") as fh:
                        cls.pages[os.path.relpath(p, cls.out)] = fh.read()
        cls.deck = data.load()

    @classmethod
    def tearDownClass(cls):
        del os.environ["PJ_BASE_URL"]

    def test_pages(self):
        for p in ("index.html", "practice/index.html", "deck/index.html", "about/index.html", "embed/daily/index.html", "404.html",
                  "score/0-of-5/index.html", "score/5-of-5/index.html", "score/10-of-10/index.html"):
            self.assertIn(p, self.pages)
        for p in self.deck:
            self.assertIn("pitch/%s/index.html" % p["slug"], self.pages)
        for f in ("data/deck.json", "sitemap.xml", "robots.txt", ".nojekyll", "assets/core.js", "assets/game.js"):
            self.assertTrue(os.path.exists(os.path.join(self.out, f)), f)

    def test_game_page_wiring(self):
        html = self.pages["index.html"]
        self.assertIn('data-mode="daily"', html)
        self.assertIn('data-epoch="%s"' % site.DAILY_EPOCH, html)
        self.assertIn("assets/core.js", html)
        self.assertIn('data-mode="practice"', self.pages["practice/index.html"])

    def test_seo_on_indexable_pages(self):
        for rel, html in self.pages.items():
            p = P()
            p.feed(html)
            if p.meta.get("robots") == "noindex":
                continue
            self.assertTrue(p.title.strip(), rel)
            self.assertLessEqual(len(p.title), 120, rel)
            self.assertTrue(40 <= len(p.meta.get("description", "")) <= 320, rel)
            self.assertTrue(p.meta.get("canonical", "").startswith(BASE + "/"), rel)
            for block in p.ld:
                json.loads(block)

    def test_score_and_embed_pages_are_not_indexed(self):
        for rel in ("score/3-of-5/index.html", "embed/daily/index.html", "404.html"):
            self.assertIn('content="noindex"', self.pages[rel])
        with open(os.path.join(self.out, "sitemap.xml")) as fh:
            sm = fh.read()
        self.assertNotIn("/score/", sm)
        self.assertNotIn("/embed/", sm)
        self.assertIn("%s/pitch/doorbot/" % BASE, sm)

    def test_internal_links_resolve(self):
        missing = []
        for rel, html in self.pages.items():
            if rel == "404.html":
                continue
            p = P()
            p.feed(html)
            for href in p.links:
                if href.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                target = urlparse(urljoin("http://x/" + rel, href)).path.lstrip("/")
                if not target or target.endswith("/"):
                    target += "index.html"
                if target.startswith("og/"):
                    continue
                if not os.path.exists(os.path.join(self.out, target)):
                    missing.append("%s -> %s" % (rel, href))
        self.assertEqual(missing, [])

    def test_deck_json_matches_the_deck(self):
        with open(os.path.join(self.out, "data/deck.json")) as fh:
            d = json.load(fh)
        self.assertEqual(len(d["pitches"]), len(self.deck))
        self.assertEqual(d["daily_size"], site.DAILY_SIZE)
        self.assertTrue(all(p["sources"] for p in d["pitches"]))

    def test_disclaimer_everywhere(self):
        for rel, html in self.pages.items():
            if rel.startswith("embed/"):
                continue
            self.assertIn("not investment advice", html.replace("Nothing here is investment advice", "not investment advice"), rel)

    def test_pitch_page_hides_the_outcome_until_asked(self):
        html = self.pages["pitch/quibi/index.html"]
        before, _, after = html.partition('<details class="reveal"')
        self.assertNotIn("shut down that December", before)
        self.assertIn("shut down that December", after)


if __name__ == "__main__":
    unittest.main()
