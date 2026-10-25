"""Build the static game site into dist/.

    python3 -m judge.site

Environment (all optional):
    PJ_BASE_URL     canonical origin + path (default: the GitHub Pages URL)
    PJ_REPO         owner/name for correction links
    PJ_GOATCOUNTER  https://<code>.goatcounter.com/count (cookieless analytics; off when empty)
    PJ_SPONSOR_URL  the money slot: a "support the game" link (off when empty)
    PJ_OUT          output directory (default dist/)
"""
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from html import escape
from urllib.parse import quote

from . import data

ROOT = data.ROOT
SITE = "Would You Fund It?"
DEFAULT_BASE = "https://theguysaccount.github.io/pitch-judge-investor-game"
DEFAULT_REPO = "theguysaccount/pitch-judge-investor-game"
DAILY_EPOCH = "2026-10-25"   # daily challenge #1
DAILY_SIZE = 5
PRACTICE_SIZE = 10
DISCLAIMER = ("A game about past startups, for fun and practice. Outcomes come from public sources linked on each pitch. "
              "Nothing here is investment advice, and past outcomes say nothing about any current company or offering.")


def esc(s):
    return escape(str(s), quote=True)


def asset_version():
    h = hashlib.sha256()
    folder = os.path.join(ROOT, "site", "assets")
    for name in sorted(os.listdir(folder)):
        with open(os.path.join(folder, name), "rb") as fh:
            h.update(name.encode() + fh.read())
    return h.hexdigest()[:10]


class Ctx:
    def __init__(self, out=None):
        self.base = os.environ.get("PJ_BASE_URL", DEFAULT_BASE).rstrip("/")
        self.repo = os.environ.get("PJ_REPO", DEFAULT_REPO)
        self.goat = os.environ.get("PJ_GOATCOUNTER", "").strip()
        self.sponsor = os.environ.get("PJ_SPONSOR_URL", "").strip()
        self.out = out or os.environ.get("PJ_OUT") or os.path.join(ROOT, "dist")
        self.built = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        self.asset_v = asset_version()
        self.urls = []
        self.og = []


class Page:
    def __init__(self, ctx, path):
        self.ctx, self.path = ctx, path
        self.prefix = "../" * (0 if path in ("", "404.html") else path.rstrip("/").count("/") + 1)

    def u(self, target=""):
        return self.prefix + target

    @property
    def canonical(self):
        return self.ctx.base + "/" + self.path


NAV = [("", "Daily"), ("practice/", "Practice"), ("deck/", "All pitches"), ("about/", "How it works")]


def layout(pg, title, description, body, og="og/home.png", jsonld=None, noindex=False, body_class=""):
    c = pg.ctx
    lds = jsonld if isinstance(jsonld, list) else ([jsonld] if jsonld else [])
    full = title if SITE in title else "%s | %s" % (title, SITE)
    head = ['<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">',
            "<title>%s</title>" % esc(full), '<meta name="description" content="%s">' % esc(description),
            '<link rel="canonical" href="%s">' % esc(pg.canonical),
            '<meta property="og:type" content="website"><meta property="og:site_name" content="%s">' % esc(SITE),
            '<meta property="og:title" content="%s">' % esc(title), '<meta property="og:description" content="%s">' % esc(description),
            '<meta property="og:url" content="%s">' % esc(pg.canonical), '<meta property="og:image" content="%s/%s">' % (esc(c.base), esc(og)),
            '<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">',
            '<meta name="twitter:card" content="summary_large_image"><meta name="theme-color" content="#14532d">',
            '<link rel="icon" href="%s" type="image/svg+xml">' % pg.u("assets/favicon.svg"),
            '<link rel="stylesheet" href="%s">' % pg.u("assets/style.css?v=" + c.asset_v)]
    if noindex:
        head.append('<meta name="robots" content="noindex">')
    if c.goat:
        head.append('<meta name="pj-goatcounter" content="%s">' % esc(c.goat))
    for ld in lds:
        head.append('<script type="application/ld+json">%s</script>' % json.dumps(ld, ensure_ascii=False).replace("</", "<\\/"))
    head.append("</head>")
    nav = "".join('<a href="%s"%s>%s</a>' % (pg.u(p), ' aria-current="page"' if p == pg.path else "", n) for p, n in NAV)
    header = ('<header class="site"><div class="wrap"><a class="brand" href="%s"><span class="logo">$?</span>%s</a><nav aria-label="Main">%s</nav></div></header>'
              % (pg.u(""), esc(SITE), nav))
    support = ""
    if c.sponsor:
        support = '<p class="support"><a href="%s" rel="noopener">Support the game</a></p>' % esc(c.sponsor)
    footer = ('<footer class="site"><div class="wrap">%s<p><strong>%s</strong> is a game built on real startup pitches with public outcomes. '
              '<a href="%s">How it works</a> · <a href="%s">Every pitch and its sources</a> · <a href="https://github.com/%s">Source</a> · '
              '<a href="https://github.com/%s/issues/new?labels=correction&title=Correction">Report an error</a></p><p class="fine">%s</p></div></footer>'
              % (support, esc(SITE), pg.u("about/"), pg.u("deck/"), esc(c.repo), esc(c.repo), esc(DISCLAIMER)))
    scripts = '<script src="%s" defer></script>' % pg.u("assets/app.js?v=" + c.asset_v)
    return "".join(head) + '<body class="%s">%s<main class="wrap">%s</main>%s%s</body></html>' % (esc(body_class), header, body, footer, scripts)


