"""Weekly self-test of the live game: pages answer, the deck loads, embeds render, and every cited source resolves.

    python3 scripts/health.py [base_url]

Writes a report to $GITHUB_STEP_SUMMARY. Exits 1 if a page or the deck fails, or if more than 10% (minimum 3) of the
cited sources are broken. Bot walls (401/403/429) are not counted as broken.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_BASE = "https://theguysaccount.github.io/pitch-judge-investor-game"
UA = "Mozilla/5.0 (compatible; pitch-judge-linkcheck/1.0; +https://github.com/theguysaccount/pitch-judge-investor-game)"


def get(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.status, resp.read()


def check_source(url):
    for attempt in range(2):
        try:
            st, _ = get(url, timeout=25)
            return url, st, 200 <= st < 400
        except urllib.error.HTTPError as exc:
            if exc.code in (401, 403, 429):
                return url, exc.code, True
            last = exc.code
        except Exception as exc:
            last = type(exc).__name__
        time.sleep(2)
    return url, last, False


def main(base):
    base = base.rstrip("/")
    lines, failed = ["## Live game", ""], False
    for p in ("/", "/practice/", "/deck/", "/about/", "/pitch/doorbot/", "/score/3-of-5/", "/embed/daily/", "/sitemap.xml",
              "/assets/core.js", "/assets/game.js"):
        try:
            st, body = get(base + p + "?selftest=%d" % int(time.time()))
            ok = st == 200 and len(body) > 100
        except Exception as exc:
            st, ok = str(exc), False
        failed |= not ok
        lines.append("- %s %s %s" % ("ok  " if ok else "FAIL", p, st))
    try:
        _, body = get(base + "/data/deck.json")
        deck = json.loads(body)["pitches"]
        ok = len(deck) >= 50
        failed |= not ok
        lines.append("- %s deck.json has %d pitches" % ("ok  " if ok else "FAIL", len(deck)))
    except Exception as exc:
        failed = True
        lines.append("- FAIL deck.json: %s" % exc)
        deck = []
    with open(os.path.join(ROOT, "data", "pitches.json"), encoding="utf-8") as fh:
        urls = sorted({s["url"] for p in json.load(fh) for s in p["sources"]})
    with ThreadPoolExecutor(max_workers=8) as pool:
        res = list(pool.map(check_source, urls))
    broken = [(u, s) for u, s, ok in res if not ok]
    lines += ["", "## Sources", "", "%d URLs checked, %d broken" % (len(res), len(broken))] + ["- %s (%s)" % b for b in broken]
    if len(broken) > max(3, 0.10 * len(res)):
        failed = True
    text = "\n".join(lines)
    print(text)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as fh:
            fh.write(text + "\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else os.environ.get("PJ_BASE_URL", DEFAULT_BASE)))
