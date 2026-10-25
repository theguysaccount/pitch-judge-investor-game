"""Load and validate the pitch deck (data/pitches.json). The build refuses a deck that fails validation."""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DECK = os.path.join(ROOT, "data", "pitches.json")
OUTCOMES = {
    "breakout": ("Breakout", "\U0001F984", "A $1 billion+ outcome: an acquisition, an IPO, or a private valuation of at least $1 billion."),
    "success": ("Success", "✅", "Acquired, or a lasting business with sizeable sales, below the $1 billion mark."),
    "bust": ("Bust", "\U0001F4A5", "Shut down, bankrupt, or sold off for a fraction of the money put in."),
}
KINDS = ("startup", "tv")
SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
# Words in company names that are ordinary English and may legitimately appear in an anonymised pitch.
COMMON = {"the", "labs", "inc", "products", "productions", "later", "of", "and", "com", "app", "service", "company", "teas", "secret",
          "bird", "essential", "vine", "mint", "ring", "path", "convoy", "mailbox", "fab", "quip", "jet", "zoom", "pebble",
          "flickr", "cruise", "scrub", "daddy", "coffee", "meets", "bagel", "maine", "lobster", "cousins", "better", "place",
          "ten", "thirty", "one", "elves", "tipsy", "kodiak", "cakes", "chewy"}


def load(path=DECK):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def name_tokens(name):
    """Distinctive tokens of a company name, to check that the anonymised pitch does not give it away."""
    toks = re.findall(r"[A-Za-z][A-Za-z0-9.]+", name)
    return [t for t in toks if t.lower().strip(".") not in COMMON and len(t) > 2]


def leaks(p):
    """Return the distinctive name tokens that appear in what the player sees before deciding."""
    shown = " ".join([p["headline"], p["pitch"]] + p["facts"])
    found = []
    for t in name_tokens(p["name"]):
        if re.search(r"(?<![A-Za-z])%s(?![A-Za-z])" % re.escape(t.strip(".")), shown):
            found.append(t)
    return found


def validate(deck):
    errors = []
    slugs = set()
    for i, p in enumerate(deck):
        tag = p.get("slug", "#%d" % i)
        for key in ("slug", "name", "year", "kind", "stage", "headline", "pitch", "facts", "outcome", "outcome_text",
                    "outcome_year", "pros", "tags", "sources"):
            if key not in p:
                errors.append("%s: missing %s" % (tag, key))
        if any(e.startswith(tag + ": missing") for e in errors):
            continue
        if not SLUG_RE.match(p["slug"]):
            errors.append("%s: bad slug" % tag)
        if p["slug"] in slugs:
            errors.append("%s: duplicate slug" % tag)
        slugs.add(p["slug"])
        if p["outcome"] not in OUTCOMES:
            errors.append("%s: outcome must be one of %s" % (tag, sorted(OUTCOMES)))
        if p["kind"] not in KINDS:
            errors.append("%s: kind must be startup or tv" % tag)
        if p["kind"] == "tv" and p.get("pros_call") not in ("invest", "pass"):
            errors.append("%s: TV pitches need pros_call invest or pass" % tag)
        if not (isinstance(p["year"], int) and 1990 <= p["year"] <= 2030):
            errors.append("%s: year" % tag)
        if not (isinstance(p["outcome_year"], int) and p["outcome_year"] >= p["year"]):
            errors.append("%s: outcome_year must be on or after the pitch year" % tag)
        if not 80 <= len(p["pitch"]) <= 420:
            errors.append("%s: pitch should be 80-420 characters" % tag)
        if not p["facts"] or len(p["facts"]) > 3:
            errors.append("%s: 1-3 facts" % tag)
        if not p["sources"] or not all(s.get("url", "").startswith("https://") for s in p["sources"]):
            errors.append("%s: every pitch needs https sources" % tag)
        lk = leaks(p)
        if lk:
            errors.append("%s: the anonymised pitch gives away the name (%s)" % (tag, ", ".join(lk)))
    return errors