def outcome_badge(o):
    label, emoji, _ = data.OUTCOMES[o]
    return '<span class="badge o-%s">%s %s</span>' % (o, emoji, label)


def game_shell(pg, mode):
    return ('<section class="game" id="game" data-mode="%s" data-deck="%s" data-epoch="%s" data-size="%d" data-base="%s" aria-live="polite">'
            '<noscript><p>This game needs JavaScript. Every pitch and outcome is also listed on <a href="%s">the deck page</a>.</p></noscript>'
            '<p class="fine">Loading the pitches…</p></section><script src="%s" defer></script><script src="%s" defer></script>'
            % (mode, pg.u("data/deck.json"), DAILY_EPOCH, DAILY_SIZE if mode == "daily" else PRACTICE_SIZE, esc(pg.ctx.base), pg.u("deck/"),
               pg.u("assets/core.js?v=" + pg.ctx.asset_v), pg.u("assets/game.js?v=" + pg.ctx.asset_v)))


def home(ctx, deck):
    pg = Page(ctx, "")
    counts = {o: sum(1 for p in deck if p["outcome"] == o) for o in data.OUTCOMES}
    body = ('<section class="hero"><h1>Would you have funded it?</h1><p class="sub">Five real startup pitches a day, shown as investors saw them, '
            'with the name hidden. Invest or pass, then see what actually happened. Same five for everyone, every day.</p></section>%s'
            '<section class="panel how"><h2>How to play</h2><ol><li>Read the pitch: the year, the stage and what the founders had then.</li>'
            '<li>Invest if you think it worked out; pass if you think it went bust.</li><li>Your call is right if you invested in a %s or %s, '
            'or passed on a %s. Share your score; come back tomorrow for five more.</li></ol>'
            '<p class="fine">The deck: %d pitches from %d to %d, %d of them from a TV pitch show, with %d breakouts, %d successes and %d busts. '
            '<a href="%s">Practice mode</a> deals ten at random.</p></section>'
            % (game_shell(pg, "daily"), outcome_badge("breakout"), outcome_badge("success"), outcome_badge("bust"), len(deck),
               min(p["year"] for p in deck), max(p["year"] for p in deck), sum(1 for p in deck if p["kind"] == "tv"),
               counts["breakout"], counts["success"], counts["bust"], pg.u("practice/")))
    ld = [{"@context": "https://schema.org", "@type": "WebSite", "name": SITE, "url": ctx.base + "/"},
          {"@context": "https://schema.org", "@type": "Game", "name": SITE, "url": ctx.base + "/",
           "description": "A daily game: real startup pitches with the names hidden. Invest or pass, then see the real outcome.",
           "genre": "Quiz", "isAccessibleForFree": True}]
    ctx.og.append(("home", og_card("Daily startup pitch game", "Would you have funded it?", "Five real pitches a day. Invest or pass. See what happened.")))
    return pg, layout(pg, "Would You Fund It? A daily startup investing game",
                      "Real startup and TV pitches with the names hidden. Invest or pass, then see whether it became a breakout, a success or a bust. "
                      "Five new pitches every day.", body, jsonld=ld, body_class="home")


def practice(ctx):
    pg = Page(ctx, "practice/")
    body = ('<section class="hero"><h1>Practice: ten random pitches</h1><p class="sub">No daily limit. A fresh deal of ten pitches from the '
            'whole deck every time.</p></section>%s' % game_shell(pg, "practice"))
    return pg, layout(pg, "Startup investing quiz: practice mode",
                      "Ten random real startup pitches with known outcomes. Would you invest or pass? Test your judgment as many times as you like.",
                      body)


def pitch_page(ctx, p, deck):
    pg = Page(ctx, "pitch/%s/" % p["slug"])
    facts = "".join("<li>%s</li>" % esc(f) for f in p["facts"])
    srcs = " · ".join('<a href="%s" rel="nofollow noopener" target="_blank">%s</a>' % (esc(s["url"]), esc(s["title"])) for s in p["sources"])
    pros = esc(p["pros"])
    if p["kind"] == "tv":
        pros = "On the TV pitch show: %s" % pros
    same = [q for q in deck if q["outcome"] == p["outcome"] and q["slug"] != p["slug"]][:4]
    other = [q for q in deck if q["outcome"] != p["outcome"] and set(q["tags"]) & set(p["tags"])][:4]
    more = "".join('<li><a href="%s">%s</a> (%d) %s</li>' % (pg.u("pitch/%s/" % q["slug"]), esc(q["name"]), q["year"], outcome_badge(q["outcome"]))
                   for q in other + same)
    body = ('<nav class="crumbs"><a href="%s">Daily game</a> › <a href="%s">All pitches</a> › %s</nav>'
            '<article class="case"><p class="kicker">%d · %s%s</p><h1>Would you have funded %s?</h1>'
            '<section class="card pitchcard"><p class="hl">%s</p><p>%s</p><ul class="facts">%s</ul>'
            '<div class="choices" data-outcome="%s"><button type="button" class="btn invest" data-call="invest">Invest</button>'
            '<button type="button" class="btn pass" data-call="pass">Pass</button></div></section>'
            '<details class="reveal" id="reveal"><summary>Show what happened</summary><div class="answer"><p class="verdict-line">%s</p>'
            '<p><b>%s</b> %s</p><p class="pros">%s</p><p class="fine">Sources: %s</p></div></details>'
            '<section class="panel"><h2>More pitches</h2><ul class="more">%s</ul><p><a class="btn" href="%s">Play today’s five</a></p></section></article>'
            % (pg.u(""), pg.u("deck/"), esc(p["name"]), p["year"], esc(p["stage"]), " · TV pitch" if p["kind"] == "tv" else "",
               esc(p["name"]), esc(p["headline"]), esc(p["pitch"]), facts, esc(p["outcome"]), outcome_badge(p["outcome"]),
               esc(p["name"]), esc(p["outcome_text"]), pros, srcs, more, pg.u("")))
    label, emoji, _ = data.OUTCOMES[p["outcome"]]
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": "Would you have funded %s?" % p["name"],
          "description": "%s: the %d pitch, and what happened (%s)." % (p["name"], p["year"], label), "url": pg.canonical,
          "author": {"@type": "Organization", "name": SITE}, "publisher": {"@type": "Organization", "name": SITE},
          "about": {"@type": "Organization", "name": p["name"]}, "citation": [s["url"] for s in p["sources"]]}
    desc = "The %d %s pitch for %s: %s. Would you have invested? Decide, then see what happened." % (
        p["year"], "TV" if p["kind"] == "tv" else p["stage"].lower(), p["name"], p["headline"][0].lower() + p["headline"][1:])
    return pg, layout(pg, "Would you have funded %s? The %d pitch and what happened" % (p["name"], p["year"]), desc[:300], body,
                      og="og/home.png", jsonld=ld)


def deck_page(ctx, deck):
    pg = Page(ctx, "deck/")
    sections = []
    for o in ("breakout", "success", "bust"):
        rows = "".join('<tr><td><a href="%s">%s</a></td><td>%d</td><td>%s</td><td>%s</td></tr>'
                       % (pg.u("pitch/%s/" % p["slug"]), esc(p["name"]), p["year"], esc("TV pitch" if p["kind"] == "tv" else p["stage"]),
                          esc(p["outcome_text"])) for p in sorted((p for p in deck if p["outcome"] == o), key=lambda p: p["year"]))
        label, emoji, explain = data.OUTCOMES[o]
        sections.append('<section class="panel"><h2>%s %s <span class="count">%d</span></h2><p class="fine">%s</p><div class="scroll"><table>'
                        '<thead><tr><th>Company</th><th>Pitch year</th><th>Stage</th><th>What happened</th></tr></thead><tbody>%s</tbody></table></div></section>'
                        % (emoji, label, sum(1 for p in deck if p["outcome"] == o), esc(explain), rows))
    body = ('<h1>Every pitch in the deck</h1><p class="sub warn">Spoilers: this page lists every company and how it turned out. '
            'Play first: <a href="%s">today’s five</a>.</p>%s' % (pg.u(""), "".join(sections)))
    ld = {"@context": "https://schema.org", "@type": "Dataset", "name": "Startup pitches with known outcomes",
          "description": "Real startup and TV pitches with the year, stage and a sourced outcome (breakout, success or bust).",
          "url": pg.canonical, "license": "https://creativecommons.org/licenses/by/4.0/", "isAccessibleForFree": True,
          "creator": {"@type": "Organization", "name": SITE},
          "distribution": [{"@type": "DataDownload", "encodingFormat": "application/json", "contentUrl": ctx.base + "/data/deck.json"}]}
    return pg, layout(pg, "Startups that boomed and busted: every pitch and outcome",
                      "%d real startup and TV pitches, from Zappos and YouTube to Quibi and Theranos, with what each founder pitched and what happened, "
                      "with sources." % len(deck), body, jsonld=ld)


def score_page(ctx, n, of):
    pg = Page(ctx, "score/%d-of-%d/" % (n, of))
    mode = "daily" if of == DAILY_SIZE else "practice"
    title = "I called %d of %d startups right" % (n, of)
    body = ('<section class="hero"><h1>%s</h1><p class="sub">On %s, you read real startup pitches with the names hidden and decide: invest or pass. '
            'Then you see what actually happened.</p><p><a class="btn" href="%s">Can you beat %d/%d?</a></p></section>'
            % (esc(title), esc(SITE), pg.u("" if mode == "daily" else "practice/"), n, of))
    ctx.og.append(("score-%d-of-%d" % (n, of), og_card("%s %s" % (SITE, "daily" if mode == "daily" else "practice"), title,
                                                       "Real startup pitches. Real outcomes. Invest or pass.", score=(n, of))))
    return pg, layout(pg, "%s on %s" % (title, SITE), "%s on %s. Real startup pitches with the names hidden: invest or pass, then see what happened."
                      % (title, SITE), body, og="og/score-%d-of-%d.png" % (n, of), noindex=True)


def about(ctx, deck):
    pg = Page(ctx, "about/")
    with open(os.path.join(ROOT, "site", "pages", "about.html"), encoding="utf-8") as fh:
        html = fh.read()
    html = (html.replace("{{u}}", pg.u("")).replace("{{base}}", ctx.base).replace("{{repo}}", ctx.repo).replace("{{n}}", str(len(deck)))
            .replace("{{tv}}", str(sum(1 for p in deck if p["kind"] == "tv"))).replace("{{disclaimer}}", esc(DISCLAIMER))
            .replace("{{epoch}}", DAILY_EPOCH))
    return pg, layout(pg, "How Would You Fund It? works", "How the startup pitch game picks pitches, hides names, scores your calls "
                      "and sources every outcome.", html)


def embed(ctx):
    pg = Page(ctx, "embed/daily/")
    html = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta name="robots" content="noindex"><title>Today’s pitch</title><link rel="stylesheet" href="%s"></head><body class="embed">'
            '<div class="ewidget" id="ewidget" data-deck="%s" data-epoch="%s" data-size="%d" data-base="%s"><span class="eh">%s</span>'
            '<p class="ep">Loading today’s pitch…</p><a class="btn" href="%s/" target="_blank" rel="noopener">Play today’s five</a></div>'
            '<script src="%s" defer></script><script src="%s" defer></script></body></html>'
            % (pg.u("assets/style.css?v=" + ctx.asset_v), pg.u("data/deck.json"), DAILY_EPOCH, DAILY_SIZE, esc(ctx.base), esc(SITE), esc(ctx.base),
               pg.u("assets/core.js?v=" + ctx.asset_v), pg.u("assets/embed.js?v=" + ctx.asset_v)))
    return pg, html


def not_found(ctx):
    pg = Page(ctx, "404.html")
    pg.prefix = ctx.base + "/"
    body = '<h1>Pass.</h1><p class="sub">That page does not exist. <a href="%s/">Play today’s five pitches</a>.</p>' % esc(ctx.base)
    return pg, layout(pg, "Page not found", "This page is not part of Would You Fund It?", body, noindex=True)


def og_card(kicker, headline, sub, score=None):
    big = ""
    if score:
        big = '<div class="ogscore">%d<span>/%d</span></div>' % score
    return ('<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="../assets/style.css"></head><body class="og">'
            '<div class="ogwrap"><div class="ogtop"><span class="logo">$?</span>%s</div>%s<h1>%s</h1><p>%s</p>'
            '<div class="ogbtns"><span class="b1">Invest</span><span class="b2">Pass</span></div></div></body></html>'
            % (esc(kicker), big, esc(headline), esc(sub)))


def deck_json(deck):
    keep = ("slug", "name", "year", "kind", "stage", "headline", "pitch", "facts", "outcome", "outcome_text", "outcome_year", "pros",
            "pros_call", "sources")
    return {"daily_epoch": DAILY_EPOCH, "daily_size": DAILY_SIZE, "pitches": [{k: p[k] for k in keep if k in p} for p in deck]}


def write(ctx, path, text):
    full = os.path.join(ctx.out, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as fh:
        fh.write(text)


def emit(ctx, pg, html, sitemap=True):
    target = pg.path + "index.html" if (pg.path == "" or pg.path.endswith("/")) else pg.path
    write(ctx, target, html)
    if sitemap:
        ctx.urls.append(pg.canonical)


def build(out=None, quiet=False):
    deck = data.load()
    problems = data.validate(deck)
    if problems:
        raise SystemExit("Refusing to build:\n  " + "\n  ".join(problems))
    ctx = Ctx(out)
    if os.path.exists(ctx.out):
        shutil.rmtree(ctx.out)
    os.makedirs(ctx.out)
    shutil.copytree(os.path.join(ROOT, "site", "assets"), os.path.join(ctx.out, "assets"))
    emit(ctx, *home(ctx, deck))
    emit(ctx, *practice(ctx))
    emit(ctx, *deck_page(ctx, deck))
    emit(ctx, *about(ctx, deck))
    for p in deck:
        emit(ctx, *pitch_page(ctx, p, deck))
    for of in (DAILY_SIZE, PRACTICE_SIZE):
        for n in range(of + 1):
            emit(ctx, *score_page(ctx, n, of), sitemap=False)
    emit(ctx, *embed(ctx), sitemap=False)
    emit(ctx, *not_found(ctx), sitemap=False)
    for name, html in ctx.og:
        write(ctx, "_og/%s.html" % name, html)
    write(ctx, "data/deck.json", json.dumps(deck_json(deck), ensure_ascii=False))
    key_path = os.path.join(ROOT, "site", "indexnow-key.txt")
    if os.path.exists(key_path):
        with open(key_path) as fh:
            key = fh.read().strip()
        write(ctx, "%s.txt" % key, key)
    today = ctx.built[:10]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += ["<url><loc>%s</loc><lastmod>%s</lastmod></url>" % (escape(u), today) for u in ctx.urls]
    sm.append("</urlset>")
    write(ctx, "sitemap.xml", "\n".join(sm) + "\n")
    write(ctx, "robots.txt", "User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n" % ctx.base)
    write(ctx, "urls.txt", "\n".join(ctx.urls) + "\n")
    write(ctx, ".nojekyll", "")
    if not quiet:
        print("built %d pages (%d pitches) into %s" % (len(ctx.urls), len(deck), ctx.out))
    return ctx


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else None)
